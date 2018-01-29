from piston.handler import BaseHandler
from _caQuery.models import *

import requests
import zlib

MAX_RESULTS = 10

class AutoComplete(BaseHandler):
    allowed_methods = ('GET')
    def read(self, request):
        print "zzzzzzz"
        api_id = request.GET['id']
        term = request.GET['term']
        try:
            api = AutoCompleteAPI.objects.get(pk=api_id)
            data = {'s': [(api.tableName, api.attrName)],
                    'f': [api.tableName],
                    'fw': [(api.tableName, api.attrName, 'like', ["%%" + term + "%%"], None, None, None)],
                    'geth': False,
                    'distinct': True,
                    'l': MAX_RESULTS,
                    'viewname': ''}
            r = requests.post(api.url, data=zlib.compress(json.dumps(data)), verify=False, headers={'Content-Type': 'application/octet-stream'})
            print r.content
            x = json.loads(zlib.decompress(r.content))
            return [y[0] for y in x]
        except Exception as e:
            print str(e)
            return []

