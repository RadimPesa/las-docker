#from django.conf.urls.defaults import patterns, include, url
#from _caQuery.views import *
#from caquery import settings
#import os.path
from django.conf.urls.defaults import patterns, include
from django.contrib import admin
from django.contrib.auth.views import *

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

#media = os.path.join(os.path.dirname(__file__), 'media')

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'caQuery.views.home', name='home'),
    # url(r'^caQuery/', include('caQuery.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    (r'^$', '_caQuery.views.mdam'),
    (r'^api/', include('api.urls')),
    (r'^admin/', include(admin.site.urls)),
    #(r'^login/$', "_caQuery.views.login"),
    (r'^logout/$', "_caQuery.views.logout"),
    (r'^home/$', "_caQuery.views.home"),
    (r'^datasources/$', "_caQuery.views.datasources"),
    (r'^manageqe/$', "_caQuery.views.manageqe"),
    (r'^newqe/$', "_caQuery.views.newqe"),
    (r'^tablebrowser/$', "_caQuery.views.tablebrowser"),
    (r'^qpaths/$', "_caQuery.views.qpaths"),

    (r'^querygen/$', "_caQuery.views.querygen"),
    (r'^createtemplate/$', "_caQuery.views.createTemplate"),
    (r'^results/$', "_caQuery.views.displayresults"),
    (r'^getresultsdata/$', "_caQuery.views.getresults"),
    (r'^history/$', "_caQuery.views.historyQuery"),
    (r'^templates/$', "_caQuery.views.editTemplate"),
    (r'^translators/$', "_caQuery.views.editTranslator"),   

    (r'^genealogytree/$', "_caQuery.views.plotXenoTree"),   
    

    (r'^updatePredefLists/$', "_caQuery.views.updateAllPredefinedLists"),

    (r'^report/$', "_caQuery.views.report"), 

    #(r'^aliqretr/$', "_caQuery.views.aliquotsretrieving"),
    (r'^auth/', include('LASAuth.urls')),
    (r'^permission/',include('editpermission.urls')),
    (r'^forbidden/$', 'django.views.defaults.permission_denied'),
    (r'^error/$','_caQuery.views.error'),


)


#commentato nel server
if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^caQuery_media/(?P<path>.*)$', 'django.views.static.serve',  
         {'document_root':     settings.MEDIA_ROOT}),
        (r'^accounts/login/$', 'django.contrib.auth.views.login', {'template_name': 'login.html'}),

    )

