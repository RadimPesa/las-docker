from django.shortcuts import render_to_response, redirect
from forms import *
from models import *
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest
from django.core.urlresolvers import reverse
from django.template import RequestContext
import urllib
import urllib2
import hashlib
import hmac
import json
from django.contrib.auth.models import User,Permission
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.decorators import user_passes_test
from django.conf import settings
from django.core.exceptions import PermissionDenied
from apisecurity.decorators import required_parameters
from registration.backends import get_backend
from registration.models import RegistrationProfile
from apisecurity.apikey import *
#from django.core.mail import EmailMessage
from emails import *
from django.db import transaction
from django.views.decorators.csrf import csrf_exempt
from xhtml2pdf import pisa
from django.template.loader import render_to_string
import cStringIO as StringIO
import cgi
import os
import xlwt
from script import *
from restoreDemo import *
from django.forms.models import model_to_dict
from py2neo import *
from django.utils import timezone

import loginas.utils

RETURN_TO_FIELD_NAME = 'return_to'
SESSION_KEY_FIELD_NAME = 'session_key'
APP_FIELD_NAME = 'appid'
RETURN_STATUS_FIELD_NAME = 'status'
USER_FIELD_NAME = 'uid'
HMAC_FIELD_NAME = 'hmac'
ANSWER_YES = 'yes'
ANSWER_NO = 'no'

def login_required(function):
    def wrapper(request, *args, **kw):
        from django.contrib.sessions.models import Session
        import datetime
        #users_online = Session.objects.filter(expire_date__gte = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")).count()        
        users_online = Session.objects.filter(expire_date__gte = timezone.now()).count()        
        #print "utenti online",users_online       
        #dirty_sessions = Session.objects.filter(expire_date__lte = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        dirty_sessions = Session.objects.filter(expire_date__lte = timezone.now())
        um_list = LASUser_logged_in_module.objects.filter(father_session_key__in=dirty_sessions)
        for um in um_list:
            um.delete()                        
            url = um.lasmodule.logout_url
            print "LASauthServer: logout "+url
            if not url.endswith('/'):
                url += '/'
            k = str(um.lasmodule.remote_key)
            app_name = um.lasmodule.shortname
            h = hmac.new(k, k + app_name + um.session_key, hashlib.sha256).hexdigest()
            data = {APP_FIELD_NAME : app_name, SESSION_KEY_FIELD_NAME : um.session_key, HMAC_FIELD_NAME : h}
            req = urllib2.Request(url, urllib.urlencode(data))
            try:
                res = urllib2.urlopen(req)
                print res.read()
            except Exception, e:
                print e
            
        #Session.objects.filter(expire_date__lte = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")).delete()
        Session.objects.filter(expire_date__lte = timezone.now()).delete()
        user=request.user  
        #if settings.DEMO:
            #if DemoRestore.objects.filter(end_datetime__isnull=True).count()>0:
            #    return HttpResponse('ASPETTA')
            #else:
            #    restoreDemo()                
            #session_opened=Session.objects.filter(expire_date__gte = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            #if LASUser_logged_in_module.objects.filter(father_session_key__in=session_opened).count()==0:
            #    import threading
            #    threading.Thread(target=runInParallel,args=[resetDatabases]).start() #, resetCaxeno,resetBiobank,resetStorage,resetMicro
            #    if not user.is_authenticated():
            #        return HttpResponseRedirect(reverse("loginmanager.views.LASLogin"))
            #    else:
            #        return function(request, *args, **kw)
            #return HttpResponseRedirect(reverse("loginmanager.views.LASLogin"))
        if not user.is_authenticated():
            return HttpResponseRedirect(reverse("loginmanager.views.LASLogin"))
        else:       
            return function(request, *args, **kw)

    return wrapper


def logoutFromLASModules(request):
    um_list = LASUser_logged_in_module.objects.filter(father_session_key=request.session.session_key)
    for um in um_list:
        url = um.lasmodule.logout_url
        print "LASauthServer: logout "+url
        if not url.endswith('/'):
            url += '/'
        k = str(um.lasmodule.remote_key)
        app_name = um.lasmodule.shortname
        h = hmac.new(k, k + app_name + um.session_key, hashlib.sha256).hexdigest()
        data = {APP_FIELD_NAME : app_name, SESSION_KEY_FIELD_NAME : um.session_key, HMAC_FIELD_NAME : h}
        req = urllib2.Request(url, urllib.urlencode(data))
        try:
            res = urllib2.urlopen(req)
            print res.read()
        except Exception, e:
            print e
        
        um.delete()

@login_required
def logout(request):
    logoutFromLASModules(request)
 
    for sesskey in request.session.keys():
        del request.session[sesskey]

    auth.logout(request)
      
    
    #for sesskey in request.session.keys():
    #    del request.session[sesskey]
    
    return HttpResponseRedirect(reverse("loginmanager.views.LASLogin"))

def LASLogin(request):

    from django.contrib.sessions.models import Session
    import datetime
    #dirty_sessions = Session.objects.filter(expire_date__lte = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    dirty_sessions = Session.objects.filter(expire_date__lte = timezone.now())
    print "dirty_sessions", dirty_sessions  
    um_list = LASUser_logged_in_module.objects.filter(father_session_key__in=dirty_sessions)
    for um in um_list:
        url = um.lasmodule.logout_url
        print "LASauthServer: logout "+url
        if not url.endswith('/'):
            url += '/'
        k = str(um.lasmodule.remote_key)
        app_name = um.lasmodule.shortname
        h = hmac.new(k, k + app_name + um.session_key, hashlib.sha256).hexdigest()
        data = {APP_FIELD_NAME : app_name, SESSION_KEY_FIELD_NAME : um.session_key, HMAC_FIELD_NAME : h}
        req = urllib2.Request(url, urllib.urlencode(data))
        try:
            res = urllib2.urlopen(req)
            print res.read()
        except Exception, e:
            print e
        um.delete()  

    projects = [app for app in settings.INSTALLED_APPS if app in ['mercuric'] ]
    print projects
    try:
        if LASStatus.objects.get(id=1).status==False:
            return render_to_response('login2.html', {'projects':projects, 'notActive':True})
    except:
        print "ADD RECORD TO LASSTatus!!"
        pass

    if request.method == 'POST':
        if 'username' in request.POST and 'password' in request.POST:
            #from login form
            form = LoginForm(request.POST)
            if form.is_valid():
                username = request.POST['username']
                password = request.POST['password']
                user = auth.authenticate(username=username, password=password)
                if user is not None and user.is_active:
                    auth.login(request, user)
                    import sys
                    if 'remote_request' in request.session:
                        #we're on this page as a result of a redirect
                        #redirect back to application requesting authentication
                        #ans = buildAuthResponse(request.session[APP_FIELD_NAME], request.session[SESSION_KEY_FIELD_NAME], user)
			ans = buildAuthResponse(request.session[APP_FIELD_NAME], request.session[SESSION_KEY_FIELD_NAME], user, request.session.session_key)
                        h = buildHMAC(request.session[APP_FIELD_NAME], ans, user.username, request.session[SESSION_KEY_FIELD_NAME])
                        return render_to_response('continuelogin.html', {'dest': request.session[RETURN_TO_FIELD_NAME], 'status': ans, 'session_key': request.session[SESSION_KEY_FIELD_NAME], 'uid': user.username, 'hmac': h})
                    else:
                        #no redirect
                        #return list of modules available to user
                        return HttpResponseRedirect(reverse('loginmanager.views.index'))
                else:
                    return render_to_response('login2.html', {'err_message': "Bad username or password!", 'projects':projects})
            else:
                return render_to_response('login2.html', {'err_message': "Invalid input!", 'projects':projects})
        elif RETURN_TO_FIELD_NAME in request.POST and SESSION_KEY_FIELD_NAME in request.POST and APP_FIELD_NAME in request.POST and HMAC_FIELD_NAME in request.POST:
            #we've been redirected here
            if not request.user.is_authenticated():
                #user is not yet authenticated on LASAuthServer
                if verifyHMAC(request.POST[HMAC_FIELD_NAME], request.POST[APP_FIELD_NAME], request.POST[RETURN_TO_FIELD_NAME], request.POST[SESSION_KEY_FIELD_NAME]):
                    #hmac is valid
                    #save POST parameters in session
                    request.session['remote_request'] = True
                    request.session[RETURN_TO_FIELD_NAME] = request.POST[RETURN_TO_FIELD_NAME]
                    request.session[SESSION_KEY_FIELD_NAME] = request.POST[SESSION_KEY_FIELD_NAME]
                    request.session[APP_FIELD_NAME] = request.POST[APP_FIELD_NAME]
                #return login form
                return render_to_response('login2.html', {'projects':projects})
            else:
                #user is already authenticated on LASAuthServer
                if verifyHMAC(request.POST[HMAC_FIELD_NAME], request.POST[APP_FIELD_NAME], request.POST[RETURN_TO_FIELD_NAME], request.POST[SESSION_KEY_FIELD_NAME]):
                    #hmac is valid
                    #ans = buildAuthResponse(request.POST[APP_FIELD_NAME], request.POST[SESSION_KEY_FIELD_NAME], request.user)
		    ans = buildAuthResponse(request.POST[APP_FIELD_NAME], request.POST[SESSION_KEY_FIELD_NAME], request.user, request.session.session_key)
                    h = buildHMAC(request.POST[APP_FIELD_NAME], ans, request.user.username, request.POST[SESSION_KEY_FIELD_NAME])
                    return render_to_response('continuelogin.html', {'dest': request.POST[RETURN_TO_FIELD_NAME], 'status': ans, 'session_key': request.POST[SESSION_KEY_FIELD_NAME], 'uid': request.user.username, 'hmac': h, 'permessi' :True})
                else:
                    #hmac is not valid, just return list of modules available for user
                    #TODO: warn about possible request forgery?
                    return HttpResponseRedirect(reverse('loginmanager.views.index'))
        else:
            #method is POST and not from redirect and not from login form
            if not request.user.is_authenticated():
                #user is not yet authenticated on LASAuthServer
                #return login form
                return render_to_response('login2.html', {'projects':projects})
            else:
                #user is already authenticated on LASAuthServer
                #return list of modules available for user
                return HttpResponseRedirect(reverse('loginmanager.views.index'))
    else:
        #method is GET
        if not request.user.is_authenticated():
            #user is not yet authenticated on LASAuthServer
            #return login form
            return render_to_response('login2.html', {'projects':projects})
        else:
            #user is already authenticated on LASAuthServer
            #return list of modules available for user
            return HttpResponseRedirect(reverse('loginmanager.views.index'))


def buildAuthResponse(app_name, session_key, user, father_key):
    print app_name,session_key,user,father_key
    try:
        luser = LASUser.objects.get(pk=user.pk)
        app = luser.modules.get(shortname=app_name)
        ans = ANSWER_YES
        try:
            father_session= Session.objects.get(session_key=father_key)
        except:
            father_session = None
        print father_session.session_key
        um, c = LASUser_logged_in_module.objects.get_or_create(lasuser=luser,lasmodule=app,father_session_key=father_session)
        um.session_key = session_key
        um.save()
    except Exception,e:
        print e
        ans = ANSWER_NO
    return ans

def buildHMAC(app_name, ans, username, session_key):
    try:
        k = str(LASModule.objects.get(shortname=app_name).remote_key)
    except:
        return ''
    return hmac.new(k, k + app_name + ans + username + session_key, hashlib.sha256).hexdigest()
    

def verifyHMAC(rcvdHmac, appName, returnUrl, sessionKey):
    try:
        k = str(LASModule.objects.get(shortname=appName).remote_key)
    except:
        return False
    h = hmac.new(k, k + appName + returnUrl + sessionKey, hashlib.sha256).hexdigest()
    if rcvdHmac == h:
        print "HMAC verification succeeded"
        return True
    else:
        print "HMAC verification failed"
        return False


@login_required
def index(request):
    try:
        user = request.user
        luser = LASUser.objects.get(pk=user.id)

    except Exception,e:
        print e
        return HttpResponseRedirect(reverse("loginmanager.views.logout"))
    name = user.username
    mod_list = []
    menu = {}

    for m in MenuCat.objects.all():
        menu[m.id] = {'title':m.name, 'mods': [], 'lenmod':0, 'shortname':'m'+str(m.id)}

    print menu
    for m in luser.modules.filter(menucat_id__isnull = False).order_by('menucat_id', 'name'):
        if m.name != 'LASAuthServer':
            mod = {}        
            mod['name'] = m.name
            mod['url'] = m.home_url
            menu[m.menucat_id.id]['mods'].append(mod)
            menu[m.menucat_id.id]['lenmod'] += 1


    
    menu_sort = []
    for key in sorted(menu):
        menu_sort.append(menu[key])

    print menu_sort
    #print RequestContext(request)
    piFlag=False
    managerFlag=False
    adminFlag=False
    if user.username=='lasmanager':
        managerFlag=True
    if WG.objects.filter(owner=user).count()>0 or WG_lasuser.objects.filter(lasuser=LASUser.objects.get(username=request.user.username),laspermission=LASPermission.objects.get(name='Manage Working Groups')).count()>0:
        piFlag=True
    if WG_lasuser.objects.filter(lasuser=luser,WG=WG.objects.get(name='admin')).count()>0:
        adminFlag=True

    return render_to_response('index.html',{'name':name, 'menu': menu_sort,'PI':piFlag,'admin':adminFlag,'manager':managerFlag}, RequestContext(request))



