import string, json, urllib, urllib2
from piston.handler import BaseHandler
from archive.models import *
from archive.utils import *
from django.core import serializers
from django.db import models
from django.http import HttpResponse
from django.db.models import Q
from global_request_middleware import *
#from Storage.api.utils import *

class Simple:
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
        return json.dumps(a)

    def getAttributes(self):
        return self.attributes

def getInfoP(barcode):
    children=[]
    piastra=Container.objects.get(barcode=barcode)
    #guardo se e' una piastra con i pozzetti
    gentipo=ContTypeHasContType.objects.filter(idContainer=piastra.idContainerType)
    piascostar=False
    for tip in gentipo:
        if tip.idContained==None:
            piascostar=True
    #parte nuova del codice    
    print 'costar',piascostar     
    if not piascostar:
        #qui carico i figli di quella piastra, che rappresenta il classico procedimento di caricamento
        contentList = Container.objects.filter(idFatherContainer = piastra)
        if len(contentList)!=0:
            listemp=[]
            for figli in contentList:
                listemp.append(figli.id)
            lisal=Aliquot.objects.filter(idContainer__in=listemp,endTimestamp=None)
            
            for figlio in contentList:
                diz={}
                diz['barcode']=figlio.barcode
                diz['position']=figlio.position
                #print 'figlio',figlio.full
                diz['full']='False'
                diz['gen']=''
                for aliq in lisal:
                    if aliq.idContainer.barcode==figlio.barcode:        
                        if aliq.position=='' or aliq.position==None:
                            diz['gen']=aliq.genealogyID
                            diz['full']='True'
                            break
                children.append(diz)                
    else:
        #vedo se per caso la piastra e' quella con i pozzetti e se si' vuol dire che compare direttamente nella tabella Aliquot
        #entra qui anche se il barcode e' una provetta singola e devo fare in modo di vederla come piena se lo e'
        lisaliq=Aliquot.objects.filter(idContainer=piastra,endTimestamp=None)
        print 'lisaliq',lisaliq
        regole=json.loads(piastra.idGeometry.rules)
        for r in regole['items']:
            diz={}
            diz['barcode']=piastra.barcode+'|'+r['id']
            diz['position']=r['id']
            diz['gen']=''
            diz['full']='False'
            for al in lisaliq:
                if al.position=='' or al.position==None:
                    diz['gen']=al.genealogyID
                    diz['full']='True'
                else:
                    if r['id']==al.position:
                        diz['gen']=al.genealogyID
                        diz['full']='True'
            children.append(diz)
            
    print 'children',children
    fatherC=''
    if piastra.idFatherContainer!=None:
        fatherC=piastra.idFatherContainer.barcode
    containerF = {'barcodeF':fatherC, 'containerType' :piastra.idContainerType.name, 'position' : piastra.position, 'availability' : piastra.availability, 'full':piastra.full}
    return {'info':containerF, 'rules': json.loads(piastra.idGeometry.rules),'children':children}

    '''children = []
    container = Container.objects.get(barcode = barcode)
    #select = ['idContainerType', 'idFatherContainer', 'position', 'barcode', 'availability', 'full']
    fatherC = ""
    if container.idFatherContainer:
        #fatherC = Simple(container.idFatherContainer, select).getAttributes()
        fatherC = container.idFatherContainer.barcode
    i = 0
    contentList = Container.objects.filter(idFatherContainer = container)
    select = ['idContainerType', 'position', 'barcode', 'availability', 'full']
    for c in contentList:
        children.append(Simple(c,select).getAttributes())
    containerF = {'barcodeF':fatherC, 'containerType' :container.idContainerType.name, 'position' : container.position, 'availability' : container.availability, 'full':container.full}

    return {'info':containerF, 'rules': json.loads(container.idGeometry.rules),'children':children}'''

