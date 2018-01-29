from __init__ import *
from catissue.tissue.utils import *

#dato un file con tutte le misure permette di inserirle in serie per varie aliquote
'''from catissue.tissue import *
import datetime
enable_graph()
disable_graph()
qualprot=QualityProtocol.objects.get(name='RNAMeasure')
strumbio=Instrument.objects.get(name='BIOANALYZER')
strumnano=Instrument.objects.get(name='NANODROP')
concbio=Measure.objects.get(name='concentration',idInstrument=strumbio)
concnano=Measure.objects.get(name='concentration',idInstrument=strumnano)
pur230=Measure.objects.get(name='purity',measureUnit='260/230')
pur280=Measure.objects.get(name='purity',measureUnit='260/280')
qualrin=Measure.objects.get(name='quality',idInstrument=strumbio)
f = open('rnarev.txt', 'rb')
lines=f.readlines()
for l in lines:
    print 'l',l
    if l.strip()!='':
        val=l.strip().split('\t')
        gen=val[1]
        nanodrop=val[2]
        bioan=val[3]
        rin=val[4]
        p280=val[5]
        p230=val[6]
        aliq=Aliquot.objects.get(uniqueGenealogyID=gen)
        print 'aliq',aliq
        qualsched=AliquotQualitySchedule.objects.get(idAliquot=aliq,revaluationExecuted=0,deleteTimestamp=None)
        print 'qualsched',qualsched
        qualev=QualityEvent(idQualityProtocol=qualprot,idQualitySchedule=qualsched.idQualitySchedule,idAliquot=aliq,misurationDate=date.today(),insertionDate=date.today(),operator='francesco.galimi',quantityUsed=0)
        qualev.save()
        evmisur=MeasurementEvent(idMeasure=concbio,idQualityEvent=qualev,value=bioan)
        evmisur.save()
        evmisur=MeasurementEvent(idMeasure=concnano,idQualityEvent=qualev,value=nanodrop)
        evmisur.save()
        evmisur=MeasurementEvent(idMeasure=pur230,idQualityEvent=qualev,value=p230)
        evmisur.save()
        evmisur=MeasurementEvent(idMeasure=pur280,idQualityEvent=qualev,value=p280)
        evmisur.save()
        evmisur=MeasurementEvent(idMeasure=qualrin,idQualityEvent=qualev,value=rin)
        evmisur.save()
        featconc=Feature.objects.get(idAliquotType=aliq.idAliquotType.id,name='Concentration')
        aliqfeat=AliquotFeature.objects.get(idAliquot=aliq,idFeature=featconc)
        aliqfeat.value=nanodrop
        aliqfeat.save()
        print 'alfeat',aliqfeat
        qualsched.revaluationExecuted=1
        qualsched.save()'''

@laslogin_required
@login_required
def RevalueAliquotsView(request):
    da_rivalutare=[]
    request.session['rivalutare']=da_rivalutare
    variables = RequestContext(request)   
    return render_to_response('tissue2/revalue/start.html',variables)


@get_functionality_decorator
def ajax_revalued_autocomplete(request):
    if 'term' in request.GET:
        #aliq = Aliquot.objects.filter(Q(uniqueGenealogyID__icontains=request.GET.get('term'))&Q(derived=1)&Q(availability=1))[:10]
        aliq = Aliquot.objects.filter(uniqueGenealogyID__icontains=request.GET.get('term'),availability=1)[:10]
        res=[]
        for p in aliq:
            p = {'id':p.id, 'label':p.__unicode__(), 'value':p.__unicode__()}
            res.append(p)
        return HttpResponse(simplejson.dumps(res))
    return HttpResponse()

@get_functionality_decorator
def AjaxRevaluedNewMeasureTypeAutocomplete(request):
    try:
        if 'term' in request.GET:
            misure = Measure.objects.filter(name__istartswith=request.GET.get('term')).values('name').distinct()[:10]
            res=[]
            for p in misure:
                p = { 'label':p['name'], 'value':p['name']}
                res.append(p)
            return HttpResponse(simplejson.dumps(res))
        return HttpResponse()
    except Exception,e:
        print 'err',e

