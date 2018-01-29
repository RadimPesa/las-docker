from piston.handler import BaseHandler
from piston.handler import AnonymousBaseHandler
from catissue.tissue.models import *
from django.core import serializers
from django.db import models
from django.http import HttpResponse
from django.db.models import Q
import string
import operator,random
from catissue.api.utils import *
from catissue.tissue.utils import *
import datetime
import urllib, urllib2, json,ast,requests
from django.views.decorators.csrf import csrf_exempt
from django.contrib import auth
from django.conf import settings
from django.template.loader import render_to_string
from django.core.mail import send_mail, EmailMultiAlternatives
from itertools import chain
from django.utils.decorators import method_decorator
from catissue.apisecurity.decorators import get_functionality_decorator
from dateutil.relativedelta import *
from catissue.global_request_middleware import *
import inspect
from catissue import tissue
from piston.utils import rc
from urllib2 import HTTPError
from django.utils import timezone

class GetDbSchemaHandler(BaseHandler):
    allowed_methods = ('GET')
    @method_decorator(get_functionality_decorator)
    def read(self, request):
        try:
            e = []
            r = []
            for name,obj in inspect.getmembers(tissue.models):
                if inspect.isclass(obj):
                    #e.append(name)
                    f = []
                    for x in obj._meta.fields:
                        f.append(x.name)
                        if x.rel:
                            r.append((name, x.rel.to._meta.object_name, x.name))
                    e.append((name,f))
        
            return {'entities': e, 'relationships': r}
        except Exception,e:
            print 'err',e


#dato un tipo di kit, restituisce il nome del file con le sue istruzioni
class KiteProtHandler(BaseHandler):
    allowed_methods = ('GET')
    @method_decorator(get_functionality_decorator)
    def read(self, request,nome):
        try:
            k=KitType.objects.get(name=str(nome))
            filek=k.instructions
            return {'data':filek}
        except:
            return {"data":'errore'}
        
#dato un codice di kit, mi dice se esiste gia' o no 
class KitBarcodeHandler(BaseHandler):
    allowed_methods = ('GET')
    @method_decorator(get_functionality_decorator)
    def read(self, request,barcode):
        try:
            print 'barc',barcode
            kit=Kit.objects.filter(Q(barcode=barcode))
            if kit.count()!=0:
                return {'data':'1'}
            else:
                return {'data':'0'}
        except Exception, e:
            print 'err',e
            return {"data":'errore'}
        
'''#Anche per gli impianti di caxeno. Data una lista di barcode delle provette,
#viene restituito il GenID delle aliquote che sono in quelle provette 
class TubeHandler(BaseHandler):
    allowed_methods = ('GET')
    @method_decorator(get_functionality_decorator)
    def read(self, request, barcode):
        lista=[]
        #il barcode ha la forma barcodeprovetta&posizione&coordinate_nella_piastra e i vari barc sono separati da
        #virgola
        if barcode:
            try:
                provette=barcode.split(',')
                #aliqvitali=AliquotType.objects.get(abbreviation='VT')
                #recupero l'oggetto feature relativo al numero di pezzi per le aliq vitali
                #featu=Feature.objects.get(Q(name='NumberOfPieces')&Q(idAliquotType=aliqvitali))
                #print 'fe',featu
                #scandisco i barcode
                for prov in provette:
                    barc=prov.split('&')
                    #barc[0] ha il codice della provetta, mentre barc[1] ha la posizione
                    listagen=Aliquot.objects.filter(Q(barcodeID=barc[0])&Q(availability=1))
                    #se la provetta e' piena
                    #VERSION FOR GRAPH_DB
                    if settings.USE_GRAPH_DB==True:
                        if listagen.count_old()!=0:
                            if listagen.count()==0:
                                prov=barc[0]+','+barc[1]+','+barc[2]+',NOT AVAILABLE,X'

                            else:
                                gen=listagen[0]
                                featu=Feature.objects.filter(Q(name='NumberOfPieces')&Q(idAliquotType=gen.idAliquotType.id))
                                if len(featu)!=0:
                                    pezzi=AliquotFeature.objects.filter(Q(idAliquot=gen)&Q(idFeature=featu[0]))
                                    if len(pezzi)!=0:
                                        prov=barc[0]+','+barc[1]+','+barc[2]+','+gen.uniqueGenealogyID+','+str(int(pezzi[0].value))
                                    else:
                                        prov=barc[0]+','+barc[1]+','+barc[2]+','+gen.uniqueGenealogyID+',0'
                                else:
                                    prov=barc[0]+','+barc[1]+','+barc[2]+','+gen.uniqueGenealogyID+',0'
                        else:
                            prov=barc[0]+','+barc[1]+','+barc[2]
                    #se la provetta e' vuota
                    else:
                        #VERSION WITH NO GRAPH_DB
                        if listagen.count()!=0:
                            #prendo il genID dato il barc della provetta
                            gen=listagen[0]
                            #visto che uso questa api anche per la schermata dello storage in cui
                            #rimetto a posto i container, devo distinguere tra derivati e aliq
                            #originali o block
                            #recupero l'oggetto feature relativo al numero di pezzi
                            featu=Feature.objects.filter(Q(name='NumberOfPieces')&Q(idAliquotType=gen.idAliquotType.id))
                            if len(featu)!=0:
                                #print 'feat',featu
                                pezzi=AliquotFeature.objects.filter(Q(idAliquot=gen)&Q(idFeature=featu[0]))
                                #print 'n pezzi',pezzi.value
                                if len(pezzi)!=0:
                                    prov=barc[0]+','+barc[1]+','+barc[2]+','+gen.uniqueGenealogyID+','+str(int(pezzi[0].value))
                                else:
                                    prov=barc[0]+','+barc[1]+','+barc[2]+','+gen.uniqueGenealogyID+',0'
                            else:
                                prov=barc[0]+','+barc[1]+','+barc[2]+','+gen.uniqueGenealogyID+',0'
                        #se la provetta e' vuota
                        else:
                            prov=barc[0]+','+barc[1]+','+barc[2]
                    lista.append(prov)
                return{"data":lista}
            except Exception,e:
                print 'err',e
                return {"data":'errore'}
        else:
            return  {'data':'inserire barcode'}'''
       
#Anche per gli impianti di caxeno. Data una lista di barcode delle provette,
#viene restituito il GenID delle aliquote che sono in quelle provette 
class TubeHandler(BaseHandler):
    allowed_methods = ('GET')
    @method_decorator(get_functionality_decorator)
    def read(self, request, barcode):
        lista=[]
        #il barcode ha la forma barcodeprovetta&posizione&coordinate_nella_piastra e i vari barc sono separati da
        #virgola
        if barcode:
            try:
                provette=barcode.split(',')
                #scandisco i barcode
                stringa=''
                for prov in provette:
                    barc=prov.split('&')[0]
                    stringa+=barc+'&'
                stringtot=stringa[:-1]
                diz=AllAliquotsContainer(stringtot)
                print 'provette',provette
                for prov in provette:
                    print 'prov',prov
                    barc=prov.split('&')
                    print 'barc',barc
                    listemp=diz[barc[0]]
                    #listemp e' formata da gen|barc|pos
                    lisgen=[]
                    for val in listemp:
                        vv=val.split('|')
                        gen=vv[0]
                        lisgen.append(gen)
                    #barc[0] ha il codice della provetta, mentre barc[1] ha la posizione
                    listagen=Aliquot.objects.filter(uniqueGenealogyID__in=lisgen,availability=1)
                    #se la provetta e' piena
                    if settings.USE_GRAPH_DB==False or 'admin' in get_WG():
                        if listagen.count()!=0:
                            #prendo il genID dato il barc della provetta
                            gen=listagen[0]
                            #visto che uso questa api anche per la schermata dello storage in cui
                            #rimetto a posto i container, devo distinguere tra derivati e aliq
                            #originali o block
                            #recupero l'oggetto feature relativo al numero di pezzi
                            featu=Feature.objects.filter(Q(name='NumberOfPieces')&Q(idAliquotType=gen.idAliquotType.id))
                            if len(featu)!=0:
                                #print 'feat',featu
                                pezzi=AliquotFeature.objects.filter(Q(idAliquot=gen)&Q(idFeature=featu[0]))
                                #print 'n pezzi',pezzi.value
                                if len(pezzi)!=0:
                                    prov=barc[0]+','+barc[1]+','+barc[2]+','+gen.uniqueGenealogyID+','+str(int(pezzi[0].value))
                                else:
                                    prov=barc[0]+','+barc[1]+','+barc[2]+','+gen.uniqueGenealogyID+',0'
                            else:
                                prov=barc[0]+','+barc[1]+','+barc[2]+','+gen.uniqueGenealogyID+',0'
                        #se la provetta e' vuota
                        else:
                            prov=barc[0]+','+barc[1]+','+barc[2]
                        lista.append(prov)
                    else:
                        disable_graph()
                        if Aliquot.objects.filter(uniqueGenealogyID__in=lisgen,availability=1).count()!=0:
                            if Aliquot.objects.filter(uniqueGenealogyID__in=lisgen,availability=1).count()==0:
                                prov=barc[0]+','+barc[1]+','+barc[2]+',NOT AVAILABLE,X'
                            else:
                                enable_graph()
                                gen=listagen[0]
                                featu=Feature.objects.filter(Q(name='NumberOfPieces')&Q(idAliquotType=gen.idAliquotType.id))
                                if len(featu)!=0:
                                    pezzi=AliquotFeature.objects.filter(Q(idAliquot=gen)&Q(idFeature=featu[0]))
                                    if len(pezzi)!=0:
                                        prov=barc[0]+','+barc[1]+','+barc[2]+','+gen.uniqueGenealogyID+','+str(int(pezzi[0].value))
                                    else:
                                        prov=barc[0]+','+barc[1]+','+barc[2]+','+gen.uniqueGenealogyID+',0'
                                else:
                                    prov=barc[0]+','+barc[1]+','+barc[2]+','+gen.uniqueGenealogyID+',0'
                            enable_graph()
                        else:
                            enable_graph()
                            prov=barc[0]+','+barc[1]+','+barc[2]
                        lista.append(prov)
                return{"data":lista}
            except Exception,e:
                print 'err',e
                return {"data":'errore'}
        else:
            return  {'data':'inserire barcode'}


#per gli impianti di caxeno. Caxeno comunica un dizionario di dati con i codici delle
#piastre all'interno delle quali c'e' l'indicazione se svuotare o meno la piastra. Poi
#anncora all'interno ci sono le posizioni della piastra che sono state toccate con dentro
#il numero di pezzi iniziale e quello attuale dopo l'impianto.       
class CancHandler(BaseHandler):
    allowed_methods = ('GET','POST',)  
    model= Aliquot
    @transaction.commit_on_success
    @csrf_exempt
    @method_decorator(get_functionality_decorator)
    def create(self, request):
        print request.POST
        try:
            listaimpl=json.loads(request.POST.get('implants'))
            listastor=[]
            
            for piastre in listaimpl:
                flag=False
                print 'piastra',piastre
                for val in listaimpl[piastre]:
                    print 'val',val
                    if val=='emptyFlag':
                        flag=listaimpl[piastre][val]
                        print 'flag',flag
                        if flag==True:
                            #vuol dire che devo svuotare tutta la piastra                        
                            address = Urls.objects.get(default = '1').url
                            req = urllib2.Request(address+"/api/plate/"+piastre + '/VT/', headers={"workingGroups" : get_WG_string()})
                            u = urllib2.urlopen(req)
                            data = json.loads(u.read())
                            print 'data',data
                            #prendo tutti i figli della piastra
                            for d in data['children']:
                                #vedo se ci sono campioni in quella piastra e li rendo 
                                #indisponibili
                                lista_aliq=Aliquot.objects.filter(uniqueGenealogyID=d['gen'],availability=1)
                                if len(lista_aliq)!=0:
                                    lista_aliq[0].availability=0
                                    lista_aliq[0].save()
                                    listastor.append(lista_aliq[0].uniqueGenealogyID)
                    else:
                        #se il flag e' true ho gia' eliminato le aliq della piastra,
                        #quindi non devo fare piu' niente
                        if flag==False:
                            #devo toccare solo i campioni effettivamente impiantati
                            #per ottenere il barcode data la posizione    
                            gen=listaimpl[piastre][val]['aliquot']
                            print 'gen',gen
    
                            lista_aliq=Aliquot.objects.filter(uniqueGenealogyID=gen,availability=1)
                            if len(lista_aliq)!=0:
                                aliq=lista_aliq[0]
                                print 'aliq',aliq
                                #prendo i pezzi rimanenti dopo l'impianto
                                if listaimpl[piastre][val]['actualQ']!=None:
                                    pezzi_nuovi=int(listaimpl[piastre][val]['actualQ'])
                                    print 'pezzi',pezzi_nuovi
                                    if pezzi_nuovi==0:   
                                        #rendo indisponibile il campione     
                                        aliq.availability=0
                                        aliq.save()
                                        listastor.append(aliq.uniqueGenealogyID)
                                    else:
                                        #aggiorno il numero di pezzi
                                        #recupero l'oggetto feature relativo al numero di pezzi per le aliq di quel tipo, se c'e'
                                        lfeatu=Feature.objects.filter(name='NumberOfPieces',idAliquotType=aliq.idAliquotType.id)
                                        if len(lfeatu)!=0:
                                            lpezzi=AliquotFeature.objects.filter(idAliquot=aliq,idFeature=lfeatu[0])
                                            if len(lpezzi)!=0:
                                                pezzi=lpezzi[0]
                                                print 'pezzi',pezzi.value
                                                pezzi.value=pezzi_nuovi
                                                pezzi.save()
                            
            print 'listastor',listastor
            if len(listastor)!=0:
                #mi collego allo storage
                address=Urls.objects.get(default=1).url
                url = address+"/full/"
                print url
                values = {'lista' : json.dumps(listastor), 'tube': 'empty','canc':True,'operator':None}
                data = urllib.urlencode(values)
                req = urllib2.Request(url,data=data, headers={"workingGroups" : get_WG_string()})
                urllib2.urlopen(req)   
            
            return {"data":'ok'}
        except Exception, e:
            print 'errore',e
            transaction.rollback()
            return {"data":'errore'}
            
class TissueHandler(BaseHandler):
    allowed_methods = ('GET')
    model = TissueType
    @method_decorator(get_functionality_decorator)
    def read(self, request):
            try:
                tess=TissueType.objects.all()
                return {'data':tess}
            except:
                return {"data":'errore'}
            
class CollectionTypeHandler(BaseHandler):
    allowed_methods = ('GET')
    @method_decorator(get_functionality_decorator)
    def read(self, request):
            try:
                liscoll=CollectionType.objects.all()
                return {'data':liscoll}
            except:
                return {"data":'errore'}

#per avere il contenuto di una piastra dato il suo barcode
class LoadHandler(BaseHandler):
    allowed_methods = ('GET')
    model = Aliquot
    @method_decorator(get_functionality_decorator)
    def read(self, request,barcode,tipo,store,derived):
        try:
            listaaliq=[]
            print 'derived',derived
            if store:
                url = Urls.objects.get(default = '1').url + "/api/plate/"+barcode+'/'+tipo+'/'+store
            else:
                url=Urls.objects.get(default = '1').url + "/api/plate/"+barcode+'/'+tipo
            try:
                #prendo i dati dall'archivio che mi da' la posizione e il barcode delle aliq
                req = urllib2.Request(url, headers={"workingGroups" : get_WG_string()})
                u = urllib2.urlopen(req)
                #u = urllib2.urlopen(url)
                res =  u.read()
                #print res
                data = json.loads(res)
                print 'data',data
            except Exception, e:
                print 'e',e
                return {'data':'errore_store'}
               
            if data['data']=='errore_aliq':
                return {'data':'errore_aliq'}
            if data['data']=='errore_piastra':
                return {'data':'errore_piastra'}  
            if derived!='':
                tipoal=AliquotType.objects.get(abbreviation=tipo)
                #recupero l'oggetto feature relativo al numero di pezzi per le aliq di quel tipo
                featu=Feature.objects.filter(name='NumberOfPieces',idAliquotType=tipoal)
                print featu
            #scandisco i barcode
            for w in data['children']:
                #solo se la provetta e' piena
                
                if w['full']=='True':
                    if derived!='':
                        #prendo il genID dato il barc della provetta
                        aliq=Aliquot.objects.get(uniqueGenealogyID=w['gen'],availability=1)
                        #solo se e' un'aliquota originale ha i pezzi
                        if len(featu)!=0:
                            pezzi=AliquotFeature.objects.get(idAliquot=aliq,idFeature=featu[0])
                            w['numberOfPieces']=pezzi.value
                    else:
                        #se e' derivata metto un campo fittizio
                        w['derive']='1'
                listaaliq.append(w)
            print 'lista',listaaliq
            return {'data':listaaliq}
        except Exception,e:
            print 'err',e
            return {"data":'errore'}
        
#dato il numero di protocollo mi restituisce tutti i singoli kit del tipo generico di kit
#collegato a quel protocollo
class SingleKitHandler(BaseHandler):
    allowed_methods = ('GET')
    @method_decorator(get_functionality_decorator)
    def read(self, request,tipo):
        try:
            print '[BBM] api kit'
            prot=DerivationProtocol.objects.get(id=tipo)
            kit=prot.idKitType
            print 'kit',kit
            query=Kit.objects.filter(idKitType=kit.id,remainingCapacity__gt=0)
            return {'data':query,'tipo':tipo}
        except Exception,e:
            print 'err',e
            return {"data":'errore'}
        
#dato il numero di protocollo mi da' il nome del tipo di kit associato
class KitHandler(BaseHandler):
    allowed_methods = ('GET')
    @method_decorator(get_functionality_decorator)
    def read(self, request,tipo):
        try:
            prot=DerivationProtocol.objects.get(id=tipo)
            if prot.idKitType!=None:
                kit=prot.idKitType
            else:
                kit={'name':''}
            #query=KitType.objects.get(id=kit.id)
            return {'data':kit}
        except:
            return {"data":'errore'}

#dato il genealogy mi da' il nome dei file associati agli eventi di derivazione in
#cui quell'aliquota e' stata la madre
class DerivedFileHandler(BaseHandler):
    allowed_methods = ('GET')
    @method_decorator(get_functionality_decorator)
    def read(self, request,gen):
        try:
            lista1=[]
            listafile=[]
            valore=''
            aliq=Aliquot.objects.get(uniqueGenealogyID=gen)
            alder=AliquotDerivationSchedule.objects.filter(idAliquot=aliq,derivationExecuted=1,deleteTimestamp=None)
            for i in range(0,len(alder)):
                lista1.append( Q(**{'idAliquotDerivationSchedule': alder[i]} ))
            if len(lista1)!=0:
                #prendo le aliq derivate, ma anche quelle collegate a quel quality event
                #perche' rivalutate
                listaqual=QualityEvent.objects.filter(Q(reduce(operator.or_, lista1))|Q(idAliquot=aliq))
            else:
                listaqual=QualityEvent.objects.filter(idAliquot=aliq)
            print 'lqual',listaqual
            if len(listaqual)!=0:
                del lista1[:]
                for i in range(0,len(listaqual)):
                    lista1.append( Q(**{'idQualityEvent': listaqual[i]} ))
                    if len(lista1)!=0:
                        listafile=QualityEventFile.objects.filter(Q(reduce(operator.or_, lista1)))
                        #print 'lista',listafile
            if len(listafile)!=0:
                for i in range(0,len(listafile)):
                    data=listafile[i].idQualityEvent.misurationDate
                    d=str(data).split('-')
                    dat=d[2]+'-'+d[1]+'-'+d[0]
                    #devo discriminare se e' una rivalutazione o una derivazione
                    if listafile[i].idQualityEvent.idAliquotDerivationSchedule!=None:
                        #e' una derivazione
                        valore=valore+listafile[i].file+'&'+dat+'&'+'Derivation|'
                    else:
                        #e' una rivalutazione
                        valore=valore+listafile[i].file+'&'+dat+'&'+'Revaluation|'
                    
            return {'data':valore}
        except Exception, e:
            print 'err',e
            return {"data":'errore'}

#serve nelle aliquote derivate per vedere se il genealogy id dell'aliquota da derivare,
#introdotto dall'utente, esiste o meno nel DB, se e' del tipo giusto e se l'aliquota non
#e' gia' stata programmata per la derivazione      
class DerivedAliquotHandler(BaseHandler):
    allowed_methods = ('GET')
    @method_decorator(get_functionality_decorator)
    def read(self, request,gen,protoc):
        try:
            
            diz=AllAliquotsContainer(gen)
            lista=diz[gen]
            if len(lista)==0:
                return{'data':'inesistente'}
            
            #e' una lista in cui ogni valore e' una stringa formata da gen|barcode|posizione
            for val in lista:
                ch=val.split('|')
                #per controllare se l'aliquota e' di questo wg        
                lisal=Aliquot.objects.filter(uniqueGenealogyID=ch[0],availability=1)
                if len(lisal)==0:
                    return{'data':'inesistente'}
                else:                    
                    al=lisal[0]
                trovato=0
                #vedo se l'aliquota e' gia' stata programmata per la derivazione e verra' esaurita alla fine
                aldersched=AliquotDerivationSchedule.objects.filter(idAliquot=al,derivationExecuted=0,deleteTimestamp=None,aliquotExhausted=1)
                print 'alqual',aldersched
                if(aldersched.count()!=0):
                    return {'data':'presente'}
                
                #protoc e' l'id del tipo di derivato creato (DNA, RNA...)
                tipi=TransformationChange.objects.filter(idToType=protoc)
                for t in tipi:
                    if al.idAliquotType.id==t.idFromType.id:
                        trovato=1
                        print 'from',t.idFromType
                        break
                if trovato==0:
                    return {'data':'tipoerr'}
                
                #se sto creando plasma(PL) o PBMC(VT) devo controllare che il tipo di tessuto sia sangue
                aliqtipo=AliquotType.objects.get(id=protoc)
                if aliqtipo.abbreviation=='PL' or aliqtipo.abbreviation=='VT':
                    if al.idSamplingEvent.idTissueType.abbreviation!='BL':
                        return {'data':'tipoerr'}

            return {'data':lista}
        except Exception,e:
            print 'errore',e
            return {"data":'errore'}

#per caricare le piastre a priori durante la derivazione e quindi per sapere se il
#tipo della piastra e' giusto
class DerivedLoadHandler(BaseHandler):
    allowed_methods = ('GET')
    @method_decorator(get_functionality_decorator)
    def read(self, request, barcodeP, typeP):
        try:
            print barcodeP           
            #spezzo in base a | per avere i singoli tipi di piastra (ad es RNA,DNA)
            tipi=typeP.split('&')
            #mi serve per sapere quale e' il tipo della piastra
            tipoeffettivo=tipi[0]
            address = Urls.objects.get(default = '1').url
            conta=0
            for i in range(0,len(tipi)-1):
                try:
                    #u = urllib2.urlopen(address+"/api/plate/"+barcodeP + '/' + tipi[i]+'/')
                    req = urllib2.Request(address+"/api/plate/"+barcodeP + '/' + tipi[i]+'/', headers={"workingGroups" : get_WG_string()})
                    u = urllib2.urlopen(req)
                    data = json.loads(u.read())
                    print 'data',data
                except Exception, e:
                    print 'e',e
                    return {'data':'errore_store'}
                
                if data['data']=='errore_aliq':
                    conta+=1
                    if (i+1)!=len(tipi)-1:
                        tipoeffettivo=tipi[i+1]
                        print 'tipo',tipoeffettivo
                if data['data']=='errore_piastra':
                    return {'data':'errore_piastra'}  
                if data['data']=='errore':
                    return {'data':'errore'}
            print 'conta',conta
            if conta==(len(tipi)-1):
                return {'data':'errore_aliq'} 
            return {'data':tipoeffettivo} 
        except Exception, e:
            print 'err',e
            return {"data": 'errore'}

#dato l'id del protocollo di derivazione, mi da' l'abbreviazione del tipo di derivato
#che vado a creare e anche tutti gli altri parametri
class DerivedCalculateHandler(BaseHandler):
    allowed_methods = ('GET')
    @method_decorator(get_functionality_decorator)
    def read(self, request,prot):
        try:
            lista=[]
            #per capire qual e' il tipo di derivato prodotto
            pro=int(prot)
            listatipi=TransformationDerivation.objects.filter(idDerivationProtocol=pro)
            print 'listatipi',listatipi
            tipo=listatipi[0].idTransformationChange.idToType.abbreviation
            tipesteso=listatipi[0].idTransformationChange.idToType.longName
            #devo sapere quali tipi di aliq sono selezionabili come ingresso del prot
            for tip in listatipi:
                tipoal=tip.idTransformationChange.idFromType.abbreviation
                if tipoal not in lista:
                    lista.append(tipoal)
            #apro il file con dentro i parametri per la derivazione
            percorso=os.path.join(os.path.dirname(__file__),'tissue_media/File_Format/Regole_aliq_derivate.txt')
            percorso=percorso.replace('api','tissue')
            print 'perc2',percorso
            f=open(percorso)
            lines = f.readlines()
            f.close()
            riga=''
            #prendo il protocollo di derivazione
            derprot=DerivationProtocol.objects.get(id=pro)
            numal=FeatureDerivation.objects.get(name='number_Aliquot')
            volal=FeatureDerivation.objects.get(name='volume_Aliquot')
            concal=FeatureDerivation.objects.get(name='concentration_Aliquot')
            #regole=json.loads(derprot.rules)
            #num_aliq=regole['number_Aliquot']
            #vol=regole['volume_Aliquot']
            #conc=regole['concentration_Aliquot']
            featnumal=FeatureDerProtocol.objects.get(idDerProtocol=derprot,idFeatureDerivation=numal)
            num_aliq=int(featnumal.value)
            featvolal=FeatureDerProtocol.objects.get(idDerProtocol=derprot,idFeatureDerivation=volal)
            vol=featvolal.value
            featconcal=FeatureDerProtocol.objects.get(idDerProtocol=derprot,idFeatureDerivation=concal)
            conc=featconcal.value
            #calcolo l'estremo inferiore con num_aliq*vol*conc
            #es_inf=int(num_aliq)*float(vol)*(float(conc)/1000.0)
            #print 'estremo inf',es_inf
            #calcolo l'estremo superiore con (num_aliq+4)*vol*conc
            #es_sup=(int(num_aliq)+4)*float(vol)*(float(conc)/1000.0)
            #print 'estremo sup',es_sup
            riga+=tipo+';'+str(num_aliq)+';'+str(vol)+';'+str(conc)+';'#+str(es_sup)+';'+str(es_inf)+';'
            for line in lines:
                valori=line.split(';')
                #se ho trovato la riga giusta che inizia con il nome del derivato
                if valori[0]==tipo:
                    riga+=valori[1]+';'+valori[2]+';'+valori[3].strip()
            print 'riga',riga
            
            return {'data':tipesteso,'riga':riga,'tipi':lista}
        except Exception, e:
            print 'err',e
            return {"data": 'errore'}

#dato l'id del protocollo di derivazione e l'abbreviazione del tipo di derivato che si
#vuole creare, mi dice se le due cose sono compatibili, cioe' se applicando quel 
#protocollo si riesce ad ottenere quel derivato
class DerivedChooseHandler(BaseHandler):
    allowed_methods = ('GET')
    @method_decorator(get_functionality_decorator)
    def read(self, request,protoc,tipo):
        try:
            #per capire qual e' il tipo di derivato prodotto
            pro=int(protoc)
            t=TransformationDerivation.objects.filter(idDerivationProtocol=pro)
            ti=t[0].idTransformationChange.idToType.abbreviation
            if ti!=tipo:
                return {"data": 'err'}
            else:
                return {"data": 'ok'}
        except Exception, e:
            print 'err',e
            return {"data": 'errore'}
        
#serve a restituire tutti i genid delle aliquote derivate create in una certa sessione
class DerivedFinalSessionHandler(BaseHandler):
    allowed_methods = ('GET')
    @method_decorator(get_functionality_decorator)
    def read(self, request):
        try:
            lista=request.session.get('lista_al_der_sessione')
            print 'lista',lista
            ris=''
            for i in range(0,len(lista)):
                lis_derevent=DerivationEvent.objects.filter(idAliqDerivationSchedule=lista[i].id)
                print 'lis_der',lis_derevent
                if len(lis_derevent)!=0:
                    #prendo il derivation event
                    derevent=lis_derevent[0]
                    print 'derevent',derevent
                    #prendo le aliquote con quel sampling event
                    lis_aliquote=Aliquot.objects.filter(idSamplingEvent=derevent.idSamplingEvent.id)
                    for aliq in lis_aliquote:
                        ris+=aliq.uniqueGenealogyID+':'+str(i+1)+'|'
            print 'ris',ris
            return {"data": ris}
        except Exception, e:
            print 'err',e
            return {"data": 'errore'}
        