@login_required
@transaction.commit_on_success()
def manageAccount(request):
    if request.method=='POST':        
        try:
            if request.POST.get('action')=='manageCircles':
                if request.POST.get('step')=='checkName':
                    try:
                        blackList=['Pi','Assigner','Executor','User','Password','Username','Planner','Suffix']
                        name=request.POST.get('name')
                        print name
                        if name not in blackList:
  			    return_dict={'message':'ok'}
			else:
                            return_dict={'message':'invalid'}
                    except Exception,e:
                        print e
                        return_dict={'message':'error'}
                    json_response = json.dumps(return_dict)
                    return HttpResponse(json_response,mimetype='application/json')
                elif request.POST.get('step')=='update':
                    wg=WG.objects.get(id=request.POST.get('wgID'))
                    circlesList=json.loads(request.POST.get('circlesList'))
                    gdb=neo4j.GraphDatabaseService(settings.GRAPH_DB_URL)
                    for k,v in circlesList.items():
                        if len(v)==0:
                            q=neo4j.CypherQuery(gdb,"MATCH (n:User), (wg:WG) WHERE n.identifier='"+request.user.username+"' and wg.identifier='"+wg.name+"' MATCH (n)-[r:has"+k+"]->() DELETE r")
                            r=q.execute()
                        else:
                            for item in v:
                                q=neo4j.CypherQuery(gdb,"MATCH (n:User), (s:User) WHERE n.identifier='"+request.user.username+"' and s.identifier='"+item+"' CREATE (n)-[r:has"+k+"]->(s) RETURN r")
                                r=q.execute()
                        try:
                            rt=RelationalTag.objects.get(name=k)
                        except:
                            rt=RelationalTag(name=k)
                            rt.save()
		    return_dict={'message':'ok'}
		    json_response = json.dumps(return_dict)
                    return HttpResponse(json_response,mimetype='application/json')
                    
            if request.POST.get('action')=='manageNotifications':
                try:
                    print request.POST
                    wgList=json.loads(request.POST.get('wgList'))
                    lasuser=LASUser.objects.get(username=request.user.username)
                    for wgItem in wgList:
                        wg=WG.objects.get(id=wgItem['id'])
                        wg_lasuser=WG_lasuser.objects.filter(lasuser=lasuser,WG=wg)
                        WG_lasuser_recipient.objects.filter(wg_lasuser__in=wg_lasuser).delete()
                        WG_lasuser_relationalTag.objects.filter(wg_lasuser__in=wg_lasuser).delete()
                        for perm in wgItem['laspermission']:
                            lasper=LASPermission.objects.get(id=perm['id'])
                            wg_lasuser=WG_lasuser.objects.get(lasuser=lasuser,WG=wg,laspermission=lasper)
                            if perm['selectedRecipients'] is not None:
                                stringRec=json.dumps(perm['selectedRecipients'])
                                try:
                                    record=WG_lasuser_recipient.objects.get(wg_lasuser=wg_lasuser)
                                    record.recipientList=stringRec
                                    record.save()
                                except:
                                    record=WG_lasuser_recipient(wg_lasuser=wg_lasuser,recipientList=stringRec)
                                    record.save()

                            if perm['selectedTags'] is not None:
                                for relationalTag in perm['selectedTags']:
                                    tag=RelationalTag.objects.get(name=str(relationalTag))
                                    record=WG_lasuser_relationalTag(wg_lasuser=wg_lasuser,relationalTag=tag)
                                    record.save()
                            try:
                                templateMail=WG_lasuser_templateMail.objects.get(wg_lasuser=wg_lasuser)
                                templateMail.templateMail=perm['templateMail']
                                templateMail.save()
                            except:
                                templateMail=WG_lasuser_templateMail(wg_lasuser=wg_lasuser,templateMail=perm['templateMail'])
                                templateMail.save()
                    return_dict={'message':'ok'}
                    json_response = json.dumps(return_dict)
                    return HttpResponse(json_response,mimetype='application/json')
                except Exception,e:
                    print 'Exception in save notification recipients',e
                    return_dict={'message':'error'}
                    json_response = json.dumps(return_dict)
                    return HttpResponse(json_response,mimetype='application/json')


            wgID=request.POST.get('wgID')
            action=request.POST.get('action')
            wg=WG.objects.get(id=wgID)
            if action=='requestActivities':
                import datetime
                userID=request.POST.get('userID')
                luser=LASUser.objects.get(id=userID)
                actID=request.POST.getlist('userActivities[]')
                actList=Activity.objects.filter(id__in=actID)
                for act in actList:
                    tempRecord=ActivityRequest(activity=act,WG=wg,timestamp=datetime.datetime.now(),lasuser=luser)
                    tempRecord.save()
                
                subject='New Request in LAS for your Working Group!'
                message='Dear user,\nthere is a new request for your working group in LAS!\n\nJoin the platform to evaluate it!'
                subject=subject.encode('utf-8')
                message=message.encode('utf-8')
                act=Activity.objects.get(name='WG Management')
                bccList=list()
                ccList=list()
                toList=LASUser.objects.filter(id__in=WG_lasuser_activities.objects.filter(WG=wg,activity=act).values_list('lasuser',flat=True).distinct()).values_list('email',flat=True)
                #toList.append(wg.owner.email)
                toList=list(set(toList))
                email = EmailMessage(subject,message,"",toList,bccList,"","","",ccList)
                for upfile in request.FILES.getlist('file'):
                    filename = upfile.name
                    email.attach(upfile.name, upfile.read(), upfile.content_type)
                
                email.send(fail_silently=False)
                return_dict = {"message": "ok"}
                json_response = json.dumps(return_dict)
                return HttpResponse(json_response,mimetype='application/json')

            tempRecords=LASUser_invite.objects.filter(lasuser=LASUser.objects.get(username=request.user.username),WG=wg)
            if action=='reject':
                tempRecords.delete()
                return_dict = {"message": "ok"}
                json_response = json.dumps(return_dict)
                return HttpResponse(json_response,mimetype='application/json')
            else:
                luser=LASUser.objects.get(username=request.user.username)
                user=User.objects.get(pk=luser.pk)
                modulesSet=set()
                permsList=list()
                userDict={}
                actList=Activity.objects.filter(id__in=Role_potential_activities.objects.filter(role__id__in=tempRecords.values_list('role',flat=True)).values_list('potential_activities',flat=True)).values_list('id',flat=True)
                try:
                    for a in actList:
                        if WG_lasuser_activities.objects.filter(lasuser=luser,WG=wg,activity=Activity.objects.get(id=a)).count()==0:
                            item=WG_lasuser_activities(lasuser=luser,WG=wg,activity=Activity.objects.get(id=a))
                            item.save()
                    permList= Activities_LASPermissions.objects.filter(activity__id__in=actList).values_list('laspermission',flat=True).distinct()
                    perms=dict()
                    for perm in permList:
                        laspermission=LASPermission.objects.get(id=perm)
                        modulesSet.add(laspermission.lasmodule.shortname)
                        try:
                            WG_lasuser.objects.get(WG=wg,lasuser=luser,laspermission=laspermission)
                        except:
                            wg_lasuser=WG_lasuser(WG=wg,lasuser=luser,laspermission=laspermission)
                            wg_lasuser.save()
                        perm=Permission.objects.get(codename=laspermission.codename)
                        if (user.has_perm("loginmanager."+perm.codename)==False):
                            user.user_permissions.add(perm)
                        if not laspermission.lasmodule.shortname in perms:
                            perms[laspermission.lasmodule.shortname]=""
                        perms[laspermission.lasmodule.shortname]+=perm.codename+","

                        userDict['username']=luser.username
                        userDict['first_name']=luser.first_name
                        userDict['last_name']=luser.last_name
                        userDict['email']=luser.email
                        userDict['permissions']=perms
                        permsList.append(userDict)
                except Exception,e:
                    print 'ECCEZIONREQ',e
                for m in modulesSet:
                    lasmodule=LASModule.objects.get(shortname=m)
                    if lasmodule.name!='LASAuthServer':
                        address=lasmodule.home_url
                        url = address+"permission/addToWG/"
                        t = getApiKey()
                        print url
                        values = {'wg':wg.name,'permsList[]':permsList,'api_key':t,'wgOwner':wg.owner.username}
                        data = urllib.urlencode(values,True)
                        try:
                            resp=urllib2.urlopen(url, data)
                            res1 =  resp.read()
                        except Exception, e:
                            user.delete()
                            transaction.rollback()
                            if str(e.code)== '403':
                                print "fail api"
                                return_dict = {"message": "API error"}
                            else:
                                return_dict = {"message": "error"}
                            json_response = json.dumps(return_dict)
                            return HttpResponse(json_response,mimetype='application/json')
                    if LASUser_modules.objects.filter(lasuser=luser,lasmodule=lasmodule).count()==0:
                        rel= LASUser_modules(lasuser=luser,lasmodule=lasmodule)
                        rel.save()
                for a in Affiliation.objects.filter(id__in=LASUser_affiliation.objects.filter(lasuser=wg.owner).values_list('affiliation',flat=True)):
                    try:
                        user_aff=LASUser_affiliation.objects.get(lasuser=LASUser.objects.get(username=request.user.username),affiliation=a)
                    except:
                        user_aff=LASUser_affiliation(lasuser=LASUser.objects.get(username=request.user.username),affiliation=a,is_principal_investigator=False)
                        user_aff.save()

                tempRecords.delete()
                return_dict = {"message": "ok"}
                json_response = json.dumps(return_dict)
                return HttpResponse(json_response,mimetype='application/json')
        except Exception,e:
            print e
	    transaction.rollback()
            return_dict = {"message": "error"}
            json_response = json.dumps(return_dict)
            return HttpResponse(json_response,mimetype='application/json')

    else:
        lasuser=LASUser.objects.get(username=request.user.username)
        workingGroups=WG.objects.filter(id__in=WG_lasuser_activities.objects.filter(lasuser=LASUser.objects.get(username=request.user.username)).values_list('WG',flat=True)).distinct()
        wgList=list()
        for item in workingGroups:
            wgDict={}
            wgDict['wg']=item
            activities=Activity.objects.filter(id__in=WG_lasuser_activities.objects.filter(WG=item,lasuser=LASUser.objects.get(username=request.user.username)).values_list('activity',flat=True).distinct())
            wgDict['currentActivities']=activities
            if ActivityRequest.objects.filter(WG=item,lasuser=LASUser.objects.get(username=request.user.username)).count()>0:
                wgDict['requestedActivities']=ActivityRequest.objects.filter(WG=item,lasuser=LASUser.objects.get(username=request.user.username))
 	    else:
                 wgDict['potentialActivities']=Activity.objects.all().exclude(father_activity__isnull=True).exclude(id__in=[o.id for o in activities])

            #MANAGE NOTIFICATION SECTION
            activitiesQS=Activity.objects.filter(id__in=Activities_LASPermissions.objects.filter(laspermission__in=LASPermission.objects.filter(id__in=WG_lasuser.objects.filter(lasuser=lasuser,WG=item).values_list('laspermission',flat=True).distinct())).values_list('activity',flat=True).distinct())
            macroActivities=set()
            #for act in activitiesQS:
            #    macroActivities.add(act.father_activity)
            wg=model_to_dict(item)
            activities=list()

            wgDict['tags']={}
            gdb=neo4j.GraphDatabaseService(settings.GRAPH_DB_URL)
            q=neo4j.CypherQuery(gdb,"MATCH (start:User), (wg:WG), (end:User) where start.identifier='"+request.user.username+"' and wg.identifier='"+item.name+"' MATCH (wg)<-[:belongs]-(end)<-[r]-(start)-[:belongs]->(wg)  return type(r),end.identifier")
            r=q.execute()
            for x in r.data:
                if not x[0].split('has')[1] in wgDict['tags']:
                    wgDict['tags'][x[0].split('has')[1]]=set()
                wgDict['tags'][x[0].split('has')[1]].add(x[1])
            q=neo4j.CypherQuery(gdb,"MATCH (wg:WG) WHERE wg.identifier='"+item.name+"' MATCH (wg)<-[:belongs]-(users) return users.identifier")
            r=q.execute()
            wgDict['users']=set()
            for x in r.data:
                wgDict['users'].add(User.objects.get(username=x[0]))

            for act in activitiesQS:
                a=model_to_dict(act)
                a['father_activity']=act.father_activity
                a['laspermissions']=list()
                for perm in act.laspermissions.filter(id__in=WG_lasuser.objects.filter(WG=item,lasuser=lasuser).values_list('laspermission',flat=True).distinct()).exclude(report__isnull=True):
                    p={}
                    p['id']=perm.id
                    p['name']=perm.name
                    tags=RelationalTag.objects.filter(id__lte=6)
                    tagList=[x.name for x in tags]
                    for k in wgDict['tags'].iterkeys():
                        tagList.append(k)
                    tags=RelationalTag.objects.filter(name__in=tagList)
                    p['tags']=tags
                    #SOTTO MODIFICARE
                    p['selectedTags']=tags.filter(id__in=WG_lasuser_relationalTag.objects.filter(wg_lasuser__id__in=WG_lasuser.objects.filter(WG=item,lasuser=lasuser,laspermission=perm)).values_list('relationalTag',flat=True).distinct())
                    p['recipients']=list(User.objects.filter(id__in=WG_lasuser.objects.filter(WG=item,laspermission=perm).values_list('lasuser',flat=True).distinct()).values_list('email',flat=True))
                    wg_lasuser=WG_lasuser.objects.get(WG=item,laspermission=perm,lasuser=lasuser)
                    try:
                        selectedRecipients=json.loads(WG_lasuser_recipient.objects.get(wg_lasuser=wg_lasuser).recipientList)
                        #selectedRecipients=selectedRecipients.split(',')
                    except Exception,e:
                        print e
                        selectedRecipients=[]
                    p['selectedRecipients']=selectedRecipients
                    p['recipients'].extend(p['selectedRecipients'])
                    try:
                        p['templateMail']=WG_lasuser_templateMail.objects.get(wg_lasuser=wg_lasuser).templateMail
                    except Exception,e:
                        p['templateMail']=''
                    a['laspermissions'].append(p)
                if len(a['laspermissions'])>0:
                    activities.append(a)
                    macroActivities.add(act.father_activity)

            wgDict['macroActivities']=macroActivities
            wgDict['activities']=activities

            wgList.append(wgDict)
        #CIRCLES
        rt=RelationalTag.objects.all()

        ### loginas ###
        hasPreviousUser = loginas.utils.existsPreviousUser(request)
        isSuperUser = request.user.is_superuser

        return render_to_response('manageAccount.html',{'tempRecord':LASUser_invite.objects.filter(lasuser=LASUser.objects.get(username=request.user.username)),'workingGroups':wgList,'fatherActivities':Activity.objects.filter(father_activity__isnull=True), 'tags':rt, 'hasPreviousUser': hasPreviousUser, 'isSuperUser': isSuperUser},RequestContext(request))


@login_required
@user_passes_test(lambda u: u.username=='lasmanager')
def manageAdmin(request):
    return render_to_response('manageAdmin.html', RequestContext(request))


@login_required
@user_passes_test(lambda u: u.username=='lasmanager')
def manageUsersList(request):
    try:
        user = request.user
    except:
        return HttpResponseRedirect(reverse("loginmanager.views.logout"))
    user_list = []
    for x in LASUser.objects.all():
        u = {}
        u['id']=x.id
        u['username'] = x.username
        u['email'] = x.email
        u['first_name']=x.first_name
        u['last_name']=x.last_name
        user_list.append(u)
    return render_to_response('manageUsersList.html',{'user_list': user_list}, RequestContext(request))
   



@login_required
@user_passes_test(lambda u: u.username=='lasmanager')
@transaction.commit_on_success()
def editUserPermissions(request,userID):    
    try:    
        luser = LASUser.objects.get(pk=userID)
        user= User.objects.get(username=luser.username)
        content_type= ContentType.objects.get(app_label="loginmanager", model="laspermission")
        perms= Permission.objects.filter(content_type=content_type)
        permsok=set()
        permsnok=set()
        moduliSuper=set()
        moduli=set()
        moduli=LASUser_modules.objects.filter(lasuser=luser)
        for m in moduli:
            try:
                if LASUser_modules.objects.get(lasuser=luser,lasmodule=m).is_superuser==1:
                    moduliSuper.add(m)
            except Exception,e:
                print e
        for x in perms:
            try:
                lperms=LASPermission.objects.get(pk=x.pk)   
            except:
                lperms=None
            if lperms is not None:
                try:
                    mod=lperms.lasmodule
                    if user.has_perm("loginmanager."+x.codename):
                        permsok.add(lperms)
                    else:
                        if lperms.lasmodule in moduliSuper:
                            user.user_permissions.add(x)
                            permsok.add(lperms)
                        else:
                            permsnok.add(lperms) 
                except Exception, e:
                    print e          
        return render_to_response('manageUserPermissions.html',{'permsok':permsok, 'permsnok': permsnok, 'moduli':moduli, 'u':user, 'moduliSuper':moduliSuper}, RequestContext(request))
    except:
        try:
            user = request.user
            luser = LASUser.objects.get(pk=user.id)
        except:
            return HttpResponseRedirect(reverse("loginmanager.views.logout"))  
        user_list = []
        for x in LASUser.objects.all():
            u = {}
            u['id']=x.id
            u['username'] = x.username
            u['email'] = x.email
            u['first_name']=x.first_name
            u['last_name']=x.last_name
            user_list.append(u)
        return render_to_response('manageUsersList.html',{'user_list': user_list}, RequestContext(request))


@login_required
@user_passes_test(lambda u: u.username=='lasmanager')
@transaction.commit_on_success()
def editUserModules(request,userID):
    try:
        user = LASUser.objects.get(pk=userID)     
        modulesok=set()
        modulesnok=set()
        moduli=LASModule.objects.filter(is_active=1)
        modulesok=user.modules.all()
        for m in moduli:
            if m not in modulesok:
                modulesnok.add(m)

        return render_to_response('editUserModules.html',{'modulesok':modulesok, 'modulesnok': modulesnok, 'u':user}, RequestContext(request))
    except:
        try:
            user = request.user
            luser = LASUser.objects.get(pk=user.id)
        except:
            return HttpResponseRedirect(reverse("loginmanager.views.logout"))
        
        user_list = []
        for x in LASUser.objects.all():
            u = {}
            u['id']=x.id
            u['username'] = x.username
            u['email'] = x.email
            u['first_name']=x.first_name
            u['last_name']=x.last_name
            user_list.append(u)
        return render_to_response('manageUsersList.html',{'user_list': user_list}, RequestContext(request))




@login_required
@user_passes_test(lambda u: u.username=='lasmanager')
def editUser(request,userID):
    try:
        luser = LASUser.objects.get(pk=userID)
        user = User.objects.get(pk=userID)
        return render_to_response('manageUser.html',{'u':user}, RequestContext(request))
    except Exception,e:
        print "eccezione: "+str(e)
        user_list = []
    for x in LASUser.objects.all():
        u = {}
        u['id']=x.id
        u['username'] = x.username
        u['email'] = x.email
        u['first_name']=x.first_name
        u['last_name']=x.last_name
        user_list.append(u)
    return render_to_response('manageUsersList.html',{'user_list': user_list}, RequestContext(request))



