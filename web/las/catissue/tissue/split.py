from __init__ import *
from catissue.tissue.utils import *

@laslogin_required
@login_required
def SplitAliquotsView(request):
    da_dividere=[]
    request.session['dividere']=da_dividere
    variables = RequestContext(request)   
    return render_to_response('tissue2/split/start.html',variables)

@transaction.commit_on_success
@laslogin_required
@login_required
#@user_passes_test(lambda u: u.has_perm('tissue.can_view_plan_aliquots_to_split'),login_url=settings.BASE_URL+'/tissue/error/')
@permission_decorator('tissue.can_view_BBM_plan_aliquots_to_split')
def InsertSplitAliquots(request):
    if request.session.has_key('dividere'):
        da_dividere=request.session.get('dividere')
    else:
        da_dividere=[]
    if request.method=='POST':
        print request.POST
        print request.FILES  
        try:          
            if 'salva' in request.POST:
                listaaliq=json.loads(request.POST.get('dati'))
                lisgen=[]
                if len(listaaliq)!=0:
                    for val in listaaliq:
                        print 'val',val
                        listemp=[]
                        listemp.append(val)
                        if listemp not in lisgen:
                            lisgen.append(listemp)
                print 'lis da dividere',lisgen
                request.session['dividere']=lisgen
                return HttpResponse()
            #ho cliccato sul tasto 'add file'
            if 'aggiungi_file' in request.POST:
                lisaliq=[]
                lisbarc=[]
                lispos=[]

                if 'file' in request.FILES:
                    print 'da dividere',da_dividere
                    for lis in da_dividere:
                        print 'lis',lis
                        for val in lis:
                            print 'val',val
                            ch=val.split('|')
                            lisaliq.append(ch[0])
                            lisbarc.append(ch[1])
                            lispos.append(ch[2])
                    
                    f=request.FILES['file']
                    linee=f.readlines()
                    stringalinee=''
                    for i in range(0,len(linee)):
                        c=linee[i]
                        #c e' la singola riga del file
                        #il .strip toglie gli eventuali spazi e il \r finale nella riga
                        c=c.strip()
                        print 'c',c
                        if c!='':
                            stringalinee+=c+'&'
                    stringtot=stringalinee[:-1]     
                    diz=AllAliquotsContainer(stringtot)
                    
                    for gen in diz:
                        lista=diz[gen]
                        if len(lista)==0:
                            raise ErrorRevalue('Error: aliquot '+gen+' does not exist in storage')
                        else:
                            if lista not in da_dividere:                                
                                #e' una lista in cui ogni valore e' una stringa formata da gen|barcode|posizione
                                for val in lista:
                                    ch=val.split('|')
                                    lisaliq.append(ch[0])
                                    lisbarc.append(ch[1])
                                    lispos.append(ch[2])
                                    
                                    #per controllare se l'aliquota e' di questo wg
                                    lisali=Aliquot.objects.filter(uniqueGenealogyID=ch[0],availability=1)
                                    if len(lisali)==0:
                                        raise ErrorDerived('Error: aliquot '+gen+' does not exist in storage')
                                    else:
                                        al=lisali[0]
                                                                            
                                    print 'al',al
                                    #guardo se l'aliquota e' un derivato
                                    if al.derived==0:
                                        raise ErrorRevalue('Error: aliquot '+gen+' is not derived')
                                    
                                    #vedo se l'aliquota e' gia' stata programmata per la divisione
                                    alsplisched=AliquotSplitSchedule.objects.filter(idAliquot=al,splitExecuted=0,deleteTimestamp=None)
                                    print 'alqual',alsplisched
                                    if(alsplisched.count()!=0):
                                        raise ErrorRevalue('Error: aliquot '+gen+' is already scheduled for splitting')
                                    
                                da_dividere.append(lista)
                    print 'split',da_dividere
                    #request.session['rivalutare']=da_rivalutare
                    variables = RequestContext(request,{'rivalutare':zip(lisaliq,lisbarc,lispos)})
                    return render_to_response('tissue2/split/split.html',variables)
            
            if 'conferma' in request.POST:
                print 'da dividere',da_dividere
                name=request.user.username
                lisaliq=[]
                lisbarc=[]
                lispos=[]
                
                #salvo lo splitsched per lo split
                schedule=SplitSchedule(scheduleDate=date.today(),
                                         operator=name)
                schedule.save()
                for lis in da_dividere:
                    for valori in lis:
                        val=valori.split('|')
                        gen=val[0]
                        barc=val[1]
                        pos=val[2]
                        a=Aliquot.objects.get(availability=1,uniqueGenealogyID=gen)
                        #creo l'oggetto e metto a 0 i campi che non mi servono in questo momento
                        rev_aliq=AliquotSplitSchedule(idAliquot=a,
                                                        idSplitSchedule=schedule,
                                                        splitExecuted=0
                                                        )
                        rev_aliq.save()
                        lisaliq.append(gen)
                        lisbarc.append(barc)
                        lispos.append(pos)
                variables = RequestContext(request,{'fine':True,'rivalutare':zip(lisaliq,lisbarc,lispos)})
                return render_to_response('tissue2/split/split.html',variables)
            
        except ErrorRevalue as e:
            print 'My exception occurred, value:', e.value
            variables = RequestContext(request, {'errore':e.value})
            return render_to_response('tissue2/split/split.html',variables)
        except:
            print 'err',e
            transaction.rollback()
            errore=True
            variables = RequestContext(request, {'errore':errore})
            return render_to_response('tissue2/index.html',variables)

    variables = RequestContext(request, {'rivalutare':da_dividere})
    return render_to_response('tissue2/split/split.html',variables)

