from __init__ import *
from catissue.api.handlers import LocalIDListHandler

@laslogin_required
@login_required
@permission_decorator('tissue.can_view_BBM_mercuric')
def collectionMerc(request):
    try:
        if request.method=='POST':
            print request.POST
            form = CollectionMercForm(request.POST)
        else:
            form = CollectionMercForm()
        variables = RequestContext(request, {'form': form})   
        return render_to_response('collection.html',variables)
    except Exception,e:
        print 'errore',e
        variables = RequestContext(request, {'errore':True})
        return render_to_response('index.html',variables)


@laslogin_required
@login_required
@permission_decorator('tissue.can_view_BBM_mercuric')
@transaction.commit_manually
def collectionSaveMerc(request):
    if request.method=='POST':
        print request.POST
        print 'Mercuric'
        try:
            if 'final' in request.POST:   
                listaaliq=request.session.get('aliquotCollectionMercuric')
                print 'listaaliq',listaaliq
                lista,intest=LastPartCollectionMercuric(listaaliq)
                variables = RequestContext(request,{'fine2':True,'aliq':lista,'intest':intest})
                return render_to_response('collection.html',variables)
            if 'salva' in request.POST:
                set_initWG(set(['Mercuric_WG']))
                listaal=[]
                lisbarclashub=[]
                pezziusati=0
                disponibile=1
                derivato=0
                liscasi=[]
                listacoll=[]
                lisexists=[]
                lisnotexists=[]
                lislocalid=[]
                
                tum=CollectionType.objects.get(abbreviation='CRC')
                tess=TissueType.objects.get(abbreviation='BL')
                protcoll=CollectionProtocol.objects.get(name='Mercuric')
                tipoaliq=AliquotType.objects.get(abbreviation='PL')
                casuale=True
                
                #mi faccio dare la lista dei localid per mercuric per sapere quali ci sono gia'
                hand=LocalIDListHandler()
                diztemp=hand.read(request,str(protcoll.id))
                lislocalmerc=diztemp[protcoll.id]
                print 'lislocalmerc',lislocalmerc
                
                listaaliq=json.loads(request.POST.get('dati'))
                lcasi=json.loads(request.POST.get('liscasi'))
                print 'lcasi',lcasi
                
                lisconsensi=[]
                for key in lcasi:
                    valch=key.split('|')
                    paz=valch[0]
                    lisconsensi.append(paz+'_'+protcoll.project)
                diztotconsensi=checkListInformedConsent(lisconsensi)
                print 'diztotcons',diztotconsensi
                operatore=request.POST.get('operatore')
                
                for key in lcasi:                  
                    #chiave e' formata da paziente|data|idsorgente
                    #val e' una lista di dizionari
                    print 'key',key
                    val=listaaliq[key]
                    print 'val',val
                    #per ogni chiave creo una collezione
                    valor=LasHubNewCase(request, casuale, tum.abbreviation)
                    print 'r.text',valor
                    caso=NewCase(valor, casuale, tum)
                    
                    #se il lashub non e' attivo
                    if valor=='not active' and len(liscasi)!=0:
                        #se voglio un valore casuale allora devo andare a vedere se c'e' gia' quel valore nel dizionario
                        if casuale:
                            trovato=False
                            while not trovato:
                                pres=False
                                if caso in liscasi:
                                    #vuol dire che devo ricreare un nuovo caso
                                    caso=NewCase(valor, casuale, tum)
                                    print 'caso nuovo',caso
                                    pres=True
                                #termino il ciclo while perche' non ho trovato doppioni per il codice del caso
                                print 'pres',pres
                                if not pres:
                                    trovato=True
                    #non devo fare lo zfill, il caso arriva gia' su 4 lettere
                    liscasi.append(caso)
                    
                    valch=key.split('|')
                    paz=valch[0]
                    data_coll=valch[1]
                    posto=Source.objects.get(id=valch[2])
                    
                    #val[3] e' il consenso informato
                    cons=paz
                    
                    '''handler=CheckPatientHandler()
                    valore=handler.read(request, cons, paz, posto.id)
                    print 'val',valore
                    ris=valore['event']
                    print 'risss',ris
                    if ris=='duplic':
                        raise Exception'''                                                                
                    
                    collez=Collection(itemCode=caso,
                                 idSource=posto,
                                 idCollectionType=tum,
                                 collectionEvent=cons,
                                 patientCode=paz,
                                 idCollectionProtocol=protcoll)
                    print 'collez',collez
                    collez.save()
                    
                    valore=diztotconsensi[paz+'_'+protcoll.project]
                    print 'val',valore
                    if valore==None:
                        #vuol dire che l'ic non esiste ancora
                        diztemp={'caso':collez.itemCode,'tum':collez.idCollectionType.abbreviation,'consenso':collez.collectionEvent,'progetto':collez.idCollectionProtocol.project,'source':collez.idSource.internalName,'wg':['Mercuric_WG'],'operator':operatore}
                        if paz in lislocalmerc:
                            #il paziente esiste gia'
                            diztemp['paziente']=collez.patientCode
                        else:
                            #il paziente inserito non esiste ancora
                            if collez.patientCode=='':
                                #il paziente non e' stato inserito dall'utente, quindi non viene creato niente
                                diztemp['paziente']=''
                            else:
                                #il paziente e' stato inserito
                                diztemp['newLocalId']=collez.patientCode
                        lisnotexists.append(diztemp)
                    else:
                        lisexists.append({'caso':collez.itemCode,'tum':collez.idCollectionType.abbreviation,'consenso':collez.collectionEvent,'progetto':collez.idCollectionProtocol.project,'wg':['Mercuric_WG']})
                        localid=valore['patientUuid']
                        lislocalid.append(localid)
                    
                    #per il LASHub
                    iniziogen=collez.idCollectionType.abbreviation+collez.itemCode
                    if iniziogen not in listacoll:
                        listacoll.append(iniziogen)
                                        
                    #salvo la serie
                    ser,creato=Serie.objects.get_or_create(operator=operatore,
                                                           serieDate=data_coll)
                    
                    #salvo il campionamento
                    campionamento=SamplingEvent(idTissueType=tess,
                                                 idCollection=collez,
                                                 idSource=posto,
                                                 idSerie=ser,
                                                 samplingDate=data_coll)
                    campionamento.save()
                    print 'camp',campionamento
                    #per dare il contatore al genid dei campioni
                    contatore=1
                    for diz in val:                        
                        barcode=diz['barcode']
                        genid=tum.abbreviation+caso+tess.abbreviation+'H0000000000'+tipoaliq.abbreviation+str(contatore).zfill(2)+'00'
                        contatore+=1
                        print 'genid',genid
                        print 'len gen',len(genid)
                                            
                        a=Aliquot(barcodeID=barcode,
                                  uniqueGenealogyID=str(genid),
                                  idSamplingEvent=campionamento,
                                  idAliquotType=tipoaliq,
                                  timesUsed=pezziusati,
                                  availability=disponibile,
                                  derived=derivato
                                  )
                        print 'a',a

                        a.save()
                        
                        lisbarclashub.append(barcode)
                        
                        volu=float(diz['vol'])
                        #converto da ml a ul
                        vol=volu*1000
                        featvol=Feature.objects.get(idAliquotType=tipoaliq,name='Volume')
                        aliqfeaturevol=AliquotFeature(idAliquot=a,
                                               idFeature=featvol,
                                               value=vol)
                        aliqfeaturevol.save()
                        
                        valori=genid+',,,0,'+barcode+','+tipoaliq.abbreviation+',true,'+str(volu)+','+str(posto)+','+str(data_coll)+','+str(paz)+','
                        listaal.append(valori)
                        print 'listaaliq',listaal
                        
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
                        raise ErrorDerived('Error: barcode '+res+' already exists')
                
                request,errore=SalvaInStorageMercuric(listaal,request)
                print 'err', errore   
                if errore==True:
                    transaction.rollback()
                    variables = RequestContext(request, {'errore':errore})
                    return render_to_response('index.html',variables)                                            
                
                #comunico al LASHub che quella collezione e' stata salvata e quei barcode sono stati utilizzati
                prefisso= 'https://' if settings.LAS_AUTH_USE_HTTPS else 'http://'
                address=request.get_host()+settings.HOST_URL
                indir=prefisso+address
                url = indir + '/clientHUB/saveAndFinalize/'
                print 'url',url
                values = {'typeO' : 'aliquot', 'listO': str(listacoll)}
                requests.post(url, data=values, verify=False, headers={"workingGroups" : get_WG_string()})
                values2 = {'typeO' : 'container', 'listO': str(lisbarclashub)}
                requests.post(url, data=values2, verify=False, headers={"workingGroups" : get_WG_string()})
                
                #devo fare gia' il commit perche' devo passare al modulo clinico la collezione, che deve gia' esistere sul grafo
                #altrimenti non si riesce a collegare il nodo collezione con il consenso informato
                transaction.commit()
                #faccio la API al modulo clinico per dirgli di salvare
                errore=saveInClinicalModule(lisexists,lisnotexists,['Mercuric_WG'],operatore,lislocalid)
                if errore:
                    raise Exception
                
                request.session['aliquotCollectionMercuric']=listaal
                transaction.commit()
                return HttpResponse()
        except ErrorDerived as e:
            transaction.rollback()
            print 'My exception occurred, value:', e.value
            variables = RequestContext(request, {'errore':e.value})
            return render_to_response('collection.html',variables)
        except Exception,e:
            print 'err',e
            transaction.rollback()
            errore=True
            variables = RequestContext(request, {'errore':errore})
            return render_to_response('index.html',variables)



