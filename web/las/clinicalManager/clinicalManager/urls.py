from django.conf.urls import patterns, include, url
from django.contrib import admin
from clinicalManager import views


urlpatterns = patterns('',
    # Clinical Home
    url(r'^$', views.start_redirect),
    url(r'^home/$', views.index),


    # COREs
    url(r'^corePatient/', include('corePatient.urls')),
    url(r'^coreProject/', include('coreProject.urls')),
    url(r'^coreInstitution/', include('coreInstitution.urls')),
    url(r'^coreOncoPath/', include('coreOncoPath.urls')),

    #APPs
    url(r'^appEnrollment/', include('appEnrollment.urls')),
    url(r'^appPathologyManagement/', include('appPathologyManagement.urls')),


    #Admin
    # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),

    #Other
    url(r'^permission/', include('editpermission.urls')),
    #LASAuth
    url(r'^auth/', include('LASAuth.urls')),
    url(r'^error/$',views.error),
    # APIs docs
    #url(r'^docs/', include('rest_framework_swagger.urls')),

    #url(r'^docs/', include('rest_framework_swagger.urls'))
)
