from __init__ import *
from catissue.tissue.split import *
from catissue.api.handlers import StorageTubeHandler

#per caricare il primo passo, quello con la convalida dei campioni
@laslogin_required
@login_required
@permission_decorator('tissue.can_view_BBM_plan_aliquots_to_split')
def LoadValidateAliquot(request):
    request.session['robotsplitload']=True
    return ExecSplitAliquots(request)

#per salvare nel DB di hamilton i valori dei campioni da creare
@transaction.commit_manually
@transaction.commit_manually(using='dbhamilton')
@laslogin_required
@login_required
@permission_decorator('tissue.can_view_BBM_plan_aliquots_to_split')
def PlanDilution(request):
    try:
        if request.method=='POST':
            print request.POST        
            #con javascript faccio una post che mi fa scattare questo if. Salvo i dati nella sessione
            #per poi riprenderli dopo quando clicco su submit
            if 'salva' in request.POST:                
                dizaliq=json.loads(request.POST.get('dizaliq'))
                dizremain=json.loads(request.POST.get('dizremain'))
                request.session['dizaliqsplitrobot']=dizaliq
                request.session['dizremainsplitrobot']=dizremain
                print 'dizaliq',dizaliq
                print 'dizremain',dizremain
                transaction.commit()
                transaction.commit(using='dbhamilton')
                return HttpResponse()
            #entra qui se l'utente ha cliccato su confirm all
            if 'finish' in request.POST:
                name=request.user.username
                print 'name',name
                aliq_da_svuotare=[]
                if request.session.has_key('dizaliqsplitrobot'):
                    #chiave l'idalsched e valore una lista con i vari campioni da creare
                    dizaliq=request.session.get('dizaliqsplitrobot')
                    del request.session['dizaliqsplitrobot']
                if request.session.has_key('dizremainsplitrobot'):
                    dizremain=request.session.get('dizremainsplitrobot')
                    del request.session['dizremainsplitrobot']
                if request.session.has_key('aliqSplitPlanDilutionRobot'):
                    lisfin=request.session.get('aliqSplitPlanDilutionRobot')
                    del request.session['aliqSplitPlanDilutionRobot']
                nameexperiment=request.POST.get('exp_name')
                                
                tipoprot=ProtocolTypeHamilton.objects.get(name='dilution')
                lisprot=ProtocolHamilton.objects.filter(protocol_type_id=tipoprot)
                #prendo il primo della lista tanto non dovrebbe mai esserci piu' di un protocollo di diluizione
                protdilution=lisprot[0]
                
                #vedo se ci sono delle procedure non fallite
                fallita=True
                for v in dizremain.values():
                    check=v['checkstop']
                    if check=='false':
                        fallita=False
                        break
                if not fallita:
                    idconttipo=request.POST.get('container')
                    print 'idconttipo',idconttipo
                    conttipo=LabwareTypeHamilton.objects.get(id=idconttipo)
                    plan=PlanHamilton(name=nameexperiment,
                                  timestamp=timezone.localtime(timezone.now()),
                                  operator=name,
                                  labwareid=conttipo)
                    plan.save()
                    p_hasprotocol=PlanHasProtocolHamilton(plan_id=plan,
                                                          protocol_id=protdilution)
                    p_hasprotocol.save()
                    
                    if conttipo.description!='matrix':
                        #per il rank devo vedere se nel carrello del robot ho gia' qualcosa in coda, che proviene magari da un'estrazione che ho fatto prima di cui
                        #pero' ho fatto solo la quantificazione e non ancora la diluizione. Quindi ho delle posizioni gia' piene nel carrello e non posso partire da 1
                        #per il rank, ma devo sommare uno spiazzamento.
                        #Non filtro sull'operatore perche' ho bisogno di avere tutti gli aliqdersched in coda, anche quelli di altri utenti
                        lisplan=list(PlanHamilton.objects.filter(processed__isnull=True).values_list('id',flat=True))
                        print 'lisplan',lisplan
                        maxrank=0
                        lisrank=list(SampleHamilton.objects.filter(plan_id__in=lisplan).values_list('rank',flat=True))
                        if len(lisrank)!=0:
                            maxrank=max(lisrank)
                        print 'maxrank',maxrank
                        lisaliqder=AliquotDerivationSchedule.objects.filter(Q(idPlanRobot__in=lisplan)|Q(Q(idPlanDilution__in=lisplan)&Q(derivationExecuted=1)))
                        print 'lisaliqder',lisaliqder
                        delta=len(lisaliqder)
                        if maxrank>delta:
                            delta=maxrank
                        #e' None se tutti gli altri piani ancora da eseguire sono dei matrix e non hanno quindi un rank
                        if maxrank==None:
                            delta=0
                        print 'delta',delta
                    
                lista_report=[]
                
                for i in range(0,len(lisfin)):
                    #e' l'aliqsplitschedule
                    alsplit=lisfin[i]
                    barcode=dizremain[str(alsplit.id)]['barcode']
                    print 'barcode',barcode
                    pos=dizremain[str(alsplit.id)]['position']
                    lista_report.append(ReportToHtml([alsplit.idAliquot.uniqueGenealogyID,barcode,pos]))

                    alsplit.splitExecuted=1                        
                    if alsplit.operator=='':
                        alsplit.operator=request.user
                    exh=dizremain[str(alsplit.id)]['exhausted']
                    if exh=='true':
                        alsplit.aliquotExhausted=1
                    #controllo se l'utente ha bloccato qui la procedura impostando il check
                    checkstop=dizremain[str(alsplit.id)]['checkstop']
                    if checkstop=='false':
                        if conttipo.description!='matrix':
                            rank=i+1+delta
                        else:
                            rank=None
                        #devo prendere il volume del campione, se c'e'
                        aliq=alsplit.idAliquot
                        vol=-1
                        lfeatvol=Feature.objects.filter(name='Volume',idAliquotType=aliq.idAliquotType)
                        if len(lfeatvol)!=0:
                            lfeat=AliquotFeature.objects.filter(idFeature=lfeatvol[0],idAliquot=aliq)
                            if len(lfeat)!=0:
                                vol=lfeat[0].value
                        print 'vol',vol
                        samp=SampleHamilton(genid=alsplit.idAliquot.uniqueGenealogyID,
                                        barcode=barcode,
                                        volume=vol,
                                        rank=rank,
                                        plan_id=plan)
                        samp.save()
                        #puo' capitare che se non e' stata calcolata la conc della madre, non posso creare le figlie, quindi nel dizaliq non avro'
                        #l'id dell'aldersched e semplicemente non creo niente, ma metto solo come concluso l'aliqdersched
                        if str(alsplit.id) in dizaliq:
                            lischild=dizaliq[str(alsplit.id)]
                            print 'lischild',lischild
                            for j in range(0,len(lischild)):
                                #ch e' un dizionario con i valori della singola aliquota da creare
                                ch=lischild[str(j)]
                                vol=float(ch['volume'])
                                print 'vol',vol
                                
                                #solo se il volume e' diverso da zero creo il campione
                                if vol!=0:
                                    #devo vedere se e' da creare il remain
                                    create=dizremain[str(alsplit.id)]['create']
                                    verify=1
                                    if j!=len(lischild)-1 or create:
                                        #se sono all'ultimo campione, cioe' il rimanente, metto verify a zero perche' cosi' non costringo il robot
                                        #a controllare il volume e quindi prende tutto cio' che e' rimasto nella madre indiscriminatamente 
                                        if j==len(lischild)-1:
                                            verify=0
                                        aliqfiglia=ChildHamilton(taskid=int(ch['task']),
                                                                 volume=float(ch['madre']),
                                                                 vol_kit=float(ch['acqua']),
                                                                 concentration=float(ch['concentration']),
                                                                 verify_remain=verify,
                                                                 sample_id=samp)
                                        print 'aliqfiglia',aliqfiglia
                                        aliqfiglia.save()
                    else:                        
                        if exh=='true':
                            aliq_da_svuotare.append(alsplit.idAliquot)
                            print 'aliq_svuotare',aliq_da_svuotare                                                
                        #Non devo diminuire il volume della madre perche' lo split non e' stato eseguito: l'utente ha bloccato
                        #la procedura prima dell'esecuzione 
                        
                    if not fallita:
                        alsplit.idPlanRobot=plan.id
                    alsplit.save()
                gen_da_svuotare=[]
                print 'al da svuotare',aliq_da_svuotare
                for i in range(0,len(aliq_da_svuotare)):
                    #rendo indisponibili le aliquote esauste
                    aliq_da_svuotare[i].availability=0
                    gen_da_svuotare.append(aliq_da_svuotare[i].uniqueGenealogyID)
                    aliq_da_svuotare[i].save()
                    
                print 'listastor',gen_da_svuotare
                if len(gen_da_svuotare)!=0:
                    #mi collego allo storage per svuotare le provette contenenti le aliq
                    #esaurite
                    address=Urls.objects.get(default=1).url
                    url = address+"/full/"
                    print url
                    values = {'lista' : json.dumps(gen_da_svuotare), 'tube': 'empty','canc':True,'operator':name}
                    data = urllib.urlencode(values)
                    req = urllib2.Request(url,data=data, headers={"workingGroups" : get_WG_string()})
                    urllib2.urlopen(req)
                transaction.commit()
                transaction.commit(using='dbhamilton')
                if fallita:
                    #vuol dire che devo terminare qui la procedura
                    variables = RequestContext(request,{'vuota':True,'lista_der':lista_report})
                    return render_to_response('tissue2/split_robot/set_procedure.html',variables)
                else:
                    variables = RequestContext(request,{'fine':True,'lista_der':lista_report})
                    return render_to_response('tissue2/split_robot/set_procedure.html',variables)
    except Exception,e:
        print 'err dilution robot:',e
        transaction.rollback()
        transaction.rollback(using='dbhamilton')
        variables = RequestContext(request, {'errore':True})
        return render_to_response('tissue2/index.html',variables)