#Serve nelle derivazioni con il robot per prendere i valori delle misure dal DB di Hamilton e scriverli nel DB del LAS 
class DerivedUpdateValueMeasureHandler(BaseHandler):
    allowed_methods = ('GET')
    @method_decorator(get_functionality_decorator)
    @transaction.commit_manually
    @transaction.commit_manually(using='dbhamilton')
    def read(self, request):
        try:
            #chiave il timestamp e valore l'aldersched
            #diztime={}
            #listimestamp=[]
            #stringat=''
            name=request.user.username
            instr=Instrument.objects.get(name='Hamilton')
            featrobot=FeatureDerivation.objects.get(name='Robot')
            lisprotrobot=FeatureDerProtocol.objects.filter(idFeatureDerivation=featrobot).values_list('idDerProtocol',flat=True)
            #devo prendere i protocolli per le misure, quindi quelli di tipo uv e fluo
            lisprotype=ProtocolTypeHamilton.objects.filter(name__in=['fluo','uv']).values_list('id',flat=True)
            lisprot=ProtocolHamilton.objects.filter(protocol_type_id__in=lisprotype).values_list('id',flat=True)
            print 'lisprot',lisprot
            lisplanprot=PlanHasProtocolHamilton.objects.filter(protocol_id__in=lisprot).values_list('plan_id',flat=True)
            lisplan=PlanHamilton.objects.filter(operator=name,id__in=lisplanprot,executed__isnull=False,processed__isnull=True)
            listapiani=[]
            for pl in lisplan:
                listapiani.append(pl.id)
            lissample=SampleHamilton.objects.filter(plan_id__in=listapiani).order_by('rank')
            print 'lissample',lissample
            #chiave l'idalidersched e valore un dizionario con volume e concentrazioni presenti
            dizmisure={}
            #per ogni campione devo prendere le misure collegate e salvarle nel DB della biobanca            
            for samp in lissample:
                dizmis={}
                lismis=MeasureHamilton.objects.filter(sample_id=samp)
                print 'lismis',lismis
                for mis in lismis:
                    nome=mis.name                    
                    if nome in dizmis:
                        diztemp=dizmis[nome]
                        version=diztemp['version']
                        time=diztemp['time']
                        print 'time',time                            
                        print 'version',version
                        print 'mis version',mis.version
                        #devo prendere l'ultima misura, quindi quella con la versione maggiore oppure quella piu' recente cioe' con il timestamp
                        #maggiore. Facendo cosi' potrei prendere la nuova versione pero' di una misura fatta prima di un'altra e quindi non l'ultima
                        #in ordine di tempo. Ma va bene cosi'
                        if mis.run_id.timestamp>time or mis.version>version:
                            diztemp['value']=mis.value
                            diztemp['version']=mis.version
                            diztemp['time']=mis.run_id.timestamp
                        dizmis[nome]=diztemp
                    else:
                        diztemp={}
                        diztemp['value']=mis.value
                        diztemp['version']=mis.version
                        diztemp['time']=mis.run_id.timestamp
                        dizmis[nome]=diztemp
                    #prendo il timestamp dell'ultima misura che tanto e' uguale a quella delle altre
                    datamisura=mis.run_id.timestamp
                plan=samp.plan_id
                
                aliquota=Aliquot.objects.get(uniqueGenealogyID=samp.genid)
                #stringat+=samp.genid+'&'
                #prendo l'aliqdersched
                laliqdersched=AliquotDerivationSchedule.objects.filter(Q(idPlanRobot__in=listapiani)&Q(idAliquot=aliquota)&Q(derivationExecuted=0)&Q(Q(operator=name)|Q(operator=''))&~Q(idDerivationProtocol=None)&Q(idDerivationProtocol__in=lisprotrobot)&~Q(volumeOutcome=None)&Q(measurementExecuted=1)&Q(deleteTimestamp=None))
                print 'laliqdersched',laliqdersched
                if len(laliqdersched)>1:
                    transaction.rollback()
                    transaction.rollback(using='dbhamilton')
                    return {'error':'Sample '+samp.genid+' has more than one derivation planned'}
                elif len(laliqdersched)==0:
                    #vuol dire che ho preso dei sample di un plan non ancora eseguito che pero' non appartengono alla derivazione, ma alla rivalutazione
                    #quindi vado avanti e non considero questi sample
                    continue 
                aliqdersched=laliqdersched[0]
                #listimestamp.append(aliqdersched.validationTimestamp)
                #diztime[aliqdersched.validationTimestamp]={'gen':samp.genid}
                lprotocol=PlanHasProtocolHamilton.objects.filter(plan_id=plan)
                vol_taken=0.0
                for p in lprotocol:
                    vol_taken+=p.protocol_id.vol_taken
                
                qualprot=QualityProtocol.objects.get(idAliquotType=aliqdersched.idDerivedAliquotType,description='hamilton')
                #creo il qualityevent
                qualev=QualityEvent(idQualityProtocol=qualprot,
                                    idAliquot=aliquota,
                                    idAliquotDerivationSchedule=aliqdersched,
                                    misurationDate=datetime.date(datamisura.year,datamisura.month,datamisura.day),
                                    insertionDate=date.today(),
                                    operator=name,
                                    quantityUsed=float(vol_taken))
                qualev.save()
                print 'dizmis',dizmis
                diztemp={}
                for nome,dizvalori in dizmis.items():
                    try:
                        float(dizvalori['value'])
                    except:
                        #passa al valore dopo perche' non e' un valore valido
                        continue
                    if nome.lower().startswith('concentration'):
                        #per fare un'interrogazione che non tenga conto delle maiuscole/minuscole
                        lmisura=Measure.objects.filter(idInstrument=instr,name__iexact=nome)
                        diztemp[lmisura[0].id]=float(dizvalori['value'])
                    elif nome=='260/230':
                        lmisura=Measure.objects.filter(idInstrument=instr,name='purity',measureUnit='260/230')
                    elif nome=='260/280':
                        lmisura=Measure.objects.filter(idInstrument=instr,name='purity',measureUnit='260/280')
                    if len(lmisura)==0:
                        transaction.rollback()
                        transaction.rollback(using='dbhamilton')
                        return {'error':'Measure '+nome+' not recognized'}
                    
                    #arrotondo a 3 cifre decimali
                    valorefloat=round(float(dizvalori['value']),3)
                    evmisur=MeasurementEvent(idMeasure=lmisura[0],
                                            idQualityEvent=qualev,
                                            value=valorefloat)
                    evmisur.save()
                voltot=aliqdersched.volumeOutcome
                voleffettivo=voltot-vol_taken
                diztemp['volume']=voleffettivo
                dizmisure[aliqdersched.id]=diztemp
                aliqdersched.measurementExecuted=1
                aliqdersched.save()
                plan.processed=timezone.localtime(timezone.now())
                plan.save()
            print 'listapiani',listapiani
            lisaliqdersched=AliquotDerivationSchedule.objects.filter(Q(idPlanRobot__in=listapiani)&Q(Q(operator=name)|Q(operator=''))&~Q(idDerivationProtocol=None)&Q(idDerivationProtocol__in=lisprotrobot)&Q(deleteTimestamp=None)).order_by('validationTimestamp')            
            stringat=''
            lisfallite=[]
            lisfinale=[]
            prot=None
            for al in lisaliqdersched:
                stringat+=al.idAliquot.uniqueGenealogyID+'&'
                #prendo l'ultimo prot di derivazione della lista, tanto ho solo bisogno di sapere i parametri del prot
                prot=al.idDerivationProtocol
                if al.failed==1:           
                    lisfallite.append(al.id)
                lisfinale.append({'gen':al.idAliquot.uniqueGenealogyID,'id':al.id})
            print 'prot',prot
            stringtotale=stringat[:-1]
            dizpos=AllAliquotsContainer(stringtotale)
            '''lisbarc=[]
            lispos=[]            
            
            for al in lisaliqdersched:
                listatemp=dizpos[al.idAliquot.uniqueGenealogyID]
                for val in listatemp:
                    ch=val.split('|')
                    #se il campione e' esaurito perche' appartiene ad una derivazione fallita in cui e' stato esaurito il campione, allora non
                    #ho la posizione e quindi metto una stringa vuota
                    if len(ch)>1:
                        lisbarc.append(ch[1])
                        lispos.append(ch[2])
                    else:
                        lisbarc.append('')
                        lispos.append('')'''
            
            print 'dizmisure',dizmisure
            num_aliq='' 
            vol='' 
            concen=''
            if prot!=None:
                numal=FeatureDerivation.objects.get(name='number_Aliquot')
                volal=FeatureDerivation.objects.get(name='volume_Aliquot')
                concal=FeatureDerivation.objects.get(name='concentration_Aliquot')
                featnumal=FeatureDerProtocol.objects.get(idDerProtocol=prot,idFeatureDerivation=numal)
                num_aliq=int(featnumal.value)
                featvolal=FeatureDerProtocol.objects.get(idDerProtocol=prot,idFeatureDerivation=volal)
                vol=featvolal.value
                featconcal=FeatureDerProtocol.objects.get(idDerProtocol=prot,idFeatureDerivation=concal)
                concen=featconcal.value
            print 'lista',lisaliqdersched
            #passo alla schermata il nome del primo plan che trovo. So che puo' essercene piu' di 1, ma scelgo comunque il primo. Al massimo sara' l'utente a
            #cambiare il nome del plan che compare nella schermata
            nomplan=''
            labwareid=0
            if len(lisplan)!=0:
                nomplan=lisplan[0].name
                labwareid=lisplan[0].labwareid.id
            print 'num al',num_aliq
            transaction.commit()
            transaction.commit(using='dbhamilton')
            return {'dizpos':json.dumps(dizpos),'lisdersched':json.dumps(lisfinale),'dizmisure':json.dumps(dizmisure),'lisfallite':json.dumps(lisfallite),'num_al':num_aliq,'vol_al':vol,'conc_al':concen,'nomeplan':nomplan,'labwareid':labwareid}
        except Exception, e:
            print 'err',e
            transaction.rollback()
            transaction.rollback(using='dbhamilton')
            return {'error': 'Error in saving data'}
        
#serve a restituire tutti i genid delle aliquote da dividere create in una certa sessione
class SplitFinalSessionHandler(BaseHandler):
    allowed_methods = ('GET')
    @method_decorator(get_functionality_decorator)
    def read(self, request):
        try:
            lista=request.session.get('aliqdividere')
            print 'lista',lista
            ris=''
            for i in range(0,len(lista)):
                if lista[i].splitExecuted==1:
                    #prendo le aliquote con quel sampling event
                    lis_aliquote=Aliquot.objects.filter(idSamplingEvent=lista[i].idSamplingEvent.id)
                    for aliq in lis_aliquote:
                        ris+=aliq.uniqueGenealogyID+':'+str(i+1)+'|'
            print 'ris',ris
            return {"data": ris}
        except Exception, e:
            print 'err',e
            return {"data": 'errore'}

#mi restituisce l'indirizzo dello storage
class AddressHandler(BaseHandler):
    allowed_methods = ('GET')
    @method_decorator(get_functionality_decorator)
    def read(self, request):
        try:
            indirizzo=Urls.objects.get(default = '1').url
            return {'data':indirizzo}
        except:
            return {"data":'errore'}

#serve nelle aliquote da rivalutare per vedere se il genealogy id dell'aliquota da rivalutare,
#introdotto dall'utente, esiste o meno nel DB e se l'aliquota non e' gia' stata programmata
#per la rivalutazione
class RevaluateAliquotHandler(BaseHandler):
    allowed_methods = ('GET')
    @method_decorator(get_functionality_decorator)
    def read(self, request,gen,split):
        try:
            diz=AllAliquotsContainer(gen)
            lista=diz[gen]
            if len(lista)==0:
                return{'data':'inesistente'}

            #e' una lista in cui ogni valore e' una stringa formata da gen|barcode|posizione
            for val in lista:
                ch=val.split('|')
                #per controllare se l'aliquota e' di questo wg        
                lisal=Aliquot.objects.filter(uniqueGenealogyID=ch[0],availability=1)
                if len(lisal)==0:
                    return{'data':'inesistente'}
                else:                    
                    al=lisal[0]
                #guardo se l'aliquota e' un derivato. Non lo faccio piu' per permettere di inserire anche tessuti
                #e metterli esauriti
                #if al.derived==0:
                    #return {'data':'derivato'}
                
                if split:
                    #vedo se l'aliq e' gia' stata programmata per la divisione
                    alqualsched=AliquotSplitSchedule.objects.filter(idAliquot=al,splitExecuted=0,deleteTimestamp=None)
                else:
                    #vedo se l'aliquota e' gia' stata programmata per la rivalutazione
                    alqualsched=AliquotQualitySchedule.objects.filter(idAliquot=al,revaluationExecuted=0,deleteTimestamp=None)
                print 'alqual',alqualsched
                if(alqualsched.count()!=0):
                    return {'data':'presente'}

            return {'data':lista}
        except Exception,e:
            print 'err',e
            return {"data":'errore'}
        
#serve nella sezione delle aliquote esterne. Data l'abbreviazione di un tumore, restituisce
#le collezioni che contengono aliquote di quel tumore
class ExternHandler(BaseHandler):
    allowed_methods = ('GET')
    @method_decorator(get_functionality_decorator)
    def read(self, request,tipo):
        try:
            tumore=CollectionType.objects.get(longName__iexact=tipo)
            
            idtumore=tumore.id
            query=Collection.objects.filter(idCollectionType=idtumore)
            return {'data':query}
        except:
            return {"data":'errore'}
        
#serve nella sezione delle aliquote esterne. Mi restituisce tutti i tipi di aliquote
class ExternAliquotTypeHandler(BaseHandler):
    allowed_methods = ('GET')
    @method_decorator(get_functionality_decorator)
    def read(self, request):
        try:
            aliq=AliquotType.objects.all()             
            return {'data':aliq}
        except:
            return {"data":'errore'}
        
#serve per creare un nuovo genid nella sezione delle aliquote esterne
class ExternNewgenidHandler(BaseHandler):
    allowed_methods = ('GET')
    @method_decorator(get_functionality_decorator)
    def read(self, request,tum,caso,tess,centro,tesstopo,tipoaliq,contat,cell):
        try:
            tumore=CollectionType.objects.get(id=tum)
            inizio=tumore.abbreviation+caso
            tessuto=TissueType.objects.get(id=tess).abbreviation
            if tesstopo!='None':
                ttopo=MouseTissueType.objects.get(id=tesstopo).abbreviation
            else:
                #se centro comincia con H vuol dire che sto inserendo un tessuto umano e quindi devo mettere tutti zeri
                if centro[0]=='H':
                    ttopo='000'
                else:
                    ttopo='001'
            contatore='01'
            #per le linee cellulari
            scong=''
            passage=''
            if not cell:
                #per fare in modo che il tipoaliq possa essere a volte l'id a volte l'abbreviazione (VT,SF...)
                try:
                    value = int(tipoaliq)
                    tipal=AliquotType.objects.get(id=value).abbreviation
                except ValueError:
                    tipal=AliquotType.objects.get(abbreviation=tipoaliq).abbreviation
                if tipal=='DNA':
                    genid=inizio+tessuto+centro+ttopo+'D'
                    disable_graph()
                    lista_aliquote=Aliquot.objects.filter(Q(uniqueGenealogyID__startswith=genid)&Q(uniqueGenealogyID__endswith='000')&Q(derived=1)).order_by('-uniqueGenealogyID')
                    enable_graph()
                    if lista_aliquote.count()!=0:
                        #prendo il primo oggetto che e' quello che ha il contatore piu' alto
                        maxgen=lista_aliquote[0].uniqueGenealogyID
                        nuovoge=GenealogyID(maxgen)
                        maxcont=nuovoge.getAliquotExtraction()
                        contatore=int(maxcont)
                    else:
                        contatore=0
                    #contatore mi da' il primo cont disponibile secondo il DB. Contat mi da' il primo disponibile
                    #basandosi sulla schermata. Quindi li sommo e ottengo quello definitivo.
                    contfinale=int(contatore)+(int(contat))
                    if contfinale <10:
                        conta = '0' + str(contfinale)
                    else:
                        conta=str(contfinale)
                    genid+=conta+'000'
                elif tipal=='RNA':
                    genid=inizio+tessuto+centro+ttopo+'R'
                    disable_graph()
                    lista_aliquote=Aliquot.objects.filter(Q(uniqueGenealogyID__startswith=genid)&Q(uniqueGenealogyID__endswith='000')&Q(derived=1)).order_by('-uniqueGenealogyID')
                    enable_graph()
                    if lista_aliquote.count()!=0:
                        #prendo il primo oggetto che e' quello che ha il contatore piu' alto
                        maxgen=lista_aliquote[0].uniqueGenealogyID
                        nuovoge=GenealogyID(maxgen)
                        maxcont=nuovoge.getAliquotExtraction()
                        contatore=int(maxcont)
                    else:
                        contatore=0
                    #contatore mi da' il primo cont disponibile secondo il DB. Contat mi da' il primo disponibile
                    #basandosi sulla schermata. Quindi li sommo e ottengo quello definitivo.
                    contfinale=int(contatore)+(int(contat))
                    if contfinale <10:
                        conta = '0' + str(contfinale)
                    else:
                        conta=str(contfinale)
                    genid+=conta+'000'
                elif tipal=='cDNA':
                    genid=inizio+tessuto+centro+ttopo+'R'+contatore+'D'
                    disable_graph()
                    lista_aliquote=Aliquot.objects.filter(Q(uniqueGenealogyID__startswith=genid)&Q(derived=1)).order_by('-uniqueGenealogyID')
                    enable_graph()
                    if lista_aliquote.count()!=0:
                        #prendo il primo oggetto che e' quello che ha il contatore piu' alto
                        maxgen=lista_aliquote[0].uniqueGenealogyID
                        nuovoge=GenealogyID(maxgen)
                        maxcont=nuovoge.get2DerivationGen()
                        contatore=int(maxcont)
                    else:
                        contatore=0
                    #contatore mi da' il primo cont disponibile secondo il DB. Contat mi da' il primo disponibile
                    #basandosi sulla schermata. Quindi li sommo e ottengo quello definitivo.
                    contfinale=int(contatore)+(int(contat))
                    if contfinale <10:
                        conta = '0' + str(contfinale)
                    else:
                        conta=str(contfinale)
                    genid+=conta
                elif tipal=='cRNA':
                    genid=inizio+tessuto+centro+ttopo+'R'+contatore+'R'
                    disable_graph()
                    lista_aliquote=Aliquot.objects.filter(Q(uniqueGenealogyID__startswith=genid)&Q(derived=1)).order_by('-uniqueGenealogyID')
                    enable_graph()
                    if lista_aliquote.count()!=0:
                        #prendo il primo oggetto che e' quello che ha il contatore piu' alto
                        maxgen=lista_aliquote[0].uniqueGenealogyID
                        nuovoge=GenealogyID(maxgen)
                        maxcont=nuovoge.get2DerivationGen()
                        contatore=int(maxcont)
                    else:
                        contatore=0
                    #contatore mi da' il primo cont disponibile secondo il DB. Contat mi da' il primo disponibile
                    #basandosi sulla schermata. Quindi li sommo e ottengo quello definitivo.
                    contfinale=int(contatore)+(int(contat))
                    if contfinale <10:
                        conta = '0' + str(contfinale)
                    else:
                        conta=str(contfinale)
                    genid+=conta
                else:
                    genid=inizio+tessuto+centro+ttopo+tipal
                    disable_graph()
                    lista_aliquote=Aliquot.objects.filter(Q(uniqueGenealogyID__startswith=genid)&Q(derived=0)).order_by('-uniqueGenealogyID')
                    enable_graph()
                    if lista_aliquote.count()!=0:
                        #prendo il primo oggetto che e' quello che ha il contatore piu' alto
                        maxgen=lista_aliquote[0].uniqueGenealogyID
                        nuovoge=GenealogyID(maxgen)
                        maxcont=nuovoge.getAliquotExtraction()
                        contatore=int(maxcont)
                    else:
                        contatore=0
                    #serve per ovviare al problema delle aliquote fittizie inserite. Infatti se inserisco una nuova aliq dopo una vt99 diventa vt100
                    #e non va bene. Quindi tolgo 20 dal contatore.
                    if contatore>98:
                        contatore=contatore-10
                        liscont=[]
                        for aliq in lista_aliquote:
                            nuovoge=GenealogyID(aliq.uniqueGenealogyID)
                            maxcont=nuovoge.getAliquotExtraction()
                            liscont.append(int(maxcont))
                        while (contatore+1) in liscont:
                            contatore+=1
                    print 'contatore',contatore
                    #contatore mi da' il primo cont disponibile secondo il DB. Contat mi da' il primo disponibile
                    #basandosi sulla schermata. Quindi li sommo e ottengo quello definitivo.
                    contfinale=int(contatore)+(int(contat))
                    if contfinale <10:
                        conta = '0' + str(contfinale)
                    else:
                        conta=str(contfinale)
                    genid+=conta+'00'
            else:
                #centro e' il vettore (A o S)
                genid=inizio+tessuto+centro
                disable_graph()
                lista_aliquote=Aliquot.objects.filter(uniqueGenealogyID__startswith=genid,derived=0).order_by('-id')
                enable_graph()
                print 'lista aliq',lista_aliquote
                if len(lista_aliquote)!=0:
                    #prendo il primo oggetto che e' quello che ha il lineage piu' alto
                    maxgen=lista_aliquote[0].uniqueGenealogyID
                    nuovoge=GenealogyID(maxgen)
                    lin=nuovoge.getLineage()
                    n=translateLineage(lin)
                    linfin=newLineage(n)
                    print 'linfin',linfin
                    scong=nuovoge.getSamplePassage()
                    passage=nuovoge.getMouse()
                else:
                    linfin='0A'
                    scong='0'
                    passage='0'

                #il contatore dipende solo dalla schermata di inserimento, perche' nel DB non ho sicuramente
                #altri gen come questo
                contfinale=int(contat)
                conta=str(contfinale).zfill(2)
                genid+=linfin
                
            print 'genid',genid
            print 'scong',scong
            print 'pass',passage
            return {'cont':contfinale,'gen':genid,'scong':scong,'passage':passage,'presenti':contatore}
        except Exception,e:
            print 'err',e
            return {"data":'errore'}

#per avere il contenuto di una piastra dato il suo barcode
class TableHandler(BaseHandler):
    allowed_methods = ('GET')
    @method_decorator(get_functionality_decorator)
    def read(self, request, barcodeP, typeP,ext):        
        #print 'request',request
        try:
            abbr = ""
            name = ""
            print 'tipo',typeP
            #e' una lista con tutti i gen. Serve per le linee cellulari al caricamento di una piastra
            lisaliquote=[]
            if typeP == 'VT':
                abbr = 'v'
                name = 'vital'
                long_name = 'VIABLE'
            if typeP == 'SF':
                abbr = 's'
                name = 'sf'
                long_name = 'SNAP FROZEN'
            if typeP == 'RL':
                abbr = 'r'
                name = 'rna'
                long_name = 'RNA LATER'
            if typeP == 'DNA':
                abbr = 'r'
                name = 'rna'
                long_name = 'DNA'
            if typeP == 'RNA':
                abbr = 'r'
                name = 'rna'
                long_name = 'RNA'
            if typeP == 'cDNA':
                abbr = 'r'
                name = 'rna'
                long_name = 'cDNA'
            if typeP == 'cRNA':
                abbr = 'r'
                name = 'rna'
                long_name = 'cRNA'
            if typeP == 'PL':
                abbr = 'l'
                name = 'plasma'
                long_name = 'PLASMA'
            if typeP == 'PX':
                abbr = 'x'
                name = 'paxtube'
                long_name = 'PAX TUBE'
            if typeP == 'FR':
                abbr = 'f'
                name = 'urine'
                long_name = 'URINE'
            if typeP == 'FS':
                abbr = 'e'
                name = 'urine'
                long_name = 'SEDIMENT'
            if typeP == 'PS':
                abbr = 'r'
                name = 'rna'
                long_name = 'PARAFFIN SECTION'
            if typeP == 'OS':
                abbr = 'r'
                name = 'rna'
                long_name = 'OCT SECTION'
            if typeP == 'P':
                abbr = 'r'
                name = 'rna'
                long_name = 'PROTEIN'
            if typeP == 'LS':
                abbr = 'r'
                name = 'rna'
                long_name = 'LABELED SECTION'
            string = ""
            print 'barcodeP',barcodeP
            address = Urls.objects.get(default = '1').url
            try:
                barc=barcodeP.replace('#','%23')
                #se tratto una piastra di tipo esterno, ho una certa url
                if ext:
                    req = urllib2.Request(address+"/api/plate/"+barc + '/' + typeP+'/extern', headers={"workingGroups" : get_WG_string()})
                    u = urllib2.urlopen(req)
                    #u=urllib2.urlopen(address+"/api/plate/"+barc + '/' + typeP+'/extern')
                else:
                    req = urllib2.Request(address+"/api/plate/"+barc + '/' + typeP+'/', headers={"workingGroups" : get_WG_string()})
                    u = urllib2.urlopen(req)
                    #u = urllib2.urlopen(address+"/api/plate/"+barc + '/' + typeP+'/')
                data = json.loads(u.read())
                #print 'data',data
            except Exception, e:
                print 'e',e
                return {'data':'errore_store','aliquote':lisaliquote}
            
            if data['data']=='errore_aliq':
                return {'data':'errore_aliq','aliquote':lisaliquote}
            if data['data']=='errore_piastra':
                return {'data':'errore_piastra','aliquote':lisaliquote}

            #response, dim = tableImpl(data,typeP)
            row_label = data['rules']['row_label']
            column_label = data['rules']['column_label']
            j = 0
            #creare una lista di barcode da inviare alla biobanca per poi analizzarne la risposta
            try:
                response, dim = CreaTabella(data,typeP)
                #dimensioni della piastra
                x = int(dim[0])
                y = int(dim[1])
                #inizializzo la tabella. Qui verra' scritto il codice HTML per creare le singole celle della tabella visualizzata dall'utente
                codeList = []
                i = 0
                j = 0
                while i < int(y):
                    codeList.append([])
                    j = 0
                    while j < int(x):
                        #calcolo l'id del tasto
                        id=abbr+'-'+chr(i+ord('A'))+str(j+1)
                        codeList[i].append('<td align="center"><button type="submit" align="center" disabled="disabled" id="'+id+'">X</button></td>')
                        j = j + 1
                    i = i + 1

                #recupero i dati relativi alle aliquote eventualmente contenute nelle varie provette
                #res = json.loads(response)
                for r in response:
                    if len(r.split(',')) > 3:
                        #se la provetta contiene un'aliquota
                        pieces = r.split(',')
                        barcode =  pieces[0]
                        id_position = pieces[1]
                        coordinates = pieces[2]
                        aliquot = pieces[3]                        
                        quantity = pieces[4]
                        c = coordinates.split('|')
                        x = c[0]
                        y = c[1]
                        codeList[int(y)-1][int(x)-1] = '<td> <button type="submit" align="center" id="'+ abbr + '-' + id_position + '" sel="s" pos="'+ id_position + '" gen="'+aliquot+'" title="'+aliquot+'" barcode="'+ barcode+'" disabled="disabled">'+ quantity +'</button></td>'
                        lisaliquote.append(aliquot)
                    else:
                        #se la provetta e' vuota
                        pieces = r.split(',')
                        barcode =  pieces[0]
                        id_position = pieces[1]
                        coordinates = pieces[2]
                        c = coordinates.split('|')
                        x = c[0]
                        y = c[1]
                        codeList[int(y)-1][int(x)-1] = '<td><button type="submit" align="center" pos="'+ id_position + '" id="'+ abbr + '-' + id_position + '"  barcode="'+ barcode+'">0</button></td>'
            except Exception, e:
                print 'error',e

            #creo il codice per la tabella HTML
            #lun e' il numero di colonne che l'intestazione della tabella deve coprire
            lun=int(dim[0])+1
            string += '<table align="center" id="' + str(name) + '" plate="' + str(barcodeP) + '"><tbody><tr><th colspan="' + str(lun) + '">' + str(long_name) + '</th></tr>'
            string += '<tr>'
            string += '<td></td>'
            for c in column_label:
                string += '<td align="center" class="intest"><strong>' + str(c) + '</strong></td>'
            string += '</tr>'
            i = 0
            for code in codeList:
                string += '<tr>'
                string += '<td align="center" class="intest"><strong><br>' + str(row_label[i]) + '</strong></td>'
                for c in code:
                    if c != "":
                        string += c
                string += '</tr>'
                i = i +1
            string += "</tbody></table></div></div>"
            return {'data':string,'aliquote':lisaliquote}
        except Exception, e:
            print 'err',e
            return {"data": 'errore','aliquote':lisaliquote}

#mi restituisce tutti gli strumenti presenti
class InstrumentHandler(BaseHandler):
    allowed_methods = ('GET')
    @method_decorator(get_functionality_decorator)
    def read(self, request):
        try:
            lista=[]
            listastrum=Instrument.objects.all()
            for strum in listastrum:
                s=strum.name+'&'+strum.code
                lista.append(s)
            return {'data':listastrum}
        except:
            return {"data":'errore'}

#Data una serie di genid mi restituisce i pezzi presenti
class LoadTubeHandler(BaseHandler):
    allowed_methods = ('GET')
    @method_decorator(get_functionality_decorator)
    def read(self, request,barcode,tipo):
        try:
            lista=[]
            print 'barcode',barcode
            #solo se la piastra ha delle provette dentro
            if barcode!='x':
                #tipo non viene piu' usato perche' e' l'aliq che da' il tipo
                #non c'e' piu' un tipo generico della piastra
                #aliqtip=AliquotType.objects.get(abbreviation=tipo)
                provette=barcode.split(',')
                print 'provette',provette
                for prov in provette:
                    dati=prov.split('&')
                    print 'dati',dati
                    genealogy=dati[3]
                    listagen=Aliquot.objects.filter(uniqueGenealogyID=genealogy,availability=1)
                    #se la provetta e' piena
                    print 'listagen',listagen
                    if settings.USE_GRAPH_DB==False or 'admin' in get_WG():
                        if listagen.count()!=0:
                            gen=listagen[0]
                            tipaliq=AliquotType.objects.get(abbreviation=gen.idAliquotType.abbreviation)
                            if tipaliq.type=='Original' or tipaliq.type=='Block':                             
                                #recupero l'oggetto feature relativo al numero di pezzi per le aliq
                                featu=Feature.objects.filter(name='NumberOfPieces',idAliquotType=tipaliq)
                                print 'fe',featu
                                if len(featu)!=0:
                                    pezzi=AliquotFeature.objects.filter(idAliquot=gen,idFeature=featu[0])
                                    if len(pezzi)!=0:
                                        pzz=str(int(pezzi[0].value))
                                    else:
                                        pzz='#'
                                else:
                                    pzz='#'
                                #print 'n pezzi',pezzi.value
                                prov=dati[0]+','+dati[1]+','+dati[2]+','+gen.uniqueGenealogyID+','+pzz+','+tipaliq.abbreviation
                            else:
                                #se l'aliq e' derivata metto a 0 il num di pezzi
                                prov=dati[0]+','+dati[1]+','+dati[2]+','+gen.uniqueGenealogyID+',#,'+tipaliq.abbreviation
                        #se la provetta e' vuota
                        else:
                            prov=dati[0]+','+dati[1]+','+dati[2]
                        lista.append(prov)
                    else:
                        disable_graph()
                        count_old=Aliquot.objects.filter(uniqueGenealogyID=genealogy,availability=1).count()
                        enable_graph()
                        if count_old!=0:
                            if listagen.count()==0:
                                prov=str(dati[0])+','+str(dati[1])+','+str(dati[2])+',NOT AVAILABLE,X,X'
                            else:
                                gen=listagen[0]
                                tipaliq=AliquotType.objects.get(abbreviation=gen.idAliquotType.abbreviation)
                                if tipaliq.type=='Original' or tipaliq.type=='Block':                                   
                                    #recupero l'oggetto feature relativo al numero di pezzi per le aliq
                                    featu=Feature.objects.filter(name='NumberOfPieces',idAliquotType=tipaliq)
                                    print 'fe',featu
                                    if len(featu)!=0:
                                        pezzi=AliquotFeature.objects.filter(idAliquot=gen,idFeature=featu[0])
                                        if len(pezzi)!=0:
                                            pzz=str(int(pezzi[0].value))
                                        else:
                                            pzz='#'
                                    else:
                                        pzz='#'
                                    #print 'n pezzi',pezzi.value
                                    prov=dati[0]+','+dati[1]+','+dati[2]+','+gen.uniqueGenealogyID+','+pzz+','+tipaliq.abbreviation
                                else:
                                    #se l'aliq e' derivata metto a 0 il num di pezzi
                                    prov=dati[0]+','+dati[1]+','+dati[2]+','+gen.uniqueGenealogyID+',#,'+tipaliq.abbreviation
                                    #se la provetta e' vuota
                        else:
                            prov=dati[0]+','+dati[1]+','+dati[2]
                        lista.append(prov)                    
            return {'data':lista}
        except Exception,e:
            print 'errr',e
            return {"data":'errore'}

#serve nella parte delle aliquote vitali da posizionare sulla piastra per vedere se il genealogy 
#id dell'aliquota da posizionare, introdotto dall'utente, esiste o meno nel DB e se
#l'aliquota non e' gia' stata programmata per il posizionamento
'''class PositionAliquotHandler(BaseHandler):
    allowed_methods = ('GET')
    @method_decorator(get_functionality_decorator)
    def read(self, request,gen):
        try:
            tipo=AliquotType.objects.get(abbreviation='VT')
            
            diz=AllAliquotsContainer(gen)
            lista=diz[gen]
            if len(lista)==0:
                return{'data':'inesistente'}
            
            #e' una lista in cui ogni valore e' una stringa formata da gen|barcode|posizione
            for val in lista:
                ch=val.split('|')
                
                #per controllare se l'aliquota e' di questo wg        
                lisal=Aliquot.objects.filter(uniqueGenealogyID=ch[0],availability=1)
                if len(lisal)==0:
                    return{'data':'inesistente'}
                else:                    
                    al=lisal[0]
                    
                #guardo se l'aliquota e' VT
                if al.idAliquotType!=tipo:
                    return {'data':'nonvitale'}
                
                #vedo se l'aliquota e' gia' stata programmata per il posizionamento
                alqualsched=AliquotPositionSchedule.objects.filter(idAliquot=al,positionExecuted=0,deleteTimestamp=None)
                print 'alqual',alqualsched
                if(alqualsched.count()!=0):
                    return {'data':'presente'}
                
                #devo verificare che il campione abbia una data di archiviazione per sapere se e'
                #possibile posizionarlo o meno
                #datainiz=datetime.date(2013,1,1)
                #dat=al.idSamplingEvent.samplingDate
                #print 'dat',dat
                #if al.archiveDate==None and dat>datainiz:
                #    return {'data':'nonstore'}

            return {'data':lista}            
        except Exception,e:
            print 'errore',e
            return {"data":'errore'}'''

#mi restituisce il nome dell'utente attualmente collegato
class UserHandler(BaseHandler):
    allowed_methods = ('GET')
    @method_decorator(get_functionality_decorator)
    def read(self, request):
        try:
            name=request.user.username
            return {'data':name}
        except:
            return {"data":'errore'}
        
