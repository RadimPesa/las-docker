from django.contrib import admin
from models import *
admin.site.register(Chip)
admin.site.register(ChipType)
admin.site.register(Instrument)
admin.site.register(Software)
admin.site.register(Aliquot)
admin.site.register(HybProtocol)
admin.site.register(Assignment)
admin.site.register(Request)
admin.site.register(ScanEvent)
admin.site.register(Aliquot_has_Request)
admin.site.register(Experiment)
admin.site.register(Assignment_has_Scan)
admin.site.register(ScanProtocol)
admin.site.register(Parameter)
admin.site.register(Protocol_has_Parameter_value)