def SalvaInStorageMercuric(listaaliquota,request):
    listaffpe=''
    listaaliq=''
    listatipialiq=[]
    errore=False
    for i in range(0,len(listaaliquota)):
        val=listaaliquota[i].split(',')
        if val[6]=='false':
            #in val[4] c'e' il barcode della provetta
            listaaliq.append(val[4]+','+val[0]+','+val[9])
            listatipialiq.append(val[5])
        else:
            #in val[5] c'e' il tipo dell'aliq (VT,SF...)
            listaffpe=listaffpe+val[4]+','+val[5]+','+val[0]+','+val[9]+'&'
    print 'listaaliq',listaaliq
    print 'listaffpeeeee',listaffpe
    #per salvare in rna,snap o vitale
    url1 = Urls.objects.get(default = '1').url + "/full/"
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
        return render_to_response('tissue2/index.html',variables)
        print e
    if (res1 == 'err')or(len(listaffpe)!=0 and res2=='err'):
        print 'errore'
        #transaction.rollback()
        errore=True
        return request,errore
    return request,errore


def LastPartCollectionMercuric(listaaliq):
    lista=[]
    for i in range(0,len(listaaliq)):
        info=listaaliq[i].split(',')
        lista.append(ReportToHtml([i+1,info[8],info[9],info[10],info[4],info[7]]))
    intest='<th>N</th><th>Place</th><th>Date</th><th>Patient code</th><th>Barcode</th><th>Volume(ml)</th>'
    
    print 'lista',lista
    print 'intest',intest
    return lista,intest
