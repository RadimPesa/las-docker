from __init__ import *

def retrieveLayouts ():
    storageUrl = Urls.objects.get(id_webservice=WebService.objects.get(name='storage').id, available=True)
    u = urllib2.urlopen(storageUrl.url + "api/info/geometry")
    res=u.read()
    
    res=json.loads(res)
    results = []
    for r in res['data']:
    	results.append(r)
    print 'List of geometry'
    print results
    return results


def getGeometry (geoId):
    storageUrl = Urls.objects.get(id_webservice=WebService.objects.get(name='storage').id, available=True)
    u = urllib2.urlopen(storageUrl.url + "api/geometry/create/" + geoId)
    res=u.read()
    res=json.loads(res)
    return res['data']