@login_required
@user_passes_test(lambda u: u.username=='lasmanager')
def saveUserPermissions(request):
    try:
        if request.method == 'POST':
            username= request.POST['username']
            permessiOk = request.POST['permessiOk']
            permessiNok = request.POST['permessiNok']
            user = User.objects.get(username=username)
            luser=LASUser.objects.get(username=username)
            
            #INIZIALIZZO DIZIONARIO CHE CONTERRA' ELENCO PERMESSI PER MODULO
            dict1=dict()
            dictFlag=dict()
            dictError=dict();
            for m in moduli:
                dict1[m.shortname]=''
                dictFlag[m.shortname]=False;
                dictError[m.shortname]=False;
            #SPLIT DELLA STRINGA DEI PERMESSI GLOBALE    
            if permessiOk != "":
                p=permessiOk.split(",")
                #ASSEGNO OGNI SINGOLO PERMESSO ALL'UTENTE DEL LASAUTHSERVER
                #E LO MEMORIZZO NELL'ELEMENTO DEL DIZIONARIO RELATIVO AL SUO MODULO
                for x in p:
                    if x!="":
                        perm=Permission.objects.get(codename=x)
                        lperms=LASPermission.objects.get(pk=perm.pk)
                        if (user.has_perm("loginmanager."+perm.codename)==False):
                            dictFlag[lperms.lasmodule.shortname]=True
                            dict1[lperms.lasmodule.shortname]+=x+","
		        if user.is_superuser==True:
                            userMod= LASUser_modules.objects.get(lasuser=luser,lasmodule=lperms.lasmodule)
                            if userMod.is_superuser==False:    
                                dictFlag[lperms.lasmodule.shortname]=True
                                dict1[lperms.lasmodule.shortname]+=x+","
            if permessiNok != "":
                p1=permessiNok.split(",")
                #ASSEGNO OGNI SINGOLO PERMESSO ALL'UTENTE DEL LASAUTHSERVER
                #E LO MEMORIZZO NELL'ELEMENTO DEL DIZIONARIO RELATIVO AL SUO MODULO
                for x in p1:
                    if x!="":
                        perm=Permission.objects.get(codename=x)
                        lperms=LASPermission.objects.get(pk=perm.pk)
                        if (user.has_perm("loginmanager."+perm.codename)==True):
                            dictFlag[lperms.lasmodule.shortname]=True
                       
    	            
            errore=False
            errorString=""
            for m in moduli:
                if (dictFlag[m.shortname]==True):
                    address=LASModule.objects.get(shortname=m.shortname).home_url
                    url = address+"permission/editPermission/"       
                    print "provo modulo: "+m.shortname
                    print url
        
                    try:
                        t = getApiKey()
                    except Exception,e:
                        print e
                    values = {'lista' : dict1[m.shortname], 'username': username, 'api_key':t}
                    data = urllib.urlencode(values)
                    try:
                        resp=urllib2.urlopen(url, data)
                        res1 =  resp.read()
        
            
                    except urllib2.HTTPError, e:
                        print e
                        if str(e.code)== '403':
                            errore=True;
                            dictError[m.shortname]=True
                            errorString+=m.shortname+": APIauth Error\n"
        
                        else:
                            dictError[m.shortname]=True
                            errore=True
                            errorString+=m.shortname+": Network Error\n"
                    except Exception,e:
                            print e
                            dictError[m.shortname]=True
                            errore=True
                            errorString+=m.shortname+": General Error\n"
    
            #AGGIORNO SUL SERVER SOLO I PERMESSI DEGLI UTENIT PER CUI L'API NON e' FALLITA
            for m in moduli:
                if ((dictError[m.shortname]==False)and(dictFlag[m.shortname]==True)):
                    if permessiOk != "":    
                        for x in p:
                            if x!="":
                                perm=Permission.objects.get(codename=x)
                                if (user.has_perm("loginmanager."+perm.codename)==False):
                                    user.user_permissions.add(perm)
                    if permessiNok != "":
                        for x in p1:
                            if x!="":
                                perm=Permission.objects.get(codename=x)
                                if (user.has_perm("loginmanager."+perm.codename)==True):
                                    user.user_permissions.remove(perm)
            
            
            if errore==False:
                return_dict = {"message": "ok"}
                json_response = json.dumps(return_dict)
                return HttpResponse(json_response,mimetype='application/json')
            else:
                return_dict = {"message": "error","error_string":"One or more errors occured, please retry later. \n\nPermissions in following modules could be not synchronized\nErrors: \n"+errorString }
                json_response = json.dumps(return_dict)
                return HttpResponse(json_response,mimetype='application/json')
        else:
            return HttpResponseRedirect(reverse("loginmanager.views.manageAdmin"))
    
    except Exception,e:
        print e
        return_dict = {"message": "error","error_string":"One or more errors occured, please retry later. \n"}
        json_response = json.dumps(return_dict)
        return HttpResponse(json_response,mimetype='application/json')


@login_required
@user_passes_test(lambda u: u.username=='lasmanager')
def saveUserModules(request):
    try:    
        if request.method == 'POST':
            username= request.POST['username']
            modulesOk = request.POST['modulesOk']
            modulesNok = request.POST['modulesNok']
            user = User.objects.get(username=username)
            luser = LASUser.objects.get(pk=user.id)
            modulesAtt=luser.modules.all();
            errore=False
            errorString=""
            
            if modulesOk != "":
                mok=modulesOk.split(",")
                for m in mok:
                    print m
                    mod=LASModule.objects.get(shortname=m)
                    if mod not in modulesAtt:
                        rel= LASUser_modules(lasuser=luser,lasmodule=mod,is_superuser=0)
                        rel.save()
                        address=LASModule.objects.get(shortname=mod.shortname).home_url
                        url = address+"permission/editModules/"                    
                        print url
                        try:
                            t = getApiKey()
                        except Exception,e:
                            print e
                            userMod= LASUser_modules.objects.get(lasuser=luser,lasmodule=mod).delete();
                        values = {'username': luser.username, 'enable':'yes','password':luser.password,'first_name':luser.first_name,'last_name':luser.last_name,'email':luser.email, 'api_key':t} 
                        data = urllib.urlencode(values)
                        try:
                            resp=urllib2.urlopen(url, data)
                            res1 =  resp.read()
    
                        except urllib2.HTTPError, e:
                            print e
                            if str(e.code)== '403':
                                errore=True;
                                errorString+=mod.shortname+": APIauth Error\n"
                                print errorString
    
                            else:
                                errore=True
                                errorString+=mod.shortname+": General Error\n"
                                print errorString
                            userMod= LASUser_modules.objects.get(lasuser=luser,lasmodule=mod).delete()
                        except Exception,e:
                            print e
                            errore=True
                            errorString+=mod.shortname+": General Error\n"
                            print errorString
                            userMod= LASUser_modules.objects.get(lasuser=luser,lasmodule=mod).delete()
                                
            
            if modulesNok != "":
                mnok=modulesNok.split(",")
                for m in mnok:
                    print m
                    mod=LASModule.objects.get(shortname=m)
                    if mod in modulesAtt:
                        print m
                        userMod= LASUser_modules.objects.get(lasuser=luser,lasmodule=mod).delete()
                        address=LASModule.objects.get(shortname=mod.shortname).home_url
                        url = address+"permission/editModules/"                    
                        try:
                            t = getApiKey()
                        except Exception,e:
                            print e
                            rel= LASUser_modules(lasuser=luser,lasmodule=mod,is_superuser=0)
                            rel.save()
                            
                        values = {'username': username, 'enable':'no', 'api_key':t}
                        data = urllib.urlencode(values)
                        try:
                            resp=urllib2.urlopen(url, data)
                            res1 =  resp.read()
    
                        except urllib2.HTTPError, e:
                            print e
                            if str(e.code)== '403':
                                errore=True;
                                errorString+=mod.shortname+": APIauth Error\n"
                                print errorString
                            else:
                                errore=True
                                errorString+=mod.shortname+": General Error\n"
                                print errorString
                            rel= LASUser_modules(lasuser=luser,lasmodule=mod,is_superuser=0)
                            rel.save()
                        except Exception,e:
                            print e
                            errore=True
                            errorString+=mod.shortname+": General Error\n"
                            print errorString
                            rel= LASUser_modules(lasuser=luser,lasmodule=mod,is_superuser=0)
                            rel.save()
                                
            if errore==False:
                return_dict = {"message": "ok"}
                json_response = json.dumps(return_dict)
                return HttpResponse(json_response,mimetype='application/json')
            else:
                return_dict = {"message": "error","error_string":"One or more errors occured, please retry later. \n\nErrors:\n"+errorString }
                json_response = json.dumps(return_dict)
                return HttpResponse(json_response,mimetype='application/json')
        
        else:
            return HttpResponseRedirect(reverse("loginmanager.views.manageAdmin"))
    except Exception,e:
        print e
        return_dict = {"message": "error","error_string":"One or more errors occured, please retry later. \n"}
        json_response = json.dumps(return_dict)
        return HttpResponse(json_response,mimetype='application/json')


@required_parameters(parameters=('api_key'))
@transaction.commit_on_success()
def syncPermissions(request):
    try:
        lista=set();
        lista=request.POST.get('lista')
        listanomi=request.POST.get('listanomi')
        lista_perm=lista.split(',')
        lista_perm_name=listanomi.split(',')
        shortname=request.POST.get('shortname')
        modulo=LASModule.objects.get(shortname=shortname)
        perm_attuali=LASPermission.objects.filter(lasmodule_id=modulo.id)
        lista_perm_attuali=list()
        for x in perm_attuali:
            lista_perm_attuali.append(x.codename)
    
	for i,p in enumerate(lista_perm):
            print str(i),str(lista_perm_name[i]),str(p)
            if p!="":
                if p not in lista_perm_attuali:
                    content_type = ContentType.objects.get(app_label="loginmanager", model="laspermission")
		    print str(i),str(lista_perm_name[i]),str(p)
                    lasperm = LASPermission(name=lista_perm_name[i],codename=p,content_type=content_type,lasmodule=modulo)
                    lasperm.save();
        lista_perm_attuali=set(lista_perm_attuali)
	lista_perm=set(lista_perm)
        diffSet=lista_perm_attuali-lista_perm
        content_type = ContentType.objects.get(app_label="loginmanager", model="laspermission")
	for item in diffSet:
	    lasperm=LASPermission.objects.get(codename=item,content_type=content_type,lasmodule=modulo)
	    lasperm.delete()
        return HttpResponse("ok")
	    
    except Exception, e:
        print e
        return HttpResponse("err")

    
@login_required
@user_passes_test(lambda u: u.username=='lasmanager')
def manageRegistrations(request):
    if request.method=='POST':
        if request.POST.get('action')=='accept':
            try:
                backend = get_backend()
                p=request.POST.get('profile')
                modules = request.POST.get('modules')
                modules=modules.split(',')
                
                try:
                    profile= RegistrationProfile.objects.get(pk=p)
                except:
                    profile=None
                    return HttpResponse("err")
                
                if profile is not None and profile.status=='untreated':
                    backend.accept(profile, request=request)
                    u=User.objects.get(pk=profile.user_id)
                    luser=LASUser(id=u.id,first_name=u.first_name,last_name=u.last_name, username=u.username,email=u.email,is_active=u.is_active,password=u.password)
                    luser.save()
                
                    errore=False
                    errorString=""
                    print modules
                    for m in modules:
                        if m!="":
                            mod=LASModule.objects.get(id=m)
                            rel= LASUser_modules(lasuser=luser,lasmodule=mod,is_superuser=0)
                            rel.save()
                            address=mod.home_url
                            url = address+"permission/editModules/"
                            print url                    
                            try:
                                t = getApiKey()
                            except Exception,e:
                                print e
                                luser.modules.remove(mod)
                            
			    values = {'username': luser.username, 'enable':'yes','password':luser.password,'first_name':luser.first_name,'last_name':luser.last_name,'email':luser.email, 'api_key':t}
                            data = urllib.urlencode(values)
                            try:
                                resp=urllib2.urlopen(url, data)
                                res1 =  resp.read()
        
                            except urllib2.HTTPError, e:
                                print e
                                if str(e.code)== '403':
                                    errore=True;
                                    errorString+=mod.shortname+": APIauth Error\n"
                                    print errorString
                                else:
                                    errore=True
                                    errorString+=mod.shortname+": General Error\n"
                                    print errorString
                                luser.modules.remove(mod)
                            
                            except Exception,e:
                                print e
                                errore=True
                                errorString+=mod.shortname+": General Error\n"
                                luser.modules.remove(mod)
                    
                    temp =TemporaryModules.objects.get(user=u)
                    temp.delete()
                    if errore==False:
                        return_dict = {"message": "ok"}
                        json_response = json.dumps(return_dict)
                        return HttpResponse(json_response,mimetype='application/json')
                    else:
                        return_dict = {"message": "error","error_string":"User created, but one or more errors occured in modules update, please retry later. \n\nErrors:\n"+errorString }
                        json_response = json.dumps(return_dict)
                        return HttpResponse(json_response,mimetype='application/json')
                        
            except Exception, e:
                print e
                return HttpResponse("err")

        elif request.POST.get('action')=='reject':
            try:
                backend = get_backend()
                p=request.POST.get('profile')
                try:
                    profile= RegistrationProfile.objects.get(pk=p)
                except:
                    profile=None
                if profile is not None and profile.status=='untreated':
                    backend.reject(profile, request=request)
                u=User.objects.get(pk=profile.user_id)
                temp =TemporaryModules.objects.get(user=u)
                temp.delete()
                return_dict = {"message": "ok"}
                json_response = json.dumps(return_dict)
                return HttpResponse(json_response,mimetype='application/json')
            except Exception, e:
                print e
                return HttpResponse("err")   

        elif request.POST.get('action')=='delete':
            try:
                backend = get_backend()
                p=request.POST.get('profile')
                try:
                    profile= RegistrationProfile.objects.get(pk=p)
                except:
                    profile=None
                if profile is not None and profile.status=='rejected':
                    profile.delete()
                    u=User.objects.get(pk=profile.user_id)
                    u.delete()
                    return_dict = {"message": "ok"}
                    json_response = json.dumps(return_dict)
                    return HttpResponse(json_response,mimetype='application/json')
            except Exception, e:
                print e
                return HttpResponse("err")   

    try:
        backend = get_backend()
        profile_list= RegistrationProfile.objects.all();
        untreated_list = []
        pending_list = []
        rejected_list = []
        for p in profile_list:
            if p.status=='untreated':
                untreated_list.append(p)
            elif p.status =='accepted':
                pending_list.append(p)
            elif p.status =='rejected':
                rejected_list.append(p) 
            
        modules_list= TemporaryModules.objects.all()
    
        
    except Exception, e:
        print e
        return HttpResponseRedirect(reverse("loginmanager.views.logout"))

    return render_to_response('manageRegistrations.html',{'untreated_list': untreated_list,'pending_list': pending_list ,'rejected_list': rejected_list, 'modules_list':modules_list}, RequestContext(request))
        


@login_required
def requestModules(request):
    try:
        if request.method == 'POST':
            modulesOk = request.POST['modulesOk']
            luser = LASUser.objects.get(pk=request.user.id)
            
            mok=modulesOk.split(",")
            moduleRequest= ModuleRequest(user=luser,status="pending")
            moduleRequest.save()
            for m in mok:
                if m!="":
                    moduleRequest.modules.add(LASModule.objects.get(shortname=m))
            return_dict = {"message": "ok","req_id":moduleRequest.id}
            json_response = json.dumps(return_dict)
            return HttpResponse(json_response,mimetype='application/json')
                        
        else:
            user = LASUser.objects.get(pk=request.user.id)   
            modulesok=set()
            modulesnok=set()
            modulesreq=set()
            moduli=LASModule.objects.filter(is_active=1)
            modulesok=user.modules.all()
            if ModuleRequest.objects.filter(user=user).count() >0 :
                moduleRequest= ModuleRequest.objects.filter(user=user,status="pending")
                for req in moduleRequest:
                    for m in req.modules.all():
                        modulesreq.add(m)
            for m in moduli:
                if m not in modulesok and m not in modulesreq:
                    modulesnok.add(m)
            return render_to_response('requestModules.html',{'modulesnok': modulesnok,}, RequestContext(request))
    except Exception, e:
        print e
        return HttpResponseRedirect(reverse("loginmanager.views.logout"))


