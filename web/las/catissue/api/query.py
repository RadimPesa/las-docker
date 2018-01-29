from piston.handler import BaseHandler
from catissue.tissue.models import *
from django.core import serializers
from django.db import models
from django.http import HttpResponse
from django.db.models import Q
import operator,datetime
from catissue.api.utils import *
from catissue.tissue.utils import *
import urllib, urllib2, json,ast
from django.views.decorators.csrf import csrf_exempt
from catissue.tissue.genealogyID import *


#per caQuery. Restituisce tutti i collection type
class QueryCollTypeHandler(BaseHandler):
    allowed_methods = ('GET')
    def read(self, request):
        try:
            disable_graph()
            lista_tum=[]
            lista=CollectionType.objects.all()
            for l in lista:
                if l.longName not in lista_tum:
                    lista_tum.append(l.longName)
            return {'Collection Type':lista_tum}
        except:
            return {'data':'errore'}
        
#per caQuery. Restituisce tutti gli ospedali
class QuerySourceHandler(BaseHandler):
    allowed_methods = ('GET')
    def read(self, request):
        try:
            disable_graph()
            lista_source=[]
            lista=Source.objects.filter(type='Hospital')
            for l in lista:
                if l.name not in lista_source:
                    lista_source.append(l.name)
            return {'Source':lista_source}
        except:
            return {'data':'errore'}
        
#per caQuery. Restituisce tutti i tessuti umani
class QueryTissueHandler(BaseHandler):
    allowed_methods = ('GET')
    def read(self, request):
        try:
            disable_graph()
            lista_tess=[]
            lista=TissueType.objects.all()
            for l in lista:
                if l.longName not in lista_tess:
                    lista_tess.append(l.longName)
            return {'Tissue':lista_tess}
        except:
            return {'data':'errore'}
        
#per caQuery. Restituisce tutti i tessuti murini
class QueryTissueTypeHandler(BaseHandler):
    allowed_methods = ('GET')
    def read(self, request):
        try:
            disable_graph()
            lista_tess=[]
            lista=MouseTissueType.objects.all()
            for l in lista:
                if l.longName not in lista_tess:
                    lista_tess.append(l.longName)
            return {'Tissue Type':lista_tess}
        except:
            return {'data':'errore'}
        
#per caQuery. Restituisce tutti i tipi di aliquota
class QueryAliqTypeHandler(BaseHandler):
    allowed_methods = ('GET')
    def read(self, request):
        try:
            disable_graph()
            lista_aliq=[]
            lista=AliquotType.objects.all()
            for l in lista:
                if l.longName not in lista_aliq:
                    lista_aliq.append(l.longName)
            return {'Aliquot Type':lista_aliq}
        except:
            return {'data':'errore'}
        
#per caQuery. Restituisce tutti i protocolli di derivazione
class QueryNameHandler(BaseHandler):
    allowed_methods = ('GET')
    def read(self, request):
        try:
            disable_graph()
            lista_prot=[]
            lista=DerivationProtocol.objects.all()
            for l in lista:
                if l.name not in lista_prot:
                    lista_prot.append(l.name)
            return {'Name':lista_prot}
        except:
            return {'data':'errore'}
        
#per caQuery. Restituisce tutti i kit di derivazione
class QueryKitTypeHandler(BaseHandler):
    allowed_methods = ('GET')
    def read(self, request):
        try:
            disable_graph()
            lista_kit=[]
            lista=KitType.objects.all()
            for l in lista:
                if l.name not in lista_kit:
                    lista_kit.append(l.name)
            return {'Kit Type':lista_kit}
        except:
            return {'data':'errore'}
        
#per caQuery. Restituisce tutti i produttori di kit di derivazione
class QueryProducerHandler(BaseHandler):
    allowed_methods = ('GET')
    def read(self, request):
        try:
            disable_graph()
            lista_prod=[]
            lista=KitType.objects.all()
            for l in lista:
                if l.producer not in lista_prod: 
                    lista_prod.append(l.producer)
            return {'Producer':lista_prod}
        except:
            return {'data':'errore'}
        
#per caQuery. Restituisce tutti i tipi di esperimenti (es. sanger o rtPCR)
class QueryExpHandler(BaseHandler):
    allowed_methods = ('GET')
    def read(self, request):
        try:
            disable_graph()
            lista_exp=[]
            lista=Experiment.objects.all()
            for l in lista:
                if l.name not in lista_exp: 
                    lista_exp.append(l.name)
            return {'Experiment Type':lista_exp}
        except:
            return {'data':'errore'}

