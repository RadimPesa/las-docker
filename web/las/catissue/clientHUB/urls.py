from django.conf.urls.defaults import *
from django.views.generic import DetailView, ListView

urlpatterns = patterns('clientHUB.views',
    (r'^getAndLock/$', 'getAndLock'),
    (r'^saveAndFinalize/$', 'saveAndFinalize'),
    (r'^checkBarcode/$', 'checkBarcode'),
    #(r'^completelogin/$', 'login_complete'),
    #(r'^remotelogout/$', 'remote_logout'),
)
