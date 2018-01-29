import string, json, urllib, urllib2,operator,requests,datetime
from piston.handler import BaseHandler
from archive.models import *
from archive.utils import *
from django.core import serializers
from django.db import models
from django.http import HttpResponse
from django.db.models import Q
from api.utils import *
from django.views.decorators.csrf import csrf_exempt
from django.contrib import auth
from django.utils.decorators import method_decorator
from apisecurity.decorators import required_parameters
from django.conf import settings
from django.utils.decorators import method_decorator
from apisecurity.decorators import get_functionality_decorator
from dateutil.relativedelta import *
from global_request_middleware import *
from django.utils import timezone

#restituisce, ricevuto un barcode, il suo tipo, il contenitore padre e tutto il suo contenuto
class Container_handler(BaseHandler):
    allowed_methods = ('GET')
    @method_decorator(get_functionality_decorator)
    def read(self, request, barcode):
        try:
            print 'barcode cont',barcode
            if len(barcode.split('|')) == 1:
                return(getInfoP(barcode))
            else:
                p = barcode.split('|')
                barc = p[0]
                requestTypeP = p[1]
                liscont=Container.objects.filter(barcode=barc)
                print 'liscont',liscont
                if len(liscont)==0:
                    return {"info": 'err'}
                typeP = ContainerFeature.objects.get(idContainer = liscont[0], idFeature = Feature.objects.get(name = 'AliquotType')).value

                if typeP == requestTypeP:
                    return(getInfoP(barc))
                else:
                    return {'info' : 'misType'}
        except Exception, e:
            #print e
            return {"info": 'err'}
        
   
        
#data una serie di barcode di provette, restituisce le informazioni sulle piastre
#a cui appartengono. Infine restituisce un dizionario con l'accoppiamento barcode
#piastra
class InfoPlateHandler(BaseHandler):
    allowed_methods = ('GET')
    model = Container
    @method_decorator(get_functionality_decorator)
    def read(self, request, barcode):
        try:
            print barcode
            listabarc=barcode.split('&')
            diz={}
            diz2={}
            print 'l',listabarc
            for i in range(0,len(listabarc)):
                provetta=Container.objects.get(barcode=listabarc[i])
                barc_pias=provetta.idFatherContainer.barcode
                info_pias=getInfoP(barc_pias)
                print info_pias
                diz[barc_pias]=info_pias
                diz2[provetta.barcode]=barc_pias
            return {'plates' : diz,'match':diz2}
        except Exception, e:
            print e
            return {'data': 'err'}
        
'''#svuota la piastra ricevuta in input
class EmptyPlate_handler(BaseHandler):
    allowed_methods = ('GET')
    @method_decorator(get_functionality_decorator)
    def read(self, request, barcode, addressStorage, addressBioB):
        try:
            prefisso= 'https://' if settings.LAS_AUTH_USE_HTTPS else 'http://'
            url = prefisso + addressStorage + "/api.container/" + barcode+ "?workingGroups="+get_WG_string()
            print url
            req = urllib2.Request(url, headers={"workingGroups" : get_WG_string()})
            u = urllib2.urlopen(req)
            #u = urllib2.urlopen(url)
            data =  json.loads(u.read())

            barcodeStr = ""
            for d in data['children']:
                for rr in data['rules']['items']:
                    if rr['id'] == d['position']:
                        if barcodeStr == "":
                            barcodeStr = str(d['barcode'])
                        else:
                            barcodeStr = barcodeStr + '&' + str(d['barcode'])
            
            prefisso= 'https://' if settings.LAS_AUTH_USE_HTTPS else 'http://'
            url = prefisso + addressStorage + "/archive/full/"
            print url
            values = {'lista' : barcodeStr, 'tube': 'empty','workingGroups':get_WG_string()}
            data = urllib.urlencode(values)
            req = urllib2.Request(url,data=data, headers={"workingGroups" : get_WG_string()})
            u = urllib2.urlopen(req)
            #u = urllib2.urlopen(url, data)

            #mandare alla biobanca l'elenco dei barcode delle provette per permettere cosi' di svuotarle tutte
            prefisso= 'https://' if settings.LAS_AUTH_USE_HTTPS else 'http://'
            url = prefisso + addressBioB + "/api/aliquot/canc/"
            print url
            values = {'barcode' : barcodeStr,'empty':'ok','workingGroups':get_WG_string()}
            data = urllib.urlencode(values)
            req = urllib2.Request(url,data=data, headers={"workingGroups" : get_WG_string()})
            u = urllib2.urlopen(req)
            #u = urllib2.urlopen(url, data)

            return {'mess':'ok'}
        except Exception, e:
            return {"info":e}'''
            
#per avere il contenuto di una piastra dato il suo barcode e il suo tipo
class LoadHandler(BaseHandler):
    allowed_methods = ('GET')
    model = Container
    @method_decorator(get_functionality_decorator)
    def read(self, request, barcode,tipo,store,ext):
        try:
            print 'barc',barcode
            piastra=Container.objects.get(barcode=barcode,present=1)
            tipoaliqgen=Feature.objects.get(name='AliquotType')
            print 'tipoaliqgen',tipoaliqgen
            idtipoaliqgen=tipoaliqgen.id
            '''tipopiastragen=Feature.objects.get(name='PlateAim')
            idtipopiastragen=tipopiastragen.id'''
            print 't',tipo
            #serve solo nel caso in cui invio il barcode di una provetta durante
            #l'inserimento di aliq esterne
            if ext and tipo=='TUBEEXTERN':
                #verifico che il barcode della provetta che inserisco per l'aliquota esterna non esista gia'
                listac=Container.objects.filter(barcode=barcode)
                if listac.count!=0:
                    return {'data':'barc_duplicato'} 
            #sono nel caso in cui sto trasferendo dalla piastra trans alla stored e sto
            #chiamando questa funzione per la piastra stored
            #if (tipo=='TRANS') and (store):
            #    tip='VT'
            #sono nel caso in cui sto trasferendo dalla piastra vitale alla trans e sto
            #chiamando questa funzione per la piastra stored
            #elif tipo=='VT' and store:
            #    tip='TRANS'
            #else:
            tip=tipo.split('&')
            print 'tipo',tip
            for t in tip:
                #verifico che la piastra possa contenere quel tipo di aliquote
                tipoaliq=ContainerFeature.objects.filter(idFeature=idtipoaliqgen,idContainer=piastra,value=t)
                print 'tipoaliq',tipoaliq
                if(tipoaliq.count()==0) :
                    return {'data':'errore_aliq'} 
            
            '''if tip=='TRANS':
                #verifico che la piastra sia di quel tipo (operativa, stored...)
                tipopiastra=ContainerFeature.objects.filter(Q(idFeature=idtipopiastragen)&Q(idContainer=piastra)&Q(value='Transient'))
                if(tipopiastra.count()==0):
                    return {'data':'errore_piastra'}
            #per le piastre che contengono aliquote provenienti da altri ospedali
            elif ext:
                #verifico che la piastra sia di quel tipo (operativa, stored...)
                tipopiastra=ContainerFeature.objects.filter(Q(idFeature=idtipopiastragen)&Q(idContainer=piastra)&Q(value='Extern'))
                if(tipopiastra.count()==0):
                    return {'data':'errore_piastra'}
            else:
                
                #verifico che la piastra sia di quel tipo (operativa, stored...)
                if not store:
                    tipopiastra=ContainerFeature.objects.filter(Q(idFeature=idtipopiastragen)&Q(idContainer=piastra)&(Q(value='Operative')|Q(value='Transient')))
                else:
                    tipopiastra=ContainerFeature.objects.filter(Q(idFeature=idtipopiastragen)&Q(idContainer=piastra)&Q(value='Stored'))
                if(tipopiastra.count()==0):
                    return {'data':'errore_piastra'}'''
            
            #verifico che il cont sia una piastra
            if piastra.idContainerType.idGenericContainerType.abbreviation!='plate' and piastra.idContainerType.idGenericContainerType.abbreviation!='tube':
                return {'data':'errore_piastra'}
            
            children=caricaFigli(piastra)
            
            select = ['idContainerType', 'position', 'barcode', 'availability', 'full']
            if piastra.idContainerType.idGenericContainerType.abbreviation=='plate':
                contentList = Container.objects.filter(idFatherContainer = piastra)
                piass=True
            #se il codice caricato e' una provetta allora gli passo il container stesso
            elif piastra.idContainerType.idGenericContainerType.abbreviation=='tube':
                contentList = Container.objects.filter(barcode=barcode)
                piass=False
            #parte vecchia del codice
            '''for c in contentList:
                print 'c',c
                diz=Simple(c,select).getAttributes()
                children.append(diz)'''
            return {'typeC':piastra.idContainerType.name,'children':children,'rules': json.loads(piastra.idGeometry.rules),'data':'ok','piastra':piass}
        except Exception,e:
            print 'err',e
            return {"data":'errore'}

