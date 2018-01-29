from __init__ import *
from catissue.api.handlers import LocalIDListHandler

@laslogin_required
@login_required
@permission_decorator('tissue.can_view_BBM_funnel')
def collectionFunnel(request):
    try:
        if request.method=='POST':
            print request.POST
            form = CollectionFunnelForm(request.POST)
        else:
            form = CollectionFunnelForm()
        variables = RequestContext(request, {'form': form})
        return render_to_response('collectionFunnel.html',variables)
    except Exception,e:
        print 'errore',e
        variables = RequestContext(request, {'errore':True})
        return render_to_response('indexFunnel.html',variables)


@laslogin_required
@login_required
@permission_decorator('tissue.can_view_BBM_funnel')
@transaction.commit_manually
def collectionSaveFunnel(request):
    if request.method=='POST':
        print request.POST
        print 'Funnel'
        try:
            if 'final' in request.POST:   
                listaaliq=request.session.get('aliquotCollectionFunnel')
                print 'listaaliq',listaaliq
                lista,intest=LastPartCollectionFunnel(listaaliq)
                variables = RequestContext(request,{'fine2':True,'aliq':lista,'intest':intest})
                return render_to_response('collectionFunnel.html',variables)
            if 'salva' in request.POST:
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
                protcoll=CollectionProtocol.objects.get(project='Funnel')
                tipoaliqpl=AliquotType.objects.get(abbreviation='PL')
                tipoaliqpbmc=AliquotType.objects.get(abbreviation='VT')
                casuale=True
                
                #mi faccio dare la lista dei localid per funnel per sapere quali ci sono gia'
                hand=LocalIDListHandler()
                diztemp=hand.read(request,str(protcoll.id))
                lislocalfunnel=diztemp[protcoll.id]
                print 'lislocalfunnel',lislocalfunnel
                
                listaaliq=json.loads(request.POST.get('dati'))
                lcasi=json.loads(request.POST.get('liscasi'))
                print 'lcasi',lcasi
                
                operatore=request.POST.get('operatore')
                #prendo il wg dell'operatore per impostarlo nella collezione
                oper=User.objects.get(username=operatore)
                liswg=WG_User.objects.filter(user=oper)
                
                #se il protocollo e' della Marsoni allora devo mettere in share anche lei per le aliquote
                liscollinvestig=CollectionProtocolInvestigator.objects.filter(idCollectionProtocol=protcoll)
                trovato=False
                if len(liscollinvestig)!=0:
                    for coll in liscollinvestig:
                        if coll.idPrincipalInvestigator.surname=='Marsoni' and coll.idPrincipalInvestigator.name=='Silvia':
                            trovato=True
                            break
                #un utente in Funnel appartiene ad un solo WG
                listawg=[liswg[0].WG.name]
                if trovato:
                    listawg.append('Marsoni_WG')
                print 'listawg',listawg
                set_initWG(listawg)

                workingGroup=listawg
                
                lisconsensi=[]
                for key in lcasi:
                    valch=key.split('|')
                    paz=valch[0]
                    lisconsensi.append(paz+'_'+protcoll.project)
                diztotconsensi=checkListInformedConsent(lisconsensi)
                print 'diztotcons',diztotconsensi
                
                for key in lcasi:
                    #chiave e' formata da paziente|data|idsorgente
                    #val e' una lista di dizionari
                    print 'key',key
                    val=listaaliq[key]
                    print 'val',val
                    #per ogni chiave creo una collezione
                    #creo il caso casuale
                    caso=NewCase('not active', casuale, tum)
                    #se il lashub non e' attivo
                    if len(liscasi)!=0:
                        trovato=False
                        while not trovato:
                            pres=False
                            if caso in liscasi:
                                #vuol dire che devo ricreare un nuovo caso
                                caso=NewCase('not active', casuale, tum)
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
                    
                    '''listacollez=Collection.objects.filter(idSource=posto,patientCode=paz).order_by('id')
                    print 'lista',listacollez
                    if len(listacollez)!=0:
                        #c'e' una collezione: devo proporre un coll event
                        #prendo il coll event dell'ultima collezione
                        eve=listacollez[len(listacollez)-1].collectionEvent
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
                            valev=evespl[len(evespl)-1]
                            print 'valev',valev
                            if valev.isdigit():
                                for i in range(0,len(evespl)-1):
                                    print 'evespl[i]',evespl[i]
                                    evefin+=evespl[i]+'_'
                                #incremento il valore di 1
                                evefin+=str(int(valev)+1)
                            else:
                                if eve[len(eve)-1]!='_':
                                    evefin=eve+'_1'
                                else:
                                    evefin=eve+'1'
                    else:
                        evefin=paz'''                                                           
                    evefin=paz
                    collez=Collection(itemCode=caso,
                                 idSource=posto,
                                 idCollectionType=tum,
                                 collectionEvent=evefin,
                                 patientCode=paz,
                                 idCollectionProtocol=protcoll)
                    print 'collez',collez                    
                    collez.save()
                                        
                    valore=diztotconsensi[paz+'_'+protcoll.project]
                    print 'val',valore
                    if valore==None:
                        #vuol dire che l'ic non esiste ancora
                        diztemp={'caso':collez.itemCode,'tum':collez.idCollectionType.abbreviation,'consenso':collez.collectionEvent,'progetto':collez.idCollectionProtocol.project,'source':collez.idSource.internalName,'wg':workingGroup,'operator':operatore}
                        if paz in lislocalfunnel:
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
                        lisexists.append({'caso':collez.itemCode,'tum':collez.idCollectionType.abbreviation,'consenso':collez.collectionEvent,'progetto':collez.idCollectionProtocol.project,'wg':workingGroup})
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
                    contatoreplasma=1
                    contatorepbmc=1
                    for diz in val:                        
                        barcode=diz['barcode']
                        tipo=diz['tipo']
                        #se e' PBMC
                        if tipo=='1':
                            tipoaliq=tipoaliqpbmc
                            contatore=contatorepbmc
                            contatorepbmc+=1
                        #se e' plasma
                        elif tipo=='0':
                            tipoaliq=tipoaliqpl
                            contatore=contatoreplasma
                            contatoreplasma+=1
                        #devo guardare il contatore
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
                        conta=''                        
                        #se e' PBMC
                        if tipo=='1':
                            conta=float(diz['conta'])
                            featconta=Feature.objects.get(Q(idAliquotType=tipoaliq)&Q(name='Count'))
                            aliqfeatureconta=AliquotFeature(idAliquot=a,
                                                       idFeature=featconta,
                                                       value=conta)
                            aliqfeatureconta.save()
                            print 'aliq',aliqfeatureconta
                            
                        valori=genid+',,,0,'+barcode+','+tipoaliq.abbreviation+',true,'+str(volu)+','+str(conta)+','+str(posto)+','+str(data_coll)+','+str(paz)+','
                        listaal.append(valori)
                        print 'listaaliq',listaal
                        
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
                
                request,errore=SalvaInStorageFunnel(listaal,request)
                print 'err', errore   
                if errore==True:
                    transaction.rollback()
                    variables = RequestContext(request, {'errore':errore})
                    return render_to_response('indexFunnel.html',variables)
                
                #devo fare gia' il commit perche' devo passare al modulo clinico la collezione, che deve gia' esistere sul grafo
                #altrimenti non si riesce a collegare il nodo collezione con il consenso informato
                transaction.commit()
                #faccio la API al modulo clinico per dirgli di salvare
                errore=saveInClinicalModule(lisexists,lisnotexists,workingGroup,operatore,lislocalid)
                if errore:
                    raise Exception
                
                request.session['aliquotCollectionFunnel']=listaal
                transaction.commit()
                return HttpResponse()
        except ErrorDerived as e:
            transaction.rollback()
            print 'My exception occurred, value:', e.value
            variables = RequestContext(request, {'errore':e.value})
            return render_to_response('collectionFunnel.html',variables)
        except Exception,e:
            print 'err',e
            transaction.rollback()
            errore=True
            variables = RequestContext(request, {'errore':errore})
            return render_to_response('indexFunnel.html',variables)


