from django.conf.urls.defaults import patterns, include, url
import settings
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'beaming.views.home', name='home'),
    # url(r'^beaming/', include('beaming.foo.urls')),
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),
    (r'^$', 'rtpcr.views.start_redirect'),
    (r'^admin/', include(admin.site.urls)),
    #home
    (r'^home/$', "rtpcr.views.home"),
    (r'^logout', 'rtpcr.views.logout_view'),
    (r'^error/$', 'rtpcr.views.error'),
    # request
    (r'^pending_request/$', "rtpcr.views.pending_request"),
    (r'^new_request/(?P<request_id>\d+)/$', "rtpcr.views.upload_request"),
    (r'^new_request/$', "rtpcr.views.confirm_request"),
    (r'^request/$', "rtpcr.views.create_request"),
    # procedure
    (r'^select_request/$', "rtpcr.views.select_request"),  
    (r'^validate_samples/$', "rtpcr.views.validate_samples"), 
    (r'^validated_request/$', "rtpcr.views.validated_request"),
    # experiment
    (r'^select_validated_session/$', "rtpcr.views.select_validated_session"),  
    (r'^define_experiment/$', "rtpcr.views.define_experiment"),  
    (r'^layout_experiment/$', "rtpcr.views.layoutExperiment"), 

    # measures collection (raw data)
    (r'^select_experiment/$', "rtpcr.views.select_experiment"), 
    (r'^upload_results/$', "rtpcr.views.upload_results"),  

    # measures collection (analysis data)
    (r'^select_analysis/$', "rtpcr.views.select_analysis"),
    (r'^read_measures/$', "rtpcr.views.read_measures"), 
    (r'^measurement_event/$', "rtpcr.views.measure_event"),  
    (r'^experiment_event/$', "rtpcr.views.experiment_event"),
    
    # review analysis
    (r'^select_analysis_for_review/$', "rtpcr.views.select_analysis_for_review"),
    (r'^review_analysis/$', "rtpcr.views.review_analysis"),

    # configuration
    (r'^assay/$', "rtpcr.views.defineAssay"),
    # APIs
    (r'^api.', include('api.urls')),
    # LASAuth
    (r'^auth/', include('LASAuth.urls')),   
    (r'forbidden/', 'django.views.defaults.permission_denied'),
    (r'permission/', include('editpermission.urls')),
)

if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^rtpcr_media/(?P<path>.*)$', 'django.views.static.serve',
         {'document_root': settings.MEDIA_ROOT}),
    )