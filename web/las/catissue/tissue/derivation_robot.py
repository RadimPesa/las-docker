from __init__ import *
from catissue.tissue.utils import *
from catissue.tissue.derived import *
from catissue.api.handlers import StorageTubeHandler

#per caricare il primo passo della derivazione, quello in cui scelgo il protocollo. Prendo solo i protocolli del robot
@laslogin_required
@login_required
@permission_decorator('tissue.can_view_BBM_select_aliquots_and_protocols')
def LoadStep1(request):
    request.session['robotstep1']=True
    return ExecDerivedAliquots(request)

#per caricare il secondo passo della derivazione, quello in cui scelgo il kit. Prendo solo i protocolli del robot
@laslogin_required
@login_required
@permission_decorator('tissue.can_view_BBM_select_kit')
def LoadStepKit(request):
    request.session['robotstep2']=True
    return LoadKitDerivedAliquots(request)

#per caricare la schermata per il terzo passo della derivazione
@laslogin_required
@login_required
@permission_decorator('tissue.can_view_BBM_perform_QC_QA')
def LoadInsertMeasure(request):
    name=request.user.username
    lista2=[]
    expvol=FeatureDerivation.objects.get(name='ExpectedVolume')
    print 'expvol',expvol
    #devo prendere solo le derivazioni i cui protocolli prevedono il robot
    featrobot=FeatureDerivation.objects.get(name='Robot')
    lisprotrobot=FeatureDerProtocol.objects.filter(idFeatureDerivation=featrobot).values_list('idDerProtocol',flat=True)
    aliq_da_derivare=AliquotDerivationSchedule.objects.filter(Q(derivationExecuted=0)&Q(Q(operator=name)|Q(operator=''))&~Q(idDerivationProtocol=None)&Q(idDerivationProtocol__in=lisprotrobot)&~Q(loadQuantity=None)&Q(measurementExecuted=0)&Q(deleteTimestamp=None)).order_by('validationTimestamp','initialDate','id')
    print 'aliq derivare',aliq_da_derivare
    #devo filtrare ancora per togliere quelli che non hanno un kit, ma che dovrebbero averlo
    lisfin=[]
    for aliq in aliq_da_derivare:
        if aliq.idKit!=None or aliq.idDerivationProtocol.idKitType==None:
            lisfin.append(aliq)
    stringat=''
    lisaliq=[]
    lisbarc=[]
    lispos=[]
    for alsched in lisfin:
        listafeat=FeatureDerProtocol.objects.filter(idDerProtocol=alsched.idDerivationProtocol,idFeatureDerivation=expvol)
        volatteso=''
        if len(listafeat)!=0:
            volatteso=listafeat[0].value
            if volatteso==0:
                volatteso=''
        lista2.append(volatteso)
        stringat+=alsched.idAliquot.uniqueGenealogyID+'&'
        lisaliq.append(alsched)
    stringtotale=stringat[:-1]
    diz=AllAliquotsContainer(stringtotale)
                
    for al in lisfin:
        listatemp=diz[al.idAliquot.uniqueGenealogyID]
        for val in listatemp:
            ch=val.split('|')                        
            lisbarc.append(ch[1])
            lispos.append(ch[2])
    print 'listavolattesi',lista2
    #devo prendere i protocolli per le misure, quindi quelli di tipo uv e fluo
    lisprotype=ProtocolTypeHamilton.objects.filter(name__in=['fluo','uv']).values_list('id',flat=True)
    lisprot=ProtocolHamilton.objects.filter(protocol_type_id__in=lisprotype)
    print 'lisprot',lisprot
    #prendo i tipi di container
    lislabware=LabwareTypeHamilton.objects.all()
    variables = RequestContext(request,{'lista':zip(lisaliq,lisbarc,lispos,lista2),'lisprot':lisprot,'liscont':lislabware})
    return render_to_response('tissue2/derive_robot/load_measure.html',variables)

