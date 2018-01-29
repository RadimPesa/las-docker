from django.conf.urls.defaults import *
from piston.resource import Resource
from piston.authentication import HttpBasicAuthentication
from catissue.api.handlers import *
from catissue.api.query import *

class CsrfExemptResource(Resource):
    """A Custom Resource that is csrf exempt"""
    def __init__(self, handler, authentication=None):
        super(CsrfExemptResource, self).__init__(handler, authentication)
        self.csrf_exempt = getattr(self.handler, 'csrf_exempt', True)
 
kit_h=Resource(KiteProtHandler)
kitbarcode_h=Resource(KitBarcodeHandler)
tube_h = Resource(TubeHandler)
derivative_h = Resource(DerivativeHandler)
tissue_h=Resource(TissueHandler)
collectiontype_h=Resource(CollectionTypeHandler)
load_h=Resource(LoadHandler)
derivedkit_h=Resource(SingleKitHandler)
derived_h=Resource(KitHandler)
derivedChoose_h=Resource(DerivedChooseHandler)
derivedAliquot_h=Resource(DerivedAliquotHandler)
derivedfile_h=Resource(DerivedFileHandler)
derivedload_h=Resource(DerivedLoadHandler)
derivedcalculate_h=Resource(DerivedCalculateHandler)
derivedfinalsession_h=Resource(DerivedFinalSessionHandler)
derivedupdatevaluemeasure_h=Resource(DerivedUpdateValueMeasureHandler)
splitfinalsession_h=Resource(SplitFinalSessionHandler)
address_h=Resource(AddressHandler)
canc_h = CsrfExemptResource(CancHandler)
revaluateAliquot_h=Resource(RevaluateAliquotHandler)
extern_h=Resource(ExternHandler)
extern_aliquot_type_h=Resource(ExternAliquotTypeHandler)
extern_newgenid_h=Resource(ExternNewgenidHandler)
instr_h=Resource(InstrumentHandler)
table_handler = Resource(TableHandler)
load_tube_h=Resource(LoadTubeHandler)
#positionAliquot_h=Resource(PositionAliquotHandler)
user_h=Resource(UserHandler)
feature_h = Resource(FeatureHandler)
genidbarc_h = Resource(GenIdBarcHandler)
genericload_h = Resource(GenericLoadHandler)
patientaliqinfo_h = Resource(PatientAliqInfoHandler)
patientlist_h = Resource(PatientListHandler)
patientclinicalfeature_h = Resource(PatientClinicalFeatureHandler)
mask_h = Resource(MaskHandler)
infoaliqtype_h = Resource(InfoAliqTypeHandler)
collecttube_h = Resource(CollectTubeHandler)
storagetube_h = Resource(StorageTubeHandler)
collabortube_h = Resource(CollaborTubeHandler)
checkpatient_h = Resource(CheckPatientHandler)
transferAliquot_h=Resource(TransferAliquotHandler)
transferListBarcode_h=CsrfExemptResource(TransferListBarcodeHandler)
allaliquots_h = Resource(AllAliquotsHandler)
archivealiquots_h = Resource(ArchiveAliquotsHandler)
cellAutocomplete_h = Resource(CellAutocompleteHandler)
cellnewcase_h = Resource(CellNewCaseHandler)
savecell_h = CsrfExemptResource(SaveCellHandler)
returncontainer_h = CsrfExemptResource(ReturnContainerHandler)
infoaliq_h = CsrfExemptResource(InfoAliqHandler)
aliqdata_h = CsrfExemptResource(AliqDataHandler)
batchexplant_h = CsrfExemptResource(BatchExplantHandler)
slideAliquot_h = Resource(SlideAliquotHandler)
slideProtocol_h = Resource(SlideProtocolHandler)
slideload_h = Resource(SlideLoadHandler)
slidefinalsession_h=Resource(SlideFinalSessionHandler)
getClinicalFeature_h = Resource(GetClinicalFeatureHandler)
get_genes_h = Resource(GetGenes)
get_mutations_h = Resource(GetMutations)
get_drugs_h = Resource(GetDrugs)
getcollection_h = Resource(GetCollection)
getsources_h = Resource(GetSources)
gethospital_h = Resource(GetHospital)
getgenIDvalues_h = Resource(GetGenIDValues)
localidlist_h = Resource(LocalIDListHandler)
labelAliquot_h = Resource(LabelAliquotHandler)
labelGeneAutocomplete_h = Resource(LabelGeneAutocompleteHandler)
labelProbeInfo_h = Resource(LabelProbeInfoHandler)
labelMarknameAutocomplete_h = Resource(LabelMarknameAutocompleteHandler)
labelProtocolAutocomplete_h = Resource(LabelProtocolAutocompleteHandler)
labelGetFiles_h = Resource(LabelGetFilesHandler)
labelinsert_h = Resource(LabelInsertHandler)
labellist_h = Resource(LabelListHandler)