#restituisce i dati per costruire la tabella in HTML e le dimensioni della piastra
#nel vettore dim. Il tipo e' il tipo aliq abbreviato
def CreaTabella (data,tipo):
    #prendo le dimensioni della piastra
    dimension = data['rules']['dimension']
    print 'dimension',dimension
    print 'data',data
    barcodeStr = ''
    dim = []
    diztipialiq={}
    diztipocontainer={}
    dizindicialiq={}
    #dizionario per sapere se all'interno del cont si possono posizionare direttamente le aliquote
    dizsalvaliq={}
    #diz per sapere se il cont contiene altri cont o delle aliq
    dizpieno={}
    
    lis_pezzi_url=[]
    lis_gen=[]
    llgeom=Geometry.objects.filter(name='1x1')
    feataliq=Feature.objects.get(name='AliquotType')
    for d in dimension:
        dim.append(d)
        #lastIndex = lastIndex + str(d)
    piascostar=False
    if 'piascostar' in data:
        piascostar=data['piascostar']
    for d in data['children']:
        for rr in data['rules']['items']:
            if rr['id'] == d['position']:
                point = ""
                for p in rr['position']:
                    if point != "":
                        #point = str(point) +  str(p)
                        point = str(point) + '|' + str(p)
                    else:
                        point = str(p)
                
                barc_prov=str(d['barcode']).replace(' ','%20')
                #dato il barc trovo il gen corrispondente
                cont=None
                conttipo=None
                salvaaliq=False
                pieno=False
                #print 'piascostar',piascostar
                if piascostar:
                    #vuol dire che e' una piastra con i pozzetti e quindi il barc e' fittizio ed e' formato da
                    #piastra|posizione
                    bb=barc_prov.split('|')
                    cont=Container.objects.get(barcode=bb[0],present=1)
                    #puo' essere anche una provetta singola, quindi devo distinguere i due casi
                    if 'cont' in data:
                        cont=data['cont']
                        if cont.idContainerType.idGenericContainerType.abbreviation=='tube' and len(llgeom)!=0 and cont.idGeometry==llgeom[0]:
                            laliq=Aliquot.objects.filter(idContainer=cont,endTimestamp=None)
                            #anche nelle provette singole lascio barc|pos nel caso di visualizzazione del contenuto. Invece
                            #per il padre metto solo barc
                            #barc_prov=bb[0]
                            conttipo=cont.idContainerType
                        else:
                            laliq=Aliquot.objects.filter(idContainer=cont,position=bb[1],endTimestamp=None)
                        salvaaliq=True
                    else:
                        laliq=Aliquot.objects.filter(idContainer=cont,position=bb[1],endTimestamp=None)
                else:
                    cont=Container.objects.get(barcode=barc_prov,present=1)
                    if cont.idContainerType.idGenericContainerType.abbreviation=='tube':
                        laliq=Aliquot.objects.filter(idContainer=cont,endTimestamp=None)
                    else:
                        laliq=Aliquot.objects.filter(idContainer=cont,position='',endTimestamp=None)
                    conttipo=cont.idContainerType
                    #vedo se li' dentro possono starci i campioni
                    lisrapporti=ContTypeHasContType.objects.filter(idContainer=cont.idContainerType)
                    for rap in lisrapporti:
                        if rap.idContained==None:
                            salvaaliq=True
                            break
                diztipocontainer[barc_prov]=conttipo
                dizsalvaliq[barc_prov]=salvaaliq
                
                listipi=[]
                tipoaliq=ContainerFeature.objects.filter(idFeature=feataliq,idContainer=cont).order_by('id')
                #se il container non ha specificato delle aliquote che puo' contenere, allora le puo' contenere tutte
                if len(tipoaliq)!=0:
                    for tip in tipoaliq:
                        listipi.append(tip.value)
                else:
                    defval=FeatureDefaultValue.objects.filter(idFeature=feataliq)
                    for val in defval:
                        listipi.append(val.idDefaultValue.abbreviation)
                diztipialiq[barc_prov]=listipi
                gen=''
                print 'laliq',laliq
                if len(laliq)!=0:
                    pieno=True
                    #visto che ci possono essere piu' aliquote per container, non posso semplicemente
                    #prendere la [0], ma devo aumentare l'indice
                    chiave=barc_prov+str(d['position'])+str(point)
                    if chiave in dizindicialiq:
                        indice=dizindicialiq[chiave]
                        indice=indice+1
                        dizindicialiq[chiave]=indice
                    else:
                        indice=0
                        dizindicialiq[chiave]=0
                    gen=laliq[indice].genealogyID
                #vedo se il cont ne contiene altri
                lisc=Container.objects.filter(idFatherContainer=cont)
                if len(lisc)!=0:
                    pieno=True
                dizpieno[barc_prov]=pieno
                barcodeStr += barc_prov + '&' + str(d['position']) + '&' + str(point) + '&' + gen + ','
                
                #2000 e' il numero di caratteri scelto per fare in modo che la url
                #della api non sia troppo lunga
                if len(barcodeStr)>2000:
                    #cancello la virgola alla fine della stringa
                    lu=len(barcodeStr)-1
                    strbarc=barcodeStr[:lu]
                    print 'strbarc',strbarc
                    lis_pezzi_url.append(strbarc)
                    barcodeStr=''
                
    #cancello la virgola alla fine della stringa
    lu=len(barcodeStr)-1
    strbarc=barcodeStr[:lu]
    print 'strbarc',strbarc
    if strbarc!='':
        lis_pezzi_url.append(strbarc)
    
    if len(lis_pezzi_url)!=0:
        indir=Urls.objects.get(default=1).url
        #print 'indir',indir
        for elementi in lis_pezzi_url:
            stringa=elementi.replace('#','%23')
            req = urllib2.Request(indir+"/api/load/tubes/"+stringa+"/"+tipo, headers={"workingGroups" : get_WG_string()})
            u = urllib2.urlopen(req)
            #u = urllib2.urlopen(indir+"/api/tubes/"+stringa+ "?workingGroups="+get_WG_string())
            #in data ho i genid di tutti i blocchi di quel cassetto
            data = json.loads(u.read())
            print 'data',data
            if data['data']=='errore':
                return [], dim,'errore',diztipialiq,diztipocontainer,dizsalvaliq,dizpieno
            for pezzi in data['data']:
                lis_gen.append(pezzi)
        print 'lis_gen',lis_gen
                
    '''if barcodeStr!="":
        stringa=barcodeStr[0:len(barcodeStr)-1]
    else:
        stringa='x'
    print 'stringa',stringa
    stringa=stringa.replace('#','%23')
    try:
        address = Urls.objects.get(default = '1').url
        req = urllib2.Request(address+"/api/load/tubes/"+stringa+"/"+tipo, headers={"workingGroups" : get_WG_string()})
        u = urllib2.urlopen(req)
    except Exception, e:
        print 'e',e
        return 'x', 'y', 'errore',{}'''
    return lis_gen, dim,'ok',diztipialiq,diztipocontainer,dizsalvaliq,dizpieno

