# -*- coding: utf-8 -*-
from piston.handler import BaseHandler
from MMM.models import *
from django.core import serializers
from django.db import models
from django.http import HttpResponse
from django.db.models import Q
import operator,datetime
import urllib, urllib2, json,ast
from django.views.decorators.csrf import csrf_exempt
from utils import ClassSimple
from django.utils import simplejson


#per caQuery. Restituisce tutti i Chip Type
class QueryChipTypeHandler(BaseHandler):
    allowed_methods = ('GET')
    def read(self, request):
        try:
            lista_chip_type=[]
            lista=ChipType.objects.all()
            for l in lista:
                if l.title not in lista_chip_type:
                    lista_chip_type.append(l.title)
            return {'Chip Type':lista_chip_type}
        except:
            return {'data':'errore'}

#per caQuery. Autocompletamento        
class QueryChipOwnerHandler(BaseHandler):
    allowed_methods = ('GET')
    def read(self, request):
        try:
            print request.GET
            if 'q' in request.GET:
                chips = Chip.objects.filter(owner__icontains=request.GET.get('q'))[:10]
                res=[]
                for c in chips:
                    co = c.owner
                    if co not in res:
                        res.append(co)
                #print res
                return res
            return " "
        except Exception, e:
            print e
            print "[MMM][api query] - error ChipOwner autocomplete"

#per caQuery. Autocompletamento        
class QueryChipManufacturerHandler(BaseHandler):
    allowed_methods = ('GET')
    def read(self, request):
        try:
            print request.GET
            if 'q' in request.GET:
                chips = ChipType.objects.filter(manufacter__icontains=request.GET.get('q'))[:10]
                res=[]
                for c in chips:
                    cm = c.manufacter
                    if cm not in res:
                        res.append(cm)
                #print res
                return res
            return " "
        except Exception, e:
            print e
            print "[MMM][api query] - error ChipOwner autocomplete"

            
#per caQuery. Restituisce tutti gli Hybrid Protocol
class QueryHybProtocolHandler(BaseHandler):
    allowed_methods = ('GET')
    def read(self, request):
        try:
            lista_h_protocols=[]
            lista=HybProtocol.objects.all()
            for l in lista:
                if l.name not in lista_h_protocols:
                    lista_h_protocols.append(l.name)
            return {'Protocol':lista_h_protocols}
        except:
            return {'data':'errore'}
        
#per caQuery. Restituisce tutti gli Hybrid Protocol, ma con il nome parametro Name
class QueryHybProtocolNameHandler(BaseHandler):
    allowed_methods = ('GET')
    def read(self, request):
        try:
            lista_h_protocols=[]
            lista=HybProtocol.objects.all()
            for l in lista:
                if l.name not in lista_h_protocols:
                    lista_h_protocols.append(l.name)
            return {'Name':lista_h_protocols}
        except:
            return {'data':'errore'}


#per caQuery. Restituisce tutti gli Scan Protocol
class QueryScanProtocolHandler(BaseHandler):
    allowed_methods = ('GET')
    def read(self, request):
        try:
            lista_s_protocols=[]
            lista=ScanProtocol.objects.all()
            for l in lista:
                if l.name not in lista_s_protocols:
                    lista_s_protocols.append(l.name)
            return {'Protocol':lista_s_protocols}
        except:
            return {'data':'errore'}

  
        
#per caQuery. Restituisce tutti gli Hybrid Instruments
class QueryHybInstrumentHandler(BaseHandler):
    allowed_methods = ('GET')
    def read(self, request):
        try:
            lista_h_instruments=[]
            lista=Instrument.objects.filter(scan="0")
            for l in lista:
                if l.name not in lista_h_instruments:
                    lista_h_instruments.append(l.name)
            return {'Instrument':lista_h_instruments}
        except:
            return {'data':'errore'}
        
        
#per caQuery. Restituisce tutti gli Scan Software
class QuerySoftwareHandler(BaseHandler):
    allowed_methods = ('GET')
    def read(self, request):
        try:
            lista_soft=[]
            lista=Software.objects.all()
            for l in lista:
                if l.name not in lista_soft:
                    lista_soft.append(l.name)
            return {'Software':lista_soft}
        except:
            return {'data':'errore'}
        
        
#per caQuery. Restituisce tutti gli Scan Instrument
class QueryScanInstrumentHandler(BaseHandler):
    allowed_methods = ('GET')
    def read(self, request):
        try:
            lista_instr=[]
            lista=Instrument.objects.filter(scan="1")
            for l in lista:
                if l.name not in lista_instr:
                    lista_instr.append(l.name)
            return {'Instrument':lista_instr}
        except:
            return {'data':'errore'}


#per caQuery. Autocompletamento        
class QueryExGroupHandler(BaseHandler):
    allowed_methods = ('GET')
    def read(self, request):
        try:
            print request.GET
            if 'q' in request.GET:
                list = RawData_has_Group.objects.filter(group__icontains=request.GET.get('q'))[:10]
                res=[]
                for l in list:
                    eg = l.group
                    if eg not in res:
                        res.append(eg)
                #print res
                return res
            return " "
        except Exception, e:
            print e
            print "[MMM][api query] - error ChipOwner autocomplete"


#per caQuery. Autocompletamento        
class QueryRawDataOwnerHandler(BaseHandler):
    allowed_methods = ('GET')
    def read(self, request):
        try:
            print request.GET
            if 'q' in request.GET:
                list = Aliquot.filter(owner__icontains=request.GET.get('q'))[:10]
                res=[]
                for l in list:
                    ow = l.owner
                    if ow not in res:
                        res.append(ow)
                #print res
                return res
            return " "
        except Exception, e:
            print e
            print "[MMM][api query] - error ChipOwner autocomplete"


#per caQuery. Autocompletamento        
class QueryExperimentHandler(BaseHandler):
    allowed_methods = ('GET')
    def read(self, request):
        try:
            print request.GET
            if 'q' in request.GET:
                list = Experiment.filter(title__icontains=request.GET.get('q'))[:10]
                res=[]
                for l in list:
                    ex = l.title
                    if ex not in res:
                        res.append(ex)
                #print res
                return res
            return " "
        except Exception, e:
            print e
            print "[MMM][api query] - error ChipOwner autocomplete"

#per caQuery. Autocompletamento        
class QueryProjectHandler(BaseHandler):
    allowed_methods = ('GET')
    def read(self, request):
        try:
            print request.GET
            if 'q' in request.GET:
                list = Project.filter(title__icontains=request.GET.get('q'))[:10]
                res=[]
                for l in list:
                    pr = l.title
                    if pr not in res:
                        res.append(pr)
                #print res
                return res
            return " "
        except Exception, e:
            print e
            print "[MMM][api query] - error ChipOwner autocomplete"


