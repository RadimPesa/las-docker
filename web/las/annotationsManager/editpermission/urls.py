from django.conf.urls.defaults import *
from django.views.generic import DetailView, ListView

urlpatterns = patterns('editpermission.views',
    (r'^editPermission/', 'editPermission'),
    (r'^editModules/', 'editModules'),
)