#per caQuery. API per le aliquote
class QueryAliquotsHandler(BaseHandler):
    allowed_methods = ('GET','POST')
    def read(self, request):
        return {'data':'ok'}
    def create(self, request):
        try:
            disable_graph()
            print request.POST
            sample_list=[]
            tipoal=[]
            lista1=[]
            lista2=[]
            lista3=[]
            aliq_list=[]
            listaaliqfinale=[]
            listaali=[]
            listaal=[]
            listacoll=[]
            l=[]
            
            predecess=request.POST.get('predecessor')
            print 'pred',predecess
            lista=request.POST.get('list')
            print 'lista',lista
            if lista!='':
                lis=ast.literal_eval(lista)
            
            successore=request.POST.get('successor')
            print 'successore',successore
            param=request.POST.get('parameter')
            print 'param',param
            val=request.POST.get('values')
            print 'val',val
            valori=val.split('|')
            
            #solo se la lista dei predecessori contiene degli elementi
            if lista!='' and len(lis)!=0:  
                #controllo chi e' il predecessore del blocchetto
                if predecess=='Aliquots':
                    #c'e' un predecessore
                    pred=True
                    listaid=lis['id']
                    for i in range(0,len(listaid)):
                        #print 'elem',listaid[i]
                        listaali.append( Q(**{'id': listaid[i]} ))
                    if len(listaali)!=0:
                        listaal=Aliquot.objects.filter(Q(reduce(operator.or_, listaali)))
    
                elif predecess=='Collections':
                    pred=True
                    listaid=lis['id']
                    for i in range(0,len(listaid)):
                        #print 'elem',listaid[i]
                        listacoll.append( Q(**{'id': listaid[i]} ))
                    if len(listacoll)!=0:
                        liscollezioni=Collection.objects.filter(Q(reduce(operator.or_, listacoll)))
                        print 'liscollezioni',liscollezioni
                        if len(liscollezioni)!=0:
                            for coll in liscollezioni:
                                lista1.append( Q(**{'idCollection': coll.id} ))
                            if len(lista1)!=0:
                                lissamp=SamplingEvent.objects.filter(reduce(operator.or_, lista1))
                                if len(lissamp)!=0:
                                    for samp in lissamp:
                                        lista2.append( Q(**{'idSamplingEvent': samp.id} ))
                                    if len(lista2)!=0:
                                        listaal=Aliquot.objects.filter(reduce(operator.or_, lista2))
                
                elif predecess=='Transform. Protocols':
                    pred=True
                    listaid=lis['id']
                    for i in range(0,len(listaid)):
                        #print 'elem',listaid[i]
                        lista1.append( Q(**{'id': listaid[i]} ))
                    if len(lista1)!=0:
                        liskit=Kit.objects.filter(Q(reduce(operator.or_, lista1)))
                        print 'liskit',liskit
                        if len(liskit)!=0:
                            del lista1[:]
                            for kit in liskit:
                                lista1.append( Q(**{'idKit': kit.id} ))
                            if len(lista1)!=0:
                                lisderevent=AliquotDerivationSchedule.objects.filter(reduce(operator.or_, lista1))
                            print 'lisder',lisderevent
                            if len(lisderevent)!=0:
                                for der in lisderevent:
                                    lista2.append( Q(**{'id': der.idAliquot.id} ))
                                if len(lista2)!=0:
                                    listaal=Aliquot.objects.filter(reduce(operator.or_, lista2))               

                elif predecess=='Transform. Events':
                    pred=True
                    listaid=lis['id']
                    for i in range(0,len(listaid)):
                        #print 'elem',listaid[i]
                        lista1.append( Q(**{'id': listaid[i]} ))    
                    if len(lista1)!=0:
                        listader=AliquotDerivationSchedule.objects.filter(Q(reduce(operator.or_, lista1))&Q(derivationExecuted=1))
                        print 'lis2',listader
                        if len(listader)!=0:
                            del lista1[:]
                            for dersched in listader:
                                if param=='GROUP BY':
                                    lista1.append(dersched.idAliquot.id)
                                else:
                                    #questo e' per i padri
                                    lista1.append( Q(**{'id': dersched.idAliquot.id} ))
                                #questo per le figlie
                                lista2.append( Q(**{'idAliqDerivationSchedule': dersched.id} ))
                            #ho gli idAliqDerivationSchedule e devo prendere i der event per poi
                            #avere i sampling event e quindi poi le aliq figlie
                            lisderevent=DerivationEvent.objects.filter(reduce(operator.or_, lista2))
                            if param=='GROUP BY':
                                for derev in lisderevent:
                                    if derev.idSamplingEvent!=None:
                                        lista3.append(derev.idSamplingEvent.id)
                                print 'lista3',len(lista3)
                                
                                if len(lista1)!=0:
                                    for x in lista1:
                                        aliqq=Aliquot.objects.filter(id=x)
                                        if len(aliqq)!=0:
                                            listaal.append(aliqq[0])
                                if len(lista3)!=0:
                                    for x in lista3:
                                        lista_aliq=Aliquot.objects.filter(idSamplingEvent=x)
                                        for aliq in lista_aliq:
                                            listaal.append(aliq)
                            else:     
                                if len(lisderevent)==0:
                                    lista3.append(Q(**{'id': '-1'}))
                                else:
                                    for derev in lisderevent:
                                        if derev.idSamplingEvent!=None:
                                            lista3.append(Q(**{'idSamplingEvent': derev.idSamplingEvent.id}))
                                        else:
                                            lista3.append(Q(**{'id': '-1'}))
                                print 'lista3',len(lista3)
                                if len(lista1)!=0:
                                    listaal=Aliquot.objects.filter(Q(reduce(operator.or_, lista1))|Q(reduce(operator.or_, lista3)))    
                            
                            '''for derev in listader:
                                #devo aggiungere alla lista delle aliq sia quelle
                                #padri che quelle figlie
                                #questo e' per prendere le aliq padre
                                lista1.append( Q(**{'id': derev.idAliquot.id} ))
                                #questo e' per le aliq figlie
                                if derev.idSamplingEvent!=None:
                                    lista3.append(Q(**{'idSamplingEvent': derev.idSamplingEvent.id}))
                            if len(lista1)!=0 :
                                listaal=Aliquot.objects.filter(Q(reduce(operator.or_, lista1))|Q(reduce(operator.or_, lista3)))'''
                
                elif predecess=='Containers':
                    pred=True
                    #ho la lista dei gen e devo restituire le aliquote contenute
                    lisgen=lis['genID']
                    for i in range(0,len(lisgen)):
                        lista1.append( Q(**{'uniqueGenealogyID': lisgen[i]} ))
                    if len(lista1)!=0:
                        listaal=Aliquot.objects.filter(Q(reduce(operator.or_, lista1)))
                
                elif predecess=='Genealogy ID_':
                    pred=True
                    listagen=lis['genID']
                    listemp=[]
                    for gen in listagen:
                        gennuovo=gen.replace('-','_')
                        lisaliq=Aliquot.objects.raw("select id from aliquot where uniqueGenealogyID like %s",[gennuovo])
                        #print 'lisaliq',lisaliq
                        for al in lisaliq:
                            listemp.append(al.id)
                    listaal=Aliquot.objects.filter(id__in=listemp)
                    '''listaliq=Aliquot.objects.all()
                    for al in listaliq:
                        ge=GenealogyID(al.uniqueGenealogyID)
                        for i in range(0,len(listagen)):
                            gen2=GenealogyID(listagen[i])
                            if gen2.compareGenIDs(ge):
                                #print 'gen2',gen2.getGenID()
                                lista1.append(Q(**{'id': al.id}))
                    if len(lista1)!=0:
                        listaal=Aliquot.objects.filter(Q(reduce(operator.or_, lista1)))'''
                
                elif predecess=='start':
                    pred=False
                #vuol dire che e' uno dei blocchi di un altro modulo
                else:
                    pred=True
                    listagen=lis['genID']
                    if param=='GROUP BY':
                        for i in range(0,len(listagen)):
                            listaali.append(listagen[i])
                        if len(listaali)!=0:
                            for x in listaali:
                                aliqq=Aliquot.objects.filter(uniqueGenealogyID=x)
                                if len(aliqq)!=0:
                                    listaal.append(aliqq[0])
                    else:
                        for i in range(0,len(listagen)):
                            #print 'elem',listagen[i]
                            listaali.append( Q(**{'uniqueGenealogyID': listagen[i]} ))
                        if len(listaali)!=0:
                            listaal=Aliquot.objects.filter(Q(reduce(operator.or_, listaali)))
                print 'list',listaal
            
            else:
                if predecess=='start':
                    pred=False
                else:
                    pred=True
            
            if val=='':
                if not pred:
                    listaaliqfinale=Aliquot.objects.all()
                else:
                    listaaliqfinale=listaal
            else:    
                del lista1[:]
                del lista2[:]
                del lista3[:]
                if param=='Tissue Type':
                    #devo convertire i nomi di tessuto nelle loro abbreviazioni
                    for i in range(0,len(valori)):
                        tess=MouseTissueType.objects.filter(longName=valori[i])
                        if len(tess)!=0:
                            lista3.append(tess[0].abbreviation)
                    #se filtro sui sampling event provenienti da las, non trovo le aliquote
                    #vitali fittizie inserite per tenere traccia degli impianti storici
                    
                    #prendo tutti i sampling event che hanno las come sorgente
                    #sorg=Source.objects.get(type='Las')
                    #listasamp=SamplingEvent.objects.filter(idSource=sorg)
                    #prendo tutte le aliquote provenienti da quei sampling event
                    #for sam in listasamp:
                        #aliq_list.append(Q(**{'idSamplingEvent': sam.id} ))
                        #if len(aliq_list)!=0:
                    if not pred:
                        #listaaliq=Aliquot.objects.filter(reduce(operator.or_, aliq_list))
                        listaaliq=Aliquot.objects.all()
                    else:
                        if len(listaal)!=0:
                            #listaaliq=listaal.filter(reduce(operator.or_, aliq_list))
                            listaaliq=listaal
                    if len(listaaliq)!=0:
                        #scandisco le aliq prendendo solo quelle il cui genid soddisfa
                        #i parametri
                        for al in listaaliq:
                            ge = GenealogyID(al.uniqueGenealogyID)
                            for i in range(0,len(lista3)):
                                if lista3[i]==ge.getTissueType():
                                    lista2.append(Q(**{'uniqueGenealogyID': al.uniqueGenealogyID} ))
                                    break
                        if len(lista2)!=0:
                            if not pred:
                                listaaliqfinale=Aliquot.objects.filter(reduce(operator.or_, lista2))
                            else:
                                if len(listaal)!=0:
                                    listaaliqfinale=listaal.filter(reduce(operator.or_, lista2))
                        
                elif param=='Aliquot Type':
                    for i in range(0,len(valori)):
                        tipoal.append( Q(**{'longName': valori[i]} ))
                    print 'tipoal',tipoal
                    tipi=AliquotType.objects.filter( reduce(operator.or_, tipoal) )
                    print 'tipi',tipi
                    if len(tipi)!=0:
                        for t in tipi:
                            print 't.id',t.id
                            aliq_list.append(Q(**{'idAliquotType': t.id} ))
                        if len(aliq_list)!=0:
                            if not pred:
                                listaaliqfinale=Aliquot.objects.filter(reduce(operator.or_, aliq_list))
                            else:
                                if len(listaal)!=0:
                                    listaaliqfinale=listaal.filter(reduce(operator.or_, aliq_list))
                
                elif param=='Aliquot Barcode':
                    stringalinee=''
                    for i in range(0,len(valori)):
                        stringalinee+=valori[i]+'&'
                    stringtot=stringalinee[:-1]
                    diz=AllAliquotsContainer(stringtot)
                    #diz ha chiave il barc passato e come valore una lista con tutte le aliq dentro quel container
                    #formata da gen|barc|posizione 
                    for key,val in diz.items():
                        for stringa in val:
                            ch=stringa.split('|')
                            lista1.append( Q(**{'uniqueGenealogyID': ch[0]} ))
                    print 'aliq_lista',lista1
                    if len(lista1)!=0:
                        if not pred:
                            listaaliqfinale=Aliquot.objects.filter(reduce(operator.or_, lista1))
                        else:
                            if len(listaal)!=0:
                                listaaliqfinale=listaal.filter(reduce(operator.or_, lista1))
                
                elif param=='Exhausted':
                    if valori[0]=='Yes':
                        disp=0
                    elif valori[0]=='No':
                        disp=1
                    if not pred:
                        listaaliqfinale=Aliquot.objects.filter(availability=disp)
                    else:
                        if len(listaal)!=0:
                            listaaliqfinale=listaal.filter(availability=disp)
                    
                elif param=='Operator':
                    for i in range(0,len(valori)):
                        lista1.append( Q(**{'operator': valori[i]} ))
                    print 'lista1',lista1
                    ser=Serie.objects.filter( Q(reduce(operator.or_, lista1)) )
                    print 'serie',ser
                    if len(ser)!=0:
                        for s in ser:
                            sample_list.append(Q(**{'idSerie': s.id} ))
                        if len(sample_list)!=0:
                            samp=SamplingEvent.objects.filter(reduce(operator.or_, sample_list))
                            print 'samp',samp
                            #prendo le aliq
                            if len(samp)!=0:
                                for sam in samp:
                                    aliq_list.append(Q(**{'idSamplingEvent': sam.id} ))
                                if len(aliq_list)!=0:
                                    if not pred:
                                        listaaliqfinale=Aliquot.objects.filter(reduce(operator.or_, aliq_list))
                                    else:
                                        if len(listaal)!=0:
                                            listaaliqfinale=listaal.filter(reduce(operator.or_, aliq_list))
                
                #mi arriva il parametro(<, >, =) seguito da _ e poi dal numero
                #ed eventualmente seguito da un'altra coppia operatore_numero
                elif param=='Date':
                    samp=[]
                    attr=valori[0].split('_')
                    if attr[0]=='<':
                        samp=SamplingEvent.objects.filter(samplingDate__lte=attr[1])
                    elif attr[0]=='>':
                        samp=SamplingEvent.objects.filter(samplingDate__gte=attr[1])
                    elif attr[0]=='=':
                        samp=SamplingEvent.objects.filter(samplingDate=attr[1])
                    print 'samp',samp
                    if len(valori)>1:
                        attr2=valori[1].split('_')
                        if attr2[0]=='<':
                            samp=samp.filter(samplingDate__lte=attr2[1])
                    if len(samp)!=0:
                        for sam in samp:
                            aliq_list.append(Q(**{'idSamplingEvent': sam.id} ))
                        if len(aliq_list)!=0:
                            if not pred:
                                listaaliqfinale=Aliquot.objects.filter(reduce(operator.or_, aliq_list))
                            else:
                                if len(listaal)!=0:
                                    listaaliqfinale=listaal.filter(reduce(operator.or_, aliq_list))
                
                elif param=='Aliquot Number':
                    #devo convertire la stringa che mi arriva aggiungendo uno zero
                    #davanti nel caso in cui ci sia una sola cifra
                    for i in range(0,len(valori)):
                        if len(valori[i])==1:
                            v='0'+str(valori[i])
                        else:
                            v=valori[i]
                        lista3.append(v)
                    if not pred:
                        listaaliq=Aliquot.objects.all()
                    else:
                        if len(listaal)!=0:
                            listaaliq=listaal
                    if len(listaaliq)!=0:
                        #scandisco le aliq prendendo solo quelle il cui genid soddisfa
                        #i parametri
                        for al in listaaliq:
                            ge = GenealogyID(al.uniqueGenealogyID)
                            for i in range(0,len(lista3)):
                                if lista3[i]==ge.getAliquotExtraction():
                                    lista2.append(Q(**{'uniqueGenealogyID': al.uniqueGenealogyID} ))
                                    break
                        if len(lista2)!=0:
                            if not pred:
                                listaaliqfinale=Aliquot.objects.filter(reduce(operator.or_, lista2))
                            else:
                                if len(listaal)!=0:
                                    listaaliqfinale=listaal.filter(reduce(operator.or_, lista2))

                elif param=='2nd Derivation Number':
                    #devo convertire la stringa che mi arriva aggiungendo uno zero
                    #davanti nel caso in cui ci sia una sola cifra
                    for i in range(0,len(valori)):
                        if len(valori[i])==1:
                            v='0'+str(valori[i])
                        else:
                            v=valori[i]
                        lista3.append(v)
                    if not pred:
                        listaaliq=Aliquot.objects.all()
                    else:
                        if len(listaal)!=0:
                            listaaliq=listaal
                    if len(listaaliq)!=0:
                        #scandisco le aliq prendendo solo quelle il cui genid soddisfa
                        #i parametri
                        for al in listaaliq:
                            ge = GenealogyID(al.uniqueGenealogyID)
                            for i in range(0,len(lista3)):
                                if lista3[i]==ge.get2DerivationGen():
                                    lista2.append(Q(**{'uniqueGenealogyID': al.uniqueGenealogyID} ))
                                    break
                        if len(lista2)!=0:
                            if not pred:
                                listaaliqfinale=Aliquot.objects.filter(reduce(operator.or_, lista2))
                            else:
                                if len(listaal)!=0:
                                    listaaliqfinale=listaal.filter(reduce(operator.or_, lista2))

                #valori in questo caso e' >_num1|<_num2 oppure <_num
                elif param=='Original Volume (ul)' or param=='Residual Volume (ul)':
                    if param=='Original Volume (ul)':
                        feat=Feature.objects.filter(name='OriginalVolume')
                    elif param=='Residual Volume (ul)':
                        feat=Feature.objects.filter(name='Volume')
                    for f in feat:
                        lista1.append(Q(**{'idFeature': f.id} ))
                    print 'lista1',lista1

                    lisfeat=[]
                    attr=valori[0].split('_')
                    vol=float(attr[1])
                    if attr[0]=='<':
                        lisfeat=AliquotFeature.objects.filter( Q(reduce(operator.or_, lista1))&Q(value__lte=vol))
                    elif attr[0]=='>':
                        lisfeat=AliquotFeature.objects.filter( Q(reduce(operator.or_, lista1))&Q(value__gte=vol))
                    elif attr[0]=='=':
                        lisfeat=AliquotFeature.objects.filter( Q(reduce(operator.or_, lista1))&Q(value=vol))
                    if len(valori)>1:
                        attr2=valori[1].split('_')
                        vo=float(attr2[1])
                        if attr2[0]=='<':
                            lisfeat=lisfeat.filter(value__lte=vo)

                    print 'lista feat',lisfeat
                    if len(lisfeat)!=0:
                        for sam in lisfeat:
                            aliq_list.append(Q(**{'id': sam.idAliquot.id} ))
                        print 'aliqlista',aliq_list
                        if len(aliq_list)!=0:
                            if not pred:
                                listaaliqfinale=Aliquot.objects.filter(reduce(operator.or_, aliq_list))
                            else:
                                if len(listaal)!=0:
                                    listaaliqfinale=listaal.filter(reduce(operator.or_, aliq_list))
                
                elif param=='Concentration (ng/ul)':
                    feat=Feature.objects.filter(name='Concentration')
                    for f in feat:
                        lista1.append(Q(**{'idFeature': f.id} ))
                    print 'lista1',lista1

                    lisfeat=[]
                    attr=valori[0].split('_')
                    vol=float(attr[1])
                    if attr[0]=='<':
                        lisfeat=AliquotFeature.objects.filter( Q(reduce(operator.or_, lista1))&Q(value__lte=vol))
                    elif attr[0]=='>':
                        lisfeat=AliquotFeature.objects.filter( Q(reduce(operator.or_, lista1))&Q(value__gte=vol))
                    elif attr[0]=='=':
                        lisfeat=AliquotFeature.objects.filter( Q(reduce(operator.or_, lista1))&Q(value=vol))
                    if len(valori)>1:
                        attr2=valori[1].split('_')
                        vo=float(attr2[1])
                        if attr2[0]=='<':
                            lisfeat=lisfeat.filter(value__lte=vo)

                    print 'lista feat',lisfeat
                    if len(lisfeat)!=0:
                        for sam in lisfeat:
                            aliq_list.append(Q(**{'id': sam.idAliquot.id} ))
                        print 'aliqlista',aliq_list
                        if len(aliq_list)!=0:
                            if not pred:
                                listaaliqfinale=Aliquot.objects.filter(reduce(operator.or_, aliq_list))
                            else:
                                if len(listaal)!=0:
                                    listaaliqfinale=listaal.filter(reduce(operator.or_, aliq_list))
                
                elif param=='Quantity (ug)':
                    featconc=Feature.objects.filter(name='Concentration')
                    featvol=Feature.objects.filter(name='Volume')
                    for f in featconc:
                        lista1.append(Q(**{'idFeature': f.id} ))
                    for f in featvol:
                        lista2.append(Q(**{'idFeature': f.id} ))
                    lisfeat=[]
                    attr=valori[0].split('_')
                    limite=float(attr[1])
                    #prendo tutti gli oggetti feature che hanno la concentrazione
                    lisconc=AliquotFeature.objects.filter(Q(reduce(operator.or_, lista1)))
                    print 'lisconc',lisconc
                    for conc in lisconc:
                        vol=AliquotFeature.objects.filter(Q(reduce(operator.or_, lista2))&Q(idAliquot=conc.idAliquot))
                        if len(vol)!=0 and vol[0].value!=-1:
                            quant=float((conc.value/1000)*vol[0].value)
                            #print 'quant',quant
                            #se ci sono due valori che definiscono un intervallo
                            if len(valori)>1:
                                attr2=valori[1].split('_')
                                limite2=float(attr2[1])
                                if attr2[0]=='<' and quant>=limite and quant<=limite2:
                                    lisfeat.append(conc)
                            #se c'e' un valore solo che fa da parametro
                            else:
                                if attr[0]=='<' and quant<=limite:
                                    lisfeat.append(conc)
                                elif attr[0]=='>' and quant>=limite:
                                    lisfeat.append(conc)
                                elif attr[0]=='=' and quant==limite:
                                    lisfeat.append(conc)
                    print 'lista feat',lisfeat
                    if len(lisfeat)!=0:
                        for sam in lisfeat:
                            aliq_list.append(Q(**{'id': sam.idAliquot.id} ))
                        print 'aliqlista',aliq_list
                        if len(aliq_list)!=0:
                            if not pred:
                                listaaliqfinale=Aliquot.objects.filter(reduce(operator.or_, aliq_list))
                            else:
                                if len(listaal)!=0:
                                    listaaliqfinale=listaal.filter(reduce(operator.or_, aliq_list))
                            
                elif param=='Quality (RIN)':
                    lista4=[]
                    #do' un valore iniziale fittizio
                    lista4.append(Q(**{'id': -1} ))
                    aliq_list.append(Q(**{'idSamplingEvent': -1} ))
                    #QualityEvent.objects.all().order_by('-misurationDate')
                    listatipomis=Measure.objects.filter(name='quality')
                    for i in range(0,len(listatipomis)):
                        lista2.append( Q(**{'idMeasure': listatipomis[i]} ))
                        
                    lismisure=[]
                    attr=valori[0].split('_')
                    limite=float(attr[1])
                    if attr[0]=='<':
                        lismisure=MeasurementEvent.objects.filter( Q(reduce(operator.or_, lista2))&Q(value__lte=limite))
                    elif attr[0]=='>':
                        lismisure=MeasurementEvent.objects.filter( Q(reduce(operator.or_, lista2))&Q(value__gte=limite))
                    elif attr[0]=='=':
                        lismisure=MeasurementEvent.objects.filter( Q(reduce(operator.or_, lista2))&Q(value=limite))
                    if len(valori)>1:
                        attr2=valori[1].split('_')
                        vo=float(attr2[1])
                        if attr2[0]=='<':
                            lismisure=lismisure.filter(value__lte=vo)

                    print 'lismisure',lismisure
                    if len(lismisure)!=0:
                        for mis in lismisure:
                            print 'mis',mis.idQualityEvent.id
                            lista1.append(Q(**{'id': mis.idQualityEvent.id}))
                        if len(lista1)!=0:
                            #prendo i quality event associati alle misure
                            listaqual=QualityEvent.objects.filter(reduce(operator.or_, lista1))
                            print 'listaqual',listaqual
                            if len(listaqual)!=0:
                                del lista2[:]
                                for qual in listaqual:
                                    if qual.idAliquotDerivationSchedule!=None:
                                        lista2.append(Q(**{'id': qual.idAliquotDerivationSchedule.id} ))
                                    #se e' una rivalutazione
                                    elif qual.idQualitySchedule!=None:
                                        lista4.append(Q(**{'id': qual.idAliquot.id} ))
                                #devo vedere che anche lista4 contenga qualcosa. >1 perche' c'e' l'elemento 
                                #fittizio iniziale        
                                if len(lista2)!=0 or len(lista4)>1:
                                    #prendo i derivation event associati ai quality event, da cui prendero' i
                                    #sampling event con le relative aliquote derivate create
                                    #non prendo il padre perche' la qualita' riguarda il singolo evento di 
                                    #derivazione che e' quindi collegato solo alle figlie
                                    if len(lista2)!=0:
                                        listaderevent=AliquotDerivationSchedule.objects.filter(reduce(operator.or_, lista2))
                                        print 'derevent',listaderevent
                                        if len(listaderevent)!=0:
                                            for der in listaderevent:
                                                #lista4.append( Q(**{'id': der.idAliquot.id} ))
                                                lista3.append( Q(**{'idAliqDerivationSchedule': der.id} ))
                                            lisderevent=DerivationEvent.objects.filter(reduce(operator.or_, lista3))
                                            print 'lis',lisderevent
                                            for derev in lisderevent:
                                                aliq_list.append(Q(**{'idSamplingEvent': derev.idSamplingEvent.id} ))
                                    print 'aliqlist',aliq_list
                                    if len(aliq_list)>1 or len(lista4)>1:
                                        if not pred:
                                            listaaliqf=Aliquot.objects.filter(Q(reduce(operator.or_, aliq_list))|Q(reduce(operator.or_, lista4)))
                                        else:
                                            if len(listaal)!=0:
                                                listaaliqf=listaal.filter(Q(reduce(operator.or_, aliq_list))|Q(reduce(operator.or_, lista4)))
                                        print 'listafin',listaaliqf   
                                        #devo vedere se in questa lista c'e' qualche aliquota che e' stata rivalutata
                                        #successivamente e che quindi non soddisfa piu' i parametri per essere presente
                                        tipomis=Measure.objects.get(Q(name='quality')&Q(measureUnit='RIN'))
                                        for al in listaaliqf:
                                            listaaliqfinale.append(al)
                                            rimosso=0
                                            #controllo che non debba toglierla perche' il suo sampling event magari raggruppa anche
                                            #altri campioni che devono stare in lista, ma questa non deve starci
                                            valor=float(TrovaQuality(al))
                                            print 'val',valor
                                            
                                            if len(valori)>1:
                                                attr2=valori[1].split('_')
                                                limite2=float(attr2[1])
                                                print 'limite',limite
                                                print 'limm2',limite2
                                                if attr2[0]=='<' and (valor<limite or valor>limite2):
                                                    listaaliqfinale.remove(al)
                                                    rimosso=1
                                            else:
                                                if attr[0]=='<' and valor>limite:
                                                    listaaliqfinale.remove(al)
                                                    rimosso=1
                                                elif attr[0]=='>' and valor<limite:
                                                    listaaliqfinale.remove(al)
                                                    rimosso=1
                                                elif attr[0]=='=' and valor!=limite:
                                                    listaaliqfinale.remove(al)
                                                    rimosso=1
                                            print 'rimosso',rimosso
                                            if not rimosso:        
                                                qualev=QualityEvent.objects.filter(Q(idAliquot=al)& ~Q(idQualitySchedule=None)).order_by('-misurationDate','-id')
                                                print 'qualev',qualev
                                                if len(qualev)!=0:
                                                    #in qualev[0] ho la rivalutazione piu' recente
                                                    qual=qualev[0]
                                                    #vedo il valore di questa rivalutazione
                                                    misev=MeasurementEvent.objects.filter(Q(idMeasure=tipomis)&Q(idQualityEvent=qual))
                                                    
                                                    if len(misev)!=0:
                                                        print 'val',misev[0].value
                                                        valor=misev[0].value
                                                        if len(valori)>1:
                                                            attr2=valori[1].split('_')
                                                            limite2=float(attr2[1])
                                                            if attr2[0]=='<' and (valor<limite or valor>limite2):
                                                                listaaliqfinale.remove(al)
                                                        else:
                                                            if attr[0]=='<' and valor>limite:
                                                                listaaliqfinale.remove(al)
                                                            elif attr[0]=='>' and valor<limite:
                                                                listaaliqfinale.remove(al)
                                                            elif attr[0]=='=' and valor!=limite:
                                                                listaaliqfinale.remove(al)
                                                    
            print 'lista',listaaliqfinale
                    
            #controllo chi e' il successore del blocchetto
            #se succ e' vero do' una lista di id interni, se e' falso do' una lista 
            #di genid
            if successore=='Aliquots' or successore=='Split Event' or successore=='Collections' or successore=='Transform. Protocols' or successore=='Transform. Events' or successore=='AND' or successore=='OR' or successore=='NOT IN':
                for ali in listaaliqfinale:
                    l.append(ali.id)
                print 'listaid',l
                return {'id':l}
            elif successore=='End':
                select=['uniqueGenealogyID','timesUsed','archiveDate','idSamplingEvent','idAliquotType','id']
                for ali in listaaliqfinale:
                    diz=ClassSimple(ali,select).getAttributes()
                    if ali.availability==True:
                        diz['Exhausted']='False'
                    elif ali.availability==False:
                        diz['Exhausted']='True'
                    #aggiungo la data di creazione del campione
                    diz['Sampling Date']=ali.idSamplingEvent.samplingDate
                    #guardo se il parametro era un filtro su vol, conc, quant o qual
                    if param=='Original Volume (ul)':
                        feat=Feature.objects.get(Q(name='OriginalVolume')&Q(idAliquotType=ali.idAliquotType))
                        aliqfeat=AliquotFeature.objects.get(Q(idAliquot=ali)&Q(idFeature=feat))
                        val=str(aliqfeat.value)
                        diz[param]=val
                    elif param=='Residual Volume (ul)':
                        feat=Feature.objects.get(Q(name='Volume')&Q(idAliquotType=ali.idAliquotType))
                        aliqfeat=AliquotFeature.objects.get(Q(idAliquot=ali)&Q(idFeature=feat))
                        val=str(aliqfeat.value)
                        diz[param]=val
                    elif param=='Concentration (ng/ul)':
                        feat=Feature.objects.get(Q(name='Concentration')&Q(idAliquotType=ali.idAliquotType))
                        aliqfeat=AliquotFeature.objects.get(Q(idAliquot=ali)&Q(idFeature=feat))
                        val=str(aliqfeat.value)
                        diz[param]=val
                    elif param=='Quantity (ug)':
                        featconc=Feature.objects.get(Q(name='Concentration')&Q(idAliquotType=ali.idAliquotType))
                        featvol=Feature.objects.get(Q(name='Volume')&Q(idAliquotType=ali.idAliquotType))
                        aliqconc=(AliquotFeature.objects.get(Q(idAliquot=ali)&Q(idFeature=featconc))).value
                        aliqvol=(AliquotFeature.objects.get(Q(idAliquot=ali)&Q(idFeature=featvol))).value
                        va=(aliqconc/1000)*aliqvol
                        val=str(round(va,2))
                        diz[param]=val
                    elif param=='Quality (RIN)':
                        '''#ho l'aliquota figlia di una derivazione e devo prendere il
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
                                    val=str(misev[0].value)'''
                        val=TrovaQuality(ali)
                        diz[param]=val
                    
                    l.append(diz)
                print 'listaend',l
                return {'objects':l}
            #nel caso abbia come successore il blocchetto Container dello storage
            elif successore=='Containers':
                for ali in listaaliqfinale:
                    l.append(ali.uniqueGenealogyID)
                print 'lista gen',l
                return {'id':l}
            else:
                for ali in listaaliqfinale:
                    l.append(ali.uniqueGenealogyID)
                print 'listagen',l
                return {'genID':l}
            
            #return {'Source':lista_source}
        except Exception, e:
            print 'ecc',e
            return {'data':'errore'}

