from piston.handler import BaseHandler
from archive.models import *
from api.utils import *
from django.core import serializers
from django.db import models
from django.http import HttpResponse
from django.db.models import Q
import operator
import urllib, urllib2, json,ast
from django.views.decorators.csrf import csrf_exempt

#il bottone Cont. Relationships e' legato all'url http://devircc.polito.it/storage/api/query/cont_rel

#per caQuery. Restituisce tutti i container type
class QueryContTypeHandler(BaseHandler):
    allowed_methods = ('GET')
    def read(self, request):
        try:
            lista_tip=[]
            lista=ContainerType.objects.all()
            for l in lista:
                if l.name not in lista_tip:
                    lista_tip.append(l.name)
            return {'Container Type':lista_tip}
        except:
            return {'data':'errore'}
        
#per caQuery. Restituisce tutti i tipi di feature
class QueryFeatureHandler(BaseHandler):
    allowed_methods = ('GET')
    def read(self, request):
        try:
            lista_tip=[]
            lista=Feature.objects.all()
            for l in lista:
                if l.name not in lista_tip:
                    lista_tip.append(l.name)
            return {'Feature':lista_tip}
        except:
            return {'data':'errore'}
        
#per caQuery. Restituisce tutti i valori delle feature
class QueryFeatureValueHandler(BaseHandler):
    allowed_methods = ('GET')
    def read(self, request):
        try:
            lista_tip=[]
            lista=DefaultValue.objects.all()
            for l in lista:
                if l.longName=='Operative':
                    l.longName='Working'
                if l.longName=='Stored':
                    l.longName='Archive'
                if l.longName not in lista_tip:
                    lista_tip.append(l.longName)
            return {'Feature Value':lista_tip}
        except:
            return {'data':'errore'}

#per caQuery. Query fittizia che restituisce solo Yes
class QueryParentHandler(BaseHandler):
    allowed_methods = ('GET')
    def read(self, request):
        try:
            lista_tip=['Yes']
            return {'Parent':lista_tip}
        except:
            return {'data':'errore'}