@login_required
@user_passes_test(lambda u: u.username=='lasmanager')
def manageModulesRequest(request):
    try:
        if request.method=='POST':
            try:
                username=request.POST.get('username')
                modules = request.POST.get('modules')
                modules=modules.split(',')
                luser=LASUser.objects.get(username=username)
                errore=False
                errorString=""
                for m in modules:
                    if m!="":
                        mod=LASModule.objects.get(id=m)
                        luser.modules.add(mod)
                        luser.save()
                        address=mod.home_url
                        url = address+"permission/editModules/"
                        print url                    
                        try:
                            t = getApiKey()
                        except Exception,e:
                            print e
                            luser.modules.remove(mod)
                            luser.save()
                        values = {'username': luser.username, 'enable':'yes','password':luser.password,'first_name':luser.first_name,'last_name':luser.last_name,'email':luser.email, 'api_key':t}
                        data = urllib.urlencode(values)
                        try:
                            resp=urllib2.urlopen(url, data)
                            res1 =  resp.read()
    
                        except urllib2.HTTPError, e:
                            print e
                            if str(e.code)== '403':
                                errore=True;
                                errorString+=mod.shortname+": APIauth Error\n"
                                print errorString
                            else:
                                errore=True
                                errorString+=mod.shortname+": General Error\n"
                                print errorString
                            luser.modules.remove(mod)
                            luser.save()
                        
                        except Exception,e:
                            print e
                            errore=True
                            errorString+=mod.shortname+": General Error\n"
                            print errorString
                            luser.modules.remove(mod)
                            luser.save()
                
                for req in ModuleRequest.objects.filter(user=luser):
                    req.status="processed"
                    req.save()
                if errore==False:
                    return_dict = {"message": "ok"}
                    json_response = json.dumps(return_dict)
                    return HttpResponse(json_response,mimetype='application/json')
                else:
                    return_dict = {"message": "error","error_string":"One or more errors occured in modules update, please retry later. \n\nErrors:\n"+errorString }
                    json_response = json.dumps(return_dict)
                    return HttpResponse(json_response,mimetype='application/json')
                    
            except Exception, e:
                print e
                return HttpResponse("err")
        
        request_list=ModuleRequest.objects.filter(status="pending")
        return render_to_response('manageModulesRequest.html', {'request_list': request_list},RequestContext(request))
    except:
        return HttpResponse("err")
    
    
@login_required
def requestPermissions(request):
    try:      
        if request.method == 'POST':
            permessiOk = request.POST['permessiOk']
            user=request.user
            luser=LASUser.objects.get(username=user.username)
            moduli=luser.modules.all() 
            p=permessiOk.split(",") 
            permissionRequest= PermissionRequest(user=luser,status="pending")
            permissionRequest.save()
            for x in p:
                if x!="":
                    perm=Permission.objects.get(codename=x)
                    lperms=LASPermission.objects.get(pk=perm.pk)
                    permissionRequest.permissions.add(lperms)
            return_dict = {"message": "ok" ,"req_id":permissionRequest.id}
            json_response = json.dumps(return_dict)
            return HttpResponse(json_response,mimetype='application/json') 
                        
        else:
            luser = LASUser.objects.get(pk=request.user.id)
            user=request.user   
            permsok=set()
            permsnok=set()
            moduli=set()
            permissionsreq=set()
            if PermissionRequest.objects.filter(user=luser).count() >0 :
                luser = LASUser.objects.get(pk=request.user.id)
                permissionRequest=PermissionRequest.objects.filter(user=luser,status="pending")
                for req in permissionRequest:
                    for m in req.permissions.all():
                        permissionsreq.add(m)

            content_type= ContentType.objects.get(app_label="loginmanager", model="laspermission")
            perms= Permission.objects.filter(content_type=content_type)
            moduli=luser.modules.all()
            for x in perms:
                try:
                    lperms=LASPermission.objects.get(pk=x.pk)   
                except:
                    lperms=None 
                if lperms is not None:
                    if user.has_perm("loginmanager."+x.codename) or lperms in permissionsreq:
                        permsok.add(lperms)
                    else:
                        permsnok.add(lperms) 
            return render_to_response('requestPermissions.html',{'permsnok': permsnok, 'moduli':moduli, 'u':user}, RequestContext(request))
    except Exception,e:
        print e
        return HttpResponseRedirect(reverse("loginmanager.views.logout"))  

        
@login_required
@user_passes_test(lambda u: u.username=='lasmanager')
def managePermissionsRequest(request):
    try:
        if request.method=='POST':
            try:
                username=request.POST.get('username')
                user=User.objects.get(username=username)
                permissions = request.POST.get('permissions')
                dict1=dict()
                dictFlag=dict()
                dictError=dict();
                luser=LASUser.objects.get(username=username)
                requestes=PermissionRequest.objects.filter(user=luser)
                if permissions!="":
                    moduli=set()
                    moduli=LASUser_modules.objects.filter(lasuser=luser)
                    permissions=permissions.split(',')
                    for req in requestes:
                        for perm in req.permissions.all():
                            dict1[perm.lasmodule.shortname]=''
                            dictError[perm.lasmodule.shortname]=False;
                        
                        for p in permissions:
                            if p!="":
                                lasp= LASPermission.objects.get(id=p)
                                dict1[lasp.lasmodule.shortname]+=lasp.codename+","
                            print dict1
                #ASSEGNO OGNI SINGOLO PERMESSO ALL'UTENTE DEL LASAUTHSERVER
                #E LO MEMORIZZO NELL'ELEMENTO DEL DIZIONARIO RELATIVO AL SUO MODULO
                    errore=False;
                    errorString="";
                    for m in moduli:
                        if (dict1[m.shortname]!=''):
                            print dict1[m.shortname]
                    for m in moduli:    
                        if (dict1[m.shortname]!=''):
                            address=LASModule.objects.get(shortname=m.shortname).home_url
                            url = address+"permission/editPermission/"       
                            print url
                            try:
                                t = getApiKey()
                            except Exception,e:
                                print e
                            values = {'lista' : dict1[m.shortname], 'username': luser.username, 'api_key':t}
                            data = urllib.urlencode(values)
                            try:
                                resp=urllib2.urlopen(url, data)
                                res1 =  resp.read()
    
                            except urllib2.HTTPError, e:
                                print e
                                if str(e.code)== '403':
                                    errore=True;
                                    dictError[m.shortname]=True
                                    errorString+=m.shortname+": APIauth Error\n"
                
                                else:
                                    dictError[m.shortname]=True
                                    errore=True
                                    errorString+=m.shortname+": Network Error\n"
                            except Exception,e:
                                    print e
                                    dictError[m.shortname]=True
                                    errore=True
                                    errorString+=m.shortname+": General Error\n"
        
                    #AGGIORNO SUL SERVER SOLO I PERMESSI DEGLI UTENIT PER CUI L'API NON e' FALLITA
                    for m in moduli:
                        if ((dictError[m.shortname]==False)and(dict1[m.shortname]!='')):
                            for x in permissions:
                                if x!="":
                                    lasp=LASPermission.objects.get(id=x)
                                    perm=Permission.objects.get(codename=lasp.codename)
                                    if (user.has_perm("loginmanager."+perm.codename)==False):
                                        user.user_permissions.add(perm)
                    
                    for req in PermissionRequest.objects.filter(user=luser):
                        req.status="processed"
                        req.save()
                    if errore==True:
                        return_dict = {"message": "error","error_string":"One or more errors occured, please retry later. \n\nPermissions in following modules could be not synchronized\nErrors: \n"+errorString }
                        json_response = json.dumps(return_dict)
                        return HttpResponse(json_response,mimetype='application/json')
                    
                
                for req in PermissionRequest.objects.filter(user=luser):
                    req.status="processed"
                    req.save()
                
                return_dict = {"message": "ok"}
                json_response = json.dumps(return_dict)
                return HttpResponse(json_response,mimetype='application/json')
                
            except Exception, e:
                print e
                return HttpResponse("err")
            
        request_list=PermissionRequest.objects.filter(status="pending")
        return render_to_response('managePermissionsRequest.html', {'request_list': request_list},RequestContext(request))
    except Exception,e:
        print e
        return HttpResponse("err")
    

@login_required
def moduleRequestReport(request):
    reqId=request.POST.get('req_id')
    req= ModuleRequest.objects.get(id=reqId)
    return render_to_response('moduleRequestReport.html', {'req': req},RequestContext(request))
    

@login_required
def permissionRequestReport(request):
    reqId=request.POST.get('req_id')
    req= PermissionRequest.objects.get(id=reqId)
    return render_to_response('permissionRequestReport.html', {'req': req},RequestContext(request))
   
@login_required
def currentPermissions(request):
    user=request.user
    luser=LASUser.objects.get(username=user.username)
    currentMod=luser.modules.all()
    currentPerm=set()
    
    for x in LASPermission.objects.all():
        perm=Permission.objects.get(codename=x.codename)
        if (user.has_perm("loginmanager."+perm.codename)==True):
            currentPerm.add(x)
    
    reqModules= ModuleRequest.objects.filter(user=user,status="pending")
    reqPermissions= PermissionRequest.objects.filter(user=user,status="pending")
    
    return render_to_response('currentPermissions.html', {'currentMod':currentMod,'currentPerm':currentPerm,'reqModules':reqModules,'reqPermissions':reqPermissions},RequestContext(request))
    


@login_required
@user_passes_test(lambda u: u.username=='lasmanager')
def sendMailOLD(request):
    try:
        if request.method=='POST':
            if request.POST.get('step'):
                return render_to_response('sendMail.html',RequestContext(request))
            else:
                try:
                    message=request.POST.get('message')
                    subject=request.POST.get('subject')
                    toRecipients=request.POST.get('toRecipients')
                    ccRecipients=request.POST.get('ccRecipients')
                    bccRecipients=request.POST.get('bccRecipients')
                    percorso=request.POST.get('path')
                    toList=list()
                    ccList=list()
                    bccList=list()
                    if toRecipients=="":
                        toRecipients= []
                    else:
                        toRecipients=toRecipients.split(',')
                        toRecipients.pop()
                        for u in LASUser.objects.filter(username__in=toRecipients):
                            if u.email!="":
                                toList.append(u.email)
                    if ccRecipients=="":
                        ccRecipients= []
                    else:
                        ccRecipients=ccRecipients.split(',')
                        ccRecipients.pop()
                        for u in LASUser.objects.filter(username__in=ccRecipients):
                            if u.email!="":
                                ccList.append(u.email)
                    if bccRecipients=="":
                        bccRecipients=[]
                    else:
                        bccRecipients=bccRecipients.split(',')
                        bccRecipients.pop()
                        for u in LASUser.objects.filter(username__in=bccRecipients):
                            if u.email!="":
                                bccList.append(u.email)
                    
                    subject=subject.encode('utf-8')
                    message=message.encode('utf-8')
                    
                    email = EmailMessage(subject,message,"",toList,bccList,"","","",ccList)
                    for upfile in request.FILES.getlist('file'):
                        filename = upfile.name
                        email.attach(upfile.name, upfile.read(), upfile.content_type)
                    
                    email.send(fail_silently=False)
                    return render_to_response('sendMail.html',{"message":"ok"},RequestContext(request))
                except Exception,e:
                    print e
                    return render_to_response('sendMail.html',{"message":"error"},RequestContext(request))
        else:    
            modules=LASModule.objects.filter(is_active=1)
            return render_to_response('selectUsersMail.html',{'modules':modules},RequestContext(request))
    except Exception,e:
        print e,'errorMail'
        return_dict = {"message": "error"}
        json_response = json.dumps(return_dict)
        return HttpResponse(json_response,mimetype='application/json')



@login_required
@user_passes_test(lambda u: u.username=='lasmanager')
def sendMail(request):
    try:
        if request.method=='POST':
            try:
                message=request.POST.get('message')
                subject=request.POST.get('subject')
                toRecipients=request.POST.get('toRecipients')
                ccRecipients=request.POST.get('ccRecipients')
                bccRecipients=request.POST.get('bccRecipients')
                percorso=request.POST.get('path')
                bccList=set()
                for x in json.loads(bccRecipients):
                    bccList.add(x)
                subject=subject.encode('utf-8')
                message=message.encode('utf-8')
                
                email = EmailMessage(subject,message,"",[],list(bccList),"","","",[])
                for upfile in request.FILES.getlist('file'):
                    filename = upfile.name
                    email.attach(upfile.name, upfile.read(), upfile.content_type)
                
                email.send(fail_silently=False)
                return render_to_response('sendMail.html',{"message":"ok"},RequestContext(request))
            except Exception,e:
                print e
                return render_to_response('sendMail.html',{"message":"error"},RequestContext(request))
        else:   
            wgDict=dict() 
            wgList=WG.objects.all()
            for wg in wgList:
                usersList=User.objects.filter(id__in=WG_lasuser.objects.filter(WG=wg).values_list('lasuser').distinct())
                wgDict[wg.name]=[x.email for x in usersList]
                
            return render_to_response('centralMail.html',{'wgDict':wgDict},RequestContext(request))
    except Exception,e:
        print e,'errorMail'
        return_dict = {"message": "error"}
        json_response = json.dumps(return_dict)
        return HttpResponse(json_response,mimetype='application/json')


'''
SECTION GESTIONE REGISTRAZIONI PI
'''



