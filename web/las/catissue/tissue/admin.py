from catissue.tissue.models import *
from django.contrib import admin
from django.contrib.admin.templatetags.admin_list import date_hierarchy
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

class AliquotAdmin(admin.ModelAdmin):
    list_display = ('barcodeID','uniqueGenealogyID','idSamplingEvent','idAliquotType',
                    'timesUsed','availability','derived','archiveDate')
    search_fields=['uniqueGenealogyID','barcodeID']

class AliquotDerScheduleAdmin(admin.ModelAdmin):
    list_display = ('idAliquot','idDerivationSchedule','idDerivedAliquotType','idDerivationProtocol',
                    'idKit','derivationExecuted','operator','failed','loadQuantity',
                    'volumeOutcome','initialDate','measurementExecuted','aliquotExhausted','deleteTimestamp',
                    'deleteOperator','validationTimestamp','notes','idPlanRobot','idPlanDilution')

class AliquotExperimentAdmin(admin.ModelAdmin):
    list_display = ('idAliquot','idExperiment','idExperimentSchedule','takenValue','remainingValue','operator',
                    'experimentDate','aliquotExhausted','confirmed','fileInserted','notes','deleteTimestamp','deleteOperator','validationTimestamp')
    search_fields=['takenValue','remainingValue','operator','experimentDate','notes']
    
class AliquotFeatureAdmin(admin.ModelAdmin):
    list_display = ('idAliquot','idFeature','value')
    search_fields=['value']

class AliquotLabelScheduleAdmin(admin.ModelAdmin):
    list_display = ('idAliquot','idLabelSchedule','idLabelConfiguration','idSamplingEvent','operator','executionDate',
                    'executed','fileInsertionDate','fileInserted','notes','validationTimestamp','deleteTimestamp','deleteOperator')
    
class AliquotPosScheduleAdmin(admin.ModelAdmin):
    list_display = ('idAliquot','idPositionSchedule','positionExecuted','notes','deleteTimestamp','deleteOperator')
    
class AliquotQualScheduleAdmin(admin.ModelAdmin):
    list_display = ('idAliquot','idQualitySchedule','revaluationExecuted','validationTimestamp','operator','idPlanRobot','deleteTimestamp','deleteOperator')

class AliquotSlideScheduleAdmin(admin.ModelAdmin):
    list_display = ('idAliquot','idSlideSchedule','idSamplingEvent','idSlideProtocol','operator','aliquotExhausted',
                    'executionDate','executed','notes','deleteTimestamp','deleteOperator')

class AliquotSplitScheduleAdmin(admin.ModelAdmin):
    list_display = ('idAliquot','idSplitSchedule','idSamplingEvent','splitExecuted','aliquotExhausted','validationTimestamp',
                    'operator','idPlanRobot','deleteTimestamp','deleteOperator')
    
class AliquotTransferScheduleAdmin(admin.ModelAdmin):
    list_display = ('idAliquot','idTransfer')
    
class AliquotTypeAdmin(admin.ModelAdmin):
    list_display = ('abbreviation','longName','type')    
    
class AliquotTypeExpAdmin(admin.ModelAdmin):
    list_display = ('idExperiment','idAliquotType')
    
class AliquotVectorAdmin(admin.ModelAdmin):
    list_display = ('name','abbreviation')

class BlockBioentityAdmin(admin.ModelAdmin):
    list_display = ('idBlockProcedure','genealogyID')
    
class BlockProcedureAdmin(admin.ModelAdmin):
    list_display = ('workGroup','genealogyID','extendToChildren','operator','executionTime')
    
class ClinicalFeatureAdmin(admin.ModelAdmin):
    list_display = ('name','measureUnit','type','idClinicalFeature')

class ClinicalFeatureCollectionTypeAdmin(admin.ModelAdmin):
    list_display = ('idClinicalFeature','idCollectionType','value')
    search_fields=['value']

class CollectionAdmin(admin.ModelAdmin):
    list_display = ('itemCode','idCollectionType','idSource','collectionEvent','patientCode','idCollectionProtocol')
    search_fields=['itemCode','collectionEvent','patientCode']
    
