from __init__ import *

#serve per avere informazioni sui campioni come barcode, piastra, volume, concentrazione
def retrieveAliquots (aliq_biobank, operator):
    biobankUrl = Urls.objects.get(id_webservice=WebService.objects.get(name='biobank').id, available=True)
    listagen=[]
    lisval=aliq_biobank.split('&')
    lgen=''
    lis_pezzi_url=[]
    for val in lisval:
        lgen+=val+'&'
        if len(lgen)>2000:
        #cancello la & alla fine della stringa
            lis_pezzi_url.append(lgen[:-1])
            lgen=''
    #cancello la & alla fine della stringa
    strgen=lgen[:-1]
    print 'strgen',strgen
    if strgen!='':
        lis_pezzi_url.append(strgen)
    
    if len(lis_pezzi_url)!=0:
        for elementi in lis_pezzi_url:
            
            url = biobankUrl.url + "api/derivative/"+elementi + "/" + operator
            print 'WG biobank', get_WG_string()
            req = urllib2.Request(url, headers={"workingGroups" : get_WG_string()})
            u = urllib2.urlopen(req)
            data = json.loads(u.read())
            listatemp=data['data']
            print 'listatemp',listatemp
            listagen=listagen+listatemp            
    dizfin={}
    dizfin['data']=listagen
    return dizfin


def updateAliquots(data):
    biobankUrl = Urls.objects.get(id_webservice=WebService.objects.get(name='biobank').id, available=True)
    url = biobankUrl.url + "update/volume/"
    req = urllib2.Request(url, data=data, headers={"workingGroups" : get_WG_string()})
    u = urllib2.urlopen(req)
    res=u.read()
    return res


def setExperiment (aliquots):
    biobankUrl = Urls.objects.get(id_webservice=WebService.objects.get(name='biobank').id, available=True)
    url = biobankUrl.url + "api/experiment/confirm"
    aliquots = json.dumps(aliquots)
    data = urllib.urlencode({'aliquots':aliquots, 'experiment':'NextGenerationSequencing'})
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
    data = urllib.urlencode({'aliquots':aliquots, 'experiment':'NextGenerationSequencing'})
    req = urllib2.Request(url, data=data, headers={"workingGroups" : get_WG_string()})
    u = urllib2.urlopen(req)
    res = u.read()
    res = json.loads(res)
    print res
    if res['data'] != 'OK':
        raise Exception('Problem connecting with biobank for experimental aliquots')    

#serve per avere la lista di tutti gli ospedali presenti. Usata nella schermata di inserimento dei campioni esterni al LAS
def retrieveSources ():
    biobankUrl = Urls.objects.get(id_webservice=WebService.objects.get(name='biobank').id, available=True)
    url = biobankUrl.url + "api/getSources/"
    print 'WG biobank', get_WG_string()
    req = urllib2.Request(url, headers={"workingGroups" : get_WG_string()})
    u = urllib2.urlopen(req)
    res=u.read()
    res=ast.literal_eval(res)
    return res

#serve per avere la lista di tutti i tessuti presenti. Usata nella schermata di inserimento dei campioni esterni al LAS
def retrieveTissue ():
    biobankUrl = Urls.objects.get(id_webservice=WebService.objects.get(name='biobank').id, available=True)
    url = biobankUrl.url + "api/tissue/"
    req = urllib2.Request(url, headers={"workingGroups" : get_WG_string()})
    u = urllib2.urlopen(req)
    res=u.read()
    return res

#serve per avere la lista di tutti i tumori presenti. Usata nella schermata di inserimento dei campioni esterni al LAS
def retrieveCollectionType ():
    biobankUrl = Urls.objects.get(id_webservice=WebService.objects.get(name='biobank').id, available=True)
    url = biobankUrl.url + "api/collectiontype/"
    req = urllib2.Request(url, headers={"workingGroups" : get_WG_string()})
    u = urllib2.urlopen(req)
    res=u.read()
    return res

