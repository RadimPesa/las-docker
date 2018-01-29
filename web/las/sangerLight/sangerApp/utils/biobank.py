from __init__ import *

def retrieveAliquots (aliq_biobank, operator):
    biobankUrl = Urls.objects.get(id_webservice=WebService.objects.get(name='biobank').id, available=True)
    url = biobankUrl.url + "api/derivative/"+aliq_biobank + "/" + operator
    req = urllib2.Request(url, headers={"workingGroups" : get_WG_string()})
    u = urllib2.urlopen(req)
    #u = urllib2.urlopen()
    res=u.read()
    res=ast.literal_eval(res)
    return res


def updateAliquots(data):
    biobankUrl = Urls.objects.get(id_webservice=WebService.objects.get(name='biobank').id, available=True)
    url = biobankUrl.url + "update/volume/"
    req = urllib2.Request(url, data=data, headers={"workingGroups" : get_WG_string()})
    u = urllib2.urlopen(req)
    res=u.read()


def setExperiment (aliquots):
    biobankUrl = Urls.objects.get(id_webservice=WebService.objects.get(name='biobank').id, available=True)
    url = biobankUrl.url + "api/experiment/confirm"
    aliquots = json.dumps(aliquots)
    data = urllib.urlencode({'aliquots':aliquots, 'experiment':'SangerSequencing'})
    req = urllib2.Request(url, data=data, headers={"workingGroups" : get_WG_string()})
    u = urllib2.urlopen(req)
    res = u.read()
    res = json.loads(res)
    print res
    if res['data'] != 'OK':
        raise Exception('Problem connecting with biobank for experimental aliquots')

def resetAliquotRequested (aliquots):
    biobankUrl = Urls.objects.get(id_webservice=WebService.objects.get(name='biobank').id, available=True)
    url = biobankUrl.url + "api/experiment/canc"
    aliquots = json.dumps(aliquots)
    data = urllib.urlencode({'aliquots':aliquots, 'experiment':'SangerSequencing'})
    req = urllib2.Request(url, data=data, headers={"workingGroups" : get_WG_string()})
    u = urllib2.urlopen(req)
    res = u.read()
    res = json.loads(res)
    print res
    if res['data'] != 'OK':
        raise Exception('Problem connecting with biobank for experimental aliquots')    

 
