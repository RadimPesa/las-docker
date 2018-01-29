from django.conf.urls.defaults import patterns, include, url
import settings

# Uncomment the next two lines to enable the admin:
from django.contrib import admin

admin.autodiscover()



urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'fingerprinting.views.home', name='home'),
    # url(r'^fingerprinting/', include('fingerprinting.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),

    (r'^$', 'profiling.views.start_redirect'),
    (r'^admin/', include(admin.site.urls)),
    #home
    (r'^home/$', "profiling.views.home"),
    (r'^logout', 'profiling.views.logout_view'),
    (r'^error/$', 'profiling.views.error'),
    # request
    (r'^pending_request/$', "profiling.views.pending_request"),
    (r'^new_request/(?P<request_id>\d+)/$', "profiling.views.upload_request"),
    (r'^new_request/$', "profiling.views.confirm_request"),
    (r'^request/$', "profiling.views.create_request"),
    # procedure
    (r'^select_request/$', "profiling.views.select_request"),  
    (r'^validate_samples/$', "profiling.views.validate_samples"), 
    (r'^validated_request/$', "profiling.views.validated_request"),
    # experiment
    (r'^select_validated_session/$', "profiling.views.select_validated_session"),  
    (r'^define_experiment/$', "profiling.views.define_experiment"),  
    (r'^layout_experiment/$', "profiling.views.layoutExperiment"),  

    # measures collection (raw data)
    (r'^select_experiment/$', "profiling.views.select_experiment"),  
    (r'^upload_results/$', "profiling.views.upload_results"), 
    # measures collection (analysis data)
    (r'^select_analysis/$', "profiling.views.select_analysis"),
    (r'^read_measures/$', "profiling.views.read_measures"), 
    (r'^measurement_event/$', "profiling.views.measure_event"),  
    (r'^experiment_event/$', "profiling.views.experiment_event"),   
    
    # configuration
    (r'^assay/$', "profiling.views.defineAssay"),
    # retrieve results
    (r'^filter_results/(?P<filter_id>\d+)/$', "profiling.views.filter_results"), 
    (r'^view_results/$', "profiling.views.view_results"), 
    # APIs
    (r'^api.', include('api.urls')),
    # LASAuth
    (r'^auth/', include('LASAuth.urls')),   
    (r'forbidden/', 'django.views.defaults.permission_denied'),
    (r'permission/', include('editpermission.urls')),

)

if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^profiling_media/(?P<path>.*)$', 'django.views.static.serve',
         {'document_root': settings.MEDIA_ROOT}),
    )