#per caQuery. API per i container
class QueryContainersHandler(BaseHandler):
    allowed_methods = ('GET','POST')
    def read(self, request):
        return {'data':'ok'}
    def create(self, request):
        try:
            print request.POST
            lista1=[]
            lista2=[]
            lista3=[]
            listacontfinale=[]
            listac=[]
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
                    #ho la lista dei gen id e devo restituire i container 
                    listagen=lis['id']
                    if param=='GROUP BY':
                        for gen in listagen:
                            print 'gen',gen
                            laliq=Aliquot.objects.filter(genealogyID=gen,endTimestamp=None)
                            for al in laliq:
                                contt=al.idContainer
                                print 'cont',contt
                                #se si tratta di una provetta prendo la piastra padre
                                if contt.idContainerType.idGenericContainerType.name=='Tube/BioCassette':
                                    if contt.idFatherContainer!=None:
                                        listac.append(contt.idFatherContainer)
                                else:
                                    listac.append(contt)
                    else:
                        for gen in listagen:
                            print 'elem',gen
                            laliq=Aliquot.objects.filter(genealogyID=gen,endTimestamp=None)
                            for al in laliq:
                                lista1.append( Q(**{'id': al.idContainer.id} ))
                        if len(lista1)!=0:
                            listac=Container.objects.filter(Q(reduce(operator.or_, lista1)))
                                
                    '''if param=='GROUP BY':
                        for i in range(0,len(listabarc)):
                            #print 'elem',listabarc[i]
                            lista1.append(listabarc[i])
                        if len(lista1)!=0:
                            for x in lista1:
                                #print 'x',x
                                con=Container.objects.filter(barcode=x)
                                if len(con)!=0:
                                    contt=con[0]
                                    #se si tratta di una provetta prendo la piastra padre
                                    if contt.idContainerType.idGenericContainerType.name=='Tube/BioCassette':
                                        if contt.idFatherContainer!=None:
                                            listac.append(contt.idFatherContainer)
                                    else:
                                        listac.append(contt)
                    else:
                        for i in range(0,len(listabarc)):
                            print 'elem',listabarc[i]
                            lista1.append( Q(**{'barcode': listabarc[i]} ))
                        if len(lista1)!=0:
                            listac=Container.objects.filter(Q(reduce(operator.or_, lista1)))'''
                
                elif predecess=='Containers' or predecess=='Father Container':
                    #c'e' un predecessore
                    pred=True
                    #ho la lista dei barcode e devo restituire i container
                    listabarc=lis['id']
                    for i in range(0,len(listabarc)):
                        lista1.append( Q(**{'id': listabarc[i]} ))
                    if len(lista1)!=0:
                        listac=Container.objects.filter(Q(reduce(operator.or_, lista1)))
                
                elif predecess=='Container Positions':
                    pred=True
                    listabarc=lis['id']
                    if param=='GROUP BY':
                        for i in range(0,len(listabarc)):
                            if listabarc[i][0:2]=='-1':
                                vall=listabarc[i].split('^')
                                #in vall[1] ho il barcode
                                bar=vall[1]
                                #print 'bar',bar
                                cont=Container.objects.filter(barcode=bar)
                                if len(cont)!=0:
                                    lista1.append(cont[0].id)
                            else:
                                lista1.append(listabarc[i])
                        #print 'len',len(lista1)
                        if len(lista1)!=0:
                            for x in lista1:
                                #print 'x',x
                                con=Container.objects.filter(id=x)
                                if len(con)!=0:
                                    contt=con[0]
                                    #se si tratta di una provetta prendo la piastra padre
                                    if contt.idContainerType.idGenericContainerType.name=='Tube/BioCassette':
                                        if contt.idFatherContainer!=None:
                                            listac.append(contt.idFatherContainer)
                                    else:
                                        listac.append(contt)
                    else:
                        for i in range(0,len(listabarc)):
                            if listabarc[i][0:2]=='-1':
                                vall=listabarc[i].split('^')
                                #in vall[1] ho il barcode
                                bar=vall[1]
                                cont=Container.objects.get(barcode=bar)
                                lista1.append( Q(**{'id': cont.id} ))
                            else:
                                lista1.append( Q(**{'id': listabarc[i]} ))
                        if len(lista1)!=0:
                            listac=Container.objects.filter(Q(reduce(operator.or_, lista1)))
                        
                elif predecess=='start':
                    pred=False
                    
                print 'list',listac
                
            else:
                if predecess=='start':
                    pred=False
                else:
                    pred=True
            
            if val=='':
                if not pred:
                    listacontfinale=Container.objects.all()
                else:
                    listacontfinale=listac
            else:    
                del lista1[:]
                del lista2[:]
                del lista3[:]
                if param=='Barcode':
                    for i in range(0,len(valori)):
                        print 'valori',valori[i]
                        lista1.append( Q(**{'barcode': valori[i]} ))
                    print 'lista',lista1
                    if len(lista1)!=0:
                        if not pred:
                            listacontfinale=Container.objects.filter(reduce(operator.or_, lista1))
                        else:
                            if len(listac)!=0:
                                listacontfinale=listac.filter(reduce(operator.or_, lista1))
                                
                elif param=='Container Type':
                    for i in range(0,len(valori)):
                        lista1.append( Q(**{'name': valori[i]} ))
                    listatipi=ContainerType.objects.filter( Q(reduce(operator.or_, lista1)) )
                    print 'listatipi',listatipi
                    if len(listatipi)!=0:
                        for tipi in listatipi:
                            lista2.append(Q(**{'idContainerType': tipi.id} ))
                        if len(lista2)!=0:
                            if not pred:
                                listacontfinale=Container.objects.filter(reduce(operator.or_, lista2))
                            else:
                                if len(listac)!=0:
                                    listacontfinale=listac.filter(reduce(operator.or_, lista2))
                
                elif param=='Feature':
                    for i in range(0,len(valori)):
                        lista1.append( Q(**{'name': valori[i]} ))
                    listafeat=Feature.objects.filter( Q(reduce(operator.or_, lista1)))
                    if len(listafeat)!=0:
                        for f in listafeat:
                            lista2.append(Q(**{'idFeature': f.id}))
                        if len(lista2)!=0:
                            listacontfeat=ContainerFeature.objects.filter(reduce(operator.or_, lista2))
                            if len(listacontfeat)!=0:
                                for contfeat in listacontfeat:
                                    lista3.append(Q(**{'id': contfeat.idContainer.id}))
                                if len(lista3)!=0: 
                                    if not pred:
                                        listacontfinale=Container.objects.filter(reduce(operator.or_, lista3))
                                    else:
                                        if len(listac)!=0:
                                            listacontfinale=listac.filter(reduce(operator.or_, lista3))
            
                elif param=='Feature Value':
                    for i in range(0,len(valori)):
                        if valori[i]=='Working':
                            valori[i]='Operative'
                        if valori[i]=='Archive':
                            valori[i]='Stored'
                        #in valori[i] ho il nome per esteso, mentre per filtrare ho
                        #bisogno dell'abbreviazione. Utilizzando la tabella Default Value
                        #passo da nome per esteso ad abbreviazione
                        defval=DefaultValue.objects.get(longName=valori[i])
                        if defval.abbreviation!=None:
                            valori[i]=defval.abbreviation
                        lista2.append( Q(**{'value': valori[i]} ))
                    if len(lista2)!=0:
                        listacontfeat=ContainerFeature.objects.filter(reduce(operator.or_, lista2))
                        if len(listacontfeat)!=0:
                            for contfeat in listacontfeat:
                                lista3.append(Q(**{'id': contfeat.idContainer.id}))
                            if len(lista3)!=0: 
                                if not pred:
                                    listacontfinale=Container.objects.filter(reduce(operator.or_, lista3))
                                else:
                                    if len(listac)!=0:
                                        listacontfinale=listac.filter(reduce(operator.or_, lista3))
                                    
                elif param=='Full':
                    if valori[0]=='Yes':
                        fu=1
                    elif valori[0]=='No':
                        fu=0
                    if not pred:
                        listacontfinale=Container.objects.filter(full=fu)
                    else:
                        if len(listac)!=0:
                            listacontfinale=listac.filter(full=fu)
                
                elif param=='Parent Barcode':
                    for i in range(0,len(valori)):
                        print 'valori',valori[i]
                        lista1.append( Q(**{'barcode': valori[i]} ))
                    print 'lista',lista1
                    if len(lista1)!=0:
                        listacont=Container.objects.filter(reduce(operator.or_, lista1))
                        for c in listacont:
                            lista2.append( Q(**{'idFatherContainer': c.id} ))
                            if len(lista2)!=0:
                                if not pred:
                                    listacontfinale=Container.objects.filter(reduce(operator.or_, lista2))
                                else:
                                    if len(listac)!=0:
                                        listacontfinale=listac.filter(reduce(operator.or_, lista2))
                    
                elif param=='Erased':
                    if valori[0]=='Yes':
                        pr=0
                    elif valori[0]=='No':
                        pr=1
                    if not pred:
                        listacontfinale=Container.objects.filter(present=pr)
                    else:
                        if len(listac)!=0:
                            listacontfinale=listac.filter(present=pr)

            print 'lista',listacontfinale
            if successore=='Containers' or successore=='Container Positions' or successore=='Father Container' or successore=='AND' or successore=='OR' or successore=='NOT IN':
                for cont in listacontfinale:
                    l.append(cont.id)
                print 'listaid',l
                return {'id':l}
            elif successore=='End':
                select=['barcode','idContainerType','idFatherContainer','idGeometry','position','full','availability','owner','id']
                feat=Feature.objects.get(name='PlateAim')
                for cont in listacontfinale:
                    diz=Simple(cont,select).getAttributes()
                    if cont.present==True:
                        diz['Erased']='False'
                    elif cont.present==False:
                        diz['Erased']='True'
                    #se e' una piastra metto anche lo scopo: operativa, archivio, ecc
                    alfeat=ContainerFeature.objects.filter(Q(idFeature=feat)&Q(idContainer=cont))
                    if len(alfeat)!=0:
                        if alfeat[0].value=='Stored':
                            valore='Archive'
                        elif alfeat[0].value=='Operative':
                            valore='Working'
                        else:
                            valore=alfeat[0].value
                        diz['Aim']=valore
                    else:
                        diz['Aim']='None'
                    l.append(diz)
                print 'listaend',l
                return {'objects':l}
            #nel caso abbia come successore il blocchetto Aliquots
            elif successore=='Aliquots':
                #serve per ottenere tutti i barcode delle provette contenute nella
                #lista dei container
                lista=[]
                listafigli=visit_children(listacontfinale,l)
                #nel caso in cui ho delle piastre costar, allora le inserisco a mano nella
                #listafigli, perche' la funzione visit_children non me le mette
                for cont in listacontfinale:
                    if cont not in listafigli:
                        listafigli.append(cont)
                print 'lista barc',listafigli
                for c in listafigli:
                    print 'c',c
                    laliq=Aliquot.objects.filter(idContainer=c,endTimestamp=None)
                    for al in laliq:
                        lista.append(al.genealogyID)
                    #lista.append(c.barcode)
                print 'lisgen',lista
                return {'genID':lista}
        except Exception, e:
            print 'ecc',e
            return {'data':'errore'}

