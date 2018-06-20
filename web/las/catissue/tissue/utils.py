from catissue.tissue.models import *
from catissue.tissue.genealogyID import *
from catissue.tissue.forms import *
from django.db import transaction
from django.db.models import Q
from django.template.context import RequestContext
from django.shortcuts import render_to_response
from django.http import HttpResponse
import string,urllib,urllib2,json,requests,random, ast
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from catissue.global_request_middleware import *
from lasEmail import *

from django.conf import settings
import os.path
from catissue.settings import TEMP_URL

#funzione che salva una lista di aliquote nel DB
@transaction.commit_on_success
def creaAliq(dict,lista,tumore,tessuto,caso,tipoaliq,request):
    pezziusati=0
    disponibile=1
    derivato=0
    k=1
    errore=False
    #per contenere i dati da inviare allo storage per salvare poi le aliquote alla fine
    if request.session.has_key('aliquots'):
        listaaliq=request.session.get('aliquots')
    else:
        listaaliq=[]
    #per contenere le aliquote da salvare alla fine
    if request.session.has_key('listaaliquote'):
        laliq=request.session.get('listaaliquote')
    else:
        laliq=[]
    #per contenere il numero di pezzi delle aliq
    if request.session.has_key('listafeature'):
        lfeature=request.session.get('listafeature')
    else:
        lfeature=[]
    print 'lista prima',listaaliq
    try:
        for key in lista:
            #for key,value in dict_rna.items():
            value=dict.get(key)
            if tipoaliq=='FF':
                value=1
            print 'value',value
            if k<10:
                s='0'+str(k)
            else:
                s=k
            val=key.split('-')
            g = GenealogyID('')
            data={'origin':str(tumore),'caseCode':str(caso),'tissue':str(tessuto),'sampleVector':'H','lineage':'00','samplePassage':'00','mouse':'000','tissueType':'000','archiveMaterial2':tipoaliq,'aliqExtraction2':str(s),'2derivationGen':'00'}
            g.updateGenID(data)
            genid=g.getGenID()
            print 'gen',genid
            #genid=str(tumore)+str(caso)+str(tessuto)+"H000000000"+tipoaliq+str(s)+"00"
            k=k+1
            tipoaliquota= AliquotType.objects.get(abbreviation=tipoaliq)
            
            barcode=None
            #se sto trattando vitale, rna e snap
            if(tipoaliq!='FF'):
                #in val[2] ho il barcode della piastra
                url = Urls.objects.get(default = '1').url + "/api/container/"+val[2]
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
                    errore=True
                    
                #per ottenere il barcode data la posizione    
                for w in data['children']:
                    #in val[1] ho la posizione selezionata
                    if w['position']==val[1]:
                        barcode=w['barcode']
                        print 'barc',barcode
                        break;
                #aggiorno la lista con i dati di tutte le aliquote salvate
                valori=str(genid)+','+str(value)+','+val[2]+','+val[1]+','+barcode+','+tipoaliq
                print 'valori',valori
            #se ho ffpe il barcode ce l'ho gia' e non devo andare a leggerlo
            else:
                barcode=val[2]
                #aggiorno la lista con i dati di tutte le aliquote salvate
                valori=genid+','+str(value)+','+val[2]+', '+','+barcode+','+tipoaliq
            print 'barcode',barcode
            s=SamplingEvent()
            a=Aliquot(barcodeID=barcode,
                       uniqueGenealogyID=str(genid),
                       idSamplingEvent=s,
                       idAliquotType=tipoaliquota,
                       timesUsed=pezziusati,
                       availability=disponibile,
                       derived=derivato
                       )
            print 'a',a
            #a.save()
            
            listaaliq.append(valori)
            listastorage=list(listaaliq)
            laliq.append(a)
            print 'listaaliq',listaaliq
            request.session['aliquots']=listaaliq
            request.session['listaaliquote']=laliq
            request.session['listastorage']=listastorage
            
            #salvo il numero di pezzi
            fea=Feature.objects.get(Q(idAliquotType=tipoaliquota)&Q(name='NumberOfPieces'))
            aliqfeature=AliquotFeature(idAliquot=a,
                                       idFeature=fea,
                                       value=value)
            #aliqfeature.save()
            #il salvataggio avviene dopo alla fine di tutta la collezione
            print 'aliq',aliqfeature
            lfeature.append(aliqfeature)
            request.session['listafeature']=lfeature
        
        print 'laliq',laliq    
        #request,errore=SalvaInStorage(laliq,request)

        if errore==True:
            raise Exception
        dict.clear()
        del lista[:]
        return dict,lista,errore
    except:
        transaction.rollback()
        errore=True
        return None,None,errore

#funzione che salva il numero di pezzi dell'aliquota e salva nell'archivio l'informazione
#relativa ad una nuova provetta piena
def SalvaInStorage(listaaliquota,request):
    listaffpe=''
    listaaliq=[]
    listatipialiq=[]
    errore=False
    for i in range(0,len(listaaliquota)):
        val=listaaliquota[i].split(',')
        if val[6]=='false':
            #in val[4] c'e' il barcode della provetta, in val[0] il gen, in val[12] la data
            listaaliq.append(val[4]+','+val[0]+','+val[12])
            listatipialiq.append(val[5])
        else:
            #in val[5] c'e' il tipo dell'aliq (VT,SF...), in val[4] il barc e in val[0] il genid
            listaffpe=listaffpe+val[4]+','+val[5]+','+val[0]+','+val[12]+'&'
    print 'listaaliq',listaaliq
    print 'listaffpeeeee',listaffpe
    #per salvare in rna,snap o vitale
    url1 = Urls.objects.get(default = '1').url + "/full/"
    val1={'lista':json.dumps(listaaliq),'tube':'full','tipo':listatipialiq,'operator':request.user.username}
    
    try:
        if len(listaaliq)!=0:
            print 'url1',url1
            data = urllib.urlencode(val1)
            req = urllib2.Request(url1,data=data, headers={"workingGroups" : get_WG_string()})
            u = urllib2.urlopen(req)
            #u = urllib2.urlopen(url1, data)
            res1 =  u.read()
            print 'res1--->', res1
        else:
            res1='ok'
        if len(listaffpe)!=0:
            #per salvare in ffpe,of o ch
            url2 = Urls.objects.get(default = '1').url + "/saveFFPE/"
            val2={'lista':listaffpe,'user':request.user.username}
            print 'url2',url2
            data = urllib.urlencode(val2)
            req = urllib2.Request(url2,data=data, headers={"workingGroups" : get_WG_string()})
            u = urllib2.urlopen(req)
            #u = urllib2.urlopen(url2, data)
            res2 =  u.read()
    except Exception, e: 
        #transaction.rollback()
        errore=True
        variables = RequestContext(request, {'errore':errore})
        print 'err salvainstorage', variables
        return render_to_response('tissue2/index.html',variables)
        print e
    if (res1 == 'err')or(len(listaffpe)!=0 and res2=='err'):
        print 'errore salvainstorage'
        #transaction.rollback()
        errore=True
        return request,errore
    return request,errore

#per gestire la parte di creazione del resoconto finale della collezione
def LastPartCollection(request,pdf):
    lista=[]
    if request.session.has_key('aliquots'):
        listaaliq=request.session.get('aliquots')
    print 'listaaliq',listaaliq
    sangue=False
    tess=False
    #devo capire se ci sono dei campioni di sangue o no
    for i in range(0,len(listaaliq)):
        info=listaaliq[i].split(',')
        #info[7] contiene il volume dell'eventuale campione di sangue
        if info[7]==' ':
            tess=True
        else:
            sangue=True
    intest=''
    print 'sang',sangue
    print 'tess',tess
    listacsv=[]
    intestcsv=[]
    if sangue==False and tess==True:
        for i in range(0,len(listaaliq)):
            info=listaaliq[i].split(',')
            lista.append(ReportCollectionToHtml(i+1,info[0],info[3],info[4],info[1],info[2],pdf))
            listacsv.append(str(i+1)+";"+str(info[0])+";"+str(info[3])+";"+info[4]+";"+info[1]+";"+info[2])
        if pdf=='n':
            intest='<th>N</th><th>GenealogyID</th><th>N. of pieces</th><th>Barcode</th><th>Plate</th><th>Position</th>'
        else:
            intest='<th align = \'center\'  width="3%"><strong><br>N</strong></th><th align = \'center\'><strong><br>GenealogyID</strong></th><th align = \'center\'  width="5%"><strong><br>N. of pieces</strong></th><th align = \'center\'><strong><br>Barcode</strong></th><th align = \'center\'><strong><br>Plate</strong></th><th align = \'center\' width="4%"><strong><br>Pos</strong></th>'
        intestcsv.append('N;GenealogyID;Number of pieces;Barcode;Plate;Position')
        
    elif sangue==True and tess==False:
        for i in range(0,len(listaaliq)):
            info=listaaliq[i].split(',')
            lista.append(ReportBloodCollectionToHtml(i+1,info[0],info[4],info[7],info[8],pdf))
            voll=str(info[7]).replace('.',',')
            conta=str(info[8]).replace('.',',')
            listacsv.append(str(i+1)+"\t"+str(info[0])+"\t"+str(info[4])+"\t"+voll+"\t"+conta)
        if pdf=='n':
            intest='<th>N</th><th>GenealogyID</th><th>Barcode</th><th>Volume(ml)</th><th>Count(cell/ml)</th>'
        else:
            intest='<th align = \'center\'  width="3%"><strong><br>N</strong></th><th align = \'center\'><strong><br>GenealogyID</strong></th><th align = \'center\'><strong><br>Barcode</strong></th><th align = \'center\'><strong><br>Volume(ml)</strong></th><th align = \'center\'><strong><br>Count(cell/ml)</strong></th>'
        intestcsv.append('N\tGenealogyID\tBarcode\tVolume(ml)\tCount(cell/ml)')
    elif sangue==True and tess==True:
        for i in range(0,len(listaaliq)):
            info=listaaliq[i].split(',')
            lista.append(ReportMixCollectionToHtml(i+1,info[0],info[3],info[4],info[1],info[2],info[7],info[8],pdf))
            voll=str(info[7]).replace('.',',')
            conta=str(info[8]).replace('.',',')
            listacsv.append(str(i+1)+"\t"+str(info[0])+"\t"+str(info[3])+"\t"+str(info[4])+"\t"+str(info[1])+"\t"+str(info[2])+"\t"+voll+"\t"+conta)
        if pdf=='n':
            intest='<th>N</th><th>GenealogyID</th><th>N. of pieces</th><th>Barcode</th><th>Plate</th><th>Position</th><th>Volume(ml)</th><th>Count(cell/ml)</th>'
        else:
            intest='<th align = \'center\'  width="3%"><strong><br>N</strong></th><th align = \'center\'><strong><br>GenealogyID</strong></th><th align = \'center\'  width="5%"><strong><br>N. of pieces</strong></th><th align = \'center\'><strong><br>Barcode</strong></th><th align = \'center\'><strong><br>Plate</strong></th><th align = \'center\'><strong><br>Position</strong></th><th align = \'center\'><strong><br>Volume(ml)</strong></th><th align = \'center\'><strong><br>Count(cell/ml)</strong></th>'
        intestcsv.append('N\tGenealogyID\tNumber of pieces\tBarcode\tPlate\tPosition\tVolume(ml)\tCount(cell/ml)');
    print 'lista',lista
    print 'intest',intest
    print 'listacsv',listacsv
    return lista,intest,listacsv,intestcsv

