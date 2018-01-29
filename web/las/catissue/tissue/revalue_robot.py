from __init__ import *
from catissue.tissue.revalue import *

#per caricare il primo passo della rivalutazione, quello con la convalida dei campioni
@laslogin_required
@login_required
@permission_decorator('tissue.can_view_BBM_revalue_aliquots')
def LoadValidateAliquot(request):
    request.session['robotrevalueload']=True
    return ExecRevalueAliquots(request)

#per confermare la schermata della scelta del protocollo di misura e scrivere nelle tabelle di hamilton i dati dei campioni e del plan
@transaction.commit_manually
@transaction.commit_manually(using='dbhamilton')
@laslogin_required
@login_required
@permission_decorator('tissue.can_view_BBM_revalue_aliquots')
def PlanQuantification(request):   
    try:
        print request.POST
        name=request.user.username
        lista_report=[]        
        if request.session.has_key('aliqrivPlanQuantRobot'):
            lisfin=request.session.get('aliqrivPlanQuantRobot')
            del request.session['aliqrivPlanQuantRobot']
        if request.session.has_key('dizinfoaliqrivPlanQuantRobot'):
            dizposizioni=request.session.get('dizinfoaliqrivPlanQuantRobot')
            del request.session['dizinfoaliqrivPlanQuantRobot']
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
            
        idconttipo=request.POST.get('container')        
        conttipo=LabwareTypeHamilton.objects.get(id=idconttipo)
        print 'conttipo',conttipo
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
        
        if conttipo.description!='matrix':
            #per il rank devo vedere se nel carrello del robot ho gia' qualcosa in coda, che proviene magari da un'estrazione che ho fatto prima di cui
            #pero' ho fatto solo la quantificazione e non ancora la diluizione. Quindi ho delle posizioni gia' piene nel carrello e non posso partire da 1
            #per il rank, ma devo sommare uno spiazzamento.
            #Non filtro sull'operatore perche' ho bisogno di avere tutti gli aliqdersched in coda, anche quelli di altri utenti
            #Anche se qui sto rivalutando tengo comunque conto delle eventuali derivazioni in corso
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
            gen='gen_'+str(i)
            barc='barc_'+str(i)
            geneal=request.POST.get(gen)
            barcode=request.POST.get(barc)
            #prendo il revaluation schedule
            alrev=lisfin[i]            
            alrev.operator=request.user
            alrev.idPlanRobot=idplan
            alrev.revaluationExecuted=1
            alrev.save()
            print 'alrev',alrev
            
            if conttipo.description!='matrix':
                rank=i+1+delta
            else:
                rank=None
            #devo prendere il volume del campione, se c'e'
            aliq=alrev.idAliquot
            vol=-1
            lfeatvol=Feature.objects.filter(name='Volume',idAliquotType=aliq.idAliquotType)
            if len(lfeatvol)!=0:
                lfeat=AliquotFeature.objects.filter(idFeature=lfeatvol[0],idAliquot=aliq)
                if len(lfeat)!=0:
                    vol=lfeat[0].value
            print 'vol',vol
            samp=SampleHamilton(genid=geneal,
                                barcode=barcode,
                                volume=vol,
                                rank=rank,
                                plan_id=plan)
            samp.save()           
                
        for al in lisfin:
            listatemp=dizposizioni[al.idAliquot.uniqueGenealogyID]
            for val in listatemp:
                ch=val.split('|')                
                lista_report.append(ReportToHtml([al.idAliquot.uniqueGenealogyID,ch[1],ch[2]]))                    
        print 'lis report',lista_report
        transaction.commit()
        transaction.commit(using='dbhamilton')        
        #faccio comparire una pagina per dire che i dati lato LAS sono stati salvati. Bisogna aspettare che il robot agisca
        variables = RequestContext(request,{'fine':True,'lista_der':lista_report})
        return render_to_response('tissue2/revalue_robot/set_procedure.html',variables)
    except Exception,e:
        print 'error',e
        transaction.rollback()
        transaction.rollback(using='dbhamilton')
        variables = RequestContext(request, {'errore':True})
        return render_to_response('tissue2/index.html',variables)
    