#restituisce tutte le foglie dell'albero
def visit_children(listadavisitare,listadef):
    #print 'listavisitare',listadavisitare
    for c in listadavisitare:
        #print 'ccc',c
        #se sono barcode di provette, mi blocco
        if c.idContainerType.idGenericContainerType.abbreviation=='tube':
            if c not in listadef:
                listadef.append(c)            
        else:
            #devo prendere i figli 
            listacont=Container.objects.filter(idFatherContainer=c)
            print 'listacont',listacont
            listadef=visit_children(listacont,listadef)
    return listadef

#restituisce tutte le foglie e anche i container intermedi
def visit_children2(listadavisitare,listadef):
    #print 'listavisitare',listadavisitare
    for c in listadavisitare:
        #print 'ccc',c
        if c not in listadef:
            listadef.append(c)
        #se sono barcode di provette, mi blocco
        if c.idContainerType.idGenericContainerType.abbreviation!='tube':
            #devo prendere i figli 
            listacont=Container.objects.filter(idFatherContainer=c)
            print 'listacont',listacont
            listadef=visit_children2(listacont,listadef)
    print 'listadef',listadef
    return listadef

def visit_father(listacontfigli,listadavisitare,listafin,passaggio):
    lista=[]
    lista2=[]
    listatemp=[]
    listainserire=[]
    print 'listacontfigli',listacontfigli
    for cont in listadavisitare:
        #serve per le piastre con i pozzetti. Le metto in questa lista temporanea che poi aggiungero' alla fine
        #per fare in modo che queste piastre vengano analizzate al ciclo successivo di ricorsione quando tutti 
        #i container saranno piastre e non adesso quando tutti sono provette
        if passaggio ==0 and cont.idContainerType.idGenericContainerType.abbreviation=='plate':
            listainserire.append(cont)
        padre=cont.idFatherContainer
        #faccio una lista con tutti i padri
        if padre!=None and padre not in lista:
            lista.append(padre)
    print 'lista',lista
    for padre in lista:
        print 'padre',padre
        #prendo i figli del singolo padre
        #se il cont e' una piastra allora prendo solo i figli (provette) pieni, altrimenti prendo tutti i figli
        if padre.idContainerType.idGenericContainerType.abbreviation=='plate':
            listafigli=Container.objects.filter(idFatherContainer=padre,full=1,present=1)
        else:
            listafigli=Container.objects.filter(idFatherContainer=padre,present=1)
        #guardo se ogni figlio di quel padre si trova nella lista dei container figli che ho passato 
        #all'inizio
        print 'listafigli',listafigli
        for figlio in listafigli:
            #print 'figlio',figlio
            #print 'listacontfigli dopo',listacontfigli
            if figlio.barcode.upper() not in listacontfigli:
                #metto qui i padri da togliere dalla lista dei padri ancora da scandire.
                #Vuol dire che quel container non ha tutti i suoi figli programmati per il 
                #trasferimento quindi non ha senso andare a vedere il suo padre
                #in un altro ciclo successivo
                listatemp.append(padre)
                print 'rimosso',padre
                break
    #tolgo da lista il contenuto di listatemp
    listadopo=[x for x in lista if x not in listatemp]
    print 'listadopo',listadopo
    for c in listainserire:
        listadopo.append(c)
    continua=False
    for p in listadopo:
        lista2.append(p.barcode.upper())
        listafin.append(p)
        if p.idFatherContainer!=None:
            continua=True
    print 'listafin',listafin      
    if len(listadopo)!=0 and continua==True:          
        listadopo=visit_father(lista2,listadopo,listafin,int(passaggio)+1)
    return listafin
    