#per caQuery. API per i Chip
class QueryChipsHandler(BaseHandler):
    allowed_methods = ('GET','POST')
    def read(self, request):
        return {'data':'ok'}
    def create(self, request):
        try:
            print "[MMM][api query] ", request.POST
            
            listachips = []
            chip_list = []
            listachipsfinale = []
            l=[]
            
            pred = False
            
            predecess=request.POST.get('predecessor')
            print '[MMM][api query] - pred',predecess
            lista=request.POST.get('list')
            print '[MMM][api query] - lista',lista
            if lista!='':
                lis=ast.literal_eval(lista)
            
            successore=request.POST.get('successor')
            print '[MMM][api query] - successore',successore
            param=request.POST.get('parameter')
            print '[MMM][api query] - param',param
            val=request.POST.get('values')
            print '[MMM][api query] - val',val
            valori=val.split('|')
            
            #solo se la lista dei predecessori contiene degli elementi
            if lista!='' and len(lis)!=0:  
                #controllo chi e' il predecessore del blocchetto
                
                if predecess=='Aliquots':
                    lista1=[]
                    lista_al=[]
                    lista2=[]
                    lista_ass=[]
                    lista3=[]
                    pred=True
                    listagen=lis['genID']
                    #print listagen
                    print '[MMM][api query] - pred: Aliquots'
                    for i in range(0,len(listagen)):
                        #print 'elem',listaid[i]
                        lista1.append( Q(**{'genId': listagen[i]} ))
                    if len(lista1)!=0:
                        lista_al=Aliquot.objects.filter(reduce(operator.or_, lista1))
                        if len(lista_al)!=0:
                            for a in lista_al:
                                lista2.append( Q(**{'idAliquot': a.id} ))
                            if len(lista2)!=0:
                                lista_ass=Assignment.objects.filter(reduce(operator.or_, lista2))
                                
                                if len(lista_ass)!=0:
                                    for a in lista_ass:
                                        lista3.append( Q(**{'id': a.idChip.id} ))
                                    if len(lista3)!=0:
                                        chip_list=Chip.objects.filter(reduce(operator.or_, lista3))
                                        #print chip_list                            
                    
                
                elif predecess=='Chips':
                    pred=True
                    listaid=lis['id']
                    print '[MMM][api query] - pred: Chips'
                    for i in range(0,len(listaid)):
                        #print 'elem',listaid[i]
                        listachips.append( Q(**{'id': listaid[i]} ))
                    if len(listachips)!=0:
                        chip_list=Chip.objects.filter(Q(reduce(operator.or_, listachips)))
    
                  
                elif predecess=='Hybrid. Events':
                    lista1 = []
                    listaeventi = []
                    pred=True
                    listaid=lis['id']
                    print '[MMM][api query] - pred: Hybrid. Events'
                    for i in range(0,len(listaid)):
                        listaeventi.append( Q(**{'id': listaid[i]} ))
                    if len(listaeventi)!=0:
                        event_list=HybEvent.objects.filter(Q(reduce(operator.or_, listaeventi)))
                        if len(event_list)!=0:
                            for e in event_list:
                                lista1.append( Q(**{'idHybEvent': e.id} ))
                            if len(lista1)!=0:
                                chip_list=Chip.objects.filter(reduce(operator.or_, lista1))
                                #print chip_list
                        
                
                elif predecess=='Scan Events':
                    lista1=[]
                    lista2=[]
                    listaeventi = []
                    lista_ass_2 = []
                    lista_ass3 = []
                    pred=True
                    listaid=lis['id']
                    print '[MMM][api query] - pred: Scan Events'
                    for i in range(0,len(listaid)):
                        listaeventi.append( Q(**{'id': listaid[i]} ))
                    if len(listaeventi)!=0:
                        event_list=ScanEvent.objects.filter(Q(reduce(operator.or_, listaeventi)))
                        if len(event_list)!=0:
                            for e in event_list:
                                lista1.append( Q(**{'idScanEvent': e.id} ))
                            if len(lista1)!=0:
                                lista_ass=Assignment_has_Scan.objects.filter(reduce(operator.or_, lista1))
                                #print lista_ass
                                for a in lista_ass:
                                    lista_ass_2.append(Q(**{'id': a.idAssignment.id} ))
                                    if len(lista_ass_2)!=0:
                                        lista_ass3=Assignment.objects.filter(reduce(operator.or_, lista_ass_2))
                                
                                for b in lista_ass3:
                                    lista2.append( Q(**{'id': b.idChip.id} ))
                                if len(lista2)!=0:
                                    chip_list=Chip.objects.filter(reduce(operator.or_, lista2))
                                    #print chip_list
                        
                
                elif predecess=='Raw Data':
                    
                    lista1=[]
                    lista2=[]
                    listaraw = []
                    pred=True
                    listaid=lis['id']
                    lista_ass=[]
                    print '[MMM][api query] - pred: Raw Data'
                    for i in range(0,len(listaid)):
                        listaraw.append( Q(**{'id': listaid[i]} ))
                    if len(listaraw)!=0:
                        raw_list=RawData.objects.filter(Q(reduce(operator.or_, listaraw)))
                        if len(raw_list)!=0:
                            
                            if param=='GROUP BY':
                                countoccurr = []
                                print "[MMM][api query] - GROUP BY"
                                for r in raw_list:
                                    lista_ass.append(r.idAssignment)
                                #print lista_ass
                                for a in lista_ass:
                                    lista2.append(a.idChip.id)
                                if len(lista2)!=0:
                                    for x in lista2:    
                                        countoccurr.append(Chip.objects.get(id=x))
                                    #print "countoccurr"
                                    #print countoccurr
                                    chip_list = countoccurr
                            else:
                                for r in raw_list:
                                    lista_ass.append(r.idAssignment)
                                #print lista_ass
                                for a in lista_ass:
                                    lista2.append( Q(**{'id': a.idChip.id} ))
                                if len(lista2)!=0:
                                    chip_list=Chip.objects.filter(reduce(operator.or_, lista2))
                                    #print chip_list
                        
                #elif predecess=='start': #non serve, se il predecess e' start allora non ho niente in list
                #    pred=False
                
                #vuol dire che e' uno dei blocchi di un altro modulo
                    
                print '[MMM][api query] - list',chip_list
            
            else:
                if predecess=='start':
                    pred=False
                
            if val=='':
                if not pred:
                    listachipsfinale=Chip.objects.all()
                else:
                    listachipsfinale=chip_list
            else:   
                print "[MMM][api query] - ci sono valori" 
                if param=='Barcode':
                    lista1 = []
                    for i in range(0,len(valori)):
                        lista1.append( Q(**{'barcode':valori[i]} ))
                    if len(lista1)!=0:
                        if not pred:
                            listachipsfinale=Chip.objects.filter(reduce(operator.or_, lista1))
                        else:
                            if len(chip_list)!=0:
                                listachipsfinale=chip_list.filter(reduce(operator.or_, lista1))                
                
                elif param=='Expiry Date':
                    lista1 = []
                    
                    query = Chip.objects.all()
                    if len(valori) == 1:
                        value = valori[0].split('_')
                        if value[0] == '>':
                            query = query.filter(expirationDate__gte = value[1])
                        elif value[0] == '=':
                            query = query.filter(expirationDate = value[1])
                        elif value[0] == '<':
                            query = query.filter(expirationDate__lte = value[1])
                    else:
                        for v in valori:
                            value = v.split('_')
                            if value[0] == '>':
                                query = query.filter(expirationDate__gte = value[1])
                            elif value[0] == '=':
                                query = query.filter(expirationDate = value[1])
                            elif value[0] == '<':
                                query = query.filter(expirationDate__lte = value[1])
                    
                    for q in query:
                        lista1.append( Q(**{'id':q.id}))
                        
                    if len(lista1)!=0:
                        if not pred:
                            listachipsfinale=Chip.objects.filter(reduce(operator.or_, lista1))
                        else:
                            if len(chip_list)!=0:
                                listachipsfinale=chip_list.filter(reduce(operator.or_, lista1))                
                    
                    
                
                elif param=='Owner':
                    lista1 = []
                    for i in range(0,len(valori)):
                        lista1.append( Q(**{'owner':valori[i]} ))
                    
                    if len(lista1)!=0:
                        if not pred:
                            listachipsfinale=Chip.objects.filter(reduce(operator.or_, lista1))
                        else:
                            if len(chip_list)!=0:
                                listachipsfinale=chip_list.filter(reduce(operator.or_, lista1))                
                
                
                elif param=='Batch Number':
                    lista1 = []
                    for i in range(0,len(valori)):
                        lista1.append( Q(**{'batchNumber':valori[i]} ))
                    
                    if len(lista1)!=0:
                        if not pred:
                            listachipsfinale=Chip.objects.filter(reduce(operator.or_, lista1))
                        else:
                            if len(chip_list)!=0:
                                listachipsfinale=chip_list.filter(reduce(operator.or_, lista1))                
                
                
                elif param=='Chip Type':
                    lista1 = []
                    lista2 = []
                    
                    for i in range(0,len(valori)):
                        lista1.append( Q(**{'title':valori[i]} ))
                    if len(lista1)!=0:
                        chip_types = ChipType.objects.filter(reduce(operator.or_, lista1))
                    if len(chip_types)!=0:
                        for c in chip_types:
                            lista2.append(Q(idChipType = c))
                        if not pred:
                            listachipsfinale=Chip.objects.filter(reduce(operator.or_, lista2))
                        else:
                            if len(chip_list)!=0:
                                listachipsfinale=chip_list.filter(reduce(operator.or_, lista2))                
                
                
                elif param=='Manufacturer':
                    lista1 = []
                    lista2 = []
                    for i in range(0,len(valori)):
                        lista1.append( Q(**{'manufacter':valori[i]} ))
                    if len(lista1)!=0:
                        type_list = ChipType.objects.filter(Q(reduce(operator.or_, lista1)))
                    if len(type_list)!=0:
                        for t in type_list:
                            lista2.append(Q(idChipType = t))               
                        if not pred:
                            listachipsfinale=Chip.objects.filter(reduce(operator.or_, lista2))
                        else:
                            if len(chip_list)!=0:
                                listachipsfinale=chip_list.filter(reduce(operator.or_, lista2))                
                
                
                elif param=='Organism':
                    lista1 = []
                    lista2 = []
                    for i in range(0,len(valori)):
                        lista1.append( Q(**{'organism':valori[i]} ))
                    if len(lista1)!=0:
                        type_list = ChipType.objects.filter(Q(reduce(operator.or_, lista1)))
                    if len(type_list)!=0:
                        for t in type_list:
                            lista2.append(Q(idChipType = t))               
                        if not pred:
                            listachipsfinale=Chip.objects.filter(reduce(operator.or_, lista2))
                        else:
                            if len(chip_list)!=0:
                                listachipsfinale=chip_list.filter(reduce(operator.or_, lista2))                
                
                
                elif param=='Number of Positions':
                    argument_list = []
                    if len(valori) == 1:
                        value = valori[0].split('_')
                        p = int(value[1])
                        query = ChipType.objects.all()
                        for c in query:
                            numberofpos = int(c.numberPositions)
                            if value[0] == '>':
                                if numberofpos >= p:
                                    argument_list.append(Q(idChipType = c ))
                            elif value[0] == '=':
                                if numberofpos == p:
                                    argument_list.append(Q(idChipType = c ))
                            elif value[0] == '<':
                                if numberofpos <= p:
                                    argument_list.append(Q(idChipType = c ))
                        if len(argument_list)!=0:
                            if not pred:
                                listachipsfinale=Chip.objects.filter(reduce(operator.or_, argument_list))
                            else:
                                if len(chip_list)!=0:
                                    listachipsfinale=chip_list.filter(reduce(operator.or_, argument_list))                
                    
                    else:
                        v = valori
                        valueF = v[0].split('_')
                        valueT = v[1].split('_')
                        
                        valueF = int(valueF[1])
                        valueT = int(valueT[1])
                        
                        query = ChipType.objects.all()
                        
                        for c in query:
                            numberofpos = int(c.numberPositions)
                            if valueF <= numberofpos and valueT >= numberofpos:
                                argument_list.append(Q(idChipType = c ))
                        if len(argument_list)!=0:
                            if not pred:
                                listachipsfinale=Chip.objects.filter(reduce(operator.or_, argument_list))
                            else:
                                if len(chip_list)!=0:
                                    listachipsfinale=chip_list.filter(reduce(operator.or_, argument_list))                
                
                
                elif param=='Number of Probes':
                    argument_list = []
                    if len(valori) == 1:
                        value = valori[0].split('_')
                        p = int(value[1])
                        query = ChipType.objects.all()
                        for c in query:
                            numberofpos = int(c.probesNumber)    
                            if value[0] == '>':
                                if numberofpos >= p:
                                    argument_list.append(Q(idChipType = c))
                            elif value[0] == '=':
                                if numberofpos == p:
                                    argument_list.append(Q(idChipType = c))
                            elif value[0] == '<':
                                if numberofpos <= p:
                                    argument_list.append(Q(idChipType = c))
                        if len(argument_list)!=0:
                            if not pred:
                                listachipsfinale=Chip.objects.filter(reduce(operator.or_, argument_list))
                            else:
                                if len(chip_list)!=0:
                                    listachipsfinale=chip_list.filter(reduce(operator.or_, argument_list))                
                
                    else:
                        v = valori
                        valueF = v[0].split('_')
                        valueT = v[1].split('_')
                        
                        valueF = int(valueF[1])
                        valueT = int(valueT[1])
                        
                        query = ChipType.objects.all()
                        
                        for c in query:
                            numberofpos = int(c.probesNumber)
                            if valueF <= numberofpos and valueT >= numberofpos:
                                argument_list.append(Q(idChipType = c ))
                        
                        if len(argument_list)!=0:
                            if not pred:
                                listachipsfinale=Chip.objects.filter(reduce(operator.or_, argument_list))
                            else:
                                if len(chip_list)!=0:
                                    listachipsfinale=chip_list.filter(reduce(operator.or_, argument_list))                
                
                
                
            #controllo chi e' il successore del blocchetto
            #se succ e' vero do' una lista di id interni, se e' falso do' una lista 
            #di genid
            if successore=='Chips' or successore=='Hybrid. Events' or successore=='Scan Events' or successore=='Raw Data' or successore=='AND' or successore=='OR' or successore=='NOT IN':
                for a in listachipsfinale:
                    l.append(a.id)
                print '[MMM][api query] - listaid',l
                return {'id':l}
            elif successore=='End':
                select=['idChipType','idHybEvent','barcode','expirationDate','dmapFile','owner','batchNumber','notes']
                for a in listachipsfinale:
                    l.append(ClassSimple(a,select).getAttributes())
                print '[MMM][api query] - listaend',l
                return {'objects':l}
            #nel caso abbia come successore il blocchetto Aliquots
            elif successore=='Aliquots': 
                lista1=[]
                lista2=[]
                al_list_ = []
                l = []
                lista_ass = []
                for c in listachipsfinale:
                    lista1.append(Q(**{'idChip': c.id} ))               
                    if len(lista1)!=0:
                        lista_ass = Assignment.objects.filter(Q(reduce(operator.or_, lista1)))
                        #print lista_ass
                for a in lista_ass:
                    al_list_.append(Aliquot.objects.get(id = a.idAliquot.id)) #li mando duplicati per permettere il group by
                                
                for c in al_list_:
                    if c.genId:
                        l.append(c.genId)
                print '[MMM][api query] - listagen',l
                return {'genID':l}
            
        except Exception, e:
            print '[MMM][api query] - ecc',e
            return {'data':'errore'}

    
