from django.contrib import admin
from caquery._caQuery.models import *

admin.site.register(GenIDFieldType)
admin.site.register(GenIDType)
admin.site.register(GenIDField)
admin.site.register(GenIDFieldValue)
admin.site.register(QueryableEntity)
admin.site.register(JoinedTable)
admin.site.register(JoinedTable_has_DSRelationship)
admin.site.register(QueryPath)
admin.site.register(Output)
admin.site.register(Output_has_JTAttribute)