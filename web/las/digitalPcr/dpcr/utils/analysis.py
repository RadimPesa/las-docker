from __init__ import *

def getFormulas (elementList):
    print elementList
    url = Urls.objects.get(id_webservice=WebService.objects.get(name='analysis'), available=True)
    values = {'elementList' : json.dumps(elementList)}
    print values
    r = requests.get(url.url + 'api/getformulas', params=values, verify = False)
    print r.text
    response = json.loads(r.text)
    #print response
    return response

def computeFormulas (computationList):
    try:
        url = Urls.objects.get(id_webservice=WebService.objects.get(name='analysis'), available=True)
        values = {'computationList' : computationList}
        print 'sending values'
        r = requests.post(url.url + 'api.computeformulas', data=json.dumps(values), verify = False)
        #print r.text
        response = json.loads(r.text)
        #print response
        return response
    except Exception, e:
        print e 
        return {'status': 'Error', 'description': 'Error in retrieving data'}

def getFormulasByIds (formulaList):
    url = Urls.objects.get(id_webservice=WebService.objects.get(name='analysis'), available=True)
    values = {'formulaList' : json.dumps(formulaList)}
    r = requests.get(url.url + 'api/getformulaIds', params=values, verify = False)
    #print r.text
    response = json.loads(r.text)
    #print response
    return response


def getFormulasNameByIds(formulaList):
    url = Urls.objects.get(id_webservice=WebService.objects.get(name='analysis'), available=True)
    values = {'formulaList' : json.dumps(formulaList)}
    r = requests.get(url.url + 'api/getformulaName', params=values, verify = False)
    #print r.text
    response = json.loads(r.text)
    #print response
    return response
