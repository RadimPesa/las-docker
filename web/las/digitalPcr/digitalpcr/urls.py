from django.conf.urls.defaults import patterns, include, url
import settings

# Uncomment the next two lines to enable the admin:
from django.contrib import admin

admin.autodiscover()



urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'digitalpcr.views.home', name='home'),
    # url(r'^digitalpcr/', include('digitalpcr.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),

    (r'^$', 'dpcr.views.start_redirect'),

    (r'^admin/', include(admin.site.urls)),
    
    #home
    (r'^home/$', "dpcr.views.home"),
    
    (r'^logout', 'dpcr.views.logout_view'),
    
    (r'^error/$', 'dpcr.views.error'),

    # request

    (r'^pending_request/$', "dpcr.views.pending_request"),

    (r'^new_request/(?P<request_id>\d+)/$', "dpcr.views.upload_request"),

    (r'^new_request/$', "dpcr.views.confirm_request"),

    (r'^request/$', "dpcr.views.create_request"),

    # procedure

    (r'^select_request/$', "dpcr.views.select_request"),  
      
    (r'^validate_samples/$', "dpcr.views.validate_samples"), 

    (r'^validated_request/$', "dpcr.views.validated_request"),

    # experiment

    (r'^select_validated_session/$', "dpcr.views.select_validated_session"),  

    (r'^define_experiment/$', "dpcr.views.define_experiment"),  

    (r'^select_experiment/$', "dpcr.views.select_experiment"),  

    (r'^layout_experiment/$', "dpcr.views.layoutExperiment"),  
    
    # measures collection
    
    (r'^read_measures/$', "dpcr.views.read_measures"), 

    (r'^save_measures/$', "dpcr.views.save_measures"),  
        
    (r'^measurement_event/$', "dpcr.views.measure_event"), 

    # retrieve results
    
    (r'^filter_results/(?P<filter_id>\d+)/$', "dpcr.views.filter_results"), 

    (r'^view_results/$', "dpcr.views.view_results"), 

    # configuration
    
    (r'^assay/$', "dpcr.views.defineAssay"),

    # APIs
    (r'^api.', include('api.urls')),
    
    # LASAuth
     
    (r'^auth/', include('LASAuth.urls')),   

    (r'forbidden/', 'django.views.defaults.permission_denied'),

    (r'permission/', include('editpermission.urls')),

)

if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^dpcr_media/(?P<path>.*)$', 'django.views.static.serve',
         {'document_root': settings.MEDIA_ROOT}),
    )