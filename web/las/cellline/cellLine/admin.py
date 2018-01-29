from cellLine.models import *
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User


class Urls_HandlerAdmin(admin.ModelAdmin): #
	list_display = ('name', 'url')
admin.site.register(Urls_handler, Urls_HandlerAdmin)

class CondProtElemAdmin(admin.ModelAdmin): #
	list_display = ('name', 'condition_protocol_element_id')
admin.site.register(Condition_protocol_element, CondProtElemAdmin)

class CondFeatAdmin(admin.ModelAdmin): #
	list_display = ('name','unity_measure','default_value', 'condition_protocol_element_id')
admin.site.register(Condition_feature, CondFeatAdmin)

class CondhasFeatAdmin(admin.ModelAdmin): #
	list_display = ('value','condition_configuration_id')
admin.site.register(Condition_has_feature, CondhasFeatAdmin)

class AliqAdmin(admin.ModelAdmin): #
	list_display = ('gen_id','archive_details_id','experiment_details_id')
admin.site.register(Aliquots, AliqAdmin)

class ExperDetailsAdmin(admin.ModelAdmin): #
	list_display = ('id','events_id')
admin.site.register(Experiment_details, ExperDetailsAdmin)

class ExperInVitroAdmin(admin.ModelAdmin): #
	list_display = ('genID','barcode_container','position','is_available', 'is_exausted')
admin.site.register(Experiment_in_vitro, ExperInVitroAdmin)

class CellsAdmin(admin.ModelAdmin): #
	list_display = ('genID', 'nickname')
admin.site.register(Cells, CellsAdmin)

class CellDetailsAdmin(admin.ModelAdmin): #
	list_display = ('num_plates','start_date_time','end_date_time')
admin.site.register(Cell_details, CellDetailsAdmin)

class CellDetailsFeatureAdmin(admin.ModelAdmin): #
	list_display = ('cell_details_id','feature_id','start_date_time','end_date_time','operator_id','value')
admin.site.register(Cell_details_feature, CellDetailsFeatureAdmin)

class Cell_cond_conf_Admin(admin.ModelAdmin): #
	list_display = ('id','version')
admin.site.register(Condition_configuration, Cell_cond_conf_Admin)

class Cell_cond_prot_Admin(admin.ModelAdmin): #
	list_display = ('id','protocol_name','creation_date_time')
admin.site.register(Condition_protocol, Cell_cond_prot_Admin)

class Type_events_Admin(admin.ModelAdmin): #
	list_display = ('id','type_name')
admin.site.register(Type_events, Type_events_Admin)

class Events_Admin(admin.ModelAdmin): #
	list_display = ('date_time_event','cellline_users_id', 'type_event_id','cell_details_id')
admin.site.register(Events, Events_Admin)

class Expansion_details_Admin(admin.ModelAdmin): #
	list_display = ('events_id','input_area', 'reduction_factor', 'output_area')
admin.site.register(Expansion_details, Expansion_details_Admin)

class Eliminated_Admin(admin.ModelAdmin): #
	list_display = ('events_id','amount')
admin.site.register(Eliminated_details, Eliminated_Admin)

class Archive_details_Admin(admin.ModelAdmin): #
	list_display = ('experiment_in_vitro_id', 'amount')
admin.site.register(Archive_details, Archive_details_Admin)

class SelectionProtocol_Admin(admin.ModelAdmin): #
	list_display = ('name', 'datasheet')
#admin.site.register(Selection_protocol, SelectionProtocol_Admin)

class SelectionDetails_Admin(admin.ModelAdmin): #
	list_display = ('id','experiment_in_vitro_id')
#admin.site.register(Selection_details, SelectionDetails_Admin)

class Instrument_Admin(admin.ModelAdmin): #
	list_display = ('name', 'code')
admin.site.register(Instrument, Instrument_Admin)

class MeasureType_Admin(admin.ModelAdmin): #
	list_display = ('name', 'unity_measure', 'cell_destroy')
admin.site.register(Measure_type, MeasureType_Admin)

class MeasureDetails_Admin(admin.ModelAdmin): #
	list_display = ('id','events_id')
admin.site.register(Measure_details, MeasureDetails_Admin)

class MeasureEventHas_Admin(admin.ModelAdmin): #
	list_display = ('value', 'datasheet')
admin.site.register(Measure_event_has_measure_type, MeasureEventHas_Admin)

class ConditionHasExperiments_Admin(admin.ModelAdmin): #
	list_display = ('start_time', 'end_time')
admin.site.register(Condition_has_experiments, ConditionHasExperiments_Admin)

class Allowed_values_Admin(admin.ModelAdmin):
    list_display = ('allowed_value','condition_feature_id')
admin.site.register(Allowed_values, Allowed_values_Admin)

class ExternalRequest_Admin(admin.ModelAdmin):
    list_display = ('data','done','action','username','assigner','date_time','deleteTimestamp','deleteOperator')
admin.site.register(External_request, ExternalRequest_Admin)

admin.site.register(Feature)