#per gestire la parte di creazione del resoconto finale delle aliquote esterne
def LastPartExternAliquot(request,pdf):
    lista=[]
    if request.session.has_key('aliquotEsterne'):
        listaaliq=request.session.get('aliquotEsterne')
    print 'listaaliq',listaaliq
    deriv=False
    linee=False
    #devo capire se ci sono dei derivati o no e delle linee cellulari o no
    for i in range(0,len(listaaliq)):
        info=listaaliq[i].split(',')
        #info[5] contiene il tipo del campione
        if info[5]=='DNA' or info[5]=='RNA' or info[5]=='cDNA' or info[5]=='cRNA':
            deriv=True
        if info[13]!='' or info[14]!='':
            linee=True

    intest=''
    print 'deriv',deriv
    listacsv=[]
    intestcsv=[]
    if deriv==False:
        for i in range(0,len(listaaliq)):
            info=listaaliq[i].split(',')
            if linee:
                lista.append(ReportToHtml([i+1,info[0],info[3],info[4],info[1],info[2],info[13],info[14]]))
                listacsv.append(str(i+1)+";"+str(info[0])+";"+str(info[3])+";"+info[4]+";"+info[1]+";"+info[2]+";"+info[13]+";"+info[14])
            else:
                lista.append(ReportToHtml([i+1,info[0],info[3],info[4],info[1],info[2]]))
                listacsv.append(str(i+1)+";"+str(info[0])+";"+str(info[3])+";"+info[4]+";"+info[1]+";"+info[2])
        if pdf=='n':
            if linee:
                intest='<th>N</th><th>GenealogyID</th><th>N. of pieces</th><th>Barcode</th><th>Plate</th><th>Position</th><th>Volume (ul)</th><th>Count (cell/ml)</th>'
            else:
                intest='<th>N</th><th>GenealogyID</th><th>N. of pieces</th><th>Barcode</th><th>Plate</th><th>Position</th>'
        else:
            intest='<th align = \'center\'  width="3%"><strong><br>N</strong></th><th align = \'center\'><strong><br>GenealogyID</strong></th><th align = \'center\'  width="5%"><strong><br>N. of pieces</strong></th><th align = \'center\'><strong><br>Barcode</strong></th><th align = \'center\'><strong><br>Plate</strong></th><th align = \'center\' width="4%"><strong><br>Pos</strong></th>'
        intestcsv.append('N;GenealogyID;Number of pieces;Barcode;Plate;Position')
        
    elif deriv==True:
        for i in range(0,len(listaaliq)):
            info=listaaliq[i].split(',')
            voll=str(info[7]).replace('.',',')
            conc=str(info[8]).replace('.',',')
            pur1=str(info[9]).replace('.',',')
            pur2=str(info[10]).replace('.',',')
            ge=str(info[11]).replace('.',',')
            if linee:
                #se e' una VT puo' essere una linea, quindi il volume e' in info[13]
                if info[5]=='VT':
                    lista.append(ReportToHtml([i+1,info[0],info[4],info[13],info[8],info[9],info[10],info[11],info[14]]))
                    listacsv.append(str(i+1)+"\t"+str(info[0])+"\t"+str(info[4])+"\t"+str(info[13])+"\t"+conc+"\t"+pur1+"\t"+pur2+"\t"+ge+"\t"+str(info[14]))
                else:                    
                    lista.append(ReportToHtml([i+1,info[0],info[4],info[7],info[8],info[9],info[10],info[11],info[14]]))
                    listacsv.append(str(i+1)+"\t"+str(info[0])+"\t"+str(info[4])+"\t"+voll+"\t"+conc+"\t"+pur1+"\t"+pur2+"\t"+ge+"\t"+str(info[14]))
            else:
                lista.append(ReportToHtml([i+1,info[0],info[4],info[7],info[8],info[9],info[10],info[11]]))   
                listacsv.append(str(i+1)+"\t"+str(info[0])+"\t"+str(info[4])+"\t"+voll+"\t"+conc+"\t"+pur1+"\t"+pur2+"\t"+ge)
        if pdf=='n':
            if linee:
                intest='<th>N</th><th>GenealogyID</th><th>Barcode</th><th>Volume (ul)</th><th>Conc. (ng/ul)</th><th>Purity (260/280)</th><th>Purity (260/230)</th><th>GE/Vex (GE/ml)</th><th>Count (cell/ml)</th>'
            else:
                intest='<th>N</th><th>GenealogyID</th><th>Barcode</th><th>Volume (ul)</th><th>Conc. (ng/ul)</th><th>Purity (260/280)</th><th>Purity (260/230)</th><th>GE/Vex (GE/ml)</th>'
        else:
            intest='<th align = \'center\'  width="3%"><strong><br>N</strong></th><th align = \'center\'><strong><br>GenealogyID</strong></th><th align = \'center\'><strong><br>Barcode</strong></th><th align = \'center\' width="9%"><strong><br>Volume(ul)</strong></th><th align = \'center\' width="9%"><strong><br>Conc. (ng/ul)</strong></th>\
            <th align = \'center\' width="9%"><strong><br>Purity (260/280)</strong></th><th align = \'center\' width="9%"><strong><br>Purity (260/230)</strong></th><th align = \'center\' width="9%"><strong><br>GE/Vex (GE/ml)</strong></th>'
        intestcsv.append('N\tGenealogyID\tBarcode\tVolume(ul)\tConc. (ng/ul)\tPurity (260/280)\tPurity (260/230)\tGE/Vex (GE/ml)')
    print 'lista',lista
    print 'intest',intest
    print 'listacsv',listacsv
    return lista,intest,listacsv,intestcsv

#per gestire la parte di creazione del resoconto finale della collezione di linee cellulari
def LastPartCellLine(request,pdf):
    lista=[]
    if request.session.has_key('cellLineNuove'):
        listaaliq=request.session.get('cellLineNuove')
    print 'listaaliq',listaaliq
    intest=''
    listacsv=[]
    intestcsv=[]

    for i in range(0,len(listaaliq)):
        info=listaaliq[i].split(',')
        lista.append(ReportCellLineToHtml(i+1,info[0],info[4],info[1],info[2],pdf))
        listacsv.append(str(i+1)+";"+str(info[0])+";"+info[4]+";"+info[1]+";"+info[2])
    if pdf=='n':
        intest='<th>N</th><th>GenealogyID</th><th>Barcode</th><th>Plate</th><th>Position</th>'
    else:
        intest='<th align = \'center\'  width="3%"><strong><br>N</strong></th><th align = \'center\'><strong><br>GenealogyID</strong></th><th align = \'center\'><strong><br>Barcode</strong></th><th align = \'center\'><strong><br>Plate</strong></th><th align = \'center\' width="4%"><strong><br>Pos</strong></th>'
    intestcsv.append('N;GenealogyID;Barcode;Plate;Position')
        
    print 'lista',lista
    print 'intest',intest
    print 'listacsv',listacsv
    return lista,intest,listacsv,intestcsv

#per gestire la parte di creazione del resoconto finale delle aliquote esterne
def LastPartCollectionBatch(request,pdf):
    lista=[]
    if request.session.has_key('aliquotCollectionBatch'):
        listaaliq=request.session.get('aliquotCollectionBatch')
    print 'listaaliq',listaaliq
    deriv=False
    #devo capire se ci sono dei derivati o no
    for i in range(0,len(listaaliq)):
        info=listaaliq[i].split(',')
        #info[5] contiene il tipo del campione
        if info[5]=='DNA' or info[5]=='RNA' or info[5]=='cDNA' or info[5]=='cRNA':
            deriv=True
            break

    intest=''
    print 'deriv',deriv
    listacsv=[]
    intestcsv=[]
    if deriv==False:        
        for i in range(0,len(listaaliq)):
            info=listaaliq[i].split(',')
            lista.append(ReportToHtml([i+1,info[0],info[4],info[7],info[9]]))
        if pdf=='n':
            intest='<th>N</th><th>GenealogyID</th><th>Barcode</th><th>Volume(ul)</th><th>Count(cell/ml)</th>'
        else:
            intest='<th align = \'center\'  width="3%"><strong><br>N</strong></th><th align = \'center\'><strong><br>GenealogyID</strong></th><th align = \'center\'><strong><br>Barcode</strong></th><th align = \'center\'><strong><br>Volume(ml)</strong></th><th align = \'center\'><strong><br>Count(cell/ml)</strong></th>'
        
    elif deriv==True:
        for i in range(0,len(listaaliq)):
            info=listaaliq[i].split(',')
            lista.append(ReportToHtml([i+1,info[0],info[4],info[7],info[8],info[9]]))
        if pdf=='n':
            intest='<th>N</th><th>GenealogyID</th><th>Barcode</th><th>Volume(ul)</th><th>Conc. (ng/ul)</th><th>Count(cell/ml)</th>'
        else:
            intest='<th align = \'center\'  width="3%"><strong><br>N</strong></th><th align = \'center\'><strong><br>GenealogyID</strong></th><th align = \'center\'><strong><br>Barcode</strong></th>\
            <th align = \'center\' width="9%"><strong><br>Volume(ml)</strong></th><th align = \'center\' width="9%"><strong><br>Conc. (ng/ul)</strong></th>'


    print 'lista',lista
    print 'intest',intest
    print 'listacsv',listacsv
    return lista,intest,listacsv,intestcsv

#serve per trasformare la visualizzazione delle aliquote collezionate in un formato
#compatibile con la visualizzazione in html
def ReportToHtml(lista):
    stringa='<tr>'
    for val in lista:
        stringa+='<td align="center">'+str(val)+'</td>'
    stringa+='</tr>'
    return stringa


#per gestire la parte di creazione del resoconto finale della derivazione
def LastPartDerivation(request,pdf,listaaliq):
    operatore=request.user.username
    lista=[]
    intest=''
    intcsv=''
    dizcsv={}
    intestcsv=[]
    diz={}
    dizsupervisori={}
    #if request.session.has_key('listaValAliqDer'):
        #listaaliq=request.session.get('listaValAliqDer')
    print 'listaaliq',listaaliq

    #operatore=request.session.get('operatore_derivazione')
    listamisure=[]
    misconc=[]
    #devo prendere tutte le misure fatte
    for i in range(0,len(listaaliq)):
        info=listaaliq[i].split('&')
        print 'info',info[0]
        #in info[0] ho il genid dell'aliquota derivata creata
        disable_graph()
        aliquot=Aliquot.objects.get(uniqueGenealogyID=info[0])
        #devo capire con che unita' di misura e' stata salvata la conc
        lisfeat=AliquotFeature.objects.filter(idAliquot=aliquot)
        enable_graph()
        for feat in lisfeat:
            if feat.idFeature.name=='Concentration':
                if feat.idFeature.measureUnit not in misconc:
                    misconc.append(feat.idFeature.measureUnit)
                
        print 'aliq',aliquot
        print 'operatore',operatore
        alder=DerivationEvent.objects.get(idSamplingEvent=aliquot.idSamplingEvent,operator=operatore)
        #prendo il qual event
        lisqualevent=QualityEvent.objects.filter(idAliquotDerivationSchedule=alder.idAliqDerivationSchedule)
        if len(lisqualevent)!=0:
            #prendo il qualev piu' recente
            qualevent=lisqualevent[len(lisqualevent)-1]
            #prendo gli eventi di misura
            misure=MeasurementEvent.objects.filter(idQualityEvent=qualevent)
            diz[info[0]]=misure
            for mis in misure:
                if mis.idMeasure not in listamisure:
                    listamisure.append(mis.idMeasure)
        print 'listamis',listamisure
        print 'diz',diz
        
        #creo un dizionario con dentro come chiave il nome del supervisore e come valore una lista con le procedure che lo
        #riguardano
        assegnatario=User.objects.get(username = alder.idAliqDerivationSchedule.idDerivationSchedule.operator)
        
        if assegnatario.email !='' and assegnatario.username!=operatore:
            diztemp={}
            diztemp['gen']=info[0]
            diztemp['barc']=info[1]
            diztemp['plate']=info[2]
            diztemp['pos']=info[3]
            diztemp['vol']=info[5]
            diztemp['conc']=info[4]
            if dizsupervisori.has_key(assegnatario.email):
                listatemp=dizsupervisori[assegnatario.email]
            else:
                listatemp=[]
            listatemp.append(diztemp)
            dizsupervisori[assegnatario.email]=listatemp
    #se nella lista ho piu' di una unita' di misura vuol dire che c'e' discordanza e quindi non scrivo niente nell'intestazione,
    #altrimenti scrivo l'unica unita' che c'e'
    print 'misconc',misconc
    if len(misconc)>1 or len(misconc)==0:
        unitamis=''
    else:
        unitamis=misconc[0]
    if pdf=='n':
        intest=intest+'<th>N</th><th>GenID</th><th>Barcode</th><th>Plate</th><th>Position</th><th>Volume (ul)</th><th>Concentration ('+unitamis+')</th>'
    else:
        intest='<th align = \'center\' width="3%"><strong><br>N</strong></th><th align = \'center\'><strong><br>GenID</strong></th><th align = \'center\' width="9%"><strong><br>Barcode</strong></th><th align = \'center\'><strong><br>Plate</strong></th><th align = \'center\' width="4%"><strong><br>Pos</strong></th><th align = \'center\' width="6%"><strong><br>Conc (ng/uL)</strong></th><th align = \'center\' width="6%"><strong><br>Vol (uL)</strong></th>'
    intcsv=intcsv+'N\tGenID\tBarcode\tPlate\tPosition\tVol(uL)\tConc(ng/uL)'
    for mes in listamisure:
        if pdf=='n':
            intest=intest+'<th>'+mes.name.capitalize()+' ('+mes.measureUnit+') '+mes.idInstrument.name+'</th>'
        else:
            intest=intest+'<th align = \'center\' width="9%"><strong><br>'+mes.name.capitalize()+' ('+mes.measureUnit+') '+mes.idInstrument.name+'</strong></th>'
        intcsv=intcsv+'\t'+mes.name.capitalize()+' ('+mes.measureUnit+') '+mes.idInstrument.name
    intestcsv.append(intcsv)
    #inserisco i dati
    for i in range(0,len(listaaliq)):
        s=listaaliq[i].split('&')
        if pdf=='n':
            valparziali=ReportDerivationToHtml(i+1,s[0],s[1],s[2],s[3],s[5],s[4],'n')
        else:
            valparziali=ReportDerivationToHtml(i+1,s[0],s[1],s[2],s[3],s[5],s[4],'s')
        conc=str(s[4]).replace('.',',')
        vol=str(s[5]).replace('.',',')
        valcsv=str(s[0])+"\t"+str(s[1])+"\t"+s[2]+"\t"+s[3]+"\t"+vol+"\t"+conc
                
        #scandisco le misure generali presenti n questa sessione
        for mis in listamisure:
            listamisaliq=diz[s[0]]
            #scndisco le misure del singolo campione
            valore=''
            for misaliq in listamisaliq:
                if mis.name==misaliq.idMeasure.name and mis.measureUnit==misaliq.idMeasure.measureUnit and mis.idInstrument.code==misaliq.idMeasure.idInstrument.code:
                    valore=str(misaliq.value)
                    break
            #print 'valore',valore
            if pdf=='n':
                valparziali=valparziali+'<td align="center">'+valore+'</td>'
            else:
                valparziali=valparziali+'<td align="center"><br>'+valore+'</td>'
            valvirgola=str(valore).replace('.', ',')
            valcsv2=valcsv+"\t"+valvirgola
        valparziali=valparziali+'</tr>'     
        lista.append(valparziali)
        #s[0] e' il gen
        dizcsv[str(s[0])]=valcsv
    print 'lista',lista
    print 'intest',intest
    print 'dizcsv',dizcsv
    return lista,intest,dizcsv,intestcsv,dizsupervisori,unitamis