class CollectionClinicalFeatureAdmin(admin.ModelAdmin):
    list_display = ('idCollection','idSamplingEvent','idClinicalFeature','value')
    search_fields=['value']

class CollectionProtocolAdmin(admin.ModelAdmin):
    list_display = ('name','title','project','projectDateRelease','informedConsent',
                    'informedConsentDateRelease','ethicalCommittee','approvalDocument',
                    'approvalDate','get_defaultSharings')

class CollectionProtocolInvestAdmin(admin.ModelAdmin):
    list_display = ('idCollectionProtocol','idPrincipalInvestigator')
    
class CollectionProtocolParticipAdmin(admin.ModelAdmin):
    list_display = ('idCollectionProtocol','idParticipant')
    
class CollectionProtocolSponsorAdmin(admin.ModelAdmin):
    list_display = ('idCollectionProtocol','idSponsor')
    
class CollectionTypeAdmin(admin.ModelAdmin):
    list_display = ('abbreviation','longName','type')
    
class DerEventAdmin(admin.ModelAdmin):
    list_display = ('idSamplingEvent','idAliqDerivationSchedule','derivationDate','operator')
    date_hierarchy='derivationDate'
    
class DerProtocolAdmin(admin.ModelAdmin):
    list_display = ('idKitType','name')
    
class DerScheduleAdmin(admin.ModelAdmin):
    list_display = ('scheduleDate','operator')
    date_hierarchy='scheduleDate'
    
class DrugAdmin(admin.ModelAdmin):
    list_display = ('name','externalId')
    
class ExperimentAdmin(admin.ModelAdmin):
    list_display = ('name','folder')

class ExperimentFileAdmin(admin.ModelAdmin):
    list_display = ('idAliquotExperiment','fileName','linkId','idFileType')

class ExperimentScheduleAdmin(admin.ModelAdmin):
    list_display = ('scheduleDate','operator')
    date_hierarchy='scheduleDate'
    
class FeatureAdmin(admin.ModelAdmin):
    list_display = ('idAliquotType','name','measureUnit')

'''class FeatureDerivationAdmin(admin.ModelAdmin):
    list_display = ('name')'''

class FeatureDerAliqTypeAdmin(admin.ModelAdmin):
    list_display = ('idFeatureDerivation','idAliqType','unityMeasure')

class FeatureDerProtocolAdmin(admin.ModelAdmin):
    list_display = ('idDerProtocol','idFeatureDerivation','value','unityMeasure')
    
class FeatureSlideProtocolAdmin(admin.ModelAdmin):
    list_display = ('idSlideProtocol','idFeatureDerivation','value','unityMeasure')

class FileTypeAdmin(admin.ModelAdmin):
    list_display = ('name','abbreviation')
    
class FileTypeExpAdmin(admin.ModelAdmin):
    list_display = ('idExperiment','idFileType')
    
class InstrumentAdmin(admin.ModelAdmin):
    list_display = ('code','name','manufacturer','description')

class KitAdmin(admin.ModelAdmin):
    list_display = ('idKitType','barcode','openDate','expirationDate','remainingCapacity','lotNumber')
    search_fields=['barcode']
    
class KitTypeAdmin(admin.ModelAdmin):
    list_display = ('name','capacity','producer','catalogueNumber','instructions')

class LabelConfigurationAdmin(admin.ModelAdmin):
    list_display = ('name','idLabelProtocol')

class LabelConfigurationLabelFeatureAdmin(admin.ModelAdmin):
    list_display = ('idLabelConfiguration','idLabelFeature','idLabelMarker','value')

class LabelFeatureAdmin(admin.ModelAdmin):
    list_display = ('name','measureUnit','type')

class LabelFeatureHierarchyAdmin(admin.ModelAdmin):
    list_display = ('idFatherFeature','idChildFeature')

class LabelFileAdmin(admin.ModelAdmin):
    list_display = ('idAliquotLabelSchedule','fileName','originalFileName','fileId','rawNodeId','deleteTimestamp','deleteOperator')

class LabelMarkerLabelFeatureAdmin(admin.ModelAdmin):
    list_display = ('idLabelMarker','idLabelFeature','value')

