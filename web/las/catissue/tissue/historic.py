from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.contrib import auth
from django.template.context import RequestContext
from catissue.tissue.forms import *
from __init__ import *
from catissue.tissue.utils import *

#per copiare i vecchi dati dei derivati nelle giuste tabelle durante il passaggio
#su caircc. Il tutto a seguito del cambiamento della struttura dei derivati
@transaction.commit_on_success
@csrf_exempt
def CopyDerivationEvent(request):
    try:
        listaderevent=DerivationEvent.objects.all()
        for derevent in listaderevent:
            print 'derevent',derevent
            if derevent.idAliquot!=None:
                aliqdersched=AliquotDerivationSchedule.objects.get(idAliquot=derevent.idAliquot.id)
                print 'aliq',aliqdersched
                aliqdersched.idKit=derevent.idKit
                aliqdersched.failed=derevent.failed
                aliqdersched.loadQuantity=derevent.loadQuantity
                aliqdersched.volumeOutcome=derevent.volumeOutcome
                aliqdersched.measurementExecuted=1
                aliqdersched.initialDate=derevent.derivationDate
                aliqdersched.save()
        #prendo tutti i quality event
        listaqual=QualityEvent.objects.all()
        #al=Aliquot.objects.get(id=773)
        #listaqual=QualityEvent.objects.filter(idAliquot=al)
        for qualevent in listaqual:
            aliqdersched=AliquotDerivationSchedule.objects.get(idAliquot=qualevent.idAliquot.id)
            print 'aliq',aliqdersched
            qualevent.idAliquotDerivationSchedule=aliqdersched
            qualevent.operator=aliqdersched.operator
            qualevent.save()
        return HttpResponse("ok")
    except Exception, e:            
        transaction.rollback()
        print 'eccezione',e
        return HttpResponse("err")  

#funzione usata una sola volta per aggiungere degli zeri davanti al valore del caso delle collezioni.
#Necessaria a causa del passaggio del campo itemcode da int a varchar
@transaction.commit_on_success
@csrf_exempt
def ChangeCollection(request):
    try:
        listacoll=Collection.objects.all()
        for coll in listacoll:
            try:
                caso=int(coll.itemCode)
                #serve a mettere degli zeri davanti al numero del caso per formare il genealogy id
                if caso<10:
                    caso='000'+str(caso)
                elif caso <100:
                    caso='00'+str(caso)
                elif caso <1000:
                    caso='0'+str(caso)
                coll.itemCode=caso
                coll.save()
            except:
                pass                
        return HttpResponse("ok")
    except Exception, e:            
        transaction.rollback()
        print 'eccezione',e
        return HttpResponse("err")  
    
#funzione usata una sola volta per cambiare le date dei sampling legati agli FFPE
@transaction.commit_on_success
@csrf_exempt
def ChangeDateSampling(request):
    try:
        if request.method=='POST':
            print request.POST
            print request.FILES  
            form=HistoricForm(request.FILES)
            listafile=request.FILES.getlist('file')
            
            #e' il file archive tissue
            f1=listafile[0]
            tissue = f1.readlines()
            f1.close()
            
            #e' il file serie con le date
            f2=listafile[1]
            series = f2.readlines()
            f2.close()
            
            #prendo tutti i sampling fatti il 1-1-2010 che sono quelli da modificare
            listasamp=SamplingEvent.objects.filter(samplingDate='2010-01-01')
            print 'listasamp',listasamp
            for samp in listasamp:
                data=''
                #prendo le aliquote collegate al samp
                listaaliq=Aliquot.objects.filter(idSamplingEvent=samp,availability=1)
                #prendo la prima, tanto sono state fatte tutte nella stessa data
                print 'listaal',listaaliq
                if len(listaaliq)!=0:
                    gen=listaaliq[0].uniqueGenealogyID
                    print 'gen',gen
                    for valor in tissue:          
                        righe_tess=valor.split(';')
                        gen_tess=righe_tess[4]
                        gen_modif=gen[0:3]+gen[4:10]+gen[11:14]+'0'+gen[15:17]+gen[20:24]
                        #print 'tess',gen_tess
                        #print 'modif',gen_modif
                        
                        if gen_tess==gen_modif:
                            #print 'tess',gen_tess
                            #print 'modif',gen_modif
                            chiave_serie=righe_tess[2]
                            print 'chiave',chiave_serie
                            #prendo gli ultimi quattro caratteri della stringa
                            num_serie=chiave_serie[-4:]
                            print 'num_serie',num_serie
                            for serie in series:
                                val=serie.split(';')
                                num=val[0]
                                n=num[-4:]
                                #print 'n',n
                                #print 'num',num
                                if n==num_serie:
                                    '''oper=val[1]
                                    if oper=='Zanella':
                                        operat='eugenia.zanella'
                                    elif oper=='Migliardi':
                                        operat='giorgia.migliardi'''
                                    dat=val[2]
                                    d=dat.split('/')
                                    data=d[2]+'-'+d[1]+'-'+d[0]
                                    break
                                    #print 'operat inter',operat
                        #aggiorno la data
                        if data!='':
                            
                            #devo aggiornare anche la serie
                            serie,creato=Serie.objects.get_or_create(operator='eugenia.zanella',
                                                                     serieDate=data)
                            
                            samp.samplingDate=data
                            samp.idSerie=serie
                            samp.save()
                
            return HttpResponse("ok")
        else:
            form = HistoricForm()
        variables = RequestContext(request, {'form':form})
        return render_to_response('tissue2/historic/storico_mice_deriv.html',variables)
        
    except Exception, e:            
        transaction.rollback()
        print 'eccezione',e
        return HttpResponse("err") 

#per cambiare il genid dei campioni fittizi inseriti (i VT99). Viene sommato 200 al 
#codice del topo nel genid. Serve solo una volta per caircc.
@transaction.commit_on_success
@csrf_exempt
def ChangeMouse(request):
    try:
        #prendo solo le aliquote vitali
        vit=AliquotType.objects.get(abbreviation='VT')
        listaal=Aliquot.objects.filter(idAliquotType=vit)
        for al in listaal:
            ge = GenealogyID(al.uniqueGenealogyID)
            origine=ge.getSampleVector()
            #vedo se l'aliquota e' di origine murina
            if origine=='X':
                contatore=ge.getAliquotExtraction()
                #vedo se il contatore e' 99
                if contatore=='99':
                    topo=ge.getMouse()
                    #solo se e' la prima volta che lo faccio. Per evitare di
                    #sommare piu' volte il 200
                    if topo[0]!='2':
                        nuovo_topo=str(int(topo)+200)
                        #aggiorno il genid
                        ge.updateGenID({'mouse':nuovo_topo})
                        nuovo_gen=ge.getGenID()
                        al.uniqueGenealogyID=nuovo_gen
                        al.save()
        return HttpResponse("ok")
    except Exception, e:            
        transaction.rollback()
        print 'eccezione',e
        return HttpResponse("err")  
    
#nei quality event per copiare nella data di inserimento la data di misurazione. Serve
#solo una volta.
@transaction.commit_on_success
def MeasureDateCopy(request):
    try:
        #prendo i quality event
        listaqual=QualityEvent.objects.filter(Q(idQualitySchedule=None)&~Q(idAliquotDerivationSchedule=None)&Q(insertionDate=None))
        print 'lung',len(listaqual)
        for qual in listaqual:
            data=qual.misurationDate
            qual.insertionDate=data
            qual.save()
        return HttpResponse("ok")
    except Exception,e:
        print 'err',e
        transaction.rollback()
        return HttpResponse("err")

#Per inizializzare il lashub. Viene creato un file con tutte le istruzioni in SQL
@transaction.commit_on_success
def HubCreate(request):
    try:
        stringa=''
        #prendo le collezioni
        listacoll=Collection.objects.all()
        oggi=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print 'adesso',oggi
        idobj=1
        idval=1
        for coll in listacoll:
            #inserimento nella tabella object
            stringa+='insert into object values ('+str(idobj)+',1,\''+str(oggi)+'\',1);\n'
            #inserimento delle feature della collezione
            stringa+='insert into object_value values ('+str(idval)+','+str(idobj)+',1,\''+coll.idCollectionType.abbreviation+'\');\n'
            idval=idval+1
            stringa+='insert into object_value values ('+str(idval)+','+str(idobj)+',2,\''+coll.itemCode+'\');\n'
            idval=idval+1
            idobj=idobj+1
        
        f2=open(os.path.join(os.path.dirname(__file__),'tissue_media/File_Format/create1.sql'),'w')
        f2.write(stringa)
        f2.close()
        return HttpResponse("ok")
    except Exception,e:
        print 'err',e
        transaction.rollback()
        return HttpResponse("err")

#serve per caricare le vecchie collezioni
@transaction.commit_on_success
def Historic(request):
    try:
        percorso=os.path.join(os.path.dirname(__file__),'tissue_media/Historical/Collection.csv')
        #f = open('C:/Documents and Settings/x/Documenti/Tesi/Collection.csv')
        print 'perc',percorso
        
        f=open(percorso)
        lines = f.readlines()
        f.close()
    
        for line in lines:
            valori=line.split(';')
            coll_ev=valori[14]
            ospedale=valori[6]
            codice=valori[8]
            
            tumore=codice[0:3]
            #devo prendere il caso
            caso=codice[3:]
            if ospedale!='' and codice!='':
                osp=Source.objects.get(Q(name__startswith=ospedale)&Q(type='Hospital'))
                tum=CollectionType.objects.get(abbreviation=tumore)
                cas=int(caso)
                #verifico se il caso c'e' gia'
                coll=Collection.objects.filter(Q(idCollectionType=tum)&Q(itemCode=cas))
                #if coll.count()!=0:
                #    raise ErrorHistoric(caso)
                
                collezione,creato=Collection.objects.get_or_create(itemCode=cas,
                         idSource=osp,
                         idCollectionType=tum,
                         collectionEvent=coll_ev)
                #collezione.save()
                print 'tum',tumore
                print 'osp',osp
                print 'caso',caso
    
        return HttpResponse("ok")  
    except ErrorHistoric as e:
        print 'My exception occurred, value:', e.value
        transaction.rollback()
        return HttpResponse("err")
    except Exception,e:
        print 'err',e
        transaction.rollback()
        return HttpResponse("err")  

#serve per salvare degli eventi di campionamento fittizi che facciano apparire giusta
#la data di collezionamento
@transaction.commit_on_success
def HistoricSamplingEvent(request):
    try:
        if request.method=='POST':
            print request.POST
            print request.FILES  
            form=HistoricForm(request.FILES)
            listafile=request.FILES.getlist('file')
            
            #e' il file delle collezioni    
            f1=listafile[0]
            lines = f1.readlines()
            f1.close()
            j=0
            for line in lines:
                valori=line.split(';')
                codice=valori[8]
                tumore=codice[0:3]
                #devo prendere il caso
                caso=codice[3:]
                tum=CollectionType.objects.get(abbreviation=tumore)
                cas=int(caso)
                #verifico se il caso c'e' gia'
                coll=Collection.objects.get(Q(idCollectionType=tum)&Q(itemCode=cas))
                tessuto=TissueType.objects.get(abbreviation='LM')
                data_coll=valori[0]
                d=data_coll.split('/')
                dat=d[2]+'-'+d[1]+'-'+d[0]
                serie_def,creato=Serie.objects.get_or_create(operator='None',
                                                             serieDate=dat)
                samp_ev,creato=SamplingEvent.objects.get_or_create(idTissueType=tessuto,
                                                                idCollection=coll,
                                                                idSource=coll.idSource,
                                                                idSerie=serie_def,
                                                                samplingDate=dat)
                print 'samp',samp_ev
                j=j+1
                #if j==4:
                    #break
            return HttpResponse("ok")  
        else:
            form = HistoricForm()
        variables = RequestContext(request, {'form':form})
        return render_to_response('tissue2/historic/storico_sampl.html',variables)
    except ErrorHistoric as e:
        print 'My exception occurred, value:', e.value
        transaction.rollback()
        return HttpResponse("err")
    except Exception,e:
        print 'err',e
        transaction.rollback()
        return HttpResponse("err") 

#per caricare i campioni storici del file di Excel ArchiveTissue
@transaction.commit_on_success
def HistoricTissue(request):
    try:
        if request.method=='POST':
            print request.POST
            print request.FILES  
            form=HistoricForm(request.FILES)
            listafile=request.FILES.getlist('file')
            
            #e' il file archive_tissue
            f1=listafile[0]
            #percorso=os.path.join(os.path.dirname(__file__),'tissue_media/Historical/Tessuti.csv')
            #f = open('C:/Documents and Settings/x/Documenti/Tesi/Collection.csv')
            #print 'perc',percorso
            #f=open(percorso)
            lines = f1.readlines()
            f1.close()
            
            #e' il file per le serie di collezionamento
            f2=listafile[1]
            #percorso2=os.path.join(os.path.dirname(__file__),'tissue_media/Historical/SerieTessuti.csv')
            #print 'perc',percorso2
            #f=open(percorso2)
            series = f2.readlines()
            f2.close()
            
            #e' il file archive_container da cui ricavo il barcode del box
            f3=listafile[2]
            contain= f3.readlines()
            f3.close()
            
            #e' il file summary per le aliquote nelle piastre Thermo
            f4=listafile[3]
            aliq_summ= f4.readlines()
            f4.close()
            
            #riempio un dizionario in cui ad ogni gen id del file summary.csv e'
            #associata l'indicazione se c'e' una corrispondenza nel file archive_tissue
            dizio={}
                       
            tumori=CollectionType.objects.all()
            tessuti=TissueType.objects.all()
            tipi_aliq=AliquotType.objects.all()
            cas_generico=re.compile('(0\d\d\d)$')
            cas_thermo=re.compile('(\d\d\d)$')
            umano=re.compile('(X|H)$')
            topo=re.compile('([A-Za-z]\d\d\d\d\d(TUM|LNG|LIV|GUT|BLD|MLI|MBR|MLN))$')
            topo_thermo=re.compile('([A-Za-z]\d\d\d\d\d)$')
            uomo=re.compile('(000000000)$')
            uomo_thermo=re.compile('(000000)$')
            contatore=re.compile('(\d\d)$')
            rack_box=re.compile('(\d)+$')
            pos=re.compile('([A-Ja-j]\d\d*)$')
            store=re.compile('(Store00\d)$')
            
            err=''
            
            '''if pos.match('23'):
                print 'si'
            else:
                print 'no'''
            
            for righe_aliq in aliq_summ:
                rig=righe_aliq.split('\t')
                gen_id_prova=rig[0].strip()
                dizio[gen_id_prova]='0'
                #serve per valutare il codice del tumore
                '''tum=gen_id_prova[0:3]
                trovato=False
                for i in range(0,len(tumori)):
                    if tum==str(tumori[i].abbreviation):
                        trovato =True
                        break; 
                if trovato==False:
                    err+=gen_id_prova+': tumore inesistente. '+rig[5]
                    continue
                #serve per valutare il codice del caso
                #il problema e' che alcuni hanno 3 cifre altri 4
                caso=gen_id_prova[3:7]
                partenza=7
                if not cas_generico.match(caso):
                    caso2=gen_id_prova[3:6]
                    partenza=6
                    if not cas_thermo.match(caso2):
                        err+=gen_id_prova+': caso errato. '+rig[5]
                        continue
                #serve per valutare il codice del tessuto
                tess=gen_id_prova[partenza:partenza+2]
                trovato2=False
                for i in range(0,len(tessuti)):
                    if tess==str(tessuti[i].abbreviation):
                        trovato2 =True
                        break;                             
                if trovato2==False:
                    err+=gen_id_prova+': tessuto inesistente. '+rig[5]
                    continue
                #serve per valutare l'H o la X
                tipo=gen_id_prova[partenza+2:partenza+3]
                #print 'tipo',tipo
                if not umano.match(tipo):
                    err+=gen_id_prova+': Problema su X/H. '+rig[5]
                    continue
                parte_centr=gen_id_prova[partenza+3:partenza+9]
                #serve per valutare i 6 valori dopo l'H o la X
                if tipo=='X':
                    if not topo_thermo.match(parte_centr):
                        err+=gen_id_prova+': Problema su codice topo. '+rig[5]
                        continue
                elif tipo=='H':
                    if not uomo_thermo.match(parte_centr):
                        #err+=gen_id_prova+': Problema sul numero di zeri dopo H. '+rig[4]
                        continue
                #serve per valutare il tipo di aliq (VT,SF...)
                tipo_al=gen_id_prova[partenza+9:partenza+11]
                trovato3=False
                for i in range(0,len(tipi_aliq)):
                    if tipo_al==str(tipi_aliq[i].abbreviation):
                        trovato3 =True
                        break; 
                if trovato3==False:
                    print 'tipo',tipo_al
                    err+=gen_id_prova+': Problema sul tipo di aliquota (RL,SF,...). '+rig[4]
                    continue
                #serve per valutare il contatore finale del genid
                cont=gen_id_prova[partenza+11:partenza+13]
                if not contatore.match(cont):
                    err+=gen_id_prova+': Problema sul contatore finale. '+rig[5]
                    continue
            file=open(os.path.join(os.path.dirname(__file__),'tissue_media/Historical/ErrAliquotsSF2.txt'),'w')
            file.write(err)
            file.close()'''
            '''if topo.match('X05002MBR'):
                print 'si'
            else:
                print 'no'''
            #salvo prima tutte le serie presenti nel file e poi dopo le richiamo quando
            #salvo il sampling event
            '''for serie in series:
                val=serie.split(';')
                operatore=val[1]
                print 'operatore',operatore
                data=val[2]
                print 'data',data
                d=data.split('/')
                print 'd',d[0]
                dat=d[2]+'-'+d[1]+'-'+d[0]
                print 'dat',dat
                se,creato=Serie.objects.get_or_create(operator=operatore,
                                                      serieDate=dat)'''
            nserie=''
            operat=''
            data=''
            j=0
            lista_archivio=''
            stringa=''
            stringa+='Barcode;GenealogyId;AliquotType;Pieces;Plate;Position\n'
            listagen=[]
            for kk in range(0,len(lines)):
                line=lines[kk]
                valori=line.split(';')
                '''sto=valori[26]
                rack=valori[27]
                box=valori[28]
                posiz=valori[29]
                if sto!='':
                    if not store.match(sto):
                        print 'store',line
                    if not rack_box.match(rack):
                        print 'rack',line
                    if not rack_box.match(box):
                        print 'box',line
                    if not pos.match(posiz):
                        print 'pos',line'''
                        
                gen=valori[6]
                if gen=="":
                    raise ErrorHistoric(valori[0])
                if len(gen)!=23:
                    raise ErrorHistoric(gen+' '+line)
                #serve per valutare il codice del tumore
                tum=gen[0:3]
                trovato=False
                for i in range(0,len(tumori)):
                    if tum==str(tumori[i].abbreviation):
                        trovato =True
                        break; 
                if trovato==False:
                    raise ErrorHistoric(gen+' '+line)
                #serve per valutare il codice del caso
                caso=gen[3:7]
                if not cas_generico.match(caso):
                    raise ErrorHistoric(gen+' '+line)
                #serve per valutare il codice del tessuto
                tess=gen[7:9]
                trovato2=False
                for i in range(0,len(tessuti)):
                    if tess==str(tessuti[i].abbreviation):
                        trovato2 =True
                        break;                             
                if trovato2==False:
                    raise ErrorHistoric(gen+' '+line)
                #serve per valutare l'H o la X
                tipo=gen[9:10]
                #print 'tipo',tipo
                if not umano.match(tipo):
                    raise ErrorHistoric(gen+' '+line)
                parte_centr=gen[10:19]
                #serve per valutare i nove valori dopo l'H o la X
                if tipo=='X':
                    if not topo.match(parte_centr):
                        raise ErrorHistoric(gen+' '+line)
                elif tipo=='H':
                    if not uomo.match(parte_centr):
                        print 'problema H'
                        raise ErrorHistoric(gen+' '+line) 
                #serve per valutare il tipo di aliq (VT,SF...)
                tipo_al=gen[19:21]
                trovato3=False
                for i in range(0,len(tipi_aliq)):
                    if tipo_al==str(tipi_aliq[i].abbreviation):
                        trovato3 =True
                        break; 
                if trovato3==False:
                    print 'tipo',tipo_al
                    raise ErrorHistoric(gen+' '+line)
                #serve per valutare il contatore finale del genid
                cont=gen[21:23]
                if not contatore.match(cont):
                    print 'contatore'
                    raise ErrorHistoric(gen+' '+line)
                
                
                #serve per vedere se qualche genid e' duplicato
                if gen not in listagen:
                    listagen.append(gen)
                else:
                    #raise ErrorHistoric(gen+' '+line)
                    print 'duplicato',gen+' '+line
                
                
                #devo creare il sampling event
                #prendo la collezione
                tumore=CollectionType.objects.get(abbreviation=tum)
                cas=int(caso)
                coll=Collection.objects.filter(Q(idCollectionType=tumore)&Q(itemCode=cas))
                if coll.count()!=1:
                    raise ErrorHistoric(gen+' '+line)
                coll=Collection.objects.get(Q(idCollectionType=tumore)&Q(itemCode=cas)) 
                #prendo il tipo di tessuto
                tessuto=TissueType.objects.get(abbreviation=tess)
                chiave_serie=valori[1]
                #prendo gli ultimi quattro caratteri della stringa
                num_serie=chiave_serie[-4:]
                #print 'num',num_serie
                #print 'nserie',nserie
                if nserie!=num_serie:
                    nserie=num_serie
                    for serie in series:
                        val=serie.split(';')
                        num=val[0]
                        n=num[-4:]
                        if n==num_serie:
                            operat=val[1]
                            dat=val[2]
                            d=dat.split('/')
                            data=d[2]+'-'+d[1]+'-'+d[0]
                serie_def=Serie.objects.get(Q(operator=operat)&Q(serieDate=data))
                #print 'serie',serie_def
                tipo_al=gen[19:21]
                #mi occupo del tipo di aliq (VT,RL...)
                ti_aliq=AliquotType.objects.get(abbreviation=tipo_al)
                #per adesso salvo solo RL, SF e VT e non FF
                if ti_aliq.type=='Original':
                    '''samp_ev,creato=SamplingEvent.objects.get_or_create(idTissueType=tessuto,
                                                                idCollection=coll,
                                                                idSource=coll.idSource,
                                                                idSerie=serie_def,
                                                                samplingDate=data)'''
                    barcode=valori[16]
                    #mi occupo adesso del salvataggio delle provette nello storage
                    sto=''                  
                    #serve per le aliq vecchie nei box
                    if len(valori)>26:
                        sto=valori[26]
                        rack=valori[27]
                        box=valori[28]
                        posiz=valori[29]
                        
                    if sto!='':
                        barc_box_effettivo=''
                        for righe in contain:
                            rig=righe.split(';')
                            barc_store=rig[1]
                            barc_rack=rig[2]
                            barc_box=rig[3]
                            if barc_store==sto and barc_rack==rack and barc_box==box:
                                barc_box_effettivo=rig[6]
                                #devo vedere se la posizione e' espressa come un numero o come
                                #lettera e numero
                                if not pos.match(posiz):
                                    #per sapere le posizioni totali della piastra
                                    pos_tot=rig[5]
                                    #puo' essere 9 o 10
                                    riferimento=int(math.sqrt(int(pos_tot)))
                                    #print 'pos no',posiz
                                    #divido il numero per 9 e ottengo un valore da convertire in
                                    #lettera
                                    valore_num=int(int(posiz)/riferimento)

                                    #prendo il resto della divisione per 9 o 10 e quello e' il numero
                                    #da affiancare alla lettera
                                    numero=(int(posiz)%riferimento)
                                    if numero==0:
                                        numero=riferimento
                                        valore_num-=1
                                    #print 'val num',valore_num
                                    lettera=chr(valore_num+ord('A'))
                                    
                                    posiz=str(lettera)+str(numero)
                                    #print 'nuova_pos',posiz
                                break
                        if barc_box_effettivo=='':
                            print 'box non presente'
                            raise ErrorHistoric(sto+' '+rack+' '+box+'  '+line)
                        else:
                            
                            #vedo se l'aliq e' disponibile
                            disponibile=valori[24].strip()
                            #print 'disponibile',valori[24]
                            if disponibile=='y' or disponibile=='Y':
                                disp=1
                                lista_archivio+=barc_box_effettivo+'|'+barcode+'|'+posiz+','
                            elif disponibile=='n' or disponibile=='N':
                                disp=0
                    #se sto trattando le aliq nuove nelle piastre Thermo
                    else:
                        #prendo il genid corto, senza i due zeri finali, a cui devo
                        #aggiungere uno zero davanti al numero del caso per poterlo
                        #confrontare con il genid che c'e' nel file summary.csv e 
                        #capire cosi' dove e' posizionata l'aliquota
                        
                        #if ti_aliq.abbreviation!='VT':
                        gen_corto=valori[4]
                        if ti_aliq.abbreviation=='RL' or ti_aliq.abbreviation=='VT':
                            gen_effett=gen_corto[0:3].upper()+'0'+gen_corto[3:].upper()
                        elif ti_aliq.abbreviation=='SF':
                            gen_effett=gen_corto
                        #print 'gen_effett',gen_effett
                        #scandisco le righe del file
                        for righe_aliq in aliq_summ:
                            rig=righe_aliq.split('\t')
                            genid_file=rig[0].strip()
                            trovato=0
                            if str(genid_file)==gen_effett:
                                trovato=1
                                barc_box_effettivo=rig[1]
                                posiz=rig[2]
                                barcode=rig[3]
                                disponibile=rig[4].strip()
                                if disponibile=='':
                                    disp=1
                                elif disponibile=='esaurito':
                                    #print 'esaurito',line
                                    disp=0
                                dizio[genid_file]='1'
                                break
                        if trovato==0:
                            print 'gen non presente in summary.csv',gen_effett
                            #aaaaaaa=1
                            #raise ErrorHistoric(gen_effett+'  '+line)
                        else:
                            if disp==1:
                                lista_archivio+=barc_box_effettivo+'|'+barcode+'|'+posiz+','                     
                    
                    #else:
                    #    raise ErrorHistoric(gen+' '+disponibile+' '+line)
                    if len(valori)<26:
                        pezzi_usati=0
                    else:
                        #print 'len',len(valori)
                        pezzi_usati=valori[23].strip()
                        if pezzi_usati=='' or pezzi_usati=='? null':
                            pezzi_usati=0
                    derive=0
                    #aggiungo i due zeri finali al gen id e lo 0 davanti al lineage
                    g=gen[0:10].upper()+'0'+gen[10:].upper()+'00'
                    if tipo=='X':
                        gen2=g[0:14]+'2'+g[15:]
                        print 'gen2',gen2
                    else:
                        gen2=g
                    #print 'g',g
                    #salvo l'aliquota
                    '''al=Aliquot(barcodeID=barcode,
                               uniqueGenealogyID=gen2,
                               idSamplingEvent=samp_ev,
                               idAliquotType=ti_aliq,
                               availability=disp,
                               timesUsed=pezzi_usati,
                               derived=derive)
                    al.save()
                    #salvo il numero di pezzi dell'aliquota
                    num_pezzi=valori[22].strip()
                    if num_pezzi=='':
                        num_pezzi=2
                    fea=Feature.objects.get(Q(idAliquotType=ti_aliq)&Q(name='NumberOfPieces'))
                    aliqfeature=AliquotFeature(idAliquot=al,
                                               idFeature=fea,
                                               value=num_pezzi)
                    aliqfeature.save()
                    
                            
                    stringa+=str(barcode)+';'+str(g)+';'+str(ti_aliq.abbreviation)+';'+str(num_pezzi)+';'+str(barc_box_effettivo)+';'+str(posiz)+'\n'
                '''
                #j+=1
                #if j==40:
                    #break
            
            #vedo se tutte le aliq di summary.csv hanno una corrispodenza in archive_tissue
            #for key,value in dizio.items():
                #if value=='0':
                    #print 'aliq senza corrispondenza in archive_tissue',key
                    #raise ErrorHistoric(key)
                
            #tolgo l'ultima , alla fine della stringa
            '''lung=len(lista_archivio)-1
            l_arch_def=lista_archivio[:lung]
            print 'l_arch_def',l_arch_def
            #comunico allo storage le provette che deve salvare
            url = Urls.objects.get(default = '1').url + "/historic/tube"          
            val1={'lista':l_arch_def}

            print 'url1',url
            data = urllib.urlencode(val1)
            u = urllib2.urlopen(url, data)
            res =  u.read() 
            if res=='err':
                raise ErrorHistoric('salvataggio storage')'''
            f2=open(os.path.join(os.path.dirname(__file__),'tissue_media/Historical/HistoricalTissues.csv'),'w')
            f2.write(stringa)
            f2.close()

            return HttpResponse("ok")
        else:
            form = HistoricForm()
        variables = RequestContext(request, {'form':form})
        return render_to_response('tissue2/historic/storico_tess.html',variables)
    except ErrorHistoric as e:
        print 'My exception occurred, value:', e.value
        transaction.rollback()
        return HttpResponse("err")
    except Exception,e:
        print 'err',e
        transaction.rollback()
        return HttpResponse("err")

