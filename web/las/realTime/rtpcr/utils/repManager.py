from __init__ import *

def uploadRepFile(data, fileLocation):
    print 'uploadRepFile'
    print data
    print fileLocation
    repositoryUrl = Urls.objects.get(id_webservice=WebService.objects.get(name='repository').id, available=True)
    print repositoryUrl.url+ "api.uploadFile"
    r = requests.post(repositoryUrl.url+ "api.uploadFile", data=data, files={'file': open(fileLocation)}, verify=False)
    response = json.loads(r.text)
    print response
    if response['status'] == "Ok":
        return response['objectId']
    else:
        return "Fail"