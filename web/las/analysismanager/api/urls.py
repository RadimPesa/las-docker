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


computeformula = CsrfExemptResource(ComputeFormula)
getformulas = CsrfExemptResource(GetFormulas)
getformulabyIds = CsrfExemptResource(GetFormulaByIds)
getformulaname = CsrfExemptResource(GetFormulaName)
readRandomize = CsrfExemptResource(ReadRandomize)
runRandomize = CsrfExemptResource(RunRandomize)


urlpatterns = patterns('',
    url(r'^computeformulas$', computeformula),
    url(r'^getformulas$', getformulas),
    url(r'^getformulaIds$', getformulabyIds),
    url(r'^getformulaName$', getformulaname),
    url(r'^readRandomize$', readRandomize),
    url(r'^runRandomize$', runRandomize),
)