#per cancellare gli split pianificati
@transaction.commit_on_success
@laslogin_required
@login_required
#@user_passes_test(lambda u: u.has_perm('tissue.can_view_split_aliquots'),login_url=settings.BASE_URL+'/tissue/error/')
@permission_decorator('tissue.can_view_BBM_split_aliquots')
def CancSplitAliquots(request):
    try:
        name=request.user.username
        print request.POST
        if request.method=='POST':
            if 'salva' in request.POST:
                operatore=User.objects.get(username=name)
                listasplit=[]
                listaaliq=json.loads(request.POST.get('dati'))
                print 'listaaliq',listaaliq
                for gen in listaaliq:
                    aliq=Aliquot.objects.get(uniqueGenealogyID=gen)
                    listasplisched=AliquotSplitSchedule.objects.filter(idAliquot=aliq,splitExecuted=0,idSamplingEvent=None,deleteTimestamp=None)
                    if len(listasplisched)!=0:
                        splisched=listasplisched[0]
                        #splisched.deleteTimestamp= datetime.datetime.now()
                        splisched.deleteTimestamp= timezone.localtime(timezone.now())
                        splisched.deleteOperator=operatore
                        splisched.save()
                        listasplit.append(splisched)
                print 'listasplit',listasplit
                request.session['listasplit_canc']=listasplit
                return HttpResponse()
            if 'final' in request.POST:
                lista=[]
                laliq=[]
                listar=request.session.get('listasplit_canc')
                print 'listar',listar
                lgen=''
                for val in listar:
                    lgen+=val.idAliquot.uniqueGenealogyID+'&'
                    laliq.append(val.idAliquot.uniqueGenealogyID)
                lgenfin=lgen[:-1]
                diz=AllAliquotsContainer(lgenfin)
                print 'dizio',diz
                for i in range(0,len(listar)):
                    revsch=listar[i]
                    dat=revsch.idSplitSchedule.scheduleDate
                    print 'dat',dat
                    data2=str(dat).split('-')
                    d=data2[2]+'-'+data2[1]+'-'+data2[0]
                    print 'd',d
                    valori=diz[revsch.idAliquot.uniqueGenealogyID]
                    val=valori[0].split('|')
                    barc=val[1]
                    pos=val[2]
                    
                    '''assegnatario=User.objects.get(username=revsch.idSplitSchedule.operator)
                    #creo un dizionario con dentro come chiave il nome del supervisore e come valore una lista con le procedure che lo
                    #riguardano
                    if assegnatario.email !='' and assegnatario.username!=name:
                        diztemp={}
                        diztemp['gen']=revsch.idAliquot.uniqueGenealogyID
                        diztemp['barc']=barc
                        diztemp['pos']=pos
                        diztemp['dat']=dat
                        if dizsupervisori.has_key(assegnatario.email):
                            listatemp=dizsupervisori[assegnatario.email]
                            listatemp.append(diztemp)
                        else:
                            listatemp=[]
                            listatemp.append(diztemp)
                        dizsupervisori[assegnatario.email]=listatemp'''
                        
                    lista.append(ReportScheduleCancToHtml(i+1,revsch.idAliquot.uniqueGenealogyID,barc,pos,revsch.idSplitSchedule.operator,d,'n'))
                print 'lista',lista
                
                InviaMail('Split',name,laliq,listar,diz)
                
                variables = RequestContext(request,{'lista_sch':lista})
                return render_to_response('tissue2/revalue/cancel.html',variables)
    except Exception,e:
        print 'err',e
        transaction.rollback()
        errore=True
        variables = RequestContext(request, {'errore':errore})
        return render_to_response('tissue2/index.html',variables)