#per gestire la parte di creazione del resoconto finale della rivalutazione
def LastPartRevaluation(listaaliq):
    lista=[]
    intest=''
    diz={}
    
    print 'listaaliq',listaaliq

    listamisure=[]
    #devo prendere tutte le misure fatte
    for i in range(0,len(listaaliq)):
        info=listaaliq[i].split('&')
        print 'info',info[0]
        #in info[0] ho il genid dell'aliquota derivata creata
        aliquot=Aliquot.objects.get(uniqueGenealogyID=info[0])
        print 'aliq',aliquot
        #prendo il qual event
        lisqualevent=QualityEvent.objects.filter(idAliquot=aliquot,insertionDate=date.today())        
        if len(lisqualevent)!=0:
            #prendo il qualev piu' recente
            qualevent=lisqualevent[len(lisqualevent)-1]
            #prendo gli eventi di misura
            misure=MeasurementEvent.objects.filter(idQualityEvent=qualevent)
            diz[info[0]]=misure
            for mis in misure:
                if mis.idMeasure not in listamisure:
                    listamisure.append(mis.idMeasure)
        else:
            diz[info[0]]=[]
        print 'listamis',listamisure
        print 'diz',diz                

    intest=intest+'<th>N</th><th>Genealogy ID</th><th>Barcode</th><th>Position</th><th>Exhausted</th>'
    
    for mes in listamisure:
        intest=intest+'<th>'+mes.name.capitalize()+' ('+mes.measureUnit+') '+mes.idInstrument.name+'</th>'

    #inserisco i dati
    for i in range(0,len(listaaliq)):
        s=listaaliq[i].split('&')
        valparziali=ReportToHtml([i+1,s[0],s[1],s[2],s[3]])
        #devo cancellare il </tr> che mi mette la funzione di prima, cosi' da poter continuare sulla stessa riga
        valparziali=valparziali[:-5]
        print 'valparz',valparziali
        
        listamisaliq=diz[s[0]]
        #scandisco le misure generali presenti in questa sessione
        for mis in listamisure:
            #scandisco le misure del singolo campione
            valore=''
            for misaliq in listamisaliq:
                if mis.name==misaliq.idMeasure.name and mis.measureUnit==misaliq.idMeasure.measureUnit and mis.idInstrument.code==misaliq.idMeasure.idInstrument.code:
                    valore=str(misaliq.value)
                    break
            print 'valore',valore
            valparziali=valparziali+'<td align="center">'+valore+'</td>'
            
        valparziali=valparziali+'</tr>'     
        lista.append(valparziali)
    print 'lista',lista
    print 'intest',intest
    return lista,intest

#per gestire la parte finale del posizionamento sulla piastra vitale
def LastPartPosition(request,pdf):
    lista=[]
    if request.session.has_key('lisValPositionReport'):
        listaaliq=request.session.get('lisValPositionReport')
    print 'listaaliq',listaaliq
    
    listacsv=[]
    intestcsv=[]
    for i in range(0,len(listaaliq)):
        info=listaaliq[i].split('&')
        lista.append(ReportToHtml([i+1,info[0],info[1],info[2],info[3],info[4],info[5]]))
        listacsv.append(str(i+1)+"\t"+str(info[0])+"\t"+str(info[1])+"\t"+info[2]+"\t"+info[3]+"\t"+info[4]+"\t"+info[5])
    if pdf=='n':
        intest='<th>N</th><th>GenealogyID</th><th>Old barcode</th><th>Old position</th><th>Current barcode</th><th>Container</th><th>Position</th>'
    else:
        intest='<th align = \'center\' width="3%"><strong><br>N</strong></th><th align = \'center\'><strong><br>GenealogyID</strong></th><th align = \'center\'><strong><br>Old barcode</strong></th><th align = \'center\'><strong><br>Old position</strong></th><th align = \'center\'><strong><br>Current barcode</strong></th><th align = \'center\'><strong><br>Container</strong></th><th align = \'center\' width="4%"><strong><br>Pos</strong></th>'
    intestcsv.append('N\tGenealogyID\tOld barcode\tOld position\tCurrent barcode\tContainer\tPosition')
    
    print 'lista',lista
    print 'intest',intest
    print 'listacsv',listacsv
    return lista,intest,listacsv,intestcsv

#per gestire la creazione del pdf e csv nella schermata orientata al paziente
def LastPartPatient(request,pdf):
    intest=''
    listacsv=[]
    intestcsv=[]
    lista=[]
    intcsv=''
    if request.session.has_key('listaaliqpatientpdf'):
        listaaliq=request.session.get('listaaliqpatientpdf')
    if request.session.has_key('listacolonnepatientpdf'):
        listacolonne=request.session.get('listacolonnepatientpdf')
    
    print 'listaaliq',listaaliq
    print 'listacol',listacolonne
    #creo l'intestazione prendendo listacolonne    
    intest+='<th align = \'center\' width="3%"><strong><br>N</strong></th>'
    intcsv+='N\t'
    for val in listacolonne:
        intest+='<th align = \'center\' ><strong><br>'+val+'</strong></th>'
        intcsv+=val+'\t'
    #tolgo l'ultimo \t alla fine della stringa
    lung=len(intcsv)-1
    intcsv=intcsv[:lung]
    intestcsv.append(intcsv)
    print 'intcsv',intcsv
    print 'intest',intest
    
    #inserisco i valori per ogni singola aliquota
    i=1
    for aliq in listaaliq:
        valparziali='<tr><td align="center"><br><strong>'+str(i)+'</strong></td>'        
        csvparz=str(i)
        for val in aliq:
            for v in aliq[val]:
                valparziali+='<td align="center"><br>'+v+'</td>'
                if v.isdigit():
                    val=v.replace('.',',')
                else:
                    val=v
                csvparz+='\t'+val
        valparziali+='</tr>'
        lista.append(valparziali)
        listacsv.append(csvparz)
        i=i+1
    print 'lista',lista
    return lista,intest,listacsv,intestcsv

#per gestire la parte finale del trasferimento di campioni
def LastPartTransfer(request,pdf,diction,listaaliq):
    lista=[]
    #if request.session.has_key('listaaliqtrasferire'):
    #    listaaliq=request.session.get('listaaliqtrasferire')
    print 'listaaliq',listaaliq
    
    dizcsv={}
    intestcsv=[]
    for i in range(0,len(listaaliq)):
        al=listaaliq[i]
        vol=''
        volfin=''
        #devo vedere se il campione ha un volume
        lisfeatvol=Feature.objects.filter(Q(name='Volume')&Q(idAliquotType=al.idAliquot.idAliquotType)&Q(measureUnit='ul'))
        print 'lisfeatvol',lisfeatvol
        if len(lisfeatvol)!=0:
            lisaliqfeat=AliquotFeature.objects.filter(Q(idFeature=lisfeatvol[0])&Q(idAliquot=al.idAliquot))
            if len(lisaliqfeat)!=0:
                vol=int(lisaliqfeat[0].value)
                print 'vol',vol
                if vol>0:
                    volfin=str(vol).replace('.',',')
        print 'volfin',volfin
        #devo prendere il codice paziente
        codpaz=al.idAliquot.idSamplingEvent.idCollection.patientCode
        print 'codpaz',codpaz
        #prendo la data di creazione del campione
        datacreazione=str(al.idAliquot.idSamplingEvent.samplingDate)
        print 'datacreazione',datacreazione
        
        valori=diction[al.idAliquot.uniqueGenealogyID]
        val=valori[0].split('|')
        barc=val[1]
        pos=val[2]
        print 'valori',valori
        lista.append(ReportTransferToHtml(i+1,al.idAliquot.uniqueGenealogyID,barc,pos,str(vol),str(codpaz),datacreazione,pdf))
        dizcsv[al.idAliquot.uniqueGenealogyID]=str(al.idAliquot.uniqueGenealogyID)+"\t"+str(barc)+"\t"+str(pos)+"\t"+volfin+"\t"+str(codpaz)+"\t"+datacreazione
    if pdf=='n':
        intest='<th>N</th><th>GenealogyID</th><th>Barcode</th><th>Position</th><th>Volume(ul)</th><th>Patient code</th><th>Creation date</th>'
    else:
        intest='<th align = \'center\' width="3%"><strong><br>N</strong></th><th align = \'center\'><strong><br>GenealogyID</strong></th><th align = \'center\'><strong><br>Barcode</strong></th><th align = \'center\'><strong><br>Position</strong></th><th align = \'center\'><strong><br>Volume(ul)</strong></th><th align = \'center\'><strong><br>Patient code</strong></th><th align = \'center\'><strong><br>Creation date</strong></th>'
    intestcsv.append('N\tGenealogyID\tBarcode\tVolume(ul)')
    
    print 'lista',lista
    print 'intest',intest
    print 'dizcsv',dizcsv
    return lista,intest,dizcsv,intestcsv