checkBarcode_h = Resource(CheckBarcodeHandler)
readFile_h = Resource(ReadFileHandler)

experiment_list_h=Resource(ExpListHandler)
experiment_confirm_h=CsrfExemptResource(ExpConfirmHandler)
experiment_canc_h=CsrfExemptResource(ExpCancHandler)
experiment_load_h=CsrfExemptResource(ExpLoadHandler)
experiment_viewdata_h=Resource(ExpViewDataHandler)

facility_loadaliquots_h=CsrfExemptResource(FacilityLoadAliquotHandler)
facility_savealiquots_h=CsrfExemptResource(FacilitySaveAliquotsHandler)

change_alias_h=CsrfExemptResource(ChangeAliasHandler)

query_coll_h=Resource(QueryCollTypeHandler)
query_source_h=Resource(QuerySourceHandler)
query_tissue_h=Resource(QueryTissueHandler)
query_tissuetype_h=Resource(QueryTissueTypeHandler)
query_aliqtype_h=Resource(QueryAliqTypeHandler)
query_name_h=Resource(QueryNameHandler)
query_kittype_h=Resource(QueryKitTypeHandler)
query_producer_h=Resource(QueryProducerHandler)
query_exp_h=Resource(QueryExpHandler)

query_aliquots_h=CsrfExemptResource(QueryAliquotsHandler)
query_collections_h=CsrfExemptResource(QueryCollectionsHandler)
query_protocols_h=CsrfExemptResource(QueryProtocolsHandler)
query_events_h=CsrfExemptResource(QueryEventsHandler)
query_experiments_h=CsrfExemptResource(QueryExperimentsHandler)
query_split_h=CsrfExemptResource(QuerySplitHandler)

loginResource=CsrfExemptResource(LoginHandler)
logoutResource=CsrfExemptResource(LogoutHandler)

getDbSchema_h=CsrfExemptResource(GetDbSchemaHandler)

saveWgAliquot_h=CsrfExemptResource(SaveWgAliquot)
shareAliquots_h=CsrfExemptResource(ShareAliquots)

save_blocks_h=CsrfExemptResource(SaveBlocks)
save_derived_h=CsrfExemptResource(SaveDerived)
transfer_vials_h=CsrfExemptResource(TransferVials)

