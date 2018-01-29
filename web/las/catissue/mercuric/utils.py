from catissue.tissue.models import *
from catissue.tissue.genealogyID import *
from mercuric.forms import *
from django.db import transaction
from django.db.models import Q
from django.template.context import RequestContext
from django.shortcuts import render_to_response
from django.http import HttpResponse
import string,urllib,urllib2,json,requests,random
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from global_request_middleware import *

from django.conf import settings
import os.path

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
    listaaliq=''
    listatipialiq=[]
    errore=False
    for i in range(0,len(listaaliquota)):
        val=listaaliquota[i].split(',')
        if val[6]=='false':
            #in val[4] c'e' il barcode della provetta
            listaaliq=listaaliq+val[4]+'&'
            listatipialiq.append(val[5])
        else:
            #in val[5] c'e' il tipo dell'aliq (VT,SF...)
            listaffpe=listaffpe+val[4]+','+val[5]+','+val[0]+'&'
    print 'listaaliq',listaaliq
    print 'listaffpeeeee',listaffpe
    #per salvare in rna,snap o vitale
    url1 = Urls.objects.get(default = '1').url + "/archive/full/"
    val1={'lista':json.dumps(listaaliq),'tube':'full','tipo':listatipialiq}
    
    try:
        if len(listaaliq)!=0:
            print 'url1',url1
            data = urllib.urlencode(val1)
            req = urllib2.Request(url1,data=data, headers={"workingGroups" : get_WG_string()})
            u = urllib2.urlopen(req)
            #u = urllib2.urlopen(url1, data)
            res1 =  u.read()
        else:
            res1='ok'
        if len(listaffpe)!=0:
            #per salvare in ffpe,of o ch
            url2 = Urls.objects.get(default = '1').url + "/archive/saveFFPE/"
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
        return render_to_response('tissue2/index.html',variables)
        print e
    if (res1 == 'err')or(len(listaffpe)!=0 and res2=='err'):
        print 'errore'
        #transaction.rollback()
        errore=True
        return request,errore
    return request,errore

#per gestire la parte di creazione del resoconto finale della collezione
def LastPartCollection(listaaliq):
    lista=[]
    for i in range(0,len(listaaliq)):
        info=listaaliq[i].split(',')
        lista.append(ReportToHtml([i+1,info[8],info[9],info[10],info[4],info[7]]))
    intest='<th>N</th><th>Place</th><th>Date</th><th>Patient code</th><th>Barcode</th><th>Volume(ml)</th>'
    
    print 'lista',lista
    print 'intest',intest
    return lista,intest

