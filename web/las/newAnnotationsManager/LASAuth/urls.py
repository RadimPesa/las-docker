from django.conf.urls.defaults import *
from django.views.generic import DetailView, ListView

urlpatterns = patterns('LASAuth.views',
    (r'^startlogin/$', 'login_begin'),
    (r'^completelogin/$', 'login_complete'),
    (r'^remotelogout/$', 'remote_logout'),
)

