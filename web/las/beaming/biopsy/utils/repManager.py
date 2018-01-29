from __init__ import *


def uploadRepFile(data, fileLocation):
    print 'uploadRepFile'
    repositoryUrl = Urls.objects.get(id_webservice=WebService.objects.get(name='repository').id, available=True)
    print repositoryUrl.url
    r = requests.post(repositoryUrl.url+ "api.uploadFile", data=data, files={'file': open(fileLocation)}, verify=False)
    print r.text
    response = json.loads(r.text)
    print response
    if response['status'] == "Ok":
        return response['objectId']
    else:
        return "Fail"


def uploadExperiment(data, fileLocation):
    print 'uploadExperiment'
    repositoryUrl = Urls.objects.get(id_webservice=WebService.objects.get(name='repository').id, available=True)
    print repositoryUrl.url
    files = {}
    for f in os.listdir(fileLocation):
        files[f] = open(os.path.join(fileLocation, f))
    r = requests.post(repositoryUrl.url+ "api.uploadExperiment", data=data, files=files, verify=False)
    #print r.text
    response = json.loads(r.text)
    print response
    if response['status'] == "Ok":
        return response['objectId']
    else:
        return "Fail"