def SalvaInStorageFunnel(listaaliquota,request):
    listaffpe=''
    listaaliq=''
    listatipialiq=[]
    errore=False
    for i in range(0,len(listaaliquota)):
        val=listaaliquota[i].split(',')
        if val[6]=='false':
            #in val[4] c'e' il barcode della provetta, in val[10] la data
            listaaliq.append(val[4]+','+val[0]+','+val[10])
            listatipialiq.append(val[5])
        else:
            #in val[5] c'e' il tipo dell'aliq (VT,SF...)
            listaffpe=listaffpe+val[4]+','+val[5]+','+val[0]+','+val[10]+'&'
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
        return render_to_response('tissue2/indexFunnel.html',variables)
        print e
    if (res1 == 'err')or(len(listaffpe)!=0 and res2=='err'):
        print 'errore'
        #transaction.rollback()
        errore=True
        return request,errore
    return request,errore


def LastPartCollectionFunnel(listaaliq):
    lista=[]
    for i in range(0,len(listaaliq)):
        info=listaaliq[i].split(',')
        lista.append(ReportToHtml([i+1,info[9],info[10],info[11],info[4],info[7],info[8]]))
    intest='<th>N</th><th>Place</th><th>Date</th><th>Patient code</th><th>Barcode</th><th>Volume (ml)</th><th>Count (cell/ml)</th>'
    
    print 'lista',lista
    print 'intest',intest
    return lista,intest