#per caQuery. API per i protocolli di ibridazione
class QueryHybProtocolsHandler(BaseHandler):
    allowed_methods = ('GET','POST')
    def read(self, request):
        return {'data':'ok'}
    def create(self, request):
        try:
            print "[MMM][api query] ", request.POST
            
            listaprotocols = []
            protocols_list = []
            listaprotocolsfinale = []
            l=[]
            
            pred = False
            
            predecess=request.POST.get('predecessor')
            print '[MMM][api query] - pred',predecess
            lista=request.POST.get('list')
            print '[MMM][api query] - lista',lista
            if lista!='':
                lis=ast.literal_eval(lista)
            
            successore=request.POST.get('successor')
            print '[MMM][api query] - successore',successore
            param=request.POST.get('parameter').encode('cp1252', 'ignore')
            print '[MMM][api query] - param',param
            val=request.POST.get('values')
            print '[MMM][api query] - val',val
            valori=val.split('|')
            
            #solo se la lista dei predecessori contiene degli elementi
            if lista!='' and len(lis)!=0:  
                #controllo chi e' il predecessore del blocchetto
                
                if predecess=='Hybrid. Protocols':
                    listaprotocols_ = []
                    pred=True
                    listaid=lis['id']
                    print '[MMM][api query] - pred: Hybrid. Protocols'
                    for i in range(0,len(listaid)):
                        listaprotocols_.append( Q(**{'id': listaid[i]} ))
                    if len(listaprotocols_)!=0:
                        protocols_list=HybProtocol.objects.filter(Q(reduce(operator.or_, listaprotocols_)))
    
                elif predecess=='Hybrid. Events':
                    listaevents = []
                    lista_ev = []
                    listaprotocols_ = []
                    pred=True
                    listaid=lis['id']
                    print '[MMM][api query] - pred: Hybrid. Events'
                    
                    if param=='GROUP BY':
                        countoccurr = []
                        print "[MMM][api query] - GROUP BY"
                        
                        for i in range(0,len(listaid)):
                            e = HybEvent.objects.get(id = listaid[i])
                            countoccurr.append(e.idHybProtocol)
                            
                        protocols_list = countoccurr
                    
                    else:
                    
                        for i in range(0,len(listaid)):
                            listaevents.append( Q(**{'id': listaid[i]} ))
                        if len(listaevents)!=0:
                            lista_ev=HybEvent.objects.filter(Q(reduce(operator.or_, listaevents)))
                            for e in lista_ev:
                                listaprotocols_.append( Q(**{'id': e.idHybProtocol.id} ))
                            
                            protocols_list=HybProtocol.objects.filter(Q(reduce(operator.or_, listaprotocols_)))
        
                        
                print '[MMM][api query] - list',protocols_list
            
            else:
                if predecess=='start':
                    pred=False
                
            if val=='':
                if not pred:
                    listaprotocolsfinale=HybProtocol.objects.all()
                else:
                    listaprotocolsfinale=protocols_list
            else:   
                print "[MMM][api query] - ci sono valori" 
                
                if param=='Name':
                    lista1 = []
                    protocolli = []
                    for i in range(0,len(valori)):
                        lista1.append( Q(**{'name':valori[i]} ))
                    if len(lista1)!=0:
                        if not pred:
                            listaprotocolsfinale = HybProtocol.objects.filter(reduce(operator.or_, lista1))
                        else:
                            if len(protocols_list)!=0:
                                listaprotocolsfinale=protocols_list.filter(reduce(operator.or_, lista2))  
                
                elif param=='Hybridization Time (hours)':
                    argument_list = []
                    if len(valori) == 1:
                        value = valori[0].split('_')
                        p = int(value[1])
                        query = HybProtocol.objects.all()
                        for c in query:
                            ore = int(c.hybTime)
                            if value[0] == '>':
                                if ore >= p:
                                    argument_list.append(Q(id = c.id))
                            elif value[0] == '=':
                                if ore == p:
                                    argument_list.append(Q(id = c.id))
                            elif value[0] == '<':
                                if ore <= p:
                                    argument_list.append(Q(id = c.id))
                        if len(argument_list)!=0:
                            if not pred:
                                listaprotocolsfinale=HybProtocol.objects.filter(reduce(operator.or_, argument_list))
                            else:
                                if len(protocols_list)!=0:
                                    listaprotocolsfinale=protocols_list.filter(reduce(operator.or_, argument_list))                
                    
                    else:
                        v = valori
                        valueF = v[0].split('_')
                        valueT = v[1].split('_')
                        
                        valueF = int(valueF[1])
                        valueT = int(valueT[1])
                        
                        query = HybProtocol.objects.all()
                        
                        for c in query:
                            ore = int(c.hybTime)
                            if valueF <= ore and valueT >= ore:
                                argument_list.append(Q(id = c.id))
                        if len(argument_list)!=0:
                            if not pred:
                                listaprotocolsfinale=HybProtocol.objects.filter(reduce(operator.or_, argument_list))
                            else:
                                if len(protocols_list)!=0:
                                    listaprotocolsfinale=protocol_list.filter(reduce(operator.or_, argument_list))                
                
                              
                elif param=='Denaturation Time (min)':
                    argument_list = []
                    if len(valori) == 1:
                        value = valori[0].split('_')
                        p = int(value[1])
                        query = HybProtocol.objects.all()
                        for c in query:
                            ore = int(c.denTime)
                            if value[0] == '>':
                                if ore >= p:
                                    argument_list.append(Q(id = c.id))
                            elif value[0] == '=':
                                if ore == p:
                                    argument_list.append(Q(id = c.id))
                            elif value[0] == '<':
                                if ore <= p:
                                    argument_list.append(Q(id = c.id))
                        if len(argument_list)!=0:
                            if not pred:
                                listaprotocolsfinale=HybProtocol.objects.filter(reduce(operator.or_, argument_list))
                            else:
                                if len(protocols_list)!=0:
                                    listaprotocolsfinale=protocols_list.filter(reduce(operator.or_, argument_list))                
                    
                    else:
                        v = valori
                        valueF = v[0].split('_')
                        valueT = v[1].split('_')
                        
                        valueF = int(valueF[1])
                        valueT = int(valueT[1])
                        
                        query = HybProtocol.objects.all()
                        
                        for c in query:
                            ore = int(c.denTime)
                            if valueF <= ore and valueT >= ore:
                                argument_list.append(Q(id = c.id))
                        if len(argument_list)!=0:
                            if not pred:
                                listaprotocolsfinale=HybProtocol.objects.filter(reduce(operator.or_, argument_list))
                            else:
                                if len(protocols_list)!=0:
                                    listaprotocolsfinale=protocol_list.filter(reduce(operator.or_, argument_list))                
                
                    
                elif param=='Load Quantity (ng)':
                    argument_list = []
                    if len(valori) == 1:
                        value = valori[0].split('_')
                        p = int(value[1])
                        query = HybProtocol.objects.all()
                        for c in query:
                            ore = int(c.loadQuantity)
                            if value[0] == '>':
                                if ore >= p:
                                    argument_list.append(Q(id = c.id))
                            elif value[0] == '=':
                                if ore == p:
                                    argument_list.append(Q(id = c.id))
                            elif value[0] == '<':
                                if ore <= p:
                                    argument_list.append(Q(id = c.id))
                        if len(argument_list)!=0:
                            if not pred:
                                listaprotocolsfinale=HybProtocol.objects.filter(reduce(operator.or_, argument_list))
                            else:
                                if len(protocols_list)!=0:
                                    listaprotocolsfinale=protocols_list.filter(reduce(operator.or_, argument_list))                
                    
                    else:
                        v = valori
                        valueF = v[0].split('_')
                        valueT = v[1].split('_')
                        
                        valueF = int(valueF[1])
                        valueT = int(valueT[1])
                        
                        query = HybProtocol.objects.all()
                        
                        for c in query:
                            ore = int(c.loadQuantity)
                            if valueF <= ore and valueT >= ore:
                                argument_list.append(Q(id = c.id))
                        if len(argument_list)!=0:
                            if not pred:
                                listaprotocolsfinale=HybProtocol.objects.filter(reduce(operator.or_, argument_list))
                            else:
                                if len(protocols_list)!=0:
                                    listaprotocolsfinale=protocol_list.filter(reduce(operator.or_, argument_list))                
                
                    
                elif param=='Hybridization Temperature (C)':
                    argument_list = []
                    if len(valori) == 1:
                        value = valori[0].split('_')
                        p = int(value[1])
                        query = HybProtocol.objects.all()
                        for c in query:
                            ore = int(c.hybridTemp)
                            if value[0] == '>':
                                if ore >= p:
                                    argument_list.append(Q(id = c.id))
                            elif value[0] == '=':
                                if ore == p:
                                    argument_list.append(Q(id = c.id))
                            elif value[0] == '<':
                                if ore <= p:
                                    argument_list.append(Q(id = c.id))
                        if len(argument_list)!=0:
                            if not pred:
                                listaprotocolsfinale=HybProtocol.objects.filter(reduce(operator.or_, argument_list))
                            else:
                                if len(protocols_list)!=0:
                                    listaprotocolsfinale=protocols_list.filter(reduce(operator.or_, argument_list))                
                    
                    else:
                        v = valori
                        valueF = v[0].split('_')
                        valueT = v[1].split('_')
                        
                        valueF = int(valueF[1])
                        valueT = int(valueT[1])
                        
                        query = HybProtocol.objects.all()
                        
                        for c in query:
                            ore = int(c.hybridTemp)
                            if valueF <= ore and valueT >= ore:
                                argument_list.append(Q(id = c.id))
                        if len(argument_list)!=0:
                            if not pred:
                                listaprotocolsfinale=HybProtocol.objects.filter(reduce(operator.or_, argument_list))
                            else:
                                if len(protocols_list)!=0:
                                    listaprotocolsfinale=protocol_list.filter(reduce(operator.or_, argument_list))                
                
                    
                elif param=='Denaturation Temperature (C)':
                    argument_list = []
                    if len(valori) == 1:
                        value = valori[0].split('_')
                        p = int(value[1])
                        query = HybProtocol.objects.all()
                        for c in query:
                            ore = int(c.denTemp)
                            if value[0] == '>':
                                if ore >= p:
                                    argument_list.append(Q(id = c.id))
                            elif value[0] == '=':
                                if ore == p:
                                    argument_list.append(Q(id = c.id))
                            elif value[0] == '<':
                                if ore <= p:
                                    argument_list.append(Q(id = c.id))
                        if len(argument_list)!=0:
                            if not pred:
                                listaprotocolsfinale=HybProtocol.objects.filter(reduce(operator.or_, argument_list))
                            else:
                                if len(protocols_list)!=0:
                                    listaprotocolsfinale=protocols_list.filter(reduce(operator.or_, argument_list))                
                    
                    else:
                        v = valori
                        valueF = v[0].split('_')
                        valueT = v[1].split('_')
                        
                        valueF = int(valueF[1])
                        valueT = int(valueT[1])
                        
                        query = HybProtocol.objects.all()
                        
                        for c in query:
                            ore = int(c.denTemp)
                            if valueF <= ore and valueT >= ore:
                                argument_list.append(Q(id = c.id))
                        if len(argument_list)!=0:
                            if not pred:
                                listaprotocolsfinale=HybProtocol.objects.filter(reduce(operator.or_, argument_list))
                            else:
                                if len(protocols_list)!=0:
                                    listaprotocolsfinale=protocol_list.filter(reduce(operator.or_, argument_list))                
                
                    
                    
                elif param=='Hybridization Buffer (ul)':
                    argument_list = []
                    if len(valori) == 1:
                        value = valori[0].split('_')
                        p = int(value[1])
                        query = HybProtocol.objects.all()
                        for c in query:
                            ore = int(c.hybBuffer)
                            if value[0] == '>':
                                if ore >= p:
                                    argument_list.append(Q(id = c.id))
                            elif value[0] == '=':
                                if ore == p:
                                    argument_list.append(Q(id = c.id))
                            elif value[0] == '<':
                                if ore <= p:
                                    argument_list.append(Q(id = c.id))
                        if len(argument_list)!=0:
                            if not pred:
                                listaprotocolsfinale=HybProtocol.objects.filter(reduce(operator.or_, argument_list))
                            else:
                                if len(protocols_list)!=0:
                                    listaprotocolsfinale=protocols_list.filter(reduce(operator.or_, argument_list))                
                    
                    else:
                        v = valori
                        valueF = v[0].split('_')
                        valueT = v[1].split('_')
                        
                        valueF = int(valueF[1])
                        valueT = int(valueT[1])
                        
                        query = HybProtocol.objects.all()
                        
                        for c in query:
                            ore = int(c.hybBuffer)
                            if valueF <= ore and valueT >= ore:
                                argument_list.append(Q(id = c.id))
                        if len(argument_list)!=0:
                            if not pred:
                                listaprotocolsfinale=HybProtocol.objects.filter(reduce(operator.or_, argument_list))
                            else:
                                if len(protocols_list)!=0:
                                    listaprotocolsfinale=protocol_list.filter(reduce(operator.or_, argument_list))                
                
                    
                    
                elif param=='Total Volume (ul)':
                    argument_list = []
                    if len(valori) == 1:
                        value = valori[0].split('_')
                        p = int(value[1])
                        query = HybProtocol.objects.all()
                        for c in query:
                            ore = int(c.totalVolume)
                            if value[0] == '>':
                                if ore >= p:
                                    argument_list.append(Q(id = c.id))
                            elif value[0] == '=':
                                if ore == p:
                                    argument_list.append(Q(id = c.id))
                            elif value[0] == '<':
                                if ore <= p:
                                    argument_list.append(Q(id = c.id))
                        if len(argument_list)!=0:
                            if not pred:
                                listaprotocolsfinale=HybProtocol.objects.filter(reduce(operator.or_, argument_list))
                            else:
                                if len(protocols_list)!=0:
                                    listaprotocolsfinale=protocols_list.filter(reduce(operator.or_, argument_list))                
                    
                    else:
                        v = valori
                        valueF = v[0].split('_')
                        valueT = v[1].split('_')
                        
                        valueF = int(valueF[1])
                        valueT = int(valueT[1])
                        
                        query = HybProtocol.objects.all()
                        
                        for c in query:
                            ore = int(c.totalVolume)
                            if valueF <= ore and valueT >= ore:
                                argument_list.append(Q(id = c.id))
                        if len(argument_list)!=0:
                            if not pred:
                                listaprotocolsfinale=HybProtocol.objects.filter(reduce(operator.or_, argument_list))
                            else:
                                if len(protocols_list)!=0:
                                    listaprotocolsfinale=protocol_list.filter(reduce(operator.or_, argument_list))                
                
                    
                                
            
            #controllo chi e' il successore del blocchetto
            #se succ e' vero do' una lista di id interni, se e' falso do' una lista 
            #di genid
            if successore=='Hybrid. Protocols' or successore=='Hybrid. Events' or successore=='AND' or successore=='OR' or successore=='NOT IN':
                for a in listaprotocolsfinale:
                    l.append(a.id)
                print '[MMM][api query] - listaid',l
                return {'id':l}
            elif successore=='End':
                select=['name','loadQuantity','hybridTemp','hybTime','notes','hybBuffer','totalVolume','denTemp','denTime']
                for a in listaprotocolsfinale:
                    l.append(ClassSimple(a,select).getAttributes())
                print '[MMM][api query] - listaend',l
                return {'objects':l}
                            
        except Exception, e:
            print '[MMM][api query] - ecc',e
            return {'data':'errore'}  
          
                