#per gestire la parte di creazione del resoconto finale delle aliquote esterne
def LastPartExternAliquot(request,pdf):
    lista=[]
    if request.session.has_key('aliquotEsterne'):
        listaaliq=request.session.get('aliquotEsterne')
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
            lista.append(ReportCollectionToHtml(i+1,info[0],info[3],info[4],info[1],info[2],pdf))
            listacsv.append(str(i+1)+";"+str(info[0])+";"+str(info[3])+";"+info[4]+";"+info[1]+";"+info[2])
        if pdf=='n':
            intest='<th>N</th><th>GenealogyID</th><th>N. of pieces</th><th>Barcode</th><th>Plate</th><th>Position</th>'
        else:
            intest='<th align = \'center\'  width="3%"><strong><br>N</strong></th><th align = \'center\'><strong><br>GenealogyID</strong></th><th align = \'center\'  width="5%"><strong><br>N. of pieces</strong></th><th align = \'center\'><strong><br>Barcode</strong></th><th align = \'center\'><strong><br>Plate</strong></th><th align = \'center\' width="4%"><strong><br>Pos</strong></th>'
        intestcsv.append('N;GenealogyID;Number of pieces;Barcode;Plate;Position')
        
    elif deriv==True:
        for i in range(0,len(listaaliq)):
            info=listaaliq[i].split(',')
            lista.append(ReportExternCollectionToHtml(i+1,info[0],info[4],info[7],info[8],info[9],info[10],info[11],pdf))
            voll=str(info[7]).replace('.',',')
            conc=str(info[8]).replace('.',',')
            pur1=str(info[9]).replace('.',',')
            pur2=str(info[10]).replace('.',',')
            ge=str(info[11]).replace('.',',')
            listacsv.append(str(i+1)+"\t"+str(info[0])+"\t"+str(info[4])+"\t"+voll+"\t"+conc+"\t"+pur1+"\t"+pur2+"\t"+ge)
        if pdf=='n':
            intest='<th>N</th><th>GenealogyID</th><th>Barcode</th><th>Volume(ml)</th><th>Conc. (ng/ul)</th><th>Purity (260/280)</th><th>Purity (260/230)</th><th>GE/Vex (GE/ml)</th>'
        else:
            intest='<th align = \'center\'  width="3%"><strong><br>N</strong></th><th align = \'center\'><strong><br>GenealogyID</strong></th><th align = \'center\'><strong><br>Barcode</strong></th><th align = \'center\' width="9%"><strong><br>Volume(ml)</strong></th><th align = \'center\' width="9%"><strong><br>Conc. (ng/ul)</strong></th>\
            <th align = \'center\' width="9%"><strong><br>Purity (260/280)</strong></th><th align = \'center\' width="9%"><strong><br>Purity (260/230)</strong></th><th align = \'center\' width="9%"><strong><br>GE/Vex (GE/ml)</strong></th>'
        intestcsv.append('N\tGenealogyID\tBarcode\tVolume(ml)\tConc. (ng/ul)\tPurity (260/280)\tPurity (260/230)\tGE/Vex (GE/ml)')
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
            intest='<th>N</th><th>GenealogyID</th><th>Barcode</th><th>Volume(ml)</th><th>Count(cell/ml)</th>'
        else:
            intest='<th align = \'center\'  width="3%"><strong><br>N</strong></th><th align = \'center\'><strong><br>GenealogyID</strong></th><th align = \'center\'><strong><br>Barcode</strong></th><th align = \'center\'><strong><br>Volume(ml)</strong></th><th align = \'center\'><strong><br>Count(cell/ml)</strong></th>'
        
    elif deriv==True:
        for i in range(0,len(listaaliq)):
            info=listaaliq[i].split(',')
            lista.append(ReportToHtml([i+1,info[0],info[4],info[7],info[8],info[9]]))
        if pdf=='n':
            intest='<th>N</th><th>GenealogyID</th><th>Barcode</th><th>Volume(ml)</th><th>Conc. (ng/ul)</th><th>Count(cell/ml)</th>'
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
def LastPartDerivation(request,pdf):
    name=request.user.username
    lista=[]
    intest=''
    intcsv=''
    listacsv=[]
    intestcsv=[]
    diz={}
    dizsupervisori={}
    if request.session.has_key('listaValAliqDer'):
        listaaliq=request.session.get('listaValAliqDer')
    print 'listaaliq',listaaliq

    data=request.session.get('data_derivazione')
    operatore=request.session.get('operatore_derivazione')
    listamisure=[]
    #devo prendere tutte le misure fatte
    for i in range(0,len(listaaliq)):
        info=listaaliq[i].split('&')
        print 'info',info[0]
        #in info[0] ho il genid dell'aliquota derivata creata
        disable_graph()
        aliquot=Aliquot.objects.get(uniqueGenealogyID=info[0])
        enable_graph()
        print 'aliq',aliquot
        alder=DerivationEvent.objects.get(idSamplingEvent=aliquot.idSamplingEvent,derivationDate=data,operator=operatore)
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
        
        if assegnatario.email !='' and assegnatario.username!=name:
            if dizsupervisori.has_key(assegnatario.email):
                listat=dizsupervisori[assegnatario.email]
                listat.append(aliquot)
                dizsupervisori[assegnatario.email]=listat
            else:
                listatemp=[]
                listatemp.append(aliquot)
                dizsupervisori[assegnatario.email]=listatemp
                
    if pdf=='n':
        intest=intest+'<th>N</th><th>GenID</th><th>Barcode</th><th>Plate</th><th>Position</th><th>Conc(ng/ul)</th><th>Vol(ul)</th>'
    else:
        intest='<th align = \'center\' width="3%"><strong><br>N</strong></th><th align = \'center\'><strong><br>GenID</strong></th><th align = \'center\' width="9%"><strong><br>Barcode</strong></th><th align = \'center\'><strong><br>Plate</strong></th><th align = \'center\' width="4%"><strong><br>Pos</strong></th><th align = \'center\' width="6%"><strong><br>Conc (ng/uL)</strong></th><th align = \'center\' width="6%"><strong><br>Vol (uL)</strong></th>'
    intcsv=intcsv+'N\tGenID\tBarcode\tPlate\tPosition\tConc(ng/uL)\tVol(uL)'
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
            valparziali=ReportDerivationToHtml(i+1,s[0],s[1],s[2],s[3],s[4],s[5],'n')
        else:
            valparziali=ReportDerivationToHtml(i+1,s[0],s[1],s[2],s[3],s[4],s[5],'s')
        conc=str(s[4]).replace('.',',')
        vol=str(s[5]).replace('.',',')
        valcsv=str(i+1)+"\t"+str(s[0])+"\t"+str(s[1])+"\t"+s[2]+"\t"+s[3]+"\t"+conc+"\t"+vol
        
        listamisaliq=diz[s[0]]
        #scandisco le misure generali presenti n questa sessione
        for mis in listamisure:
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
            valcsv=valcsv+"\t"+valvirgola
        valparziali=valparziali+'</tr>'     
        lista.append(valparziali)
        listacsv.append(valcsv)
    print 'lista',lista
    print 'intest',intest
    print 'listacsv',listacsv
    return lista,intest,listacsv,intestcsv,dizsupervisori

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
        lista.append(ReportPositionToHtml(i+1,info[0],info[1],info[2],info[3],info[4],pdf))
        listacsv.append(str(i+1)+"\t"+str(info[0])+"\t"+str(info[1])+"\t"+info[2]+"\t"+info[3]+"\t"+info[4])
    if pdf=='n':
        intest='<th>N</th><th>GenealogyID</th><th>Old barcode</th><th>Current barcode</th><th>Container</th><th>Position</th>'
    else:
        intest='<th align = \'center\' width="3%"><strong><br>N</strong></th><th align = \'center\'><strong><br>GenealogyID</strong></th><th align = \'center\'><strong><br>Old barcode</strong></th><th align = \'center\'><strong><br>Current barcode</strong></th><th align = \'center\'><strong><br>Container</strong></th><th align = \'center\' width="4%"><strong><br>Pos</strong></th>'
    intestcsv.append('N\tGenealogyID\tOld barcode\tCurrent barcode\tContainer\tPosition')
    
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