#serve per trasformare la visualizzazione delle aliquote collezionate in un formato
#compatibile con la visualizzazione in html
#si puo' usare sia per la tabella di riepilogo che per la creazione del pdf
def ReportCollectionToHtml(n,genid,pezzi,barcode,piastra,pos,pdf):
    if pdf=="s":
        return '<tr><td align="center"><br><strong>'+str(n)+'</td><td align="center"><br>'+genid+'</td><td align="center"><br>'+str(pezzi)+'</td><td align="center"><br>'+barcode+'</td><td align="center"><br>'+piastra+'</td><td align="center"><br>'+ pos +'</td></tr>'
    else:
        return '<tr><td align="center">'+str(n)+'</td><td align="center">'+genid+'</td><td align="center">'+str(pezzi)+'</td><td align="center">'+barcode+'</td><td align="center">'+piastra+'</td><td align="center">'+ pos +'</td></tr>'

#serve per trasformare la visualizzazione delle aliquote collezionate in un formato
#compatibile con la visualizzazione in html
#si puo' usare sia per la tabella di riepilogo che per la creazione del pdf
def ReportBloodCollectionToHtml(n,genid,piastra,volume,conta,pdf):
    if pdf=="s":
        return '<tr><td align="center"><br><strong>'+str(n)+'</td><td align="center"><br>'+genid+'</td><td align="center"><br>'+str(piastra)+'</td><td align="center"><br>'+volume+'</td><td align="center"><br>'+ conta +'</td></tr>'
    else:
        return '<tr><td align="center">'+str(n)+'</td><td align="center">'+genid+'</td><td align="center">'+str(piastra)+'</td><td align="center">'+volume+'</td><td align="center">'+ conta +'</td></tr>'

#serve per trasformare la visualizzazione delle aliquote collezionate in un formato
#compatibile con la visualizzazione in html
#si puo' usare sia per la tabella di riepilogo che per la creazione del pdf
def ReportMixCollectionToHtml(n,genid,pezzi,barcode,piastra,pos,volume,conta,pdf):
    if pdf=="s":
        return '<tr><td align="center"><br><strong>'+str(n)+'</td><td align="center"><br>'+genid+'</td><td align="center"><br>'+str(pezzi)+'</td><td align="center"><br>'+barcode+'</td><td align="center"><br>'+piastra+'</td><td align="center"><br>'+pos+'</td><td align="center"><br>'+volume+'</td><td align="center"><br>'+conta+'</td></tr>'
    else:
        return '<tr><td align="center">'+str(n)+'</td><td align="center">'+genid+'</td><td align="center">'+str(pezzi)+'</td><td align="center">'+barcode+'</td><td align="center">'+piastra+'</td><td align="center">'+ pos +'</td><td align="center">'+volume+'</td><td align="center">'+conta+'</td></tr>'

#serve per trasformare la visualizzazione delle aliquote collezionate in un formato
#compatibile con la visualizzazione in html
#si puo' usare sia per la tabella di riepilogo che per la creazione del pdf
def ReportExternCollectionToHtml(n,genid,provetta,volume,conc,pur1,pur2,ge,pdf):
    if pdf=="s":
        return '<tr><td align="center"><br><strong>'+str(n)+'</td><td align="center"><br>'+genid+'</td><td align="center"><br>'+str(provetta)+'</td><td align="center"><br>'+volume+'</td><td align="center"><br>'+ conc +'</td><td align="center"><br>'+ pur1 +'</td><td align="center"><br>'+ pur2 +'</td><td align="center"><br>'+ ge +'</td></tr>'
    else:
        return '<tr><td align="center">'+str(n)+'</td><td align="center">'+genid+'</td><td align="center">'+str(provetta)+'</td><td align="center">'+volume+'</td><td align="center">'+ conc +'</td><td align="center">'+ pur1 +'</td><td align="center">'+ pur2 +'</td><td align="center">'+ ge +'</td></tr>'

#serve per trasformare la visualizzazione delle aliquote collezionate in un formato
#compatibile con la visualizzazione in html
#si puo' usare sia per la tabella di riepilogo che per la creazione del pdf
def ReportCellLineToHtml(n,genid,barcode,piastra,pos,pdf):
    if pdf=="s":
        return '<tr><td align="center"><br><strong>'+str(n)+'</td><td align="center"><br>'+genid+'</td><td align="center"><br>'+barcode+'</td><td align="center"><br>'+piastra+'</td><td align="center"><br>'+ pos +'</td></tr>'
    else:
        return '<tr><td align="center">'+str(n)+'</td><td align="center">'+genid+'</td><td align="center">'+barcode+'</td><td align="center">'+piastra+'</td><td align="center">'+ pos +'</td></tr>'

#serve per trasformare la visualizzazione delle aliquote derivate in un formato
#compatibile con la visualizzazione in html
#si puo' usare sia per la tabella di riepilogo che per la creazione del pdf
def ReportDerivationToHtml(n,genid,barcode,piastra,pos,conc,vol,pdf):
    if pdf=="s":
        return '<tr><td align="center"><br><strong>'+str(n)+'</td><td align="center"><br>'+genid+'</td><td align="center"><br>'+barcode+'</td><td align="center"><br>'+piastra+'</td><td align="center"><br>'+ pos +'</td><td align="center"><br>'+conc+'</td><td align="center"><br>'+vol+'</td>'
    else:
        return '<tr><td align="center">'+str(n)+'</td><td align="center">'+genid+'</td><td align="center">'+barcode+'</td><td align="center">'+piastra+'</td><td align="center">'+ pos +'</td><td align="center">'+conc+'</td><td align="center">'+vol+'</td>'
 
'''#serve per trasformare la visualizzazione dei kit inseriti in un formato
#compatibile con la visualizzazione in html
#si puo' usare sia per la tabella di riepilogo che per la creazione del pdf
def ReportKitToHtml(n,tipo,barcode,data,lotto,pdf):
    if pdf=="s":
        return '<tr><td align="center"><br><strong>'+str(n)+'</td><td align="center"><br><strong>'+tipo+'</td><td align="center"><br>'+barcode+'</td><td align="center"><br>'+data+'</td><td align="center"><br>'+ lotto +'</td></tr>'
    else:
        return '<tr><td align="center">'+tipo+'</td><td align="center">'+barcode+'</td><td align="center">'+data+'</td><td align="center">'+ lotto +'</td></tr>' 
'''
#serve per trasformare la visualizzazione dei campioni il cui volume e' da diminuire in un
#formato compatibile con la visualizzazione in html
#si puo' usare sia per la tabella di riepilogo che per la creazione del pdf
def ReportVolumeToHtml(n,esperim,gen,barcode,pos,conc,takenvol,finalvol,esausta,pdf):
    if pdf=="s":
        return '<tr><td align="center"><br><strong>'+str(n)+'</td><td align="center"><br><strong>'+esperim+'</td><td align="center"><br><strong>'+gen+'</td><td align="center"><br>'+barcode+'</td><td align="center"><br>'+pos+'</td><td align="center"><br>'+conc+'</td><td align="center"><br>'+ takenvol +'</td><td align="center"><br>'+ finalvol +'</td><td align="center"><br>'+ esausta +'</td></tr>'
    else:
        return '<tr><td align="center">'+str(n)+'</td><td align="center">'+esperim+'</td><td align="center">'+gen+'</td><td align="center">'+barcode+'</td><td align="center">'+pos+'</td><td align="center">'+conc+'</td><td align="center">'+ takenvol +'</td><td align="center">'+ finalvol +'</td><td align="center">'+ esausta +'</td></tr>' 

#serve per trasformare la visualizzazione delle aliquote programmate per rivalutazione, split o 
#posizionamento e poi cancellate in un formato compatibile con la visualizzazione in html
#si puo' usare sia per la tabella di riepilogo che per la creazione del pdf
def ReportScheduleCancToHtml(n,genid,barcode,pos,assigner,data,pdf):
    if pdf=="s":
        return '<tr><td align="center"><br><strong>'+str(n)+'</td><td align="center"><br>'+genid+'</td><td align="center"><br>'+barcode+'</td><td align="center"><br>'+pos+'</td><td align="center"><br>'+assigner+'</td><td align="center"><br>'+ data +'</td></tr>'
    else:
        return '<tr><td align="center">'+str(n)+'</td><td align="center">'+genid+'</td><td align="center">'+barcode+'</td><td align="center">'+pos+'</td><td align="center">'+assigner+'</td><td align="center">'+ data +'</td></tr>'
   
def ReportTransferToHtml(n,genid,barc,pos,vol,codpaz,data,pdf):
    if pdf=="s":
        return '<tr><td align="center"><br><strong>'+str(n)+'</td><td align="center"><br>'+genid+'</td><td align="center"><br>'+barc+'</td><td align="center"><br>'+pos+'</td><td align="center"><br>'+vol+'</td><td align="center"><br>'+codpaz+'</td><td align="center"><br>'+data+'</td></tr>'
    else:
        return '<tr><td align="center">'+str(n)+'</td><td align="center">'+genid+'</td><td align="center">'+barc+'</td><td align="center">'+pos+'</td><td align="center">'+vol+'</td><td align="center">'+codpaz+'</td><td align="center">'+data+'</td></tr>'

class Misura(models.Model):
    tipo=models.CharField()
    unit=models.CharField()
    tipostrum=models.CharField()
    codstrum=models.CharField()
    val=models.FloatField()
    
class AggiornaVolume(models.Model):
    gen=models.CharField()
    barcode=models.CharField()
    position=models.CharField()
    concattuale=models.CharField()
    volattuale=models.CharField()
    volpreso=models.CharField()
    quantpresa=models.CharField()
    volequiv=models.CharField()
    volfinale=models.CharField()
    replicati=models.CharField()
    def __unicode__(self):
        return self.gen+' '+self.concattuale

#restituisce i dati per costruire la tabella in HTML e le dimensioni della piastra
#nel vettore dim. Il tipo e' il tipo aliq abbreviato
def CreaTabella (data,tipo):
    #prendo le dimensioni della piastra
    lista=[]
    dimension = data['rules']['dimension']
    print 'dimension',dimension
    dim = []
   
    #print 'fe',featu
    for d in dimension:
        dim.append(d)
        #lastIndex = lastIndex + str(d)
    #per vedere se quello che sto trattando e' una piastra o una provetta
    #contpiastra=data['piastra']
    for d in data['children']:
        for rr in data['rules']['items']:
            #devo fare il controllo perche' se il posto e' vuoto, allora in d['position'] non c'e' quell'id (es: A3, F3)
            #se e' una provetta non e' detto che la posizione sia A1, quindi mi baso sull'altra condizione
            #che mi viene restituita dallo storage
            if rr['id'] == d['position'] :#or contpiastra==False:
                point = ""
                for p in rr['position']:
                    if point != "":
                        point = str(point) + '|' + str(p)
                    else:
                        point = str(p)
                
                listagen=Aliquot.objects.filter(uniqueGenealogyID=str(d['gen']),availability=1)
                
                #VERSION FOR GRAPH_DB
                if settings.USE_GRAPH_DB==True and 'admin' not in get_WG():
                    disable_graph()
                    count_old=Aliquot.objects.filter(uniqueGenealogyID=str(d['gen']),availability=1)
                    enable_graph()
                                      
                    if count_old.count()!=0:
                        if listagen.count()==0:
                            prov=str(d['barcode'])+','+str(d['position'])+','+str(point)+',NOT AVAILABLE,X'
                        else:
                            
                            #if aliqtip.type=='Original':
                            #    #prendo il genID dato il barc della provetta
                            #    gen=Aliquot.objects.get(Q(barcodeID=str(d['barcode']))&Q(availability=1)&Q(derived=0))
                            #    if len(featu)!=0:
                            #        pezzi=AliquotFeature.objects.filter(Q(idAliquot=gen)&Q(idFeature=featu[0]))
                            #        if len(pezzi)!=0:
                            #            pzz=str(int(pezzi[0].value))
                            #        else:
                            #            pzz='0'
                            #    else:
                            #        pzz='0'
                            #        #print 'n pezzi',pezzi.value
                            #    prov=str(d['barcode'])+','+str(d['position'])+','+str(point)+','+gen.uniqueGenealogyID+','+pzz
                            #else:
                            #se l'aliq e' derivata metto a 0 il num di pezzi
                            #    gen=Aliquot.objects.get(Q(barcodeID=str(d['barcode']))&Q(availability=1)&Q(derived=1))
                            #    prov=str(d['barcode'])+','+str(d['position'])+','+str(point)+','+gen.uniqueGenealogyID+',0
                            aliqtip=AliquotType.objects.get(abbreviation=listagen[0].idAliquotType.abbreviation)
                            #recupero l'oggetto feature relativo al numero di pezzi per le aliq
                            featu=Feature.objects.filter(Q(name='NumberOfPieces')&Q(idAliquotType=aliqtip))
                            prov=CreaStringa(listagen[0], featu, d, point)
                    #se la provetta e' vuota
                    else:
                        prov=str(d['barcode'])+','+str(d['position'])+','+str(point)
                else:
                    #VERSION WITH NO GRAPH_DB    
                    #se la provetta e' piena
                    if listagen.count()!=0:
                        aliqtip=AliquotType.objects.get(abbreviation=listagen[0].idAliquotType.abbreviation)
                        #recupero l'oggetto feature relativo al numero di pezzi per le aliq
                        featu=Feature.objects.filter(Q(name='NumberOfPieces')&Q(idAliquotType=aliqtip))
                        prov=CreaStringa(listagen[0], featu, d, point)
                    #se la provetta e' vuota
                    else:
                        prov=str(d['barcode'])+','+str(d['position'])+','+str(point)
                if prov not in lista:
                    lista.append(prov)

    print 'lis',lista
    return lista, dim

   