@get_functionality_decorator
def AjaxRevaluedNewMeasureUnitAutocomplete(request):
    if 'term' in request.GET:
        misure = Measure.objects.filter(measureUnit__istartswith=request.GET.get('term')).values('measureUnit').distinct()[:10]
        res=[]
        for p in misure:
            p = {'label':p['measureUnit'], 'value':p['measureUnit']}
            res.append(p)
        return HttpResponse(simplejson.dumps(res))
    return HttpResponse()

@transaction.commit_on_success
@laslogin_required
@login_required
#@user_passes_test(lambda u: u.has_perm('tissue.can_view_plan_aliquots_to_revalue'),login_url=settings.BASE_URL+'/tissue/error/')
@permission_decorator('tissue.can_view_BBM_plan_aliquots_to_revalue')
def InsertRevalueAliquots(request):
    if request.session.has_key('rivalutare'):
        da_rivalutare=request.session.get('rivalutare')
    else:
        da_rivalutare=[]
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
                print 'lis da riva',lisgen
                request.session['rivalutare']=lisgen
                return HttpResponse()
            #ho cliccato sul tasto 'add file'
            if 'aggiungi_file' in request.POST:
                lisaliq=[]
                lisbarc=[]
                lispos=[]

                if 'file' in request.FILES:
                    print 'da rivvv',da_rivalutare
                    for lis in da_rivalutare:
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
                            if lista not in da_rivalutare:                                
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
                                    #guardo se l'aliquota e' un derivato. Non lo faccio piu' per permettere di inserire anche tessuti
                                    #e metterli esauriti
                                    #if al.derived==0:
                                        #raise ErrorRevalue('Error: aliquot '+gen+' is not derived')
                                    
                                    #vedo se l'aliquota e' gia' stata programmata per la rivalutazione
                                    alqualsched=AliquotQualitySchedule.objects.filter(idAliquot=al,revaluationExecuted=0,deleteTimestamp=None)
                                    print 'alqual',alqualsched
                                    if(alqualsched.count()!=0):
                                        raise ErrorRevalue('Error: aliquot '+gen+' is already scheduled for revaluation')
                                da_rivalutare.append(lista)
                                    
                    print 'rivvv',da_rivalutare
                    #request.session['rivalutare']=da_rivalutare
                    variables = RequestContext(request,{'rivalutare':zip(lisaliq,lisbarc,lispos)})
                    return render_to_response('tissue2/revalue/revaluated.html',variables)
            #ho cliccato sul tasto 'confirm'    
            if 'conferma' in request.POST:
                print 'da rivalutare',da_rivalutare
                name=request.user.username
                lisaliq=[]
                lisbarc=[]
                lispos=[]
                
                #salvo la QualitySchedule per la rivalutazione
                schedule=QualitySchedule(scheduleDate=date.today(),
                                         operator=name)
                schedule.save()
                for lis in da_rivalutare:
                    for valori in lis:
                        val=valori.split('|')
                        gen=val[0]
                        barc=val[1]
                        pos=val[2]
                        a=Aliquot.objects.get(availability=1,uniqueGenealogyID=gen)
                        #creo l'oggetto e metto a 0 i campi che non mi servono in questo momento
                        rev_aliq=AliquotQualitySchedule(idAliquot=a,
                                                        idQualitySchedule=schedule,
                                                        revaluationExecuted=0)
                        rev_aliq.save()
                        lisaliq.append(gen)
                        lisbarc.append(barc)
                        lispos.append(pos)
                variables = RequestContext(request,{'fine':True,'rivalutare':zip(lisaliq,lisbarc,lispos)})
                return render_to_response('tissue2/revalue/revaluated.html',variables)

        except ErrorRevalue as e:
            print 'My exception occurred, value:', e.value
            variables = RequestContext(request, {'errore':e.value})
            return render_to_response('tissue2/revalue/revaluated.html',variables)
        except Exception,e:
            print 'err',e
            transaction.rollback()
            errore=True
            variables = RequestContext(request, {'errore':errore})
            return render_to_response('tissue2/index.html',variables)

    variables = RequestContext(request, {'rivalutare':da_rivalutare})
    return render_to_response('tissue2/revalue/revaluated.html',variables)