@login_required
@transaction.commit_on_success()
def manageWorkingGroups(request):
    if request.method=='POST':
        if request.POST.get('step')=='assignActivities':
            try:
                wg=WG.objects.get(id=request.POST.get('wgID'))
                lasuser=LASUser.objects.get(id=request.POST.get('lasuserID'))
                user=User.objects.get(id=request.POST.get('lasuserID'))
                activitiesList=request.POST.getlist('activitiesList[]')
                for act in activitiesList:
                    if WG_lasuser_activities.objects.filter(WG=wg,lasuser=lasuser,activity=Activity.objects.get(id=act)).count()==0:
                        m2m=WG_lasuser_activities(WG=wg,lasuser=lasuser,activity=Activity.objects.get(id=act))
                        m2m.save()

                modulesSet=set()
                perms=dict()
                userDict=dict()
                permsList=list()
                permsOk=LASPermission.objects.filter(id__in=Activities_LASPermissions.objects.filter(activity__id__in=activitiesList).values_list('laspermission',flat=True))
                for p in permsOk:
                    modulesSet.add(p.lasmodule)
                    try:
                        wg_lasuser_perm=WG_lasuser.objects.get(WG=wg,lasuser=lasuser,laspermission=p)
                    except:
                        wg_lasuser_perm=WG_lasuser(WG=wg,lasuser=lasuser,laspermission=p)
                        wg_lasuser_perm.save()
                    if (user.has_perm("loginmanager."+p.codename)==False):
                        user.user_permissions.add(Permission.objects.get(id=p.id))
                    if not p.lasmodule.shortname in perms:
                        perms[p.lasmodule.shortname]=""
                    perms[p.lasmodule.shortname]+=p.codename+","

                userDict['username']=user.username
                userDict['first_name']=user.first_name
                userDict['last_name']=user.last_name
                userDict['email']=user.email
                userDict['permissions']=perms
                permsList.append(userDict)
                for m in modulesSet:
                    if m.name!='LASAuthServer':
                        address=m.home_url
                        url = address+"permission/setUserPermissions/"
                        t = getApiKey()
                        print "final api",url
                        values = {'wg':wg.name,'permsList[]':permsList,'api_key':t,'wgOwner':wg.owner.username}
                        data = urllib.urlencode(values,True)
                        try:
                            resp=urllib2.urlopen(url, data)
                            res1 =  resp.read()
                        except Exception, e:
                            transaction.rollback()
                            print e, 
                            if str(e.code)== '403':
                                print "fail api"
                                return_dict = {"message": "API error"}
                            else:
                                return_dict = {"message": "error"}
                            json_response = json.dumps(return_dict)
                            #return HttpResponse(json_response,mimetype='application/json')
                    try:
                        luser_module=LASUser_modules.objects.get(lasuser=lasuser,lasmodule=m)
                    except:
                        luser_module=LASUser_modules(lasuser=lasuser,lasmodule=m,is_superuser=0)
                        luser_module.save()
                ActivityRequest.objects.filter(WG=wg,lasuser=lasuser).delete()
                return_dict = {"message": "ok"}
                json_response = json.dumps(return_dict)
                return HttpResponse(json_response,mimetype='application/json')
            except Exception,e:
                print 'ecc',e
                return_dict = {"message": "error"}
                json_response = json.dumps(return_dict)
                return HttpResponse(json_response,mimetype='application/json')
                
        if request.POST.get('step')=='deleteUsers':
            try:
                modulesSet=set()
                permsList=list()
                wgID=request.POST.get('wgID')
                usersList=request.POST.getlist('usersList[]')
                wg=WG.objects.get(id=wgID)
                for u in usersList:
                    userDict={}
                    luser=LASUser.objects.get(pk=u)
                    user=User.objects.get(username=luser.username)
                    wgLasuser=WG_lasuser.objects.filter(lasuser=luser,WG=wg)
                    perms=dict()
                    for item in wgLasuser:
                        if not item.laspermission.lasmodule.shortname in perms:
                            perms[item.laspermission.lasmodule.shortname]=""
                        perms[item.laspermission.lasmodule.shortname]+=item.laspermission.codename+","
                    #API a REMOVE FROM WG
                    #RIMUOVERE wgLasuser
                        modulesSet.add(item.laspermission.lasmodule.shortname)
                        tempPerm=item.laspermission
                        item.delete()
                        if WG_lasuser.objects.filter(lasuser=luser,laspermission=tempPerm).count()==0:
                            user=User.objects.get(username=luser.username)
                            perm=Permission.objects.get(codename=tempPerm.codename)
                            user.user_permissions.remove(perm)

                    userDict['username']=user.username
                    userDict['first_name']=user.first_name
                    userDict['last_name']=user.last_name
                    userDict['email']=user.email
                    userDict['permissions']=perms
                    permsList.append(userDict)

                    for m in modulesSet:
                        lasmodule=LASModule.objects.get(shortname=m)
    		        if lasmodule.name!='LASAuthServer':
                            address=lasmodule.home_url
                            url = address+"permission/removeFromWG/"
                            t = getApiKey()
                            print url
                            #print permToSend
                            values = {'wg':wg.name,'permsList[]':permsList,'api_key':t,'wgOwner':wg.owner.username}
                            data = urllib.urlencode(values,True)
                            try:
                                resp=urllib2.urlopen(url, data)
                                res1 =  resp.read()
                            except Exception, e:
                                transaction.rollback()
                                print e
                                if str(e.code)== '403':
                                    print "fail api"
                                    return_dict = {"message": "API error"}
                                else:
                                    return_dict = {"message": "error"}
                                json_response = json.dumps(return_dict)
                                return HttpResponse(json_response,mimetype='application/json')

                    WG_lasuser_activities.objects.filter(WG=wg,lasuser=luser).delete()
                return_dict = {"message": "ok"}
                json_response = json.dumps(return_dict)
                return HttpResponse(json_response,mimetype='application/json')
            except Exception,e:
                print "Fail in delete user",e
                transaction.rollback()
                return_dict = {"message": "error"}
                json_response = json.dumps(return_dict)
                return HttpResponse(json_response,mimetype='application/json')

        elif request.POST.get('step')=='updateFunctionalities':
            try:
                permsList=list()
                modulesSet=set(LASModule.objects.exclude(shortname='AMM'))
                wgID=request.POST.get('wgID')
                userID=request.POST.get('userID')
                activitiesList=request.POST.getlist('userActivities[]')
                print wgID
                wg=WG.objects.get(id=wgID)
                userDict={}
                perms=dict()
                luser=LASUser.objects.get(id=userID)
                user=User.objects.get(id=userID)
                WG_lasuser.objects.filter(WG=wg,lasuser=luser).delete()
                WG_lasuser_activities.objects.filter(WG=wg,lasuser=luser).delete()
                activities=Activity.objects.filter(id__in=activitiesList)
                for a in activities:
                    print a.name
                    m2m=WG_lasuser_activities(WG=wg,lasuser=luser,activity=a)
                    m2m.save()
                permsOk=LASPermission.objects.filter(id__in=Activities_LASPermissions.objects.filter(activity__in=activities).values_list('laspermission',flat=True))
                for p in permsOk:
                    try:
                        WG_lasuser.objects.get(lasuser=luser,laspermission=p)
                        user.user_permissions.remove(Permission.objects.get(id=p.id))
                    except:
                        pass
                for p in permsOk:
                    try:
                        wg_lasuser_perm=WG_lasuser.objects.get(WG=wg,lasuser=luserd,laspermission=p)
                    except:
                        wg_lasuser_perm=WG_lasuser(WG=wg,lasuser=luser,laspermission=p)
                        wg_lasuser_perm.save()
                    if (user.has_perm("loginmanager."+p.codename)==False):
                        user.user_permissions.add(Permission.objects.get(id=p.id))
                    if not p.lasmodule.shortname in perms:
                        perms[p.lasmodule.shortname]=""
                    perms[p.lasmodule.shortname]+=p.codename+","

                    if WG_lasuser.objects.filter(lasuser__id=user.id,laspermission=p).count()==0:
                        user.user_permissions.remove(Permission.objects.get(id=p.id))
                userDict['username']=user.username
                userDict['first_name']=user.first_name
                userDict['last_name']=user.last_name
                userDict['email']=user.email
                userDict['permissions']=perms
                permsList.append(userDict)
                for m in modulesSet:
                    if m.name!='LASAuthServer':
                        address=m.home_url
                        url = address+"permission/setUserPermissions/"
                        t = getApiKey()
                        print "final api",url
                        values = {'wg':wg.name,'permsList[]':permsList,'api_key':t,'wgOwner':wg.owner.username}
                        data = urllib.urlencode(values,True)
                        try:
                            resp=urllib2.urlopen(url, data)
                            res1 =  resp.read()
                        except Exception, e:
                            transaction.rollback()
                            print e
                            if str(e.code)== '403':
                                print "fail api"
                                return_dict = {"message": "API error"}
                            else:
                                return_dict = {"message": "error"}
                            json_response = json.dumps(return_dict)
                            #return HttpResponse(json_response,mimetype='application/json')
                    try:
                        luser_module=LASUser_modules.objects.get(lasuser=luser,lasmodule=m)
                    except:
                        luser_module=LASUser_modules(lasuser=luser,lasmodule=m,is_superuser=0)
                        luser_module.save()
            except Exception,e:
                transaction.rollback()
                print e
                return_dict={"message":"error"}
                json_response = json.dumps(return_dict)
                return HttpResponse(json_response,mimetype='application/json')

            return_dict = {"message": "ok"}
            json_response = json.dumps(return_dict)
            return HttpResponse(json_response,mimetype='application/json')
        elif request.POST.get('step')=='inviteUsers':
            wg=WG.objects.get(id=request.POST.get('wgID'))
            try:
                print request.POST.get('email')
                luser=LASUser.objects.get(email=request.POST.get('email'))
                if WG_lasuser.objects.filter(WG=wg,lasuser=luser).count()>0:
                    return_dict = {"message": "alreadyExist"}
                    json_response = json.dumps(return_dict)
                    return HttpResponse(json_response,mimetype='application/json')
                else:
                    if LASUser_invite.objects.filter(WG=wg,lasuser=luser).count()>0:
                        return_dict = {"message": "alreadyInvited"}
                        json_response = json.dumps(return_dict)
                        return HttpResponse(json_response,mimetype='application/json')

                    for role in Role.objects.filter(id__in=request.POST.getlist('rolesList[]')):
                        temp=LASUser_invite(lasuser=luser,WG=wg,role=role)
                        temp.save()
                    subject='Join a new Working Group in LAS!'
                    message='Dear user,\nyou received an invitation to a LAS Working Group.\nPlease login at %s and check your control panel in order to inspect the request.' % settings.DOMAIN_URL
                    subject=subject.encode('utf-8')
                    message=message.encode('utf-8')
                    toList=list()
                    toList.append(luser.email)
                    try:
                        email = EmailMessage(subject,message,"",toList,[],"","","",[])
                        email.send(fail_silently=False)
                        return_dict = {"message": "ok"}
                        json_response = json.dumps(return_dict)
                        return HttpResponse(json_response,mimetype='application/json')
                    except Exception,e:
                        transaction.rollback()
                        return_dict = {"message": "mailSendError"}
                        json_response = json.dumps(return_dict)
                        return HttpResponse(json_response,mimetype='application/json')

            except Exception,e:
                print "user not in LAS"
                roleString=''
                for role in Role.objects.filter(id__in=request.POST.getlist('rolesList[]')):
                    if roleString!='':
                        roleString+=', '
                    roleString+=role.name
                subject='Join LAS!'
                message='Dear user,\nyou received an invitation to join a Working Group in the LAS platform.\n\nRequest report:\nPrincipal Investigator: '+wg.owner.first_name+' '+wg.owner.last_name +'.\nRole(s): '+roleString+'\n\nPlease register at %s and select your Principal Investigator and role(s).' % settings.DOMAIN_URL
                subject=subject.encode('utf-8')
                message=message.encode('utf-8')
                toList=list()
                toList.append(request.POST.get('email'))
                try:
                    email = EmailMessage(subject,message,"",toList,[],"","","",[])
                    email.send(fail_silently=False)
                    return_dict = {"message": "ok"}
                    json_response = json.dumps(return_dict)
                except:
                    transaction.rollback()
                    return_dict = {"message": "mailSendError"}
                    json_response = json.dumps(return_dict)
                    return HttpResponse(json_response,mimetype='application/json')
                return HttpResponse(json_response,mimetype='application/json')

    else:
        luser=LASUser.objects.get(username=request.user.username)
        workingGroups= WG.objects.filter(owner=luser)
        print WG.objects.filter(id__in= WG_lasuser.objects.filter(lasuser=LASUser.objects.get(username=request.user.username),laspermission=LASPermission.objects.get(name='Manage Working Groups')).distinct().values_list('WG_id',flat=True))
        workingGroups=workingGroups | WG.objects.filter(id__in= WG_lasuser.objects.filter(lasuser=LASUser.objects.get(username=request.user.username),laspermission=LASPermission.objects.get(name='Manage Working Groups')).distinct().values_list('WG_id',flat=True))
        wgList=list()
        userPermList=list()
        for w in workingGroups:
            wg={}
            wg['id']=w.id
            wg['name']=w.name
            wg['usersList']=LASUser.objects.filter(id__in=WG_lasuser_activities.objects.filter(WG=w).values_list('lasuser',flat=True))
            wgList.append(wg)
            wg['requests']=ActivityRequest.objects.filter(WG=w)
        father_activities=Activity.objects.filter(father_activity__isnull=True)
        lasuser_activities=Activity.objects.filter(id__in=WG_lasuser_activities.objects.filter(lasuser=luser).values_list('activity',flat=True))
        pi_father_activities=Activity.objects.filter(id__in=lasuser_activities.values_list('father_activity',flat=True).distinct()).values_list('name',flat=True)
        supervisorList=set()
        supervisorList.add(luser)
        for wg in workingGroups:
            supervisorList.add(wg.owner)
        supervisorList=list(supervisorList)
        tempReg=LASUserTempRegSupervisors.objects.filter(supervisor__in=supervisorList)

        return render_to_response('manageWorkingGroups.html',{'workingGroups':wgList,'pendingRegistrations':tempReg,'piActivities':lasuser_activities,'piFatherAct':pi_father_activities,'rolesList':Role.objects.all(),'affiliationsList':Affiliation.objects.filter(id__in=LASUser_affiliation.objects.filter(lasuser=luser).values_list('affiliation',flat=True))},RequestContext(request))



@login_required
def managePiRegistration(request,recordID):
    try:
        tempRecord= LASUserTempRegSupervisors.objects.get(id=recordID)
    except:
        return HttpResponseRedirect(reverse("loginmanager.views.manageWorkingGroups"))
    luser=LASUser.objects.get(username=request.user.username)
    workingGroups= WG.objects.filter(owner=luser)| WG.objects.filter(id__in= WG_lasuser.objects.filter(lasuser=LASUser.objects.get(username=request.user.username),laspermission=LASPermission.objects.get(name='Manage Working Groups')).distinct().values_list('WG_id',flat=True))
    wgList=list()
    userPermList=list()
    for w in workingGroups:
        wg={}
        wg['id']=w.id
        wg['name']=w.name
        wgList.append(wg)

    #if tempRecord.supervisor!=luser:
    #    return HttpResponseRedirect(reverse("django.views.defaults.permission_denied"))

    ownerActivitiesSet=Activity.objects.filter(father_activity__isnull=False,id__in = WG_lasuser_activities.objects.filter(lasuser=luser).values_list('activity',flat=True))
    baseActivitiesSet=Activity.objects.filter(father_activity__isnull=False,id__in=Role_potential_activities.objects.filter(role__in=tempRecord.roles.all()).values_list('potential_activities', flat=True))
    baseActivitiesList=baseActivitiesSet & ownerActivitiesSet
    extraActivitiesList=ownerActivitiesSet.exclude(id__in= baseActivitiesSet)
    actDict={}
    baseActDict={}
    extraActDict={}
    for x in baseActivitiesList:
        if x.father_activity.name not in actDict:
            actDict[x.father_activity.name]=list()
        aDict=dict()
        aDict['name']=x.name
        aDict['id']=x.id
        aDict['found']=1
        actDict[x.father_activity.name].append(aDict)

    for x in extraActivitiesList:
        if x.father_activity.name not in actDict:
            actDict[x.father_activity.name]=list()
        aDict=dict()
        aDict['name']=x.name
        aDict['id']=x.id
        aDict['found']=0
        actDict[x.father_activity.name].append(aDict)
    return render_to_response('managePIRegistration.html',{'pendingRegistration':tempRecord,'actDict':actDict,'workingGroups':wgList,'recordID':tempRecord.pk},RequestContext(request))



