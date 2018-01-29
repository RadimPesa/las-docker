from piston.handler import BaseHandler
from _caQuery.models import *

import requests
import zlib

class GetGenIdStruct(BaseHandler):
    allowed_methods = ('GET')
    def read(self, request):
        genid = {}
        for x in GenIDType.objects.all().order_by('name'):
            genid[x.name] = {'fields': [{'name': y.name, 'start': y.start, 'end': y.end, 'ftype': y.field_type.id, 'values': [z.value for z in y.genidfieldvalue_set.all().order_by('value')]} for y in x.genidfield_set.all().order_by('start')], 'relatedQe': x.relatedQE.id if x.relatedQE else None}
        return genid