from django.conf.urls.defaults import patterns, include, url
from piston.resource import Resource
from piston.authentication import HttpBasicAuthentication
from query import *
from handlers import *


class CsrfExemptResource(Resource):
    """A Custom Resource that is csrf exempt"""
    def __init__(self, handler, authentication=None):
        super(CsrfExemptResource, self).__init__(handler, authentication)
        self.csrf_exempt = getattr(self.handler, 'csrf_exempt', True)



newrequest = CsrfExemptResource(NewRequest)
delete_request = CsrfExemptResource(DeleteRequest)
get_layout = CsrfExemptResource(GetLayout)
loadResults = CsrfExemptResource(LoadResults)
autocomplete_insertsample = Resource(AutocompleteInsertSample)
load_sample_biobank = Resource(LoadSampleFromBiobank)
autocomplete_loadsample = Resource(AutocompleteLoadSample)
autocomplete_labelexperiment = Resource(AutocompleteLabelExperiment)
sample_reanalyze = Resource(SampleReanalyze)

urlpatterns = patterns('',
    url(r'^newngsrequest$', newrequest),
    url(r'^deleterequest$', delete_request),
    url(r'^getLayout/(?P<layoutid>[\w|\W]*)$', get_layout),
    url(r'^loadResults$', loadResults), 
    url(r'^insertsample/autocomplete/$', autocomplete_insertsample),
    url(r'^insertsample/loadfrombiobank/(?P<cod>[\w|\W]*)/(?P<operator>[\w|\W]*)/$', load_sample_biobank),
    url(r'^loadsample/autocomplete/$', autocomplete_loadsample),
    url(r'^labelexperiment/autocomplete/$', autocomplete_labelexperiment),
    url(r'^sample/reanalyze/(?P<label>[\w|\W]*)/$', sample_reanalyze),
)