@login_required
def evaluateUserRegistration(request):
    if request.method=='POST':
        if request.POST.get('action')=='accept':
            joinedWG=request.POST.getlist('joinedWG[]')
            recordID=request.POST.get('recordID')
            tempRecord=LASUserTempRegSupervisors.objects.get(id=recordID)
            userID=tempRecord.lasUserTemporaryRegistration.user.pk
            modulesToAdd=set()
            if len(joinedWG)>0:
                try:
                    backend = get_backend()
                    profile= RegistrationProfile.objects.get(user_id=userID)
                except Exception,e:
                    print "fail",e
                    return_dict = {"message": "error"}
                    json_response = json.dumps(return_dict)
                    return HttpResponse(json_response,mimetype='application/json')
                if profile is not None and profile.status=='untreated':
                    backend.accept(profile, request=request)

            luser=LASUser.objects.get(id=userID)
            user=User.objects.get(pk=userID)
            gdb=neo4j.GraphDatabaseService(settings.GRAPH_DB_URL)
            try:
                q=neo4j.CypherQuery(gdb,"CREATE (n:Social:User {identifier:'"+user.username+"'}) return n")
                r=q.execute()
            except Exception,e:
                print 'error in save user on graph',e    
            for jwg in joinedWG:
                modulesSet=set()
                permsList=list()
                userDict={}
                actList=request.POST.getlist('wgActBase['+jwg+'][]')
                try:
                    for a in actList:
                        if WG_lasuser_activities.objects.filter(lasuser=luser,WG=WG.objects.get(id=jwg),activity=Activity.objects.get(id=a)).count()==0:
                            item=WG_lasuser_activities(lasuser=luser,WG=WG.objects.get(id=jwg),activity=Activity.objects.get(id=a))
                            item.save()
                    permList= Activities_LASPermissions.objects.filter(activity__id__in=actList).values_list('laspermission',flat=True).distinct()
                    perms=dict()
                    wg=WG.objects.get(id=jwg)
                    for perm in permList:
                        laspermission=LASPermission.objects.get(id=perm)
                        modulesSet.add(laspermission.lasmodule.shortname)
                        try:
                            WG_lasuser.objects.get(WG=wg,lasuser=luser,laspermission=laspermission)
                        except:
                            wg_lasuser=WG_lasuser(WG=wg,lasuser=luser,laspermission=laspermission)
                            wg_lasuser.save()
                        perm=Permission.objects.get(codename=laspermission.codename)
                        if (user.has_perm("loginmanager."+perm.codename)==False):
                            user.user_permissions.add(perm)
                        if not laspermission.lasmodule.shortname in perms:
                            perms[laspermission.lasmodule.shortname]=""
                        perms[laspermission.lasmodule.shortname]+=perm.codename+","

                        userDict['username']=user.username
                        userDict['first_name']=user.first_name
                        userDict['last_name']=user.last_name
                        userDict['email']=user.email
                        userDict['permissions']=perms
                        permsList.append(userDict)
                    q=neo4j.CypherQuery(gdb,"MATCH (n:User),(wg:WG) where n.identifier='"+user.username+"' and wg.identifier='"+wg.name+"' CREATE UNIQUE (n)-[:belongs]->(wg) return n.identifier")
                    r=q.execute()
                except Exception,e:
                    print e
                for m in modulesSet:
                    lasmodule=LASModule.objects.get(shortname=m)
		    if lasmodule.name!='LASAuthServer':
                        #CHECK IF LASAUTHSRV!!
                        address=lasmodule.home_url
                        url = address+"permission/addToWG/"
                        t = getApiKey()
                        print url
                        values = {'wg':wg.name,'permsList[]':permsList,'api_key':t,'wgOwner':wg.owner.username}
                        data = urllib.urlencode(values,True)
                        try:
                            resp=urllib2.urlopen(url, data)
                            res1 =  resp.read()
                        except Exception, e:
                            print e
                            user.delete()
                            if str(e.code)== '403':
                                print "fail api"
                                return_dict = {"message": "API error"}
                            else:
                                return_dict = {"message": "error"}
                            json_response = json.dumps(return_dict)
                            return HttpResponse(json_response,mimetype='application/json')
                    if LASUser_modules.objects.filter(lasuser=luser,lasmodule=lasmodule,is_superuser=0).count()==0:
                        rel= LASUser_modules(lasuser=luser,lasmodule=lasmodule,is_superuser=0)
                        rel.save()
            #AGGIORNAR WG LOCALI
            #DELETE TEMP
            temporaryReg=LASUserTemporaryRegistration.objects.get(user=user)
            temporaryReg.delete()
            return_dict = {"message": "ok"}
            json_response = json.dumps(return_dict)
            return HttpResponse(json_response,mimetype='application/json')
        else:
            try:
                recordID=request.POST.get('recordID')
                tempRecord=LASUserTempRegSupervisors.objects.get(id=recordID)
                user=tempRecord.lasUserTemporaryRegistration.user
                tempRecord.delete()
                if LASUserTempRegSupervisors.objects.filter(lasUserTemporaryRegistration__user=user).count()==0:
                    try:
                        backend = get_backend()
                        profile= RegistrationProfile.objects.get(user=user)
                    except:
                        profile=None
                    if profile is not None and profile.status=='untreated':
                        backend.reject(profile, request=request)
                        user.delete()

                return_dict = {"message": "ok"}
                json_response = json.dumps(return_dict)
                return HttpResponse(json_response,mimetype='application/json')
            except Exception,e:
                print e
                return_dict = {"message": "error"}
                json_response = json.dumps(return_dict)
                return HttpResponse(json_response,mimetype='application/json')
    else:
        return HttpResponse('ok')



@login_required
def manageUserWorkingGroup(request,wgID,uID):
    try:
        try:
            wg=WG.objects.get(id=wgID,owner=LASUser.objects.get(username=request.user.username))
        except:
            if WG_lasuser.objects.filter(WG=WG.objects.get(id=wgID),lasuser=LASUser.objects.get(username=request.user.username),laspermission=LASPermission.objects.get(name='Manage Working Groups')).count()>0:
                wg= wg=WG.objects.get(id=wgID)
            else:
                raise Exception('Not Allowed')
        owner=wg.owner
        if WG_lasuser_activities.objects.filter(WG=wg,lasuser=LASUser.objects.get(id=uID)).count()==0:
            return HttpResponseRedirect(reverse("loginmanager.views.index"))
        else:#LOGICa
            luser=owner
            pi_activities=Activity.objects.filter(id__in=WG_lasuser_activities.objects.filter(WG=wg,lasuser=luser).values_list('activity',flat=True)).exclude(father_activity__isnull=True)
            pi_father_activities=Activity.objects.filter(id__in=pi_activities.values_list('father_activity',flat=True).distinct()).values_list('name',flat=True)
            current_activities=Activity.objects.filter(id__in=WG_lasuser_activities.objects.filter(WG=wg,lasuser=LASUser.objects.get(id=uID)).values_list('activity',flat=True))
            current_father_activities=Activity.objects.filter(id__in=current_activities.values_list('father_activity',flat=True).distinct())
            userDict=dict()
            for act in current_activities:
                if act.father_activity.name not in userDict:
                    userDict[act.father_activity.name]=list()
                actDict=dict()
                actDict['name']=act.name
                actDict['id']=act.id
                actDict['found']=1
                userDict[act.father_activity.name].append(actDict)
            for act in set(pi_activities).difference(set(current_activities)):
                if act.father_activity.name not in userDict:
                    userDict[act.father_activity.name]=list()
                actDict=dict()
                actDict['name']=act.name
                actDict['id']=act.id
                actDict['found']=0
                userDict[act.father_activity.name].append(actDict)
                print act.name 
            return render_to_response('manageUserWG.html',{'lasuser':LASUser.objects.get(id=uID),'wg':wg,'userDict':userDict},RequestContext(request))
    except Exception,e:
        print e
        return HttpResponseRedirect(reverse("loginmanager.views.index"))



@login_required
@user_passes_test(lambda u: u.username=='lasmanager')
@transaction.commit_on_success()
def manageRegistrationsManager(request):
    if request.method=='POST':
        if request.POST.get('action')=='accept':
            try:
                backend = get_backend()
                p=request.POST.get('profile')
                activities = request.POST.get('activities')
                activities=activities.split(',')
                try:
                    profile= RegistrationProfile.objects.get(pk=p)
                except:
                    profile=None
                    return_dict = {"message":"error"}
                    json_response = json.dumps(return_dict)
                    return HttpResponse(json_response,mimetype='application/json')
                try:
                    if profile is not None and profile.status=='untreated':
                        backend.accept(profile, request=request)
                        user=User.objects.get(pk=profile.user_id)
                        temp=PiTemporaryRegistration.objects.get(user=user)
                        luser=LASUser.objects.get(pk=profile.user_id)
                        wg=WG.objects.get(owner=luser)
                        errore=False
                        errorString=""
                        modulesSet=set()
                        permsList=list()
                        perms=dict()
                        userDict={}
                        laspermissions=LASPermission.objects.filter(id__in=Activities_LASPermissions.objects.filter(activity_id__in=PiTemporaryRegistration_Activities.objects.filter(piTemporaryRegistration__id=temp.id).values_list('activity',flat='True')).values_list('laspermission',flat='True'))
                        for laspermission in laspermissions:
                            modulesSet.add(laspermission.lasmodule.shortname)
                            try:
                                WG_lasuser.objects.get(WG=wg,lasuser=luser,laspermission=laspermission)
                            except:
                                wg_lasuser=WG_lasuser(WG=wg,lasuser=luser,laspermission=laspermission)
                                wg_lasuser.save()
                            perm=Permission.objects.get(codename=laspermission.codename)
                            if (user.has_perm("loginmanager."+perm.codename)==False):
                                user.user_permissions.add(perm)
                            if not laspermission.lasmodule.shortname in perms:
                                perms[laspermission.lasmodule.shortname]=""
                            perms[laspermission.lasmodule.shortname]+=perm.codename+","

                            userDict['username']=user.username
                            userDict['first_name']=user.first_name
                            userDict['last_name']=user.last_name
                            userDict['email']=user.email
                            userDict['permissions']=perms
                            permsList.append(userDict)
                        for m in modulesSet:
                            lasmodule=LASModule.objects.get(shortname=m)
                            if lasmodule.name!='LASAuthServer':
                                address=lasmodule.home_url
                                url = address+"permission/addToWG/"
                                t = getApiKey()
                                print url
                                values = {'wg':wg.name,'permsList[]':permsList,'api_key':t,'wgOwner':wg.owner.username}
                                data = urllib.urlencode(values,True)
                                try:
                                    resp=urllib2.urlopen(url, data)
                                    res1 =  resp.read()
                                except Exception, e:
                                    print 'Eccezione in salvataggio PI 1)',e
                                    if str(e.code)== '403':
                                        print "fail api"
                                        return_dict = {"message": "API error"}
                                    else:
                                        return_dict = {"message": "error"}
                                    #transaction.rollback()
                                    #json_response = json.dumps(return_dict)
                                    #return HttpResponse(json_response,mimetype='application/json')
                            if LASUser_modules.objects.filter(lasuser=luser,lasmodule=lasmodule,is_superuser=0).count()==0:
                                rel= LASUser_modules(lasuser=luser,lasmodule=lasmodule,is_superuser=0)
                                rel.save()
                        activityList=Activity.objects.filter(id__in=PiTemporaryRegistration_Activities.objects.filter(piTemporaryRegistration__id=temp.id).values_list('activity',flat='True'))
                        for act in activityList:
                            try:
                                lasuserAct=WG_lasuser_activities.objects.get(WG=wg,lasuser=luser,activity=act)
                            except Exception,e:
                                lasuserAct=WG_lasuser_activities(WG=wg,lasuser=luser,activity=act)
                                lasuserAct.save()
                        try:
                            potSup=PotentialSupervisor.objects.get(email=luser.email)
                            for item in LASUserTempRegPotSupervisors.objects.filter(potentialSupervisor=potSup):
                                tempReg=LASUserTempRegSupervisors(lasUserTemporaryRegistration=item.lasUserTemporaryRegistration,supervisor=luser)
                                tempReg.save()
                                tempReg.roles=item.roles.all()
                                item.delete()
                            potSup.delete()
                        except Exception,e:
                            print 'Eccezione in salvataggio PI 2)',e
                            #transaction.rollback()
                            #return_dict = {"message":"error"}
                            #json_response = json.dumps(return_dict)
                            #return HttpResponse(json_response,mimetype='application/json')

                except Exception,e:
                    print 'Eccezione in salvataggio PI 3)',e
                    transaction.rollback()
                    user=User.objects.get(pk=profile.user_id)
                    user.delete()
                    return_dict = {"message":"error"}
                    json_response = json.dumps(return_dict)
                    return HttpResponse(json_response,mimetype='application/json')
                return_dict = {"message":"ok"}
                json_response = json.dumps(return_dict)
                temporaryReg=PiTemporaryRegistration.objects.get(user=user)
                temporaryReg.delete()
                return HttpResponse(json_response,mimetype='application/json')

            except Exception, e:
                transaction.rollback()
                print 'Eccezione in salvataggio PI 4)',e
                return HttpResponse("err")
        elif request.POST.get('action')=='reject':
            try:
                backend = get_backend()
                p=request.POST.get('profile')
                try:
                    profile= RegistrationProfile.objects.get(pk=p)
                except:
                    profile=None
                if profile is not None and profile.status=='untreated':
                    backend.reject(profile, request=request)
                    user=User.objects.get(id=profile.user.id)
                    user.delete()
                return_dict = {"message": "ok"}
                json_response = json.dumps(return_dict)
                return HttpResponse(json_response,mimetype='application/json')
            except Exception, e:
                print e
                transaction.rollback()
                return_dict = {"message":"error"}
                json_response = json.dumps(return_dict)
                return HttpResponse(json_response,mimetype='application/json')
        elif request.POST.get('action')=='delete':
            try:
                backend = get_backend()
                p=request.POST.get('profile')
                try:
                    profile= RegistrationProfile.objects.get(pk=p)
                except:
                    profile=None
                if profile is not None and profile.status=='rejected':
                    profile.delete()
                    luser=LASUser.objects.get(pk=profile.user_id)
                    luser.delete()
                    try:
                        u=LASUser.objects.get(pk=profile.user_id)
                        u.delete()
                    except Exception, e:
                        print "gia rimosso"
                    return_dict = {"message": "ok"}
                    json_response = json.dumps(return_dict)
                    return HttpResponse(json_response,mimetype='application/json')
            except Exception, e:
                print e
                transaction.rollback()
                return_dict = {"message":"error"}
                json_response = json.dumps(return_dict)
                return HttpResponse(json_response,mimetype='application/json')

    try:
        backend = get_backend()
        profile_list= RegistrationProfile.objects.filter(user__id__in=PiTemporaryRegistration.objects.all().values_list('user', flat=True))
        untreated_list = []
        pending_list = []
        rejected_list = []
        for p in profile_list:
            u={}
            u['profile']=p
            if p.status=='untreated':
                u['father_activities']=set()
                u['activities']= Activity.objects.filter(father_activity__isnull=False,id__in=PiTemporaryRegistration_Activities.objects.filter(piTemporaryRegistration__in=PiTemporaryRegistration.objects.filter(user=p.user)).values_list('activity', flat=True))
                act_list=u['activities']
                for act in act_list:
                    u['father_activities'].add(act.father_activity)
                untreated_list.append(u)
            elif p.status =='accepted':
                pending_list.append(u)
            elif p.status =='rejected':
                rejected_list.append(u)
    except Exception, e:
        print e
        return HttpResponseRedirect(reverse("loginmanager.views.logout"))

    return render_to_response('manageRegistrationsManager.html',{'untreated_list': untreated_list,'pending_list': pending_list ,'rejected_list': rejected_list}, RequestContext(request))

        
@csrf_exempt
def generate_report(request):
    try:
        print request.POST['tabledata']
        dataTable = json.loads(request.POST['tabledata'])
        formatFile = dataTable['fileformat']
        filename = dataTable['filename']
        print formatFile, filename
        result = StringIO.StringIO()
        if formatFile == 'pdf':
            filename += '.pdf'
            html  = render_to_string('reportPdf.html', { 'pagesize' : 'landscape', 'header':dataTable['header'], 'body':dataTable['body'], 'title':dataTable['title']}, context_instance=RequestContext(request))
            pdf = pisa.CreatePDF(StringIO.StringIO(html.encode("UTF-8")), dest=result )
	    #pdf = pisa.CreatePDF(StringIO.StringIO(html.encode("UTF-8")), dest=result, link_callback=fetch_resources)
            if pdf.err:
                raise Exception("error in rendering pdf")
        elif formatFile == 'las':
            filename += '.las'
            result.write('\t'.join([h['title'] for h in dataTable['header']]))
            result.write('\n')
            for row in dataTable['body']:
                result.write('\t'.join([str(cell['data']) for cell in row]))
                result.write('\n')
        elif formatFile == 'data':
            filename += '.data'
            for row in dataTable['body']:
                result.write('\t'.join([str(cell['data']) for cell in row]))
                result.write('\n')
        elif formatFile == 'excel':
            filename += '.xls'
            wbk = xlwt.Workbook()
            sheet = wbk.add_sheet('Data')
            fontBold = xlwt.Font()
            fontBold.bold = True
            patternH = xlwt.Pattern() # Create the Pattern 
	    patternH.pattern = xlwt.Pattern.SOLID_PATTERN # May be: NO_PATTERN, SOLID_PATTERN, or 0x00 through 0x12 
            patternH.pattern_fore_colour = 22 # May be: 8 through 63. 0 = Black, 1 = White, 2 = Red, 3 = Green, 4 = Blue, 5 = Yellow, 6 = Magenta, 7 = Cyan, 16 = Maroon, 17 = Dark Green, 18 = Dark Blue, 19 = Dark Yellow , almost brown), 20 = Dark Magenta, 21 = Teal, 22 = Light Gray, 23 = Dark Gray, the list goes on... 
            patternC = xlwt.Pattern()
            patternC.pattern = xlwt.Pattern.SOLID_PATTERN
            patternC.pattern_fore_colour = 5
            styleHeader = xlwt.XFStyle()
            styleHeader.pattern = patternH
            styleHeader.font = fontBold
            styleCell = xlwt.XFStyle()
            styleCell.pattern = patternC
            row = 0
            col = 0
            for h in dataTable['header']:
                sheet.write(row, col, str(h['title']), styleHeader)
                col +=1
            row += 1
            for r in dataTable['body']:
                col = 0
                for cell in r:
                    dCell = cell['data']
                    try:
                        float(dCell)
                        dCell = float(dCell)
                    except ValueError:
                        pass
                    if 'highsel' in cell['class'].strip():
		        sheet.write(row, col, dCell, styleCell)
                    else:
                        sheet.write(row, col, dCell)
                    col+=1
                row +=1
            print 'fff'
            wbk.save(result) # write to stdout
        response = HttpResponse(result.getvalue(), mimetype='application/octet-stream')
        response['Content-Disposition'] = 'attachment; filename=' + filename
        return response
    except Exception, e:
        print "exception",e
        return HttpResponseBadRequest("Page not available")



