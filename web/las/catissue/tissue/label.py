from __init__ import *
from catissue.tissue.utils import *
from catissue.api.handlers import TableHandler, LabelListHandler
from PIL import Image

@get_functionality_decorator
def AjaxLabelProducerAutocomplete(request):
    try:
        if 'term' in request.GET:
            featprod=LabelFeature.objects.get(name='Producer')
            lisvalfeat=LabelMarkerLabelFeature.objects.filter(idLabelFeature=featprod,value__icontains=request.GET.get('term')).values('value').distinct()[:10]

            res=[]
            for p in lisvalfeat:
                p = { 'value':p['value']}
                res.append(p)
            return HttpResponse(simplejson.dumps(res))
        return HttpResponse()
    except Exception,e:
        print 'err',e

@transaction.commit_on_success
@laslogin_required
@login_required
@permission_decorator('tissue.can_view_BBM_plan_aliquots_to_label')
def InsertLabelAliquots(request):
    #PARTE SHARING
    assignUsersList=[]
    if settings.USE_GRAPH_DB == True:
        for g in get_WG():
            assignUsersDict={}
            assignUsersDict['wg']=WG.objects.get(name=g)
            assignUsersDict['usersList']=list()
            for u in User.objects.filter(~Q(username='admin')&~Q(first_name='')).filter(id__in=WG_User.objects.filter(user__is_active=1,WG__name=g,permission__codename=get_functionality()).values_list("user",flat=True)).order_by('last_name'):
                assignUsersDict['usersList'].append(u)
            assignUsersList.append(assignUsersDict)
        for g in WG.objects.all():
            addressUsersDict={}
            addressUsersDict['wg']=g
            addressUsersDict['usersList']=list()
            for u in User.objects.filter(~Q(username='admin')&~Q(first_name='')).filter(id__in=WG_User.objects.filter(user__is_active=1,WG=g,permission__codename=get_functionality()).values_list("user",flat=True)).order_by('last_name'):
                addressUsersDict['usersList'].append(u)
    else:
        assignUsersDict={}
        assignUsersDict['wg']=''
        assignUsersDict['usersList']=list()
        for u in User.objects.filter(~Q(username='admin')&~Q(first_name='')&Q(is_active=1)).order_by('last_name'):
            assignUsersDict['usersList'].append(u)
        assignUsersList.append(assignUsersDict)
        
    if request.session.has_key('vetrinilabelprog'):
        da_dividere=request.session.get('vetrinilabelprog')
    else:
        da_dividere=[]
    form=SlideInsertForm()
    if request.method=='POST':
        print request.POST
        print request.FILES  
        try:          
            if 'salva' in request.POST:
                listaaliq=json.loads(request.POST.get('dati'))
                operat=request.POST.get('operat')
                note=request.POST.get('note')
                print 'operat',operat
                lisgen=[]
                if len(listaaliq)!=0:
                    for val in listaaliq:
                        print 'val',val
                        listemp=[]
                        listemp.append(val)
                        if listemp not in lisgen:
                            lisgen.append(listemp)
                request.session['vetrinilabelprog']=lisgen
                request.session['opervetrinilabel']=operat
                request.session['notevetrinilabel']=note
                return HttpResponse()
            #ho cliccato sul tasto 'add file'
            if 'aggiungi_file' in request.POST:
                lisaliq=[]
                lisbarc=[]
                lispos=[]
                operat=request.session.get('opervetrinilabel')
                note=request.session.get('notevetrinilabel').strip()
                if 'file' in request.FILES:
                    print 'da preparare',da_dividere
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
                            lisgen=[]
                            if lista not in da_dividere:                                
                                #e' una lista in cui ogni valore e' una stringa formata da gen|barcode|posizione
                                for val in lista:
                                    ch=val.split('|')
                                    lisgen.append(ch[0])
                                    lisaliq.append(ch[0])
                                    lisbarc.append(ch[1])
                                    lispos.append(ch[2])
                                    
                                print 'lisgen',lisgen
                                #listaaliq=Aliquot.objects.filter(uniqueGenealogyID__in=lisgen,availability=1)
                                listaliq=[]
                                for gen in lisgen:
                                    #per controllare se l'aliquota e' di questo wg
                                    lisali=Aliquot.objects.filter(uniqueGenealogyID=gen,availability=1)
                                    if len(lisali)==0:
                                        raise ErrorRevalue('Error: aliquot '+gen+' does not exist in storage')
                                    listaliq.append(lisali[0])
                                
                                for al in listaliq:
                                    print 'al',al                                                                        
                                    #vedo se l'aliquota e' gia' stata programmata per la procedura
                                    alsplisched=AliquotLabelSchedule.objects.filter(idAliquot=al,executed=0,fileInserted=0,deleteTimestamp=None)
                                    print 'alqual',alsplisched
                                    if len(alsplisched)!=0:
                                        raise ErrorRevalue('Error: aliquot '+gen+' is already scheduled for this procedure')
                                    
                                    #devo vedere se l'aliq puo' essere pianificata per essere tagliata                
                                    if al.idAliquotType.abbreviation!='PS' and al.idAliquotType.abbreviation!='OS':
                                        raise ErrorRevalue('Error: aliquot type of '+gen+' is incompatible with this procedure')
                                da_dividere.append(lista)
                                    
                    print 'slide',da_dividere
                    variables = RequestContext(request,{'label':True,'rivalutare':zip(lisaliq,lisbarc,lispos),'form':form,'t':operat,'note':note,'assignUsersList':assignUsersList})
                    return render_to_response('tissue2/slide/slide.html',variables)
            
            if 'conferma' in request.POST:
                print 'da dividere',da_dividere
                name=request.user.username
                note=request.session.get('notevetrinilabel').strip()
                lisaliq=[]
                lisbarc=[]
                lispos=[]
                
                esec=request.session.get('opervetrinilabel')
                print 'esec',esec
                if esec!='':
                    esecutore=User.objects.get(id=esec)
                else:
                    esecutore=None
                print 'esecutore',esecutore
                pianificatore=User.objects.get(username=name)
                #salvo il labelsched
                schedule=LabelSchedule(scheduleDate=date.today(),
                                         operator=pianificatore)
                schedule.save()
                listal=[]
                #mi serve dopo per riempire il corpo del messaggio dell'e-mail
                dizaliqgen={}
                for lis in da_dividere:
                    for valori in lis:
                        val=valori.split('|')
                        gen=val[0]
                        barc=val[1]
                        pos=val[2]
                        a=Aliquot.objects.get(availability=1,uniqueGenealogyID=gen)
                        #creo l'oggetto e metto a 0 i campi che non mi servono in questo momento
                        rev_aliq=AliquotLabelSchedule(idAliquot=a,
                                                      idLabelSchedule=schedule,
                                                      operator=esecutore,
                                                      executed=0,
                                                      notes=note)
                        rev_aliq.save()
                        listal.append(rev_aliq)
                        lisaliq.append(gen)
                        lisbarc.append(barc)
                        lispos.append(pos)
                        dizaliqgen[gen]=barc+'|'+pos
                request.session['listafinalelabelreport']=zip(lisaliq,lisbarc,lispos)
                if esecutore!=None:
                    print 'dizaliqgen',dizaliqgen
                    email = LASEmail (functionality=get_functionality(), wgString=get_WG_string())
                    msg=['You have been designated to label these aliquots:','','Assigner:\t'+name,'Description:\t'+note,'','Aliquots:','N\tGenealogy ID\tBarcode\tPosition']
                    aliquots=Aliquot.objects.filter(uniqueGenealogyID__in=lisaliq,availability=1)
                    wgList=WG.objects.filter(id__in=Aliquot_WG.objects.filter(aliquot__in=aliquots).values_list('WG',flat=True).distinct())
                    print 'wglist',wgList
                    for wg in wgList:
                        print 'wg',wg
                        email.addMsg([wg.name], msg)
                        aliq=aliquots.filter(id__in=Aliquot_WG.objects.filter(WG=wg).values_list('aliquot',flat=True).distinct())
                        print 'aliq',aliq
                        i=1
                        #per mantenere l'ordine dei campioni anche nell'e-mail
                        for aliqtr in listal:
                            for al in aliq:   
                                if aliqtr.idAliquot.uniqueGenealogyID==al.uniqueGenealogyID:
                                    lval=dizaliqgen[al.uniqueGenealogyID]
                                    val=lval.split('|')
                                    barc=val[0]
                                    pos=val[1]
                                    email.addMsg([wg.name],[str(i)+'\t'+al.uniqueGenealogyID+'\t'+barc+'\t'+pos])
                                    i=i+1
                        #devo mandare l'e-mail all'operatore incaricato di eseguire la procedura
                        email.addRoleEmail([wg.name], 'Assignee', [esecutore.username])
                        email.addRoleEmail([wg.name], 'Executor', [request.user.username])
                        print 'messaggio',email.mailDict
                    try:
                        email.send()
                    except Exception, e:
                        print 'err',e
                        pass
                else:
                    #altrimenti non riesce ad impostarmi i valori nella sessione
                    time.sleep(1)
                
                urlfin=settings.DOMAIN_URL+settings.HOST_URL+'/label/insert/final/'
                print 'urlfin',urlfin
                return HttpResponseRedirect(urlfin)
                            
        except ErrorRevalue as e:
            print 'My exception occurred, value:', e.value
            variables = RequestContext(request, {'errore':e.value})
            return render_to_response('tissue2/slide/slide.html',variables)
        except Exception, e:
            print 'err',e
            transaction.rollback()
            variables = RequestContext(request, {'errore':True})
            return render_to_response('tissue2/index.html',variables)
        
    variables = RequestContext(request, {'rivalutare':da_dividere,'form':form,'assignUsersList':assignUsersList,'label':True})
    return render_to_response('tissue2/slide/slide.html',variables)

#per far vedere il report finale dell'inserimento delle fettine
@laslogin_required
@login_required
@permission_decorator('tissue.can_view_BBM_plan_aliquots_to_label')
def InsertLabelAliquotsFinal(request):
    liste=request.session.get('listafinalelabelreport')
    variables = RequestContext(request,{'fine':True,'rivalutare':liste,'label':True})
    return render_to_response('tissue2/slide/slide.html',variables)