#per caQuery. API per le collezioni
class QueryCollectionsHandler(BaseHandler):
    allowed_methods = ('GET','POST')
    def read(self, request):
        return {'data':'ok'}
    def create(self, request):
        try:
            disable_graph()
            listacoll=[]
            listacollfinale=[]
            l=[]
            lista1=[]
            lista2=[]
            tess_list=[]
            liscollezioni=[]
            
            print request.POST
            predecess=request.POST.get('predecessor')
            print 'pred',predecess
            lista=request.POST.get('list')
            print 'lista',lista
            if lista!='':
                lis=ast.literal_eval(lista)
            
            successore=request.POST.get('successor')
            print 'successore',successore
            param=request.POST.get('parameter')
            print 'param',param
            val=request.POST.get('values')
            print 'val',val
            valori=val.split('|')
            
            #solo se la lista dei predecessori contiene degli elementi
            if lista!='' and len(lis)!=0:  
                #controllo chi e' il predecessore del blocchetto. Per collections ci puo'
                #essere solo aliquots come altro predecessore
                if predecess=='Collections':
                    #c'e' un predecessore
                    pred=True
                    listaid=lis['id']
                    for i in range(0,len(listaid)):
                        #print 'elem',listaid[i]
                        listacoll.append( Q(**{'id': listaid[i]} ))
                    if len(listacoll)!=0:
                        liscollezioni=Collection.objects.filter(Q(reduce(operator.or_, listacoll)))
    
                elif predecess=='Aliquots':
                    pred=True
                    listaid=lis['id']
                    for i in range(0,len(listaid)):
                        #print 'elem',listaid[i]
                        listacoll.append( Q(**{'id': listaid[i]} ))
                    if len(listacoll)!=0:
                        listaal=Aliquot.objects.filter(Q(reduce(operator.or_, listacoll)))
                        print 'list',listaal
                        if len(listaal)!=0:
                            if param=='GROUP BY':
                                #ho le aliquote e devo risalire alle collezioni a cui appartengono
                                #lascio i duplicati per il group by
                                for al in listaal:
                                    lista1.append(al.idSamplingEvent.idCollection.id)
                                if len(lista1)!=0:
                                    for x in lista1:
                                        collec=Collection.objects.filter(id=x)
                                        if len(collec)!=0:
                                            liscollezioni.append(collec[0])
                            else:    
                                #ho le aliquote e devo risalire alle collezioni a cui appartengono
                                for al in listaal:
                                    lista1.append( Q(**{'id': al.idSamplingEvent.idCollection.id} ))
                                if len(lista1)!=0:
                                    liscollezioni=Collection.objects.filter(Q(reduce(operator.or_, lista1)))
                    
                elif predecess=='start':
                    pred=False
                #vuol dire che e' uno dei blocchi di un altro modulo
                else:
                    pred=True
                    listagen=lis['genID']
                    for i in range(0,len(listagen)):
                        g=GenealogyID(listagen[i])
                        tumore=CollectionType.objects.get(abbreviation=g.getOrigin())
                        collez=Collection.objects.get(Q(idCollectionType=tumore)&Q(itemCode=g.getCaseCode()))
                        if param=='GROUP BY':
                            lista1.append(collez)
                        else:
                            if collez not in lista1:
                                lista1.append(collez)
                    if len(lista1)!=0:
                        if param=='GROUP BY':
                            for el in lista1:
                                lista2.append(el.id)
                            if len(lista2)!=0:
                                for x in lista2:
                                    collec=Collection.objects.filter(id=x)
                                    if len(collec)!=0:
                                        liscollezioni.append(collec[0])
                        else:
                            for el in lista1:
                                lista2.append( Q(**{'id': el.id} ))
                            if len(lista2)!=0:
                                liscollezioni=Collection.objects.filter(Q(reduce(operator.or_, lista2)))
                        
                        '''listagenid.append( Q(**{'uniqueGenealogyID': listagen[i]} ))
                    if len(listagenid)!=0:
                        listaal=Aliquot.objects.filter(Q(reduce(operator.or_, listagenid)))
                        print 'list',listaal
                        if len(listaal)!=0:
                            #ho le aliquote e devo risalire alle collezioni a cui appartengono
                            for al in listaal:
                                lista1.append( Q(**{'id': al.idSamplingEvent.idCollection.id} ))
                            if len(lista1)!=0:
                                liscollezioni=Collection.objects.filter(Q(reduce(operator.or_, lista1)))'''
            
            else:
                if predecess=='start':
                    pred=False
                else:
                    pred=True
            
            print 'liscollezioni',liscollezioni
            
            if val=='':
                if not pred:
                    listacollfinale=Collection.objects.all()
                else:
                    listacollfinale=liscollezioni
            else:
                del lista1[:]
                del lista2[:]    
                if param=='Collection Event':
                    for i in range(0,len(valori)):
                        lista1.append( Q(**{'collectionEvent': valori[i]} ))
                    print 'lista',lista1
                    if not pred:
                        listacollfinale=Collection.objects.filter(reduce(operator.or_, lista1))
                    else:
                        if len(liscollezioni)!=0:
                            listacollfinale=liscollezioni.filter(reduce(operator.or_, lista1))
                
                elif param=='Collection Type':
                    for i in range(0,len(valori)):
                        lista1.append( Q(**{'longName': valori[i]} ))
                    listatum=CollectionType.objects.filter( Q(reduce(operator.or_, lista1)) )
                    if len(listatum)!=0:
                        for tum in listatum:
                            lista2.append(Q(**{'idCollectionType': tum.id} ))
                        if len(lista2)!=0:
                            if not pred:
                                listacollfinale=Collection.objects.filter(reduce(operator.or_, lista2))
                            else:
                                if len(liscollezioni)!=0:
                                    listacollfinale=liscollezioni.filter(reduce(operator.or_, lista2))
                
                elif param=='Item Code':
                    for i in range(0,len(valori)):
                        print 'valori',valori[i]
                        #solo se e' un numero lo metto nella lista
                        if valori[i].isdigit():
                            caso=int(valori[i])
                            #serve a mettere degli zeri davanti al numero del caso per formare il genealogy id
                            if caso<10:
                                caso='000'+str(caso)
                            elif caso <100:
                                caso='00'+str(caso)
                            elif caso <1000:
                                caso='0'+str(caso)
                        else:
                            caso=valori[i]
                        lista1.append( Q(**{'itemCode': caso} ))
                    print 'lista',lista1
                    if len(lista1)!=0:
                        if not pred:
                            listacollfinale=Collection.objects.filter(reduce(operator.or_, lista1))
                        else:
                            if len(liscollezioni)!=0:
                                listacollfinale=liscollezioni.filter(reduce(operator.or_, lista1))
                
                elif param=='Patient ID':
                    for i in range(0,len(valori)):
                        lista1.append( Q(**{'patientCode': valori[i]} ))
                    print 'lista',lista1
                    if not pred:
                        listacollfinale=Collection.objects.filter(reduce(operator.or_, lista1))
                    else:
                        if len(liscollezioni)!=0:
                            listacollfinale=liscollezioni.filter(reduce(operator.or_, lista1))
                
                elif param=='Source':
                    for i in range(0,len(valori)):
                        lista1.append( Q(**{'name': valori[i]} ))
                    print 'lista1',lista1
                    listasorg=Source.objects.filter( Q(reduce(operator.or_, lista1)) )
                    print 'l',listasorg
                    if len(listasorg)!=0:
                        for sorg in listasorg:
                            lista2.append(Q(**{'idSource': sorg.id} ))
                        if len(lista2)!=0:
                            if not pred:
                                listacollfinale=Collection.objects.filter(reduce(operator.or_, lista2))
                            else:
                                if len(liscollezioni)!=0:
                                    listacollfinale=liscollezioni.filter(reduce(operator.or_, lista2))
                
                elif param=='Operator':
                    for i in range(0,len(valori)):
                        lista1.append( Q(**{'operator': valori[i]} ))
                    print 'lista1',lista1
                    ser=Serie.objects.filter( Q(reduce(operator.or_, lista1)) )
                    print 'serie',ser
                    if len(ser)!=0:
                        for s in ser:
                            lista2.append(Q(**{'idSerie': s.id} ))
                        if len(lista2)!=0:
                            samp=SamplingEvent.objects.filter(reduce(operator.or_, lista2))
                            print 'samp',samp
                            print 'lungsamp',len(samp)
                            #prendo le aliq
                            if len(samp)!=0:
                                del lista1[:]
                                for sam in samp:
                                    lista1.append(Q(**{'id': sam.idCollection.id} ))
                                if len(lista1)!=0:
                                    if not pred:
                                        listacollfinale=Collection.objects.filter(reduce(operator.or_, lista1))
                                    else:
                                        if len(liscollezioni)!=0:
                                            listacollfinale=liscollezioni.filter(reduce(operator.or_, lista1))
                
                elif param=='Date':
                    attr=valori[0].split('_')
                    attr2=attr[1].split('-')
                    datarif=datetime.date(int(attr2[0]),int(attr2[1]),int(attr2[2]))
                    #se ho un intervallo di date
                    if len(valori)>1:
                        att=valori[1].split('_')
                        att2=att[1].split('-')
                        datarif2=datetime.date(int(att2[0]),int(att2[1]),int(att2[2]))
                    #prendo le collezioni e vedo qual e' la data di campionamento piu'
                    #vecchia
                    if len(liscollezioni)!=0:
                        l_coll=liscollezioni
                    else:
                        l_coll=Collection.objects.all()
                    for c in l_coll:
                        listasamp=SamplingEvent.objects.filter(idCollection=c).order_by('samplingDate')
                        if len(listasamp)!=0:
                            datasamp=listasamp[0].samplingDate
                            print 'datasamp',datasamp
                            if attr[0]=='<' and datasamp<datarif:
                                lista1.append(Q(**{'id': c.id} ))
                            elif attr[0]=='>' and datasamp>datarif:
                                if len(valori)>1:
                                    if att[0]=='<' and datasamp<datarif2:
                                        lista1.append(Q(**{'id': c.id} ))
                                else:
                                    lista1.append(Q(**{'id': c.id} ))
                            elif attr[0]=='=' and datasamp==datarif:
                                lista1.append(Q(**{'id': c.id} ))
                    
                    if len(lista1)!=0:
                        if not pred:
                            listacollfinale=Collection.objects.filter(reduce(operator.or_, lista1))
                        else:
                            if len(liscollezioni)!=0:
                                listacollfinale=liscollezioni.filter(reduce(operator.or_, lista1))
                    '''samp=[]
                    attr=valori[0].split('_')
                    if attr[0]=='<':
                        samp=SamplingEvent.objects.filter(samplingDate__lte=attr[1])
                    elif attr[0]=='>':
                        samp=SamplingEvent.objects.filter(samplingDate__gte=attr[1])
                    elif attr[0]=='=':
                        samp=SamplingEvent.objects.filter(samplingDate=attr[1])
                    if len(valori)>1:
                        attr2=valori[1].split('_')
                        if attr2[0]=='<':
                            samp=samp.filter(samplingDate__lte=attr2[1])
                    print 'samp',samp
                    #listasamp=SamplingEvent.objects.filter(idCollection=coll).order_by('samplingDate')
                        
                    if len(samp)!=0:
                        for sam in samp:
                            lista1.append(Q(**{'id': sam.idCollection.id} ))'''
                        
                
                elif param=='Tissue':
                    for i in range(0,len(valori)):
                        tess_list.append( Q(**{'longName': valori[i]} ))
                    tessuto=TissueType.objects.filter( Q(reduce(operator.or_, tess_list)) )
                    if len(tessuto)!=0:
                        #prendo i sampling event con quei tessuti
                        for t in tessuto:
                            print 't.id',t.id
                            lista1.append(Q(**{'idTissueType': t.id} ))
                        if len(lista1)!=0:
                            samp=SamplingEvent.objects.filter(reduce(operator.or_, lista1))
                            print 'samp',samp
                            #prendo le aliq
                            if len(samp)!=0:
                                for sam in samp:
                                    lista2.append(Q(**{'id': sam.idCollection.id} ))
                                if len(lista2)!=0:
                                    if not pred:
                                        listacollfinale=Collection.objects.filter(reduce(operator.or_, lista2))
                                    else:
                                        if len(liscollezioni)!=0:
                                            listacollfinale=liscollezioni.filter(reduce(operator.or_, lista2))
                 
            print 'lista',listacollfinale
            #controllo chi e' il successore del blocchetto
            #se e' un mio blocchetto do' una lista di id interni, se no do' una lista 
            #di genid
            if successore=='Aliquots' or successore=='Collections' or successore=='Transform. Protocols' or successore=='Transform. Events' or successore=='AND' or successore=='OR' or successore=='NOT IN':
                for coll in listacollfinale:
                    l.append(coll.id)
                print 'listaid',l
                return {'id':l}
            elif successore=='End':
                select=['itemCode','idCollectionType','idSource','collectionEvent','patientCode','idCollectionProtocol','id']
                for coll in listacollfinale:
                    diz=ClassSimple(coll,select).getAttributes()
                    #aggiungo il genid della collezione cioe' i primi 7 caratteri del gen
                    if coll.itemCode<10:
                        paz='000'+str(coll.itemCode)
                    elif coll.itemCode<100:
                        paz='00'+str(coll.itemCode)
                    elif coll.itemCode<1000:
                        paz='0'+str(coll.itemCode)
                    else:
                        paz=str(coll.itemCode)
                        
                    diz['Genealogy']=coll.idCollectionType.abbreviation+paz
                    #devo aggiungere la data di collezionamento che e' la data piu' vecchia
                    #fra le date degli eventi di collezionamento
                    #prendo tutti i sampling event collegati alla collezione
                    listasamp=SamplingEvent.objects.filter(idCollection=coll).order_by('samplingDate')
                    if len(listasamp)!=0:
                        diz['Collection Date']=listasamp[0].samplingDate
                        diz['Operator']=listasamp[0].idSerie.operator
                    else:
                        diz['Collection Date']='None'
                        diz['Operator']='None'
                    l.append(diz)
                print 'listaend',l
                return {'objects':l}
            else:
                del lista1[:]
                del lista2[:]
                for coll in listacollfinale:
                    lista1.append( Q(**{'idCollection': coll.id} ))
                if len(lista1)!=0:
                    lissamp=SamplingEvent.objects.filter(reduce(operator.or_, lista1))
                    if len(lissamp)!=0:
                        for samp in lissamp:
                            lista2.append( Q(**{'idSamplingEvent': samp.id} ))
                        if len(lista2)!=0:
                            listaaliq=Aliquot.objects.filter(reduce(operator.or_, lista2))
                            if len(listaaliq)!=0:
                                for al in listaaliq:
                                    l.append(al.uniqueGenealogyID)
                print 'listagen',l
                return {'genID':l}

        except Exception, e:
            print 'ecc',e
            return {'data':'errore'}
        