#Per gli altri moduli. Data una lista di genid di cDNA o di cRNA viene restituito
#il volume, la concentrazione e la data di creazione dell'aliquota         
class DerivativeHandler(BaseHandler):
    allowed_methods = ('GET')
    @method_decorator(get_functionality_decorator)
    def read(self, request, genid, operator):
        lista=[]
        #i vari gen sono separati da &
        if genid:
            try:
                lista_gen=genid.split('&')
                #scandisco i gen
                tipo_dna=AliquotType.objects.get(abbreviation='DNA')
                tipo_rna=AliquotType.objects.get(abbreviation='RNA')
                tipo_cdna=AliquotType.objects.get(abbreviation='cDNA')
                tipo_crna=AliquotType.objects.get(abbreviation='cRNA')
                lgen=''
                #salvo prima di tutto l'indicazione della disponibilita' della provetta
                for g in lista_gen:
                    #vedo se le aliq sono di quel tipo o no
                    listagen=Aliquot.objects.filter(Q(uniqueGenealogyID=g)&Q(availability=1)&(Q(idAliquotType=tipo_dna)|Q(idAliquotType=tipo_rna)|Q(idAliquotType=tipo_cdna)|Q(idAliquotType=tipo_crna)))
                    print 'listagen',listagen
                    if listagen.count()!=0:
                        lgen+=listagen[0].uniqueGenealogyID+'&'
                if lgen=='':
                    lgen='No'
                lisgen=lgen.replace('#','%23')
                
                storbarc=StorageTubeHandler()
                data=storbarc.read(request, lisgen, operator)
                dizprov=json.loads(data['data'])
                print 'dizprov',dizprov
                diz={}
                for key,val in dizprov.items():
                    print 'd',key
                    v=val.split('|')
                    diz[key]=v
                print 'diz',diz
                for i in range (0,len(lista_gen)):    
                    listagen=Aliquot.objects.filter(Q(uniqueGenealogyID=lista_gen[i])&Q(availability=1)&(Q(idAliquotType=tipo_dna)|Q(idAliquotType=tipo_rna)|Q(idAliquotType=tipo_cdna)|Q(idAliquotType=tipo_crna)))
                    print 'aliq',listagen
                    if listagen.count()!=0:
                        #nella posizione 6 ho la disponibilita'
                        disponibil=diz[listagen[0].uniqueGenealogyID][6]
                        print 'disp',disponibil
                        if disponibil=='Yes':
                            #recupero l'oggetto feature relativo al volume
                            featuvol=Feature.objects.get(Q(name='Volume')&Q(idAliquotType=listagen[0].idAliquotType.id))
                            #recupero l'oggetto feature relativo alla concentrazione
                            featuconc=Feature.objects.get(Q(name='Concentration')&Q(idAliquotType=listagen[0].idAliquotType.id))
                            #print 'feat',featu
                            vol=AliquotFeature.objects.get(Q(idAliquot=listagen[0])&Q(idFeature=featuvol))
                            print 'vol',vol.value
                            conc=AliquotFeature.objects.get(Q(idAliquot=listagen[0])&Q(idFeature=featuconc))
                            print 'conc',conc.value
                            data_creaz=str(listagen[0].idSamplingEvent.samplingDate)
                            #dat=data_creaz.split('-')
                            #d=dat[2]+'-'+dat[1]+'-'+dat[0]
                            barc=diz[listagen[0].uniqueGenealogyID][0]
                            posiz=diz[listagen[0].uniqueGenealogyID][1]
                            cont_padre=diz[listagen[0].uniqueGenealogyID][2]
                            pospiastranelrack=diz[listagen[0].uniqueGenealogyID][3]
                            rack=diz[listagen[0].uniqueGenealogyID][4]
                            freezer=diz[listagen[0].uniqueGenealogyID][5]
                            prov=lista_gen[i]+'&'+str(vol.value)+'&'+str(conc.value)+'&'+data_creaz+'&'+barc+'&'+cont_padre+'&'+posiz+'&'+pospiastranelrack+'&'+rack+'&'+freezer
                        else:
                            prov=lista_gen[i]+'&notavailable'
                    #se il genid non esiste
                    else:
                        prov=lista_gen[i]+'&notexist'
                    lista.append(prov)
                return{'data':lista}
            except Exception,e:
                print 'err',e
                return {'data':'errore'}
        else:
            return  {'data':'inserire genid'} 

#per gli altri moduli. Data una lista di genid vengono restituite tutte le feature
#di ogni campione con il relativo valore.
class FeatureHandler(BaseHandler):
    allowed_methods = ('GET')
    @method_decorator(get_functionality_decorator)
    def read(self, request, genid):
        #i vari gen sono separati da &
        if genid:
            lista=[]
            try:
                lista_gen=genid.split('&')
                for g in lista_gen:
                    aliq=Aliquot.objects.get(uniqueGenealogyID=g)
                    listafeat=AliquotFeature.objects.filter(idAliquot=aliq)
                    diz2={}
                    for feat in listafeat:
                        diz2[feat.idFeature.name]=feat.value
                    diz={'aliquot':g,'feature':diz2,'type':aliq.idAliquotType.abbreviation}
                    lista.append(diz)
                return{'data':lista}
            except Exception,e:
                print 'err',e
                return {"data":'errore'}
        else:
            return  {'data':'inserire genid'} 

#per la schermata che permette di diminuire il volume. Data una stringa, verifica che 
#sia un genid o un barcode validi, altrimenti restituisce errore
class GenIdBarcHandler(BaseHandler):
    allowed_methods = ('GET')
    @method_decorator(get_functionality_decorator)
    def read(self, request, val,exp):
            try:
                esperim=Experiment.objects.get(id=exp)
                diz=AllAliquotsContainer(val)
                lista=diz[val]
                if len(lista)==0:
                    return{'data':'inesistente'}
                
                lisgen=[]
                #e' una lista in cui ogni valore e' una stringa formata da gen|barcode|posizione
                for val in lista:
                    diz={}
                    ch=val.split('|')
                    gen=ch[0]
                    barc=ch[1]
                    pos=ch[2]
                    laliq=Aliquot.objects.filter(uniqueGenealogyID=gen,availability=1)
                    if len(laliq)==0:
                        return{'data':'inesistente'}
                    else:
                        aliq=laliq[0]
                        aliqexp=AliquotTypeExperiment.objects.filter(idExperiment=esperim,idAliquotType=aliq.idAliquotType)
    
                        if aliqexp.count()==0:
                            return {'data':'esperimento'}
                        
                        #controllo se e' un esperimento di generazione o scongelamento linee e se si' devo controllare che
                        #il tipo di aliq sia coerente
                        gg=GenealogyID(gen)
                        vettore=gg.getSampleVector()
                        print 'vettore',vettore
                        if esperim.name=='CellLineGeneration' and (vettore=='S' or vettore=='A' or vettore=='O'):
                            return {'data':'esperimento'}
                        if esperim.name=='CellLineThawing' and (vettore!='S' and vettore!='A' and vettore!='O'):
                            return {'data':'esperimento'}
                        
                        #vedo se l'aliquota e' gia' collegata ad una riduzione di volume ancora
                        #da confermare
                        alexpsched=AliquotExperiment.objects.filter(idAliquot=aliq,confirmed=0,deleteTimestamp=None)
                        if(alexpsched.count()!=0):
                            return {'data':'presente'}
                        #prendo le feature dell'aliquota
                        concval=''
                        volval=''
                        #booleano per capire se il campione puo' avere un volume o meno
                        volume=False
                        lconc=Feature.objects.filter(Q(name='Concentration')&Q(idAliquotType=aliq.idAliquotType))
                        lvol=Feature.objects.filter(Q(name='Volume')&Q(idAliquotType=aliq.idAliquotType))
                        if len(lconc)!=0:
                            lisconc=AliquotFeature.objects.filter(Q(idAliquot=aliq)&Q(idFeature=lconc[0]))
                            #se il derivato non ha conc e vol viene salvato nel DB -1. Quindi cambio -1
                            #con None
                            if len(lisconc)!=0:
                                if lisconc[0].value==-1:
                                    concval='None'
                                else:
                                    concval=str(lisconc[0].value)
                        if len(lvol)!=0:
                            lisvol=AliquotFeature.objects.filter(Q(idAliquot=aliq)&Q(idFeature=lvol[0]))
                            if len(lisvol)!=0:
                                if lisvol[0].value==-1:
                                    volval='None'
                                else:
                                    volval=str(lisvol[0].value)
                                    volume=True
                        valfinale=gen+'|'+barc+'|'+pos+'|'+concval+'|'+volval
                        diz['val']=valfinale
                        diz['derivato']=volume
                        lisgen.append(diz)
                return{'data':json.dumps(lisgen)}
            except Exception,e:
                print 'err',e
                return {"data":'errore'}
            
#Serve per discriminare tra caricamento di piastre e caricamento di provette
class GenericLoadHandler(BaseHandler):
    allowed_methods = ('GET')
    @method_decorator(get_functionality_decorator)
    def read(self, request, barcode,aliquot,typeP):
        try:
            print 'barcode',barcode
            #se carico una piastra, chiamo la solita API per le piastre
            if typeP=='plate':
                tab=TableHandler()
                return tab.read(request, barcode, aliquot,None)
            #se carico una provetta singola
            elif typeP=='tube':
                #vedo se il container esiste e se si' che sia vuoto, altrimenti errore
                try:
                    address = Urls.objects.get(default = '1').url
                    barc=barcode.replace('#','%23')
                    req = urllib2.Request(address+"/api/biocassette/"+barc+"/"+aliquot, headers={"workingGroups" : get_WG_string()})
                    u = urllib2.urlopen(req)
                    data = json.loads(u.read())
                    print 'data2',data
                    if data['data']!='ok':
                        return data
                except Exception, e:
                    print 'e',e
                    return {'data':'errore_store'}
                print 'aliquot',aliquot
                if aliquot=='VT':
                    abbr = 'v'
                    name = 'vital'
                    long_name = 'VIABLE'
                elif aliquot=='SF':
                    abbr = 's'
                    name = 'sf'
                    long_name = 'SNAP FROZEN'
                elif aliquot=='RL':
                    abbr = 'r'
                    name = 'rna'
                    long_name = 'RNA LATER'
                elif aliquot=='P':
                    abbr = 'r'
                    name = 'rna'
                    long_name = 'PROTEIN'
                else:
                    abbr = 'r'
                    name = 'rna'
                    long_name = aliquot
                print 'long_name',long_name 
                #devo creare l'html da visualizzare
                html=''
                html += '<table align="center" id="'+name+'"><tbody><tr><th>'+long_name+'</th></tr>'
                html += '<tr>'
                html += '<td align="center"><button type="submit" align="center" id="'+abbr+'-A1" pos="A1" >0</button></td></tr>'
                html += "</tbody></table>"
                return {'data':html}
        except Exception,e:
            print 'err',e
            return {"data":'errore'}

#restituisce la lista degli esperimenti presenti con nome e cartella relativa. Serve per il modulo che trasferisce i file che ha bisogno di presentare
#all'utente la lista degli esperimenti. In piu' aggiungo a mano l'esperimento "hamilton robot"
class ExpListHandler(BaseHandler):
    allowed_methods = ('GET')
    @method_decorator(get_functionality_decorator)
    def read(self, request):
        try:
            lisexp=Experiment.objects.filter(folder__isnull=False).order_by('name')
            print 'lisexp',lisexp
            lisfin=[]
            for exp in lisexp:
                diztemp={'name':exp.name,'folder':exp.folder}
                lisfin.append(diztemp)
                #metto hamilton dopo l'esperimento histology
                if exp.name.lower().startswith('hist'):                    
                    #aggiungo hamilton
                    lisfin.append({'name':'Hamilton Robot','folder':'Hamilton'})
                    print 'lisfin',lisfin
            return {'experiments':lisfin}
        except:
            return {'experiments':'error'}

#Serve per confermare l'esecuzione dell'esperimento quando viene fatto da un altro modulo
#Es: beaming, uarray 
class ExpConfirmHandler(BaseHandler):
    allowed_methods = ('GET','POST')
    @method_decorator(get_functionality_decorator)
    def read(self, request):
        return {'data':'ok'}
    @method_decorator(get_functionality_decorator)
    def create(self, request):
        try:
            print request.POST
            lista=request.POST.get('aliquots')
            esp=request.POST.get('experiment')
            lis=json.loads(lista)
            print 'lis',lis
            esp=Experiment.objects.get(name=esp)
            print 'esp',esp
            lgen=[]
            for elem in lis:
                aliq=Aliquot.objects.get(uniqueGenealogyID=elem)
                print 'aliq',aliq
                aliqesp=AliquotExperiment.objects.filter(idAliquot=aliq,idExperiment=esp,confirmed=0)
                print 'aliqesp',aliqesp
                if len(aliqesp)!=0:
                    aliqesp[0].confirmed=1
                    aliqesp[0].save()
                    lgen.append(elem)
            
            if 'operator' in request.POST:
                operator=request.POST['operator']
                address=Urls.objects.get(default=1).url
                #devo comunicare allo storage che il container non e' piu' disponibile
                print 'lgen',lgen
                if len(lgen)!=0:
                    url1 = address + "/container/availability/"
                    val1={'lista':json.dumps(lgen),'tube':'0','nome':operator}
                    print 'url1',url1
                    data = urllib.urlencode(val1)
                    req = urllib2.Request(url1,data=data, headers={"workingGroups" : get_WG_string()})
                    u = urllib2.urlopen(req)
                    res1 =  u.read()
                    if res1=='err':
                        raise Exception
            
            return {'data':'OK'}
        
        except Exception, e:
            print 'ecc',e
            return {'data':'errore'}
       
'''#Serve per confermare l'esecuzione dell'esperimento quando viene fatto da un altro modulo
#poi aggiorna anche il volume
#Es: beaming, uarray 
class ExpConfirmHandler(BaseHandler):
    allowed_methods = ('POST')
    @method_decorator(get_functionality_decorator)
    def create(self, request):
        try:
            print request.POST
            dizio=request.POST.get('aliquots')
            print 'dizio',dizio
            esp=request.POST.get('experiment')
            operator=request.POST.get('operator')
            oper=User.objects.get(username=operator)
            #parametro per dire se devo cancellare o salvare le informazioni
            canc=request.POST.get('undo')
            diz=json.loads(dizio)
            print 'diz',diz
            esp=Experiment.objects.get(name=esp)
            print 'esp',esp
            if canc=='False':
                crea=False
                lgen=[]
                lesauriti=[]
                dizsupervisori={}
                aliqesp=[]
                lisgenconfermati=[]
                lisexp=[]
                laliq=Aliquot.objects.filter(uniqueGenealogyID__in=diz)
                print 'laliq',laliq
                
                strgen=''
                for g in laliq:
                    strgen+=g.uniqueGenealogyID+'&'
                lgenfin=strgen[:-1]
                diction=AllAliquotsContainer(lgenfin)
                
                for aliq in laliq:
                    print 'aliq',aliq
                    dapianific=diz[aliq.uniqueGenealogyID]['plan']
                    esausto=diz[aliq.uniqueGenealogyID]['exhausted']
                    volume=diz[aliq.uniqueGenealogyID]['volume']
                    volpreso=-1
                    #recupero l'oggetto feature relativo al volume e aggiorno con quello attuale
                    featuvol=Feature.objects.filter(name='Volume',idAliquotType=aliq.idAliquotType)
                    if len(featuvol)!=0:
                        vo=AliquotFeature.objects.filter(idAliquot=aliq,idFeature=featuvol[0])
                        if len(vo)!=0:
                            vol=vo[0]
                            print 'vol',vol.value
                            volvecchio=vol.value
                            print 'volume',volume
                            volpreso=float(volvecchio)-float(volume)
                            if not esausto:
                                vol.value=float(volume)
                            else:
                                #se il campione e' esaurito metto a zero il volume
                                vol.value=0.0
                            vol.save()
                    
                    print 'plan',dapianific
                    if not dapianific:
                        aliqesp=AliquotExperiment.objects.filter(idAliquot=aliq,idExperiment=esp,confirmed=0)
                        print 'aliqesp',aliqesp
                        if len(aliqesp)!=0:
                            exp=aliqesp[0]
                            exp.confirmed=1
                            exp.aliquotExhausted=esausto
                            exp.remainingValue=volume
                            exp.takenValue=volpreso
                            exp.save()
                            lisexp.append(exp)
                            valori=diction[aliq.uniqueGenealogyID]
                            val=valori[0].split('|')
                            barc=val[1]
                            pos=val[2]
                            print 'valori',valori
                            
                            assegnatario=exp.idExperimentSchedule.operator
                            print 'assegn',assegnatario.email
                            print 'name',operator
                            print 'assegna username',assegnatario.username
                            lisgenconfermati.append(aliq.uniqueGenealogyID)
                            diztemp={}
                            diztemp['gen']=aliq.uniqueGenealogyID
                            diztemp['barc']=barc
                            diztemp['pos']=pos
                            if volpreso==-1:
                                diztemp['takenvol']=''
                            else:
                                diztemp['takenvol']=volpreso
                            diztemp['leftvol']=volume
                            diztemp['exhaus']=esausto
                            diztemp['exp']=exp.idExperiment.name
                            diztemp['note']=exp.notes
                            diztemp['pianif']=exp.idExperimentSchedule.operator.username
                            dizsupervisori[aliq.uniqueGenealogyID]=diztemp
                        
                    else:
                        #devo creare la pianificazione e salvarla come eseguita
                        if not crea:
                            #creo l'exp schedule, ma lo salvo solo una volta all'inizio
                            expsched=ExperimentSchedule(scheduleDate=datetime.date.today(),
                                                        operator=oper)
                            expsched.save()
                            print 'expsched',expsched
                            crea=True
                        aliqespe=AliquotExperiment(idAliquot=aliq,
                                                 idExperiment=esp,
                                                 idExperimentSchedule=expsched,
                                                 takenValue=volpreso,
                                                 remainingValue=volume,
                                                 operator=operator,
                                                 experimentDate=datetime.date.today(),
                                                 aliquotExhausted=esausto,
                                                 confirmed=True)
                        print 'aliqespe',aliqespe
                        aliqespe.save()
                        
                    if not esausto:
                        lgen.append(aliq.uniqueGenealogyID)
                    
                    #se e' esaurita l'aliquota
                    if esausto:
                        aliq.availability=0
                        aliq.save()
                        lesauriti.append(aliq.uniqueGenealogyID)
                        
                address=Urls.objects.get(default=1).url
                #devo comunicare allo storage che il container non e' piu' disponibile
                if len(lgen)!=0:
                    url1 = address + "/container/availability/"
                    val1={'lista':json.dumps(lgen),'tube':'0','nome':operator}
                    print 'url1',url1
                    data = urllib.urlencode(val1)
                    req = urllib2.Request(url1,data=data, headers={"workingGroups" : get_WG_string()})
                    u = urllib2.urlopen(req)
                    #u = urllib2.urlopen(url1, data)
                    res1 =  u.read()
                    if res1=='err':
                        raise Exception
                
                if len(lesauriti)!=0:
                    #mi collego allo storage per svuotare le provette contenenti le aliq
                    #esaurite
                    url = address+"/full/"
                    print url
                    values = {'lista' : json.dumps(lesauriti), 'tube': 'empty','canc':True}
                    data = urllib.urlencode(values)
                    req = urllib2.Request(url,data=data, headers={"workingGroups" : get_WG_string()})
                    u = urllib2.urlopen(req)
                    #u=urllib2.urlopen(url, data)
                    res1 =  u.read()
                    if res1=='err':
                        raise Exception
                
                #solo se ho confermato qualche esperimento mando l'e-mail
                if len(aliqesp)!=0:
                    email = LASEmail (functionality='can_view_BBM_execute_experiments', wgString=get_WG_string())
                    msg=['Experiment executed','','Assigned to:\t'+operator,'','Aliquots:','N\tGenealogy ID\tBarcode\tPosition\tTaken volume(uL)\tFinal volume(uL)\tExhausted\tExperiment\tDescription']                    
                    #non metto availability=1 perche' se l'aliquota e' esaurita non me la prende e non va bene
                    lisdafiltrare=Aliquot.objects.filter(uniqueGenealogyID__in=lisgenconfermati)
                    wgList=WG.objects.filter(id__in=Aliquot_WG.objects.filter(aliquot__in=lisdafiltrare).values_list('WG',flat=True).distinct())
                    print 'wglist',wgList
                    for wg in wgList:
                        print 'wg',wg
                        email.addMsg([wg.name], msg)
                        aliq=lisdafiltrare.filter(id__in=Aliquot_WG.objects.filter(WG=wg).values_list('aliquot',flat=True).distinct())
                        print 'aliq',aliq
                        i=1
                        lisplanner=[]
                        #per mantenere l'ordine dei campioni anche nell'e-mail
                        for exp in lisexp:
                            for al in aliq:
                                if exp.idAliquot.uniqueGenealogyID==al.uniqueGenealogyID:
                                    dizvalori=dizsupervisori[al.uniqueGenealogyID]
                                    print 'dizvalori',dizvalori
                                    barc=dizvalori['barc']
                                    pos=dizvalori['pos']
                                    volpres=dizvalori['takenvol']
                                    if volpres==-1:
                                        volpres=''
                                    volrim=dizvalori['leftvol']
                                    if volrim==-1:
                                        volrim=''
                                    esausta='False'
                                    if dizvalori['exhaus']==1:
                                        esausta='True'
                                    email.addMsg([wg.name],[str(i)+'\t'+al.uniqueGenealogyID+'\t'+barc+'\t'+pos+'\t'+str(volpres)+'\t'+str(volrim)+'\t'+esausta+'\t'+dizvalori['exp']+'\t'+dizvalori['note']])
                                    i=i+1
                                    if dizvalori['pianif'] not in lisplanner:
                                        lisplanner.append(dizvalori['pianif'])
                        print 'lisplanner',lisplanner
                        #mando l'e-mail al pianificatore
                        email.addRoleEmail([wg.name], 'Planner', lisplanner)
                        email.addRoleEmail([wg.name], 'Executor', [operator])
                    try:
                        email.send()
                    except Exception, e:
                        print 'err experiment:',e
                        pass
                   
                return {'data':'OK'}
        except Exception, e:
            print 'ecc',e
            return {'data':'errore'}'''
        
#Per gli altri moduli. Serve per cancellare gli esperimenti che l'utente ha deciso di togliere 
class ExpCancHandler(BaseHandler):
    allowed_methods = ('GET','POST')
    @method_decorator(get_functionality_decorator)
    def read(self, request):
        return {'data':'ok'}
    @method_decorator(get_functionality_decorator)
    def create(self, request):
        try:
            print request.POST
            lista=request.POST.get('aliquots')
            esp=request.POST.get('experiment')
            laliq=[]
            if 'operator' in request.POST:
                oper=request.POST.get('operator')
            else:
                oper='emanuele.geda'
            operatore=User.objects.get(username=oper)
            notes=request.POST.get('notes')
            lis=json.loads(lista)
            print 'lis',lis
            esp=Experiment.objects.get(name=esp)
            print 'esp',esp
            i=1
            
            lgen=''
            for val in lis:
                lgen+=val+'&'
                laliq.append(val)
            lgenfin=lgen[:-1]
            diz=AllAliquotsContainer(lgenfin)
            print 'func',get_functionality()
            email = LASEmail (functionality='can_view_BBM_execute_experiments', wgString=get_WG_string())
            msg=['Experiment aborted','','Assigned to:\t'+oper,'Notes:\t'+notes,'','Aliquots:','N\tGenealogy ID\tBarcode\tPosition\tAssignment date\tExperiment\tDescription']
            aliquots=Aliquot.objects.filter(uniqueGenealogyID__in=laliq,availability=1)
            wgList=WG.objects.filter(id__in=Aliquot_WG.objects.filter(aliquot__in=aliquots).values_list('WG',flat=True).distinct())
            print 'wglist',wgList
            for wg in wgList:
                print 'wg',wg
                email.addMsg([wg.name], msg)
                aliq=aliquots.filter(id__in=Aliquot_WG.objects.filter(WG=wg).values_list('aliquot',flat=True).distinct())
                print 'aliq',aliq
                i=1
                lisplanner=[]
                #per mantenere l'ordine dei campioni anche nell'e-mail
                for elem in lis:
                    print 'elem',elem
                    aliquota=Aliquot.objects.get(uniqueGenealogyID=elem)
                    lisaliqesp=AliquotExperiment.objects.filter(idAliquot=aliquota,idExperiment=esp,confirmed=0,deleteTimestamp=None)
                    print 'aliqesp',lisaliqesp
                    if len(lisaliqesp)!=0:
                        aliqesp=lisaliqesp[0]

                        valori=diz[elem]
                        val=valori[0].split('|')
                        barc=val[1]
                        pos=val[2]
                        assegnatario=aliqesp.idExperimentSchedule.operator.username
                        for al in aliq:   
                            if elem==al.uniqueGenealogyID:
                                email.addMsg([wg.name],[str(i)+'\t'+al.uniqueGenealogyID+'\t'+barc+'\t'+pos+'\t'+str(aliqesp.idExperimentSchedule.scheduleDate)+'\t'+aliqesp.idExperiment.name+'\t'+aliqesp.notes])
                                i=i+1                                
                                if assegnatario not in lisplanner:
                                    lisplanner.append(assegnatario)
                        #aliqesp.deleteTimestamp= datetime.datetime.now()
                        aliqesp.deleteTimestamp=timezone.localtime(timezone.now())
                        aliqesp.deleteOperator=operatore
                        aliqesp.save()
                print 'lisplanner',lisplanner
                #devo mandare l'e-mail al pianificatore della procedura
                email.addRoleEmail([wg.name], 'Planner', lisplanner)
                email.addRoleEmail([wg.name], 'Executor', [oper])
            try:
                if len(lisplanner)!=0:
                    email.send()
            except Exception, e:
                print 'errore',e
                pass
            '''for elem in lis:
                print 'elem',elem
                aliq=Aliquot.objects.get(uniqueGenealogyID=elem)
                lisaliqesp=AliquotExperiment.objects.filter(idAliquot=aliq,idExperiment=esp,confirmed=0,deleteTimestamp=None)
                print 'aliqesp',lisaliqesp
                if len(lisaliqesp)!=0:
                    aliqesp=lisaliqesp[0]
            
                    dat=aliqesp.idExperimentSchedule.scheduleDate
                    print 'dat',dat
                    data2=str(dat).split('-')
                    d=data2[2]+'-'+data2[1]+'-'+data2[0]
                    print 'd',d
                    
                    valori=diz[elem]
                    val=valori[0].split('|')
                    barc=val[1]
                    pos=val[2]
                    
                    assegnatario=aliqesp.idExperimentSchedule.operator
                    #creo un dizionario con dentro come chiave il nome del supervisore e come valore una lista con le procedure che lo
                    #riguardano
                    if assegnatario.email !='' and assegnatario.username!=oper:
                        diztemp={}
                        diztemp['gen']=aliqesp.idAliquot.uniqueGenealogyID
                        diztemp['barc']=barc
                        diztemp['pos']=pos
                        diztemp['dat']=dat
                        diztemp['exp']=aliqesp.idExperiment
                        diztemp['note']=aliqesp.notes
                        if dizsupervisori.has_key(assegnatario.email):
                            listatemp=dizsupervisori[assegnatario.email]
                            listatemp.append(diztemp)
                        else:
                            listatemp=[]
                            listatemp.append(diztemp)
                        dizsupervisori[assegnatario.email]=listatemp

                    #aliqesp.deleteTimestamp= datetime.datetime.now()
                    aliqesp.deleteTimestamp=timezone.localtime(timezone.now())
                    aliqesp.deleteOperator=operatore
                    aliqesp.save()
                    
                    i=i+1
                
            print 'dizfin',dizsupervisori
            if len(dizsupervisori)!=0:
                for key,value in dizsupervisori.items():
                    file_data = render_to_string('tissue2/update/report_experiment_canc.html', {'listafin':value,'esec':oper,'notes':notes}, RequestContext(request))
                    
                    subject, from_email = 'Cancel experiment', settings.EMAIL_HOST_USER
                    text_content = 'This is an important message.'
                    html_content = file_data
                    msg = EmailMultiAlternatives(subject, text_content, from_email, [key])
                    msg.attach_alternative(html_content, "text/html")
                    msg.send()'''
            
            return {'data':'OK'}
        
        except Exception, e:
            print 'ecc',e
            return {'data':'errore'}

#Per i moduli esterni, nel caso si vogliano trattare campioni senza pianificazione nella biobanca
#E' previsto avere piu' barcode insieme, ma di solito ne verra' passato solo uno
class ExpLoadHandler(BaseHandler):
    allowed_methods = ('GET')
    @method_decorator(get_functionality_decorator)
    def read(self, request):
        try:
            #print request
            #lista di barc separati da |
            lisbarcode = request.GET['barcode']
            print 'barcode',lisbarcode
            esperimento = request.GET['experiment']
            esp=Experiment.objects.get(name=esperimento)
            print 'exp',esperimento
            operatore = request.GET['operator']
            print 'oper',operatore
            #barc=lisbarcode.replace('|','&')
            genbarc=GenIdBarcHandler()
            lbarc=lisbarcode.split('|')
            diz={}
            lisgen=''
            for barc in lbarc:
                data=genbarc.read(request, barc, esp.id)
                lis=data['data']
                print 'lis',lis
                #e' gia' programmata per l'esperimento
                if lis=='presente':
                    diz[barc]={'err':'present'}
                #non puo' essere programmata per quell'esperimento
                elif lis=='esperimento':
                    diz[barc]={'err':'experiment'}
                elif lis=='inesistente':
                    diz[barc]={'err':'notexist'}
                else:
                    dizionario=json.loads(data['data'])[0]
                    print 'data',dizionario
                    val=dizionario['val']
                    print 'val',val
                    lval=val.split('|')
                    diztemp={'gen':lval[0],'conc':lval[3],'vol':lval[4]}
                    print 'diztemp',diztemp
                    diz[barc]=diztemp
                    lisgen+=lval[0]+'&'
            
            if lisgen!='':
                storbarc=StorageTubeHandler()
                data=storbarc.read(request, lisgen, operatore)
                dizprov=json.loads(data['data'])
                print 'dizprov',dizprov
                #la chiave e' il gen e il val contiene i dati sulla posizione del campione
                for key,val in dizprov.items():
                    v=val.split('|')
                    disp=v[6]
                    if disp=='No':
                        #in v[0] c'e' il barc della provetta
                        if diz.has_key(v[0]):
                            diz[v[0]]={'err':'notavailable'}
                        elif diz.has_key(key):
                            diz[key]={'err':'notavailable'}
            
            print 'diz',diz
            return{'data':json.dumps(diz)}
        except Exception, e:
            print 'ecc',e
            return {'data':'errore'}