#per caricare i campioni storici delle piastre CRL, che non erano presenti nel primo
#caricamento di tessuti
@transaction.commit_on_success
def HistoricTissueCRL(request):
    try:
        if request.method=='POST':
            print request.POST
            print request.FILES  
            form=HistoricForm(request.FILES)
            listafile=request.FILES.getlist('file')
            
            #e' il file summary dei tessuti da caricare
            f1=listafile[0]
            aliq_summ = f1.readlines()
            f1.close()
            
            tumori=CollectionType.objects.all()
            tessuti=TissueType.objects.all()
            tipi_aliq=AliquotType.objects.all()
            cas_generico=re.compile('(0\d\d\d)$')
            cas_thermo=re.compile('(\d\d\d)$')
            umano=re.compile('(X|H)$')
            topo=re.compile('([A-Za-z]\d\d\d\d\d(TUM|LNG|LIV|GUT|BLD|MLI|MBR|MLN))$')
            topo_thermo=re.compile('([A-Za-z]\d\d\d\d\d)$')
            uomo=re.compile('(000000000)$')
            uomo_thermo=re.compile('(000000)$')
            contatore=re.compile('(\d\d)$')
            rack_box=re.compile('(\d)+$')
            pos=re.compile('([A-Ja-j]\d\d*)$')
            store=re.compile('(Store00\d)$')
            
            err=''
            lista_archivio=''
            listagen=[]
            k=0
            
            for righe_aliq in aliq_summ:
                rig=righe_aliq.split('\t')
                gen_id_prova=rig[0].strip()
                #serve per valutare il codice del tumore
                tum=gen_id_prova[0:3]
                trovato=False
                for i in range(0,len(tumori)):
                    if tum==str(tumori[i].abbreviation):
                        trovato =True
                        break; 
                if trovato==False:
                    err+=gen_id_prova+': tumore inesistente. '+rig[5]
                    continue
                #serve per valutare il codice del caso
                #il problema e' che alcuni hanno 3 cifre altri 4
                caso=gen_id_prova[3:6]
                partenza=6
                if not cas_thermo.match(caso):
                    err+=gen_id_prova+': caso errato. '+rig[5]
                    continue
                #serve per valutare il codice del tessuto
                tess=gen_id_prova[partenza:partenza+2]
                trovato2=False
                for i in range(0,len(tessuti)):
                    if tess==str(tessuti[i].abbreviation):
                        trovato2 =True
                        break;                             
                if trovato2==False:
                    err+=gen_id_prova+': tessuto inesistente. '+rig[5]
                    continue
                #serve per valutare l'H o la X
                tipo=gen_id_prova[partenza+2:partenza+3]
                #print 'tipo',tipo
                if not umano.match(tipo):
                    err+=gen_id_prova+': Problema su X/H. '+rig[5]
                    continue
                parte_centr=gen_id_prova[partenza+3:partenza+9]
                #serve per valutare i 6 valori dopo l'H o la X
                if tipo=='X':
                    if not topo_thermo.match(parte_centr):
                        err+=gen_id_prova+': Problema su codice topo. '+rig[5]
                        continue
                elif tipo=='H':
                    if not uomo_thermo.match(parte_centr):
                        #err+=gen_id_prova+': Problema sul numero di zeri dopo H. '+rig[4]
                        continue
                #serve per valutare il tipo di aliq (VT,SF...)
                tipo_al=gen_id_prova[partenza+9:partenza+11]
                trovato3=False
                for i in range(0,len(tipi_aliq)):
                    if tipo_al==str(tipi_aliq[i].abbreviation):
                        trovato3 =True
                        break; 
                if trovato3==False:
                    print 'tipo',tipo_al
                    err+=gen_id_prova+': Problema sul tipo di aliquota (RL,SF,...). '+rig[4]
                    continue
                #serve per valutare il contatore finale del genid
                cont=gen_id_prova[partenza+11:partenza+13]
                if not contatore.match(cont):
                    err+=gen_id_prova+': Problema sul contatore finale. '+rig[5]
                    continue
                
                #serve per vedere se qualche genid e' duplicato
                if gen_id_prova not in listagen:
                    listagen.append(gen_id_prova)
                else:
                    #raise ErrorHistoric(gen+' '+line)
                    print 'duplicato',gen_id_prova+' '+aliq_summ
                           
                #devo creare il sampling event
                #prendo la collezione
                tumore=CollectionType.objects.get(abbreviation=tum)
                cas=int(caso)
                coll=Collection.objects.filter(Q(idCollectionType=tumore)&Q(itemCode=cas))
                if coll.count()!=1:
                    raise ErrorHistoric(gen_id_prova+' '+aliq_summ)
                coll=Collection.objects.get(Q(idCollectionType=tumore)&Q(itemCode=cas)) 
                #prendo il tipo di tessuto
                tessuto=TissueType.objects.get(abbreviation=tess)
                #devo prendere la serie
                data='2012-08-21'
                serie_def=Serie.objects.get(Q(operator='eugenia.zanella')&Q(serieDate=data))
                samp_ev,creato=SamplingEvent.objects.get_or_create(idTissueType=tessuto,
                                                                idCollection=coll,
                                                                idSource=coll.idSource,
                                                                idSerie=serie_def,
                                                                samplingDate=data)
                
                if tipo=='X':
                    gen2=gen_id_prova[0:3]+'0'+gen_id_prova[3:9]+'0'+gen_id_prova[9:12]+'2'+gen_id_prova[13:15]+'TUM'+gen_id_prova[15:]+'00'
                    print 'gen2',gen2
                #print 'g',g
                barcode=rig[3].strip()
                barc_piastra=rig[1].strip()
                posiz=rig[2].strip()
                lista_archivio+=barc_piastra+'|'+barcode+'|'+posiz+','
                #mi occupo del tipo di aliq (VT,RL...)
                ti_aliq=AliquotType.objects.get(abbreviation=tipo_al)
                #salvo l'aliquota
                al=Aliquot(barcodeID=barcode,
                           uniqueGenealogyID=gen2,
                           idSamplingEvent=samp_ev,
                           idAliquotType=ti_aliq,
                           availability=1,
                           timesUsed=0,
                           derived=0)
                al.save()
                #salvo il numero di pezzi dell'aliquota
                num_pezzi=1
                
                fea=Feature.objects.get(Q(idAliquotType=ti_aliq)&Q(name='NumberOfPieces'))
                aliqfeature=AliquotFeature(idAliquot=al,
                                           idFeature=fea,
                                           value=num_pezzi)
                aliqfeature.save()
                
                #k=k+1
                #if k==2:
                    #break
            
            lung=len(lista_archivio)-1
            l_arch_def=lista_archivio[:lung]
            print 'l_arch_def',l_arch_def
            #comunico allo storage le provette che deve salvare
            url = Urls.objects.get(default = '1').url + "/historic/tube"          
            val1={'lista':l_arch_def}

            print 'url1',url
            data = urllib.urlencode(val1)
            req = urllib2.Request(url,data=data, headers={"workingGroups" : get_WG_string()})
            u = urllib2.urlopen(req)
            #u = urllib2.urlopen(url, data)
            res =  u.read() 
            if res=='err':
                raise ErrorHistoric('salvataggio storage')
            print err
            return HttpResponse("ok")
        else:
            form = HistoricForm()
        variables = RequestContext(request, {'form':form})
        return render_to_response('tissue2/historic/storico_CRL_tess.html',variables)
    except ErrorHistoric as e:
        print 'My exception occurred, value:', e.value
        transaction.rollback()
        return HttpResponse("err")
    except Exception,e:
        print 'err',e
        transaction.rollback()
        return HttpResponse("err")

#serve per caricare nel DB le aliquote vitali impiantate nei topi che sono stati
#recuperati dallo storico degli impianti
@transaction.commit_on_success
def HistoricXeno(request):
    try:
        if request.method=='POST':
            print request.POST
            print request.FILES  
            form=HistoricForm(request.FILES)
            
            #if form.is_valid():
            #percorso=os.path.join(os.path.dirname(__file__),'tissue_media/Historical/DateImpianti.txt')
            #f = open('C:/Documents and Settings/x/Documenti/Tesi/Collection.csv')
            #print 'perc',percorso
            #f=open(percorso)
            f=request.FILES.get('file')
            '''for a in f.chunks():
                #per cancellare eventuali \n alla fine del file
                a=a.strip()'''
            lines = f.readlines()
            f.close()
            lista=[]
            diz={}
            k=0
            print 'lines',lines
            for line in lines:
                valori=line.split('\t')
                codice=valori[2].strip()
                data=valori[3].strip()
                
                tumore=codice[0:3]
                #devo prendere il caso
                caso=codice[3:7]
                print 'caso',caso
                print 'tum',tumore
    
                tum=CollectionType.objects.get(abbreviation=tumore)
                cas=int(caso)
                #verifico se il caso c'e' gia'
                coll=Collection.objects.filter(Q(idCollectionType=tum)&Q(itemCode=cas))
                if coll.count()==0:
                    #raise ErrorHistoric(caso)
                    lista.append(tumore+' '+caso)
                coll=Collection.objects.get(Q(idCollectionType=tum)&Q(itemCode=cas))
                #salvo la serie
                ser,creato=Serie.objects.get_or_create(operator='None',
                                                       serieDate=data)
                print 'ser',creato
                #prendo la sorgente
                sorg=Source.objects.get(Q(name=coll.idSource.name)&Q(type='Hospital'))
                print 'sorg',sorg
                t=codice[7:9]
                tessuto_esp=TissueType.objects.get(abbreviation=t)
                #salvo il campionamento
                campionamento,creato=SamplingEvent.objects.get_or_create(idTissueType=tessuto_esp,
                                             idCollection=coll,
                                             idSource=sorg,
                                             idSerie=ser,
                                             samplingDate=data)
                print 'camp',campionamento
                print 'creato',creato
                tipoaliq=codice[20:22]
                tipoaliquota= AliquotType.objects.get(abbreviation=tipoaliq)
                print 'tipo aliquota',tipoaliq
                gen=str(codice)
                a,creato=Aliquot.objects.get_or_create(uniqueGenealogyID=gen,
                       idSamplingEvent=campionamento,
                       idAliquotType=tipoaliquota,
                       timesUsed=0,
                       availability=0,
                       derived=0
                       )
                print 'a',a
                if(diz.has_key(gen)):
                    valore=diz.pop(gen)
                    diz[gen]=valore+1
                #se il tasto non e' nella mappa lo inserisco
                else:
                    diz[gen]=1
                #k+=1
                #if k==4:
                #    break
            print 'diz',diz
            for key,val in diz.items():
                aliq=Aliquot.objects.get(uniqueGenealogyID=key)
                #salvo il numero di pezzi
                fea=Feature.objects.get(Q(idAliquotType=tipoaliquota)&Q(name='NumberOfPieces'))
                aliqfeature=AliquotFeature(idAliquot=aliq,
                                           idFeature=fea,
                                           value=val)
                aliqfeature.save()    
                
            #print 'lista',lista
            return HttpResponse("ok")  
            #else:
                #variables = RequestContext(request, {'form':form})
                #return render_to_response('tissue2/historic/storico.html',variables)
        else:
            form = HistoricForm()
        variables = RequestContext(request, {'form':form})
        return render_to_response('tissue2/historic/storico.html',variables)
    except ErrorHistoric as e:
        print 'My exception occurred, value:', e.value
        transaction.rollback()
        return HttpResponse("err")
    except Exception,e:
        print 'err',e
        transaction.rollback()
        return HttpResponse("err")  

#per fare un controllo sulla coerenza tra l'id dell'espianto e il relativo genid
#collegato    
@transaction.commit_on_success
def HistoricExplants(request):
    try:
        if request.method=='POST':
            print request.POST
            print request.FILES  
            form=HistoricForm(request.FILES)
            listafile=request.FILES.getlist('file')
            
            #e' il file archive_tissue
            f1=listafile[0]
            lines = f1.readlines()
            f1.close()
            
            #e' il file per le serie di collezionamento
            f2=listafile[1]
            serie_coll = f2.readlines()
            f2.close()
            
            
            #ricordarsi della colonna in piu' nel file, la colonna CHECK
            
            #e' il file degli espianti con l'indicazione del genid
            f3=listafile[2]
            espianti= f3.readlines()
            f3.close()
            
            #e' il file delle serie degli espianti con la data
            f4=listafile[3]
            serie_esp= f4.readlines()
            f4.close()
            
            espr_esp=re.compile('(EXPL[a-zA-Z0-9]+)$')
            nserie=''
            ser_esp=''
            operat_camp=''
            dat_camp=''
            operat_esp=''
            dat_esp=''
            data_appoggio=''
            stringa=''
            lista_expl=[]
            
            k=0
            jj=0
            for espi in espianti:
                val_esp=espi.split(';')
                id_esp=val_esp[0]
                gen_esp=val_esp[2]
                if gen_esp in lista_expl:
                    print 'duplicato',id_esp
                    stringa+=val_esp[0]+': genid duplicato '+gen_esp+'\n'
                else:
                    lista_expl.append(gen_esp)
                num_ff=val_esp[7]
                num_vt=val_esp[8]
                num_rl=val_esp[9]
                num_sf=val_esp[10]
                if num_ff!='':
                    num_ff=int(num_ff)
                else:
                    num_ff=0
                if num_vt!='':
                    num_vt=int(num_vt)
                else:
                    num_vt=0
                if num_rl!='':
                    num_rl=int(num_rl)
                else:
                    num_rl=0
                if num_sf!='':
                    num_sf=int(num_sf)
                else:
                    num_sf=0
                num_tot=num_ff+num_vt+num_rl+num_sf
                num_pezzi=0
                #print espi
                contatore=0
                for line in lines:
                    valori=line.split(';')
                    explid=valori[3]
                    
                    if explid==id_esp:
                        num_pezzi=valori[22].strip()
                        if num_pezzi!='':
                            num_pezzi=int(num_pezzi)
                        else:
                            num_pezzi=100
                        contatore+=num_pezzi
                        #print 'cont',contatore
                #if num_tot!=contatore and num_pezzi!=0:
                    #stringa+=val_esp[0]+': numero pezzi tess: '+str(contatore)+'num pezzi espianti: '+str(num_tot)+'\n'
                #jj+=1
                #if jj==140:
                    #break
                
            for line in lines:
                valori=line.split(';')
                #guardo la serie in modo da avere la data del collezionamento
                chiave_serie=valori[1]
                
                explid=valori[3]
                #prendo gli ultimi quattro caratteri della stringa
                num_serie=chiave_serie[-4:]
                #prendo la data di creazione dei campioni
                if nserie!=num_serie:
                    nserie=num_serie
                    for serie in serie_coll:
                        val=serie.split(';')
                        num=val[0]
                        n=num[-4:]
                        if n==num_serie:
                            operat_camp=val[1]
                            dat=val[2]
                            d=dat.split('/')
                            dat_camp=datetime.date(int(d[2]),int(d[1]),int(d[0]))
                            #print 'data camp',dat_camp

                #print 'esp_esp',explid
                if espr_esp.match(explid):
                    gen_id_15=valori[2]
                    #print 'gen id',gen_id_15
                    for espi in espianti:
                        val_esp=espi.split(';')
                        id_esp=val_esp[0]
                        #se l'id dell'espianto coincide con quello che c'e' nel file
                        #dei tessuti
                        if explid==id_esp:
                            #prendo il genid nel file degli espianti 
                            gen_esp=val_esp[2]
                            if gen_id_15!=gen_esp:
                                print 'err gen', valori[0]+' '+gen_id_15
                                stringa+=valori[0]+': il genid della colonna C di ArchiveTissue.xls non corrisponde con il gen della colonna C di Explants.xls\n'
                            #faccio adesso il controllo tra la data dell'espianto e
                            #quella di creazione dei campioni
                            serie_espianto=val_esp[1]
                            #prendo la data di creazione dei campioni
                            if ser_esp!=serie_espianto:
                                ser_esp=serie_espianto
                                for serie in serie_esp:
                                    val=serie.split(';')
                                    num=val[0]
                                    if num==serie_espianto:
                                        operat_esp=val[1]
                                        dat2=val[2]
                                        d=dat2.split('/')
                                        dat_esp=datetime.date(int(d[2]),int(d[1]),int(d[0]))
                                        giorni=datetime.timedelta(days=2)
                                        #aggiungo due giorni alla data attuale
                                        data_appoggio=dat_esp+giorni
                                        #print 'data esp',data_appoggio
                            #se la data di campionamento e' oltre due giorni dopo 
                            #quella di espianto o e' prima di quella dell'espianto,
                            #allora c'e' un errore.
                            #if dat_camp>data_appoggio or dat_camp<dat_esp:
                                #print 'errore data',valori[0]+' '+gen_id_15
                                #stringa+=valori[0]+' problemi sulle date. Data espianto: '+dat2+' Data serie aliquote: '+dat+'\n'
                            #se serve eseguo anche un controllo sugli operatori,
                            #guardando se chi ha fatto l'espianto e' anche quello
                            #che ha fatto la serie di aliquote
                            #if operat_camp.lower()!=operat_esp.lower():
                                #print 'err operatore',valori[0]+' '+gen_id_15
                                #stringa+=valori[0]+' problemi con gli operatori. Operatore espianto: '+operat_esp.lower()+' Operatore serie aliquote: '+operat_camp+'\n'
                            
                k+=1
                if k==2:
                    break
            stringa+='\n'
            
            f2=open(os.path.join(os.path.dirname(__file__),'tissue_media/Historical/Err_explants3.txt'),'w')
            f2.write(stringa)
            f2.close()
            return HttpResponse("ok")
        else:
            form = HistoricForm()    
        variables = RequestContext(request, {'form':form})
        return render_to_response('tissue2/historic/storico_expl.html',variables)
    except ErrorHistoric as e:
        print 'My exception occurred, value:', e.value
        transaction.rollback()
        return HttpResponse("err")
    except Exception,e:
        print 'err',e
        transaction.rollback()
        return HttpResponse("err")

