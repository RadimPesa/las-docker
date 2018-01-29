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
    (r'^$', 'sangerApp.views.start_redirect'),
    (r'^admin/', include(admin.site.urls)),
    #home
    (r'^home/$', "sangerApp.views.home"),
    (r'^logout', 'sangerApp.views.logout_view'),
    (r'^error/$', 'sangerApp.views.error'),
    # request
    (r'^pending_request/$', "sangerApp.views.pending_request"),
    (r'^new_request/(?P<request_id>\d+)/$', "sangerApp.views.upload_request"),
    (r'^new_request/$', "sangerApp.views.confirm_request"),
    (r'^request/$', "sangerApp.views.create_request"),
    # procedure
    (r'^select_request/$', "sangerApp.views.select_request"),  
    (r'^validate_samples/$', "sangerApp.views.validate_samples"), 
    (r'^validated_request/$', "sangerApp.views.validated_request"),
    # experiment
    (r'^select_validated_session/$', "sangerApp.views.select_validated_session"),  
    (r'^define_experiment/$', "sangerApp.views.define_experiment"),  
    (r'^layout_experiment/$', "sangerApp.views.layoutExperiment"),  
    
    # measures collection (raw data)
    (r'^select_experiment/$', "sangerApp.views.select_experiment"),  
    (r'^upload_results/$', "sangerApp.views.upload_results"), 
    # measures collection (analysis data)
    (r'^select_analysis/$', "sangerApp.views.select_analysis"),
    (r'^read_measures/$', "sangerApp.views.read_measures"), 
    (r'^measurement_event/$', "sangerApp.views.measure_event"),  
    (r'^experiment_event/$', "sangerApp.views.experiment_event"),      
    # configuration
    (r'^assay/$', "sangerApp.views.defineAssay"),
    # APIs
    (r'^api.', include('api.urls')),
    # LASAuth
    (r'^auth/', include('LASAuth.urls')),   
    (r'forbidden/', 'django.views.defaults.permission_denied'),
    (r'permission/', include('editpermission.urls')),
)

if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^sanger_media/(?P<path>.*)$', 'django.views.static.serve',
         {'document_root': settings.MEDIA_ROOT}),
    )