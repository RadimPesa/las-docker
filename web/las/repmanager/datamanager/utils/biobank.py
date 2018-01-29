from __init__ import *

def retrieveAliquots (aliq_biobank):
    biobankUrl = Urls.objects.get(id_webservice=WebService.objects.get(name='biobank').id, available=True)
    print biobankUrl.url + "api/derivative/"+aliq_biobank
    u = urllib2.urlopen(biobankUrl.url + "api/derivative/"+aliq_biobank)
    res=u.read()
    res=ast.literal_eval(res)
    return res


def updateAliquots(data):
    biobankUrl = Urls.objects.get(id_webservice=WebService.objects.get(name='biobank').id, available=True)
    u = urllib2.urlopen(biobankUrl.url + "update/volume/", data)
    res=u.read()

    