#serve nella schermata di recupero delle informazioni sugli esperimenti eseguiti
class ExpViewDataHandler(BaseHandler):
    allowed_methods = ('POST')
    @method_decorator(get_functionality_decorator)
    def create(self, request, filetype):
        try:
            print request.POST
            lisexptot=AliquotExperiment.objects.filter(confirmed=1,deleteTimestamp__isnull=True)
            raw_data = json.loads(request.raw_post_data)
            lisexp=raw_data['experiment']
            print 'lisexp',lisexp
            filtro=False
            #tutti i campi dei filtri sono in AND
            if len(lisexp)!=0:
                lexp=Experiment.objects.filter(name__in=lisexp)
                lisexptot=lisexptot.filter(idExperiment__in=lexp)
                filtro=True
            
            lisoper=raw_data['operator']
            if len(lisoper)!=0:
                lisexptot=lisexptot.filter(operator__in=lisoper)
                filtro=True
                
            datadal=raw_data['datatot']
            dataal=raw_data['dataal']
            if datadal!='':
                attr=datadal.split('_')
                attr2=attr[1].split('-')
                print 'attr2',attr2
                datarif=datetime.date(int(attr2[0]),int(attr2[1]),int(attr2[2]))                                
                if attr[0]=='<':
                    lisexptot=lisexptot.filter(experimentDate__lte=datarif)
                elif attr[0]=='eq':
                    lisexptot=lisexptot.filter(experimentDate=datarif)
                elif attr[0]=='>':
                    lisexptot=lisexptot.filter(experimentDate__gte=datarif)
                    if dataal!='':
                        att2=dataal.split('-')
                        datarif2=datetime.date(int(att2[0]),int(att2[1]),int(att2[2]))
                        lisexptot=lisexptot.filter(experimentDate__lte=datarif2)                                        
                filtro=True
                
            print 'lisexptot',lisexptot
            #se non ho impostato dei filtri, il MDAM mi restituisce l'insieme vuoto, quindi non mi rallenta il recupero dati
            resSet=getMDAMData(request,False)
            print 'reseset',resSet
            #resSet={'LNF0003NCH0000000000RL0100':'NUEN643924'}
            #devo prendere gli esperimenti collegati a quei campioni            
            if resSet!=None:
                print 'len',len(resSet.keys())
                lisaliq=Aliquot.objects.filter(uniqueGenealogyID__in=resSet.keys())
                lisexptot=lisexptot.filter(idAliquot__in=lisaliq)
                filtro=True
            print 'lisexptot dopo mdam',lisexptot
            #se non ho filtrato niente restituisco subito una lista vuota. Altrimenti avrei come risultato tutti gli esperimenti
            #e non riesco a gestirli nella schermata che diventa lenta
            if filtro==False:
                return []
            #prendo i file collegati agli esperimenti che ho selezionato
            #se filetype e' None allora non aggiungo filtri e faccio vedere tutti i file
            if filetype=='None':
                lisfile=ExperimentFile.objects.filter(idAliquotExperiment__in=lisexptot)
            else:
                tipofile=FileType.objects.get(abbreviation=filetype)
                lisfile=ExperimentFile.objects.filter(idAliquotExperiment__in=lisexptot,idFileType=tipofile)
                #voglio vedere solo i dati degli esperimenti che hanno file di quel tipo, quindi prendo gli id degli aliquotexperiment
                lisid=[]
                for ff in lisfile:
                    lisid.append(ff.idAliquotExperiment.id)
                lisexptot=lisexptot.filter(id__in=lisid)
            print 'lisfile',lisfile
            dizfile={}
            for exp in lisfile:
                idaliqexp=exp.idAliquotExperiment.id
                if idaliqexp in dizfile:
                    listemp=dizfile[idaliqexp]
                else:
                    listemp=[]
                diztemp={'nome':exp.fileName,'id':str(exp.id),'link':exp.linkId}
                listemp.append(diztemp)
                dizfile[idaliqexp]=listemp                
            print 'dizfile',dizfile
            #uso questo metodo per prendere il barcode perche' ho bisogno di sapere il codice anche delle provette esaurite,
            #cosa che non avrei con la funzione AllAliquotsContainer
            strgen=''
            lis_pezzi_url=[]
            dizgen={}
            for exp in lisexptot:
                strgen+=exp.idAliquot.uniqueGenealogyID+'&'
                if len(strgen)>2000:
                #cancello la & alla fine della stringa
                    lis_pezzi_url.append(strgen[:-1])
                    strgen=''
            #cancello la & alla fine della stringa
            lgen=strgen[:-1]
            print 'lgen',lgen
            if lgen!='':
                lis_pezzi_url.append(lgen)
            
            if len(lis_pezzi_url)!=0:
                for elementi in lis_pezzi_url:
                    storbarc=StorageTubeHandler()
                    data=storbarc.read(request, elementi, request.user.username)
                    dizprov=json.loads(data['data'])
                    dizgen = dict(dizgen.items() + dizprov.items())                  
            print 'dizgen',dizgen
                                               
            lisfin=[]            
            for exp in lisexptot:
                coll=exp.idAliquot.idSamplingEvent.idCollection
                gen=exp.idAliquot.uniqueGenealogyID
                diztemp={}
                
                barc=''
                #pos=''
                if dizgen.has_key(exp.idAliquot.uniqueGenealogyID):
                    lval=dizgen[exp.idAliquot.uniqueGenealogyID]
                    val=lval.split('|')
                    barc=val[0]
                    #pos=val[1]
                                
                diztemp['gen']=gen
                diztemp['idaliq']=str(exp.idAliquot.id)
                diztemp['barcode']=barc
                diztemp['availability']=str(exp.idAliquot.availability)
                diztemp['patient']=coll.patientCode
                diztemp['informed']=coll.collectionEvent
                #diztemp['protocol']=''
                #if coll.idCollectionProtocol!=None:
                    #diztemp['protocol']=coll.idCollectionProtocol.name
                diztemp['experiment']=exp.idExperiment.name
                diztemp['volume']=str(exp.takenValue)      
                diztemp['operator']=exp.operator
                diztemp['date']=str(exp.experimentDate)
                diztemp['notes']=str(exp.notes)
                #mi occupo di eventuali file
                if exp.id in dizfile:
                    diztemp['file']=dizfile[exp.id]
                lisfin.append(diztemp)
            print 'lisfin',lisfin
            return lisfin
        except Exception, e:
            print 'err',e
            return []

#per i moduli molecolari (ad es. NGS). Data una lista di gen o barcode, restituisce i dati 
#delle misure di quei campioni
class FacilityLoadAliquotHandler(BaseHandler):
    allowed_methods = ('GET')
    @method_decorator(get_functionality_decorator)
    def read(self, request,codice,operator):
        try:
            print 'codice',codice
            print 'operatore',operator
            dizfin={}
            #chiave il gen e valore il codice che ho inviato tramite API
            dizconversione={}
            #codice e' formato da gen o barcode separati da & e lo spezzettamento lo fa gia' allaliquotscontainer 
            diz=AllAliquotsContainer(codice)
            lgen=''
            lisgenfiltrati=[]
            mispur230=Measure.objects.get(name='purity',measureUnit='260/230')
            mispur280=Measure.objects.get(name='purity',measureUnit='260/280')
            #diz ha chiave gen o barc e valore una stringa formata da gen|barcode|posizione
            for k,val in diz.items():
                if len(val)==0:
                    dizfin[k]={'exists':'no'}
                    dizconversione[k]=k
                else:
                    ch=val[0].split('|')
                    #per controllare se l'aliquota e' di questo wg        
                    lisal=Aliquot.objects.filter(uniqueGenealogyID=ch[0],availability=1)
                    print 'lisal',lisal
                    if len(lisal)==0:
                        dizfin[k]={'exists':'no'}
                        dizconversione[k]=k
                    else:
                        lgen+=ch[0]+'&'
                        lisgenfiltrati.append(ch[0])
                        dizconversione[ch[0]]=k
            if len(lisgenfiltrati)!=0:
                #chiedo allo storage se quei campioni non appartengono gia' a qualcun altro  
                storbarc=StorageTubeHandler()
                data=storbarc.read(request, lgen, operator)
                dizprov=json.loads(data['data'])
                print 'dizprov',dizprov
                
                diz={}
                for key,val in dizprov.items():
                    print 'd',key
                    v=val.split('|')
                    diz[key]=v
                print 'diz',diz
                print 'lisgenfiltrati',lisgenfiltrati
                lisg=Aliquot.objects.filter(uniqueGenealogyID__in=lisgenfiltrati,availability=1)
                for al in lisg:
                    gen=al.uniqueGenealogyID
                    #nella posizione 6 ho la disponibilita'
                    disponibil=diz[gen][6]
                    if disponibil=='No':
                        dizfin[gen]={'available':'no'}
                    else:
                        dizfin[gen]={'exists':'yes','available':'yes'}
                        #salvo il tipo che deve essere solo DNa o RNA, ma il controllo lo faccio poi lato client
                        dizfin[gen]['type']=al.idAliquotType.abbreviation
                        if al.idAliquotType.abbreviation=='DNA' or al.idAliquotType.abbreviation=='RNA':
                            #recupero l'oggetto feature relativo al volume
                            featuvol=Feature.objects.get(name='Volume',idAliquotType=al.idAliquotType)
                            #recupero l'oggetto feature relativo alla concentrazione
                            featuconc=Feature.objects.get(name='Concentration',idAliquotType=al.idAliquotType)
                            #print 'feat',featu
                            lvol=AliquotFeature.objects.filter(idAliquot=al,idFeature=featuvol)
                            if len(lvol)!=0:
                                print 'vol',lvol[0].value
                                dizfin[gen]['vol']=str(lvol[0].value)
                            lconc=AliquotFeature.objects.filter(idAliquot=al,idFeature=featuconc)
                            if len(lconc)!=0:
                                print 'conc',lconc[0].value
                                dizfin[gen]['conc']=str(lconc[0].value)
                            
                            dizfin[gen]['date']=str(al.idSamplingEvent.samplingDate)
                            dizfin[gen]['source']=al.idSamplingEvent.idSource.internalName
                            dizfin[gen]['genealogy']=al.uniqueGenealogyID
                            dizfin[gen]['tumor']=al.idSamplingEvent.idCollection.idCollectionType.abbreviation
                            dizfin[gen]['tissue']=al.idSamplingEvent.idTissueType.abbreviation
                            dizfin[gen]['user']=al.idSamplingEvent.idSerie.operator
                            
                            #dal campione risalgo al der event
                            lisderevent=DerivationEvent.objects.filter(idSamplingEvent=al.idSamplingEvent)
                            if len(lisderevent)!=0:
                                #prendo il campione madre del derivato
                                aliqmadre=lisderevent[0].idAliqDerivationSchedule.idAliquot
                                genmadre=GenealogyID(aliqmadre.uniqueGenealogyID)
                                dizfin[gen]['mothervector']=genmadre.getSampleVector()
                                dizfin[gen]['mothertype']=genmadre.getArchivedMaterial()
                                #prendo il qual event dall'aliqderivationschedule
                                lisqual=QualityEvent.objects.filter(idAliquotDerivationSchedule=lisderevent[0].idAliqDerivationSchedule)
                                if len(lisqual)!=0:
                                    #prendo l'evento di misura con il valore associato
                                    liseventi=MeasurementEvent.objects.filter(idMeasure=mispur230,idQualityEvent=lisqual[0])
                                    if len(liseventi)!=0:
                                        dizfin[gen]['pur230']=liseventi[0].value
                                    liseventi=MeasurementEvent.objects.filter(idMeasure=mispur280,idQualityEvent=lisqual[0])
                                    if len(liseventi)!=0:
                                        dizfin[gen]['pur280']=liseventi[0].value
                            #devo vedere se il campione e' stato rivalutato
                            lisriv=QualityEvent.objects.filter(idAliquot=al).order_by('-misurationDate','-id')
                            if len(lisriv)!=0:
                                lista=[]
                                for riv in lisriv:
                                    lista.append(riv.id)
                                #in lisriv[0] ho il valore piu' recente
                                #prendo l'evento di misura con il valore associato
                                liseventi=MeasurementEvent.objects.filter(idMeasure=mispur230,idQualityEvent__in=lista).order_by('-id')
                                if len(liseventi)!=0:
                                    dizfin[gen]['pur230']=liseventi[0].value
                                liseventi=MeasurementEvent.objects.filter(idMeasure=mispur280,idQualityEvent__in=lista).order_by('-id')
                                if len(liseventi)!=0:
                                    dizfin[gen]['pur280']=liseventi[0].value            
            print 'dizfin prima',dizfin
            #devo convertire le chiavi di dizfin in modo da avere lo stesso codice (che puo' essere gen o barcode)
            #che ho inviato tramite API
            print 'dizconversione',dizconversione
            for k,val in dizfin.items():
                nuovachiave=dizconversione[k]
                dizfin[nuovachiave]=val
                if nuovachiave!=k:
                    del dizfin[k]
            print 'dizfin dopo',dizfin
            return {'data':json.dumps(dizfin)}
        except Exception,e:
            print 'errore',e
            return {"data":'errore'}

#Per salvare le aliquote nuove che vengono create nel modulo molecolare (ad es. NGS) in caso di un esperimento esterno
#al LAS in cui si tracciano solo i campioni nuovi che vengono creati
class FacilitySaveAliquotsHandler(BaseHandler):
    allowed_methods = ('POST')
    @transaction.commit_on_success
    @method_decorator(get_functionality_decorator)
    def create(self, request):
        try:
            print request.POST
            lisnotexists=[]
            listaal=[]
            #e' formata da una lista di dizionari, in cui in ognuno ci sono i vari campi con i dati del campione
            listacampioni=json.loads(request.POST.get('aliquots'))
            print 'listacampioni',listacampioni
            #e' il tipo di esperimento effettuato (ad es. NGS)
            esperimento=request.POST.get('experiment')
            operatore=request.POST.get('operator')
            tumore=CollectionType.objects.get(abbreviation=esperimento)
            casuale=False
            #faccio la chiamata al LASHub per farmi dare il codice del caso
            val=LasHubNewCase(request, casuale, tumore.abbreviation)
            #ha gia' gli zeri davanti
            caso=NewCase(val, casuale, tumore)
            print 'caso',caso
            pr=CollectionProtocol.objects.get(title=esperimento)
            
            print 'wg',get_WG_string()
            #se il protocollo e' della Marsoni allora devo mettere in share anche lei per le aliquote
            liscollinvestig=CollectionProtocolInvestigator.objects.filter(idCollectionProtocol=pr)
            trovato=False
            if len(liscollinvestig)!=0:
                for coll in liscollinvestig:
                    if coll.idPrincipalInvestigator.surname=='Marsoni' and coll.idPrincipalInvestigator.name=='Silvia':
                        trovato=True
                        break
            listawg=[get_WG_string()]
            if trovato:
                listawg.append('Marsoni_WG')
            print 'listawg',listawg
            set_initWG(listawg)
            
            #il tessuto e' quello della facility con doppio 0
            tessuto_esp=TissueType.objects.get(longName='Facility')
            #scandisco per avere i campioni ordinati nei vari centri di provenienza, in modo che sorgente diversa
            #vuol dire collezione diversa
            #chiave la sorgente con le due lettere maiuscole e valore una lista con l'oggetto collezione e quello sorgente
            dizsorgenti={}
            #chiave il nome del campione e valore il contatore finale del barc che mi indica quale numero devo mettere alla fine
            diznomisample={}
            #chiave la label e valore il genid
            dizlabelgen={}
            
            for diz in listacampioni:
                #devo farlo solo se e' un campione nuovo e non se sto caricando un vecchio campione dalla biobanca
                gen=diz['genealogy']
                if gen=='':
                    print 'diz',diz
                    sorg=diz['source']                
                    if sorg not in dizsorgenti:
                        posto=Source.objects.get(internalName=sorg,type='Hospital')
                        collEvent=tumore.abbreviation+caso
                        collezione,creato=Collection.objects.get_or_create(itemCode=caso,
                                     idSource=posto,
                                     idCollectionType=tumore,
                                     collectionEvent=collEvent,
                                     patientCode=collEvent,
                                     idCollectionProtocol=pr)
                        print 'collezione',collezione
                        
                        if creato:
                            #solo se ho creato una nuova collezione comunico al modulo clinico le informazioni                
                            #L'ic non esiste ancora perche' lo sto creando adesso dal nulla, quindi non faccio 
                            #il controllo di esistenza tramite le API del modulo clinico. La chiave paziente la metto vuota perche' sto creando un paziente nuovo.
                            #Se mettessi il valore, il modulo clinico andrebbe a cercare quel paziente sul grafo e non trovandolo darebbe errore. Invece cosi' crea lui il nuovo dato
                            diztemp={'caso':collezione.itemCode,'tum':collezione.idCollectionType.abbreviation,'consenso':collezione.collectionEvent,'progetto':collezione.idCollectionProtocol.name,'source':collezione.idSource.internalName,'wg':[get_WG_string()],'operator':operatore,'paziente':''}
                            lisnotexists.append(diztemp)
                        
                        dizsorgenti[sorg]=[posto,collezione]
                        cas=int(caso)+1
                        caso=str(cas).zfill(4)
            print 'dizsorg',dizsorgenti
            #chiave la prima parte del genid e valore il contatore finale
            dizcontatori={}
            for diz in listacampioni:
                #devo farlo solo se e' un campione nuovo e non se sto caricando un vecchio campione dalla biobanca
                gen=diz['genealogy']
                if gen=='':
                    data_coll=diz['Extraction date']
                    if data_coll=='':
                        data_coll=str(date.today())                
                    #salvo la serie
                    ser,creato=Serie.objects.get_or_create(operator=operatore,
                                                           serieDate=data_coll)                                
                    
                    sorg=diz['source']
                    listemp=dizsorgenti[sorg]
                    #salvo il campionamento
                    campionamento,creato=SamplingEvent.objects.get_or_create(idTissueType=tessuto_esp,
                                                 idCollection=listemp[1],
                                                 idSource=listemp[0],
                                                 idSerie=ser,
                                                 samplingDate=data_coll)
                    print 'camp',campionamento
                    nomesamp=diz['Sample name']
                    
                    if nomesamp not in diznomisample:
                        val=0
                    else:
                        val=diznomisample[nomesamp]
                    val+=1
                    diznomisample[nomesamp]=val
                    iniziobarcode=nomesamp+'_'+operatore+'_'+data_coll
                    trovato=False
                    #guardo nello storage se esiste gia' questo barcode e se si' incremento il contatore finale
                    while not trovato:
                        barcode=iniziobarcode+'_'+str(val)
                        print 'barcode',barcode
                        request.META['HTTP_WORKINGGROUPS']=get_WG_string()
                        hand=CollectTubeHandler()
                        data=hand.read(request, barcode, 'Tube')
                        if data['data']!='err_esistente':
                            trovato=True
                        else:
                            val+=1
                            print 'val',val
                            diznomisample[nomesamp]=val
                    
                    ffpe='true'
                    #la maggior parte delle volte sara' DNA (se no RNA)
                    tipoaliq=diz['tipo']                
                    tipoaliquota= AliquotType.objects.get(abbreviation=tipoaliq)
                    print 'tipo aliquota',tipoaliq
                    if tipoaliq=='DNA':
                        abbrev='D'
                    else:
                        abbrev='R'
                    #devo creare il genid
                    collezione=listemp[1]
                    genid=collezione.idCollectionType.abbreviation+collezione.itemCode+tessuto_esp.abbreviation+'00000'
                        
                    if genid in dizcontatori:
                        cont=dizcontatori[genid]
                    else:
                        cont=1
                    genidfin=genid+str(cont).zfill(3)+'000'+abbrev+'01000'
                    cont+=1
                    dizcontatori[genid]=cont
                    print 'dizcontatori',dizcontatori
                    
                    a=Aliquot(barcodeID=barcode,
                           uniqueGenealogyID=genidfin,
                           idSamplingEvent=campionamento,
                           idAliquotType=tipoaliquota,
                           timesUsed=0,
                           availability=1,
                           derived=1,
                           archiveDate=data_coll)
                    print 'a',a
                    a.save()
                    
                    if 'volumefornito' in diz:
                        #prendo la feature del volume originale
                        featorigvol=Feature.objects.get(idAliquotType=tipoaliquota,name='OriginalVolume')
                        featvol=Feature.objects.get(idAliquotType=tipoaliquota,name='Volume')
                        
                        #salvo il volume
                        aliqfeaturevol=AliquotFeature(idAliquot=a,
                                           idFeature=featvol,
                                           value=diz['volumefornito'])
                        aliqfeaturevol.save()
                        
                        #salvo il volume originale
                        aliqfeatureorigvol=AliquotFeature(idAliquot=a,
                                           idFeature=featorigvol,
                                           value=diz['volumefornito'])
                        aliqfeatureorigvol.save()
                    
                    if 'Nanodrop' in diz:
                        featorigconc=Feature.objects.get(idAliquotType=tipoaliquota,name='OriginalConcentration')
                        featconc=Feature.objects.get(idAliquotType=tipoaliquota,name='Concentration')
                        
                        aliqfeature=AliquotFeature(idAliquot=a,
                                           idFeature=featconc,
                                           value=diz['Nanodrop'])
                        aliqfeature.save()
                        
                        #salvo il volume originale
                        aliqfeature=AliquotFeature(idAliquot=a,
                                           idFeature=featorigconc,
                                           value=diz['Nanodrop'])
                        aliqfeature.save()
                    
                    valori=genidfin+',,,,'+barcode+','+tipoaliq+','+ffpe+',,,,,,'+str(data_coll)
                    listaal.append(valori)
                    
                    dizlabelgen[diz['label']]={'gen':genidfin}
                else:
                    #devo decrementare il volume del campione del valore presente nel dizionario. Non lo devo piu' fare qui ma
                    #lo faccio al momento dell'esecuzione dell'esperimento, quando il modulo di ngs fara' la post verso la biobanca dicendo
                    #di decrementare il volume con quello effettivamente usato
                    '''laliq=Aliquot.objects.filter(uniqueGenealogyID=gen)
                    print 'laliq',laliq
                    if len(laliq)!=0:
                        al=laliq[0]
                        featuvol=Feature.objects.get(name='Volume',idAliquotType=al.idAliquotType)
                        lvol=AliquotFeature.objects.filter(idAliquot=al,idFeature=featuvol)
                        if len(lvol)!=0:
                            vv=lvol[0]
                            print 'vol',vv.value
                            volfin=vv.value-float(diz['volumefornito'])                            
                            print 'volfin',volfin
                            if volfin<0:
                                volfin=0
                            vv.value=volfin
                            vv.save()'''
                    dizlabelgen[diz['label']]={'gen':gen}
            print 'listaaliq',listaal
            print 'dizlabelgen',dizlabelgen
            request,errore=SalvaInStorage(listaal,request)
            print 'err', errore
            if errore==True:
                transaction.rollback()
                variables = RequestContext(request, {'errore':errore})
                return render_to_response('tissue2/index.html',variables)
            #metto il commit perche' il modulo clinico deve gia' trovare sul grafo il nodo collezione
            transaction.commit()
            
            errore=saveInClinicalModule([],lisnotexists,[get_WG_string()],operatore,[])
            if errore:
                raise Exception()
            return {'data':'ok','dictlabelgen':dizlabelgen}
        except Exception, e:
            print 'ecc',e
            transaction.rollback()
            return {'data':'errore'}
        
#mi da' tutte le informazioni di tutte le aliquote dei pazienti
class PatientAliqInfoHandler(BaseHandler):
    allowed_methods = ('GET')
    @method_decorator(get_functionality_decorator)
    def read(self, request,codpaz,aliqtipo,tesstipo,vettore,maschera,utente):
        try:
            listadiz=[]
            lista1=[]
            lista2=[]
            dizgen={}
            listaal=[]
            #prendo le collezioni di quel paziente
            listacoll=Collection.objects.filter(patientCode=codpaz)
            if len(listacoll)!=0:
                for coll in listacoll:
                    lista1.append( Q(**{'idCollection': coll.id} ))
                if len(lista1)!=0:
                    lissamp=SamplingEvent.objects.filter(reduce(operator.or_, lista1))
                    print 'lissamp',lissamp
                    if len(lissamp)!=0:
                        for samp in lissamp:
                            lista2.append( Q(**{'idSamplingEvent': samp.id} ))
                        if len(lista2)!=0:
                            #prendo tutte le aliquote che appartengono a collezioni di quel paziente
                            listaal=Aliquot.objects.filter(reduce(operator.or_, lista2))
            print 'listaal',listaal
            
            del lista1[:]
            del lista2[:]
            lista3=[]
            
            #in base alla maschera devo vedere quali campi restituire
            #se non c'e' una maschera, restituisco quella generica
            if maschera =='None':
                masch=Mask.objects.get(name='NoMask')
            else:
                masch=maschera
            listacampi=MaskMaskField.objects.filter(idMask=masch)
            listanomicampi=[]
            listacript=[]
            for campi in listacampi:
                listanomicampi.append(campi.idMaskField.name)
                listacript.append(campi.encrypted)
                    
            if len(listaal)!=0:
                if aliqtipo!='None':
                    tipal=AliquotType.objects.get(id=aliqtipo)
                if tesstipo!='None':
                    tiptess=TissueType.objects.get(id=tesstipo)
                    
                #devo filtrare queste aliquote in base ai campi scelti dall'utente
                for al in listaal:
                    if aliqtipo!='None':                        
                        if al.idAliquotType.longName==tipal.longName:
                            lista1.append( Q(**{'id': al.id} ))
                    
                    if tesstipo!='None':
                        if al.idSamplingEvent.idTissueType.longName==tiptess.longName:
                            lista2.append( Q(**{'id': al.id} ))
                    
                    if vettore!='None':
                        gen=GenealogyID(al.uniqueGenealogyID)
                        vett=gen.getSampleVector()
                        if vett==vettore:
                            lista3.append( Q(**{'id': al.id} ))
                    
                if aliqtipo!='None':
                    if len(lista1)==0:
                        return {'data':json.dumps([]),'colonne':json.dumps(listanomicampi),'cript':json.dumps(listacript)}
                    listaal=listaal.filter(reduce(operator.or_, lista1))
                if tesstipo!='None':
                    if len(lista2)==0:
                        return {'data':json.dumps([]),'colonne':json.dumps(listanomicampi),'cript':json.dumps(listacript)}
                    listaal=listaal.filter(reduce(operator.or_, lista2))
                if vettore!='None':
                    if len(lista3)==0:
                        return {'data':json.dumps([]),'colonne':json.dumps(listanomicampi),'cript':json.dumps(listacript)}
                    listaal=listaal.filter(reduce(operator.or_, lista3))
                print 'lista filtrata',listaal                
                
                #if 'Plate' in listanomicampi or 'Tube position' in listanomicampi or 'Plate position' in listanomicampi or 'Rack' in listanomicampi or 'Freezer' in listanomicampi:
                #chiamo la API in ogni caso perche' ho bisogno comunque del barc del campione
                strgen=''
                lis_pezzi_url=[]

                for aliq in listaal:
                    strgen+=aliq.uniqueGenealogyID+'&'
                    if len(strgen)>2000:
                    #cancello la & alla fine della stringa
                        lis_pezzi_url.append(strgen[:-1])
                        strgen=''
                #cancello la & alla fine della stringa
                lgen=strgen[:-1]
                print 'lgen',lgen
                if lgen!='':
                    lis_pezzi_url.append(lgen)
                
                if len(lis_pezzi_url)!=0:
                    for elementi in lis_pezzi_url:
                        storbarc=StorageTubeHandler()
                        data=storbarc.read(request, elementi, utente)
                        dizprov=json.loads(data['data'])
                        dizgen = dict(dizgen.items() + dizprov.items())                  
                print 'dizgen',dizgen
                    
                for al in listaal:
                    diz={}
                    ge = GenealogyID(al.uniqueGenealogyID)
                    if 'Plate' in listanomicampi:
                        pias=''
                        if dizgen.has_key(al.uniqueGenealogyID):
                            lval=dizgen[al.uniqueGenealogyID]
                            val=lval.split('|')
                            pias=val[2]
                        diz['Plate']=pias
                    if 'Tube position' in listanomicampi:
                        pos=''
                        if dizgen.has_key(al.uniqueGenealogyID):
                            lval=dizgen[al.uniqueGenealogyID]
                            val=lval.split('|')
                            pos=val[1]
                        diz['Tube position']=pos
                    if 'Plate position' in listanomicampi:
                        pos=''
                        if dizgen.has_key(al.uniqueGenealogyID):
                            lval=dizgen[al.uniqueGenealogyID]
                            val=lval.split('|')
                            pos=val[3]
                        diz['Plate position']=pos
                    if 'Rack' in listanomicampi:
                        rack=''
                        if dizgen.has_key(al.uniqueGenealogyID):
                            lval=dizgen[al.uniqueGenealogyID]
                            val=lval.split('|')
                            rack=val[4]
                        diz['Rack']=rack
                    if 'Freezer' in listanomicampi:
                        freezer=''
                        if dizgen.has_key(al.uniqueGenealogyID):
                            lval=dizgen[al.uniqueGenealogyID]
                            val=lval.split('|')
                            freezer=val[5]
                        diz['Freezer']=freezer
                    if 'Coll. date' in listanomicampi:
                        #se e' un derivato devo mettere la data del collezionamento del padre
                        if al.derived==1:
                            lisderevent=DerivationEvent.objects.filter(idSamplingEvent=al.idSamplingEvent)
                            if len(lisderevent)!=0:
                                datareale=str(lisderevent[0].idAliqDerivationSchedule.idAliquot.idSamplingEvent.samplingDate)
                            else:
                                #se non ha un evento di derivazione perche' e' un'aliquota esterna
                                datareale=str(al.idSamplingEvent.samplingDate)
                        else:
                            datareale=str(al.idSamplingEvent.samplingDate)
                        diz['Coll. date']=datareale
                    if 'Coll. date(1)' in listanomicampi:
                        #se e' un derivato devo mettere la data del collezionamento del padre
                        if al.derived==1:
                            lisderevent=DerivationEvent.objects.filter(idSamplingEvent=al.idSamplingEvent)
                            if len(lisderevent)!=0:
                                operat=lisderevent[0].idAliqDerivationSchedule.idAliquot.idSamplingEvent.idSerie.operator
                                #solo se l'operatore che ha fatto la collezione corrisponde con quello loggato
                                if operat==utente:
                                    datareale=str(lisderevent[0].idAliqDerivationSchedule.idAliquot.idSamplingEvent.samplingDate)
                                else:
                                    datareale=''
                            else:
                                operat=al.idSamplingEvent.idSerie.operator
                                if operat==utente:
                                    #se non ha un evento di derivazione perche' e' un'aliquota esterna
                                    datareale=str(al.idSamplingEvent.samplingDate)
                                else:
                                    datareale=''
                        else:
                            operat=al.idSamplingEvent.idSerie.operator
                            if operat==utente:
                                datareale=str(al.idSamplingEvent.samplingDate)
                            else:
                                datareale=''
                            
                        diz['Coll. date(1)']=datareale
                    if 'Extr. date' in listanomicampi:
                        #se e' un derivato devo mettere la data di creazione effettiva
                        if al.derived==1:
                            datareale=str(al.idSamplingEvent.samplingDate)
                        else:
                            datareale=''
                        diz['Extr. date']=datareale
                    if 'Collection type' in listanomicampi:
                        diz['Collection type']=al.idSamplingEvent.idCollection.idCollectionType.abbreviation
                    if 'Case' in listanomicampi:
                        diz['Case']=al.idSamplingEvent.idCollection.itemCode
                    if 'InformedCons.' in listanomicampi:
                        diz['InformedCons.']=al.idSamplingEvent.idCollection.collectionEvent
                    if 'Tissue' in listanomicampi:
                        diz['Tissue']=al.idSamplingEvent.idTissueType.abbreviation
                    if 'Aliquot type' in listanomicampi:
                        diz['Aliquot type']=al.idAliquotType.abbreviation
                    if 'Barcode' in listanomicampi:
                        barc=''
                        if dizgen.has_key(al.uniqueGenealogyID):
                            lval=dizgen[al.uniqueGenealogyID]
                            val=lval.split('|')
                            barc=val[0]
                        diz['Barcode']=barc
                    if 'Aliquot ID' in listanomicampi:
                        diz['Aliquot ID']=ge.getAliquotExtraction()
                    if 'Further info' in listanomicampi:
                        info=ge.getGeneration()+ge.getMouse()+ge.getTissueType()
                        diz['Further info']=info
                    if 'Avail.' in listanomicampi:
                        if al.availability==0:                            
                            diz['Avail.']='False'
                        else:
                            diz['Avail.']='True'
                    if '24-H urines(ml)' in listanomicampi:
                        valore=''
                        clinfeat=ClinicalFeature.objects.get(name='24-H urines')
                        collclinfeat=CollectionClinicalFeature.objects.filter(idCollection=al.idSamplingEvent.idCollection,idClinicalFeature=clinfeat)
                        if len(collclinfeat)!=0:
                            valore=collclinfeat[0].value
                        diz['24-H urines(ml)']=valore
                    if 'Therapy' in listanomicampi:
                        valore=''
                        clinfeat=ClinicalFeature.objects.get(name='anti-EGFR Therapy')
                        collclinfeat=CollectionClinicalFeature.objects.filter(idCollection=al.idSamplingEvent.idCollection,idClinicalFeature=clinfeat)
                        if len(collclinfeat)!=0:
                            valore=collclinfeat[0].value
                        diz['Therapy']=valore
                    if 'Notes' in listanomicampi:
                        valore=''
                        clinfeat=ClinicalFeature.objects.get(name='Notes')
                        collclinfeat=CollectionClinicalFeature.objects.filter(idCollection=al.idSamplingEvent.idCollection,idClinicalFeature=clinfeat)
                        if len(collclinfeat)!=0:
                            valore=collclinfeat[0].value
                        diz['Notes']=valore
                    if 'Volume(ul)' in listanomicampi:
                        vol=''
                        lisfeatvol=Feature.objects.filter(Q(name='Volume')&Q(idAliquotType=al.idAliquotType)&Q(measureUnit='ul'))
                        if len(lisfeatvol)!=0:
                            lisaliqfeat=AliquotFeature.objects.filter(Q(idFeature=lisfeatvol[0])&Q(idAliquot=al))
                            if len(lisaliqfeat)!=0:
                                vol=str(lisaliqfeat[0].value)
                        diz['Volume(ul)']=vol
                    if 'Conc.(ng/ul)' in listanomicampi:
                        '''lisfeatconc=Feature.objects.filter(Q(name='Concentration')&Q(idAliquotType=al.idAliquotType)&Q(measureUnit='ng/ul'))
                        if len(lisfeatconc)!=0:
                            lisaliqfeat=AliquotFeature.objects.filter(Q(idFeature=lisfeatconc[0])&Q(idAliquot=al))
                            if len(lisaliqfeat)!=0:
                                conc=str(lisaliqfeat[0].value)'''
                        valore=''
                        if al.derived==1:
                            strum=Instrument.objects.filter(name='QUBIT')
                            if len(strum)!=0:
                                mis=Measure.objects.get(name='concentration',idInstrument=strum[0])
                                #dal campione risalgo al der event
                                lisderevent=DerivationEvent.objects.filter(idSamplingEvent=al.idSamplingEvent)
                                if len(lisderevent)!=0:
                                    #prendo il qual event dall'aliqderivationschedule
                                    lisqual=QualityEvent.objects.filter(idAliquotDerivationSchedule=lisderevent[0].idAliqDerivationSchedule)
                                    if len(lisqual)!=0:
                                        #prendo l'evento di misura con il valore della conc associata
                                        liseventi=MeasurementEvent.objects.filter(idMeasure=mis,idQualityEvent=lisqual[0])
                                        if len(liseventi)!=0:
                                            valore=liseventi[0].value
                                #devo vedere se il campione e' stato rivalutato
                                lisriv=QualityEvent.objects.filter(idAliquot=al).order_by('-misurationDate','-id')
                                if len(lisriv)!=0:
                                    lista=[]
                                    for riv in lisriv:
                                        lista.append(riv.id)
                                    #in lisriv[0] ho il valore piu' recente
                                    #prendo l'evento di misura con il valore della conc associata
                                    liseventi=MeasurementEvent.objects.filter(idMeasure=mis,idQualityEvent__in=lista).order_by('-id')
                                    if len(liseventi)!=0:
                                        valore=liseventi[0].value
                        if valore=='':
                            lisfeatconc=Feature.objects.filter(Q(name='Concentration')&Q(idAliquotType=al.idAliquotType)&Q(measureUnit='ng/ul'))
                            if len(lisfeatconc)!=0:
                                lisaliqfeat=AliquotFeature.objects.filter(Q(idFeature=lisfeatconc[0])&Q(idAliquot=al))
                                if len(lisaliqfeat)!=0:
                                    valore=str(lisaliqfeat[0].value)
                        diz['Conc.(ng/ul)']=valore
                    if 'GE/Vex (GE/ml)' in listanomicampi:
                        valore=''
                        if al.derived==1:
                            mis=Measure.objects.get(name='GE/Vex')
                            #dal campione risalgo al der event
                            lisderevent=DerivationEvent.objects.filter(idSamplingEvent=al.idSamplingEvent)
                            if len(lisderevent)!=0:
                                #prendo il qual event dall'aliqderivationschedule
                                lisqual=QualityEvent.objects.filter(idAliquotDerivationSchedule=lisderevent[0].idAliqDerivationSchedule)
                                if len(lisqual)!=0:
                                    #prendo l'evento di misura con il valore del GE associato
                                    liseventi=MeasurementEvent.objects.filter(idMeasure=mis,idQualityEvent=lisqual[0])
                                    if len(liseventi)!=0:
                                        valore=liseventi[0].value
                            #devo vedere se il campione e' stato rivalutato
                            lisriv=QualityEvent.objects.filter(idAliquot=al).order_by('-misurationDate','-id')
                            if len(lisriv)!=0:
                                lista=[]
                                for riv in lisriv:
                                    lista.append(riv.id)
                                #in lisriv[0] ho il valore piu' recente
                                #prendo l'evento di misura con il valore del GE associato
                                liseventi=MeasurementEvent.objects.filter(idMeasure=mis,idQualityEvent__in=lista).order_by('-id')
                                if len(liseventi)!=0:
                                    valore=liseventi[0].value
                        diz['GE/Vex (GE/ml)']=valore
                    #diz['available']=al.availability
                    diz['genid']=al.uniqueGenealogyID
                    diz['patient']=al.idSamplingEvent.idCollection.patientCode
                    listadiz.append(diz)
            print 'listadiz',listadiz                    
            return {'data':json.dumps(listadiz),'colonne':json.dumps(listanomicampi),'cript':json.dumps(listacript)}
        except Exception,e:
            print 'err',e
            return {"data":'errore'}
        