#per caQuery. API per i kit di derivazione
class QueryProtocolsHandler(BaseHandler):
    allowed_methods = ('GET','POST')
    def read(self, request):
        return {'data':'ok'}
    def create(self, request):
        try:
            disable_graph()
            listak=[]
            listagenid=[]
            listakitfinale=[]
            l=[]
            lista1=[]
            lista2=[]
            liskit=[]
            
            print request.POST
            predecess=request.POST.get('predecessor')
            print 'pred',predecess
            lista=request.POST.get('list')
            print 'lista',lista
            if lista!='':
                lis=ast.literal_eval(lista)
            
            successore=request.POST.get('successor')
            print 'successore',successore
            param=request.POST.get('parameter')
            print 'param',param
            val=request.POST.get('values')
            print 'val',val

            valori=val.split('|')
            
            #solo se la lista dei predecessori contiene degli elementi
            if lista!='' and len(lis)!=0:    
                #controllo chi e' il predecessore del blocchetto. Per protocols ci puo'
                #essere aliquots, events e protocols
                if predecess=='Transform. Protocols':
                    #c'e' un predecessore
                    pred=True
                    listaid=lis['id']
                    for i in range(0,len(listaid)):
                        #print 'elem',listaid[i]
                        listak.append( Q(**{'id': listaid[i]} ))
                    if len(listak)!=0:
                        liskit=Kit.objects.filter(Q(reduce(operator.or_, listak)))
    
                elif predecess=='Aliquots':
                    pred=True
                    listaid=lis['id']
                    for i in range(0,len(listaid)):
                        #print 'elem',listaid[i]
                        listak.append( Q(**{'id': listaid[i]} ))
                    if len(listak)!=0:
                        listaal=Aliquot.objects.filter(Q(reduce(operator.or_, listak)))
                        print 'list',listaal
                        if len(listaal)!=0:
                            #ho le aliquote e devo risalire ai kit che hanno trattato quell'aliquota
                            for al in listaal:
                                lista1.append( Q(**{'idAliquot': al.id} ))
                            if len(lista1)!=0:
                                lisderevent=AliquotDerivationSchedule.objects.filter(Q(reduce(operator.or_, lista1))&Q(derivationExecuted=1))
                                print 'lisderevent',lisderevent
                                if len(lisderevent)!=0:
                                    if param=='GROUP BY':
                                        for der in lisderevent:
                                            if der.idKit!=None:
                                                #ho i der event e devo prendere i kit corrispondenti
                                                lista2.append( der.idKit.id)
                                        if len(lista2)!=0:
                                            for x in lista2:
                                                kii=Kit.objects.filter(id=x)
                                                if len(kii)!=0:
                                                    liskit.append(kii[0])
                                    else:
                                        for der in lisderevent:
                                            if der.idKit!=None:
                                                #ho i der event e devo prendere i kit corrispondenti
                                                lista2.append( Q(**{'id': der.idKit.id} ))
                                        if len(lista2)!=0:
                                            liskit=Kit.objects.filter(Q(reduce(operator.or_, lista2)))
                                       
                elif predecess=='Transform. Events':
                    pred=True
                    listaid=lis['id']
                    for i in range(0,len(listaid)):
                        #print 'elem',listaid[i]
                        listak.append( Q(**{'id': listaid[i]} ))
                    if len(listak)!=0:
                        listader=AliquotDerivationSchedule.objects.filter(Q(reduce(operator.or_, listak))&Q(derivationExecuted=1))
                        #ho i der sched e devo risalire ai kit
                        print 'lder',listader
                        if param=='GROUP BY':
                            for der in listader:
                                if der.idKit!=None:
                                    lista2.append(der.idKit.id)
                            if len(lista2)!=0:
                                for x in lista2:
                                    kii=Kit.objects.filter(id=x)
                                    if len(kii)!=0:
                                        liskit.append(kii[0])
                        else:    
                            for der in listader:
                                if der.idKit!=None:
                                    lista2.append( Q(**{'id': der.idKit.id} ))
                            if len(lista2)!=0:
                                liskit=Kit.objects.filter(Q(reduce(operator.or_, lista2)))
                        
                elif predecess=='start':
                    pred=False
                #vuol dire che e' uno dei blocchi di un altro modulo
                else:
                    pred=True
                    listagen=lis['genID']
                    for i in range(0,len(listagen)):
                        #print 'elem',listagen[i]
                        listagenid.append( Q(**{'uniqueGenealogyID': listagen[i]} ))
                    if len(listagenid)!=0:
                        listaal=Aliquot.objects.filter(Q(reduce(operator.or_, listagenid)))
                        print 'list',listaal
                        if len(listaal)!=0:
                            #ho le aliquote e devo risalire ai kit che hanno trattato quell'aliquota
                            for al in listaal:
                                lista1.append( Q(**{'idAliquot': al.id} ))
                            if len(lista1)!=0:
                                lisderevent=AliquotDerivationSchedule.objects.filter(Q(reduce(operator.or_, lista1))&Q(derivationExecuted=1))
                                print 'lisderevent',lisderevent
                                if len(lisderevent)!=0:
                                    for der in lisderevent:
                                        if der.idKit!=None:
                                            #ho i der event e devo prendere i kit corrispondenti
                                            lista2.append( Q(**{'id': der.idKit.id} ))
                                        if len(lista2)!=0:
                                            liskit=Kit.objects.filter(Q(reduce(operator.or_, lista2)))
            else:
                if predecess=='start':
                    pred=False
                else:
                    pred=True
                    
            print 'liskit',liskit
            if val=='':
                if not pred:
                    listakitfinale=Kit.objects.all()
                else:
                    listakitfinale=liskit
            else:
                del lista1[:]
                del lista2[:]    
                if param=='Name':
                    for i in range(0,len(valori)):
                        lista1.append( Q(**{'name': valori[i]} ))
                    print 'lista',lista1
                    lisprot=DerivationProtocol.objects.filter(Q(reduce(operator.or_, lista1)))
                    print 'lisprot',lisprot
                    if len(lisprot)!=0:
                        for prot in lisprot:
                            lista2.append( Q(**{'idKitType': prot.idKitType.id} ))
                        print 'lista2',lista2
                        if len(lista2)!=0:
                            if not pred:
                                listakitfinale=Kit.objects.filter(reduce(operator.or_, lista2))
                            else:
                                if len(liskit)!=0:
                                    listakitfinale=liskit.filter(reduce(operator.or_, lista2))
                
                elif param=='Kit Type':
                    for i in range(0,len(valori)):
                        lista1.append( Q(**{'name': valori[i]} ))
                    print 'lista',lista1
                    listipikit=KitType.objects.filter(Q(reduce(operator.or_, lista1)))
                    print 'listipikit',listipikit
                    if len(listipikit)!=0:
                        for tipkit in listipikit:
                            lista2.append( Q(**{'idKitType': tipkit.id} ))
                        print 'lista2',lista2
                        if len(lista2)!=0:
                            if not pred:
                                listakitfinale=Kit.objects.filter(reduce(operator.or_, lista2))
                            else:
                                if len(liskit)!=0:
                                    listakitfinale=liskit.filter(reduce(operator.or_, lista2))
                    
                elif param=='Barcode':
                    for i in range(0,len(valori)):
                        lista1.append( Q(**{'barcode': valori[i]} ))
                    print 'lista',lista1
                    if not pred:
                        listakitfinale=Kit.objects.filter(reduce(operator.or_, lista1))
                    else:
                        if len(liskit)!=0:
                            listakitfinale=liskit.filter(reduce(operator.or_, lista1))
                
                elif param=='Lot Number':
                    for i in range(0,len(valori)):
                        lista1.append( Q(**{'lotNumber': valori[i]} ))
                    print 'lista',lista1
                    if not pred:
                        listakitfinale=Kit.objects.filter(reduce(operator.or_, lista1))
                    else:
                        if len(liskit)!=0:
                            listakitfinale=liskit.filter(reduce(operator.or_, lista1))
                             
                elif param=='Open Date':
                    if not pred:
                        lisk=Kit.objects.all()
                    else:
                        #liskit e' la lista di id che arriva dai blocchetti prima
                        lisk=liskit
                    if len(lisk)!=0:
                        attr=valori[0].split('_')
                        if attr[0]=='<':
                            listakitfinale=lisk.filter(~Q(openDate=None)&Q(openDate__lte=attr[1]))
                        elif attr[0]=='>':
                            listakitfinale=lisk.filter(~Q(openDate=None)&Q(openDate__gte=attr[1]))
                        elif attr[0]=='=':
                            listakitfinale=lisk.filter(~Q(openDate=None)&Q(openDate=attr[1]))
                        if len(valori)>1:
                            attr2=valori[1].split('_')
                            if attr2[0]=='<':
                                listakitfinale=listakitfinale.filter(~Q(openDate=None)&Q(openDate__lte=attr2[1]))
                
                elif param=='Expiry Date':
                    if not pred:
                        lisk=Kit.objects.all()
                    else:
                        #liskit e' la lista di id che arriva dai blocchetti prima
                        lisk=liskit
                    if len(lisk)!=0:
                        attr=valori[0].split('_')
                        if attr[0]=='<':
                            listakitfinale=lisk.filter(Q(expirationDate__lte=attr[1]))
                        elif attr[0]=='>':
                            listakitfinale=lisk.filter(Q(expirationDate__gte=attr[1]))
                        elif attr[0]=='=':
                            listakitfinale=lisk.filter(Q(expirationDate=attr[1]))
                        if len(valori)>1:
                            attr2=valori[1].split('_')
                            if attr2[0]=='<':
                                listakitfinale=listakitfinale.filter(Q(expirationDate__lte=attr2[1]))
                
                elif param=='Producer':
                    for i in range(0,len(valori)):
                        lista1.append( Q(**{'producer': valori[i]} ))
                    print 'lista',lista1
                    listipikit=KitType.objects.filter(Q(reduce(operator.or_, lista1)))
                    print 'listipikit',listipikit
                    if len(listipikit)!=0:
                        for tipkit in listipikit:
                            lista2.append( Q(**{'idKitType': tipkit.id} ))
                        print 'lista2',lista2
                        if len(lista2)!=0:
                            if not pred:
                                listakitfinale=Kit.objects.filter(reduce(operator.or_, lista2))
                            else:
                                if len(liskit)!=0:
                                    listakitfinale=liskit.filter(reduce(operator.or_, lista2))
            
            print 'listakitfinale',listakitfinale
            #controllo chi e' il successore del blocchetto
            #se e' un mio blocchetto do' una lista di id interni, se no do' una lista 
            #di genid
            if successore=='Aliquots' or successore=='Transform. Protocols' or successore=='Transform. Events' or successore=='AND' or successore=='OR' or successore=='NOT IN':
                for k in listakitfinale:
                    l.append(k.id)
                print 'listaid',l
                return {'id':l}
            elif successore=='End':
                select=['idKitType','barcode','openDate','expirationDate','remainingCapacity','lotNumber','id']
                for kit in listakitfinale:
                    diz=ClassSimple(kit,select).getAttributes()
                    l.append(diz)
                print 'listaend',l
                return {'objects':l}
            else:
                del lista1[:]
                del lista2[:]
                for kit in listakitfinale:
                    lista1.append( Q(**{'idKit': kit.id} ))
                if len(lista1)!=0:
                    lisderevent=AliquotDerivationSchedule.objects.filter(reduce(operator.or_, lista1))
                    print 'lisder',lisderevent
                    if len(lisderevent)!=0:
                        for der in lisderevent:
                            lista2.append( Q(**{'id': der.idAliquot.id} ))
                        if len(lista2)!=0:
                            listaaliq=Aliquot.objects.filter(reduce(operator.or_, lista2))
                            print 'listaaliq',listaaliq
                            if len(listaaliq)!=0:
                                for al in listaaliq:
                                    l.append(al.uniqueGenealogyID)
                print 'listagen',l
                return {'genID':l}
                
        except Exception, e:
            print 'ecc',e
            return {'data':'errore'}
        