#per gestire la parte finale del posizionamento sulla piastra vitale
def LastPartTransfer(request,pdf,diction):
    lista=[]
    if request.session.has_key('listaaliqtrasferire'):
        listaaliq=request.session.get('listaaliqtrasferire')
    print 'listaaliq',listaaliq
    
    listacsv=[]
    intestcsv=[]
    for i in range(0,len(listaaliq)):
        al=listaaliq[i]
        vol=''
        volfin=''
        #devo vedere se il campione ha un volume
        if al.idAliquot.derived==1:
            lisfeatvol=Feature.objects.filter(Q(name='Volume')&Q(idAliquotType=al.idAliquot.idAliquotType)&Q(measureUnit='ul'))
            if len(lisfeatvol)!=0:
                lisaliqfeat=AliquotFeature.objects.filter(Q(idFeature=lisfeatvol[0])&Q(idAliquot=al.idAliquot))
                if len(lisaliqfeat)!=0:
                    vol=str(lisaliqfeat[0].value)
                    volfin=str(vol).replace('.',',')
                    
        valori=diction[al.idAliquot.uniqueGenealogyID]
        val=valori[0].split('|')
        barc=val[1]
        pos=val[2]
        print 'valori',valori
        lista.append(ReportTransferToHtml(i+1,al.idAliquot.uniqueGenealogyID,barc,pos,vol,pdf))
        listacsv.append(str(i+1)+"\t"+str(al.idAliquot.uniqueGenealogyID)+"\t"+str(barc)+"\t"+volfin)
    if pdf=='n':
        intest='<th>N</th><th>GenealogyID</th><th>Barcode</th><th>Position</th><th>Volume(ul)</th>'
    else:
        intest='<th align = \'center\' width="3%"><strong><br>N</strong></th><th align = \'center\'><strong><br>GenealogyID</strong></th><th align = \'center\'><strong><br>Barcode</strong></th><th align = \'center\'><strong><br>Position</strong></th><th align = \'center\'><strong><br>Volume(ul)</strong></th>'
    intestcsv.append('N\tGenealogyID\tBarcode\tVolume(ul)')
    
    print 'lista',lista
    print 'intest',intest
    print 'listacsv',listacsv
    return lista,intest,listacsv,intestcsv

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

