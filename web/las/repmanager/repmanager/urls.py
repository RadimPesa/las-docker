from django.conf.urls import patterns, include, url
import settings

# Uncomment the next two lines to enable the admin:
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'repmanager.views.home', name='home'),
    # url(r'^repmanager/', include('repmanager.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    (r'^$', 'datamanager.views.start_redirect'),

    (r'^admin/', include(admin.site.urls)),
    
   
    #home
    (r'^home/$', "datamanager.views.home"),
    
    (r'^logout', 'datamanager.views.logout_view'),
    
    (r'^error/$', 'datamanager.views.error'),

    # request

    (r'^get_file/(\w+)$', "datamanager.views.retrieveFile"),

    # APIs
    (r'^api.', include('api.urls')),
    
    # LASAuth
     
    (r'^auth/', include('LASAuth.urls')),   

    (r'forbidden/', 'django.views.defaults.permission_denied'),

    (r'permission/', include('editpermission.urls')),

)

if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^datamanager_media/(?P<path>.*)$', 'django.views.static.serve',
         {'document_root': settings.MEDIA_ROOT}),
    )
