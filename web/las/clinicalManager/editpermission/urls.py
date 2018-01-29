from django.conf.urls import patterns, include, url

urlpatterns = patterns('editpermission.views',
    (r'^editPermission/', 'editPermission'),
    (r'^editModules/', 'editModules'),
    #(r'^createWG/', 'createWG'),
    (r'^addToWG/', 'addToWG'),
    (r'^removeFromWG/', 'removeFromWG'),
    (r'^setUserPermissions/', 'setUserPermissions'),
)
