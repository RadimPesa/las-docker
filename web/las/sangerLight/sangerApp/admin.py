from django.contrib import admin
from models import *

admin.site.register(Aliquot)
admin.site.register(Aliquot_has_Request)
admin.site.register(Instrument)
#admin.site.register(MeasureType)
admin.site.register(Request)
admin.site.register(Sample)
admin.site.register(WebService)
admin.site.register(Urls)