#per confermare la schermata della scelta del protocollo di misura e scrivere nelle tabelle di hamilton i dati dei campioni e del plan
@transaction.commit_manually
@transaction.commit_manually(using='dbhamilton')
@laslogin_required
@login_required
@permission_decorator('tissue.can_view_BBM_perform_QC_QA')
def SaveMeasurePhase1(request):   
    try:
        print request.POST
        name=request.user.username
        lista_report=[]
        stringat=''
        #devo prendere solo le derivazioni i cui protocolli prevedono il robot
        featrobot=FeatureDerivation.objects.get(name='Robot')
        lisderprot=FeatureDerProtocol.objects.filter(idFeatureDerivation=featrobot).values_list('idDerProtocol',flat=True)
        aliq_da_derivare=AliquotDerivationSchedule.objects.filter(Q(derivationExecuted=0)&Q(Q(operator=name)|Q(operator=''))&~Q(idDerivationProtocol=None)&Q(idDerivationProtocol__in=lisderprot)&~Q(loadQuantity=None)&Q(measurementExecuted=0)&Q(deleteTimestamp=None)).order_by('validationTimestamp','initialDate','id')
        print 'aliq',aliq_da_derivare
        #devo filtrare ancora per togliere quelli che non hanno un kit, ma che dovrebbero averlo
        lisfin=[]
        for aliq in aliq_da_derivare:
            if aliq.idKit!=None or aliq.idDerivationProtocol.idKitType==None:
                lisfin.append(aliq)
        print 'aliq_da_derivare',lisfin
        aliq_da_svuotare=[]
        nameexperiment=request.POST.get('exp_name')
        lenlisprot=request.POST.get('tot_prot')
        print 'lenlisprot',lenlisprot
        lisprotexec=[]
        for i in range(0,int(lenlisprot)):
            protocollo='pr_qc_'+str(i)
            if protocollo in request.POST:
                idprot=request.POST.get(protocollo)
                lisprotexec.append(int(idprot))
        protexec=ProtocolHamilton.objects.filter(id__in=lisprotexec)
        print 'protexec',protexec        
        #data_mis ha la notazione anno-mese-giorno
        data_mis=request.POST.get('date_meas')
        oggi=timezone.localtime(timezone.now())
        dtutente=timezone.datetime.strptime(data_mis+' 1',"%Y-%m-%d %H")
        #se la data impostata dall'utente e' quella di oggi allora lascio il .now()
        #altrimenti metto la data dell'utente impostata all'1 di notte per far capire che l'ora e' fittizia
        print 'mese utente',dtutente.month
        datainiz=oggi
        if dtutente.year!=oggi.year or dtutente.month!=oggi.month or dtutente.day!=oggi.day:
            datainiz=dtutente
        
        #devo vedere se ci sono delle reazioni non fallite
        contafallite=0
        for i in range(0,len(lisfin)):
            outcome='outcome_'+str(i)
            #se la derivazione e' fallita
            if outcome in request.POST:
                contafallite+=1
        idplan=None
        if contafallite<len(lisfin):
            idconttipo=request.POST.get('container')
            print 'idconttipo',idconttipo
            conttipo=LabwareTypeHamilton.objects.get(id=idconttipo)
            #ce ne sono alcune non fallite
            #creo il plan
            plan=PlanHamilton(name=nameexperiment,
                              timestamp=datainiz,
                              operator=name,
                              labwareid=conttipo)
            plan.save()
            print 'plan',plan
            for p in protexec:
                p_hasprotocol=PlanHasProtocolHamilton(plan_id=plan,
                                                      protocol_id=p)
                p_hasprotocol.save()
            idplan=plan.id
        
        
        '''lisplanrobot=list(AliquotDerivationSchedule.objects.filter(Q(derivationExecuted=0)&~Q(idDerivationProtocol=None)&Q(idDerivationProtocol__in=lisderprot)&Q(measurementExecuted=1)&Q(volumeOutcome__isnull=False)&Q(deleteTimestamp=None)).values_list('idPlanRobot',flat=True))
        print 'lisplanrobot',lisplanrobot
        #Nella lista dei planrobot vedo quali sono quelli le cui misure sono gia' state salvate e che quindi devono comparire nel quarto passo della derivazione        
        lisplanfin=list(PlanHamilton.objects.filter(id__in=lisplanrobot).values_list('id',flat=True))
        print 'lisplanfin',lisplanfin
        lisaliqdersched=AliquotDerivationSchedule.objects.filter(Q(idPlanRobot__in=lisplanfin)&~Q(idDerivationProtocol=None)&Q(idDerivationProtocol__in=lisderprot)&Q(deleteTimestamp=None))
        print 'lisaliqdersched',lisaliqdersched
        delta=len(lisaliqdersched)
        
        #devo prendere anche il numero dei campioni ancora presenti nella corsia iniziale del robot, cioe' quelli pianificati per la diluizione,
        #che pero' non e' ancora stata eseguita materialmente dal robot.
        tipoprot=ProtocolTypeHamilton.objects.get(name='dilution')
        lisprot=ProtocolHamilton.objects.filter(protocol_type_id=tipoprot)
        #prendo il primo della lista tanto non dovrebbe mai esserci piu' di un protocollo di diluizione
        protdilution=lisprot[0]
        #prendo i plan dilution non ancora eseguiti
        lispldilution=PlanHasProtocolHamilton.objects.filter(protocol_id=protdilution).values_list('plan_id',flat=True) 
        lisplandil=list(PlanHamilton.objects.filter(id__in=lispldilution,executed__isnull=True).values_list('id',flat=True))
        print 'lisplandil',lisplandil
        #prendo gli alder collegati a quelle diluizioni. Passo dagli alder perche' qui vedo anche le derivazioni falite. Se mi basassi sui 
        #sample del robot non avrei le fallite.
        lisaliqder=AliquotDerivationSchedule.objects.filter(idPlanDilution__in=lisplandil,derivationExecuted=1)
        print 'lisaliqder',lisaliqder
        delta=len(lisaliqder)'''
        
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
        for i in range(0,len(lisfin)):
            #preparo i nomi con cui accedere alla request.post
            outcome='outcome_'+str(i)
            gen='gen_'+str(i)
            barc='barc_'+str(i)
            geneal=request.POST.get(gen)
            barcode=request.POST.get(barc)
            #prendo il derivation schedule                
            alder=lisfin[i]
            sin_kit=None
            if alder.idDerivationProtocol.idKitType!=None:
                #mi occupo del singolo kit selezionato
                sin_kit=alder.idKit
            print 'sin_kit',sin_kit
            
            if alder.operator=='':
                alder.operator=name
            
            #se la derivazione e' fallita
            if outcome in request.POST:
                print 'fallita'
                protocollo='prot_'+str(i)
                proto=request.POST.get(protocollo)
                #prendo il protocollo
                pro=DerivationProtocol.objects.get(id=proto)
                print 'prot',pro
                
                #per capire qual e' il tipo di derivato prodotto
                t=TransformationDerivation.objects.filter(idDerivationProtocol=pro)
                tipo=t[0].idTransformationChange.idToType.abbreviation
                print 'tipo derivato prodotto',tipo                            
                
                fallita=1
                volume=None
                if sin_kit!=None:
                    #diminuisco di 1 la capacita' di quel kit
                    cap=sin_kit.remainingCapacity
                    if cap>0:
                        cap=cap-1
                    sin_kit.remainingCapacity=cap
                    #se uso per la prima volta quel kit metto ad oggi la data di apertura
                    if sin_kit.openDate==None:
                        sin_kit.openDate=date.today()
                    sin_kit.save()
                
                #incremento il numero di pezzi usati per quell'aliquota
                lista_aliquota=Aliquot.objects.filter(uniqueGenealogyID=geneal,availability=1)
                if lista_aliquota.count()!=0:
                    aliquota=lista_aliquota[0]
                print 'aliquota',aliquota
            
                pezzi_usati=aliquota.timesUsed
                pezzi_usati=pezzi_usati+1
                aliquota.timesUsed=pezzi_usati
                aliquota.save()
                
                #salvo come eseguita la derivazione
                alder.derivationExecuted=1
                                
                #per rendere indisponibili le aliquote esaurite
                if alder.aliquotExhausted==1:
                    aliq_da_svuotare.append(aliquota)
                    print 'aliq_svuotare',aliq_da_svuotare
                
                #devo vedere se la derivazione e' da riprogrammare o no
                riprogramma='riprogramma_'+str(i)
                if riprogramma in request.POST:
                    print 'riprogramma',alder
                    #non creo un nuovo derivation schedule perche' tanto non avro' problemi con l'audit visto che l'aliqdersched originale e'
                    #terminato e l'unico aperto per questo campione e' questo che sto creando
                    aliquotderschedule=AliquotDerivationSchedule(idAliquot=alder.idAliquot,
                                                                 idDerivationSchedule=alder.idDerivationSchedule,
                                                                 idDerivedAliquotType=alder.idDerivedAliquotType,
                                                                 derivationExecuted=0,
                                                                 operator=name)
                    aliquotderschedule.save()
                    print 'alidersched',aliquotderschedule
                #se l'aliq madre era un'aliq derivata allora devo diminuire il suo valore
                #del volume prelevato
                #anche se era sangue devo diminuire il volume
                derived_tipo=AliquotType.objects.get(abbreviation=aliquota.idAliquotType.abbreviation)
                #prendo la feature del volume
                featvol=Feature.objects.filter(idAliquotType=derived_tipo,name='Volume')
                if (tipo=='cDNA') or (tipo=='cRNA')or (len(featvol)!=0 and aliquota.idSamplingEvent.idTissueType.abbreviation=='BL'):        
                    #prendo il valore del volume per l'aliquota madre
                    valore=AliquotFeature.objects.filter(idAliquot=aliquota,idFeature=featvol[0])
                    if len(valore)!=0:
                        #prendo la quantita' di liquido usata inizialmente
                        quantit=alder.loadQuantity
                        print 'quantita\' usata',quantit
                        #sottraggo il volume usato
                        ris=float(valore[0].value)-float(quantit)
                        print 'ris',ris
                        if ris<0:
                            ris=0.0
                        valore[0].value=float(ris)
                        valore[0].save()                
            else:
                print 'riuscita'
                fallita=0
                #preparo i nomi con cui accedere alla request.post
                vol='volume_'+str(i)
                #accedo alla request
                volume=request.POST.get(vol)
                print 'vol',volume
                
            alder.failed=fallita    
            alder.volumeOutcome=volume
            alder.idPlanRobot=idplan
            alder.measurementExecuted=1
            alder.save()
            print 'alderrr',alder
            #se la derivazione non e' fallita
            if outcome not in request.POST:
                samp=SampleHamilton(genid=geneal,
                                    barcode=barcode,
                                    volume=alder.volumeOutcome,
                                    rank=i+1+delta,
                                    plan_id=plan)
                samp.save()
            stringat+=alder.idAliquot.uniqueGenealogyID+'&'            
                
        stringtotale=stringat[:-1]
        dizpos=AllAliquotsContainer(stringtotale)
        for al in lisfin:
            listatemp=dizpos[al.idAliquot.uniqueGenealogyID]
            for val in listatemp:
                ch=val.split('|')                
                lista_report.append(ReportToHtml([al.idAliquot.uniqueGenealogyID,ch[1],ch[2]]))
            
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
        if contafallite==len(lisfin):
            #vuol dire che devo terminare qui la procedura
            variables = RequestContext(request,{'vuota':True})
            return render_to_response('tissue2/derive_robot/load_measure.html',variables)
        else:
            print 'lis report',lista_report
            #faccio comparire una pagina per dire che i dati lato LAS sono stati salvati. Bisogna aspettare che il robot agisca
            variables = RequestContext(request,{'fine':True,'lista_der':lista_report})
            return render_to_response('tissue2/derive_robot/load_measure.html',variables)
    except Exception,e:
        print 'errr',e
        transaction.rollback()
        transaction.rollback(using='dbhamilton')
        variables = RequestContext(request, {'errore':True})
        return render_to_response('tissue2/index.html',variables)

