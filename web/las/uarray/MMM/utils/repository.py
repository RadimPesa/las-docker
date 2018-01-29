from __init__ import *
import requests

def getLink(link, typeO):
    print 'getlink'
    try:
        repositoryUrl = Urls.objects.get(id_webservice=WebService.objects.get(name='repository').id, available=True)
        print '---' + repositoryUrl.url + '-----'
        u = urllib2.urlopen(repositoryUrl.url + "api.getlink/"+ link + "/" + typeO)
        res=u.read()
        print res
        res=ast.literal_eval(res)
        return res
    except Exception, e:
        print e
        return {'response':'Bad request'}

def retrieveFile(request, link):
    if request.method == "GET":
        repositoryUrl = Urls.objects.get(id_webservice=WebService.objects.get(name='repository').id, available=True)
        r = requests.get(repositoryUrl.url + "get_file/"+ link, verify=False)
        response = HttpResponse(r.content)
        for key, value in r.headers.items():
            if key != 'transfer-encoding':
                response[key] = value
        return response
        
def getUarrayNodeData(alList):
    
    try:
        repositoryUrl = Urls.objects.get(id_webservice=WebService.objects.get(name='repository').id, available=True)
        values = {'genid' : json.dumps(alList)}
        print values, repositoryUrl.url
        r = requests.get(repositoryUrl.url + 'api.getuarraysample', params=values, verify = False)
        print r.text
        aliquots = json.loads(r.text)

              
        hybevents = set([x['hybevent'] for x in aliquots['samples']])
        hevents = HybridPlan.objects.filter(id__in=hybevents)
        hDict = {}
        for h in hevents:
            hDict[str(h.id)] = h
        print hDict
        scanevents = set([x['scan'] for x in aliquots['samples']])
        sevents = ScanEvent.objects.filter(id__in=scanevents)
        scanDict = {}
        for s in sevents:
            scanDict[str(s.id)] = s
        print scanDict
        samples = aliquots['samples']
        for al in samples:
            al['scan_prot'] = scanDict[al['scan']].idProtocol.name
            al['scan_note'] = scanDict[al['scan']].notes
            al['scan_date'] = str(scanDict[al['scan']].endScanTime)
            al['hyb_date'] = str(hDict[al['hybevent']].timehybrid)
        return samples
    except Exception, e:
        print e
        return []


def getUarraychip (barcode):
    try:
        repositoryUrl = Urls.objects.get(id_webservice=WebService.objects.get(name='repository').id, available=True)
        values = {'barcode' : barcode}
        print values, repositoryUrl.url+ 'api.getuarraychip'
        r = requests.get(repositoryUrl.url + 'api.getuarraychip', params=values, verify = False)
        #print r.text
        return json.loads(r.text)
    except Exception, e:
        print e
        return []