class LabelProtocolLabelFeatureAdmin(admin.ModelAdmin):
    list_display = ('idLabelProtocol','idLabelFeature','idLabelMarker','value')

class LabelScheduleAdmin(admin.ModelAdmin):
    list_display = ('scheduleDate','operator')
    date_hierarchy='scheduleDate'
    
class MeasureAdmin(admin.ModelAdmin):
    list_display = ('idInstrument','name','measureUnit')

class MaskFieldAdmin(admin.ModelAdmin):
    list_display = ('name','identifier')    

class MaskMaskFieldAdmin(admin.ModelAdmin):
    list_display = ('idMask','idMaskField','encrypted')
    
class MaskOperatorAdmin(admin.ModelAdmin):
    list_display = ('idMask','operator')
    
class MeasurementEventAdmin(admin.ModelAdmin):
    list_display = ('idMeasure','idQualityEvent','value')
    search_fields=['value']
    
class MeasureParamAdmin(admin.ModelAdmin):
    list_display = ('idMeasure','idParameter','idQualityProtocol')

class MouseTissueTypeAdmin(admin.ModelAdmin):
    list_display = ('abbreviation','longName')
    
class ParamAdmin(admin.ModelAdmin):
    list_display = ('name','measureUnit')

class PartSponsorAdmin(admin.ModelAdmin):
    list_display = ('name','base')
    
class PosScheduleAdmin(admin.ModelAdmin):
    list_display = ('scheduleDate','operator')
    date_hierarchy='scheduleDate'
    
class PrincInvestigatorAdmin(admin.ModelAdmin):
    list_display = ('name','surname')
    
class QualEventAdmin(admin.ModelAdmin):
    list_display = ('idQualityProtocol','idQualitySchedule','idAliquot',
                    'idAliquotDerivationSchedule','misurationDate','insertionDate',
                    'operator','quantityUsed')

class QualEventFileAdmin(admin.ModelAdmin):
    list_display = ('idQualityEvent','file','judge','linkId')

class QualProtocolAdmin(admin.ModelAdmin):
    list_display = ('idAliquotType','name','description','mandatoryFields','quantityUsed')
    
class QualScheduleAdmin(admin.ModelAdmin):
    list_display = ('scheduleDate','operator')
    date_hierarchy='scheduleDate'
    
class SamplingAdmin(admin.ModelAdmin):
    list_display = ('idTissueType','idCollection','idSource','idSerie','samplingDate')
    list_filter=['samplingDate']
    date_hierarchy='samplingDate'
    
class SerieAdmin(admin.ModelAdmin):
    list_display = ('operator','serieDate')
    list_filter=['serieDate']
    date_hierarchy='serieDate'

class SlideScheduleAdmin(admin.ModelAdmin):
    list_display = ('scheduleDate','operator')
    date_hierarchy='scheduleDate'
    
class SourceAdmin(admin.ModelAdmin):
    list_display = ('name','type','internalName')

class SplitScheduleAdmin(admin.ModelAdmin):
    list_display = ('scheduleDate','operator')
    date_hierarchy='scheduleDate'
    
class TransferAdmin(admin.ModelAdmin):
    list_display = ('idTransferSchedule','operator','addressTo','plannedDepartureDate','departureDate','departureExecuted',
                    'departureValidated','deliveryDate','deliveryExecuted','deliveryValidated','idCourier','trackingNumber',
                    'deleteTimestamp','deleteOperator')

class TransferScheduleAdmin(admin.ModelAdmin):
    list_display = ('scheduleDate','operator')
    date_hierarchy='scheduleDate'
    
class TissueAdmin(admin.ModelAdmin):
    list_display = ('abbreviation','longName','type')
    
class TransformationAdmin(admin.ModelAdmin):
    list_display = ('idFromType','idToType')
    
class TransformationDerivationAdmin(admin.ModelAdmin):
    list_display = ('idDerivationProtocol','idTransformationChange')

class TransformationSlideAdmin(admin.ModelAdmin):
    list_display = ('idSlideProtocol','idTransformationChange')

class UrlsAdmin(admin.ModelAdmin):
    list_display = ('url', 'default','idWebService')
    
