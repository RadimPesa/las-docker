from django.conf.urls.defaults import patterns, include, url
import settings

# Uncomment the next two lines to enable the admin:
from django.contrib import admin

admin.autodiscover()



urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'beaming.views.home', name='home'),
    # url(r'^beaming/', include('beaming.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),

    (r'^$', 'biopsy.views.start_redirect'),

    (r'^admin/', include(admin.site.urls)),
    
    #home
    (r'^home/$', "biopsy.views.home"),
    
    (r'^logout', 'biopsy.views.logout_view'),
    
    (r'^error/$', 'biopsy.views.error'),

    # request

    (r'^pending_request/$', "biopsy.views.pending_request"),

    (r'^new_request/(?P<request_id>\d+)/$', "biopsy.views.upload_request"),

    (r'^new_request/$', "biopsy.views.confirm_request"),

    (r'^request/$', "biopsy.views.create_request"),

    # procedure

    (r'^select_request/$', "biopsy.views.select_request"),  
      
    (r'^validate_samples/$', "biopsy.views.validate_samples"), 

    (r'^validated_request/$', "biopsy.views.validated_request"),

    # experiment

    (r'^select_validated_session/$', "biopsy.views.select_validated_session"),  

    (r'^define_experiment/$', "biopsy.views.define_experiment"),  

    (r'^select_experiment/$', "biopsy.views.select_experiment"),  

    (r'^layout_experiment/$', "biopsy.views.layoutExperiment"),  
    
    # measures collection
    
    (r'^read_measures/$', "biopsy.views.read_measures"), 

    (r'^save_measures/$', "biopsy.views.save_measures"),  
        
    (r'^measurement_event/$', "biopsy.views.measure_event"), 

    # retrieve results
    
    (r'^filter_results/(?P<filter_id>\d+)/$', "biopsy.views.filter_results"), 

    (r'^view_results/$', "biopsy.views.view_results"), 

    # APIs
    (r'^api.', include('api.urls')),
    
    # LASAuth
     
    (r'^auth/', include('LASAuth.urls')),   

    (r'forbidden/', 'django.views.defaults.permission_denied'),

    (r'permission/', include('editpermission.urls')),

)

if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^biopsy_media/(?P<path>.*)$', 'django.views.static.serve',
         {'document_root': settings.MEDIA_ROOT}),
    )