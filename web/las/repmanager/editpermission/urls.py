from django.conf.urls.defaults import *
from django.views.generic import DetailView, ListView

urlpatterns = patterns('editpermission.views',
    (r'^editPermission/', 'editPermission'),
    (r'^editModules/', 'editModules'),
    #(r'^createWG/', 'createWG'),
    (r'^addToWG/', 'addToWG'),
    (r'^removeFromWG/', 'removeFromWG'),
    (r'^setUserPermissions/', 'setUserPermissions'),
)

