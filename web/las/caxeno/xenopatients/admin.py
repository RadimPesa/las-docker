from xenopatients.models import *
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

class GAdmin(admin.ModelAdmin):
    list_display = ('name', 'creationDate', 'id_protocol')

class PExAdmin(admin.ModelAdmin):
    list_display = ('id_mouse', 'id_scope', 'done')

class SIhSAdmin(admin.ModelAdmin):
    list_display = ('id_status', 'id_info')

class ChangeStatusAdmin(admin.ModelAdmin):
    list_display = ('from_status', 'to_status')

class SourceAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')

class DrugsAdmin(admin.ModelAdmin):
    list_display = ('name','description')

class ViaAdmin(admin.ModelAdmin):
    list_display = ('description',)

class StatusAdmin(admin.ModelAdmin):
    list_display = ('name','description','default')

class MTAdmin(admin.ModelAdmin):
    list_display = ('name','description')

class SDAdmin(admin.ModelAdmin):
    list_display = ('description',)

class CRGAdmin(admin.ModelAdmin):
    list_display = ('id','name')

class SeriesAdmin(admin.ModelAdmin):
    list_display = ('id', 'date', 'notes', 'id_type')
    #list_filter = ['date']
    #date_hierarchy = 'date'

class MSAdmin(admin.ModelAdmin):
    list_display = ('mouse_type_name','officialName','linkToDoc')

class MiceAdmin(admin.ModelAdmin):
    list_display = ('barcode','id_status')#, 'id_genealogy')
    search_fields=['barcode']

class EDAdmin(admin.ModelAdmin):
    list_display = ('id','id_series', 'id_mouse')

#class AliquotAdmin(admin.ModelAdmin):
#    list_display = ('id_explant', 'id_genealogy')

class MeasureAdmin(admin.ModelAdmin):
    list_display = ('id','id_type', 'x_measurement', 'y_measurement')

class IDAdmin(admin.ModelAdmin):
    list_display = ('id','id_series', 'aliquots_id', 'bad_quality_flag')

class MeasSAdmin(admin.ModelAdmin):
    list_display = ('id_operator','date')
    list_filter = ['date']
    #date_hierarchy = 'date'

class MMAdmin(admin.ModelAdmin):
    list_display = ('id', 'notes')

class QVAdmin(admin.ModelAdmin):
    list_display = ('value','description')

class QualAdmin(admin.ModelAdmin):
    list_display = ('id_value','id_mouse', 'id_series')

class QuantAdmin(admin.ModelAdmin):
    list_display = ('x_measurement','y_measurement','z_measurement', 'volume','weight','id_mouse', 'id_series','notes')
    search_fields=['x_measurement','y_measurement','volume','notes']

class ArmsAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'duration', 'forces_explant')

class DAAdmin(admin.ModelAdmin):
    list_display = ('id_via', 'drugs_id', 'arms_id', 'start_step', 'end_step', 'dose', 'schedule')

class MhAAdmin(admin.ModelAdmin):
    list_display = ('id_mouse', 'id_protocols_has_arms', 'id_operator', 'start_date')

class TissueTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'abbreviation')

class UrlsAdmin(admin.ModelAdmin):
    list_display = ('url', 'default')

class UrlStorageAdmin(admin.ModelAdmin):
    list_display = ('address', 'default')

class ToSAdmin(admin.ModelAdmin):
    list_display = ('id', 'description')

class ProtocolAdmin(admin.ModelAdmin):
    list_display = ('name','description')

class PhAAdmin(admin.ModelAdmin):
    list_display = ('id_protocol', 'id_arm')

admin.site.register(Groups, GAdmin)
admin.site.register(Programmed_explant, PExAdmin)
admin.site.register(Status_info_has_status, SIhSAdmin)
admin.site.register(Status_info)
admin.site.register(ChangeStatus, ChangeStatusAdmin)
admin.site.register(Source, SourceAdmin)
admin.site.register(Scope_details, SDAdmin)
admin.site.register(Series, SeriesAdmin)
admin.site.register(Mouse_strain, MSAdmin)
admin.site.register(Mice, MiceAdmin)
admin.site.register(Aliquots)
admin.site.register(Drugs, DrugsAdmin)
admin.site.register(Via_mode, ViaAdmin)
admin.site.register(Status, StatusAdmin)
admin.site.register(Qualitative_values, QVAdmin)
admin.site.register(Qualitative_measure, QualAdmin)
admin.site.register(Quantitative_measure, QuantAdmin)
admin.site.register(Explant_details, EDAdmin)
admin.site.register(Implant_details, IDAdmin)
admin.site.register(Measurements_series, MeasSAdmin)
admin.site.register(Arms, ArmsAdmin)
admin.site.register(Details_arms, DAAdmin)
admin.site.register(Mice_has_arms, MhAAdmin)
admin.site.register(Site)
admin.site.register(Urls, UrlsAdmin)
admin.site.register(UrlStorage, UrlStorageAdmin)
admin.site.register(TissueType, TissueTypeAdmin)
admin.site.register(Type_of_serie, ToSAdmin)
admin.site.register(Protocols, ProtocolAdmin)
admin.site.register(Protocols_has_arms, PhAAdmin)
admin.site.register(BioMice)