#per caQuery. API per gli eventi di derivazione
class QueryEventsHandler(BaseHandler):
    allowed_methods = ('GET','POST')
    def read(self, request):
        return {'data':'ok'}
    def create(self, request):
        try:
            disable_graph()
            listak=[]
            listagenid=[]
            listaevfinale=[]
            l=[]
            lista1=[]
            lista2=[]
            lista3=[]
            liseve=[]
            
            print request.POST
            predecess=request.POST.get('predecessor')
            print 'pred',predecess
            lista=request.POST.get('list')
            print 'lista',lista
            if lista!='':
                lis=ast.literal_eval(lista)
            
            successore=request.POST.get('successor')
            print 'successore',successore
            param=request.POST.get('parameter')
            print 'param',param
            val=request.POST.get('values')
            print 'val',val

            valori=val.split('|')
            
            #solo se la lista dei predecessori contiene degli elementi
            if lista!='' and len(lis)!=0:        
                #controllo chi e' il predecessore del blocchetto. Per protocols ci puo'
                #essere aliquots, events e protocols
                if predecess=='Transform. Events':
                    #c'e' un predecessore
                    pred=True
                    listaid=lis['id']
                    for i in range(0,len(listaid)):
                        #print 'elem',listaid[i]
                        listak.append( Q(**{'id': listaid[i]} ))
                    if len(listak)!=0:
                        liseve=AliquotDerivationSchedule.objects.filter(Q(reduce(operator.or_, listak))&Q(deleteTimestamp=None))
                
                elif predecess=='Transform. Protocols':
                    pred=True
                    listaid=lis['id']
                    for i in range(0,len(listaid)):
                        #print 'elem',listaid[i]
                        listak.append( Q(**{'id': listaid[i]} ))
                    if len(listak)!=0:
                        liskit=Kit.objects.filter(Q(reduce(operator.or_, listak)))
                        if len(liskit)!=0:
                            #ho i kit e devo risalire agli aliquot derivation schedule che sono
                            #stati eseguiti con quel kit
                            for k in liskit:
                                lista1.append( Q(**{'idKit': k.id} ))
                            if len(lista1)!=0:
                                liseve=AliquotDerivationSchedule.objects.filter(Q(reduce(operator.or_, lista1))&Q(deleteTimestamp=None))
                
                elif predecess=='Aliquots':
                    pred=True
                    listaid=lis['id']
                    for i in range(0,len(listaid)):
                        #print 'elem',listaid[i]
                        listak.append( Q(**{'id': listaid[i]} ))
                    if len(listak)!=0:
                        listaal=Aliquot.objects.filter(Q(reduce(operator.or_, listak)))
                        print 'list',listaal
                        if len(listaal)!=0:
                            #ho le aliquote e devo risalire agli aliquot derivation schedule
                            #in cui quell'aliquota e' stata derivata oppure e' stata creata
                            #questo e' per prendere le aliq padre
                            for al in listaal:
                                lista1.append( Q(**{'idAliquot': al.id} ))
                                #questo e' per le aliq figlie
                                lista2.append(Q(**{'idSamplingEvent': al.idSamplingEvent.id}))
                            if len(lista2)!=0 :
                                print 'lista2',lista2
                                lisder=DerivationEvent.objects.filter(Q(reduce(operator.or_, lista2)))
                                print 'lisder',lisder
                                if len(lisder)==0:
                                    lista3.append(Q(**{'id': '-1'}))
                                else:
                                    for derev in lisder:
                                        print 'derev',derev
                                        lista3.append(Q(**{'id': derev.idAliqDerivationSchedule.id}))
                                print 'lista3',lista3
                                liseve=AliquotDerivationSchedule.objects.filter((Q(reduce(operator.or_, lista1))|Q(reduce(operator.or_, lista3)))&Q(deleteTimestamp=None))
                                                       
                elif predecess=='start':
                    pred=False
                #vuol dire che e' uno dei blocchi di un altro modulo
                else:
                    pred=True
                    listagen=lis['genID']
                    print 'listagen',listagen
                    for i in range(0,len(listagen)):
                        #print 'elem',listagen[i]
                        listagenid.append( Q(**{'uniqueGenealogyID': listagen[i]} ))
                    if len(listagenid)!=0:
                        listaal=Aliquot.objects.filter(Q(reduce(operator.or_, listagenid)))
                        print 'list',listaal
                        if len(listaal)!=0:
                            #ho le aliquote e devo risalire ai der event in cui quell'aliquota
                            #e' stata derivata oppure e' stata creata
                            #questo e' per prendere le aliq padre
                            for al in listaal:
                                lista1.append( Q(**{'idAliquot': al.id} ))
                                #questo e' per le aliq figlie
                                lista2.append(Q(**{'idSamplingEvent': al.idSamplingEvent.id}))
                            if len(lista2)!=0 :
                                lisder=DerivationEvent.objects.filter(Q(reduce(operator.or_, lista2)))
                                if len(lisder)==0:
                                    lista3.append(Q(**{'id': '-1'}))
                                else:
                                    for derev in lisder:
                                        print 'derev',derev
                                        lista3.append(Q(**{'id': derev.idAliqDerivationSchedule.id}))
                                liseve=AliquotDerivationSchedule.objects.filter((Q(reduce(operator.or_, lista1))|Q(reduce(operator.or_, lista3)))&Q(deleteTimestamp=None))
            else:
                if predecess=='start':
                    pred=False
                else:
                    pred=True
            
            print 'liseve',liseve
            if val=='':
                if not pred:
                    listaevfinale=AliquotDerivationSchedule.objects.filter(deleteTimestamp=None)
                else:
                    listaevfinale=liseve
            else:
                del lista1[:]
                del lista2[:]    
                if param=='Success/Failure':
                    if valori[0]=='Success':
                        par=0
                    elif valori[0]=='Failure':
                        par=1
                    print 'par',par
                    if not pred:
                        listaevfinale=AliquotDerivationSchedule.objects.filter(failed=par)
                    else:
                        if len(liseve)!=0:
                            listaevfinale=liseve.filter(failed=par)
                
                elif param=='Date':
                    if not pred:
                        leventi=DerivationEvent.objects.filter(~Q(idAliqDerivationSchedule=None))
                    else:
                        #liseve e' la lista di id che arriva dai blocchetti prima
                        ltemp=[]
                        for aliqder in liseve:
                            print 'derev',aliqder
                            ltemp.append(Q(**{'idAliqDerivationSchedule': aliqder.id}))
                        leventi=DerivationEvent.objects.filter(Q(reduce(operator.or_, ltemp)))
                    print 'leventi',leventi
                    if len(leventi)!=0:
                        attr=valori[0].split('_')
                        if attr[0]=='<':
                            listaev=leventi.filter(Q(derivationDate__lte=attr[1]))
                        elif attr[0]=='>':
                            listaev=leventi.filter(Q(derivationDate__gte=attr[1]))
                        elif attr[0]=='=':
                            listaev=leventi.filter(Q(derivationDate=attr[1]))
                        if len(valori)>1:
                            attr2=valori[1].split('_')
                            if attr2[0]=='<':
                                listaev=listaev.filter(Q(derivationDate__lte=attr2[1]))
                        if len(listaev)!=0:
                            for derev in listaev:
                                print 'derev',derev
                                lista1.append(Q(**{'id': derev.idAliqDerivationSchedule.id}))
                            listaevfinale=AliquotDerivationSchedule.objects.filter(Q(reduce(operator.or_, lista1)))
                            
                elif param=='Operator':
                    for i in range(0,len(valori)):
                        lista1.append( Q(**{'operator': valori[i]} ))
                    print 'lista1',lista1
                    if not pred:
                        listaderev=DerivationEvent.objects.filter( Q(reduce(operator.or_, lista1)) )
                    else:
                        lisder=DerivationEvent.objects.filter( Q(reduce(operator.or_, lista1)) )
                        listaderev=[]
                        for derevent in lisder:
                            if derevent.idAliqDerivationSchedule in liseve:
                                listaderev.append(derevent)
                    print 'listaderev',listaderev
                    if len(listaderev)!=0:
                        for derev in listaderev:
                            print 'derev',derev.idAliqDerivationSchedule.id
                            lista2.append(Q(**{'id': derev.idAliqDerivationSchedule.id}))
                        listaevfinale=AliquotDerivationSchedule.objects.filter(Q(reduce(operator.or_, lista2))|(Q(reduce(operator.or_, lista1))&Q(failed=1)))            
            
            print 'listaevfinale',listaevfinale
            #controllo chi e' il successore del blocchetto
            #se e' un mio blocchetto do' una lista di id interni, se no do' una lista 
            #di genid
            if successore=='Aliquots' or successore=='Transform. Protocols' or successore=='Transform. Events' or successore=='AND' or successore=='OR' or successore=='NOT IN':
                for k in listaevfinale:
                    l.append(k.id)
                print 'listaid',l
                return {'id':l}
            elif successore=='End':
                select=['idDerivationProtocol','idDerivedAliquotType','idAliquot','idKit','idDerivationSchedule','failed','loadQuantity','volumeOutcome','aliquotExhausted','derivationExecuted','id']
                for ev in listaevfinale:
                    print 'ev',ev.id
                    diz=ClassSimple(ev,select).getAttributes()
                    #devo prendere la data di derivazione dal derivation event se c'e'
                    #perche' se la derivazione e' fallita non c'e' la data
                    derevent=DerivationEvent.objects.filter(idAliqDerivationSchedule=ev.id)
                    if len(derevent)!=0:
                        diz['Derivation Date']=derevent[0].derivationDate
                        diz['Operator']=derevent[0].operator
                    else:
                        diz['Derivation Date']='None'
                        diz['Operator']='None'
                    l.append(diz)
                print 'listaend',l
                return {'objects':l}
            else:
                #devo restituire i genid delle aliquote padri e figlie
                del lista1[:]
                del lista2[:]
                for dersched in listaevfinale:
                    #questo e' per i padri
                    lista1.append( Q(**{'id': dersched.idAliquot.id} ))
                    #questo per le figlie
                    lista2.append( Q(**{'idAliqDerivationSchedule': dersched.id} ))
                #ho gli idAliqDerivationSchedule e devo prendere i der event per poi
                #avere i sampling event e quindi poi le aliq figlie
                lisderevent=DerivationEvent.objects.filter(reduce(operator.or_, lista2))
                for derev in lisderevent:
                    lista3.append(Q(**{'idSamplingEvent': derev.idSamplingEvent.id}))
                if len(lista1)!=0 and len(lista3)!=0:
                    listaal=Aliquot.objects.filter(Q(reduce(operator.or_, lista1))|Q(reduce(operator.or_, lista3)))    
                    print 'listaaliq',listaal
                    if len(listaal)!=0:
                        for al in listaal:
                            l.append(al.uniqueGenealogyID)
                print 'listagen',l
                return {'genID':l}
        except Exception, e:
            print 'ecc',e
            return {'data':'errore'}
        
