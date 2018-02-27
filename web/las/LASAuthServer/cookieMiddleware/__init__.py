from datetime import timedelta
from django.conf import settings
from django.utils import timezone


EXPIRE_THRESHOLD = 30
class ExtendUserSession(object):
    def process_request(self, request):
        if request.user.is_authenticated():
            now = timezone.now()
            if request.session.get_expiry_date() > now:
                request.session.set_expiry(now + timedelta(seconds=settings.SESSION_COOKIE_AGE))
