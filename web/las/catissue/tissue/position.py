from __init__ import *
from catissue.tissue.utils import *

@laslogin_required
@login_required
def VitalView(request):
    da_posizionare=[]
    request.session['posizionare']=da_posizionare
    variables = RequestContext(request)   
    return render_to_response('tissue2/vital/start.html',variables)

@get_functionality_decorator
def ajax_position_autocomplete(request):
    if 'term' in request.GET:
        #prendo solo le aliq di tipo vitale
        tipo=AliquotType.objects.get(abbreviation='VT')
        aliq = Aliquot.objects.filter(Q(uniqueGenealogyID__istartswith=request.GET.get('term'))&Q(availability=1)&Q(idAliquotType=tipo))[:10]
        res=[]
        for p in aliq:
            p = {'id':p.id, 'label':p.__unicode__(), 'value':p.__unicode__()}
            res.append(p)
        return HttpResponse(simplejson.dumps(res))
    return HttpResponse()

@transaction.commit_on_success
@laslogin_required
@login_required
#@user_passes_test(lambda u: u.has_perm('tissue.can_view_plan_retrieval'),login_url=settings.BASE_URL+'/tissue/error/')
@permission_decorator('tissue.can_view_BBM_plan_retrieval')
def InsertPositionVitalAliquots(request):
    if request.session.has_key('posizionare'):
        da_posizionare=request.session.get('posizionare')
    else:
        da_posizionare=[]
    if request.method=='POST':
        print request.POST
        print request.FILES  
        try:          
            if 'salva' in request.POST:
                listaaliq=json.loads(request.POST.get('dati'))
                note=request.POST.get('note')
                lisgen=[]
                if len(listaaliq)!=0:
                    for val in listaaliq:
                        print 'val',val
                        listemp=[]
                        listemp.append(val)
                        if listemp not in lisgen:
                            lisgen.append(listemp)
                print 'lis da posiz',lisgen
                request.session['posizionare']=lisgen
                request.session['noteretrieve']=note
                return HttpResponse()
            #ho cliccato sul tasto 'add file'
            if 'aggiungi_file' in request.POST:
                form=PositionForm(request.POST,request.FILES)
                note=request.session.get('noteretrieve').strip()
                lisaliq=[]
                lisbarc=[]
                lispos=[]
                tipo=AliquotType.objects.get(abbreviation='VT')
                if 'file' in request.FILES:
                    print 'da_posizionare',da_posizionare
                    for lis in da_posizionare:
                        for val in lis:
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
                            lisgen=[]
                            if lista not in da_posizionare:
                                da_posizionare.append(lista)
                                #e' una lista in cui ogni valore e' una stringa formata da gen|barcode|posizione
                                for val in lista:
                                    ch=val.split('|')
                                    lisgen.append(ch[0])
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
                                    #guardo se l'aliquota e' vitale
                                    if al.idAliquotType!=tipo:
                                        raise ErrorRevalue('Error: aliquot '+gen+' is not viable')
                                    
                                    #vedo se l'aliquota e' gia' stata programmata per la divisione
                                    alpossched=AliquotPositionSchedule.objects.filter(idAliquot=al,positionExecuted=0,deleteTimestamp=None)
                                    print 'alqual',alpossched
                                    if(alpossched.count()!=0):
                                        raise ErrorRevalue('Error: aliquot '+gen+' is already scheduled for retrieving')
                                    
                                    #devo verificare che il campione abbia una data di archiviazione per sapere se e'
                                    #possibile posizionarlo o meno
                                    #datainiz=datetime.date(2013,1,1)
                                    #dat=al.idSamplingEvent.samplingDate
                                    #print 'dat',dat
                                    #if al.archiveDate==None and dat>datainiz:
                                    #    raise ErrorRevalue('Error: aliquot '+gen+' has not been archived yet. Please first execute it')
                                    
                    print 'posiz',da_posizionare
                    print 'lisaliq',lisaliq
                    variables = RequestContext(request,{'form':form,'posizionare':zip(lisaliq,lisbarc,lispos),'note':note})
                    return render_to_response('tissue2/vital/positioned.html',variables)

            #ho cliccato sul tasto 'confirm'    
            else:
                form=PositionForm(request.POST,request.FILES)
                
                print 'da posiz',da_posizionare
                name=request.user.username
                note=request.session.get('noteretrieve').strip()
                lisaliq=[]
                lisbarc=[]
                lispos=[]
                
                #salvo lo splitsched per lo split
                schedule=PositionSchedule(scheduleDate=date.today(),
                                         operator=name)
                schedule.save()
                for lis in da_posizionare:
                    for valori in lis:
                        val=valori.split('|')
                        gen=val[0]
                        barc=val[1]
                        pos=val[2]
                        a=Aliquot.objects.get(availability=1,uniqueGenealogyID=gen)
                        #creo l'oggetto e metto a 0 i campi che non mi servono in questo momento
                        rev_aliq=AliquotPositionSchedule(idAliquot=a,
                                                        idPositionSchedule=schedule,
                                                        positionExecuted=0,
                                                        notes=note
                                                        )
                        rev_aliq.save()
                        lisaliq.append(gen)
                        lisbarc.append(barc)
                        lispos.append(pos)
                variables = RequestContext(request,{'fine':True,'posizionare':zip(lisaliq,lisbarc,lispos)})
                return render_to_response('tissue2/vital/positioned.html',variables)
                
        except ErrorRevalue as e:
            print 'My exception occurred, value:', e.value
            variables = RequestContext(request, {'errore':e.value})
            return render_to_response('tissue2/vital/positioned.html',variables)
        except Exception,e:
            transaction.rollback()
            print 'err',e
            variables = RequestContext(request, {'errore':True})
            return render_to_response('tissue2/index.html',variables)
    else:
        form = PositionForm()
    variables = RequestContext(request, {'form':form,'rivalutare':da_posizionare})
    return render_to_response('tissue2/vital/positioned.html',variables)