#per caQuery. API per gli esperimenti
class QueryExperimentsHandler(BaseHandler):
    allowed_methods = ('GET','POST')
    def read(self, request):
        return {'data':'ok'}
    def create(self, request):
        try:
            disable_graph()
            listaexpfinale=[]
            l=[]
            lista1=[]
            lista2=[]
            lisexp=[]
            
            print request.POST
            predecess=request.POST.get('predecessor')
            print 'pred',predecess
            lista=request.POST.get('list')
            print 'lista',lista
            if lista!='':
                lis=ast.literal_eval(lista)
            
            successore=request.POST.get('successor')
            print 'successore',successore
            param=request.POST.get('parameter')
            print 'param',param
            val=request.POST.get('values')
            print 'val',val

            valori=val.split('|')
            
            #solo se la lista dei predecessori contiene degli elementi
            if lista!='' and len(lis)!=0:        
                #controllo chi e' il predecessore del blocchetto. 
                
                if predecess=='Aliquots':
                    pred=True
                                                       
                elif predecess=='start':
                    pred=False
                #vuol dire che e' uno dei blocchi di un altro modulo
                else:
                    pred=True
                    listagen=lis['genID']
                    print 'listagen',listagen
                    for i in range(0,len(listagen)):
                        #print 'elem',listagen[i]
                        lista1.append( Q(**{'uniqueGenealogyID': listagen[i]} ))
                    if len(lista1)!=0:
                        listaal=Aliquot.objects.filter(Q(reduce(operator.or_, lista1)))
                        for al in listaal:
                            lista2.append( Q(**{'idAliquot': al.id} ))
                            if len(lista2)!=0:
                                lisexp=AliquotExperiment.objects.filter(Q(reduce(operator.or_, lista2)))
            else:
                if predecess=='start':
                    pred=False
                else:
                    pred=True
            
            print 'lisexp',lisexp
            if val=='':
                if not pred:
                    listaexpfinale=AliquotExperiment.objects.all()
                else:
                    listaexpfinale=lisexp
            else:
                del lista1[:]
                del lista2[:]  
                
                if param=='Experiment Type':
                    for i in range(0,len(valori)):
                        lista1.append( Q(**{'name': valori[i]} ))
                    listaexpgen=Experiment.objects.filter( Q(reduce(operator.or_, lista1)) )
                    if len(listaexpgen)!=0:
                        for exp in listaexpgen:
                            lista2.append(Q(**{'idExperiment': exp.id} ))
                        if len(lista2)!=0:
                            if not pred:
                                listaexpfinale=AliquotExperiment.objects.filter(reduce(operator.or_, lista2))
                            else:
                                if len(lisexp)!=0:
                                    listaexpfinale=lisexp.filter(reduce(operator.or_, lista2))
                                      
                elif param=='Executed':
                    if valori[0]=='Yes':
                        disp=1
                    elif valori[0]=='No':
                        disp=0
                    if not pred:
                        listaexpfinale=AliquotExperiment.objects.filter(confirmed=disp)
                    else:
                        if len(lisexp)!=0:
                            listaexpfinale=lisexp.filter(confirmed=disp)
                
                elif param=='Date':
                    if not pred:
                        l_exper=AliquotExperiment.objects.all()
                    else:
                        #lisexp e' la lista di id che arriva dai blocchetti prima
                        l_exper=lisexp
                    print 'l_exper',l_exper
                    if len(l_exper)!=0:
                        attr=valori[0].split('_')
                        if attr[0]=='<':
                            listaev=l_exper.filter(Q(experimentDate__lte=attr[1]))
                        elif attr[0]=='>':
                            listaev=l_exper.filter(Q(experimentDate__gte=attr[1]))
                        elif attr[0]=='=':
                            listaev=l_exper.filter(Q(experimentDate=attr[1]))
                        if len(valori)>1:
                            attr2=valori[1].split('_')
                            if attr2[0]=='<':
                                listaev=listaev.filter(Q(experimentDate__lte=attr2[1]))
                        if len(listaev)!=0:
                            for espe in listaev:
                                print 'espe',espe
                                lista1.append(Q(**{'id': espe.id}))
                            listaexpfinale=AliquotExperiment.objects.filter(Q(reduce(operator.or_, lista1)))
                            
                elif param=='Operator':
                    for i in range(0,len(valori)):
                        lista1.append( Q(**{'operator': valori[i]} ))
                    print 'lista1',lista1
                    listaexp=AliquotExperiment.objects.filter(Q(reduce(operator.or_, lista1)))
                    print 'listaexp',listaexp
                    if len(listaexp)!=0:
                        for espe in listaexp:
                            lista2.append(Q(**{'id': espe.id}))
                        if not pred:
                            listaexpfinale=AliquotExperiment.objects.filter(Q(reduce(operator.or_, lista2)))
                        else:
                            if len(lisexp)!=0:
                                listaexpfinale=lisexp.filter(Q(reduce(operator.or_, lista2)))
            
            print 'listaexpfinale',listaexpfinale
            #controllo chi e' il successore del blocchetto
            #se e' un mio blocchetto do' una lista di id interni, se no do' una lista 
            #di genid
            if successore=='Aliquots' or successore=='AND' or successore=='OR' or successore=='NOT IN':
                for k in listaexpfinale:
                    l.append(k.id)
                print 'listaid',l
                return {'id':l}
            elif successore=='End':
                select=['idAliquot','idExperiment','takenValue','remainingValue','operator','experimentDate','aliquotExhausted','confirmed','notes']
                for exp in listaexpfinale:
                    print 'exp',exp.id
                    diz=ClassSimple(exp,select).getAttributes()
                    l.append(diz)
                print 'listaend',l
                return {'objects':l}
            else:
                #devo restituire i genid delle aliquote in questione
                del lista1[:]
                del lista2[:]
                for exp in listaexpfinale: 
                    l.append(exp.idAliquot.uniqueGenealogyID)
                print 'listagen',l
                return {'genID':l}
        except Exception, e:
            print 'ecc',e
            return {'data':'errore'}