#per far comparire la pagina dei vetrini da colorare con la lista delle aliquote
@laslogin_required
@login_required
@permission_decorator('tissue.can_view_BBM_execute_labelling')
def ConvalidateLabelAliquots(request):
    name=request.user.username
    operat=User.objects.get(username=name)
    lista1=AliquotLabelSchedule.objects.filter(executed=0,fileInserted=0,operator=operat,deleteTimestamp=None)
    lista2=AliquotLabelSchedule.objects.filter(executed=0,fileInserted=0,operator=None,deleteTimestamp=None)
    lista=list(chain(lista1,lista2))
    print 'lista aliq label',lista
    variables = RequestContext(request,{'lista':lista,'tipo':'label','label':True})
    return render_to_response('tissue2/vital/execute.html',variables)

#per cancellare le procedure gia' pianificate
@transaction.commit_on_success
@laslogin_required
@login_required
@permission_decorator('tissue.can_view_BBM_cancel_labelling')
def CancLabelAliquots(request):
    try:
        name=request.user.username
        print request.POST
        if request.method=='POST':
            if 'salva' in request.POST:
                operatore=User.objects.get(username=name)
                lista_canc=[]
                listaaliq=json.loads(request.POST.get('dati'))
                print 'listaaliq',listaaliq
                for gen in listaaliq:
                    aliq=Aliquot.objects.get(uniqueGenealogyID=gen)
                    lista1=AliquotLabelSchedule.objects.filter(idAliquot=aliq,executed=0,fileInserted=0,operator=operatore,deleteTimestamp=None)
                    lista2=AliquotLabelSchedule.objects.filter(idAliquot=aliq,executed=0,fileInserted=0,operator=None,deleteTimestamp=None)
                    listaaldersched=list(chain(lista1,lista2))
                    print 'listalabelsched',listaaldersched
                    if len(listaaldersched)!=0:
                        aldersched=listaaldersched[0]
                        print 'label da canc',aldersched
                        #cancello la pianificazione
                        aldersched.deleteTimestamp=timezone.localtime(timezone.now())
                        aldersched.deleteOperator=operatore
                        aldersched.save()
                        lista_canc.append(aldersched)
                request.session['listalabeldacanc']=lista_canc
                print 'listaaliq',lista_canc
                return HttpResponse()
            if 'final' in request.POST:
                lista=[]
                laliq=[]
                listar=request.session.get('listalabeldacanc')
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
                    dat=revsch.idLabelSchedule.scheduleDate
                    data2=str(dat).split('-')
                    d=data2[2]+'-'+data2[1]+'-'+data2[0]
                    print 'd',d
                    valori=diz[revsch.idAliquot.uniqueGenealogyID]
                    val=valori[0].split('|')
                    barc=val[1]
                    pos=val[2]
                        
                    lista.append(ReportScheduleCancToHtml(i+1,revsch.idAliquot.uniqueGenealogyID,barc,pos,revsch.idLabelSchedule.operator.username,d,'n'))
                print 'lista',lista
                
                InviaMail('Label',name,laliq,listar,diz)

                variables = RequestContext(request,{'lista_sch':lista})
                return render_to_response('tissue2/revalue/cancel.html',variables)
    except Exception,e:
        print 'err',e
        transaction.rollback()
        variables = RequestContext(request, {'errore':True})
        return render_to_response('tissue2/index.html',variables)

#dopo aver validato serve a far comparire la schermata di esecuzione effettiva
@laslogin_required
@login_required
@permission_decorator('tissue.can_view_BBM_execute_labelling')
def ExecEffectiveLabelAliquots(request):
    try:
        print request.POST
        name=request.user.username
        operatore=User.objects.get(username=name)
        if request.method=='POST':
            dizfinale={}
            lisbarcordinata=[]
            lgen=[]
            if 'salva' in request.POST:
                listagen=json.loads(request.POST.get('lgen'))
                print 'listagen',listagen
                request.session['listaaliqlabel']=listagen
                return HttpResponse()
            if 'conferma' in request.POST:
                adesso=timezone.localtime(timezone.now())
                print 'adesso',adesso
                #metto i secondi a zero in modo di partire dal minuto preciso. Poi ad ogni convalida aggiungo un secondo
                adesso=adesso.replace(second=0, microsecond=0)
                listagen=request.session.get('listaaliqlabel')                
                lisaliq=Aliquot.objects.filter(uniqueGenealogyID__in=listagen,availability=1)
                print 'lisaliq',lisaliq
                lis1=AliquotLabelSchedule.objects.filter(idAliquot__in=lisaliq,executed=0,fileInserted=0,operator=operatore,deleteTimestamp=None)
                lis2=AliquotLabelSchedule.objects.filter(idAliquot__in=lisaliq,executed=0,fileInserted=0,operator=None,deleteTimestamp=None)
                lisqual=list(chain(lis1,lis2))                
                strgen=''
                lisfin=[]
                i=0
                #ad ogni campione aggiungo 1 secondo al tempo di validazione
                for qual in lisqual:
                    lgen.append(qual.idAliquot.uniqueGenealogyID)
                    strgen+=qual.idAliquot.uniqueGenealogyID+'&'
                    tempovalidaz=adesso+timezone.timedelta(seconds=i)
                    qual.validationTimestamp=tempovalidaz
                    qual.save()
                    i+=1
                    print 'aliquota_label',qual.idAliquot
                
                for gen in listagen:
                    for qual in lisqual:
                        if qual.idAliquot.uniqueGenealogyID==gen:
                            lisfin.append(qual)
                
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

                request.session['listagen']={}
                
                lgenfin=strgen[:-1]
                diz=AllAliquotsContainer(lgenfin)
                
                #diz con chiave il barcode e valore il tipo di aliquota (PS o OS)
                dizbarc={}
                for alsched in lisfin:
                    valori=diz[alsched.idAliquot.uniqueGenealogyID]
                    val=valori[0].split('|')
                    barcode=val[1]
                    if barcode not in lisbarcordinata:
                        lisbarcordinata.append(barcode)
                    dizbarc[barcode]=alsched.idAliquot.idAliquotType.abbreviation
                print 'dizbarc',dizbarc
                request.META['HTTP_WORKINGGROUPS']=get_WG_string()
                tab=TableHandler()                
                for k, val in dizbarc.items():
                    codhtml=tab.read(request, k, val,None)
                    val=codhtml['data']
                    dizfinale[k]=val[0:len(val)-12]
                print 'lisbarcordinata',lisbarcordinata
                print 'dizfinale',dizfinale
                
            lprot=LabelProtocol.objects.all()
            dizgen={}
            dizfeaturemark={}
            #dizionario con chiave il tipo del marker e valore le 2 feature relative a tempo e temperatura
            dizmarkfeature={}
            #dizionario con chiave la tecnica e valore la lista dei canali o degli agenti rivelatori
            dizcanali={}
            #diz con chiave la tecnica e valore la lista di protocolli collegati
            diztecnica={}
            for pr in lprot:
                #prendo le feature del protocollo
                lfeat=LabelProtocolLabelFeature.objects.filter(idLabelProtocol=pr)
                diztemp={}
                lismark=[]                    
                for feat in lfeat:
                    if feat.idLabelFeature!=None:
                        if feat.idLabelFeature.type=='Technique':
                            nometecnica=feat.idLabelFeature.name
                            diztemp['tecnica']=nometecnica
                            #popolo il dizionario che, data una tecnica, mi da' la lista di protocolli
                            if nometecnica in diztecnica:
                                listemp=diztecnica[nometecnica]
                            else:
                                listemp=[]
                            if pr.id not in listemp:
                                listemp.append(pr.id)
                            diztecnica[nometecnica]=listemp
                            
                            #prendo le feature figlie della tecnica solo se non ci sono gia' nel dizionario
                            if nometecnica not in dizcanali:
                                lisfeat=LabelFeatureHierarchy.objects.filter(idFatherFeature=feat.idLabelFeature)
                                for fe in lisfeat:
                                    if fe.idChildFeature.type=='Channel' or fe.idChildFeature.type=='Agent':
                                        if nometecnica in dizcanali:
                                            liscanali=dizcanali[nometecnica]
                                        else:
                                            liscanali=[]
                                        liscanali.append({'name':fe.idChildFeature.name,'id':fe.idChildFeature.id})
                                        dizcanali[nometecnica]=liscanali
                    
                    if feat.idLabelMarker!=None:
                        dizmark={}
                        #prendo le feature del marker
                        lfeatmark=LabelMarkerLabelFeature.objects.filter(idLabelMarker=feat.idLabelMarker)
                        dizfeaturemark[feat.idLabelMarker.name]=lfeatmark
                        tipo=''
                        dizfeat={}
                        for fmark in lfeatmark:
                            if fmark.idLabelFeature.type=='Marker':
                                #prendo tutte le feature teoriche che puo' avere un marker e poi guardo
                                #quali di queste hanno gia' un valore
                                lisfeatteoriche=LabelFeatureHierarchy.objects.filter(idFatherFeature=fmark.idLabelFeature)
                                for ff in lisfeatteoriche:
                                    if ff.idChildFeature.type=='Time':
                                        dizfeat['time']={'name':ff.idChildFeature.name,'unit':ff.idChildFeature.measureUnit}
                                    if ff.idChildFeature.type=='Temperature':
                                        dizfeat['temperature']={'name':ff.idChildFeature.name,'unit':ff.idChildFeature.measureUnit}
                                    dizmark[ff.idChildFeature.name]=''
                                dizmark['name']=feat.idLabelMarker.name
                                tipo=fmark.idLabelFeature.name
                                dizmark['type']=tipo
                                
                        dizmarkfeature[tipo]=dizfeat
                        lismark.append(dizmark)
                diztemp['marker']=lismark
                dizgen[pr.id]=diztemp
            print 'dizcanali',dizcanali
            print 'diztecnica', diztecnica
            print 'dizmarkfeature',dizmarkfeature
            print 'dizgen',dizgen
            #devo riempire il dizionario con le feature del marker, se presenti
            for pr in dizgen:
                for diz in dizgen[pr]['marker']:
                    #diz e' il dizionario con dentro i valori di ogni singolo marker
                    lisfeature=dizfeaturemark[diz['name']]
                    print 'lisfeature',lisfeature
                    for k in diz.keys():
                        for feat in lisfeature:
                            if feat.idLabelFeature.name==k:
                                diz[k]=feat.value
            print 'dizgen dopo',dizgen
                                
        variables = RequestContext(request,{'listabarc':lisbarcordinata,'dizfin':dizfinale,'lisprot':lprot,'dizgen':json.dumps(dizgen),'dizmarkfeature':json.dumps(dizmarkfeature),'dizcanali':json.dumps(dizcanali),'diztecnica':json.dumps(diztecnica),'lgen':json.dumps(lgen)})
        return render_to_response('tissue2/label/details.html',variables)
    except Exception,e:
        print 'err',e
        variables = RequestContext(request, {'errore':True})
        return render_to_response('tissue2/index.html',variables)
    