#per far comparire la prima pagina delle aliquote da dividere
@laslogin_required
@login_required
#@user_passes_test(lambda u: u.has_perm('tissue.can_view_split_aliquots'),login_url=settings.BASE_URL+'/tissue/error/')
@permission_decorator('tissue.can_view_BBM_split_aliquots')
def ExecSplitAliquots(request):
    lista_aliq=[]
    request.session['aliqdividere']=[]
    request.session['listaaliqdividere']=[]
    
    lista=AliquotSplitSchedule.objects.filter(splitExecuted=0,deleteTimestamp=None)
    for l in lista:
        lista_aliq.append(l)
    print 'lista',lista_aliq
    robot='False'
    if 'robotsplitload' in request.session:
        print 'robot'
        del request.session['robotsplitload']
        robot='True'    
    variables = RequestContext(request,{'lista':lista_aliq,'tipo':'split','robot':robot})
    return render_to_response('tissue2/split/execute.html',variables)

#per mettere aliquote nella lista effettiva delle divisioni di oggi
@laslogin_required
@login_required
@permission_decorator('tissue.can_view_BBM_split_aliquots')
def ExecEffectiveSplitAliquots(request):
    try:
        if request.method=='POST':
            if 'salva' in request.POST:
                listagen=json.loads(request.POST.get('lgen'))
                print 'listagen',listagen
                request.session['listaaliqdividere']=listagen
                return HttpResponse()
            if 'conferma' in request.POST:
                lisfin=[]
                adesso=timezone.localtime(timezone.now())
                #metto i secondi a zero in modo di partire dal minuto preciso. Poi ad ogni convalida aggiungo un secondo
                adesso=adesso.replace(second=0, microsecond=0)
                print 'adesso',adesso
                
                listagen=request.session.get('listaaliqdividere')
                lisaliq=Aliquot.objects.filter(uniqueGenealogyID__in=listagen,availability=1)
                print 'lisaliq',lisaliq
                lisqual=AliquotSplitSchedule.objects.filter(idAliquot__in=lisaliq,splitExecuted=0,deleteTimestamp=None)
                lgen=[]
                strgen=''
                for qual in lisqual:
                    lgen.append(qual.idAliquot.uniqueGenealogyID)
                    strgen+=qual.idAliquot.uniqueGenealogyID+'&'
                    print 'aliquota_split',qual.idAliquot
                i=0
                #devo ordinare la lista degli aliquot split sched in base a come sono state convalidate le aliquote
                for gen in listagen:
                    for qual in lisqual:
                        if qual.idAliquot.uniqueGenealogyID==gen:
                            lisfin.append(qual)
                            tempovalidaz=adesso+timezone.timedelta(seconds=i)                    
                            qual.validationTimestamp=tempovalidaz
                            qual.save()
                            i+=1
                                                
                url1 = Urls.objects.get(default = '1').url + "/container/availability/"
                val1={'lista':json.dumps(lgen),'tube':'0','nome':request.user.username}

                print 'url1',url1
                data = urllib.urlencode(val1)
                req = urllib2.Request(url1,data=data, headers={"workingGroups" : get_WG_string()})
                u = urllib2.urlopen(req)
                res1 =  u.read()
                print 'res',res1
                if res1=='err':
                    variables = RequestContext(request, {'errore':True})
                    return render_to_response('tissue2/index.html',variables)
                                                
                lgenfin=strgen[:-1]
                diz=AllAliquotsContainer(lgenfin)
                
                aliq=lisfin[0].idAliquot
                valori=diz[aliq.uniqueGenealogyID]
                val=valori[0].split('|')
                barc=val[1]
                pos=val[2]
                print 'barc',barc
                print 'pos',pos
                
                lisaliquote=[]
                lisbarc=[]
                lispos=[]
                for split in lisfin:
                    valori=diz[split.idAliquot.uniqueGenealogyID]
                    val=valori[0].split('|')
                    barcode=val[1]
                    position=val[2]
                    lisaliquote.append(split)
                    lisbarc.append(barcode)
                    lispos.append(position)
                
                if 'robot' in request.POST:
                    print 'robot'
                    request.session['aliqSplitPlanDilutionRobot']=lisfin
                    #chiave l'idsplitschedule e valore un dizionario con volumi e concentrazioni presenti
                    dizmisure={}
                    for split in lisfin:
                        vol=''
                        conc=''
                        #prendo la feature del volume
                        lfeatvol=Feature.objects.filter(idAliquotType=split.idAliquot.idAliquotType,name='Volume')
                        if len(lfeatvol)!=0:
                            #prendo il volume effettivo
                            lvol=AliquotFeature.objects.filter(idAliquot=split.idAliquot,idFeature=lfeatvol[0])
                            if len(lvol)!=0:
                                vol=lvol[0].value
                                if vol==-1:
                                    vol=''
                        #prendo la feature della concentrazione
                        lfeatconc=Feature.objects.filter(idAliquotType=split.idAliquot.idAliquotType,name='Concentration')
                        if len(lfeatconc)!=0:
                            #prendo la conc effettiva
                            lconc=AliquotFeature.objects.filter(idAliquot=split.idAliquot,idFeature=lfeatconc[0])
                            if len(lconc)!=0:
                                conc=lconc[0].value
                                if conc==-1:
                                    conc=''
                        dizmisure[split.id]={'vol':vol,'conc':conc}
                    print 'dizmisure',dizmisure
                    #prendo i tipi di container
                    lislabware=LabwareTypeHamilton.objects.all()
                    variables = RequestContext(request,{'lista':zip(lisfin,lisbarc,lispos),'liscont':lislabware,'dizmisure':json.dumps(dizmisure)})
                    return render_to_response('tissue2/split_robot/set_procedure.html',variables)
                else:
                    request.session['dictaliqdivise']={}
                    a=SchemiPiastre()                    
                    vol=0.0
                    conc=0.0
                    #prendo la feature del volume
                    lfeatvol=Feature.objects.filter(idAliquotType=aliq.idAliquotType.id,name='Volume')
                    if len(lfeatvol)!=0:
                        #prendo il volume effettivo
                        lvol=AliquotFeature.objects.filter(idAliquot=aliq.id,idFeature=lfeatvol[0])
                        if len(lvol)!=0:
                            vol=lvol[0].value
                    #prendo la feature della concentrazione
                    lfeatconc=Feature.objects.filter(idAliquotType=aliq.idAliquotType.id,name='Concentration')
                    if len(lfeatconc)!=0:
                        #prendo la conc effettiva
                        lconc=AliquotFeature.objects.filter(idAliquot=aliq.id,idFeature=lfeatconc[0])
                        if len(lconc)!=0:
                            conc=lconc[0].value
                    tipo=aliq.idAliquotType.abbreviation
                    request.session['indice_dividere']=0
                    request.session['listapiastredivisionealiq']=[]
                    request.session['dizinfoaliqsplit']=diz
                    print 'tipo',tipo
                    #apro il file con dentro i parametri per la derivazione
                    percorso=os.path.join(os.path.dirname(__file__),'tissue_media/File_Format/Regole_aliq_derivate.txt')
                    print 'perc',percorso
                    f=open(percorso)
                    lines = f.readlines()
                    f.close()
                    riga=''
                
                    for line in lines:
                        valori=line.split(';')
                        #se ho trovato la riga giusta che inizia con il nome del derivato
                        if valori[0]==tipo:
                            riga+=valori[1]+';'+valori[2]+';'+valori[3].strip()
                            break
                    print 'riga',riga
                    request.session['aliqdividere']=lisfin
                    variables = RequestContext(request,{'aliquota':aliq,'barcode':barc,'position':pos,'a':a,'vol':str(vol),'conc':str(conc),'tipo':tipo,'indice':1,'lista_divid':zip(lisaliquote,lisbarc,lispos),'riga':riga,'tot_aliq':'0'})
                    return render_to_response('tissue2/split/end_split.html',variables)
    except Exception,e:
        print 'err',e
        variables = RequestContext(request, {'errore':True})
        return render_to_response('tissue2/index.html',variables)

