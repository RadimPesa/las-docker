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
get_genes = CsrfExemptResource(GetGenes)
get_mutations = CsrfExemptResource(GetMutations)
get_formulas = CsrfExemptResource(GetFormulas)
newfilter = CsrfExemptResource(NewFilter)


urlpatterns = patterns('',
    url(r'^newbeamingrequest$', newrequest),
    url(r'^deleterequest$', delete_request),
    url(r'^getLayout/(?P<layoutid>[\w|\W]*)$', get_layout),
    url(r'^getGenes/(?P<gene>[\w|\W]*)$', get_genes),
    url(r'^getMutations/(?P<gene>[\w|\W]*)$', get_mutations),
    url(r'^getFormulas$', get_formulas),
    url(r'^newbeamingFilter$', newfilter),
)
