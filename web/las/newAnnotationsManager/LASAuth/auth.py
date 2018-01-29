from django.contrib.auth.models import User
from django.utils import timezone
from LASAuth.models import LASAuthSession
from LASAuth.exceptions import *
import hmac
import hashlib

from django.conf import settings

ANSWER_YES = 'yes'

class LASAuthBackend:

    def _isValidSessionKey(self, sessionKey):
        print "_isValidSessionKey"
        try:
            s = LASAuthSession.objects.get(pk=sessionKey)
        except:
            print "session not found"
            return False
        if s.login_expire_date >= timezone.now():
            print "session valid"
            return True
        else:
            print "session expired"
            return False

    def _verifyHMAC(self, rcvdHMAC, ans, uid, sessionKey):
        print "_verifyHMAC"
        h = hmac.new(settings.AUTH_SECRET_KEY, settings.AUTH_SECRET_KEY + settings.THIS_APP_SHORTNAME + ans + uid + sessionKey, hashlib.sha256).hexdigest()
        if rcvdHMAC == h:
            print "hmac verification succeeded"
            return True
        else:
            print "hmac verification failed"
            return False

    def get_user(self, uid):
        try:
            return User.objects.get(pk=uid)
        except User.DoesNotExist:
            return None

    def authenticate(self, session_key, hmac, ans, uid):
        print "using LASAuthBackend"
        print "uid = ", uid
        #if ans == ANSWER_YES and self._isValidSessionKey(session_key) and self._verifyHMAC(hmac, ans, uid, session_key):
        #answer is yes and session key is valid and response has not been tampered with
        if ans != ANSWER_YES:
            print "answer not yes"
            raise AuthenticationDenied()
        if not self._isValidSessionKey(session_key):
            print "session invalid"
            raise AuthenticationSessionExpired()
        if not self._verifyHMAC(hmac, ans, uid, session_key):
            print "hmac verification failed"
            raise HMACVerificationFailed()
        try:
            u = User.objects.get(username=uid)
            print u
            return u
        except Exception as e:
            print str(e)
            return None
