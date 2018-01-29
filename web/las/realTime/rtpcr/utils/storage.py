from __init__ import *

def retrieveLayouts ():
    storageUrl = Urls.objects.get(id_webservice=WebService.objects.get(name='storage').id, available=True)
    url = storageUrl.url + "api/info/geometry"
    req = urllib2.Request(url, headers={"workingGroups" : get_WG_string()})
    u = urllib2.urlopen(req)
    res=u.read()
    res=json.loads(res)
    results = []
    for r in res['data']:
        results.append(r)
    return results


def getGeometry (geoId):
    storageUrl = Urls.objects.get(id_webservice=WebService.objects.get(name='storage').id, available=True)
    url = storageUrl.url + "api/geometry/create/" + geoId
    req = urllib2.Request(url, headers={"workingGroups" : get_WG_string()})
    u = urllib2.urlopen(req)
    res=u.read()
    res=json.loads(res)
    return res['data']