#per fare un controllo sulla correttezza nella creazione del genid del topo
#impiantato 
@transaction.commit_on_success
def HistoricImplants(request):
    try:
        if request.method=='POST':
            print request.POST
            print request.FILES  
            form=HistoricForm(request.FILES)
            listafile=request.FILES.getlist('file')
            
            #e' il file degli impianti
            
            
            #ricordarsi della colonna in piu' nel file, la colonna CHECK
            
            f1=listafile[0]
            lines = f1.readlines()
            f1.close()
            
            #e' il file per le serie di impianti
            f2=listafile[1]
            serie_impl = f2.readlines()
            f2.close()
            
            #e' il file degli espianti
            
            #ricordarsi della colonna in piu' nel file, la colonna CHECK
            f3=listafile[2]
            espianti= f3.readlines()
            f3.close()
            
            #e' il file delle serie degli espianti con la data
            f4=listafile[3]
            serie_esp= f4.readlines()
            f4.close()
            
            tumori=CollectionType.objects.all()
            tessuti=TissueType.objects.all()
            tipi_aliq=AliquotType.objects.all()
            cas_generico=re.compile('(\d\d\d)$')
            umano=re.compile('(X|H)$')
            topo=re.compile('([A-Za-z]\d\d\d\d\d)$')
            uomo=re.compile('(00000(0)*)$')
            
            espr_esp=re.compile('(EXPL[a-zA-Z0-9]+)$')
            ser_impl=''
            ser_esp=''
            operat_camp=''
            dat_impl=''
            operat_esp=''
            dat_esp=''
            data_appoggio=''
            lista_impl=[]
            stringa=''
            
            k=0
            for line in lines:
                valori=line.split(';')
                gen_origine=valori[5]
                gen_impl=valori[3]
                
                tum=gen_origine[0:3]
                trovato=False
                for i in range(0,len(tumori)):
                    if tum==str(tumori[i].abbreviation):
                        trovato =True
                        break; 
                #if trovato==False:
                    #print 'tumore non trovato '+gen_origine+' '+valori[0]      
                if trovato==True:
                    #serve per valutare il codice del caso
                    caso=gen_origine[3:6]
                    if not cas_generico.match(caso):
                        print 'err caso'+caso+' '+valori[0]
                    #serve per valutare il codice del tessuto
                    tess=gen_origine[6:8]
                    trovato2=False
                    for i in range(0,len(tessuti)):
                        if tess==str(tessuti[i].abbreviation):
                            trovato2 =True
                            break;                             
                    if trovato2==False:
                        print 'err tessuto'+tess+' '+valori[0]
                    #serve per valutare l'H o la X
                    tipo=gen_origine[8:9]
                    #print 'tipo',tipo
                    if not umano.match(tipo):
                        print 'err tipo H/X '+tipo+' '+valori[0]
                        stringa+=valori[0]+': errore nel genid del topo di origine\n'
                    parte_centr=gen_origine[9:15]
                    #serve per valutare i 6 valori dopo l'H o la X  
                    if tipo=='X':
                        #if not topo.match(parte_centr):
                            #print 'err topo '+tipo+' '+valori[0]
                        #devo vedere se il gen id dell'impianto e' stato creato bene
                        #costruisco il nuovo gen id da confrontare con quello che 
                        #prendo dal file Excel
                        contatore=int(gen_origine[10:12])
                        contatore+=1
                        if contatore<10:
                            cont='0'+str(contatore)
                        else:
                            cont=str(contatore)
                        confr_gen=gen_origine[0:10]+cont
                        if confr_gen!=gen_impl[0:12]:
                            #print 'err incremento contatore topo '+confr_gen+' '+valori[0]
                            stringa+=valori[0]+': errore nella creazione del genid del topo impiantato\n'
                  
                    elif tipo=='H':
                        if not uomo.match(parte_centr):
                            print 'err uomo '+tipo+' '+valori[0]
                        confr_gen1=gen_origine[0:8]+'XA01'
                        confr_gen2=gen_origine[0:8]+'XB01'
                        if confr_gen1!=gen_impl[0:12] and confr_gen2!=gen_impl[0:12]:
                            #print 'err incremento contatore uomo '+gen_impl+' '+valori[0]
                            stringa+=valori[0]+': errore nella creazione del genid del topo impiantato\n'
                    #controllo i duplicati nel gen del topo figlio
                    if gen_impl in lista_impl:
                            print 'err gen duplicato '+gen_impl+' '+valori[0]
                            stringa+=valori[0]+': genid del topo impiantato duplicato\n'
                    else:
                        lista_impl.append(gen_impl)
                #passo alla verifica di coerenza delle date di espianto con quelle di
                #impianto. Solo per gli impianti freschi
                #prendo la data di impianto
                imp_serie=valori[1]
                imp_serie=imp_serie.replace('-','')
                for ser in serie_impl:
                    val=ser.split(';')
                    #devo vedere se l'impianto e' fresco o congelato
                    tipo_impl=val[7]
                    if tipo_impl.lower()=='fresh':
                        num=val[0]
                        if num==imp_serie:
                            dat=val[2]
                            d=dat.split('/')
                            dat_impl=datetime.date(int(d[2]),int(d[1]),int(d[0]))
                            for espi in espianti:
                                val_esp=espi.split(';')
                                id_esp=val_esp[0]                    
                                #prendo il genid nel file degli espianti 
                                gen_esp=val_esp[2]
                                #verifico che il genid dell'espianto nei due file sia lo stesso
                                if gen_esp==gen_origine:
                                    #faccio adesso il controllo tra la data dell'espianto e
                                    #quella di impianto
                                    for serie in serie_esp:
                                        val=serie.split(';')
                                        num=val[0]
                                        if num==val_esp[1]:
                                            operat_esp=val[1]
                                            dat2=val[2]
                                            d=dat2.split('/')
                                            dat_esp=datetime.date(int(d[2]),int(d[1]),int(d[0]))
                                            giorni=datetime.timedelta(days=2)
                                            #aggiungo due giorni alla data attuale
                                            data_appoggio=dat_esp+giorni
                                            #print 'data esp',data_appoggio
                                            #se la data di impianto e' oltre due giorni dopo 
                                            #quella di espianto o e' prima di quella dell'espianto,
                                            #allora c'e' un errore.
                                            #print 'dat_impl',dat_impl
                                            #print 'dat_esp',dat_esp
                                            if dat_impl>data_appoggio or dat_impl<dat_esp:
                                                print 'errore data',valori[0]+' '+gen_esp
                                                stringa+=valori[0]+': problemi sulle date. Data espianto: '+str(dat2)+' Data impianto: '+str(dat)+'\n'
                                                print 'dat_impl',dat
                                                print 'dat_esp',dat2
                k+=1
                #if k==4:
                    #break
            
                
            f2=open(os.path.join(os.path.dirname(__file__),'tissue_media/Historical/Err_implants3.txt'),'w')
            f2.write(stringa)
            f2.close()
            return HttpResponse("ok")
        else:
            form = HistoricForm()    
        variables = RequestContext(request, {'form':form})
        return render_to_response('tissue2/historic/storico_impl.html',variables)
    except ErrorHistoric as e:
        print 'My exception occurred, value:', e.value
        transaction.rollback()
        return HttpResponse("err")
    except Exception,e:
        print 'err',e
        transaction.rollback()
        return HttpResponse("err")

#per salvare le aliquote di origine degli impianti storici
@transaction.commit_on_success
def HistoricSaveAliquotImplants(request):
    try:
        if request.method=='POST':
            print request.POST
            print request.FILES  
            form=HistoricForm(request.FILES)
            listafile=request.FILES.getlist('file')
            
            #e' il file degli impianti 
            f1=listafile[0]
            imp = f1.readlines()
            f1.close()
            
            #e' il file per le serie di impianti
            f2=listafile[1]
            serie_impl = f2.readlines()
            f2.close()
            
            diz={}
            k=0
            barc_da_svuotare=''
            for linee in imp:
                valori=linee.split(';')
                #e' il gen dell'aliq da salvare
                codice=valori[7].strip()
                #guardo se e' una vt99 o no
                contatore=codice[22:24]
                print 'cont',contatore
                if contatore=='99':
                    listal=Aliquot.objects.filter(uniqueGenealogyID=codice)
                    if len(listal)==0:
                        imp_serie=valori[1].strip()
                        imp_serie=imp_serie.replace('-','')
                        operatore=''
                        data=''
                        for ser in serie_impl:
                            val=ser.split(';')
                            num=val[0]
                            if num==imp_serie:
                                oper=val[1]
                                if oper=='ZANELLA':
                                    operatore='eugenia.zanella'
                                elif oper=='MIGLIARDI':
                                    operatore='giorgia.migliardi'
                                elif oper=='TORTI':
                                    operatore='davide.torti'
                                dat=val[2]
                                d=dat.split('/')
                                data=d[2]+'-'+d[1]+'-'+d[0]
                                break
                        
                        tumore=codice[0:3]
                        #devo prendere il caso
                        caso=codice[3:7]
                        print 'caso',caso
                        print 'tum',tumore
            
                        tum=CollectionType.objects.get(abbreviation=tumore)
                        cas=int(caso)
                        #verifico se il caso c'e' gia'
                        coll=Collection.objects.filter(Q(idCollectionType=tum)&Q(itemCode=cas))
                        if coll.count()==0:
                            raise ErrorHistoric(caso)
                            #lista.append(tumore+' '+caso)
                        coll=Collection.objects.get(Q(idCollectionType=tum)&Q(itemCode=cas))
                        #salvo la serie
                        ser,creato=Serie.objects.get_or_create(operator=operatore,
                                                               serieDate=data)
                        print 'ser',creato
                        #prendo la sorgente
                        sorg=Source.objects.get(Q(name=coll.idSource.name)&Q(type='Hospital'))
                        print 'sorg',sorg
                        t=codice[7:9]
                        tessuto_esp=TissueType.objects.get(abbreviation=t)
                        #salvo il campionamento
                        campionamento,creato=SamplingEvent.objects.get_or_create(idTissueType=tessuto_esp,
                                                     idCollection=coll,
                                                     idSource=sorg,
                                                     idSerie=ser,
                                                     samplingDate=data)
                        print 'camp',campionamento
                        tipoaliq=codice[20:22]
                        tipoaliquota= AliquotType.objects.get(abbreviation=tipoaliq)
                        print 'tipo aliquota',tipoaliq
                        gen=str(codice)
                        a,creato=Aliquot.objects.get_or_create(uniqueGenealogyID=gen,
                               idSamplingEvent=campionamento,
                               idAliquotType=tipoaliquota,
                               timesUsed=0,
                               availability=0,
                               derived=0)
                        print 'a',a
                        if(diz.has_key(gen)):
                            valore=diz.pop(gen)
                            diz[gen]=valore+1
                        #se il tasto non e' nella mappa lo inserisco
                        else:
                            diz[gen]=1
                
                else:
                    #devo rendere indisponibile l'aliquota in questione
                    aliq=Aliquot.objects.get(uniqueGenealogyID=codice)
                    print 'aliq',aliq
                    aliq.availability=0
                    barc_da_svuotare=barc_da_svuotare+aliq.barcodeID+'&'
                    aliq.save()
                        
                    
                #k+=1
                #if k==2:
                    #break
            print 'diz',diz
            for key,val in diz.items():
                aliq=Aliquot.objects.get(uniqueGenealogyID=key)
                #salvo il numero di pezzi
                fea=Feature.objects.get(Q(idAliquotType=tipoaliquota)&Q(name='NumberOfPieces'))
                aliqfeature,creato=AliquotFeature.objects.get_or_create(idAliquot=aliq,
                                           idFeature=fea,
                                           value=val)  
                
            print 'listastor',barc_da_svuotare
            if barc_da_svuotare!='':
                #mi collego allo storage per svuotare le provette contenenti le aliq
                #esaurite
                address=Urls.objects.get(default=1).url
                url = address+"/full/"
                print url
                values = {'lista' : barc_da_svuotare, 'tube': 'empty','canc':True}
                data = urllib.urlencode(values)
                req = urllib2.Request(url,data=data, headers={"workingGroups" : get_WG_string()})
                urllib2.urlopen(req)
                #urllib2.urlopen(url, data)
            
            return HttpResponse("ok")
        else:
            form = HistoricForm()
        variables = RequestContext(request, {'form':form})
        return render_to_response('tissue2/historic/storico_save_impl.html',variables)
    except ErrorHistoric as e:
        print 'My exception occurred, value:', e.value
        transaction.rollback()
        return HttpResponse("err")
    except Exception,e:
        print 'err',e
        transaction.rollback()
        return HttpResponse("err")