'''#per avere il contenuto di un container dato il suo barcode e il suo tipo
class MoveHandler(BaseHandler):
    allowed_methods = ('GET')
    model = Container
    @method_decorator(get_functionality_decorator)
    def read(self, request,barcode,tipo,sorg,store):
        children = []
        try:
            print 'barc',barcode
            string = ''
            cont=Container.objects.filter(barcode=barcode)
            if len(cont)==0:
                return {"data": 'errore'}
            else:
                container=cont[0]
                scopo=''
                #devo vedere se il cont puo' contenere i cont selezionati
                #tipo e' l'abbreviazione del genericconttype. Se il tipo del cont in
                #questione non puo' contenere nessun tipo del precedente genericconttype,
                #allora errore
                if tipo.isdigit():
                    gencont=GenericContainerType.objects.get(id=tipo)
                else:
                    gencont=GenericContainerType.objects.get(abbreviation=tipo)
                tipicont=ContainerType.objects.filter(idGenericContainerType=gencont)
                typehastype=ContTypeHasContType.objects.filter(idContainer=container.idContainerType)
                trovato=0
                for tiphas in typehastype:
                    print 'tiphas',tiphas
                    for tip in tipicont:
                        print 'tip',tip
                        if tiphas.idContained.id==tip.id:
                            trovato=1
                            break
                    if trovato==1:
                        break
                if trovato==0:
                    return {'data':'err_tipo'}
                
                #guardo se il cont destinazione puo' contenere i cont presenti nel 
                #cont sorg
                if store:
                    sorgente=Container.objects.get(barcode=sorg)
                    typehastypecontsorg=ContTypeHasContType.objects.filter(idContainer=sorgente.idContainerType)
                    typehastypecontdest=ContTypeHasContType.objects.filter(idContainer=container.idContainerType)
                    trovato=0
                    for tiphas in typehastypecontsorg:
                        print 'tiphas2',tiphas
                        for tip in typehastypecontdest:
                            print 'tip2',tip
                            if tiphas.idContained.id==tip.idContained.id:
                                trovato=1
                                break
                        if trovato==1:
                            break
                    if trovato==0:
                        return {'data':'err_destination'}
                    
                #solo se sto caricando una piastra o un cassetto
                if tipo=='tube':                   
                    tipoaliqgen=Feature.objects.get(name='AliquotType')
                    tipoaliq=ContainerFeature.objects.filter(Q(idFeature=tipoaliqgen)&Q(idContainer=container))
                    
                    #se e' un cassetto
                    if len(tipoaliq)==0:
                        dra=DrawHandler()
                        return dra.read(request, barcode)
                    typeP=tipoaliq[0].value
                    tipopiastragen=Feature.objects.get(name='PlateAim')
                    #prendo lo scopo della piastra
                    lisscopo=ContainerFeature.objects.filter(Q(idFeature=tipopiastragen)&Q(idContainer=container))
                    if len(lisscopo)!=0:
                        scopo=lisscopo[0].value
                    print 'scopo',scopo
                    contentList = Container.objects.filter(idFatherContainer = container)
                    select = ['idContainerType', 'position', 'barcode', 'availability', 'full']
                    for c in contentList:
                        children.append(Simple(c,select).getAttributes())
                    diz={'typeC':container.idContainerType.name,'children':children,'rules': json.loads(container.idGeometry.rules)}
                    response, dim,err,diztipi = CreaTabella(diz,typeP)
                    if err=='errore':
                        return {'data':'errore_banca'}
                    print 'response',response
                    res = json.loads(response)
                    if res['data']=='errore':
                        return {"data": 'errore'}  
                    
                abbr='r'
                long_name=container.idContainerType.name
                name = 'rna'
                regole_geom=json.loads(container.idGeometry.rules)
                dim = regole_geom['dimension']
                #dimensioni della piastra
                x = int(dim[0])
                y = int(dim[1])
                print 'x',x
                print 'y',y
                row_label = regole_geom['row_label']
                column_label = regole_geom['column_label']
                          
                #inizializzo la tabella. Qui verra' scritto il codice HTML per creare le singole celle della tabella visualizzata dall'utente
                codeList = []
                i = 0
                j = 0
                k=0
                valo=0
                while i < int(y):
                    codeList.append([])
                    j = 0
                    if int(y)>26:
                        valor=i%14
                        if valor==0:
                            valo=valo+1
                            k=0
                    while j < int(x):
                        #calcolo l'id del tasto
                        if int(y)<27:
                            id=abbr+'-'+chr(i+ord('A'))+str(j+1)
                        else:                           
                            id=abbr+'-'+chr(int(valo-1)+ord('A'))+chr(k+ord('A'))+str(j+1)
                        codeList[i].append('<td align="center"><button type="submit" align="center" disabled="disabled" id="'+id+'">X</button></td>')
                        j = j + 1
                    i = i + 1
                    k=k+1
                    
                if tipo=='tube': 
                    for r in res['data']:
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
                            
                            if aliquot=='NOT AVAILABLE':
                                codeList[int(y)-1][int(x)-1] = '<td> <button title="NOT AVAILABLE" type="submit" align="center" id="'+ abbr + '-' + id_position + '" gen="'+aliquot+'" onmouseout="tooltip.hide();" barcode="'+ barcode+'" disabled="disabled">'+ quantity +'</button></td>'
                            else:                            
                                codeList[int(y)-1][int(x)-1] = '<td> <button type="submit" align="center" id="'+ abbr + '-' + id_position + '" sel="s" gen="'+aliquot+'" onmouseout="tooltip.hide();" barcode="'+ barcode+'" disabled="disabled">'+ quantity +'</button></td>'
                        else:
                            #se la provetta e' vuota
                            pieces = r.split(',')
                            barcode =  pieces[0]
                            id_position = pieces[1]
                            coordinates = pieces[2]
                            c = coordinates.split('|')
                            x = c[0]
                            y = c[1]
                            codeList[int(y)-1][int(x)-1] = '<td><button type="submit" align="center" id="'+ abbr + '-' + id_position + '" " barcode="'+ barcode+'" sel="s" gen="'+barcode+'" onmouseout="tooltip.hide();" >0</button></td>'
                #vuol dire che sto caricando un rack o un freezer
                else:
                    #prendo i figli del cont
                    listafigli=Container.objects.filter(idFatherContainer=container)
                    print 'listafigli',listafigli
                    for cont in listafigli:
                        for val in regole_geom['items']:
                            #l'id e' nelle regole del cont
                            if cont.position==val['id']:
                                indici=val['position']
                                barcode=cont.barcode
                                codeList[int(indici[1])-1][int(indici[0])-1]= '<td> <button type="submit" align="center" id="'+ abbr + '-' + cont.position + '" sel="s" gen="'+barcode+'" onmouseout="tooltip.hide();" barcode="'+ barcode+'" disabled="disabled">0</button></td>'
        
                #creo il codice per la tabella HTML
                #lun e' il numero di colonne che l'intestazione della tabella deve coprire
                lun=int(dim[0])+1
                string += '<table align="center" id="' + str(name) + '"><tbody><tr><th colspan="' + str(lun) + '">' + str(long_name) + '</th></tr>'
                string += '<tr>'
                string += '<td class="intest"></td>'
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
                return {'data':string,'scopo':scopo}

        except Exception,e:
            print 'err',e
            return {"data":'errore'}
        
#per avere il contenuto di un cassetto dato il suo barcode e il suo tipo
class DrawHandler(BaseHandler):
    allowed_methods = ('GET')
    model = Container
    @method_decorator(get_functionality_decorator)
    def read(self, request, barcode):
        try:
            print 'barc',barcode
            
            abbr = 'r'
            name = 'rna'
            long_name = 'DRAWER/PLATE'
            cassetto=Container.objects.get(barcode=barcode)
            if cassetto.idContainerType.name!='Drawer':
                tipopiastragen=Feature.objects.get(name='PlateAim')
                tipopiastra=ContainerFeature.objects.filter(Q(idFeature=tipopiastragen)&Q(idContainer=cassetto)&Q(value='Stored'))
                if(tipopiastra.count()==0):
                    return {'data':'errore_piastra'}
            #dimensioni del cassetto
            x = int(json.loads(cassetto.idGeometry.rules)['dimension'][0])
            y = int(json.loads(cassetto.idGeometry.rules)['dimension'][1])
            
            print 'x',x
            print 'y',y
            row_label = json.loads(cassetto.idGeometry.rules)['row_label']
            column_label = json.loads(cassetto.idGeometry.rules)['column_label']
            #inizializzo la tabella. Qui verra' scritto il codice HTML per creare le singole celle della tabella visualizzata dall'utente
            codeList = []
            string = ''
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
            
            #prendo tutti i blocchi che sono in quel cassetto
            listablocchi_tot=Container.objects.filter(idFatherContainer=cassetto)    
            barc=''
            lis_pezzi_url=[]
            #in lis_gen metto tutte le biocassette di quel cassetto
            lis_gen=[]
            for bloc in listablocchi_tot:
                barc+=bloc.barcode+'&&,'
                #2000 e' il numero di caratteri scelto per fare in modo che la url
                #della api non sia troppo lunga
                if len(barc)>2000:
                    #cancello la virgola alla fine della stringa
                    lu=len(barc)-1
                    strbarc=barc[:lu]
                    print 'strbarc',strbarc
                    lis_pezzi_url.append(strbarc)
                    barc=''
            #cancello la virgola alla fine della stringa
            lu=len(barc)-1
            strbarc=barc[:lu]
            print 'strbarc',strbarc
            if strbarc!='':
                lis_pezzi_url.append(strbarc)
            
            if len(lis_pezzi_url)!=0:
                indir=Urls.objects.get(default=1).url
                #print 'indir',indir
                for elementi in lis_pezzi_url:
                    stringa=elementi.replace('#','%23')
                    req = urllib2.Request(indir+"/api/tubes/"+stringa, headers={"workingGroups" : get_WG_string()})
                    u = urllib2.urlopen(req)
                    #u = urllib2.urlopen(indir+"/api/tubes/"+stringa+ "?workingGroups="+get_WG_string())
                    #in data ho i genid di tutti i blocchi di quel cassetto
                    data = json.loads(u.read())
                    print 'data',data
                    for pezzi in data['data']:
                        lis_gen.append(pezzi)
                print 'lis_gen',lis_gen
                     
            #recupero i dati relativi ai blocchi eventualmente gia' contenuti in quel
            #cassetto. Prendo tutte le posizioni del cassetto
            for r in json.loads(cassetto.idGeometry.rules)['items']:
                pos=str(r['id'])
                #vedo quanti container sono gia' presenti in quella posizione
                listablocchi=Container.objects.filter(Q(idFatherContainer=cassetto)&Q(position=pos))
                y=r['position'][1]
                x=r['position'][0]
                #se c'e' qualche blocco in quella posizione
                if len(listablocchi)!=0:
                    gen=''
                    cod=''
                    for blocco in listablocchi:
                        for elem in lis_gen:
                            val=elem.split(',')
                            #in val[0] ho il barcode del blocchetto, in val[3] ho il genid
                            #se e' lungo 5 vuol dire che il blocchetto non e' vuoto
                            if len(val)==5:
                                if val[0]==blocco.barcode:
                                    gen=gen+val[3]+'--'+val[0]+' '
                        cod=blocco.barcode
                    #tolgo l'ultimo spazio dalla stringa
                    lung=len(gen)-1
                    strgen=gen[:lung]
                    if strgen!='':
                        quant=str(len(listablocchi))
                    else:
                        quant='0'
                    if strgen=='NOT AVAILABLE':
                        codeList[int(y)-1][int(x)-1] = '<td><button title="NOT AVAILABLE" type="submit" align="center" id="'+ abbr + '-' +pos + '" gen="'+strgen+'" barcode="'+cod+'" >'+quant+'</button></td>'
                    else:
                        codeList[int(y)-1][int(x)-1] = '<td><button type="submit" align="center" id="'+ abbr + '-' +pos + '" gen="'+strgen+'" barcode="'+cod+'" sel="s" >'+quant+'</button></td>'
                else:
                    codeList[int(y)-1][int(x)-1] = '<td><button type="submit" align="center" id="'+ abbr + '-' +pos + '" >X</button></td>'
            #creo il codice per la tabella HTML
            #lun e' il numero di colonne che l'intestazione della tabella deve coprire
            lun=int(x)+1
            string += '<table align="center" id="' + str(name) + '"><tbody><tr><th colspan="' + str(lun) + '">' + str(long_name) + '</th></tr>'
            string += '<tr>'
            string += '<td class="intest"></td>'
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
            #mi occupo del tipo di piastra caricata
            if cassetto.idContainerType.name!='Drawer':
                feataliq=Feature.objects.get(name='AliquotType')
                contfeat=ContainerFeature.objects.filter(idFeature=feataliq,idContainer=cassetto)
                if len(contfeat)!=0:
                    tipp=contfeat[0].value
                else:
                    tipp='No'
            else:
                tipp='FF'
            return {'data':string,'scopo':'','tipo':tipp,'multiplo':cassetto.idContainerType.maxPosition}
        except Exception, e:
            print 'err',e
            return {"data":'errore'}'''
        
#restituisce, ricevuta una serie di genealogy, la posizione, la piastra, 
#il rack e il freezer di ogni singola provetta. I gen sono separati da &
class TubeHandler(BaseHandler):
    allowed_methods = ('GET')
    @method_decorator(get_functionality_decorator)
    def read(self, request, barcode,utente):
        diz={}
        try:
            listagen=barcode.split('&')
            print 'utente',utente
            print 'l',listagen
            listaaliq=Aliquot.objects.filter(genealogyID__in=listagen)
            #visto che ci possono essere piu' righe per lo stesso campione perche' puo' aver
            #cambiato posizione nel corso della vita, creo un dizionario con chiave il gen e 
            #valore l'oggetto Aliquot piu' recente di quella aliquota
            dizgen={}
            for aliq in listaaliq:
                if dizgen.has_key(aliq.genealogyID):
                    aliqattuale=dizgen[aliq.genealogyID]
                    print 'aliqattuale',aliqattuale
                    #solo se la relazione dell'aliq attuale non e' terminata
                    if aliqattuale.endTimestamp!=None and aliqattuale.endTimestamp!='':
                        #devo guardare se questa nuova e' ancora attiva
                        if aliq.endTimestamp==None or aliq.endTimestamp=='':
                            #salvo questa perche' e' quella effettiva che serve
                            dizgen[aliq.genealogyID]=aliq
                        else:
                            #se e' conclusa anche questa relazione prendo quella con la data di termine
                            #piu' recente
                            print 'aliq nuova',aliq.endTimestamp
                            print 'aliq attuale',aliqattuale.endTimestamp
                            if aliq.endTimestamp>aliqattuale.endTimestamp:
                                dizgen[aliq.genealogyID]=aliq
                else:
                    dizgen[aliq.genealogyID]=aliq
                    print 'aliq',aliq
            print 'dizgen',dizgen
            for key in dizgen.keys():
                aliq=dizgen[key]
                print 'container',aliq.idContainer
                if aliq.idContainer!=None:
                    #se la relazione e' finita
                    if aliq.endTimestamp!=None and aliq.endTimestamp!='':
                        disp='No'
                    else:
                        if aliq.idContainer.availability==1:
                            disp='Yes'
                        else:
                            if utente=='None':
                                disp='No'
                            elif aliq.idContainer.owner==utente:
                                disp='Yes'
                            else:
                                disp='No'
                        print 'disp',disp
                    rack='None'
                    freezer='None'
                    if aliq.position=='' or aliq.position==None:
                        provetta=aliq.idContainer
                        #creo la stringa da restituire che contiene il barcode, la posizione
                        #e la piastra
                        #le aliq FF o OF o CH non hanno posizione e barcode
                        print 'prov',provetta
                        if provetta.position!=None and provetta.idFatherContainer!=None:
                            pospiastranelrack=provetta.idFatherContainer.position
                            if provetta.idFatherContainer.idFatherContainer!=None:
                                rack=provetta.idFatherContainer.idFatherContainer.barcode
                                if provetta.idFatherContainer.idFatherContainer.idFatherContainer!=None:
                                    freezer=provetta.idFatherContainer.idFatherContainer.idFatherContainer.barcode
                            print 'rack',rack
                            print 'gentipo',provetta.idContainerType.idGenericContainerType.name
                            if provetta.idContainerType.name!='FF' and provetta.idContainerType.name!='OF' and provetta.idContainerType.name!='CH' :
                                valori=provetta.barcode+'|'+provetta.position+'|'+unicode(provetta.idFatherContainer.barcode)+'|'+unicode(pospiastranelrack)+'|'+rack+'|'+freezer+'|'+disp
                            else:
                                valori=provetta.barcode+'|'+provetta.position+'|'+unicode(provetta.idFatherContainer.barcode)+'|None|None|'+rack+'|'+disp   
                        else:
                            valori=provetta.barcode+'|None|None|None|None|None|'+disp
                        print 'valori',valori
                    else:
                        #sto trattando il caso delle piastre con i pozzetti, quindi il container di riferimento e' gia' la piastra
                        #e non la provetta come al solito
                        piastra=aliq.idContainer
                        print 'piastra',piastra
                        pos=aliq.position
                        print 'aliq',aliq
                        if piastra.idFatherContainer!=None:
                            rack=piastra.idFatherContainer.barcode
                            print 'rack',rack
                            if piastra.idFatherContainer.idFatherContainer!=None:
                                freezer=piastra.idFatherContainer.idFatherContainer.barcode
                        print 'barc',piastra.barcode
                        valori='None|'+pos+'|'+str(piastra.barcode)+'|'+str(piastra.position)+'|'+rack+'|'+freezer+'|'+disp                    
                else:
                    #vuol dire che il campione e' esaurito perche' non ha una posizione in una provetta
                    valori='None|None|None|None|None|None|No'
                diz[aliq.genealogyID]=valori
            return{'data':json.dumps(diz)}
        except Exception, e:
            print 'err',e
            return {"data":'errore'}

#restituisce, ricevuta una serie di barcode di provette, la posizione, la piastra, 
#il rack e il freezer di ogni singola provetta. I barcode sono separati da &
'''class TubeHandler(BaseHandler):
    allowed_methods = ('GET')
    def read(self, request, barcode,utente):
        lista=[]
        try:
            listabarc=barcode.split('&')
            print 'utente',utente
            print 'l',listabarc
            for i in range(0,len(listabarc)-1):
                provetta=Container.objects.get(barcode=listabarc[i])
                #creo la stringa da restituire che contiene il barcode, la posizione
                #e la piastra
                #le aliq FF o OF o CH non hanno posizione e barcode
                print 'prov',provetta
                if provetta.availability==1:
                    disp='Yes'
                else:
                    if utente=='None':
                        disp='No'
                    elif provetta.owner==utente:
                        disp='Yes'
                    else:
                        disp='No'
                print 'disp',disp
                if provetta.position!=None and provetta.idFatherContainer!=None:
                    rack='None'
                    freezer='None'
                    pospiastranelrack=provetta.idFatherContainer.position
                    
                    if provetta.idFatherContainer.idFatherContainer!=None:
                        rack=provetta.idFatherContainer.idFatherContainer.barcode
                        if provetta.idFatherContainer.idFatherContainer.idFatherContainer!=None:
                            freezer=provetta.idFatherContainer.idFatherContainer.idFatherContainer.barcode
                    print 'rack',rack
                    print 'gentipo',provetta.idContainerType.idGenericContainerType.name
                    if provetta.idContainerType.name!='FF' and provetta.idContainerType.name!='OF' and provetta.idContainerType.name!='CH' :
                        valori=listabarc[i]+'|'+provetta.position+'|'+unicode(provetta.idFatherContainer.barcode)+'|'+unicode(pospiastranelrack)+'|'+rack+'|'+freezer+'|'+disp
                    else:
                        valori=listabarc[i]+'|'+provetta.position+'|'+unicode(provetta.idFatherContainer.barcode)+'|None|None|'+rack+'|'+disp
                    
                else:
                    valori=listabarc[i]+'|None|None|None|None|None|'+disp
                print 'valori',valori
                lista.append(valori)
            return{"data":lista}
        except Exception, e:
            print 'err',e
            return {"data":'errore'}'''
        
#mi restituisce l'indirizzo della biobanca
class AddressHandler(BaseHandler):
    allowed_methods = ('GET')
    @method_decorator(get_functionality_decorator)
    def read(self, request):
        try:
            indirizzo=Urls.objects.get(default = '1').url
            return {'data':indirizzo}
        except:
            return {"data":'errore'}
        
#serve per vedere se un contenitore di paraffina o altro esiste e se e' gia' pieno. E'
#chiamata dalla schermata della collezione.
#Serve anche quando si archiviano gli FFPE o le provette con il sangue per capire se
#il blocchetto e' gia' stato archiviato o no
class BioCasHandler(BaseHandler):
    allowed_methods = ('GET')
    @method_decorator(get_functionality_decorator)
    def read(self, request,barcode,tipo,archive):
        try:
            r=CheckBarcodeHub(barcode, request)
            if r.text=='True':
                return Biocass(barcode,tipo,archive)
            elif r.text=='False':
                if not archive:
                    return {'data':'err_esistente'}
                else:
                    return Biocass(barcode,tipo,archive)
            elif r.text=='not active':
                print 'tipoooo',tipo
                return Biocass(barcode,tipo,archive)
        except Exception, e:
            print 'err',e
            return {"data":'errore'}
        
