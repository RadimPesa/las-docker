from __init__ import *


def retrieveGeneSymbols(gene):
    url = Urls.objects.get(id_webservice=WebService.objects.get(name='annotation'), available=True)
    values = {'geneSymbol' : gene, 'exactMatch': 'true' }
    print values, url
    r = requests.get(url.url + 'api/genesFromSymbol', params=values, verify = False)

    response = json.loads(r.text)
    print response
    return response

def retrieveMutations(gene):
    url = Urls.objects.get(id_webservice=WebService.objects.get(name='annotation'), available=True)
    values = {'geneId' : gene}
    r = requests.get(url.url + 'api/mutationsFromGeneId', params=values, verify = False)
    response = json.loads(r.text)
    print response
    return response

def getInfoFromId (geneList, mutList):
    url = Urls.objects.get(id_webservice=WebService.objects.get(name='annotation'), available=True)
    values = {'geneList' : json.dumps(geneList), 'mutList':json.dumps(mutList)}
    r = requests.get(url.url + 'api/geneMutNamesFromId', params=values, verify = False)
    print r.text
    response = json.loads(r.text)
    print response
    return response
    #return res

def mutationFromCDSSyntax(geneSymb, mut):
    url = Urls.objects.get(id_webservice=WebService.objects.get(name='annotation'), available=True)
    values = {'geneSymbol' : geneSymb, 'cdsMutSyntax':mut}
    r = requests.get(url.url + 'api/mutationFromCDSSyntax', params=values, verify = False)
    response = json.loads(r.text)
    print response
    return response