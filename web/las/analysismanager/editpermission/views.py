from django.template import RequestContext
from django.http import HttpResponse
from django.contrib import auth
from LASAuth.decorators import laslogin_required
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.models import User,Permission
from apisecurity.decorators import required_parameters
from django.views.decorators.csrf import csrf_exempt
from mining.models import *

@csrf_exempt
@required_parameters(parameters=('api_key'))
def editPermission(request):
    try:
        if request.method=='POST':
            lista_perm=request.POST.get('lista')
            username=request.POST.get('username')
            p=lista_perm.split(",")
            u=User.objects.get(username=username)
            u.user_permissions.clear()
            for x in p:
                if x!="":
                    perm=Permission.objects.get(codename=x)
                    u.user_permissions.add(perm)
        return HttpResponse("ok")
    except Exception, e:
        print e
        return HttpResponse("err")



@csrf_exempt
@required_parameters(parameters=('api_key'))
def editModules(request):
    try:
        if request.method=='POST':
            enable=request.POST.get('enable')
            username=request.POST.get('username')
            password=request.POST.get('password')
            if 'email' in request.POST:
                email=request.POST.get('email')
            else:
                email=''
            if 'first_name' in request.POST:
                first_name=request.POST.get('first_name')
            else:
                first_name=''
            if 'last_name' in request.POST:
                last_name=request.POST.get('last_name')
            else:
                last_name=''
            if enable=='yes':
                try:
                    u=User.objects.get(username=username)
                except User.DoesNotExist:
                    u = None
                if u is not None:
                    u.is_active=True;
                    u.save()
                else:
                    u = User()
                    u.username = username
                    u.password=password
                    u.email=email
                    u.first_name=first_name
                    u.last_name=last_name
                    u.save()
            elif enable=='no':
                try:
                    u=User.objects.get(username=username)
                except User.DoesNotExist:
                    u = None
                if u is not None:
                    u.is_active=False;
                    u.save()
        return HttpResponse("ok")

    except Exception, e:
        print e
        return HttpResponse("err")


@csrf_exempt
#@required_parameters(parameters=('api_key'))
def addToWG(request):
    import ast
    try:
        if request.method=='POST':
            userPermsList=request.POST.getlist('permsList[]')
            wgName=request.POST.get('wg')
            wgOwner=request.POST.get('wgOwner')
            '''            
            try:
                user=User.objects.get(username=username)

            '''
            try:
                wg=WG.objects.get(name=wgName)
            except:
                try:
                    owner=User.objects.get(username=wgOwner)
                except: #CASO REGISTRAZIONE: AVRO UN USER IN LISTA, CHE E OWNER, ROBA SOTTO ARTIFICIO NECESSARIO
                    for u in userPermsList:
                        dictUser=ast.literal_eval(u)
                        if User.objects.filter(username=wgOwner).count()==0:
                            owner=User(username=dictUser['username'],password='',first_name=dictUser['first_name'],last_name=dictUser['last_name'],is_active=1,email=dictUser['email'])
                            owner.save()
                wg=WG(owner=owner,name=wgName)
                wg.save()
            for u in userPermsList:
                dictUser=ast.literal_eval(u)
                permsList=dictUser['permissions']
                try:
                    user=User.objects.get(username=dictUser['username'])
                except:
                    user=User(username=dictUser['username'],password='',first_name=dictUser['first_name'],last_name=dictUser['last_name'],is_active=1,email=dictUser['email'])
                    user.save()
                for k,v in permsList.iteritems():
                    if k==settings.THIS_APP_SHORTNAME:
                        p=v.split(",")
                        for item in p:
                            if item!="":
                                perm=Permission.objects.get(codename=item)
                                try:
                                    wg_user=WG_User.objects.get(user=user,WG=wg,permission=perm)
                                except:
                                    wg_user=WG_User(user=user,WG=wg,permission=perm)
                                    wg_user.save()
                                user.user_permissions.add(perm)

        return HttpResponse("ok")
    except Exception, e:
        print e
        return HttpResponse("err")


@csrf_exempt
#@required_parameters(parameters=('api_key'))
def removeFromWG(request):
    import ast
    try:
        if request.method=='POST':
            userPermsList=request.POST.getlist('permsList[]')
            wgName=request.POST.get('wg')
            wgOwner=request.POST.get('wgOwner')
            try:
                wg=WG.objects.get(name=wgName)
            except:
                owner=User.objects.get(username=wgOwner)
                wg=WG(owner=owner,name=wgName)
                wg.save()
            for u in userPermsList:
                dictUser=ast.literal_eval(u)
                permsList=dictUser['permissions']
                try:
                    user=User.objects.get(username=dictUser['username'])
                    for k,v in permsList.iteritems():
                        if k==settings.THIS_APP_SHORTNAME:
                            p=v.split(",")
                            for item in p:
                                print item
                                perm=Permission.objects.get(codename=item)
                                print perm.name
                                wg_users_list=WG_User.objects.filter(user=user,WG=wg,permission=perm).delete()
                                if WG_User.objects.filter(user=user,permission=perm).count()==0:
                                    user.user_permissions.remove(perm)
                except:
                    return HttpResponse("ok")

        return HttpResponse("ok")
    except Exception, e:
        print e
        return HttpResponse("err")


@csrf_exempt
#@required_parameters(parameters=('api_key'))
def setUserPermissions(request):
    import ast
    try:
        if request.method=='POST':
            userPermsList=request.POST.getlist('permsList[]')
            wgName=request.POST.get('wg')
            wgOwner=request.POST.get('wgOwner')
            try:
                wg=WG.objects.get(name=wgName)
            except:
                owner=User.objects.get(username=wgOwner)
                wg=WG(owner=owner,name=wgName)
                wg.save()

            for u in userPermsList:
                dictUser=ast.literal_eval(u)
                try:
                    user=User.objects.get(username=dictUser['username'])
                except:
                    user=User(username=dictUser['username'],password='',first_name=dictUser['first_name'],last_name=dictUser['last_name'],is_active=1,email=dictUser['email'])
                    user.save()

                #reset permessi
                users_perm=WG_User.objects.filter(user=user,WG=wg)
                for item in users_perm:
                    perm=item.permission
                    item.delete()
                    if WG_User.objects.filter(user=user,permission=perm).count()==0:
                        user.user_permissions.remove(perm)
                #set permessi
                permsList=dictUser['permissions']
                for k,v in permsList.iteritems():
                    if k==settings.THIS_APP_SHORTNAME:
                        p=v.split(",")
                        for item in p:
                            if Permission.objects.filter(codename=item).count()!=0:
                                perm=Permission.objects.get(codename=item)
                                try:
                                    wg_user=WG_User.objects.get(user=user,WG=wg,permission=perm)
                                except:
                                    wg_user=WG_User(user=user,WG=wg,permission=perm)
                                    wg_user.save()
                                user.user_permissions.add(perm)

        return HttpResponse("ok")
    except Exception, e:
        print e
        return HttpResponse("err")

