'''#per avere il contenuto di una piastra dato il suo barcode
class TableHandler(BaseHandler):
    allowed_methods = ('GET')
    @method_decorator(get_functionality_decorator)
    def read(self, request, barcodeP, typeP, store):
        #print 'request',request
        try:
            abbr = ""
            name = ""
            print 'tipo',typeP
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
            if typeP == 'FF':
                abbr = 'r'
                name = 'rna'
                long_name = 'DRAWER'
            #mi serve quando non so il tipo della piastra a priori e sto spostando
            #campioni dalle piastre costar
            tipoaliqgen=Feature.objects.get(name='AliquotType')
            #se sto spostando aliquote
            if typeP == 'well':
                abbr = 'r'
                name = 'rna'
                print 'barcode',barcodeP
                piastra=Container.objects.filter(barcode=barcodeP)
                if len(piastra)==0:
                    return {"data": 'errore'}
                else:
                    pias=piastra[0]
                    if not store:
                        listaconttipi=ContTypeHasContType.objects.filter(idContainer=pias.idContainerType)
                        #guardo se quella piastra puo' contenere aliquote nei pozzetti
                        trovato=0
                        for conttipi in listaconttipi:
                            if conttipi.idContained==None:
                                trovato=1
                                break
                        if trovato==0:
                            return {'data':'errore_vital'}
                        
                        tipoaliq=ContainerFeature.objects.filter(Q(idFeature=tipoaliqgen)&Q(idContainer=pias)).order_by('id')
                        typeP=tipoaliq[0].value
                        print 'type',typeP
                        long_name=tipoaliq[0].value
                    else:
                        typeP='TRANS'
            #se sto spostando i container     
            if typeP == 'tube':
                abbr = 'r'
                name = 'rna'
                print 'barcode',barcodeP
                piastra=Container.objects.filter(barcode=barcodeP)
                if len(piastra)==0:
                    return {"data": 'errore'}
                else:
                    pias=piastra[0]
                    
                    listaconttipi=ContTypeHasContType.objects.filter(idContainer=pias.idContainerType)
                    #guardo se quella piastra puo' contenere aliquote nei pozzetti
                    trovato=0
                    for conttipi in listaconttipi:
                        if conttipi.idContained==None:
                            return {'data':'errore_piastra'}
                    
                    tipoaliq=ContainerFeature.objects.filter(idFeature=tipoaliqgen,idContainer=pias).order_by('id')
                    print 'tipoaliq',tipoaliq
                    typeP=tipoaliq[0].value
                    print 'type',typeP
                    long_name=tipoaliq[0].value
                    
            string = ""
            print 'barc',barcodeP
            loaa=LoadHandler()
            try:
                if not store:# and not move:  
                    print 'non store'        
                    aaa=loaa.read(request, barcodeP, typeP, '', '')
                    #u = urllib2.urlopen(indir+"/api/plate/"+barcodeP + '/' + typeP+'/')
                elif store:
                    print 'store'
                    aaa=loaa.read(request, barcodeP, typeP, 'stored', '')
                    #u = urllib2.urlopen(indir+"/api/plate/"+barcodeP + '/' + typeP+'/stored')
                
                #data = json.loads(u.read())
                data=aaa
                print 'data',data
            except Exception, e:
                print 'e',e
                return {'data':'errore_store'}
            
            #se non ho un tipo non restituisco l'errore
            if typeP!='None':
                if data['data']=='errore_aliq':
                    return {'data':'errore_aliq'}
            #solo se non chiamo questa api dalla schermata di move
            #if not move:
            if data['data']=='errore_piastra':
                return {'data':'errore_piastra'}  

            #response, dim = tableImpl(data,typeP)
            row_label = data['rules']['row_label']
            column_label = data['rules']['column_label']
            j = 0
            #creare una lista di barcode da inviare alla biobanca per poi analizzarne la risposta
            try:
                
                #se sto caricando la transitoria, allora devo assegnargli il tipo di aliquota
                if typeP=='TRANS':
                    tipoaliq=ContainerFeature.objects.get(Q(idFeature=tipoaliqgen)&Q(idContainer=pias))
                    typeP=tipoaliq.value
                    print 'type',typeP
                    long_name=tipoaliq.value
                response, dim,err,diztipi = CreaTabella(data,typeP)
                if err=='errore':
                    return {'data':'errore_banca'}
                #dimensioni della piastra
                x = int(dim[0])
                y = int(dim[1])
                print 'x',x
                print 'y',y
                print 'response',response
                res = json.loads(response)
                if res['data']=='errore':
                    return {"data": 'errore'}
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
                
                for r in res['data']:
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
                        if aliquot=='NOT AVAILABLE':
                            codeList[int(y)-1][int(x)-1] = '<td> <button title="NOT AVAILABLE" type="submit" align="center" id="'+ abbr + '-' + id_position + '" gen="'+aliquot+'" barcode="'+ barcode+'" disabled="disabled">'+ quantity +'</button></td>'
                        else:
                            codeList[int(y)-1][int(x)-1] = '<td> <button type="submit" align="center" id="'+ abbr + '-' + id_position + '" sel="s" gen="'+aliquot+'" onmouseout="tooltip.hide();" barcode="'+ barcode+'" disabled="disabled">'+ quantity +'</button></td>'
                        #codeList[int(y)-1][int(x)-1] = '<td> <button type="submit" align="center" id="'+ abbr + '-' + id_position + '" sel="s" gen="'+aliquot+'" onmouseout="tooltip.hide();" barcode="'+ barcode+'" disabled="disabled">'+ quantity +'</button></td>'
                    else:
                        #se la provetta e' vuota
                        pieces = r.split(',')
                        barcode =  pieces[0]
                        id_position = pieces[1]
                        coordinates = pieces[2]
                        c = coordinates.split('|')
                        x = c[0]
                        y = c[1]
                        codeList[int(y)-1][int(x)-1] = '<td><button type="submit" align="center" id="'+ abbr + '-' + id_position + '" " barcode="'+ barcode+'">0</button></td>'
            except Exception, e:
                print 'error',e

            #creo il codice per la tabella HTML
            #lun e' il numero di colonne che l'intestazione della tabella deve coprire
            lun=int(dim[0])+1
            string += '<table align="center" id="' + str(name) + '"><tbody><tr><th colspan="' + str(lun) + '">' + str(long_name) + '</th></tr>'
            string += '<tr>'
            string += '<td class="intest"></td>'
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
            lista=[]
            lista.append(typeP)
            return {'data':string,'scopo':lista}
        except Exception, e:
            print 'err',e
            return {"data": 'errore'}'''
        