def fetch_resources(uri, rel):
    path = os.path.join(settings.MEDIA_ROOT, uri.replace(settings.MEDIA_URL, ""))
    return path




def fetch_resources(uri, rel):
    path = os.path.join(settings.MEDIA_ROOT, uri.replace(settings.MEDIA_URL, ""))
    return path


def underConstruction(request):
    return render_to_response('underConstruction.html', RequestContext(request)) 

def demoDocumentation(request):
    return render_to_response('demoDocumentation.html', RequestContext(request))



@login_required
def video(request):
    mainActivities = Activity.objects.filter(father_activity__isnull=True)
    mAct = {}
    try:
        for ma in mainActivities:            
            videos = LASVideo.objects.filter (activity__in= Activity.objects.filter(father_activity = ma ).values_list('id',flat=True) ).order_by('activity', 'rank')
            activities = {}
            print ma.id
            if len(videos):
                mAct[ma.id] = {'name':ma.name, 'activities':[], 'videos':[] }
                vList = []
                for v in videos:
                    video={}
                    video['id']=v.id
                    video['title']=v.title
                    video['description']=v.description
                    video['url']=v.url
                    video['position']=v.rank
                    video['activity']=v.activity.id
                    vList.append(video)
                    activities[v.activity.id] = v.activity.name
                act = []
                for key in sorted(activities):
                    act.append({'id':key, 'name': activities[key]})
                
                mAct[ma.id]['activities'] = act
                mAct[ma.id]['videos'] = vList
    except Exception, e:
        print e
        return HttpResponseBadRequest('Error in retrieving data')

    mAct_sort = []
    for key in sorted(mAct):
        mAct_sort.append(mAct[key])
    
    print mAct_sort
    return render_to_response('videoPage.html', {'mainActivities':mAct_sort}, RequestContext(request))
    





def manageUserAccount(request):
    if request.method=='GET':
        lasuser=LASUser.objects.get(username=request.user.username)
        wgList=WG.objects.filter(id__in=WG_lasuser.objects.filter(lasuser=lasuser).values_list('WG',flat=True).distinct())
        workingGroups=[]
        print wgList
        for item in wgList:
            activitiesQS=Activity.objects.filter(id__in=Activities_LASPermissions.objects.filter(laspermission__in=LASPermission.objects.filter(id__in=WG_lasuser.objects.filter(lasuser=lasuser,WG=item).values_list('laspermission',flat=True).distinct())).values_list('activity',flat=True).distinct())
            macroActivities=set()
            for act in activitiesQS:
                macroActivities.add(act.father_activity)
            wg=model_to_dict(item)
            activities=list()
            for act in activitiesQS:
                a=model_to_dict(act)
                a['father_activity']=act.father_activity
                a['laspermissions']=list()
                for perm in act.laspermissions.filter(id__in=WG_lasuser.objects.filter(WG=item,lasuser=lasuser).values_list('laspermission',flat=True).distinct()):
                    p={}
                    p['id']=perm.id
                    p['name']=perm.name
                    #tags=RelationalTag.objects.all()
                    #p['tags']=tags
                    p['selectedTags']=tags.filter(id__in=WG_lasuser_relationalTag.objects.filter(wg_lasuser__id__in=WG_lasuser.objects.filter(WG=item,lasuser=lasuser,laspermission=perm)).values_list('relationalTag',flat=True).distinct())
                    p['recipients']=User.objects.filter(id__in=WG_lasuser.objects.filter(WG=item,laspermission=perm).values_list('lasuser',flat=True).distinct())
                    wg_lasuser=WG_lasuser.objects.get(WG=item,laspermission=perm,lasuser=lasuser)
                    p['selectedRecipients']=User.objects.filter(id__in=WG_lasuser_recipient.objects.filter(wg_lasuser=wg_lasuser).values_list('recipient',flat=True).distinct())
                    try:
                        p['templateMail']=WG_lasuser_templateMail.objects.get(wg_lasuser=wg_lasuser).templateMail
                    except Exception,e:
                        p['templateMail']=''
                    a['laspermissions'].append(p)
                activities.append(a)

            wgDict['macroActivities']=macroActivities
            wgDict['activities']=activities
            workingGroups.append(wg)
        print workingGroups[1]
        return render_to_response('manageUserAccount.html',{'workingGroups':workingGroups}, RequestContext(request))
    else:
        try:
            wgList=json.loads(request.POST.get('wgList'))
            lasuser=LASUser.objects.get(username=request.user.username)
            for wgItem in wgList:
                wg=WG.objects.get(id=wgItem['id'])
                wg_lasuser=WG_lasuser.objects.filter(lasuser=lasuser,WG=wg)
                WG_lasuser_recipient.objects.filter(wg_lasuser__in=wg_lasuser).delete()
                WG_lasuser_relationalTag.objects.filter(wg_lasuser__in=wg_lasuser).delete()
                for perm in wgItem['laspermission']:
                    lasper=LASPermission.objects.get(id=perm['id'])
                    wg_lasuser=WG_lasuser.objects.get(lasuser=lasuser,WG=wg,laspermission=lasper)
                    for recipientMail in perm['selectedRecipients']:
                        user=User.objects.get(email=str(recipientMail))
                        record=WG_lasuser_recipient(wg_lasuser=wg_lasuser,recipient=user)
                        record.save()

                    for relationalTag in perm['selectedTags']:
                        print "setto",relationalTag
                        tag=RelationalTag.objects.get(name=str(relationalTag))
                        record=WG_lasuser_relationalTag(wg_lasuser=wg_lasuser,relationalTag=tag)
                        record.save()
                    try:
                        templateMail=WG_lasuser_templateMail.objects.get(wg_lasuser=wg_lasuser)
                        templateMail.templateMail=perm['templateMail']
                        templateMail.save()
                    except:
                        templateMail=WG_lasuser_templateMail(wg_lasuser=wg_lasuser,templateMail=perm['templateMail'])
                        templateMail.save()

            return_dict={'message':'ok'}
            json_response = json.dumps(return_dict)
            return HttpResponse(json_response,mimetype='application/json')
        except Exception,e:
            print 'Exception in save notification recipients',e
            return_dict={'message':'error'}
            json_response = json.dumps(return_dict)
            return HttpResponse(json_response,mimetype='application/json')
        



@csrf_exempt
def sendLASMail(request):
    import datetime
    if request.method=='POST':
        functionality=request.POST.get('functionality')
        mailData=json.loads(request.POST.get('mailDict'))
        gdb=neo4j.GraphDatabaseService(settings.GRAPH_DB_URL)
        try:
            for wgName,v in mailData.items():
                wg=WG.objects.get(name=wgName)
                try:
                    wg_lasuser=WG_lasuser.objects.get(lasuser=LASUser.objects.get(username=v['Executor'][0]),laspermission=LASPermission.objects.get(codename=functionality),WG=wg)
                    relTags=WG_lasuser_relationalTag.objects.filter(wg_lasuser=wg_lasuser)
                    relString=''
                    usersList=set()
                    itselfTag=False
                    for x in relTags:
                        tag=x.relationalTag
                        if tag.id>6:
                            relString+='has'+tag.name+'|'
                        elif tag.name=='PI':
                            usersList.add(wg.owner.username)
                        elif tag.name=='Executor':
                            itselfTag=True
                            if 'Executor' in v:
                                usersList=usersList.union(set(v['Executor']))
                        elif tag.name=='Planner':
                            if 'Planner' in v:
                                usersList=usersList.union(set(v['Planner']))
                        elif tag.name=='Assignee':
                            if 'Assignee' in v:
                                usersList=usersList.union(set(v['Assignee']))
                        elif tag.name=='Recipient':
                            if 'Recipient' in v:
                                usersList=usersList.union(set(v['Recipient']))
                    relString=relString[:-1]
                    if relString !='':
                        q=neo4j.CypherQuery(gdb,"START wg=node:node_auto_index(identifier='" + wgName + "') MATCH (user:User) where user.identifier='"+v['Executor'][0]+"' MATCH (wg)<-[]-(user)-[:"+relString+"]->(n)-[]->(wg) return n.identifier")
                        r=q.execute()
                        for x in r.data:
                            usersList.add(x[0])
                    if itselfTag==True:
                        usersList.add(User.objects.get(username=v['Executor'][0]).username)
                    else:
                        usersList.discard(User.objects.get(username=v['Executor'][0]).username)
                    print 'userslist',usersList
                    oList= list(User.objects.filter(username__in=usersList).values_list('email', flat=True))
                    subject=wg_lasuser.laspermission.report.subject
                    try:
                        addRecList = json.loads(WG_lasuser_recipient.objects.get(wg_lasuser=wg_lasuser).recipientList)
                    except:
                        addRecList=list()
                    oList.extend(addRecList)                
                    try:
                        template=WG_lasuser_templateMail.objects.get(wg_lasuser=wg_lasuser).templateMail
                    except:
                        template=''
                    if template=='':
                        template=wg_lasuser.laspermission.report.body
                    message=template
                    #message+='\n'+str(oList)
                    message=message.encode('utf-8')
                    subject=subject.encode('utf-8')
                    print 'message',message
                    try:
                        email = EmailMessage(subject,message,"",[],[],"","","",oList)
                        for key,message in v['msg'].items():
                            if key=='subject':
                                subject=subject+' '+message
                                subject=subject.encode('utf-8')
                                email.subject=subject
                            else:
                                body= "\n".join([line for line in message])
                                fileName='Report_'+str(v['Executor'][0])+'_'+str(datetime.datetime.now().strftime("%Y-%m-%d_%H:%M:%S"))
                                if len(message)>0:
                                    if key=='default':
                                        email.attach(fileName+'.txt',body,'text/plain')
                                    else:
                                        email.attach(str(key)+'_'+fileName+'.txt',body,'text/plain')
                        email.send(fail_silently=False)
                    except Exception,e:
                        print e
                        return_dict = {"message": "mailSendError"}
                        json_response = json.dumps(return_dict)
                        return HttpResponse(json_response,mimetype='application/json')
                except:
                    print 'User not in this wg! Skip :-)',wgName
            return_dict = {"message": "ok"}
            json_response = json.dumps(return_dict)
            return HttpResponse(json_response,mimetype='application/json')
        except Exception,e:
            print e
            return_dict = {"message": "mailSendGeneralError"}
            json_response = json.dumps(return_dict)
            return HttpResponse(json_response,mimetype='application/json')






#SHARING
@csrf_exempt
def shareEntities(request):
    if request.method=='POST':
        try:
            import datetime
            genidList=json.loads(request.POST.get('entitiesList'))
            username=request.POST.get('user')
            wgList=WG.objects.filter(id__in=WG_lasuser.objects.filter(lasuser=LASUser.objects.get(username=username)).values_list('WG',flat=True).distinct()).values_list('name',flat=True)
            gdb=neo4j.GraphDatabaseService(settings.GRAPH_DB_URL)
            for genid in genidList:
                for wg in wgList:
                    q=neo4j.CypherQuery(gdb,"START n=node:node_auto_index(identifier='"+str(genid)+"'), wg=node:node_auto_index(identifier='"+wg+"') MATCH wg-[r:OwnsData|SharesData]->n return r")
                    print q
                    r=q.execute()
                    if len(r.data)==0:
                        q=neo4j.CypherQuery(gdb,"START n=node:node_auto_index(identifier='"+str(genid)+"'), wg=node:node_auto_index(identifier='"+wg+"') CREATE (wg)-[r:SharesData {startDate:'"+str(datetime.datetime.now())
+"'}]->n return r")
                        q.execute()
                    else:
                        q=neo4j.CypherQuery(gdb,"match (n:Bioentity) where n.identifier='"+str(genid)+"' match (wg:WG) where wg.identifier='"+wg+"' match (n)-[r:OwnsData|SharesData]-(wg) where (exists((n)-[:OwnsData]-(wg)) or exists((n)-[:SharesData]-(wg))) and has(r.endDate) set r.endDate=null return r")
                        q.execute()

            address = LASModule.objects.get(shortname='BBM').home_url
            url = address + "/api/shareAliquots/"
            h=''
            wgListToSend=list()
            for wg in wgList:
                wgListToSend.append(wg)
            values = {'api_key' : h, 'genidList':json.dumps(genidList),'wgList':json.dumps(wgListToSend) }
            data = urllib.urlencode(values)
            try:
                u = urllib2.urlopen(url,data)
                res =  u.read()
                res=json.loads(res)
                if res['message']=='ok':
                    return_dict = {"message":"ok"}
                    json_response = json.dumps(return_dict)
                    return HttpResponse(json_response,mimetype='application/json')
                else:
                    print "valutare! errore in biob"
            except urllib2.HTTPError,e:
                print e
                return_dict = {"message":"error"}
                json_response = json.dumps(return_dict)
                return HttpResponse(json_response,mimetype='application/json')
        except Exception,e:
            print e
            return_dict = {"message":"error"}
            json_response = json.dumps(return_dict)
            return HttpResponse(json_response,mimetype='application/json')

#serve a cancellare la condivisione di un'aliquota con un wg. E' utile ad esempio nel trasferimento della banca per
#togliere ad un wg delle aliquote che si erano condivise prima.
@csrf_exempt
def DeleteShareEntities(request):
    if request.method=='POST':
        try:
            print request.POST
            import datetime
            gdb=neo4j.GraphDatabaseService(settings.GRAPH_DB_URL)
            #lista di gen a cui togliere la condivisione
            genidList=json.loads(request.POST.get('entitiesList'))
            print 'genidlist',genidList
            #utente al cui wg bisogna togliere la condivisione
            username=request.POST.get('user')
            wgList=WG.objects.filter(id__in=WG_lasuser.objects.filter(lasuser=LASUser.objects.get(username=username)).values_list('WG',flat=True).distinct()).values_list('name',flat=True)
            print 'wglist',wgList
            for genid in genidList:
                print 'genid',genid
                for wg in wgList:
                    print 'wg',wg
                    #q=neo4j.CypherQuery(gdb,"START n=node:node_auto_index(identifier='"+str(genid)+"'), wg=node:node_auto_index(identifier='"+wg+"') MATCH (wg-[r:SharesData]-n) SET r.endDate='"+str(datetime.datetime.now())+"' return r")
                    #cancello la relazione di share piuttosto che impostare la data di fine perche' altrimenti se si fa dopo un successivo share su quel campione, non avviene piu' la 
                    #condivisione perche' c'e' gia' una relazione tra quel wg e quell'aliquota
                    q=neo4j.CypherQuery(gdb,"START n=node:node_auto_index(identifier='"+str(genid)+"'), wg=node:node_auto_index(identifier='"+wg+"') MATCH (wg-[r:SharesData]-n) delete r")
                    print 'query',q
                    r=q.execute()
            return HttpResponse('ok')
        except Exception,e:
            print 'err',e
            return HttpResponse('error')

@login_required
@user_passes_test(lambda u: u.username=='lasmanager')
@transaction.commit_on_success()
def createAffiliation(request):
    if request.method=='GET':
        return render_to_response('createAffiliation.html', {'form':CreateAffiliation()},RequestContext(request))
    else:
        form = CreateAffiliation(request.POST)
      
        if form.is_valid():
            companyName=form.cleaned_data['companyName']
            department=form.cleaned_data['department']
            city=form.cleaned_data['city']
            state=form.cleaned_data['state']
            zipCode=form.cleaned_data['zipCode']
            affiliation=Affiliation(companyName=companyName,department=department,city=city,state=state,zipCode=zipCode,validated=1)
            affiliation.save()
            return render_to_response('createAffiliation.html', {'end':'end'}, RequestContext(request))
	else:
            return render_to_response('createAffiliation.html', {'form':form}, RequestContext(request))




