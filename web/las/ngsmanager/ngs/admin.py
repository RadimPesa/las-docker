from django.contrib import admin
from models import *

class AliquotAdmin(admin.ModelAdmin):
    list_display = ('genId','date','owner','exhausted','volume','concentration','label_request','description')
    search_fields=['genId']

class AliquotHasExperimentAdmin(admin.ModelAdmin):
    list_display = ('aliquot_id','idExperiment','feature_id','value')
    search_fields=['value']

class AliquotHasRequestAdmin(admin.ModelAdmin):
    list_display = ('aliquot_id','request_id','feature_id','value')
    search_fields=['value']
    
class ExperimentAdmin(admin.ModelAdmin):
    list_display = ('time_creation','time_executed','title','description','idOperator','request_id')

class FeatureAdmin(admin.ModelAdmin):
    list_display = ('name','measureUnit')

class MeasurementEventAdmin(admin.ModelAdmin):
    list_display = ('aliquot_id','experiment_id','namefile','link_file')
    
class RequestAdmin(admin.ModelAdmin):
    list_display = ('idOperator','timestamp','title','description','owner','pending','timechecked','source')    
    
class UrlAdmin(admin.ModelAdmin):
    list_display = ('url','available','id_webservice')
    


admin.site.register(Aliquot,AliquotAdmin)
admin.site.register(Aliquot_has_Experiment,AliquotHasExperimentAdmin)
admin.site.register(Aliquot_has_Request,AliquotHasRequestAdmin)
admin.site.register(Experiment,ExperimentAdmin)
admin.site.register(Feature,FeatureAdmin)
admin.site.register(MeasurementEvent,MeasurementEventAdmin)
admin.site.register(Request,RequestAdmin)
admin.site.register(WebService)
admin.site.register(Urls,UrlAdmin)