from django.conf.urls.defaults import *



urlpatterns = patterns('',
	url(r'^$', 'mercuric.views.MercuricLogin'),
    url(r'^index/$', 'mercuric.views.indexMercuric'),
    url(r'^logout/$', 'mercuric.views.logout'),

)