def Biocass(barcode,tipo,archive):
    cont=Container.objects.filter(barcode=barcode)
    print 'cont',cont
    #vuol dire che il blocchetto esiste gia'
    if len(cont)!=0:
        if not archive:
            #ha senso entrare qui solo se e' una provetta
            if cont[0].idContainerType.idGenericContainerType.abbreviation!='tube':
                return {'data':'err_esistente'}
            #devo vedere se e' pieno o se e' vuoto
            if cont[0].full==1 or cont[0].present==0:
                return {'data':'err_esistente'}
            else:
                if tipo=='Tube':
                    #devo vedere se il blocchetto e' del tipo giusto
                    nome=cont[0].idContainerType.name
                    print 'nome',nome
                    print 'tipo',tipo
                    if str(nome)!=str(tipo):
                        return {'data':'err_tipo'}
                else:
                    #vuol dire che in tipo ho il tipo aliquota e devo vedere se quella provetta 
                    #e' di quel tipo
                    feat=Feature.objects.get(name='AliquotType')
                    contfeat=ContainerFeature.objects.filter(idFeature=feat,idContainer=cont[0])
                    if len(contfeat)!=0:
                        if contfeat[0].value!=tipo:
                            return {'data':'errore_aliq'}
        if archive:
            #devo vedere se il blocchetto e' gia' stato posizionato o meno
            if cont[0].idFatherContainer==None:
                tip=''
                #se c'e' restituisco anche il tipo di aliquota della provetta
                tipoaliqgen=Feature.objects.get(name='AliquotType')
                listacontfeat=ContainerFeature.objects.filter(idFeature=tipoaliqgen,idContainer=cont[0])
                if len(listacontfeat)!=0:
                    tip=listacontfeat[0].value
                return {'data':'ok','tipo':tip}
            else:
                return {'data':'posiz'}
    return {'data':'ok'}

def caricaFigli(piastra):
    children=[]
    piascostar=False
    #guardo se e' una piastra con i pozzetti
    gentipo=ContTypeHasContType.objects.filter(idContainer=piastra.idContainerType)
    for tip in gentipo:
        if tip.idContained==None:
            piascostar=True
    #parte nuova del codice    
    print 'costar',piascostar
    if not piascostar:
        #qui carico i figli di quella piastra, che rappresenta il classico procedimento di caricamento
        contentList = Container.objects.filter(idFatherContainer = piastra,present=1)
        if len(contentList)!=0:
            listemp=[]
            for figli in contentList:
                listemp.append(figli.id)
            lisal=Aliquot.objects.filter(idContainer__in=listemp,endTimestamp=None)
            print 'lisal',lisal
            for figlio in contentList:
                diz={}
                diz['barcode']=figlio.barcode
                diz['position']=figlio.position
                #print 'figlio',figlio.full
                diz['full']='False'
                diz['gen']=''
                for aliq in lisal:
                    if aliq.idContainer.barcode==figlio.barcode:
                        #rilasso questo vincolo della posizione perche' se e' una piastra non costar (e questo controllo serviva
                        #in questo caso) lo gestisco gia' dopo nella CreaTabella() mettendo un controllo sul generictype se e' tube
                        #if aliq.position=='' or aliq.position==None:                        
                        diz['gen']=aliq.genealogyID
                        diz['full']='True'
                        break
                children.append(diz)                
    else:
        #vedo se per caso la piastra e' quella con i pozzetti e se si' vuol dire che compare direttamente nella tabella Aliquot
        #entra qui anche se il barcode e' una provetta singola e devo fare in modo di vederla come piena se lo e'
        lisaliq=Aliquot.objects.filter(idContainer=piastra,endTimestamp=None)
        print 'lisaliq',lisaliq
        regole=json.loads(piastra.idGeometry.rules)
        for r in regole['items']:
            aggiunto=False
            diz={}
            diz['barcode']=piastra.barcode+'|'+r['id']
            diz['position']=r['id']
            diz['gen']=''
            diz['full']='False'
            for al in lisaliq:              
                #entra qui solo se carico provette singole
                if al.position=='' or al.position==None:
                    diz['gen']=al.genealogyID
                    diz['full']='True'
                    children.append(diz)
                    aggiunto=True
                #entra qui per le piastre costar
                else:
                    if r['id']==al.position:
                        diz['gen']=al.genealogyID
                        diz['full']='True'
                        children.append(diz)
                        aggiunto=True
            if not aggiunto:
                children.append(diz)
            
    print 'children',children
    return children

