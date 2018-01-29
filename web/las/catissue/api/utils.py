import json,requests,urllib,urllib2
from catissue.tissue.models import *
from django.db.models import Q


class ClassSimple:
    def __init__(self, c, select):
        self.attributes={}
        for f in c._meta.fields:
            if len(select) == 0:
                self.attributes[f.name] = str(c.__getattribute__(f.name))
            elif f.name in select:
                self.attributes[f.name] = str(c.__getattribute__(f.name))

    def toStr(self):
        output = ''
        a = []
        for k, v in self.attributes.items():
#            output += str(k) + ':' + str(v) + ','

            b={k:str(v)}
            a.append(b)
           
        #return output[:len(output)-1]
        print json.dumps(a)
        return json.dumps(a)

    def getAttributes(self):
        return self.attributes

def TrovaQuality(ali):
    #ho l'aliquota figlia di una derivazione e devo prendere il
    #der event relativo
    print 'ali',ali
    derevent=DerivationEvent.objects.filter(idSamplingEvent=ali.idSamplingEvent)
    if len(derevent)!=0:
        listatemp=[]
        for der in derevent:
            genmadre=der.idAliqDerivationSchedule.idAliquot.uniqueGenealogyID
            print 'genmadre',genmadre
            ge=GenealogyID(genmadre)
            print 'ge',ge
            genfinmadre=ge.getCase()+ge.getTissue()+ge.getGeneration()+ge.getMouse()+ge.getTissueType()
            print 'genfinmadre',genfinmadre
            gef=GenealogyID(ali.uniqueGenealogyID)
            genfinfiglia=gef.getCase()+gef.getTissue()+gef.getGeneration()+gef.getMouse()+gef.getTissueType()
            print 'genfiglia',genfinfiglia
            if genfinmadre==genfinfiglia:
                listatemp.append(der.idAliqDerivationSchedule)
        #prendo il qual event basandomi sull'aliqderschedule oppure
        #su eventuali rivalutazioni del campione. Prendo il valore piu' recente
        qualeve=QualityEvent.objects.filter(Q(idAliquotDerivationSchedule__in=listatemp)|(Q(idAliquot=ali)& ~Q(idQualitySchedule=None))).order_by('-misurationDate','-id')
    #se e' un'aliq esterna non ha un der event
    else:
        qualeve=QualityEvent.objects.filter(Q(idAliquot=ali)& ~Q(idQualitySchedule=None)).order_by('-misurationDate','-id')
    
    print 'qualeve',qualeve
    if len(qualeve)!=0:
        val=''
        i=0
        while i<len(qualeve) and val=='':
            #prendo la misura con il suo valore
            tipomis=Measure.objects.get(Q(name='quality')&Q(measureUnit='RIN'))
            misev=MeasurementEvent.objects.filter(Q(idMeasure=tipomis)&Q(idQualityEvent=qualeve[i]))
            print 'misev',misev
            i=i+1
            if len(misev)!=0:
                val=str(misev[0].value)
    return val

def translateLineage(lineage):
    try:
        result = 0
        if lineage[0].isdigit():
            first = int(lineage[0])
            if first:
                result += (26 + first) * 36
        else:
            result += (ord(lineage[0]) - 64 )  * 36
        if lineage[1].isdigit():
            second = int(lineage[1])
            if second:
                result += 26 + second
        else:
            result += ord(lineage[1]) - 64 
        return result
    except Exception, e:
        print e
        pass
    return

#calcola il nuovo lineage per il genID delle linee cellulari
def newLineage(n):
    try:
        n = n + 1
        #print n
        first = n / 36
        second = n % 36
        base = 64
        if first > 26:
            first = first - 26
        elif first > 0:
            first = chr(base + first)
        else:
            first = 0
        if second > 26:
            second = second - 26
        elif second > 0:
            second = chr(base + second)
        else:
            second = 0
        #print str(first) + str(second)
        return str(first) + str(second)
    except Exception, e:
        print e
        pass
    return

def retrieveGeneSymbols(gene):
    url = Urls.objects.get(idWebService=WebService.objects.get(name='Annotation'))
    values = {'geneSymbol' : gene, 'exactMatch': 'true' }
    print 'url',url
    r = requests.get(url.url + '/api/genesFromSymbol', params=values, verify = False)
    response = json.loads(r.text)
    print response
    return response

def retrieveMutations(gene):
    url = Urls.objects.get(idWebService=WebService.objects.get(name='Annotation'))
    values = {'geneId' : gene}
    r = requests.get(url.url + '/api/mutationsFromGeneId', params=values, verify = False)
    response = json.loads(r.text)
    return response

