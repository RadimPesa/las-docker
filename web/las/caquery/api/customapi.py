from piston.handler import BaseHandler
from _caQuery.models import *

import requests
import zlib

MAX_RESULTS = 10

class BiobankSources(BaseHandler):
    allowed_methods = ('GET')
    def read(self, request):
        print "[MDAM - Custom API] BiobankSources"
        try:
            ds = DataSource.objects.get(name='BioBanking Management Module')
            dst = DSTable.objects.get(dataSource=ds,name='source')
            data = {'s': [(dst.name, 'internalName'), (dst.name, 'name')],
                    'f': [dst.name],
                    'geth': False,
                    'distinct': True,
                    'viewname': ''}
            r = requests.post(ds.url + 'runquery/', data=zlib.compress(json.dumps(data)), verify=False, headers={'Content-Type': 'application/octet-stream'})
            print r.content
            x = json.loads(zlib.decompress(r.content))
            return [(y[0],y[1]) for y in x]
        except Exception as e:
            print str(e)
            return []

class BiobankCollectiontypes(BaseHandler):
    allowed_methods = ('GET')
    def read(self, request):
        print "[MDAM - Custom API] BiobankCollectiontypes"
        try:
            ds = DataSource.objects.get(name='BioBanking Management Module')
            dst = DSTable.objects.get(dataSource=ds,name='collectiontype')
            data = {'s': [(dst.name, 'abbreviation'), (dst.name, 'longName')],
                    'f': [dst.name],
                    'geth': False,
                    'distinct': True,
                    'viewname': ''}
            r = requests.post(ds.url + 'runquery/', data=zlib.compress(json.dumps(data)), verify=False, headers={'Content-Type': 'application/octet-stream'})
            print r.content
            x = json.loads(zlib.decompress(r.content))
            return [(y[0],y[1]) for y in x]
        except Exception as e:
            print str(e)
            return []

class BiobankTissuetypes(BaseHandler):
    allowed_methods = ('GET')
    def read(self, request):
        print "[MDAM - Custom API] BiobankTissuetypes"
        try:
            ds = DataSource.objects.get(name='BioBanking Management Module')
            dst = DSTable.objects.get(dataSource=ds,name='tissuetype')
            data = {'s': [(dst.name, 'abbreviation'), (dst.name, 'longName')],
                    'f': [dst.name],
                    'geth': False,
                    'distinct': True,
                    'viewname': ''}
            r = requests.post(ds.url + 'runquery/', data=zlib.compress(json.dumps(data)), verify=False, headers={'Content-Type': 'application/octet-stream'})
            print r.content
            x = json.loads(zlib.decompress(r.content))
            return [(y[0],y[1]) for y in x]
        except Exception as e:
            print str(e)
            return []