def visualizzaBlocchetti(barcodeP,typeP,spostamento,tipoaliqgen,defval,piastra,liscont):
    long_name=''
    listipi=''
    string = ''
    abbr = 'r'
    name = 'rna'
    
    long_name+=' Aliquot: '
    feataliq=Feature.objects.get(name='AliquotType')
    #metto liscont[0] tanto qui mi occupo del padre e scelgo un cont a caso
    tipoaliq=ContainerFeature.objects.filter(idFeature=tipoaliqgen,idContainer=liscont[0].idFatherContainer).order_by('id')
    #se il container non ha specificato delle aliquote che puo' contenere, allora le puo' contenere tutte
    if len(tipoaliq)!=0:
        #se il cont ha tutte le aliq, allora scrivo "All"
        if len(tipoaliq)==len(defval):
            long_name+='All'
            for tip in tipoaliq:
                listipi+=tip.value+'&'
        else:
            for tip in tipoaliq:
                long_name+=tip.value+'-'
                listipi+=tip.value+'&'
            long_name=long_name[:-1]
        
    else:                  
        for val in defval:
            listipi+=val.idDefaultValue.abbreviation+'&'
        long_name+='All'
    listipi=listipi[:-1]
    
    codeList = [[0 for x in xrange(2)] for x in xrange(len(liscont))]
    print 'codelist iniz',codeList
    xx=0
    for contain in liscont:
        print 'container',contain
        children=caricaFigli(contain)
        piascostar=False
        #guardo se e' una piastra con i pozzetti
        gentipo=ContTypeHasContType.objects.filter(idContainer=contain.idContainerType)
        for tip in gentipo:
            if tip.idContained==None:
                piascostar=True
        geom=json.loads(contain.idGeometry.rules)
        dim = geom['dimension']
        x = int(dim[1])
        y = int(dim[0])
        print 'x',x
        print 'y',y
        id_position = 'A'+str(xx+1)
        posmax=contain.idContainerType.maxPosition
        if piascostar:# and x==1 and y==1: 
            diz={'typeC':contain.idContainerType.name,'children':children,'rules': geom,'piascostar':piascostar,'cont':contain}
            res, dim,err,diztipi,diztipcontainer,dizsalvaliq,dizpieno = CreaTabella(diz,typeP)
            if err=='errore':
                return {'data':'errore_banca'}
            
            #res = json.loads(response)
            print 'res',res
            
            #if res['data']=='errore':
                #return {"data": 'errore'}                       
            
            if len(res)!=0:
                #dizionario per salvare i gen, i barc e il tipoaliq per i campioni che hanno piu' aliquote nello
                #stesso posto
                dizdoppi={}
                #vuol dire che la provetta e' piena
                for r in res:
                    #print 'r',r
                    #print 'xx',xx
                    pieces = r.split(',')
                    barcode =  pieces[0]
                    coordinates = pieces[2]                             
                    if len(pieces) > 3:                           
                        #se la provetta contiene un'aliquota                    
                        aliquot = pieces[3]
                        quantity = 1
                        tipoaliq = pieces[5]                  
                        salvaliq=False
                        cont=''                       
                        barctemp=barcode.encode('utf-8')
                        pieno=False
                        if barctemp in diztipcontainer:
                            conttipo=diztipcontainer[barctemp]
                            print 'conttipi',conttipo
                            if conttipo!=None:
                                cont=str(conttipo.id)
                                posmax=conttipo.maxPosition
                            salvaliq=dizsalvaliq[barctemp]
                            pieno=dizpieno[barctemp]
                        
                        chiave=id_position+coordinates
                        if chiave in dizdoppi:
                            diztemp=dizdoppi[chiave]
                            aliqtemp=diztemp['gen']
                            aliquot=aliqtemp+'&'+aliquot                                            
                            tipotemp=diztemp['tipo']
                            pienotemp=diztemp['pieno']
                            if pienotemp or pieno:
                                pieno=True
                            if not ControllaAliquota(tipotemp, tipoaliq):
                                tipoaliq=tipotemp+'&'+tipoaliq
                            quant=diztemp['num']
                            quantity=quant+1
                        else:
                            diztemp={}
                        
                        diztemp['num']=quantity
                        diztemp['gen']=aliquot
                        diztemp['tipo']=tipoaliq
                        diztemp['pieno']=pieno
                        dizdoppi[chiave]=diztemp
                                                                                                                                                        
                        classetasto=''
                        #se il barc e' di una provetta avro' barc|A1, quindi devo far vedere solo il barc
                        barc2=barcode.split("|")
                        codeList[xx][0] = '<td class="mark">'+barc2[0]+'</td>'
                        if pieces[3]=='NOT AVAILABLE':
                            titlesel='title="NOT AVAILABLE"'
                            selez=''
                            quantity='X'
                            notavail='notavailable="True"'
                        else:
                            if str(quantity).isdigit():
                                #se salvaliq e' vera allora vuol dire che posso salvare li' dentro delle aliquote e allora devo controllare
                                #il posmax. Se e' falsa, conta solo il numero di posmax del padre
                                if salvaliq:
                                    if posmax==None or not pieno or int(posmax)-int(quantity)>0 or contain.idContainerType.maxPosition==None or int(contain.idContainerType.maxPosition)-int(quantity)>0:
                                        classetasto+=' disp'
                                else:
                                    if contain.idContainerType.maxPosition==None or int(contain.idContainerType.maxPosition)-int(quantity)>0:
                                        classetasto+=' disp'
                            else:
                                if posmax==None or int(posmax)-1>0:
                                    classetasto+=' disp'
                            titlesel=''
                            selez='sel="s"'
                            notavail=''
                        codeList[xx][1] = '<td id="h-'+ id_position +'" aliq="'+ str(salvaliq)+'" barcode="'+ barcode+ '" posmax="' + str(posmax)+'" '+notavail+' > <button '+titlesel+' type="submit" align="center" id="'+ abbr + '-' + id_position +'" col="0" row="'+str(xx)+ '" '+selez+' class="'+classetasto+ '" gen="'+aliquot+ '" pieno="'+str(pieno)+'" barcode="'+ barcode+'" aliq="'+ str(salvaliq)+'" tipo="'+ tipoaliq+'" cont="'+ cont+'" disabled="disabled">'+ str(quantity) +'</button></td>'                                
                    else:
                        #se la provetta e' vuota
                        barcode =  barcode.encode('utf-8')
                        strtipi=''
                        
                        print 'diztipi',diztipi
                        if barcode in diztipi:
                            listip=diztipi[barcode]
                            strtipi=''
                            for val in listip:                                    
                                strtipi+=val+'&'
                            strtipi=strtipi[:-1]
                        salvaliq=False
                        cont=''
                        barctemp=barcode.encode('utf-8')
                        pieno=False
                        print 'diztipicont',diztipcontainer
                        if barctemp in diztipcontainer:                                            
                            conttipo=diztipcontainer[barctemp]
                            print 'conttipi vuota',conttipo
                            if conttipo!=None:
                                cont=str(conttipo.id)
                                posmax=conttipo.maxPosition
                            salvaliq=dizsalvaliq[barctemp]
                            pieno=dizpieno[barctemp]
                        
                        chiave=id_position+coordinates
                        if chiave in dizdoppi:
                            diztemp=dizdoppi[chiave]
                            aliqtemp=diztemp['gen']
                            aliquot=aliqtemp+'&'                                                            
                            quant=diztemp['num']
                            quantity=quant+1
                            pienotemp=diztemp['pieno']
                            if pienotemp or pieno:
                                pieno=True                      
                        else:
                            diztemp={}
                            aliquot='&'
                            quantity=1                                    
                        
                        diztemp['gen']=aliquot
                        diztemp['num']=quantity
                        diztemp['pieno']=pieno                
                        dizdoppi[chiave]=diztemp
                        
                        #se il barc e' di una provetta avro' barc|A1, quindi devo far vedere solo il barc
                        barc2=barcode.split("|")
                        quantity=0
                        classetasto=''
                        if str(quantity).isdigit():
                            if salvaliq:
                                if posmax==None or not pieno or int(posmax)-int(quantity)>0 or contain.idContainerType.maxPosition==None or int(contain.idContainerType.maxPosition)-int(quantity)>0:
                                    classetasto+=' disp'
                            else:
                                if contain.idContainerType.maxPosition==None or int(contain.idContainerType.maxPosition)-int(quantity)>0:
                                    classetasto+=' disp'
                        else:
                            if posmax==None or int(posmax)-1>0:
                                classetasto+=' disp'
                        codeList[xx][0] = '<td class="mark">'+barc2[0]+'</td>'
                        codeList[xx][1] = '<td id="h-'+ id_position +'" aliq="'+ str(salvaliq)+'" barcode="'+ barcode+ '" posmax="' + str(posmax)+'" ><button type="submit" align="center" sel="s" id="'+ abbr + '-' + id_position +'" col="0" row="'+str(xx)+ '" " barcode="'+ barcode+'" aliq="'+ str(salvaliq)+ '" pieno="'+str(pieno)+ '" class="'+classetasto+ '" gen="'+aliquot+'" cont="'+ cont+'" tipo="'+ strtipi+'">'+str(quantity)+'</button></td>'                
            
        else:
            salvaliq=False
            if piascostar:
                salvaliq=True
            barcode=contain.barcode
            pieno=False
            #guardo quanti figli ha per sapere se e' pieno
            liscontfigli=Container.objects.filter(idFatherContainer=contain)
            lisaliqfigli=Aliquot.objects.filter(idContainer=contain)
            if len(liscontfigli)!=0 or len(lisaliqfigli)!=0:
                pieno=True
            classetasto=''
            aliquot='notdefined'
            cont=str(contain.idContainerType.id)
            quantity=len(liscontfigli)
            strtipi=''
            tipoaliq=ContainerFeature.objects.filter(idFeature=feataliq,idContainer=contain).order_by('id')
            #se il container non ha specificato delle aliquote che puo' contenere, allora le puo' contenere tutte
            if len(tipoaliq)!=0:
                for tip in tipoaliq:
                    strtipi+=tip.value+'&'
            else:
                defval=FeatureDefaultValue.objects.filter(idFeature=feataliq)
                for val in defval:
                    strtipi+=val.idDefaultValue.abbreviation+'&'
            strtipi=strtipi[:-1]
            codeList[xx][0] = '<td class="mark">'+barcode+'</td>'
            codeList[xx][1] = '<td id="h-'+ id_position +'" aliq="'+ str(salvaliq)+'" barcode="'+ barcode+ '" posmax="' + str(posmax)+'" ><button type="submit" align="center" itself="itself" sel="s" id="'+ abbr + '-' + id_position +'" col="0" row="'+str(xx)+ '" " barcode="'+ barcode+'" aliq="'+ str(salvaliq)+ '" pieno="'+str(pieno)+ '" class="'+classetasto+ '" gen="'+aliquot+'" cont="'+ cont+'" tipo="'+ strtipi+'">'+str(quantity)+'</button></td>'
        xx=xx+1    
    print 'codelist',codeList
    #creo il codice per la tabella HTML
    pias=liscont[0]
    if pias.idFatherContainer!=None:
        contpadre=pias.idFatherContainer.barcode
    print 'pias',pias
    #per capire che sto vedendo lo zoom su un cassetto ad es.
    mult="True"
    string += '<table align="center" id="' + str(name) + '" mult="'+ mult+ '" barcode="'+ barcodeP+ '" costar="'+ str(piascostar)+'" cont="' + str(pias.idContainerType.id) + '" tipo="' + str(listipi)+ '" row="' + str(len(liscont))+ '" col="1" father="' + str(contpadre) + '" posmax="' + str(pias.idContainerType.maxPosition) + '" ><tbody><tr><th colspan="3" >' + str(long_name) + '</th></tr>'
    print 'string',string
    string += '<tr>'
    string += '<td class="intest"><strong>N</strong></td>'
    string += '<td class="intest"><strong>Barcode</strong></td>'
    string += '<td align="center" class="intest"></td>'
    string += '</tr>'
    i = 1
    print 'codelist',codeList
    for code in codeList:
        string += '<tr>'
        string += '<td align="center" class="intest"><strong>'+str(i)+'</strong></td>'
        for c in code:
            if c != "":
                string += c
        string += '</tr>'
        i = i +1
    string += "</tbody></table></div></div>"
    return string