#mi da' tutti i patient id che soddisfano i criteri scelti dall'utente
class PatientListHandler(BaseHandler):
    allowed_methods = ('GET')
    @method_decorator(get_functionality_decorator)
    def read(self, request,operatore,ospedale,colltype,altype,datadal,dataal,protocol,consenso):
        try:
            lista1=[]
            lista2=[]
            lista3=[]
            lista4=[]
            lista5=[]
            lispaz=[]
            print 'operatore',operatore
            print 'ospedale',ospedale
            print 'colltype',colltype
            print 'datadal',datadal
            print 'dataal',dataal
            print 'protocol',protocol
            print 'consenso',consenso
            
            liscol=Collection.objects.all()
            if operatore!= 'None':
                utente=User.objects.get(id=operatore)
                print 'utente',utente
                listaser=Serie.objects.filter(operator=utente.username) 
                if len(listaser)!=0:
                    for ser in listaser:
                        lista1.append( Q(**{'idSerie': ser.id} ))
                    if len(lista1)!=0:
                        lissamp=SamplingEvent.objects.filter(reduce(operator.or_, lista1))
                        if len(lissamp)!=0:
                            for samp in lissamp:
                                lista2.append(Q(**{'id': samp.idCollection.id} ))
                print 'lista2',lista2
                #se la lista e' vuota non controllo neanche gli altri parametri, essendo tutti in and fra loro,
                #ma restituisco subito una lista vuota
                if len(lista2)==0:
                    return {'data':json.dumps([])}
                liscol=liscol.filter(reduce(operator.or_, lista2)) 
            
            if ospedale!='None':
                osp=Source.objects.get(id=ospedale)
                listacoll=Collection.objects.filter(idSource=osp)
                if len(listacoll)!=0:
                    for coll in listacoll:
                        lista3.append(Q(**{'id': coll.id} ))
                if len(lista3)==0:
                    return {'data':json.dumps([])}
                liscol=liscol.filter(reduce(operator.or_, lista3))
                
            if colltype!='None':
                ctipo=CollectionType.objects.get(id=colltype)
                listacoll=Collection.objects.filter(idCollectionType=ctipo)
                if len(listacoll)!=0:
                    for coll in listacoll:
                        lista4.append(Q(**{'id': coll.id} ))
                if len(lista4)==0:
                    return {'data':json.dumps([])}
                liscol=liscol.filter(reduce(operator.or_, lista4))
                
            if altype!='None':
                altipo=AliquotType.objects.get(id=altype)
                lisaliq=Aliquot.objects.filter(idAliquotType=altipo)
                if len(lisaliq)==0:
                    return {'data':json.dumps([])}
                listemp=[]
                for ali in lisaliq:
                    if ali.idSamplingEvent.idCollection.id not in listemp:
                        listemp.append(ali.idSamplingEvent.idCollection.id)
                print 'listemp',listemp
                liscol=liscol.filter(id__in=listemp)
            
            if datadal!='None':
                attr=datadal.split('_')
                attr2=attr[1].split('-')
                print 'attr2',attr2
                datarif=datetime.date(int(attr2[0]),int(attr2[1]),int(attr2[2]))
                if dataal!='None':
                    att2=dataal.split('-')
                    datarif2=datetime.date(int(att2[0]),int(att2[1]),int(att2[2]))
                l_coll=Collection.objects.all()
                for c in l_coll:
                    listasamp=SamplingEvent.objects.filter(idCollection=c).order_by('-samplingDate')
                    if len(listasamp)!=0:
                        datasamp=listasamp[0].samplingDate
                        #print 'datasamp',datasamp
                        #attr[1] contiene la data inserita dall'utente
                        if attr[0]=='<' and datasamp<datarif:
                            lista5.append(Q(**{'id': c.id} ))
                        elif attr[0]=='>' and datasamp>datarif:
                            if dataal!='None':
                                if datasamp<datarif2:
                                    lista5.append(Q(**{'id': c.id} ))
                            else:
                                lista5.append(Q(**{'id': c.id} ))
                        elif attr[0]=='=' and datasamp==datarif:
                            lista5.append(Q(**{'id': c.id} ))           
                if len(lista5)==0:
                    return {'data':json.dumps([])}
                liscol=liscol.filter(reduce(operator.or_, lista5))
            
            if protocol!='None':
                lista6=[]
                prot=CollectionProtocol.objects.get(id=protocol)
                listacoll=Collection.objects.filter(idCollectionProtocol=prot)
                if len(listacoll)!=0:
                    for coll in listacoll:
                        lista6.append(Q(**{'id': coll.id} ))
                if len(lista6)==0:
                    return {'data':json.dumps([])}
                liscol=liscol.filter(reduce(operator.or_, lista6))
            
            if consenso!='None':
                lista7=[]
                listacoll=Collection.objects.filter(collectionEvent=consenso)
                if len(listacoll)!=0:
                    for coll in listacoll:
                        lista7.append(Q(**{'id': coll.id} ))
                if len(lista7)==0:
                    return {'data':json.dumps([])}
                liscol=liscol.filter(reduce(operator.or_, lista7))
                    
            print 'liscol',liscol
            for co in liscol:
                if co.patientCode!=None and co.patientCode!='':
                    if co.patientCode not in lispaz:
                        lispaz.append(co.patientCode)
                                
            return {'data':json.dumps(lispaz)}
        except Exception,e:
            print 'err',e
            return {"data":'errore'}

#mi da' le informazioni dei parametri clinici delle collezioni del paziente
class PatientClinicalFeatureHandler(BaseHandler):
    allowed_methods = ('GET')
    @method_decorator(get_functionality_decorator)
    def read(self, request,codpaz,aliqtipo,tesstipo,vettore):
        try:            
            lista1=[]
            lista2=[]
            listaal=[]
            dizfin={}
            #lista per mantenere l'ordine delle collezioni all'interno del paziente
            listafin=[]
            #prendo le collezioni di quel paziente
            listacoll=Collection.objects.filter(patientCode=codpaz)
            if len(listacoll)!=0:
                for coll in listacoll:
                    lista1.append( Q(**{'idCollection': coll.id} ))
                if len(lista1)!=0:
                    lissamp=SamplingEvent.objects.filter(reduce(operator.or_, lista1))
                    print 'lissamp',lissamp
                    if len(lissamp)!=0:
                        for samp in lissamp:
                            lista2.append( Q(**{'idSamplingEvent': samp.id} ))
                        if len(lista2)!=0:
                            #prendo tutte le aliquote che appartengono a collezioni di quel paziente
                            listaal=Aliquot.objects.filter(reduce(operator.or_, lista2))
            print 'listaal',listaal
            
            del lista1[:]
            del lista2[:]
            lista3=[]                    
                    
            if len(listaal)!=0:
                if aliqtipo!='None':
                    tipal=AliquotType.objects.get(id=aliqtipo)
                if tesstipo!='None':
                    tiptess=TissueType.objects.get(id=tesstipo)
                    
                #devo filtrare queste aliquote in base ai campi scelti dall'utente
                for al in listaal:
                    if aliqtipo!='None':                        
                        if al.idAliquotType.longName==tipal.longName:
                            lista1.append( Q(**{'id': al.id} ))
                    
                    if tesstipo!='None':
                        if al.idSamplingEvent.idTissueType.longName==tiptess.longName:
                            lista2.append( Q(**{'id': al.id} ))
                    
                    if vettore!='None':
                        gen=GenealogyID(al.uniqueGenealogyID)
                        vett=gen.getSampleVector()
                        if vett==vettore:
                            lista3.append( Q(**{'id': al.id} ))
                    
                if aliqtipo!='None':
                    if len(lista1)==0:
                        return {'data':json.dumps(dizfin),'liscoll':json.dumps(listafin)}
                    listaal=listaal.filter(reduce(operator.or_, lista1))
                if tesstipo!='None':
                    if len(lista2)==0:
                        return {'data':json.dumps(dizfin),'liscoll':json.dumps(listafin)}
                    listaal=listaal.filter(reduce(operator.or_, lista2))
                if vettore!='None':
                    if len(lista3)==0:
                        return {'data':json.dumps(dizfin),'liscoll':json.dumps(listafin)}
                    listaal=listaal.filter(reduce(operator.or_, lista3))
                print 'lista filtrata',listaal
                #ho filtrato le aliquote in base ai parametri della schermata, adesso devo andare a prendere i parametri 
                #delle collezioni rimaste
                liscoll=[]
                for al in listaal:
                    idcoll=al.idSamplingEvent.idCollection.id
                    if idcoll not in liscoll:
                        liscoll.append(idcoll)
                        #metto tutte le collezioni nella lista anche quelle che non hanno dei parametri clinici associati
                        #e di conseguenza nel dizionario riepilogativo metto una lista vuota
                        caso=al.idSamplingEvent.idCollection.idCollectionType.abbreviation+al.idSamplingEvent.idCollection.itemCode                    
                        listafin.append(caso)
                        dizfin[caso]=[]
                        
                print 'liscoll',liscoll
                #devo escludere la feature dell'idCellLine, che ha solo scopi interni e non serve farlo vedere all'utente
                feat=ClinicalFeature.objects.get(name='idCellLine')
                lisvalclin=CollectionClinicalFeature.objects.filter(idCollection__in=liscoll).exclude(idClinicalFeature=feat)
                print 'lisvalclin',lisvalclin
                
                for val in lisvalclin:
                    caso=val.idCollection.idCollectionType.abbreviation+val.idCollection.itemCode
                        
                    if caso in dizfin:
                        listemp=dizfin[caso]
                    else:
                        listemp=[]
                    
                    #devo sapere a quale parametro di livello 1 appartiene quello attuale per poi visualizzarlo
                    print 'vvv',val.idClinicalFeature
                    if val.idClinicalFeature.idClinicalFeature==None:
                        nome='None'
                    else:
                        padre=val.idClinicalFeature.idClinicalFeature
                        while padre.idClinicalFeature!=None:
                            padre=padre.idClinicalFeature
                        nome=padre.name
                    diz2={'feat':val.idClinicalFeature.name,'value':val.value,'unit':val.idClinicalFeature.measureUnit,'padre':nome}
                    if val.idSamplingEvent==None:
                        #devo quindi basarmi sulla collezione per avere operatore e data
                        listasamp=SamplingEvent.objects.filter(idCollection=val.idCollection).order_by('samplingDate')
                        if len(listasamp)!=0:
                            samp=listasamp[0]
                    else:
                        samp=val.idSamplingEvent
                        
                    datasamp=str(samp.samplingDate)
                    operatsamp=samp.idSerie.operator
                    #print 'datasamp',datasamp
                    
                    diz2['date']=datasamp
                    diz2['operat']=operatsamp
                    listemp.append(diz2)
                    dizfin[caso]=listemp
                            
                print 'listafin',listafin
                print 'dizfin',dizfin
            return {'data':json.dumps(dizfin),'liscoll':json.dumps(listafin)}
        except Exception,e:
            print 'err',e
            return {"data":'errore'}

#mi restituisce la lista dei miti con cui mascherare i dati
class MaskHandler(BaseHandler):
    allowed_methods = ('GET')
    @method_decorator(get_functionality_decorator)
    def read(self, request):
        try:
            #apro il file con dentro i nomi delle divinita'
            percorso=os.path.join(os.path.dirname(__file__),'Patient/Mitologia.txt')
            print 'perc',percorso
            f=open(percorso)
            lines = f.readlines()
            f.close()
            
            return {'data':json.dumps(lines)}
        except Exception,e:
            print 'err',e
            return {"data":'errore'}
        
#mi restituisce la lista delle abbreviazioni dei tipi di aliquote
class InfoAliqTypeHandler(BaseHandler):
    allowed_methods = ('GET')
    @method_decorator(get_functionality_decorator)
    def read(self, request):
        try:
            listafin=[]
            listatipi=AliquotType.objects.all()
            for tipi in listatipi:
                listafin.append(tipi.abbreviation)
            return listafin
        except Exception,e:
            print 'err',e
            return {"data":'errore'}

#Serve per caricare le provette singole nella collezione
class CollectTubeHandler(BaseHandler):
    allowed_methods = ('GET')
    @method_decorator(get_functionality_decorator)
    def read(self, request, barcode,tipo):
        try:
            print 'tipo',tipo
            indir=Urls.objects.get(default=1).url
            barcode=barcode.replace('#','%23')
            req = urllib2.Request(indir+"/api/biocassette/"+barcode + '/' + tipo+ '/', headers={"workingGroups" : get_WG_string()})
            u = urllib2.urlopen(req)
            #u = urllib2.urlopen(indir+"/api/biocassette/"+barcode + '/' + tipo+ '/')
            data = json.loads(u.read())
            print 'data',data
            return data
            
        except Exception,e:
            print 'err',e
            return {"data":'errore'}
        
#Serve per caricare dallo storage i dati di ogni singola provetta
class StorageTubeHandler(BaseHandler):
    allowed_methods = ('GET')
    @method_decorator(get_functionality_decorator)
    def read(self, request, listabarc,utente):
        try:
            indir=Urls.objects.get(default=1).url
            listabarc=listabarc.replace('#','%23')
            req = urllib2.Request(indir+"/api/tube/"+listabarc + '/' + utente, headers={"workingGroups" : get_WG_string()})
            u = urllib2.urlopen(req)
            #u = urllib2.urlopen(indir+"/api/tube/"+listabarc + '/' + utente)
            data = json.loads(u.read())
            print 'data',data
            return data
            
        except Exception,e:
            print 'err',e
            return {"data":'errore'}
        
#Serve per verificare se un barcode esiste gia'
#E' chiamata nella schermata di inserimento delle aliquote esterne
class CollaborTubeHandler(BaseHandler):
    allowed_methods = ('GET')
    @method_decorator(get_functionality_decorator)
    def read(self, request, barcode):
        try:
            print 'barcode',barcode
            indir=Urls.objects.get(default=1).url
            barcode=barcode.replace('#','%23')
            req = urllib2.Request(indir+'/api/plate/'+barcode+'/TUBEEXTERN/extern', headers={"workingGroups" : get_WG_string()})
            u = urllib2.urlopen(req)
            #u = urllib2.urlopen(indir+'/api/plate/'+barcode+'/TUBEEXTERN/extern')
            #e' giusto che ritorni errore perche' non c'e' quel barcode nello storage 
            #e quindi la get nel DB da' l'eccezione
            data = json.loads(u.read())
            print 'data',data
            return data
            
        except Exception,e:
            print 'err',e
            return {"data":'errore'}
        
#Serve per verificare se un coll event esiste gia'
class CheckPatientHandler(BaseHandler):
    allowed_methods = ('GET')
    @method_decorator(get_functionality_decorator)
    def read(self, request, coll_event,patient,hospital,project):
        try:            
            print 'coll event',coll_event            
            prog=CollectionProtocol.objects.get(id=project)
            print'prog',prog
            #devo fare la chiamata al modulo clinico per vedere se il consenso c'e' gia' o no
            servizio=WebService.objects.get(name='Clinical')
            urlclin=Urls.objects.get(idWebService=servizio).url
            #faccio la get al modulo dandogli la lista con dentro i dizionari
            indir=urlclin+'/coreProject/api/informedConsent/?ICcode='+coll_event+'&project='+prog.project
            print 'indir',indir
            try:
                req = urllib2.Request(indir, headers={"workingGroups" : get_WG_string()})
                u = urllib2.urlopen(req)
            except HTTPError,e:
                print 'code',e.code
                if e.code == 404:
                    #se e' 404 not found vuol dire che il codice non esiste ancora, quindi l'utente puo' proseguire                
                    return{'event':'new'}
                    
            #return{'event':'new'}
            
            res = json.loads(u.read())
            print 'res',res
            paziente=res['localId']
            idgrafo=res['patientUuid']
            print 'paziente',paziente
            #res='new'
            if paziente==None:
                return {'event':'alias_exists','idgrafo':idgrafo}
            else:
                return {'event':'ci_exists','paz':paziente,'idgrafo':idgrafo}
            
            '''#se il coll_event esiste gia', allora errore
            if coll_event!='None':
                listacoll=Collection.objects.filter(collectionEvent=coll_event)
                if len(listacoll)!=0:
                    return {'event':'duplic'}
            osp=Source.objects.get(id=hospital)
            #guardo se c'e' gia' una collezione per quel paziente
            listacoll=Collection.objects.filter(idSource=osp,patientCode=patient).order_by('id')
            print 'lista',listacoll
            if len(listacoll)==0:
                return{'event':''}
            else:
                #c'e' una collezione: devo proporre un coll event
                #prendo il coll event dell'ultima collezione
                eve=listacoll[len(listacoll)-1].collectionEvent
                print 'eve',eve
                #divido in base al _
                evespl=eve.split('_')
                #se non c'era il _
                if len(evespl)==1:
                    if eve[len(eve)-1]!='_':
                        evefin=eve+'_1'
                    else:
                        evefin=eve+'1'
                else:
                    evefin=''
                    val=evespl[len(evespl)-1]
                    print 'val',val
                    if val.isdigit():
                        for i in range(0,len(evespl)-1):
                            print 'evespl[i]',evespl[i]
                            evefin+=evespl[i]+'_'
                        #incremento il valore di 1
                        evefin+=str(int(val)+1)
                    else:
                        if eve[len(eve)-1]!='_':
                            evefin=eve+'_1'
                        else:
                            evefin=eve+'1'
                return {'event':evefin}'''
        except Exception,e:
            print 'err',e
            return {"data":'errore'}
        
#serve nelle aliquote da trasferire per vedere se il genealogy id dell'aliquota,
#introdotto dall'utente, esiste o meno nel DB e se l'aliquota non
#e' gia' stata programmata per il trasferimento      
class TransferAliquotHandler(BaseHandler):
    allowed_methods = ('GET')
    @method_decorator(get_functionality_decorator)
    def read(self, request,genbarc):
        try:  
            diz=AllAliquotsContainer(genbarc)
            lista=diz[genbarc]
            if len(lista)==0:
                return{'data':'inesistente'}
            
            #e' una lista in cui ogni valore e' una stringa formata da gen|barcode|posizione
            for val in lista:
                ch=val.split('|')
                
                #per controllare se l'aliquota e' di questo wg        
                lisal=Aliquot.objects.filter(uniqueGenealogyID=ch[0],availability=1)
                if len(lisal)==0:
                    return{'data':'inesistente'}
                else:                    
                    al=lisal[0]
                
                #vedo se l'aliquota e' gia' stata programmata per il trasferimento
                listatrasf=Transfer.objects.filter(deliveryExecuted=0,deleteTimestamp=None,deleteOperator=None)
                altrasfsched=AliquotTransferSchedule.objects.filter(idAliquot=al,idTransfer__in=listatrasf)
                print 'altrasfsched',altrasfsched
                if(altrasfsched.count()!=0):
                    return {'data':'presente'}

            return {'data':lista}
            
        except Exception,e:
            print 'err',e
            return {"data":'errore'}
        
#Dato una serie di container concatenati da & mi da' la lista delle provette contenute
class TransferListBarcodeHandler(BaseHandler):
    allowed_methods = ('POST')
    @method_decorator(get_functionality_decorator)
    def create(self, request):
        try:
            barcode=request.POST.get('lbarc')
            print 'barcode',barcode
            indir=Urls.objects.get(default=1).url
            barc=barcode.replace('#','%23')
            barc=barc.replace(' ','%20')
            values = {'lbarc' : barcode}
            url=indir+'/api/check/listcontainer/'
            r =requests.post(url, data=values, verify=False, headers={"workingGroups" : get_WG_string()})
            #u = urllib2.urlopen(indir+"/api/check/listcontainer/"+barc)
            #data = json.loads(u.read())
            print 'data',json.loads(r.text)
            
            return {'data':json.loads(r.text)}
            
        except Exception,e:
            print 'err',e
            return {"data":'errore'}
        
#mi restituisce tutti i genid con i loro codici. Serve per popolare la tabella aliquote dello storage
class AllAliquotsHandler(BaseHandler):
    allowed_methods = ('GET')
    @method_decorator(get_functionality_decorator)
    def read(self, request):
        try:
            lisdiz=[]
            lisaliq=Aliquot.objects.all()
            for al in lisaliq:
                diz={}
                diz['gen']=al.uniqueGenealogyID
                diz['barcode']=al.barcodeID
                diz['startdate']=str(al.idSamplingEvent.samplingDate)
                diz['startoperator']=al.idSamplingEvent.idSerie.operator
                diz['avail']=al.availability
                lisdiz.append(diz)
            #print 'lisdiz',json.dumps(lisdiz)
            return lisdiz
        except Exception,e:
            print 'err',e
            return {"data":'errore'}

#serve per la procedura che avverte l'utente che deve archiviare dei campioni fatti una settimana fa
class ArchiveAliquotsHandler(BaseHandler):
    allowed_methods = ('GET')
    @method_decorator(get_functionality_decorator)
    def read(self, request):
        try:
            dizgen={}
            #oggi=datetime.datetime.now()
            oggi=timezone.localtime(timezone.now())
            #datalimite=oggi-relativedelta(days=7)
            datalimite=oggi-timezone.timedelta(days = 7)
            #prendo tutti i samplingevent fatti dopo il 1-11-2013 per togliere tutti i campioni storici che non 
            #hanno una data di archiviazione e che quindi potrebbero trarre in inganno
            print 'limite',datalimite
            listasamp=SamplingEvent.objects.filter(samplingDate__gte='2013-11-01',samplingDate__lte=datalimite)
            print 'listasamp',listasamp
            for samp in listasamp:
                operator=samp.idSerie.operator
                lisaliq1=Aliquot.objects.filter(availability=1, idSamplingEvent=samp,archiveDate=None)
                lisaliq=lisaliq1.exclude(barcodeID__istartswith='Diatech')
                if dizgen.has_key(operator):
                    lista=dizgen[operator]
                else:
                    lista=[]
                for al in lisaliq:
                    lista.append(al.uniqueGenealogyID+'|'+str(samp.samplingDate))
                if len(lista)!=0:
                    dizgen[operator]=lista
            print 'dizgen',dizgen
            return dizgen
        except Exception,e:
            print 'err',e
            return {"data":'errore'}
    
#per l'autocompletamento del nome delle linee cellulari
class CellAutocompleteHandler(BaseHandler):
    allowed_methods = ('GET')
    @method_decorator(get_functionality_decorator)
    def read(self, request):
        try:
            if 'term' in request.GET:  
                nomelinea=request.GET['term']
                #devo fare la chiamata al modulo per vedere se la linea e' gia' presente o no
                servizio=WebService.objects.get(name='Annotation')
                urlcell=Urls.objects.get(idWebService=servizio).url
                #faccio la get al modulo dandogli la lista con dentro i dizionari
                indir=urlcell+'/api/cellLineFromName/?name='+nomelinea
                req = urllib2.Request(indir, headers={"workingGroups" : get_WG_string()})
                u = urllib2.urlopen(req)
                
                da = u.read()
                data=json.loads(da)
                print 'data',data
                res=[]
                if len(data)!=0:
                    for val in data:
                        p = {'id':val['id'], 'label':val['name'] ,'value':val['name']}
                        res.append(p)
                return res
            return []
        except Exception,e:
            print 'err',e
            return 'errore'
        
#serve per le linee, nel caso di un cambio di sorgente ho bisogno di un nuovo caso
class CellNewCaseHandler(BaseHandler):
    allowed_methods = ('GET')
    @method_decorator(get_functionality_decorator)
    def read(self, request,tumor,sorg,cell,numero,crea):
        try:
            #devo prima guardare se esiste gia' una collezione per quella linea con quella sorgente
            #perche' puo' capitare che ci siano gia' piu' collezioni della stessa linea, ma con diverse sorgenti
            #e quindi non devo creare un caso nuovo, ma prendere quello gia' usato
            feat=ClinicalFeature.objects.get(name='idCellLine')
            lisfeat=CollectionClinicalFeature.objects.filter(idClinicalFeature=feat,value=cell)
            print 'lisfeat',lisfeat
            print 'crea',crea
            trovato=False
            for f in lisfeat:
                print 'idSource',f.idCollection.idSource.id
                print 'sorg',sorg
                if f.idCollection.idSource.id==int(sorg):
                    trovato=True
                    caso=f.idCollection.itemCode
                    print 'caso',caso
                    return {'caso':caso,'nuovo':False}
            #mi faccio dare un caso nuovo pero' solo alla prima chiamata
            if not trovato and crea!='false':
                if numero=='True':
                    casuale=False
                else:
                    casuale=True
                tumore=CollectionType.objects.get(id=tumor)
                val=LasHubNewCase(request, casuale, tumore.abbreviation)
                caso=NewCase(val, casuale, tumore)
            else:
                caso=''
            return {'caso':caso,'nuovo':True}
        except Exception,e:
            print 'err',e
            return {"data":'errore'}
        
#per salvare le aliquote vitali che arrivano dal modulo delle linee cellulari
#in caso di espansione, non di archiviazione perche' per quello c'e' SaveExplants
class SaveCellHandler(BaseHandler):
    allowed_methods = ('POST')
    @transaction.commit_on_success
    @method_decorator(get_functionality_decorator)
    def create(self, request):
        try:
            listaal=[]
            lisbarclashub=[]
            print request.POST
            pezziusati=0
            disponibile=1
            derivato=0
            
            lgenid=json.loads(request.POST.get('genIDList'))
            print 'lgenid',lgenid
            #mi da' l'operatore che ha fatto l'azione
            operatore=request.POST.get('user')
            dataoggi=date.today()
            ser,creato=Serie.objects.get_or_create(operator=operatore,
                                                   serieDate=dataoggi)
            
            sorg=Source.objects.get(Q(name='cellline')&Q(type='Las'))

            tipoaliq='VT'
            numpezzi=1
            for gen in lgenid:
                genid=gen
                
                print 'gen',genid
                
                g = GenealogyID(genid)
                #tumore=genid[0:3]
                tumore=g.getOrigin()
                print 'tumore',tumore
                #caso=genid[3:7]
                caso=g.getCaseCode()
                print 'caso',caso
                tipotum=CollectionType.objects.get(abbreviation=tumore)
                print 'tipotum',tipotum
                #prendo la collezione da associare al sampling event
                colle=Collection.objects.get(itemCode=caso,idCollectionType=tipotum)
                
                #t=genid[7:9]
                t=g.getTissue()
                tessuto_esp=TissueType.objects.get(abbreviation=t)
                print 'tessuto',tessuto_esp.id
                
                #salvo il campionamento
                campionamento,creato=SamplingEvent.objects.get_or_create(idTissueType=tessuto_esp,
                                             idCollection=colle,
                                             idSource=sorg,
                                             idSerie=ser,
                                             samplingDate=dataoggi)
                print 'camp',campionamento
                
                barcode=gen
                
                lisbarclashub.append(barcode)
                    
                ffpe='true'
                valori=genid+',,,'+str(numpezzi)+','+barcode+','+tipoaliq+','+ffpe+',,,,,,'+str(dataoggi)
                
                tipoaliquota= AliquotType.objects.get(abbreviation=tipoaliq)
                print 'tipo aliquota',tipoaliq
                a=Aliquot(barcodeID=barcode,
                       uniqueGenealogyID=str(genid),
                       idSamplingEvent=campionamento,
                       idAliquotType=tipoaliquota,
                       timesUsed=pezziusati,
                       availability=disponibile,
                       derived=derivato,
                       archiveDate=dataoggi)
                print 'a',a
                
                disable_graph()
                a.save()
                enable_graph()
                
                listaal.append(valori)
                print 'listaaliq',listaal

                #salvo il numero di pezzi
                '''fea=Feature.objects.get(Q(idAliquotType=tipoaliquota)&Q(name='NumberOfPieces'))
                aliqfeature=AliquotFeature(idAliquot=a,
                                           idFeature=fea,
                                           value=-1)
                aliqfeature.save()
                print 'aliq',aliqfeature'''
                                
            #chiamo la API dello storage per fare in modo di predisporre i container nel LASHUB, senza finalizzarli
            url1 = Urls.objects.get(default = '1').url + '/api/check/presence/'
            val1={'lista':json.dumps(lisbarclashub),'salva':True}
            print 'url1',url1
            data = urllib.urlencode(val1)
            req = urllib2.Request(url1,data=data, headers={"workingGroups" : get_WG_string()})
            u = urllib2.urlopen(req)
            re = json.loads(u.read())
            print 're',re
            res=re['data']
            print 'res',res
            if res!='ok':
                raise Exception('problemi con LASHub')
            
            #address=request.get_host()+settings.HOST_URL
            request,errore=SalvaInStorage(listaal,request)
            print 'err', errore   
            if errore==True:
                raise Exception
            
            #comunico al LASHub che quei barcode sono stati utilizzati            
            #prefisso= 'https://' if settings.LAS_AUTH_USE_HTTPS else 'http://'
            #indir=prefisso+address
            indir=settings.DOMAIN_URL+settings.HOST_URL
            url = indir + '/clientHUB/saveAndFinalize/'
            print 'url',url
            values = {'typeO' : 'container', 'listO': str(lisbarclashub)}
            requests.post(url, data=values, verify=False, headers={"workingGroups" : get_WG_string()})
        
            return 'ok'
            
        except Exception,e:
            print 'errore',e
            transaction.rollback()
            return 'err'
        
