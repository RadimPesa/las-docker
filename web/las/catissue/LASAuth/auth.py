from django.contrib.auth.models import User
from django.utils import timezone
from catissue.LASAuth.models import LASAuthSession
from catissue.LASAuth.exceptions import *
import hmac
import hashlib

from django.conf import settings

ANSWER_YES = 'yes'

class LASAuthBackend:

    def _isValidSessionKey(self, sessionKey):
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
        #if ans == ANSWER_YES and self._isValidSessionKey(session_key) and self._verifyHMAC(hmac, ans, uid, session_key):
        #answer is yes and session key is valid and response has not been tampered with
        if ans != ANSWER_YES:
            raise AuthenticationDenied()
        if not self._isValidSessionKey(session_key):
            raise AuthenticationSessionExpired()
        if not self._verifyHMAC(hmac, ans, uid, session_key):
            raise HMACVerificationFailed()
        try:
            u = User.objects.get(username=uid)
            return u
        except:
            return None
