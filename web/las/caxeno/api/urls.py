from django.conf.urls.defaults import *
from piston.resource import Resource
from api.handlers import *
from api.tablesValues import *
from api.query import *
from api.exempt import *


id_genealogy_handler = Resource(IdGenealogyHandler)
status_handler = Resource(StatusHandler)
acute_treatment_handler = Resource(AcuteTreatmentHandler)
check_destination_status_handler = Resource(CheckDestinationStatusHandler)
tissue_h = Resource(TissueHandler)
arms_handler = Resource(ArmsHandler)
step_handler = Resource(StepHandler)
give_me_step_handler = Resource(GiveMeStepHandler)
protocol_handler = Resource(ProtocolHandler)
explTable_handler = Resource(ExplTableHandler)
organize_groups_handler = Resource(OrganizeGroupsHandler)
check_group_name_handler = Resource(CheckGroupNameHandler)
mice_of_group_handler = Resource(MiceOfGroupHandler)
info_group_handler = Resource(InfoGroupHandler)
check_group_handler = Resource(CheckGroupHandler)
newGenID = Resource(NewGenIDForImplantHandler)
actionsMice = Resource(ActionsMouse)
pendingMice = Resource(PendingMouse)
duration_treatment = Resource(DurationTreatmentHandler)
mouseForTreat = Resource(MouseForTreatment)
durationArm = Resource(DurationA)
lastWeight = Resource(LastWeight)
newgen = Resource(NewGenIDExplant)
physbio = Resource(FromPhysToBio)
mouseformeasure = Resource(MouseForMeasure)


strain_list = Resource(StrainList)
source_list = Resource(SourceList)
status_list = Resource(StatusList)
lineage_list = Resource(LineageList)
site_list = Resource(SiteList)
scope_list = Resource(ScopeList)
value_list = Resource(ValueList)
drug_list = Resource(DrugList)
operator_list = Resource(OperatorList)
protocol_list = Resource(ProtocolList)
protocol_list2 = Resource(ProtocolList2)
exgroup_list = Resource(ExGroupList)
cancg_list = Resource(CancGroupList)
arms_list = Resource(ArmNameList)

mice = CsrfExemptResource(MiceH)
explants = CsrfExemptResource(ExplantsH)
arm = CsrfExemptResource(ArmH)
protocol = CsrfExemptResource(ProtocolH)
qual = CsrfExemptResource(QualH)
quant = CsrfExemptResource(QuantH)
implants = CsrfExemptResource(ImplantsH)
treats = CsrfExemptResource(TreatmentsH)
groups = CsrfExemptResource(GroupsH)

loginResource = CsrfExemptResource(LoginHandler)
logoutResource = CsrfExemptResource(LogoutHandler)

change_wg_handler = CsrfExemptResource(changeWGBiomiceH)
shareBiomice_handler=CsrfExemptResource(ShareBiomice)

urlpatterns = patterns('',
    url(r'^tissue/$', tissue_h),
    url(r'^genealogy/(?P<barcode>[\w|\W]*)/(?P<site>[\w|\W]*)/$', id_genealogy_handler),
    url(r'^status/(?P<barcode>[A-Za-z=0-9\-]*)$', status_handler),
    url(r'^status/destination/(?P<oldS>[\w|\W]+)2(?P<newS>[\w|\W]+)/(?P<barcode>[\w|\W]*)$', check_destination_status_handler),
    url(r'^acute_treatment/(?P<nameT>[\w|\W]+)$', acute_treatment_handler), #questa dicitura accetta gli spazi nell'url
    url(r'^list_arm/(?P<protocol>[\w|\W]+)$', arms_handler),
    url(r'^list_step/(?P<arm>[\w|\W]+)$', step_handler),
    url(r'^giveMeStep/(?P<statusGantt>[\w|\W]+)/(?P<drugs>[\w|\W]+)$', give_me_step_handler),
    url(r'^protocol/(?P<nameP>[\w|\W]+)$', protocol_handler),
    url(r'^explTable/(?P<barcodeP>[\w|\W]+)/(?P<typeP>[\w|\W]+)/(?P<typeC>[\w|\W]+)$', explTable_handler),
    url(r'^organizeGroups/$', organize_groups_handler),
    url(r'^countGroupName/(?P<name>[\w|\W]+)$', check_group_name_handler),
    url(r'^infoGroup/(?P<name>[\w|\W]+)$', info_group_handler),
    url(r'^checkGroup/(?P<name>[\w|\W]+)$', check_group_handler),
    url(r'^miceOfGroup/(?P<name>[\w|\W]*)$', mice_of_group_handler),
    url(r'^newGenID/$', newGenID),
    url(r'^actionsMouse/(?P<genID>[\w|\W]*)$', actionsMice),
    url(r'^pendingMouse/(?P<idEvent>[\w|\W]*)$', pendingMice),
    url(r'^durationTreatment/(?P<nameA>[\w|\W]*)$', duration_treatment),
    url(r'^mouseForTreat/(?P<barcode>[\w|\W]*)/(?P<group>[\w|\W]*)/(?P<nameT>[\w|\W]*)$', mouseForTreat),
    url(r'^durationA/(?P<nameA>[\w|\W]*)$', durationArm),
    url(r'^lastWeight/(?P<barcode>[\w|\W]*)$', lastWeight),
    url(r'^newGenIDExplant/(?P<oldG>[\w|\W]*)/(?P<tissue>[\w|\W]*)/(?P<typeA>[\w|\W]*)/(?P<counter>[\w|\W]*)$', newgen),
   
    url(r'^mouseformeasure/(?P<barcode>[\w|\W]*)/(?P<site>[\w|\W]*)$', mouseformeasure),
    url(r'^phystobio/(?P<barcode>[\w|\W]*)$', physbio),

    url(r'^changeWGBiomice/$', change_wg_handler),
    url(r'^shareBiomice/$',shareBiomice_handler),

    url(r'^query.mice$', mice),
    url(r'^query.explants$', explants),
    url(r'^query.arm$', arm),
    url(r'^query.protocol$', protocol),
    url(r'^query.qual$', qual),
    url(r'^query.quant$', quant),
    url(r'^query.implants$', implants),
    url(r'^query.treatments$', treats),
    url(r'^query.ex_group$', groups),
    
    url(r'^strainList/$', strain_list),
    url(r'^sourceList/$', source_list),
    url(r'^statusList/$', status_list),
    url(r'^lineageList/$', lineage_list),
    url(r'^siteList/$', site_list),
    url(r'^scopeList/$', scope_list),
    url(r'^qualValueList/$', value_list),
    url(r'^drugList/$', drug_list),
    url(r'^operatorList/$', operator_list),
    url(r'^protocolList/$', protocol_list),
    url(r'^protocolList2/$', protocol_list2),
    url(r'^exgroupList/$', exgroup_list),
    url(r'^cancGroupList/$', cancg_list),
    url(r'^armNameList/$', arms_list),
    
    url(r'^login$', loginResource),
    url(r'^logout$', logoutResource),    
)