#per cancellare le rivalutazioni pianificate
@transaction.commit_on_success
@laslogin_required
@login_required
#@user_passes_test(lambda u: u.has_perm('tissue.can_view_revalue_aliquots'),login_url=settings.BASE_URL+'/tissue/error/')
@permission_decorator('tissue.can_view_BBM_revalue_aliquots')
def CancRevalueAliquots(request):
    try:
        name=request.user.username
        if request.method=='POST':
            if 'salva' in request.POST:
                operatore=User.objects.get(username=name)
                listarev=[]
                listaaliq=json.loads(request.POST.get('dati'))
                print 'listaaliq',listaaliq
                for gen in listaaliq:
                    aliq=Aliquot.objects.get(uniqueGenealogyID=gen)
                    listarevsched=AliquotQualitySchedule.objects.filter(idAliquot=aliq,revaluationExecuted=0,deleteTimestamp=None)
                    if len(listarevsched)!=0:
                        revsched=listarevsched[0]
                        #revsched.deleteTimestamp= datetime.datetime.now()
                        revsched.deleteTimestamp=timezone.localtime(timezone.now())
                        revsched.deleteOperator=operatore
                        revsched.save()
                        listarev.append(revsched)
                print 'listarev',listarev
                request.session['listarev_canc']=listarev
                return HttpResponse()
            if 'final' in request.POST:
                lista=[]
                laliq=[]
                listar=request.session.get('listarev_canc')
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
                    dat=revsch.idQualitySchedule.scheduleDate
                    print 'dat',dat
                    data2=str(dat).split('-')
                    d=data2[2]+'-'+data2[1]+'-'+data2[0]
                    print 'd',d
                    valori=diz[revsch.idAliquot.uniqueGenealogyID]
                    val=valori[0].split('|')
                    barc=val[1]
                    pos=val[2]
                    
                    '''assegnatario=User.objects.get(username=revsch.idQualitySchedule.operator)
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
                        
                    lista.append(ReportScheduleCancToHtml(i+1,revsch.idAliquot.uniqueGenealogyID,barc,pos,revsch.idQualitySchedule.operator,d,'n'))
                print 'lista',lista                                
                
                InviaMail('Revaluation',name,laliq,listar,diz)
                        
                variables = RequestContext(request,{'lista_sch':lista})
                return render_to_response('tissue2/revalue/cancel.html',variables)
    except Exception,e:
        print 'err',e
        transaction.rollback()
        errore=True
        variables = RequestContext(request, {'errore':errore})
        return render_to_response('tissue2/index.html',variables)
    
#per far comparire la prima pagina delle aliquote da rivalutare con la lista delle aliquote da rivalutare
@laslogin_required
@login_required
#@user_passes_test(lambda u: u.has_perm('tissue.can_view_revalue_aliquots'),login_url=settings.BASE_URL+'/tissue/error/')
@permission_decorator('tissue.can_view_BBM_revalue_aliquots')
def ExecRevalueAliquots(request):
    lista_aliq=[]

    lista=AliquotQualitySchedule.objects.filter(revaluationExecuted=0,deleteTimestamp=None)
    for l in lista:
        lista_aliq.append(l)
    print 'lista_aliq',lista_aliq
    #chiave il gen e valore true o false se il campione ha o no un volume
    dizvolumi={}
    if 'robotrevalueload' in request.session:
        print 'robot'
        del request.session['robotrevalueload']
        robot='True'    
        for alqual in lista_aliq:
            dizvolumi[alqual.idAliquot.uniqueGenealogyID]=False
            #devo vedere se i campioni selezionati possono supportare una rivalutazione al robot. Quindi devo vedere se sono dei liquidi e se hanno un volume
            lfeatvol=Feature.objects.filter(idAliquotType=alqual.idAliquot.idAliquotType,name='Volume')
            if len(lfeatvol)!=0:
                #prendo il volume effettivo
                lvol=AliquotFeature.objects.filter(idAliquot=alqual.idAliquot,idFeature=lfeatvol[0])
                if len(lvol)!=0:
                    dizvolumi[alqual.idAliquot.uniqueGenealogyID]=True
    else:
        robot='False'
    print 'dizvolumi',dizvolumi
    variables = RequestContext(request,{'lista':lista_aliq,'tipo':'revaluation','robot':robot,'dizvolumi':json.dumps(dizvolumi)})
    return render_to_response('tissue2/revalue/execute.html',variables)

#per mettere aliquote nella lista effettiva delle rivalutazioni di oggi
@transaction.commit_on_success
@laslogin_required
@login_required
#@user_passes_test(lambda u: u.has_perm('tissue.can_view_revalue_aliquots'),login_url=settings.BASE_URL+'/tissue/error/')
@permission_decorator('tissue.can_view_BBM_revalue_aliquots')
def ExecEffectiveRevalueAliquots(request):
    try:
        if request.method=='POST':
            print request.POST
            
            if 'salva' in request.POST:
                listagen=json.loads(request.POST.get('lgen'))
                print 'listagen',listagen
                request.session['rivalutareconvalidate']=listagen
                return HttpResponse()
            if 'conferma' in request.POST:
                lisfin=[]
                adesso=timezone.localtime(timezone.now())
                #metto i secondi a zero in modo di partire dal minuto preciso. Poi ad ogni convalida aggiungo un secondo
                adesso=adesso.replace(second=0, microsecond=0)
                print 'adesso',adesso
                
                listagen=request.session.get('rivalutareconvalidate')
                lisaliq=Aliquot.objects.filter(uniqueGenealogyID__in=listagen,availability=1)
                print 'lisaliq',lisaliq
                lisqual=AliquotQualitySchedule.objects.filter(idAliquot__in=lisaliq,revaluationExecuted=0,deleteTimestamp=None)
                lgen=[]
                strgen=''                
                for qual in lisqual:
                    lgen.append(qual.idAliquot.uniqueGenealogyID)
                    strgen+=qual.idAliquot.uniqueGenealogyID+'&'
                    print 'aliquota_riv',qual.idAliquot
                i=0
                #devo ordinare la lista degli aliquot qual sched in base a come sono state convalidate le aliquote
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
                res1 = u.read()
                print 'res',res1
                if res1=='err':
                    variables = RequestContext(request, {'errore':True})
                    return render_to_response('tissue2/index.html',variables)                                
                
                lgenfin=strgen[:-1]
                diz=AllAliquotsContainer(lgenfin)
                lisbarc=[]
                lispos=[]                
                
                for alqual in lisfin:
                    valori=diz[alqual.idAliquot.uniqueGenealogyID]
                    val=valori[0].split('|')
                    barcode=val[1]
                    position=val[2]
                    lisbarc.append(barcode)
                    lispos.append(position)
                if 'robot' in request.POST:
                    print 'robot'
                    request.session['aliqrivPlanQuantRobot']=lisfin
                    request.session['dizinfoaliqrivPlanQuantRobot']=diz
                    #devo prendere i protocolli per le misure, quindi quelli di tipo uv e fluo
                    lisprotype=ProtocolTypeHamilton.objects.filter(name__in=['fluo','uv']).values_list('id',flat=True)
                    lisprot=ProtocolHamilton.objects.filter(protocol_type_id__in=lisprotype)
                    print 'lisprot',lisprot
                    #prendo i tipi di container
                    lislabware=LabwareTypeHamilton.objects.all()
                    variables = RequestContext(request,{'lista':zip(lisfin,lisbarc,lispos),'lisprot':lisprot,'liscont':lislabware})
                    return render_to_response('tissue2/revalue_robot/set_procedure.html',variables)
                else:
                    request.session['aliqrivalutare']=lisfin
                    request.session['dizinfoaliqrivalutare']=diz            
                    variables = RequestContext(request,{'lista':zip(lisfin,lisbarc,lispos)})
                    return render_to_response('tissue2/revalue/details.html',variables)
    except Exception,e:
        print 'err',e
        transaction.rollback()
        variables = RequestContext(request, {'errore':True})
        return render_to_response('tissue2/index.html',variables)

#per confermare la schermata dei dettagli delle aliquote da rivalutare e salvare i dati
@transaction.commit_on_success
@laslogin_required
@login_required
#@user_passes_test(lambda u: u.has_perm('tissue.can_view_revalue_aliquots'),login_url=settings.BASE_URL+'/tissue/error/')
@permission_decorator('tissue.can_view_BBM_revalue_aliquots')
def ConfirmDetailsRevaluedAliquots(request):
    if request.session.has_key('aliqrivalutare'):
        aliq_da_rivalutare=request.session.get('aliqrivalutare')
    if request.method=='POST':
        try:
            print request.POST
            print 'aliq_da_rivalutare',aliq_da_rivalutare
            lista_finite=[]
            listareport=[]
            name=request.user.username
            if request.session.has_key('dizinfoaliqrivalutare'):
                    dizinfo=request.session.get('dizinfoaliqrivalutare')
            else:
                strgen=''
                for qual in aliq_da_rivalutare:
                    strgen+=qual.idAliquot.uniqueGenealogyID+'&'
                
                lgenfin=strgen[:-1]
                dizinfo=AllAliquotsContainer(lgenfin)
                request.session['dizinfoaliqrivalutare']=dizinfo
            print 'diziinfo',dizinfo
            for i in range(0,len(aliq_da_rivalutare)):
                #preparo i nomi con cui accedere alla request.post
                gen='gen_'+str(i)
                esausta='exhaus_'+str(i)
                geneal=request.POST.get(gen)
                lista_al_der=Aliquot.objects.filter(uniqueGenealogyID=geneal,availability=1)
                if lista_al_der.count()!=0:
                    aliquota=lista_al_der[0]
                print 'aliq', aliquota
                #se l'aliquota e' da mettere esaurita
                if esausta in request.POST:
                    lista_finite.append(aliquota)
                else:
                    if request.session.has_key('revaluedmeasure'):
                        dictmeasure=request.session.get('revaluedmeasure')
                    print 'dictmes',dictmeasure
                    if dictmeasure.has_key(geneal):
                        valori=dictmeasure.pop(geneal)
                    print 'val',valori
                    dictmeasure[geneal]=valori
                    #prendo il qualityschedule
                    qualsched=aliq_da_rivalutare[i].idQualitySchedule
                    #in lista ho i valori di una singola misura
                    lista=valori.split('|')
                    #prendo il quality protocol
                    #in lista[0] ho l'id del quality protocol
                    qualprot=QualityProtocol.objects.get(id=lista[0])
                    print 'qualprot',qualprot
                    #salvo il volume usato per fare le misure
                    volusato=lista[1]
                    if volusato!='':
                        volus=float(volusato)
                    else:
                        volus=None
                                      
                    qualev=QualityEvent(idQualityProtocol=qualprot,
                                        idQualitySchedule=qualsched,
                                        idAliquot=aliquota,
                                        misurationDate=date.today(),
                                        insertionDate=date.today(),
                                        operator=name,
                                        quantityUsed=volus)
                    qualev.save()
                    print 'qualev',qualev
                    salvata=False
                    cambia=False
                    for j in range(3,len(lista)-1):
                        #in singola ho tutti i valori di una misura
                        val=lista[j].split('&')
                        print 'lung',len(val)
                        strum,creato=Instrument.objects.get_or_create(code=val[3],
                             name=val[2])
                        print 'strum',strum
                        misura,creato=Measure.objects.get_or_create(idInstrument=strum,
                                                                    name=val[0],
                                                                    measureUnit=val[1])
                        print 'misura',misura
                        v=float(val[4])
                        evmisur=MeasurementEvent(idMeasure=misura,
                                                idQualityEvent=qualev,
                                                value=v)
                        evmisur.save()
                        print 'ev',evmisur
                        #se devo salvare la nuova concentrazione scelta
                        if len(val)==6:
                            if val[5]=='scelta':
                                salvata=True
                                #prendo la feature della concentrazione
                                featconc=Feature.objects.get(idAliquotType=aliquota.idAliquotType.id,name='Concentration')
                                aliqfeat=AliquotFeature.objects.get(idAliquot=aliquota,idFeature=featconc)
                                aliqfeat.value=v
                                aliqfeat.save()
                                print 'alfeat',aliqfeat
                                #solo se e' un'aliquota derivata esterna e quindi non ho inserito la conc
                                #all'inizio
                                #prendo la feature della concentrazione originale
                                featorigconc=Feature.objects.get(idAliquotType=aliquota.idAliquotType.id,name='OriginalConcentration')
                                aliqorigfeat=AliquotFeature.objects.get(idAliquot=aliquota,idFeature=featorigconc)
                                if aliqorigfeat.value==-1 or cambia==True:
                                    aliqorigfeat.value=v
                                    aliqorigfeat.save()
                                    print 'aliqorigfeat',aliqorigfeat
                        #se non ho scelto una concentrazione perche' ce n'e' una sola
                        if salvata==False and val[0]=="concentration":
                            #prendo la feature della concentrazione
                            featconc=Feature.objects.get(idAliquotType=aliquota.idAliquotType.id,name='Concentration')
                            aliqfeat=AliquotFeature.objects.get(idAliquot=aliquota,idFeature=featconc)
                            aliqfeat.value=v
                            aliqfeat.save()
                            print 'alfeat',aliqfeat
                            #solo se e' un'aliquota derivata esterna e quindi non ho inserito la conc
                            #all'inizio
                            #prendo la feature della concentrazione originale
                            featorigconc=Feature.objects.get(idAliquotType=aliquota.idAliquotType.id,name='OriginalConcentration')
                            aliqorigfeat=AliquotFeature.objects.get(idAliquot=aliquota,idFeature=featorigconc)
                            if aliqorigfeat.value==-1:
                                cambia=True
                                aliqorigfeat.value=v
                                aliqorigfeat.save()
                                print 'aliqorigfeat',aliqorigfeat
                                           
                    volattuale=lista[2]
                    featvol=Feature.objects.get(idAliquotType=aliquota.idAliquotType.id,name='Volume',measureUnit='ul')
                    aliqfeat=AliquotFeature.objects.get(idAliquot=aliquota,idFeature=featvol)
                    if volattuale!='':
                        #salvo il volume attuale del campione, se e' stato inserito
                        volatt=float(volattuale)  
                        aliqfeat.value=volatt
                        aliqfeat.save()
                        print 'alfeat',aliqfeat
                        #solo se non ho inserito il volume all'inizio
                        #prendo la feature del volume originale
                        featorigvol=Feature.objects.get(idAliquotType=aliquota.idAliquotType.id,name='OriginalVolume',measureUnit='ul')
                        aliqorigfeat=AliquotFeature.objects.get(idAliquot=aliquota,idFeature=featorigvol)
                        if aliqorigfeat.value==-1:
                            cambia=True
                            aliqorigfeat.value=volatt
                            aliqorigfeat.save()
                            print 'aliqorigfeat',aliqorigfeat
                    else:
                        if volus!=None and aliqfeat.value!=-1:
                            #se non e' stato inserito un volume nuovo, devo comunque sottrarre dal vol totale
                            #quello preso per le misure
                            volfin=aliqfeat.value-float(volus)
                            if volfin<0:
                                volfin=0
                            aliqfeat.value=volfin
                            aliqfeat.save()
                            print 'aliqfeat',aliqfeat
    
                    #mi occupo del file e del giudizio
                    f=lista[len(lista)-1]
                    fi=f.split('&')
                    filenuovo=fi[0]
                    giudizio=fi[1]
                    print 'file',filenuovo
                    print 'g',giudizio
                    #solo se l'utente ha caricato un file
                    if filenuovo!=' ':
                        try:
                            fn = os.path.basename(filenuovo)
                            percorso=os.path.join(os.path.dirname(__file__),'tissue_media/Derived_temporary/'+fn)
                            #cerco di aprire il file cosi' se non c'e' mi da' errore e va bene perche' lo voglio caricare una volta sola.
                            #Invece responseUpload viene tenuto al valore precedente e va bene
                            fvecchio=open(percorso, 'rb')
                            #prendo il percorso nuovo in cui salvare il file
                            #fnnuovo = os.path.basename(filenuovo)
                            #percorsonuovo=os.path.join(os.path.dirname(__file__),'tissue_media/Derived_aliquots/'+fnnuovo)
                            #salvo il file
                            #open(percorsonuovo, 'wb').write(fvecchio.read())
                            #fvecchio.close()
                            responseUpload = uploadRepFile({'operator':request.user.username}, percorso)
                            print 'responseUpload',responseUpload
                            if responseUpload == 'Fail':
                                transaction.rollback()
                                raise Exception
                            print 'file nuovo caricato'
                            #cancello il file vecchio
                            os.remove(percorso)
                            print 'file vecchio cancellato'
                        except:
                            print 'file gia caricato'
                            pass
                        qualfile=QualityEventFile(idQualityEvent=qualev,
                                                  file=filenuovo,
                                                  judge=giudizio,
                                                  linkId=responseUpload)
                        qualfile.save()
                        print 'qualfile',qualfile        
                
                #solo se il campione non e' esaurito
                print 'esausta',esausta
                print 'gen',geneal
                print 'dizinfo',dizinfo
                
                print 'gen',geneal
                valori=dizinfo[geneal]
                print 'valori',valori
                val=valori[0].split('|')
                barcode=val[1]
                position=val[2]
                esaurita='False'
                if esausta in request.POST:
                    esaurita='True'
                stringa=geneal+'&'+barcode+'&'+position+'&'+esaurita
                print 'stringa',stringa
                listareport.append(stringa)
                #salvo che la rivalutazione e' stata eseguita
                aliq_da_rivalutare[i].revaluationExecuted=1
                aliq_da_rivalutare[i].operator=request.user
                aliq_da_rivalutare[i].save()
            print 'listareport',listareport
            gen_da_svuotare=[]
            for i in range(0,len(lista_finite)):
                #rendo indisponibili le aliquote esauste
                lista_finite[i].availability=0
                gen_da_svuotare.append(lista_finite[i].uniqueGenealogyID)
                
                lista_finite[i].save()
                
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
                urllib2.urlopen(req)
            
            lista,intest=LastPartRevaluation(listareport)    
            fine=True 
            if request.session.has_key('ListaGenMeasureAllRevaluate'):
                del request.session['ListaGenMeasureAllRevaluate']
            if request.session.has_key('revaluedmeasure'):
                del request.session['revaluedmeasure']
            if request.session.has_key('aliqrivalutare'):
                del request.session['aliqrivalutare']
            variables = RequestContext(request,{'fine':fine,'lista_riv':lista,'intest':intest})
            return render_to_response('tissue2/revalue/details.html',variables)
        except Exception, e:
            print 'err',e
            transaction.rollback()
            variables = RequestContext(request, {'errore':True})
            return render_to_response('tissue2/index.html',variables)
        
#per visualizzare il file caricato nel momento della derivazione o rivalutazione
@transaction.commit_on_success
@laslogin_required
@login_required
#@user_passes_test(lambda u: u.has_perm('tissue.can_view_file_saved'),login_url=settings.BASE_URL+'/tissue/error/')
@permission_decorator('tissue.can_view_BBM_file_saved')
def RevalueAliquotsViewFile(request):
    try:
        print request.POST
        variables = RequestContext(request)   
        return render_to_response('tissue2/revalue/file_view.html',variables)
    except:
        transaction.rollback()
        errore=True
        variables = RequestContext(request, {'errore':errore})
        return render_to_response('tissue2/index.html',variables)