#per definire nuovi protocolli di colorazione
@transaction.commit_on_success
@laslogin_required
@login_required
@permission_decorator('tissue.can_view_BBM_execute_labelling')
def DefineLabelProtocol(request):
    try:
        if request.method=='POST':
            print request.POST
            if 'salva' in request.POST:
                lismarker=json.loads(request.POST.get('dati'))
                print 'lismarker',lismarker
                request.session['listaMarkerProtocollo']=lismarker
                return HttpResponse()
            if 'final' in request.POST:
                print request.FILES
                nome=request.POST.get('name')
                tecn=request.POST.get('Technique')
                feattecnica=LabelFeature.objects.get(id=tecn,type='Technique')
                lismark=request.session.get('listaMarkerProtocollo')
                nomefile=''
                strmarker=''
                lprot=LabelProtocol.objects.filter(name=nome)
                if len(lprot)==0:
                    prot=LabelProtocol(name=nome)
                    prot.save()                
                    #per la tecnica
                    labprotfeat=LabelProtocolLabelFeature(idLabelProtocol=prot,
                                                          idLabelFeature=feattecnica,
                                                          value=feattecnica.name)
                    labprotfeat.save()
                    print 'feattecnica',labprotfeat
                    #per i marker                    
                    for m in lismark:
                        mark=LabelMarker.objects.get(name=m)
                        strmarker+=m+' - '
                        labprotfeat=LabelProtocolLabelFeature(idLabelProtocol=prot,
                                                              idLabelMarker=mark)
                        labprotfeat.save()
                    strmarker=strmarker[0:len(strmarker)-3]                    
                    if 'file'in request.FILES:
                        filemarker=request.FILES.get('file')
                        listFiles = [os.path.join(settings.TEMP_URL, filemarker.name)]
                        
                        destination = handle_uploaded_file(filemarker,settings.TEMP_URL)
                        print 'destination',destination
                        
                        responseUpload = uploadRepFile({'operator':request.user.username}, os.path.join(TEMP_URL, filemarker.name))
                        print 'response upload',responseUpload
                        if responseUpload == 'Fail':
                            raise Exception
                        remove_uploaded_files(listFiles)
                        
                        featfile=LabelFeature.objects.get(name='Protocol sheet')
                        labprotfeat=LabelProtocolLabelFeature(idLabelProtocol=prot,
                                                          idLabelFeature=featfile,
                                                          value=responseUpload)
                        labprotfeat.save()
                        print 'featfile',labprotfeat
                        nomefile=filemarker.name
                variables = RequestContext(request, {'fine':True,'nome':nome,'technique':feattecnica.name,'marker':strmarker,'file':nomefile})
                return render_to_response('tissue2/label/protocol.html',variables)
        else:
            lfeattecnica=LabelFeature.objects.filter(type='Technique')
            lrelazioni=LabelFeatureHierarchy.objects.filter(idFatherFeature__in=lfeattecnica)
            dizrel={}
            for rel in lrelazioni:
                if rel.idChildFeature.type=='Marker':
                    dizrel[rel.idFatherFeature.id]=rel.idChildFeature.name
            print 'dizrel',dizrel
            lfeatmark=LabelFeature.objects.filter(type='Marker')
            dizmarker={}
            for ff in lfeatmark:
                lisfeature=LabelMarkerLabelFeature.objects.filter(idLabelFeature=ff)
                print 'lisfeature',lisfeature
                listemp=[]
                for feature in lisfeature:
                    listemp.append(feature.idLabelMarker.name)
                dizmarker[ff.name]=listemp
            #prendo la url del modulo di annotazioni che mi serve nel caso voglia inserire un nuovo probe
            servizio=WebService.objects.get(name='NewAnnotation')
            url=Urls.objects.get(idWebService=servizio).url
            variables = RequestContext(request,{'listecn':lfeattecnica,'dizrel':json.dumps(dizrel),'dizmarker':json.dumps(dizmarker),'urlannotaz':url})
            return render_to_response('tissue2/label/protocol.html',variables)
    except Exception,e:
        print 'err',e
        transaction.rollback()
        variables = RequestContext(request, {'errore':True})
        return render_to_response('tissue2/index.html',variables)

#per definire nuovi marker
@transaction.commit_on_success
@laslogin_required
@login_required
@permission_decorator('tissue.can_view_BBM_execute_labelling')
def NewMarker(request):
    try:
        if request.method=='POST':
            print request.POST
            print request.FILES
            #salvo le informazioni del nuovo marker
            #e' il nome proprio del marker
            dizval={}
            nome=request.POST.get('nome')
            prod=request.POST.get('producer')
            diluiz1=request.POST.get('dilution1')
            diluiz2=request.POST.get('dilution2')
            catalog=request.POST.get('catalogue')
            tipomarker=request.POST.get('nomemarker')
            tempo=request.POST.get('time')
            temperatura=request.POST.get('temperature')
            #controllo se c'e' uuid come chiave. C'e' in tutte le tecniche tranne che per l'istologia
            if 'uuid' in request.POST:
                uuid=request.POST.get('uuid')
                if uuid!='':
                    dizval['Uuid']=uuid
            #creo il nuovo marker
            marker=LabelMarker(name=nome)
            marker.save()
            print 'marker',marker
                                    
            dizval[tipomarker]=tipomarker
            if prod!='':
                dizval['Producer']=prod
            if diluiz1!='' and diluiz2!='':
                dizval['Dilution']=diluiz1+':'+diluiz2
            if catalog!='':
                dizval['Catalogue number']=catalog
            if tempo!='' or temperatura!='':
                #prendo il tipo del marker
                feattipomarker=LabelFeature.objects.get(name=tipomarker)
                lrelmarker=LabelFeatureHierarchy.objects.filter(idFatherFeature=feattipomarker)
                for rfiglie in lrelmarker:
                    if rfiglie.idChildFeature.type=='Time':
                        nometempo=rfiglie.idChildFeature.name
                    elif rfiglie.idChildFeature.type=='Temperature':
                        nometemperatura=rfiglie.idChildFeature.name
                if tempo!='':
                    dizval[nometempo]=tempo
                if temperatura!='':
                    dizval[nometemperatura]=temperatura
            
            if 'file'in request.FILES:
                filemarker=request.FILES.get('file')
                listFiles = [os.path.join(settings.TEMP_URL, filemarker.name)]
                
                destination = handle_uploaded_file(filemarker,settings.TEMP_URL)
                print 'destination',destination
                
                responseUpload = uploadRepFile({'operator':request.user.username}, os.path.join(TEMP_URL, filemarker.name))
                print 'response upload',responseUpload
                if responseUpload == 'Fail':
                    raise Exception
                remove_uploaded_files(listFiles)
                dizval['Marker sheet']=responseUpload
            
            for key,val in dizval.items():        
                #salvo le feature
                feattipo=LabelFeature.objects.get(name=key)
                markfeat=LabelMarkerLabelFeature(idLabelMarker=marker,
                                                 idLabelFeature=feattipo,
                                                 value=val)
                markfeat.save()
                print 'markfeat',markfeat
            variables = RequestContext(request,{'fine':True,'nomemarker':marker.name,'tipomarker':tipomarker})
            return render_to_response('tissue2/label/newMarker.html',variables)
        else:
            print request.GET
            tecnica=request.GET['technique']
            feattecnica=LabelFeature.objects.get(id=tecnica)
            lrelazioni=LabelFeatureHierarchy.objects.filter(idFatherFeature=feattecnica)
            dizrel={}
            for rel in lrelazioni:
                diztemp={}
                if rel.idChildFeature.type=='Marker':
                    diztemp['name']=rel.idChildFeature.name
                    #prendo le relazioni in cui il marker e' padre 
                    lrelmarker=LabelFeatureHierarchy.objects.filter(idFatherFeature=rel.idChildFeature)
                    for rfiglie in lrelmarker:
                        if rfiglie.idChildFeature.type=='Time':
                            diztemp['time']=rfiglie.idChildFeature.name+' ('+rfiglie.idChildFeature.measureUnit+')'
                        elif rfiglie.idChildFeature.type=='Temperature':
                            diztemp['temperature']=rfiglie.idChildFeature.name+' ('+rfiglie.idChildFeature.measureUnit+')'
                    dizrel[rel.idFatherFeature.id]=diztemp
            print 'dizrel',dizrel
            lismarker=list(LabelMarker.objects.all().values_list('name',flat=True))
            print 'lismarker',lismarker
            variables = RequestContext(request,{'dizrel':json.dumps(dizrel),'nometecn':feattecnica.name,'lismarker':json.dumps(lismarker)})
            return render_to_response('tissue2/label/newMarker.html',variables)
    except Exception,e:
        print 'err',e
        transaction.rollback()
        variables = RequestContext(request, {'errore':True})
        return render_to_response('tissue2/index.html',variables)

