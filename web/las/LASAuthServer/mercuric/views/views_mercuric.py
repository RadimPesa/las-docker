from __init__ import *

RETURN_TO_FIELD_NAME = 'return_to'
SESSION_KEY_FIELD_NAME = 'session_key'
APP_FIELD_NAME = 'appid'
RETURN_STATUS_FIELD_NAME = 'status'
USER_FIELD_NAME = 'uid'
HMAC_FIELD_NAME = 'hmac'
ANSWER_YES = 'yes'
ANSWER_NO = 'no'

def MercuricLogin(request):
    from django.contrib.sessions.models import Session
    import datetime
    dirty_sessions = Session.objects.filter(expire_date__lte = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
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


    if request.method == 'POST':
        if 'username' in request.POST and 'password' in request.POST:
            #from login form
            form = LoginForm(request.POST)
            if form.is_valid():
                username = request.POST['username']
                password = request.POST['password']
                
                wg = WG.objects.filter(owner=LASUser.objects.get(username='mercuric'))
                wg= wg | WG.objects.filter(name='admin')
                luser=LASUser.objects.get(username=username)
                wglasuser = WG_lasuser.objects.filter(WG__in=wg,lasuser=luser)
                if wglasuser.count():
                    user = auth.authenticate(username=username, password=password)
                else:
                    user = None
                if user is not None and user.is_active:
                    auth.login(request, user)
                    import sys
                    if 'remote_request' in request.session:
                        #we're on this page as a result of a redirect
                        #redirect back to application requesting authentication
                        #ans = buildAuthResponse(request.session[APP_FIELD_NAME], request.session[SESSION_KEY_FIELD_NAME], user)
                        ans = buildAuthResponse(request.session[APP_FIELD_NAME], request.session[SESSION_KEY_FIELD_NAME], user, request.session.session_key)
                        h = buildHMAC(request.session[APP_FIELD_NAME], ans, user.username, request.session[SESSION_KEY_FIELD_NAME])
                        return render_to_response('continueloginmercuric.html', {'dest': request.session[RETURN_TO_FIELD_NAME], 'status': ans, 'session_key': request.session[SESSION_KEY_FIELD_NAME], 'uid': user.username, 'hmac': h})
                    else:
                        #no redirect
                        #return list of modules available to user
                        return HttpResponseRedirect(reverse('mercuric.views.indexMercuric'))
                else:
                    return render_to_response('loginMercuric.html', {'err_message': "You are not registered to Mercuric portal!"})
            else:
                return render_to_response('loginMercuric.html', {'err_message': "Invalid input!"})
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
                return render_to_response('loginMercuric.html')
            else:
                #user is already authenticated on LASAuthServer
                if verifyHMAC(request.POST[HMAC_FIELD_NAME], request.POST[APP_FIELD_NAME], request.POST[RETURN_TO_FIELD_NAME], request.POST[SESSION_KEY_FIELD_NAME]):
                    #hmac is valid
                    #ans = buildAuthResponse(request.POST[APP_FIELD_NAME], request.POST[SESSION_KEY_FIELD_NAME], request.user)
                    ans = buildAuthResponse(request.POST[APP_FIELD_NAME], request.POST[SESSION_KEY_FIELD_NAME], request.user, request.session.session_key)
                    h = buildHMAC(request.POST[APP_FIELD_NAME], ans, request.user.username, request.POST[SESSION_KEY_FIELD_NAME])
                    return render_to_response('continueloginmercuric.html', {'dest': request.POST[RETURN_TO_FIELD_NAME], 'status': ans, 'session_key': request.POST[SESSION_KEY_FIELD_NAME], 'uid': request.user.username, 'hmac': h, 'permessi' :True})
                else:
                    #hmac is not valid, just return list of modules available for user
                    #TODO: warn about possible request forgery?
                    return HttpResponseRedirect(reverse('mercuric.views.indexMercuric'))
        else:
            #method is POST and not from redirect and not from login form
            if not request.user.is_authenticated():
                #user is not yet authenticated on LASAuthServer
                #return login form
                return render_to_response('loginMercuric.html')
            else:
                #user is already authenticated on LASAuthServer
                #return list of modules available for user
                return HttpResponseRedirect(reverse('mercuric.views.indexMercuric'))
    else:
        #method is GET
        if not request.user.is_authenticated():
            #user is not yet authenticated on LASAuthServer
            #return login form
            return render_to_response('loginMercuric.html')
        else:
            #user is already authenticated on LASAuthServer
            #return list of modules available for user
            #return render_to_response('indexMercuric.html', {'mercuricurl': '/biobank/'}, RequestContext(request)) 
            return HttpResponseRedirect(reverse('mercuric.views.indexMercuric'))


#@login_required
def indexMercuric(request):
    print 'indexMercuric'
    try:
        user = request.user
        luser = LASUser.objects.get(pk=user.id)

    except Exception,e:
        print e
        return HttpResponseRedirect(reverse("mercuric.views.logout"))
    name = user.username
    
    #print RequestContext(request)
    urlmodule = LASModule.objects.get(shortname='BBM').home_url + 'mercuric/collection/'
    print urlmodule

    return render_to_response('indexMercuric.html', {'mercuricurl': urlmodule}, RequestContext(request))

def logout(request):
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
    
    for sesskey in request.session.keys():
        del request.session[sesskey]

    auth.logout(request)
      
    
    #for sesskey in request.session.keys():
    #    del request.session[sesskey]
    
    return HttpResponseRedirect(reverse("mercuric.views.MercuricLogin"))