#serve per trasformare la visualizzazione delle aliquote splittate in un formato
#compatibile con la visualizzazione in html
#si puo' usare sia per la tabella di riepilogo che per la creazione del pdf
def ReportSplitToHtml(n,genid,barcode,piastra,pos,conc,vol,vol_madre,acqua,gen_madre,barc_madre,pdf):
    if pdf=="s":
        return '<tr><td align="center"><br><strong>'+str(n)+'</td><td align="center"><br>'+genid+'</td><td align="center"><br>'+barcode+'</td><td align="center"><br>'+piastra+'</td><td align="center"><br>'+ pos +'</td><td align="center"><br>'+conc+'</td><td align="center"><br>'+vol+'</td><td align="center"><br>'+vol_madre+'</td><td align="center"><br>'+acqua+'</td><td align="center"><br>'+gen_madre+'</td><td align="center"><br>'+barc_madre+'</td></tr>'
    else:
        return '<tr><td align="center">'+str(n)+'</td><td align="center">'+genid+'</td><td align="center">'+barcode+'</td><td align="center">'+piastra+'</td><td align="center">'+ pos +'</td><td align="center">'+conc+'</td><td align="center">'+vol+'</td><td align="center">'+vol_madre+'</td><td align="center">'+acqua+'</td><td align="center">'+gen_madre+'</td><td align="center">'+barc_madre+'</td></tr>'
    
#serve per trasformare la visualizzazione dei kit inseriti in un formato
#compatibile con la visualizzazione in html
#si puo' usare sia per la tabella di riepilogo che per la creazione del pdf
def ReportKitToHtml(n,tipo,barcode,data,lotto,pdf):
    if pdf=="s":
        return '<tr><td align="center"><br><strong>'+str(n)+'</td><td align="center"><br><strong>'+tipo+'</td><td align="center"><br>'+barcode+'</td><td align="center"><br>'+data+'</td><td align="center"><br>'+ lotto +'</td></tr>'
    else:
        return '<tr><td align="center">'+tipo+'</td><td align="center">'+barcode+'</td><td align="center">'+data+'</td><td align="center">'+ lotto +'</td></tr>' 

#serve per trasformare la visualizzazione dei campioni il cui volume e' da diminuire in un
#formato compatibile con la visualizzazione in html
#si puo' usare sia per la tabella di riepilogo che per la creazione del pdf
def ReportVolumeToHtml(n,esperim,gen,barcode,pos,conc,takenvol,finalvol,esausta,pdf):
    if pdf=="s":
        return '<tr><td align="center"><br><strong>'+str(n)+'</td><td align="center"><br><strong>'+esperim+'</td><td align="center"><br><strong>'+gen+'</td><td align="center"><br>'+barcode+'</td><td align="center"><br>'+pos+'</td><td align="center"><br>'+conc+'</td><td align="center"><br>'+ takenvol +'</td><td align="center"><br>'+ finalvol +'</td><td align="center"><br>'+ esausta +'</td></tr>'
    else:
        return '<tr><td align="center">'+str(n)+'</td><td align="center">'+esperim+'</td><td align="center">'+gen+'</td><td align="center">'+barcode+'</td><td align="center">'+pos+'</td><td align="center">'+conc+'</td><td align="center">'+ takenvol +'</td><td align="center">'+ finalvol +'</td><td align="center">'+ esausta +'</td></tr>' 

#serve per trasformare la visualizzazione delle aliquote programmate per la derivazione
#e poi cancellate in un formato compatibile con la visualizzazione in html
#si puo' usare sia per la tabella di riepilogo che per la creazione del pdf
def ReportDerCancToHtml(n,genid,barcode,assigner,data,derivato,pdf):
    if pdf=="s":
        return '<tr><td align="center"><br><strong>'+str(n)+'</td><td align="center"><br>'+genid+'</td><td align="center"><br>'+barcode+'</td><td align="center"><br>'+assigner+'</td><td align="center"><br>'+ data +'</td><td align="center"><br>'+derivato+'</td></tr>'
    else:
        return '<tr><td align="center">'+str(n)+'</td><td align="center">'+genid+'</td><td align="center">'+barcode+'</td><td align="center">'+assigner+'</td><td align="center">'+ data +'</td><td align="center">'+derivato+'</td></tr>'

#serve per trasformare la visualizzazione delle aliquote programmate per rivalutazione, split o 
#posizionamento e poi cancellate in un formato compatibile con la visualizzazione in html
#si puo' usare sia per la tabella di riepilogo che per la creazione del pdf
def ReportScheduleCancToHtml(n,genid,barcode,pos,assigner,data,pdf):
    if pdf=="s":
        return '<tr><td align="center"><br><strong>'+str(n)+'</td><td align="center"><br>'+genid+'</td><td align="center"><br>'+barcode+'</td><td align="center"><br>'+pos+'</td><td align="center"><br>'+assigner+'</td><td align="center"><br>'+ data +'</td></tr>'
    else:
        return '<tr><td align="center">'+str(n)+'</td><td align="center">'+genid+'</td><td align="center">'+barcode+'</td><td align="center">'+pos+'</td><td align="center">'+assigner+'</td><td align="center">'+ data +'</td></tr>'