#per caricare la schermata per l'ultimo passo della derivazione, quella che permette di creare le aliquote
@laslogin_required
@login_required
@permission_decorator('tissue.can_view_BBM_create_derivatives')
def LoadCreateAliquot(request):
    name=request.user.username
    featrobot=FeatureDerivation.objects.get(name='Robot')
    instr=Instrument.objects.get(name='Hamilton')
    lismisure=Measure.objects.filter(idInstrument=instr,name__startswith='concentration')
    lmisure=[]
    for m in lismisure:
        lmisure.append(m.id)
    prot=None
    lisprotrobot=FeatureDerProtocol.objects.filter(idFeatureDerivation=featrobot).values_list('idDerProtocol',flat=True)
    #prendo gli idplanrobot che mi servono per avere tutte le derivazioni, anche quelle fallite
    lisplanrobot=list(AliquotDerivationSchedule.objects.filter(Q(derivationExecuted=0)&Q(Q(operator=name)|Q(operator=''))&~Q(idDerivationProtocol=None)&Q(idDerivationProtocol__in=lisprotrobot)&Q(measurementExecuted=1)&Q(volumeOutcome__isnull=False)&Q(deleteTimestamp=None)).values_list('idPlanRobot',flat=True))
    print 'lisplanrobot',lisplanrobot
    #Nella lista dei planrobot vedo quali sono quelli le cui misure sono gia' state salvate e che quindi devono comparire nel quarto passo della derivazione
    lisplanhamilton=PlanHamilton.objects.filter(id__in=lisplanrobot,processed__isnull=False)
    lisplanfin=[]
    for p in lisplanhamilton:
        lisplanfin.append(p.id)    
    lisaliqdersched=AliquotDerivationSchedule.objects.filter(Q(idPlanRobot__in=lisplanfin)&Q(Q(operator=name)|Q(operator=''))&~Q(idDerivationProtocol=None)&Q(idDerivationProtocol__in=lisprotrobot)&Q(deleteTimestamp=None)).order_by('validationTimestamp')
    stringat=''
    for al in lisaliqdersched:
        stringat+=al.idAliquot.uniqueGenealogyID+'&'
        #prendo l'ultimo prot di derivazione della lista, tanto ho solo bisogno di sapere i parametri del prot
        prot=al.idDerivationProtocol
    stringtotale=stringat[:-1]
    dizpos=AllAliquotsContainer(stringtotale)
    lisbarc=[]
    lispos=[]
    #chiave l'idalidersched e valore un dizionario con volumi e concentrazioni presenti
    dizmisure={}
    lisfallite=[]
    print 'dizpos',dizpos
    for al in lisaliqdersched:
        listatemp=dizpos[al.idAliquot.uniqueGenealogyID]
        for val in listatemp:
            ch=val.split('|')
            #se il campione e' esaurito perche' appartiene ad una derivazione fallita in cui e' stato esaurito il campione, allora non
            #ho la posizione e quindi metto una stringa vuota
            if len(ch)>1:
                lisbarc.append(ch[1])
                lispos.append(ch[2])
            else:
                lisbarc.append('')
                lispos.append('')
        #se per caso il campione e' esaurito allora listatemp e' vuota, ma io devo comunque inserire qualcosa nelle liste
        if len(listatemp)==0:
            lisbarc.append('')
            lispos.append('')
        #prendo il quality event
        lisqualev=QualityEvent.objects.filter(idAliquotDerivationSchedule=al).order_by('id')
        voltot=al.volumeOutcome
        diztemp={}
        if len(lisqualev)==0:
            #non ho salvato un qualev perche' non ho fatto misure
            volusato=0
        else:
            #prendo il qualev piu' recente
            qualev=lisqualev[len(lisqualev)-1]
            #prendo il valore della concentrazione
            conc=MeasurementEvent.objects.filter(idQualityEvent=qualev,idMeasure__in=lmisure)
            print 'conc',conc
            for c in conc:
                diztemp[c.idMeasure.id]=c.value
            #per il volume dell'aliq madre. Devo sottrarre il volume usato per le misure
            volusato=qualev.quantityUsed
            if volusato==None:
                volusato=0
        voleffettivo=''
        if al.failed==0:
            voleffettivo=voltot-volusato
        else:
            lisfallite.append(al.id)
        diztemp['volume']=voleffettivo
        dizmisure[al.id]=diztemp
    print 'dizmisure',dizmisure
    num_aliq='' 
    vol='' 
    concen=''
    if prot!=None:
        numal=FeatureDerivation.objects.get(name='number_Aliquot')
        volal=FeatureDerivation.objects.get(name='volume_Aliquot')
        concal=FeatureDerivation.objects.get(name='concentration_Aliquot')
        featnumal=FeatureDerProtocol.objects.get(idDerProtocol=prot,idFeatureDerivation=numal)
        num_aliq=int(featnumal.value)
        featvolal=FeatureDerProtocol.objects.get(idDerProtocol=prot,idFeatureDerivation=volal)
        vol=featvolal.value
        featconcal=FeatureDerProtocol.objects.get(idDerProtocol=prot,idFeatureDerivation=concal)
        concen=featconcal.value
    print 'lista',lisaliqdersched
    print 'lisbarc',lisbarc
    print 'lispos',lispos
    #passo alla schermata il nome del primo plan che trovo. So che puo' essercene piu' di 1, ma scelgo comunque il primo. Al massimo sara' l'utente a
    #cambiare il nome del plan che compare nella schermata
    nomplan=''
    labwareid=0
    if len(lisplanhamilton)!=0:
        nomplan=lisplanhamilton[0].name
        labwareid=lisplanhamilton[0].labwareid.id
    #prendo i tipi di container
    lislabware=LabwareTypeHamilton.objects.all()
    variables = RequestContext(request,{'lista':zip(list(lisaliqdersched),lisbarc,lispos),'dizmisure':json.dumps(dizmisure),'lisfallite':json.dumps(lisfallite),'liscont':lislabware,'lismisure':lismisure,'num_al':num_aliq,'vol_al':vol,'conc_al':concen,'nomeplan':nomplan,'labwareid':labwareid})
    return render_to_response('tissue2/derive_robot/create_aliquots.html',variables)

