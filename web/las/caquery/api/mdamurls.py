from api.mdamquery import *
from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^runquery/$', 'api.mdamquery.RunQuery'),
    url(r'^cleanupquery/$', 'api.mdamquery.CleanupQuery'),
    url(r'^getdbschema/$', 'api.mdamquery.GetDbSchemaHandler'),
    url(r'^makephi/$', 'api.mdamquery.MakePhi'),
)

