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

query_chiptype_h=Resource(QueryChipTypeHandler)
query_chipowner_h=CsrfExemptResource(QueryChipOwnerHandler)
query_chipmanufacter_h=CsrfExemptResource(QueryChipManufacturerHandler)
query_hybprotocol_h=Resource(QueryHybProtocolHandler)
query_scanprotocol_h=Resource(QueryScanProtocolHandler)
query_hybprotocolname_h=Resource(QueryHybProtocolNameHandler)
query_hybinstrument_h=Resource(QueryHybInstrumentHandler)
query_software_h=Resource(QuerySoftwareHandler)
query_scaninstrument_h=Resource(QueryScanInstrumentHandler)
query_exgroup_h = CsrfExemptResource(QueryExGroupHandler)
query_rawdataowner_h = CsrfExemptResource(QueryRawDataOwnerHandler)
query_experiment_h = CsrfExemptResource(QueryExperimentHandler)
query_project_h = CsrfExemptResource(QueryProjectHandler)


query_chips_h=CsrfExemptResource(QueryChipsHandler)
query_hybprotocols_h=CsrfExemptResource(QueryHybProtocolsHandler)
query_hybevents_h=CsrfExemptResource(QueryHybEventsHandler)
query_scanevents_h=CsrfExemptResource(QueryScanEventsHandler)
query_rawdata_h=CsrfExemptResource(QueryRawDataHandler)


findaliquot_h=CsrfExemptResource(AliquotFindHandler)
findgenid_h=CsrfExemptResource(GenealogyFindHandler)
findhybprotocol_h=CsrfExemptResource(HybProtocolFindHandler)
getchip_h=CsrfExemptResource(GetChipHandler)
findscanprotocol_h=CsrfExemptResource(ScanProtocolFindHandler)
getscanprotocol_h=CsrfExemptResource(ScanProtocolGetHandler)
getlayout_h=CsrfExemptResource(LayoutGetHandler)
updatesamples_h=CsrfExemptResource(UpdateSamples)
newrequest = CsrfExemptResource(NewRequest)
delete_request = CsrfExemptResource(DeleteRequest)
getlink = CsrfExemptResource(GetLink)
delete_hybplan = CsrfExemptResource(DeleteHybPlan)
getsample = CsrfExemptResource(GetSample)
readsamples = CsrfExemptResource(ReadSamples)


urlpatterns = patterns('',
    url(r'^query/chiptype$', query_chiptype_h),
    url(r'^query/chipowner$', query_chipowner_h),
    url(r'^query/chipmanufacturer$', query_chipmanufacter_h),
    url(r'^query/hybprotocol$', query_hybprotocol_h),
    url(r'^query/hybprotocolname$', query_hybprotocolname_h),
    url(r'^query/hybinstrument$', query_hybinstrument_h),
    url(r'^query/software$', query_software_h),
    url(r'^query/scaninstrument$', query_scaninstrument_h),
    url(r'^query/scanprotocols$', query_scanprotocol_h),
    url(r'^query/rawdatagroup$', query_exgroup_h),
    url(r'^query/rawdataowner$', query_rawdataowner_h),
    url(r'^query/experiment$', query_experiment_h),
    url(r'^query/project$', query_project_h),
    
    
    url(r'^query/chips$', query_chips_h),
    url(r'^query/hybprotocols$', query_hybprotocols_h),
    url(r'^query/hybevents$', query_hybevents_h),
    url(r'^query/scanevents$', query_scanevents_h),
    url(r'^query/rawdata$', query_rawdata_h),

    url(r'^findaliquot/(?P<label>[\w|\W]*)/(?P<date>[\w|\W]*)/(?P<owner>[\w|\W]*)$', findaliquot_h),
    url(r'^findgenid/(?P<genid>[\w|\W]*)/(?P<username>[\w|\W]*)$', findgenid_h),
    url(r'^hybprotocolinfo/(?P<protocol>[\w|\W]*)/(?P<instrument>[\w|\W]*)$', findhybprotocol_h),
    url(r'^getchip/(?P<barcode>[\w|\W]*)/(?P<status>[\w|\W]*)$', getchip_h),
    url(r'^scanprotocolinfo/(?P<protocol>[\w|\W]*)/(?P<instrument>[\w|\W]*)$', findscanprotocol_h),
    url(r'^getscanprotocol/(?P<protocol>[\w|\W]*)$', getscanprotocol_h),
    url(r'^getlayout/(?P<positions>[\w|\W]*)$', getlayout_h),
    url(r'^updatesamples$', updatesamples_h),
    url(r'^newuarrayrequest$', newrequest),
    url(r'^deleterequest$', delete_request),
    url(r'^deletehybplan$', delete_hybplan), 
    url(r'^getlink/(?P<link>[\w|\W]*)/(?P<typeO>[\w|\W]*)$', getlink),
    url(r'^getsample/(?P<genid>[\w|\W]*)$', getsample),
    url(r'^readSamples$', readsamples),
    

)
