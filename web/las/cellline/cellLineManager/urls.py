import os

from django.contrib.auth.views import * 
from django.conf.urls import patterns, include, url
from django.conf import settings
#from cellLine.views import *
from django import views 
from django.views.generic.simple import direct_to_template

#from cellLine import *
#from cellLine import archive
#from cellLine import expansion
#from cellLine import experiment_protocol
#from cellLine import generation
#from cellLine import protocol
#from cellLine import thawing
#from cellLine import repManager

#from cellLine import externalApiHandler

cell_media = os.path.join(os.path.dirname(__file__), 'site_media')

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

#if settings.DEBUG:
urlpatterns = patterns('',
	# For Login Manager
	url(r'^auth/', include('LASAuth.urls')),
	# For API
	(r'^api/', include('api.urls')),
    	url(r'^$', 'cellLine.views.home'),
    	url(r'^cell_media/(?P<path>.*)$','django.views.static.serve',{'document_root': settings.MEDIA_ROOT}),
    	url(r'^login/$','django.contrib.auth.views.login'),
    	url(r'^logout/$', 'cellLine.views.logout_view'),
		
		url(r'^generation/aliquots/$', 'cellLine.generation.generation_page_aliquots'),
		url(r'^generation/report/$', 'cellLine.generation.to_biobank'),
		url(r'^generation/pending/$', 'cellLine.generation.manage_pending'),
        url(r'^delete/pending/$', 'cellLine.generation.delete_pending'),

		url(r'^thawing/start/$', 'cellLine.thawing.start'),
		url(r'^thawing/pending/$', 'cellLine.thawing.manage_pending'),
		
		url(r'^protocol/experimental/$', 'cellLine.experiment_protocol.experiment_prot'),
		url(r'^protocol/culturing_conditions/$', 'cellLine.protocol.generation_page_prot_change_cc'),
		url(r'^protocol/culturing_conditions/save/$', 'cellLine.protocol.saveNewProtocol'),

		url(r'^expansion/$', 'cellLine.expansion.expansion_page'),
		url(r'^expansion/save_mods_cc/$', 'cellLine.expansion.save_mods_cc'),
		url(r'^expansion/save_expansion/$', 'cellLine.expansion.saveExpansion'),
		url(r'^expansion/edit_nickname/$', 'cellLine.expansion.edit_nickname'),
		
		url(r'^archive/$', 'cellLine.archive.archive_page'),
		url(r'^archive/save/$', 'cellLine.archive.save'),
	
		url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
		url(r'^admin/', include(admin.site.urls)),
		
	    url(r'^urlArchiveHandlerSendData/$', 'cellLine.externalApiHandler.UrlSendDataArchive'),
	    url(r'^searchCells/$', 'cellLine.externalApiHandler.searchCellNames'),
	    url(r'^newCell/$', 'cellLine.externalApiHandler.newCellName'),
		
		url(r'forbidden/', 'django.views.defaults.permission_denied'),
		url(r'permission/', include('editpermission.urls')),

		url(r'^get_file/(\w+)$', 'cellLine.repManager.retrieveFile'),

        url(r'^mdamapi/', include('api.mdamurls')),
        url(r'^error/$','cellLine.views.error'),
)