#per caQuery. API per le posizioni all'interno dei container.
class QueryPositionsHandler(BaseHandler):
    allowed_methods = ('GET','POST')
    def read(self, request):
        return {'data':'ok'}
    def create(self, request):
        try:
            print request.POST
            lista1=[]
            lista2=[]
            lista3=[]
            listacontfinale=[]
            listac=[]
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
                if predecess=='Containers':
                    #c'e' un predecessore
                    pred=True
                    #ho la lista dei barcode e devo restituire i container
                    listabarc=lis['id']
                    for i in range(0,len(listabarc)):
                        print 'elem',listabarc[i]
                        lista1.append( Q(**{'id': listabarc[i]} ))
                    if len(lista1)!=0:
                        listac=Container.objects.filter(Q(reduce(operator.or_, lista1)))
                        
                elif predecess=='Container Positions':
                    #c'e' un predecessore
                    pred=True
                    #ho la lista dei barcode e devo restituire i container
                    listabarc=lis['id']
                    for i in range(0,len(listabarc)):
                        print 'elem',listabarc[i]
                        if listabarc[i][0:2]=='-1':
                            vall=listabarc[i].split('^')
                            #in vall[1] ho il barcode
                            bar=vall[1]
                            cont=Container.objects.get(barcode=bar)
                            lista1.append( Q(**{'id': cont.id} ))
                        else:
                            lista1.append( Q(**{'id': listabarc[i]} ))
                    if len(lista1)!=0:
                        listac=Container.objects.filter(Q(reduce(operator.or_, lista1)))

                elif predecess=='start':
                    pred=False
                                       
                print 'list',listac
                
            else:
                if predecess=='start':
                    pred=False
                    listac=Container.objects.all()
                else:
                    pred=True
            
            if val=='':
                if not pred:
                    listaconttot=Container.objects.all()
                    for c in listaconttot:
                        regole=json.loads(c.idGeometry.rules)
                        #devo capire se il cont puo' contenere altri cont o se e'
                        #una provetta
                        if c.idContainerType.idGenericContainerType.name=='Tube/BioCassette':
                            if c.full==1:
                                for r in regole['items']:
                                    listacontfinale.append(str(c.id)+'|'+c.barcode+'|'+r['id'])
                            else:
                                for r in regole['items']:
                                    listacontfinale.append('-1^'+c.barcode+'|'+c.barcode+'|'+r['id'])
                        else:
                            for r in regole['items']:
                                #prendo il container figlio
                                contfiglio=Container.objects.filter(Q(idFatherContainer=c.id)&Q(position=r['id']))
                                if len(contfiglio)!=0:
                                    listacontfinale.append(str(contfiglio[0].id)+'|'+c.barcode+'|'+r['id'])
                                else:
                                    listacontfinale.append('-1^'+c.barcode+'|'+c.barcode+'|'+r['id'])
                else:
                    #c'e' un predecessore (che e' Containers) e quindi devo creare
                    #la lista con tutte le posizioni di quel/i container
                    for c in listac:
                        regole=json.loads(c.idGeometry.rules)
                        for r in regole['items']:
                            #prendo il container figlio
                            contfiglio=Container.objects.filter(Q(idFatherContainer=c.id)&Q(position=r['id']))
                            if len(contfiglio)!=0:
                                listacontfinale.append(str(contfiglio[0].id)+'|'+c.barcode+'|'+r['id'])
                            else:
                                listacontfinale.append('-1^'+c.barcode+'|'+c.barcode+'|'+r['id'])
            else:    
                del lista1[:]
                del lista2[:]
                del lista3[:]
                if param=='Available':
                    for c in listac:
                        #prendo le regole della geometria del container
                        regole=json.loads(c.idGeometry.rules)
                        #devo capire se il cont puo' contenere altri cont o se e'
                        #una provetta
                        if c.idContainerType.idGenericContainerType.name=='Tube/BioCassette':
                            if c.full==1:
                                for r in regole['items']:
                                    lista1.append(str(c.id)+'|'+c.barcode+'|'+r['id'])
                            else:
                                for r in regole['items']:
                                    lista2.append('-1^'+c.barcode+'|'+c.barcode+'|'+r['id'])
                        else:
                            #prendo i figli del container per vedere quali posizioni
                            #sono occupate
                            listacont=Container.objects.filter(idFatherContainer=c)                           
                            for r in regole['items']:
                                trovato=0
                                for contfiglio in listacont:
                                    if str(r['id'])==str(contfiglio.position):
                                        trovato=1
                                        #lista in cui metto le posizioni occupate del container
                                        lista1.append(str(contfiglio.id)+'|'+c.barcode+'|'+r['id'])
                                        break
                                if trovato==0:
                                    #lista in cui metto le posizioni libere del container
                                    lista2.append('-1^'+c.barcode+'|'+c.barcode+'|'+r['id'])
                        #print 'lista1',lista1
                        #print 'lista2',lista2
                    if valori[0]=='Yes':
                        listacontfinale=lista2
                    elif valori[0]=='No':
                        listacontfinale=lista1

            print 'lista',listacontfinale
            if successore=='Containers' or successore=='Container Positions' or successore=='AND' or successore=='OR' or successore=='NOT IN':
                for cont in listacontfinale:
                    #devo prendere gli id
                    valori=cont.split('|')
                    l.append(valori[0])
                print 'listaid',l
                return {'id':l}
            elif successore=='End':
                l=[]
                for cont in listacontfinale:
                    val=cont.split('|')
                    diz={}
                    
                    diz['Position']=val[2]
                    diz['id']=val[0]
                    diz['Container']=val[1]
                    l.append(diz)
                print 'listaend',l
                return {'objects':l}
        except Exception, e:
            print 'ecc',e
            return {'data':'errore'}