#per avere il contenuto di una piastra dato il suo barcode
class TableHandler(BaseHandler):
    allowed_methods = ('GET')
    @method_decorator(get_functionality_decorator)
    def read(self, request, barcodeP, typeP, spostamento):
        #print 'request',request
        try:
            long_name=''
            listipi=''
            string = ''
            print 'tipo',typeP
            print 'spostamento',spostamento
            itself=False
            contpadre=''           
            
            abbr = 'r'
            name = 'rna'
            print 'barcode',barcodeP
            #se ho fatto uno zoom su un posto con piu' aliquote dentro
            if spostamento=='aliquot':
                string,listipi=visualizzaAliquote(barcodeP)
            else:
                tipoaliqgen=Feature.objects.get(name='AliquotType')
                defval=FeatureDefaultValue.objects.filter(idFeature=tipoaliqgen)
                piastra=Container.objects.filter(barcode=barcodeP,present=1)
                print 'cont',piastra
                if len(piastra)==0:
                    #potrebbe essere che ho chiamato la API per far vedere i cont che hanno tutti una stessa
                    #posizione all'interno del padre (es. cassetto). Se e' cosi' i barc sono separati da &
                    lisbarc=barcodeP.split('&')
                    liscont=Container.objects.filter(barcode__in=lisbarc,present=1)
                    print 'liscont',liscont
                    #se il tipo spostamento e' simple vuol dire che sto caricando un cont normale e non voglio 
                    #vedere i figli di un cont
                    if len(liscont)==0 or spostamento=='simple':
                        return {"data": 'errore'}
                    else:
                        string=visualizzaBlocchetti(barcodeP,typeP,spostamento,tipoaliqgen,defval,piastra,liscont)                                                    
                else:                
                    pias=piastra[0]
                    long_name='Barcode: '+barcodeP+' Type: '+pias.idContainerType.actualName
                    piastipo=pias
                    if typeP == 'itself':
                        itself=True
                        #devo far vedere il padre con all'interno il cont caricato
                        if pias.idFatherContainer!=None:
                            pias=pias.idFatherContainer
                            long_name='Barcode: '+pias.barcode+' Type: '+pias.idContainerType.actualName
                            piastipo=pias               
                        else:
                            pias=None
                            piastipo=piastra[0]
                            
                    tipoaliq=ContainerFeature.objects.filter(idFeature=tipoaliqgen,idContainer=piastipo).order_by('id')
                    
                    long_name+=' Aliquot: '
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
                    print 'pias',pias
                    if pias!=None:
                        children=caricaFigli(pias)
                        piascostar=False
                        #guardo se e' una piastra con i pozzetti
                        gentipo=ContTypeHasContType.objects.filter(idContainer=pias.idContainerType)
                        for tip in gentipo:
                            if tip.idContained==None:
                                piascostar=True
                        print 'children',children
                        regole=json.loads(pias.idGeometry.rules)
                        diz={'typeC':pias.idContainerType.name,'children':children,'rules': regole,'piascostar':piascostar,'cont':pias}           
            
                        row_label = diz['rules']['row_label']
                        column_label = diz['rules']['column_label']
                        j = 0
                        #creare una lista di barcode da inviare alla biobanca per poi analizzarne la risposta
                        try:
                            #il typeP non mi serve piu' in questa funzione
                            res, dim,err,diztipi,diztipcontainer,dizsalvaliq,dizpieno = CreaTabella(diz,typeP)
                            if err=='errore':
                                return {'data':'errore_banca'}
                            #dimensioni della piastra
                            x = int(dim[0])
                            y = int(dim[1])
                            print 'x',x
                            print 'y',y
                            print 'res',res
                            #res = json.loads(response)
                            #if res['data']=='errore':
                                #return {"data": 'errore'}
                            #inizializzo la tabella. Qui verra' scritto il codice HTML per creare le singole celle della tabella visualizzata dall'utente
                            codeList = []
                            i = 0
                            j = 0
                            salval=False
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
                                    codeList[i].append('<td id="h-'+ id_position +'" aliq="'+ str(salval)+'" align="center"><button type="submit" class="disp" align="center" disabled="disabled" id="'+idtasto+'" col="'+str(j)+'" row="'+str(i)+'">X</button></td>')
                                    j = j + 1
                                i = i + 1
                            #dizionario per salvare i gen, i barc e il tipoaliq per i campioni che hanno piu' aliquote nello
                            #stesso posto
                            dizdoppi={}
                            #recupero i dati relativi alle aliquote eventualmente contenute nelle varie provette                        
                            for r in res:                                    
                                if len(r.split(',')) > 3:
                                    
                                    #se la provetta contiene un'aliquota
                                    pieces = r.split(',')
                                    barcode =  pieces[0]
                                    cont=''
                                    posmax=pias.idContainerType.maxPosition
                                    salvaliq=False
                                    pieno=False
                                    barctemp=barcode.encode('utf-8')
                                    if barctemp in diztipcontainer:                                        
                                        conttipo=diztipcontainer[barctemp]                                        
                                        #print 'conttipo',conttipo
                                        if conttipo!=None:
                                            cont=str(conttipo.id)
                                            posmax=conttipo.maxPosition
                                        salvaliq=dizsalvaliq[barctemp]
                                        pieno=dizpieno[barctemp]
                                    #print 'sala',salvaliq
                                    id_position = pieces[1]
                                    coordinates = pieces[2]
                                    aliquot = pieces[3]
                                    quantity = 1
                                    tipoaliq = pieces[5]
                                    print 'tipoaliq',tipoaliq
                                    chiave=id_position+coordinates
                                    if chiave in dizdoppi:
                                        diztemp=dizdoppi[chiave]
                                        aliqtemp=diztemp['gen']
                                        #serve nel caso in cui ho una provetta vuota iniziale che mi fa mettere gia' una & nella
                                        #stringa e non devo piu' aggiungerla qui
                                        #if aliqtemp[-1]=='&':
                                        #    aliquot=aliqtemp+aliquot
                                        #else:
                                        aliquot=aliqtemp+'&'+aliquot
                                        barctemp=diztemp['barc']
                                        barcode=barctemp+'&'+barcode
                                        tipotemp=diztemp['tipo']
                                        pienotemp=diztemp['pieno']
                                        if pienotemp or pieno:
                                            pieno=True
                                        #solo se il tipo di questa aliquota non e' un subset di quelle
                                        #gia' presenti
                                        if not ControllaAliquota(tipotemp, tipoaliq):
                                            tipoaliq=tipotemp+'&'+tipoaliq
                                        quant=diztemp['num']
                                        quantity=quant+1
                                        diztemp['num']=quantity
                                    else:
                                        diztemp={}                                  
                                        diztemp['num']=quantity
                                        
                                    diztemp['gen']=aliquot
                                    diztemp['barc']=barcode
                                    diztemp['tipo']=tipoaliq
                                    diztemp['pieno']=pieno
                                    dizdoppi[chiave]=diztemp                
                                    c = coordinates.split('|')
                                    x = c[0]
                                    y = c[1]
                                    classetasto=''
                                    if piascostar:
                                        classetasto+='aliqclass'
                                        if quantity==1:
                                            quantity=pieces[4]
                                            classetasto+=' foglia'                                        
                                    if pieces[3]=='NOT AVAILABLE':
                                        codeList[int(y)-1][int(x)-1] = '<td id="h-'+ id_position +'" aliq="'+ str(salvaliq)+ '" posmax="' + str(posmax)+'" notavailable="True" > <button title="NOT AVAILABLE" type="submit" align="center" id="'+ abbr + '-' + id_position +'" col="'+str(int(x)-1)+'" row="'+str(int(y)-1)+'" class="'+classetasto+ '" gen="'+aliquot+ '" pieno="'+str(pieno)+'" barcode="'+ barcode+'" aliq="'+ str(salvaliq)+'" tipo="'+ tipoaliq+'" cont="'+ cont+'" disabled="disabled">X</button></td>'
                                    else:
                                        #per sapere se il cont puo' ancora ospitare aliq o altri cont
                                        if str(quantity).isdigit():
                                            if salvaliq:
                                                if posmax==None or not pieno or int(posmax)-int(quantity)>0 or pias.idContainerType.maxPosition==None or int(pias.idContainerType.maxPosition)-int(quantity)>0:
                                                    classetasto+=' disp'
                                            else:
                                                if pias.idContainerType.maxPosition==None or int(pias.idContainerType.maxPosition)-int(quantity)>0:
                                                    classetasto+=' disp'
                                        else:
                                            if posmax==None or int(posmax)-1>0:
                                                classetasto+=' disp'
                                        codeList[int(y)-1][int(x)-1] = '<td id="h-'+ id_position +'" aliq="'+ str(salvaliq)+ '" posmax="' + str(posmax)+'" > <button type="submit" align="center" id="'+ abbr + '-' + id_position +'" col="'+str(int(x)-1)+'" row="'+str(int(y)-1)+ '" sel="s" class="'+classetasto+ '" gen="'+aliquot+ '" pieno="'+str(pieno)+'" barcode="'+ barcode+'" aliq="'+ str(salvaliq)+'" tipo="'+ tipoaliq+'" cont="'+ cont+'" disabled="disabled">'+ str(quantity) +'</button></td>'
                                    #codeList[int(y)-1][int(x)-1] = '<td> <button type="submit" align="center" id="'+ abbr + '-' + id_position + '" sel="s" gen="'+aliquot+'" onmouseout="tooltip.hide();" barcode="'+ barcode+'" disabled="disabled">'+ quantity +'</button></td>'
                                else:
                                    #se la provetta e' vuota
                                    pieces = r.split(',')
                                    barcode =  pieces[0]
                                    id_position = pieces[1]
                                    coordinates = pieces[2]                                                                        
                                    salvaliq=False
                                    cont=''
                                    posmax=pias.idContainerType.maxPosition
                                    barctemp=barcode.encode('utf-8')
                                    pieno=False
                                    if barctemp in diztipcontainer:                                        
                                        conttipo=diztipcontainer[barctemp]
                                        if conttipo!=None:
                                            cont=str(conttipo.id)
                                            posmax=conttipo.maxPosition
                                        salvaliq=dizsalvaliq[barctemp]
                                        pieno=dizpieno[barctemp]
                                        
                                    strtipi=''
                                    if barcode in diztipi:
                                        listip=diztipi[barcode]
                                        strtipi=''
                                        for val in listip:                                    
                                            strtipi+=val+'&'
                                        strtipi=strtipi[:-1]
                                    
                                    c = coordinates.split('|')
                                    x = c[0]
                                    y = c[1]
                                    
                                    chiave=id_position+coordinates
                                    if chiave in dizdoppi:
                                        diztemp=dizdoppi[chiave]
                                        aliqtemp=diztemp['gen']
                                        aliquot=aliqtemp+'&'
                                        barctemp=diztemp['barc']
                                        barcode=barctemp+'&'+barcode                                            
                                        quant=diztemp['num']
                                        quantity=quant+1
                                        pienotemp=diztemp['pieno']
                                        if pienotemp or pieno:
                                            pieno=True                      
                                    else:
                                        diztemp={}
                                        aliquot=''
                                        quantity=1                                    
                                    
                                    diztemp['gen']=aliquot
                                    diztemp['barc']=barcode
                                    diztemp['num']=quantity
                                    diztemp['pieno']=pieno
                                    diztemp['tipo']=strtipi
                                    dizdoppi[chiave]=diztemp
                                    classetasto=''
                                    if pias.idContainerType.maxPosition==1:
                                        #metto 1 perche' non faccio piu' vedere il valore del contenuto della provetta,
                                        #ma il numero di figli presenti in quella posizione
                                        quantity=1
                                        #se e' una costar non metto sel=s cosi' non si possono poi spostare i posti vuoti della piastra
                                        if piascostar:
                                            quantity=0
                                            sel=''
                                        else:
                                            sel='sel="s"'
                                        if str(quantity).isdigit():
                                            if salvaliq:
                                                if posmax==None or not pieno or int(posmax)-int(quantity)>0 or pias.idContainerType.maxPosition==None or int(pias.idContainerType.maxPosition)-int(quantity)>0:
                                                    classetasto+=' disp'
                                            else:
                                                if pias.idContainerType.maxPosition==None or int(pias.idContainerType.maxPosition)-int(quantity)>0:
                                                    classetasto+=' disp'
                                        else:
                                            if posmax==None or int(posmax)-1>0:
                                                classetasto+=' disp'
                                        genealogy=''                                        
                                    else:
                                        quantity=quantity
                                        #se e' una costar non metto sel=s cosi' non si possono poi spostare i posti vuoti della piastra
                                        if piascostar:
                                            if quantity==1:
                                                quantity=0
                                            sel=''                                            
                                        else:
                                            sel='sel="s"'
                                        if str(quantity).isdigit():
                                            if salvaliq:
                                                if posmax==None or not pieno or int(posmax)-int(quantity)>0 or pias.idContainerType.maxPosition==None or int(pias.idContainerType.maxPosition)-int(quantity)>0:
                                                    classetasto+=' disp'
                                            else:
                                                if pias.idContainerType.maxPosition==None or int(pias.idContainerType.maxPosition)-int(quantity)>0:
                                                    classetasto+=' disp'
                                        else:
                                            if posmax==None or int(posmax)-1>0:
                                                classetasto+=' disp'
                                        genealogy='gen="'+aliquot+'"'
                                    codeList[int(y)-1][int(x)-1] = '<td id="h-'+ id_position +'" aliq="'+ str(salvaliq)+ '" posmax="' + str(posmax)+'" ><button type="submit" align="center" '+sel+' id="'+ abbr + '-' + id_position +'" col="'+str(int(x)-1)+'" row="'+str(int(y)-1)+'" class="'+classetasto+ '" " barcode="'+ barcode+'" aliq="'+ str(salvaliq)+ '" '+genealogy+' pieno="'+str(pieno)+'" cont="'+ cont+'" tipo="'+ strtipi+'">'+str(quantity)+'</button></td>'                                                                                     
                                    
                        except Exception, e:
                            print 'error',e
            
                        #creo il codice per la tabella HTML
                        #lun e' il numero di colonne che l'intestazione della tabella deve coprire
                        lun=int(dim[0])+1
                        print 'pias',pias
                        multiplo=''
                        if pias.idFatherContainer!=None:
                            contpadre=pias.idFatherContainer.barcode
                            #se sono nel caso in cui ho fatto zoom- su un blocchetto il suo padre e' il cassetto, ma io voglio vedere
                            #la lista dei blocchetti e non direttamente il cassetto. Questo puo' valere anche in altri casi
                            lisc=Container.objects.filter(idFatherContainer=pias.idFatherContainer,position=pias.position)
                            if len(lisc)>1:
                                strbarc=''
                                for c in lisc:
                                    strbarc+=c.barcode+'&'
                                contpadre=strbarc[:-1]
                                multiplo='true'
                        else:
                            if typeP=='itself' and spostamento=='simple':
                                contpadre=pias.barcode
                        print 'contpadre',contpadre
                        mult="False"
                        string += '<table align="center" id="' + str(name) + '" mult="'+ mult+ '" barcode="'+ pias.barcode+ '" costar="'+ str(piascostar)+ '" multiplo="'+ multiplo+'" cont="' + str(pias.idContainerType.id) + '" tipo="' + str(listipi)+ '" col="' + str(dim[0])+ '" row="' + str(dim[1])+ '" father="' + str(contpadre) + '" posmax="' + str(pias.idContainerType.maxPosition) + '" ><tbody><tr><th colspan="' + str(lun) + '">' + str(long_name) + '</th></tr>'
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
                        string += "</tbody></table></div></div>"
                                           
                    else:
                        if piastra[0].idFatherContainer!=None:
                            contpadre=piastra[0].idFatherContainer.barcode
                        print 'contpadre', contpadre
                        piascostar=False
                        #guardo se e' una piastra con i pozzetti
                        gentipo=ContTypeHasContType.objects.filter(idContainer=piastra[0].idContainerType)
                        for tip in gentipo:
                            if tip.idContained==None:
                                piascostar=True
                        #vuol dire che devo far vedere il container stesso e non i suoi figli
                        #come quantita' non faccio piu' vedere il #, ma il numero di figli del container
                        lisc=Container.objects.filter(idFatherContainer=piastra[0])
                        pieno=False
                        if len(lisc)!=0:
                            pieno=True
                        #se il cont non e' una provetta blocco la possibilita' di inserirvi aliquote
                        salvaaliq=False
                        if piastra[0].idContainerType.idGenericContainerType.abbreviation=='tube':
                            salvaaliq=True
                        mult="False"
                        string += '<table align="center" id="rna" cont="' + str(piastra[0].idContainerType.id) + '" mult="'+ mult+ '" costar="'+ str(piascostar)+ '" barcode="'+ piastra[0].barcode+'" tipo="' + str(listipi)+ '" col="1" row="1" itself="itself" father="' + str(contpadre) + '" posmax="' + str(piastra[0].idContainerType.maxPosition) + '" ><tbody><tr><th>' + str(long_name) + '</th></tr>'
                        string += '<tr>'
                        #nella visione itself di un cont metto o- e a- come id per differenziare dalla visione normale. In modo che se 
                        #posiziono un cont in m-A1, lo vedo nella visualizzazione children, ma non nella visualizzazione itself
                        string += '<td id="a-A1"> <button type="submit" align="center" itself="itself" id="o-A1" sel="s" gen="notdefined" col="0" row="0" barcode="'+ piastra[0].barcode+ '" aliq="'+ str(salvaaliq)+ '" pieno="'+ str(pieno)+'" cont="' + str(piastra[0].idContainerType.id) + '" tipo="' + str(listipi) + '" disabled="disabled">'+str(len(lisc))+'</button></td>'
                        string += '</tr></tbody></table>'
                    
            return {'data':string,'aliq':listipi,'itself':itself}
        except Exception, e:
            print 'err',e
            return {"data": 'errore'}
        
'''#serve per capire se si puo' fare la modalita' batch nella'archiviazione delle
#aliquote o se qualche posto della piastra destinazione e' gia' occupato           
class StoreBatchHandler(BaseHandler):
    allowed_methods = ('GET')
    #print 'aliq chiamata'
    @method_decorator(get_functionality_decorator)
    def read(self, request, barcodedest,stringa):
        trovato=False
        val=string.split(stringa, "_")
        try:
            piasdest=Container.objects.get(barcode=barcodedest)
            provette=Container.objects.filter(Q(idFatherContainer=piasdest)&Q(full=1))
            for prov in provette:
                for j in range(0,len(val)):
                    if prov.position==val[j]:
                        trovato=True
                        break
            print 'trovato',trovato
            return {"data":trovato}
        except:
            return {"data":'errore'}'''
        
#serve, dato il barcode di un'aliquota, a capire se questa si trova in una piastra vitale di
#tipo stored           
class VitalHandler(BaseHandler):
    allowed_methods = ('GET')
    @method_decorator(get_functionality_decorator)
    def read(self, request, barcode):
        try:
            cont=Container.objects.get(barcode=barcode)
            feat=Feature.objects.get(name='PlateAim')
            print 'feat',feat
            #devo prendere il container padre che e' la piastra
            if cont.idFatherContainer==None:
                return {"data":0}
            contfeat=ContainerFeature.objects.get(Q(idFeature=feat)&Q(idContainer=cont.idFatherContainer.id))
            if contfeat.value!='Stored':
                return {"data":0}
            else:
                return {"data":1}
        except:
            return {"data":'errore'}
        
#dato il tipo di container restituisce i singoli container che possono contenerlo         
class InsertContHandler(BaseHandler):
    allowed_methods = ('GET')
    @method_decorator(get_functionality_decorator)
    def read(self, request, tipo):
        try:
            lista1=[]
            lis_container=[]
            lis=''
            tipo_cont=ContainerType.objects.get(name=tipo)
            #vedo quali container possono contenere il tipo scelto
            listatipi=ContTypeHasContType.objects.filter(idContained=tipo_cont)
            for i in range(0,len(listatipi)):
                lista1.append( Q(**{'idContainerType': listatipi[i].idContainer} ))
            print 'lista1',lista1
            if len(lista1)!=0:
                lis_container=Container.objects.filter( Q(reduce(operator.or_, lista1))&Q(full=0) )
            print 'lis_container',lis_container
            for i in range(0,len(lis_container)):
                lis=lis+str(lis_container[i].id)+':'+lis_container[i].barcode+';'
            return {"data":lis}
        except Exception,e:
            print 'err',e
            return {"data":'errore'}
        
