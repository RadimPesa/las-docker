from __init__ import *

def getMdamTemplates (templateList):
    mdamUrl = Urls.objects.get(id_webservice=WebService.objects.get(name='mdam').id, available=True)
    url = mdamUrl.url + "api/describetemplate/"
    templates = []
    for t in templateList:
        data = urllib.urlencode({'template_id':t})
        req = urllib2.Request(url + "?" + data, headers={"workingGroups" : get_WG_string()})
        u = urllib2.urlopen(req)
        res=u.read()
        res=ast.literal_eval(res)
        templates.append(res)
    return templates

def dictIntersect(dict1,dict2):
    res={}
    for item in dict1.keys():
        if dict2.has_key(item):
            res[item]=dict2[item]
    return res

def getAlColl(params, wg, url):
    ''' Template description
        "name": "Aliquot of a collection",
        "description": "Filter based on collection protocol, patient code, informed consent",
        "parameters": [
            {
                "type": 7,
                "description": "",
                "name": "WG",
                "id": 0
            },
            {
                "type": 5,
                "description": "",
                "name": "Patient code",
                "id": 1
            },
            {
                "type": 5,
                "description": "",
                "name": "Informed consent",
                "id": 2
            },
            {
                "type": 5,
                "description": "",
                "name": "Collection protocol",
                "id": 3
            }
        ],
        "id": "41"
    '''
    values= [{'id':'0', 'values':wg}]
    for pid, pvalues in params.items():
        if pid != '0':
            if len(pvalues):
                values.append({'id':pid, 'values': pvalues})


    values_to_send = {'template_id':41, 'parameters':json.dumps(values)} # CHANGE TEMPLATE ID
    print values_to_send
    data = urllib.urlencode(values_to_send)
    try:
        u = urllib2.urlopen(url, data)
    except Exception, e:
        print e
        print "An error occurred while trying to retrieve data from "+str(url)   

    res=u.read()
    result=json.loads(res)
    #print 'Aliquot'
    #print result
    
    resSet = {}
    # x[8] = array of translator results (i.e. last element of the row)
    # x[8][0] = array of results for translator "Container"
    # translator results can either include 0 rows or 1 row
    #current_aliquots[x[1]] = [  x[8][0][0][0] if len(x[8][0]) > 0 else None, # field #0 = Barcode

    for x in result['body']:
        g = GenealogyID(x[1]) # x[1] genid
        resSet[g.getGenID()] = ''
        if len(x[8][0]):
            resSet[g.getGenID()] = x[8][0][0][0] 
        
    return resSet


def getAlCont(params, wg, url):
    ''' Template description
        "name": "Aliquots with barcode",
        "description": "Aliquots with barcode filter and output",
        "parameters": [
            {
                "type": 4,
                "description": "",
                "name": "Barcode",
                "id": 0
            },
            {
                "type": 7,
                "description": "",
                "name": "WG",
                "id": 1
            }
        ],
        "id": "44"
    '''

    values= [{'id':'1', 'values':wg}]
    for pid, pvalues in params.items():
        if pid != '1':
            if len(pvalues):
                values.append({'id':pid, 'values': pvalues})

    values_to_send = {'template_id':44, 'parameters':json.dumps(values)} # CHANGE TEMPLATE ID
    print values_to_send
    data = urllib.urlencode(values_to_send)
    try:
        u = urllib2.urlopen(url, data)
    except Exception, e:
        print e
        print "An error occurred while trying to retrieve data from "+str(url)   

    res=u.read()
    result=json.loads(res)
    #print 'Aliquot'
    #print result
    
    resSet = {}
    # x[8] = array of translator results (i.e. last element of the row)
    # x[8][0] = array of results for translator "Container"
    # translator results can either include 0 rows or 1 row
    #current_aliquots[x[1]] = [  x[8][0][0][0] if len(x[8][0]) > 0 else None, # field #0 = Barcode

    for x in result['body']:
        g = GenealogyID(x[1]) # x[1] genid
        resSet[g.getGenID()] = ''
        if len(x[8][0]):
            resSet[g.getGenID()] = x[8][0][0][0] 
        
    return resSet

def getAllGenid(genidsQuery, wg, url):
    ''' Template description
        "name": "Aliquots genid",
        "description": "Aliquots filtered with genid, output container",
        "parameters": [
            {
                "type": 4,
                "description": "",
                "name": "Genealogy ID",
                "id": 0
            },
            {
                "type": 7,
                "description": "",
                "name": "WG",
                "id": 1
            }
        ],
        "id": "45"
    '''
    print genidsQuery
    values= [{'id':'0', 'values': genidsQuery}, {'id':'1', 'values':wg}]

    values_to_send = {'template_id':45, 'parameters':json.dumps(values)} # CHANGE TEMPLATE ID
    print values_to_send
    data = urllib.urlencode(values_to_send)
    try:
        u = urllib2.urlopen(url, data)
    except Exception, e:
        print e
        print "An error occurred while trying to retrieve data from "+str(url)   

    res=u.read()
    result=json.loads(res)
    #print 'Aliquot'
    #print result
    
    resSet = {}
    # x[8] = array of translator results (i.e. last element of the row)
    # x[8][0] = array of results for translator "Container"
    # translator results can either include 0 rows or 1 row
    #current_aliquots[x[1]] = [  x[8][0][0][0] if len(x[8][0]) > 0 else None, # field #0 = Barcode

    for x in result['body']:
        g = GenealogyID(x[1]) # x[1] genid
        resSet[g.getGenID()] = ''
        if len(x[8][0]):
            resSet[g.getGenID()] = x[8][0][0][0] 
        
    return resSet