#per comunicare alla biobanca i dati dei nuovi campioni inseriti nella schermata di 'Insert samples'
def saveExternAliquots(lista,operatore):
    biobankUrl = Urls.objects.get(id_webservice=WebService.objects.get(name='biobank').id, available=True)
    url = biobankUrl.url + "api/facility/savealiquots/"
    print 'url',url
    aliquots = json.dumps(lista)
    data = urllib.urlencode({'aliquots':aliquots,'experiment':'NGS','operator':operatore})
    req = urllib2.Request(url, data=data, headers={"workingGroups" : get_WG_string()})
    u = urllib2.urlopen(req)
    res=u.read()
    print 'res',res
    return res

#serve per avere i valori del genID da far comparire nel filtro genID esteso
def retrievegenIDValues ():
    biobankUrl = Urls.objects.get(id_webservice=WebService.objects.get(name='biobank').id, available=True)
    url = biobankUrl.url + "api/getGenIDValues/"
    req = urllib2.Request(url, headers={"workingGroups" : get_WG_string()})
    u = urllib2.urlopen(req)
    res=u.read()
    res=ast.literal_eval(res)
    print 'res',res
    ftype={'Predefined list':1,'Alphabetic':2,'Numeric':3,'Alphanumeric':4}
    listum=res['tum']
    listess=res['tess']
    lisvector=res['vector']
    lismousetissue=res['mousetess']
    listipialiq=res['tipialiq']
    lisderivati=res['der']
    lisderivati2=res['der2']
    lisaliquot=[{'name':'Tumor type','start':0,'end':2,'ftype':ftype['Predefined list'],'values':listum},{'name':'Item code','start':3,'end':6,'ftype':ftype['Alphanumeric'],'values':[]}
            ,{'name':'Tissue','start':7,'end':8,'ftype':ftype['Predefined list'],'values':listess},{'name':'Vector','start':9,'end':9,'ftype':ftype['Predefined list'],'values':lisvector}
            ,{'name':'Lineage','start':10,'end':11,'ftype':ftype['Alphanumeric'],'values':[]},{'name':'Passage','start':12,'end':13,'ftype':ftype['Numeric'],'values':[]}
            ,{'name':'Mouse number','start':14,'end':16,'ftype':ftype['Numeric'],'values':[]},{'name':'Tissue type','start':17,'end':19,'ftype':ftype['Predefined list'],'values':lismousetissue}
            ,{'name':'Aliquot type','start':20,'end':21,'ftype':ftype['Predefined list'],'values':listipialiq},{'name':'Aliquot number','start':22,'end':23,'ftype':ftype['Numeric'],'values':[]}]
    
    lisderived=[{'name':'Tumor type','start':0,'end':2,'ftype':ftype['Predefined list'],'values':listum},{'name':'Item code','start':3,'end':6,'ftype':ftype['Alphanumeric'],'values':[]}
                ,{'name':'Tissue','start':7,'end':8,'ftype':ftype['Predefined list'],'values':listess},{'name':'Vector','start':9,'end':9,'ftype':ftype['Predefined list'],'values':lisvector}
                ,{'name':'Lineage','start':10,'end':11,'ftype':ftype['Alphanumeric'],'values':[]},{'name':'Passage','start':12,'end':13,'ftype':ftype['Numeric'],'values':[]}
                ,{'name':'Mouse number','start':14,'end':16,'ftype':ftype['Numeric'],'values':[]},{'name':'Tissue type','start':17,'end':19,'ftype':ftype['Predefined list'],'values':lismousetissue}
                ,{'name':'Aliquot type','start':20,'end':20,'ftype':ftype['Predefined list'],'values':lisderivati},{'name':'Aliquot number','start':21,'end':22,'ftype':ftype['Numeric'],'values':[]}
                ,{'name':'2nd derivation type','start':23,'end':23,'ftype':ftype['Predefined list'],'values':lisderivati2},{'name':'2nd derivation number','start':24,'end':25,'ftype':ftype['Numeric'],'values':[]}]
    
    diztot={'Aliquot':{'fields':lisaliquot},'Derived aliquot':{'fields':lisderived}}
    print 'diztot',diztot
    return diztot