#Per la procedura automatica di riposizionamento delle provette. Per ogni container restituisce la
#procedura per cui e' stata utilizzata l'aliquota e il genid
class ReturnContainerHandler(BaseHandler):
    allowed_methods = ('POST')
    @method_decorator(get_functionality_decorator)
    def create(self, request):
        try:
            print request.POST
            disable_graph()
            dizgen={}
            lista=json.loads(request.POST.get('lista'))
            #ho la lista con tutti i gen
            for gen in lista:
                lisdate=[]
                #lista che contiene le procedure pianificate ma non ancora eseguite e in questo caso distinguo solo tra derivazione ed esperimenti
                lisplan=[]
                print 'gen',gen
                aliq=Aliquot.objects.filter(uniqueGenealogyID=gen,availability=1)
                print 'aliq',aliq
                if len(aliq)!=0:
                    #guardo le derivazioni
                    lisder=AliquotDerivationSchedule.objects.filter(idAliquot=aliq,deleteTimestamp=None).order_by('-initialDate')
                    print 'lisder',lisder
                    #in lisder[0] ho la data piu' recente
                    if len(lisder)!=0:
                        datader=lisder[0].initialDate
                        if datader!=None:
                            lisdate.append(datader)
                        else:
                            dataplander=lisder[0].idDerivationSchedule.scheduleDate
                            lisplan.append(lisder[0].idDerivationSchedule.scheduleDate)
                    lisexp=AliquotExperiment.objects.filter(idAliquot=aliq,deleteTimestamp=None).order_by('-experimentDate')
                    print 'lisexp',lisexp
                    if len(lisexp)!=0:
                        dataexp=lisexp[0].experimentDate
                        if dataexp!=None:
                            lisdate.append(dataexp)
                        else:
                            dataplanexp=lisexp[0].idExperimentSchedule.scheduleDate
                            lisplan.append(lisexp[0].idExperimentSchedule.scheduleDate)
                    lispos=AliquotPositionSchedule.objects.filter(idAliquot=aliq,deleteTimestamp=None).order_by('-idPositionSchedule')
                    print 'lispos',lispos
                    if len(lispos)!=0:
                        datapos=lispos[0].idPositionSchedule.scheduleDate
                        print 'datapos',datapos
                        if datapos!=None:
                            lisdate.append(datapos)
                    lisqual=AliquotQualitySchedule.objects.filter(idAliquot=aliq,deleteTimestamp=None).order_by('-idQualitySchedule')
                    print 'lisqual',lisqual
                    if len(lisqual)!=0:
                        dataqual=lisqual[0].idQualitySchedule.scheduleDate
                        if dataqual!=None:
                            lisdate.append(dataqual)
                    lissplit=AliquotSplitSchedule.objects.filter(idAliquot=aliq,deleteTimestamp=None).order_by('-idSplitSchedule')
                    print 'lissplit',lissplit
                    if len(lissplit)!=0:
                        datasplit=lissplit[0].idSplitSchedule.scheduleDate
                        if datasplit!=None:
                            lisdate.append(datasplit)                    
                    lislabel=AliquotLabelSchedule.objects.filter(idSamplingEvent=aliq[0].idSamplingEvent,deleteTimestamp=None).order_by('-idLabelSchedule')
                    print 'lislabel',lislabel
                    if len(lislabel)!=0:
                        datalabel=lislabel[0].idLabelSchedule.scheduleDate
                        if datalabel!=None:
                            lisdate.append(datalabel)
                    proc=''
                    datafin=''
                    procplan=''
                    dataplan=''                    
                    print 'lisdate',lisdate
                    if len(lisdate)!=0:
                        if len(lisder)!=0 and max(lisdate)==datader:
                            proc='Derivation'
                            datafin=datader
                        elif len(lisexp)!=0 and max(lisdate)==dataexp:
                            proc=lisexp[0].idExperiment.name
                            datafin=dataexp
                        elif len(lispos)!=0 and max(lisdate)==datapos:
                            proc='Retrieving'
                            datafin=datapos
                        elif len(lisqual)!=0 and max(lisdate)==dataqual:
                            proc='Revaluation'
                            datafin=dataqual
                        elif len(lissplit)!=0 and max(lisdate)==datasplit:
                            proc='Splitting'
                            datafin=datasplit
                        elif len(lislabel)!=0 and max(lisdate)==datalabel:
                            proc='Labelling'
                            datafin=datalabel
                    print 'lisplan',lisplan
                    if len(lisplan)!=0:
                        if len(lisder)!=0 and max(lisplan)==dataplander:
                            procplan='Derivation'
                            dataplan=dataplander
                        elif len(lisexp)!=0 and max(lisplan)==dataplanexp:
                            procplan=lisexp[0].idExperiment.name
                            dataplan=dataplanexp
                        else:
                            procplan=proc
                            dataplan=datafin
                        
                    dizgen[gen]={'procedure':proc,'data':str(datafin),'procplan':procplan,'dataplan':str(dataplan)}
                else:
                    dizgen[gen]={'procedure':'','data':'','procplan':'','dataplan':''}
            print 'dizgen',dizgen
            return {'data':json.dumps(dizgen)}
        
        except Exception, e:
            print 'ecc',e
            return {'data':'errore'}
        
#data una lista di gen restituisco le info legate a quelle aliquote
class InfoAliqHandler(BaseHandler):
    allowed_methods = ('POST')
    @method_decorator(get_functionality_decorator)
    def create(self, request):
        try:
            diztot={}
            lisgen = ast.literal_eval(request.POST.get('lisgen'))
            print 'lisgen',lisgen
            lisaliq=Aliquot.objects.filter(uniqueGenealogyID__in=lisgen,availability=1)
            for al in lisaliq:
                diztemp={}
                diztemp['data']=str(al.idSamplingEvent.samplingDate)
                diztemp['operator']=al.idSamplingEvent.idSerie.operator
                diztemp['tipoaliq']=al.idAliquotType.abbreviation
                diztot[al.uniqueGenealogyID]=diztemp
            print 'diztot',diztot
            return {'data':json.dumps(diztot)}
        except Exception,e:
            print 'errore',e            
            return 'err'

#data una lista di barc mi restituisce il gen. Non funziona piu' nella logica nuova perche' la biobanca non ha piu' il barcode
class AliqDataHandler(BaseHandler):
    allowed_methods = ('POST')
    @method_decorator(get_functionality_decorator)
    def create(self, request):
        try:
            diztot={}
            dizbarc = ast.literal_eval(request.POST.get('dizbarc'))
            print 'dizbarc',dizbarc
            for key,val in dizbarc.items():
                #key e' il barc|pos, val la pos
                barcfin=key.split('|')
                barc=barcfin[0]
                if val!='-':
                    barc=barcfin[0]+val
                print 'barc',barc                    
                lisaliq=Aliquot.objects.filter(barcodeID=barc,availability=1)
                print 'lisaliq',lisaliq
                if len(lisaliq)!=0:
                    al=lisaliq[0]
                    print 'al',al
                    diztot[al.uniqueGenealogyID]=key
                else:
                    print 'laliq',lisaliq
                    return {'data':json.dumps({'res':'err','data':{'barcode':key,'err':'empty'}})}
            print 'diztot',diztot
            return {'data':json.dumps(diztot)}
        except Exception,e:
            print 'errore',e            
            return 'err'
        
#per salvare gli espianti da file
class BatchExplantHandler(BaseHandler):
    allowed_methods = ('POST')
    @transaction.commit_on_success
    @method_decorator(get_functionality_decorator)
    def create(self, request):
        try:
            if request.method=='POST':
                listaal=[]
                lisbarclashub=[]
                print request.POST
                pezziusati=0
                disponibile=1
                derivato=0
                lisbarc=[]
                #dizionario con chiave il barc e valore piastra|posizione|tipoaliq
                dizprovette={}
                #mi da' l'operatore che ha fatto l'espianto
                operatore=request.POST.get('operator')
                data_gen=request.POST.get('date')
                listaaliq=json.loads(request.POST.get('explants'))
                
                #devo fare prima tutti i controlli di coerenza sulle provette
                for tipialiq in listaaliq:
                    for topi in listaaliq[tipialiq]:
                        for barc in listaaliq[tipialiq][topi]:
                            for prov in listaaliq[tipialiq][topi][barc]:
                                genid=prov['genID']
                                tipoaliq=tipialiq
                                piastra=barc
                                pos=prov['pos']
                                numpezzi=prov['qty']
                                print 'gen',genid
                                print 'tipoaliq',tipoaliq
                                print 'piastra',piastra
                                print 'pos',pos
                                print 'numpezzi',numpezzi
                                
                                #se sto trattando vitale, rna e snap
                                if(tipoaliq!='FF')and(tipoaliq!='OF')and(tipoaliq!='CH'):
                                    barcodepiastraurl=piastra.replace('#','%23')
                                    url = Urls.objects.get(default = '1').url + "/api/container/"+barcodepiastraurl
                                    try:
                                        #prendo i dati dall'archivio che mi da' la posizione e il barcode delle aliq
                                        req = urllib2.Request(url, headers={"workingGroups" : get_WG_string()})
                                        u = urllib2.urlopen(req)
                                        res =  u.read()
                                        #print res
                                        data = json.loads(res)
                                        #print 'data',data
                                    except Exception, e:
                                        print 'e',e
                                    
                                    #se la API mi restituisce dei valori perche' gli ho dato un codice
                                    #corretto per la piastra    
                                    if 'children' in data:    
                                        #per ottenere il barcode data la posizione
                                        barcode=''
                                        for w in data['children']:
                                            if w['position']==pos:
                                                barcode=w['barcode']
                                                print 'barc',barcode
                                                break;
                                        if barcode=='':
                                            return {'res':'err','data':'Error: '+piastra+' has not a tube in position '+pos}
                                        #da commentare poi
                                        #guardo se c'e' gia' un campione dentro quella provetta
                                        #lisaliq=Aliquot.objects.filter(barcodeID=barcode,availability=1)
                                        #if len(lisaliq)!=0:
                                        #    return json.dumps({'res':'err','data':'Error: position '+pos+' in container '+piastra+' is full'})
                                        dizprovette[barcode]=piastra+'|'+pos+'|'+tipoaliq
                                    else:
                                        #vuol dire che sto salvando una nuova provetta e quindi il barcode 
                                        #risulta essere cio' che e' salvato nella variabile piastra
                                        if piastra in lisbarc:
                                            #per togliere i barcode duplicati all'interno del file 
                                            return {'res':'err','data':'Error: '+piastra+' is already present in file'}
                                        else:
                                            lisbarc.append(piastra)
                                #se ho ffpe o of o ch o pl o px il barcode ce l'ho gia' e non devo andare a leggerlo
                                #il barcode e' salvato nella variabile piastra
                                else:
                                    if piastra in lisbarc:
                                        #per togliere i barcode duplicati all'interno del file
                                        return {'res':'err','data':'Error: '+piastra+' is already present in file'}
                                    else:           
                                        lisbarc.append(piastra)
                                    
                #devo vedere se i barcode sono univoci
                print 'lisbarc',lisbarc
                print 'dizprovette',dizprovette
                #faccio una richiesta allo storage per vedere se questi barc esistono gia'
                url1 = Urls.objects.get(default = '1').url + '/api/check/presence/'
                val1={'lista':json.dumps(lisbarc),'dizprov':json.dumps(dizprovette),'explants':True}
                print 'url1',url1
                data = urllib.urlencode(val1)
                req = urllib2.Request(url1,data=data, headers={"workingGroups" : get_WG_string()})
                u = urllib2.urlopen(req)
                #u = urllib2.urlopen(url1, data)
                re = json.loads( u.read())
                print 're',re
                res=re['data']
                print 'res',res
                #mi faccio dare dalla API la risposta gia' confezionata
                if res!='ok':
                    return {'res':'err','data':res}
                                
                if 'source' in request.POST:
                    sorg=Source.objects.get(Q(name='cellline')&Q(type='Las'))
                else:
                    #prendo la sorgente, che e' caxeno, dalla tabella source
                    sorg=Source.objects.get(name='caxeno')
                              
                for tipialiq in listaaliq:
                    for topi in listaaliq[tipialiq]:
                        for barc in listaaliq[tipialiq][topi]:
                            for prov in listaaliq[tipialiq][topi][barc]:
                                genid=prov['genID']
                                tipoaliq=tipialiq
                                piastra=barc
                                pos=prov['pos']
                                numpezzi=prov['qty']
                                print 'gen',genid
                                print 'tipoaliq',tipoaliq
                                print 'piastra',piastra
                                print 'pos',pos
                                print 'numpezzi',numpezzi
                                
                                g = GenealogyID(genid)
                                #tumore=genid[0:3]
                                tumore=g.getOrigin()
                                print 'tumore',tumore
                                #caso=genid[3:7]
                                caso=g.getCaseCode()
                                print 'caso',caso
                                tipotum=CollectionType.objects.get(abbreviation=tumore)
                                print 'tipotum',tipotum
                                #prendo la collezione da associare al sampling event
                                colle=Collection.objects.get(Q(itemCode=caso)&Q(idCollectionType=tipotum))
                                
                                #t=genid[7:9]
                                t=g.getTissue()
                                tessuto_esp=TissueType.objects.get(abbreviation=t)
                                print 'tessuto',tessuto_esp.id
                                print 'prov',prov
                                if 'date_expl' in prov:
                                    data_expl=prov['date_expl']
                                else:
                                    data_expl=data_gen
                                print 'data expl',data_expl
                                #salvo la serie
                                ser,creato=Serie.objects.get_or_create(operator=operatore,
                                                                       serieDate=data_expl)
                                
                                #salvo il campionamento
                                campionamento,creato=SamplingEvent.objects.get_or_create(idTissueType=tessuto_esp,
                                                             idCollection=colle,
                                                             idSource=sorg,
                                                             idSerie=ser,
                                                             samplingDate=data_expl)
                                print 'camp',campionamento
                                
                                barcode=None
                                #se sto trattando vitale, rna e snap
                                if(tipoaliq!='FF')and(tipoaliq!='OF')and(tipoaliq!='CH'):
                                    barcodepiastraurl=piastra.replace('#','%23')
                                    url = Urls.objects.get(default = '1').url + "/api/container/"+barcodepiastraurl
                                    try:
                                        #prendo i dati dall'archivio che mi da' la posizione e il barcode delle aliq
                                        req = urllib2.Request(url, headers={"workingGroups" : get_WG_string()})
                                        u = urllib2.urlopen(req)
                                        #u = urllib2.urlopen(url)
                                        res =  u.read()
                                        #print res
                                        data = json.loads(res)
                                        #print 'data',data
                                    except Exception, e:
                                        print 'e',e
                                    
                                    #se la API mi restituisce dei valori perche' gli ho dato un codice
                                    #corretto per la piastra    
                                    if 'children' in data:    
                                        #per ottenere il barcode data la posizione    
                                        for w in data['children']:
                                            if w['position']==pos:
                                                barcode=w['barcode']
                                                print 'barc',barcode
                                                break;
                                        ffpe='false'
                                    else:
                                        #vuol dire che sto salvando una nuova provetta e quindi il barcode 
                                        #risulta essere cio' che e' salvato nella variabile piastra
                                        barcode=piastra
                                        piastra=''
                                        pos=''
                                        ffpe='true'
                                        lisbarclashub.append(barcode)
                                    #valori=str(genid)+','+str(piastra)+','+str(pos)+','+str(numpezzi)+','+barcode+','+tipoaliq+',false, , '
                                #se ho ffpe o of o ch o pl o px il barcode ce l'ho gia' e non devo andare a leggerlo
                                #il barcode e' salvato nella variabile piastra
                                else:
                                    barcode=piastra
                                    piastra=''
                                    pos=''
                                    ffpe='true'
                                    lisbarclashub.append(barcode)
                                                                        
                                if numpezzi=='-':
                                    numpezzi=''
                                
                                valori=genid+','+str(piastra)+','+str(pos)+','+str(numpezzi)+','+barcode+','+tipoaliq+','+ffpe+',,,,,,'+str(data_expl)
                                
                                tipoaliquota= AliquotType.objects.get(abbreviation=tipoaliq)
                                print 'tipo aliquota',tipoaliq
                                a=Aliquot(barcodeID=barcode,
                                       uniqueGenealogyID=str(genid),
                                       idSamplingEvent=campionamento,
                                       idAliquotType=tipoaliquota,
                                       timesUsed=pezziusati,
                                       availability=disponibile,
                                       derived=derivato)
                                print 'a',a
                                
                                disable_graph()
                                a.save()
                                enable_graph()
    
                                
                                listaal.append(valori)
                                print 'listaaliq',listaal
                                
                                #salvo il numero di pezzi solo se ci sono
                                if numpezzi!='':
                                    fea=Feature.objects.get(Q(idAliquotType=tipoaliquota)&Q(name='NumberOfPieces'))
                                    aliqfeature=AliquotFeature(idAliquot=a,
                                                               idFeature=fea,
                                                               value=numpezzi)
                                    aliqfeature.save()
                                    print 'aliq',aliqfeature
                
                #address=request.get_host()+settings.HOST_URL
                #per controllare se nel lashub esistono gia' questi barc
                print 'lisbarc',lisbarclashub
                if len(lisbarclashub)!=0:
                    #faccio una richiesta allo storage per vedere se questi barc esistono gia'
                    url1 = Urls.objects.get(default = '1').url + '/api/check/presence/'
                    val1={'lista':json.dumps(lisbarclashub),'salva':True}
                    print 'url1',url1
                    data = urllib.urlencode(val1)
                    req = urllib2.Request(url1,data=data, headers={"workingGroups" : get_WG_string()})
                    u = urllib2.urlopen(req)
                    #u = urllib2.urlopen(url1, data)
                    re = json.loads(u.read())
                    print 're',re
                    res=re['data']
                    print 'res',res
                    if res!='ok':
                        return {'res':'err','data':'Error: barcode '+res+' already exists'}
                
                request=SalvaInStorage(listaal,request)
                
                #comunico al LASHub che quei barcode sono stati utilizzati
                #prefisso= 'https://' if settings.LAS_AUTH_USE_HTTPS else 'http://'
                #indir=prefisso+address
                '''indir=settings.DOMAIN_URL+settings.HOST_URL
                url = indir + '/clientHUB/saveAndFinalize/'
                print 'url',url
                values = {'typeO' : 'container', 'listO': str(lisbarclashub)}
                requests.post(url, data=values, verify=False, headers={"workingGroups" : get_WG_string()})'''
            return {'res':'ok'}
        except Exception,e:
            print 'errore',e
            transaction.rollback()        
            return {'res':'err','data':e}

#serve nella preparazione dei vetrini per vedere se il genealogy id dell'aliquota,
#introdotto dall'utente, esiste o meno nel DB, se e' del tipo giusto e se l'aliquota non
#e' gia' stata programmata per i vetrini      
class SlideAliquotHandler(BaseHandler):
    allowed_methods = ('GET')
    @method_decorator(get_functionality_decorator)
    def read(self, request,gen):
        try:
            
            diz=AllAliquotsContainer(gen)
            lista=diz[gen]
            if len(lista)==0:
                return{'data':'inesistente'}
            
            #prendo tutti gli aliquot type da cui si puo' partire per creare delle fette (in genere FF e OF) 
            ltrasf=TransformationSlide.objects.all()
            listapartenza=[]
            for tr in ltrasf:
                listapartenza.append(tr.idTransformationChange.idFromType.abbreviation)
            print 'lista partenza',listapartenza
            
            #e' una lista in cui ogni valore e' una stringa formata da gen|barcode|posizione
            for val in lista:
                ch=val.split('|')
                #per controllare se l'aliquota e' di questo wg        
                lisal=Aliquot.objects.filter(uniqueGenealogyID=ch[0],availability=1)
                if len(lisal)==0:
                    return{'data':'inesistente'}
                else:                    
                    al=lisal[0]
                #vedo se l'aliquota e' gia' stata programmata per la procedura
                aldersched=AliquotSlideSchedule.objects.filter(idAliquot=al,executed=0,deleteTimestamp=None)
                print 'alqual',aldersched
                if(aldersched.count()!=0):
                    return {'data':'presente'}
                
                #devo vedere se l'aliq puo' essere pianificata per essere tagliata                
                if al.idAliquotType.abbreviation not in listapartenza:
                    return {'data':'tipoerr'}

            return {'data':lista}
        except Exception,e:
            print 'errore',e
            return {"data":'errore'}
        
#dato l'id del protocollo dei vetrini, mi da' l'abbreviazione del tipo di aliq in ingresso
class SlideProtocolHandler(BaseHandler):
    allowed_methods = ('GET')
    @method_decorator(get_functionality_decorator)
    def read(self, request,prot):
        try:
            lista=[]
            pro=int(prot)
            listatipi=TransformationSlide.objects.filter(idSlideProtocol=pro)
            print 'listatipi',listatipi
            #devo sapere quali tipi di aliq sono selezionabili come ingresso del prot
            for tip in listatipi:
                tipoal=tip.idTransformationChange.idFromType.abbreviation
                if tipoal not in lista:
                    lista.append(tipoal)       
            return {'tipi':lista}
        except Exception, e:
            print 'err',e
            return {"data": 'errore'}

#Serve per caricare un vetrino che non esiste
class SlideLoadHandler(BaseHandler):
    allowed_methods = ('GET')
    @method_decorator(get_functionality_decorator)
    def read(self, request, barcode,aliquot,tipocont,pezzi):
        try:
            print 'barcode',barcode
            try:
                address = Urls.objects.get(default = '1').url
                barc=barcode.replace('#','%23')
                req = urllib2.Request(address+"/api/biocassette/"+barc+"/"+aliquot, headers={"workingGroups" : get_WG_string()})
                u = urllib2.urlopen(req)
                data = json.loads(u.read())
                print 'data',data
                if data['data']!='ok':
                    return data
            except Exception, e:
                print 'e',e
                return {'data':'errore_store'}
            print 'aliquot',aliquot
            tipocont=tipocont.replace(' ','%20')
            req = urllib2.Request(address+"/api/containertype/info/"+tipocont+"/"+pezzi+"/", headers={"workingGroups" : get_WG_string()})
            u = urllib2.urlopen(req)
            data = json.loads(u.read())
            print 'data2',data
            if data['data']=='tipo':
                return {'data':'errore_cont'}
            if data['data']=='errore':
                return {'data':'errore_store'}
            
            abbr = 's'
            name = 'rna'
            if aliquot=='PS':
                long_name = 'PARAFFIN SECTION'
            elif aliquot=='OS':
                long_name = 'OCT SECTION'
            else:
                long_name = aliquot
            print 'long_name',long_name 
            
            geom=data['data']
            print 'geom',geom
            regole=json.loads(geom['regole'])
            print 'regole',regole
            
            dim = regole['dimension']
            x = int(dim[0])
            y = int(dim[1])
            print 'x',x
            print 'y',y
            codeList = []
            i = 0
            j = 0
            while i < int(y):
                codeList.append([])
                j = 0
                while j < int(x):
                    #calcolo l'id del tasto
                    id_position=chr(i+ord('A'))+str(j+1)
                    for items in regole['items']:
                        valj=int(items['position'][0])-1
                        vali=int(items['position'][1])-1
                        if valj==int(j) and vali==int(i):
                            id_position=items['id']
                            break
                    idtasto=abbr+'-'+id_position
                    barc=barcode+'|'+id_position
                    codeList[i].append('<td id="'+ idtasto +'" align="center"><button type="submit" align="center" id="'+ idtasto +'" barcode="'+barc+'" pos="'+id_position+'" >0</button></td>')
                    j = j + 1
                i = i + 1    
            
            string=''
            #lun e' il numero di colonne che l'intestazione della tabella deve coprire
            lun=int(dim[0])+1
            row_label = regole['row_label']
            column_label = regole['column_label']
            
            string += '<table align="center" id="' + str(name) + '" plate="'+ barcode+ '" ><tbody><tr><th colspan="' + str(lun) + '">' + str(long_name) + '</th></tr>'
            string += '<tr>'
            string += '<td class="intest"></td>'
            for c in column_label:
                string += '<td align="center" class="intest"><strong>' + str(c) + '</strong></td>'
            string += '</tr>'
            i = 0
            for code in codeList:
                string += '<tr>'
                string += '<td align="center" class="intest"><strong>' + str(row_label[i]) + '</strong></td>'
                for c in code:
                    if c != "":
                        string += c
                string += '</tr>'
                i = i +1
            string += "</tbody></table>"
            return {'data':string}
        except Exception,e:
            print 'err',e
            return {"data":'errore'}

#serve a restituire tutti i genid delle aliquote da dividere create in una certa sessione
class SlideFinalSessionHandler(BaseHandler):
    allowed_methods = ('GET')
    @method_decorator(get_functionality_decorator)
    def read(self, request):
        try:
            lista=request.session.get('aliquotevetrini')
            print 'lista',lista
            ris=''
            for i in range(0,len(lista)):
                if lista[i].executed==1:
                    #prendo le aliquote con quel sampling event
                    lis_aliquote=Aliquot.objects.filter(idSamplingEvent=lista[i].idSamplingEvent.id)
                    for aliq in lis_aliquote:
                        ris+=aliq.uniqueGenealogyID+':'+str(i+1)+'|'
            print 'ris',ris
            return {"data": ris}
        except Exception, e:
            print 'err',e
            return {"data": 'errore'}

#restituisce i parametri clinici legati ad un certo tipo di categoria dato il tumore e 
#dato il nome della categoria madre 
class GetClinicalFeatureHandler(BaseHandler):
    allowed_methods = ('GET')
    @method_decorator(get_functionality_decorator)
    def read(self, request, idfeat, idtumore):
        try:
            listot=[]
            tum=CollectionType.objects.get(id=idtumore)
            clinfeat=ClinicalFeature.objects.get(id=idfeat)
            print 'clinfeat',clinfeat
            lisfeat=ClinicalFeature.objects.filter(idClinicalFeature=clinfeat).order_by('name')
            print 'lisfeat',lisfeat
            #per sapere se restituisco un'altra lista di feature madri o sono arrivato alle foglie
            listamadri=False
            livello=str(int(clinfeat.type[5:])+1) 
            for f in lisfeat:
                diztemp={}
                if f.type.startswith('Level'):
                    #prendo il valore finale di level cosi' so a che livello sono
                    livello=f.type[5:]
                    listamadri=True
                else:
                    diztemp['type']=f.type
                    diztemp['unit']=f.measureUnit
                    #devo creare la lista dei valori possibili
                    valtum=ClinicalFeatureCollectionType.objects.filter(idClinicalFeature=f,idCollectionType=tum).order_by('value')
                    print 'valtum',valtum
                    valnone=ClinicalFeatureCollectionType.objects.filter(idClinicalFeature=f,idCollectionType=None).order_by('value')
                    lisfin=list(chain(valtum,valnone))
                    lis2=[]
                    for elem in lisfin:
                        diz2={}
                        diz2['id']=elem.id
                        diz2['value']=elem.value
                        lis2.append(diz2)
                    diztemp['lisval']=lis2                    
                diztemp['id']=f.id
                diztemp['name']=f.name
                listot.append(diztemp)
            print 'listot',listot
            print 'listamadri',listamadri
            return {'data': json.dumps(listot),'listamadri':listamadri,'livello':livello}
        except Exception, e:
            print 'err',e
            return {'data': 'err'}
        
class GetGenes(BaseHandler):
    allowed_methods = ('GET')
    @method_decorator(get_functionality_decorator)
    def read (self, request, gene):
        resp = retrieveGeneSymbols(gene)
        listGenes = []
        print 'resp',resp
        for k, v in resp.items():
            for gene in v:
                listGenes.append(gene)
        #print 'listGenes',listGenes
        print 'len genes',len(listGenes)
        return listGenes

class GetMutations(BaseHandler):
    allowed_methods = ('GET')
    @method_decorator(get_functionality_decorator)
    def read (self, request, gene):
        response = retrieveMutations(gene)
        print 'len mut',len(response)
        return response

class GetDrugs(BaseHandler):
    allowed_methods = ('GET')
    @method_decorator(get_functionality_decorator)
    def read (self, request):
        lisdrug=[]
        listot=Drug.objects.all().order_by('name')
        for d in listot:
            diztemp={}
            diztemp['name']=d.name
            diztemp['extid']=d.externalId
            lisdrug.append(diztemp)
        print 'lisdrug',lisdrug
        return lisdrug

class GetCollection(BaseHandler):
    allowed_methods = ('POST')
    @method_decorator(get_functionality_decorator)
    def create(self, request):
        try:
            resSet=getMDAMData(request,False)
            if resSet==None:
                resSet={}
            #print 'resSet',resSet  
            
            dizcoll={}
            #non metto availability=true perche' mi interessano le collezioni collegate, non le aliquote
            #resSet ha come chiavi il gen e come valori il barcode
            lisaliq=Aliquot.objects.filter(uniqueGenealogyID__in=resSet.keys())
            for al in lisaliq:
                coll=al.idSamplingEvent.idCollection
                chiave=coll.idCollectionType.abbreviation+coll.itemCode
                if chiave not in dizcoll.keys():
                    diztemp={}
                    diztemp['tum']=coll.idCollectionType.longName
                    diztemp['tumid']=coll.idCollectionType.id
                    diztemp['case']=coll.itemCode
                    diztemp['source']=coll.idSource.name
                    diztemp['sourceid']=coll.idSource.id
                    diztemp['informed']=coll.collectionEvent
                    diztemp['patient']=coll.patientCode
                    if coll.idCollectionProtocol!=None:
                        diztemp['protocol']=coll.idCollectionProtocol.name
                        diztemp['protocolid']=coll.idCollectionProtocol.id
                    else:
                        diztemp['protocol']=''
                        diztemp['protocolid']=''
                    dizcoll[chiave]=diztemp
            print 'dizcoll',dizcoll
            return dizcoll
        except Exception, e:
            print 'err',e
            return {'data': 'err'}

#Restituisce tutte le sorgenti della biobanca e viene chiamata dal modulo clinico per
#creare sul grafo i vari nodi dei centri medici
class GetSources(BaseHandler):
    allowed_methods = ('GET')
    @method_decorator(get_functionality_decorator)
    def read (self, request):
        listot=[]
        
        sorg1=Source.objects.filter(type='Hospital')
        sorg2=Source.objects.filter(type='Mercuric')
        sorg3=Source.objects.filter(type__startswith='Funnel')
        lisfin=list(chain(sorg1,sorg2,sorg3))
        for ll in lisfin:
            diztemp={}
            diztemp['internalName']=ll.internalName
            diztemp['name']=ll.name
            if ll.type[0:6]=='Funnel':
                diztemp['type']='Funnel'
            else:
                diztemp['type']=ll.type
            listot.append(diztemp)
        return listot