#per caQuery. API per i container
class QueryFatherHandler(BaseHandler):
    allowed_methods = ('GET','POST')
    def read(self, request):
        return {'data':'ok'}
    def create(self, request):
        try:
            print request.POST
            lista1=[]
            lista2=[]
            lista3=[]
            listacontfinale=[]
            listac=[]
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
                if predecess=='Containers' or 'Father Container':
                    #c'e' un predecessore
                    pred=True
                    #ho la lista degli id e devo restituire i container
                    listabarc=lis['id']
                    for i in range(0,len(listabarc)):
                        lista1.append( Q(**{'id': listabarc[i]} ))
                    if len(lista1)!=0:
                        listac=Container.objects.filter(Q(reduce(operator.or_, lista1)))
                
                elif predecess=='start':
                    pred=False
                    
                print 'list',listac
                
            else:
                if predecess=='start':
                    pred=False
                else:
                    pred=True
            
            if val=='':
                if not pred:
                    listacontfinale=Container.objects.all()
                else:
                    listacontfinale=listac
            else:    
                del lista1[:]
                del lista2[:]
                del lista3[:]
                '''if param=='Parent':
                    lista1=Container.objects.filter(~Q(idFatherContainer=None))
                    if len(lista1)!=0:
                        for elem in lista1:
                            lista2.append( Q(**{'id': elem.idFatherContainer.id} ))
                        if len(lista2)!=0:
                            if not pred:
                                listacontfinale=Container.objects.filter(reduce(operator.or_, lista2))
                            else:
                                if len(listac)!=0:
                                    for el in listac:
                                        if el.idFatherContainer!=None:
                                            cont_padre=Container.objects.get(id=el.idFatherContainer.id)
                                            if cont_padre not in listacontfinale:
                                                listacontfinale.append(cont_padre)
                elif param=='Children':
                    lista1=Container.objects.filter(~Q(idFatherContainer=None))
                    if len(lista1)!=0:
                        for elem in lista1:
                            lista2.append( Q(**{'id': elem.id} ))
                        if len(lista2)!=0:
                            if not pred:
                                listacontfinale=Container.objects.filter(reduce(operator.or_, lista2))
                            else:
                                if len(listac)!=0:
                                    for el in listac:
                                        lista3.append( Q(**{'idFatherContainer': el.id} ))
                                    if len(lista3)!=0:
                                        listacontfinale=Container.objects.filter(reduce(operator.or_, lista3))'''           
                if param=='Level':
                    attr=valori[0].split('_')
                    num=int(attr[1])
                    if not pred:
                        lista2=Container.objects.all()
                    else:
                        lista2=listac
                    listafin=[]
                    if len(valori)>1:
                        attr2=valori[1].split('_')
                        num2=int(attr2[1])
                        if attr2[0]=='<':
                            for cont in lista2:
                                tmp=cont
                                #con questo ciclo trovo il padre di num livello, ma a me
                                #serve il padre di num+1 livello
                                for i in range(0,num):
                                    if tmp!=None:
                                        c_nuovo=tmp.idFatherContainer
                                        tmp=c_nuovo
                                #con questo ciclo trovo i padri di num2 livello
                                for i in range(num,num2):
                                    if tmp!=None:
                                        if tmp not in listafin and tmp!=None:
                                            listafin.append(tmp)
                                        c_nuovo=tmp.idFatherContainer
                                        tmp=c_nuovo
                                        print 'tmp',tmp
                                        
                                if num==num2:
                                    listafin.append(tmp)
                    else:
                        if attr[0]=='=':
                            for cont in lista2:
                                tmp=cont
                                for i in range(0,num):
                                    if tmp!=None:
                                        c_nuovo=tmp.idFatherContainer
                                        tmp=c_nuovo
                                if tmp not in listafin and tmp!=None:
                                    listafin.append(tmp)
                        elif attr[0]=='<':
                            for cont in lista2:
                                tmp=cont
                                for i in range(0,num):
                                    if tmp!=None:
                                        c_nuovo=tmp.idFatherContainer
                                        tmp=c_nuovo
                                        if tmp not in listafin and tmp!=None:
                                            listafin.append(tmp)
                        elif attr[0]=='>':
                            for cont in lista2:
                                tmp=cont
                                #con questo ciclo trovo il padre di num livello, ma a me
                                #serve il padre di num+1 livello
                                for i in range(0,num):
                                    if tmp!=None:
                                        c_nuovo=tmp.idFatherContainer
                                        tmp=c_nuovo
                                #con questo ciclo trovo i padri di num+1 livello
                                #10 e' un numero arbitrario
                                for i in range(num,10):
                                    if tmp!=None:
                                        if tmp not in listafin and tmp!=None:
                                            listafin.append(tmp)
                                        c_nuovo=tmp.idFatherContainer
                                        tmp=c_nuovo
                    
                    listacontfinale=listafin
                        
            print 'lista',listacontfinale
            if successore=='Containers' or successore=='Father Container' or successore=='AND' or successore=='OR' or successore=='NOT IN':
                for cont in listacontfinale:
                    l.append(cont.id)
                print 'listaid',l
                return {'id':l}
            elif successore=='End':
                select=['barcode','idContainerType','idFatherContainer','idGeometry','position','full','availability','owner','id']
                feat=Feature.objects.get(name='PlateAim')
                for cont in listacontfinale:
                    diz=Simple(cont,select).getAttributes()
                    if cont.present==True:
                        diz['Erased']='False'
                    elif cont.present==False:
                        diz['Erased']='True'
                    l.append(diz)
                    #se e' una piastra metto anche lo scopo: operativa, archivio, ecc
                    alfeat=ContainerFeature.objects.filter(Q(idFeature=feat)&Q(idContainer=cont))
                    if len(alfeat)!=0:
                        if alfeat[0].value=='Stored':
                            valore='Archive'
                        elif alfeat[0].value=='Operative':
                            valore='Working'
                        else:
                            valore=alfeat[0].value
                        diz['Aim']=valore
                    else:
                        diz['Aim']='None'
                print 'listaend',l
                return {'objects':l}
        except Exception, e:
            print 'ecc',e
            return {'data':'errore'}
