from django.conf.urls.defaults import *
from piston.resource import Resource
from api.exempt import *
from api.mdamquery import *
from api.autocomplete import *
from api.queryTemplate import *
from api.sharing import *
from api.genealogy import *
from api.customapi import *

class CsrfExemptResource(Resource):
    """A Custom Resource that is csrf exempt"""
    def __init__(self, handler, authentication=None):
        super(CsrfExemptResource, self).__init__(handler, authentication)
        self.csrf_exempt = getattr(self.handler, 'csrf_exempt', True)

runtemplate_h = CsrfExemptResource(RunTemplate)
autocomplete_h = Resource(AutoComplete)
listtemplates_h = Resource(ListTemplates)
describetemplate_h = Resource(DescribeTemplate)
shareData_h= CsrfExemptResource(ShareData)
bbsources_h = Resource(BiobankSources)
bbcolltypes_h = Resource(BiobankCollectiontypes)
bbtissuetypes_h = Resource(BiobankTissuetypes)
getWorkingGroups_h=CsrfExemptResource(GetWorkingGroups)
getGenidStruct_h=CsrfExemptResource(GetGenIdStruct)


urlpatterns = patterns('',
    url(r'^autocomplete/$', autocomplete_h, name="autocomplete-api"),
    url(r'^runtemplate/$', runtemplate_h, name="runtemplate-api"),
    url(r'^listtemplates/$', listtemplates_h, name="listtemplates-api"),
    url(r'^describetemplate/$', describetemplate_h, name="describetemplate-api"),
    url(r'^shareData/$',shareData_h, name='_caQuery.views.shareData'),
    url(r'^getWorkingGroups/$',getWorkingGroups_h),
    url(r'^getGenidStruct/$',getGenidStruct_h),
    url(r'^biobanksources/$', bbsources_h, name="bbsources-api"),
    url(r'^biobankcolltypes/$', bbcolltypes_h, name="bbcolltypes-api"),
    url(r'^biobanktissuetypes/$', bbtissuetypes_h, name="bbtissuetypes-api"),
)