#per definire nuovi probe le cui informazioni provengono dal modulo di annotazioni
@laslogin_required
@login_required
@permission_decorator('tissue.can_view_BBM_execute_labelling')
def NewProbe(request):
    try:
        print request.GET
        #prendo il nome e lo uuid del probe nel parametro della GET
        nome=request.GET['name']
        uuid=request.GET['uuid']
        #prendo una delle tre tecniche che si basano sui probe. Ade es. la FISH 
        feattecnica=LabelFeature.objects.get(name='FISH')
        lrelazioni=LabelFeatureHierarchy.objects.filter(idFatherFeature=feattecnica)
        dizrel={}
        for rel in lrelazioni:
            diztemp={}
            if rel.idChildFeature.type=='Marker':
                diztemp['name']=rel.idChildFeature.name
                #prendo le relazioni in cui il marker e' padre 
                lrelmarker=LabelFeatureHierarchy.objects.filter(idFatherFeature=rel.idChildFeature)
                for rfiglie in lrelmarker:
                    if rfiglie.idChildFeature.type=='Time':
                        diztemp['time']=rfiglie.idChildFeature.name+' ('+rfiglie.idChildFeature.measureUnit+')'
                    elif rfiglie.idChildFeature.type=='Temperature':
                        diztemp['temperature']=rfiglie.idChildFeature.name+' ('+rfiglie.idChildFeature.measureUnit+')'
                dizrel[rel.idFatherFeature.id]=diztemp
        print 'dizrel',dizrel
        lismarker=list(LabelMarker.objects.all().values_list('name',flat=True))
        print 'lismarker',lismarker
        variables = RequestContext(request,{'dizrel':json.dumps(dizrel),'nometecn':feattecnica.name,'idtecnica':feattecnica.id,'lismarker':json.dumps(lismarker),'nomeprobe':nome,'uuid':uuid})
        return render_to_response('tissue2/label/newMarker.html',variables)
    except Exception,e:
        print 'err',e
        variables = RequestContext(request, {'errore':True})
        return render_to_response('tissue2/index.html',variables)

#per cercare i probe in base al gene
@laslogin_required
@login_required
@permission_decorator('tissue.can_view_BBM_execute_labelling')
def SearchProbe(request):
    try:
        variables = RequestContext(request,{'tipomarker':'Probe'})
        return render_to_response('tissue2/label/searchProbe.html',variables)
    except Exception,e:
        print 'err',e
        variables = RequestContext(request, {'errore':True})
        return render_to_response('tissue2/index.html',variables)
    
@laslogin_required    
@transaction.commit_on_success
@login_required
@permission_decorator('tissue.can_view_BBM_execute_labelling')
def SaveLabelAliquots(request):
    if request.method=='POST':
        print request.POST
        name=request.user.username
        operatore=User.objects.get(username=name)
        try:           
            if 'final' in request.POST or 'next' in request.POST:
                listafin=request.session.get('lisFinalLabelAliquot')
                print 'listafin',listafin
                lista=[]
                dizvalori={}
                for i in range(0,len(listafin)):
                    s=listafin[i].split(',')
                    lista.append(ReportToHtml([i+1,s[0],s[1],s[6],s[7]]))
                    #dizionario con chiave il gen e valore barc|pos
                    dizvalori[s[0]]=s[1]+'|'+s[6]
                
                listaaliqlabel=request.session.get('lisFinalNewAliquotLabel')
                print 'listalabel',listaaliqlabel
                email = LASEmail (functionality=get_functionality(), wgString=get_WG_string())
                msg=['Slides labelling executed','','Assigned to:\t'+name,'','Aliquots:','N\tGenealogy ID\tBarcode\tPosition']                    
                print 'lista label',listaaliqlabel
                lisgen=[]
                dizmadri={}
                #listaaliqlabel ha dentro le aliq create
                for al in listaaliqlabel:
                    #devo risalire alle madri dei vetrini, perche' la divisione fra wg proprietari la faccio sulle madri
                    #e non sulle figlie che non esistono ancora nell'Aliquot_wg, visto che vengono create alla fine di tutto
                    alder=AliquotLabelSchedule.objects.get(idSamplingEvent=al.idSamplingEvent,operator=User.objects.get(username=name))
                    lisgen.append(alder.idAliquot.uniqueGenealogyID)
                    #faccio un dizionario con figlie come chiave e valore la madre
                    dizmadri[al.uniqueGenealogyID]=alder.idAliquot.uniqueGenealogyID
                #non metto availability=1 perche' se la madre e' esaurita non me la prende e non va bene
                aliquots=Aliquot.objects.filter(uniqueGenealogyID__in=lisgen)
                wgList=WG.objects.filter(id__in=Aliquot_WG.objects.filter(aliquot__in=aliquots).values_list('WG',flat=True).distinct())
                print 'wglist',wgList
                print 'dizmadri',dizmadri
                for wg in wgList:
                    print 'wg',wg
                    email.addMsg([wg.name], msg)
                    #aliq ha dentro le madri
                    aliq=aliquots.filter(id__in=Aliquot_WG.objects.filter(WG=wg).values_list('aliquot',flat=True).distinct())
                    print 'aliq',aliq
                    i=1
                    lisplanner=[]
                    #per mantenere l'ordine dei campioni anche nell'e-mail
                    for aliqder in listaaliqlabel:
                        for al in aliq:
                            #guardo nel dizionario delle madri se il loro rapporto e' corretto
                            madre=dizmadri[aliqder.uniqueGenealogyID]
                            print 'madre',madre
                            if madre==al.uniqueGenealogyID:
                                lval=dizvalori[aliqder.uniqueGenealogyID]
                                vv=lval.split('|')                                    
                                email.addMsg([wg.name],[str(i)+'\t'+aliqder.uniqueGenealogyID+'\t'+vv[0]+'\t'+vv[1]])
                                i=i+1
                                alsched=AliquotLabelSchedule.objects.get(idSamplingEvent=aliqder.idSamplingEvent,operator=User.objects.get(username=name))
                                if alsched.idLabelSchedule.operator.username not in lisplanner:
                                    lisplanner.append(alsched.idLabelSchedule.operator.username)
                    print 'lisplanner',lisplanner
                    #mando l'e-mail al pianificatore
                    email.addRoleEmail([wg.name], 'Planner', lisplanner)
                    email.addRoleEmail([wg.name], 'Executor', [request.user.username])
                try:
                    email.send()
                except Exception, e:
                    print 'err label last step:',e
                    pass
                if 'final' in request.POST:
                    variables = RequestContext(request,{'fine':True,'lista_der':lista})
                    return render_to_response('tissue2/label/details.html',variables)
                elif 'next' in request.POST:
                    return InsertFile(request)
            if 'salva' in request.POST:
                #diz con chiave gen|barc|pos|idprot e valore un dizionario con i valori di ogni singolo marker
                dizaliq=json.loads(request.POST.get('dati'))
                dizconf={}                
                for key,dizgen in dizaliq.items():
                    lisk=key.split('|')
                    k=lisk[0]
                    idprot=lisk[3]
                    numfeature=0
                    for chiave,valore in dizgen.items():
                        numfeature+=len(valore.items())
                    dizconf[k]=None
                    labprotocol=LabelProtocol.objects.get(id=idprot)
                    #devo vedere se una configurazione di questo tipo c'e' gia' tra quelle salvate
                    #lo faccio all'interno del ciclo for perche' magari dopo salvo una nuova configurazione e al prossimo passaggio
                    #ho bisogno di tenerne conto
                    lisconf=LabelConfiguration.objects.all().order_by('id')
                    for conf in lisconf:
                        ris=0
                        #lo faccio all'interno del ciclo for perche' magari dopo salvo una nuova configurazione e al prossimo passaggio
                        #ho bisogno di tenerne conto
                        lisfeat=LabelConfigurationLabelFeature.objects.filter(idLabelConfiguration=conf)
                        #ho la lista di tutte le feature di una configurazione
                        for feat in lisfeat:
                            print 'feat',feat
                            #prendo i dizionari con i dati reali per ogni marker inserito nella schermata. La chiave e' il nome del marker
                            for chiave,valore in dizgen.items():
                                print 'chiave',chiave
                                print 'valore',valore
                                if chiave==feat.idLabelMarker.name:
                                    #il marker e' quello giusto. Adesso devo scandire le altre feature per vedere se coincide tutto
                                    for ch, vv in valore.items():
                                        if feat.idLabelFeature.name==ch and feat.value==vv:
                                            ris+=1
                        print 'ris',ris
                        print 'numfeat',numfeature
                        if numfeature>0 and numfeature==ris:
                            #ho trovato la configurazione giusta
                            dizconf[k]=conf
                            break
                    print 'dizconf',dizconf
                    #creo una nuova configurazione per fare in modo che se due campioni di questa sessione hanno la stessa configurazione, 
                    #per il secondo campione la individuo e non ne creo un'altra
                    if dizconf[k]==None:
                        if len(lisconf)==0:
                            ultimoid=0
                        else:
                            ultimoid=lisconf[len(lisconf)-1].id
                        #chiamo la nuova configurazione con l'ultimo id +1
                        idfin=str(int(ultimoid)+1)
                        nomeconf='configuration_'+idfin
                        conf=LabelConfiguration(name=nomeconf,
                                                idLabelProtocol=labprotocol)
                        conf.save()
                        #prendo i dizionari con i dati reali per ogni marker inseriti nella schermata. La chiave e' il nome del marker
                        for chiave,valore in dizgen.items():
                            mark=LabelMarker.objects.get(name=chiave)
                            for ch, vv in valore.items():
                                feat=LabelFeature.objects.get(name=ch)
                                labelfeat=LabelConfigurationLabelFeature(idLabelConfiguration=conf,
                                                                         idLabelFeature=feat,
                                                                         idLabelMarker=mark,
                                                                         value=vv)
                                labelfeat.save()
                                print 'labelfeat',labelfeat
                        dizconf[k]=conf
                
                listaaliqslide=[]
                lisgencanc=[]
                lislabelnuove=[]
                tipofiglials=AliquotType.objects.get(abbreviation='LS')
                listempgen=[]
                for gg in dizaliq.keys():
                    gg2=gg.split('|')
                    gen=gg2[0]
                    listempgen.append(gen)
                #per prendere gli aliquotlabelschedule non posso passarmeli dalla vista precedente, perche' magari ne e' stato inserito
                #qualcuno direttamente dalla schermata                
                lisaliq=Aliquot.objects.filter(uniqueGenealogyID__in=listempgen,availability=1)
                lis1=AliquotLabelSchedule.objects.filter(idAliquot__in=lisaliq,executed=0,fileInserted=0,operator=operatore,deleteTimestamp=None)
                lis2=AliquotLabelSchedule.objects.filter(idAliquot__in=lisaliq,executed=0,fileInserted=0,operator=None,deleteTimestamp=None)
                lisqual=list(chain(lis1,lis2))
                for gg in dizaliq.keys():
                    gg2=gg.split('|')
                    gen=gg2[0]
                    lisgencanc.append(gen)
                    for qual in lisqual:
                        if gen==qual.idAliquot.uniqueGenealogyID:
                            qual.executed=1
                            qual.executionDate=date.today()
                            qual.idLabelConfiguration=dizconf[qual.idAliquot.uniqueGenealogyID]
                                                        
                            al=qual.idAliquot
                            gg=GenealogyID(gen)                
                            stringa=gg.getPartForDerAliq()
                            #aggiungo il tipo di derivato che voglio ottenere
                            stringa2=stringa+'LS'
                            disable_graph()
                            #guardo se quell'inizio di genealogy ce l'ha gia' qualche LS
                            lista_aliquote_LS=Aliquot.objects.filter(uniqueGenealogyID__startswith=stringa2).order_by('-uniqueGenealogyID')
                            enable_graph()
                            
                            print 'lista_aliquote_LS',lista_aliquote_LS
                            if lista_aliquote_LS.count()!=0:
                                #prendo il primo oggetto, che e' quello che ha il contatore piu' alto
                                maxgen=lista_aliquote_LS[0].uniqueGenealogyID
                                nuovoge=GenealogyID(maxgen)
                                maxcont=nuovoge.getAliquotExtraction()
                                contls=int(maxcont)
                            else:
                                contls=0
                            print 'contls',contls
                            
                            ser,creato=Serie.objects.get_or_create(operator=operatore,
                                                               serieDate=date.today())
                            
                            #salvo il sampling event
                            samp_ev=SamplingEvent(idTissueType=al.idSamplingEvent.idTissueType,
                                                idCollection=al.idSamplingEvent.idCollection,
                                                idSource=al.idSamplingEvent.idCollection.idSource,
                                                idSerie=ser,
                                                samplingDate=date.today())
                            samp_ev.save()
                            
                            contls=contls+1                                
                            contatore=str(contls).zfill(2)                        
                            genfiglia=gg.getPartForDerAliq()+'LS'+contatore+'00'
                            #se la madre e' gia' stata archiviata allora imposto anche nell'LS la stessa data di archiviazione
                            dataarch=None
                            if al.archiveDate!=None:
                                dataarch=al.archiveDate                        
                            #il barcode e' lo stesso della madre perche' non c'e' un cambiamento di posto
                            aliquota=Aliquot(barcodeID=al.barcodeID,
                                       uniqueGenealogyID=genfiglia,
                                       idSamplingEvent=samp_ev,
                                       idAliquotType=tipofiglials,
                                       availability=1,
                                       timesUsed=0,
                                       derived=0,
                                       archiveDate=dataarch)
                            aliquota.save()
                            print 'al label',aliquota
                            lislabelnuove.append(aliquota)
                            #la geometria del vetrino non serve perche' esiste gia' ed e' lo spazio vuoto dopo SlideMicrotome
                            #gg2[1] e' il codice del vetrino, mentre gg2[2] e' la posizione
                            valori=genfiglia+','+gg2[1]+','+tipofiglials.abbreviation+','+str(date.today())+',SlideMicrotome,'','+gg2[2]+','+al.uniqueGenealogyID
                            listaaliqslide.append(valori)
                            #cancello la madre, la cui figlia ne ha preso il posto
                            al.availability=0
                            al.save()
                            qual.idSamplingEvent=samp_ev
                            if qual.operator==None:
                                qual.operator=request.user
                            qual.save()
                request.session['lisFinalLabelAliquot']=listaaliqslide
                request.session['lisFinalNewAliquotLabel']=lislabelnuove
                if len(listaaliqslide)!=0:
                    #salvo le nuove aliquote nello storage
                    url1 = Urls.objects.get(default = '1').url + "/api/save/slide/"
                    val1={'lista':json.dumps(listaaliqslide),'user':operatore}
                    print 'url1',url1
                    data = urllib.urlencode(val1)
                    req = urllib2.Request(url1,data=data, headers={"workingGroups" : get_WG_string()})
                    u = urllib2.urlopen(req)
                    res1 =  json.loads(u.read())
                    print 'res1',res1
                    if res1['data']=='err':
                        raise Exception
                #cancello dopo aver salvato nello storage perche' se colorassi tutto un vetrino e cancellassi prima di salvare, mi 
                #eliminerebbe anche il vetrino stesso
                if len(lisgencanc)!=0:
                    svuotare=json.dumps(lisgencanc)
                    #mi collego allo storage per svuotare le provette contenenti le aliq
                    #esaurite
                    address=Urls.objects.get(default=1).url
                    url = address+"/full/"
                    print url
                    values = {'lista' : svuotare, 'tube': 'empty','canc':True,'operator':name}
                    data = urllib.urlencode(values)
                    req = urllib2.Request(url,data=data, headers={"workingGroups" : get_WG_string()})
                    urllib2.urlopen(req)
                    
                return HttpResponse()
        except Exception,e:
            print 'err',e
            transaction.rollback()
            variables = RequestContext(request, {'errore':True})
            return render_to_response('tissue2/index.html',variables)

