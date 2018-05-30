from django.conf.urls.defaults import *
from LASAuthServer import settings


# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()


urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'loginman.views.home', name='home'),
    # url(r'^loginman/', include('loginman.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),    
    url(r'^api/', include('api.urls')),
    url(r'^logout/$', "loginmanager.views.logout"),
    url(r'^accounts/requestModules/$', 'loginmanager.views.requestModules'),
    url(r'^accounts/moduleRequestReport/$', 'loginmanager.views.moduleRequestReport'),
    url(r'^accounts/permissionRequestReport/$', 'loginmanager.views.permissionRequestReport'),
    url(r'^accounts/requestPermissions/$', 'loginmanager.views.requestPermissions'),
    url(r'^accounts/currentPermissions/$', 'loginmanager.views.currentPermissions'),    
    url(r'^accounts/$', 'loginmanager.views.manageAccount'),
    url(r'^userAccount/$', 'loginmanager.views.manageUserAccount'),
    


    url('^accounts/', include('registration.urls')),
    url(r'^laslogin/$', 'loginmanager.views.LASLogin'),
    url(r'^index/$', 'loginmanager.views.index'),
    url(r'^helpdesk/$', 'loginmanager.views.helpdesk'),
    

    
    url(r'^saveUserPermissions/$', 'loginmanager.views.saveUserPermissions'),        
    url(r'^saveUserModules/$', 'loginmanager.views.saveUserModules'),    
    url(r'^manageUsersList/$', 'loginmanager.views.manageUsersList'),    

    url(r'^syncPermissions/$', 'loginmanager.views.syncPermissions'),
    url(r'^forbidden/$', "django.views.defaults.permission_denied"),
    
    url(r'^manageAdmin/users/(?P<userID>\d{1,10})/editModules/$', 'loginmanager.views.editUserModules'),
    url(r'^manageAdmin/users/(?P<userID>\d{1,10})/editPermissions/$', 'loginmanager.views.editUserPermissions'),
    url(r'^manageAdmin/users/(?P<userID>\d{1,10})/$', 'loginmanager.views.editUser'),
    url(r'^manageAdmin/users/manageModulesRequest/$', 'loginmanager.views.manageModulesRequest'),
    url(r'^manageAdmin/users/managePermissionsRequest/$', 'loginmanager.views.managePermissionsRequest'),
    url(r'^manageAdmin/users/$', 'loginmanager.views.manageUsersList'),
    url(r'^manageAdmin/registrations/$', 'loginmanager.views.manageRegistrations'),
    url(r'^manageAdmin/createAffiliation$', 'loginmanager.views.createAffiliation'),
    url(r'^manageAdmin/sendMail$', 'loginmanager.views.sendMail'),
    url(r'^manageAdmin/$', 'loginmanager.views.manageAdmin'),
    url(r'^generate_report/$', 'loginmanager.views.generate_report'),
    
    url(r'^manageWorkingGroupsAdmin/$', 'loginmanager.views.manageWorkingGroupsAdmin'),
    url(r'^manageWorkingGroups/$', 'loginmanager.views.manageWorkingGroups'),
    url(r'^manageWorkingGroups/registration/(?P<recordID>\d{1,10})/$', 'loginmanager.views.managePiRegistration'),
    url(r'^evaluateUserRegistration/$', 'loginmanager.views.evaluateUserRegistration', name="evaluateUserRegistration"),
    url(r'^manageRegistrationsManager/$', 'loginmanager.views.manageRegistrationsManager'),
    url(r'^manageWorkingGroupsAdmin/(?P<wgID>\d{1,10})/(?P<uID>\d{1,10})/$', 'loginmanager.views.manageUserWorkingGroupAdmin'),
    url(r'^manageWorkingGroups/(?P<wgID>\d{1,10})/(?P<uID>\d{1,10})/$', 'loginmanager.views.manageUserWorkingGroup'),


    url(r'^video/$', 'loginmanager.views.video'),
    
    url(r'^underConstruction/$','loginmanager.views.underConstruction'),
    url(r'demoDocumentation/$', 'loginmanager.views.demoDocumentation'),


    url(r'sendLASMail/$', 'loginmanager.views.sendLASMail'),
    url(r'^shareEntities/$', 'loginmanager.views.shareEntities'),
    url(r'^deleteShareEntities/$', 'loginmanager.views.DeleteShareEntities'),

    url(r'^privacy/$', 'loginmanager.views.privacyView'),


    url(r'^mercuric/', include('mercuric.urls')),

    url(r'^captcha/', include('captcha.urls')),

    url(r'^loginas/', include('loginas.urls')),

)


if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^lasauth_media/(?P<path>.*)$', 'django.views.static.serve',  
         {'document_root':     settings.MEDIA_ROOT}),
    )
    
    
   