#serve per trasformare la visualizzazione delle aliquote posizionate in un formato compatibile 
#con la visualizzazione in html.
#si puo' usare sia per la tabella di riepilogo che per la creazione del pdf
def ReportPositionToHtml(n,genid,vecchiobarc,barc,pias,pos,pdf):
    if pdf=="s":
        return '<tr><td align="center"><br><strong>'+str(n)+'</td><td align="center"><br>'+genid+'</td><td align="center"><br>'+vecchiobarc+'</td><td align="center"><br>'+ barc +'</td><td align="center"><br>'+ pias +'</td><td align="center"><br>'+ pos +'</td></tr>'
    else:
        return '<tr><td align="center">'+str(n)+'</td><td align="center">'+genid+'</td><td align="center">'+vecchiobarc+'</td><td align="center">'+ barc +'</td><td align="center">'+ pias +'</td><td align="center">'+ pos +'</td></tr>'

def ReportTransferToHtml(n,genid,barc,pos,vol,pdf):
    if pdf=="s":
        return '<tr><td align="center"><br><strong>'+str(n)+'</td><td align="center"><br>'+genid+'</td><td align="center"><br>'+barc+'</td><td align="center"><br>'+pos+'</td><td align="center"><br>'+vol+'</td></tr>'
    else:
        return '<tr><td align="center">'+str(n)+'</td><td align="center">'+genid+'</td><td align="center">'+barc+'</td><td align="center">'+pos+'</td><td align="center">'+vol+'</td></tr>'

class Misura(models.Model):
    tipo=models.CharField(max_length=100)
    unit=models.CharField(max_length=100)
    tipostrum=models.CharField(max_length=100)
    codstrum=models.CharField(max_length=100)
    val=models.FloatField(max_length=100)
    
class AggiornaVolume(models.Model):
    gen=models.CharField(max_length=100)
    barcode=models.CharField(max_length=100)
    position=models.CharField(max_length=100)
    concattuale=models.CharField(max_length=100)
    volattuale=models.CharField(max_length=100)
    volpreso=models.CharField(max_length=100)
    quantpresa=models.CharField(max_length=100)
    volequiv=models.CharField(max_length=100)
    volfinale=models.CharField(max_length=100)
    replicati=models.CharField(max_length=100)
    def __unicode__(self):
        return self.gen+' '+self.concattuale

#restituisce i dati per costruire la tabella in HTML e le dimensioni della piastra
#nel vettore dim. Il tipo e' il tipo aliq abbreviato
'''
def CreaTabella (data,tipo):
    #prendo le dimensioni della piastra
    lista=[]
    dimension = data['rules']['dimension']
    print 'dimension',dimension
    dim = []

    aliqtip=AliquotType.objects.get(abbreviation=tipo)

    #recupero l'oggetto feature relativo al numero di pezzi per le aliq
    featu=Feature.objects.filter(Q(name='NumberOfPieces')&Q(idAliquotType=aliqtip))
    #print 'fe',featu
    for d in dimension:
        dim.append(d)
        #lastIndex = lastIndex + str(d)
    for d in data['children']:
        for rr in data['rules']['items']:
            #devo fare il controllo perche' se il posto e' vuoto, allora in d['position'] non c'e' quell'id (es: A3, F3)
            if rr['id'] == d['position']:
                point = ""
                for p in rr['position']:
                    if point != "":
                        point = str(point) + '|' + str(p)
                    else:
                        point = str(p)
                
                listagen=Aliquot.objects.filter(uniqueGenealogyID=str(d['gen']),availability=1)

                #VERSION FOR GRAPH_DB
                if settings.USE_GRAPH_DB==True:
                    if listagen.count_old()!=0:
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
                            
                            prov=CreaStringa(listagen[0], featu, d, point)
                    #se la provetta e' vuota
                    else:
                        prov=str(d['barcode'])+','+str(d['position'])+','+str(point)
                else:
                    #VERSION WITH NO GRAPH_DB    
                    #se la provetta e' piena
                    if listagen.count()!=0:
                        prov=CreaStringa(listagen[0], featu, d, point)
                    #se la provetta e' vuota
                    else:
                        prov=str(d['barcode'])+','+str(d['position'])+','+str(point)
                lista.append(prov)

    print 'lis',lista
    return lista, dim
'''
   