def getAllColl(params, wg, url):
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


    values_to_send = {'template_id':41, 'parameters':json.dumps(values)}
    print 'values_to_send',values_to_send
    data = urllib.urlencode(values_to_send)
    try:
        u = urllib2.urlopen(url, data)
    except Exception, e:
        print e
        print "An error occurred while trying to retrieve data from "+str(url)   

    res=u.read()
    result=json.loads(res)
    #print 'result',result
    
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


def getAllCont(params, wg, url):
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

    values_to_send = {'template_id':44, 'parameters':json.dumps(values)}
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
    print 'genidsQuery',genidsQuery
    values= [{'id':'0', 'values': genidsQuery}, {'id':'1', 'values':wg}]

    values_to_send = {'template_id':45, 'parameters':json.dumps(values)}
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

def getMDAMData(request,label):
    raw_data = json.loads(request.raw_post_data)
    wg = list(get_WG())
    resSetColl = None
    resSetCont = None
    resSetGenid = None 
    resSet = None
    
    mdamUrl = Urls.objects.get(idWebService=WebService.objects.get(name='MDAM').id)
    url = mdamUrl.url + "/api/runtemplate/"
    print 'url',url
    print 'raw_data[search]',raw_data['search']
    
    for template_id, params in raw_data['search'].items():
        if template_id == '41':
            print 'template 41'
            print 'val',[len(pvalues) for pid, pvalues in params.items()]
            if sum([len(pvalues) for pid, pvalues in params.items()]):
                resSetColl = getAllColl(params, wg, url)
                #resSet.update(resSetColl)
        if template_id == '44':
            print 'template 44'
            print 'val',[len(pvalues) for pid, pvalues in params.items()]
            if sum([len(pvalues) for pid, pvalues in params.items()]):
                resSetCont = getAllCont(params, wg, url)
                #resSet.update(resSetCont)
        if template_id == '45':
            #se label e' true devo mettere un vincolo sul genealogy dicendogli di prendere solo gli LS
            print 'template 45'
            print 'params[0]',params['0']
            if len(params['0']):
                genidsQuery = []
                print 'params',params
                for g in params['0']:
                    if label and len(g)<20:
                        #serve ad aggiungere alla stringa tanti trattini fino ad arrivare ad una lunghezza di 20
                        g=g.ljust(20, '-')
                        g+='LS'
                        print 'gen',g
                    genidsQuery.append(GenealogyID(g).getGenID())
                resSetGenid = getAllGenid(genidsQuery, wg, url)
                #print resSetGenid
                #resSet.update(resSetGenid)
    
    if resSetColl!=None:
        resSet=resSetColl
        if resSetCont!=None:
            #faccio l'intersezione di questi due
            resSet=dictIntersect(resSet, resSetCont)
            if resSetGenid!=None:
                resSet=dictIntersect(resSet, resSetGenid)
        else:
            if resSetGenid!=None:
                resSet=dictIntersect(resSet, resSetGenid)
    elif resSetCont!=None:
        resSet=resSetCont
        if resSetGenid!=None:
            resSet=dictIntersect(resSet, resSetGenid)            
    elif resSetGenid!=None:
        resSet=resSetGenid
                
    #serve se voglio ottenere tutti i dati quando l'utente non mette filtri sulla ricerca. Il problema e' che e' molto lenta
    '''if resSetCont == None and resSetColl == None and resSetGenid == None:
        resSetColl = getAllColl({}, wg, url)
        resSet.update(resSetColl)'''
    return resSet

def dictIntersect(dict1,dict2):
    res={}
    for item in dict1.keys():
        if dict2.has_key(item):
            res[item]=dict2[item]
    return res

def inviaMailFunnel(error,data,subject):
    lisdest=[]
    
    mailgeda = User.objects.filter(username='emanuele.geda')
    if len(mailgeda)!=0:
        lisdest.append(mailgeda[0].email)
    mailmignone = User.objects.filter(username='andrea.mignone')
    if len(mailmignone)!=0:
        lisdest.append(mailmignone[0].email)
    mailfiori = User.objects.filter(username='alessandro.fiori')
    if len(mailfiori)!=0:
        lisdest.append(mailfiori[0].email)
    '''mailmartino = User.objects.filter(username='cosimo.martino')
    if len( mailmartino)!=0:
        lisdest.append(mailmartino[0].email)
    mailspione = User.objects.filter(username='mario.spione')
    if len( mailspione)!=0:
        lisdest.append(mailspione[0].email)'''
    
    if len(lisdest)!=0:
        message = 'Error: '+str(error)+'\n\nTimestamp: '+str(timezone.localtime(timezone.now()))+'\n\nData:\n'+json.dumps(data, sort_keys=True, indent=4, separators=(',', ': '))
        msg=EmailMessage(subject,message,"",lisdest,[],"","","",[])
        msg.send()