#per salvare nel DB di hamilton i valori dei campioni da creare
@transaction.commit_manually
@transaction.commit_manually(using='dbhamilton')
@laslogin_required
@login_required
@permission_decorator('tissue.can_view_BBM_create_derivatives')
def WriteAliquotDBRobot(request):
    try:
        if request.method=='POST':
            print request.POST
        
            #con javascript faccio una post che mi fa scattare questo if. Salvo i dati nella sessione
            #per poi riprenderli dopo quando clicco su submit
            if 'salva' in request.POST:                
                dizaliq=json.loads(request.POST.get('dizaliq'))
                dizremain=json.loads(request.POST.get('dizremain'))
                request.session['dizaliqderivaterobot']=dizaliq
                request.session['dizremainderivedrobot']=dizremain
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
                if request.session.has_key('dizaliqderivaterobot'):
                    #chiave l'idaldersched e valore una lista con i vari campioni da creare
                    dizaliq=request.session.get('dizaliqderivaterobot')
                if request.session.has_key('dizremainderivedrobot'):
                    dizremain=request.session.get('dizremainderivedrobot')
                nameexperiment=request.POST.get('exp_name')
                featrobot=FeatureDerivation.objects.get(name='Robot')
                lisprotrobot=FeatureDerProtocol.objects.filter(idFeatureDerivation=featrobot).values_list('idDerProtocol',flat=True)
                lisplanrobot=list(AliquotDerivationSchedule.objects.filter(Q(derivationExecuted=0)&Q(Q(operator=name)|Q(operator=''))&~Q(idDerivationProtocol=None)&Q(idDerivationProtocol__in=lisprotrobot)&Q(measurementExecuted=1)&Q(volumeOutcome__isnull=False)&Q(deleteTimestamp=None)).values_list('idPlanRobot',flat=True))                
                #Nella lista dei planrobot vedo quali sono quelli le cui misure sono gia' state salvate e che quindi devono comparire nel quarto passo della derivazione
                lisplanfin=list(PlanHamilton.objects.filter(id__in=lisplanrobot,processed__isnull=False).values_list('id',flat=True))                    
                lisaliqdersched=AliquotDerivationSchedule.objects.filter(Q(idPlanRobot__in=lisplanfin)&Q(Q(operator=name)|Q(operator=''))&~Q(idDerivationProtocol=None)&Q(idDerivationProtocol__in=lisprotrobot)&Q(deleteTimestamp=None)).order_by('validationTimestamp')
                print 'lisaliqdersched',lisaliqdersched
                lissample=SampleHamilton.objects.filter(plan_id__in=lisplanfin)
                print 'lissample',lissample
                #chiave il gen e valore il rank del campione, in modo che in questo plan per la diluizione copio il rank che aveva il campione
                #per la quantificazione
                dizgensamp={}
                for samp in lissample:
                    dizgensamp[samp.genid]=samp.rank
                print 'dizgensamp',dizgensamp
                tipoprot=ProtocolTypeHamilton.objects.get(name='dilution')
                lisprot=ProtocolHamilton.objects.filter(protocol_type_id=tipoprot)
                #prendo il primo della lista tanto non dovrebbe mai esserci piu' di un protocollo di diluizione
                protdilution=lisprot[0]
                '''#devo prendere il numero dei campioni ancora presenti nella corsia iniziale del robot, che possono essere li' in attesa della diluizione
                #o della quantificazione
                lisplandil=list(PlanHamilton.objects.filter(executed__isnull=True).values_list('id',flat=True))
                print 'lisplandil',lisplandil
                maxrank=max(list(SampleHamilton.objects.filter(plan_id__in=lisplandil).values_list('rank',flat=True)))
                print 'maxrank',maxrank
                #prendo gli alder collegati a quelle diluizioni. Passo dagli alder perche' qui vedo anche le derivazioni falite. Se mi basassi sui 
                #sample del robot non avrei le fallite.                
                lisaliqder=AliquotDerivationSchedule.objects.filter(idPlanDilution__in=lisplandil,derivationExecuted=1)
                print 'lisaliqder',lisaliqder               
                delta=len(lisaliqder)
                if maxrank>delta:
                    delta=maxrank
                print 'delta',delta'''
                #vedo se ci sono delle derivazioni non fallite
                fallita=True
                for k,v in dizremain.items():
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
                lista_report=[]
                
                for i in range(0,len(lisaliqdersched)):
                    alder=lisaliqdersched[i]
                    barcode=dizremain[str(alder.id)]['barcode']
                    print 'barcode',barcode
                    pos=dizremain[str(alder.id)]['position']
                    lista_report.append(ReportToHtml([alder.idAliquot.uniqueGenealogyID,barcode,pos]))
                    #solo se non e' fallita creo i dati nel DB di Hamilton
                    if alder.failed==0:
                        alder.derivationExecuted=1                        
                        if alder.operator=='':
                            alder.operator=name
                        #controllo se l'utente ha bloccato qui la procedura impostando il check
                        checkstop=dizremain[str(alder.id)]['checkstop']
                        if checkstop=='false':
                            rank=dizgensamp[alder.idAliquot.uniqueGenealogyID]
                            samp=SampleHamilton(genid=alder.idAliquot.uniqueGenealogyID,
                                            barcode=barcode,
                                            volume=alder.volumeOutcome,
                                            rank=rank,
                                            plan_id=plan)
                            samp.save()
                            #puo' capitare che se non e' stata calcolata la conc della madre, non posso creare le figlie, quindi nel dizaliq non avro'
                            #l'id dell'aldersched e semplicemente non creo niente, ma metto solo come concluso l'aliqdersched
                            if str(alder.id) in dizaliq:
                                lischild=dizaliq[str(alder.id)]
                                print 'lischild',lischild
                                for j in range(0,len(lischild)):
                                    #ch e' un dizionario con i valori della singola aliquota da creare
                                    ch=lischild[str(j)]
                                    vol=float(ch['volume'])
                                    print 'vol',vol
                                    
                                    #solo se il volume e' diverso da zero creo il campione
                                    if vol!=0:
                                        #devo vedere se e' da creare il remain
                                        create=dizremain[str(alder.id)]['create']
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
                            #l'utente ha bloccato la procedura a questo passo, quindi metto la derivazione come fallita                            
                            pro=alder.idDerivationProtocol
                            print 'prot',pro                            
                            #per capire qual e' il tipo di derivato prodotto
                            t=TransformationDerivation.objects.filter(idDerivationProtocol=pro)
                            tipo=t[0].idTransformationChange.idToType.abbreviation
                            print 'tipo derivato prodotto',tipo                            
                            
                            alder.failed=1
                            sin_kit=alder.idKit
                            if sin_kit!=None:
                                #diminuisco di 1 la capacita' di quel kit
                                cap=sin_kit.remainingCapacity
                                if cap>0:
                                    cap=cap-1
                                sin_kit.remainingCapacity=cap
                                #se uso per la prima volta quel kit metto ad oggi la data di apertura
                                if sin_kit.openDate==None:
                                    sin_kit.openDate=date.today()
                                sin_kit.save()
                                                        
                            aliquota=alder.idAliquot
                            print 'aliquota',aliquota                        
                            pezzi_usati=aliquota.timesUsed
                            pezzi_usati=pezzi_usati+1
                            aliquota.timesUsed=pezzi_usati
                            aliquota.save()
                                            
                            #per rendere indisponibili le aliquote esaurite
                            if alder.aliquotExhausted==1:
                                aliq_da_svuotare.append(aliquota)
                                print 'aliq_svuotare',aliq_da_svuotare
                                                        
                            #se l'aliq madre era un'aliq derivata allora devo diminuire il suo valore
                            #del volume prelevato
                            #anche se era sangue devo diminuire il volume
                            derived_tipo=aliquota.idAliquotType
                            #prendo la feature del volume
                            featvol=Feature.objects.filter(idAliquotType=derived_tipo,name='Volume')
                            if (tipo=='cDNA') or (tipo=='cRNA')or (len(featvol)!=0 and aliquota.idSamplingEvent.idTissueType.abbreviation=='BL'):        
                                #prendo il valore del volume per l'aliquota madre
                                valore=AliquotFeature.objects.filter(idAliquot=aliquota,idFeature=featvol[0])
                                if len(valore)!=0:
                                    #prendo la quantita' di liquido usata inizialmente
                                    quantit=alder.loadQuantity
                                    print 'quantita\' usata',quantit
                                    #sottraggo il volume usato
                                    ris=float(valore[0].value)-float(quantit)
                                    print 'ris',ris
                                    if ris<0:
                                        ris=0.0
                                    valore[0].value=float(ris)
                                    valore[0].save()
                    if not fallita:
                        alder.idPlanDilution=plan.id
                    alder.save()
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
                    variables = RequestContext(request,{'vuota':True,'lista_der':lista_report,'labwareid':'0'})
                    return render_to_response('tissue2/derive_robot/create_aliquots.html',variables)
                else:
                    variables = RequestContext(request,{'fine':True,'lista_der':lista_report,'labwareid':'0'})
                    return render_to_response('tissue2/derive_robot/create_aliquots.html',variables)
    except Exception,e:
        print 'err derivation robot:',e
        transaction.rollback()
        transaction.rollback(using='dbhamilton')
        variables = RequestContext(request, {'errore':True})
        return render_to_response('tissue2/index.html',variables)