@login_required
@transaction.commit_on_success()
def manageWorkingGroupsAdmin(request):
    if request.method=='POST':
        luser=LASUser.objects.get(username=request.user.username)
        if WG_lasuser.objects.filter(lasuser=luser,WG=WG.objects.get(name='admin')).count()==0:
            return HttpResponseRedirect(reverse("loginmanager.views.index"))
        if request.POST.get('step')=='assignActivities':
            try:
                wg=WG.objects.get(id=request.POST.get('wgID'))
                lasuser=LASUser.objects.get(id=request.POST.get('lasuserID'))
                user=User.objects.get(id=request.POST.get('lasuserID'))
                activitiesList=request.POST.getlist('activitiesList[]')
                for act in activitiesList:
                    if WG_lasuser_activities.objects.filter(WG=wg,lasuser=lasuser,activity=Activity.objects.get(id=act)).count()==0:
                        m2m=WG_lasuser_activities(WG=wg,lasuser=lasuser,activity=Activity.objects.get(id=act))
                        m2m.save()

                modulesSet=set()
                perms=dict()
                userDict=dict()
                permsList=list()
                permsOk=LASPermission.objects.filter(id__in=Activities_LASPermissions.objects.filter(activity__id__in=activitiesList).values_list('laspermission',flat=True))
                for p in permsOk:
                    modulesSet.add(p.lasmodule)
                    try:
                        wg_lasuser_perm=WG_lasuser.objects.get(WG=wg,lasuser=lasuser,laspermission=p)
                    except:
                        wg_lasuser_perm=WG_lasuser(WG=wg,lasuser=lasuser,laspermission=p)
                        wg_lasuser_perm.save()
                    if (user.has_perm("loginmanager."+p.codename)==False):
                        user.user_permissions.add(Permission.objects.get(id=p.id))
                    if not p.lasmodule.shortname in perms:
                        perms[p.lasmodule.shortname]=""
                    perms[p.lasmodule.shortname]+=p.codename+","

                userDict['username']=user.username
                userDict['first_name']=user.first_name
                userDict['last_name']=user.last_name
                userDict['email']=user.email
                userDict['permissions']=perms
                permsList.append(userDict)
                for m in modulesSet:
                    if m.name!='LASAuthServer':
                        address=m.home_url
                        url = address+"permission/setUserPermissions/"
                        t = getApiKey()
                        print "final api",url
                        values = {'wg':wg.name,'permsList[]':permsList,'api_key':t,'wgOwner':wg.owner.username}
                        data = urllib.urlencode(values,True)
                        try:
                            resp=urllib2.urlopen(url, data)
                            res1 =  resp.read()
                        except Exception, e:
                            transaction.rollback()
                            print e
                            if str(e.code)== '403':
                                print "fail api"
                                return_dict = {"message": "API error"}
                            else:
                                return_dict = {"message": "error"}
                            json_response = json.dumps(return_dict)
                            if m.shortname == 'CMM':
                                return HttpResponse(json_response,mimetype='application/json')  
                    try:
                        luser_module=LASUser_modules.objects.get(lasuser=lasuser,lasmodule=m)
                    except:
                        luser_module=LASUser_modules(lasuser=lasuser,lasmodule=m,is_superuser=0)
                        luser_module.save()
                ActivityRequest.objects.filter(WG=wg,lasuser=lasuser).delete()
                return_dict = {"message": "ok"}
                json_response = json.dumps(return_dict)
                return HttpResponse(json_response,mimetype='application/json')
            except Exception,e:
                print 'ecc',e
                return_dict = {"message": "error"}
                json_response = json.dumps(return_dict)
                return HttpResponse(json_response,mimetype='application/json')

        if request.POST.get('step')=='deleteUsers':
            try:
                modulesSet=set()
                permsList=list()
                wgID=request.POST.get('wgID')
                usersList=request.POST.getlist('usersList[]')
                wg=WG.objects.get(id=wgID)
                for u in usersList:
                    userDict={}
                    luser=LASUser.objects.get(pk=u)
                    user=User.objects.get(username=luser.username)
                    wgLasuser=WG_lasuser.objects.filter(lasuser=luser,WG=wg)
                    perms=dict()
                    for item in wgLasuser:
                        if not item.laspermission.lasmodule.shortname in perms:
                            perms[item.laspermission.lasmodule.shortname]=""
                        perms[item.laspermission.lasmodule.shortname]+=item.laspermission.codename+","
                    #API a REMOVE FROM WG
                    #RIMUOVERE wgLasuser
                        modulesSet.add(item.laspermission.lasmodule.shortname)
                        tempPerm=item.laspermission
                        item.delete()
                        if WG_lasuser.objects.filter(lasuser=luser,laspermission=tempPerm).count()==0:
                            user=User.objects.get(username=luser.username)
                            perm=Permission.objects.get(codename=tempPerm.codename)
                            user.user_permissions.remove(perm)

                    userDict['username']=user.username
                    userDict['first_name']=user.first_name
                    userDict['last_name']=user.last_name
                    userDict['email']=user.email
                    userDict['permissions']=perms
                    permsList.append(userDict)

                    for m in modulesSet:
                        lasmodule=LASModule.objects.get(shortname=m)
                        if lasmodule.name!='LASAuthServer':
                            address=lasmodule.home_url
                            url = address+"permission/removeFromWG/"
                            t = getApiKey()
                            print url
                            #print permToSend
                            values = {'wg':wg.name,'permsList[]':permsList,'api_key':t,'wgOwner':wg.owner.username}
                            data = urllib.urlencode(values,True)
                            try:
                                resp=urllib2.urlopen(url, data)
                                res1 =  resp.read()
                            except Exception, e:
                                transaction.rollback()
                                print e
                                if str(e.code)== '403':
                                    print "fail api"
                                    return_dict = {"message": "API error"}
                                else:
                                    return_dict = {"message": "error"}
                                json_response = json.dumps(return_dict)
                                return HttpResponse(json_response,mimetype='application/json')

                    WG_lasuser_activities.objects.filter(WG=wg,lasuser=luser).delete()
                return_dict = {"message": "ok"}
                json_response = json.dumps(return_dict)
                return HttpResponse(json_response,mimetype='application/json')
            except Exception,e:
                print "Fail in delete user",e
                transaction.rollback()
                return_dict = {"message": "error"}
                json_response = json.dumps(return_dict)
                return HttpResponse(json_response,mimetype='application/json')

        elif request.POST.get('step')=='updateFunctionalities':
            try:
                permsList=list()
                modulesSet=set(LASModule.objects.exclude(shortname='AMM'))
                wgID=request.POST.get('wgID')
                userID=request.POST.get('userID')
                activitiesList=request.POST.getlist('userActivities[]')
                wg=WG.objects.get(id=wgID)
                userDict={}
                perms=dict()
                luser=LASUser.objects.get(id=userID)
                user=User.objects.get(id=userID)
                WG_lasuser.objects.filter(WG=wg,lasuser=luser).delete()
                WG_lasuser_activities.objects.filter(WG=wg,lasuser=luser).delete()
                activities=Activity.objects.filter(id__in=activitiesList)
                for a in activities:
                    print a.name
                    m2m=WG_lasuser_activities(WG=wg,lasuser=luser,activity=a)
                    m2m.save()
                permsOk=LASPermission.objects.filter(id__in=Activities_LASPermissions.objects.filter(activity__in=activities).values_list('laspermission',flat=True))
                for p in permsOk:
                    try:
                        WG_lasuser.objects.get(lasuser=luser,laspermission=p)
                        user.user_permissions.remove(Permission.objects.get(id=p.id))
                    except:
                        pass
                for p in permsOk:
                    try:
                        wg_lasuser_perm=WG_lasuser.objects.get(WG=wg,lasuser=luserd,laspermission=p)
                    except:
                        wg_lasuser_perm=WG_lasuser(WG=wg,lasuser=luser,laspermission=p)
                        wg_lasuser_perm.save()
                    if (user.has_perm("loginmanager."+p.codename)==False):
                        user.user_permissions.add(Permission.objects.get(id=p.id))
                    if not p.lasmodule.shortname in perms:
                        perms[p.lasmodule.shortname]=""
                    perms[p.lasmodule.shortname]+=p.codename+","

                    if WG_lasuser.objects.filter(lasuser__id=user.id,laspermission=p).count()==0:
                        user.user_permissions.remove(Permission.objects.get(id=p.id))
                userDict['username']=user.username
                userDict['first_name']=user.first_name
                userDict['last_name']=user.last_name
                userDict['email']=user.email
                userDict['permissions']=perms
                permsList.append(userDict)
                for m in modulesSet:
                    if m.name!='LASAuthServer':
                        address=m.home_url
                        url = address+"permission/setUserPermissions/"
                        t = getApiKey()
                        print "final api",url
                        values = {'wg':wg.name,'permsList[]':permsList,'api_key':t,'wgOwner':wg.owner.username}
                        data = urllib.urlencode(values,True)
                        try:
                            resp=urllib2.urlopen(url, data)
                            res1 =  resp.read()
                        except Exception, e:
                            transaction.rollback()
                            print e
                            if str(e.code)== '403':
                                print "fail api"
                                return_dict = {"message": "API error"}
                            else:
                                return_dict = {"message": "error"}
                            json_response = json.dumps(return_dict)
                            return HttpResponse(json_response,mimetype='application/json')
                    try:
                        luser_module=LASUser_modules.objects.get(lasuser=luser,lasmodule=m)
                    except:
                        luser_module=LASUser_modules(lasuser=luser,lasmodule=m,is_superuser=0)
                        luser_module.save()
            except Exception,e:
                transaction.rollback()
                print e
                return_dict={"message":"error"}
                json_response = json.dumps(return_dict)
                return HttpResponse(json_response,mimetype='application/json')

            return_dict = {"message": "ok"}
            json_response = json.dumps(return_dict)
            return HttpResponse(json_response,mimetype='application/json')
        elif request.POST.get('step')=='inviteUsers':
            wg=WG.objects.get(id=request.POST.get('wgID'))
            try:
                print request.POST.get('email')
                luser=LASUser.objects.get(email=request.POST.get('email'))
                if WG_lasuser.objects.filter(WG=wg,lasuser=luser).count()>0:
                    return_dict = {"message": "alreadyExist"}
                    json_response = json.dumps(return_dict)
                    return HttpResponse(json_response,mimetype='application/json')
                else:
                    if LASUser_invite.objects.filter(WG=wg,lasuser=luser).count()>0:
                        return_dict = {"message": "alreadyInvited"}
                        json_response = json.dumps(return_dict)
                        return HttpResponse(json_response,mimetype='application/json')

                    for role in Role.objects.filter(id__in=request.POST.getlist('rolesList[]')):
                        temp=LASUser_invite(lasuser=luser,WG=wg,role=role)
                        temp.save()
                    subject='Join a new Working Group in LAS!'
                    message='Dear user,\nyou received an invitation to a LAS Working Group.\nPlease login at %s and check your control panel in order to inspect the request.' % settings.DOMAIN_URL
                    subject=subject.encode('utf-8')
                    message=message.encode('utf-8')
                    toList=list()
                    toList.append(luser.email)
                    try:
                        email = EmailMessage(subject,message,"",toList,[],"","","",[])
                        email.send(fail_silently=False)
                        return_dict = {"message": "ok"}
                        json_response = json.dumps(return_dict)
                        return HttpResponse(json_response,mimetype='application/json')
                    except Exception,e:
                        transaction.rollback()
                        return_dict = {"message": "mailSendError"}
                        json_response = json.dumps(return_dict)
                        return HttpResponse(json_response,mimetype='application/json')

            except Exception,e:
                print "user not in LAS"
                roleString=''
                for role in Role.objects.filter(id__in=request.POST.getlist('rolesList[]')):
                    if roleString!='':
                        roleString+=', '
                    roleString+=role.name
                subject='Join LAS!'
                message='Dear user,\nyou received an invitation to join a Working Group in the LAS platform.\n\nRequest report:\nPrincipal Investigator: '+wg.owner.first_name+' '+wg.owner.last_name +'.\nRole(s): '+roleString+'\n\nPlease register at %s and select your Principal Investigator and role(s).' % settings.DOMAIN_URL
                subject=subject.encode('utf-8')
                message=message.encode('utf-8')
                toList=list()
                toList.append(request.POST.get('email'))
                try:
                    email = EmailMessage(subject,message,"",toList,[],"","","",[])
                    email.send(fail_silently=False)
                    return_dict = {"message": "ok"}
                    json_response = json.dumps(return_dict)
                except:
                    transaction.rollback()
                    return_dict = {"message": "mailSendError"}
                    json_response = json.dumps(return_dict)
                    return HttpResponse(json_response,mimetype='application/json')
                return HttpResponse(json_response,mimetype='application/json')

    else:
        luser=LASUser.objects.get(username=request.user.username)
        if WG_lasuser.objects.filter(lasuser=luser,WG=WG.objects.get(name='admin')).count()==0:
            return HttpResponseRedirect(reverse("loginmanager.views.index"))
        workingGroups= WG.objects.all()
        wgList=list()
        userPermList=list()
        for w in workingGroups:
            wg={}
            wg['id']=w.id
            wg['name']=w.name
            wg['usersList']=LASUser.objects.filter(id__in=WG_lasuser_activities.objects.filter(WG=w).values_list('lasuser',flat=True))
            wgList.append(wg)
            wg['requests']=ActivityRequest.objects.filter(WG=w)
        father_activities=Activity.objects.filter(father_activity__isnull=True)
        lasuser_activities=Activity.objects.filter(id__in=WG_lasuser_activities.objects.filter(lasuser=luser).values_list('activity',flat=True))
        pi_father_activities=Activity.objects.filter(id__in=lasuser_activities.values_list('father_activity',flat=True).distinct()).values_list('name',flat=True)
        supervisorList=set()
        supervisorList.add(luser)
        for wg in workingGroups:
            supervisorList.add(wg.owner)
        supervisorList=list(supervisorList)
        tempReg=LASUserTempRegSupervisors.objects.filter(supervisor__in=supervisorList)

        return render_to_response('manageWorkingGroupsAdmin.html',{'workingGroups':wgList,'pendingRegistrations':tempReg,'piActivities':lasuser_activities,'piFatherAct':pi_father_activities,'rolesList':Role.objects.all(),'affiliationsList':Affiliation.objects.filter(id__in=LASUser_affiliation.objects.filter(lasuser=luser).values_list('affiliation',flat=True))},RequestContext(request))




@login_required
def manageUserWorkingGroupAdmin(request,wgID,uID):
    try:
        try:
            wg=WG.objects.get(id=wgID)
        except:
            raise Exception('Not Allowed')
        owner=wg.owner
        luser=owner
        pi_activities=Activity.objects.exclude(father_activity__isnull=True)
        pi_father_activities=Activity.objects.filter(id__in=pi_activities.values_list('father_activity',flat=True).distinct()).values_list('name',flat=True)
        current_activities=Activity.objects.filter(id__in=WG_lasuser_activities.objects.filter(WG=wg,lasuser=LASUser.objects.get(id=uID)).values_list('activity',flat=True))
        current_father_activities=Activity.objects.filter(id__in=current_activities.values_list('father_activity',flat=True).distinct())
        userDict=dict()
        for act in current_activities:
            if act.father_activity.name not in userDict:
                userDict[act.father_activity.name]=list()
            actDict=dict()
            actDict['name']=act.name
            actDict['id']=act.id
            actDict['found']=1
            userDict[act.father_activity.name].append(actDict)
        for act in set(pi_activities).difference(set(current_activities)):
            if act.father_activity.name not in userDict:
                userDict[act.father_activity.name]=list()
            actDict=dict()
            actDict['name']=act.name
            actDict['id']=act.id
            actDict['found']=0
            userDict[act.father_activity.name].append(actDict)
            print act.name
        return render_to_response('manageUserWG.html',{'lasuser':LASUser.objects.get(id=uID),'wg':wg,'userDict':userDict},RequestContext(request))
    except Exception,e:
        print e
        return HttpResponseRedirect(reverse("loginmanager.views.index"))


def privacyView(request):
    return render_to_response('privacy.html',RequestContext(request))


def helpdesk(request):
    return redirect(settings.HELPDESK)