#per caricare la schermata che contiene i campioni da creare e poi per salvarli effettivamente nel LAS
@transaction.commit_manually
@transaction.commit_manually(using='dbhamilton')
@laslogin_required
@login_required
@permission_decorator('tissue.can_view_BBM_plan_aliquots_to_split')
def SaveData(request):
    try:
        if request.method=='POST':
            print request.POST
            if request.session.has_key('lissplitscheddilutionrobot'):                
                lisaliqsched=request.session.get('lissplitscheddilutionrobot')
                del request.session['lissplitscheddilutionrobot']
            if request.session.has_key('lisplansplitdilutionrobot'):                
                lisplan=request.session.get('lisplansplitdilutionrobot')
                del request.session['lisplansplitdilutionrobot']
            name=request.user.username
            lisplanfin=[]            
            for p in lisplan:
                lisplanfin.append(p.id)
            #ho tutti gli id dei piani e prendo i sample
            lissample=SampleHamilton.objects.filter(plan_id__in=lisplanfin)
            print 'lissample',lissample
            print 'lisdersched',lisaliqsched
            alsched=None
            lista_al_split=[]
            listaaliqstorage=[]
            listatipialiq=[]
            #chiave il gen del derivato nuovo e valore un diz con vol e conc e barc
            dizvalaliqder={}
            lisaliqesaurite=[]
            for samp in lissample:
                gen=samp.genid
                contatore=0
                for alder in lisaliqsched:                    
                    if gen==alder.idAliquot.uniqueGenealogyID and samp.plan_id.id==alder.idPlanRobot:
                        alsched=alder
                        break
                print 'alsched',alsched
                lischild=ChildHamilton.objects.filter(sample_id=samp)
                print 'lischild',lischild
                #prendo la data run del primo figlio, tanto e' uguale anche per gli altri
                data_esecuz=None
                if len(lischild)!=0:
                    time_run=lischild[0].run_id.timestamp
                    data_esecuz=datetime.date(int(time_run.year),int(time_run.month),int(time_run.day))
                print 'data',data_esecuz
                aliq=alsched.idAliquot
                tipo=aliq.idAliquotType.abbreviation
                print 'tipo',tipo
                
                print 'genealogy id',gen
                ge = GenealogyID(gen)
                fine=''                                
                #mi restituisce la lunghezza della parte destinata alla seconda derivazione
                for p in range(0,ge.getLen2Derivation()):
                    fine+='0'
                    
                if tipo=='DNA' or tipo=='RNA' or tipo=='P':
                    #prendo l'inizio dell'aliquota che sto dividendo
                    #e' un derivato quindi prendo tutti i caratteri fino alla fine dei 10 zeri
                    #piu' il carattere che indica se e' RNA o DNA
                    stringa=ge.getPartForDerAliq()+ge.getArchivedMaterial()
                    print 'stringa',stringa
                    #guardo se quell'inizio di genealogy ce l'ha gia' qualche aliquota derivata
                    disable_graph()
                    lista_aliquote_derivate=Aliquot.objects.filter(uniqueGenealogyID__startswith=stringa,uniqueGenealogyID__endswith=fine,derived=1).order_by('-uniqueGenealogyID')
                    enable_graph()
                    print 'lista_aliquote',lista_aliquote_derivate
                    if lista_aliquote_derivate.count()!=0:
                        #prendo il primo oggetto che e' quello che ha il contatore piu' alto
                        maxgen=lista_aliquote_derivate[0].uniqueGenealogyID
                        nuovoge=GenealogyID(maxgen)
                        maxcont=nuovoge.getAliquotExtraction()
                        contatore=int(maxcont)
                elif tipo=='cRNA' or tipo=='cDNA':
                    #prendo tutto meno gli ultimi due caratteri che conteggiano la seconda derivazione
                    stringa=ge.getPartFor2DerivationAliq()+ge.get2Derivation()
                    #stringa=gen[0:24]
                    print 'stringa',stringa
                    #guardo se quell'inizio di genealogy ce l'ha gia' qualche aliquota derivata
                    disable_graph()
                    lista_aliquote_derivate=Aliquot.objects.filter(uniqueGenealogyID__startswith=stringa,derived=1).order_by('-uniqueGenealogyID')
                    enable_graph()
                    if lista_aliquote_derivate.count()!=0:
                        #prendo il primo oggetto che e' quello che ha il contatore piu' alto
                        maxgen=lista_aliquote_derivate[0].uniqueGenealogyID
                        nuovoge=GenealogyID(maxgen)
                        maxcont=nuovoge.get2DerivationGen()
                        contatore=int(maxcont)
                print 'contatore',contatore

                alsched.operator=request.user
                print 'alsched',alsched                                
                derived_tipo=aliq.idAliquotType                
                
                if len(lischild)!=0:
                    tumore=ge.getOrigin()
                    print 'tumore',tumore
                    caso=ge.getCaseCode()
                    print 'caso',caso
                    tipotum=CollectionType.objects.get(abbreviation=tumore)
                    #prendo la collezione da associare al sampling event
                    colle=Collection.objects.get(itemCode=caso,idCollectionType=tipotum)
                    print 'colle',colle
                    #salvo la serie
                    ser,creato=Serie.objects.get_or_create(operator=name,
                                                           serieDate=data_esecuz)
                    #prendo la sorgente dalla tabella source
                    sorg=colle.idSource
                    print 'sorg',sorg
                    t=ge.getTissue()
                    tess=TissueType.objects.get(abbreviation=t)
                    #salvo il campionamento
                    campionamento=SamplingEvent(idTissueType=tess,
                                                 idCollection=colle,
                                                 idSource=sorg,
                                                 idSerie=ser,
                                                 samplingDate=data_esecuz)
                    campionamento.save()
                    print 'camp',campionamento
                    #assegno allo split schedule il campionamento appena creato
                    alsched.idSamplingEvent=campionamento
                    
                    #prendo la feature del volume
                    featvol=Feature.objects.get(idAliquotType=derived_tipo,name='Volume')
                    #prendo la feature della concentrazione
                    featconc=None
                    lfeatconc=Feature.objects.filter(idAliquotType=derived_tipo,name='Concentration')
                    if len(lfeatconc)!=0:
                        featconc=lfeatconc[0]
                    volpresomadre=0                                                       
                    for ch in lischild:
                        #devo sommare il volume preso dalla madre con quello del diluente
                        vo=ch.volume+ch.vol_kit
                        volpresomadre+=ch.volume
                        c=ch.concentration
                        if c=='NaN' or c==0.0:
                            c=-1
                        co=float(c)                    
                        #solo se il volume e' diverso da zero creo l'aliquota derivata
                        if vo!=0.0:
                            contatore=contatore+1
                            num_ordine=str(contatore).zfill(2)                                                        
                            if tipo=='DNA' or tipo=='RNA' or tipo=='P':
                                diz_dati={'aliqExtraction1':num_ordine,'2derivation':'0','2derivationGen':'00'}  
                                ge.updateGenID(diz_dati)
                                nuovo_gen=ge.getGenID()   
                            elif tipo=='cDNA' or tipo=='cRNA':
                                diz_dati={'2derivationGen':num_ordine}  
                                ge.updateGenID(diz_dati)
                                nuovo_gen=ge.getGenID()
                            
                            barcode=ch.barcode
                            barcodeurl=barcode.replace('#','%23')   
                            #mi collego all'archivio per vedere se quel barcode esiste gia'
                            url = Urls.objects.get(default = '1').url + "/api/container/"+barcodeurl
                            try:
                                #prendo i dati dall'archivio che mi da' la posizione e il barcode delle aliq
                                req = urllib2.Request(url, headers={"workingGroups" : get_WG_string()})
                                u = urllib2.urlopen(req)
                                res =  u.read()
                                data = json.loads(res)
                            except Exception, e:
                                transaction.rollback()
                                transaction.rollback(using='dbhamilton')
                                print 'err',e
                                variables = RequestContext(request, {'errore':True})
                                return render_to_response('tissue2/index.html',variables) 
                            #se la API mi restituisce dei valori perche' gli ho dato un codice gia' esistente    
                            if 'children' in data:
                                ffpe='false'
                            else:
                                #vuol dire che sto salvando una nuova provetta
                                ffpe='true'
                            derivato=1
                            if derived_tipo.type!='Derived':
                                derivato=0
                            al_der=Aliquot(barcodeID=barcode,
                                          uniqueGenealogyID=nuovo_gen,
                                          idSamplingEvent=campionamento,
                                          idAliquotType=derived_tipo,
                                          availability=1,
                                          timesUsed=0,
                                          derived=derivato)
                            al_der.save()
                            lista_al_split.append(al_der)
                            listatipialiq.append(derived_tipo.abbreviation)
                            
                            #prendo la feature del volume originale
                            featorigvol=None
                            lfeatorigvol=Feature.objects.filter(idAliquotType=derived_tipo,name='OriginalVolume')
                            if len(lfeatorigvol)!=0:
                                featorigvol=lfeatorigvol[0]
                            #prendo la feature della concentrazione originale
                            featorigconc=None
                            lfeatorigconc=Feature.objects.filter(idAliquotType=derived_tipo,name='OriginalConcentration')
                            if len(lfeatorigconc)!=0:
                                featorigconc=lfeatorigconc[0]
                            #salvo il volume
                            aliqfeaturevol=AliquotFeature(idAliquot=al_der,
                                               idFeature=featvol,
                                               value=vo)
                            aliqfeaturevol.save()
                            
                            #salvo il volume originale
                            if featorigvol!=None:
                                aliqfeatureorigvol=AliquotFeature(idAliquot=al_der,
                                                   idFeature=featorigvol,
                                                   value=vo)
                                aliqfeatureorigvol.save()
                            #salvo la concentrazione
                            if featconc!=None:
                                aliqfeaturecon=AliquotFeature(idAliquot=al_der,
                                                   idFeature=featconc,
                                                   value=co)
                                aliqfeaturecon.save()
                                print 'aliq',aliqfeaturecon
                            if featorigconc!=None:
                                #salvo la concentrazione originale
                                aliqfeatureorigcon=AliquotFeature(idAliquot=al_der,
                                                   idFeature=featorigconc,
                                                   value=co)
                                aliqfeatureorigcon.save()
                            
                            dizvalaliqder[nuovo_gen]={'barcode':barcode,'conc':co,'vol':vo}
                            valori=nuovo_gen+',,,,'+barcode+','+derived_tipo.abbreviation+','+ffpe+',,,,,,'+str(data_esecuz)
                            listaaliqstorage.append(valori)
                    print 'volpresomadre',volpresomadre        
                    #Devo aggiornare il volume della madre
                    #prendo la feature del volume
                    lfeatvol=Feature.objects.filter(idAliquotType=derived_tipo,name='Volume')
                    if len(lfeatvol)!=0:
                        #prendo il valore del volume per l'aliquota madre
                        lvalore=AliquotFeature.objects.filter(idAliquot=aliq,idFeature=lfeatvol[0])
                        if len(lvalore)!=0:
                            volmadre=lvalore[0].value
                            print 'volmadre',volmadre
                            volfin=volmadre-float(volpresomadre)
                            print 'volfin',volfin
                            lvalore[0].value=volfin
                            lvalore[0].save()

                alsched.save()
                #se la madre e' esaurita
                if alsched.aliquotExhausted==1:
                    aliq.availability=0
                    aliq.save()
                    lisaliqesaurite.append(aliq.uniqueGenealogyID)
                                    
            print 'dizvalaliq',dizvalaliqder
            print 'lisaliqstorage',listaaliqstorage
            request,errore=SalvaInStorage(listaaliqstorage,request)
            print 'err', errore   
            if errore==True:
                transaction.rollback()
                transaction.rollback(using='dbhamilton')
                variables = RequestContext(request, {'errore':errore})
                return render_to_response('tissue2/index.html',variables)
            #prendo le posizioni dei nuovi gen derivati creati
            lis_pezzi_url=[]
            lgen=''
            dizgen={}
            for al in lista_al_split:
                gen=al.uniqueGenealogyID
                lgen+=gen+'&'
                if len(lgen)>2000:
                    lis_pezzi_url.append(lgen)
                    lgen=''
            if lgen=='':
                lis_pezzi_url.append('')
            else:
                lis_pezzi_url.append(lgen)
            for parti in lis_pezzi_url:
                if parti!='':
                    request.META['HTTP_WORKINGGROUPS']=get_WG_string()
                    storbarc=StorageTubeHandler()
                    res=storbarc.read(request, parti, 'admin')                
                    diz = json.loads(res['data'])                    
                    print 'diz',diz
                    dizgen = dict(dizgen.items() + diz.items())            
            print 'dizgen',dizgen
            lista=[]
            i=1
            for al in lista_al_split:
                gen=al.uniqueGenealogyID
                diztemp=dizvalaliqder[gen]
                if gen in dizgen:
                    lisvalori=dizgen[gen]
                    print 'lisvalori',lisvalori
                    val=lisvalori.split('|')                    
                    plate=str(val[2])
                    tubepos=str(val[1])
                lista.append(ReportToHtml([str(i),al.uniqueGenealogyID,diztemp['barcode'],plate,tubepos,str(diztemp['conc']),str(diztemp['vol'])]))
                i+=1
            
            if len(lisaliqesaurite)!=0:
                #mi collego allo storage per svuotare le provette contenenti le aliq esaurite
                address=Urls.objects.get(default=1).url
                url = address+"/full/"
                print url
                values = {'lista' : json.dumps(lisaliqesaurite), 'tube': 'empty','canc':True,'operator':name}
                data = urllib.urlencode(values)
                req = urllib2.Request(url,data=data, headers={"workingGroups" : get_WG_string()})
                urllib2.urlopen(req)                           
            
            #metto come eseguiti i piani che ho trattato
            for plan in lisplan:
                plan.processed=timezone.localtime(timezone.now())
                plan.save()
                      
            transaction.commit()
            transaction.commit(using='dbhamilton')
            variables = RequestContext(request,{'fine':True,'lista_der':lista})
            return render_to_response('tissue2/split_robot/save_data.html',variables)
        else:
            #devo prendere i campioni eseguiti, cioe' i plan eseguiti
            name=request.user.username
            lisfallite=[]            
            lisprotype=ProtocolTypeHamilton.objects.filter(name='dilution').values_list('id',flat=True)
            lisprot=ProtocolHamilton.objects.filter(protocol_type_id__in=lisprotype).values_list('id',flat=True)
            print 'lisprot',lisprot
            lisplanprot=PlanHasProtocolHamilton.objects.filter(protocol_id__in=lisprot).values_list('plan_id',flat=True)
            lisplanhamilton=PlanHamilton.objects.filter(operator=name,id__in=lisplanprot,executed__isnull=False,processed__isnull=True)
            lisplanfin=[]
            #chiave l'id e valore il nome del plan
            dizplanname={}
            for p in lisplanhamilton:
                lisplanfin.append(p.id)
                dizplanname[p.id]=p.name
            print 'lisplanfin',lisplanfin
            lisaliqsched=AliquotSplitSchedule.objects.filter(idPlanRobot__in=lisplanfin).order_by('validationTimestamp')
            print 'lissched',lisaliqsched
            lissample=SampleHamilton.objects.filter(plan_id__in=lisplanfin).values_list('genid',flat=True)
            print 'lissample',lissample
            stringat=''
            #devo trovare se c'e' qualche procedura fallita cosi' da farla vedere nella schermata, ma oscurata. Guardo quali aliqsched
            #non sono presenti nella lista dei sample del robot
            for alsched in lisaliqsched:
                gen=alsched.idAliquot.uniqueGenealogyID
                if gen not in lissample:
                    lisfallite.append(alsched.id)                                            
                stringat+=gen+'&'
                
            stringtotale=stringat[:-1]
            diz=AllAliquotsContainer(stringtotale)
            lisaliq=[]
            lisbarc=[]
            lispos=[]
            lisname=[]
            for alsched in lisaliqsched:                
                listatemp=diz[alsched.idAliquot.uniqueGenealogyID]
                for val in listatemp:
                    ch=val.split('|')
                    lisaliq.append(alsched)
                    lisbarc.append(ch[1])
                    lispos.append(ch[2])
                    lisname.append(dizplanname[alsched.idPlanRobot])
                #se per caso il campione e' esaurito allora listatemp e' vuota, ma io devo comunque inserire qualcosa nelle liste
                if len(listatemp)==0:
                    lisaliq.append(alsched)
                    lisbarc.append('')
                    lispos.append('')
                    lisname.append(dizplanname[alsched.idPlanRobot])
            request.session['lissplitscheddilutionrobot']=lisaliqsched
            request.session['lisplansplitdilutionrobot']=lisplanhamilton
            print 'lisfallite',lisfallite
            transaction.commit()
            transaction.commit(using='dbhamilton')
            variables = RequestContext(request,{'lista':zip(lisaliq,lisbarc,lispos,lisname),'lisfallite':json.dumps(lisfallite)})
            return render_to_response('tissue2/split_robot/save_data.html',variables)        
    except Exception,e:
        print 'err',e
        transaction.rollback()
        transaction.rollback(using='dbhamilton')
        variables = RequestContext(request, {'errore':True})
        return render_to_response('tissue2/index.html',variables)
    