#dato freezer, rack, piastra e posizione (tutti opzionali) verifica se ci sono ancora
#posizioni disponibili      
class CheckAvailHandler(BaseHandler):
    allowed_methods = ('GET')
    @method_decorator(get_functionality_decorator)
    def read(self, request, freezer,rack,plate,position,tipo_cont):
        try:
            pos=position.upper()
            if freezer!='undefined':
                fr=Container.objects.get(id=freezer)    
                print 'fr',fr         
                if rack=='None':
                    #sono nel caso in cui sto inserendo un nuovo rack e devo vedere se
                    #dentro al freezer c'e' ancora posto
                    regole=json.loads(fr.idGeometry.rules)
                    if fr.full==1:
                        return {"data":'0'}
                    #se il freezer e' quello con azoto, allora non c'e' una posizione
                    if fr.idContainerType.name[0:4]=='-196':
                        print 'ok'
                        #prendo le dimensioni del frigo e vedo se ci sta ancora un rack          
                        dimensioni=regole['dimension']
                        xDim=dimensioni[1]
                        yDim=dimensioni[0]
                        rack_tot=xDim*yDim
                        rack_attuali=Container.objects.filter(idFatherContainer=fr)
                        print 'r_tot',rack_tot
                        print 'r_att',len(rack_attuali)
                        if len(rack_attuali)>=rack_tot:
                            #non ho piu' posto
                            return {"data":'0'}
                        else:
                            return {"data":'1'}
                    #devo verificare se la posizione inserita sia coerente con gli id scritti
                    #nelle regole della geometria del singolo container
                    trovato=0
                    for reg in regole['items']:
                        if reg['id']==pos:
                            trovato=1
                            print 'id',reg['id']
                            break
                    if trovato==0:
                        return {"data":'err_posizione'}
                    
                    cont=Container.objects.filter(Q(idFatherContainer=fr)&Q(position=pos))
                    print 'len',len(cont)
                    if len(cont)==0:
                        return {"data":'1'}
                    else:
                        return {"data":'0'}
                else:
                    #sono nel caso in cui sto inserendo una nuova piastra in un rack
                    lista_r=Container.objects.filter(barcode=rack)
                    print 'lista',lista_r
                    if len(lista_r)==0:
                        return {"data":'0'}
                    #se il rack esiste
                    r=lista_r[0]
                    print 'r',r
                    #devo vedere se il rack selezionato puo' contenere quella tipologia
                    #di piastra
                    tip=ContainerType.objects.get(id=tipo_cont)
                    print 'tip',tip
                    #vedo quali container possono contenere il tipo scelto
                    listatipi=ContTypeHasContType.objects.filter(idContained=tip)
                    print 'lista',listatipi
                    trov=0
                    for tipi in listatipi:
                        if tipi.idContainer.id==r.idContainerType.id:
                            trov=1
                            print 'tipi',tipi.idContainer
                            break
                    if trov==0:
                        return {"data":'err_tipo_cont'}
                    
                    #devo vedere se in quel rack c'e' ancora posto
                    #verifico se il rack appartiene effettivamente a quel freezer
                    if r.idFatherContainer.id!=fr.id:
                        print 'fatherCont',r.idFatherContainer
                        return {"data":'0'}
                    #se il freezer e' quello con azoto
                    '''if fr.idContainerType.name[0:4]=='-196':
                        print 'ok'
                        #prendo le dimensioni del rack e vedo se ci sta ancora una piastra          
                        regole=json.loads(r.idGeometry.rules)
                        dimensioni=regole['dimension']
                        xDim=dimensioni[1]
                        yDim=dimensioni[0]
                        pias_tot=xDim*yDim
                        pias_attuali=Container.objects.filter(idFatherContainer=r)
                        print 'pias_tot',pias_tot
                        print 'pias_att',len(pias_attuali)
                        if len(pias_attuali)>=pias_tot:
                            #non ho piu' posto
                            return {"data":'0'}
                        else:
                            return {"data":'1'}'''
                    
                    #devo verificare se la posizione inserita sia coerente con gli id scritti
                    #nelle regole della geometria del singolo container
                    regole=json.loads(r.idGeometry.rules)
                    trovato=0
                    for reg in regole['items']:
                        if reg['id']==pos:
                            trovato=1
                            print 'id',reg['id']
                            break
                    if trovato==0:
                        return {"data":'err_posizione'}
                    
                    cont=Container.objects.filter(Q(idFatherContainer=r)&Q(position=pos))
                    print 'len',len(cont)
                    if len(cont)==0:
                        return {"data":'1'}
                    else:
                        return {"data":'0'}
            else:
                #sto inserendo una singola provetta. Devo vedere se la piastra esiste
                #e se c'e' posto dentro
                pias=Container.objects.filter(barcode=plate)
                if len(pias)==0:
                    return {"data":'inesist'}
                else:
                    pias=Container.objects.get(barcode=plate)
                    #devo vedere se la piastra o cassetto selezionato puo' contenere
                    #quella tipologia di container
                    tip=ContainerType.objects.get(id=tipo_cont)
                    print 'tip',tip
                    #vedo quali container possono contenere il tipo scelto
                    listatipi=ContTypeHasContType.objects.filter(idContained=tip)
                    print 'lista',listatipi
                    trov=0
                    for tipi in listatipi:
                        if tipi.idContainer.id==pias.idContainerType.id:
                            trov=1
                            print 'tipi',tipi.idContainer
                            break
                    if trov==0:
                        return {"data":'err_tipo_cont'}
                    print 'pos',pos
                    vv=pos.split('&')
                    pos=vv[0]
                    #devo verificare se la posizione inserita sia coerente con gli id scritti
                    #nelle regole della geometria del singolo container           
                    regole=json.loads(pias.idGeometry.rules)
                    trovato=0
                    for reg in regole['items']:
                        if reg['id']==pos:
                            trovato=1
                            print 'id',reg['id']
                            break
                    if trovato==0:
                        return {"data":'err_posizione'}
                    #se sto creando una biocas, ho la pos seguita da '&BIOC', quindi dividendo in 
                    #base alla '&' se la lunghezza e' 2 allora non devo controllare oltre
                    
                    if len(vv)==1:
                        #questo solo se sto inserendo una provetta in una piastra. Non ha 
                        #senso se sto creando una biocassetta, che ha una posizione, ma non ci sono
                        #limiti di spazio per un singolo posto
                        cont=Container.objects.filter(Q(idFatherContainer=pias)&Q(position=pos))
                        print 'len',len(cont)
                        if len(cont)==0:
                            return {"data":'1'}
                        else:
                            return {"data":'0'}
                    else:
                        return {"data":'1'}
                
        except Exception,e:
            print 'err',e
            return {"data":'errore'}
        
'''#per il modulo delle linee cellulari. Per caricare una piastra o una singola provetta
#con il loro contenuto
class LoadCellHandler(BaseHandler):
    allowed_methods = ('GET')
    model = Container
    @method_decorator(get_functionality_decorator)
    def read(self, request,barcode):
        children = []
        try:
            print 'barc',barcode
            string = ''
            cont=Container.objects.filter(barcode=barcode)
            if len(cont)==0:
                return {'data': 'err_nonesist'}
            else:
                container=cont[0]
                
                tipogen=container.idContainerType.idGenericContainerType.abbreviation
                if tipogen!='plate' and tipogen!='tube':
                    return {'data': 'err_tipo'}
                 
                tipoaliqgen=Feature.objects.get(name='AliquotType')
                tipoaliq=ContainerFeature.objects.filter(Q(idFeature=tipoaliqgen)&Q(idContainer=container))
                #se e' una provetta
                if len(tipoaliq)==0:
                    typeP='VT'
                    barcode=barcode.replace('#','%23')
                    #A1 e l'1|1 finale indicano la posizione dell'aliquota all'interno della provetta
                    stringa=barcode+'&A1&1|1'
                    address = Urls.objects.get(default = '1').url
                    req = urllib2.Request(address+"/api/load/tubes/"+stringa+"/"+typeP, headers={"workingGroups" : get_WG_string()})
                    u = urllib2.urlopen(req)
                    #u = urllib2.urlopen(address+"/api/load/tubes/"+stringa+"/"+typeP+ "?workingGroups="+get_WG_string())
                    response= u.read()
                #se e' una piastra
                else:
                    typeP=tipoaliq[0].value
                    contentList = Container.objects.filter(idFatherContainer = container)
                    select = ['idContainerType', 'position', 'barcode', 'availability', 'full']
                    for c in contentList:
                        children.append(Simple(c,select).getAttributes())
                    dict={'typeC':container.idContainerType.name,'children':children,'rules': json.loads(container.idGeometry.rules)}
                    response, dim,err,diztipi = CreaTabella(dict,typeP)
                    if err=='errore':
                        return {'data':'errore_banca'}
                print 'response',response
                res = json.loads(response)
                if res['data']=='errore':
                    return {'data': 'errore'}
                    
                abbr='r'
                long_name=container.idContainerType.name
                name = 'rna'
                regole_geom=json.loads(container.idGeometry.rules)
                dim = regole_geom['dimension']
                #dimensioni della piastra
                x = int(dim[0])
                y = int(dim[1])
                print 'x',x
                print 'y',y
                row_label = regole_geom['row_label']
                column_label = regole_geom['column_label']
                          
                #inizializzo la tabella. Qui verra' scritto il codice HTML per creare le singole celle della tabella visualizzata dall'utente
                codeList = []
                i = 0
                j = 0
                k=0
                valo=0
                while i < int(y):
                    codeList.append([])
                    j = 0
                    if int(y)>26:
                        valor=i%14
                        if valor==0:
                            valo=valo+1
                            k=0
                    while j < int(x):
                        #calcolo l'id del tasto
                        if int(y)<27:
                            id=abbr+'-'+chr(i+ord('A'))+str(j+1)
                        else:                           
                            id=abbr+'-'+chr(int(valo-1)+ord('A'))+chr(k+ord('A'))+str(j+1)
                        codeList[i].append('<td align="center"><button type="submit" align="center" disabled="disabled" id="'+id+'">X</button></td>')
                        j = j + 1
                    i = i + 1
                    k=k+1

                for r in res['data']:
                    if len(r.split(',')) > 3:
                        #se la provetta contiene un'aliquota
                        pieces = r.split(',')
                        barcode =  pieces[0]
                        id_position = pieces[1]
                        coordinates = pieces[2]
                        aliquot = pieces[3]
                        quantity = pieces[4]
                        tipoaliq = pieces[5]
                        c = coordinates.split('|')
                        x = c[0]
                        y = c[1]
                        if aliquot=='NOT AVAILABLE':
                            codeList[int(y)-1][int(x)-1] = '<td> <button type="submit" title="NOT AVAILABLE" align="center" id="'+ abbr + '-' + id_position + '" pos="'+ id_position + '" gen="'+aliquot+'"  barcode="'+ barcode+'" tipo="'+ tipoaliq+'" disabled="disabled">'+ quantity +'</button></td>'
                        else:
                            codeList[int(y)-1][int(x)-1] = '<td> <button type="submit" align="center" id="'+ abbr + '-' + id_position + '" sel="s" pos="'+ id_position + '" gen="'+aliquot+'"  barcode="'+ barcode+'" tipo="'+ tipoaliq+'" disabled="disabled">'+ quantity +'</button></td>'
                        
                    else:
                        #se la provetta e' vuota
                        pieces = r.split(',')
                        barcode =  pieces[0]
                        id_position = pieces[1]
                        coordinates = pieces[2]
                        c = coordinates.split('|')
                        x = c[0]
                        y = c[1]
                        codeList[int(y)-1][int(x)-1] = '<td><button type="submit" align="center" id="'+ abbr + '-' + id_position + '" " barcode="'+ barcode+'" pos="'+ id_position + '" gen="'+barcode+'" disabled="disabled"  >0</button></td>'
                
                #creo il codice per la tabella HTML
                #lun e' il numero di colonne che l'intestazione della tabella deve coprire
                lun=int(dim[0])+1
                string += '<table align="center" id="' + str(name) + '"><tbody><tr><th colspan="' + str(lun) + '">' + str(long_name) + '</th></tr>'
                string += '<tr>'
                string += '<td class="intest"></td>'
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
                return {'data':string}

        except Exception,e:
            print 'err',e
            return {'data':'errore'}'''

#mi restituisce la lista dei tipi di container legati al tipo piastra
class InfoContTypeHandler(BaseHandler):
    allowed_methods = ('GET')
    @method_decorator(get_functionality_decorator)
    def read(self, request):
        try:
            lista=[]
            tipopias=GenericContainerType.objects.get(abbreviation='plate')
            listaconttipi=ContainerType.objects.filter(idGenericContainerType=tipopias)
            for tipi in listaconttipi:
                if tipi not in lista:
                    #restituisco actualName che e' quello che vede l'utente.
                    #Invece name e' per scopi interni al codice
                    lista.append(tipi.actualName)
            return lista
        except:
            return {"data":'errore'}
        
#mi restituisce la lista di tutte le geometrie presenti
class InfoGeometryHandler(BaseHandler):
    allowed_methods = ('GET')
    @method_decorator(get_functionality_decorator)
    def read(self, request):
        try:
            lista=[]           
            lisgeom=Geometry.objects.all()
            for geom in lisgeom:
                diz={}
                diz['name']=geom.name
                #diz['rules']=geom.rules
                diz['id']=geom.id
                lista.append(diz)
            return {'data':lista}
        except Exception, e:
            print 'err',e
            return {"data":'errore'}
        
#per creare nuove geometrie
class GeometryCreateHandler(BaseHandler):
    allowed_methods = ('GET')
    @method_decorator(get_functionality_decorator)
    def read(self, request,idgeom):
        try:
            string=''
            geom=Geometry.objects.get(id=idgeom)
            regole=json.loads(geom.rules)
            print 'reg',regole
            #inizializzo la tabella. Qui verra' scritto il codice HTML per creare le singole celle della tabella visualizzata dall'utente
            codeList = []
            i = 0
            j = 0
            dimension = regole['dimension']
            righe=regole['row_label']
            colonne=regole['column_label']
            print 'dimension',dimension
            x=dimension[0]
            y=dimension[1]
            while i < int(y):
                codeList.append([])
                j = 0
                while j < int(x):
                    #calcolo l'id del tasto
                    idposto=str(righe[i])+str(colonne[j])
                    #print 'id',idposto
                    codeList[i].append('<td align="center"><button type="submit" class="cell" align="center" row="'+str(righe[i])+'" col="'+str(colonne[j])+'" id="'+idposto+'">0</button></td>')
                    j = j + 1
                i = i + 1
                
            #lun e' il numero di colonne che l'intestazione della tabella deve coprire
            lun=int(x)+1
            string += '<table align="center"><tbody>'
            #    string += '<tr><th colspan="' + str(lun) + '"></th></tr>'
            string += '<tr>'
            string += '<td></td>'
            for c in colonne:
                string += '<td align="center" class="column" col="'+str(c)+'" ><strong>' + str(c) + '</strong></td>'
            string += '</tr>'
            i = 0
            for code in codeList:
                string += '<tr>'
                string += '<td align="center" class="row" row="'+str(righe[i])+'" ><strong>' + str(righe[i]) + '</strong></td>'
                for c in code:
                    if c != "":
                        string += c
                string += '</tr>'
                i = i +1
            string += '</tbody></table>'
            return {'data':string}
        except Exception, e:
            print 'err',e
            return {"data":'errore'}
        
#dato il tipo di aliquota restituisce tutti i container che possono contenere quel
#tipo e che non sono ancora stati posizionati         
class FreeContainerHandler(BaseHandler):
    allowed_methods = ('GET')
    @method_decorator(get_functionality_decorator)
    def read(self, request, tipo):
        try:
            diz={}
            listafin=[]
            lisal=[]
            #nom='Tube'
            #if tipo=='FF' or tipo=='OF' or tipo=='CH':
            #    nom=tipo
            gentipo=GenericContainerType.objects.get(abbreviation='tube')
            tipocont=ContainerType.objects.filter(idGenericContainerType=gentipo)
            
            listacont=Container.objects.filter(idContainerType__in=tipocont,idFatherContainer=None,present=1)
            
            print 'lung',len(listacont)
            feat=Feature.objects.get(name='AliquotType')
            listatip=ContainerFeature.objects.filter(idFeature=feat,idContainer__in=listacont,value=tipo)
            print 'listatip',listatip
            for c in listatip:
                listafin.append(c.idContainer.id)
            print 'listafin',listafin
            lisaliqtot=Aliquot.objects.filter(idContainer__in=listafin,endTimestamp=None)
            print 'lisaliq',lisaliqtot
                
            '''for con in listacont:
                #devo vedere se il cont ha come aliquottype quello passato alla API
                listatip=ContainerFeature.objects.filter(idFeature=feat,idContainer__in=listacont,value=tipo)
                if len(listatip)!=0:
                    lista1.append(Q(**{'id': con.id} ))
            if len(lista1)!=0:
                listafin=listacont.filter(reduce(operator.or_, lista1))
            else:
                #se non c'e' nessuna provetta di quel tipo, restituisco la lista vuota
                listafin=[]'''
            for al in lisaliqtot:
                lisal.append(al.genealogyID)
            indir=Urls.objects.get(default=1).url
            print 'indir',indir
            url=indir+'/api/infoaliq/'
            values = {'lisgen' : lisal}
            data = urllib.urlencode(values)
            req = urllib2.Request(url,data=data, headers={"workingGroups" : get_WG_string()})
            u = urllib2.urlopen(req)
            resp=json.loads(u.read())
            diz=json.loads(resp['data'])
            print 'diz',diz
            #devo aggiungere l'informazione del barcode
            for al in lisaliqtot:
                #nel diz potrebbero non esserci tutte le aliquote perche' alcune potrebbero appartenere
                #a wg diversi
                if al.genealogyID in diz: 
                    diztemp=diz[al.genealogyID]
                    #verifico che il tipo aliq sia coerente con quello scelto dall'utente nella schermata.
                    #Ho gia' filtrato prima in base al tipo di aliq, ma era solo in base alle informazioni presenti nello storage. Quindi se una provetta
                    #puo' contenere tutto, me la ritroverei sempre nella lista anche se filtro in base ad un certo tipo di aliq 
                    tipoaliq=diztemp['tipoaliq']
                    if tipoaliq==tipo:
                        diztemp['barcode']=al.idContainer.barcode
                        diz[al.genealogyID]=diztemp
                    else:
                        del diz[al.genealogyID]
            print 'dizdopo',diz
            return {'data':diz}
            
        except Exception,e:
            print 'err',e
            return {'data':'errore'}
        