#per far comparire la schermata con le misure effettuate dal robot e poi per salvarle
@transaction.commit_manually
@transaction.commit_manually(using='dbhamilton')
@laslogin_required
@login_required
@permission_decorator('tissue.can_view_BBM_revalue_aliquots')
def SaveData(request):    
    try:
        name=request.user.username
        if request.method=='POST':
            print request.POST
            if 'salva' in request.POST:
                dizconc=json.loads(request.POST.get('dizfin'))                
                request.session['dizconcsceltarevaluaterobot']=dizconc
                print 'dizconc',dizconc                
                transaction.commit()
                transaction.commit(using='dbhamilton')
                return HttpResponse()
            #entra qui se l'utente ha cliccato su confirm all e serve per salvare effettivamente le misure nel LAS
            if 'finish' in request.POST:
                if request.session.has_key('dizconcsceltarevaluaterobot'):
                    dizconcscelta=request.session.get('dizconcsceltarevaluaterobot')
                    del request.session['dizconcsceltarevaluaterobot']
                if request.session.has_key('dictmeasurerevaluerobot'):
                    dizmeasure=request.session.get('dictmeasurerevaluerobot')
                    del request.session['dictmeasurerevaluerobot']
                if request.session.has_key('lissamplerevaluerobot'):
                    lisqualsched=request.session.get('lissamplerevaluerobot')
                    del request.session['lissamplerevaluerobot']
                if request.session.has_key('dizpositionrevaluerobot'):
                    dizposition=request.session.get('dizpositionrevaluerobot')
                    del request.session['dizpositionrevaluerobot']
                
                instr=Instrument.objects.get(name='Hamilton')
                print 'dizposition',dizposition
                listareport=[]
                for alqual in lisqualsched:
                    plan=PlanHamilton.objects.get(id=alqual.idPlanRobot)
                    lprotocol=PlanHasProtocolHamilton.objects.filter(plan_id=plan)
                    vol_taken=0.0
                    for p in lprotocol:
                        vol_taken+=p.protocol_id.vol_taken
                    print 'vol_taken',vol_taken
                    lisrun=RunHamilton.objects.filter(plan_id=plan)
                    if len(lisrun)!=0:                        
                        datamisura=lisrun[0].timestamp
                        datam=datetime.date(datamisura.year,datamisura.month,datamisura.day)
                    else:
                        datam=date.today()
                    
                    qualprot=QualityProtocol.objects.get(idAliquotType=alqual.idAliquot.idAliquotType,description='hamilton')
                    #creo il qualityevent
                    print 'qualprot',qualprot
                    qualev=QualityEvent(idQualityProtocol=qualprot,
                                        idQualitySchedule=alqual.idQualitySchedule,
                                        idAliquot=alqual.idAliquot,
                                        misurationDate=datam,
                                        insertionDate=date.today(),
                                        operator=name,
                                        quantityUsed=float(vol_taken))                    
                    qualev.save()
                    print 'qualev',qualev
                    dizmisqual=dizmeasure[alqual.id]
                    print 'dizmisqual',dizmisqual
                    for nome,valore in dizmisqual.items():
                        lmisura=[]
                        if nome.lower().startswith('concentration'):
                            #per fare un'interrogazione che non tenga conto delle maiuscole/minuscole
                            lmisura=Measure.objects.filter(idInstrument=instr,name__iexact=nome)
                        elif nome=='260/230':
                            lmisura=Measure.objects.filter(idInstrument=instr,name='purity',measureUnit='260/230')
                        elif nome=='260/280':
                            lmisura=Measure.objects.filter(idInstrument=instr,name='purity',measureUnit='260/280')
                        if len(lmisura)==0:
                            raise Exception('Measure '+nome+' not recognized')
                        print 'valore',valore
                        evmisur=MeasurementEvent(idMeasure=lmisura[0],
                                                idQualityEvent=qualev,
                                                value=float(valore['value']))
                        evmisur.save()
                    #devo salvare per il campione la nuova conc se c'e'
                    if str(alqual.id) in dizconcscelta:
                        valoreconc=dizconcscelta[str(alqual.id)]['val']
                        print 'valoreconc',valoreconc
                        lfeatconc=Feature.objects.filter(idAliquotType=alqual.idAliquot.idAliquotType,name='Concentration')
                        if len(lfeatconc)!=0:
                            laliqfeat=AliquotFeature.objects.filter(idAliquot=alqual.idAliquot,idFeature=lfeatconc[0])
                            if len(laliqfeat)!=0:
                                aliqfeat=laliqfeat[0]
                                aliqfeat.value=valoreconc
                                aliqfeat.save()
                                print 'alfeat',aliqfeat
                        #solo se e' un'aliquota derivata esterna e quindi non ho inserito la conc all'inizio
                        lfeatorigconc=Feature.objects.filter(idAliquotType=alqual.idAliquot.idAliquotType,name='OriginalConcentration')
                        if len(lfeatorigconc)!=0:
                            laliqorigfeat=AliquotFeature.objects.filter(idAliquot=alqual.idAliquot,idFeature=lfeatorigconc[0])
                            if len(laliqorigfeat)!=0:
                                aliqorigfeat=laliqorigfeat[0]
                                if aliqorigfeat.value==-1:
                                    aliqorigfeat.value=valoreconc
                                    aliqorigfeat.save()
                                    print 'aliqorigfeat',aliqorigfeat
                                    
                    #devo sottrarre dal campione il volume usato per fare la rivalutazione
                    lfeatvol=Feature.objects.filter(idAliquotType=alqual.idAliquot.idAliquotType,name='Volume',measureUnit='ul')
                    if len(lfeatvol)!=0:
                        laliqfeat=AliquotFeature.objects.filter(idAliquot=alqual.idAliquot,idFeature=lfeatvol[0])
                        if len(laliqfeat)!=0:
                            aliqfeat=laliqfeat[0]
                            if aliqfeat.value!=-1:
                                volfin=aliqfeat.value-float(vol_taken)
                                if volfin<0:
                                    volfin=0
                                aliqfeat.value=volfin
                                aliqfeat.save()
                                print 'aliqfeat',aliqfeat
                    
                    valori=dizposition[alqual.idAliquot.uniqueGenealogyID]
                    print 'valori',valori
                    val=valori[0].split('|')
                    barcode=val[1]
                    position=val[2]
                    esaurita='False'
                    stringa=alqual.idAliquot.uniqueGenealogyID+'&'+barcode+'&'+position+'&'+esaurita
                    print 'stringa',stringa
                    listareport.append(stringa)
                    
                    plan.processed=timezone.localtime(timezone.now())
                    plan.save()                    
                print 'listareport',listareport
                lista,intest=LastPartRevaluation(listareport)                
                transaction.commit()
                transaction.commit(using='dbhamilton')
                variables = RequestContext(request,{'fine':True,'lista_riv':lista,'intest':intest})
                return render_to_response('tissue2/revalue_robot/save_data.html',variables)
        else:
            #chiave l'idalqualsched e valore un dizionario con le misure trovate
            dizmisure={}
            #devo prendere i protocolli per le misure, quindi quelli di tipo uv e fluo
            lisprotype=ProtocolTypeHamilton.objects.filter(name__in=['fluo','uv']).values_list('id',flat=True)
            lisprot=ProtocolHamilton.objects.filter(protocol_type_id__in=lisprotype).values_list('id',flat=True)
            print 'lisprot',lisprot
            lisplanprot=PlanHasProtocolHamilton.objects.filter(protocol_id__in=lisprot).values_list('plan_id',flat=True)
            listapiani=PlanHamilton.objects.filter(operator=name,id__in=lisplanprot,executed__isnull=False,processed__isnull=True)
            lisplanfin=[]            
            for p in listapiani:
                lisplanfin.append(p.id)            
            lisqualsched=AliquotQualitySchedule.objects.filter(idPlanRobot__in=lisplanfin).order_by('validationTimestamp')
            print 'lisqualsched',lisqualsched
            stringat=''
            #lista con i nomi delle misure
            lisnomimisure=[]
            diznomimisure={}
            for qual in lisqualsched:
                gen=qual.idAliquot.uniqueGenealogyID
                samp=SampleHamilton.objects.filter(genid=gen,plan_id__in=lisplanfin)
                #devo usare due dizionari perche' non riesco a fare il json del timestamp della misura
                dizmis={}                
                dizdef={}
                lismis=MeasureHamilton.objects.filter(sample_id=samp[0])
                print 'lismis',lismis
                for mis in lismis:
                    nome=mis.name                    
                    if nome in dizmis:
                        diztemp=dizmis[nome]
                        version=diztemp['version']
                        time=diztemp['time']
                        print 'time',time                            
                        print 'version',version
                        print 'mis version',mis.version
                        #devo prendere l'ultima misura, quindi quella con la versione maggiore oppure quella piu' recente cioe' con il timestamp
                        #maggiore. Facendo cosi' potrei prendere la nuova versione pero' di una misura fatta prima di un'altra e quindi non l'ultima
                        #in ordine di tempo. Ma va bene cosi'
                        if mis.run_id.timestamp>time or mis.version>version:
                            diztemp['value']=mis.value
                            diztemp['version']=mis.version
                            diztemp['time']=mis.run_id.timestamp
                            dizdef[nome]={'value':mis.value}
                        dizmis[nome]=diztemp                        
                    else:                        
                        diztemp={}
                        diztemp['value']=mis.value
                        diztemp['version']=mis.version
                        diztemp['time']=mis.run_id.timestamp
                        dizmis[nome]=diztemp
                        dizdef[nome]={'value':mis.value}
                #una volta trovata la misura piu' recente, scandisco il dizionario per vedere se quella misura e' un numero. Se non lo e' la cancello
                for nomemis,diz in dizdef.items():
                    try:
                        float(diz['value'])
                    except:
                        #se non e' un numero elimino la misura
                        del dizdef[nomemis]
                        continue
                    diz['value']=round(float(diz['value']),3)
                    if str(nomemis) not in lisnomimisure:
                        lisnomimisure.append(str(nomemis))
                print 'dizdefdopo',dizdef
                stringat+=gen+'&'
                dizmisure[qual.id]=dizdef
            print 'dizmisure',dizmisure
            lisnomimisure=sorted(lisnomimisure,key=str.lower)
            print 'lisnomimisure',lisnomimisure
            i=1
            for mis in lisnomimisure:
                diznomimisure[mis]=i
                i+=1
            stringtotale=stringat[:-1]
            dizpos=AllAliquotsContainer(stringtotale)
            lisbarc=[]
            lispos=[]            
            
            for al in lisqualsched:
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
            
            request.session['dictmeasurerevaluerobot']=dizmisure
            request.session['lissamplerevaluerobot']=lisqualsched
            request.session['dizpositionrevaluerobot']=dizpos
            transaction.commit()
            transaction.commit(using='dbhamilton')
            #per far comparire la schermata iniziale
            variables = RequestContext(request,{'lista':zip(list(lisqualsched),lisbarc,lispos),'dizmisure':json.dumps(dizmisure),'diznomimisure':json.dumps(diznomimisure),'lisnomimisure':lisnomimisure})
            return render_to_response('tissue2/revalue_robot/save_data.html',variables)
    except Exception,e:
        print 'error',e
        transaction.rollback()
        transaction.rollback(using='dbhamilton')
        variables = RequestContext(request, {'errore':True})
        return render_to_response('tissue2/index.html',variables)

