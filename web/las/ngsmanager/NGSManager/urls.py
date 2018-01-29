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
    (r'^$', 'ngs.views.start_redirect'),
    (r'^admin/', include(admin.site.urls)),
    #home
    (r'^home/$', "ngs.views.home"),
    (r'^logout', 'ngs.views.logout_view'),
    (r'^error/$', 'ngs.views.error'),
    # request
    (r'^pending_request/$', "ngs.views.pending_request"),
    (r'^new_request/(?P<request_id>\d+)/$', "ngs.views.upload_request"),
    (r'^new_request/$', "ngs.views.confirm_request"),
    (r'^request/$', "ngs.views.create_request"),
    
    (r'^insert_sample/$', "ngs.views.views_request.insert_sample"),
    (r'^insert_sample/final/$', "ngs.views.views_request.insert_sample_final"),
    
    # procedure
    (r'^select_request/$', "ngs.views.select_request"),  
    (r'^validate_samples/$', "ngs.views.validate_samples"), 
    (r'^validated_request/$', "ngs.views.validated_request"),
    # experiment
    (r'^select_validated_session/$', "ngs.views.select_validated_session"),  
    #(r'^define_experiment/$', "ngs.views.define_experiment"),  
    (r'^select_experiment/$', "ngs.views.select_experiment"),
    
    (r'^execute_experiment/$', "ngs.views.views_experiment.execute_experiment"),
    (r'^execute_experiment/insertdata/$', "ngs.views.views_experiment.execute_experiment_insertdata"),
    (r'^execute_experiment/save/$', "ngs.views.views_experiment.execute_experiment_save"),
    (r'^execute_experiment/final/$', "ngs.views.views_experiment.execute_experiment_final"),
      
    # measures collection
    (r'^read_measures/$', "ngs.views.read_measures"), 
    (r'^measurement_event/$', "ngs.views.measure_event"),  
    # get results
    (r'^get_results/$', "ngs.views.get_results"), 
    (r'^downloadResults$', "ngs.views.downloadResults"), 

    

    # APIs
    (r'^api.', include('api.urls')),
    # LASAuth
    (r'^auth/', include('LASAuth.urls')),   
    (r'forbidden/', 'django.views.defaults.permission_denied'),
    (r'permission/', include('editpermission.urls')),
)

if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^ngs_media/(?P<path>.*)$', 'django.views.static.serve',
         {'document_root': settings.MEDIA_ROOT}),
    )