#per caricare la schermata che contiene i campioni da creare e poi per salvarli effettivamente nel LAS
@laslogin_required
@login_required
@permission_decorator('tissue.can_view_BBM_create_derivatives')
@transaction.commit_manually
@transaction.commit_manually(using='dbhamilton')
def CreateDerivatives(request):
    try:
        if request.method=='POST':
            print request.POST
            if request.session.has_key('lisderschedcreatederivativesrobot'):                
                lisaliqdersched=request.session.get('lisderschedcreatederivativesrobot')
                del request.session['lisderschedcreatederivativesrobot']
            if request.session.has_key('lisplancreatederivativesrobot'):                
                lisplan=request.session.get('lisplancreatederivativesrobot')
                del request.session['lisplancreatederivativesrobot']
            name=request.user.username
            lisplanfin=[]            
            for p in lisplan:
                lisplanfin.append(p.id)
            #ho tutti gli id dei piani e prendo i sample
            lissample=SampleHamilton.objects.filter(plan_id__in=lisplanfin)
            print 'lissample',lissample
            print 'lisdersched',lisaliqdersched
            aldersched=None
            lista_al_der=[]
            listaaliqstorage=[]
            listatipialiq=[]
            #chiave il gen del derivato nuovo e valore un diz con vol e conc e barc
            dizvalaliqder={}
            lisaliqesaurite=[]
            for samp in lissample:
                gen=samp.genid
                contatore=0
                for alder in lisaliqdersched:                    
                    if gen==alder.idAliquot.uniqueGenealogyID and samp.plan_id.id==alder.idPlanDilution:
                        aldersched=alder
                        break
                print 'aldersched',aldersched
                lischild=ChildHamilton.objects.filter(sample_id=samp)
                print 'lischild',lischild
                #prendo la data run del primo figlio, tanto e' uguale anche per gli altri
                data_esecuz=None
                if len(lischild)!=0:
                    time_run=lischild[0].run_id.timestamp
                    data_esecuz=datetime.date(int(time_run.year),int(time_run.month),int(time_run.day))
                print 'data',data_esecuz
                aliq=aldersched.idAliquot
                tipo=aldersched.idDerivedAliquotType.abbreviation                
                print 'tipo',tipo
                if aliq.derived==0:
                    if tipo=='DNA':
                        der='D'
                    elif tipo=='RNA':
                        der='R'
                    elif tipo=='P':
                        der='P'
                    elif tipo=='PL':
                        der='PL'
                    elif tipo=='VT':
                        der='VT'
                elif aliq.derived==1:
                    if tipo=='cDNA':
                        der='D'
                    elif tipo=='cRNA':
                        der='R'  
                print 'genealogy id',gen
                ge = GenealogyID(gen)
                fine=''
                print 'geee',ge.getGenID()
                
                #mi restituisce la lunghezza della parte destinata alla seconda derivazione
                for p in range(0,ge.getLen2Derivation()):
                    fine+='0'
                deriv=1
                if der=='PL' or der=='VT':
                    fine='00'
                    deriv=0
                if aliq.derived==0:
                    #prendo l'inizio dell'aliquota che sto derivando adesso
                    #e' un'aliq originale quindi prendo tutti i caratteri fino alla fine
                    #dei 10 zeri                  
                    stringa=ge.getPartForDerAliq()
                    #stringa=gen[0:20]
                    #aggiungo il tipo di derivato che voglio ottenere (R o D)
                    stringa=stringa+der                    
                    #guardo se quell'inizio di genealogy ce l'ha gia' qualche aliquota derivata
                    #cerco anche i derivati che finiscono con '000' per trovare solo i 
                    #dna o gli rna puri e non riderivati per ottenre cRNA o cDNA
                    #e' giusto considerare anche le aliq non disponibili                    
                    disable_graph()
                    lista_aliquote_derivate=Aliquot.objects.filter(uniqueGenealogyID__startswith=stringa,uniqueGenealogyID__endswith=fine,derived=deriv).order_by('-uniqueGenealogyID')
                    enable_graph()
                    
                    print 'lista_aliquote',lista_aliquote_derivate
                    if lista_aliquote_derivate.count()!=0:
                        #prendo il primo oggetto che e' quello che ha il contatore piu' alto
                        maxgen=lista_aliquote_derivate[0].uniqueGenealogyID
                        nuovoge=GenealogyID(maxgen)
                        maxcont=nuovoge.getAliquotExtraction()
                        contatore=int(maxcont)
                elif aliq.derived==1:
                    #prendo l'inizio dell'aliquota che sto derivando adesso
                    #e' un derivato quindi prendo tutti i caratteri meno gli ultimi tre
                    stringa=ge.getPartFor2DerivationAliq()
                    #stringa=gen[0:23]
                    #aggiungo il tipo di derivato che voglio ottenere (R o D)
                    stringa=stringa+der
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
                
                #diminuisco la capacita' del kit usato
                kit=aldersched.idKit
                if kit!=None:                    
                    cap=kit.remainingCapacity
                    if cap>0:
                        cap=cap-1
                    kit.remainingCapacity=cap
                    #se uso per la prima volta quel kit metto ad oggi la data di apertura
                    if kit.openDate==None:
                        kit.openDate=date.today()
                    kit.save()
                
                #incremento il numero di volte in cui e' stata usata quell'aliquota
                pezzi_usati=aliq.timesUsed
                pezzi_usati=pezzi_usati+1
                aliq.timesUsed=pezzi_usati
                aliq.save()
                
                #se l'aliq madre era un'aliq derivata allora devo diminuire il suo valore
                #del volume prelevato per creare le figlie
                #anche se era sangue devo diminuire il volume
                derived_tipo=aliq.idAliquotType
                #prendo la feature del volume
                featvol=Feature.objects.filter(idAliquotType=derived_tipo,name='Volume')
                if (tipo=='cDNA') or (tipo=='cRNA') or (len(featvol)!=0 and aliq.idSamplingEvent.idTissueType.abbreviation=='BL') or (len(featvol)!=0 and aliq.idSamplingEvent.idTissueType.abbreviation=='UR'):
                    #prendo il valore del volume per l'aliquota madre
                    valore=AliquotFeature.objects.filter(idAliquot=aliq,idFeature=featvol[0])
                    if len(valore)!=0:
                        #sottraggo il volume usato
                        ris=float(valore[0].value)-float(aldersched.loadQuantity)
                        print 'ris',ris
                        if ris<0:
                            ris=0.0
                        valore[0].value=float(ris)
                        valore[0].save()
                
                if len(lischild)!=0:
                    tumore=ge.getOrigin()
                    print 'tumore',tumore
                    #caso=gen[3:7]
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
                    #t=gen[7:9]
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
                    #creo un nuovo derivation event
                    derev=DerivationEvent(idSamplingEvent=campionamento,
                                             idAliqDerivationSchedule=aldersched,
                                             derivationDate=data_esecuz,
                                             operator=name)
                    derev.save()
                    print 'der',derev
                    
                    derived_tipo=aldersched.idDerivedAliquotType
                    
                    #prendo la feature del volume
                    featvol=Feature.objects.get(idAliquotType=derived_tipo,name='Volume')
                    #prendo la feature della concentrazione
                    featconc=None
                    lfeatconc=Feature.objects.filter(idAliquotType=derived_tipo,name='Concentration')
                    if len(lfeatconc)!=0:
                        featconc=lfeatconc[0]
                        
                    for ch in lischild:
                        #devo sommare il volume preso dalla madre con quello del diluente
                        vo=ch.volume+ch.vol_kit
                        c=ch.concentration
                        if c=='NaN' or c==0.0:
                            c=-1
                        co=float(c)                    
                        #solo se il volume e' diverso da zero creo l'aliquota derivata
                        if vo!=0.0:
                            contatore=contatore+1
                            num_ordine=str(contatore).zfill(2)
                            
                            if aliq.derived==0:
                                if derived_tipo.type!='Derived':
                                    #nel caso di creazione di plasma o di PBMC
                                    diz_dati={'archiveMaterial2':der,'aliqExtraction2':num_ordine,'2derivationGen':'00'}
                                else:
                                    diz_dati={'archiveMaterial1':der,'aliqExtraction1':num_ordine,'2derivation':'0','2derivationGen':'00'}  
                                ge.updateGenID(diz_dati)
                                nuovo_gen=ge.getGenID()   
                            elif aliq.derived==1:
                                diz_dati={'2derivation':der,'2derivationGen':num_ordine}  
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
                                #print 'data',data
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
                            lista_al_der.append(al_der)
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
                        
                #salvo che la derivazione e' stata eseguita
                aldersched.derivationExecuted=1
                if aldersched.operator=='':
                    aldersched.operator=name
                aldersched.save()
                #se la madre e' esaurita
                if aldersched.aliquotExhausted==1:
                    aliq.availability=0
                    aliq.save()
                    lisaliqesaurite.append(aliq.uniqueGenealogyID)
                                    
            print 'dizvalaliqder',dizvalaliqder
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
            for al in lista_al_der:
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
            lista_val_aliq_der=[]
            for al in lista_al_der:
                gen=al.uniqueGenealogyID
                diztemp=dizvalaliqder[gen]
                if gen in dizgen:
                    lisvalori=dizgen[gen]
                    print 'lisvalori',lisvalori
                    val=lisvalori.split('|')                    
                    plate=str(val[2])
                    tubepos=str(val[1])
                stringa=al.uniqueGenealogyID+'&'+diztemp['barcode']+'&'+plate+'&'+tubepos+'&'+str(diztemp['conc'])+'&'+str(diztemp['vol'])
                lista_val_aliq_der.append(stringa)
            
            if len(lisaliqesaurite)!=0:
                #mi collego allo storage per svuotare le provette contenenti le aliq
                #esaurite
                address=Urls.objects.get(default=1).url
                url = address+"/full/"
                print url
                values = {'lista' : json.dumps(lisaliqesaurite), 'tube': 'empty','canc':True,'operator':name}
                data = urllib.urlencode(values)
                req = urllib2.Request(url,data=data, headers={"workingGroups" : get_WG_string()})
                urllib2.urlopen(req)
                
            #prendo la lista con tutte le aliq salvate dentro e le converto per la visualizzazione in html
            lista,intest,dizcsv,inte,dizsupervisori,unitamis=LastPartDerivation(request,'n',lista_val_aliq_der)
            
            #metto come eseguiti i piani che ho trattato
            for plan in lisplan:
                plan.processed=timezone.localtime(timezone.now())
                plan.save()
            
            email = LASEmail (functionality=get_functionality(), wgString=get_WG_string())
            msg=['Derivation procedure executed','','Assigned to:\t'+name,'','Aliquots:','N\tGenealogy ID\tBarcode\tPlate\tPosition\tVolume(ul)\tConcentration(ng/ul)']                    
            print 'lista al der',lista_al_der
            lisgen=[]
            dizmadri={}
            #lista_al_der ha dentro le aliq derivate create
            for al in lista_al_der:
                #devo risalire alle madri dei derivati, perche' la divisione fra wg proprietari la faccio sulle madri
                #e non sulle figlie che non esistono ancora nell'Aliquot_wg, visto che vengono create alla fine di tutto
                alder=DerivationEvent.objects.get(idSamplingEvent=al.idSamplingEvent,operator=name)
                lisgen.append(alder.idAliqDerivationSchedule.idAliquot.uniqueGenealogyID)
                #faccio un dizionario con figlie come chiave e valore la madre
                dizmadri[al.uniqueGenealogyID]=alder.idAliqDerivationSchedule.idAliquot.uniqueGenealogyID
            #non metto availability=1 perche' se la madre e' esaurita non me la prende e non va bene
            aliquots=Aliquot.objects.filter(uniqueGenealogyID__in=lisgen)
            wgList=WG.objects.filter(id__in=Aliquot_WG.objects.filter(aliquot__in=aliquots).values_list('WG',flat=True).distinct())
            print 'wglist',wgList
            print 'dizmadri',dizmadri
            for wg in wgList:
                print 'wg',wg
                email.addMsg([wg.name], msg)
                #aliq ha dentro le madri della derivazione
                aliq=aliquots.filter(id__in=Aliquot_WG.objects.filter(WG=wg).values_list('aliquot',flat=True).distinct())
                print 'aliq',aliq
                i=1
                lisplanner=[]
                #per mantenere l'ordine dei campioni anche nell'e-mail
                for aliqder in lista_al_der:
                    for al in aliq:
                        #guardo nel dizionario delle madri se il loro rapporto e' corretto
                        madre=dizmadri[aliqder.uniqueGenealogyID]
                        print 'madre',madre
                        if madre==al.uniqueGenealogyID:
                            stringatab=dizcsv[aliqder.uniqueGenealogyID]
                            email.addMsg([wg.name],[str(i)+'\t'+stringatab])
                            i=i+1
                            alder=DerivationEvent.objects.get(idSamplingEvent=aliqder.idSamplingEvent,operator=name)
                            if alder.idAliqDerivationSchedule.idDerivationSchedule.operator not in lisplanner:
                                lisplanner.append(alder.idAliqDerivationSchedule.idDerivationSchedule.operator)
                print 'lisplanner',lisplanner
                #mando l'e-mail al pianificatore
                email.addRoleEmail([wg.name], 'Planner', lisplanner)
                email.addRoleEmail([wg.name], 'Executor', [request.user.username])
            try:
                email.send()
            except Exception, e:
                print 'err email:',e
                pass
                
            transaction.commit()
            transaction.commit(using='dbhamilton')
            variables = RequestContext(request,{'fine':True,'lista_der':lista,'intest':intest})
            return render_to_response('tissue2/derive_robot/create_derivatives.html',variables)
        else:
            #devo prendere i campioni eseguiti, cioe' i plan eseguiti
            name=request.user.username
            lisfallite=[]
            featrobot=FeatureDerivation.objects.get(name='Robot')
            lisprotrobot=FeatureDerProtocol.objects.filter(idFeatureDerivation=featrobot).values_list('idDerProtocol',flat=True)
            lisprotype=ProtocolTypeHamilton.objects.filter(name='dilution').values_list('id',flat=True)
            lisprot=ProtocolHamilton.objects.filter(protocol_type_id__in=lisprotype).values_list('id',flat=True)
            print 'lisprot',lisprot
            lisplanprot=PlanHasProtocolHamilton.objects.filter(protocol_id__in=lisprot).values_list('plan_id',flat=True)
            lisplanhamilton=PlanHamilton.objects.filter(id__in=lisplanprot,executed__isnull=False,processed__isnull=True)
            lisplanfin=[]
            #chiave l'id e valore il nome del plan
            dizplanname={}
            for p in lisplanhamilton:
                lisplanfin.append(p.id)
                dizplanname[p.id]=p.name
            print 'lisplanfin',lisplanfin
            lisaliqdersched=AliquotDerivationSchedule.objects.filter(Q(idPlanDilution__in=lisplanfin)&Q(Q(operator=name)|Q(operator=''))&~Q(idDerivationProtocol=None)&Q(idDerivationProtocol__in=lisprotrobot)&Q(derivationExecuted=1)&Q(deleteTimestamp=None)).order_by('validationTimestamp')
            print 'lisaliqdersched',lisaliqdersched
            stringat=''
            for alder in lisaliqdersched:
                stringat+=alder.idAliquot.uniqueGenealogyID+'&'
            stringtotale=stringat[:-1]
            diz=AllAliquotsContainer(stringtotale)
            lisaliq=[]
            lisbarc=[]
            lispos=[]
            lisname=[]
            for alder in lisaliqdersched:
                if alder.failed==1:
                    lisfallite.append(alder.id)
                listatemp=diz[alder.idAliquot.uniqueGenealogyID]
                for val in listatemp:
                    ch=val.split('|')
                    lisaliq.append(alder)
                    lisbarc.append(ch[1])
                    lispos.append(ch[2])
                    lisname.append(dizplanname[alder.idPlanDilution])
                #se per caso il campione e' esaurito allora listatemp e' vuota, ma io devo comunque inserire qualcosa nelle liste
                if len(listatemp)==0:
                    lisaliq.append(alder)
                    lisbarc.append('')
                    lispos.append('')
                    if alder.failed==1:
                        lisname.append('Failed')
                    else:
                        lisname.append(dizplanname[alder.idPlanDilution])
            request.session['lisderschedcreatederivativesrobot']=lisaliqdersched
            request.session['lisplancreatederivativesrobot']=lisplanhamilton                    
            transaction.commit()
            transaction.commit(using='dbhamilton')
            variables = RequestContext(request,{'lista':zip(lisaliq,lisbarc,lispos,lisname),'lisfallite':json.dumps(lisfallite)})
            return render_to_response('tissue2/derive_robot/create_derivatives.html',variables)        
    except Exception,e:
        print 'err',e
        transaction.rollback()
        transaction.rollback(using='dbhamilton')
        variables = RequestContext(request, {'errore':True})
        return render_to_response('tissue2/index.html',variables)
