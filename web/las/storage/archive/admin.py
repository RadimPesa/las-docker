from archive.models import *
from django.contrib import admin

class AliquotAdmin(admin.ModelAdmin):
    list_display = ('genealogyID', 'idContainer','position','startTimestamp','endTimestamp','startOperator','endOperator')
    search_fields=['genealogyID']

class ContainerTypeAdmin(admin.ModelAdmin):
    list_display = ('idGenericContainerType','actualName','name','maxPosition','catalogNumber','producer','linkFile','idGeometry','oneUse')

class GeometryAdmin(admin.ModelAdmin):
    list_display = ('name', 'rules')

class ContainerAdmin(admin.ModelAdmin):
    list_display = ('idContainerType','idFatherContainer','idGeometry', 'position', 'barcode', 'availability', 
                    'full','owner','present','oneUse')
    search_fields=['barcode']

class ContainerAuditAdmin(admin.ModelAdmin):
    list_display = ('idContainerType','idFatherContainer','idGeometry', 'position', 'barcode', 'availability', 
                    'full','owner','present','oneUse','username','_audit_timestamp','_audit_change_type')
    search_fields=['barcode']

class ContainerFeatureAdmin(admin.ModelAdmin):
    list_display = ('idFeature', 'idContainer','value')
    search_fields=['value']

class CTypeHasCTypeAdmin(admin.ModelAdmin):
    list_display = ('idContainer', 'idContained')

class ContainerTypeFeatureAdmin(admin.ModelAdmin):
    list_display = ('idFeature', 'idContainerType')
    
class ContainerInputAdmin(admin.ModelAdmin):
    list_display = ('idContainer', 'idInput')

class ContainerOutputAdmin(admin.ModelAdmin):
    list_display = ('idOutput', 'idContainer')
    
class ContainerRequestAdmin(admin.ModelAdmin):
    list_display = ('idRequest', 'idContainer','executed')

class GenContTypeAdmin(admin.ModelAdmin):
    list_display = ('name','abbreviation')

class RequestAdmin(admin.ModelAdmin):
    list_display = ('date', 'operator')

class OutputAdmin(admin.ModelAdmin):
    list_display = ('date', 'operator')
    
class InputAdmin(admin.ModelAdmin):
    list_display = ('date', 'operator')
    
class DefaultValueAdmin(admin.ModelAdmin):
    list_display = ('abbreviation', 'longName')
    
class FeatureDefaultValueAdmin(admin.ModelAdmin):
    list_display = ('idFeature', 'idDefaultValue')
    
class UrlAdmin(admin.ModelAdmin):
    list_display = ('url', 'default')

admin.site.register(Aliquot, AliquotAdmin)
admin.site.register(ContainerType, ContainerTypeAdmin)
admin.site.register(Geometry, GeometryAdmin)
admin.site.register(Container, ContainerAdmin)
admin.site.register(ContainerAudit, ContainerAuditAdmin)
admin.site.register(ContTypeHasContType, CTypeHasCTypeAdmin)
admin.site.register(Feature)
admin.site.register(GenericContainerType, GenContTypeAdmin)
admin.site.register(ContainerFeature,ContainerFeatureAdmin)
admin.site.register(Request, RequestAdmin)
admin.site.register(ContainerRequest,ContainerRequestAdmin)
admin.site.register(Output, OutputAdmin)
admin.site.register(ContainerOutput,ContainerOutputAdmin)
admin.site.register(Input, InputAdmin)
admin.site.register(ContainerTypeFeature,ContainerTypeFeatureAdmin)
admin.site.register(ContainerInput,ContainerInputAdmin)
admin.site.register(Urls, UrlAdmin)
admin.site.register(DefaultValue, DefaultValueAdmin)
admin.site.register(FeatureDefaultValue, FeatureDefaultValueAdmin)