#serve per caricare nel DB i derivati storici presi dal file Excel
@transaction.commit_on_success
def HistoricDerived(request):
    try:
        if request.method=='POST':
            print request.POST
            print request.FILES
            form=HistoricForm(request.FILES)
            
            listafile=request.FILES.getlist('file')
            
            #e' il file archive_derivatives
            f1=listafile[0]           
            lines = f1.readlines()
            f1.close()

            #e' il file per le serie di derivazione
            f2=listafile[2]            
            series = f2.readlines()
            f2.close()
            
            #e' il file archive_container da cui ricavo il barcode del box
            f3=listafile[1]
            contain= f3.readlines()
            f3.close()
            
            #e' il file summary per le aliquote nelle piastre Thermo
            f4=listafile[3]
            aliq_summ= f4.readlines()
            f4.close()
            
            #e' il file transfevent per gli eventi di derivazione
            f5=listafile[4]
            eventi_trasf= f5.readlines()
            f5.close()
            
            #e' il file archive_tissue
            f6=listafile[5]
            linee_tess = f6.readlines()
            f6.close()
            
            tumori=CollectionType.objects.all()
            tessuti=TissueType.objects.all()
            tipi_aliq=re.compile('(D|R)$')
            cas_generico=re.compile('(0\d\d\d)$')
            cas_thermo=re.compile('(\d\d\d)$')
            umano=re.compile('(X|H)$')
            topo_thermo=re.compile('(0[A-Za-z]\d\d\d\d\d000)$')
            topo_corto=re.compile('([A-Za-z]\d\d\d\d\d)$')
            uomo_corto=re.compile('(000000)$')
            uomo_thermo=re.compile('(0000000000)$')
            contatore=re.compile('(\d\d\d\d\d)$')
            cont_archivio=re.compile('(\d\d[DR]\d\d)$')
            rack_box=re.compile('(\d)+$')
            pos=re.compile('([A-Ja-j]\d\d*)$')
            store=re.compile('(Store00\d)$')
            
            err=''
            #riempio un dizionario in cui ad ogni gen id del file summary.csv e'
            #associata l'indicazione se c'e' una corrispondenza nel file archive_tissue
            dizio={}
            for righe_aliq in aliq_summ:
                rig=righe_aliq.split('\t')
                gen_id_prova=rig[0].strip()
                dizio[gen_id_prova]='0'
                #serve per valutare il codice del tumore
                tum=gen_id_prova[0:3]
                trovato=False
                for i in range(0,len(tumori)):
                    if tum==str(tumori[i].abbreviation):
                        trovato =True
                        break; 
                if trovato==False:
                    err+=gen_id_prova+': tumore inesistente. '+rig[5]
                    continue
                #serve per valutare il codice del caso
                #il problema e' che alcuni hanno 3 cifre altri 4
                caso=gen_id_prova[3:7]
                partenza=7
                if not cas_generico.match(caso):
                    caso2=gen_id_prova[3:6]
                    partenza=6
                    if not cas_thermo.match(caso2):
                        err+=gen_id_prova+': caso errato. '+rig[5]
                        continue
                #serve per valutare il codice del tessuto
                tess=gen_id_prova[partenza:partenza+2]
                trovato2=False
                for i in range(0,len(tessuti)):
                    if tess==str(tessuti[i].abbreviation):
                        trovato2 =True
                        break;                             
                if trovato2==False:
                    err+=gen_id_prova+': tessuto inesistente. '+rig[5]
                    continue
                #serve per valutare l'H o la X
                tipo=gen_id_prova[partenza+2:partenza+3]
                #print 'tipo',tipo
                if not umano.match(tipo):
                    err+=gen_id_prova+': Problema su X/H. '+rig[5]
                    continue
                parte_centr=gen_id_prova[partenza+3:partenza+9]
                #serve per valutare i 6 valori dopo l'H o la X
                if tipo=='X':
                    delta=9
                    if not topo_corto.match(parte_centr):
                        parte_centr=gen_id_prova[partenza+3:partenza+13]
                        delta=13
                        if not topo_thermo.match(parte_centr):
                            err+=gen_id_prova+': Problema su codice topo. '+rig[5]
                        continue
                elif tipo=='H':
                    delta=9
                    if not uomo_corto.match(parte_centr):
                        #err+=gen_id_prova+': Problema sul numero di zeri dopo H. '+rig[4]
                        continue
                #serve per valutare il tipo di aliq (D,R...)
                tipo_al=gen_id_prova[partenza+delta:partenza+delta+1]
                if not tipi_aliq.match(tipo_al):
                    err+=gen_id_prova+': Problema sul tipo di aliquota (D,R,...). '+rig[4]
                    continue
                #serve per valutare il contatore finale del genid
                cont=gen_id_prova[partenza+delta+1:partenza+delta+6]
                if not contatore.match(cont):
                    err+=gen_id_prova+': Problema sul contatore finale. '+rig[5]
                    continue
            print err
            #file=open(os.path.join(os.path.dirname(__file__),'tissue_media/Historical/ErrAliquotsder.txt'),'w')
            #file.write(err)
            #file.close()
            #salvo prima tutte le serie presenti nel file e poi dopo le richiamo quando
            #salvo il sampling event
            for serie in series:
                val=serie.split(';')
                oper=val[1].strip()
                if oper=='Zanella':
                    operatore='eugenia.zanella'
                elif oper=='Porporato':
                    operatore='roberta.porporato'
                elif oper=='Galimi':
                    operatore='francesco.galimi'
                print 'operatore',operatore
                data=val[2]
                print 'data',data
                d=data.split('/')
                print 'd',d[0]
                dat=d[2]+'-'+d[1]+'-'+d[0]
                print 'dat',dat
                se,creato=Serie.objects.get_or_create(operator=operatore,
                                                      serieDate=dat)
            
            
            nserie=''
            operat=''
            data=''
            j=0
            lista_archivio=''
            for kk in range(0,len(lines)):
                line=lines[kk]
                line=line.strip()
                valori=line.split(';')
                gen=valori[2]
                '''sto=valori[14]
                rack=valori[15]
                box=valori[16]
                posiz=valori[17]
                #print 'posiz',posiz
                if sto!='':
                    if not store.match(sto):
                        print 'store',line
                    if not rack_box.match(rack):
                        print 'rack',line
                    if not rack_box.match(box):
                        print 'box',line
                    if not pos.match(posiz):
                        print 'pos',line'''
                        
                
                if gen=="":
                    raise ErrorHistoric(valori[0])
                if len(gen)!=26:
                    print 'lung gen',line
                    #raise ErrorHistoric(gen+' '+line)
                #serve per valutare il codice del tumore
                tum=gen[0:3]
                trovato=False
                for i in range(0,len(tumori)):
                    if tum==str(tumori[i].abbreviation):
                        trovato =True
                        break; 
                if trovato==False:
                    print 'tumore',line
                    #raise ErrorHistoric(gen+' '+line)
                #serve per valutare il codice del caso
                caso=gen[3:7]
                if not cas_generico.match(caso):
                    print 'caso',line
                    #raise ErrorHistoric(gen+' '+line)
                #serve per valutare il codice del tessuto
                tess=gen[7:9]
                trovato2=False
                for i in range(0,len(tessuti)):
                    if tess==str(tessuti[i].abbreviation):
                        trovato2 =True
                        break;                             
                if trovato2==False:
                    print 'tessuto',line
                    #raise ErrorHistoric(gen+' '+line)
                #serve per valutare l'H o la X
                tipo=gen[9:10]
                #print 'tipo',tipo
                if not umano.match(tipo):
                    print 'umano',line
                    #raise ErrorHistoric(gen+' '+line)
                parte_centr=gen[10:20]
                #serve per valutare i nove valori dopo l'H o la X
                if tipo=='X':
                    if not topo_thermo.match(parte_centr):
                        print 'problema X',line
                        #raise ErrorHistoric(gen+' '+line)
                elif tipo=='H':
                    if not uomo_thermo.match(parte_centr):
                        print 'problema H',line
                        #raise ErrorHistoric(gen+' '+line) 
                
                #serve per valutare il contatore finale del genid
                cont=gen[18:23]
                if not cont_archivio.match(cont):
                    print 'contatore',line
                    #raise ErrorHistoric(gen+' '+line)
                
                #prendo la collezione
                tumore=CollectionType.objects.get(abbreviation=tum)
                cas=int(caso)
                coll2=Collection.objects.filter(Q(idCollectionType=tumore)&Q(itemCode=cas))
                if coll2.count()!=1:
                    raise ErrorHistoric(gen+' '+line)
                coll=coll2[0]
                #prendo il tipo di tessuto
                tessuto=TissueType.objects.get(abbreviation=tess)
                #prendo il trasf event
                chiave_trasf=valori[1]
                trovato=0
                trov2=0
                operatore=''
                data=''
                gen_madre=''
                origine=''
                val_eventi=''
                for trasf in eventi_trasf:
                    line2=trasf.strip()
                    val_eventi=line2.split(';')
                    chiave_tr=val_eventi[0]
                    trovato=0
                    if chiave_tr==chiave_trasf:
                        trovato=1
                        chiave_serie=val_eventi[1]
                        #prendo l'aliquota madre
                        gen_madre=val_eventi[6]
                        origine=val_eventi[3]
                        trov2=0
                        for serie in series:
                            val=serie.split(';')
                            ch_ser=val[0]
                            if chiave_serie==ch_ser:
                                trov2=1
                                oper=val[1]
                                if oper=='Zanella':
                                    operatore='eugenia.zanella'
                                elif oper=='Porporato':
                                    operatore='roberta.porporato'
                                elif oper=='Galimi':
                                    operatore='francesco.galimi'
                                dat=val[2]
                                d=dat.split('/')
                                data=d[2]+'-'+d[1]+'-'+d[0]
                                break
                    if trov2==1:
                        break
                #if trovato==0 or trov2==0:
                    #print 'problema serie',chiave_tr+' '+line
                serie_def=Serie.objects.get(Q(operator=operatore)&Q(serieDate=data))
                #print 'serie',serie_def
                tipo_al=valori[6].strip()
                #mi occupo del tipo di aliq figlia (DNA,RNA...)
                ti_aliq=AliquotType.objects.get(abbreviation=tipo_al)
                #salvo solo il DNA e l'RNA e i campioni non presenti nelle piastre diatech
                piastra=valori[5].strip().lower()
                if piastra!='':
                    val_pias=piastra[0:7]
                else:
                    val_pias=''

                if val_pias!='diatech':
                    
                    #salvo il derivation schedule
                    der_sched,creato=DerivationSchedule.objects.get_or_create(scheduleDate=data,
                                                                              operator=operatore)
                    #salvo il sampling event
                    samp_ev,creato=SamplingEvent.objects.get_or_create(idTissueType=tessuto,
                                                                idCollection=coll,
                                                                idSource=coll.idSource,
                                                                idSerie=serie_def,
                                                                samplingDate=data)
                    #trasformo il gen della madre nel formato salvato nella biobanca
                    #print 'gen_madre[8:9]',gen_madre[8:9]
                    #if gen_madre[8:9]=='X':
                    #    gen_madre_def=gen_madre[0:3]+'0'+gen_madre[3:9]+'0'+gen_madre[9:12]+'2'+gen_madre[13:15]+'TUM'+gen_madre[15:]+'00'
                    #elif gen_madre[8:9]=='H':
                    #    gen_madre_def=gen_madre[0:3]+'0'+gen_madre[3:15]+'0000'+gen_madre[15:]+'00'
                    #print 'gen_def',gen_madre_def
                    
                    #devo aggiungere il TUM
                    gen_madre_def=gen_madre[0:17]+'TUM'+gen_madre[20:]
                    
                    l_aliq=Aliquot.objects.filter(uniqueGenealogyID=gen_madre_def)
                    if len(l_aliq)!=0:
                        aliq=l_aliq[0]
                    else:
                        #prima di crearla, provo a vedere se c'e' una madre che ha il 2 dello storico
                        gen_madre_def=gen_madre[0:14]+'2'+gen_madre[15:17]+'TUM'+gen_madre[20:]
                        l_aliq=Aliquot.objects.filter(uniqueGenealogyID=gen_madre_def)
                        if len(l_aliq)!=0:
                            aliq=l_aliq[0]
                        else:
                            #vuol dire che devo creare l'aliquota madre perche' non esiste
                            tip_al=AliquotType.objects.get(abbreviation='RNA')
                            aliq=Aliquot(uniqueGenealogyID=gen_madre_def,
                                       idSamplingEvent=samp_ev,
                                       idAliquotType=tip_al,
                                       availability=0,
                                       timesUsed=0,
                                       derived=0)
                            aliq.save()
                            
                            #salvo il numero di pezzi. Ha senso solo se la madre e' RL
                            '''fea=Feature.objects.get(Q(idAliquotType=tip_al)&Q(name='NumberOfPieces'))
                            aliqfeature=AliquotFeature(idAliquot=aliq,
                                                       idFeature=fea,
                                                       value=1)
                            aliqfeature.save()'''
                        
                    tipo_madre=AliquotType.objects.get(id=aliq.idAliquotType.id)
                    
                    #devo prendere il protocollo di derivazione
                    der_prot=DerivationProtocol.objects.filter(name__istartswith=tipo_al)
                    if len(der_prot)!=0:
                        d_prot=der_prot[0]
                    else:
                        print 'problema sul prot. di derivazione', line
                    
                    #salvo la quantita' presa dalla madre
                    quant=val_eventi[10].strip()
                    #print 'quant',quant
                    if quant!='':
                        quant=float(quant)
                    else:
                        quant=None

                    fallit=val_eventi[11]
                    if fallit=='0':
                        fallita=1
                    elif fallit=='1':
                        fallita=0

                    #vedo se l'aliq madre e' esaurita o meno
                    if aliq.availability==0:
                        esausta=1
                    else:
                        esausta=0
                        
                    
                    al_der_sch,creato=AliquotDerivationSchedule.objects.get_or_create(idAliquot=aliq,
                                                         idDerivationSchedule=der_sched,
                                                         idDerivedAliquotType=ti_aliq,
                                                         idDerivationProtocol=d_prot,
                                                         derivationExecuted=1,
                                                         operator=operatore,
                                                         loadQuantity=quant,
                                                         failed=fallita,
                                                         initialDate=data,
                                                         measurementExecuted=1,
                                                         aliquotExhausted=esausta)
                    #print 'al der sche',al_der_sch
                    #mi occupo delle misure effettuate sulla madre. Salvo il quality
                    #event solo se sono state effettivamente compiute delle misure.
                    qualita=valori[10].strip()
                    purezza=valori[11].strip()
                    concmadre=valori[19].strip()
                    pur230=valori[20].strip()
                    if qualita!='' or purezza!='' or concmadre!='' or pur230!='':
                        #Prendo il quality protocol che e' il protocollo di misurazione
                        #che varia a seconda del tipo di derivato
                        #print 'tipo figlia',ti_aliq
                        qual_prot=QualityProtocol.objects.get(idAliquotType=ti_aliq)
                        
                        qual_ev,creato=QualityEvent.objects.get_or_create(idQualityProtocol=qual_prot,
                                             idAliquot=aliq,
                                             idAliquotDerivationSchedule=al_der_sch,
                                             misurationDate=data,
                                             operator=operatore)
                        #salvo piu' oggetti perche' un'aliq potrebbe avere piu' misurazioni
                        if qualita!='':
                            qual=qualita.replace(',','.')
                            mis_qual=Measure.objects.get(name='quality')
                            mes_ev,creato=MeasurementEvent.objects.get_or_create(idMeasure=mis_qual,
                                                                          idQualityEvent=qual_ev,
                                                                          value=float(qual))
                        if purezza!='':
                            pur=purezza.replace(',','.')
                            mis_pur=Measure.objects.get(Q(name='purity')&Q(measureUnit='260/280'))
                            mes_ev,creato=MeasurementEvent.objects.get_or_create(idMeasure=mis_pur,
                                                                          idQualityEvent=qual_ev,
                                                                          value=float(pur))
                        
                        if pur230!='':
                            pu230=pur230.replace(',','.')
                            mis_pu230=Measure.objects.get(Q(name='purity')&Q(measureUnit='260/230'))
                            mes_ev,creato=MeasurementEvent.objects.get_or_create(idMeasure=mis_pu230,
                                                                          idQualityEvent=qual_ev,
                                                                          value=float(pu230))
                        
                        if concmadre!='':
                            cmadre=concmadre.replace(',','.')
                            strum=Instrument.objects.get(name='BIOANALYZER')
                            mis_c=Measure.objects.get(Q(name='concentration')&Q(idInstrument=strum))
                            mes_ev,creato=MeasurementEvent.objects.get_or_create(idMeasure=mis_c,
                                                                          idQualityEvent=qual_ev,
                                                                          value=float(cmadre))
                    
                    #salvo il derivation event
                    der_ev,creato=DerivationEvent.objects.get_or_create(idSamplingEvent=samp_ev,
                                                                        idAliqDerivationSchedule=al_der_sch,
                                                                        derivationDate=data,
                                                                        operator=operatore)
                        
                    barcode=valori[4]
                    sto=valori[14]
                    rack=valori[15]
                    box=valori[16]
                    posiz=valori[17]
                    #prendo la piastra
                    pias=valori[5].strip()
                    evento=valori[1]
                    blocca=0
                    if pias!='':
                        inizio_pias=pias[0:7].lower()
                        #print 'pias',inizio_pias
                        if inizio_pias=='diatech':
                            blocca=1
                    #se il campione e' in una piastra diatech non lo salvo
                    if blocca==0:    
                        if sto!='':
                            barc_box_effettivo=''
                            for righe in contain:
                                rig=righe.split(';')
                                barc_store=rig[1]
                                barc_rack=rig[2]
                                barc_box=rig[3]
                                if barc_store==sto and barc_rack==rack and barc_box==box:
                                    barc_box_effettivo=rig[6]
                                    #devo vedere se la posizione e' espressa come un numero o come
                                    #lettera e numero
                                    if not pos.match(posiz):
                                        #per sapere le posizioni totali della piastra
                                        pos_tot=rig[5]
                                        #puo' essere 9 o 10
                                        riferimento=int(math.sqrt(int(pos_tot)))
                                        #print 'pos no',posiz
                                        #divido il numero per 9 e ottengo un valore da convertire in
                                        #lettera
                                        valore_num=int(int(posiz)/riferimento)
        
                                        #prendo il resto della divisione per 9 o 10 e quello e' il numero
                                        #da affiancare alla lettera
                                        numero=(int(posiz)%riferimento)
                                        if numero==0:
                                            numero=riferimento
                                            valore_num-=1
                                        #print 'val num',valore_num
                                        lettera=chr(valore_num+ord('A'))
                                        
                                        posiz=str(lettera)+str(numero)
                                        #print 'nuova_pos',posiz
                                    break
                            if barc_box_effettivo=='':
                                disp=0
                                pass
                                #print 'box non presente',sto+' '+rack+' '+box+' '+line
                                #raise ErrorHistoric(sto+' '+rack+' '+box+'  '+line)
                            else:
                                
                                #vedo se l'aliq e' disponibile
                                disponibile=valori[13].strip()
                                #print 'disponibile',valori[13]
                                if disponibile=='y' or disponibile=='Y' or disponibile=='':
                                    disp=1
                                    lista_archivio+=barc_box_effettivo+'|'+barcode+'|'+posiz+','
                                elif disponibile=='no':
                                    disp=0
                        #se sto trattando le aliq nuove nelle piastre Thermo
                        else:
                            #gen e' il gen lungo da 26 caratteri che c'e' nel file dei derivati
                            #gen1 e' il gen corto del DNA. 3 cifre per il caso, 1 per il
                            #lineage e senza il TUM
                            gen1=gen[0:3]+gen[4:10]+gen[11:17]+gen[20:]
                            #print 'gen1',gen1
                            #gen2 e' il gen corto ma con il contatore dell'aliquota alla 
                            #fine
                            gen2=gen1[0:17]+'10'+gen1[16:18]
                            #print 'gen2',gen2
                            #scandisco le righe del file summary.csv
                            for righe_aliq in aliq_summ:
                                rig=righe_aliq.split('\t')
                                genid_file=rig[0].strip()
                                trovato=0
                                if str(genid_file)==gen1 or str(genid_file)==gen or str(genid_file)==gen2:
                                    trovato=1
                                    barc_box_effettivo=rig[1]
                                    posiz=rig[2]
                                    barcode=rig[3]
                                    disponibile=rig[4].strip()
                                    if disponibile=='':
                                        disp=1
                                    elif disponibile=='esaurito':
                                        #print 'esaurito',line
                                        disp=0
                                    dizio[genid_file]='1'
                                    break
                                
                            if trovato==0:
                                pass
                                print 'gen non presente in summary.csv',gen
                                #raise ErrorHistoric(gen_effett+'  '+line)
                            else:
                                if disp==1:
                                    lista_archivio+=barc_box_effettivo+'|'+barcode+'|'+posiz+','                     
                                
                        pezzi_usati=0
                        derive=1
                        
                        if tipo=='X':
                            gen2=gen[0:14]+'2'+gen[15:17]+'TUM'+gen[20:]
                        else:
                            gen2=gen
                        #print 'g',gen2 
                        #salvo l'aliquota solo se non e' in una piastra diatech
                        
                        al=Aliquot(barcodeID=barcode,
                                   uniqueGenealogyID=gen2,
                                   idSamplingEvent=samp_ev,
                                   idAliquotType=ti_aliq,
                                   availability=disp,
                                   timesUsed=pezzi_usati,
                                   derived=derive)
                        al.save()
                        #salvo il volume e la concentrazione dell'aliquota
                        volume=valori[7].strip()
                        if volume=='':
                            vol=-1
                        else:
                            vol=volume.replace(',','.')
                        fea=Feature.objects.get(Q(idAliquotType=ti_aliq)&Q(name='OriginalVolume'))
                        aliqfeature=AliquotFeature(idAliquot=al,
                                                   idFeature=fea,
                                                   value=float(vol))
                        aliqfeature.save()
                        
                        fea=Feature.objects.get(Q(idAliquotType=ti_aliq)&Q(name='Volume'))
                        aliqfeature=AliquotFeature(idAliquot=al,
                                                   idFeature=fea,
                                                   value=float(vol))
                        aliqfeature.save()
                        
                        concentrazione=valori[8].strip()
                        if concentrazione=='':
                            conc=-1
                        else:
                            conc=concentrazione.replace(',','.')
                        fea=Feature.objects.get(Q(idAliquotType=ti_aliq)&Q(name='OriginalConcentration'))
                        aliqfeature=AliquotFeature(idAliquot=al,
                                                   idFeature=fea,
                                                   value=float(conc))
                        aliqfeature.save()
                        
                        fea=Feature.objects.get(Q(idAliquotType=ti_aliq)&Q(name='Concentration'))
                        aliqfeature=AliquotFeature(idAliquot=al,
                                                   idFeature=fea,
                                                   value=float(conc))
                        aliqfeature.save()
                                        
                '''j=j+1
                if j==200:
                    break'''
                
                #guardo che il pezzo iniziale della madre sia identico a quello 
                #dei derivati figli
                '''for i in range(0,len(eventi_trasf)):
                    line=eventi_trasf[i].strip()
                    val_ev=line.split(';')
                    id=val_ev[0]
                    if evento==id:
                        inizio_gen=val_ev[6]
                        gen_effett=inizio_gen
                        #print 'gen_effett',gen_effett
                        #print 'gen',gen[0:17]
                        if gen_effett[0:17]!=gen[0:17]:
                            print 'problema gen',line'''
                            #print 'gen_effett',gen_effett
                            #print 'gen',gen[0:17]
                    #if i==3:
                        #break
                        
                        
            #scandisco gli eventi di trasf e salvo le derivazioni fallite
            '''for i in range(0,len(eventi_trasf)):
                line=eventi_trasf[i].strip()
                val_eventi=line.split(';')
                fallit=val_eventi[11]
                
                #solo se la derivazione e' fallita
                if fallit=='0':
                    fallita=1
                    chiave_tr=val_eventi[0]

                    chiave_serie=val_eventi[1]
                    #prendo l'aliquota madre
                    gen_madre=val_eventi[7]
                    origine=val_eventi[3]
                    trov2=0
                    for serie in series:
                        val=serie.split(';')
                        ch_ser=val[0]
                        if chiave_serie==ch_ser:
                            trov2=1
                            oper=val[1]
                            if oper=='Zanella':
                                operatore='eugenia.zanella'
                            elif oper=='Porporato':
                                operatore='roberta.porporato'
                            elif oper=='Galimi':
                                operatore='francesco.galimi'
                            dat=val[2]
                            d=dat.split('/')
                            data=d[2]+'-'+d[1]+'-'+d[0]
                            break
                    if origine=='T':
                        #if trovato==0 or trov2==0:
                            #print 'problema serie',chiave_tr+' '+line
                        serie_def=Serie.objects.get(Q(operator=operatore)&Q(serieDate=data))
                        #salvo il derivation schedule
                        der_sched,creato=DerivationSchedule.objects.get_or_create(scheduleDate=data,
                                                                                 operator=operatore)
                        tum=gen_madre[0:3]
                        caso=gen_madre[3:6]
                        tumore=CollectionType.objects.get(abbreviation=tum)
                        cas=int(caso)
                        coll2=Collection.objects.filter(Q(idCollectionType=tumore)&Q(itemCode=cas))
                        if coll2.count()!=1:
                            raise ErrorHistoric(gen+' '+line)
                        coll=coll2[0]
                        #prendo il tipo di tessuto
                        tess=gen_madre[6:8]
                        tessuto=TissueType.objects.get(abbreviation=tess)
                        #salvo il sampling event
                        samp_ev,creato=SamplingEvent.objects.get_or_create(idTissueType=tessuto,
                                                                idCollection=coll,
                                                                idSource=coll.idSource,
                                                                idSerie=serie_def,
                                                                samplingDate=data)
                        
                        #trasformo il gen della madre nel formato salvato nella biobanca
                        #print 'gen_madre[8:9]',gen_madre[8:9]
                        if gen_madre[8:9]=='X':
                            gen_madre_def=gen_madre[0:3]+'0'+gen_madre[3:9]+'0'+gen_madre[9:12]+'2'+gen_madre[13:15]+'TUM'+gen_madre[15:]+'00'
                        elif gen_madre[8:9]=='H':
                            gen_madre_def=gen_madre[0:3]+'0'+gen_madre[3:15]+'0000'+gen_madre[15:]+'00'
                        print 'gen_def',gen_madre_def
                        
                        l_aliq=Aliquot.objects.filter(uniqueGenealogyID=gen_madre_def)
                        if len(l_aliq)!=0:
                            aliq=l_aliq[0]
                        else:
                            #vuol dire che devo creare l'aliquota madre perche' non esiste
                            tip_al=AliquotType.objects.get(abbreviation=gen_madre_def[20:22])
                            aliq=Aliquot(uniqueGenealogyID=gen_madre_def,
                                       idSamplingEvent=samp_ev,
                                       idAliquotType=tip_al,
                                       availability=0,
                                       timesUsed=1,
                                       derived=0)
                            aliq.save()
                            
                            #salvo il numero di pezzi
                            fea=Feature.objects.get(Q(idAliquotType=tip_al)&Q(name='NumberOfPieces'))
                            aliqfeature=AliquotFeature(idAliquot=aliq,
                                                       idFeature=fea,
                                                       value=1)
                            aliqfeature.save()
                        
                        #imposto DNA a priori perche' non so cosa si voleva estrarre, tanto
                        #la derivazione e' fallita
                        tipo_aliq=AliquotType.objects.get(abbreviation='DNA')
                        
                        #salvo la quantita' presa dalla madre
                        quant=val_eventi[10].strip()
                        if quant!='':
                            quant=float(quant)
                        else:
                            quant=None
    
                        #vedo se l'aliq madre e' esaurita o meno
                        if aliq.availability==0:
                            esausta=1
                        else:
                            esausta=0
                        
                        al_der_sch,creato=AliquotDerivationSchedule.objects.get_or_create(idAliquot=aliq,
                                                             idDerivationSchedule=der_sched,
                                                             idDerivedAliquotType=tipo_aliq,
                                                             derivationExecuted=1,
                                                             operator=operatore,
                                                             loadQuantity=quant,
                                                             failed=fallita,
                                                             initialDate=data,
                                                             measurementExecuted=1,
                                                             aliquotExhausted=esausta)'''
            
            #scandisco gli eventi di trasf e aggiorno il times used della madre
            for i in range(0,len(eventi_trasf)):
                line=eventi_trasf[i].strip()
                val_eventi=line.split(';')
                gen_madre=val_eventi[6]
                origine=val_eventi[3]

                #if gen_madre[8:9]=='X':
                #    gen_madre_def=gen_madre[0:3]+'0'+gen_madre[3:9]+'0'+gen_madre[9:12]+'2'+gen_madre[13:15]+'TUM'+gen_madre[15:]+'00'
                #elif gen_madre[8:9]=='H':
                #    gen_madre_def=gen_madre[0:3]+'0'+gen_madre[3:15]+'0000'+gen_madre[15:]+'00'
                #print 'gen_def',gen_madre_def
                gen_madre_def=gen_madre[0:17]+'TUM'+gen_madre[20:]
                l_aliq=Aliquot.objects.filter(uniqueGenealogyID=gen_madre_def)
                if len(l_aliq)!=0:
                    aliq_madre_trovata=l_aliq[0]
                else:
                    #Provo a vedere se la madre ha il 2 dello storico
                    gen_madre_def=gen_madre[0:14]+'2'+gen_madre[15:17]+'TUM'+gen_madre[20:]
                    l_aliq=Aliquot.objects.filter(uniqueGenealogyID=gen_madre_def)
                    if len(l_aliq)!=0:
                        aliq_madre_trovata=l_aliq[0]
                
                #aggiungo 1 al times used della madre
                volte=int(aliq_madre_trovata.timesUsed)
                volte=volte+1
                aliq_madre_trovata.timesUsed=volte
                aliq_madre_trovata.save()
                
            #vedo se tutte le aliq di summary.csv hanno una corrispodenza in archive_derivatives
            '''for key,value in dizio.items():
                if value=='0':
                    print 'aliq senza corrispondenza in archive_derivatives',key'''
                    #raise ErrorHistoric(key)
            #controllo che la madre compaia nell'archivio tessuti
            '''for i in range(0,len(eventi_trasf)):
                
                line=eventi_trasf[i].strip()
                val_ev=line.split(';')
                inizio_gen=val_ev[7]
                trovato=0
                for j in range(0,len(linee_tess)):
                    l=linee_tess[j].strip()
                    singolo_tess=l.split(';')
                    g_tess=singolo_tess[4]
                    if inizio_gen==g_tess:
                        trovato=1
                        break
                if trovato==0:
                    print 'manca aliquota',line'''
            #tolgo l'ultima , alla fine della stringa
            lung=len(lista_archivio)-1
            l_arch_def=lista_archivio[:lung]
            #print 'l_arch_def',l_arch_def
            #comunico allo storage le provette che deve salvare
            url = Urls.objects.get(default = '1').url + "/historic/tube"          
            val1={'lista':l_arch_def}

            print 'url1',url
            data = urllib.urlencode(val1)
            req = urllib2.Request(url,data=data, headers={"workingGroups" : get_WG_string()})
            u = urllib2.urlopen(req)
            #u = urllib2.urlopen(url, data)
            res =  u.read() 
            if res=='err':
                raise ErrorHistoric('salvataggio storage')
            return HttpResponse("ok")
            
        else:
            form = HistoricForm()
        variables = RequestContext(request, {'form':form})
        return render_to_response('tissue2/historic/storico_deriv.html',variables)
    except ErrorHistoric as e:
        print 'My exception occurred, value:', e.value
        transaction.rollback()
        return HttpResponse("err")
    except Exception,e:
        print 'err',e
        transaction.rollback()
        return HttpResponse("err")  