#per far comparire la schermata per inserire i file
@laslogin_required
@login_required
@permission_decorator('tissue.can_view_BBM_manage_label_file')
def InsertFile(request):
    try:        
        operatore=request.user
        lis1=AliquotLabelSchedule.objects.filter(executed=1,fileInserted=0,operator=operatore,deleteTimestamp=None).order_by('validationTimestamp')
        lis2=AliquotLabelSchedule.objects.filter(executed=1,fileInserted=0,operator=None,deleteTimestamp=None).order_by('validationTimestamp')
        lisqual=list(chain(lis1,lis2))
        
        lisfin=[]
        strgen=''
        dizfin={}
        #chiave il gen dell'LS e valore il protocollo e la data
        dizdati={}
        print 'lisqual',lisqual
        for qual in lisqual:            
            #devo prendere l'aliquota figlia del vetrino, quindi la LS
            aliq=Aliquot.objects.get(idSamplingEvent=qual.idSamplingEvent,availability=1)
            lisfin.append(aliq)
            strgen+=aliq.uniqueGenealogyID+'&'
            dizfin[qual]=aliq
            data=str(qual.executionDate)
            protocollo=qual.idLabelConfiguration.idLabelProtocol.name
            dizdati[aliq.uniqueGenealogyID]={'date':data,'prot':protocollo}
        
        lgenfin=strgen[:-1]
        diz=AllAliquotsContainer(lgenfin)
        lisbarc=[]
        lispos=[]                
        print 'lisfin',lisfin
        for al in lisfin:
            valori=diz[al.uniqueGenealogyID]
            val=valori[0].split('|')
            barcode=val[1]
            position=val[2]
            lisbarc.append(barcode)
            lispos.append(position)
        request.session['dizaliqlabel']=diz
        request.session['dizlabelinsertfile']=dizfin
        request.session['dizlabelsavefile']={}
        
        variables = RequestContext(request,{'lista':zip(lisfin,lisbarc,lispos,lisqual),'dizdati':json.dumps(dizdati)})
        return render_to_response('tissue2/label/fileInsert.html',variables)  
    except Exception,e:
        print 'err',e
        variables = RequestContext(request, {'errore':True})
        return render_to_response('tissue2/index.html',variables)
    
#per salvare i file inseriti
@laslogin_required
@transaction.commit_on_success
@login_required
@permission_decorator('tissue.can_view_BBM_manage_label_file')
def SaveFile(request):
    print request.POST
    print request.FILES
    
    try:
        if 'dati' in request.POST:
            #faccio una POST dalla schermata per comunicare il dizionario con dentro la corrispondenza tra nome file nuovo e nome vecchio
            dizdati=json.loads(request.POST['diz'])
            print 'dizdati',dizdati
            request.session['dizlabelsavefile']=dizdati
            return HttpResponse()
        else:
            #diz con chiave il nome vecchio del file e valore un diz con chiave "newname" che ha il nome file nuovo
            dizdati=request.session.get('dizlabelsavefile')
            #diz con chiave l'aliqlabelsched e valore l'aliq figlia (la LS)
            dizlabel=request.session.get('dizlabelinsertfile')
            #diz con chiave il gen e valore un diz con una lista con il nome dei file e l'aliquotlabelsched
            dizgenfile={}
            strgen=''
            genAn = GenomicAnalysis()
            lisgenealogy=[]
            #cerco se ci sono dei nofile per salvare che non e' stato inserito nessun file
            for key in request.POST.keys():
                if key.startswith('nofile'):
                    #prendo l'indice del nofile
                    indice=key.split('_')[1]
                    #prendo il gen
                    genpost=request.POST.get('gen_'+str(indice))
                    print 'genpost',genpost
                    lisgenealogy.append(genpost)
            for k in request.FILES.keys():
                genid=k.split('_')[0]
                if genid not in lisgenealogy:
                    lisgenealogy.append(genid)
            print 'lisgenealogy',lisgenealogy
            
            for idgen in lisgenealogy:
                labsched=None
                for k,v in dizlabel.items():
                        #ciclo sui gen del dizionario con le procedure pianificate
                        gendiz=v.uniqueGenealogyID
                        if idgen==gendiz:
                            labsched=k
                            break
                print 'labsched',labsched
                #se non ho ancora trovato il labelschedule, allora devo accedere al DB perche' vuol dire che questo campione e'
                #stato inserito manualmente dall'utente nella schermata
                if labsched==None:
                    aliq=Aliquot.objects.get(uniqueGenealogyID=idgen,availability=1)
                    labsched=AliquotLabelSchedule.objects.filter(idSamplingEvent=aliq.idSamplingEvent,executed=1,fileInserted=1,deleteTimestamp=None)[0]
                    strgen+=aliq.uniqueGenealogyID+'&'
                #metto la data di oggi anche per i file caricati dopo vario tempo dal primo inserimento    
                labsched.fileInsertionDate=date.today()
                labsched.fileInserted=1
                labsched.save()
                #inserisco nel dizionario del report finale il campione sia che abbia impostato il "no file"
                #sia che abbia inserito effettivamente un file
                dizgenfile[idgen]={'aliqlabel':labsched,'listfile':[]}
            
            #salvo effettivamente i file
            listFiles=[]
            for k,v in request.FILES.items():
                genid=k.split('_')[0]
                print 'v',v
                print 'dizdati',dizdati
                
                destination = handle_uploaded_file(v,settings.TEMP_URL)
                print 'destination',destination
                estensione=os.path.splitext(destination)[1]
                print 'estensione',estensione
                #in v ho il nome originale del file, ma io lo devo rimappare leggendo nel dizionario
                nuovonome=dizdati[v.name]['newname']
                nuovopercorso=settings.TEMP_URL+nuovonome+estensione
                print 'nuovo',nuovopercorso
                os.rename(destination, nuovopercorso)
                listFiles.append(nuovopercorso)
                responseUpload = uploadRepFile({'operator':request.user.username}, nuovopercorso)
                print 'response upload',responseUpload
                if responseUpload == 'Fail':
                    transaction.rollback()
                    raise Exception
                
                #creo il nodo raw passandogli l'id di mongo db che verra' salvato come label insieme a uno uuid casuale
                #che mi salvo nel DB per potermi riferire, al momento dell'analisi, a quel nodo raw data. Passo anche il gen
                #del campione coinvolto e mi crea una relazione tra nodo raw data e nodo aliquota
                
                raw_uuid = genAn.createRawData(target_genid=genid,data_link=responseUpload)                
                print 'raw_uuid ', raw_uuid
                labsched=dizgenfile[genid]['aliqlabel']
                labelfile=LabelFile(idAliquotLabelSchedule=labsched,
                                    fileName=nuovonome+estensione,
                                    originalFileName=v.name,
                                    fileId=responseUpload,
                                    rawNodeId=raw_uuid)
                labelfile.save()
                
                #listnomifile.append(nuovonome+estensione)
                
                dizgenfile[genid]['listfile'].append(nuovonome+estensione)
            print 'listfiles',listFiles
            remove_uploaded_files(listFiles)
                        
            dizfin=request.session.get('dizaliqlabel')
            lista=[]
            diz={}
            if strgen!='':
                lgenfin=strgen[:-1]
                diz=AllAliquotsContainer(lgenfin)
            #unisco il dizionario preso dalla sessione, che contiene i campioni a cui devo ancora inserire un file, con 
            #quello creato adesso che contiene i campioni inseriti a mano dall'utente nella schermata
            dizfin.update(diz)
            print 'dizfin',dizfin
            print 'dizgenfile',dizgenfile
            i=1
            #k e' il gen
            for k, valore in dizgenfile.items():
                print 'k',k
                print 'valore',valore
                strnomifile=''
                for val in valore['listfile']:
                    strnomifile+=val+'; '
                strnomifile=strnomifile[:len(strnomifile)-2]
                print 'nomifile',strnomifile
                posti=dizfin[k]
                val2=posti[0].split('|')
                print 'val2',val2
                barc=val2[1]
                pos=val2[2]
                
                lista.append(ReportToHtml([str(i),k,barc,pos,strnomifile]))
                i+=1            
                       
            print 'lista finale',lista                    
            if request.session.has_key('dizlabelinsertfile'):
                del request.session['dizlabelinsertfile']
            if request.session.has_key('lisaliqlabel'):
                del request.session['lisaliqlabel']
            
            request.session['listafinalesalvafile']=lista
            urlfin=settings.DOMAIN_URL+settings.HOST_URL+'/label/save/final/'
            print 'urlfin',urlfin
            
            return HttpResponseRedirect(urlfin)
                
    except Exception,e:
        print 'err',e
        transaction.rollback()
        variables = RequestContext(request, {'errore':True})
        return render_to_response('tissue2/index.html',variables)