def visualizzaAliquote(lisgen):
    long_name=''
    barcodeStr=''
    listipi=''
    abbr='r'
    string = ''
    tipoaliqgen=Feature.objects.get(name='AliquotType')
    defval=FeatureDefaultValue.objects.filter(idFeature=tipoaliqgen)
    #ho una stringa con i gen separati da &
    lgen=lisgen.split("&")
    lisaliq=Aliquot.objects.filter(genealogyID__in=lgen,endTimestamp=None)
    cont=lisaliq[0].idContainer
    long_name+=' Aliquot: '
    #metto liscont[0] tanto qui mi occupo del padre e scelgo un cont a caso
    tipoaliq=ContainerFeature.objects.filter(idFeature=tipoaliqgen,idContainer=cont).order_by('id')
    #se il container non ha specificato delle aliquote che puo' contenere, allora le puo' contenere tutte
    if len(tipoaliq)!=0:
        #se il cont ha tutte le aliq, allora scrivo "All"
        if len(tipoaliq)==len(defval):
            long_name+='All'
            for tip in tipoaliq:
                listipi+=tip.value+'&'
        else:
            for tip in tipoaliq:
                long_name+=tip.value+'-'
                listipi+=tip.value+'&'
            long_name=long_name[:-1]
        
    else:                  
        for val in defval:
            listipi+=val.idDefaultValue.abbreviation+'&'
        long_name+='All'
    listipi=listipi[:-1]
    
    codeList = [[0 for x in xrange(2)] for x in xrange(len(lisaliq))] 
    print 'codelist iniz',codeList
    xx=0
        
    for aliq in lisaliq:
        barcodeStr += '&&&' + aliq.genealogyID + ','
    if barcodeStr!="":
        stringa=barcodeStr[0:len(barcodeStr)-1]
    else:
        stringa='x'
    print 'stringa',stringa
    stringa=stringa.replace('#','%23')
    try:
        address = Urls.objects.get(default = '1').url
        req = urllib2.Request(address+"/api/load/tubes/"+stringa+"/children", headers={"workingGroups" : get_WG_string()})
        u = urllib2.urlopen(req)
    except Exception, e:
        print 'e',e
        return 'x', 'y', 'errore',{}
    res = json.loads(u.read())
    print 'res',res                        
    if res['data']=='errore':
        return {"data": 'errore'}
    
    salvaaliq=True
    pieno=True
    if len(res['data'])!=0:
        #vuol dire che la provetta e' piena
        for r in res['data']:
            print 'r',r
            print 'xx',xx                                
            if len(r.split(',')) > 3:                           
                #se la provetta contiene un'aliquota
                pieces = r.split(',')
                #do il barc uguale al gen
                barcode =  pieces[3]
                contid=str(cont.idContainerType.id)
                posmax=cont.idContainerType.maxPosition

                id_position = 'A'+str(xx+1)
                aliquot = pieces[3]
                quantity = pieces[4]
                tipoaliq = pieces[5]
                                                  
                classetasto='aliqclass foglia'
                codeList[xx][0] = '<td class="mark">'+aliquot+'</td>'
                if aliquot=='NOT AVAILABLE':
                    codeList[xx][1] = '<td id="h-'+ id_position +'" aliq="'+ str(salvaaliq)+ '" posmax="' + str(posmax)+'" notavailable="True" > <button title="NOT AVAILABLE" type="submit" align="center" id="'+ abbr + '-' + id_position +'" col="0" row="'+str(xx)+ '" class="'+classetasto+ '" gen="'+aliquot+'" barcode="'+ barcode+ '" pieno="'+str(pieno)+ '" aliq="'+ str(salvaaliq)+'" tipo="'+ tipoaliq+'" cont="'+ contid+'" disabled="disabled">'+ str(quantity) +'</button></td>'
                else:
                    if str(quantity).isdigit():
                        if posmax==None or int(posmax)-int(quantity)>0:
                            classetasto+=' disp'
                    else:
                        if posmax==None or int(posmax)-1>0:
                            classetasto+=' disp'
                    codeList[xx][1] = '<td id="h-'+ id_position +'" aliq="'+ str(salvaaliq)+ '" posmax="' + str(posmax)+'" > <button type="submit" align="center" id="'+ abbr + '-' + id_position +'" col="0" row="'+str(xx)+ '" sel="s" class="'+classetasto+ '" gen="'+aliquot+'" barcode="'+ barcode+ '" pieno="'+str(pieno)+ '" aliq="'+ str(salvaaliq)+'" tipo="'+ tipoaliq+'" cont="'+ contid+'" disabled="disabled">'+ str(quantity) +'</button></td>'                                

            xx=xx+1    
    #creo il codice per la tabella HTML
    pias=cont
    #do' come padre il cont stesso cosi' quando faccio zoom- rivedo la provetta
    contpadre=pias
    piascostar=True
    multiplo="True"
    string += '<table align="center" id="rna" leaf="leaf" cont="' + str(pias.idContainerType.id) + '" mult="'+ multiplo+ '" costar="'+ str(piascostar)+ '" barcode="'+ lisgen+'" tipo="' + str(listipi)+ '" row="' + str(len(lisaliq))+ '" col="1" father="' + str(contpadre) + '" posmax="' + str(pias.idContainerType.maxPosition) + '" ><tbody><tr><th colspan="3" >' + str(long_name) + '</th></tr>'
    string += '<tr>'
    string += '<td class="intest"><strong>N</strong></td>'
    string += '<td class="intest"><strong>Genealogy ID</strong></td>'
    string += '<td align="center" class="intest"></td>'
    string += '</tr>'
    i = 1
    for code in codeList:
        string += '<tr>'
        string += '<td align="center" class="intest"><strong>'+str(i)+'</strong></td>'
        for c in code:
            if c != "":
                string += c
        string += '</tr>'
        i = i +1
    string += "</tbody></table></div></div>"     
    return string,listipi    
        
    