#serve per vedere se i barcode delle provette dei derivati compaiono gia' nel LAS
@transaction.commit_on_success
def HistoricDerivedDuplicate(request):
    try:
        if request.method=='POST':
            print request.POST
            print request.FILES
            form=HistoricForm(request.FILES)
            
            listafile=request.FILES.getlist('file')
            
            #e' il file archive_derivatives
            f1=listafile[0]
            
            lines = f1.readlines()
            f1.close()
            
            for i in range(0,len(lines)):
                line=lines[i]
                line=line.strip()
                valori=line.split(';')
                barcode=valori[0]
                if barcode!='' and not barcode.startswith('C') and not barcode.startswith('F'):
                    l_aliq=Aliquot.objects.filter(barcodeID=barcode)
                    if len(l_aliq)!=0:
                        print 'barcode duplicato',line 
            return HttpResponse("ok")
            
        else:
            form = HistoricForm()
        variables = RequestContext(request, {'form':form})
        return render_to_response('tissue2/historic/storico_deriv_duplicate.html',variables)
    except ErrorHistoric as e:
        print 'My exception occurred, value:', e.value
        transaction.rollback()
        return HttpResponse("err")
    except Exception,e:
        print 'err',e
        transaction.rollback()
        return HttpResponse("err")  
    
#serve per salvare i container non salvati dallo script prima
@transaction.commit_on_success
def HistoricDerivedContainer(request):
    try:
        if request.method=='POST':
            print request.POST
            print request.FILES
            form=HistoricForm(request.FILES)
            
            listafile=request.FILES.getlist('file')
            
            #e' il file archive_derivatives ridotto
            f1=listafile[1]
            
            lines = f1.readlines()
            f1.close()
            
            #e' il file archive_container da cui ricavo il barcode del box
            f3=listafile[0]
            contain= f3.readlines()
            f3.close()
            
            lista_archivio=''
            for i in range(0,len(lines)):
                line=lines[i]
                line=line.strip()
                valori=line.split(';')
                barcode=valori[4]
                sto=valori[14]
                rack=valori[15]
                box=valori[16]
                posiz=valori[17]
                if sto!='':
                    barc_box_effettivo=''
                    for righe in contain:
                        rig=righe.split(';')
                        barc_store=rig[1]
                        barc_rack=rig[2]
                        barc_box=rig[3]
                        if barc_store==sto and barc_rack==rack and barc_box==box:
                            barc_box_effettivo=rig[6]
                    if barc_box_effettivo=='':
                        pass
                        print 'box non presente',sto+' '+rack+' '+box+' '+line
                        #raise ErrorHistoric(sto+' '+rack+' '+box+'  '+line)
                    else:
                        
                        #vedo se l'aliq e' disponibile
                        disponibile=valori[13].strip()
                        #print 'disponibile',valori[13]
                        if disponibile=='y' or disponibile=='Y' or disponibile=='':
                            disp=1
                            lista_archivio+=barc_box_effettivo+'|'+barcode+'|'+posiz+','
                        elif disponibile=='no':
                            disp=0
                 
            #tolgo l'ultima , alla fine della stringa
            lung=len(lista_archivio)-1
            l_arch_def=lista_archivio[:lung]
            #print 'l_arch_def',l_arch_def
            #comunico allo storage le provette che deve salvare
            url = Urls.objects.get(default = '1').url + "/historic/tube"          
            val1={'lista':l_arch_def}

            print 'url1',url
            data = urllib.urlencode(val1)
            req = urllib2.Request(url,data=data, headers={"workingGroups" : get_WG_string()})
            u = urllib2.urlopen(req)
            #u = urllib2.urlopen(url, data)
            res =  u.read() 
            if res=='err':
                raise ErrorHistoric('salvataggio storage')
                                
            return HttpResponse("ok")
            
        else:
            form = HistoricForm()
        variables = RequestContext(request, {'form':form})
        return render_to_response('tissue2/historic/storico_deriv_container.html',variables)
    except ErrorHistoric as e:
        print 'My exception occurred, value:', e.value
        transaction.rollback()
        return HttpResponse("err")
    except Exception,e:
        print 'err',e
        transaction.rollback()
        return HttpResponse("err")  

#serve per vedere se le madri delle derivazioni provengono da topi con chip o no.
#Per capire se bisogna mettere il +200 nei rispettivi derivati
@transaction.commit_on_success
def HistoricMiceDerived(request):
    try:
        if request.method=='POST':
            print request.POST
            print request.FILES
            form=HistoricForm(request.FILES)
            
            listafile=request.FILES.getlist('file')
            
            #e' il file trasf event
            f1=listafile[0]
            
            lines = f1.readlines()
            f1.close()
            
            #e' il file impianti
            f1=listafile[1]
            
            impl = f1.readlines()
            f1.close()
            
            for i in range(0,len(lines)):
                line=lines[i]
                line=line.strip()
                valori=line.split(';')
                gen_aliq=valori[8]
                for imp in impl:
                    line2=imp.strip()
                    val_eventi=line2.split(';')
                    chip=val_eventi[2]
                    gen_topo=val_eventi[4]
                    if chip!='' and gen_aliq==gen_topo:
                        print 'trovato',line
                        
            return HttpResponse("ok")
            
        else:
            form = HistoricForm()
        variables = RequestContext(request, {'form':form})
        return render_to_response('tissue2/historic/storico_mice_deriv.html',variables)
    except ErrorHistoric as e:
        print 'My exception occurred, value:', e.value
        transaction.rollback()
        return HttpResponse("err")
    except Exception,e:
        print 'err',e
        transaction.rollback()
        return HttpResponse("err")
    
#per caricare le linee cellulari storiche
@transaction.commit_on_success
def HistoricCellLine(request):
    try:
        if request.method=='POST':
            print request.POST
            print request.FILES  
            form=HistoricForm(request.FILES)
            listafile=request.FILES.getlist('file')
            
            #e' il file delle linee da caricare
            f1=listafile[0]
            aliq_summ = f1.readlines()
            f1.close()
            
            lista_archivio=''
            listacoll=[]
            k=0
            
            #mi occupo del tipo di aliq (VT)
            ti_aliq=AliquotType.objects.get(abbreviation='VT')
            #dizionario in cui la chiave e' linea+passaggio+data e il valore e' il numero di campioni di quel tipo che ci sono 
            dizgenerale={}
            for i in range (0,len(aliq_summ)):
                righe_aliq=aliq_summ[i]
                rig=righe_aliq.split(';')    
                
                barc=rig[0].strip()
                if barc!='':
                    nomelinea=rig[2].strip()
                    passaggio=rig[3].strip()
                    if passaggio=='':
                        passaggio='1'
                    datacong=rig[4].strip()
                    tumore=CollectionType.objects.get(abbreviation='CRC')
                    
                    #se la combinazione dei tre non c'e' ancora nel diz, devo creare un nuovo caso
                    chiave=nomelinea+'-P'+passaggio+'-'+datacong
                    
                    creaoggetti=False
                    if not dizgenerale.has_key(chiave):
                        #faccio la chiamata al LASHub per farmi dare il codice del caso
                        prefisso= 'https://' if settings.LAS_AUTH_USE_HTTPS else 'http://'
                        address=request.get_host()+settings.HOST_URL
                        indir=prefisso+address
                        url = indir + '/clientHUB/getAndLock/'
                        print 'url',url
                        values = {'randomFlag' : False, 'case': 'CRC'}
                        
                        r = requests.post(url, data=values, verify=False)
                        
                        print 'r.text',r.text
                        if r.text=='not active':
                            
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
                            caso=r.text
                        
                        print 'caso',caso
                        dizgenerale[chiave]='1|'+str(caso)
                        contatore=1
                        creaoggetti=True
                    else:
                        valor=dizgenerale[chiave].split('|')
                        contatore=int(valor[0])+1
                        caso=valor[1]
                        dizgenerale[chiave]=str(contatore)+'|'+str(caso)
                            
                    #aggiungo la parte finale al barcode per disambiguare quelli uguali
                    barc+='_'+str(contatore)
                    
                    sorg=rig[5].strip()
                    print 'sorg',sorg
                    if sorg=='#N/D':
                        sorg='Unknown'
                    sorgente,creato=Source.objects.get_or_create(type='Hospital',name=sorg)
    
                    collevent=chiave
                    #devo creare la collezione
                    coll,creato1=Collection.objects.get_or_create(itemCode=caso,
                                    idCollectionType=tumore,
                                    idSource=sorgente,
                                    collectionEvent=collevent
                                    )
                    
                    iniziogen=coll.idCollectionType.abbreviation+coll.itemCode
                    if iniziogen not in listacoll:
                        listacoll.append(iniziogen)   
                    
                    if creaoggetti:
                        #devo creare il sampling event
                        #prendo il tipo di tessuto
                        tess=rig[14].strip()
                        print 'tess',tess
                        if tess=='Primary':
                            abbr='PR'
                        elif tess=='Lymph node metastasis':
                            abbr='LY'
                        elif tess=='Lung Metastasis':
                            abbr='TM'
                        elif tess=='Lymph node metastasis':
                            abbr='LY'
                        elif tess=='Liver Metastasis':
                            abbr='LM'
                        elif tess=='Ascitic Fluid':
                            abbr='AF'
                        tessuto=TissueType.objects.get(abbreviation=abbr)
                        
                        lineage='A'
                        lin=rig[13].strip()
                        if lin=='Suspension':
                            lineage='S'
    
                        dat=datacong.split('/')
                        datadef=dat[2]+'-'+dat[1]+'-'+dat[0]
                        print 'datadef',datadef
                        #mi occupo dell'operatore
                        operatore=rig[6].strip()
                        if operatore=='Carlotta':
                            oper='carlotta.cancelliere'
                        elif operatore=='Mary':
                            oper='mariangela.russo'
                        elif operatore=='Sandra':
                            oper='sandra.misale'
                             
                        serie_def,creato2=Serie.objects.get_or_create(operator=oper,
                                                                      serieDate=datadef)
                        samp_ev=SamplingEvent(idTissueType=tessuto,
                                            idCollection=coll,
                                            idSource=coll.idSource,
                                            idSerie=serie_def,
                                            samplingDate=datadef)
                        samp_ev.save()
                        print 'samp',samp_ev
                    
                    barc_piastra=rig[8].strip()
                    posiz=rig[9].strip()
                    lista_archivio+=barc_piastra+'|'+barc+'|'+posiz+','

                    passaggio=rig[3].strip()
                    if passaggio=='':
                        passaggio=1
                    passfin=str(passaggio).zfill(3)
                    
                    scong=rig[11].strip()
                    if scong=='' or scong=='0':
                        scong=1
                    scongfin=str(scong).zfill(2)
                    
                    #creo il genid
                    val=str(contatore).zfill(2)
                    print 'val',val
                    genid=coll.idCollectionType.abbreviation+caso+tessuto.abbreviation+lineage+'0A'+scongfin+passfin+'000'+ti_aliq.abbreviation+val+'00'
                    print 'gen',genid
                    #vedo se esiste gia' un'aliquota con questo codice 
                    lisal=Aliquot.objects.filter(uniqueGenealogyID=genid)
                    print 'lisal',lisal
                    if len(lisal)!=0:
                        raise Exception

                    #salvo l'aliquota
                    al=Aliquot(barcodeID=barc,
                               uniqueGenealogyID=genid,
                               idSamplingEvent=samp_ev,
                               idAliquotType=ti_aliq,
                               availability=1,
                               timesUsed=0,
                               derived=0)
                    print 'al',al
                    al.save()
                    
                    k=k+1
                    #if k==10:
                    #    break
                    
            print 'lista archivio',lista_archivio
            lung=len(lista_archivio)-1
            l_arch_def=lista_archivio[:lung]
            print 'l_arch_def',l_arch_def
            #comunico allo storage le provette che deve salvare
            url = Urls.objects.get(default = '1').url + "/historic/tube"          
            val1={'lista':l_arch_def}

            print 'url1',url
            data = urllib.urlencode(val1)
            req = urllib2.Request(url,data=data, headers={"workingGroups" : get_WG_string()})
            u = urllib2.urlopen(req)
            #u = urllib2.urlopen(url, data)
            res =  u.read() 
            if res=='err':
                raise ErrorHistoric('salvataggio storage')
            
            prefisso= 'https://' if settings.LAS_AUTH_USE_HTTPS else 'http://'
            address=request.get_host()+settings.HOST_URL
            indir=prefisso+address
            url = indir + '/clientHUB/saveAndFinalize/'
            print 'url',url
            values = {'typeO' : 'aliquot', 'listO': str(listacoll)}
            requests.post(url, data=values, verify=False)
            
            return HttpResponse("ok")
        else:
            form = HistoricForm()
        variables = RequestContext(request, {'form':form})
        return render_to_response('tissue2/historic/storico_sampl.html',variables)
    except ErrorHistoric as e:
        print 'My exception occurred, value:', e.value
        transaction.rollback()
        return HttpResponse("err")
    except Exception,e:
        print 'err',e
        transaction.rollback()
        return HttpResponse("err")

#per caricare le linee cellulari storiche del file di Luraghi
@transaction.commit_on_success
def HistoricCellLuraghi(request):
    try:
        if request.method=='POST':
            print request.POST
            print request.FILES  
            form=HistoricForm(request.FILES)
            listafile=request.FILES.getlist('file')
            
            #e' il file delle linee da caricare
            f1=listafile[0]
            aliq_summ = f1.readlines()
            f1.close()
            
            lista_archivio=''
            k=0
            #metto come possessore Bertotti_wg perche' possiede l'aliquota originale e poi metto in condivisione Boccaccio_wg
            set_initWG(set(['Bertotti_WG']))
            sorg=Source.objects.get(name='cellline')
            #mi occupo del tipo di aliq (VT)
            ti_aliq=AliquotType.objects.get(abbreviation='VT')
            for i in range (0,len(aliq_summ)):
                righe_aliq=aliq_summ[i]
                rig=righe_aliq.split(';')
                
                barc=rig[12].strip()
                if barc!='':
                    gen_id_prova=rig[9].strip()
                    tum=gen_id_prova[0:3]
                    caso=gen_id_prova[3:7]
                    
                    tumore=CollectionType.objects.get(abbreviation=tum)
                    cas=str(caso)
                    liscoll=Collection.objects.filter(Q(idCollectionType=tumore)&Q(itemCode=cas))
                    if liscoll.count()!=1:
                        raise ErrorHistoric(righe_aliq)
                    coll=liscoll[0] 
                    #prendo il tipo di tessuto
                    tess=gen_id_prova[7:9]
                    tessuto=TissueType.objects.get(abbreviation=tess)
                    operat='diblaura'
                    dat=rig[3].strip()
                    dd=dat.split('/')
                    data=dd[2]+'-'+dd[1]+'-'+dd[0]
                    
                    #devo salvare la serie            
                    serie_def,creato2=Serie.objects.get_or_create(operator=operat,
                                                      serieDate=data)
                
                    
                    samp_ev,creato3=SamplingEvent.objects.get_or_create(idTissueType=tessuto,
                                                                    idCollection=coll,
                                                                    idSource=sorg,
                                                                    idSerie=serie_def,
                                                                    samplingDate=data)

                    #salvo l'aliquota
                    al=Aliquot(barcodeID=barc,
                               uniqueGenealogyID=gen_id_prova,
                               idSamplingEvent=samp_ev,
                               idAliquotType=ti_aliq,
                               availability=1,
                               timesUsed=0,
                               derived=0)
                    al.save()                                    
                    
                    padre=rig[10].strip()
                    pos=rig[11].strip()
                    lista_archivio+=padre+'|'+barc+'|'+pos+'|'+gen_id_prova+'|'+data+','
                    
                k=k+1
                #if k==2:
                #    break                    
            
            print 'lista archivio',lista_archivio
            lung=len(lista_archivio)-1
            l_arch_def=lista_archivio[:lung]
            print 'l_arch_def',l_arch_def
            #comunico allo storage le provette che deve salvare
            url = Urls.objects.get(default = '1').url + "/historic/tube"          
            val1={'lista':l_arch_def}
            print 'url1',url
            data = urllib.urlencode(val1)
            req = urllib2.Request(url,data=data, headers={"workingGroups" : get_WG_string()})
            u = urllib2.urlopen(req)
            res =  u.read() 
            if res=='err':
                raise ErrorHistoric('salvataggio storage')
            
            return HttpResponse("ok")
        else:
            form = HistoricForm()
        variables = RequestContext(request, {'form':form})
        return render_to_response('tissue2/historic/storico_sampl.html',variables)
    except ErrorHistoric as e:
        print 'My exception occurred, value:', e.value
        transaction.rollback()
        return HttpResponse("err")
    except Exception,e:
        print 'err',e
        transaction.rollback()
        return HttpResponse("err")

#serve solo una volta per le linee storiche di Luraghi per impostarne la condivisione con Boccaccio_WG
@transaction.commit_on_success
def HistoricCellShare(request):
    try:     
        if request.method=='POST':
            print request.POST
            print request.FILES  
            form=HistoricForm(request.FILES)
            listafile=request.FILES.getlist('file')            
            #e' il file delle linee da caricare
            f1=listafile[0]
            aliq_summ = f1.readlines()
            f1.close()
            k=0
            
            for i in range (0,len(aliq_summ)):
                righe_aliq=aliq_summ[i]
                rig=righe_aliq.split(';')
                
                barc=rig[12].strip()
                print 'barc',barc
                if barc!='':
                    genid=rig[9].strip()
                    print 'genid',genid
                    gdb=neo4j.GraphDatabaseService(settings.GRAPH_DB_URL)
                    #verifico prima se non esiste gia' una relazione con quel wg
                    q=neo4j.CypherQuery(gdb,"START n=node:node_auto_index(identifier='"+str(genid)+"'), wg=node:node_auto_index(identifier='Primo_WG') MATCH wg-[r:OwnsData|SharesData]->n return r")
                    print q
                    r=q.execute()
                    if len(r.data)==0:
                        q=neo4j.CypherQuery(gdb,"START n=node:node_auto_index(identifier='"+str(genid)+"'), wg=node:node_auto_index(identifier='Primo_WG') CREATE (wg)-[r:SharesData {startDate:'"+str(datetime.datetime.now())+"'}]->n return r")
                        q.execute()                    
                        #aggiungo anche la riga in aliquot_wg
                        disable_graph()
                        aliquot=Aliquot.objects.get(uniqueGenealogyID=genid)
                        wg=WG.objects.get(name='Primo_WG')
                        if Aliquot_WG.objects.filter(aliquot=aliquot,WG=wg).count()==0:
                            m2m=Aliquot_WG(aliquot=aliquot,
                                           WG=wg)
                            m2m.save()
                        enable_graph()
                k=k+1
                #if k==2:
                #    break                    
            
            return HttpResponse("ok")
        else:
            form = HistoricForm()
        variables = RequestContext(request, {'form':form})
        return render_to_response('tissue2/historic/storico_save_impl.html',variables)
    except Exception,e:
        print 'err',e
        transaction.rollback()
        return HttpResponse("err")