#restituisce i dati per costruire la tabella in HTML e le dimensioni della piastra
#nel vettore dim. Il tipo e' il tipo aliq abbreviato
def CreaTabella (data,tipo):
    #prendo le dimensioni della piastra
    lista=[]
    dimension = data['rules']['dimension']
    print 'dimension',dimension
    barcodeStr = ""
    dim = []

    aliqtip=AliquotType.objects.get(abbreviation=tipo)
    if aliqtip.type=='Original':
        #recupero l'oggetto feature relativo al numero di pezzi per le aliq
        featu=Feature.objects.filter(Q(name='NumberOfPieces')&Q(idAliquotType=aliqtip))
        #print 'fe',featu
    for d in dimension:
        dim.append(d)
        #lastIndex = lastIndex + str(d)
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

                if aliqtip.type=='Original':
                    listagen=Aliquot.objects.filter(Q(barcodeID=str(d['barcode']))&Q(availability=1)&Q(derived=0))
                    al_type=1
                else:
                    listagen=Aliquot.objects.filter(Q(barcodeID=str(d['barcode']))&Q(availability=1)&Q(derived=1))
                    al_type=2
                #se la provetta e' piena
                if settings.USE_GRAPH_DB==False or 'admin' in get_WG():

                    if listagen.count()!=0:
                        if aliqtip.type=='Original':
                            #prendo il genID dato il barc della provetta
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
    return lista, dim
   
def CreaStringa(aliq,featu,d,point):
    pzz='0'
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

def InviaMail(dizsupervisori,request,scopo,name):
    
    if len(dizsupervisori)!=0:
        for key,value in dizsupervisori.items():
            file_data = render_to_string('tissue2/revalue/report_canc.html', {'listafin':value,'scopo':scopo,'esec':name}, RequestContext(request))
            
            subject, from_email = 'Cancel schedule', 'lasircc.manager@gmail.com'
            text_content = 'This is an important message.'
            html_content = file_data
            msg = EmailMultiAlternatives(subject, text_content, from_email, [key])
            msg.attach_alternative(html_content, "text/html")
            msg.send()


def LasHubNewCase(request,casuale,tumore):
    #prefisso= 'https://' if settings.LAS_AUTH_USE_HTTPS else 'http://'
    #address=request.get_host()+settings.HOST_URL
    #indir=prefisso+address
    indir=settings.DOMAIN_URL+settings.HOST_URL
    url = indir + '/clientHUB/getAndLock/'
    print 'url',url
    values = {'randomFlag' : casuale, 'case': tumore}
    
    r = requests.post(url, data=values, verify=False, headers={"workingGroups" : get_WG_string()})
    print r.text
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
                co=listaord[(len(listaord))-1]
                print 'co',co
                caso=int(co.itemCode)
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

'''# remove files if they are in tmp directory
def remove_uploaded_files(filelist):
    print filelist
    for f in filelist:
        if os.path.split(f)[0] == os.path.split(TEMP_URL)[0]:
            print 'Removing file: ' + str(os.path.split(f)[1])
            os.remove(f)'''

def uploadRepFile(data, fileLocation):
    print 'uploadRepFile'
    repositoryUrl = Urls.objects.get(idWebService=WebService.objects.get(name='Repository').id)
    print repositoryUrl.url
    r = requests.post(repositoryUrl.url+ "api.uploadFile", data=data, files={'file': open(fileLocation)}, verify=False)
    #print r.text
    response = json.loads(r.text)
    print response
    if response['status'] == "Ok":
        return response['objectId']
    else:
        return "Fail"


def uploadExperiment(data, fileLocation):
    print 'uploadExperiment'
    repositoryUrl = Urls.objects.get(idWebService=WebService.objects.get(name='Repository').id)
    print repositoryUrl.url
    files = {}
    for f in os.listdir(fileLocation):
        files[f] = open(os.path.join(fileLocation, f))
    r = requests.post(repositoryUrl.url+ "api.uploadExperiment", data=data, files=files, verify=False)
    print r.text
    response = json.loads(r.text)
    print response
    if response['status'] == "Ok":
        return response['objectId']
    else:
        return "Fail"



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
        page.strong('Urine: ')
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
    if request.session.has_key('aliquotCollectionMercuric'):
        del request.session['aliquotCollectionMercuric']
        
        
    