#hamilton
class ChildHamiltonAdmin(admin.ModelAdmin):
    list_display = ('taskid','barcode','volume','vol_kit','concentration','verify_remain','sample_id','run_id')
    search_fields=['barcode']

class LabwareTypeHamiltonAdmin(admin.ModelAdmin):
    list_display = ('name','description')
    
class MeasureHamiltonAdmin(admin.ModelAdmin):
    list_display = ('name','value','sample_id','run_id','version')
    
class OutFileHamiltonAdmin(admin.ModelAdmin):
    list_display = ('path','run_id')

class PlanHamiltonAdmin(admin.ModelAdmin):
    list_display = ('name','timestamp','operator','executed','processed','alerted','labwareid')

class PlanHasProtocolHamiltonAdmin(admin.ModelAdmin):
    list_display = ('plan_id','protocol_id')

class ProtocolHamiltonAdmin(admin.ModelAdmin):
    list_display = ('name','protocol','vol_kit','vol_taken','replica','protocol_type_id')

class ProtStdHamiltonAdmin(admin.ModelAdmin):
    list_display = ('id_protocol','concentration')
    
class RunHamiltonAdmin(admin.ModelAdmin):
    list_display = ('timestamp','plan_id')

class SampleHamiltonAdmin(admin.ModelAdmin):
    list_display = ('genid','barcode','volume','concentration','rank','plan_id')
    search_fields=['genid']

class SampleHasOutFileHamiltonAdmin(admin.ModelAdmin):
    list_display = ('sample_id','out_file_id')