#per caricare i campioni di tessuto del beaming
@transaction.commit_on_success
def HistoricBeamingTissue(request):
    try:
        if request.method=='POST':
            dizmesi={'JAN':'01','FEB':'02','MAR':'03','APR':'04','MAY':'05','JUN':'06','JUL':'07','AUG':'08','SEP':'09','OCT':'10','NOV':'11','DEC':'12'}
            print request.POST
            print request.FILES  
            form=HistoricForm(request.FILES)
            listafile=request.FILES.getlist('file')
            
            #e' il file dei tessuti da caricare
            f1=listafile[0]
            aliq_summ = f1.readlines()
            f1.close()
            
            lista_archivio=''
            k=0
            
            stringa=''
            oggi=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            idobj=74000
            idval=74000
            
            datainiz=datetime.date(1990,1,1)
            for righe_aliq in aliq_summ:
                rig=righe_aliq.split(';')    
                #prendo solo pbmc e plasma
                tipoaliq=rig[3].strip()
                if tipoaliq=='PLASMA' or tipoaliq=='PBMC':
                    
                    caso=rig[16].strip()
                    tum=rig[1].strip()
                    tumore=CollectionType.objects.get(abbreviation=tum)
                    sorg=rig[15].strip()
                    sorgente=Source.objects.get(Q(type='Hospital')&Q(name=sorg))
                    protcoll=CollectionProtocol.objects.get(name='CirculatingDNA')
                    codpaz=rig[22].strip()
                    collevent=codpaz+'_'+caso
                    #devo creare la collezione
                    coll,creato1=Collection.objects.get_or_create(itemCode=caso,
                                    idCollectionType=tumore,
                                    idSource=sorgente,
                                    collectionEvent=collevent,
                                    patientCode=codpaz,
                                    idCollectionProtocol=protcoll
                                    )
                    #per il lashub. Solo se ho creato una nuova collezione.
                    if creato1:
                        #inserimento nella tabella object
                        stringa+='insert into object values ('+str(idobj)+',1,\''+str(oggi)+'\',1);\n'
                        #inserimento delle feature della collezione
                        stringa+='insert into object_value values ('+str(idval)+','+str(idobj)+',1,\''+coll.idCollectionType.abbreviation+'\');\n'
                        idval=idval+1
                        stringa+='insert into object_value values ('+str(idval)+','+str(idobj)+',2,\''+coll.itemCode+'\');\n'
                        idval=idval+1
                        idobj=idobj+1
                        
                    #devo creare il sampling event
                    #prendo il tipo di tessuto
                    tess=rig[2].strip()
                    #e' una get insensibile a maiuscole o minuscole
                    tessuto=TissueType.objects.get(longName__iexact=tess)
                    #devo salvare la serie
                    data=rig[13].strip()
                    if data!='':
                        dat=data.split('-')
                        datadef=dat[2]+'-'+dizmesi[dat[1]]+'-'+dat[0]
                        print 'datadef',datadef
                    else:
                        #se la data e' vuota e ho creato una nuova collezione, allora creo una
                        #nuova data cosi' da non avere tutti i sampling event alla stessa data
                        if creato1:
                            datadef=str(datainiz)
                            datainiz=datainiz+datetime.timedelta(days=1)
                    serie_def,creato2=Serie.objects.get_or_create(operator='giulia.siravegna',
                                                      serieDate=datadef)
                    samp_ev,creato3=SamplingEvent.objects.get_or_create(idTissueType=tessuto,
                                                                    idCollection=coll,
                                                                    idSource=coll.idSource,
                                                                    idSerie=serie_def,
                                                                    samplingDate=datadef)
                    
                    barcode=rig[0].strip()
                    barc_piastra=rig[5].strip()
                    posiz=rig[6].strip()
                    lista_archivio+=barc_piastra+'|'+barcode+'|'+posiz+','
                    #mi occupo del tipo di aliq (VT,RL...)
                    if tipoaliq=='PBMC':
                        tipoaliq='Viable'
                    ti_aliq=AliquotType.objects.get(longName__iexact=tipoaliq)
                    #creo il genid
                    trovato=False
                    id=1
                    while not trovato:
                        val=str(id).zfill(2)
                        genid=coll.idCollectionType.abbreviation+caso+tessuto.abbreviation+'H0000000000'+ti_aliq.abbreviation+val+'00'
                        print 'gen',genid
                        #vedo se esiste gia' un'aliquota con questo codice 
                        lisal=Aliquot.objects.filter(uniqueGenealogyID=genid)
                        print 'lisal',lisal
                        if len(lisal)==0:
                            trovato=1
                        else:
                            id=id+1

                    #guardo se e' esaurita
                    volum=rig[7].strip()
                    if volum=='ESAURITO':
                        avail=0
                    else:
                        avail=1
                    #salvo l'aliquota
                    al=Aliquot(barcodeID=barcode,
                               uniqueGenealogyID=genid,
                               idSamplingEvent=samp_ev,
                               idAliquotType=ti_aliq,
                               availability=avail,
                               timesUsed=0,
                               derived=0)
                    al.save()
                    #salvo il volume dell'aliquota
                    if volum!='ESAURITO':
                        lisvol=volum.split(' ')
                        volfin=lisvol[0]
                        print 'volfin',volfin
                        fea=Feature.objects.get(Q(idAliquotType=ti_aliq)&Q(name='Volume')&Q(measureUnit='ul'))
                        aliqfeature=AliquotFeature(idAliquot=al,
                                                   idFeature=fea,
                                                   value=volfin)
                        aliqfeature.save()
                    #salvo la conta dell'aliq
                    conta=rig[8].strip()
                    if conta!='':
                        liscont=conta.split(' ')
                        contafin=float(liscont[0])*1000000
                        print 'contafin',contafin
                        fea=Feature.objects.get(Q(idAliquotType=ti_aliq)&Q(name='Count')&Q(measureUnit='cell/ml'))
                        aliqfeature=AliquotFeature(idAliquot=al,
                                                   idFeature=fea,
                                                   value=contafin)
                        aliqfeature.save()
                    k=k+1
                    if k==40:
                        break
            
            '''print 'lista archivio',lista_archivio
            lung=len(lista_archivio)-1
            l_arch_def=lista_archivio[:lung]
            print 'l_arch_def',l_arch_def
            #comunico allo storage le provette che deve salvare
            url = Urls.objects.get(default = '1').url + "/historic/tube"          
            val1={'lista':l_arch_def}

            print 'url1',url
            data = urllib.urlencode(val1)
            u = urllib2.urlopen(url, data)
            res =  u.read() 
            if res=='err':
                raise ErrorHistoric('salvataggio storage')'''
            
            f2=open(os.path.join(os.path.dirname(__file__),'tissue_media/File_Format/beaming_tissue.sql'),'w')
            f2.write(stringa)
            f2.close()
            return HttpResponse("ok")
        else:
            form = HistoricForm()
        variables = RequestContext(request, {'form':form})
        return render_to_response('tissue2/historic/storico_beam_tess.html',variables)
    except ErrorHistoric as e:
        print 'My exception occurred, value:', e.value
        transaction.rollback()
        return HttpResponse("err")
    except Exception,e:
        print 'err',e
        transaction.rollback()
        return HttpResponse("err")
    
#serve per caricare nel DB i derivati storici presi dal file Excel
@transaction.commit_on_success
def HistoricBeamingDerived(request):
    try:
        if request.method=='POST':
            print request.POST
            print request.FILES
            dizmesi={'JAN':'01','FEB':'02','MAR':'03','APR':'04','MAY':'05','JUN':'06','JUL':'07','AUG':'08','SEP':'09','OCT':'10','NOV':'11','DEC':'12'}
            form=HistoricForm(request.FILES)
            
            listafile=request.FILES.getlist('file')
            
            #e' il file archive_derivatives
            f1=listafile[0]           
            lines = f1.readlines()
            f1.close()

            stringa=''
            data=''
            j=0
            lista_archivio=''
            operatore='benedetta.mussolin'
            dizmadri={}
            
            oggi=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            idobj=100000
            idval=100000
            
            datainiz=datetime.date(2000,1,1)
            for kk in range(0,len(lines)):
                line=lines[kk]
                line=line.strip()
                rig=line.split(';')               
                #prendo solo pbmc e plasma
                tipoaliq=rig[3].strip()
                if tipoaliq=='DNA':
                    caso=rig[16].strip()
                    tum=rig[1].strip()
                    tumore=CollectionType.objects.get(abbreviation=tum)
                    sorg=rig[15].strip()
                    sorgente=Source.objects.get(Q(type='Hospital')&Q(name=sorg))
                    protcoll=CollectionProtocol.objects.get(name='CirculatingDNA')
                    codpaz=rig[22].strip()
                    collevent=codpaz+'_'+caso
                    #devo creare la collezione
                    coll,creato1=Collection.objects.get_or_create(itemCode=caso,
                                    idCollectionType=tumore,
                                    idSource=sorgente,
                                    collectionEvent=collevent,
                                    patientCode=codpaz,
                                    idCollectionProtocol=protcoll
                                    )
                    #per il lashub. Solo se ho creato una nuova collezione.
                    if creato1:
                        #inserimento nella tabella object
                        stringa+='insert into object values ('+str(idobj)+',1,\''+str(oggi)+'\',1);\n'
                        #inserimento delle feature della collezione
                        stringa+='insert into object_value values ('+str(idval)+','+str(idobj)+',1,\''+coll.idCollectionType.abbreviation+'\');\n'
                        idval=idval+1
                        stringa+='insert into object_value values ('+str(idval)+','+str(idobj)+',2,\''+coll.itemCode+'\');\n'
                        idval=idval+1
                        idobj=idobj+1
                        
                    #devo creare il sampling event
                    #prendo il tipo di tessuto
                    tess=rig[2].strip()
                    #e' una get insensibile a maiuscole o minuscole
                    tessuto=TissueType.objects.get(longName__iexact=tess)
                    #devo salvare la serie
                    data=rig[13].strip()
                    if data!='':
                        dat=data.split('-')
                        datadef=dat[2]+'-'+dizmesi[dat[1]]+'-'+dat[0]
                        print 'datadef',datadef
                    else:
                        #se la data e' vuota e ho creato una nuova collezione, allora creo una
                        #nuova data cosi' da non avere tutti i sampling event alla stessa data
                        if creato1:
                            datadef=str(datainiz)
                            datainiz=datainiz+datetime.timedelta(days=1)
                            
                    serie_def,creato2=Serie.objects.get_or_create(operator=operatore,
                                                      serieDate=datadef)                    
                    
                    #salvo il derivation schedule
                    der_sched,creato=DerivationSchedule.objects.get_or_create(scheduleDate=datadef,
                                                                              operator=operatore)
                    #salvo il sampling event
                    samp_ev=SamplingEvent(idTissueType=tessuto,
                                                                idCollection=coll,
                                                                idSource=coll.idSource,
                                                                idSerie=serie_def,
                                                                samplingDate=datadef)
                    samp_ev.save()
                    prot_der=rig[4].strip()
                    der_prot=DerivationProtocol.objects.get(name=prot_der)
                    
                    #mi occupo della madre se c'e', altrimenti la creo
                    barc_madre=rig[17].strip()
                    if barc_madre!='':
                        aliq=Aliquot.objects.get(barcodeID=barc_madre)
                    else:
                        #vuol dire che devo creare l'aliquota madre perche' non esiste.
                        #In base al protocollo di derivazione capisco qual era la madre
                        if der_prot.name=='CirculatingDNA extraction':
                            tipo='PL'
                        elif der_prot.name=='DNA extraction (Promega)':
                            tipo='VT'
                        elif der_prot.name=='DNA extraction (Xylene)':
                            tipo='FF'
                        tip_al=AliquotType.objects.get(abbreviation=tipo)
                        print 'tip al',tip_al
                        gen_madre_def=coll.idCollectionType.abbreviation+caso+tessuto.abbreviation+'H0000000000'+tip_al.abbreviation+'0100'
                        aliqq=Aliquot.objects.filter(uniqueGenealogyID=gen_madre_def)
                        if len(aliqq)==0:
                            aliq,creato=Aliquot.objects.get_or_create(uniqueGenealogyID=gen_madre_def,
                                   idSamplingEvent=samp_ev,
                                   idAliquotType=tip_al,
                                   availability=0,
                                   timesUsed=0,
                                   derived=0)
                        else:
                            aliq=aliqq[0]
                        
                        #salvo il numero di pezzi. Ha senso solo se la madre e' FF
                        if tipo=='FF':
                            fea=Feature.objects.get(Q(idAliquotType=tip_al)&Q(name='NumberOfPieces'))
                            aliqfeature,creato=AliquotFeature.objects.get_or_create(idAliquot=aliq,
                                                                             idFeature=fea,
                                                                             value=1)
                    print 'aliq madre',aliq
                    if creato1:
                        if aliq in dizmadri:
                            val=dizmadri[aliq]
                            val=val+1
                            dizmadri[aliq]=val
                        else:
                            dizmadri[aliq]=1
                    tipodna=AliquotType.objects.get(abbreviation='DNA')
                    if aliq.availability==1:
                        esausta=0
                    else:
                        esausta=1
                    #se non ci sono misure associate posso riutilizzare lo stesso aldersched perche' cosi'
                    #sono sicuro che non si sovrappongono sullo stesso aldersched piu' misure dello stesso tipo
                    GEml=rig[12].strip()
                    purezza=rig[10].strip()
                    #concmadre=rig[9].strip()
                    pur230=rig[11].strip()
                    if GEml=='' and purezza=='' and pur230=='':
                        al_der_sch,creato=AliquotDerivationSchedule.objects.get_or_create(idAliquot=aliq,
                                                             idDerivationSchedule=der_sched,
                                                             idDerivedAliquotType=tipodna,
                                                             idDerivationProtocol=der_prot,
                                                             derivationExecuted=1,
                                                             operator=operatore,
                                                             failed=0,
                                                             initialDate=datadef,
                                                             measurementExecuted=1,
                                                             aliquotExhausted=esausta)
                        print 'riutilizzo al der sche',al_der_sch
                    else:
                        #devo creare in ogni caso un nuovo aldersched perche' anche se si tratta della stessa aliq madre,
                        #ho misure diverse che sottintendono piu' derivazioni
                        al_der_sch=AliquotDerivationSchedule(idAliquot=aliq,
                                                             idDerivationSchedule=der_sched,
                                                             idDerivedAliquotType=tipodna,
                                                             idDerivationProtocol=der_prot,
                                                             derivationExecuted=1,
                                                             operator=operatore,
                                                             failed=0,
                                                             initialDate=datadef,
                                                             measurementExecuted=1,
                                                             aliquotExhausted=esausta)
                        al_der_sch.save() 
                        print 'creato al der sche',al_der_sch
                    #mi occupo delle misure effettuate sulla madre. Salvo il quality
                    #event solo se sono state effettivamente compiute delle misure.
                    
                    if GEml!='' or purezza!='' or pur230!='':
                        #Prendo il quality protocol che e' il protocollo di misurazione
                        #che varia a seconda del tipo di derivato
                        #print 'tipo figlia',ti_aliq
                        qual_prot=QualityProtocol.objects.get(name='CirculatingDNA Nanodrop')
                        
                        qual_ev,creato=QualityEvent.objects.get_or_create(idQualityProtocol=qual_prot,
                                             idAliquot=aliq,
                                             idAliquotDerivationSchedule=al_der_sch,
                                             misurationDate=datadef,
                                             insertionDate=datadef,
                                             operator=operatore)
                        #salvo piu' oggetti perche' un'aliq potrebbe avere piu' misurazioni
                        if GEml!='':
                            qual=GEml.replace(',','.')
                            mis_qual=Measure.objects.get(name='GE/Vex')
                            mes_ev,creato=MeasurementEvent.objects.get_or_create(idMeasure=mis_qual,
                                                                          idQualityEvent=qual_ev,
                                                                          value=float(qual))
                        if purezza!='':
                            pur=purezza.replace(',','.')
                            mis_pur=Measure.objects.get(Q(name='purity')&Q(measureUnit='260/280'))
                            mes_ev,creato=MeasurementEvent.objects.get_or_create(idMeasure=mis_pur,
                                                                          idQualityEvent=qual_ev,
                                                                          value=float(pur))
                        
                        if pur230!='':
                            pu230=pur230.replace(',','.')
                            mis_pu230=Measure.objects.get(Q(name='purity')&Q(measureUnit='260/230'))
                            mes_ev,creato=MeasurementEvent.objects.get_or_create(idMeasure=mis_pu230,
                                                                          idQualityEvent=qual_ev,
                                                                          value=float(pu230))
                        
                        '''if concmadre!='':
                            cmadre=concmadre.replace(',','.')
                            strum=Instrument.objects.get(name='NANODROP')
                            mis_c=Measure.objects.get(Q(name='concentration')&Q(idInstrument=strum))
                            mes_ev,creato=MeasurementEvent.objects.get_or_create(idMeasure=mis_c,
                                                                          idQualityEvent=qual_ev,
                                                                          value=float(cmadre))'''
                    
                    #salvo il derivation event
                    der_ev,creato=DerivationEvent.objects.get_or_create(idSamplingEvent=samp_ev,
                                                                        idAliqDerivationSchedule=al_der_sch,
                                                                        derivationDate=datadef,
                                                                        operator=operatore)
                        
                    barcode=rig[0].strip()
                    barc_piastra=rig[5].strip()
                    posiz=rig[6].strip()
                    lista_archivio+=barc_piastra+'|'+barcode+'|'+posiz+','

                    #creo il genid
                    trovato=False
                    id=1
                    while not trovato:
                        val=str(id).zfill(2)
                        gen2=coll.idCollectionType.abbreviation+caso+tessuto.abbreviation+'H0000000000D'+val+'000'
                        print 'gen',gen2
                        #vedo se esiste gia' un'aliquota con questo codice 
                        lisal=Aliquot.objects.filter(uniqueGenealogyID=gen2)
                        print 'lisal',lisal
                        if len(lisal)==0:
                            trovato=1
                        else:
                            id=id+1

                    #guardo se e' esaurita
                    volum=rig[7].strip()
                    if volum=='ESAURITO':
                        avail=0
                    else:
                        avail=1
                    
                    #salvo l'aliquota                   
                    al=Aliquot(barcodeID=barcode,
                               uniqueGenealogyID=gen2,
                               idSamplingEvent=samp_ev,
                               idAliquotType=tipodna,
                               availability=avail,
                               timesUsed=0,
                               derived=1)
                    al.save()
                    #salvo il volume e la concentrazione dell'aliquota
                    if volum=='':
                        vol=-1
                    elif volum=='ESAURITO':
                        vol=0
                    else:
                        #devo dividere in base allo spazio per togliere le lettere "ul"
                        vvv=volum.split(' ')
                        vol=vvv[0].replace(',','.')
                    fea=Feature.objects.get(Q(idAliquotType=tipodna)&Q(name='OriginalVolume'))
                    aliqfeature=AliquotFeature(idAliquot=al,
                                               idFeature=fea,
                                               value=float(vol))
                    aliqfeature.save()
                    
                    fea=Feature.objects.get(Q(idAliquotType=tipodna)&Q(name='Volume'))
                    aliqfeature=AliquotFeature(idAliquot=al,
                                               idFeature=fea,
                                               value=float(vol))
                    aliqfeature.save()
                    
                    concentrazione=rig[9].strip()
                    if concentrazione=='':
                        conc=-1
                    else:
                        conc=concentrazione.replace(',','.')
                    fea=Feature.objects.get(Q(idAliquotType=tipodna)&Q(name='OriginalConcentration'))
                    aliqfeature=AliquotFeature(idAliquot=al,
                                               idFeature=fea,
                                               value=float(conc))
                    aliqfeature.save()
                    
                    fea=Feature.objects.get(Q(idAliquotType=tipodna)&Q(name='Concentration'))
                    aliqfeature=AliquotFeature(idAliquot=al,
                                               idFeature=fea,
                                               value=float(conc))
                    aliqfeature.save()
                                            
                    #j=j+1
                    #if j==14:
                        #break
                
                
            
            #scandisco gli eventi di trasf e aggiorno il times used della madre
            for key,value in dizmadri.items():
                key.timesUsed=value
                key.save()
            
            #tolgo l'ultima , alla fine della stringa
            lung=len(lista_archivio)-1
            l_arch_def=lista_archivio[:lung]
            #print 'l_arch_def',l_arch_def
            #comunico allo storage le provette che deve salvare
            url = Urls.objects.get(default = '1').url + "/historic/tube"          
            val1={'lista':l_arch_def}

            print 'url1',url
            data = urllib.urlencode(val1)
            req = urllib2.Request(url,data=data, headers={"workingGroups" : get_WG_string()})
            u = urllib2.urlopen(req)
            #u = urllib2.urlopen(url, data)
            res =  u.read() 
            if res=='err':
                raise ErrorHistoric('salvataggio storage')
                   
            f2=open(os.path.join(os.path.dirname(__file__),'tissue_media/File_Format/beaming_derived.sql'),'w')
            f2.write(stringa)
            f2.close()
                   
            return HttpResponse("ok")
            
        else:
            form = HistoricForm()
        variables = RequestContext(request, {'form':form})
        return render_to_response('tissue2/historic/storico_deriv.html',variables)
    except ErrorHistoric as e:
        print 'My exception occurred, value:', e.value
        transaction.rollback()
        return HttpResponse("err")
    except Exception,e:
        print 'err',e
        transaction.rollback()
        return HttpResponse("err")
    