#per caQuery. API per gli eventi di split dei derivati
class QuerySplitHandler(BaseHandler):
    allowed_methods = ('GET','POST')
    def read(self, request):
        return {'data':'ok'}
    def create(self, request):
        try:
            disable_graph()
            listak=[]
            listagenid=[]
            listaevfinale=[]
            l=[]
            lista1=[]
            lista2=[]
            liseve=[]
            
            print request.POST
            predecess=request.POST.get('predecessor')
            print 'pred',predecess
            lista=request.POST.get('list')
            print 'lista',lista
            if lista!='':
                lis=ast.literal_eval(lista)
            
            successore=request.POST.get('successor')
            print 'successore',successore
            param=request.POST.get('parameter')
            print 'param',param
            val=request.POST.get('values')
            print 'val',val

            valori=val.split('|')
            
            #solo se la lista dei predecessori contiene degli elementi
            if lista!='' and len(lis)!=0:        
                #controllo chi e' il predecessore del blocchetto. 
                if predecess=='Aliquots':
                    pred=True
                    listaid=lis['id']
                    for i in range(0,len(listaid)):
                        listak.append( Q(**{'id': listaid[i]} ))
                    if len(listak)!=0:
                        listaal=Aliquot.objects.filter(Q(reduce(operator.or_, listak)))
                        print 'list',listaal
                        if len(listaal)!=0:
                            #ho le aliquote e devo risalire agli aliquot split
                            #in cui quell'aliquota e' stata splittata oppure e' stata creata.
                            #Questo e' per prendere le aliq padre
                            for al in listaal:
                                lista1.append( Q(**{'idAliquot': al.id} ))
                                #questo e' per le aliq figlie
                                lista2.append(Q(**{'idSamplingEvent': al.idSamplingEvent.id}))
                            if len(lista2)!=0 :                               
                                liseve=AliquotSplitSchedule.objects.filter(Q(reduce(operator.or_, lista1))|Q(reduce(operator.or_, lista2)))
                                                       
                elif predecess=='start':
                    pred=False
                #vuol dire che e' uno dei blocchi di un altro modulo
                else:
                    pred=True
                    listagen=lis['genID']
                    print 'listagen',listagen
                    for i in range(0,len(listagen)):
                        #print 'elem',listagen[i]
                        listagenid.append( Q(**{'uniqueGenealogyID': listagen[i]} ))
                    if len(listagenid)!=0:
                        listaal=Aliquot.objects.filter(Q(reduce(operator.or_, listagenid)))
                        print 'list',listaal
                        if len(listaal)!=0:
                            #ho le aliquote e devo risalire agli aliquot split in cui quell'aliquota
                            #e' stata splittata oppure e' stata creata
                            #questo e' per prendere le aliq padre
                            for al in listaal:
                                lista1.append( Q(**{'idAliquot': al.id} ))
                                #questo e' per le aliq figlie
                                lista2.append(Q(**{'idSamplingEvent': al.idSamplingEvent.id}))
                            if len(lista2)!=0 :                                
                                liseve=AliquotSplitSchedule.objects.filter(Q(reduce(operator.or_, lista1))|Q(reduce(operator.or_, lista2)))
            else:
                if predecess=='start':
                    pred=False
                else:
                    pred=True
            
            print 'liseve',liseve
            if val=='':
                if not pred:
                    listaevfinale=AliquotSplitSchedule.objects.all()
                else:
                    listaevfinale=liseve
            else:
                del lista1[:]
                del lista2[:] 
                #da mettere a posto   
                if param=='Success/Failure':
                    if valori[0]=='Success':
                        par=0
                    elif valori[0]=='Failure':
                        par=1
                    print 'par',par
                    if not pred:
                        listaevfinale=AliquotSplitSchedule.objects.filter(failed=par)
                    else:
                        if len(liseve)!=0:
                            listaevfinale=liseve.filter(failed=par)            
            
            print 'listaevfinale',listaevfinale
            #controllo chi e' il successore del blocchetto
            #se e' un mio blocchetto do' una lista di id interni, se no do' una lista 
            #di genid
            if successore=='Aliquots' or successore=='Transform. Protocols' or successore=='Transform. Events' or successore=='AND' or successore=='OR' or successore=='NOT IN':
                for k in listaevfinale:
                    l.append(k.id)
                print 'listaid',l
                return {'id':l}
            elif successore=='End':
                select=['idAliquot','idSplitSchedule','idSamplingEvent','splitExecuted','id']
                for ev in listaevfinale:
                    diz=ClassSimple(ev,select).getAttributes()
                    l.append(diz)
                print 'listaend',l
                return {'objects':l}
            else:
                #devo restituire i genid delle aliquote padri e figlie
                del lista1[:]
                del lista2[:]
                for splitsched in listaevfinale:
                    #questo e' per i padri
                    lista1.append( Q(**{'id': splitsched.idAliquot.id} ))
                    #devo vedere se lo split e' stato eseguito
                    if splitsched.idSamplingEvent!=None:
                        #questo per le figlie
                        lista2.append( Q(**{'idSamplingEvent': splitsched.idSamplingEvent.id} ))
                if len(lista1)!=0 and len(lista2)!=0:
                    listaal=Aliquot.objects.filter(Q(reduce(operator.or_, lista1))|Q(reduce(operator.or_, lista2)))    
                    print 'listaaliq',listaal
                    if len(listaal)!=0:
                        for al in listaal:
                            l.append(al.uniqueGenealogyID)
                print 'listagen',l
                return {'genID':l}
        except Exception, e:
            print 'ecc',e
            return {'data':'errore'}