'''#restituisce i dati per costruire la tabella in HTML e le dimensioni della piastra
#nel vettore dim. Il tipo e' il tipo aliq abbreviato
def CreaTabella (data,tipo):
    #prendo le dimensioni della piastra
    lista=[]
    dimension = data['rules']['dimension']
    print 'dimension',dimension
    barcodeStr = ""
    dim = []

    aliqtip=AliquotType.objects.get(abbreviation=tipo)
    print 'aliqtip',aliqtip
    #if aliqtip.type=='Original':
        #recupero l'oggetto feature relativo al numero di pezzi per le aliq
        #featu=Feature.objects.filter(Q(name='NumberOfPieces')&Q(idAliquotType=aliqtip))
        #print 'fe',featu
    for d in dimension:
        dim.append(d)
        #lastIndex = lastIndex + str(d)
    print 'data',data
    #per vedere se quello che sto trattando e' una piastra o una provetta
    contpiastra=data['piastra']
    for d in data['children']:
        for rr in data['rules']['items']:
            #se e' una provetta non e' detto che la posizione sia A1, quindi mi baso sull'altra condizione
            #che mi viene restituita dallo storage
            if rr['id'] == d['position'] or contpiastra==False:
                point = ""
                for p in rr['position']:
                    if point != "":
                        #point = str(point) +  str(p)
                        point = str(point) + '|' + str(p)
                    else:
                        point = str(p)

                if aliqtip.type=='Original':
                    listagen=Aliquot.objects.filter(Q(barcodeID=str(d['barcode']))&Q(availability=1)&Q(derived=0))
                    al_type=1
                else:
                    listagen=Aliquot.objects.filter(Q(barcodeID=str(d['barcode']))&Q(availability=1)&Q(derived=1))
                    al_type=2
                #print 'listagen',listagen
                #se la provetta e' piena
                if settings.USE_GRAPH_DB==False or 'admin' in get_WG():
                    
                    if listagen.count()!=0:
                        if aliqtip.type=='Original':
                            #prendo il genID dato il barc della provetta
                            gen=Aliquot.objects.get(Q(barcodeID=str(d['barcode']))&Q(availability=1)&Q(derived=0))
                            print 'gen',gen
                            featu=Feature.objects.filter(Q(name='NumberOfPieces')&Q(idAliquotType=gen.idAliquotType))
                            if len(featu)!=0:
                                print 'featu[0]',featu[0]
                                pezzi=AliquotFeature.objects.filter(Q(idAliquot=gen)&Q(idFeature=featu[0]))
                                print 'pezzi',pezzi
                                if len(pezzi)!=0:
                                    pzz=str(int(pezzi[0].value))
                                else:
                                    pzz='0'
                            else:
                                pzz='0'
                            #print 'n pezzi',pezzi.value
                            prov=str(d['barcode'])+','+str(d['position'])+','+str(point)+','+gen.uniqueGenealogyID+','+pzz
                        else:
                            #se l'aliq e' derivata metto a 0 il num di pezzi
                            gen=Aliquot.objects.get(Q(barcodeID=str(d['barcode']))&Q(availability=1)&Q(derived=1))
                            prov=str(d['barcode'])+','+str(d['position'])+','+str(point)+','+gen.uniqueGenealogyID+',0'
                    #se la provetta e' vuota
                    else:
                        prov=str(d['barcode'])+','+str(d['position'])+','+str(point)
                    lista.append(prov)
                else:
                    if al_type==1:
                        disable_graph()
                        count_old=Aliquot.objects.filter(Q(barcodeID=str(d['barcode']))&Q(availability=1)&Q(derived=0)).count()
                        enable_graph()
                    else:
                        disable_graph()
                        count_old=Aliquot.objects.filter(Q(barcodeID=str(d['barcode']))&Q(availability=1)&Q(derived=1)).count()
                        enable_graph()
                    if count_old!=0:
                        if listagen.count()==0:
                            prov=str(d['barcode'])+','+str(d['position'])+','+str(point)+',NOT AVAILABLE,X'
                        else:
                            if aliqtip.type=='Original':
                            #prendo il genID dato il barc della provetta
                            #print d['barcode']
                                gen=Aliquot.objects.get(Q(barcodeID=str(d['barcode']))&Q(availability=1)&Q(derived=0))
                                if len(featu)!=0:
                                    pezzi=AliquotFeature.objects.filter(Q(idAliquot=gen)&Q(idFeature=featu[0]))
                                    if len(pezzi)!=0:
                                        pzz=str(int(pezzi[0].value))
                                    else:
                                        pzz='0'
                                else:
                                    pzz='0'
                                #print 'n pezzi',pezzi.value
                                prov=str(d['barcode'])+','+str(d['position'])+','+str(point)+','+gen.uniqueGenealogyID+','+pzz
                            else:
                                #se l'aliq e' derivata metto a 0 il num di pezzi
                                gen=Aliquot.objects.get(Q(barcodeID=str(d['barcode']))&Q(availability=1)&Q(derived=1))
                                prov=str(d['barcode'])+','+str(d['position'])+','+str(point)+','+gen.uniqueGenealogyID+',0'
                        #se la provetta e' vuota
                    else:
                        prov=str(d['barcode'])+','+str(d['position'])+','+str(point)
                    print prov
                    lista.append(prov)

    #address = Urls.objects.get(default = '1').url
    #u = urllib2.urlopen(address+"/api/tubes/"+barcodeStr[0:len(barcodeStr)-1])
    print 'lis',lista
    return lista, dim'''
   
def CreaStringa(aliq,featu,d,point):
    pzz='#'
    if len(featu)!=0:
        pezzi=AliquotFeature.objects.filter(idAliquot=aliq,idFeature=featu[0])
        if len(pezzi)!=0:
            pzz=str(int(pezzi[0].value))
                    
    prov=str(d['barcode'])+','+str(d['position'])+','+str(point)+','+str(d['gen'])+','+pzz

    return prov

def AllAliquotsContainer(genbarc):
    dizgen={}
    barc=genbarc.replace('#','%23')
    barc=barc.replace(' ','%20')
    lisval=barc.split('&')
    lbarc=''
    lis_pezzi_url=[]
    for val in lisval:
        lbarc+=val+'&'
        if len(lbarc)>2000:
        #cancello la & alla fine della stringa
            lis_pezzi_url.append(lbarc[:-1])
            lbarc=''
    #cancello la & alla fine della stringa
    strbarc=lbarc[:-1]
    print 'strbarc',strbarc
    if strbarc!='':
        lis_pezzi_url.append(strbarc)
    
    if len(lis_pezzi_url)!=0:
        for elementi in lis_pezzi_url:
            indir=Urls.objects.get(default=1).url
            req = urllib2.Request(indir+"/api/list/container/"+elementi, headers={"workingGroups" : get_WG_string()})
            u = urllib2.urlopen(req)
            #u = urllib2.urlopen(indir+"/api/list/container/"+elementi)
            data = json.loads(u.read())
            diz=data['data']
            print 'diz',diz
            dizgen = dict(dizgen.items() + diz.items())
    return dizgen

def InviaMail(scopo,name,laliq,listar,diz):
    
    '''if len(dizsupervisori)!=0:
        for key,value in dizsupervisori.items():
            file_data = render_to_string('tissue2/revalue/report_canc.html', {'listafin':value,'scopo':scopo,'esec':name}, RequestContext(request))
            
            subject, from_email = 'Cancel schedule', settings.EMAIL_HOST_USER
            text_content = 'This is an important message.'
            html_content = file_data
            msg = EmailMultiAlternatives(subject, text_content, from_email, [key])
            msg.attach_alternative(html_content, "text/html")
            msg.send()'''
    email = LASEmail (functionality=get_functionality(), wgString=get_WG_string())
    msg=[scopo+' schedules deleted','','Assigned to:\t'+name,'','Aliquots:','N\tGenealogy ID\tBarcode\tPosition\tAssignment date']
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
        for alder in listar:
            for al in aliq:   
                if alder.idAliquot.uniqueGenealogyID==al.uniqueGenealogyID:
                    lval=diz[al.uniqueGenealogyID]
                    val=lval[0].split('|')
                    barc=val[1]
                    pos=val[2]
                    if scopo=='Revaluation':
                        data=alder.idQualitySchedule.scheduleDate
                        pianificatore=alder.idQualitySchedule.operator
                    elif scopo=='Split':
                        data=alder.idSplitSchedule.scheduleDate
                        pianificatore=alder.idSplitSchedule.operator
                    elif scopo=='Retrieve':
                        data=alder.idExperimentSchedule.scheduleDate
                        pianificatore=alder.idExperimentSchedule.operator.username
                    elif scopo=='Label':
                        data=alder.idLabelSchedule.scheduleDate
                        pianificatore=alder.idLabelSchedule.operator.username
                    email.addMsg([wg.name],[str(i)+'\t'+al.uniqueGenealogyID+'\t'+barc+'\t'+pos+'\t'+str(data)])
                    i=i+1                                
                    if pianificatore not in lisplanner:
                        lisplanner.append(pianificatore)
        print 'lisplanner',lisplanner
        #devo mandare l'e-mail al pianificatore della procedura
        email.addRoleEmail([wg.name], 'Planner', lisplanner)
        email.addRoleEmail([wg.name], 'Executor', [name])
    try:
        email.send()
    except Exception, e:
        print 'errore',e
        pass
        
#chiamata al LASHub per farmi dare il codice del caso
def LasHubNewCase(request,casuale,tumore):
    #prefisso= 'https://' if settings.LAS_AUTH_USE_HTTPS else 'http://'
    #address=request.get_host()+settings.HOST_URL
    #indir=prefisso+address
    indir=settings.DOMAIN_URL+settings.HOST_URL
    url = indir + '/clientHUB/getAndLock/'
    print 'url',url
    values = {'randomFlag' : casuale, 'case': tumore}
    
    r = requests.post(url, data=values, verify=False, headers={"workingGroups" : get_WG_string()})
    return r.text

def NewCase(val,casuale,tumore):
    if val=='not active':
        if casuale:
            #devo scegliere il codice a caso
            trovato=False
            while not trovato:
                #Concatena la stringa vuota con quattro lettere scelte a caso tra le lettere maiuscole
                caso=''.join(random.choice(string.ascii_uppercase) for x in range(4))
                #Vedo se quel caso c'e' gia' nel DB e se c'e' ne creo uno nuovo
                listacoll=Collection.objects.filter(itemCode=caso)
                if len(listacoll)==0:
                    trovato=True
        else:
            #conto quante collezioni ci sono per quel tipo di tumore
            collezioni=Collection.objects.filter(idCollectionType=tumore)
            print 'collezioni',collezioni
            if(collezioni.count()==0):
                caso=0
            else:
                lis=[]
                for coll in collezioni:
                    #se l'itemcode e' una serie di lettere non lo metto nella lista di quelli da ordinare
                    if coll.itemCode.isdigit():
                        lis.append(coll)
                #ordino in base all'itemCode    
                listaord=sorted(lis, key=lambda x: int(x.itemCode))
                print 'listaord',listaord
                #prendo l'ultima collezione per quel tipo di tumore
                if len(listaord)!=0:
                    co=listaord[(len(listaord))-1]
                    print 'co',co
                    caso=int(co.itemCode)
                else:
                    caso=0
            caso=caso+1
            #serve a mettere degli zeri davanti al numero del caso per formare il genealogy id
            caso=str(caso).zfill(4)
    else:
        caso=val
    return caso

