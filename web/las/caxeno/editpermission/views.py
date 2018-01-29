from django import forms
from django.db import transaction
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.contrib import auth
from django.db.models import Q
import urllib, urllib2, os, json, ast
from django.utils import simplejson
from LASAuth.decorators import laslogin_required
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.models import User,Permission
from django.contrib.contenttypes.models import ContentType
from apisecurity.decorators import required_parameters
from django.views.decorators.csrf import csrf_exempt
from xenopatients.models import *
from django.conf import settings

@csrf_exempt
@required_parameters(parameters=('api_key'))
def editPermission(request):
    try:
        if request.method=='POST':
            lista_perm=request.POST.get('lista')
            username=request.POST.get('username')
            print request.POST
            p=lista_perm.split(",")
            u=User.objects.get(username=username)
            u.user_permissions.clear()
            for x in p:
                if x!="":
                    print "sto settando"
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
            print 'username', username
            password=request.POST.get('password')
            print request.POST
            if enable=='yes':
                try:
                    u=User.objects.get(username=username)
                except User.DoesNotExist:
                    u = None
                if u is not None:
                    u.is_active=True;
                    u.save()
                else:
                    cu = User(username=username,password=password,is_superuser=1)
                    cu.save()
                    cu.id_supervisor=User.objects.get(pk=cu.pk)
                    cu.save()
                    print 'got it'
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
def createWG(request):
    try:

        if request.method=='POST':
            permDict=request.POST.get('lista')
            permDict = json.loads(permDict)
            name=request.POST.get('WG_name')
            #print owner
            owner=User.objects.get(username=request.POST.get('owner'))
            wg=WG(name=name,owner=owner)
            print "creato"
            wg.save()
            print "gruppo salvato"
            for user in permDict:
                for p in permDict[user]:
                    try:
                        permission=Permission.objects.get(codename=p)
                        if User.objects.filter(username=user).count()>0:
                            user=User.objects.get(username=user)
                            wg_user=WG_User(WG=wg,user=user,permission=permission)
                            wg_user.save()
                    except Exception, e:
                        print e
                        if WG.objects.filter(name=name).count()>0:
                            wg=WG.objects.get(name=name)
                            usersList=WG_User.objects.filter(WG=wg).delete()
                            wg.delete()
                        return HttpResponse("err")
            return HttpResponse("ok")
    except Exception, e:
        if WG.objects.filter(name=name).count()>0 and name is not None:
            wg=WG(name=name)
            usersList=WG_User.objects.filter(WG=wg).delete()
            wg.delete()
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
                            #owner=User(username=dictUser['username'],password='',first_name=dictUser['first_name'],last_name=dictUser['last_name'],is_active=1,email=dictUser['email'])
                            #owner.save()
                            cu = User(username=dictUser['username'],password='',first_name=dictUser['first_name'],last_name=dictUser['last_name'],is_active=1,email=dictUser['email'],is_superuser=0)
                            cu.save()
                            owner=User.objects.get(username=cu.username)
                wg=WG(owner=owner,name=wgName)
                wg.save()
            for u in userPermsList:
                dictUser=ast.literal_eval(u)
                permsList=dictUser['permissions']
                try:
                    user=User.objects.get(username=dictUser['username'])
                except:
                    #user=User(username=dictUser['username'],password='',first_name=dictUser['first_name'],last_name=dictUser['last_name'],is_active=1,email=dictUser['email'])
                    #user.save()
                    cu = User(first_name=dictUser['first_name'],last_name=dictUser['last_name'],is_active=1,email=dictUser['email'],username=dictUser['username'],password='',is_superuser=0)
                    cu.save()

                for k,v in permsList.iteritems():
                    if k==settings.THIS_APP_SHORTNAME:
                        user=User.objects.get(username=dictUser['username'])
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
            '''            
            try:
                user=User.objects.get(username=username)

            '''
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
                    #user non esiste
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
                    #user=User(username=dictUser['username'],password='',first_name=dictUser['first_name'],last_name=dictUser['last_name'],is_active=1,email=dictUser['email'])
                    #user.save()
                    cu = User(username=dictUser['username'],password='',first_name=dictUser['first_name'],last_name=dictUser['last_name'],is_active=1,email=dictUser['email'],is_superuser=0)
                    cu.save()
                #reset permessi
                users_perm=WG_User.objects.filter(user=User.objects.get(username=dictUser['username']),WG=wg)
                user=User.objects.get(username=dictUser['username'])
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