#per caricare i campioni storici di FF
@transaction.commit_on_success
def HistoricFFPETissue(request):
    try:
        if request.method=='POST':
            print request.POST
            print request.FILES
            form=HistoricForm(request.FILES)
            listafile=request.FILES.getlist('file')
            
            #e' il file dei blocchetti da caricare
            f1=listafile[1]
            aliq_summ = f1.readlines()
            f1.close()
            
            #e' il file con le posizioni dei blocchetti
            f2=listafile[2]
            listaposizioni = f2.readlines()
            f2.close()
            
            #e' il file archivetissue
            f3=listafile[0]
            tissue = f3.readlines()
            f3.close()
            
            #e' il file series con le date
            f4=listafile[3]
            series = f4.readlines()
            f4.close()
            
            lista_archivio=''
            lista_da_posiz=''
            k=0
            
            tumori=CollectionType.objects.all()
            tessuti=TissueType.objects.all()
            tipi_aliq=AliquotType.objects.all()
            cas_generico=re.compile('(0\d\d\d)$')
            cas_thermo=re.compile('(\d\d\d)$')
            umano=re.compile('(X|H)$')
            topo=re.compile('([A-Za-z]\d\d\d\d\d(TUM|LNG|LIV|GUT|BLD|MLI|MBR|MLN))$')
            topo_thermo=re.compile('([A-Za-z]\d\d\d\d\d)$')
            uomo=re.compile('(000000000)$')
            uomo_thermo=re.compile('(000000)$')
            contatore=re.compile('(\d\d)$')
            pos=re.compile('([A-Ja-j]\d\d*)$')
            
            datainiz=datetime.date(2010,1,1)
            ti_aliq=AliquotType.objects.get(abbreviation='FF')
            
            #for righe_aliq in aliq_summ:
            for kk in range(0,len(aliq_summ)):
                righe_aliq=aliq_summ[kk]
                rig=righe_aliq.split(';')    
                salta=rig[2].strip()
                #print 'rig',righe_aliq
                if salta!='1':
                    err=''
                    gen_id_prova=rig[1].strip()
                    barcode=rig[0].strip()
                    print 'gen',gen_id_prova
                    #serve per valutare il codice del tumore
                    tum=gen_id_prova[0:3]
                    trovato=False
                    for i in range(0,len(tumori)):
                        if tum==str(tumori[i].abbreviation):
                            trovato =True
                            break; 
                    if trovato==False:
                        err=gen_id_prova+': tumore inesistente. '+rig[1]
                        continue
                    #serve per valutare il codice del caso
                    #il problema e' che alcuni hanno 3 cifre altri 4
                    caso=gen_id_prova[3:7]
                    partenza=7
                    if not cas_generico.match(caso):
                        caso2=gen_id_prova[3:6]
                        partenza=6
                        if not cas_thermo.match(caso2):
                            err=gen_id_prova+': caso errato. '+rig[1]
                            continue
                    #serve per valutare il codice del tessuto
                    tess=gen_id_prova[partenza:partenza+2]
                    #print 'tess',tess
                    trovato2=False
                    for i in range(0,len(tessuti)):
                        if tess==str(tessuti[i].abbreviation):
                            trovato2 =True
                            break;                             
                    if trovato2==False:
                        err=gen_id_prova+': tessuto inesistente. '+rig[1]
                        continue
                    #serve per valutare l'H o la X
                    tipo=gen_id_prova[partenza+2:partenza+3]
                    #print 'tipo',tipo
                    if not umano.match(tipo):
                        err=gen_id_prova+': Problema su X/H. '+rig[1]
                        continue
                    parte_centr=gen_id_prova[partenza+3:partenza+9]
                    #serve per valutare i 6 valori dopo l'H o la X
                    if tipo=='X':
                        if not topo_thermo.match(parte_centr):
                            err=gen_id_prova+': Problema su codice topo. '+rig[1]
                            continue
                    elif tipo=='H':
                        if not uomo_thermo.match(parte_centr):
                            err=gen_id_prova+': Problema sul numero di zeri dopo H. '+rig[1]
                            continue
                    #serve per valutare il tipo di aliq (VT,SF...)
                    tipo_al=gen_id_prova[partenza+12:partenza+14]
                    #print 'tipoal',tipo_al
                    trovato3=False
                    for i in range(0,len(tipi_aliq)):
                        if tipo_al==str(tipi_aliq[i].abbreviation):
                            trovato3 =True
                            break; 
                    if trovato3==False:
                        print 'tipo',tipo_al
                        err=gen_id_prova+': Problema sul tipo di aliquota (RL,SF,...). '+rig[1]
                        #print err
                    #serve per valutare il contatore finale del genid
                    cont=gen_id_prova[partenza+14:partenza+16]
                    if not contatore.match(cont):
                        err=gen_id_prova+': Problema sul contatore finale. '+rig[1]
                        #print err
                    if err!='':    
                        print 'problemi',err

                    #trovo la posizione del blocchetto
                    for righe_pos in listaposizioni:
                        rig_posiz=righe_pos.split(';')
                        barc=rig_posiz[8].strip()
                        if barc==barcode:
                            cass='H000'+rig_posiz[10].strip()
                            pos=rig_posiz[11].strip()
                    print 'pos',pos
                    #devo vedere se il campione esiste gia' o no
                    lisaliq=Aliquot.objects.filter(barcodeID=barcode)
                    
                    #c'e' gia' il campione quindi devo solo posizionarlo
                    if len(lisaliq)!=0:
                        al=lisaliq[0]
                        #gen_effettivo=gen_id_prova[0:10]+'0'+gen_id_prova[10:]
                        lista_da_posiz+=cass+'|'+barcode+'|'+pos+','
                            
                    #devo creare il campione
                    else:
                        tumore=CollectionType.objects.get(abbreviation=tum)
                        cas=str(caso)
                        liscoll=Collection.objects.filter(Q(idCollectionType=tumore)&Q(itemCode=cas))
                        if liscoll.count()!=1:
                            raise ErrorHistoric(righe_aliq)
                        coll=liscoll[0] 
                        #prendo il tipo di tessuto
                        tessuto=TissueType.objects.get(abbreviation=tess)
                        operat=''
                        data=''
                        for valor in tissue:
                            
                            righe_tess=valor.split(';')
                            gen_tess=righe_tess[4]
                            gen_modif=gen_id_prova[0:3]+gen_id_prova[4:16]+gen_id_prova[19:23]
                            #print 'tess',gen_tess
                            #print 'modif',gen_modif
                            if gen_tess==gen_modif:
                                print 'tess',gen_tess
                                print 'modif',gen_modif
                                chiave_serie=righe_tess[2]
                                print 'chiave',chiave_serie
                                #prendo gli ultimi quattro caratteri della stringa
                                num_serie=chiave_serie[-4:]
                                print 'num_serie',num_serie
                                for serie in series:
                                    val=serie.split(';')
                                    num=val[0]
                                    n=num[-4:]
                                    #print 'n',n
                                    #print 'num',num
                                    if n==num_serie:
                                        oper=val[1]
                                        if oper=='Zanella':
                                            operat='eugenia.zanella'
                                        elif oper=='Migliardi':
                                            operat='giorgia.migliardi'
                                        dat=val[2]
                                        d=dat.split('/')
                                        data=d[2]+'-'+d[1]+'-'+d[0]
                                        #print 'operat inter',operat
                        print 'operat',operat
                        if operat=='' or data=='':
                            operat='eugenia.zanella'
                            data=datainiz
                        
                        #devo salvare la serie            
                        serie_def,creato2=Serie.objects.get_or_create(operator=operat,
                                                          serieDate=data)
                    
                    
                        samp_ev,creato3=SamplingEvent.objects.get_or_create(idTissueType=tessuto,
                                                                        idCollection=coll,
                                                                        idSource=coll.idSource,
                                                                        idSerie=serie_def,
                                                                        samplingDate=data)
                    
                        lista_archivio+=cass+'|'+barcode+'|'+pos+','

                        #creo il genid
                        genid=gen_id_prova[0:10]+'0'+gen_id_prova[10:13]+'2'+gen_id_prova[14:]
                        avail=1
                        
                        #salvo l'aliquota
                        al=Aliquot(barcodeID=barcode,
                                   uniqueGenealogyID=genid,
                                   idSamplingEvent=samp_ev,
                                   idAliquotType=ti_aliq,
                                   availability=avail,
                                   timesUsed=0,
                                   derived=0)
                        al.save()
                        
                        #salvo il numero di pezzi dell'aliquota
                        num_pezzi=1
                        fea=Feature.objects.get(Q(idAliquotType=ti_aliq)&Q(name='NumberOfPieces'))
                        aliqfeature=AliquotFeature(idAliquot=al,
                                                   idFeature=fea,
                                                   value=num_pezzi)
                        aliqfeature.save()
                        
                    k=k+1
                    if k==2:
                        break
                    
            print 'lista posiz',lista_da_posiz
            lung=len(lista_da_posiz)-1
            l_arch_def=lista_da_posiz[:lung]
            print 'l_arch_def',l_arch_def
            #comunico allo storage le provette che deve posizionare
            url = Urls.objects.get(default = '1').url + "/historic/ffpe"          
            val1={'lista':l_arch_def}
            print 'url1',url
            data = urllib.urlencode(val1)
            req = urllib2.Request(url,data=data, headers={"workingGroups" : get_WG_string()})
            u = urllib2.urlopen(req)
            #u = urllib2.urlopen(url, data)
            res =  u.read() 
            if res=='err':
                raise ErrorHistoric('salvataggio storage')
            
            print 'lista archivio',lista_archivio
            lung=len(lista_archivio)-1
            l_arch_def=lista_archivio[:lung]
            print 'l_arch_def',l_arch_def
            #comunico allo storage le provette che deve salvare
            url = Urls.objects.get(default = '1').url + "/historic/tube"          
            val1={'lista':l_arch_def}
            print 'url1',url
            data = urllib.urlencode(val1)
            req = urllib2.Request(url,data=data, headers={"workingGroups" : get_WG_string()})
            u = urllib2.urlopen(req)
            #u = urllib2.urlopen(url, data)
            res =  u.read() 
            if res=='err':
                raise ErrorHistoric('salvataggio storage')
            
            return HttpResponse("ok")
        else:
            form = HistoricForm()
        variables = RequestContext(request, {'form':form})
        return render_to_response('tissue2/historic/storico_tess.html',variables)
    except ErrorHistoric as e:
        print 'My exception occurred, value:', e.value
        transaction.rollback()
        return HttpResponse("err")
    except Exception,e:
        print 'err',e
        transaction.rollback()
        return HttpResponse("err")
    
#per controllare la coerenza tra collection event e codice del caso
@transaction.commit_on_success
def CheckPatientID(request):
    try:
        if request.method=='POST':
            print request.POST
            print request.FILES  
            form=HistoricForm(request.FILES)
            listafile=request.FILES.getlist('file')
            
            #e' il file con le corrispondenze tra coll event e codice caso
            f1=listafile[0]
            coll_summ = f1.readlines()
            f1.close()
            
            err=''
            k=0
            for righe in coll_summ:
                rig=righe.strip().split(';') 
                #print 'rig',rig   
                colev1=rig[2].strip()
                #print 'colev1',colev1
                colev2=rig[3].strip()
                #print 'coelv2',colev2
                colmau=rig[6].strip().lower()
                #prendo le ultime 4 cifre
                caso1=rig[4].strip()[-4:]
                #print 'caso',caso1
                caso2=rig[5].strip()[-4:]
                
                if colev1!='':
                    collec=Collection.objects.filter(collectionEvent=colev1)
                    if len(collec)!=0:
                        casocoll=collec[0].itemCode
                        if casocoll!=caso1:
                            err+='coll event1 non corrisponde al caso. '+righe
                    else:
                        #se non trovo una collezione, ma anche la riga del file e' vuota, allora va bene
                        if caso1!='':
                            err+='collezione senza caso1. '+righe
                if colev2!='':
                    collec=Collection.objects.filter(collectionEvent=colev2)
                    if len(collec)!=0:
                        casocoll=collec[0].itemCode
                        if casocoll!=caso2:
                            err+='coll event2 non corrisponde al caso. '+righe
                    else:
                        #se non trovo una collezione, ma anche la riga del file e' vuota, allora va bene
                        if caso2!='':
                            err+='collezione senza caso2. '+righe
                if colmau!='':
                    collec=Collection.objects.filter(collectionEvent=colmau)
                    if len(collec)!=0:
                        casocoll=collec[0].itemCode.lower()
                        if casocoll!=caso1:
                            err+='coll event mau non corrisponde al caso. '+righe
                    else:
                        #se non trovo una collezione, ma anche la riga del file e' vuota, allora va bene
                        if caso1!='':
                            err+='collezione mau senza caso. '+righe
                
                #k=k+1
                #if k==3:
                    #break            
            print 'err',err
            return HttpResponse("ok")
        else:
            form = HistoricForm()
        variables = RequestContext(request, {'form':form})
        return render_to_response('tissue2/historic/storico_expl.html',variables)
    except ErrorHistoric as e:
        print 'My exception occurred, value:', e.value
        transaction.rollback()
        return HttpResponse("err")
    except Exception,e:
        print 'err',e
        transaction.rollback()
        return HttpResponse("err")
    
#per salvare il valore del codice paziente in corrispondenza del caso
@transaction.commit_on_success
def SavePatientID(request):
    try:
        if request.method=='POST':
            print request.POST
            print request.FILES  
            form=HistoricForm(request.FILES)
            listafile=request.FILES.getlist('file')
            
            #e' il file con le corrispondenze tra coll event e codice caso
            f1=listafile[0]
            coll_summ = f1.readlines()
            f1.close()

            k=0
            for righe in coll_summ:
                rig=righe.strip().split(';')
                caso1=rig[4].strip()[-4:]
                print 'caso1',caso1
                tum1=rig[4].strip()[:3]
                #print 'tum1',tum1
                caso2=rig[5].strip()[-4:]
                print 'caso2',caso2
                tum2=rig[5].strip()[:3]
                #print 'tum2',tum2
                paziente=rig[1].strip()
                print 'paz',paziente
                
                if caso1!='':
                    tipotum=CollectionType.objects.get(abbreviation=tum1)
                    collez=Collection.objects.get(itemCode=caso1,idCollectionType=tipotum)
                    collez.patientCode=paziente
                    collez.save()
                    
                if caso2!='':
                    tipotum=CollectionType.objects.get(abbreviation=tum2)
                    collez=Collection.objects.get(itemCode=caso2,idCollectionType=tipotum)
                    collez.patientCode=paziente
                    collez.save()
                
                #k=k+1
                #if k==5:
                    #break
            return HttpResponse("ok")
        else:
            form = HistoricForm()
        variables = RequestContext(request, {'form':form})
        return render_to_response('tissue2/historic/storico_impl.html',variables)
    except ErrorHistoric as e:
        print 'My exception occurred, value:', e.value
        transaction.rollback()
        return HttpResponse("err")
    except Exception,e:
        print 'err',e
        transaction.rollback()
        return HttpResponse("err")
    
#caricando gli impianti storici sono venuti fuori errori sugli impianti inseriti in 
#precedenza con le VT99. Questa vista serve a correggere le aliquote legate a quegli 
#impianti che poi hanno dato origine a degli espianti. Viene corretto il lineage o il 
#passaggio
@transaction.commit_on_success
def HistoricChangeAliquot(request):
    try:
        if request.method=='POST':
            print request.POST
            print request.FILES  
            form=HistoricForm(request.FILES)
            listafile=request.FILES.getlist('file')
            
            #e' il file con la prima lista delle aliq da correggere
            f1=listafile[0]
            lis_aliq = f1.readlines()
            f1.close()
            
            #e' il file con la seconda lista delle aliq da correggere
            f1=listafile[1]
            lis_2 = f1.readlines()
            f1.close()
            
            stringa='vecchio gen\t nuovo gen\n'
            
            for l in lis_aliq:
                valori=l.split(';')
                ge=valori[3].strip()
                gen_vecchio=ge
                #print 'gen_ vecchio',gen_vecchio
                aliq=Aliquot.objects.get(uniqueGenealogyID=gen_vecchio)
                print 'aliq',aliq
                #se e' CRC77 devo ridurre il passaggio di 1
                #altrimenti devo cambiare A con B o viceversa
                gen=GenealogyID(gen_vecchio)
                if gen_vecchio[0:7]=='CRC0077':
                    passaggio=int(gen.getSamplePassage())
                    passaggio=str(int(passaggio-1))
                    if len(passaggio)<2:
                        passaggio='0'+passaggio
                    gen.updateGenID({'samplePassage':passaggio})
                    
                else:
                    lin=gen.getLineage()
                    if lin=='0A':
                        nuovo_lin='0B'
                    else:
                        nuovo_lin='0A'
                    gen.updateGenID({'lineage':nuovo_lin})
                
                nuovo_gen=gen.getGenID()
                #print 'nuovo gen',nuovo_gen
                aliq.uniqueGenealogyID=nuovo_gen
                stringa+=gen_vecchio+'\t'+nuovo_gen+'\n'
                #aliq.save()
                
                #vedo se l'aliq ha dato origine a dei derivati
                l_der=AliquotDerivationSchedule.objects.filter(idAliquot=aliq)
                if len(l_der)!=0:
                    #print 'trovato der',aliq
                    for der in l_der:
                        derev=DerivationEvent.objects.filter(idAliqDerivationSchedule=der)
                        if len(derev)!=0:
                            #prendo le aliq derivate
                            lista_al=Aliquot.objects.filter(idSamplingEvent=derev[0].idSamplingEvent)
                            for al in lista_al:
                                gen_vec=al.uniqueGenealogyID
                                gen=GenealogyID(gen_vec)
                                if gen_vec[0:7]=='CRC0077':
                                    passaggio=int(gen.getSamplePassage())
                                    passaggio=str(int(passaggio-1))
                                    if len(passaggio)<2:
                                        passaggio='0'+passaggio
                                    gen.updateGenID({'samplePassage':passaggio})
                                    
                                else:
                                    lin=gen.getLineage()
                                    if lin=='0A':
                                        nuovo_lin='0B'
                                    else:
                                        nuovo_lin='0A'
                                    gen.updateGenID({'lineage':nuovo_lin})
                                
                                nuovo_g=gen.getGenID()
                                #print 'nuovo gen',nuovo_g
                                al.uniqueGenealogyID=nuovo_g
                                #al.save()
            
            #e' la lista 2, quella con solo i CRC77
            #devo diminuire di 1 il passaggio e cambiare il numero del topo
            for ali in lis_2:
                valori=ali.split(';')
                ge=valori[3].strip()
                nuovo_topo=valori[4].strip()
                aliq=Aliquot.objects.get(uniqueGenealogyID=ge)
                print 'aliq',aliq
                gen=GenealogyID(ge)
                passaggio=int(gen.getSamplePassage())
                passaggio=str(int(passaggio-1))
                if len(passaggio)<2:
                    passaggio='0'+passaggio
                nuovo_topo=str(nuovo_topo)
                if len(nuovo_topo)<2:
                    nuovo_topo='00'+nuovo_topo
                elif len(nuovo_topo)<3:
                    nuovo_topo='0'+nuovo_topo
                gen.updateGenID({'samplePassage':passaggio,'mouse':nuovo_topo})
                nuovo_gen=gen.getGenID()
                print 'nuovo gen',nuovo_gen
                aliq.uniqueGenealogyID=nuovo_gen
                stringa+=ge+'\t'+nuovo_gen+'\n'
                #aliq.save()
                
                #vedo se l'aliq ha dato origine a dei derivati
                l_der=AliquotDerivationSchedule.objects.filter(idAliquot=aliq)
                if len(l_der)!=0:
                    #print 'trovato der',aliq
                    for der in l_der:
                        derev=DerivationEvent.objects.filter(idAliqDerivationSchedule=der)
                        if len(derev)!=0:
                            #prendo le aliq derivate
                            lista_al=Aliquot.objects.filter(idSamplingEvent=derev[0].idSamplingEvent)
                            for al in lista_al:
                                gen_vec=al.uniqueGenealogyID
                                gen=GenealogyID(gen_vec)
                                gen.updateGenID({'samplePassage':passaggio,'mouse':nuovo_topo})
                                nuovo_g=gen.getGenID()
                                #print 'nuovo gen',nuovo_g
                                al.uniqueGenealogyID=nuovo_g
                                #al.save()
                                                                   
            f2=open(os.path.join(os.path.dirname(__file__),'tissue_media/Historical/Aliq_corrette.txt'),'w')
            f2.write(stringa)
            f2.close()
            return HttpResponse("ok")
        else:
            form = HistoricForm()    
        variables = RequestContext(request, {'form':form})
        return render_to_response('tissue2/historic/storico_error_impl.html',variables)
    except ErrorHistoric as e:
        print 'My exception occurred, value:', e.value
        transaction.rollback()
        return HttpResponse("err")
    except Exception,e:
        print 'err',e
        transaction.rollback()
        return HttpResponse("err")
    
#per controllare se i cRNA ibridati storici esistono tutti nella biobanca
def CheckcRNA(request):
    try:
        if request.method=='POST':
            print request.POST
            print request.FILES  
            form=HistoricForm(request.FILES)
            listafile=request.FILES.getlist('file')
            
            #e' il file con la lista dei cRNA
            f1=listafile[0]
            coll_summ = f1.readlines()
            f1.close()

            k=1
            stringa1=''
            stringa2=''
            for righe in coll_summ:
                rig=righe.strip().split('\t')
                genid=rig[2].upper()
                
                lisaliq=Aliquot.objects.filter(uniqueGenealogyID=genid)
                #se l'aliq c'e' gia' allora va bene, altrimenti provo ad aggiungere il 2
                if len(lisaliq)==0:
                    gencon2=genid[0:14]+'2'+genid[15:]
                    #print 'gen2',gencon2
                    lis2=Aliquot.objects.filter(uniqueGenealogyID=gencon2)
                    if len(lis2)==0:
                        stringa1+=genid+' '+str(k)+'\n'
                    else:
                        stringa2+=genid+' '+str(k)+'\n'
                k=k+1
            f1=open(os.path.join(os.path.dirname(__file__),'tissue_media/Historical/Aliquote_non_presenti.txt'),'w')
            f1.write(stringa1)
            f1.close()
            
            f2=open(os.path.join(os.path.dirname(__file__),'tissue_media/Historical/Aliquote_con_2.txt'),'w')
            f2.write(stringa2)
            f2.close()
            return HttpResponse("ok")
        else:
            form = HistoricForm()
        variables = RequestContext(request, {'form':form})
        return render_to_response('tissue2/historic/storico_mice_deriv.html',variables)
    except Exception,e:
        print 'err',e
        return HttpResponse("err")
    
#per controllare se certi topi, una volta espiantati, possano dare origine a delle aliquote gia' presenti nella biobanca 
def CheckTopiImpiantati(request):
    try:
        if request.method=='POST':
            print request.POST
            print request.FILES
            form=HistoricForm(request.FILES)
            listafile=request.FILES.getlist('file')
            
            #e' il file con la lista dei topi
            f1=listafile[0]
            topi_summ = f1.readlines()
            f1.close()

            stringa1=''
            for righe in topi_summ:
                rig=righe.strip().split('\t')
                #parto da 1 per togliere le virgolette che mette il csv e fermarmi prima degli zeri propri del topo
                genid=rig[4][1:18]
                print 'genid',genid
                
                lisaliq=Aliquot.objects.filter(uniqueGenealogyID__istartswith=genid)
                #se c'e' l'aliq allora devo segnalarlo e metterla nella lista di quelli da cambiare
                if len(lisaliq)!=0:
                    stringa1+=genid+' \n'
            f1=open(os.path.join(os.path.dirname(__file__),'tissue_media/Historical/Topi_presenti.txt'),'w')
            f1.write(stringa1)
            f1.close()

            return HttpResponse("ok")
        else:
            form = HistoricForm()
        variables = RequestContext(request, {'form':form})
        return render_to_response('tissue2/historic/storico_error_impl.html',variables)
    except Exception,e:
        print 'err',e
        return HttpResponse("err")

