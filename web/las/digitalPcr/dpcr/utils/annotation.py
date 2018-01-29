from __init__ import *


def retrieveGeneSymbols(gene):
    print "[retrieveGeneSymbols] BEGIN"
    url = Urls.objects.get(id_webservice=WebService.objects.get(name='annotation'), available=True)
    values = {'q' : gene}
    print values, url
    r = requests.get(url.url + 'newapi/geneInfo', params=values, verify = False)
    response = json.loads(r.text)
    print response
    res = {gene: [{'id_gene': x['id'], 'gene_name': x['symbol'], 'chromosome': x['chrom']} for x in response]}
    return res


def retrieveMutations(gene):
    print "[retrieveMutations] BEGIN"
    url = Urls.objects.get(id_webservice=WebService.objects.get(name='annotation'), available=True)
    #values = {'geneId' : gene}
    values = {'annot_type': 'sequence_alteration', 'gene_uuid': gene, 'ext_info': 'true'}
    #r = requests.get(url.url + 'api/mutationsFromGeneId', params=values, verify = False)
    r = requests.get(url.url + 'newapi/searchReferences', params=values, verify = False)
    response = json.loads(r.text)
    print response
    res = [{'aa_mut_syntax': x['hgvs_p'], 'id_mutation': x['uuid'], 'cds_mut_syntax': x['hgvs_c'], 'transcript': x['tx_ac']} for x in response]
    return res

def getInfoFromId (geneList, mutList):
    print "[getInfoFromId] BEGIN"
    url = Urls.objects.get(id_webservice=WebService.objects.get(name='annotation'), available=True)
    values = {'geneList' : json.dumps([x for x in geneList if x !='']), 'mutList':json.dumps([x for x in mutList if x !=''])}
    print values
    r = requests.get(url.url + 'api/geneMutNamesFromId', params=values, verify = False)
    print r.text
    response = json.loads(r.text)
    print response
    return response
    #return res

def mutationFromCDSSyntax(geneSymb, mut):
    print "[mutationFromCDSSyntax] BEGIN"
    url = Urls.objects.get(id_webservice=WebService.objects.get(name='annotation'), available=True)
    values = {'geneSymbol' : geneSymb, 'cdsMutSyntax':mut}
    print values
    r = requests.get(url.url + 'api/mutationFromCDSSyntax', params=values, verify = False)
    response = json.loads(r.text)
    print response
    return response