'''#Serve per caricare dalla biobanca i gen delle aliquote da riposizionare
class ReturnHandler(BaseHandler):
    allowed_methods = ('GET')
    @method_decorator(get_functionality_decorator)
    def read(self, request, listabarc):
        try:
            print 'listabarc',listabarc
            listabarc=listabarc.replace('#','%23')
            indir=Urls.objects.get(default=1).url
            req = urllib2.Request(indir+"/api/tubes/"+listabarc, headers={"workingGroups" : get_WG_string()})
            u = urllib2.urlopen(req)
            data = json.loads(u.read())
            print 'data',data
            return data
            
        except Exception,e:
            print 'err',e
            return {"data":'errore'}'''
        
#Data una lista di barc mi restituisce un dizionario in cui la chiave e' un container e il valore e' la lista delle provette 
#contenute all'interno. Serve nel caso in cui si vuole pianificare un'operazione su tutta una piastra. In questo
#caso vengono restituiti tutti i campioni presenti all'interno
class ListaContHandler(BaseHandler):
    allowed_methods = ('GET')
    @method_decorator(get_functionality_decorator)
    def read(self, request, listabarc):
        try:
            diz={}
            print 'listabarc',listabarc
            parti=listabarc.split('&')
            for cont in parti:
                listainiz=[]
                lista=[]
                listemp=[]
                container=Container.objects.filter(barcode=cont)
                if len(container)!=0:
                    listainiz.append(container[0])
                    lis2=visit_children(listainiz, lista)
                    print 'lis2',lis2
                    for c in lis2:
                        lisaliq=Aliquot.objects.filter(idContainer=c,endTimestamp=None)
                        for al in lisaliq:
                            barc=al.idContainer.barcode                     
                            val=al.genealogyID+'|'+barc+'|'+al.position
                            listemp.append(val)
                    #se diztemp e' vuoto puo' darsi che il container inserito dall'utente sia una piastra con i pozzetti 
                    #che quindi non ha figli. Devo guardare nella tabella Aliquot se e' presente il container stesso e non i suoi figli
                    print 'listemp1',listemp
                    if len(listemp)==0:
                        print 'container',container
                        listaliq=Aliquot.objects.filter(idContainer=container,endTimestamp=None).order_by('position')
                        print 'listaaliq',listaliq
                        for al in listaliq:
                            barc=al.idContainer.barcode
                        
                            val=al.genealogyID+'|'+barc+'|'+al.position
                            listemp.append(val)
                    diz[cont]=listemp
                    print 'listemp',listemp
                #vuol dire che quello che ho passato non e' un barcode di container,
                #ma un genid
                else:
                    lisaliq=Aliquot.objects.filter(genealogyID=cont,endTimestamp=None)
                    if len(lisaliq)!=0:
                        al=lisaliq[0]
                        if al.idContainer!=None:
                            barc=al.idContainer.barcode
                        
                            val=al.genealogyID+'|'+barc+'|'+al.position
                            listemp.append(val)
                            diz[cont]=listemp
                        else:                        
                            diz[cont]=[]
                    else:
                        #se non e' neanche un genid, allora restituisco il dizionario con una lista vuota
                        diz[cont]=[]              
                
            return {'data':diz}
        except Exception,e:
            print 'err',e
            return {"data":'errore'}
        
#serve per verificare che siano presenti tutti i campioni di un determinato container
class CheckListaContainerHandler(BaseHandler):
    allowed_methods = ('POST')
    @method_decorator(get_functionality_decorator)
    def create(self, request):
        try:
            listafinale=[]
            listabarc=request.POST.get('lbarc')
            print 'listabarc',listabarc
            #e' la lista con tutti i codici delle provette
            parti=listabarc.split('&')
        
            liscont=Container.objects.filter(barcode__in=parti)
            
            listapadri=visit_father(parti,liscont,[],0)
            print 'listapadri',listapadri
            for c in listapadri:
                listafinale.append(c.barcode)
            print 'listafinale',listafinale
            return listafinale
        except Exception,e:
            print 'err',e
            return {"data":'errore'}
        
#per cancellare il container padre da ogni container della lista di gen passati attraverso la POST
class CancFatherHandler(BaseHandler):
    allowed_methods = ('POST')
    @method_decorator(get_functionality_decorator)
    def create(self, request):
        try:
            print request.POST
            dizgen=json.loads(request.POST.get('dizgen'))
            print 'dizgen',dizgen
            lisaliq=Aliquot.objects.filter(genealogyID__in=dizgen.keys(),endTimestamp=None)
            print 'lisaliq',lisaliq
            if 'containermove' in request.POST:
                contmove=request.POST.get('containermove')
            else:
                contmove='tube'
            #prendo la feature aliquottype
            feataliq=Feature.objects.get(name='AliquotType')
            for al in lisaliq:
                c=al.idContainer
                if c.idContainerType.idGenericContainerType.abbreviation=='tube':
                    if contmove=='plate' and c.idFatherContainer!=None:
                        c=c.idFatherContainer
                        if contmove=='rack' and c.idFatherContainer!=None:
                            c=c.idFatherContainer
                elif c.idContainerType.idGenericContainerType.abbreviation=='plate':
                    #se sono gia' al livello piastra e voglio spostare il rack in toto salgo di un livello se posso
                    if contmove=='rack' and c.idFatherContainer!=None:
                        c=c.idFatherContainer
                padre=None
                pos=None
                #se nella post c'e' save, allora devo salvare il padre e la posizione e non cancellarla
                #Serve per quei container trasferiti erroneamente
                if 'save' in request.POST:
                    #prendo tutte le righe dell'audit che riguardano quel cont ordinandole in base alla data
                    lisaudit=ContainerAudit.objects.filter(id=c.id).order_by('-_audit_timestamp')
                    print 'lisaudit',lisaudit
                    for caudit in lisaudit:
                        #devo andare a prendere il primo idFatherContainer che non sia None
                        if caudit.idFatherContainer is not None:
                            padre=caudit.idFatherContainer
                            pos=caudit.position
                            break
                else:                    
                    #devo collegare al container il tipo di aliquota contenuta se non e' gia' presente questa informazione
                    #questo solo se e' una provetta e non una piastra o altro
                    if dizgen[al.genealogyID]!=None:
                        tipoaliq=dizgen[al.genealogyID]
                        contfeat,creato=ContainerFeature.objects.get_or_create(idFeature=feataliq,
                                              idContainer=c,
                                              value=tipoaliq)
                        print 'contfeat',contfeat,'creato',creato
                c.idFatherContainer=padre
                c.position=pos
                c.save()
            return {"data":'ok'}
        except:
            return {"data":'errore'}
        
#dato il tipo generico di container, mi da' i tipi di container che ne fanno parte     
class GenericTypeHandler(BaseHandler):
    allowed_methods = ('GET')
    @method_decorator(get_functionality_decorator)
    def read(self, request, tipo):
        try:
            l=[]
            tipo_cont=GenericContainerType.objects.get(id=tipo)
            #vedo quali sono i tipi di container collegati a quel tipo generico
            liscont=ContainerType.objects.filter(idGenericContainerType=tipo_cont)
            select=['id','actualName','idGeometry','oneUse']
            for conttipo in liscont:
                diz=Simple(conttipo,select).getAttributes()
                l.append(diz)
            return {"data":l}
        except Exception,e:
            print 'err',e
            return {"data":'errore'}
        
#dato il padre mi da' tutte le posizioni libere al suo interno
class EmptyPositionsHandler(BaseHandler):
    allowed_methods = ('GET')
    @method_decorator(get_functionality_decorator)
    def read(self, request, cod, tipocont, tipoaliq):
        try:
            liscont=Container.objects.filter(barcode=cod)
            if len(liscont)==0:
                return {"data":'inesistente'}
            else:
                cont=liscont[0]
                conttipo=ContainerType.objects.get(id=tipocont)
                #vedo quali container puo' contenere il padre inserito
                listatipi=ContTypeHasContType.objects.filter(idContainer=cont.idContainerType)
                print 'lista',listatipi
                trov=0
                for tipi in listatipi:
                    if tipi.idContained!=None and tipi.idContained.id==conttipo.id:
                        trov=1
                        print 'tipi',tipi.idContained
                        break
                if trov==0:
                    return {"data":'err_tipo_cont'}
                
                listip=''
                for tt in listatipi:
                    if tt.idContained!=None:
                        listip+=str(tt.idContained.id)+'-'
                if len(listip)!=0:
                    listip=listip[:-1]
                #prendo la lista degli id dei tipi di aliquota
                feat=Feature.objects.get(name='AliquotType')
                liscontfeat=ContainerFeature.objects.filter(idFeature=feat,idContainer=cont)
                #se c'e' qualcosa nelle feature che riguarda quel container allora verifico la 
                #coerenza dei tipi di aliquota. Se non c'e' niente allora non controllo perche'
                #vuol dire che quel container puo' contenere qualsiasi tipo di aliquota
                if len(liscontfeat)!=0:  
                    l_aliq=tipoaliq.split('&')
                    lisvalori=DefaultValue.objects.filter(id__in=l_aliq)
                    for val in lisvalori:
                        trov=0
                        for feat in liscontfeat:  
                            if val.abbreviation==feat.value:
                                trov=1
                                break
                        if trov==0:
                            return {"data":'err_tipo_aliq'}
                    #creo la stringa con i tipi di aliq supportati
                    lisaliq=''
                    lisdefvalue=DefaultValue.objects.all().exclude(abbreviation=None)
                    for feat in liscontfeat:
                        for val in lisdefvalue:
                            if feat.value==val.abbreviation:
                                lisaliq+=str(val.id)+'-'
                                break
                else:
                    lisaliq='-'
                
                #chiamo la API che mi da' il codice html per disegnare la piastra
                hand=TableHandler()
                data=hand.read(request, cod, 'children', 'simple')
                print 'data',data['data']
                #return data
                #prendo i figli
                regole=json.loads(cont.idGeometry.rules)
                listafigli=Container.objects.filter(idFatherContainer=cont)
                listafin=[]
                posmax=cont.idContainerType.maxPosition
                if len(listafigli)==0:
                    for reg in regole['items']:
                        listafin.append(reg['id'])
                else:
                    #prendo le regole della geometria   
                    for reg in regole['items']:
                        pos=reg['id']
                        trovato=0
                        for figli in listafigli:
                            if figli.position==pos:
                                trovato+=1                            
                        if posmax==None or trovato<posmax:
                            listafin.append(reg['id'])
                    print 'pos',pos
                return {'data':data['data'],'listafin':listafin,'aliq':lisaliq[:-1],'cont':listip}
        except Exception,e:
            print 'err',e
            return {"data":'errore'}
        
#mi restituisce le info di un singolo container
class InfoContHandler(BaseHandler):
    allowed_methods = ('GET')
    @method_decorator(get_functionality_decorator)
    def read(self, request,barcode):
        try:
            cont=Container.objects.get(barcode=barcode)
            #devo vedere quali tipi di campioni possono entrare in quel container
            feat=Feature.objects.get(name='AliquotType')
            liscontfeat=ContainerFeature.objects.filter(idContainer=cont,idFeature=feat)
            if len(liscontfeat)==0:
                listipifin='All'
            else:
                listipi=''
                for contfeat in liscontfeat:
                    listipi+=contfeat.value+'-'
                listipifin=listipi[:-1]
                print 'listipifin',listipifin
            return {'tipo':cont.idContainerType.actualName,'geom':cont.idGeometry.name,'tipialiquote':listipifin}
        except:
            return {"data":'errore'}
        
#per controllare che ai container inseriti tramite file vengano assegnate informazioni corrette
#e coerenti con gli altri container
class ValidateContHandler(BaseHandler):
    allowed_methods = ('POST')
    @method_decorator(get_functionality_decorator)
    def create(self, request):
        try:
            print request.POST
            
            if request.session.has_key('dizgenbarcode'):
                dizgenerale=request.session.get('dizgenbarcode')
                print 'dizgenerale',dizgenerale
            else:
                dizgenerale={}
            
            geom=request.POST.get('geom')
            geo=geom.split('x')
            #geo[0] contiene le righe, geo[1] contiene le colonne
            regolegeometria=json.loads(creaGeometria(geo[0], geo[1]))
            
            tipo=request.POST.get('tipo')
            conttip=ContainerType.objects.get(id=tipo)
            if conttip.maxPosition!=None:
                numfigliteor=int(geo[0])*int(geo[1])*int(conttip.maxPosition)
                       
            aliq=str(request.POST.get('aliq'))
            dizbarc=json.loads(request.POST.get('dizbarc'))
            for k,v in dizbarc.items():
                val=v.split('|')
                padre=val[0]
                position=val[1]
                #per ogni barc nuovo verifico che suo padre possa contenerlo
                if padre in dizgenerale.keys():
                    print 'k',k
                    #faccio un controllo sul tipo di container
                    tipopadre=dizgenerale[padre]['tipo']
                    tipofiglio=tipo
                    if not (ControllaTipo(tipopadre, tipofiglio)):
                        return{'data':'Error: '+padre+' can\'t contain '+k}
                        
                    #faccio un controllo sul tipo di aliquote contenute
                    aliqpadre=dizgenerale[padre]['aliq']
                    aliqfiglio=aliq
                    if not ControllaAliquota(aliqpadre, aliqfiglio):
                        return{'data':'Error: some biological contents of '+k+' is not supported by '+padre}
                    
                    #controllo che il numero di figli contenuti sia coerente con la geometria del padre
                    geometria=dizgenerale[padre]['geom']
                    geo=geometria.split('x')
                    #geo[0] contiene le righe, geo[1] contiene le colonne
                    regolegeom=json.loads(creaGeometria(geo[0], geo[1]))
                    #devo prendere il numero massimo di posizioni del tipo di container
                    conttipo=ContainerType.objects.get(id=tipopadre)
                    #se non sto reinserendo lo stesso container
                    if conttipo.maxPosition!=None and not dizgenerale.has_key(k):
                        numfigliteorici=int(geo[0])*int(geo[1])*int(conttipo.maxPosition)
                        #prendo tutti i figli
                        contatore=0
                        dizposizioni={}
                        for chiave,val in dizgenerale.items():
                            #se qualche container ha come padre questo
                            if val['padre']==padre:
                                contatore+=1
                                posiz=val['pos']
                                #devo verificare che non ci siano posizioni duplicate
                                if dizposizioni.has_key(posiz):
                                    contatore=dizposizioni[posiz]
                                    contatore+=1
                                    dizposizioni[posiz]=contatore
                                else:
                                    dizposizioni[posiz]=1
                        print 'dizposizioni',dizposizioni
                        for ch,valore in dizposizioni.items():
                            if valore>conttipo.maxPosition:
                                return{'data':'Error: position '+ch+' is duplicate in container '+padre}
                        print 'contatore',contatore
                        print 'numteorico',numfigliteorici        
                        if contatore>=numfigliteorici:
                            return{'data':'Error: geometry of '+padre+' is not consistent with number of children you inserted'}
                    
                    #controllo che i figli siano in posizioni coerenti con la geometria del padre
                    if not ControllaPosizioni(regolegeom, position):
                        return{'data':'Error: position '+position+' is inconsistent with geometry of container '+padre}
                        
                #se non c'e' il padre devo vedere se ci sono i figli
                else:
                    cont=0
                    dizpos={}
                    for chiave,val in dizgenerale.items():
                        #se qualche container ha come padre questo                     
                        if val['padre']==k:
                            #print 'figlio',chiave
                            
                            #faccio un controllo sul tipo di container
                            tipofiglio=val['tipo']
                            tipopadre=tipo
                            if not (ControllaTipo(tipopadre, tipofiglio)):
                                return{'data':'Error: '+k+' can\'t contain '+chiave}
                            
                            #faccio un controllo sul tipo di aliquote contenute
                            aliqfiglio=val['aliq']
                            aliqpadre=aliq
                            if not ControllaAliquota(aliqpadre, aliqfiglio):
                                return{'data':'Error: some biological contents of '+k+' is not supported by '+chiave}
                            
                            cont+=1
                            posiz=val['pos']
                            #devo verificare che non ci siano posizioni duplicate
                            if dizpos.has_key(posiz):
                                contatore=dizpos[posiz]
                                contatore+=1
                                dizpos[posiz]=contatore
                            else:
                                dizpos[posiz]=1
                            #devo vedere se la posizione gia' assegnata al figlio e' coerente con la geometria del 
                            #padre che sto inserendo
                            if not ControllaPosizioni(regolegeometria, posiz):
                                return{'data':'Error: position '+val['pos']+' of container '+chiave+' is inconsistent with geometry of container '+k}
                    
                    if conttip.maxPosition!=None:
                        for ch,valore in dizpos.items():
                            if valore>conttip.maxPosition:
                                return{'data':'Error: position '+ch+' is duplicate in container '+k}
                        print 'contatore',cont
                        print 'numteorico',numfigliteor              
                        #controllo che il numero di figli contenuti sia coerente con la geometria del padre
                        if cont>numfigliteor:
                            return{'data':'Error: geometry of '+k+' is not consistent with number of its children'}
                            
                diztemp={}
                diztemp['padre']=padre
                diztemp['pos']=position
                diztemp['geom']=geom
                diztemp['tipo']=tipo
                diztemp['aliq']=aliq
                dizgenerale[k]=diztemp
            print 'dizgenerale',dizgenerale
            request.session['dizgenbarcode']=dizgenerale
            return {'data':'ok'}
        except Exception, e:
            print 'ecc',e
            return {'data':'errore'}

