import os, json, requests

#funzioni per la gestione e il salvataggio del file nel repository
def handle_uploaded_file(f, folderDest,name):
    destination = open(os.path.join(folderDest, name), 'wb+')
    for chunk in f:
        destination.write(chunk)
    destination.close()
    return os.path.join(folderDest, name)

def uploadRepFile(data, fileLocation, repositoryUrl):
    print 'uploadRepFile'
    #repositoryUrl = 'https://gene.polito.it/repmanager'
    print 'repositoryUrl',repositoryUrl
    r = requests.post(repositoryUrl+ '/api.uploadFile', data=data, files={'file': open(fileLocation)}, verify=False)

    print r.text
    response = json.loads(r.text)
    print response
    if response['status'] == 'Ok':
        return response['objectId']
    else:
        return 'Fail'

# remove files if they are in tmp directory
def remove_uploaded_files(filelist):
    print filelist
    for f in filelist:
        if os.path.split(f)[0] == os.path.split(settings.TEMP_URL)[0]:
            print 'Removing file: ' + str(os.path.split(f)[1])
            os.remove(f)