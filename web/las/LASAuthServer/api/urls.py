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

query_moduleuser_h=CsrfExemptResource(QueryModuleUserHandler)
checklogin_h=CsrfExemptResource(CheckLoginHandler)
autocompleteuser_h=CsrfExemptResource(AutocompleteUserHandler)

urlpatterns = patterns('',
    url(r'^moduleuser$', query_moduleuser_h),
    url(r'^checklogin/$', checklogin_h),
    url(r'^autocompleteuser$', autocompleteuser_h, name="autocompleteuserapi"),
) 
