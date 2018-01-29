from django.conf.urls.defaults import *
from piston.resource import Resource
from piston.authentication import HttpBasicAuthentication

from api.handlers import *

class CsrfExemptResource(Resource):
    """A Custom Resource that is csrf exempt"""
    def __init__(self, handler, authentication=None):
        super(CsrfExemptResource, self).__init__(handler, authentication)
        self.csrf_exempt = getattr(self.handler, 'csrf_exempt', True)

# Generation From Aliquots
url_handler_generationAliquots_loadplate = Resource(UrlLoadPlateGenerationAliquots)
archive_loadplate = Resource(LoadPlateArchive)
# protocol infos in choosing-protocol page	
url_handler_protocol_infos_getter = Resource(Protocol_infos_getter)
expansion_genID = Resource(ExpansionNewGenIDHandler)
cc_details = Resource(CcDetailsHandler)
getInfoProtocol_h = Resource(getInfoProtocolHandler)
# genId generation-counter update in aliquot-selection page
url_handler_genid_generation_getter = Resource(Genid_generation_getter)

element_infos_handler = Resource(ElementInfosHandler)

newGenID = Resource(NewGenIDHandler)
externalRequest = CsrfExemptResource(ExternalRequest)

change_wg_handler = CsrfExemptResource(changeWGHandler)
shareCells_h=CsrfExemptResource(ShareCells)

storagetube_h = Resource(StorageTubeHandler)
checkchildren_h = Resource(CheckChildrenHandler)
getNickName_h = Resource(GetNickNameHandler)

urlpatterns = patterns('',
	# Generation From Aliquots
	url(r'^urlGenerationAliquotsHandlerLoadPlate/(?P<name>[\w|\W]+)/(?P<codicePiastra>[\w|\W]+)/(?P<typeP>[\w|\W]+)/$', url_handler_generationAliquots_loadplate),
	# protocol infos in choosing-protocol page	
	url(r'^archive_loadplate/(?P<barcode>[\w|\W]+)/(?P<aliquot>[\w|\W]+)/(?P<typeC>[\w|\W]+)/$', archive_loadplate),

    url(r'^urlProtocolInfosGetter/(?P<conf_id>[\w|\W]+)/$', url_handler_protocol_infos_getter),
    # genId generation-counter update in aliquot-selection page
    url(r'^urlGenId-generationGetter/$', url_handler_genid_generation_getter),

	# Protocol Generation
	url(r'^getElements/(?P<nameE>[\w|\W]+)/$', element_infos_handler),
	#url(r'^expansion_genID/(?P<oldG>[\w|\W]+)/(?P<cc_id>[\w|\W]+)/$', expansion_genID),
	url(r'^expansion_genID/$', expansion_genID),
	url(r'^cc_details/(?P<cc_id>[\w|\W]+)/$', cc_details),
    
    url(r'^getInfoProtocol/$', getInfoProtocol_h),

	url(r'^newGenID/(?P<oldG>[\w|\W]+)/(?P<typeA>[\w|\W]+)/(?P<counter>[\w|\W]+)/(?P<tissueType>[\w|\W]+)/$', newGenID),
	url(r'^externalRequest/$', externalRequest),
	url(r'^changeWGCellLine/$', change_wg_handler),
    url(r'^shareCells/$',shareCells_h),
    
    url(r'^storage/tube/(?P<listagen>[\w|\W]+)/(?P<utente>[\w|\W]+)$', storagetube_h),
    url(r'^check/children/$', checkchildren_h),
    url(r'^getNickName/(?P<genid>[\w|\W]+)/$', getNickName_h),

)
