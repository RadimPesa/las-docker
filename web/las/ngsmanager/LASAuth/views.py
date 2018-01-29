from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
import django.contrib.auth as auth
from django.contrib.sessions.models import Session
from LASAuth.models import LASAuthSession
from LASAuth.exceptions import *
from datetime import timedelta, datetime
import urllib
import hmac
import hashlib
from NGSManager import settings
from django.shortcuts import render_to_response
try:
    from django.views.decorators.csrf import csrf_exempt
except ImportError:
    from django.contrib.csrf.middleware import csrf_exempt
from django.views.decorators.csrf import ensure_csrf_cookie

MAX_SESSION_AGE = 60
RETURN_TO_FIELD_NAME = 'return_to'
SESSION_KEY_FIELD_NAME = 'session_key'
APP_FIELD_NAME = 'appid'
HMAC_FIELD_NAME = 'hmac'
RETURN_STATUS_FIELD_NAME = 'status'
USER_FIELD_NAME = 'uid'

@csrf_exempt
def remote_logout(request):
    if request.method == 'POST' and SESSION_KEY_FIELD_NAME in request.POST and HMAC_FIELD_NAME in request.POST:
        session_key = request.POST[SESSION_KEY_FIELD_NAME]
        h = hmac.new(settings.AUTH_SECRET_KEY, settings.AUTH_SECRET_KEY + settings.THIS_APP_SHORTNAME + session_key, hashlib.sha256).hexdigest()
        print request.POST[HMAC_FIELD_NAME]
        print request.POST[SESSION_KEY_FIELD_NAME]
        if h == request.POST[HMAC_FIELD_NAME]:
            try:
                s = LASAuthSession.objects.get(pk=session_key)
                s.session_open = False
                s.save()
                return HttpResponse('ok')
            except:
                return HttpResponse('already logged out')
        return HttpResponse('logout failed3')
    else:
        return HttpResponse('This page should never be requested by your browser.')



def login_begin(request):
    if 'next' in request.GET:
        next_url = request.GET['next']
    else:
        next_url = ''
    return_url = request.build_absolute_uri(reverse('LASAuth.views.login_complete')).replace('http://', 'https://' if settings.LAS_AUTH_USE_HTTPS else 'http://')
    print "return url is"
    print return_url
    app_name = settings.THIS_APP_SHORTNAME
    login_expire_date = datetime.now() + timedelta(seconds=MAX_SESSION_AGE)
    s = LASAuthSession(next_url=next_url, login_expire_date=login_expire_date, session_open=False)
    s.generateSessionKey()
    s.save()
    h = hmac.new(settings.AUTH_SECRET_KEY, settings.AUTH_SECRET_KEY + app_name + return_url + s.session_key, hashlib.sha256).hexdigest()
    url = settings.LAS_AUTH_SERVER_URL
    return render_to_response('initlogin.html', {'dest': url,
     RETURN_TO_FIELD_NAME: return_url,
     SESSION_KEY_FIELD_NAME: s.session_key,
     APP_FIELD_NAME: app_name,
     HMAC_FIELD_NAME: h})



@csrf_exempt
@ensure_csrf_cookie
def login_complete(request):
    print "method is"
    print request.method
    if request.method == 'POST' and RETURN_STATUS_FIELD_NAME in request.POST and SESSION_KEY_FIELD_NAME in request.POST and USER_FIELD_NAME in request.POST and HMAC_FIELD_NAME in request.POST:
        try:
            u = auth.authenticate(session_key=request.POST[SESSION_KEY_FIELD_NAME], hmac=request.POST[HMAC_FIELD_NAME], ans=request.POST[RETURN_STATUS_FIELD_NAME], uid=request.POST[USER_FIELD_NAME])
        except AuthenticationSessionExpired:
            return HttpResponse('Session expired.')
        except HMACVerificationFailed:
            return HttpResponse('An invalid response was received from the authentication server. Please log in again or contact your administrator.')
        except AuthenticationDenied:
            return HttpResponse('You do not appear to have permission to access this module. Please contact your administrator to obtain the required credentials.')
        if u is not None and u.is_active:
            auth.login(request, u)
            s = LASAuthSession.objects.get(pk=request.POST[SESSION_KEY_FIELD_NAME])
            request.session.save()
            s.django_session_key = Session.objects.get(pk=request.session.session_key)
            s.session_open = True
            s.save()
            print "next_url"
            print s.next_url
            return HttpResponseRedirect(s.next_url)
        else:
            return HttpResponse('User not found.')
    else:
        return HttpResponse('This page should never be requested by your browser.')