#per caQuery. API per gli eventi di ibridazione
class QueryHybEventsHandler(BaseHandler):
    allowed_methods = ('GET','POST')
    def read(self, request):
        return {'data':'ok'}
    def create(self, request):
        try:
            print "[MMM][api query]", request.POST
            
            listaevents = []
            event_list = []
            listaeventsfinale = []
            l=[]
            
            pred = False
            
            predecess=request.POST.get('predecessor')
            print '[MMM][api query] - pred',predecess
            lista=request.POST.get('list')
            print '[MMM][api query] - lista',lista
            if lista!='':
                lis=ast.literal_eval(lista)
            
            successore=request.POST.get('successor')
            print '[MMM][api query] - successore',successore
            param=request.POST.get('parameter')
            print '[MMM][api query] - param',param
            val=request.POST.get('values')
            print '[MMM][api query] - val',val
            valori=val.split('|')
            
            #solo se la lista dei predecessori contiene degli elementi
            if lista!='' and len(lis)!=0:  
                #controllo chi e' il predecessore del blocchetto
                
                if predecess=='Aliquots':
                    lista1=[]
                    lista_al=[]
                    lista2=[]
                    lista_ass=[]
                    lista3=[]
                    pred=True
                    listagen=lis['genID']
                    #print listagen
                    print '[MMM][api query] - pred: Aliquots'
                    for i in range(0,len(listagen)):
                        lista1.append( Q(**{'genId': listagen[i]} ))
                    if len(lista1)!=0:
                        lista_al=Aliquot.objects.filter(reduce(operator.or_, lista1))
                        if len(lista_al)!=0:
                            for a in lista_al:
                                lista2.append( Q(**{'idAliquot': a.id} ))
                            if len(lista2)!=0:
                                lista_ass=Assignment.objects.filter(reduce(operator.or_, lista2))
                                
                                if len(lista_ass)!=0:
                                    for a in lista_ass:
                                        lista3.append( Q(**{'idChip': a.idChip} ))
                                    if len(lista3)!=0:
                                        event_list=HybEvent.objects.filter(reduce(operator.or_, lista3))
                                        print "[MMM][api query] - event_list", event_list                            
                   
                elif predecess=='Hybrid. Protocols':
                    listaprotocols = []
                    pred=True
                    listaid=lis['id']
                    print '[MMM][api query] - pred: Hybrid. Protocols'
                    for i in range(0,len(listaid)):
                        listaprotocols.append( Q(**{'idHybProtocol': listaid[i]} ))
                    if len(listaprotocols)!=0:
                        event_list=HybEvent.objects.filter(reduce(operator.or_, listaprotocols))
    
                elif predecess=='Hybrid. Events':
                    listaevents = []
                    pred=True
                    listaid=lis['id']
                    print '[MMM][api query] - pred: Hybrid. Events'
                    for i in range(0,len(listaid)):
                        listaevents.append( Q(**{'id': listaid[i]} ))
                    if len(listaevents)!=0:
                        event_list=HybEvent.objects.filter(Q(reduce(operator.or_, listaevents)))
    
                
                elif predecess=='Chips':
                    pred=True
                    listachips = []
                    listaid=lis['id']
                    print '[MMM][api query] - pred: Chips'
                    
                    if param=='GROUP BY':
                            countoccurr = []
                            print "[MMM][api query] - GROUP BY"
                            
                            for i in range(0,len(listaid)):
                                e = Chip.objects.get(id = listaid[i])
                                if e.idHybEvent != None:
                                    countoccurr.append(e.idHybEvent)
                                
                            event_list = countoccurr
                    else:
                    
                        for i in range(0,len(listaid)):
                            listachips.append( Q(**{'idChip': listaid[i]} ))
                        if len(listachips)!=0:
                            event_list=HybEvent.objects.filter(Q(reduce(operator.or_, listachips)))
                
                
                print '[MMM][api query] - list',event_list
            
            else:
                if predecess=='start':
                    pred=False
                
            if val=='':
                if not pred:
                    listaeventsfinale=HybEvent.objects.all()
                else:
                    listaeventsfinale=event_list
            else:   
                print "[MMM][api query] - ci sono valori" 
                
                if param=='Protocol':
                    lista1 = []
                    lista2 = []
                    protocolli = []
                    for i in range(0,len(valori)):
                        lista1.append( Q(**{'name':valori[i]} ))
                    if len(lista1)!=0:
                        protocolli = HybProtocol.objects.filter(reduce(operator.or_, lista1))
                        for p in protocolli:
                            lista2.append(Q(idHybProtocol = p))
                        if not pred:
                            listaeventsfinale=HybEvent.objects.filter(reduce(operator.or_, lista2))
                        else:
                            if len(event_list)!=0:
                                listaeventsfinale=event_list.filter(reduce(operator.or_, lista2))                
                
                elif param=='Instrument':
                    lista1 = []
                    lista2 = []
                    strumenti = []
                    for i in range(0,len(valori)):
                        lista1.append( Q(**{'name':valori[i]} ))
                    if len(lista1)!=0:
                        strumenti = Instrument.objects.filter(reduce(operator.or_, lista1))
                        for p in strumenti:
                            lista2.append(Q(idInstrument = p))
                        if not pred:
                            listaeventsfinale=HybEvent.objects.filter(reduce(operator.or_, lista2))
                        else:
                            if len(event_list)!=0:
                                listaeventsfinale=event_list.filter(reduce(operator.or_, lista2))                
                    
                
                elif param=='Operator':
                    lista1 = []
                    for i in range(0,len(valori)):
                        lista1.append( Q(**{'Operator':valori[i]} ))
                        if len(lista1) !=0:
                            if not pred:
                                listaeventsfinale=HybEvent.objects.filter(reduce(operator.or_, lista1))
                            else:
                                if len(event_list)!=0:
                                    listaeventsfinale=event_list.filter(reduce(operator.or_, lista1))                
                        
                
                elif param=='Date':
                    lista1 = []
                    
                    query = HybEvent.objects.all()
                    if len(valori) == 1:
                        value = valori[0].split('_')
                        if value[0] == '>':
                            query = query.filter(date__gte = value[1])
                        elif value[0] == '=':
                            query = query.filter(date = value[1])
                        elif value[0] == '<':
                            query = query.filter(date__lte = value[1])
                    else:
                        for v in valori:
                            value = v.split('_')
                            if value[0] == '>':
                                query = query.filter(date__gte = value[1])
                            elif value[0] == '=':
                                query = query.filter(date = value[1])
                            elif value[0] == '<':
                                query = query.filter(date__lte = value[1])
                    
                    for q in query:
                        lista1.append( Q(**{'id':q.id}))
                    
                      
                    if len(lista1)!=0:
                        if not pred:
                            listaeventsfinale=HybEvent.objects.filter(reduce(operator.or_, lista1))
                        else:
                            if len(event_list)!=0:
                                listaeventsfinale=event_list.filter(reduce(operator.or_, lista1))                
                    
            
            #controllo chi e' il successore del blocchetto
            #se succ e' vero do' una lista di id interni, se e' falso do' una lista 
            #di genid
            if successore=='Chips' or successore=='Hybrid. Protocols' or successore=='Hybrid. Events' or successore=='AND' or successore=='OR' or successore=='NOT IN':
                for a in listaeventsfinale:
                    l.append(a.id)
                print '[MMM][api query] - listaid',l
                return {'id':l}
            elif successore=='End':
                select=['idHybProtocol','idInstrument','Operator','date','idChip']
                for a in listaeventsfinale:
                    l.append(ClassSimple(a,select).getAttributes())
                print '[MMM][api query] - listaend',l
                return {'objects':l}
            #nel caso abbia come successore il blocchetto Aliquots
            elif successore=='Aliquots': 
                lista1=[]
                lista2=[]
                l = []
                for c in listaeventsfinale:
                    lista1.append(Q(**{'idChip': c.idChip.id} ))               
                    if len(lista1)!=0:
                        lista_ass = Assignment.objects.filter(Q(reduce(operator.or_, lista1)))
                        #print lista_ass
                        for a in lista_ass:
                            lista2.append( Q(**{'id': a.idAliquot.id} ))
                        if len(lista2)!=0:
                            al_list_=Aliquot.objects.filter(reduce(operator.or_, lista2))
                            #print al_list_
                        
                    #vedo se il barcode non e' nullo, tanto comunque quando filtro sui container
                    #i barcode nulli non vengono presi in considerazione
                for c in al_list_:
                    if c.genId:
                        l.append(c.genId)
                print '[MMM][api query] - listagen',l
                return {'genID':l}
    
                    
        except Exception, e:
            print '[MMM][api query] - ecc',e
            return {'data':'errore'}