#dato un protocollo di collezionamento, chiama il modulo clinico e restituisce la lista
#dei posti collegati
class GetHospital(BaseHandler):
    allowed_methods = ('GET')
    @method_decorator(get_functionality_decorator)
    def read (self, request,prot):
        try:
            #prot e' l'id. Devo passare alla API del modulo clinico il nome interno
            protocollo=CollectionProtocol.objects.get(id=prot)
            #devo fare la chiamata al modulo clinico per avere la lista degli ospedali
            servizio=WebService.objects.get(name='Clinical')
            urlclin=Urls.objects.get(idWebService=servizio).url
            #faccio la get al modulo dandogli la lista con dentro i dizionari
            indir=urlclin+'/coreInstitution/api/institution/'+protocollo.project
            print 'indir',indir
            
            try:
                req = urllib2.Request(indir, headers={"workingGroups" : get_WG_string()})
                u = urllib2.urlopen(req)
            except HTTPError,e:
                print 'code',e.code
                if e.code == 409:   
                    return {"data":[]}
                
            lista = json.loads(u.read())
            print 'lista',lista
            #qui ho la lista di dizionari che rappresentano ciascuno un posto ed hanno delle chiavi
            #con le varie informazioni
            #lista=[{'identifier':'AA','name':'Istituto di Candiolo'}]
            if protocollo.project!='Funnel' and protocollo.project!='Mercuric':                
                lissource=Source.objects.filter(type='Hospital')
            else:
                lissource=Source.objects.filter(type__startswith=protocollo.project)
            lisfin=[]
            for val in lista:
                nomeesteso=val['name']
                nomeinterno=val['identifier']
                #grazie al nome interno vado a prendere il valore dell'id dalla mia tabella
                for s in lissource:
                    if s.internalName==nomeinterno:
                        lisfin.append([str(s.id),nomeesteso])
            print 'lisfin',lisfin
            return {"data":lisfin}
        except Exception,e:
            print 'err',e
            return {"data":'errore'}

class GetGenIDValues(BaseHandler):
    allowed_methods = ('GET')
    @method_decorator(get_functionality_decorator)
    def read (self, request):
        dizfin={}
        listum=list(CollectionType.objects.all().order_by('abbreviation').values_list('abbreviation',flat=True))
        dizfin['tum']=listum
        listess=list(TissueType.objects.all().order_by('abbreviation').values_list('abbreviation',flat=True))
        dizfin['tess']=listess
        lisvector=list(AliquotVector.objects.all().order_by('abbreviation').values_list('abbreviation',flat=True))
        dizfin['vector']=lisvector
        lismousetissue=list(MouseTissueType.objects.all().order_by('abbreviation').values_list('abbreviation',flat=True))
        dizfin['mousetess']=lismousetissue
        listipialiq=list(AliquotType.objects.all().order_by('abbreviation').exclude(type='Derived').values_list('abbreviation',flat=True))
        dizfin['tipialiq']=listipialiq
        lisderivati=['D','R','P']
        dizfin['der']=lisderivati
        lisderivati2=['D','R']
        dizfin['der2']=lisderivati2
        return dizfin

#per l'autocompletamento del codice paziente nella collezione
class LocalIDListHandler(BaseHandler):
    allowed_methods = ('GET')
    @method_decorator(get_functionality_decorator)
    def read(self, request,prot):
        try:
            print 'prot',prot
            lisprot=prot.split(',')
            lpr=[]
            for pr in lisprot:
                protocollo=CollectionProtocol.objects.get(id=pr)
                lpr.append(protocollo)
            print 'lpr',lpr
            #devo fare la chiamata al modulo clinico per avere la lista dei localid di quel progetto 
            servizio=WebService.objects.get(name='Clinical')
            urlcell=Urls.objects.get(idWebService=servizio).url            
            indir=urlcell+'/coreProject/api/localId/?list='
            for pro in lpr:
                indir+=pro.project+','
            indir=indir[0:len(indir)-1]
            print 'indir',indir
            req = urllib2.Request(indir, headers={"workingGroups" : get_WG_string()})
            u = urllib2.urlopen(req)
            
            da = json.loads(u.read())
            print 'data',da
            dizfin={}
            for proto in lpr:
                for k,val in da.items():
                    print 'k',k
                    print 'val',val
                    print 'proto',proto.project
                    if k==proto.project:
                        print 'proto.id',proto.id                        
                        if val==None:
                            dizfin[proto.id]=[]
                        else:
                            dizfin[proto.id]=list(set(val))
            print 'dizfin',dizfin
            return dizfin
        except Exception,e:
            print 'err',e
            return 'errore'

#Serve per verificare se il barcode esiste o no nello storage
class CheckBarcodeHandler(BaseHandler):
    allowed_methods = ('POST')
    @method_decorator(get_functionality_decorator)
    def create(self, request):
        try:
            barcode=request.POST.get('lbarc')
            indir=Urls.objects.get(default=1).url+ '/api/check/presence/'
            barcode=barcode.replace('#','%23')
            lisbarc=barcode.split('&')
            val1={'lista':json.dumps(lisbarc),'dizprov':json.dumps({})}
            print 'indir',indir
            data = urllib.urlencode(val1)
            req = urllib2.Request(indir,data=data, headers={"workingGroups" : get_WG_string()})
            u = urllib2.urlopen(req)
            #u = urllib2.urlopen(url1, data)
            data = json.loads( u.read())
            print 'data',data
            return data
            
        except Exception,e:
            print 'err',e
            return {"data":'errore'}
        
class ReadFileHandler(BaseHandler):
    allowed_methods = ('POST')
    def create(self, request):
        print request.POST
        try:
            numeropezzi=5
            controlla=True
            if 'progetto' in request.POST:
                prog=request.POST.get('progetto')
                if prog=='motricolor':
                    controlla=False
            resp = {}
            print request.FILES
            f = request.FILES['file_batch']
            linee=f.readlines()
            elems = []
            #parto da 1 per saltare l'intestazione
            for i in range(1,len(linee)):
                line=linee[i].strip()
                print 'line',line
                if line!='':
                    tokens = line.strip().split('\t')
                    print 'len pezzi',len(tokens)                    
                    if controlla and len(tokens) != numeropezzi:
                        raise Exception('File format error. '+str(numeropezzi)+' fields are required: please correct line '+str(i))                    
                    note=''
                    if len(tokens)>numeropezzi:
                        note=tokens[5]
                    elems.append({'place':tokens[0], 'date':tokens[1], 'patient':tokens[2], 'barc':tokens[3], 'vol':tokens[4],'note':note})           
            print 'elems',elems
            resp['elements'] = elems
            return resp
        except Exception, e:
            print 'err',e
            return {'response': e }

#serve nella colorazione dei vetrini per vedere se il genealogy id dell'aliquota,
#introdotto dall'utente, esiste o meno nel DB, se e' del tipo giusto e se l'aliquota non
#e' gia' stata programmata per i vetrini      
class LabelAliquotHandler(BaseHandler):
    allowed_methods = ('GET')
    @method_decorator(get_functionality_decorator)
    def read(self, request,gen,save):
        try:    
            operatore=request.user
            diz=AllAliquotsContainer(gen)
            lista=diz[gen]
            if len(lista)==0:
                return{'data':'inesistente'}
            
            #e' una lista in cui ogni valore e' una stringa formata da gen|barcode|posizione
            for val in lista:
                ch=val.split('|')
                #per controllare se l'aliquota e' di questo wg        
                lisal=Aliquot.objects.filter(uniqueGenealogyID=ch[0],availability=1)
                if len(lisal)==0:
                    return{'data':'inesistente'}
                else:                    
                    al=lisal[0]
                #vedo se l'aliquota e' gia' stata programmata per la procedura
                aldersched=AliquotLabelSchedule.objects.filter(idAliquot=al,executed=0,fileInserted=0,deleteTimestamp=None)
                print 'alqual',aldersched
                if(aldersched.count()!=0):
                    return {'data':'presente'}
                
                #devo vedere se l'aliq puo' essere pianificata per essere colorata   
                if al.idAliquotType.abbreviation!='PS' and al.idAliquotType.abbreviation!='OS':
                    return {'data':'tipoerr'}
            #se non ho avuto degli errori prima allora creo la pianificazione per quello che c'e' nella lista
            #Non salvo ogni oggetto singolarmente perche' potrebbe succedere che inserendo un codice di un vetrino, alcuni campioni siano gia'
            #pianificati e altri no e quindi rischio di salvare delle pianificazioni sbagliate            
            if save:
                lgen=[]
                adesso=timezone.localtime(timezone.now())
                print 'adesso',adesso
                #metto i secondi a zero in modo di partire dal minuto preciso. Poi ad ogni campione aggiungo un secondo
                adesso=adesso.replace(second=0, microsecond=0)
                i=0
                
                schedule=LabelSchedule(scheduleDate=date.today(),
                                      operator=operatore)
                schedule.save()
                for val in lista:
                    ch=val.split('|')
                    #per controllare se l'aliquota e' di questo wg        
                    al=Aliquot.objects.get(uniqueGenealogyID=ch[0],availability=1)
                    #vuol dire che ho chiamato la API direttamente dalla schermata di esecuzione della colorazione dei 
                    #vetrini quindi devo salvare la pianificazione della procedura
                    tempovalidaz=adesso+timezone.timedelta(seconds=i)
                    #creo l'oggetto e metto a 0 i campi che non mi servono in questo momento
                    rev_aliq=AliquotLabelSchedule(idAliquot=al,
                                                  idLabelSchedule=schedule,
                                                  operator=operatore,
                                                  executed=0,
                                                  validationTimestamp=tempovalidaz)
                    rev_aliq.save()
                    print 'salvato sched',rev_aliq
                    lgen.append(ch[0])
                    i+=1
                print 'lgen',lgen
                #devo comunicare allo storage che adesso questi campioni li ha in mano quell'utente                
                url1 = Urls.objects.get(default = '1').url + "/container/availability/"
                val1={'lista':json.dumps(lgen),'tube':'0','nome':request.user.username}

                print 'url1',url1
                data = urllib.urlencode(val1)
                req = urllib2.Request(url1,data=data, headers={"workingGroups" : get_WG_string()})
                u = urllib2.urlopen(req)
                res1 =  u.read()
                print 'res',res1
                if res1=='err':
                    raise Exception
                
            return {'data':lista}
        except Exception,e:
            print 'errore',e
            return {"data":'errore'}
    
#per l'autocompletamento del nome dei geni nella colorazione dei vetrini
class LabelGeneAutocompleteHandler(BaseHandler):
    allowed_methods = ('GET')
    @method_decorator(get_functionality_decorator)
    def read(self, request):
        try:
            if 'term' in request.GET:  
                nomegene=request.GET['term']
                servizio=WebService.objects.get(name='NewAnnotation')
                url=Urls.objects.get(idWebService=servizio).url
                #faccio la get al modulo dandogli il nome del gene
                indir=url+'/newapi/geneInfo/?q='+nomegene
                req = urllib2.Request(indir, headers={"workingGroups" : get_WG_string()})
                u = urllib2.urlopen(req)
                
                da = u.read()
                data=json.loads(da)
                print 'data',data
                res=[]
                if len(data)!=0:
                    for val in data:
                        p = {'id':val['id'], 'label':val['symbol']+'  ('+val['ac']+')' ,'value':val['symbol']+'  ('+val['ac']+')'}
                        res.append(p)
                return res
            return []
        except Exception,e:
            print 'err',e
            return 'errore'

#dato un gene restituisce i possibili probe
class LabelProbeInfoHandler(BaseHandler):
    allowed_methods = ('GET')
    @method_decorator(get_functionality_decorator)
    def read(self, request):
        try: 
            uuidgene=request.GET['gene_uuid']
            print 'uuid',uuidgene
            servizio=WebService.objects.get(name='NewAnnotation')
            url=Urls.objects.get(idWebService=servizio).url
            #faccio la get al modulo dandogli il gene
            indir=url+'/newapi/probeInfo/?gene_uuid='+uuidgene
            req = urllib2.Request(indir, headers={"workingGroups" : get_WG_string()})
            u = urllib2.urlopen(req)
            
            da = u.read()
            data=json.loads(da)
            print 'data',data                
            return data
        except Exception,e:
            print 'err',e
            return 'errore'

#restituisce tutti i marker di un certo tipo con l'autocompletamento in base al nome
class LabelMarknameAutocompleteHandler(BaseHandler):
    allowed_methods = ('GET')
    @method_decorator(get_functionality_decorator)
    def read(self, request):
        try: 
            term=request.GET['term']
            tipomark=request.GET['marker']
            print 'tipo mark',tipomark
            lismarker=LabelMarker.objects.filter(name__icontains=term)
            feat=LabelFeature.objects.get(name=tipomark,type='Marker')
            #ho la feature e adesso devo prendere i marker di quel tipo
            lisfeature=LabelMarkerLabelFeature.objects.filter(idLabelFeature=feat,idLabelMarker__in=lismarker)
            print 'lisfeature',lisfeature
            res=[]
            for p in lisfeature:
                p = {'id':p.idLabelMarker.id, 'label':p.idLabelMarker.name}
                res.append(p)
            print 'res',res
            return res
        except Exception,e:
            print 'err',e
            return 'errore'
        
#restituisce tutti i protocolli di colorazione con l'autocompletamento in base al nome
class LabelProtocolAutocompleteHandler(BaseHandler):
    allowed_methods = ('GET')
    @method_decorator(get_functionality_decorator)
    def read(self, request):
        try: 
            term=request.GET['term']
            lisprot=LabelProtocol.objects.filter(name__icontains=term)            
            res=[]
            for p in lisprot:
                p = {'id':p.id, 'label':p.name}
                res.append(p)
            print 'res',res
            return res
        except Exception,e:
            print 'err',e
            return 'errore'

#serve nella schermata di recupero delle immagini dei vetrini per avere i campioni concordi con i filtri scelti
class LabelGetFilesHandler(BaseHandler):
    allowed_methods = ('POST')
    @method_decorator(get_functionality_decorator)
    def create(self, request):
        try:
            #tutti i campi dei filtri sono in AND
            resSet=getMDAMData(request,True)
            #resSet={'MEL0008MPH0000000000LS0100':'micro3','LNG0983BLH0000000000LS0100':'micro','CRCDZJBLMH0000000000LS0200':'psfun11','GTR0008LMH0000000000LS0300':'micro2'}
            #devo prendere i sampling dei campioni afferenti al protocollo eventualmente selezionato nel filtro
            raw_data = json.loads(request.raw_post_data)
            lisprot=raw_data['protocol']
            dizaliqprot={}
            if len(lisprot)!=0:
                listaid=LabelProtocol.objects.filter(name__in=lisprot).values_list('id',flat=True)
                print 'lista',listaid
                lisconf=LabelConfiguration.objects.filter(idLabelProtocol__in=listaid).values_list('id',flat=True)
                lislabsched=AliquotLabelSchedule.objects.filter(idLabelConfiguration__in=lisconf,executed=1,deleteTimestamp=None).values_list('idSamplingEvent',flat=True)
                lisaliq=Aliquot.objects.filter(idSamplingEvent__in=lislabsched)
                print 'lisaliq',lisaliq
                lisgen=''
                for al in lisaliq:
                    lisgen+=al.uniqueGenealogyID+'&'                    
                    
                stringtot=lisgen[:-1]
                diz=AllAliquotsContainer(stringtot)
                print 'diz',diz
                for k, val in diz.items():
                    v=val[0].split('|')
                    #in v[1] ho il codice del vetrino
                    dizaliqprot[k]=v[1]                
            
                #interseco a resSet i dati di dizaliqprot
                if resSet!=None:                
                    resSet=dictIntersect(resSet, dizaliqprot)
                else:
                    resSet=dizaliqprot
                
            print 'resSet',resSet  
            if resSet==None:
                resSet={}
            samplesToViz = {}
            lissampl=Aliquot.objects.filter(uniqueGenealogyID__in= resSet.keys()).values_list('idSamplingEvent',flat=True)
            
            #escludo i file cancellati
            filesSample = LabelFile.objects.filter( idAliquotLabelSchedule__in = AliquotLabelSchedule.objects.filter(idSamplingEvent__in= lissampl,executed=1,deleteTimestamp=None ),deleteTimestamp=None)
            #contiene tutti i campioni che soddisfano i criteri di ricerca impostati dall'utente nella schermata e
            #che hanno uno o piu' file associati
            for f in filesSample:
                s = f.idAliquotLabelSchedule
                laliq=Aliquot.objects.filter(idSamplingEvent=s.idSamplingEvent)
                for aliq in laliq:
                    if not samplesToViz.has_key(aliq.id):
                        samplesToViz[aliq.id] = {'genid': aliq.uniqueGenealogyID, 'barcode': resSet[aliq.uniqueGenealogyID] ,'exec_date': str(s.executionDate), 'runs':{}}
                    if not samplesToViz[aliq.id]['runs'].has_key(s.id):
                        oper=''
                        if s.operator!=None:
                            oper=s.operator.username
                        samplesToViz[aliq.id]['runs'][s.id] = { 'notes': s.notes, 'description': s.notes,'operator':oper, 'files': {}}
                    samplesToViz[aliq.id]['runs'][s.id]['files'][f.id] = {'link': f.fileId, 'name':f.fileName}
            print 'diz campioni',samplesToViz
            return samplesToViz
        except Exception, e:
            print 'err',e
            return {'data': 'err'}

#serve nella colorazione dei vetrini nella schermata di inserimento del file per inserire nuovi campioni di LS
#a cui aggiungere il file    
class LabelInsertHandler(BaseHandler):
    allowed_methods = ('GET')
    @method_decorator(get_functionality_decorator)
    def read(self, request,gen):
        try:
            #dizionario con chiave il genid e valore una lista con il nome dei file gia' presenti per quel vetrino
            dizfile={}   
            diz=AllAliquotsContainer(gen)
            lista=diz[gen]
            if len(lista)==0:
                return{'data':'inesistente'}
            lisfin=[]
            #e' una lista in cui ogni valore e' una stringa formata da gen|barcode|posizione
            for val in lista:
                ch=val.split('|')
                #per controllare se l'aliquota e' di questo wg        
                lisal=Aliquot.objects.filter(uniqueGenealogyID=ch[0],availability=1)
                if len(lisal)==0:
                    return{'data':'inesistente'}
                else:                    
                    al=lisal[0]
                #prendo la procedura collegata al campione di LS passato (se c'e')
                print 'al.idSamp',al.idSamplingEvent.id
                aldersched=AliquotLabelSchedule.objects.filter(idSamplingEvent=al.idSamplingEvent,executed=1,fileInserted=1,deleteTimestamp=None)
                print 'aliq label',aldersched
                if(aldersched.count()==0):
                    return {'data':'assente'}
                data=str(aldersched[0].executionDate)
                protocollo=aldersched[0].idLabelConfiguration.idLabelProtocol.name
                valore=val+'|'+aldersched[0].idAliquot.uniqueGenealogyID+'|'+data+'|'+protocollo
                lisfin.append(valore)
                #qui prendo tutti i file anche quelli cancellati perche' mi serve poi per dare dei nomi univoci                
                #ai nuovi file che inserisco
                lisfile=LabelFile.objects.filter(idAliquotLabelSchedule=aldersched[0])
                print 'lisfile',lisfile
                if len(lisfile)!=0:
                    listemp=[]
                    for f in lisfile:
                        listemp.append(f.fileName)
                    dizfile[al.uniqueGenealogyID]=listemp
                
            return {'data':lisfin, 'dizfile':json.dumps(dizfile)}
        except Exception,e:
            print 'errore',e
            return {"data":'errore'}

#mi da' la lista dei vetrini colorati che rispondono a certe caratteristiche. Serve nella schermata di colorazione dei vetrini
#nella parte dell'inserimento dei risultati delle analisi per avere la lista dei vetrini per cui inserire i risultati. 
class LabelListHandler(BaseHandler):
    allowed_methods = ('GET')
    @method_decorator(get_functionality_decorator)
    def read(self, request,tipo,tecn,protocollo,operatore,genid,datadal,dataal,utente):
        try:
            lista1=[]
            dizgen={}
            listadiz=[]         
            print 'genid',genid
            aliqtip=AliquotType.objects.get(abbreviation='LS')
            print 'wg',get_WG_string()
            #se e' stata indicata una parte del gen, filtro anche in base a quella
            if genid!='None':
                lisaliq=Aliquot.objects.filter(idAliquotType=aliqtip,uniqueGenealogyID__icontains=genid,availability=1)
            else:
                lisaliq=Aliquot.objects.filter(idAliquotType=aliqtip,availability=1)
            print 'lisaliq',lisaliq
            
            tecnica=LabelFeature.objects.get(id=tecn)
            print 'tecnica',tecnica
            #devo prendere tutti i protocolli che hanno quella tecnica
            lisprotid=LabelProtocolLabelFeature.objects.filter(idLabelFeature=tecnica).values_list('idLabelProtocol',flat=True)
            lisconfig=LabelConfiguration.objects.filter(idLabelProtocol__in=lisprotid).values_list('id',flat=True)
            lislabel=AliquotLabelSchedule.objects.filter(idLabelConfiguration__in=lisconfig,executed=1,fileInserted=1,deleteTimestamp=None).values_list('idSamplingEvent',flat=True)
            print 'lislabel',lislabel
            #adesso devo prendere le aliquote che hanno quei sampling event
            aliquote=Aliquot.objects.filter(idSamplingEvent__in=lislabel,availability=1).values_list('id',flat=True)
            print 'aliq',aliquote
            
            #da togliere il commento                    
            #lisaliq=lisaliq.filter(id__in=aliquote)
                                    
            
            if protocollo!= 'None':
                lisconfig=LabelConfiguration.objects.filter(idLabelProtocol=protocollo).values_list('id',flat=True)
                lislabel=AliquotLabelSchedule.objects.filter(idLabelConfiguration__in=lisconfig,executed=1,fileInserted=1,deleteTimestamp=None).values_list('idSamplingEvent',flat=True)
                print 'lislabel',lislabel
                #adesso devo prendere le aliquote che hanno quei sampling event
                aliquote=Aliquot.objects.filter(idSamplingEvent__in=lislabel,availability=1).values_list('id',flat=True)
                print 'aliq',aliquote
                lisaliq=lisaliq.filter(id__in=aliquote)
                #se la lista e' vuota non controllo neanche gli altri parametri, essendo tutti in and fra loro,
                #ma restituisco subito una lista vuota
                if len(lisaliq)==0:
                    return {'data':json.dumps([])}
            
            if operatore!= 'None':
                oper=User.objects.get(id=operatore)
                print 'oper',oper
                #prendo gli id dei samplingevent
                lislabel=AliquotLabelSchedule.objects.filter(operator=oper,executed=1,fileInserted=1,deleteTimestamp=None).values_list('idSamplingEvent',flat=True)
                print 'lislabel',lislabel
                #adesso devo prendere le aliquote che hanno quei sampling event
                aliquote=Aliquot.objects.filter(idSamplingEvent__in=lislabel,availability=1).values_list('id',flat=True)
                print 'aliq',aliquote
                lisaliq=lisaliq.filter(id__in=aliquote)
                
                if len(lisaliq)==0:
                    return {'data':json.dumps([])}

            if datadal!='None':
                attr=datadal.split('_')
                attr2=attr[1].split('-')
                datarif=datetime.date(int(attr2[0]),int(attr2[1]),int(attr2[2]))
                if dataal!='None':
                    att2=dataal.split('-')
                    datarif2=datetime.date(int(att2[0]),int(att2[1]),int(att2[2]))
                for aliq in lisaliq:
                    datasamp=aliq.idSamplingEvent.samplingDate
                    print 'datasamp',datasamp
                    #attr[1] contiene la data inserita dall'utente
                    if attr[0]=='<' and datasamp<=datarif:
                        lista1.append(aliq)
                    elif attr[0]=='>' and datasamp>=datarif:
                        if dataal!='None':
                            if datasamp<=datarif2:
                                lista1.append(aliq)
                        else:
                            lista1.append(aliq)
                    elif attr[0]=='=' and datasamp==datarif:
                        lista1.append(aliq)
                print 'lista1',lista1
                if len(lista1)==0:
                    return {'data':json.dumps([])}
                lisaliq=lista1                                    
                                            
            print 'lisaliq finale',lisaliq
            lissamplingid=[]
            #chiave il samplid e valore l'aliquota
            dizaliqsampl={}            
            
            stringtot=''
            for aliq in lisaliq:
                lissamplingid.append(aliq.idSamplingEvent)
                dizaliqsampl[aliq.idSamplingEvent.id]=aliq
                stringtot+=aliq.uniqueGenealogyID+'&'
            
            lgenfin=stringtot[:-1]
            dizgen=AllAliquotsContainer(lgenfin)
            print 'dizgen',dizgen
            
            if tipo=='Part':
                #chiave il barc e valore una lista di gen
                dizbarc={}
                for gen,val in dizgen.items():
                    lval=dizgen[gen][0]
                    val=lval.split('|')
                    barc=val[1]
                    if barc in dizbarc:
                        listemp=dizbarc[barc]
                    else:
                        listemp=[]
                    listemp.append(gen)
                    dizbarc[barc]=listemp
                print 'dizbarc',dizbarc
                #se ho selezionato che voglio solo i vetrini per cui non ho mai inserito valori, devo filtrare ancora
                #lo faccio alla fine di tutto perche' mi serve avere anche il codice del vetrino, in modo che se un campione di un vetrino
                #e' gia' stato analizzato devo togliere dalla lista finale anche gli altri presenti li' sopra.
                lislabsched=AliquotLabelSchedule.objects.filter(idSamplingEvent__in=lissamplingid).values_list('id',flat=True)
                print 'lislab',lislabsched
                #potrei avere piu' labelresult per uno stesso campione.
                #prendo tutti i labelresult anche quelli con valori nulli, perche' poi saranno da togliere dalla lista generale
                lisres=LabelResult.objects.filter(idAliquotLabelSchedule__in=lislabsched)
                print 'lisres',lisres
                lisaliqgen=[]
                for result in lisres:
                    #prendo l'oggetto aliquota
                    al=dizaliqsampl[result.idAliquotLabelSchedule.idSamplingEvent.id]
                    print 'al',al
                    #aggiungo alla lista degli id da togliere dalla lista totale questa aliquota
                    #devo trovare, se ci sono, gli altri campioni che appartengono a questo vetrino e aggiungerli alla lista
                    if dizgen.has_key(al.uniqueGenealogyID):
                        lval=dizgen[al.uniqueGenealogyID][0]
                        val=lval.split('|')
                        barc=val[1]
                        print 'barc',barc
                        lisgen=dizbarc[barc]
                        #aggiungo alla lista originale i nuovi valori togliendo i duplicati
                        lisaliqgen=list(set(lisaliqgen)|set(lisgen))
                print 'lisaliqgen',lisaliqgen
                aliquote=Aliquot.objects.filter(uniqueGenealogyID__in=lisaliqgen,availability=1).values_list('id',flat=True)
                lisaliq=lisaliq.exclude(id__in=aliquote)
            #mi precarico tutti i marker in un dizionario cosi' da non dover accedere al DB per ogni campione
            lisfeat=LabelProtocolLabelFeature.objects.all().exclude(idLabelMarker=None)
            #chiave il nome del protocollo e valore una lista con i marker collegati
            dizmarker={}
            for fe in lisfeat:
                if fe.idLabelProtocol.name in dizmarker:
                    listemp=dizmarker[fe.idLabelProtocol.name]
                else:
                    listemp=[]
                if fe.idLabelMarker.name not in listemp:
                    listemp.append(fe.idLabelMarker.name)
                    dizmarker[fe.idLabelProtocol.name]=listemp
            print 'dizmarker',dizmarker
            
            for al in lisaliq:
                diz={}
                lislabel=AliquotLabelSchedule.objects.filter(idSamplingEvent=al.idSamplingEvent,executed=1,deleteTimestamp=None)
                if len(lislabel)!=0:
                    label=lislabel[0]
                    if dizgen.has_key(al.uniqueGenealogyID):
                        lval=dizgen[al.uniqueGenealogyID][0]
                        val=lval.split('|')
                        barc=val[1]
                        position=val[2]
                        if position=='':
                            position='A1'
                    diz['barcode']=barc
                    diz['position']=position
                    diz['genealogy']=al.uniqueGenealogyID                
                    diz['data']=str(al.idSamplingEvent.samplingDate)                    
                    config=LabelConfiguration.objects.get(id=label.idLabelConfiguration.id)
                    diz['prot']=config.idLabelProtocol.name
                    diz['operator']=label.operator.username
                    diz['marker']=dizmarker[config.idLabelProtocol.name]
                    listadiz.append(diz)
            print 'listadiz',listadiz
            request.session['listaLabelSaveResult']=listadiz       
            return {'data':json.dumps(listadiz)}
        except Exception,e:
            print 'err',e
            return {"data":'errore'}

class LoginHandler(BaseHandler):
    allowed_methods = ('POST')
    @method_decorator(get_functionality_decorator)
    def create(self, request):
        #time.sleep(5)
        username = request.POST['username']
        password = request.POST['password']
        user = auth.authenticate(username=username, password=password)
        if user is not None and user.is_active:
            auth.login(request, user)
            return {'sessionid' : str(request.session.session_key)}
        else:
            return {'sessionid' : 'none'}

class LogoutHandler(BaseHandler):
    allowed_methods = ('POST')
    @method_decorator(get_functionality_decorator)
    def create(self, request):
        auth.logout (request)

class SaveWgAliquot(BaseHandler):
    allowed_methods = ('POST')
    def create(self, request):
        try:
            print request.POST
            genid=request.POST.get('genid')
            wgList=json.loads(request.POST.get('wgList'))
            print wgList
            disable_graph()
            aliquot=Aliquot.objects.get(uniqueGenealogyID=genid)
            enable_graph()
            for item in wgList:
                wg=WG.objects.get(name=item)
                if Aliquot_WG.objects.filter(aliquot=aliquot,WG=wg).count()==0:
                    m2m=Aliquot_WG(aliquot=aliquot,WG=wg)
                    m2m.save()
            return {'data':'ok'}
        except Exception,e:
            print 'err',e
            return {'data':'error'}

class ShareAliquots(BaseHandler):
    allowed_methods = ('POST')
    def create(self, request):
        try:
            genidList=json.loads(request.POST.get('genidList'))
            wgList=json.loads(request.POST.get('wgList'))
            disable_graph()
            for genid in genidList:
                aliquot=Aliquot.objects.get(uniqueGenealogyID=genid)
                for item in wgList:
                    wg=WG.objects.get(name=item)
                    if Aliquot_WG.objects.filter(aliquot=aliquot,WG=wg).count()==0:
                        m2m=Aliquot_WG(aliquot=aliquot,WG=wg)
                        m2m.save()
            enable_graph()
            return {'message':'ok'}
        except Exception,e:
            print 'err',e
            return {'message':'error'}

