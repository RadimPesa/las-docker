from __init__ import *

def retrieveAliquots (aliq_biobank, operator):
    biobankUrl = Urls.objects.get(id_webservice=WebService.objects.get(name='biobank').id, available=True)
    req = urllib2.Request(biobankUrl.url + "api/derivative/"+aliq_biobank + "/" + operator, headers={"workingGroups" : get_WG_string()})
    u = urllib2.urlopen(req)
    res=u.read()
    res=ast.literal_eval(res)
    return res


def updateAliquots(data):
    biobankUrl = Urls.objects.get(id_webservice=WebService.objects.get(name='biobank').id, available=True)
    req = urllib2.Request(biobankUrl.url + "update/volume/", data=data, headers={"workingGroups" : get_WG_string()})
    u = urllib2.urlopen(req)
    res=u.read()

def setExperiment (aliquots):
    biobankUrl = Urls.objects.get(id_webservice=WebService.objects.get(name='biobank').id, available=True)
    aliquots = json.dumps(aliquots)
    data = urllib.urlencode({'aliquots':aliquots, 'experiment':'MicroArray'})
    req = urllib2.Request(biobankUrl.url + "api/experiment/confirm", data=data, headers={"workingGroups" : get_WG_string()})
    u = urllib2.urlopen(req)
    res = u.read()
    res = json.loads(res)
    print res
    if res['data'] != 'OK':
        raise Exception('Problem connecting with biobank for experimental aliquots')

def resetAliquotRequested (aliquots, operator):
    biobankUrl = Urls.objects.get(id_webservice=WebService.objects.get(name='biobank').id, available=True)
    aliquots = json.dumps(aliquots)
    data = urllib.urlencode({'aliquots':aliquots, 'experiment':'MicroArray', 'operator':operator})
    req = urllib2.Request(biobankUrl.url + "api/experiment/canc", data=data, headers={"workingGroups" : get_WG_string()})
    u = urllib2.urlopen(req)
    res = u.read()
    res = json.loads(res)
    print res
    if res['data'] != 'OK':
        raise Exception('Problem connecting with biobank for experimental aliquots')    