admin.site.register(Aliquot,AliquotAdmin)
admin.site.register(AliquotDerivationSchedule,AliquotDerScheduleAdmin)
admin.site.register(AliquotFeature,AliquotFeatureAdmin)
admin.site.register(AliquotExperiment,AliquotExperimentAdmin)
admin.site.register(AliquotLabelSchedule,AliquotLabelScheduleAdmin)
admin.site.register(AliquotPositionSchedule,AliquotPosScheduleAdmin)
admin.site.register(AliquotQualitySchedule,AliquotQualScheduleAdmin)
admin.site.register(AliquotSlideSchedule,AliquotSlideScheduleAdmin)
admin.site.register(AliquotSplitSchedule,AliquotSplitScheduleAdmin)
admin.site.register(AliquotTransferSchedule,AliquotTransferScheduleAdmin)
admin.site.register(AliquotType,AliquotTypeAdmin)
admin.site.register(AliquotTypeExperiment,AliquotTypeExpAdmin)
admin.site.register(AliquotVector,AliquotVectorAdmin)
admin.site.register(BlockBioentity,BlockBioentityAdmin)
admin.site.register(BlockProcedure,BlockProcedureAdmin)
admin.site.register(ClinicalFeature,ClinicalFeatureAdmin)
admin.site.register(ClinicalFeatureCollectionType,ClinicalFeatureCollectionTypeAdmin)
admin.site.register(Collection,CollectionAdmin)
admin.site.register(CollectionClinicalFeature,CollectionClinicalFeatureAdmin)
admin.site.register(CollectionProtocol,CollectionProtocolAdmin)
admin.site.register(CollectionProtocolInvestigator,CollectionProtocolInvestAdmin)
admin.site.register(CollectionProtocolParticipant,CollectionProtocolParticipAdmin)
admin.site.register(CollectionProtocolSponsor,CollectionProtocolSponsorAdmin)
admin.site.register(CollectionType,CollectionTypeAdmin)
admin.site.register(Courier)
admin.site.register(DerivationEvent,DerEventAdmin)
admin.site.register(DerivationProtocol,DerProtocolAdmin)
admin.site.register(DerivationSchedule,DerScheduleAdmin)
admin.site.register(Drug,DrugAdmin)
admin.site.register(Experiment,ExperimentAdmin)
admin.site.register(ExperimentFile,ExperimentFileAdmin)
admin.site.register(ExperimentSchedule,ExperimentScheduleAdmin)
admin.site.register(Feature,FeatureAdmin)
admin.site.register(FeatureDerivation)
admin.site.register(FeatureDerAliqType,FeatureDerAliqTypeAdmin)
admin.site.register(FeatureDerProtocol,FeatureDerProtocolAdmin)
admin.site.register(FeatureSlideProtocol,FeatureSlideProtocolAdmin)
admin.site.register(FileType,FileTypeAdmin)
admin.site.register(FileTypeExperiment,FileTypeExpAdmin)
admin.site.register(Instrument,InstrumentAdmin)
admin.site.register(Kit,KitAdmin)
admin.site.register(KitType,KitTypeAdmin)
admin.site.register(LabelConfiguration,LabelConfigurationAdmin)
admin.site.register(LabelConfigurationLabelFeature,LabelConfigurationLabelFeatureAdmin)
admin.site.register(LabelFile,LabelFileAdmin)
admin.site.register(LabelFeature,LabelFeatureAdmin)
admin.site.register(LabelFeatureHierarchy,LabelFeatureHierarchyAdmin)
admin.site.register(LabelMarker)
admin.site.register(LabelMarkerLabelFeature,LabelMarkerLabelFeatureAdmin)
admin.site.register(LabelProtocol)
admin.site.register(LabelProtocolLabelFeature,LabelProtocolLabelFeatureAdmin)
admin.site.register(LabelSchedule,LabelScheduleAdmin)
admin.site.register(Mask)
admin.site.register(MaskField,MaskFieldAdmin)
admin.site.register(MaskMaskField,MaskMaskFieldAdmin)
admin.site.register(MaskOperator,MaskOperatorAdmin)
admin.site.register(Measure,MeasureAdmin)
admin.site.register(MeasurementEvent,MeasurementEventAdmin)
admin.site.register(MeasureParameter,MeasureParamAdmin)
admin.site.register(MouseTissueType,MouseTissueTypeAdmin)
admin.site.register(Parameter,ParamAdmin)
admin.site.register(ParticipantSponsor,PartSponsorAdmin)
admin.site.register(PositionSchedule,PosScheduleAdmin)
admin.site.register(PrincipalInvestigator,PrincInvestigatorAdmin)
admin.site.register(QualityEvent,QualEventAdmin)
admin.site.register(QualityEventFile,QualEventFileAdmin)
admin.site.register(QualityProtocol,QualProtocolAdmin)
admin.site.register(QualitySchedule,QualScheduleAdmin)
admin.site.register(SamplingEvent,SamplingAdmin)
admin.site.register(Serie,SerieAdmin)
admin.site.register(SlideProtocol)
admin.site.register(SlideSchedule,SlideScheduleAdmin)
admin.site.register(Source,SourceAdmin)
admin.site.register(SplitSchedule,SplitScheduleAdmin)
admin.site.register(TissueType,TissueAdmin)
admin.site.register(Transfer,TransferAdmin)
admin.site.register(TransferSchedule,TransferScheduleAdmin)
admin.site.register(TransformationChange,TransformationAdmin)
admin.site.register(TransformationDerivation,TransformationDerivationAdmin)
admin.site.register(TransformationSlide,TransformationSlideAdmin)
admin.site.register(Urls,UrlsAdmin)
admin.site.register(WebService)
#hamilton
admin.site.register(ChildHamilton,ChildHamiltonAdmin)
admin.site.register(LabwareTypeHamilton,LabwareTypeHamiltonAdmin)
admin.site.register(MeasureHamilton,MeasureHamiltonAdmin)
admin.site.register(OutFileHamilton,OutFileHamiltonAdmin)
admin.site.register(PlanHamilton,PlanHamiltonAdmin)
admin.site.register(PlanHasProtocolHamilton,PlanHasProtocolHamiltonAdmin)
admin.site.register(ProtocolHamilton,ProtocolHamiltonAdmin)
admin.site.register(ProtocolTypeHamilton)
admin.site.register(ProtStdHamilton,ProtStdHamiltonAdmin)
admin.site.register(RunHamilton,RunHamiltonAdmin)
admin.site.register(SampleHamilton,SampleHamiltonAdmin)
admin.site.register(SampleHasOutFileHamilton,SampleHasOutFileHamiltonAdmin)
