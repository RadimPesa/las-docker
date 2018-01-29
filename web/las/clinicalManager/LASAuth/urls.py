from django.conf.urls import patterns, url, include
from django.views.generic import DetailView, ListView

urlpatterns = patterns('LASAuth.views',
    (r'^startlogin/$', 'login_begin'),
    (r'^completelogin/$', 'login_complete'),
    (r'^remotelogout/$', 'remote_logout'),
)
