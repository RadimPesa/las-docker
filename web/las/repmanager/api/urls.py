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

newFile = CsrfExemptResource(NewFileRep)
newExperiment = CsrfExemptResource(NewExpRep)
getlink = CsrfExemptResource(GetLink)
getuarraysample = CsrfExemptResource(GetSampleInfo)
getuarraychip = CsrfExemptResource(GetChipInfo)

urlpatterns = patterns('',
	url(r'^uploadFile$', newFile),
	url(r'^uploadExperiment$', newExperiment),
	url(r'^getlink/(?P<link>[\w|\W]*)/(?P<typeO>[\w|\W]*)$', getlink),
	url(r'^getuarraysample$', getuarraysample),
	url(r'^getuarraychip$', getuarraychip),
#   url(r'^findaliquot/(?P<label>[\w|\W]*)/(?P<date>[\w|\W]*)/(?P<owner>[\w|\W]*)$', findaliquot_h),
)
