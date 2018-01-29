from __init__ import *

def retrieveAliquots (aliq_biobank, operator):
    print 'retrieve aliquots'
    biobankUrl = Urls.objects.get(id_webservice=WebService.objects.get(name='biobank').id, available=True)
    req = urllib2.Request(biobankUrl.url + "api/derivative/"+aliq_biobank + "/" + operator, headers={"workingGroups" : get_WG_string()})
    u = urllib2.urlopen(req)
    res=u.read()
    res=ast.literal_eval(res)
    return res


def updateAliquots(data):
    biobankUrl = Urls.objects.get(id_webservice=WebService.objects.get(name='biobank').id, available=True)
    req = urllib2.Request(biobankUrl.url + "update/volume/", data, headers={"workingGroups" : get_WG_string()})
    u = urllib2.urlopen(req)
    res=u.read()


def setExperiment (aliquots):
    biobankUrl = Urls.objects.get(id_webservice=WebService.objects.get(name='biobank').id, available=True)
    aliquots = json.dumps(aliquots)
    data = urllib.urlencode({'aliquots':aliquots, 'experiment':'Sequenom'})
    req = urllib2.Request(biobankUrl.url + "api/experiment/confirm", data, headers={"workingGroups" : get_WG_string()})
    u = urllib2.urlopen(req)
    res = u.read()
    res = json.loads(res)
    print res
    if res['data'] != 'OK':
        raise Exception('Problem connecting with biobank for experimental aliquots')

def resetAliquotRequested (aliquots):
    biobankUrl = Urls.objects.get(id_webservice=WebService.objects.get(name='biobank').id, available=True)
    aliquots = json.dumps(aliquots)
    data = urllib.urlencode({'aliquots':aliquots, 'experiment':'Sequenom'})
    req = urllib2.Request(biobankUrl.url + "api/experiment/canc", data, headers={"workingGroups" : get_WG_string()})
    u = urllib2.urlopen(req)
    res = u.read()
    res = json.loads(res)
    print res
    if res['data'] != 'OK':
        raise Exception('Problem connecting with biobank for experimental aliquots')    


def getSampleByContainer(barcode, samplePlate):
    try:
        biobankUrl = Urls.objects.get(id_webservice=WebService.objects.get(name='biobank').id, available=True)
    
        req = urllib2.Request(biobankUrl.url + "api/plate/load/" + barcode + "/DNA/stored", headers={"workingGroups" : get_WG_string()})
        u = urllib2.urlopen(req)
        res = u.read()
        res = json.loads(res)
        if res['data'] == 'errore_piastra':
            req = urllib2.Request(biobankUrl.url + "api/plate/load/" + barcode + "/DNA/", headers={"workingGroups" : get_WG_string()})
            u = urllib2.urlopen(req)
            res = u.read()
            res = json.loads(res)
        #print res
        plateContent = []
        for al in res['data']:
            plateContent.append( (al['gen'], al['position']) )
        print set(plateContent), set(samplePlate), set(plateContent) - set(samplePlate)
        if len(set(plateContent) - set(samplePlate)):
            return False
        else:
            return True
    except Exception, e:
        print e
        return False
