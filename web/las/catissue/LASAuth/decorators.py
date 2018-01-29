from django.http import HttpResponseRedirect
from django.contrib import auth
from catissue.LASAuth.models import LASAuthSession

def laslogin_required(view_func):
    def decorator(request, *args, **kwargs):
        try:
            s = LASAuthSession.objects.get(django_session_key=request.session.session_key)
            session_open = s.session_open
        except:
            session_open = False
        if not session_open:
            auth.logout(request)
            for sesskey in request.session.keys():
                del request.session[sesskey]
        return view_func(request, *args, **kwargs)
    return decorator