#per caQuery. API per gli eventi di scansione
class QueryScanEventsHandler(BaseHandler):
    allowed_methods = ('GET','POST')
    def read(self, request):
        return {'data':'ok'}
    def create(self, request):
        try:
            print "[MMM][api query] ", request.POST
            
            listaevents = []
            event_list = []
            listaeventsfinale = []
            l=[]
            
            pred = False
            
            predecess=request.POST.get('predecessor')
            print '[MMM][api query] - pred',predecess
            lista=request.POST.get('list')
            print '[MMM][api query] - lista',lista
            if lista!='':
                lis=ast.literal_eval(lista)
            
            successore=request.POST.get('successor')
            print '[MMM][api query] - successore',successore
            param=request.POST.get('parameter')
            print '[MMM][api query] - param',param
            val=request.POST.get('values')
            print '[MMM][api query] - val',val
            valori=val.split('|')
            
            #solo se la lista dei predecessori contiene degli elementi
            if lista!='' and len(lis)!=0:  
                #controllo chi e' il predecessore del blocchetto
                   
                if predecess=='Raw Data':
                    listaass = []
                    lista_ass = []
                    lista_ass2 = []
                    lista2 = []
                    pred=True
                    listaid=lis['id']
                    print '[MMM][api query] - pred: Raw Data'
                    for i in range(0,len(listaid)):
                        listaass.append( Q(**{'id': listaid[i]} ))
                    if len(listaass)!=0:
                        lista_ass = RawData.objects.filter(Q(reduce(operator.or_, listaass)))
                        #print lista_ass
                        
                        if param=='GROUP BY':
                            countoccurr = []
                            print "[MMM][api query] - GROUP BY"
                            for r in lista_ass:
                                lista2.append(r.idScanEvent.id)
                            #print lista_ass
                            if len(lista2)!=0:
                                for x in lista2:    
                                    countoccurr.append(ScanEvent.objects.get(id=x))
                                #print "countoccurr"
                                #print countoccurr
                                event_list = countoccurr
                        
                        else:
                            for a in lista_ass:
                                lista2.append( Q(**{'id': a.idScanEvent.id} ))
                            if len(lista2)!=0:
                                event_list=ScanEvent.objects.filter(reduce(operator.or_, lista2))
    
                elif predecess=='Scan Events':
                    listaevents = []
                    pred=True
                    listaid=lis['id']
                    print '[MMM][api query] - pred: Scan Events'
                    for i in range(0,len(listaid)):
                        listaevents.append( Q(**{'id': listaid[i]} ))
                    if len(listaevents)!=0:
                        event_list=ScanEvent.objects.filter(Q(reduce(operator.or_, listaevents)))
    
                elif predecess=='Chips':
                    listaass = []
                    lista_ass = []
                    lista2 = []
                    lista3 = []
                    pred=True
                    listaid=lis['id']
                    print '[MMM][api query] - pred: Chips'
                            
                    if param=='GROUP BY':
                        countoccurr = []
                        print "[MMM][api query] - GROUP BY"
                        
                        for i in range(0,len(listaid)):
                            e = Chip.objects.get(id = listaid[i])
                            lista_ass = Assignment.objects.filter(idChip = e);
                            try:
                                eventi = Assignment_has_Scan.objects.filter(idAssignment = lista_ass[0])    
                                for e in eventi:
                                    countoccurr.append(e.idScanEvent)
                            except: #chip non scansionato
                                pass
                        event_list = countoccurr
                
                    else:
                        for i in range(0,len(listaid)):
                            listaass.append( Q(**{'idChip': listaid[i]} ))
                        if len(listaass)!=0:
                            lista_ass = Assignment.objects.filter(Q(reduce(operator.or_, listaass)));
                            if len(lista_ass)!=0:
                    
                                for a in lista_ass:
                                    lista2.append(Q(**{'idAssignment': a.id}))
                                lista2 = Assignment_has_Scan.objects.filter(Q(reduce(operator.or_, lista2)))
                                if len(lista2)!=0:
                                    for li in lista2:
                                        lista3.append(Q(**{'id': li.idScanEvent.id} ))
                        if len(lista3)!=0:
                            event_list=ScanEvent.objects.filter(reduce(operator.or_, lista3))
    
            
                print '[MMM][api query] - list',event_list
            
            else:
                if predecess=='start':
                    pred=False
                
            if val=='':
                if not pred:
                    listaeventsfinale=ScanEvent.objects.all()
                else:
                    listaeventsfinale=event_list
                    
            else:   
                print "[MMM][api query] - ci sono valori" 
                
                if param=='Instrument':
                    lista1 = []
                    lista2 = []
                    lista3 = []
                    lista4 = []
                    strumenti = []
                    for i in range(0,len(valori)):
                        lista1.append( Q(**{'name':valori[i]} ))
                    if len(lista1)!=0:
                        strumenti = Instrument.objects.filter(reduce(operator.or_, lista1))
                        for p in strumenti:
                            lista2.append(Q(idInstrument = p))
                        if len(lista2)!=0:
                            parameters = Parameter.objects.filter(reduce(operator.or_, lista2))
                            for pa in parameters:
                                lista3.append(Q(idParameter=pa))
                        if len(lista3)!=0:
                            values = Protocol_has_Parameter_value.objects.filter(reduce(operator.or_, lista3))
                            for v in values:
                                lista4.append(Q(idProtocol=v.idProtocol))
                        if len(lista4)!=0:
                            if not pred:
                                listaeventsfinale=ScanEvent.objects.filter(reduce(operator.or_, lista4))
                            else:
                                if len(event_list)!=0:
                                    listaeventsfinale=event_list.filter(reduce(operator.or_, lista4))                
                
                elif param=='Software':
                    lista1 = []
                    lista2 = []
                    lista3 = []
                    software = []
                    for i in range(0,len(valori)):
                        lista1.append( Q(**{'name':valori[i]} ))
                    if len(lista1)!=0:
                        software = Software.objects.filter(reduce(operator.or_, lista1))
                        for p in software:
                            lista2.append(Q(idSoftware = p))
                    if len(lista2)!=0:
                        protocols = ScanProtocol.objects.filter(reduce(operator.or_, lista2))
                        for s in protocols:
                            lista3.append(Q(idProtocol = s))
                        
                        if len(lista3)!=0:
                            if not pred:
                                listaeventsfinale=ScanEvent.objects.filter(reduce(operator.or_, lista3))
                            else:
                                if len(event_list)!=0:
                                    listaeventsfinale=event_list.filter(reduce(operator.or_, lista3))                
                    
                elif param=='Operator':
                    lista1 = []
                    for i in range(0,len(valori)):
                        lista1.append( Q(**{'operator':valori[i]} ))
                        if len(lista1) !=0:
                            if not pred:
                                listaeventsfinale=ScanEvent.objects.filter(reduce(operator.or_, lista1))
                            else:
                                if len(event_list)!=0:
                                    listaeventsfinale=event_list.filter(reduce(operator.or_, lista1))                
                
                elif param=='Protocol':
                    lista1 = []
                    lista2 = []
                    for i in range(0,len(valori)):
                        lista1.append( Q(**{'name':valori[i]} ))
                        if len(lista1) !=0:
                            protocolli = ScanProtocol.objects.filter(reduce(operator.or_, lista1))
                            for p in protocolli:
                                lista2.append(Q(**{'idProtocol':p} ))
                            if len(lista2)!=0:
                                if not pred:
                                    listaeventsfinale=ScanEvent.objects.filter(reduce(operator.or_, lista2))
                                else:
                                    if len(event_list)!=0:
                                        listaeventsfinale=event_list.filter(reduce(operator.or_, lista2))                
                
                
                elif param=='Date':
                    lista1 = []
                    
                    query = ScanEvent.objects.all()
                    if len(valori) == 1:
                        value = valori[0].split('_')
                        if value[0] == '>':
                            query = query.filter(date__gte = value[1])
                        elif value[0] == '=':
                            query = query.filter(date = value[1])
                        elif value[0] == '<':
                            query = query.filter(date__lte = value[1])
                    else:
                        for v in valori:
                            value = v.split('_')
                            if value[0] == '>':
                                query = query.filter(date__gte = value[1])
                            elif value[0] == '=':
                                query = query.filter(date = value[1])
                            elif value[0] == '<':
                                query = query.filter(date__lte = value[1])
                    
                    for q in query:
                        lista1.append( Q(**{'id':q.id}))
                    
                      
                    if len(lista1)!=0:
                        if not pred:
                            listaeventsfinale=ScanEvent.objects.filter(reduce(operator.or_, lista1))
                        else:
                            if len(event_list)!=0:
                                listaeventsfinale=event_list.filter(reduce(operator.or_, lista1))                
                    
            
            #controllo chi e' il successore del blocchetto
            #se succ e' vero do' una lista di id interni, se e' falso do' una lista 
            #di genid
            if successore=='Chips' or successore=='Raw Data' or successore=='Scan Events' or successore=='AND' or successore=='OR' or successore=='NOT IN':
                for a in listaeventsfinale:
                    l.append(a.id)
                print '[MMM][api query] - listaid',l
                return {'id':l}
            elif successore=='End':
                select=['idProtocol','time','date','operator']
                for a in listaeventsfinale:
                    l.append(ClassSimple(a,select).getAttributes())
                print '[MMM][api query] - listaend',l
                return {'objects':l}
                    
        except Exception, e:
            print '[MMM][api query] - ecc',e
            return {'data':'errore'}

    