def isfloat(value):
    try:
        float(value)
        return True
    except ValueError:
        return False
    
#funzioni per la gestione e il salvataggio del file nel repository
def handle_uploaded_file(f, folderDest):
    destination = open(os.path.join(folderDest, f.name), 'wb+')
    for chunk in f.chunks():
        destination.write(chunk)
    destination.close()
    return os.path.join(folderDest, f.name)

# remove files if they are in tmp directory
def remove_uploaded_files(filelist):
    print filelist
    for f in filelist:
        if os.path.split(f)[0] == os.path.split(TEMP_URL)[0]:
            print 'Removing file: ' + str(os.path.split(f)[1])
            os.remove(f)

def uploadRepFile(data, fileLocation):
    print 'uploadRepFile'
    repositoryUrl = Urls.objects.get(idWebService=WebService.objects.get(name='Repository').id)
    print 'repurl',repositoryUrl.url
    r = requests.post(repositoryUrl.url+ '/api.uploadFile', data=data, files={'file': open(fileLocation)}, verify=False)
    print 'r.text',r.text
    response = json.loads(r.text)
    print response
    if response['status'] == 'Ok':
        return response['objectId']
    else:
        return 'Fail'

def getMdamTemplates (templateList):
    mdamUrl = Urls.objects.get(idWebService=WebService.objects.get(name='MDAM').id)
    url = mdamUrl.url + '/api/describetemplate/'
    templates = []
    print 'url',url
    for t in templateList:
        data = urllib.urlencode({'template_id':t})
        print 'data',data
        req = urllib2.Request(url + '?' + data, headers={'workingGroups' : get_WG_string()})
        u = urllib2.urlopen(req)
        res=u.read()
        res=ast.literal_eval(res)
        templates.append(res)
    return templates

#per togliere la condivisione di un'aliquota con il wg di destinazione. Serve nel transfer quando
#si vuole cancellare la condivisione
def togli_condivisione(listatrasf,pianificatore,ricevente):
    try:
        disable_graph()
        #pianificatore e' un oggetto User che rappresenta l'utente che possedeva l'aliq prima della
        #condivisione
        lisuser2=WG_User.objects.filter(user=pianificatore)
        liswgorig=[]
        for item in lisuser2:
            if item.WG.name not in liswgorig:
                #salvo in questa lista il nome dei wg a cui apparteneva l'aliq prima della condivisione
                liswgorig.append(item.WG.name)
        lgenid=[]
        for trasf in listatrasf:
            aliq=trasf.idAliquot
            lgenid.append(aliq.uniqueGenealogyID)
            lisalwg=Aliquot_WG.objects.filter(aliquot=aliq)
            #devo togliere i wg del dest solo se non appartengono anche al pianificatore
            for alwg in lisalwg:
                if alwg.WG.name not in liswgorig:
                    #cancello l'oggetto
                    alwg.delete()
        enable_graph()
        
        #passo la lista dei gen e il nome del destinatario, cosi' so a quale wg togliere la condivisione
        url = Urls.objects.get(idWebService=WebService.objects.get(name='LASAuthServer')).url + "/deleteShareEntities/"
        data={'entitiesList':json.dumps(lgenid),'user':ricevente}
    
        print 'urlLASAUTH',url
        data = urllib.urlencode(data)
        req = urllib2.Request(url,data=data, headers={"workingGroups" : get_WG_string()})
        u = urllib2.urlopen(req)
        res1 =  u.read()
        if res1=='error':
            print "error during delete sharing"
            return 'err'        
        return 'ok'
    except Exception,e:
        print 'err',e
        return 'err'
    
def saveInClinicalModule(lisexist,lisnotexist,wg,operatore,lislocalid):
    try:
        #non posso usare il wg e l'operatore passati alla funzione perche' ogni campione ha il suo salvato nel dizionario
        #faccio la POST al modulo clinico per comunicargli i dati della nuova collezione da collegare al paziente
        servizio=WebService.objects.get(name='Clinical')
        urlclin=Urls.objects.get(idWebService=servizio).url
        lispaz2=[]
        #diz con chiave paziente|consenso e valore tum+caso
        #diztemp={}
        print 'lisexists',lisexist
        print 'lisnotexists',lisnotexist
        print 'lislocalid',lislocalid
        if len(lisnotexist)!=0:
            #devo vedere se nella lista ci sono dei consensi duplicati e se si' li metto nella lista degli esistenti
            listemp=[]
            lisnuova=list(lisnotexist)
            for diz in lisnuova:
                print 'diz',diz
                cons=diz['consenso']
                print 'cons',cons
                if cons not in listemp:
                    listemp.append(cons)
                else:
                    #aggiungo nella lista degli esistenti
                    lisexist.append(diz)
                    #tolgo il dizionario dalla lista originale
                    for dizinterno in lisnotexist:
                        if dizinterno['caso']==diz['caso']:
                            lisnotexist.remove(diz)
                            break
                print 'listemp',listemp
            print 'lisexists dopo',lisexist
            print 'lisnotexists dopo',lisnotexist
            for diz in lisnotexist:
                print 'diz',diz
                coll_genid = padGenid(diz['tum']+diz['caso'])
                print 'coll_genid',coll_genid
                dizio2={'ICcode':diz['consenso'],'project':diz['progetto'],'collection':coll_genid,'medicalCenter':diz['source'],'wg':diz['wg'][0],'operator':diz['operator']}
                #solo se c'e' un paziente aggiungo la chiave nel dizionario
                if 'paziente' in diz:
                    if diz['paziente']!='':
                        dizio2['localId']=diz['paziente']
                #indica che il paziente deve essere creato perche' non esisteva
                if 'newLocalId' in diz:
                    dizio2['newLocalId']=diz['newLocalId']
                lispaz2.append(dizio2)
                #diztemp[diz['progetto']+'|'+diz['consenso']]=diz['tum']+diz['caso']
            print 'lispaz',lispaz2
            val1=json.dumps({'patients':lispaz2})
            url1 = urlclin + '/appEnrollment/api/enrollment/'
            print 'url2',url1
            #data = urllib.urlencode(val1)
            #req = urllib2.Request(url1,data=data, headers={"workingGroups" : get_WG_string()})
            #u = urllib2.urlopen(req)
            #re = json.loads(u.read())
            #print 're',re
            r=requests.post(url1, data=val1, verify=False, headers={'workingGroups' : get_WG_string(),'Content-type': 'application/json'})
            #devo fare il controllo se la POST ha avuto successo
            status=r.status_code
            print 'status',status
            print 'text',r.text
            if status==400:
                return True
            
        if len(lisexist)!=0:
            for diz in lisexist:
                coll_genid = padGenid(diz['tum']+diz['caso'])
                print 'coll_genid',coll_genid
                #la chiave sharings vuole una lista
                valori={'ICcode':diz['consenso'],'project':diz['progetto'],'collection':coll_genid,'sharings':diz['wg']}
                #diztemp[diz['progetto']+'|'+diz['consenso']]=diz['tum']+diz['caso']
                val1=json.dumps(valori)
                url1 = urlclin + '/coreProject/api/informedConsent/'
                print 'url1',url1
                #data = urllib.urlencode(val1)
                #req = urllib2.Request(url1,data=data, headers={"workingGroups" : get_WG_string()})
                #u = urllib2.urlopen(req)
                #re = json.loads(u.read())
                #print 're',re
                r=requests.post(url1, data=val1, verify=False, headers={'workingGroups' : get_WG_string(),'Content-type': 'application/json'})
                #devo fare il controllo se la POST ha avuto successo
                status=r.status_code
                print 'status',status
                print 'text',r.text
                if status==400:
                    return True
        
        #devo fare un'altra POST al modulo clinico al core pazienti passandogli gli uuid dei pazienti e il relativo wg
        #a cui devono essere collegati
        if len(lislocalid)!=0:
            #la chiave sharings vuole una lista
            val1=json.dumps({'sharings':wg})
            for local in lislocalid:                
                url3 = urlclin + '/corePatient/api/patient/'+local+'/'
                print 'url3',url3
                print 'val1',val1
                r=requests.put(url3, data=val1, verify=False, headers={'Content-type': 'application/json'})
                #devo fare il controllo se la PUT ha avuto successo
                status=r.status_code
                print 'status',status
                print 'text',r.text
                if status==400:
                    return True
        
        '''#diz con chiave progetto|consenso e valore l'uid
        dizris=json.loads(re['dictCode'])
        dizfin={}
        for k,v in dizris.items():
            dizfin[diztemp[k]]=v
        #imposto l'uid del nodo del consenso che dovro' recuperare per collegare la collezione al consenso
        set_ICCodeCollection(dizfin)'''
        return False
    except Exception,e:
        print 'err',e
        return True
    
def submitLabelAnalysis(payload):
    annotUrl = Urls.objects.get(idWebService=WebService.objects.get(name='NewAnnotation'))
    url = annotUrl.url + 'newapi/createAnalysis/'
    
    r = requests.post(url, data=json.dumps(payload), headers={'content-type': 'application/json'}, verify=False)

    if r.status_code == '200':
        res=json.loads(r.text)
        print res
        return res['refset_label']
    else:
        print r.status_code, r.text
        raise Exception('BAD REQUEST in label analysis')
    
def submitAnalysis(payload):
    annotUrl = Urls.objects.get(idWebService=WebService.objects.get(name='NewAnnotation'))
    url = annotUrl.url + 'newapi/submitAnalysisResults/'
    r = requests.post(url, data=json.dumps(payload), headers={'content-type': 'application/json'}, verify=False)
    print 'status code',r.status_code
    if r.status_code == '200':
        print r.text
        return
    else:
        print r.status_code, r.text
        raise Exception('BAD REQUEST in submit analysis')
    

#funzione in cui, data una lista di ic e di progetti, ho un dizionario in cui, per ogni ic, ho le sue
#informazioni associate, se esistono
def checkListInformedConsent(liscons):
    try:
        #liscons contiene una serie di stringhe nella forma cons_progetto
        print 'liscons',liscons
        stringacons=''
        lis_pezzi_url=[]
        for val in liscons:
            
            print 'val prima',val
            cc=val.split('_')
            cons=cc[0]
            for jj in range(1,(len(cc)-1)):
                cons+='_'+cc[jj]
            cons+='|'+cc[len(cc)-1]
            print 'cons dopo',cons
            
            stringacons+=cons+','
            #2000 e' il numero di caratteri scelto per fare in modo che la url
            #della api non sia troppo lunga
            if len(stringacons)>2000:
                #cancello la virgola alla fine della stringa
                strbarc=stringacons[:-1]
                print 'strbarc',strbarc
                lis_pezzi_url.append(strbarc)
                stringacons=''
        #cancello la virgola alla fine della stringa
        strbarc=stringacons[:-1]
        print 'strbarc',strbarc
        if strbarc!='':
            lis_pezzi_url.append(strbarc)
        
        diz_tot={}
        if len(lis_pezzi_url)!=0:
            servizio=WebService.objects.get(name='Clinical')
            urlclin=Urls.objects.get(idWebService=servizio).url
            for elementi in lis_pezzi_url:
                print 'elementi',elementi
                req = urllib2.Request(urlclin+"/coreProject/api/icBatch/?list="+elementi, headers={"workingGroups" : get_WG_string()})
                u = urllib2.urlopen(req)
                data = json.loads(u.read())
                print 'data',data
                for k,val in data.items():
                    cc=k.split('|')
                    knuovo=cc[0]+'_'+cc[1]
                    diz_tot[knuovo]=val
        print 'diz_tot',diz_tot
        return diz_tot
    except Exception,e:
        print 'err',e
        return {}