#per cancellare i posizionamenti gia' pianificati
@transaction.commit_on_success
@laslogin_required
@login_required
#@user_passes_test(lambda u: u.has_perm('tissue.can_view_retrieve_aliquots'),login_url=settings.BASE_URL+'/tissue/error/')
@permission_decorator('tissue.can_view_BBM_retrieve_aliquots')
def CancVitalAliquots(request):
    try:
        name=request.user.username
        print request.POST
        if request.method=='POST':
            if 'salva' in request.POST:
                operatore=User.objects.get(username=name)
                listavit=[]
                listaaliq=json.loads(request.POST.get('dati'))
                print 'listaaliq',listaaliq
                esp=Experiment.objects.get(name='RetrieveForImplant')
                for gen in listaaliq:
                    aliq=Aliquot.objects.get(uniqueGenealogyID=gen)                    
                    listapossched=AliquotExperiment.objects.filter(idAliquot=aliq,idExperiment=esp,confirmed=0,deleteTimestamp=None)
                    #listapossched=AliquotPositionSchedule.objects.filter(idAliquot=aliq,positionExecuted=0,deleteTimestamp=None)
                    if len(listapossched)!=0:
                        possched=listapossched[0]
                        #possched.deleteTimestamp= datetime.datetime.now()
                        possched.deleteTimestamp=timezone.localtime(timezone.now())
                        possched.deleteOperator=operatore
                        possched.save()
                        listavit.append(possched)
                print 'listavit',listavit
                request.session['listavit_canc']=listavit
                return HttpResponse()
            if 'final' in request.POST:
                lista=[]
                laliq=[]
                listar=request.session.get('listavit_canc')
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
                    dat=revsch.idExperimentSchedule.scheduleDate
                    print 'dat',dat
                    data2=str(dat).split('-')
                    d=data2[2]+'-'+data2[1]+'-'+data2[0]
                    print 'd',d
                    valori=diz[revsch.idAliquot.uniqueGenealogyID]
                    val=valori[0].split('|')
                    barc=val[1]
                    pos=val[2]
                    
                    '''assegnatario=User.objects.get(username=revsch.idExperimentSchedule.operator.username)
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
                        
                    lista.append(ReportScheduleCancToHtml(i+1,revsch.idAliquot.uniqueGenealogyID,barc,pos,revsch.idExperimentSchedule.operator.username,d,'n'))
                print 'lista',lista
                
                InviaMail('Retrieve',name,laliq,listar,diz)

                variables = RequestContext(request,{'lista_sch':lista})
                return render_to_response('tissue2/revalue/cancel.html',variables)
    except Exception,e:
        print 'err',e
        transaction.rollback()
        variables = RequestContext(request, {'errore':True})
        return render_to_response('tissue2/index.html',variables)

#per far comparire la prima pagina delle aliquote da posizionare con la lista delle 
#aliquote da posizionare sulla piastra vitale
@laslogin_required
@login_required
#@user_passes_test(lambda u: u.has_perm('tissue.can_view_retrieve_aliquots'),login_url=settings.BASE_URL+'/tissue/error/')
@permission_decorator('tissue.can_view_BBM_retrieve_aliquots')
def ExecPositionVitalAliquots(request):
    name=request.user.username
    lista_aliq=[]
    request.session['aliqposizionare']=[]
    request.session['listaaliqposiz']=[]
    esp=Experiment.objects.get(name='RetrieveForImplant')
    lista1=AliquotExperiment.objects.filter(idExperiment=esp,confirmed=0,operator=name,deleteTimestamp=None)
    lista2=AliquotExperiment.objects.filter(idExperiment=esp,confirmed=0,operator='',deleteTimestamp=None)
    lista=list(chain(lista1,lista2))
    for l in lista:
        lista_aliq.append(l)
    print 'lista_aliq',lista_aliq
    variables = RequestContext(request,{'lista':lista_aliq,'tipo':'position'})
    return render_to_response('tissue2/vital/execute.html',variables)

#per mettere aliquote nella lista effettiva dei posizionamenti da fare oggi
@laslogin_required
@login_required
#@user_passes_test(lambda u: u.has_perm('tissue.can_view_retrieve_aliquots'),login_url=settings.BASE_URL+'/tissue/error/')
@permission_decorator('tissue.can_view_BBM_retrieve_aliquots')
def ExecEffectivePositionVitalAliquots(request):
    try:
        name=request.user.username
        if request.method=='POST':
            if 'salva' in request.POST:
                listagen=json.loads(request.POST.get('lgen'))
                print 'listagen',listagen
                request.session['listaaliqposiz']=listagen
                return HttpResponse()
            if 'conferma' in request.POST:
                lisfin=[]
                esp=Experiment.objects.get(name='RetrieveForImplant')
                listagen=request.session.get('listaaliqposiz')
                #devo vedere il tipo dell'aliq
                lisaliq=Aliquot.objects.filter(uniqueGenealogyID__in=listagen,availability=1)
                print 'lisaliq',lisaliq
                lis1=AliquotExperiment.objects.filter(idAliquot__in=lisaliq,idExperiment=esp,confirmed=0,operator=name,deleteTimestamp=None)
                lis2=AliquotExperiment.objects.filter(idAliquot__in=lisaliq,idExperiment=esp,confirmed=0,operator='',deleteTimestamp=None)
                lisqual=list(chain(lis1,lis2))
                #lisqual=AliquotPositionSchedule.objects.filter(idAliquot__in=lisaliq,positionExecuted=0,deleteTimestamp=None)
                lgen=[]
                strgen=''
                for qual in lisqual:
                    lgen.append(qual.idAliquot.uniqueGenealogyID)
                    strgen+=qual.idAliquot.uniqueGenealogyID+'&'
                    print 'aliquota_riv',qual.idAliquot
                #devo ordinare la lista degli aliquot qual sched in base a come sono state convalidate le aliquote
                for gen in listagen:
                    for qual in lisqual:
                        if qual.idAliquot.uniqueGenealogyID==gen:
                            lisfin.append(qual)
                
                request.session['aliqposizionare']=lisfin
                
                url1 = Urls.objects.get(default = '1').url + "/container/availability/"
                val1={'lista':json.dumps(lgen),'tube':'0','nome':request.user.username}

                print 'url1',url1
                data = urllib.urlencode(val1)
                req = urllib2.Request(url1,data=data, headers={"workingGroups" : get_WG_string()})
                u = urllib2.urlopen(req)
                #u = urllib2.urlopen(url1, data)
                res1 =  u.read()
                print 'res',res1
                if res1=='err':
                    variables = RequestContext(request, {'errore':True})
                    return render_to_response('tissue2/index.html',variables)
                
                request.session['listagen']={}
                a=SchemiPiastre()
                lispezzi=[]
                
                lgenfin=strgen[:-1]
                diz=AllAliquotsContainer(lgenfin)
                
                lisaliquote=[]
                lisbarc=[]
                lispos=[]
                for alsched in lisfin:
                    valori=diz[alsched.idAliquot.uniqueGenealogyID]
                    val=valori[0].split('|')
                    barcode=val[1]
                    position=val[2]
                    lisaliquote.append(alsched)
                    lisbarc.append(barcode)
                    lispos.append(position)                 
                    #prendo la feature per il numero di pezzi
                    lfeat=Feature.objects.filter(name='NumberOfPieces',idAliquotType=alsched.idAliquot.idAliquotType.id)
                    
                    if len(lfeat)!=0:
                        
                        print 'f',lfeat
                        #prendo il numero di pezzi
                        lalfeat=AliquotFeature.objects.filter(idAliquot=alsched.idAliquot.id,idFeature=lfeat[0])
                        if len(lalfeat)!=0:
                            alfeat=lalfeat[0]
                            print 'pezzi',alfeat.value
                            lispezzi.append(int(alfeat.value))
                        else:
                            lispezzi.append(0)
                    else:
                        lispezzi.append(0)
                    print 'lispezzi',lispezzi
                
                
        variables = RequestContext(request,{'listagen':zip(lisaliquote,lisbarc,lispos,lispezzi),'a':a})
        return render_to_response('tissue2/vital/details.html',variables)
    except Exception,e:
        print 'err',e
        variables = RequestContext(request, {'errore':True})
        return render_to_response('tissue2/index.html',variables)

#per confermare la schermata dei dettagli delle aliquote da posizionare e salvare i dati
@transaction.commit_on_success
@laslogin_required
@login_required
#@user_passes_test(lambda u: u.has_perm('tissue.can_view_retrieve_aliquots'),login_url=settings.BASE_URL+'/tissue/error/')
@permission_decorator('tissue.can_view_BBM_retrieve_aliquots')
def ConfirmDetailsPositionVitalAliquots(request):
    if request.session.has_key('listagen'):
        dictgen=request.session.get('listagen')
    if request.method=='POST':
        try:
            print request.POST
            name=request.user.username
            if 'carica' in request.POST:
                diz=json.loads(request.POST.get('diz'))
                print 'diz',diz
                dictgen={}
                for key,val in diz.items():
                    print 'key',key
                    print 'val',val
                    vv=val.split('|')
                    print 'vv',vv
                    geneal=vv[3]
                    piastradest=vv[1]
                    posiznuova=vv[0]
                    dictgen[geneal]=posiznuova+'%'+piastradest
                print 'dictgen',dictgen
                request.session['listagen']=dictgen
                #request.session['piastradestinazione']=piastradest
                print 'dict',dictgen
                return HttpResponse()
            if 'salva' in request.POST:
                listaaliq=[]
                lisvalreport=[]
                print 'salva'
                esp=Experiment.objects.get(name='RetrieveForImplant')
                #faccio una post allo storage per cambiare i barcode ai gen
                url = Urls.objects.get(default = '1').url + '/api/change/barcode/'
                val={'diz':json.dumps(dictgen),'user':request.user.username}
                data = urllib.urlencode(val)
                print 'url',url
                req = urllib2.Request(url,data=data, headers={"workingGroups" : get_WG_string()})
                u = urllib2.urlopen(req)
                res =  json.loads(u.read())
                print 'res',res['data']
                if res['data']=='errore':
                    raise Exception
                dati = json.loads(res['data'])
                print 'dati',dati
                for key,value in dictgen.items():
                    valori=dati[key]
                    print 'key',key
                    print 'valori',valori
                    #valori e' formato da barcvecchio|posvecchia|barcnuovo
                    vv=valori.split('|')
                    stringa=value.split('%')
                    stringa=key+'&'+vv[0]+'&'+vv[1]+'&'+vv[2]+'&'+stringa[1]+'&'+stringa[0]
                    lisvalreport.append(stringa)
                    listaaliq.append(Aliquot.objects.get(uniqueGenealogyID=key,availability=1))
                request.session['lisValPositionReport']=lisvalreport
                
                for a in listaaliq:
                    #salvo il fatto che il posizionamento e' stato eseguito
                    print 'a',a
                    posiz=AliquotExperiment.objects.get(idAliquot=a,idExperiment=esp,confirmed=0,deleteTimestamp=None)
                    #posiz=AliquotPositionSchedule.objects.get(idAliquot=a,positionExecuted=0,deleteTimestamp=None)
                    print 'pos',posiz
                    posiz.confirmed=1
                    if posiz.operator=='':
                        posiz.operator=name
                    posiz.save()
                lista,intest,l,inte=LastPartPosition(request,'n')
                variables = RequestContext(request,{'fine':True,'lista':lista,'intest':intest})
                return render_to_response('tissue2/vital/details.html',variables)
        except Exception,e:
            print 'err',e
            transaction.rollback()
            errore=True
            variables = RequestContext(request, {'errore':errore})
            return render_to_response('tissue2/index.html',variables)


