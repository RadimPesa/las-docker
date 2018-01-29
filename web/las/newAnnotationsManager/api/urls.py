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

genesFromSymbol = CsrfExemptResource(GenesFromSymbol)
mutationsFromGeneId = CsrfExemptResource(MutationsFromGeneId)
mutationFromCDSSyntax = CsrfExemptResource(MutationFromCDSSyntax)
createMutationAnnotation = CsrfExemptResource(CreateMutationAnnotation)
topFreqMutFromAASyntax = CsrfExemptResource(TopFreqMutFromAASyntax)
geneMutNamesFromId = CsrfExemptResource(GeneMutNamesFromId)
snpFromName = CsrfExemptResource(SnpFromName)
cellLineFromName = CsrfExemptResource(CellLineFromName)
newCellLine = CsrfExemptResource(NewCellLine)
writeAnnotation_SequenceAlteration = CsrfExemptResource(Write_Annotation_SequenceAlteration)
writeAnnotation_CopyNumberVariation = CsrfExemptResource(Write_Annotation_CopyNumberVariation)

urlpatterns = patterns('',
    url(r'^genesFromSymbol/$', genesFromSymbol),
    url(r'^mutationsFromGeneId/$', mutationsFromGeneId),
    url(r'^mutationFromCDSSyntax/$', mutationFromCDSSyntax),
    url(r'^topFreqMutFromAASyntax/$', topFreqMutFromAASyntax),
    url(r'^createMutationAnnotation/$', createMutationAnnotation),
    url(r'^geneMutNamesFromId/$', geneMutNamesFromId),
    url(r'^snpFromName/$', snpFromName),
    url(r'^cellLineFromName/$', cellLineFromName),
    url(r'^newCellLine/$', newCellLine),
    url(r'^writeAnnotation.SequenceAlteration/$', writeAnnotation_SequenceAlteration),
    url(r'^writeAnnotation.CopyNumberVariation/$', writeAnnotation_CopyNumberVariation),
)