urlpatterns = patterns('',
#url(r'^place/$', place_h),                       
#url(r'^place/(?P<parameters>[A-Za-z&=0-9 ]+)$', place_h),
url(r'^address/$', address_h),
url(r'^tissue/$', tissue_h),
url(r'^collectiontype/$', collectiontype_h),
url(r'^extern/type/(?P<tipo>[\w|\W]+)$', extern_h),
#url(r'^extern/aliquot/(?P<tipo>[\w|\W]+)$', extern_aliquot_h),
url(r'^ext/aliquottype/$', extern_aliquot_type_h),
url(r'^ext/newgenid/(?P<tum>[\w|\W]+)/(?P<caso>[\w|\W]+)/(?P<tess>[\w|\W]+)/(?P<centro>[\w|\W]+)/(?P<tesstopo>[\w|\W]+)/(?P<tipoaliq>[\w|\W]+)/(?P<contat>[\w|\W]+)/(?P<cell>(cell)*)$', extern_newgenid_h),
url(r'^derived/(?P<tipo>[0-9]+)$', derived_h),
url(r'^derived/choose/(?P<protoc>[0-9]+)/(?P<tipo>[\w|\W]+)$', derivedChoose_h),
url(r'^derived/aliquot/(?P<gen>[\w|\W]+)/(?P<protoc>[\w|\W]+)$', derivedAliquot_h),
url(r'^derived/kit/(?P<tipo>[0-9]+)$', derivedkit_h),
url(r'^derived/file/(?P<gen>[\w|\W]+)$', derivedfile_h),
url(r'^derived/load/(?P<barcodeP>[\w|\W]+)/(?P<typeP>[\w|\W]+)/$', derivedload_h),
url(r'^derived/calculate/(?P<prot>[\w|\W]+)$', derivedcalculate_h),
url(r'^derived/finalsession/$', derivedfinalsession_h),
url(r'^derived/updatevaluemeasure/$', derivedupdatevaluemeasure_h),
url(r'^split/final/$', splitfinalsession_h),
url(r'^kit/(?P<nome>[\w|\W]+)$', kit_h),
url(r'^kitbarcode/(?P<barcode>[\w|\W]+)$', kitbarcode_h),
url(r'^tubes/(?P<barcode>[\w|\W|#]+)$',tube_h),
url(r'^derivative/(?P<genid>[\w|\W]+)/(?P<operator>[\w|\W]+)$',derivative_h),
url(r'^load/tubes/(?P<barcode>[\w|\W|#]+)/(?P<tipo>[\w|\W]+)$',load_tube_h),
url(r'^aliquot/canc/$',canc_h),
url(r'^plate/load/(?P<barcode>[A-Za-z&=0-9 ,]+)/(?P<tipo>[A-Za-z]+)/(?P<store>(stored)*)(?P<derived>(derived)*)$',load_h),
url(r'^revaluate/aliquot/(?P<gen>[\w|\W]+)/(?P<split>(split)*)$', revaluateAliquot_h),
url(r'^instrument/$', instr_h),
url(r'^table/(?P<barcodeP>[\w|\W]+)/(?P<typeP>[\w|\W]+)/(?P<ext>(extern)*)$', table_handler),
#url(r'^position/aliquot/(?P<gen>[\w|\W]+)$', positionAliquot_h),
url(r'^user/$', user_h),
url(r'^feature/(?P<genid>[\w|\W]+)$',feature_h),
url(r'^genidbarc/(?P<val>[\w|\W]+)/(?P<exp>[\w|\W]+)$',genidbarc_h),
url(r'^generic/load/(?P<barcode>[\w|\W]+)/(?P<aliquot>[\w|\W]+)/(?P<typeP>[\w|\W]+)$',genericload_h),
url(r'^patientaliqinfo/(?P<codpaz>[\w|\W]+)/(?P<aliqtipo>[\w|\W]+)/(?P<tesstipo>[\w|\W]+)/(?P<vettore>[\w|\W]+)/(?P<maschera>[\w|\W]+)/(?P<utente>[\w|\W]+)$',patientaliqinfo_h),
url(r'^patientlist/(?P<operatore>[\w|\W]+)/(?P<ospedale>[\w|\W]+)/(?P<colltype>[\w|\W]+)/(?P<altype>[\w|\W]+)/(?P<datadal>[\w|\W]+)/(?P<dataal>[\w|\W]+)/(?P<protocol>[\w|\W]+)/(?P<consenso>[\w|\W]+)$',patientlist_h),
url(r'^patientclinical/(?P<codpaz>[\w|\W]+)/(?P<aliqtipo>[\w|\W]+)/(?P<tesstipo>[\w|\W]+)/(?P<vettore>[\w|\W]+)/$',patientclinicalfeature_h),
url(r'^mask/$', mask_h),
url(r'^info/aliquottype$', infoaliqtype_h),
url(r'^collect/singletube/(?P<barcode>[\w|\W]+)/(?P<tipo>[\w|\W]+)/$', collecttube_h),
url(r'^storage/tube/(?P<listabarc>[\w|\W]+)/(?P<utente>[\w|\W]+)$', storagetube_h),
url(r'^collaboration/tube/(?P<barcode>[\w|\W]+)$', collabortube_h),
url(r'^check/patient/(?P<coll_event>[\w|\W]+)/(?P<patient>[\w|\W]+)/(?P<hospital>[\w|\W]+)/(?P<project>[\w|\W]+)$', checkpatient_h),
url(r'^transfer/aliquot/(?P<genbarc>[\w|\W]+)$', transferAliquot_h),
url(r'^transfer/listbarcode/$', transferListBarcode_h),
url(r'^allaliquots/$', allaliquots_h),
url(r'^archivealiquots/$', archivealiquots_h),
url(r'^cell/autocomplete/$', cellAutocomplete_h),
url(r'^cell/new_case/(?P<tumor>[\w|\W]+)/(?P<sorg>[\w|\W]+)/(?P<cell>[\w|\W]+)/(?P<numero>[\w|\W]+)/(?P<crea>[\w|\W]+)$', cellnewcase_h),
url(r'^save/cell/$', savecell_h),
url(r'^return/container/$', returncontainer_h),
url(r'^infoaliq/$', infoaliq_h),
url(r'^aliquotdata/$', aliqdata_h),
url(r'^save/batchexplant/$', batchexplant_h),
url(r'^slide/aliquot/(?P<gen>[\w|\W]+)/$', slideAliquot_h),
url(r'^slide/protocol/(?P<prot>[\w|\W]+)$', slideProtocol_h),
url(r'^slide/load/(?P<barcode>[\w|\W]+)/(?P<aliquot>[\w|\W]+)/(?P<tipocont>[\w|\W]+)/(?P<pezzi>[\w|\W]+)/$',slideload_h),
url(r'^slide/final/$', slidefinalsession_h),
url(r'^getClinicalFeature/(?P<idfeat>[\w|\W]+)/(?P<idtumore>[\w|\W]+)/$', getClinicalFeature_h),
url(r'^getGenes/(?P<gene>[\w|\W]*)$', get_genes_h),
url(r'^getMutations/(?P<gene>[\w|\W]*)$', get_mutations_h),
url(r'^getDrugs/$', get_drugs_h),
url(r'^getCollection/$', getcollection_h),
url(r'^getSources/$', getsources_h),
url(r'^getHospital/(?P<prot>[\w|\W]+)/$', gethospital_h),
url(r'^getGenIDValues/$', getgenIDvalues_h),
url(r'^localID/list/(?P<prot>[\w|\W]+)/$', localidlist_h),
url(r'^label/aliquot/(?P<gen>[\w|\W]+)/(?P<save>(save)*)$', labelAliquot_h),
url(r'^label/gene/autocomplete/$', labelGeneAutocomplete_h),
url(r'^label/ampliconinfo/$', labelProbeInfo_h),
url(r'^label/markname/autocomplete/$', labelMarknameAutocomplete_h),
url(r'^label/protocol/autocomplete/$', labelProtocolAutocomplete_h),
url(r'^label/getFiles/$', labelGetFiles_h),
url(r'^label/insert/(?P<gen>[\w|\W]+)/$', labelinsert_h),
url(r'^label/list/(?P<tipo>[\w|\W]+)/(?P<tecn>[\w|\W]+)/(?P<protocollo>[\w|\W]+)/(?P<operatore>[\w|\W]+)/(?P<genid>[\w|\W]+)/(?P<datadal>[\w|\W]+)/(?P<dataal>[\w|\W]+)/(?P<utente>[\w|\W]+)$',labellist_h),

#per mercuric
url(r'^check/barcode/$', checkBarcode_h),
url(r'^read/file/$', readFile_h),

url(r'^experiment/list$', experiment_list_h),
url(r'^experiment/confirm$', experiment_confirm_h),
url(r'^experiment/canc$', experiment_canc_h),
url(r'^experiment/load/$', experiment_load_h),
url(r'^experiment/viewdata/(?P<filetype>[\w|\W]+)/$', experiment_viewdata_h),
#per ngs
url(r'^facility/savealiquots/$', facility_savealiquots_h),
url(r'^facility/loadaliquots/(?P<codice>[\w|\W]+)/(?P<operator>[\w|\W]+)$', facility_loadaliquots_h),

url(r'^alias/change/$', change_alias_h),

url(r'^query/collectiontype$', query_coll_h),
url(r'^query/source$', query_source_h),
url(r'^query/tissue$', query_tissue_h),
url(r'^query/tissuetype$', query_tissuetype_h),
url(r'^query/aliquottype$', query_aliqtype_h),
url(r'^query/name$', query_name_h),
url(r'^query/kittype$', query_kittype_h),
url(r'^query/producer$', query_producer_h),
url(r'^query/exptype$', query_exp_h),

url(r'^query/aliquots$', query_aliquots_h),
url(r'^query/collections$', query_collections_h),
url(r'^query/protocols$', query_protocols_h),
url(r'^query/events$', query_events_h),
url(r'^query/experiments$', query_experiments_h),
url(r'^query/split$', query_split_h),

url(r'^query/getDbSchema$', getDbSchema_h),

url(r'^login$', loginResource),
url(r'^logout$', logoutResource),

url(r'^saveWgAliquot/$',saveWgAliquot_h),
url(r'^shareAliquots/$',shareAliquots_h),

#per funnel
url(r'^blocks/$', save_blocks_h),
url(r'^derivedsamples/$', save_derived_h),
url(r'^vials/$', transfer_vials_h),
)