#creo un dizionario con la struttura del genid
def getGenealogyDict():
    ftype={'Predefined list':1,'Alphabetic':2,'Numeric':3,'Alphanumeric':4}
    listum=list(CollectionType.objects.all().order_by('abbreviation').values_list('abbreviation',flat=True))
    listess=list(TissueType.objects.all().order_by('abbreviation').values_list('abbreviation',flat=True))
    lisvector=list(AliquotVector.objects.all().order_by('abbreviation').values_list('abbreviation',flat=True))    
    lismousetissue=list(MouseTissueType.objects.all().order_by('abbreviation').values_list('abbreviation',flat=True))
    listipialiq=list(AliquotType.objects.all().order_by('abbreviation').exclude(type='Derived').values_list('abbreviation',flat=True))
    lisderivati=['D','R','P']
    lisderivati2=['D','R']
    
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
    
    return diztot

class SchemiPiastre():  
    def table_extern(self):
        page=markup.page()
        page.table(id='rna')
        page.th(colspan=10)
        page.add('')
        page.th.close()
        page.tr()
        page.td()
        page.td.close()
        for i in range(1,10):
            page.td(align='center')
            page.strong(i)
            page.td.close()
        page.tr.close()
        for i in range (1,10):
            page.tr()
            page.td()
            page.br()
            page.strong(str(i).translate(trasftab))
            page.td.close()
            for j in range(1,10):
                page.td()
                page.button(type='submit', id='r-'+str(i).translate(trasftab)+str(j))
                #page.add(str(0))
                page.button.close()
                page.td.close()
            page.tr.close()
        page.table.close()
        return page
    
    def table_vital(self):
        page=markup.page()
        page.table(id='vital',align='center')
        page.th(colspan=7)
        page.add('VIABLE')
        page.th.close()
        page.tr()
        page.td()
        page.td.close()
        for i in range(1,7):
            page.td(align='center')
            page.strong(i)
            page.td.close()
        page.tr.close()
        for i in range (1,5):
            page.tr()
            page.td()
            page.br()
            page.strong(str(i).translate(trasftab))
            page.td.close()
            for j in range(1,7):
                page.td()
                page.button(type='submit', id='v-'+str(i).translate(trasftab)+str(j))
                #page.add(str(0))
                page.button.close()
                page.td.close()
            page.tr.close()
        page.table.close()
        return page
    def table_rna(self):
        page=markup.page()
        page.table(id='rna')
        page.th(colspan=13)
        page.add('RNA LATER')
        page.th.close()
        page.tr()
        page.td()
        page.td.close()
        for i in range(1,13):
            page.td(align='center')
            page.strong(i)
            page.td.close()
        page.tr.close()
        for i in range (1,9):
            page.tr()
            page.td()
            page.br()
            page.strong(str(i).translate(trasftab))
            page.td.close()
            for j in range(1,13):
                page.td()
                page.button(type='submit', id='r-'+str(i).translate(trasftab)+str(j))
                #page.add(str(0))
                page.button.close()
                page.td.close()
            page.tr.close()
        page.table.close()
        return page
    def table_ffpe(self):
        page=markup.page()
        page.table(align='center',id='ffpe')
        page.th(colspan=6)
        page.add('FFPE')
        page.th.close()
        
        for i in range (1,5):
            page.tr()
            page.td()
            page.br()
            page.strong(i)
            page.td.close()
            page.td()
            page.button(type='submit', id='f-'+str(i))
            page.button.close()
            page.td.close()
            page.td()
            page.label('Barcode:')
            page.label.close()
            page.input(type='text', id='inputf'+str(i),maxlength=45,size=15)
            page.td()
            page.br()
            page.strong(i+4)
            page.td.close()
            page.td()
            page.button(type='submit', id='f-'+str(i+4))
            page.button.close()
            page.td.close()
            page.td()
            page.label('Barcode:')
            page.label.close()
            page.input(type='text', id='inputf'+str(i+4),maxlength=45,size=15)
            page.tr.close()
        page.table.close()
        return page
    def table_sf(self):
        page=markup.page()
        page.table(id='sf')
        page.th(colspan=13)
        page.add('SNAP FROZEN')
        page.th.close()
        page.tr()
        page.td()
        page.td.close()
        for i in range(1,13):
            page.td(align='center')
            page.strong(i)
            page.td.close()
        page.tr.close()
        for i in range (1,9):
            page.tr()
            page.td()
            page.br()
            page.strong(str(i).translate(trasftab))
            page.td.close()
            for j in range(1,13):
                page.td()
                page.button(type='submit', id='s-'+str(i).translate(trasftab)+str(j))
                #page.add(str(0))
                page.button.close()
                page.td.close()
            page.tr.close()
        page.table.close()
        return page
    
    def table_tubes(self):
        page = markup.page()
        page.table(align='center',id='tubes')

        page.th()
        page.td()
        page.td.close()
        page.td()
        page.td.close()
        page.td("Last inserted aliquot: ")
        page.td.close()
        
        page.tr()
        page.td()
        page.strong('FFPE: ')
        page.td.close()
        page.td()
        page.button(type='submit', id='f-0')
        page.button.close()
        page.td.close()
        page.td(style='padding-left:2em;')
        page.label('Barcode:')
        page.label.close()
        page.input(type='text', id='inputf0',maxlength=45, size=8)
        page.td.close()
        page.td()
        page.p("-", id = 'f-output', align='center' )
        page.td.close()
        page.tr.close()
        
        page.tr()
        page.td()
        page.strong('OCT: ')
        page.td.close()
        page.td()
        page.button(type='submit', id='o-0')
        page.button.close()
        page.td.close()
        page.td(style='padding-left:2em;')
        page.label('Barcode:')
        page.label.close()
        page.input(type='text', id='inputo0',maxlength=45, size='8')
        page.td.close()
        page.td()
        page.p("-", id = 'o-output', align='center' )
        page.td.close()
        page.tr.close()

        page.tr()
        page.td()
        page.strong('CB: ')
        page.td.close()
        page.td()
        page.button(type='submit', id='c-0')
        page.button.close()
        page.td.close()
        page.td(style='padding-left:2em;')
        page.label('Barcode:')
        page.label.close()
        page.input(type='text', id='inputc0',maxlength=45, size='8')
        page.td.close()
        page.td()
        page.p("-", id = 'c-output', align='center' )
        page.td.close()
        page.tr.close()

        page.table.close()
        return page
    def table_blood(self):
        page = markup.page()
        page.table(align='center',id='tab_blood')

        page.tr()
        page.td()
        page.td.close()
        page.td()
        page.td.close()
        page.td()
        page.td.close()
        page.td()
        page.td.close()
        page.td()
        page.td.close()
        page.td()
        page.td.close()
        page.td("Last inserted aliquot: ",style='padding-bottom:1.5em;')
        page.td.close()
        page.tr.close()
        
        page.tr()
        page.td()
        page.strong('Plasma: ')
        page.td.close()
        page.td()
        page.button(type='submit', id='plas')
        page.button.close()
        page.td.close()
        page.td(style='padding-left:2em;')
        page.label('Barcode:')
        page.label.close()
        page.input(type='text', id='barcplas',maxlength=45, size=8)
        page.td.close()
        page.td(style='font-size:15px;padding-left:1em;')
        page.input(type='radio', name='cho_PL', value='tube', style='display:inline;')
        page.span(style='display:inline;')
        page.add('Tube')
        page.span.close()
        page.input(type='radio', name='cho_PL', value='plate', style='display:inline;')
        page.span(style='display:inline;')
        page.add('Plate')
        page.span.close()
        page.td.close()
        page.td(style='padding-left:2em;')
        page.label('Volume(ml):')
        page.label.close()
        page.input(type='text', id='volplas',maxlength=10, size=6)
        page.td.close()
        page.td()
        page.td.close()
        page.td()
        page.p("-", id = 'plasoutput', align='center' )
        page.td.close()
        page.tr.close()
        
        page.tr()
        page.td()
        page.strong('Whole blood: ')
        page.td.close()
        page.td()
        page.button(type='submit', id='who')
        page.button.close()
        page.td.close()
        page.td(style='padding-left:2em;')
        page.label('Barcode:')
        page.label.close()
        page.input(type='text', id='barcwho',maxlength=45, size='8')
        page.td.close()
        page.td(style='font-size:15px;padding-left:1em;')
        page.input(type='radio', name='cho_SF', value='tube', style='display:inline;')
        page.span(style='display:inline;')
        page.add('Tube')
        page.span.close()
        page.input(type='radio', name='cho_SF', value='plate', style='display:inline;')
        page.span(style='display:inline;')
        page.add('Plate')
        page.span.close()
        page.td.close()
        page.td(style='padding-left:2em;')
        page.label('Volume(ml):')
        page.label.close()
        page.input(type='text', id='volwho',maxlength=10, size=6)
        page.td.close()
        page.td()
        page.td.close()
        page.td()
        page.p("-", id = 'whooutput', align='center' )
        page.td.close()
        page.tr.close()

        page.tr()
        page.td()
        page.strong('PAX tube: ')
        page.td.close()
        page.td()
        page.button(type='submit', id='pax')
        page.button.close()
        page.td.close()
        page.td(style='padding-left:2em;')
        page.label('Barcode:')
        page.label.close()
        page.input(type='text', id='barcpax',maxlength=45, size='8')
        page.td.close()
        page.td(style='font-size:15px;padding-left:1em;')
        page.input(type='radio', name='cho_PX', value='tube', style='display:inline;')
        page.span(style='display:inline;')
        page.add('Tube')
        page.span.close()
        page.input(type='radio', name='cho_PX', value='plate', style='display:inline;')
        page.span(style='display:inline;')
        page.add('Plate')
        page.span.close()
        page.td.close()
        page.td(style='padding-left:2em;')
        page.label('Volume(ml):')
        page.label.close()
        page.input(type='text', id='volpax',maxlength=10, size=6)
        page.td.close()
        page.td()       
        page.td.close()
        page.td()
        page.p("-", id = 'paxoutput', align='center' )
        page.td.close()
        page.tr.close()
        
        page.tr()
        page.td()
        page.strong('PBMC: ')
        page.td.close()
        page.td()
        page.button(type='submit', id='pbmc')
        page.button.close()
        page.td.close()
        page.td(style='padding-left:2em;')
        page.label('Barcode:')
        page.label.close()
        page.input(type='text', id='barcpbmc',maxlength=45, size='8')
        page.td.close()
        page.td(style='font-size:15px;padding-left:1em;')
        page.input(type='radio', name='cho_VT', value='tube', style='display:inline;')
        page.span(style='display:inline;')
        page.add('Tube')
        page.span.close()
        page.input(type='radio', name='cho_VT', value='plate', style='display:inline;')
        page.span(style='display:inline;')
        page.add('Plate')
        page.span.close()
        page.td.close()
        page.td(style='padding-left:2em;')
        page.label('Volume(ml):')
        page.label.close()
        page.input(type='text', id='volpbmc',maxlength=10, size=6)
        page.td.close()
        page.td(style='padding-left:2em;')
        page.label('Count(cell/ml):')
        page.label.close()
        page.input(type='text', id='contapbmc',maxlength=10, size=6)
        page.td.close()
        page.td()
        page.p("-", id = 'pbmcoutput', align='center' )
        page.td.close()
        page.tr.close()

        page.table.close()
        return page
    
    def table_urine(self):
        page = markup.page()
        page.table(align='center',id='tab_uri')

        page.tr()
        page.td()
        page.td.close()
        page.td()
        page.td.close()
        page.td()
        page.td.close()
        page.td()
        page.td.close()
        page.td()
        page.td.close()
        page.td()
        page.td.close()
        page.td("Last inserted aliquot: ",style='padding-bottom:1.5em;')
        page.td.close()
        page.tr.close()
        
        page.tr()
        page.td()
        page.strong('Frozen: ')
        page.td.close()
        page.td()
        page.button(type='submit', id='uri')
        page.button.close()
        page.td.close()
        page.td(style='padding-left:2em;')
        page.label('Barcode:')
        page.label.close()
        page.input(type='text', id='barcuri',maxlength=45, size=8)
        page.td.close()
        page.td(style='font-size:15px;padding-left:1em;')
        page.input(type='radio', name='cho_FR', value='tube', style='display:inline;')
        page.span(style='display:inline;')
        page.add('Tube')
        page.span.close()
        page.input(type='radio', name='cho_FR', value='plate', style='display:inline;')
        page.span(style='display:inline;')
        page.add('Plate')
        page.span.close()
        page.td.close()
        page.td(style='padding-left:2em;')
        page.label('Volume(ml):')
        page.label.close()
        page.input(type='text', id='voluri',maxlength=10, size=6)
        page.td.close()
        page.td()
        page.td.close()
        page.td()
        page.p("-", id = 'urioutput', align='center' )
        page.td.close()
        page.tr.close()
        
        page.tr()
        page.td()
        page.strong('Frozen Sediments: ')
        page.td.close()
        page.td()
        page.button(type='submit', id='sedim')
        page.button.close()
        page.td.close()
        page.td(style='padding-left:2em;')
        page.label('Barcode:')
        page.label.close()
        page.input(type='text', id='barcsedim',maxlength=45, size=8)
        page.td.close()
        page.td(style='font-size:15px;padding-left:1em;')
        page.input(type='radio', name='cho_FS', value='tube', style='display:inline;')
        page.span(style='display:inline;')
        page.add('Tube')
        page.span.close()
        page.input(type='radio', name='cho_FS', value='plate', style='display:inline;')
        page.span(style='display:inline;')
        page.add('Plate')
        page.span.close()
        page.td.close()
        page.td(style='padding-left:2em;')
        page.label('Volume(ml):')
        page.label.close()
        page.input(type='text', id='volsedim',maxlength=10, size=6)
        page.td.close()
        page.td()
        page.td.close()
        page.td()
        page.p("-", id = 'sedimoutput', align='center' )
        page.td.close()
        page.tr.close()
        
        page.table.close()
        return page
    