#per caQuery. API per i Raw Data
class QueryRawDataHandler(BaseHandler):
    allowed_methods = ('GET','POST')
    def read(self, request):
        return {'data':'ok'}
    def create(self, request):
        try:
            print "[MMM][api query]", request.POST
            
            listaraw = []
            raw_list = []
            listarawfinale = []
            l=[]
            
            pred = False
            
            predecess=request.POST.get('predecessor')
            print '[MMM][api query] - pred',predecess
            lista=request.POST.get('list')
            print '[MMM][api query] - lista',lista
            if lista!='':
                lis=ast.literal_eval(lista)
            
            successore=request.POST.get('successor')
            print '[MMM][api query] - successore',successore
            param=request.POST.get('parameter')
            print '[MMM][api query] - param',param
            val=request.POST.get('values')
            print '[MMM][api query] - val',val
            valori=val.split('|')
            
            #solo se la lista dei predecessori contiene degli elementi
            if lista!='' and len(lis)!=0:  
                #controllo chi e' il predecessore del blocchetto
                   
                if predecess=='Raw Data':
                    lista1 = []
                    pred=True
                    listaid=lis['id']
                    print '[MMM][api query] - pred: Raw Data'
                    for i in range(0,len(listaid)):
                        lista1.append( Q(**{'id': listaid[i]} ))
                    if len(lista1)!=0:
                        raw_list=RawData.objects.filter(reduce(operator.or_, lista1))
                
                elif predecess=='Scan Events':
                    listaass = []
                    lista_ass = []
                    lista2 = []
                    pred=True
                    listaid=lis['id']
                    print '[MMM][api query] - pred: Scan Events'
                    for i in range(0,len(listaid)):
                        listaass.append( Q(**{'idScanEvent': listaid[i]} ))
                    if len(listaass)!=0:
                        raw_list=RawData.objects.filter(reduce(operator.or_, listaass))
    
                elif predecess=='Chips':
                    listaass = []
                    lista_ass = []
                    lista2 = []
                    pred=True
                    listaid=lis['id']
                    print '[MMM][api query] - pred: Chips'
                    for i in range(0,len(listaid)):
                        listaass.append( Q(**{'idChip': listaid[i]} ))
                    if len(listaass)!=0:
                        lista_ass = Assignment.objects.filter(Q(reduce(operator.or_, listaass)));
                        if len(lista_ass)!=0:
                            for a in lista_ass:
                                lista2.append( Q(**{'idAssignment': a} ))
                    if len(lista2)!=0:
                        raw_list=RawData.objects.filter(reduce(operator.or_, lista2))
                
                elif predecess=='Aliquots':
                    lista1=[]
                    lista_al=[]
                    lista2=[]
                    lista_ass=[]
                    lista3=[]
                    pred=True
                    listagen=lis['genID']
                    #print listagen
                    print '[MMM][api query] - pred: Aliquots'
                    for i in range(0,len(listagen)):
                        #print 'elem',listaid[i]
                        lista1.append( Q(**{'genId': listagen[i]} ))
                    if len(lista1)!=0:
                        lista_al=Aliquot.objects.filter(reduce(operator.or_, lista1))
                        if len(lista_al)!=0:
                            for a in lista_al:
                                lista2.append( Q(**{'idAliquot': a.id} ))
                            if len(lista2)!=0:
                                lista_ass=Assignment.objects.filter(reduce(operator.or_, lista2));
                                
                                if len(lista_ass)!=0:
                                    for a in lista_ass:
                                        lista3.append( Q(**{'idAssignment': a} ))
                                    if len(lista3)!=0:
                                        raw_list=RawData.objects.filter(reduce(operator.or_, lista3))
                                        #print raw_list                            
                    
                print '[MMM][api query] - list',raw_list
            
            else:
                if predecess=='start':
                    pred=False
                
            if val=='':
                if not pred:
                    listarawfinale=RawData.objects.all()
                else:
                    listarawfinale=raw_list
                
            
            else:   
                print "[MMM][api query] - ci sono valori" 
                #print param
                if param=='Experimental Group':
                    lista1 = []
                    lista2 = []
                    r_g = []
                    lista3 = []
                    for i in range(0,len(valori)):
                        lista1.append(Q(**{'name':valori[i]} ))
                    if len(lista1)!=0:
                        gruppi = Group.objects.filter(reduce(operator.or_, lista1))
                        for p in gruppi:
                            lista2.append(Q(group = p))
                        if len(lista2)!=0:
                            r_g = RawData_has_Group.objects.filter(reduce(operator.or_, lista2))
                            for r in r_g:
                                lista3.append(Q(**{'id':r.rawdata.id} ))
                        if len(lista3)!=0:
                            if not pred:
                                listarawfinale=RawData.objects.filter(reduce(operator.or_, lista3))
                            else:
                                if len(raw_list)!=0:
                                    listarawfinale=raw_list.filter(reduce(operator.or_, lista3))                
                
                
                elif param=='Experiment':
                    lista1 = []
                    lista2 = []
                    lista4 = []
                    r_g = []
                    lista3 = []
                    for i in range(0,len(valori)):
                        lista1.append(Q(**{'title':valori[i]} ))
                    if len(lista1)!=0:
                        esperimenti = Experiment.objects.filter(reduce(operator.or_, lista1))
                        #print esperimenti
                        for p in esperimenti:
                            lista2.append(Q(experiment_id = p.id))
                        if len(lista2)!=0:
                            gruppi = Group.objects.filter(reduce(operator.or_, lista2))
                            #print gruppi
                            for g in gruppi:
                                
                                lista4.append(Q(group = g.id))
                        if len(lista4)!=0:
                            r_g = RawData_has_Group.objects.filter(reduce(operator.or_, lista4))
                            #print r_g
                            for r in r_g:
                                lista3.append(Q(**{'id':r.rawdata.id} ))
                        if len(lista3)!=0:
                            if not pred:
                                listarawfinale=RawData.objects.filter(reduce(operator.or_, lista3))
                                #print listarawfinale
                            else:
                                if len(raw_list)!=0:
                                    listarawfinale=raw_list.filter(reduce(operator.or_, lista3))                
                    
                
                elif param=='Project':
                    lista1 = []
                    lista2 = []
                    lista4 = []
                    r_g = []
                    lista3 = []
                    lista5 = []
                    for i in range(0,len(valori)):
                        lista1.append(Q(**{'title':valori[i]} ))
                    if len(lista1)!=0:
                        progetti = Project.objects.filter(reduce(operator.or_, lista1))
                        for p in progetti:
                            lista2.append(Q(idProject = p.id))
                        if len(lista2)!=0:
                            esperimenti = Experiment.objects.filter(reduce(operator.or_, lista2))
                            for e in esperimenti:
                                lista4.append(Q(experiment_id = e.id))
                        if len(lista4)!=0:
                            gruppi = Group.objects.filter(reduce(operator.or_, lista4))
                            for g in gruppi:
                                lista5.append(Q(group = g.id))
                        if len(lista5)!=0:
                            r_g = RawData_has_Group.objects.filter(reduce(operator.or_, lista5))
                            for r in r_g:
                                lista3.append(Q(**{'id':r.rawdata.id} ))
                        if len(lista3)!=0:
                            if not pred:
                                listarawfinale=RawData.objects.filter(reduce(operator.or_, lista3))
                            else:
                                if len(raw_list)!=0:
                                    listarawfinale=raw_list.filter(reduce(operator.or_, lista3))                
                
                elif param=='Owner':
                    lista1 = []
                    lista2 = []
                    lista3 = []
                    for i in range(0,len(valori)):
                        lista1.append(Q(**{'owner':valori[i]}))
                    if len(lista1)!=0:
                        aliquote = Aliquot.objects.filter(reduce(operator.or_, lista1))
                    for a in aliquote:
                        lista2.append(Q(idAliquot = a.id))
                    if len(lista2)!=0:
                        ass = Assignment.objects.filter(reduce(operator.or_, lista2));
                    for b in ass:
                        lista3.append(Q(idAssignment = b))
                    if len(lista3)!=0:
                            if not pred:
                                listarawfinale=RawData.objects.filter(reduce(operator.or_, lista3))
                            else:
                                if len(raw_list)!=0:
                                    listarawfinale=raw_list.filter(reduce(operator.or_, lista3))                
                
                
            #controllo chi e' il successore del blocchetto
            #se succ e' vero do' una lista di id interni, se e' falso do' una lista 
            #di genid
            if successore=='Chips' or successore=='Raw Data' or successore=='Scan Events' or successore=='AND' or successore=='OR' or successore=='NOT IN':
                for a in listarawfinale:
                    l.append(a.id)
                print '[MMM][api query] - listaid',l
                return {'id':l}
            elif successore=='End':
                select=['idScanEvent','link','idAssignment']
                for a in listarawfinale:
                    l.append(ClassSimple(a,select).getAttributes())
                print '[MMM][api query] - listaend',l
                return {'objects':l}
            
            #nel caso abbia come successore il blocchetto Aliquots
            elif successore=='Aliquots':  #da testare con la biobanca
                lista1=[]
                lista2=[]
                al_list_ = []
                lista_ass = []
                l = []
                for c in listarawfinale:
                    lista1.append(Q(**{'id': c.idAssignment.id} ))               
                    if len(lista1)!=0:
                        lista_ass = Assignment.objects.filter(Q(reduce(operator.or_, lista1)))
                        #print lista_ass
                for a in lista_ass:
                    lista2.append(a.idAliquot.id)
                if len(lista2)!=0:
                    for le in lista2:
                        al_list_.append(Aliquot.objects.get(id = le)) #li mando duplicati per permettere il group by
                    #print "--------------------"
                    print "[MMM][api query]", al_list_
                        
                for c in al_list_:
                    if c.genId:
                        l.append(c.genId)
                print '[MMM][api query] - listagen',l
                return {'genID':l}
                
                    
        except Exception, e:
            print '[MMM][api query] - ecc',e
            return {'data':'errore'}