#API che riceve in ingresso una lista di blocchetti e ne fa il salvataggio
class SaveBlocks(BaseHandler):   
    @transaction.commit_on_success
    @method_decorator(get_functionality_decorator)
    def create(self, request):
        try:
            print 'API save blocks'
            print request.POST
            print request.raw_post_data
            #diz con chiave formata da paz+cons+posto+prot+tum e valore l'oggetto Collezione relativo. Per sapere se            
            #una collezione e' gia' stata creata. Non posso usare il get or create perche' l'item code cambia sempre.
            dizcollezioni={}
            #diz con tum+caso+tess come chiave e il contatore del genid come valore
            dizcontatore={}
            listaal=[]
            vv=json.loads(request.raw_post_data)
            print 'vv',vv
            lisexists=[]
            lisnotexists=[]
            lislocalid=[]
            listablocchi=vv['specimens']
            print 'listablocchi',listablocchi
            
            lisconsensi=[]
            #diz con chiave il nome del protocollo e come valore il project
            dizprot={}
            stringaid=''
            for blocco in listablocchi:
                prot=blocco['project']
                consenso=blocco['ICcode']
                if prot not in dizprot.keys():
                    protoc=CollectionProtocol.objects.get(project=prot)
                    stringaid+=str(protoc.id)+','
                    dizprot[prot]=protoc.project
                    progg=protoc.project
                else:
                    progg=dizprot[prot]
                #per avere la lista con i consensi e i progetti    
                val=consenso+'_'+progg
                print 'val save batch',val
                if val not in lisconsensi:
                    lisconsensi.append(val)
                        
            stringaid=stringaid[0:len(stringaid)-1]
            print 'stringaid',stringaid
            #mi faccio dare la lista dei localid per i protocolli per sapere quali ci sono gia'
            hand=LocalIDListHandler()
            dizlocalid=hand.read(request,stringaid)
            print 'dizlocalid',dizlocalid
            
            diztotconsensi=checkListInformedConsent(lisconsensi)
            print 'diztotcons',diztotconsensi
            
            for blocco in listablocchi:
                print 'blocco',blocco
                barc=blocco['barcode']
                #e' ad es. funnel
                prot=blocco['project']
                paz=blocco['localId']
                consenso=blocco['ICcode']
                #ad es CRC
                tum=blocco['type']
                #valori PR,LI,SM,TM,BM,LY,00
                tissue=blocco['tissue']
                
                operatore=blocco['operator']
                #prendo il wg dell'operatore per impostarlo nella collezione
                oper=User.objects.get(username=operatore)
                liswg=WG_User.objects.filter(user=oper)                
                
                #prendo le due lettere iniziali del barc che mi indicano il posto di provenienza
                posto=barc[0:2]
                print 'posto',posto
                lospedale=Source.objects.filter(internalName=posto)
                #c'e' il problema che Niguarda e Candiolo compaiono piu' volte con lo stesso nome interno
                #quindi devo discriminare in base al tipo di sorgente
                print 'lospedale',lospedale
                if len(lospedale)>1:
                    for osp in lospedale:
                        if prot=='Funnel':
                            if osp.type[0:6]=='Funnel':
                                ospedale=osp
                                break
                        else:
                            if osp.type=='Hospital':
                                ospedale=osp
                                break
                        
                print 'ospedale',ospedale
                tumore=CollectionType.objects.get(abbreviation=tum)
                protoc=CollectionProtocol.objects.get(project=prot)
                
                #se il protocollo e' della Marsoni allora devo mettere in share anche lei per le aliquote
                liscollinvestig=CollectionProtocolInvestigator.objects.filter(idCollectionProtocol=protoc)
                trovato=False
                if len(liscollinvestig)!=0:
                    for coll in liscollinvestig:
                        if coll.idPrincipalInvestigator.surname=='Marsoni' and coll.idPrincipalInvestigator.name=='Silvia':
                            trovato=True
                            break
                listawg=[liswg[0].WG.name]
                if trovato:
                    listawg.append('Marsoni_WG')
                print 'listawg',listawg
                set_initWG(listawg)
                
                workingGroup=[liswg[0].WG.name]
                
                if tissue!='00':
                    if tissue=='LI':
                        tissue='LM'
                    tess=TissueType.objects.get(abbreviation=tissue)
                else:
                    #se e' 00 vuol dire che e' tessuto normale, pero' in base al tumore cambia il tessuto normale
                    if tum=='CRC':
                        #se e' CRC e' normal mucosa
                        tess=TissueType.objects.get(abbreviation='NM')
                #solo se non ho ancora creato una collezione per quella serie di dati
                chiave=paz+consenso+ospedale.name+prot+tum
                if not dizcollezioni.has_key(chiave):
                    #il consenso e' uguale al codice paziente perche' un paziente firma solo un consenso. Quindi 
                    #devo disambiguare il consenso mettendo _ seguito da un numero.
                    #Non lo devo piu' fare perche' adesso posso anche avere un consenso duplicato, tanto la
                    #coerenza e' mantenuta dal modulo di dati clinici                
                    #guardo se c'e' gia' una collezione per quel paziente
                    '''listacoll=Collection.objects.filter(idSource=ospedale,patientCode=paz).order_by('id')
                    print 'lista',listacoll
                    if len(listacoll)!=0:
                        #c'e' una collezione: devo proporre un coll event
                        #prendo il coll event dell'ultima collezione
                        eve=listacoll[len(listacoll)-1].collectionEvent
                        print 'eve',eve
                        #divido in base al _
                        evespl=eve.split('_')
                        #se non c'era il _
                        if len(evespl)==1:
                            if eve[len(eve)-1]!='_':
                                evefin=eve+'_1'
                            else:
                                evefin=eve+'1'
                        else:
                            evefin=''
                            #val contiene l'ultimo numero del consenso
                            val=evespl[len(evespl)-1]
                            print 'val',val
                            if val.isdigit():
                                for i in range(0,len(evespl)-1):
                                    print 'evespl[i]',evespl[i]
                                    evefin+=evespl[i]+'_'
                                #incremento il valore di 1
                                evefin+=str(int(val)+1)
                            else:
                                if eve[len(eve)-1]!='_':
                                    evefin=eve+'_1'
                                else:
                                    evefin=eve+'1'
                    else:
                        evefin=consenso'''
                    evefin=consenso
                    #creo il caso casuale
                    caso=NewCase('not active', True, tumore)
                    #voglio un valore casuale e devo andare a vedere se c'e' gia' quel valore nel dizionario
                    trovato=False
                    while not trovato:
                        #uso due valori booleani perche' nel caso faccia un nuovo caso devo riscandire il diz per vedere
                        #se va bene anche questo nuovo caso
                        pres=False
                        for k,coll in dizcollezioni.items(): 
                            #coll e' un oggetto collezione
                            if coll.idCollectionType.abbreviation==tumore.abbreviation:
                                if coll.itemCode==caso:
                                    #vuol dire che devo ricreare un nuovo caso
                                    caso=NewCase('not active', True, tumore)
                                    print 'caso nuovo',caso
                                    pres=True
                        #termino il ciclo while perche' non ho trovato doppioni per il codice del caso
                        print 'pres',pres
                        if not pres:
                            trovato=True                                    
                        
                    collezione=Collection(itemCode=caso,
                                 idSource=ospedale,
                                 idCollectionType=tumore,
                                 collectionEvent=evefin,
                                 patientCode=paz,
                                 idCollectionProtocol=protoc)
                    collezione.save()
                    
                    valore=diztotconsensi[evefin+'_'+protoc.project]
                    print 'val',valore
                    if valore==None:
                        #vuol dire che l'ic non esiste ancora
                        diztemp={'caso':collezione.itemCode,'tum':collezione.idCollectionType.abbreviation,'consenso':collezione.collectionEvent,'progetto':collezione.idCollectionProtocol.project,'source':collezione.idSource.internalName,'wg':workingGroup,'operator':operatore}
                        lislocal=dizlocalid[protoc.id]
                        if paz in lislocal:
                            #il paziente esiste gia'
                            diztemp['paziente']=collezione.patientCode
                        else:
                            #il paziente inserito non esiste ancora
                            if collezione.patientCode=='':
                                #il paziente non e' stato inserito dall'utente, quindi non viene creato niente
                                diztemp['paziente']=''
                            else:
                                #il paziente e' stato inserito
                                diztemp['newLocalId']=collezione.patientCode
                        lisnotexists.append(diztemp)
                    else:
                        lisexists.append({'caso':collezione.itemCode,'tum':collezione.idCollectionType.abbreviation,'consenso':collezione.collectionEvent,'progetto':collezione.idCollectionProtocol.project,'wg':workingGroup})
                        localid=valore['patientUuid']
                        lislocalid.append(localid)
                                            
                    dizcollezioni[chiave]=collezione
                else:
                    collezione=dizcollezioni[chiave]
                print 'collezione',collezione
                
                #salvo la serie
                ser,creato=Serie.objects.get_or_create(operator=operatore,
                                                       serieDate=date.today())
                print 'ser',ser
                
                #il sampling lo creo per ogni aliquota con get or create perche' puo' cambiare il tessuto 
                campionamento,creato=SamplingEvent.objects.get_or_create(idTissueType=tess,
                                             idCollection=collezione,
                                             idSource=ospedale,
                                             idSerie=ser,
                                             samplingDate=date.today())
                print 'camp',campionamento
                chiavediz=tumore.abbreviation+caso+tess.abbreviation
                if dizcontatore.has_key(chiavediz):
                    contatore=int(dizcontatore[chiavediz])
                    contatore=contatore+1
                    contatore=str(contatore).zfill(2)
                else:
                    contatore='01'
                dizcontatore[chiavediz]=contatore                
                print 'dizcontatore',dizcontatore
                
                genid=chiavediz+'H0000000000FF'+contatore+'00'
                tipoaliquota=AliquotType.objects.get(abbreviation='FF')
                
                a=Aliquot(barcodeID=barc,
                       uniqueGenealogyID=str(genid),
                       idSamplingEvent=campionamento,
                       idAliquotType=tipoaliquota,
                       timesUsed=0,
                       availability=1,
                       derived=0,
                       archiveDate=date.today())
                print 'a',a
                a.save()
                numpezzi=1
                #salvo il numero di pezzi
                fea=Feature.objects.get(Q(idAliquotType=tipoaliquota)&Q(name='NumberOfPieces'))
                aliqfeature=AliquotFeature(idAliquot=a,
                                           idFeature=fea,
                                           value=numpezzi)
                aliqfeature.save()
                print 'aliq',aliqfeature
                valori=genid+',,,'+str(numpezzi)+','+barc+','+tipoaliquota.abbreviation+',true,,,,,,'+str(date.today())
                listaal.append(valori)
            
            request,errore=SalvaInStorage(listaal,request)
            print 'err', errore
            if errore==True:
                raise Exception
            #devo fare gia' il commit perche' devo passare al modulo clinico la collezione, che deve gia' esistere sul grafo
            #altrimenti non si riesce a collegare il nodo collezione con il consenso informato
            transaction.commit()
            #faccio la API al modulo clinico per dirgli di salvare            
            errore=saveInClinicalModule(lisexists,lisnotexists,workingGroup,operatore,lislocalid)
            if errore:
                raise Exception
            
            response = rc.ALL_OK
            response.content = json.dumps({'status':'200'})
            print 'response',response
            print 'resp',response.content
            return response
        except Exception,e:
            print 'err',e
            #mando un'e-mail per segnalare l'errore
            inviaMailFunnel(e,json.loads(request.raw_post_data),"Error in 'Save blocks' Funnel API")
            transaction.rollback()
            response = rc.BAD_REQUEST
            response.content = json.dumps({'status':'400'})
            print 'response',response.content
            return response
            #return Response(json.dumps({'status':'400'}), status=status.HTTP_201_CREATED)
            #return json.dumps({'status':'400'})

#API che riceve in ingresso una lista di derivati e li salva
class SaveDerived(BaseHandler):
    allowed_methods = ('POST')
    @transaction.commit_on_success
    @method_decorator(get_functionality_decorator)
    def create(self, request):
        try:
            print 'API save derived'
            print request.POST
            print request.raw_post_data
            vv=json.loads(request.raw_post_data)
            print 'vv',vv
            #lista con i derivati da salvare
            listaaliq=vv['aliquots']
            #scandisco una prima volta per avere il gen delle madri dato il barcode
            lisbarc=''
            listaal=[]
            listaaliqslide=[]
            #diz con chiave il barc della madre e con valore una lista di diz che contengono i dati passati alla API
            dizmadri={}
            for al in listaaliq:
                barcmadre=al['fatherSpecimenBarcode']
                if dizmadri.has_key(barcmadre):
                    lisfiglie=dizmadri[barcmadre]
                else:
                    lisfiglie=[]
                    lisbarc+=barcmadre+'&'
                lisfiglie.append(al)
                dizmadri[barcmadre]=lisfiglie
                
            stringtot=lisbarc[:-1]
            print 'stringtot',stringtot
            diz=AllAliquotsContainer(stringtot)
            print 'dizmadri',dizmadri
            #key e' il barc della madre, val e' la lista delle figlie
            #puo' essere che la madre abbia figlie sia di DNA che di PS
            for key,val in dizmadri.items():
                lista=diz[key]
                #e' una lista in cui ogni valore e' una stringa formata da gen|barcode|posizione
                ch=lista[0].split('|')
                genmadre=ch[0]
                
                disable_graph()
                almadre=Aliquot.objects.get(uniqueGenealogyID=genmadre)
                gg=GenealogyID(genmadre)
                
                stringa=gg.getPartForDerAliq()
                #aggiungo il tipo di derivato che voglio ottenere (R o D)
                stringa1=stringa+'D'
                #guardo se quell'inizio di genealogy ce l'ha gia' qualche aliquota derivata
                #cerco anche i derivati che finiscono con '000' per trovare solo i 
                #dna o gli rna puri e non riderivati per ottenre cRNA o cDNA
                #e' giusto considerare anche le aliq non disponibili                
                lista_aliquote_derivate=Aliquot.objects.filter(uniqueGenealogyID__startswith=stringa1,uniqueGenealogyID__endswith='000',derived=1).order_by('-uniqueGenealogyID')
                
                print 'lista_aliquote',lista_aliquote_derivate
                if lista_aliquote_derivate.count()!=0:
                    #prendo il primo oggetto che e' quello che ha il contatore piu' alto
                    maxgen=lista_aliquote_derivate[0].uniqueGenealogyID
                    nuovoge=GenealogyID(maxgen)
                    maxcont=nuovoge.getAliquotExtraction()
                    contdna=int(maxcont)
                else:
                    contdna=0                
                print 'contdna',contdna
                
                #aggiungo il tipo di derivato che voglio ottenere
                stringa2=stringa+'PS'
                #guardo se quell'inizio di genealogy ce l'ha gia' qualche PS
                lista_aliquote_PS=Aliquot.objects.filter(uniqueGenealogyID__startswith=stringa2).order_by('-uniqueGenealogyID')
                
                print 'lista_aliquote_PS',lista_aliquote_PS
                if lista_aliquote_PS.count()!=0:
                    #prendo il primo oggetto che e' quello che ha il contatore piu' alto
                    maxgen=lista_aliquote_PS[0].uniqueGenealogyID
                    nuovoge=GenealogyID(maxgen)
                    maxcont=nuovoge.getAliquotExtraction()
                    contslide=int(maxcont)
                else:
                    contslide=0                
                print 'contslide',contslide
                
                #aggiungo il tipo di derivato che voglio ottenere
                stringa2=stringa+'LS'
                #guardo se quell'inizio di genealogy ce l'ha gia' qualche PS
                lista_aliquote_LS=Aliquot.objects.filter(uniqueGenealogyID__startswith=stringa2).order_by('-uniqueGenealogyID')
                enable_graph()
                
                print 'lista_aliquote_LS',lista_aliquote_LS
                if lista_aliquote_LS.count()!=0:
                    #prendo il primo oggetto che e' quello che ha il contatore piu' alto
                    maxgen=lista_aliquote_LS[0].uniqueGenealogyID
                    nuovoge=GenealogyID(maxgen)
                    maxcont=nuovoge.getAliquotExtraction()
                    contls=int(maxcont)
                else:
                    contls=0                
                print 'contls',contls

                salvadna=False
                salvaslide=False
                salvals=False
                #serve a sapere se una volta salvate le figlie devo aggiornare il times used della madre
                #solo se ho salvato del DNA
                aggiornamadre=False
                tipofigliadna=AliquotType.objects.get(abbreviation='DNA')
                tipofigliaps=AliquotType.objects.get(abbreviation='PS')
                tipofiglials=AliquotType.objects.get(abbreviation='LS')
                featspessps=Feature.objects.get(Q(idAliquotType=tipofigliaps)&Q(name='Thickness'))
                featspessls=Feature.objects.get(Q(idAliquotType=tipofiglials)&Q(name='Thickness'))
                print 'val',val
                campionamento=None
                campionamentops=None
                campionamentols=None
                for alfiglia in val:
                    operatore=alfiglia['operator']
                    barcfiglia=alfiglia['childBarcode']
                    tipoaliq=alfiglia['aliquotType']                    
                    if tipoaliq=='DNA':
                        aggiornamadre=True
                        
                        #salvo queste informazioni una volta sola per tutt i DNA di questa madre                        
                        if not salvadna:
                            ser,creato=Serie.objects.get_or_create(operator=operatore,
                                                           serieDate=date.today())
                            
                            #salvo il sampling event
                            samp_ev=SamplingEvent(idTissueType=almadre.idSamplingEvent.idTissueType,
                                                idCollection=almadre.idSamplingEvent.idCollection,
                                                idSource=almadre.idSamplingEvent.idCollection.idSource,
                                                idSerie=ser,
                                                samplingDate=date.today())
                            samp_ev.save()
                            campionamento=samp_ev
                            #salvo il derivation schedule
                            der_sched,creato=DerivationSchedule.objects.get_or_create(scheduleDate=date.today(),
                                                                                  operator=operatore)
                            
                            d_prot=DerivationProtocol.objects.get(name='DNA extraction (FFPE)')
                            #metto derivation executed a 0 perche' se no ci sono problemi con l'audit
                            al_der_sch=AliquotDerivationSchedule(idAliquot=almadre,
                                                             idDerivationSchedule=der_sched,
                                                             idDerivedAliquotType=tipofigliadna,
                                                             idDerivationProtocol=d_prot,
                                                             derivationExecuted=0,
                                                             operator=operatore,
                                                             failed=0,
                                                             initialDate=date.today(),
                                                             measurementExecuted=1,
                                                             aliquotExhausted=0)
                            al_der_sch.save()
                            al_der_sch.derivationExecuted=1
                            al_der_sch.save()
                            #salvo il derivation event
                            der_ev=DerivationEvent(idSamplingEvent=samp_ev,
                                                idAliqDerivationSchedule=al_der_sch,
                                                derivationDate=date.today(),
                                                operator=operatore)
                            der_ev.save()
                            salvadna=True
                        
                        contdna=contdna+1                    
                        contatore=str(contdna).zfill(2)                        
                        genfiglia=gg.getPartForDerAliq()+'D'+contatore+'000'
                        print 'gendna',genfiglia
                        al=Aliquot(barcodeID=barcfiglia,
                                   uniqueGenealogyID=genfiglia,
                                   idSamplingEvent=campionamento,
                                   idAliquotType=tipofigliadna,
                                   availability=1,
                                   timesUsed=0,
                                   derived=1,
                                   archiveDate=date.today())
                        al.save()
                        print 'al dna',al
                        #devo salvare le feature se ci sono
                        if 'volume' in alfiglia:
                            volume=alfiglia['volume'].strip()
                            vol=volume.replace(',','.')
                        else:
                            vol=-1
                            
                        fea=Feature.objects.get(Q(idAliquotType=tipofigliadna)&Q(name='OriginalVolume'))
                        aliqfeature=AliquotFeature(idAliquot=al,
                                                   idFeature=fea,
                                                   value=float(vol))
                        aliqfeature.save()
                        
                        fea=Feature.objects.get(Q(idAliquotType=tipofigliadna)&Q(name='Volume'))
                        aliqfeature=AliquotFeature(idAliquot=al,
                                                   idFeature=fea,
                                                   value=float(vol))
                        aliqfeature.save()
                        
                        if 'concentration' in alfiglia:
                            concentrazione=alfiglia['concentration'].strip()
                            conc=concentrazione.replace(',','.')
                        else:
                            conc=-1
                            
                        fea=Feature.objects.get(Q(idAliquotType=tipofigliadna)&Q(name='OriginalConcentration'))
                        aliqfeature=AliquotFeature(idAliquot=al,
                                                   idFeature=fea,
                                                   value=float(conc))
                        aliqfeature.save()
                        
                        fea=Feature.objects.get(Q(idAliquotType=tipofigliadna)&Q(name='Concentration'))
                        aliqfeature=AliquotFeature(idAliquot=al,
                                                   idFeature=fea,
                                                   value=float(conc))
                        aliqfeature.save()
                        
                        valori=genfiglia+',,,,'+barcfiglia+','+tipofigliadna.abbreviation+',true,,,,,,'+str(date.today())
                        listaal.append(valori)
                        
                    elif tipoaliq=='SLIDE' or tipoaliq=='HE':                        
                        numfette=int(alfiglia['nSlices'])
                        print 'numfette',numfette
                        operat=User.objects.get(username=operatore)
                        ser,creato=Serie.objects.get_or_create(operator=operatore,
                                                               serieDate=date.today())
                        
                        #salvo lo slide schedule
                        slide_sched,creato=SlideSchedule.objects.get_or_create(scheduleDate=date.today(),
                                                                              operator=operat)
                        if tipoaliq=='SLIDE':
                            if not salvaslide:                                                            
                                #salvo il sampling event
                                samp_ev=SamplingEvent(idTissueType=almadre.idSamplingEvent.idTissueType,
                                                    idCollection=almadre.idSamplingEvent.idCollection,
                                                    idSource=almadre.idSamplingEvent.idCollection.idSource,
                                                    idSerie=ser,
                                                    samplingDate=date.today())
                                samp_ev.save()
                                campionamentops=samp_ev
                                
                                slideprot=SlideProtocol.objects.get(name='Microtome')
                                al_slide_sch=AliquotSlideSchedule(idAliquot=almadre,
                                                                 idSlideSchedule=slide_sched,
                                                                 idSamplingEvent=campionamentops,
                                                                 idSlideProtocol=slideprot,
                                                                 operator=operat,
                                                                 executionDate=date.today(),
                                                                 executed=1,
                                                                 aliquotExhausted=0)
                                al_slide_sch.save()
                                                          
                                salvaslide=True
                                
                        #salvo l'aliq slide sched anche per il LS
                        if tipoaliq=='HE':
                            if not salvals:                                
                                #salvo il sampling event
                                samp_ev=SamplingEvent(idTissueType=almadre.idSamplingEvent.idTissueType,
                                                    idCollection=almadre.idSamplingEvent.idCollection,
                                                    idSource=almadre.idSamplingEvent.idCollection.idSource,
                                                    idSerie=ser,
                                                    samplingDate=date.today())
                                samp_ev.save()
                                campionamentols=samp_ev
                                
                                slideprot=SlideProtocol.objects.get(name='Labeled')
                                al_slide_sch=AliquotSlideSchedule(idAliquot=almadre,
                                                                 idSlideSchedule=slide_sched,
                                                                 idSamplingEvent=campionamentols,
                                                                 idSlideProtocol=slideprot,
                                                                 operator=operat,
                                                                 executionDate=date.today(),
                                                                 executed=1,
                                                                 aliquotExhausted=0)
                                al_slide_sch.save()
                                                          
                                salvals=True
                                
                        #devo creare un'aliquota per ogni fetta del vetrino
                        for i in range(0,numfette):
                            if tipoaliq=='SLIDE':
                                contslide=contslide+1                                
                                contatore=str(contslide).zfill(2)                        
                                genfiglia=gg.getPartForDerAliq()+'PS'+contatore+'00'
                                tipoalfiglia=tipofigliaps
                                fspess=featspessps
                                camp=campionamentops
                            elif tipoaliq=='HE':
                                contls=contls+1                                
                                contatore=str(contls).zfill(2)                        
                                genfiglia=gg.getPartForDerAliq()+'LS'+contatore+'00'
                                tipoalfiglia=tipofiglials
                                fspess=featspessls
                                camp=campionamentols
                            print 'genslide',genfiglia
                            posiz='A'+str(i+1)
                            al=Aliquot(barcodeID=barcfiglia+'|'+posiz,
                                       uniqueGenealogyID=genfiglia,
                                       idSamplingEvent=camp,
                                       idAliquotType=tipoalfiglia,
                                       availability=1,
                                       timesUsed=0,
                                       derived=0,
                                       archiveDate=date.today())
                            al.save()
                            print 'al slide',al
                            
                            #devo salvare le feature se ci sono
                            if 'thickness' in alfiglia:
                                spess=alfiglia['thickness'].strip()
                                aliqfeature=AliquotFeature(idAliquot=al,
                                                           idFeature=fspess,
                                                           value=float(spess))
                            aliqfeature.save()
                            
                            geom='1x'+str(numfette)
                            valori=genfiglia+','+barcfiglia+','+tipoalfiglia.abbreviation+','+str(date.today())+',SlideMicrotome,'+geom+','+posiz
                            listaaliqslide.append(valori)
                        
                if aggiornamadre:
                    #aggiungo 1 al times used della madre
                    volte=int(almadre.timesUsed)
                    volte=volte+1
                    almadre.timesUsed=volte
                    almadre.save()
                    
            print 'listaal',listaal
            if len(listaal)!=0:
                request,errore=SalvaInStorage(listaal,request)
                print 'err', errore
                if errore==True:
                    raise Exception        
            
            if len(listaaliqslide)!=0:
                #salvo le nuove aliquote nello storage
                url1 = Urls.objects.get(default = '1').url + "/api/save/slide/"
                val1={'lista':json.dumps(listaaliqslide),'user':operatore}
                if len(listaaliq)!=0:
                    print 'url1',url1
                    data = urllib.urlencode(val1)
                    req = urllib2.Request(url1,data=data, headers={"workingGroups" : 'admin'})
                    u = urllib2.urlopen(req)
                    res1 =  json.loads(u.read())
                    print 'res1',res1
                    if res1['data']=='err':
                        raise Exception
            
            response = rc.ALL_OK
            response.content = json.dumps({'status':'200'})
            return response
        except Exception,e:
            print 'err',e
            #mando un'e-mail per segnalare l'errore
            inviaMailFunnel(e,json.loads(request.raw_post_data),"Error in 'Save derived' Funnel API")
            
            transaction.rollback()
            response = rc.BAD_REQUEST
            response.content = json.dumps({'status':'400'})
            return response

#API che riceve in ingresso una lista di plasmi e pianifica un trasferimento
class TransferVials(BaseHandler):
    allowed_methods = ('POST')
    @transaction.commit_on_success
    @method_decorator(get_functionality_decorator)
    def create(self, request):
        try:
            print 'API transfer vials'
            print request.POST
            print request.raw_post_data
            vv=json.loads(request.raw_post_data)
            print 'vv',vv
            dizcancpadri={}
            lgen=[]
            dizemail={}
            lisaliqtransf=[]
            #lista con i diz
            listadizgenerale=vv['aliquots']
            for diz in listadizgenerale:
                genemail=[]              
                operat=diz['operator']
                mittente=User.objects.get(username=operat)
                ricevente=User.objects.get(username='benedetta.mussolin')
                #ricevente=User.objects.get(username='emanuele.geda')
                lisbarc=''
                listabarcgenerale=diz['vials']
                #diz con chiave il barc della madre e con valore una lista di diz che contengono i dati passati alla API
                for barc in listabarcgenerale:
                    lisbarc+=barc+'&'                
                    
                stringtot=lisbarc[:-1]
                print 'stringtot',stringtot
                diz=AllAliquotsContainer(stringtot)
                
                #salvo la transfschedule
                schedule=TransferSchedule(scheduleDate=date.today(),
                                          operator=mittente)
                schedule.save()
                corriere=Courier.objects.get(name='Internal')
                #creo il trasferimento
                trasf=Transfer(idTransferSchedule=schedule,
                              operator=mittente,
                              addressTo=ricevente,
                              departureDate=date.today(),
                              departureExecuted=1,
                              departureValidated=1,
                              idCourier=corriere)
                trasf.save()
                print 'transfer',trasf
                disable_graph()
                #per ogni barc creo un altransfsched
                for barc in listabarcgenerale:
                    lista=diz[barc]
                    #e' una lista in cui ogni valore e' una stringa formata da gen|barcode|posizione
                    #quando in un barc ci sono piu' aliquote allora devo fare questo ciclo for
                    #pero' per il plasma come in questo caso non dovrebbe succedere
                    for ll in lista:
                        ch=ll.split('|')
                        gen=ch[0]
                                        
                        al=Aliquot.objects.get(uniqueGenealogyID=gen,availability=1)
                        
                        altrans=AliquotTransferSchedule(idAliquot=al,
                                                        idTransfer=trasf)
                        altrans.save()
                        print 'aliqTrasferire',altrans
                        dizcancpadri[gen]=al.idAliquotType.abbreviation
                        lgen.append(gen)
                        genemail.append(gen)
                        dizemail[gen]=[ll]
                        lisaliqtransf.append(altrans)
                
                listareport,intest,dizcsv,inte=LastPartTransfer(request,'n',dizemail,lisaliqtransf)
                email = LASEmail (functionality='can_view_BBM_send_aliquots', wgString=get_WG_string())
                msg=['Samples transferring','','Sent to:\t'+ricevente.username,'Shipment date:\t'+str(date.today()),'','These aliquots have been sent:','N\tGenealogy ID\tBarcode\tPosition\tVolume(ul)']            
                aliquots=Aliquot.objects.filter(uniqueGenealogyID__in=genemail,availability=1)
                wgList=WG.objects.filter(id__in=Aliquot_WG.objects.filter(aliquot__in=aliquots).values_list('WG',flat=True).distinct())
                print 'wglist',wgList
                enable_graph()
                for wg in wgList:
                    print 'wg',wg
                    email.addMsg([wg.name], msg)
                    aliq=aliquots.filter(id__in=Aliquot_WG.objects.filter(WG=wg).values_list('aliquot',flat=True).distinct())
                    print 'aliq',aliq
                    i=1
                    #per mantenere l'ordine dei campioni anche nell'e-mail
                    for gen in genemail:
                        for al in aliq:
                            if gen==al.uniqueGenealogyID:
                                stringatab=dizcsv[al.uniqueGenealogyID]
                                email.addMsg([wg.name],[str(i)+'\t'+stringatab])
                                i=i+1
                    #mando l'e-mail al destinatario e al pianificatore
                    email.addRoleEmail([wg.name], 'Recipient', [ricevente.username])
                    email.addRoleEmail([wg.name], 'Executor', [mittente.username])
                try:
                    email.send()
                except Exception, e:
                    raise Exception
            
            storage=Urls.objects.get(default = '1').url
            #per cancellare il padre delle provette
            print 'diz',diz
            url = storage + '/api/canc/father/'
            val={'dizgen':json.dumps(dizcancpadri)}            
            print 'url',url
            data = urllib.urlencode(val)
            req = urllib2.Request(url,data=data, headers={"workingGroups" : 'admin'})
            u = urllib2.urlopen(req)
            res =  u.read()
            if res=='errore':
                raise Exception
            
            #per rendere indisponibili i container trasferiti
            url1 = storage + '/container/availability/'
            val1={'lista':json.dumps(lgen),'tube':'0','nome':'transfer'}
            print 'url1',url1
            data1 = urllib.urlencode(val1)
            req1 = urllib2.Request(url1,data=data1, headers={"workingGroups" : 'admin'})
            u = urllib2.urlopen(req1)
            res1 =  u.read()
            if res1=='err':
                raise Exception
            
            #per la condivisione dei campioni
            url = Urls.objects.get(idWebService=WebService.objects.get(name='LASAuthServer')).url + "/shareEntities/"
            data={'entitiesList':json.dumps(lgen),'user':ricevente.username}
    
            print 'urlLASAUTH',url
            data = urllib.urlencode(data)
            req = urllib2.Request(url,data=data, headers={"workingGroups" : 'admin'})
            u = urllib2.urlopen(req)
            res1 =  u.read()
            if res1=='error':
                print "error during sharing aliquots"
                raise Exception
            
            response = rc.ALL_OK
            response.content = json.dumps({'status':'200'})
            return response
        except Exception,e:
            print 'err',e
            #mando un'e-mail per segnalare l'errore
            inviaMailFunnel(e,json.loads(request.raw_post_data),"Error in 'Transfer vial' Funnel API")
            transaction.rollback()
            response = rc.BAD_REQUEST
            response.content = json.dumps({'status':'400'})
            return response

#serve per cambiare il codice paziente alle collezioni. Viene chiamata dal modulo clinico. 
class ChangeAliasHandler(BaseHandler):
    allowed_methods = ('POST')
    def create(self, request):
        try:
            print request.POST
            print request.raw_post_data
            #chiave il progetto e valore un dizionario con chiave il vecchio cod paziente e valore il nuovo cod paziente
            al=json.loads(request.raw_post_data)
            dictalias=al['dictalias']
            print 'dictalias',dictalias
            for prog,dizionario in dictalias.items():
                pr=CollectionProtocol.objects.get(project=prog)
                print 'diz',dizionario
                #e' il caso in cui ho una collezione che non aveva un cod paziente
                if '_|ic|_' in dizionario and '_|alias|_' in dizionario:
                    lisic=dizionario['_|ic|_']
                    newalias=dizionario['_|alias|_']
                    liscoll=Collection.objects.filter(collectionEvent__in=lisic,idCollectionProtocol=pr)
                    print 'liscoll',liscoll
                    for coll in liscoll:
                        coll.patientCode=newalias
                        print 'collection',coll
                        coll.save()
                else:
                    for oldalias,newalias in dizionario.items():
                        print 'oldalias',oldalias
                        liscoll=Collection.objects.filter(patientCode=oldalias,idCollectionProtocol=pr)
                        print 'liscoll',liscoll
                        for coll in liscoll:
                            coll.patientCode=newalias
                            print 'collection',coll
                            coll.save()
            return {'message':'ok'}
        except Exception,e:
            print 'err',e
            return {'message':'error'}