#per far vedere il report finale del salvataggio dei file
@laslogin_required
@login_required
@permission_decorator('tissue.can_view_BBM_manage_label_file')
def SaveFileFinal(request):
    lista=request.session.get('listafinalesalvafile')
    variables = RequestContext(request,{'fine':True,'lista_fin':lista})
    return render_to_response('tissue2/label/fileInsert.html',variables)

#per far vedere la schermata che permette di scaricare i file salvati prima   
@laslogin_required
@login_required
@permission_decorator('tissue.can_view_BBM_manage_label_file')
def DownloadFileInit(request):
    mdamTemplates = getMdamTemplates([41,44,45])
    print 'mdamTemplates',mdamTemplates
    mdamurl=Urls.objects.get(idWebService=WebService.objects.get(name='MDAM').id).url
    listot=getGenealogyDict()
    variables = RequestContext(request, {'mdamTemplates':json.dumps(mdamTemplates), 'mdam_url':mdamurl,'genid':json.dumps(listot) })   
    return render_to_response('tissue2/label/download.html',variables)

#per passare alla schermata il contenuto del file che si vuole scaricare
@csrf_exempt
@get_functionality_decorator
def DownloadFileFinal(request):
    try:
        print request.POST
        #e' una lista con dentro stringhe formate da idaliq|idaliqlabelsched|idlabelfile
        sNodesJson = json.loads(request.POST['selectedNodes'])
        dataStruct = json.loads(request.POST['dataStruct'])
        
        sNodes = {}
        selectedNodes = [ s.strip().split('|') for s in sNodesJson ]
        print 'sNodesJson', sNodesJson
        print 'selectedNodes', selectedNodes
        for pathNode in selectedNodes:
            current_level = sNodes
            for part in pathNode:
                if part not in current_level:
                    current_level[part] = {}
                current_level = current_level[part]
        #e' un diz con chiave idaliq e valore un diz con chiave idaliqlabsched e valore un diz con chiave idlabelfile e
        #valore vuoto
        print 'sNodes', sNodes

        tmpDir = request.user.username.replace('.','-') + '_' + str(date.today())
        os.mkdir ( os.path.join(settings.TEMP_URL, tmpDir) )

        repositoryUrl = Urls.objects.get(idWebService=WebService.objects.get(name='Repository').id)

        for sid, sample in dataStruct.items():
            #e' l'id dell'aliq
            print 'sid', sid
            #e' un diz con dentro tutti i dati di quell'aliq
            print 'sample', sample
            #se quell'aliq ha un file selezionato da scaricare da parte dell'utente
            if sNodes.has_key(sid):
                currPath = os.path.join(settings.TEMP_URL, tmpDir, sample['genid'] + '_' + sample['barcode']+'_'+sample['exec_date'] )
                #creo la cartella piu' esterna con gen_barcode_dataesecuzione
                os.mkdir ( currPath )
                for rid, run in sample['runs'].items():
                    if sNodes[sid].has_key(rid):
                        #e' l'idaliqlabelsched
                        print 'rid', rid
                        #e' un diz con dentro i file
                        print 'run',run
                        #currPath = os.path.join(settings.TEMP_URL, tmpDir, sample['genid'] + '_' + sample['barcode'], sample['exec_date'] + '_' + run['notes'] )
                        #os.mkdir ( currPath )
                        for fid, fileSource in run['files'].items():
                            #e' l'idlabelfile
                            print 'fid', fid
                            print 'fileSource', fileSource
                            if sNodes[sid][rid].has_key(fid):
                                link = fileSource['link']
                                r = requests.get(repositoryUrl.url + "/get_file/"+ link, verify=False, stream=True)
                                with open(os.path.join(currPath, fileSource['name']) , 'wb') as f:
                                    for chunk in r.iter_content(chunk_size=1024): 
                                        if chunk: # filter out keep-alive new chunks
                                            f.write(chunk)
                                            f.flush()
        #prima creo la struttura con tutte le cartelle annidate e poi chiamo questa funzione che ne fa il tar gz
        archiveFile = tarfile.open(os.path.join(TEMP_URL, tmpDir + '.tar.gz'),mode='w:gz')
        print 'creato .tar.gz'

        archiveFile.add( os.path.join(settings.TEMP_URL, tmpDir) , arcname=tmpDir)
        print 'aggiunta cartella'
        archiveFile.close()
        
        fout = open(os.path.join(TEMP_URL, tmpDir + '.tar.gz'))
        response = HttpResponse(fout, content_type='application/octet-stream')
        #creo la risposta con dentro il file tar gz che ho creato 
        response['Content-Disposition'] = 'attachment; filename=' + tmpDir + '.tar.gz'
        
        shutil.rmtree( os.path.join(settings.TEMP_URL, tmpDir))
        os.remove(os.path.join(TEMP_URL, tmpDir + '.tar.gz'))
        return response
    except Exception, e:
        print e
        return HttpResponseBadRequest("Error in retrieving data")
    