#per verificare se la lista di barc passati esiste gia' nel DB dello storage.
#E' usata anche per fare tutti i controlli nel batch degli espianti
class CheckPresenceHandler(BaseHandler):
    allowed_methods = ('POST')
    @method_decorator(get_functionality_decorator)
    def create(self, request):
        print request.POST
        try:
            lisbarc = json.loads(request.POST.get('lista'))
            print 'lisbar',lisbarc      
            if 'salva' in request.POST:
                #Viene fatto il controllo sul LASHub
                presente=Barcode_unico(lisbarc, request)
                if presente:
                    return {'data' : 'err'}
                else:
                    return {'data' : 'ok'}
            elif 'posiziona' in request.POST:
                #per posizionare le provette nella piastra.
                #lisbarc in realta' contiene un dizionario con chiave il barc della provetta
                #e valore piastra|posizione|tipoaliq
                for key,val in lisbarc.items():
                    cont=Container.objects.get(barcode=key)
                    vv=val.split('|')
                    piastra=Container.objects.filter(barcode=vv[0])
                    #faccio il controllo se esiste la piastra perche' potrebbero arrivare codici
                    #inesistenti dalla schermata del collezionamento batch da file
                    if len(piastra)!=0:
                        cont.idFatherContainer=piastra[0]
                        cont.position=vv[1]
                        cont.save()
                return {'data' : 'ok'}
            else:
                #Non viene fatto il controllo sul LASHub
                liscont=Container.objects.filter(barcode__in=lisbarc)
                print 'liscont',liscont
                if len(liscont)!=0:
                    return {'data' : 'Error: barcode '+str(liscont[0].barcode)+' already exists'}
                #devo fare il controllo se le posizioni sono libere e coerenti e se la piastra e' del tipo giusto
                dizprov=json.loads(request.POST.get('dizprov'))
                print 'diz',dizprov
                #lista in cui salvare le piastre che trovo all'interno del diz, cosi' da non accedere sempre al DB
                #per verificare la presenza delle piastre
                dizpresenti={}
                lispiasassenti=[]
                feat=Feature.objects.get(name='AliquotType')
                #key e' il barc della provetta, val e' piastra|posizione|tipoaliq
                for key,val in dizprov.items():
                    vv=val.split('|')
                    piastra=vv[0]
                    if not dizpresenti.has_key(piastra) and piastra not in lispiasassenti:
                        lpias=Container.objects.filter(barcode=piastra)
                        if len(lpias)!=0:
                            #devo vedere se e' una piastra
                            if lpias[0].idContainerType.idGenericContainerType.abbreviation=='plate' or 'explants' in request.POST:
                                #prendo le aliq che puo' contenere la piastra
                                lfeat=ContainerFeature.objects.filter(idFeature=feat,idContainer=lpias[0])
                                tipi=''
                                for f in lfeat:
                                    tipi+=f.value+'&'
                                tipfin=tipi[:len(tipi)-1]
                                print 'tipfin',tipfin
                                #prendo le posizioni gia' occupate di quella piastra
                                lfigli=Container.objects.filter(idFatherContainer=lpias[0])
                                strposiz=''
                                for figli in lfigli:
                                    strposiz+=figli.position+'&'
                                posizfin=strposiz[:len(strposiz)-1]
                                print 'posizfin',posizfin
                                dizpresenti[piastra]=tipfin+'|'+posizfin+'|'+lpias[0].idGeometry.rules
                            else:
                                return {'data' : 'Error: barcode '+str(lpias[0].barcode)+' is not a plate'}
                        else:
                            lispiasassenti.append(piastra)
                    print 'dizpresenti',dizpresenti
                    if dizpresenti.has_key(piastra):
                        #prendo l'oggetto container
                        valori=dizpresenti[piastra].split('|')
                        print 'valori',valori
                        #guardo se quella piastra puo' contenere quei tipi di aliq
                        if not ControllaAliquota(valori[0], vv[2]):
                            return{'data':'Error: plate '+piastra+' cannot contain '+vv[2]}
                        #guardo se la geometria e' coerente con la posizione
                        regolegeometria=json.loads(valori[2])
                        if not ControllaPosizioni(regolegeometria, vv[1]):
                            return{'data':'Error: position '+vv[1]+' is inconsistent with geometry of container '+piastra}
                        
                        if not 'explants' in request.POST:
                            #guardo se quel posto nella piastra e' vuoto
                            lposiz=valori[1].split('&')
                            lfiglio=[]
                            lfiglio.append(vv[1])
                            #se la posiz nuova c'e' nel set dei figli allora non va bene
                            print 'vv[1]',vv[1]
                            if set(lfiglio).issubset(set(lposiz)):
                                return{'data':'Error: position '+vv[1]+' is already occupied in container '+piastra}
                    #se sto controllando per gli espianti, devo vedere se quella provetta ha gia' tutte le proprie posizioni occupate
                    #da decommentare poi
                    if 'explants' in request.POST:
                        #se sto trattando una piastra costar, in key avro' piastra|pos
                        lcont=Container.objects.filter(barcode=key,present=1)
                        print 'lcont',lcont
                        if len(lcont)==0:
                            kk=key.split('|')
                            lcont=Container.objects.filter(barcode=kk[0],present=1)
                            print 'ccc',lcont
                            lisaliq=Aliquot.objects.filter(idContainer=lcont[0],position=kk[1],endTimestamp=None)
                        else:
                            lisaliq=Aliquot.objects.filter(idContainer=lcont[0],endTimestamp=None)
                        print 'lisaliq',lisaliq
                        posmaxcont=lcont[0].idContainerType.maxPosition
                        #posmaxcont e' coerente con quello che sto trattando: una costar o una provetta singola, 
                        print 'posmaxcont',posmaxcont
                        if posmaxcont!=None:
                            if len(lisaliq)>=int(posmaxcont):
                                return{'data':'Error: position '+vv[1]+' in container '+piastra+' is full'}
                return {'data' : 'ok','piastre':json.dumps(lispiasassenti)}
        except Exception, e:
            print 'ecc',e
            return {'data':'error'}

#serve per cambiare il barcode dei campioni. Viene chiamata dalla biobanca nella schermata del posizionamento
#delle aliq vitali sulla piastra operativa
class ChangeBarcodeHandler(BaseHandler):
    allowed_methods = ('POST')
    @transaction.commit_on_success
    @method_decorator(get_functionality_decorator)
    def create(self, request):
        try:
            name=''
            if 'user' in request.POST:
                name=request.POST.get('user')
            lutente=User.objects.filter(username=name)
            utente=None
            if len(lutente)!=0:
                utente=lutente[0]
            print 'utente',utente
            diz=json.loads(request.POST.get('diz'))
            print 'diz',diz
            #dizionario per salvare le informazioni da far ritornare alla biobanca per creare il report
            #la chiave e' il gen e poi c'e' barcvecchio|posvecchia|barcnuovo
            dizinfo={}
            for key,value in diz.items():
                #in key ho il genealogy, in val ho pos%piastra
                stringa=value.split('%')
                #in stringa[0] ho la nuova posizione, in stringa[1] la piastra
                aliq=Aliquot.objects.get(genealogyID=key,endTimestamp=None)
                print 'aliq',aliq
                #devo chiudere questa relazione perche' il campione ha cambiato posizione
                #aliq.endTimestamp=datetime.datetime.now()
                aliq.endTimestamp=timezone.localtime(timezone.now())
                aliq.endOperator=utente
                aliq.save()
                #svuoto il container sorgente solo se era una provetta
                if aliq.position=='':
                    provetta=aliq.idContainer
                    #Solo se il cont e' monouso
                    #guardo quanti figli ha
                    liscontfigli=Container.objects.filter(idFatherContainer=provetta)
                    lisaliqfigli=Aliquot.objects.filter(idContainer=provetta,endTimestamp=None)
                    if len(liscontfigli)==0 and len(lisaliqfigli)==0:
                        if provetta.oneUse:
                            provetta.idFatherContainer=None
                            provetta.availability=1
                            provetta.full=0
                            provetta.present=0
                            provetta.owner=''
                            print 'provetta dopo',provetta
                            provetta.save()
                #ne creo una nuova
                #devo vedere se e' una piastra con i pozzetti o no
                pias=Container.objects.get(barcode=stringa[1])
                if pias.idContainerType.idGenericContainerType.abbreviation=='plate':
                    piascostar=False
                    #guardo se e' una piastra con i pozzetti
                    gentipo=ContTypeHasContType.objects.filter(idContainer=pias.idContainerType)
                    for tip in gentipo:
                        if tip.idContained==None:
                            piascostar=True                
                    print 'costar',piascostar
                    if piascostar:
                        pos=stringa[0]
                        cont=pias
                    else:
                        #prendo tutti i figli della piastra
                        lfigli=Container.objects.filter(idFatherContainer=pias,present=1)
                        print 'lfigli',lfigli
                        for figlio in lfigli:                            
                            if figlio.position==stringa[0]:
                                print 'pos',figlio.position
                                cont=figlio
                                cont.full=1
                                cont.save()
                        pos=''
                elif pias.idContainerType.idGenericContainerType.abbreviation=='tube':
                    pos=stringa[0]
                    cont=pias
                #creo l'aliq
                #la data iniziale e' giusto che sia oggi perche' nella schermata del posizionamento
                #non si puo' impostare la data
                a=Aliquot(genealogyID=key,
                          idContainer=cont,
                          position=pos,
                          #startTimestamp=datetime.datetime.now(),
                          startTimestamp=timezone.localtime(timezone.now()),
                          startOperator=utente
                          )
                a.save()
                print 'a',a
                dizinfo[key]=aliq.idContainer.barcode+'|'+aliq.position+'|'+cont.barcode
            #devo ritornare i dati alla biobanca per fare il report finale
            return {'data':json.dumps(dizinfo)}
        except Exception,e:            
            print 'err',e
            transaction.rollback()
            return {'data':'errore'}

#mi restituisce le info delle relazioni consentite tra tipi di container
class InfoRelationshipHandler(BaseHandler):
    allowed_methods = ('GET')
    @method_decorator(get_functionality_decorator)
    def read(self, request):
        try:
            lisfin=[]
            lrelazioni=ContTypeHasContType.objects.all()
            for rel in lrelazioni:
                if rel.idContainer!=None:
                    diztemp={}
                    diztemp['padre']=rel.idContainer.id
                    if rel.idContained==None:
                        diztemp['figlio']=''
                    else:
                        diztemp['figlio']=rel.idContained.id
                    lisfin.append(diztemp)      
            return lisfin
        except Exception,e:
            print 'err',e
            return {"data":'errore'}
        