#per cancellare i dati dalla sessione
def CancSession(request):
    if request.session.has_key('coll'):
        del request.session['coll']
    if request.session.has_key('codPazienteCollezione'):
        del request.session['codPazienteCollezione']
    if request.session.has_key('collEventCollezione'):
        del request.session['collEventCollezione']
    if request.session.has_key('codPazienteCollezioneEsterna'):
        del request.session['codPazienteCollezioneEsterna']
    if request.session.has_key('collEventCollezioneEsterna'):
        del request.session['collEventCollezioneEsterna']
    if request.session.has_key('aliquots'):
        del request.session['aliquots']
    if request.session.has_key('plate'):
        del request.session['plate']
    if request.session.has_key('lista_aliquote_der'):
        del request.session['lista_aliquote_der']
    if request.session.has_key('tipoderivatoprodotto'):
        del request.session['tipoderivatoprodotto']
    if request.session.has_key('listaaliquote'):
        del request.session['listaaliquote']
    if request.session.has_key('listastorage'):
        del request.session['listastorage']   
    if request.session.has_key('listafeature'):
        del request.session['listafeature']
    if request.session.has_key('tessutisalvare'):
        del request.session['tessutisalvare']
    if request.session.has_key('genealogyMeasureView'):
        del request.session['genealogyMeasureView']
    if request.session.has_key('listaGenMisure'):
        del request.session['listaGenMisure']   
    if request.session.has_key('revaluedmeasure'):
        del request.session['revaluedmeasure']
    if request.session.has_key('listaValAliqDer'):
        del request.session['listaValAliqDer']
    if request.session.has_key('ProtQualMeasureAll'):
        del request.session['ProtQualMeasureAll']
    if request.session.has_key('GenealogyIdMeasureAll'):
        del request.session['GenealogyIdMeasureAll']
    if request.session.has_key('ListaGenMeasureAllRevaluate'):
        del request.session['ListaGenMeasureAllRevaluate']
    if request.session.has_key('ListaGenealogyMeasureAll'):
        del request.session['ListaGenealogyMeasureAll']
    if request.session.has_key('listaValAliqSplit'):
        del request.session['listaValAliqSplit']
    if request.session.has_key('listapiastrealiqderivate'):
        del request.session['listapiastrealiqderivate']
    if request.session.has_key('indice'):
        del request.session['indice']
    if request.session.has_key('dictaliqderivate'):
        del request.session['dictaliqderivate']
    if request.session.has_key('derivedmeasure'):
        del request.session['derivedmeasure']
    if request.session.has_key('rivalutare'):
        del request.session['rivalutare']
    if request.session.has_key('derivare'):
        del request.session['derivare']
    if request.session.has_key('posizionare'):
        del request.session['posizionare']
    if request.session.has_key('dividere'):
        del request.session['dividere']
    if request.session.has_key('data_collezionamento'):
        del request.session['data_collezionamento']
    if request.session.has_key('operatore_collezionamento'):
        del request.session['operatore_collezionamento']
    if request.session.has_key('data_collezionamento_esterno'):
        del request.session['data_collezionamento_esterno']
    if request.session.has_key('operatore_collezionamento_esterno'):
        del request.session['operatore_collezionamento_esterno']
    if request.session.has_key('data_derivazione'):
        del request.session['data_derivazione']
    if request.session.has_key('operatore_derivazione'):
        del request.session['operatore_derivazione']
    if request.session.has_key('data_posizionamento'):
        del request.session['data_posizionamento']
    if request.session.has_key('operatore_posizionamento'):
        del request.session['operatore_posizionamento']
    if request.session.has_key('data_split'):
        del request.session['data_split']
    if request.session.has_key('operatore_split'):
        del request.session['operatore_split']
    if request.session.has_key('listarev_canc'):
        del request.session['listarev_canc']
    if request.session.has_key('listasplit_canc'):
        del request.session['listasplit_canc']
    if request.session.has_key('listavit_canc'):
        del request.session['listavit_canc']
    if request.session.has_key('listaexperiment_canc'):
        del request.session['listaexperiment_canc']       
    if request.session.has_key('campo_riv_misure'):
        del request.session['campo_riv_misure']
    if request.session.has_key('lisValPositionReport'):
        del request.session['lisValPositionReport']
    if request.session.has_key('listaaliqpatientpdf'):
        del request.session['listaaliqpatientpdf']
    if request.session.has_key('listacolonnepatientpdf'):
        del request.session['listacolonnepatientpdf']
    if request.session.has_key('dizclinicalparameter'):
        del request.session['dizclinicalparameter']
    if request.session.has_key('aliquotEsterne'):
        del request.session['aliquotEsterne']
    if request.session.has_key('aliqTrasferire'):
        del request.session['aliqTrasferire']
    if request.session.has_key('listaaliqtrasferire'):
        del request.session['listaaliqtrasferire']
    if request.session.has_key('noteretrieve'):
        del request.session['noteretrieve']
    if request.session.has_key('exectransfer'):
        del request.session['exectransfer']
    if request.session.has_key('dattransfer'):
        del request.session['dattransfer']
    if request.session.has_key('addrtransfer'):
        del request.session['addrtransfer']
    if request.session.has_key('aliqDerivare'):
        del request.session['aliqDerivare']
    if request.session.has_key('risderivare'):
        del request.session['risderivare']
    if request.session.has_key('operderivare'):
        del request.session['operderivare']
    if request.session.has_key('aliqesperimenti'):
        del request.session['aliqesperimenti']
    if request.session.has_key('genealogyesperimenti'):
        del request.session['genealogyesperimenti']
    if request.session.has_key('datesperim'):
        del request.session['datesperim']
    if request.session.has_key('expesperim'):
        del request.session['expesperim']
    if request.session.has_key('operatesperim'):
        del request.session['operatesperim']
    if request.session.has_key('noteesperim'):
        del request.session['noteesperim']
    if request.session.has_key('rivalutareconvalidate'):
        del request.session['rivalutareconvalidate']
    if request.session.has_key('listaBatchCollection'):
        del request.session['listaBatchCollection']
    if request.session.has_key('aliquotCollectionBatch'):
        del request.session['aliquotCollectionBatch']
    if request.session.has_key('cellLineNuove'):
        del request.session['cellLineNuove']
    if request.session.has_key('dizinfoaliqsplit'):
        del request.session['dizinfoaliqsplit']
    if request.session.has_key('dizinfoaliqderivare'):
        del request.session['dizinfoaliqderivare']
    if request.session.has_key('dizinfoaliqrivalutare'):
        del request.session['dizinfoaliqrivalutare']
    if request.session.has_key('prepvetrini'):
        del request.session['prepvetrini']
    if request.session.has_key('noteslide'):
        del request.session['noteslide']
    if request.session.has_key('listaaliqvetrini'):
        del request.session['listaaliqvetrini']
    if request.session.has_key('dizinfoaliqvetrini'):
        del request.session['dizinfoaliqvetrini']
    if request.session.has_key('aliquotevetrini'):
        del request.session['aliquotevetrini']
    if request.session.has_key('indice_vetrini'):
        del request.session['indice_vetrini']
    if request.session.has_key('lista_aliquote_vetrini'):
        del request.session['lista_aliquote_vetrini']
    if request.session.has_key('listaValAliqSlide'):
        del request.session['listaValAliqSlide']
    if request.session.has_key('dictaliqvetrini'):
        del request.session['dictaliqvetrini']
    if request.session.has_key('data_slide'):
        del request.session['data_slide']
    if request.session.has_key('operatore_slide'):
        del request.session['operatore_slide']
    if request.session.has_key('notederived'):
        del request.session['notederived']
    if request.session.has_key('unitaconcderivati'):
        del request.session['unitaconcderivati']
    if request.session.has_key('dizionarioderivaticambiati'):
        del request.session['dizionarioderivaticambiati']
    if request.session.has_key('workgrBatchCollection'):
        del request.session['workgrBatchCollection']
    if request.session.has_key('clinicalparamreopencollection'):
        del request.session['clinicalparamreopencollection']
    if request.session.has_key('clinicalParameterModifiedCollection'):
        del request.session['clinicalParameterModifiedCollection']
    if request.session.has_key('FinalReceiveValidatedAliquots'):
        del request.session['FinalReceiveValidatedAliquots']
    if request.session.has_key('workgesperim'):
        del request.session['workgesperim']
    if request.session.has_key('aliquotCollectionMercuric'):
        del request.session['aliquotCollectionMercuric']
    if request.session.has_key('aliquotCollectionFunnel'):
        del request.session['aliquotCollectionFunnel']
    if request.session.has_key('dizmoduloclinico'):
        del request.session['dizmoduloclinico']
    if request.session.has_key('listafinalederivazionereport'):
        del request.session['listafinalederivazionereport']
    if request.session.has_key('listafinaleslidereport'):
        del request.session['listafinaleslidereport']
    if request.session.has_key('listafinaletransferreport'):
        del request.session['listafinaletransferreport']
    if request.session.has_key('listafinalecollectionbatchreport'):
        del request.session['listafinalecollectionbatchreport']
    if request.session.has_key('vetrinilabelprog'):
        del request.session['vetrinilabelprog']
    if request.session.has_key('opervetrinilabel'):
        del request.session['opervetrinilabel']
    if request.session.has_key('notevetrinilabel'):
        del request.session['notevetrinilabel']
    if request.session.has_key('listafinalelabelreport'):
        del request.session['listafinalelabelreport']
    if request.session.has_key('listalabeldacanc'):
        del request.session['listalabeldacanc']
    if request.session.has_key('listaaliqlabel'):
        del request.session['listaaliqlabel']
    if request.session.has_key('listaMarkerProtocollo'):
        del request.session['listaMarkerProtocollo']
    if request.session.has_key('lisFinalLabelAliquot'):
        del request.session['lisFinalLabelAliquot']
    if request.session.has_key('lisFinalNewAliquotLabel'):
        del request.session['lisFinalNewAliquotLabel']
    if request.session.has_key('listafinalesalvafile'):
        del request.session['listafinalesalvafile']
    if request.session.has_key('listaLabelSaveResult'):
        del request.session['listaLabelSaveResult']
    if request.session.has_key('dizaliqderivaterobot'):
        del request.session['dizaliqderivaterobot']
    if request.session.has_key('dizremainderivedrobot'):
        del request.session['dizremainderivedrobot']
            
