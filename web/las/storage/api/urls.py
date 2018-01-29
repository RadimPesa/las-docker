from django.conf.urls.defaults import *
from piston.resource import Resource
from api.handlers import *
from api.query import *

class CsrfExemptResource(Resource):
    """A Custom Resource that is csrf exempt"""
    def __init__(self, handler, authentication=None):
        super(CsrfExemptResource, self).__init__(handler, authentication)
        self.csrf_exempt = getattr(self.handler, 'csrf_exempt', True)

container_handler = Resource(Container_handler)
#emptyplate_handler = Resource(EmptyPlate_handler)
load_h = Resource(LoadHandler)
biocassette_h=Resource(BioCasHandler)
tube_handler = Resource(TubeHandler)
address_h=Resource(AddressHandler)
table_handler = Resource(TableHandler)
#storebatch_h=Resource(StoreBatchHandler)
vital_h=Resource(VitalHandler)
#move_h=Resource(MoveHandler)
#draw_h=Resource(DrawHandler)
insert_cont_h=Resource(InsertContHandler)
check_avail_h=Resource(CheckAvailHandler)
infoplate_h=Resource(InfoPlateHandler)
#loadcell_h=Resource(LoadCellHandler)
infoconttype_h=Resource(InfoContTypeHandler)
infogeometry_h=Resource(InfoGeometryHandler)
geometrycreate_h=Resource(GeometryCreateHandler)
freecontainer_h=Resource(FreeContainerHandler)
#return_h=Resource(ReturnHandler)
listacont_h=Resource(ListaContHandler)
checklistacont_h=Resource(CheckListaContainerHandler)
cancfather_h=CsrfExemptResource(CancFatherHandler)
generic_type_h=Resource(GenericTypeHandler)
empty_pos_h=Resource(EmptyPositionsHandler)
infocontainer_h=Resource(InfoContHandler)
validatecontainer_h=Resource(ValidateContHandler)
checkpresence_h=Resource(CheckPresenceHandler)
changebarcode_h=Resource(ChangeBarcodeHandler)
inforelationship_h=Resource(InfoRelationshipHandler)
infoaliquot_h=Resource(InfoAliquotHandler)
getinfocontainer_h=Resource(GetInfoContainerHandler)
containertypeinfo_h=Resource(ContainerTypeInfoHandler)
saveslide_h=CsrfExemptResource(SaveSlideHandler)

restorealiquot_h=Resource(RestoreAliquotHandler)

query_conttype_h=Resource(QueryContTypeHandler)
query_feature_h=Resource(QueryFeatureHandler)
query_featurevalue_h=Resource(QueryFeatureValueHandler)
query_parent_h=Resource(QueryParentHandler)

query_containers_h=CsrfExemptResource(QueryContainersHandler)
query_positions_h=CsrfExemptResource(QueryPositionsHandler)
query_relations_h=CsrfExemptResource(QueryFatherHandler)

loginResource=CsrfExemptResource(LoginHandler)
logoutResource=CsrfExemptResource(LogoutHandler)

urlpatterns = patterns('',
    url(r'^container/(?P<barcode>[\w|\W]+)$', container_handler),
    url(r'^tube/(?P<barcode>[\w|\W]+)/(?P<utente>[\w|\W]+)$', tube_handler),
    #url(r'^emptyPlate/(?P<barcode>[A-Za-z0-9]+)&(?P<addressStorage>[A-Za-z0-9\./:]+)&(?P<addressBioB>[A-Za-z0-9\./:]+)$', emptyplate_handler),
    url(r'^plate/(?P<barcode>[\w|\W]+)/(?P<tipo>[A-Za-z]+)/(?P<store>(stored)*)(?P<ext>(extern)*)$',load_h),
    url(r'^biocassette/(?P<barcode>[\w|\W]+)/(?P<tipo>[\w|\W]+)/(?P<archive>(archive)*)$', biocassette_h),
    url(r'^address/$', address_h),
    url(r'^table/(?P<barcodeP>[\w|\W]+)/(?P<typeP>[\w|\W]+)/(?P<spostamento>[\w|\W]+)/$', table_handler),
    #url(r'^aliquot/(?P<barcodedest>[\w|\W]+)/(?P<stringa>[\w|\W]+)$', storebatch_h),
    url(r'^vital/(?P<barcode>[\w|\W]+)/$', vital_h),
    #url(r'^move/(?P<barcode>[\w|\W]+)/(?P<tipo>[\w|\W]+)/(?P<sorg>[\w|\W]+)/(?P<store>(stored)*)$', move_h),
    #url(r'^draw/(?P<barcode>[\w|\W]+)$', draw_h),
    url(r'^insert_cont/(?P<tipo>[\w|\W]+)/$', insert_cont_h),
    url(r'^check_availability/(?P<freezer>[\w|\W]+)/(?P<rack>[\w|\W]+)/(?P<plate>[\w|\W]+)/(?P<position>[\w|\W]+)/(?P<tipo_cont>[\w|\W]+)/$', check_avail_h),
    url(r'^info/plate/(?P<barcode>[\w|\W]+)/$', infoplate_h),
    #url(r'^loadcellline/(?P<barcode>[\w|\W]+)/$', loadcell_h),
    url(r'^info/containertype/$', infoconttype_h),
    url(r'^info/geometry/$', infogeometry_h),
    url(r'^geometry/create/(?P<idgeom>[\w|\W]+)$', geometrycreate_h),
    url(r'^freecontainer/(?P<tipo>[\w|\W]+)/$', freecontainer_h),
    #url(r'^return/(?P<listabarc>[\w|\W]+)/$', return_h),
    url(r'^list/container/(?P<listabarc>[\w|\W]+)/$', listacont_h),
    url(r'^check/listcontainer/$', checklistacont_h),
    url(r'^canc/father/$', cancfather_h),
    url(r'^generic/type/(?P<tipo>[\w|\W]+)/$', generic_type_h),
    url(r'^positions/empty/(?P<cod>[\w|\W]+)/(?P<tipocont>[\w|\W]+)/(?P<tipoaliq>[\w|\W]+)$', empty_pos_h),
    url(r'^info/container/(?P<barcode>[\w|\W]+)/$', infocontainer_h),
    url(r'^validate/container$', validatecontainer_h),
    url(r'^check/presence/$', checkpresence_h),
    url(r'^change/barcode/$', changebarcode_h),
    url(r'^info/relationship/$', inforelationship_h),
    url(r'^info/aliquot/$', infoaliquot_h),
    url(r'^get/infocontainer/(?P<barcode>[\w|\W]+)/$', getinfocontainer_h),
    url(r'^containertype/info/(?P<name>[\w|\W]+)/(?P<pezzi>[\w|\W]+)/$', containertypeinfo_h),
    url(r'^save/slide/$', saveslide_h),

    url(r'^restore/$', restorealiquot_h),
    
    url(r'^query/containertype$', query_conttype_h),
    url(r'^query/feature$', query_feature_h),
    url(r'^query/featurevalue$', query_featurevalue_h),
    url(r'^query/parent$', query_parent_h),
    
    url(r'^query/containers$', query_containers_h),
    url(r'^query/positions$', query_positions_h),
    url(r'^query/cont_rel$', query_relations_h),
    
    url(r'^login$', loginResource),
    url(r'^logout$', logoutResource),
)