#dato un dizionario con dentro dei barc di provette o piastre, restituisce il gen e il num pezzi
class InfoAliquotHandler(BaseHandler):
    allowed_methods = ('POST')
    @method_decorator(get_functionality_decorator)
    def create(self, request):
        try:
            print request.POST
            lisbarc=json.loads(request.POST.get('listBarcode'))
            print 'lisbarc',lisbarc
            dizaliqdef={}
            dizpias={}
            dizbarc={}
            for diz in lisbarc:
                barc=diz['barcode']
                pos=diz['pos']     
                print 'barc',barc
                
                #codice vecchio da commentare
                '''dizbarc[barc+'|'+pos]=pos
                if(pos!='-'):
                    bbb=barc+pos                    
                lcont=Container.objects.filter(barcode=bbb)
                if len(lcont)==0:
                    return json.dumps({'res':'err','data':{'barcode':barc+'|'+pos,'err':'notexists'}})'''
                
                             
                #non posso caricare tutti i cont insieme successivamente perche' devo segnalare se 
                #qualche cont non esiste 
                if barc in dizpias:
                    cont=dizpias[barc]
                else:
                    lcont=Container.objects.filter(barcode=barc)
                    if len(lcont)==0:
                        return json.dumps({'res':'err','data':{'barcode':barc+'|'+pos,'err':'notexists'}})
                    cont=lcont[0]
                    dizpias[barc]=lcont[0]
                #se pos='-', vuol dire che e' una provetta singola, altrimenti e' una piastra
                if pos=='-':
                    pos=''                      
                lisaliq=Aliquot.objects.filter(idContainer=cont,position=pos,endTimestamp=None)
                print 'lisaliq',lisaliq
                if len(lisaliq)==0:
                    return json.dumps({'res':'err','data':{'barcode':barc+'|'+pos,'err':'empty'}})
		if pos=='':
                    dizaliqdef[lisaliq[0].genealogyID]=barc
                else:
                    dizaliqdef[lisaliq[0].genealogyID]=barc+'|'+pos
                
            #codice vecchio da commentare
            '''address = Urls.objects.get(default = '1').url
            url=address+'/api/aliquotdata/'
            val={'dizbarc':dizbarc}
            data = urllib.urlencode(val)
            req = urllib2.Request(url,data=data, headers={"workingGroups" : get_WG_string()})
            u = urllib2.urlopen(req)
            res =  json.loads(u.read())
            import ast
            dizaliqdef=ast.literal_eval(res['data'])
            if 'res' in dizaliqdef:
                if dizaliqdef['res']=='err':
                    return json.dumps({'res':'err','data':{'barcode':dizaliqdef['data']['barcode'],'err':'empty'}})'''
            
            
            print 'dizaliqdef',dizaliqdef
            #chiamo la API per avere le informazioni di ogni singola aliquota
            lisgen=''
            lis_pezzi_url=[]
            for aliq in dizaliqdef.keys():
                lisgen+=aliq+'&'
                #2000 e' il numero di caratteri scelto per fare in modo che la url
                #della api non sia troppo lunga
                if len(lisgen)>2000:
                    #cancello la virgola alla fine della stringa
                    strbarc=lisgen[:-1]
                    print 'strbarc',strbarc
                    lis_pezzi_url.append(strbarc)
                    lisgen=''
            #cancello la virgola alla fine della stringa
            strbarc=lisgen[:-1]
            print 'strbarc',strbarc
            if strbarc!='':
                lis_pezzi_url.append(strbarc)
            
            diz_tot={}
            if len(lis_pezzi_url)!=0:
                indir=Urls.objects.get(default=1).url
                for elementi in lis_pezzi_url:
                    req = urllib2.Request(indir+"/api/feature/"+elementi, headers={"workingGroups" : get_WG_string()})
                    u = urllib2.urlopen(req)
                    data = json.loads(u.read())
                    print 'data',data
                    for al in data['data']:
                        print 'al',al
                        gen=al['aliquot']
                        if al['type']!='VT':
                            return json.dumps({'res':'err','data':{'barcode':dizaliqdef[gen],'err':'type'}})
                        lisfeat=al['feature']
                        print 'lisfeat',lisfeat
                        pezzi=0
                        for feat in lisfeat:
                            print 'feat',feat
                            print 'l',lisfeat[feat]
                            if feat=='NumberOfPieces':
                                pezzi=lisfeat[feat]
                        diztemp={}
                        diztemp['genID']=gen
                        diztemp['qty']=pezzi
                        diz_tot[dizaliqdef[gen]]=diztemp
            print 'diz_tot',diz_tot
            return json.dumps({'res':'ok','data':diz_tot})
        except Exception,e:
            print 'err',e
            return {'res':'err','data':'errore'}
        
#serve nella schermata di cambiamento delle caratteristiche di un container.
#Dati dei barcode separati da |, restituisce le loro caratteristiche
class GetInfoContainerHandler(BaseHandler):
    allowed_methods = ('GET')
    @method_decorator(get_functionality_decorator)
    def read(self, request,barcode):
        try:
            dizgen={}            
            lbarc=barcode.split('|')
            for barc in lbarc:
                dizdati={}
                listipi=[]
                lcont=Container.objects.filter(barcode=barc)
                if len(lcont)==0:
                    return {'data':'inesist'}
                cont=lcont[0]
                #devo verificare che il container sia vuoto prima di cambiare le sue caratteristiche
                liscontfigli=Container.objects.filter(idFatherContainer=cont)
                lisaliqfigli=Aliquot.objects.filter(idContainer=cont,endTimestamp=None)
                if len(liscontfigli)!=0 or len(lisaliqfigli)!=0:
                    return {'data':'pieno'}
                dizdati['generic']=cont.idContainerType.idGenericContainerType.id
                dizdati['type']=cont.idContainerType.id
                
                feataliq=Feature.objects.get(name='AliquotType')
                tipoaliq=ContainerFeature.objects.filter(idFeature=feataliq,idContainer=cont).order_by('id')
                defval=FeatureDefaultValue.objects.filter(idFeature=feataliq)
                #se il container non ha specificato delle aliquote che puo' contenere, allora le puo' contenere tutte
                if len(tipoaliq)!=0:
                    for tip in tipoaliq:
                        for val in defval:
                            if tip.value==val.idDefaultValue.abbreviation:
                                listipi.append(val.idDefaultValue.id)
                else:                
                    for val in defval:
                        listipi.append(val.idDefaultValue.id)
                print 'listipi',listipi
                dizdati['aliq']=listipi
                
                regole_geom=json.loads(cont.idGeometry.rules)
                dim = regole_geom['dimension']
                dizdati['row']=dim[1]
                dizdati['col']=dim[0]
                mono=False
                if cont.oneUse:
                    mono=True                
                dizdati['monouso']=mono
                print 'dizdati',dizdati
                #ho bisogno anche di sapere le aliq e i tipi di cont che puo' contenere il padre di questo cont
                laliqpadre=[]
                lconttipipadre=[]
                if cont.idFatherContainer!=None:
                    contpadre=cont.idFatherContainer
                    tipoaliq=ContainerFeature.objects.filter(idFeature=feataliq,idContainer=contpadre).order_by('id')
                    #se il container non ha specificato delle aliquote che puo' contenere, allora le puo' contenere tutte
                    if len(tipoaliq)!=0:
                        for tip in tipoaliq:
                            for val in defval:
                                if tip.value==val.idDefaultValue.abbreviation:
                                    laliqpadre.append(val.idDefaultValue.id)
                    else:                
                        for val in defval:
                            laliqpadre.append(val.idDefaultValue.id)
                    #devo capire quali tipi di cont puo' ospitare il padre
                    listatipi=ContTypeHasContType.objects.filter(idContainer=contpadre.idContainerType)
                    for tipi in listatipi:
                        if tipi.idContained!=None:
                            lconttipipadre.append(tipi.idContained.id)                    
                else:
                    #se non c'e' un padre allora metto tutte le aliquote cosi' da non imporre vincoli
                    for val in defval:
                        laliqpadre.append(val.idDefaultValue.id)
                    listatipi=ContainerType.objects.all()
                    for tipi in listatipi:
                        lconttipipadre.append(tipi.id)
                print 'ltipipadre',lconttipipadre
                print 'laliqpadre',laliqpadre
                dizdati['aliqpadre']=laliqpadre
                dizdati['tipipadre']=lconttipipadre
                
                dizgen[barc]=dizdati
            print 'dizgen',dizgen
            return {'data':'ok','diz':json.dumps(dizgen)}
        except:
            return {"data":'errore'}
        
#dato il nome di un cont type, mi restituisce le regole della geometria collegata.
#Serve nella biobanca per caricare un vetrino che non esiste
class ContainerTypeInfoHandler(BaseHandler):
    allowed_methods = ('GET')
    @method_decorator(get_functionality_decorator)
    def read(self, request,name,pezzi):
        try:
            lconttipo=ContainerType.objects.filter(name=name)
            if len(lconttipo)==0:
                return {'data':'tipo'}
            else:
                diz={}
                nomegeom=lconttipo[0].idGeometry.name
                reg=lconttipo[0].idGeometry.rules
                #pezzi e' il numero di sezioni che devono stare in un vetrino
                #dal cont type prendo la geometria impostata all'inizio e vedo se combacia. Se l'utente ha cambiato
                #il numero di pezzi nella schermata, allora creo una nuova geometria se non c'e'
                nn=nomegeom.split('x')
                if nn[1]!=int(pezzi):
                    geomnuova='1x'+str(pezzi)
                    lgeom=Geometry.objects.filter(name=geomnuova)
                    if len(lgeom)==0:
                        #creo una nuova geometria
                        stringa=creaGeometria('1', pezzi)
                        geometria=Geometry(name=geomnuova,
                                  rules=stringa)
                        geometria.save()
                    else:
                        geometria=lgeom[0]                        
                    print 'geom',geometria
                    nomegeom=geometria.name
                    reg=geometria.rules
                diz['regole']=reg
                diz['nome']=nomegeom
                return {'data':diz}
        except Exception, e:
            print 'err',e
            return {'data':'errore'}
        
#per salvare le fette nuove sui vetrini
class SaveSlideHandler(BaseHandler):
    allowed_methods = ('POST')
    @transaction.commit_on_success
    @method_decorator(get_functionality_decorator)
    def create(self, request):
        try:
            print request.POST
            listaaliq=json.loads(request.POST.get('lista'))
            print 'listaaliq',listaaliq
            name=''
            if 'user' in request.POST:
                name=request.POST.get('user')
            lutente=User.objects.filter(username=name)
            utente=None
            if len(lutente)!=0:
                utente=lutente[0]
            print 'utente',utente
            feataliq=Feature.objects.get(name='AliquotType')
            for valori in listaaliq:
                val=valori.split(',')
                #val[0] e' il gen, poi barcode, abbreviazione tipo aliquota, data, tipo vetrino, geometria e posizione
                #vedo se il container esiste gia'
                lcont=Container.objects.filter(barcode=val[1])
                if len(lcont)==0:
                    #devo salvare il nuovo cont
                    tipocont=ContainerType.objects.get(name=val[4])
                    
                    lgeom=Geometry.objects.filter(name=val[5])
                    if len(lgeom)==0:
                        dimens=val[5].split('x')
                        #creo una nuova geometria
                        stringa=creaGeometria(dimens[0], dimens[1])                   
                        geometria=Geometry(name=val[5],
                                  rules=stringa)
                        geometria.save()
                    else:
                        geometria=lgeom[0]
                    
                    cc=Container(idContainerType=tipocont,
                                idGeometry=geometria,
                                barcode=val[1],
                                availability=1,
                                full=0,
                                oneUse=tipocont.oneUse)
                    cc.save()                                    
                else:
                    cc=lcont[0]
                
                contfeat,creato=ContainerFeature.objects.get_or_create(idFeature=feataliq,
                                              idContainer=cc,
                                              value=val[2])
                print 'contfeat',contfeat
                                        
                #devo salvare il campione che e' stato posizionato nel vetrino
                #oggi=datetime.datetime.now()
                oggi=timezone.localtime(timezone.now())
                datainiz=oggi
                
                data=val[3]
                dat=data.split('-')
                dtutente=timezone.datetime(int(dat[0]),int(dat[1]),int(dat[2]),1,0,0)
                print 'dtutente',dtutente
                #se la data impostata dall'utente e' quella di oggi allora lascio il .now()
                #altrimenti metto la data dell'utente impostata all'1 di notte per far capire che l'ora e' fittizia
                print 'mese utente',dtutente.month
                if dtutente.year!=oggi.year or dtutente.month!=oggi.month or dtutente.day!=oggi.day:
                    datainiz=dtutente
                
                #creo l'aliq
                a=Aliquot(genealogyID=str(val[0]),
                          idContainer=cc,
                          position=val[6],
                          startTimestamp=datainiz,
                          startOperator=utente
                          )
                a.save()
                
                regole_geom=json.loads(cc.idGeometry.rules)
                dim = regole_geom['dimension']
                x = int(dim[1])
                y = int(dim[0])
                print 'x',x
                print 'y',y
                posmax=cc.idContainerType.maxPosition
                if posmax!=None:
                    dimensione=x*y*int(posmax)
                    print 'dimensione',dimensione
                    laliq=Aliquot.objects.filter(idContainer=cc,endTimestamp=None)
                    print 'laliq',laliq
                    if len(laliq)>=dimensione:
                        cc.full=1
                        print 'container pieno'
                        cc.save()                          
            return {"data":'ok'}
        except Exception,e:
            print 'err',e
            transaction.rollback()
            return {'data':'err'}

#per ripristinare i campioni passati attraverso una lista
class RestoreAliquotHandler(BaseHandler):
    allowed_methods = ('POST')
    @transaction.commit_on_success
    @method_decorator(get_functionality_decorator)
    def create(self, request):
        try:
            print request.POST
            listaaliq=json.loads(request.POST.get('lista'))
            print 'listaaliq',listaaliq
            for gen in listaaliq:
                print 'gen',gen
                laliq=Aliquot.objects.filter(genealogyID=gen,endTimestamp__isnull=False)
                if len(laliq)!=0:
                    aliq=laliq[0]
                    aliq.endTimestamp=None
                    aliq.endOperator=None
                    aliq.save()
                    if aliq.idContainer!=None:
                        cont=aliq.idContainer
                        print 'cont',cont
                        if cont.idContainerType.idGenericContainerType.abbreviation=='tube':
                            cont.full=1
                            cont.availability=1
                            cont.owner=''
                        padre=None
                        #se il cont non ha un padre attualmente lo devo ripristinare prendendo l'ultimo padre che ha avuto (se esiste)
                        if cont.idFatherContainer==None:
                            #prendo tutte le righe dell'audit che riguardano quel cont ordinandole in base alla data
                            lisaudit=ContainerAudit.objects.filter(id=cont.id).exclude(present=0).order_by('-_audit_timestamp')
                            #nel primo valore della lista audit, ho il valore del padre (che puo' anche essere null)
                            padre=lisaudit[0].idFatherContainer
                            print 'padre',padre
                            cont.idFatherContainer=padre
                        
                        cont.present=1
                        cont.save()
                        
                        if padre!=None:
                            #devo vedere se con l'aggiunta di questo campione la piastra si e' riempita
                            if padre.idContainerType.idGenericContainerType.abbreviation=='plate':
                                posmax=padre.idContainerType.maxPosition
                                if posmax!=None:
                                    regole_geom=json.loads(padre.idGeometry.rules)
                                    dim = regole_geom['dimension']
                                    x = int(dim[1])
                                    y = int(dim[0])
                                    print 'x',x
                                    print 'y',y
                                    #devo tenere conto anche della posmax                        
                                    dimensione=x*y*int(posmax)
                                    lcont=Container.objects.filter(idFatherContainer=padre,present=1)
                                    print 'lcont',lcont
                                    if len(lcont)==dimensione:
                                        padre.full=1
                                        print 'piastra piena'
                                        padre.save()
                        #se il cont stesso e' una piastra devo vedere se con l'aggiunta di questo campione si e' riempita
                        if cont.idContainerType.idGenericContainerType.abbreviation=='plate':
                            posmax=cont.idContainerType.maxPosition
                            if posmax!=None:
                                regole_geom=json.loads(cont.idGeometry.rules)
                                dim = regole_geom['dimension']
                                x = int(dim[1])
                                y = int(dim[0])
                                print 'x',x
                                print 'y',y
                                #devo tenere conto anche della posmax                    
                                dimensione=x*y*int(posmax)
                                laliq=Aliquot.objects.filter(idContainer=cont,endTimestamp=None)
                                print 'laliq',laliq
                                if len(laliq)==dimensione:
                                    cont.full=1
                                    print 'piastra piena'
                                    cont.save()
            return 'ok'
        except Exception,e:
            print 'err',e
            transaction.rollback()
            return 'err'

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
