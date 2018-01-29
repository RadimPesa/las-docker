from django.conf.urls.defaults import patterns, include, url
import settings

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'analysismanager.views.home', name='home'),
    # url(r'^analysismanager/', include('analysismanager.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),

    (r'^$', 'mining.views.start_redirect'),

    (r'^admin/', include(admin.site.urls)),
    
   
    #home
    (r'^home/$', "mining.views.home"),
    
    (r'^logout', 'mining.views.logout_view'),
    
    (r'^error/$', 'mining.views.error'),

    (r'^writeformulas', 'mining.views.writeformulas'),

    (r'^randomize', 'mining.views.randomize'),
    
    # APIs
    (r'^api.', include('api.urls')),

    # LASAuth
     
    (r'^auth/', include('LASAuth.urls')),   

    (r'forbidden/', 'django.views.defaults.permission_denied'),

    (r'permission/', include('editpermission.urls')),
)

if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^mining_media/(?P<path>.*)$', 'django.views.static.serve',
         {'document_root': settings.MEDIA_ROOT}),
    )