from django.conf.urls.defaults import patterns, include, url
import settings

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'Candiolo.views.home', name='home'),
    # url(r'^Candiolo/', include('Candiolo.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:

    (r'^$', 'MMM.views.start_redirect'),

    (r'^admin/', include(admin.site.urls)),
    
   
    #home
    (r'^home/$', "MMM.views.home"),
    
    (r'^logout', 'MMM.views.logout_view'),
    
    (r'^error/$', 'MMM.views.error'),

    #New Chip
    (r'^new_chip/$', "MMM.views.new_chip"),
    
    (r'^new_chip_type/$', "MMM.views.new_chip_type"),

    (r'^view_chips/$', "MMM.views.chips_view"),

    #Request

    (r'^pending_request/$', "MMM.views.pending_request"),

    (r'^new_request/$', "MMM.views.upload_request_file"),

    (r'^new_request/(?P<request_id>\d+)/$', "MMM.views.upload_request"),

    (r'^request/$', "MMM.views.confirm_request"),

    (r'^finalize_request/$', "MMM.views.finalize_request"),    
    
    #Hybridization
    
    (r'^plan_hybrid/$', "MMM.views.plan_hybrid"),

    (r'^plan_view/$', "MMM.views.plan_view"),

    (r'^select_plan/$', "MMM.views.select_plan"),

    (r'^check_hybrid/$', "MMM.views.check_hybrid"),

    (r'^check_view/$', "MMM.views.check_view"),

    (r'^select_hybrid/$', "MMM.views.select_hybrid"),

    (r'^hybrid/$', "MMM.views.hybridize"),

    (r'^hybridevent/$', "MMM.views.hybrization_view"),

    (r'^hybrididization_protocol/$', "MMM.views.hybrid_protocols"),

    (r'^info_hybridization_protocol/$', "MMM.views.hybridprot_info"),

    # Scan 

    (r'^pre_scan/$', "MMM.views.pre_scan"),

    (r'^scan/$', "MMM.views.scan"),

    (r'^select_scan/$', "MMM.views.select_scan"),    

    (r'^scanqc/$', "MMM.views.scan_quality"),    

    (r'^view_scanqc/$', "MMM.views.view_scanqc"),

    (r'^scan_protocols/$', "MMM.views.scan_protocols"),

    (r'^info_scan_protocol/$', "MMM.views.scanprot_info"),
  


    # Experiments

    (r'^explore_scans/$', "MMM.views.explore_scan"),    

    (r'^compose_dataset/$', "MMM.views.compose_data"),

    (r'^experiment/(?P<experimentid>\d+)/$', "MMM.views.uarrayExperiment"),


    # APIs
    (r'^api.', include('api.urls')),

    (r'^get_file/(\w+)$', "MMM.utils.retrieveFile"),
    
    # LASAuth
     
    (r'^auth/', include('LASAuth.urls')),   

    (r'forbidden/', 'django.views.defaults.permission_denied'),

    (r'permission/', include('editpermission.urls')),
    

)

if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^uarray_media/(?P<path>.*)$', 'django.views.static.serve',
         {'document_root':     settings.MEDIA_ROOT}),
    )