#per ottenere la lista dei file da visualizzare nella galleria
@csrf_exempt
@get_functionality_decorator
def ViewGallery(request):
    try:
        print request.POST
        #e' una lista con dentro stringhe formate da idaliq|idaliqlabelsched|idlabelfile
        sNodesJson = json.loads(request.POST['selectedNodes'])
        dataStruct = json.loads(request.POST['dataStruct'])
        lislabfeat=LabelFeature.objects.filter(type='Marker')
        sNodes = {}
        selectedNodes = [ s.strip().split('|') for s in sNodesJson ]
        print 'sNodesJson', sNodesJson
        print 'selectedNodes', selectedNodes
        for pathNode in selectedNodes:
            current_level = sNodes
            for part in pathNode:
                if part not in current_level:
                    current_level[part] = {}
                current_level = current_level[part]
        #e' un diz con chiave idaliq e valore un diz con chiave idaliqlabsched e valore un diz con chiave idlabelfile e
        #valore vuoto
        print 'sNodes', sNodes
        #e' la cartella radice all'interno della quale salvo tutti i file da far vedere nella schermata
        tmpDir = 'label'
        #cancello adesso la sessione di prima cosi' cancello la cartella label e tutto quello che c'e' dentro.
        #Questo solo se la cartella esiste
        if os.path.exists(os.path.join(settings.TEMP_URL, tmpDir)):            
            shutil.rmtree( os.path.join(settings.TEMP_URL, tmpDir))
        
        os.mkdir ( os.path.join(settings.TEMP_URL, tmpDir) )
        currPath = os.path.join(settings.TEMP_URL, tmpDir)
        repositoryUrl = Urls.objects.get(idWebService=WebService.objects.get(name='Repository').id)
        
        dizfile={}
        lfeattecnica=LabelFeature.objects.filter(type='Technique')
        for sid, sample in dataStruct.items():
            #e' l'id dell'aliq
            print 'sid', sid
            #e' un diz con dentro tutti i dati di quell'aliq
            print 'sample', sample
            #se quell'aliq ha un file selezionato da scaricare da parte dell'utente
            if sNodes.has_key(sid):
                #currPath = os.path.join(settings.TEMP_URL, tmpDir, sample['genid'] + '_' + sample['barcode']+'_'+sample['exec_date'] )
                #creo la cartella piu' esterna con gen_barcode_dataesecuzione
                #os.mkdir ( currPath )
                for rid, run in sample['runs'].items():
                    if sNodes[sid].has_key(rid):
                        #e' l'idaliqlabelsched
                        print 'rid', rid
                        labsched=AliquotLabelSchedule.objects.get(id=rid)
                        aliq=Aliquot.objects.filter(idSamplingEvent=labsched.idSamplingEvent)
                        #e' un diz con dentro i file
                        print 'run',run
                        for fid, fileSource in run['files'].items():
                            #e' l'idlabelfile
                            print 'fid', fid
                            print 'fileSource', fileSource
                            if sNodes[sid][rid].has_key(fid):
                                diztemp={}
                                link = fileSource['link']
                                r = requests.get(repositoryUrl.url + "/get_file/"+ link, verify=False, stream=True)
                                with open(os.path.join(currPath, fileSource['name']) , 'wb') as f:
                                    for chunk in r.iter_content(chunk_size=1024): 
                                        if chunk: # filter out keep-alive new chunks
                                            f.write(chunk)
                                            f.flush()
                                print 'file caricato'
                                img = Image.open(os.path.join(currPath, fileSource['name']))
                                # get the image's width and height in pixels
                                width, height = img.size
                                diztemp['dim']=str(width)+'x'+str(height)
                                #dizfile[fileSource['name']]={'dimens':str(width)+'x'+str(height)}
                                
                                #devo prendere il marcatore utilizzato in questa procedura
                                lisconf=LabelConfigurationLabelFeature.objects.filter(idLabelConfiguration=labsched.idLabelConfiguration).values_list('idLabelMarker',flat=True).distinct()
                                print 'lisconf',lisconf
                                lfeatmark=LabelMarkerLabelFeature.objects.filter(idLabelMarker__in=lisconf,idLabelFeature__in=lislabfeat)
                                print 'lfeatmark',lfeatmark
                                listemp=[]
                                for feat in lfeatmark:
                                    diz2={}
                                    diz2['nome']=feat.idLabelMarker.name
                                    #in value ho il tipo di marcatore (anticorpo, colorante ecc.)
                                    diz2['tipo']=feat.value
                                    listemp.append(diz2)
                                diztemp['marker']=listemp
                                #metto l'id dell'aliq perche' mi serve dopo nella schermata per andare a recuperare gen e barc del vetrino
                                diztemp['id']=aliq[0].id
                                #prendo il protocollo collegato alla configurazione
                                if labsched.idLabelConfiguration.idLabelProtocol!=None:
                                    diztemp['prot']=labsched.idLabelConfiguration.idLabelProtocol.name
                                    #prendo la tecnica che e' una feature del protocollo
                                    ltecnic=LabelProtocolLabelFeature.objects.filter(idLabelProtocol=labsched.idLabelConfiguration.idLabelProtocol,idLabelFeature__in=lfeattecnica)
                                    print 'ltecnic',ltecnic
                                    diztemp['tecn']=ltecnic[0].value
                                else:
                                    diztemp['prot']=''
                                    diztemp['tecn']=''
                                
                                dizfile[fileSource['name']]=diztemp
        
        print 'dizfile',dizfile
        return HttpResponse(json.dumps(dizfile))
        #return render_to_response('tissue2/label/download.html',variables)
    except Exception, e:
        print 'err',e
        return HttpResponse('error')

#per far vedere la schermata che permette di eliminare i file collegati ad un vetrino
@laslogin_required
@login_required
@permission_decorator('tissue.can_view_BBM_manage_label_file')
def DeleteFile(request):
    print 'BBM label delete file'
    if request.session.has_key('labelDeleteFileFinal'):
        del request.session['labelDeleteFileFinal']
    mdamTemplates = getMdamTemplates([41,44,45])
    print 'mdamTemplates',mdamTemplates
    mdamurl=Urls.objects.get(idWebService=WebService.objects.get(name='MDAM').id).url
    listot=getGenealogyDict()
    variables = RequestContext(request, {'mdamTemplates':json.dumps(mdamTemplates),'mdam_url':mdamurl,'delete':True,'genid':json.dumps(listot) })   
    return render_to_response('tissue2/label/download.html',variables)

#per cancellare i file selezionati
@laslogin_required
@transaction.commit_on_success
@login_required
@permission_decorator('tissue.can_view_BBM_manage_label_file')
def DeleteFileFinal(request):
    print request.POST
    print request.FILES
    try:
        if 'salva' in request.POST:
            operatore=request.user
            #e' una lista con dentro stringhe formate da idaliq|idaliqlabelsched|idlabelfile
            lisdati=json.loads(request.POST['dati'])
            print 'lisdati',lisdati
            #e' un dizionario con chiave idaliq e valore i dati dell'aliquota
            dizaliq=json.loads(request.POST['daticampioni'])
            print 'dizaliq',dizaliq
            lisreport=[]
            #prendo il label file e segno che e' stato cancellato
            lisgenerale=[]            
            dizlabfile={}
            for val in lisdati:
                v=val.strip().split('|')
                lisgenerale.append(v[2])
                #mi serve avere il campione a cui si riferisce il file
                dizlabfile[v[2]]=v[0]
            lislabfile=LabelFile.objects.filter(id__in=lisgenerale)
            print 'lislabfile',lislabfile
            print 'dizlabfile',dizlabfile
            #imposto operatore e data di cancellazione
            i=1
            for f in lislabfile:
                f.deleteTimestamp=timezone.localtime(timezone.now())
                f.deleteOperator=operatore
                f.save()
                print 'f',f
                #devo salvare i dati dei file cancellati per riproporli dopo nel report finale. Li metto in una lista
                #che salvo nella request.session
                idaliq=dizlabfile[str(f.id)]
                val=dizaliq[idaliq]
                print 'val',val
                gen=val['genid']
                barcode=val['barcode']
                lisreport.append(ReportToHtml([str(i),gen,barcode,f.fileName]))
                i+=1
            request.session['labelDeleteFileFinal']=lisreport
            return HttpResponse()
        else:            
            listafin=request.session.get('labelDeleteFileFinal')
            variables = RequestContext(request,{'fine':True,'delete':True,'lista_fin':listafin})
            return render_to_response('tissue2/label/download.html',variables)            
                
    except Exception,e:
        print 'err',e
        transaction.rollback()
        variables = RequestContext(request, {'errore':True})
        return render_to_response('tissue2/index.html',variables)

#per far comparire la schermata in cui inserire i risultati delle analisi
@laslogin_required
@login_required
@permission_decorator('tissue.can_view_BBM_execute_labelling')
def AnalysisResult(request):
    try:
        if request.session.has_key('valoriLabelResult'):
            del request.session['valoriLabelResult']

        lfeattecnica=LabelFeature.objects.filter(type='Technique').order_by('name')
        loperatori=User.objects.all().exclude(first_name='').order_by('last_name')
        print 'lisoper',loperatori
        #chiave la tecnica e valore una lista dei protocolli di colorazione
        dizprot={}
        lisfeat=LabelProtocolLabelFeature.objects.filter(idLabelFeature__in=lfeattecnica).order_by('value')
        for feat in lisfeat:
            if feat.idLabelFeature.name in dizprot:
                listemp=dizprot[feat.idLabelFeature.name]
            else:
                listemp=[]
            vallista=feat.idLabelProtocol.name+'|'+str(feat.idLabelProtocol.id)            
            if vallista not in listemp:
                listemp.append(vallista)
            dizprot[feat.idLabelFeature.name]=listemp
        print 'dizprot',dizprot
        variables = RequestContext(request,{'listecn':lfeattecnica,'lisoper':loperatori,'dizprot':json.dumps(dizprot)})
        return render_to_response('tissue2/label/analysis.html',variables)
    except Exception,e:
        print 'err',e
        variables = RequestContext(request, {'errore':True})
        return render_to_response('tissue2/index.html',variables)

#per salvare i risultati delle analisi
@laslogin_required
@transaction.commit_on_success
@login_required
@permission_decorator('tissue.can_view_BBM_execute_labelling')
def ResultSave(request):
    print request.POST
    try:
        name=request.user.username
        operatore=User.objects.get(username=name)
        if 'salva' in request.POST:
            tipo_exp='In-situ hybridization'
            ref_type='copy_number_variation'
            #lista di dizionari riempita dalla API labelList che mi da' le informazioni sui vetrini di cui sto inserendo i risultati dell'analisi
            listadizionari=request.session.get('listaLabelSaveResult')
            #diz con chiave gen e valore un diz con chiave il probe e valore il numero inserito
            dizaliq=json.loads(request.POST.get('dati'))
            #lista per salvare i valori da far comparire nel report finale
            listavalori=[]
            genAn = GenomicAnalysis()
            print 'dizaliq',dizaliq
            #diz con chiave id dell'alilabelsched e valore una lista con gli uuid dei file caricati
            dizaliqlabsched={}
            #diz con chiave id dell'aliqlabsched e valore una lista con gli oggetti labelresult
            dizlabresult={}
            i=1
            for gen,val in dizaliq.items():
                for probe,numero in val.items():
                    mark=LabelMarker.objects.get(name=probe)
                    al=Aliquot.objects.get(uniqueGenealogyID=gen)
                    lislabsched=AliquotLabelSchedule.objects.filter(idSamplingEvent=al.idSamplingEvent)
                    if len(lislabsched)!=0:
                        #salvo il valore
                        result=LabelResult(idAliquotLabelSchedule=lislabsched[0],
                                           idLabelMarker=mark,
                                           operator=operatore,
                                           timestamp=timezone.localtime(timezone.now()),
                                           value=numero)
                        #lo salvo dopo quando conosco anche lo uuid dell'analisi
                        print 'result',result
                        barcode=''
                        for diz in listadizionari:
                            if diz['genealogy']==gen:
                                barcode=diz['barcode']
                                break
                        if lislabsched[0].id not in dizaliqlabsched:
                            lislabfile=LabelFile.objects.filter(idAliquotLabelSchedule=lislabsched[0]).values_list('rawNodeId',flat=True)
                            print 'lislabfile',lislabfile
                            dizaliqlabsched[lislabsched[0].id]=lislabfile
                        if lislabsched[0].id not in dizlabresult:
                            listemp=[]
                        else:
                            listemp=dizlabresult[lislabsched[0].id]
                        listemp.append(result)
                        dizlabresult[lislabsched[0].id]=listemp
                        listavalori.append(ReportToHtml([str(i),gen,barcode,mark.name,numero]))
                        print 'listavalori',listavalori
                        i+=1
            print 'dizaliqlabsched',dizaliqlabsched
            print 'dizlabresult',dizlabresult
            request.session['valoriLabelResult']=listavalori
            #devo comunicare i risultati al modulo di annotazioni.
            #Prima di tutto creo il nodo analisi sul grafo che deve essere collegato al/i nodo/i raw_data che rappresentano le immagini che ho caricato
            #prima e su cui viene fatta l'analisi
            for idlabsched,listauuid in dizaliqlabsched.items():
                analysis_uuid = genAn.createAnalysisbatch(uuid_list=listauuid)
                print 'analysis_uuid ', analysis_uuid
                lisresult=dizlabresult[idlabsched]
                for res in lisresult:
                    res.analysisId=analysis_uuid
                    res.save()
            
                #submitLabelAnalysis({'analysis_uuid':analysis_uuid, 'analysis_name':analysisData['analysis_name'], 'exp_type':tipo_exp, 'params':analysisData['params'], 'ref_type': ref_type})
            #submitAnalysis({'analysis_uuid':analysis_uuid, 'raw_data_uuid': plan.raw_id, 'annotations':{'copy_number_variation': analysisData['annotations']}, 'failed':analysisData['failed'] })

            
            return HttpResponse()
        if 'final' in request.POST:
            listafin=request.session.get('valoriLabelResult')
            print 'listafin',listafin
            variables = RequestContext(request,{'fine':True,'lista_fin':listafin})
            return render_to_response('tissue2/label/analysis.html',variables)
            
    except Exception,e:
        print 'err',e
        transaction.rollback()
        variables = RequestContext(request, {'errore':True})
        return render_to_response('tissue2/index.html',variables)
    