#viene chiamata per ogni aliquota presente nella lista delle aliquote da dividere
@transaction.commit_on_success
@laslogin_required
@login_required
#@user_passes_test(lambda u: u.has_perm('tissue.can_view_split_aliquots'),login_url=settings.BASE_URL+'/tissue/error/')
@permission_decorator('tissue.can_view_BBM_split_aliquots')
def LastPartSplitAliquots(request):
    lista_al_divi=[]
    if request.session.has_key('aliqdividere'):
        aliq_da_dividere=request.session.get('aliqdividere')
    if request.session.has_key('indice_dividere'):
        ind=request.session.get('indice_dividere')
    if request.session.has_key('lista_aliquote_divid'):
        lista_al_divi=request.session.get('lista_aliquote_divid') 
    if request.session.has_key('listaValAliqSplit'):
        lista_val_aliq_split=request.session.get('listaValAliqSplit')
    else:
        lista_val_aliq_split=[]
    if request.session.has_key('dictaliqdivise'):
        dictnum=request.session.get('dictaliqdivise')
    if request.session.has_key('dizinfoaliqsplit'):
        dizinfo=request.session.get('dizinfoaliqsplit')
    else:
        strgen=''
        for qual in aliq_da_dividere:
            strgen+=qual.idAliquot.uniqueGenealogyID+'&'
        
        lgenfin=strgen[:-1]
        dizinfo=AllAliquotsContainer(lgenfin)
        request.session['dizinfoaliqsplit']=dizinfo
    if request.method=='POST':
        print request.POST
        try:         
            #con javascript faccio una post che mi fa scattare questo if. Salvo i dati nella sessione
            #per poi riprenderli dopo quando clicco su confirm all
            if 'posizione' in request.POST:
                #posiznuova=request.POST.get('posnuova')
                #num=request.POST.get('numero')
                #piastradest=request.POST.get('barcodedest')
                dictnum=json.loads(request.POST.get('diz'))
                request.session['dictaliqdivise']=dictnum
                print 'dictnum divi',dictnum["1"]
                return HttpResponse()
            #entra qui se l'utente ha cliccato su confirm all
            if 'conf' in request.POST or 'finish' in request.POST:
                contatore=0
                listabarc=[]
                listatipialiq=[]
                lisbarclashub=[]
                listaaliqstorage=[]
                
                #prendo il numero di aliquote che ho creato
                num_aliq=request.POST.get('aliquots')
                gen=request.POST.get('gen')
                listaaliq=Aliquot.objects.filter(Q(uniqueGenealogyID=gen)&Q(availability=1))
                #prendo l'aliquota madre
                if listaaliq.count()!=0:
                    aliq=listaaliq[0]
                
                #per trovare il tipo di derivato che ottengo
                tipo=request.POST.get('protocollo')
                print 'tipo',tipo
                ge = GenealogyID(gen)
                fine=''
                #mi restituisce la lunghezza della parte destinata alla seconda derivazione
                for p in range(0,ge.getLen2Derivation()):
                    fine+='0'
                #fine='000'
                if tipo=='DNA' or tipo=='RNA':
                    #prendo l'inizio dell'aliquota che sto dividendo
                    #e' un derivato quindi prendo tutti i caratteri fino alla fine dei 10 zeri
                    #piu' il carattere che indica se e' RNA o DNA
                    stringa=ge.getPartForDerAliq()+ge.getArchivedMaterial()
                    #stringa=gen[0:21]
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
                
                #salvo che la divisione e' stata eseguita
                #prendo lo split schedule
                alsplit=AliquotSplitSchedule.objects.get(idAliquot=aliq,splitExecuted=0,deleteTimestamp=None)
                alsplit.splitExecuted=1
                alsplit.operator=request.user
                print 'alsplit',alsplit
                
                #Devo diminuire il valore del volume per la madre
                #Il volume prelevato per creare le figlie
                derived_tipo=AliquotType.objects.get(abbreviation=aliq.idAliquotType.abbreviation)
                #prendo la feature del volume
                featvol=Feature.objects.get(Q(idAliquotType=derived_tipo)&Q(name='Volume'))
                #prendo il valore del volume per l'aliquota madre
                valore=AliquotFeature.objects.get(Q(idAliquot=aliq)&Q(idFeature=featvol))

                vol_madre_attuale=request.POST.get('vol_madre')
                valore.value=float(vol_madre_attuale)
                valore.save()                                
                    
                tumore=ge.getOrigin()
                #tumore=gen[0:3]
                print 'tumore',tumore
                caso=ge.getCaseCode()
                #caso=gen[3:7]
                print 'caso',caso
                tipotum=CollectionType.objects.get(abbreviation=tumore)
                #prendo la collezione da associare al sampling event
                colle=Collection.objects.get(Q(itemCode=caso)&Q(idCollectionType=tipotum))
                print 'colle',colle
                #salvo la serie
                ser,creato=Serie.objects.get_or_create(operator=request.user.username,
                                                       serieDate=date.today())
                #prendo la sorgente dalla tabella source
                sorg=Source.objects.get(id=colle.idSource.id)
                print 'sorg',sorg
                t=ge.getTissue()
                #t=gen[7:9]
                tess=TissueType.objects.get(abbreviation=t)
                #salvo il campionamento
                campionamento=SamplingEvent(idTissueType=tess,
                                             idCollection=colle,
                                             idSource=sorg,
                                             idSerie=ser,
                                             samplingDate=date.today())
                campionamento.save()
                print 'camp',campionamento
                
                #assegno allo split schedule il campionamento appena creato
                alsplit.idSamplingEvent=campionamento
                alsplit.save()
                
                name=request.user.username
                request.session['data_split']=date.today()
                request.session['operatore_split']=name
                
                derived_tipo=AliquotType.objects.get(abbreviation=tipo)
                #prendo la feature del volume
                featvol=Feature.objects.get(Q(idAliquotType=derived_tipo)&Q(name='Volume'))
                #prendo la feature della concentrazione
                featconc=Feature.objects.get(Q(idAliquotType=derived_tipo)&Q(name='Concentration'))
                print 'num',num_aliq
                piastra=-1
                data=""
                lista_conc=[]
                lista_vol=[]
                for i in range(0,int(num_aliq)):
                    #preparo i nomi con cui accedere alla request.post
                    vol='volume_'+str(i)
                    conc='conc_'+str(i)
                    vol_mad='vol_madre_'+str(i)
                    acq='acqua_'+str(i)
                    v=request.POST.get(vol)
                    c=request.POST.get(conc)
                    vol_madre=request.POST.get(vol_mad)
                    acqua=request.POST.get(acq)
                    lista_vol.append(v)
                    lista_conc.append(c)
                    vo=float(v)
                    co=float(c)
                    
                    #solo se volume e concentrazione sono diversi da zero creo l'aliquota
                    if vo!=0.0 and co!=0.0:
                        barcode=None
                        contatore=contatore+1
                        if contatore<10:
                            num_ordine='0'+str(contatore)
                        else:
                            num_ordine=str(contatore)
                        
                        if tipo=='DNA' or tipo=='RNA':
                            diz_dati={'aliqExtraction1':num_ordine,'2derivation':'0','2derivationGen':'00'}  
                            ge.updateGenID(diz_dati)
                            nuovo_gen=ge.getGenID()  
                            #nuovo_gen=gen[0:20]+num_ordine+'000'    
                        elif tipo=='cDNA' or tipo=='cRNA':
                            diz_dati={'2derivationGen':num_ordine}  
                            ge.updateGenID(diz_dati)
                            nuovo_gen=ge.getGenID()
                            #nuovo_gen=gen[0:23]+num_ordine
                        
                        #prendo il valore della piastra
                        dizionario=dictnum[str(i+1)]
                        #in diz[0] ho la posizione, in diz[1] ho la piastra
                        diz=dizionario.split('|')
                        print 'diz',diz
                        if(diz[1]!=piastra):
                            piastra=diz[1]
                            barcodepiastraurl=piastra.replace('#','%23')
                            #per ottenere il barcode data la posizione   
                            #mi collego all'archivio per avere i barcode dato il numero di piastra
                            url = Urls.objects.get(default = '1').url + "/api/container/"+barcodepiastraurl
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
                                transaction.rollback()
                                print e
                                errore=True
                                variables = RequestContext(request, {'errore':errore})
                                return render_to_response('tissue2/index.html',variables) 
                        #se la API mi restituisce dei valori perche' gli ho dato un codice
                        #corretto per la piastra    
                        if 'children' in data:
                            posizi=diz[0]
                            for w in data['children']:
                                #in p[i] ho la posizione
                                if w['position']==diz[0]:
                                    barcode=w['barcode']
                                    print 'barc',barcode
                                    break;
                            ffpe='false'
                        else:
                            #vuol dire che sto salvando una nuova provetta e quindi il barcode 
                            #risulta essere cio' che e' salvato nella variabile piastra
                            posizi=''
                            barcode=piastra
                            piastra=''
                            lisbarclashub.append(barcode)
                            ffpe='true'
    
                        al_der=Aliquot(barcodeID=barcode,
                                      uniqueGenealogyID=nuovo_gen,
                                      idSamplingEvent=campionamento,
                                      idAliquotType=derived_tipo,
                                      availability=1,
                                      timesUsed=0,
                                      derived=1)
                        al_der.save()
                        
                        lista_al_divi.append(al_der)
                        
                        listabarc.append(barcode+','+nuovo_gen)
                        listatipialiq.append(derived_tipo.abbreviation)
                        
                        #prendo la feature del volume originale
                        featorigvol=Feature.objects.get(Q(idAliquotType=derived_tipo)&Q(name='OriginalVolume'))
                        #prendo la feature della concentrazione originale
                        featorigconc=Feature.objects.get(Q(idAliquotType=derived_tipo)&Q(name='OriginalConcentration'))
                        #salvo il volume
                        aliqfeaturevol=AliquotFeature(idAliquot=al_der,
                                           idFeature=featvol,
                                           value=vo)
                        aliqfeaturevol.save()
                        
                        #salvo il volume originale
                        aliqfeatureorigvol=AliquotFeature(idAliquot=al_der,
                                           idFeature=featorigvol,
                                           value=vo)
                        aliqfeatureorigvol.save()
                        #salvo la concentrazione
                        aliqfeaturecon=AliquotFeature(idAliquot=al_der,
                                           idFeature=featconc,
                                           value=co)
                        aliqfeaturecon.save()
                        print 'aliq',aliqfeaturecon
                        #salvo la concentrazione originale
                        aliqfeatureorigcon=AliquotFeature(idAliquot=al_der,
                                           idFeature=featorigconc,
                                           value=co)
                        aliqfeatureorigcon.save()
                        
                        valor=dizinfo[aliq.uniqueGenealogyID]
                        val=valor[0].split('|')
                        barcmadre=val[1]
                        posmadre=val[2]
                        print 'barc',barcmadre
                        print 'pos',posmadre
                        #stringa per visualizzare poi la tabella riepilogativa finale
                        #diz[1] e' la piastra, diz[0] e' la posizione
                        stringa=nuovo_gen+'&'+barcode+'&'+piastra+'&'+posizi+'&'+str(co)+'&'+str(vo)+'&'+str(vol_madre)+'&'+str(acqua)+'&'+aliq.uniqueGenealogyID+'&'+barcmadre+'&'+posmadre
                        lista_val_aliq_split.append(stringa)
                        valori=nuovo_gen+','+str(piastra)+',,,'+barcode+','+derived_tipo.abbreviation+','+ffpe+',,,,,,'+str(date.today())
                        listaaliqstorage.append(valori)
                        request.session['listaValAliqSplit']=lista_val_aliq_split
                #per fare in modo che le provette utilizzate vengano impostate nello
                #storage come piene
                request,errore=SalvaInStorage(listaaliqstorage,request)
                print 'err', errore   
                if errore==True:
                    transaction.rollback()
                    variables = RequestContext(request, {'errore':errore})
                    return render_to_response('tissue2/index.html',variables)
                
                if len(lisbarclashub)!=0:
                    #prefisso= 'https://' if settings.LAS_AUTH_USE_HTTPS else 'http://'
                    #address=request.get_host()+settings.HOST_URL
                    #indir=prefisso+address
                    indir=settings.DOMAIN_URL+settings.HOST_URL
                    url = indir + '/clientHUB/saveAndFinalize/'
                    print 'url',url
                    values2 = {'typeO' : 'container', 'listO': str(lisbarclashub)}
                    requests.post(url, data=values2, verify=False, headers={"workingGroups" : get_WG_string()})
    
                request.session['lista_aliquote_divid']=lista_al_divi    
                lista_al_da_div=request.session.get('aliqdividere')
                lista_al_da_div[ind].splitExecuted=1
                lista_al_da_div[ind].operator=request.user
                lista_al_da_div[ind].idSamplingEvent=campionamento
                request.session['aliqdividere']=lista_al_da_div
                
                ind=ind+1
                request.session['indice_dividere']=ind
                
                #vedo se la madre e' finita
                if 'exhausted' in request.POST:
                    aliq.availability=0
                    aliq.save()
                    #mi collego allo storage per svuotare le provette contenenti le aliq
                    #esaurite
                    address=Urls.objects.get(default=1).url
                    url = address+"/full/"
                    print url
                    values = {'lista' : json.dumps([aliq.uniqueGenealogyID]), 'tube': 'empty','canc':True,'operator':name}
                    data = urllib.urlencode(values)
                    req = urllib2.Request(url,data=data, headers={"workingGroups" : get_WG_string()})
                    urllib2.urlopen(req)
                    
                    #request.session['listaAliqSplitTerminate']=lista_aliq_split_term
                 
                if ind<len(aliq_da_dividere) and 'finish' not in request.POST:
                    #mi occupo delle piastre
                    #prendo le piastre caricate dall'utente
                    listapias=request.session.get('listapiastredivisionealiq')
                    numpianuove=request.POST.get('numnuovepiastre')
                    print 'num',numpianuove
                    #preparo i nomi con cui accedere alla post
                    cod='piastra_'
                    piastipo='tipopiastra_'
                    for i in range(0,int(numpianuove)):
                        codpiastra=cod+str(i)
                        piastratipo=piastipo+str(i)
                        codpias=request.POST.get(codpiastra)
                        piastratip=request.POST.get(piastratipo)
                        print 'c',codpias
                        print 'p',piastratip
                        valore=codpias+' '+piastratip
                        print 'valore',valore
                        listapias.append(valore)
                    request.session['listapiastredivisionealiq']=listapias
                    #per trovare il tipo dell'aliq successiva
                    tip=aliq_da_dividere[ind].idAliquot.idAliquotType.abbreviation
                    print 'tip',tip
                    aliq=aliq_da_dividere[ind].idAliquot
                    
                    #apro il file con dentro i parametri per la derivazione
                    percorso=os.path.join(os.path.dirname(__file__),'tissue_media/File_Format/Regole_aliq_derivate.txt')
                    print 'perc',percorso
                    f=open(percorso)
                    lines = f.readlines()
                    f.close()                    
                        
                    valori=dizinfo[aliq.uniqueGenealogyID]
                    val=valori[0].split('|')
                    barc=val[1]
                    pos=val[2]
                    print 'barc',barc
                    print 'pos',pos
                    
                    lisaliquote=[]
                    lisbarc=[]
                    lispos=[]
                    for split in aliq_da_dividere:
                        valori=dizinfo[split.idAliquot.uniqueGenealogyID]
                        val=valori[0].split('|')
                        barcode=val[1]
                        pos=val[2]
                        lisaliquote.append(split)
                        lisbarc.append(barcode)
                        lispos.append(pos)
                    
                    riga=''                
                    for line in lines:
                        valori=line.split(';')
                        #se ho trovato la riga giusta che inizia con il nome del derivato
                        if valori[0]==tip:
                            riga+=valori[1]+';'+valori[2]+';'+valori[3].strip()
                            break
                    print 'riga',riga
                    
                    a=Collection()
                    
                    v=0.0
                    c=0.0
                    #prendo la feature del volume
                    lfeatvol=Feature.objects.filter(Q(idAliquotType=aliq.idAliquotType.id)&Q(name='Volume'))
                    if len(lfeatvol)!=0:
                        #prendo il volume effettivo
                        lvol=AliquotFeature.objects.filter(Q(idAliquot=aliq.id)&Q(idFeature=lfeatvol[0]))
                        if len(lvol)!=0:
                            v=lvol[0].value
                    #prendo la feature della concentrazione
                    lfeatconc=Feature.objects.filter(Q(idAliquotType=aliq.idAliquotType.id)&Q(name='Concentration'))
                    if len(lfeatconc)!=0:
                        #prendo la conc effettiva
                        lconc=AliquotFeature.objects.filter(Q(idAliquot=aliq.id)&Q(idFeature=lfeatconc[0]))
                        if len(lconc)!=0:
                            c=lconc[0].value
                                                                                        
                    print 'listapias',listapias
                    variables = RequestContext(request,{'aliquota':aliq,'barcode':barc,'position':pos,'a':a,'vol':v,'conc':c,'tipo':tip,'listapiastre':listapias,'indice':(ind+1),'lista_divid':zip(lisaliquote,lisbarc,lispos),'riga':riga,'lista_conc_vol':zip(lista_vol,lista_conc),'tot_aliq':num_aliq})
                    return render_to_response('tissue2/split/end_split.html',variables)
                else:
                    '''#devo svuotare tutte le madri impostate prima
                    print 'list term',lista_aliq_split_term
                    
                    gen_da_svuotare=[]
                    for i in range(0,len(lista_aliq_split_term)):
                        #rendo indisponibili le aliquote esauste
                        lista_aliq_split_term[i].availability=0
                        gen_da_svuotare.append(lista_aliq_split_term[i].uniqueGenealogyID)
                        
                        lista_aliq_split_term[i].save()
                        
                    print 'listasvuotare',gen_da_svuotare
                    if len(gen_da_svuotare)!=0:
                        #mi collego allo storage per svuotare le provette contenenti le aliq
                        #esaurite
                        address=Urls.objects.get(default=1).url
                        url = address+"/full/"
                        print url
                        values = {'lista' : json.dumps(gen_da_svuotare), 'tube': 'empty','canc':True,'operator':name}
                        data = urllib.urlencode(values)
                        req = urllib2.Request(url,data=data, headers={"workingGroups" : get_WG_string()})
                        urllib2.urlopen(req)'''
                    
                    fine=True
                    lista=[]
                    #prendo la lista con tutte le aliq salvate dentro e le converto 
                    #per la visualizzazione in html
                    if request.session.has_key('listaValAliqSplit'):
                        lista_split=request.session.get('listaValAliqSplit')
                    else:
                        lista_split=[]
                    print 'listaaliq',lista_split
                    for i in range(0,len(lista_split)):
                        s=lista_split[i].split('&')
                        lista.append(ReportToHtml([i+1,s[0],s[1],s[2],s[3],s[4],s[5],s[6],s[7],s[8],s[9],s[10]]))
                    print 'lista',lista
                    variables = RequestContext(request,{'fine':fine,'lista_der':lista})
                    return render_to_response('tissue2/split/end_split.html',variables)
        except Exception,e:
            print 'err',e
            transaction.rollback()
            errore=True
            variables = RequestContext(request, {'errore':errore})
            return render_to_response('tissue2/index.html',variables)

