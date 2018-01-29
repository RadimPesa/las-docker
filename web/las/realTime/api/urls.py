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

urlpatterns = patterns('',
    url(r'^newrealtimerequest$', newrequest),
    url(r'^deleterequest$', delete_request),
    url(r'^getLayout/(?P<layoutid>[\w|\W]*)$', get_layout),
    #url(r'^findaliquot/(?P<label>[\w|\W]*)/(?P<date>[\w|\W]*)/(?P<owner>[\w|\W]*)$', findaliquot_h),
    # django rest framework API
    url(r'^analysisDescription/$', 'api.handlers.analysisDescription'),
    url(r'^analysisInput/$', 'api.handlers.analysisInput'),
    url(r'^analysisOutput/$', 'api.handlers.analysisOutput'),
)