#per permettere l'inserimento dei valori tramite file
@laslogin_required
@login_required
@permission_decorator('tissue.can_view_BBM_execute_labelling')
def InsertExperimentResultFile(request):
    try:
        if request.method=='POST':
            print request.POST
            print request.FILES
            utente=request.user.username
            val=request.POST.get('template')
            #e' il tipo di tecnica usata (FISH, CISH...)
            tecnica=request.POST.get('idtecnica')
            print 'tecnica',tecnica
            #per sapere se prendere tutti i vetrini colorati o solo quelli per cui non e' mai stato inserito un valore
            tipo=request.POST.get('numvetrini')
            print 'tipo',tipo
            #chiamo la API per avere le aliquote in questione
            print 'wglabelpy',get_WG_string()
            request.META['HTTP_WORKINGGROUPS']=get_WG_string()
            hand=LabelListHandler()
            dizionario=hand.read(request, tipo, tecnica, 'None', 'None', 'None', 'None', 'None', utente)
            #lista di dizionari in cui ognuno rappresenta un LS con le sue informazioni
            lisdiz=json.loads(dizionario['data'])
            print 'lisdiz',lisdiz
                        
            #devo scandire la lista e salvare i nomi dei marker per scriverli poi nell'intestazione del file
            lisfinmarker=[]
            dizgenealogy={}
            dizbarcode={}
            dizmarker={}
            for diz in lisdiz:
                gen=diz['genealogy']
                barcode=diz['barcode']
                position=diz['position']
                dizgenealogy[gen]=barcode+'|'+position
                dizbarcode[barcode+'|'+position]=gen
                lismarker=diz['marker']
                dizmarker[gen]=lismarker
                for mark in lismarker:
                    if mark not in lisfinmarker:
                        lisfinmarker.append(str(mark))
            print 'lisfinmarker',lisfinmarker
            #ordino alfabeticamente la lista
            lisfinmarker=sorted(lisfinmarker, key=str.lower)
            #vuol dire che l'utente ha cliccato sull'opzione che gli fa vedere il file Excel precompilato
            if val=='vedi_file':
                response = HttpResponse(mimetype='text/csv')
                response['Content-Disposition'] = 'attachment; filename=Label_result_insert_value.las'
                stringa=''
                
                for m in lisfinmarker:
                    stringa+=m+'\t'
                stringa=stringa[:len(stringa)-1]
                print 'stringa',stringa   
    
                writer = csv.writer(response)
                writer.writerow(['GenealogyID\tBarcode\tPosition\t'+stringa])                
                
                #se sto scegliendo di analizzare solo i nuovi vetrini allora precompilo il file con la lista dei gen, barc e pos
                #di tutti questi vetrini i cui valori non sono mai stati inseriti prima
                if tipo=='Part':
                    for diz in lisdiz:
                        gen=diz['genealogy']
                        barcode=diz['barcode']
                        position=diz['position']
                        riga=gen+'\t'+barcode+'\t'+position+'\t'
                        for i in range (0,len(lisfinmarker)):
                            riga+='\t'
                        riga=riga[:len(riga)-1]
                        print 'riga',riga
                        writer.writerow([riga])
                        
                return response
            
            if val=='ins_file':
                dizio={}
                #chiave il gen e valore un diz con chiave il marker e valore la misura inserita dall'utente
                dizfinale={}
                #lista di diz che contengono i valori da visualizzare nel data table riassuntivo
                lisdizvisualiz=[]
                lista1=['GenealogyID','Barcode','Position']
                f=request.FILES['file']
                for a in f.chunks():
                    #c e' un vettore e in ogni posto c'e' una riga del file
                    c=a.split('\n')
                    #la prima riga contiene l'intestazione del file e mi serve
                    #per capire come sono messi i valori all'interno
                    val_primariga=c[0].strip().split('\t')
                    k=0
                    for titoli in val_primariga:
                        if titoli!='':
                            dizio[titoli]=k
                            k=k+1
                    print 'dizio',dizio
                    #parto da 1 perche' la prima riga contiene l'intestazione
                    for i in range(1,len(c)):
                        vvv=c[i].strip()
                        if vvv!='':
                            riga_fin=c[i].split('\t')
                            #devo capire dove si trova il genid e il barcode
                            indicegen=dizio[lista1[0]]
                            indicebarc=dizio[lista1[1]]
                            indicepos=dizio[lista1[2]]
                            print 'riga_fin',riga_fin
                            gen=riga_fin[indicegen].strip()
                            barc=riga_fin[indicebarc].strip()
                            pos=riga_fin[indicepos].strip()
                            print 'gen',gen
                            print 'barc',barc
                            print 'pos',pos
                            
                            if barc!='' and pos=='':
                                #provo con l'assegnare A1 alla posizione se magari quel campione e' da solo nel vetrino
                                chiave=barc+'|A1'
                                if chiave not in dizbarcode:
                                    raise ErrorDerived('Error: please insert position for barcode '+barc)
                            if barc!='' and gen=='':
                                #se ho solo barc e pos allora cerco qual e' il gen
                                chiave=barc+'|'+pos
                                if chiave not in dizbarcode:
                                    #non c'e' il gen quindi quel campione non e' disponibile per l'inserimento dei valori, perche' magari ha gia'
                                    #un valore ed io ho scelto di prendere in considerazione solo i nuovi campioni, quindi non posso aggiungere
                                    #altri valori
                                    raise ErrorDerived('Error: aliquot in '+barc+' in '+pos+' is not available for value insertion')
                                else:
                                    gen=dizbarcode[chiave]
                            if gen!='':
                                lisaliq=Aliquot.objects.filter(uniqueGenealogyID=gen,availability=1)
                                if len(lisaliq)==0:
                                    raise ErrorDerived('Error: aliquot '+gen+' does not exist in storage')
                                if gen not in dizgenealogy:
                                    raise ErrorDerived('Error: aliquot '+gen+' is not available for value insertion')
                            else:
                                raise ErrorDerived('Error: please insert a valid genealogy ID or barcode')
                            #devo scandire le altre colonne e vedere i valori inseriti per i marker
                            trovato=False
                            for mark in lisfinmarker:
                                indice=dizio[mark]
                                val=riga_fin[indice].strip()
                                print 'val',val                                
                                if val!='':
                                    trovato=True
                                    #devo controllare se ha senso mettere un valore per quel gen in corrispondenza di quel probe
                                    lismark=dizmarker[gen]
                                    print 'lismark',lismark
                                    if mark not in lismark:
                                        raise ErrorDerived('Error: for aliquot '+gen+' probe '+mark+' has not been used. You cannot insert a value for it.')
                                    if val!='NA' and val!='NO':
                                        try:
                                            val=float(val.replace(',','.'))
                                        except ValueError:
                                            raise ErrorDerived('Error: You can only insert number. Please correct value for aliquot '+gen+' for probe '+mark)
                                    
                                    if val=='NO':
                                        val=''
                                    if gen in dizfinale:
                                        diztemp=dizfinale[gen]
                                    else:
                                        diztemp={}
                                    print 'val',val
                                    diztemp[mark]=val
                                    dizfinale[gen]=diztemp
                            #se alla fine del ciclo non ho trovato nessun valore allora eccezione
                            if not trovato:
                                raise ErrorDerived('Error: please insert at least one value for aliquot '+gen)
                            
                            dizval={}
                            dizval['genealogy']=gen
                            chiave=dizgenealogy[gen]
                            ch=chiave.split('|')
                            dizval['barcode']=ch[0]
                            dizval['position']=ch[1]
                            dizval['marker']=dizfinale[gen]
                            lisdizvisualiz.append(dizval)
                print 'dizfinale',dizfinale
                print 'lisdizvisualiz',lisdizvisualiz
                lfeattecnica=LabelFeature.objects.filter(type='Technique').order_by('name')
                variables = RequestContext(request,{'dizfinale':json.dumps(dizfinale),'lisvisualizz':json.dumps(lisdizvisualiz),'file':True,'listecn':lfeattecnica,'tecnica':tecnica})
                return render_to_response('tissue2/label/analysis.html',variables)
    except ErrorDerived as e:
        print 'My exception occurred, value:', e.value
        variables = RequestContext(request, {'errore':e.value})
        return render_to_response('tissue2/label/analysis.html',variables)            
    except Exception,e:
        print 'err',e
        variables = RequestContext(request, {'errore':True})
        return render_to_response('tissue2/index.html',variables)
    
    