#per caricare gli aggiornamenti delle linee cellulari
@transaction.commit_on_success
def UpdateCellLine(request):
    try:
        if request.method=='POST':
            print request.POST
            print request.FILES  
            form=HistoricForm(request.FILES)
            listafile=request.FILES.getlist('file')
            wg='Bardelli_WG'
            set_initWG([wg])
            lisnotexists=[]
            pr=CollectionProtocol.objects.get(project='CellLines')
            #e' il file delle linee da caricare
            f1=listafile[0]
            aliq_summ = f1.readlines()
            f1.close()
            
            lista_archivio=''
            k=0
            disable_graph()
            #mi occupo del tipo di aliq (VT)
            ti_aliq=AliquotType.objects.get(abbreviation='VT')
            lisserie=Serie.objects.filter(Q(operator='carlotta.cancelliere')|Q(operator='sandra.misale')|Q(operator='mariangela.russo'))
            #print 'lisserie',lisserie
            lisampl=SamplingEvent.objects.filter(idSerie__in=lisserie)
            #print 'lisampl',lisampl
            listaal=Aliquot.objects.filter(Q(idAliquotType=ti_aliq)&Q(idSamplingEvent__in=lisampl))
            enable_graph()
            #dizionario in cui la chiave e' linea+passaggio+data e il valore e' il numero di campioni di quel tipo che ci sono 
            dizgenerale={}
            for i in range (0,len(aliq_summ)):                              
                righe_aliq=aliq_summ[i]
                rig=righe_aliq.split(';')    
                
                barc=rig[0].strip()
                if barc!='':
                    nomelinea=rig[1].strip()
                    passaggio=rig[2].strip()
                    if passaggio=='':
                        passaggio='1'
                    datacong=rig[3].strip()
                    tumore=CollectionType.objects.get(abbreviation='CRC')
                    
                    trovato=False
                    linmax=ord('A')
                    caso=''
                    vector='A'
                    scongelam='0'
                    for al in listaal:
                        #prendo il barc e vedo quale sia la linea cellulare
                        barcode=al.barcodeID
                        vbarc=barcode.split('_')
                        valbar=vbarc[0].split('-')
                        linea=valbar[0]
                        if linea==nomelinea:
                            print 'aliq',al
                            gen=GenealogyID(al.uniqueGenealogyID)
                            #lin=ord(gen.getLineage()[1])
                            #il sample passage per le linee sono gli scongelamenti
                            scongtemp=gen.getSamplePassage()
                            print 'scongtemp',scongtemp
                            print 'scongelam',int(scongelam)
                            print 'scongtemp',int(scongtemp)
                            if int(scongtemp)>int(scongelam):
                                scongelam=scongtemp
                            print 'scongelam',scongelam
                            #if lin>linmax:
                                #linmax+=1
                            #print 'linmax',linmax
                            coll=al.idSamplingEvent.idCollection
                            caso=coll.itemCode
                            tes=al.idSamplingEvent.idTissueType
                            vector=gen.getSampleVector()
                            trovato=True
                    
                    dat=datacong.split('/')
                    datadef=dat[2]+'-'+dat[1]+'-'+dat[0]
                    print 'datadef',datadef
                    #mi occupo dell'operatore
                    operatore=rig[4].strip()
                    if operatore=='Carlotta':
                        oper='carlotta.cancelliere'
                    elif operatore=='Mary':
                        oper='mariangela.russo'
                    elif operatore=='Sandra':
                        oper='sandra.misale'
                    
                    chiave=nomelinea+'-P'+passaggio+'-'+datacong
                    #solo se ho trovato dei campioni appartenenti a quella linea                 
                    if trovato:
                        #linmax+=1
                        scongelam=int(scongelam)+1
                        creaoggetti=False
                        if not dizgenerale.has_key(chiave):
                                 
                            serie_def,creato2=Serie.objects.get_or_create(operator=oper,
                                                                          serieDate=datadef)
                            samp_ev=SamplingEvent(idTissueType=tes,
                                                idCollection=coll,
                                                idSource=coll.idSource,
                                                idSerie=serie_def,
                                                samplingDate=datadef)
                            samp_ev.save()
                            print 'samp',samp_ev
                            dizgenerale[chiave]=1
                            contatore=1
                            creaoggetti=True                          
                    
                        else:
                            valor=dizgenerale[chiave]
                            contatore=int(valor)+1
                            
                            dizgenerale[chiave]=contatore
                    #e' una linea che non esiste
                    else:
                        #se la combinazione dei tre non c'e' ancora nel diz, devo creare un nuovo caso
                        creaoggetti=False
                        print 'dizgenerale',dizgenerale
                        print 'chiave',chiave
                        if not dizgenerale.has_key(chiave):
                            #faccio la chiamata al LASHub per farmi dare il codice del caso
                            prefisso= 'https://' if settings.LAS_AUTH_USE_HTTPS else 'http://'
                            address=request.get_host()+settings.HOST_URL
                            indir=prefisso+address
                            url = indir + '/clientHUB/getAndLock/'
                            print 'url',url
                            values = {'randomFlag' : False, 'case': 'CRC'}
                            
                            r = requests.post(url, data=values, verify=False)
                            
                            print 'r.text',r.text
                            if r.text=='not active':
                                
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
                                caso=r.text
                            
                            print 'caso',caso
                            dizgenerale[chiave]='1|'+str(caso)
                            contatore=1
                            creaoggetti=True
                        else:
                            valor=dizgenerale[chiave].split('|')
                            contatore=int(valor[0])+1
                            caso=valor[1]
                            dizgenerale[chiave]=str(contatore)+'|'+str(caso)
                                               
                        sorg=rig[9].strip()
                        print 'sorg',sorg
                        if sorg=='#N/D':
                            sorg='Unknown'
                        sorgente=Source.objects.get(type='Hospital',name=sorg)
        
                        collevent=nomelinea
                        #devo creare la collezione
                        coll,creato1=Collection.objects.get_or_create(itemCode=caso,
                                        idCollectionType=tumore,
                                        idSource=sorgente,
                                        collectionEvent=collevent,
                                        idCollectionProtocol=pr)
                        if creato1:
                            #solo se ho creato una nuova collezione comunico al modulo clinico le informazioni                
                            #L'ic non esiste ancora perche' lo sto creando adesso dal nulla, quindi non faccio 
                            #il controllo di esistenza tramite le API del modulo clinico. La chiave paziente la metto vuota perche' sto creando un paziente nuovo.
                            #Se mettessi il valore, il modulo clinico andrebbe a cercare quel paziente sul grafo e non trovandolo darebbe errore. Invece cosi' crea lui il nuovo dato
                            diztemp={'caso':coll.itemCode,'tum':coll.idCollectionType.abbreviation,'consenso':coll.collectionEvent,'progetto':coll.idCollectionProtocol.project,'source':coll.idSource.internalName,'wg':[wg],'operator':oper,'paziente':''}
                            lisnotexists.append(diztemp)                                                
                        
                        if creaoggetti:
                            #devo creare il sampling event
                            #prendo il tipo di tessuto
                            tess=rig[8].strip()
                            print 'tess',tess
                            if tess=='Primary':
                                abbr='PR'
                            elif tess=='Lymph node metastasis':
                                abbr='LY'
                            elif tess=='Lung Metastasis':
                                abbr='TM'
                            elif tess=='Lymph node metastasis':
                                abbr='LY'
                            elif tess=='Liver Metastasis':
                                abbr='LM'
                            elif tess=='Ascitic Fluid':
                                abbr='AF'
                            tes=TissueType.objects.get(abbreviation=abbr)                                    
                                 
                            serie_def,creato2=Serie.objects.get_or_create(operator=oper,
                                                                          serieDate=datadef)
                            samp_ev=SamplingEvent(idTissueType=tes,
                                                idCollection=coll,
                                                idSource=coll.idSource,
                                                idSerie=serie_def,
                                                samplingDate=datadef)
                            samp_ev.save()
                            print 'samp',samp_ev
                    
                    #aggiungo la parte finale al barcode per disambiguare quelli uguali
                    barc+='_'+str(contatore)
                    print 'barc',barc
                    lineage=chr(linmax)
                    lineagefin=str(lineage).zfill(2)
                    print 'linfin',lineagefin
                    
                    barc_piastra=rig[6].strip()
                    posiz=rig[7].strip()                    

                    passaggio=rig[2].strip()
                    if passaggio=='':
                        passaggio=1
                    passfin=str(passaggio).zfill(3)
                    
                    scong=rig[10].strip()
                    print 'scong',scong
                    if scong=='' or scong=='0':
                        scong=scongelam
                    scongfin=str(scong).zfill(2)
                    
                    #creo il genid
                    val=str(contatore).zfill(2)
                    print 'val',val
                    genid=coll.idCollectionType.abbreviation+caso+tes.abbreviation+vector+lineagefin+scongfin+passfin+'001'+ti_aliq.abbreviation+val+'00'
                    print 'gen',genid
                    #vedo se esiste gia' un'aliquota con questo codice 
                    lisal=Aliquot.objects.filter(uniqueGenealogyID=genid)
                    print 'lisal',lisal
                    if len(lisal)!=0:
                        raise Exception

                    #salvo l'aliquota
                    al=Aliquot(barcodeID=barc,
                               uniqueGenealogyID=genid,
                               idSamplingEvent=samp_ev,
                               idAliquotType=ti_aliq,
                               availability=1,
                               timesUsed=0,
                               derived=0)
                    print 'al',al
                    al.save()
                    lista_archivio+=barc_piastra+'|'+barc+'|'+posiz+'|'+genid+'|'+datadef+','
                #k=k+1
                #if k==12:
                    #break
                    
            print 'lista archivio',lista_archivio
            lung=len(lista_archivio)-1
            l_arch_def=lista_archivio[:lung]
            print 'l_arch_def',l_arch_def
            #comunico allo storage le provette che deve salvare
            url = Urls.objects.get(default = '1').url + "/historic/tube"          
            val1={'lista':l_arch_def}

            print 'url1',url
            data = urllib.urlencode(val1)
            req = urllib2.Request(url,data=data, headers={"workingGroups" : get_WG_string()})
            u = urllib2.urlopen(req)
            #u = urllib2.urlopen(url, data)
            res =  u.read() 
            if res=='err':
                raise ErrorHistoric('salvataggio storage')                
            
            #metto il commit perche' il modulo clinico deve gia' trovare sul grafo il nodo collezione
            transaction.commit()
            
            errore=saveInClinicalModule([],lisnotexists,[wg],'',[])
            if errore:
                raise Exception()
            
            return HttpResponse("ok")
        else:
            form = HistoricForm()
        variables = RequestContext(request, {'form':form})
        return render_to_response('tissue2/historic/storico_save_impl.html',variables)
    except ErrorHistoric as e:
        print 'My exception occurred, value:', e.value
        transaction.rollback()
        return HttpResponse("err")
    except Exception,e:
        print 'err',e
        transaction.rollback()
        return HttpResponse("err")

#serve una volta per aggiornare i casi nelle linee cellulari
@transaction.commit_on_success
def NewCellLine(request):
    try:
        #prendo solo le aliquote vitali
        vit=AliquotType.objects.get(abbreviation='VT')
        tumcrc=CollectionType.objects.get(abbreviation='CRC')
        tumovr=CollectionType.objects.get(abbreviation='OVR')
        lisserie=Serie.objects.filter(Q(operator='carlotta.cancelliere')|Q(operator='sandra.misale')|Q(operator='mariangela.russo'))
        print 'lisserie',lisserie
        lisampl=SamplingEvent.objects.filter(idSerie__in=lisserie)
        print 'lisampl',lisampl
        listaal=Aliquot.objects.filter(Q(idAliquotType=vit)&Q(idSamplingEvent__in=lisampl))
        print 'listaal',listaal
        print 'lung',len(listaal)
        diz={}
        dizordinamenti={}
        
        for sampl in lisampl:
            collez=sampl.idCollection
            #cambio il coll event
            colleven=collez.collectionEvent
            valcollev=colleven.split('-')
            collez.collectionEvent=valcollev[0]
            print 'valcoll',valcollev[0]
            #collez.save()
        
        for al in listaal:
            #prendo il barc e vedo quale sia la linea cellulare
            barc=al.barcodeID
            vbarc=barc.split('_')
            valbar=vbarc[0].split('-')
            linea=valbar[0]
            if diz.has_key(linea):
                diztemp=diz[linea]
            else:
                diztemp={}
                
            if dizordinamenti.has_key(linea):
                lisord=dizordinamenti[linea]
            else:
                lisord=[]
                
            if diztemp.has_key(vbarc[0]):
                listemp=diztemp[vbarc[0]]
            else:
                listemp=[]
            listemp.append(al)
            diztemp[vbarc[0]]=listemp
            if vbarc[0] not in lisord:
                lisord.append(vbarc[0])
            dizordinamenti[linea]=lisord
            diz[linea]=diztemp
            
        for key,val in diz.items():
            #val e' un dizionario
            lisordinata=dizordinamenti[key]
            print 'lisord',lisordinata
            print 'val',val
            caso=''
            for i in range(0,len(lisordinata)):
                chiave=lisordinata[i]                    
                print 'chiave',chiave
                lisaliq=val[chiave]
                print 'lisaliq',lisaliq
                if i==0:
                    #devo prendere il caso
                    al=lisaliq[0]
                    gen=GenealogyID(al.uniqueGenealogyID)
                    caso=gen.getCaseCode()
                else:
                    for aliq in lisaliq:
                        print 'aliq',aliq
                        gen=GenealogyID(aliq.uniqueGenealogyID)
                        #cambio il codice del caso
                        print 'caso',caso
                        gen.updateGenID({'caseCode':caso})
                        #devo aggiornare il lineage
                        lin=ord('A')+i
                        lineage='0'+chr(lin)
                        print 'lineage',lineage
                        gen.updateGenID({'lineage':lineage})
                        aliq.uniqueGenealogyID=gen.getGenID()
                        #aliq.save()
                        #cambio il valore della collezione nel sampling
                        collez=Collection.objects.get(Q(Q(idCollectionType=tumcrc)|Q(idCollectionType=tumovr))&Q(itemCode=caso))
                        print 'collez',collez
                        
                        samp=aliq.idSamplingEvent
                        samp.idCollection=collez
                        print 'samp',samp
                        #samp.save()
                print 'casoext',caso
        print 'lung',len(listaal)
        print 'diz',diz
        return HttpResponse("ok")
    except Exception,e:
        print 'err',e
        transaction.rollback()
        return HttpResponse("err")
    
#serve una volta per salvare gli id delle linee nelle collezioni gia' esistenti
@transaction.commit_on_success
def CellUpdateCollection(request):
    try:
        feat=ClinicalFeature.objects.get(name='idCellLine')
        servizio=WebService.objects.get(name='Annotation')
        urlcell=Urls.objects.get(idWebService=servizio).url
        lisserie=Serie.objects.filter(Q(operator='carlotta.cancelliere')|Q(operator='sandra.misale')|Q(operator='mariangela.russo'))
        print 'lisserie',lisserie
        lisampl=SamplingEvent.objects.filter(idSerie__in=lisserie)
        listemp=[]
        for sampl in lisampl:
            listemp.append(sampl.idCollection.id)
        liscoll=Collection.objects.filter(id__in=listemp)
        print 'liscoll',liscoll
        i=0
        for coll in liscoll:
            nomelinea=coll.collectionEvent
            print 'nomelinea',nomelinea
            indir=urlcell+'/api/cellLineFromName/?name='+nomelinea
            req = urllib2.Request(indir, headers={"workingGroups" : get_WG_string()})
            u = urllib2.urlopen(req)
            #u = urllib2.urlopen(indir)
            
            da = u.read()
            data=json.loads(da)
            #print 'data',data
            if len(data)!=0:
                trovato=False
                for val in data:
                    print 'val',val
                    nomemodif=val['name'].replace('-','')
                    nomemodif=nomemodif.replace(' ','')
                    if nomemodif.upper()==nomelinea.upper():
                        res=val['id']
                        trovato=True
                        break
                if not trovato:
                    res='-1'
                print 'res',res
            else:
                res='-1'
                print 'res',res
            if res=='-1':
                #devo salvare la linea nel DB delle annotazioni
                indir=urlcell+'/api/newCellLine/'
                val2={'name':nomelinea}
                data1 = urllib.urlencode(val2)
                req = urllib2.Request(indir,data=data1, headers={"workingGroups" : get_WG_string()})
                u = urllib2.urlopen(req)
                #u = urllib2.urlopen(indir, data1)
                result =  json.loads(u.read())
                res=result['id']
                print 'res salvato',res
            
            #salvo il valore dell'id nelle feature della collezione
            clinfeat,creato=CollectionClinicalFeature.objects.get_or_create(idCollection=coll,
                                               idClinicalFeature=feat,
                                               value=res)
            i=i+1
            #if i==5:
                #break
        return HttpResponse("ok")
    except Exception,e:
        print 'err',e
        transaction.rollback()
        return HttpResponse("err")
    
#serve solo una volta per modificare il vettore delle linee storiche in A
@transaction.commit_on_success
def CellChangeVector(request):
    try:
        #prendo solo le aliquote vitali
        vit=AliquotType.objects.get(abbreviation='VT')

        lisserie=Serie.objects.filter(Q(operator='carlotta.cancelliere')|Q(operator='sandra.misale')|Q(operator='mariangela.russo'))
        print 'lisserie',lisserie
        lisampl=SamplingEvent.objects.filter(idSerie__in=lisserie)
        print 'lisampl',lisampl
        listaal=Aliquot.objects.filter(Q(idAliquotType=vit)&Q(idSamplingEvent__in=lisampl))
        print 'listaal',listaal
        print 'lung',len(listaal)
        
        i=0
        for al in listaal:
            gen=GenealogyID(al.uniqueGenealogyID)
            vect=gen.getSampleVector()
            print 'vett',vect
            if vect=='S':
                gen.updateGenID({'sampleVector':'A'})
                al.uniqueGenealogyID=gen.getGenID()
                al.save()
            i=i+1
            #if i==5:
                #break
        return HttpResponse("ok")
    except Exception,e:
        print 'err',e
        transaction.rollback()
        return HttpResponse("err")
    
#serve solo una volta per modificare il lineage delle linee storiche in A
@transaction.commit_on_success
def CellChangeLineage(request):
    try:
        #prendo solo le aliquote vitali
        vit=AliquotType.objects.get(abbreviation='VT')

        lisserie=Serie.objects.filter(Q(operator='carlotta.cancelliere')|Q(operator='sandra.misale')|Q(operator='mariangela.russo'))
        print 'lisserie',lisserie
        lisampl=SamplingEvent.objects.filter(idSerie__in=lisserie)
        print 'lisampl',lisampl
        listaal=Aliquot.objects.filter(Q(idAliquotType=vit)&Q(idSamplingEvent__in=lisampl))
        print 'listaal',listaal
        print 'lung',len(listaal)
        
        i=0
        for al in listaal:
            gen=GenealogyID(al.uniqueGenealogyID)
            lin=gen.getLineage()
            print 'lin',lin
            if lin!='0A':
                gen.updateGenID({'lineage':'0A'})
                al.uniqueGenealogyID=gen.getGenID()
                al.save()
            i=i+1
            #if i==16:
                #break
        return HttpResponse("ok")
    except Exception,e:
        print 'err',e
        transaction.rollback()
        return HttpResponse("err")
    
#serve solo una volta per correggere le derivazioni storiche e togliere i sampling event multipli
@transaction.commit_on_success
def CheckDerivation(request):
    try:
        lisder=DerivationEvent.objects.raw("select * from derivationevent group by idSamplingEvent having count(*)>1 ")
        print 'lisde',lisder
        listemp=[]
        for l in lisder:
            if l.idSamplingEvent!=None:
                listemp.append(l.idSamplingEvent)
        tipo_dna=AliquotType.objects.get(abbreviation='DNA')
        tipo_rna=AliquotType.objects.get(abbreviation='RNA')
        tipo_cdna=AliquotType.objects.get(abbreviation='cDNA')
        tipo_crna=AliquotType.objects.get(abbreviation='cRNA')
        for i in range(0,len(listemp)):
            samp=listemp[i]
            lisder=DerivationEvent.objects.filter(idSamplingEvent=samp)
            print 'lisder',lisder
            for der in lisder:
                lisfiglie=[]
                #prendo la madre dall'aliqdersched
                genmadre=der.idAliqDerivationSchedule.idAliquot.uniqueGenealogyID
                print 'genmadre',genmadre
                ge=GenealogyID(genmadre)
                genfinmadre=ge.getCase()+ge.getTissue()+ge.getGeneration()+ge.getMouse()+ge.getTissueType()
                print 'genfinmadre',genfinmadre
                lisaliq=Aliquot.objects.filter(Q(idSamplingEvent=der.idSamplingEvent)&(Q(idAliquotType=tipo_dna)|Q(idAliquotType=tipo_rna)|Q(idAliquotType=tipo_cdna)|Q(idAliquotType=tipo_crna)))
                for al in lisaliq:
                    gef=GenealogyID(al.uniqueGenealogyID)
                    genfinfiglia=gef.getCase()+gef.getTissue()+gef.getGeneration()+gef.getMouse()+gef.getTissueType()
                    print 'genfiglia',genfinfiglia
                    if genfinmadre==genfinfiglia:
                        lisfiglie.append(al)
                print 'lisfiglie',lisfiglie
                if len(lisfiglie)!=0:
                    #salvo il nuovo sampling event
                    samplev=SamplingEvent(idTissueType=der.idSamplingEvent.idTissueType,
                                          idCollection=der.idSamplingEvent.idCollection,
                                          idSource=der.idSamplingEvent.idSource,
                                          idSerie=der.idSamplingEvent.idSerie,
                                          samplingDate=der.idSamplingEvent.samplingDate)
                    print 'samplev',samplev
                    samplev.save()
                    for al in lisfiglie:
                        al.idSamplingEvent=samplev
                        al.save()
                    der.idSamplingEvent=samplev
                    der.save()
        return HttpResponse("ok")
    except Exception,e:
        print 'err',e
        transaction.rollback()
        return HttpResponse("err")

#per cambiare i gen che hanno TUMPL in BLDPL
def CambiaTumInBiobanca(request):
    enable_graph()
    disable_graph()
    lisaliq=Aliquot.objects.filter(uniqueGenealogyID__contains='TUMPL')
    try:
        for al in lisaliq:
            g=GenealogyID(al.uniqueGenealogyID)
            if g.getTissueType()=='TUM':
                try:
                    g.updateGenID({'tissueType':'BLD'})
                    al.uniqueGenealogyID=g.getGenID()
                    disable_graph()
                    al.save()
                except:
                    pass
    except:
        pass
    
#per cambiare i gen che hanno TUMPL in BLDPL
def CambiaTumInStorage(request):
    lisaliq=Aliquot.objects.filter(genealogyID__contains='TUMPL')
    for al in lisaliq:
        gen=al.genealogyID
        print gen
        tess=gen[17:20]
        print tess
        if tess=='TUM':
            try:
                nuovogen=gen[0:17]+'BLD'+gen[20:]
                print nuovogen
                al.genealogyID=nuovogen
                al.save()
            except:
                pass
            
#per cambiare i gen che hanno TUMPL in BLDPL
def CambiaTumInXeno(request):
    lisid=[]
    #prendo le aliquote da cambiare nello xeno
    lisaliq=Aliquot.objects.filter(id_genealogy__contains='TUMPL')
    for al in lisaliq:
        g=GenealogyID(al.id_genealogy)
        if g.getTissueType()=='TUM':
            g.updateGenID({'tissueType':'BLD'})
            al.id_genealogy=g.getGenID()
            print al
            lisid.append(al.id)
            disable_graph()
            al.save()
    enable_graph()
    lisal=Aliquot.objects.filter(id__in=lisid)
    for al in lisal:
        #con questo inserisco direttamente il nodo nel grafo
        add_aliquot_node(al)
    
    
    
