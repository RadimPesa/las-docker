from __init__ import *
from catissue.tissue.utils import *
from derivation_robot import *

@laslogin_required
@login_required
def DerivedAliquotsView(request):
    da_derivare=[]
    if request.session.has_key('genealogyMeasureView'):
        del request.session['genealogyMeasureView']
    request.session['derivare']=da_derivare
    variables = RequestContext(request)   
    return render_to_response('tissue2/derived/start.html',variables)

@laslogin_required
@login_required
def DerivedAliquotsSelect(request):
    variables = RequestContext(request)   
    return render_to_response('tissue2/derived/menu_der.html',variables)

@get_functionality_decorator
def ajax_derived_autocomplete(request):
    if 'WG' in request.GET:
        wgSet=set()
        try:
            #nel caso arrivi una lista di wg sotto forma di stringa, con i wg separati da spazio
            #Inserisco cosi' nella lista finale tutti i wg
            workgr=request.GET.get('WG')
            lwork=workgr.split(',')
            for wg in lwork:
                wgSet.add(WG.objects.get(name=wg).name)
        except Exception,e:
            print e
        set_WG(wgSet)
        if 'term' in request.GET:
            if 'slide' in request.GET:
                aliqff=AliquotType.objects.filter(abbreviation='FF')
                aliqof=AliquotType.objects.filter(abbreviation='OF')
                aliqgen = list(chain(aliqff, aliqof))
                aliq = Aliquot.objects.filter(uniqueGenealogyID__icontains=request.GET.get('term'),availability=1,idAliquotType__in=aliqgen)[:10]
            elif 'label' in request.GET:
                aliqps=AliquotType.objects.filter(abbreviation='PS')
                aliqos=AliquotType.objects.filter(abbreviation='OS')
                aliqgen = list(chain(aliqps, aliqos))
                aliq = Aliquot.objects.filter(uniqueGenealogyID__icontains=request.GET.get('term'),availability=1,idAliquotType__in=aliqgen)[:10]
            elif 'filelabel' in request.GET:
                aliqls=AliquotType.objects.filter(abbreviation='LS')
                aliq = Aliquot.objects.filter(uniqueGenealogyID__icontains=request.GET.get('term'),availability=1,idAliquotType=aliqls)[:10]
            else:
                aliq = Aliquot.objects.filter(Q(uniqueGenealogyID__icontains=request.GET.get('term'))&Q(availability=1))[:10]
        else:
            aliq = Aliquot.objects.none()
        res=[]
        for p in aliq:
            p = {'id':p.id, 'label':p.__unicode__(), 'value':p.__unicode__()}
            res.append(p)
        return HttpResponse(simplejson.dumps(res))
    return HttpResponse()

@transaction.commit_on_success
@laslogin_required
@login_required
@permission_decorator('tissue.can_view_BBM_create_new_protocol')
def saveProtocols(request):
    if request.method=='POST':
        print request.POST
        form=ProtocolForm(request.POST)
        try:
            if form.is_valid():
                dizmis={'0':'mg','1':'ul'}
                nome=request.POST.get('name').strip()
                sorgenti=form.cleaned_data.get('source')
                quantit=round(float(request.POST.get('load_Quantity').strip()),2)
                quant=request.POST.get('l_quant').strip()
                vol_expect=round(float(request.POST.get('exp_Volume').strip()),2)
                vol_max=request.POST.get('max_Volume').strip()
                num_aliq=int(request.POST.get('num_Aliq').strip())
                vol_aliq=round(float(request.POST.get('vol_Aliq').strip()),2)
                conc_aliq=round(float(request.POST.get('conc_Aliq').strip()),2)
                unitamis=request.POST.get('unity_measure')
                kit=None
                kitname=''
                kitid=request.POST.get('kit')
                if kitid!='':
                    kit=KitType.objects.get(id=kitid)
                    kitname=kit.name
                risultato=AliquotType.objects.get(id=request.POST.get('result'))
                
                p=DerivationProtocol(name=nome,
                       idKitType=kit)
                p.save()

                for s in sorgenti:
                    tipoAliq=AliquotType.objects.get(id=s)
                    TransformationChange.objects.get_or_create(idFromType=tipoAliq,
                                                                     idToType=risultato)
    
                    tr=TransformationChange.objects.get(Q(idFromType=tipoAliq)&Q(idToType=risultato))
                    print tr
                    trasfDer=TransformationDerivation(idDerivationProtocol=p,
                                                      idTransformationChange=tr)
                    trasfDer.save()
                print 'vol max',vol_max
                if vol_max=='':
                    #e' DNA o RNA
                    mis_unit=dizmis[unitamis]
                    if mis_unit=='mg':
                        misura='LoadQuantity'
                    elif mis_unit=='ul':
                        misura='LoadVolume'
                
                    l_vol=quant
                    v_max=vol_max
                    nome_report='Input'
                else:
                    #e' cDNA o cRNA
                    misura='LoadQuantity'
                    mis_unit='ug'
                    nome_report='Reaction quantity'
                    
                    l_vol=round(float(quant),2)
                    v_max=round(float(vol_max),2)
                    feat=FeatureDerProtocol(idDerProtocol=p,idFeatureDerivation=FeatureDerivation.objects.get(name='LoadVolume'),value=l_vol,unityMeasure='ul')
                    feat.save()
                    feat=FeatureDerProtocol(idDerProtocol=p,idFeatureDerivation=FeatureDerivation.objects.get(name='MaxVolume'),value=v_max,unityMeasure='ul')
                    feat.save()
                
                feat=FeatureDerProtocol(idDerProtocol=p,idFeatureDerivation=FeatureDerivation.objects.get(name=misura),value=quantit,unityMeasure=mis_unit)
                feat.save()
                feat=FeatureDerProtocol(idDerProtocol=p,idFeatureDerivation=FeatureDerivation.objects.get(name='ExpectedVolume'),value=vol_expect,unityMeasure='ul')
                feat.save()
                feat=FeatureDerProtocol(idDerProtocol=p,idFeatureDerivation=FeatureDerivation.objects.get(name='number_Aliquot'),value=num_aliq)
                feat.save()
                feat=FeatureDerProtocol(idDerProtocol=p,idFeatureDerivation=FeatureDerivation.objects.get(name='volume_Aliquot'),value=vol_aliq,unityMeasure='ul')
                feat.save()
                feat=FeatureDerProtocol(idDerProtocol=p,idFeatureDerivation=FeatureDerivation.objects.get(name='concentration_Aliquot'),value=conc_aliq,unityMeasure='ng/ul')
                feat.save()
                robot='No'
                if 'robot' in request.POST:
                    feat=FeatureDerProtocol(idDerProtocol=p,idFeatureDerivation=FeatureDerivation.objects.get(name='Robot'),value=1)
                    feat.save()
                    robot='Yes'
                intest='<th>Protocol name</th><th>Derivative</th><th>'+nome_report+' ('+mis_unit+')</th><th>Max volume (uL)</th><th>Reaction volume (uL)</th><th>Outcome volume (uL)</th><th>Aliquot number</th><th>Aliquot volume (uL)</th><th>Aliquot conc. (ng/uL)</th><th>Kit</th><th>Robot</th>'
                report='<tr align="center"><td>'+nome+'</td><td>'+risultato.longName+'</td><td>'+str(quantit)+'</td><td>'+str(v_max)+'</td><td>'+str(l_vol)+'</td><td>'+str(vol_expect)+'</td><td>'+str(num_aliq)+'</td><td>'+str(vol_aliq)+'</td><td>'+str(conc_aliq)+'</td><td>'+kitname+'</td><td>'+robot+'</td></tr>'
                variables = RequestContext(request, {'fine':True,'intest':intest,'dati_prot':report})
                return render_to_response('tissue2/protocols.html',variables)
            else:
                lisprot=list(DerivationProtocol.objects.all().values_list('name',flat=True))
                variables = RequestContext(request, {'form':form,'lisprot':json.dumps(lisprot)})
                return render_to_response('tissue2/protocols.html',variables)
        except Exception,e:
            print 'errore',e
            transaction.rollback()
            variables = RequestContext(request, {'errore':True})
            return render_to_response('tissue2/index.html',variables)
    else:
        form = ProtocolForm()
    lisprot=list(DerivationProtocol.objects.all().values_list('name',flat=True))
    variables = RequestContext(request, {'form':form,'lisprot':json.dumps(lisprot)})
    return render_to_response('tissue2/protocols.html',variables)

@transaction.commit_on_success
@laslogin_required
@login_required
#@user_passes_test(lambda u: u.has_perm('tissue.can_view_plan_derivation'),login_url=settings.BASE_URL+'/tissue/error/')
@permission_decorator('tissue.can_view_BBM_plan_derivation')
def InsertDerivedAliquots(request):
    name=request.user.username
    assignUsersList=[]
    addressUsersList=[]
    if settings.USE_GRAPH_DB == True:
        #PARTE SHARING        
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
            addressUsersList.append(addressUsersDict)
    else:
        assignUsersDict={}
        assignUsersDict['wg']=''
        assignUsersDict['usersList']=list()
        for u in User.objects.filter(~Q(username='admin')&~Q(first_name='')&Q(is_active=1)).order_by('last_name'):
            assignUsersDict['usersList'].append(u)
        assignUsersList.append(assignUsersDict)
        addressUsersList.append(assignUsersDict)
        
    if request.session.has_key('derivare'):
        da_derivare=request.session.get('derivare')
    else:
        da_derivare=[]
    if request.method=='POST':
        print request.POST
        print request.FILES  
        try:       
            if 'salva' in request.POST:
                listaaliq=json.loads(request.POST.get('dati'))
                res=request.POST.get('res')
                operat=request.POST.get('operat')
                note=request.POST.get('note')
                lisgen=[]
                if len(listaaliq)!=0:
                    for val in listaaliq:
                        print 'val',val
                        listemp=[]
                        listemp.append(val)
                        if listemp not in lisgen:
                            lisgen.append(listemp)
                print 'lis da derivare',lisgen
                request.session['derivare']=lisgen
                request.session['risderivare']=res
                request.session['operderivare']=operat
                request.session['notederived']=note
                return HttpResponse()   
            
            #ho cliccato sul tasto 'add file'
            if 'aggiungi_file' in request.POST:
                form=DerivedInit(request.POST,request.FILES)
                res=request.session.get('risderivare')
                operat=request.session.get('operderivare')
                note=request.session.get('notederived').strip()
                lisaliq=[]
                lisbarc=[]
                lispos=[]
                if 'file' in request.FILES:
                    print 'da_derivare',da_derivare
                    for lis in da_derivare:
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
                            raise ErrorDerived('Error: aliquot '+gen+' does not exist in storage')
                        else:
                            lisgen=[]
                            if lista not in da_derivare:                                
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
                                        raise ErrorDerived('Error: aliquot '+gen+' does not exist in storage')
                                    listaliq.append(lisali[0])
                                    
                                for al in listaliq:
                                    print 'al',al
                                    trovato=0
                                    #vedo se l'aliquota e' gia' stata programmata per la derivazione e verra' esaurita alla fine
                                    aldersched=AliquotDerivationSchedule.objects.filter(idAliquot=al,derivationExecuted=0,deleteTimestamp=None,aliquotExhausted=1)
                                    if(aldersched.count()!=0):
                                        raise ErrorDerived('Error: Aliquot '+gen+' is already scheduled for derivation and it will be exhausted in the end of the procedure')
                                    #vedo quali tipi di trasformazione sono legati a quel protocollo
                                    tipi=TransformationChange.objects.filter(idToType=res)
                                    for t in tipi:
                                        if al.idAliquotType.id==t.idFromType.id:
                                            trovato=1
                                            print 'from',t.idFromType
                                            break
                                    if trovato==0:
                                        #se l'aliquota non e' del tipo giusto sollevo un'eccezione
                                        raise ErrorDerived('Error: aliquot type of '+gen+' is incompatible with protocol types')
                                    #se sto creando plasma(PL) o PBMC(VT) devo controllare che il tipo di tessuto sia sangue
                                    aliqtipo=AliquotType.objects.get(id=res)
                                    if aliqtipo.abbreviation=='PL' or aliqtipo.abbreviation=='VT':
                                        if al.idSamplingEvent.idTissueType.abbreviation!='BL':
                                            raise ErrorDerived('Error: aliquot type of '+gen+' is incompatible with protocol types')
                                da_derivare.append(lista)
                                    
                    print 'deriv',da_derivare
                    print 'lisaliq',lisaliq
                    variables = RequestContext(request,{'form':form,'posizionare':zip(lisaliq,lisbarc,lispos),'protocol':res,'t':operat,'assignUsersList':assignUsersList,'addressUsersList':addressUsersList,'fileLoaded':'True'})
                    return render_to_response('tissue2/derived/derived.html',variables) 
            
            if 'conferma' in request.POST:
                lisaliq=[]
                lisbarc=[]
                lispos=[]
                    
                esec=request.session.get('operderivare')
                if esec!='':
                    esecutore=User.objects.get(id=esec).username
                else:
                    esecutore=''
                    
                res=request.session.get('risderivare')
                prot=AliquotType.objects.get(id=res)
                note=request.session.get('notederived').strip()
                print 'da_derivare',da_derivare
                
                lisgen=[]
                for lis in da_derivare:
                    for valori in lis:
                        val=valori.split('|')
                        gen=val[0]
                        lisgen.append(val[0])
                        
                print 'lisgen',lisgen
                listaaliq=Aliquot.objects.filter(uniqueGenealogyID__in=lisgen,availability=1)
                
                for al in listaaliq:
                    trovato=0
                    #vedo se l'aliquota e' gia' stata programmata per la derivazione
                    #aldersched=AliquotDerivationSchedule.objects.filter(idAliquot=al,derivationExecuted=0,deleteTimestamp=None)
                    #if(aldersched.count()!=0):
                        #raise ErrorDerived('Error: Aliquot '+al.uniqueGenealogyID+' is already scheduled for derivation')
                    #vedo quali tipi di trasformazione sono legati a quel protocollo
                    tipi=TransformationChange.objects.filter(idToType=res)
                    for t in tipi:
                        if al.idAliquotType.id==t.idFromType.id:
                            trovato=1
                            print 'from',t.idFromType
                            break
                    if trovato==0:
                        #se l'aliquota non e' del tipo giusto sollevo un'eccezione
                        raise ErrorDerived('Error: aliquot type of '+al.uniqueGenealogyID+' is incompatible with protocol types')
                    print 'al',al
                
                #salvo la DerivationSchedule per la derivazione
                schedule=DerivationSchedule(scheduleDate=date.today(),
                                            operator=name)
                schedule.save()
                listal=[]
                #mi serve dopo per riempire il corpo del messaggio dell'e-mail
                dizaliqgen={}
                for lis in da_derivare:
                    for valori in lis:
                        val=valori.split('|')
                        gen=val[0]
                        barc=val[1]
                        pos=val[2]
                        a=Aliquot.objects.get(availability=1,uniqueGenealogyID=gen)
                        #creo l'oggetto AliquotDerivationSchedule
                        alsched=AliquotDerivationSchedule(idAliquot=a,
                                                          idDerivationSchedule=schedule,
                                                          idDerivedAliquotType=prot,
                                                          derivationExecuted=0,
                                                          operator=esecutore,
                                                          notes=note
                                                          )
                        alsched.save()
                        listal.append(alsched)
                        lisaliq.append(gen)
                        lisbarc.append(barc)
                        lispos.append(pos)
                        dizaliqgen[gen]=barc+'|'+pos
                print 'dizaliqgen',dizaliqgen
                request.session['listafinalederivazionereport']=zip(lisaliq,lisbarc,lispos)
                if esecutore!='':
                    email = LASEmail (functionality=get_functionality(), wgString=get_WG_string())
                    msg=['You have been designated to execute the following:','','Assigner:\t'+name,'Derive:\t'+str(prot.abbreviation),'Description:\t'+note,'','Aliquots:','N\tGenealogy ID\tBarcode\tPosition']
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
                        email.addRoleEmail([wg.name], 'Assignee', [esecutore])
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
                    
                urlfin=settings.DOMAIN_URL+settings.HOST_URL+'/derived/insert/final/'
                print 'urlfin',urlfin
                return HttpResponseRedirect(urlfin)
 
        except ErrorDerived as e:
            print 'My exception occurred, value:', e.value
            transaction.rollback()
            variables = RequestContext(request, {'errore':e.value,'assignUsersList':assignUsersList,'addressUsersList':addressUsersList})
            return render_to_response('tissue2/derived/derived.html',variables)
        except Exception,e:
            print 'errore',e
            transaction.rollback()
            variables = RequestContext(request, {'errore':True,'assignUsersList':assignUsersList,'addressUsersList':addressUsersList})
            return render_to_response('tissue2/index.html',variables)
    else:
        form = DerivedInit()
    variables = RequestContext(request, {'form':form,'posizionare':da_derivare,'assignUsersList':assignUsersList,'addressUsersList':addressUsersList})
    return render_to_response('tissue2/derived/derived.html',variables)   

#per far vedere il report finale dell'inserimento delle derivazioni
@transaction.commit_on_success
@laslogin_required
@login_required
@permission_decorator('tissue.can_view_BBM_plan_derivation')
def InsertDerivedAliquotsFinal(request):
    liste=request.session.get('listafinalederivazionereport')
    variables = RequestContext(request,{'fine':True,'posizionare':liste})
    return render_to_response('tissue2/derived/derived.html',variables)

#per far comparire la prima pagina delle aliquote da derivare in cui l'utente sceglie,
#fra quelle assegnate a lui, quelle da derivare oggi
@transaction.commit_on_success
@laslogin_required
@login_required
#@user_passes_test(lambda u: u.has_perm('tissue.can_view_select_aliquots_and_protocols'),login_url=settings.BASE_URL+'/tissue/error/')
@permission_decorator('tissue.can_view_BBM_select_aliquots_and_protocols')
def ExecDerivedAliquots(request):
    if request.session.has_key('derivedmeasure'):
        del request.session['derivedmeasure']
    try:
        name=request.user.username
        operatore=User.objects.get(username=name)
        if request.method=='POST':
            print request.POST
            lista_aliq=[]
            request.session['aliqderivare']=[]
            request.session['listaaliqderivare']=[]
            #ho cliccato su conferma
            #mi da' il numero di aliquote totali
            num=request.POST.get('num_aliq')
            #vedo se devo cancellare delle pianificazioni
            canc=request.POST.get('elimina')            
            if canc=='s':
                lista_canc=[]
                lista=[]
                lgen=''
                laliq=[]
                for i in range(0,int(num)):
                    #preparo la stringa per accedere alla post
                    can='canc_'+str(i)
                    print 'canc',can
                    if can in request.POST:
                        ge='gen_'+str(i)
                        gen=request.POST.get(ge)
                        print 'gen',gen
                        #adesso ho il genealogy id e prendo la relativa aliqDerSched
                        aliq=Aliquot.objects.get(uniqueGenealogyID=gen,availability=1)
                        print 'aliq',aliq
                        listaaldersched=AliquotDerivationSchedule.objects.filter(idAliquot=aliq,derivationExecuted=0,idKit=None,deleteTimestamp=None,loadQuantity=None)
                        print 'listaaldersched',listaaldersched
                        if listaaldersched.count()!=0:
                            laliq.append(gen)
                            lgen+=gen+'&'
                            aldersched=listaaldersched[0]
                            print 'der',aldersched
                            #cancello la pianificazione
                            #aldersched.deleteTimestamp= datetime.datetime.now()
                            aldersched.deleteTimestamp=timezone.localtime(timezone.now())
                            aldersched.deleteOperator=operatore
                            aldersched.save()
                            lista_canc.append(aldersched)
                            
                lgenfin=lgen[:-1]
                diz=AllAliquotsContainer(lgenfin)
                 
                print 'listaaliq',lista_canc
                                
                email = LASEmail (functionality=get_functionality(), wgString=get_WG_string())
                msg=['Derivation procedure deleted','','Assigned to:\t'+name,'','Aliquots:','N\tGenealogy ID\tBarcode\tPosition\tAssignment date\tDerivative']
                aliquots=Aliquot.objects.filter(uniqueGenealogyID__in=laliq,availability=1)
                wgList=WG.objects.filter(id__in=Aliquot_WG.objects.filter(aliquot__in=aliquots).values_list('WG',flat=True).distinct())
                print 'wglist',wgList
                for wg in wgList:
                    print 'wg',wg
                    email.addMsg([wg.name], msg)
                    aliq=aliquots.filter(id__in=Aliquot_WG.objects.filter(WG=wg).values_list('aliquot',flat=True).distinct())
                    print 'aliq',aliq
                    i=1
                    lisplanner=[]
                    #per mantenere l'ordine dei campioni anche nell'e-mail
                    for alder in lista_canc:
                        for al in aliq:   
                            if alder.idAliquot.uniqueGenealogyID==al.uniqueGenealogyID:
                                lval=diz[al.uniqueGenealogyID]
                                val=lval[0].split('|')
                                barc=val[1]
                                pos=val[2]
                                email.addMsg([wg.name],[str(i)+'\t'+al.uniqueGenealogyID+'\t'+barc+'\t'+pos+'\t'+str(alder.idDerivationSchedule.scheduleDate)+'\t'+alder.idDerivedAliquotType.longName])
                                i=i+1                                
                                if alder.idDerivationSchedule.operator not in lisplanner:
                                    lisplanner.append(alder.idDerivationSchedule.operator)
                    print 'lisplanner',lisplanner
                    #devo mandare l'e-mail al pianificatore della procedura
                    email.addRoleEmail([wg.name], 'Planner', lisplanner)
                    email.addRoleEmail([wg.name], 'Executor', [request.user.username])
                try:
                    email.send()
                except Exception, e:
                    print 'errore',e
                    pass
                
                for i in range(0,len(lista_canc)):
                    alder=lista_canc[i]
                    data=alder.idDerivationSchedule.scheduleDate
                    valori=diz[alder.idAliquot.uniqueGenealogyID]
                    val=valori[0].split('|')
                    barc=val[1]
                    pos=val[2]
                    lista.append(ReportToHtml([i+1,alder.idAliquot.uniqueGenealogyID,barc,pos,alder.idDerivationSchedule.operator,data,alder.idDerivedAliquotType.longName]))                                
                variables = RequestContext(request,{'fine':True,'lista_der':lista})
                return render_to_response('tissue2/derived/choose.html',variables) 
            #prendo il protocollo
            pro=request.POST.get('prot')
            protoc=DerivationProtocol.objects.get(id=pro)
            print 'pr',protoc
            #prendo il kit
            #ki=request.POST.get('single_kit')
            #kit=Kit.objects.get(barcode=ki)
            #print 'k',kit
            for i in range(0,int(num)):
                #preparo la stringa per accedere alla post
                sel='sele_'+str(i)
                print 'sel',sel
                if sel in request.POST:
                    ge='gen_'+str(i)
                    gen=request.POST.get(ge)
                    print 'gen',gen
                    #adesso ho il genealogy id e prendo la relativa aliqDerSched
                    aliq=Aliquot.objects.get(uniqueGenealogyID=gen,availability=1)
                    print 'aliq',aliq
                    listaaldersched=AliquotDerivationSchedule.objects.filter(Q(idAliquot=aliq)&Q(derivationExecuted=0)&Q(Q(operator=name)|Q(operator=''))&Q(loadQuantity=None)&Q(idKit=None)&Q(deleteTimestamp=None))
                    print 'listaaldersched',listaaldersched
                    if listaaldersched.count()!=0:
                        aldersched=listaaldersched[0]
                        print 'der',aldersched
                        aldersched.idDerivationProtocol=protoc
                        #aldersched.idKit=kit
                        aldersched.save()
            robot=request.POST.get('robot')
            featrobot=FeatureDerivation.objects.get(name='Robot')
            lisprotrobot=FeatureDerProtocol.objects.filter(idFeatureDerivation=featrobot).values_list('idDerProtocol',flat=True)
            #visto che devo usare la Q per il not, la sfrutto anche per l'or sull'operatore
            if robot=='False':
                lista=AliquotDerivationSchedule.objects.filter(Q(derivationExecuted=0)&Q(Q(operator=name)|Q(operator=''))&~Q(idDerivationProtocol=None)&~Q(idDerivationProtocol__in=lisprotrobot)&Q(idKit=None)&Q(loadQuantity=None)&Q(initialDate=None)&Q(deleteTimestamp=None))
            else:
                lista=AliquotDerivationSchedule.objects.filter(Q(derivationExecuted=0)&Q(Q(operator=name)|Q(operator=''))&~Q(idDerivationProtocol=None)&Q(idDerivationProtocol__in=lisprotrobot)&Q(idKit=None)&Q(loadQuantity=None)&Q(initialDate=None)&Q(deleteTimestamp=None))
            print 'lista',lista
            for l in lista:
                lista_aliq.append(l)
            request.session['listaaliqderivare']=lista_aliq
            print 'listaaliq',lista_aliq     
            variables = RequestContext(request,{'lista':lista_aliq,'robot':robot})
            return render_to_response('tissue2/derived/execute.html',variables)               
        else:
            print 'name',name
            robot='False'
            lista1=AliquotDerivationSchedule.objects.filter(derivationExecuted=0,operator=name,loadQuantity=None,idKit=None,deleteTimestamp=None)
            lista2=AliquotDerivationSchedule.objects.filter(derivationExecuted=0,operator='',loadQuantity=None,idKit=None,deleteTimestamp=None)
            lista=list(chain(lista1,lista2))
            print 'lista aliq derivation',lista
            stringat=''
            for alder in lista:
                stringat+=alder.idAliquot.uniqueGenealogyID+'&'
            stringtotale=stringat[:-1]
            diz=AllAliquotsContainer(stringtotale)
            lisaliq=[]
            lisbarc=[]
            lispos=[]
            for al in lista:
                listatemp=diz[al.idAliquot.uniqueGenealogyID]
                for val in listatemp:
                    ch=val.split('|')
                    lisaliq.append(al)
                    lisbarc.append(ch[1])
                    lispos.append(ch[2])
            listatrasf=[]
            listaprot=[]
            for l in lista:
                listatrasf.append( l.idDerivedAliquotType.id)
                        
            #prendo i trasfChange che hanno come tipo finale i tipi che rappresentano i
            #risultati della derivazione ancora da effettuare
            if len(listatrasf)!=0:
                listr=TransformationChange.objects.filter(idToType__in=listatrasf).values_list('id',flat=True)
                print 'l',listr
                #prendo i transfderivation
                if len(listr)!=0:                    
                    listatrasfder=TransformationDerivation.objects.filter(idTransformationChange__in=listr).values_list('idDerivationProtocol',flat=True)
                    print 'li',listatrasfder
                    #prendo i protocolli
                    if len(listatrasfder)!=0:                                
                        featrobot=FeatureDerivation.objects.get(name='Robot')
                        lisderprot=FeatureDerProtocol.objects.filter(idFeatureDerivation=featrobot).values_list('idDerProtocol',flat=True)
                        print 'lisderprot',lisderprot
                        if 'robotstep1' in request.session:
                            print 'robot'
                            del request.session['robotstep1']
                            robot='True'
                            lisfin=list(set(lisderprot)&set(listatrasfder))
                        else:
                            lisfin=list(set(listatrasfder)-set(lisderprot))
                            robot='False'
                        print 'lisfin',lisfin
                        listaprot=DerivationProtocol.objects.filter(id__in=lisfin).order_by('name')
                                                    
            #listaprot=DerivationProtocol.objects.all().order_by('name')
            print 'lista',listaprot
            print 'l',lista
            
            variables = RequestContext(request,{'lista':listaprot,'listaliq':zip(lisaliq,lisbarc,lispos),'robot':robot})
            return render_to_response('tissue2/derived/choose.html',variables) 
    except Exception,e:
        print 'err',e
        transaction.rollback()
        variables = RequestContext(request,{'errore':True})
        return render_to_response('tissue2/index.html',variables)

#per mettere aliquote nella lista effettiva delle derivazioni di oggi
@laslogin_required
@login_required
#@user_passes_test(lambda u: u.has_perm('tissue.can_view_select_aliquots_and_protocols'),login_url=settings.BASE_URL+'/tissue/error/')
@permission_decorator('tissue.can_view_BBM_select_aliquots_and_protocols')
def ExecEffectiveDerivedAliquots(request):
    try:
        if request.method=='POST':
            name=request.user.username
            print request.POST
            if 'salva' in request.POST:
                listagen=json.loads(request.POST.get('lgen'))
                print 'listagen',listagen
                request.session['listaaliqderivare']=listagen
                return HttpResponse()
            if 'conferma' in request.POST:
                lisfin=[]
                robot=request.POST.get('robot')
                listagen=request.session.get('listaaliqderivare')
                #devo vedere il tipo dell'aliq
                lisaliq=Aliquot.objects.filter(uniqueGenealogyID__in=listagen,availability=1)
                print 'lisaliq',lisaliq
                featrobot=FeatureDerivation.objects.get(name='Robot')
                lisprotrobot=FeatureDerProtocol.objects.filter(idFeatureDerivation=featrobot).values_list('idDerProtocol',flat=True)
                if robot=='False':
                    lisqual=AliquotDerivationSchedule.objects.filter(Q(idAliquot__in=lisaliq)&Q(derivationExecuted=0)&Q(Q(operator=name)|Q(operator=''))&~Q(idDerivationProtocol=None)&~Q(idDerivationProtocol__in=lisprotrobot)&Q(idKit=None)&Q(loadQuantity=None)&Q(initialDate=None)&Q(deleteTimestamp=None))
                else:
                    lisqual=AliquotDerivationSchedule.objects.filter(Q(idAliquot__in=lisaliq)&Q(derivationExecuted=0)&Q(Q(operator=name)|Q(operator=''))&~Q(idDerivationProtocol=None)&Q(idDerivationProtocol__in=lisprotrobot)&Q(idKit=None)&Q(loadQuantity=None)&Q(initialDate=None)&Q(deleteTimestamp=None))
                lgen=[]
                strgen=''
                for qual in lisqual:
                    lgen.append(qual.idAliquot.uniqueGenealogyID)
                    strgen+=qual.idAliquot.uniqueGenealogyID+'&'
                    print 'aliquota_deriv',qual.idAliquot
                #devo ordinare la lista degli aliquot der sched in base a come sono state convalidate le aliquote
                for gen in listagen:
                    for qual in lisqual:
                        if qual.idAliquot.uniqueGenealogyID==gen:
                            lisfin.append(qual)
                
                request.session['aliqderivare']=lisfin
                
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
                    
                listavol=[]
                listaconc=[]
                listatipi=[]
                listaload=[]
                lista2=[]
                lista3=[]
                loadvol=FeatureDerivation.objects.get(name='LoadVolume')
                loadquant=FeatureDerivation.objects.get(name='LoadQuantity')
                maxvol=FeatureDerivation.objects.get(name='MaxVolume')
                
                lgenfin=strgen[:-1]
                diz=AllAliquotsContainer(lgenfin)
                request.session['dizinfoaliqsplit']=diz
                
                lisbarc=[]
                lispos=[]                
                #uso una variabile per capire se sto derivando o retrotrascrivendo. Tanto non
                #posso unire le due cosa nella stessa schermata, quindi basta una variabile sola
                deriv_compl=False
                #prendo per ogni aliq derivata il volume rimanente nella provetta
                for alsched in lisfin:
                    valori=diz[alsched.idAliquot.uniqueGenealogyID]
                    val=valori[0].split('|')
                    barcode=val[1]
                    position=val[2]
                    lisbarc.append(barcode)
                    lispos.append(position)
                    #per capire qual e' il tipo di derivato prodotto                    
                    tipo=alsched.idDerivedAliquotType.abbreviation
                    if tipo not in listatipi:
                        listatipi.append(tipo)
                    featvol=Feature.objects.filter(idAliquotType=alsched.idAliquot.idAliquotType.id,name='Volume')
                    
                    if alsched.idAliquot.idAliquotType.type=='Derived':       
                        aliqfeat=AliquotFeature.objects.filter(idAliquot=alsched.idAliquot,idFeature=featvol[0])
                        if len(aliqfeat)!=0:
                            listavol.append(aliqfeat[0].value)
                        else:
                            listavol.append('None')
                        featconc=Feature.objects.filter(idAliquotType=alsched.idAliquot.idAliquotType,name='Concentration')
                        aliqfeat2=AliquotFeature.objects.filter(idAliquot=alsched.idAliquot,idFeature=featconc[0])
                        if len(aliqfeat2)!=0:
                            listaconc.append(aliqfeat2[0].value)
                        else:
                            listaconc.append('None')

                        deriv_compl=True
                        #devo fare delle liste con dentro i valori del prot di derivazione
                        listafeat=FeatureDerProtocol.objects.filter(idDerProtocol=alsched.idDerivationProtocol,idFeatureDerivation=loadquant)
                        if len(listafeat)!=0:
                            loadquant=listafeat[0].value
                        listafeat2=FeatureDerProtocol.objects.filter(idDerProtocol=alsched.idDerivationProtocol,idFeatureDerivation=loadvol)
                        if len(listafeat2)!=0:
                            loadvol=listafeat2[0].value
                        listafeat3=FeatureDerProtocol.objects.filter(idDerProtocol=alsched.idDerivationProtocol,idFeatureDerivation=maxvol)
                        if len(listafeat3)!=0:
                            maxvol=listafeat3[0].value
                        listaload.append(loadquant)
                        lista2.append(loadvol)
                        lista3.append(maxvol)
                    else:
                        #anche se il campione non e' un derivato potrebbe avere un volume (es. plasma)
                        if len(featvol)!=0:
                            aliqfeat=AliquotFeature.objects.filter(idAliquot=alsched.idAliquot,idFeature=featvol[0])
                            if len(aliqfeat)!=0:
                                listavol.append(aliqfeat[0].value)
                            else:
                                listavol.append('None')
                        else:
                            listavol.append('None')
                            
                        listaconc.append('None')
                        #devo fare delle liste con dentro i valori del prot di derivazione
                        #guardo se il prot ha una quantita' da caricare
                        listafeat=FeatureDerProtocol.objects.filter(idDerProtocol=alsched.idDerivationProtocol,idFeatureDerivation=loadquant)
                        if len(listafeat)!=0:
                            load=listafeat[0].value
                            unit=listafeat[0].unityMeasure
                        else:
                            #guardo se il prot ha un volume da caricare
                            listafeat2=FeatureDerProtocol.objects.filter(idDerProtocol=alsched.idDerivationProtocol,idFeatureDerivation=loadvol)
                            if len(listafeat2)!=0:
                                load=listafeat2[0].value
                                unit=listafeat2[0].unityMeasure
                        if load==0:
                            load=''
                        print 'load',load
                        print 'unita',unit
                        listaload.append(load)
                        lista2.append(unit)
                        lista3.append('')
                print 'listavol',listavol
                print 'listatipi',listatipi
                #devo trovare gli altri utenti del wg dell'operatore per presentarli sotto forma di lista nella schermata. Serve se l'operatore decide
                #di dare i campioni a qualcun altro
                if settings.USE_GRAPH_DB == True:
                    perm=Permission.objects.get(codename=get_functionality())
                    print 'perm',perm
                    print 'getwg',get_WG_string()
                    #se l'utente ha piu' di un wg li prendo tutti
                    wglist=WG.objects.filter(name__in=get_WG())
                    #if ',' in wgfin:
                        #lwg=wgfin.split(',')
                        #wgfin=lwg[0]
                    lisuser=User.objects.filter(id__in=WG_User.objects.filter(user__is_active=1,WG__in=wglist,permission=perm).values_list("user",flat=True)).order_by('last_name')
                else:
                    perm=Permission.objects.get(codename='can_view_BBM_select_aliquots_and_protocols')
                    #lisuser=User.objects.filter(id__in=WG_User.objects.filter(user__is_active=1,permission=perm).values_list("user",flat=True)).order_by('last_name')
                    lisuser=User.objects.filter(~Q(username='admin')&~Q(first_name='')&Q(is_active=1)).order_by('last_name')
                
                print 'lisuser',lisuser                
                variables = RequestContext(request,{'lista':zip(lisfin,listaload,lista2,lista3,lisbarc,lispos),'listavol':listavol,'listaconc':listaconc,'listatipiprot':listatipi,'complementary':deriv_compl,'lisutenti':lisuser,'robot':robot})
                return render_to_response('tissue2/derived/details.html',variables)
    except Exception,e:
        print 'err',e
        variables = RequestContext(request, {'errore':True})
        return render_to_response('tissue2/index.html',variables)

#per confermare la prima schermata dei dettagli delle aliquote da derivare (quella con la
#load quantity e l'indicazione se l'aliquota e' esausta)
@transaction.commit_on_success
@laslogin_required
@login_required
#@user_passes_test(lambda u: u.has_perm('tissue.can_view_select_aliquots_and_protocols'),login_url=settings.BASE_URL+'/tissue/error/')
@permission_decorator('tissue.can_view_BBM_select_aliquots_and_protocols')
def ConfirmDetailsDerivedAliquots(request):
    if request.session.has_key('aliqderivare'):
        aliq_da_derivare=request.session.get('aliqderivare')
    if request.method=='POST':
        try:
            print request.POST
            print 'aliq_da_derivare',aliq_da_derivare
            #adesso=datetime.datetime.now()
            adesso=timezone.localtime(timezone.now())
            print 'adesso',adesso
            #metto i secondi a zero in modo di partire dal minuto preciso. Poi ad ogni convalida aggiungo un secondo
            adesso=adesso.replace(second=0, microsecond=0)
            print 'adesso2',adesso
            lgen=[]
            for i in range(0,len(aliq_da_derivare)):
                #preparo i nomi con cui accedere alla request.post
                #outcome='outcome_'+str(i)
                gen='gen_'+str(i)
                #kit='kit_'+str(i)
                protocollo='prot_'+str(i)
                geneal=request.POST.get(gen)
                proto=request.POST.get(protocollo)
                lista_aliquota=Aliquot.objects.filter(uniqueGenealogyID=geneal,availability=1)
                if lista_aliquota.count()!=0:
                    aliquota=lista_aliquota[0]
                print 'aliquota',aliquota
                #prendo il protocollo
                pro=DerivationProtocol.objects.get(id=proto)
                print 'prot',pro
                #prendo il derivation schedule
                #alder=AliquotDerivationSchedule.objects.get(idAliquot=aliquota,derivationExecuted=0,deleteTimestamp=None)
                alder=aliq_da_derivare[i]
                #prendo la quantita' di liquido usata inizialmente
                quant='quant_'+str(i)
                quantit=request.POST.get(quant)
                print 'quant',quantit
                #leggo il check per l'aliquota finita
                es=0
                esausta='exhausted_'+str(i)
                if esausta in request.POST:
                    es=1
                else:
                    #metto in lista i gen che eventualmente cambieranno possesso, ma scegliendo solo quelli che non verranno esauriti 
                    lgen.append(alder.idAliquot.uniqueGenealogyID)
                    
                tempovalidaz=adesso+timezone.timedelta(seconds=i)
                #salvo nell'aliquotDerivationSchedule i nuovi dati che ho acquisito in
                #questa schermata
                alder.loadQuantity=float(quantit)
                alder.initialDate=date.today()
                alder.aliquotExhausted=es
                alder.validationTimestamp=tempovalidaz
                alder.save()
            #eventuale utente a cui do' le provette dopo che ho derivato
            nuovoutente=request.POST.get('newusertubes')
            if nuovoutente!='':
                n_utente=User.objects.get(id=nuovoutente)
                url1 = Urls.objects.get(default = '1').url + "/container/availability/"
                print 'lgen',lgen
                val1={'lista':json.dumps(lgen),'tube':'0','nome':n_utente.username}

                print 'url1',url1
                data = urllib.urlencode(val1)
                req = urllib2.Request(url1,data=data, headers={"workingGroups" : get_WG_string()})
                u = urllib2.urlopen(req)
                res1 =  u.read()
                print 'res',res1
                if res1=='err':
                    variables = RequestContext(request, {'errore':True})
                    return render_to_response('tissue2/index.html',variables)
            if 'stop' in request.POST:
                #vuol dire che devo terminare qui la procedura
                variables = RequestContext(request,{'fine':True})
                return render_to_response('tissue2/derived/details.html',variables)
            if 'next' in request.POST:
                robot=request.POST.get('robot')
                if robot=='True':
                    request.session['robotstep2']=True
                #vuol dire che devo passare alla prossima schermata                            
                #devo filtrare ulteriormente dividendo in due liste le derivazioni che prevedono
                #un kit e quelle che non ce l'hanno
                liskitsi=[]
                for aliq in aliq_da_derivare:
                    if aliq.idDerivationProtocol.idKitType!=None:
                        liskitsi.append(aliq)
                print 'kitsi',liskitsi
                #se c'e' qualche derivazione che ha bisogno del kit, allora faccio comparire come al solito
                #la schermata del passo 2 della derivazione a cui devo aggiungere anche le derivazioni che erano gia' al passo 2
                if len(liskitsi)!=0:
                    return LoadKitDerivedAliquots(request)
                else:
                    #vuol dire che nessuna derivazione ha bisogno del kit e allora vado direttamente
                    #alla schermata di misurazioni
                    if robot=='True':
                        return LoadInsertMeasure(request)
                    else:
                        return LoadDetailsDerivedAliquots2(request)
        except Exception,e:
            print 'errr',e
            transaction.rollback()
            errore=True
            variables = RequestContext(request, {'errore':errore})
            return render_to_response('tissue2/index.html',variables)

#per caricare la schermata per il secondo passo della derivazione, quello in cui
#inserisco il kit
@laslogin_required
@login_required
#@user_passes_test(lambda u: u.has_perm('tissue.can_view_select_kit'),login_url=settings.BASE_URL+'/tissue/error/')
@permission_decorator('tissue.can_view_BBM_select_kit')
def LoadKitDerivedAliquots(request):    
    name=request.user.username
    #visto che devo ordinare in base al momento della validazione, tengo la Q e la sfrutto anche per filtrare sull'operatore con la OR
    featrobot=FeatureDerivation.objects.get(name='Robot')
    lisprotrobot=FeatureDerProtocol.objects.filter(idFeatureDerivation=featrobot).values_list('idDerProtocol',flat=True)
    if 'robotstep2' in request.session:
        print 'robot'        
        del request.session['robotstep2']
        robot='True'
        aliq_da_derivare=AliquotDerivationSchedule.objects.filter(Q(derivationExecuted=0)&Q(Q(operator=name)|Q(operator=''))&~Q(idDerivationProtocol=None)&Q(idDerivationProtocol__in=lisprotrobot)&Q(idKit=None)&~Q(loadQuantity=None)&~Q(initialDate=None)&Q(volumeOutcome=None)&Q(measurementExecuted=0)&Q(deleteTimestamp=None)).order_by('validationTimestamp','initialDate','id')
    else:
        robot='False'
        aliq_da_derivare=AliquotDerivationSchedule.objects.filter(Q(derivationExecuted=0)&Q(Q(operator=name)|Q(operator=''))&~Q(idDerivationProtocol=None)&~Q(idDerivationProtocol__in=lisprotrobot)&Q(idKit=None)&~Q(loadQuantity=None)&~Q(initialDate=None)&Q(volumeOutcome=None)&Q(measurementExecuted=0)&Q(deleteTimestamp=None)).order_by('validationTimestamp','initialDate','id')
    #devo filtrare ulteriormente dividendo in due liste le derivazioni che prevedono
    #un kit e quelle che non ce l'hanno
    liskitsi=[]
    for aliq in aliq_da_derivare:
        if aliq.idDerivationProtocol.idKitType!=None:
            liskitsi.append(aliq)
    print 'kitsi',liskitsi
    #se c'e' qualche derivazione che ha bisogno del kit, allora faccio comparire come al solito
    #la schermata del passo 2 della derivazione
    stringat=''
    for alder in liskitsi:
        stringat+=alder.idAliquot.uniqueGenealogyID+'&'
    stringtotale=stringat[:-1]
    diz=AllAliquotsContainer(stringtotale)
    lisaliq=[]
    lisbarc=[]
    lispos=[]
    for al in liskitsi:
        listatemp=diz[al.idAliquot.uniqueGenealogyID]
        for val in listatemp:
            ch=val.split('|')
            lisaliq.append(al)
            lisbarc.append(ch[1])
            lispos.append(ch[2])
    variables = RequestContext(request,{'lista':zip(lisaliq,lisbarc,lispos),'robot':robot})
    return render_to_response('tissue2/derived/save_kit.html',variables)

#per caricare la schermata per il secondo passo della derivazione, quello in cui
#inserisco il kit
@transaction.commit_on_success
@laslogin_required
@login_required
#@user_passes_test(lambda u: u.has_perm('tissue.can_view_select_kit'),login_url=settings.BASE_URL+'/tissue/error/')
@permission_decorator('tissue.can_view_BBM_select_kit')
def SaveKitDerivedAliquots(request):
    if request.method=='POST':
        print request.POST
        try:
            name=request.user.username
            robot=request.POST.get('robot')
            featrobot=FeatureDerivation.objects.get(name='Robot')
            lisprotrobot=FeatureDerProtocol.objects.filter(idFeatureDerivation=featrobot).values_list('idDerProtocol',flat=True)
            if robot=='True':
                aliq_da_derivare=AliquotDerivationSchedule.objects.filter(Q(derivationExecuted=0)&Q(Q(operator=name)|Q(operator=''))&~Q(idDerivationProtocol=None)&Q(idDerivationProtocol__in=lisprotrobot)&Q(idKit=None)&~Q(loadQuantity=None)&~Q(initialDate=None)&Q(volumeOutcome=None)&Q(measurementExecuted=0)&Q(deleteTimestamp=None)).order_by('validationTimestamp','initialDate','id')
            else:
                aliq_da_derivare=AliquotDerivationSchedule.objects.filter(Q(derivationExecuted=0)&Q(Q(operator=name)|Q(operator=''))&~Q(idDerivationProtocol=None)&~Q(idDerivationProtocol__in=lisprotrobot)&Q(idKit=None)&~Q(loadQuantity=None)&~Q(initialDate=None)&Q(volumeOutcome=None)&Q(measurementExecuted=0)&Q(deleteTimestamp=None)).order_by('validationTimestamp','initialDate','id')
            
            liskitsi=[]
            for aliq in aliq_da_derivare:                
                if aliq.idDerivationProtocol.idKitType!=None:
                    liskitsi.append(aliq)
            print 'kitsi',liskitsi
            i=0
            for alsched in liskitsi:
                kit='kit_'+str(i)
                #solo se per quella aliquota e' stato inserito il kit, 
                #altrimenti lo salto
                s_kit=request.POST.get(kit)
                if s_kit !='':
                    #iexact per renderlo insensibile a maiuscole, minuscole
                    sin_kit=Kit.objects.get(barcode__iexact=s_kit,remainingCapacity__gt=0)
                    print 'kit',sin_kit
                    alsched.idKit=sin_kit
                    alsched.save()
                i+=1
            if 'stop' in request.POST:
                #vuol dire che devo terminare qui la procedura
                variables = RequestContext(request,{'fine':True})
                return render_to_response('tissue2/derived/save_kit.html',variables)
            if 'next' in request.POST:
                if robot=='True':
                    #devo caricare la schermata di inserimento misure apposta per il robot
                    return LoadInsertMeasure(request)
                else:
                    return LoadDetailsDerivedAliquots2(request)
        except Exception,e:
            print 'err',e
            transaction.rollback()
            errore=True
            variables = RequestContext(request, {'errore':errore})
            return render_to_response('tissue2/index.html',variables)
        
#per caricare la schermata per il terzo passo della derivazione
@laslogin_required
@login_required
#@user_passes_test(lambda u: u.has_perm('tissue.can_view_perform_QC_QA'),login_url=settings.BASE_URL+'/tissue/error/')
@permission_decorator('tissue.can_view_BBM_perform_QC_QA')
def LoadDetailsDerivedAliquots2(request):
    name=request.user.username
    lista2=[]
    expvol=FeatureDerivation.objects.get(name='ExpectedVolume')
    print 'expvol',expvol
    #devo prendere solo le derivazioni i cui protocolli non prevedono robot
    featrobot=FeatureDerivation.objects.get(name='Robot')
    lisderprot=FeatureDerProtocol.objects.filter(idFeatureDerivation=featrobot).values_list('idDerProtocol',flat=True)
    aliq_da_derivare=AliquotDerivationSchedule.objects.filter(Q(derivationExecuted=0)&Q(Q(operator=name)|Q(operator=''))&~Q(idDerivationProtocol=None)&~Q(idDerivationProtocol__in=lisderprot)&~Q(loadQuantity=None)&~Q(initialDate=None)&Q(volumeOutcome=None)&Q(measurementExecuted=0)&Q(deleteTimestamp=None)).order_by('validationTimestamp','initialDate','id')
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
    #print 'listavol',listavol
    print 'listavolattesi',lista2
    variables = RequestContext(request,{'lista':zip(lisaliq,lisbarc,lispos,lista2)})
    return render_to_response('tissue2/derived/2.details.html',variables)  

#per far comparire la schermata delle misure nelle aliquote derivate o nelle rivalutazioni
@laslogin_required
@login_required
#@user_passes_test(lambda u: u.has_perm('tissue.can_view_perform_QC_QA'),login_url=settings.BASE_URL+'/tissue/error/')
@permission_decorator('tissue.can_view_BBM_perform_QC_QA')
def DerivedAliquotsMeasure(request):
    print 'chiamata measure'
    if request.session.has_key('protqual'):
        lprot=request.session.get('protqual')
    if request.session.has_key('genealogyidaliqmeasure'):
        gen=request.session.get('genealogyidaliqmeasure')
    if request.session.has_key('idalderaliqmeasure'):
        idalder=request.session.get('idalderaliqmeasure')
    try:
        if request.method=='POST':
            print 'post'
            if 'primo' in request.POST:
                print request.POST
                #prendo il tipo di aliquota che ottengo con la derivazione (ad es DNA)
                #in base al genid (che leggo dalla post) dell'aliquota da derivare
                gen=request.POST.get('gen')
                al=Aliquot.objects.get(uniqueGenealogyID=gen,availability=1)
                print 'gen',gen
                print 'al',al.idAliquotType
                if 'revaluate' in request.POST:
                    tipoaliq=AliquotType.objects.get(id=al.idAliquotType.id)
                    print 'tipoaliq',tipoaliq
                    idalder=''
                else:
                    #aldersched=AliquotDerivationSchedule.objects.get(idAliquot=al,derivationExecuted=0,deleteTimestamp=None,loadQuantity__isnull=False,measurementExecuted=0)
                    idalder=request.POST.get('idaldersched')
                    aldersched=AliquotDerivationSchedule.objects.get(id=idalder)
                    tipoaliq=AliquotType.objects.get(id=aldersched.idDerivedAliquotType.id)
                    print 'aliq',tipoaliq
                lista=QualityProtocol.objects.filter(idAliquotType=tipoaliq)
                print 'lista',lista
                request.session['protqual']=lista
                request.session['genealogyidaliqmeasure']=gen
                request.session['idalderaliqmeasure']=idalder
                print 'idalder',idalder
                variables = RequestContext(request,{'lista':lista,'gen':gen,'idalder':idalder})
                return render_to_response('tissue2/derived/measure.html',variables) 
        variables = RequestContext(request,{'lista':lprot,'gen':gen,'idalder':idalder})
        return render_to_response('tissue2/derived/measure.html',variables) 
    except Exception,e:
        print 'err',e

#per salvare in un dizionario i dati delle misure per ogni singola aliquota
@laslogin_required
@login_required
#@user_passes_test(lambda u: u.has_perm('tissue.can_view_perform_QC_QA'),login_url=settings.BASE_URL+'/tissue/error/')
@permission_decorator('tissue.can_view_BBM_perform_QC_QA')
def DerivedAliquotsMeasureSave(request):
    if request.session.has_key('derivedmeasure'):
        dictmeasure=request.session.get('derivedmeasure')
    else:
        dictmeasure={}
    if request.session.has_key('revaluedmeasure'):
        revmeasure=request.session.get('revaluedmeasure')
    else:
        revmeasure={}
    if request.method=='POST':
        print request.POST
        print request.FILES
        #ho i dati del primo form, quello che discrimina tra i tipi di protocolli di misurazione
        if 'Prot_Type' in request.POST:
            tutti='False'
            tipoprot=request.POST.get('Prot_Type')
            genid=request.POST.get('geneal')
            al=Aliquot.objects.get(uniqueGenealogyID=genid,availability=1)
            qualprot=QualityProtocol.objects.get(id=tipoprot)
            #solo se sono nelle misure per i derivati e non nelle rivalutazioni
            if 'riv' not in request.POST:                
                #aldersched=AliquotDerivationSchedule.objects.get(idAliquot=al,derivationExecuted=0,deleteTimestamp=None,loadQuantity__isnull=False,measurementExecuted=0)
                idalder=request.POST.get('idaldersched')
                aldersched=AliquotDerivationSchedule.objects.get(id=idalder)
                #prendo il derivation protocol e passo all'html il nome del protocollo
                prot=DerivationProtocol.objects.get(id=aldersched.idDerivationProtocol.id)
                #per sostituire gli spazi con il %20 riconosciuto da html
                n=prot.name;
                print 'nome',prot.name
                rival=False
            #se sto rivalutando
            else:
                n=qualprot.name
                rival=True
                idalder=''
            #se sto usando la schermata per la parte in cui si misurano le aliq tutte
            #insieme
            if 'tutti' in request.POST:
                tutti='True'
            misure=MeasureParameter.objects.filter(idQualityProtocol=qualprot)
            diz=AllAliquotsContainer(al.uniqueGenealogyID)
            listatemp=diz[al.uniqueGenealogyID]
            for val in listatemp:
                ch=val.split('|')                        
                barc=ch[1]
                pos=ch[2]
                
            variables = RequestContext(request,{'lista':misure,'gen':genid,'barc':barc,'pos':pos,'proto':qualprot,'nomeproto':n,'all':tutti,'al':al,'riv':rival,'idalder':idalder})
            return render_to_response('tissue2/derived/measure_save.html',variables) 
        #ho i dati delle misure effettive
        else:
            strgenerale=''
            genid=request.POST.get('genealogy')
            al=Aliquot.objects.get(uniqueGenealogyID=genid)
            protoco=request.POST.get('tipoprot')
            #all'inizio della stringa ho il tipo di protocollo
            strgenerale=strgenerale+protoco+'|'
            #metto nella stringa generale il volume usato per le misure
            volusato=request.POST.get('volusato')
            strgenerale=strgenerale+volusato+'|'
            #metto nella stringa generale il volume attuale che ha senso solo nelle rivalutazioni
            if 'volattuale' in request.POST:
                volatt=request.POST.get('volattuale')
            else:
                volatt=''
            strgenerale=strgenerale+volatt+'|'
            idalder=request.POST.get('idaldersched')
            lunghezza=request.POST.get('lung')
            if 'scelta_conc' in request.POST:
                scelta=request.POST.get('scelta_conc')
                print 'scelta',scelta
            for i in range(0,int(lunghezza)):
                stringa=''
                #preparo i nomi con cui accedere alla request.post
                tipo='tipo_'+str(i)
                unita='unit_'+str(i)
                tipstrum='tipostrum_'+str(i)
                cstrum='codstrum_'+str(i)
                valore='val_'+str(i)
                nuova='nuovamis_'+str(i)
                #accedo alla post
                tipomis=request.POST.get(tipo).strip()
                unitmis=request.POST.get(unita).strip()
                tipostrumento=request.POST.get(tipstrum).strip()
                codstrumento=request.POST.get(cstrum).strip()
                val=request.POST.get(valore).strip()
                if val!='':
                    #devo vedere se la misura e' GE/Vex, allora devo dividere il valore per il volume preso
                    if tipomis=='GE/Vex' and 'riv' not in request.POST:
                        #name=request.user.username
                        #aliqq=Aliquot.objects.get(uniqueGenealogyID=genid)
                        #prendo il volume caricato
                        #aliqder=AliquotDerivationSchedule.objects.get(Q(idAliquot=aliqq)&Q(derivationExecuted=0)&Q(Q(operator=name)|Q(operator=''))&~Q(idDerivationProtocol=None)&~Q(idKit=None)&~Q(loadQuantity=None)&~Q(initialDate=None)&Q(volumeOutcome=None)&Q(measurementExecuted=0)&Q(deleteTimestamp=None))
                        aliqder=AliquotDerivationSchedule.objects.get(id=idalder)
                        #converto in ml il volume, che e' in ul
                        load=aliqder.loadQuantity
                        loadquant=float(load)/1000.0
                        val=float(val)/loadquant
                        val=str(round(val,2))
                    #devo distinguere tra il caso in cui il nome dello strum e' scritto 
                    #nella pagina e il caso in cui e' scelto dal menu' a tendina
                    if nuova in request.POST:
                        listastrum=Instrument.objects.filter(id=tipostrumento)
                        if listastrum.count()!=0:
                            tipos=listastrum[0].name
                            print 't',tipos
                            tipostrumento=tipos
                            print 'nomestrum',tipostrumento
                    stringa=stringa+tipomis+'&'+unitmis+'&'+str(tipostrumento)+'&'+codstrumento+'&'+val+'&'
                    #se ho dovuto scegliere la concentrazione
                    if 'scelta_conc' in request.POST:
                        if str(i)==scelta:
                            #metto in fondo alla stringa la parola 'scelta'
                            stringa=stringa+'scelta&'
                    #tolgo l'ultima & alla fine della stringa
                    lung=len(stringa)-1
                    stringanuova=stringa[:lung]
                    strgenerale=strgenerale+stringanuova+'|'
            print 'str',strgenerale
            #mi occupo dell'eventuale file e del giudizio
            if 'image' in request.FILES:
                f=request.FILES['image']
                fn = os.path.basename(f.name)
                percorso=os.path.join(os.path.dirname(__file__),'tissue_media/Derived_temporary/'+fn)
                open(percorso, 'wb').write(f.read())
                print 'Il file "' + fn + '" e\' stato caricato'
                #in 'immagine' ho il nome del file da salvare nel db
                immagine=f.name
                #accedo al valore del giudizio
                giud=request.POST.get('judge')
                strgenerale=strgenerale+immagine+'&'+giud
            else:
                #metto alla fine una lettera fittizia per capire che non c'e' il file
                strgenerale=strgenerale+' & ' 
            if 'riv' in request.POST:
                revmeasure[genid]=strgenerale
                request.session['revaluedmeasure']=revmeasure
                print 'dict rev',revmeasure
            else:   
                dictmeasure[genid+'|'+idalder]=strgenerale
                request.session['derivedmeasure']=dictmeasure
                print 'dict',dictmeasure
            #guardo se sto usando la vista per il caso in cui devo misurare tutte
            #le aliq insieme
            tutti=request.POST.get('tutti')
            if tutti=='False':
                fine=True
                variables = RequestContext(request,{'fine':fine,'genid':genid,'al':al})
                return render_to_response('tissue2/derived/measure_save.html',variables) 
            else:
                #nel caso usi questa schermata per la rivalutazione
                if 'riv' in request.POST:
                    lista=request.session.get('ListaGenMeasureAllRevaluate')
                    print 'listariv',lista
                    lista.remove(genid)
                    request.session['ListaGenMeasureAllRevaluate']=lista
                else:
                    lista=request.session.get('ListaGenealogyMeasureAll')
                    print 'lista',lista                    
                    lista.pop(0)
                    dizaliqdersched=request.session.get('dizAliqDerSchedMeasureAll')
                    print 'dizaliqdersched',dizaliqdersched
                    lischiavi=dizaliqdersched.keys()
                    chiavemin=min(lischiavi)
                    del dizaliqdersched[chiavemin]
                    request.session['ListaGenealogyMeasureAll']=lista
                if len(lista)!=0:
                    gen=lista[0]
                    al=Aliquot.objects.get(uniqueGenealogyID=gen)
                    qualprot=QualityProtocol.objects.get(id=protoco)
                    #solo se sono nelle misure per i derivati e non nelle rivalutazioni
                    if 'riv' not in request.POST:
                        lischiavi=dizaliqdersched.keys()
                        chiavemin=min(lischiavi)
                        idaliqdersched=dizaliqdersched[chiavemin]
                        #aldersched=AliquotDerivationSchedule.objects.get(idAliquot=al,derivationExecuted=0,deleteTimestamp=None,loadQuantity__isnull=False,measurementExecuted=0)
                        aldersched=AliquotDerivationSchedule.objects.get(id=idaliqdersched)
                        #prendo il derivation protocol e passo all'html il nome del protocollo
                        prot=DerivationProtocol.objects.get(id=aldersched.idDerivationProtocol.id)
                        #per sostituire gli spazi con il %20 riconosciuto da html
                        n=prot.name;
                        print 'nome',prot.name
                        rival=False
                    #se sto rivalutando
                    else:
                        n=qualprot.name
                        rival=True
                        idaliqdersched=''
                    #se sto usando la schermata per la parte in cui si misurano le aliq tutte
                    #insieme
                    tutti='True'
                    misure=MeasureParameter.objects.filter(idQualityProtocol=qualprot)
                    diz=AllAliquotsContainer(al.uniqueGenealogyID)
                    listatemp=diz[al.uniqueGenealogyID]
                    for val in listatemp:
                        ch=val.split('|')                        
                        barc=ch[1]
                        pos=ch[2]
                    variables = RequestContext(request,{'lista':misure,'gen':gen,'barc':barc,'pos':pos,'proto':qualprot,'nomeproto':n,'all':tutti,'al':al,'riv':rival,'idalder':idaliqdersched})
                    return render_to_response('tissue2/derived/measure_save.html',variables) 
                else:
                    fine=True
                    tutti='True'
                    variables = RequestContext(request,{'fine':fine,'genid':genid,'all':tutti,'al':al})
                    return render_to_response('tissue2/derived/measure_save.html',variables) 

#per far comparire la schermata che visualizza le misure effettuate per un'aliquota
@laslogin_required
@login_required
#@user_passes_test(lambda u: u.has_perm('tissue.can_view_perform_QC_QA'),login_url=settings.BASE_URL+'/tissue/error/')
@permission_decorator('tissue.can_view_BBM_perform_QC_QA')
def DerivedAliquotsMeasureView(request):
    print 'chiamata measure view'
    if request.session.has_key('derivedmeasure'):
        dictmeasure=request.session.get('derivedmeasure')
    else:
        dictmeasure={}
    if request.session.has_key('revaluedmeasure'):
        revmeasure=request.session.get('revaluedmeasure')
    else:
        revmeasure={}
    if request.session.has_key('genealogyMeasureView'):
        gen=request.session.get('genealogyMeasureView')  
    else:
        gen=''
    if request.session.has_key('listaGenMisure'):
        listagen=request.session.get('listaGenMisure')
    if request.method=='POST':
        print 'post meaview'
        if 'primo' in request.POST:
            print request.POST
            listagen=[]
            #prendo l'aliquota di cui visualizzare le misure
            genid=request.POST.get('gen')
            if 'riv' in request.POST:
                if revmeasure.has_key(genid):
                    valori=revmeasure.pop(genid)
                    revmeasure[genid]=valori
                else:
                    errore=True
                    print 'err interno',errore
                    if request.session.has_key('genealogyMeasureView'):
                        del request.session['genealogyMeasureView']
                    variables = RequestContext(request,{'errore':errore})
                    return render_to_response('tissue2/derived/measure_view.html',variables)
            else:
                idalder=request.POST.get('idaldersched')
                if dictmeasure.has_key(genid+'|'+idalder):
                    valori=dictmeasure[genid+'|'+idalder]
                elif dictmeasure.has_key(genid):
                    valori=dictmeasure[genid]
                else:
                    errore=True
                    print 'err interno',errore
                    if request.session.has_key('genealogyMeasureView'):
                        del request.session['genealogyMeasureView']
                    variables = RequestContext(request,{'errore':errore})
                    return render_to_response('tissue2/derived/measure_view.html',variables)
            print 'val',valori
            #in lista ho i valori di una singola misura
            lista=valori.split('|')
            #parto da 3 perche' nel primo posto della lista ho il numero di protocollo
            #di qualita' e nel secondo ho il volume usato per le misure e nel terzo il vol attuale
            #solo nelle rivalutazioni
            for i in range(3,len(lista)-1):
                #in singola ho tutti i valori di una misura
                singola=lista[i].split('&')
                m=Misura(tipo=singola[0],
                         unit=singola[1],
                         tipostrum=singola[2],
                         codstrum=singola[3],
                         val=singola[4])
                listagen.append(m)
            request.session['listaGenMisure']=listagen
            
            request.session['genealogyMeasureView']=genid
            variables = RequestContext(request,{'lista':listagen})
            return render_to_response('tissue2/derived/measure_view.html',variables)
    if gen!='':
        variables = RequestContext(request,{'lista':listagen})
        return render_to_response('tissue2/derived/measure_view.html',variables)
    else:
        errore=True
        print 'err',errore
        variables = RequestContext(request,{'errore':True})
        return render_to_response('tissue2/derived/measure_view.html',variables)
    
#per far comparire la schermata delle misure per misurare insieme tutte le aliquote
@laslogin_required
@login_required
#@user_passes_test(lambda u: u.has_perm('tissue.can_view_perform_QC_QA'),login_url=settings.BASE_URL+'/tissue/error/')
@permission_decorator('tissue.can_view_BBM_perform_QC_QA')
def DerivedAliquotsMeasureAllAliquots(request):
    if request.session.has_key('ProtQualMeasureAll'):
        lprot=request.session.get('ProtQualMeasureAll')
    if request.session.has_key('GenealogyIdMeasureAll'):
        gen=request.session.get('GenealogyIdMeasureAll')
    if request.session.has_key('AlderSchedMeasureAll'):
        aldersched=request.session.get('AlderSchedMeasureAll')
    if request.session.has_key('campo_riv_misure'):
        rev=request.session.get('campo_riv_misure')
    if request.method=='POST':
        if 'primo' in request.POST:
            lista=[]
            listagenealogy=[]
            print request.POST
            #prendo il tipo di aliquota che ottengo con la derivazione (ad es DNA)
            #in base al primo genid (che leggo dalla post) dell'aliquota da derivare
            listagen=request.POST.get('gen')
            #e' formato da gen|idaldersched&gen|idaldersched            
            vv=listagen.split('&')
            #chiave il numero d'ordine e valore l'idaldersched relativo
            dizaldersched={}
            for i in range(0,(len(vv))-1):
                valori=vv[i].split('|')
                gen=valori[0]
                if len(valori)>1:                    
                    idaldersched=valori[1]
                    dizaldersched[i]=idaldersched
                listagenealogy.append(gen)
            print 'listagen',listagenealogy
            vesempio=vv[0].split('|')
            print 'vesempio',vesempio
            genesempio=vesempio[0]
            if len(vesempio)>1:                
                idalder=vesempio[1]
            else:
                idalder=''
            print 'genesempio',genesempio
            al=Aliquot.objects.get(uniqueGenealogyID=genesempio)
            print 'gen',genesempio
            print 'al',al.idAliquotType
            if 'revaluate' in request.POST:
                tipoaliq=AliquotType.objects.get(id=al.idAliquotType.id)
                print 'tipoaliq',tipoaliq
            else:
                #aldersched=AliquotDerivationSchedule.objects.get(idAliquot=al,derivationExecuted=0,deleteTimestamp=None,loadQuantity__isnull=False,measurementExecuted=0)
                aldersched=AliquotDerivationSchedule.objects.get(id=idalder)                
                tipoaliq=AliquotType.objects.get(id=aldersched.idDerivedAliquotType.id)
                print 'aliq',tipoaliq
            listaqual=QualityProtocol.objects.filter(idAliquotType=tipoaliq)
            for protocolli in listaqual:
                lista.append(protocolli)
            print 'listatutti',lista
            request.session['ProtQualMeasureAll']=lista
            request.session['GenealogyIdMeasureAll']=genesempio
            request.session['AlderSchedMeasureAll']=idalder
            if 'revaluate' in request.POST:
                request.session['ListaGenMeasureAllRevaluate']=listagenealogy
                rev='True'
            else:
                request.session['ListaGenealogyMeasureAll']=listagenealogy
                request.session['dizAliqDerSchedMeasureAll']=dizaldersched
                rev='False'
            request.session['campo_riv_misure']=rev
            tutti='True'
            print 'rev',rev
            variables = RequestContext(request,{'lista':lista,'gen':genesempio,'all':tutti,'idalder':idalder})
            return render_to_response('tissue2/derived/measure.html',variables)
    tutti='True'
    variables = RequestContext(request,{'lista':lprot,'gen':gen,'all':tutti,'rev':rev,'idalder':aldersched})
    return render_to_response('tissue2/derived/measure.html',variables)

#per permettere l'inserimento delle misure tramite file
#e' previsto solo per le derivazioni e non anche per le rivalutazioni perche' nelle rivalutazioni dovrei scegliere la 
#concentrazione effettiva da salvare e con il file non si puo'
#non e' supportato il caso di doppioni, cioe' la stessa aliquota pianificata due volte con due procedure diverse che si trovano entrambe al passo 3. In
#questo caso non e' possibile inserire il file perche' non saprei distinguere la procedura in questione leggendo semplicemente il genid dal file
@laslogin_required
@login_required
@permission_decorator('tissue.can_view_BBM_perform_QC_QA')
def DerivedAliquotsInsertMeasureFile(request):
    if request.method=='POST':
        print request.POST
        print request.FILES
        val=request.POST.get('template')
        
        listagen=request.session.get('ListaGenealogyMeasureAll')
        print 'lista',listagen
        val_prot=request.POST.get('tip_prot')
        qualprot=QualityProtocol.objects.get(id=val_prot)
        misure=MeasureParameter.objects.filter(idQualityProtocol=qualprot)
        
        if val=='vedi_file':
            name=request.user.username
            print 'name',name
            #vuol dire che l'utente ha cliccato sull'opzione che gli fa vedere il file
            #Excel precompilato            
            response = HttpResponse(mimetype='text/csv')
            response['Content-Disposition'] = 'attachment; filename=Insert_Measure.las'
            stringa=''
            string2=''
            for m in misure:
                nomemis=m.idMeasure.name
                if nomemis=='GE/Vex':
                    nomemis='GE'
                unit=m.idMeasure.measureUnit
                if unit=='GE/ml':
                    unit='[GE]'

                stringa+=nomemis+' '+unit+' '+m.idMeasure.idInstrument.name+' '+m.idMeasure.idInstrument.code+'\t'
                string2+='\t'

            writer = csv.writer(response)
            writer.writerow(['GenealogyID\tBarcode\tPosition\t'+stringa+'Used volume(ul)\tDerivation protocol'])
            j=1
            stringtot=''
            for gen in listagen:
                stringtot+=gen+'&'
            lgenfin=stringtot[:-1]
            diz=AllAliquotsContainer(lgenfin)
            for gen in listagen:
                al=Aliquot.objects.get(uniqueGenealogyID=gen,availability=1)
                if 'riv' not in request.POST:
                    aldersched=AliquotDerivationSchedule.objects.get(Q(idAliquot=al)&Q(derivationExecuted=0)&Q(deleteTimestamp=None)&Q(loadQuantity__isnull=False)&Q(measurementExecuted=0)&Q(Q(operator=name)|Q(operator='')))
                    #prendo il derivation protocol e prendo il suo nome
                    prot=DerivationProtocol.objects.get(id=aldersched.idDerivationProtocol.id)
                listatemp=diz[al.uniqueGenealogyID]
                for val in listatemp:
                    ch=val.split('|')
                    barc=ch[1]
                    pos=ch[2]
                writer.writerow([gen+'\t'+barc+'\t'+pos+'\t'+string2+str(qualprot.quantityUsed)+'\t'+prot.name])

            #response = HttpResponse(mimetype='application/vnd.ms-excel')                       
            return response
        
        if val=='ins_file':
            try:
                f=request.FILES['file']
                dizio={}
                dictmeasure={}
                for a in f.chunks():
                    #c e' un vettore e in ogni posto c'e' una riga del file
                    c=a.split('\n')
                    #la prima riga contiene l'intestazione del file con le misure e mi serve
                    #per capire come sono messi i valori all'interno
                    val_primariga=c[0].strip().split('\t')
                     
                    for m in misure: 
                        nomemis=m.idMeasure.name
                        if nomemis=='GE/Vex':
                            nomemis='GE'
                        unit=m.idMeasure.measureUnit
                        if unit=='GE/ml':
                            unit='[GE]'  
                        stringa_misure=nomemis+' '+unit+' '+m.idMeasure.idInstrument.name+' '+m.idMeasure.idInstrument.code               
                        k=0
                        for titoli in val_primariga:
                            if stringa_misure==titoli:
                                stringa_effett=m.idMeasure.name+'&'+m.idMeasure.measureUnit+'&'+m.idMeasure.idInstrument.name+'&'+m.idMeasure.idInstrument.code
                                dizio[k]=stringa_effett
                            k=k+1
                            
                    print 'dizio',dizio
                    #parto da 1 perche' la prima riga contiene l'intestazione
                    for i in range(1,len(c)):
                        c[i]=c[i].strip()
                        if c[i]!='':
                            riga_fin=c[i].split('\t')
                            gen=riga_fin[0]
                            #controllo che il gen che c'e' nel file ci sia nella lista
                            #dei gen da derivare
                            trovato=0
                            for g in listagen:
                                if g==gen:
                                    trovato=1
                            if trovato==0:
                                raise ErrorDerived('Error: aliquot '+gen+' is not in derivation list')
                            #il primo valore e' il gen, l'ultimo e' il protocollo di derivazione
                            stringa_gen=''
                            strgenerale=''
                            #all'inizio della stringa ho il gen ,barcode e posizione
                            strgenerale=strgenerale+val_prot+'|'
                            for j in range(3,len(riga_fin)-2):
                                misura=dizio[j]
                                #in misura ho la prima parte della stringa da salvare.
                                #Devo solo aggiungere il valore della misura
                                vall=riga_fin[j].replace(',','.')
                                #solo se il valore per la misura e' stato compilato
                                if vall!='':
                                    #print 'vall',vall
                                    try:
                                        valore=float(vall)
                                    except ValueError:
                                        raise ErrorDerived('Error: You can only insert number. Please correct value for aliquot '+gen)
                                    #devo vedere se la misura e' GE/Vex, allora devo dividere il valore per il volume preso
                                    missplit=misura.split('&')
                                    if missplit[0]=='GE/Vex':
                                        name=request.user.username
                                        aliqq=Aliquot.objects.get(uniqueGenealogyID=gen)
                                        #prendo il volume caricato
                                        aliqder=AliquotDerivationSchedule.objects.get(Q(idAliquot=aliqq)&Q(derivationExecuted=0)&Q(Q(operator=name)|Q(operator=''))&~Q(idDerivationProtocol=None)&~Q(idKit=None)&~Q(loadQuantity=None)&~Q(initialDate=None)&Q(measurementExecuted=0)&Q(deleteTimestamp=None))
                                        #converto in ml il volume, che e' in ul
                                        load=aliqder.loadQuantity
                                        loadquant=float(load)/1000.0
                                        valore=valore/loadquant
                                        valore=str(round(valore,2))
                                    
                                    stringa_gen=stringa_gen+misura+'&'+str(valore)+'|'
                            print 'str_gen',stringa_gen
                            #prendo il volume usato per le misure
                            volusatomisure=riga_fin[len(riga_fin)-2].replace(',','.')
                            print 'volusato misure',volusatomisure
                            #aggiungo un posto vuoto per il volume attuale, che pero' ha senso solo 
                            #nelle rivalutazioni
                            strgenerale+=volusatomisure+'||'
                            
                            strgenerale=strgenerale+stringa_gen
                            #metto alla fine una lettera fittizia per capire che non c'e' il file 
                            #con l'immagine. Ma in questo caso non ci sara' mai.
                            strgenerale=strgenerale+' & '
                
                            dictmeasure[gen]=strgenerale
                request.session['derivedmeasure']=dictmeasure
                print 'dict',dictmeasure
                #stringa=stringa+tipomis.lower()+'&'+unitmis+'&'+str(tipostrumento)+'&'+codstrumento+'&'+val+'&'
                
                fine=True
                tutti='True'
                variables = RequestContext(request,{'fine':fine,'all':tutti})
                return render_to_response('tissue2/derived/measure_save.html',variables)
            except ErrorDerived as e:
                print 'My exception occurred, value:', e.value
                variables = RequestContext(request, {'errore':e.value})
                return render_to_response('tissue2/derived/measure.html',variables)            
            except Exception, e:
                print 'err', e
                variables = RequestContext(request, {'errore':'Something went wrong. Probably you have to choose a correct measurement protocol'})
                return render_to_response('tissue2/derived/measure.html',variables)
            
#per confermare la schermata dei dettagli delle aliquote da derivare
@transaction.commit_on_success
@laslogin_required
@login_required
#@user_passes_test(lambda u: u.has_perm('tissue.can_view_perform_QC_QA'),login_url=settings.BASE_URL+'/tissue/error/')
@permission_decorator('tissue.can_view_BBM_perform_QC_QA')
def DetailsDerivedAliquots2(request):   
    name=request.user.username
    #devo prendere solo le derivazioni i cui protocolli non prevedono robot
    featrobot=FeatureDerivation.objects.get(name='Robot')
    lisderprot=FeatureDerProtocol.objects.filter(idFeatureDerivation=featrobot).values_list('idDerProtocol',flat=True)
    aliq_da_derivare=AliquotDerivationSchedule.objects.filter(Q(derivationExecuted=0)&Q(Q(operator=name)|Q(operator=''))&~Q(idDerivationProtocol=None)&~Q(idDerivationProtocol__in=lisderprot)&~Q(loadQuantity=None)&Q(volumeOutcome=None)&Q(measurementExecuted=0)&Q(deleteTimestamp=None)).order_by('validationTimestamp','initialDate','id')
    print 'aliq',aliq_da_derivare
    #devo filtrare ancora per togliere quelli che non hanno un kit, ma che dovrebbero averlo
    lisfin=[]
    for aliq in aliq_da_derivare:
        if aliq.idKit!=None or aliq.idDerivationProtocol.idKitType==None:
            lisfin.append(aliq)
    aliq_da_cancellare=[]
    aliq_da_svuotare=[]
    #lista_alder=[]
    lista_qualevent=[]
    if request.session.has_key('derivedmeasure'):
        dictmeasure=request.session.get('derivedmeasure')
    else:
        dictmeasure={}
    if request.method=='POST':
        try:
            print request.POST
            print 'aliq_da_derivare',lisfin
            for i in range(0,len(lisfin)):
                #preparo i nomi con cui accedere alla request.post
                outcome='outcome_'+str(i)
                gen='gen_'+str(i)
                #kit='kit_'+str(i)               
                
                protocollo='prot_'+str(i)
                geneal=request.POST.get(gen)
                proto=request.POST.get(protocollo)
                
                lista_aliquota=Aliquot.objects.filter(uniqueGenealogyID=geneal,availability=1)
                if lista_aliquota.count()!=0:
                    aliquota=lista_aliquota[0]
                print 'aliquota',aliquota

                #prendo il protocollo
                pro=DerivationProtocol.objects.get(id=proto)
                print 'prot',pro
                #prendo il derivation schedule
                #alder=AliquotDerivationSchedule.objects.get(idAliquot=aliquota,derivationExecuted=0,deleteTimestamp=None,loadQuantity__isnull=False,measurementExecuted=0)
                alder=lisfin[i]
                sin_kit=None
                if alder.idDerivationProtocol.idKitType!=None:
                    #mi occupo del singolo kit selezionato
                    sin_kit=Kit.objects.get(id=alder.idKit.id)
                print 'sin_kit',sin_kit
                #prendo la quantita' di liquido usata inizialmente
                quantit=alder.loadQuantity
                print 'quantita\' usata',quantit
                #per capire qual e' il tipo di derivato prodotto
                t=TransformationDerivation.objects.filter(idDerivationProtocol=pro)
                tipo=t[0].idTransformationChange.idToType.abbreviation
                print 'tipo derivato prodotto',tipo
            
                #se la derivazione e' fallita
                if outcome in request.POST:
                    print 'fallita'
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
                    #inserisco nella lista l'aliquota che sara' poi da cancellare perche' e' fallita la reazione
                    aliq_da_cancellare.append(alder)
                    
                    #incremento il numero di pezzi usati per quell'aliquota
                    pezzi_usati=aliquota.timesUsed
                    pezzi_usati=pezzi_usati+1
                    aliquota.timesUsed=pezzi_usati
                    aliquota.save()
                    
                    #salvo come eseguita la derivazione
                    alder.derivationExecuted=1
                    if alder.operator=='':
                        alder.operator=name
                    alder.save()
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
                        valore=AliquotFeature.objects.filter(Q(idAliquot=aliquota)&Q(idFeature=featvol[0]))
                        if len(valore)!=0:
                            #sottraggo il volume usato
                            ris=float(valore[0].value)-float(quantit)
                            print 'ris',ris
                            if ris<0:
                                ris=0.0
                            valore[0].value=float(ris)
                            valore[0].save()
                    
                    alder.idKit=sin_kit
                    alder.volumeOutcome=volume
                    alder.failed=fallita
                    alder.measurementExecuted=1
                    alder.save()
                    print 'alderrr',alder
                    #lista_alder.append(alder)
                else:
                    print 'riuscita'
                    fallita=0
                    #preparo i nomi con cui accedere alla request.post
                    vol='volume_'+str(i)
                    #accedo alla request
                    volume=request.POST.get(vol)
                    print 'vol',volume                    
                
                #controllo se sto estraendo da sangue intero(SF) o se sto estraendo plasma o PBMC
                #Lo faccio qui perche', visto che non inserisco misure, non entra enll'if dopo
                if (aliquota.idSamplingEvent.idTissueType.abbreviation=='BL' and aliquota.idAliquotType.abbreviation=='SF') or alder.idDerivedAliquotType.abbreviation=='PL' or alder.idDerivedAliquotType.abbreviation=='VT':
                    alder.idKit=sin_kit
                    alder.volumeOutcome=volume
                    alder.failed=fallita
                    alder.measurementExecuted=1
                    alder.save()
                    
                if dictmeasure.has_key(geneal) or dictmeasure.has_key(geneal+'|'+str(alder.id)):
                    alder.idKit=sin_kit
                    alder.volumeOutcome=volume
                    alder.failed=fallita
                    alder.measurementExecuted=1
                    alder.save()
                    print 'alderrr',alder
                    #lista_alder.append(alder)
    
                    #se la derivazione non e' fallita
                    if outcome not in request.POST:
                        mis_data='date_meas_'+str(i)
                        #data_misur ha la notazione anno-mese-giorno
                        data_misur=request.POST.get(mis_data)
                        
                        print 'dictmes',dictmeasure
                        if dictmeasure.has_key(geneal):
                            valori=dictmeasure[geneal]
                        elif dictmeasure.has_key(geneal+'|'+str(alder.id)):
                            valori=dictmeasure[geneal+'|'+str(alder.id)]
                        print 'val',valori
                        #dictmeasure[geneal]=valori
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
                                            idAliquot=aliquota,
                                            idAliquotDerivationSchedule=alder,
                                            misurationDate=data_misur,
                                            insertionDate=date.today(),
                                            operator=name,
                                            quantityUsed=volus)
                        qualev.save()
                        print 'qualev',qualev
                        lista_qualevent.append(qualev)
                        request.session['qualityEvent']=lista_qualevent
                        for i in range(3,len(lista)-1):
                            #in singola ho tutti i valori di una misura
                            val=lista[i].split('&')
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
                                #fvecchio=open(percorso, 'rb')
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
                #urllib2.urlopen(url, data)
                
            #tolgo dalla lista delle aliq da derivare le reazioni non andate a buon fine
            #aliq_da_derivare=list(aliq_da_derivare)
            #for j in range(0,len(aliq_da_cancellare)):
                #aliq_da_derivare.remove(aliq_da_cancellare[j]);
                #lista_alder.remove(aliq_da_cancellare[j])

            aliq_da_derivare=AliquotDerivationSchedule.objects.filter(Q(derivationExecuted=0)&Q(Q(operator=name)|Q(operator=''))&~Q(idDerivationProtocol=None)&~Q(idDerivationProtocol__in=lisderprot)&~Q(initialDate=None)&Q(measurementExecuted=1)&Q(deleteTimestamp=None)).order_by('validationTimestamp','initialDate','id')
            print 'al da der',aliq_da_derivare
            if len(aliq_da_derivare)!=0:               
                argument_list = []
                a=Collection()
                
                #prendo le concentrazioni esistenti
                misu=Measure.objects.filter(name='concentration')
                for m in misu:
                    argument_list.append( Q(**{'idMeasure': m} ))
                print 'lista qual event',lista_qualevent
                '''if len(lista_qualevent)==0:
                    qualev=QualityEvent.objects.get(idAliquotDerivationSchedule=aliq_da_derivare[0].id)
                    print 'qualev',qualev
                    lista_qualevent.append(qualev)'''
                #prendo il quality event
                lisqualev=QualityEvent.objects.filter(idAliquotDerivationSchedule=aliq_da_derivare[0].id).order_by('id')
                voltot=aliq_da_derivare[0].volumeOutcome
                if len(lisqualev)==0:
                    #non ho salvato un qualev perche' non ho fatto misure ad es per derivare dal sangue intero
                    conc=[]
                    volusato=0
                else:
                    #prendo il qualev piu' recente
                    qualev=lisqualev[len(lisqualev)-1]
                    #prendo il valore della concentrazione
                    conc=MeasurementEvent.objects.filter(Q(idQualityEvent=qualev)&Q(reduce(operator.or_, argument_list)))
                    print 'conc',conc
                    #per il volume dell'aliq madre. Devo sottrarre il volume usato per le misure
                    volusato=qualev.quantityUsed
                    if volusato==None:
                        volusato=0                   
                    
                voleffettivo=voltot-volusato                
                #per passare l'aliquota
                g=aliq_da_derivare[0].idAliquot.uniqueGenealogyID
                print 'gggg',g

                lista_aliquota=Aliquot.objects.filter(uniqueGenealogyID=g,availability=1)
                if lista_aliquota.count()!=0:
                    al=lista_aliquota[0]
                print 'al',al
                derprot=aliq_da_derivare[0].idDerivationProtocol.name
                derprot=derprot.replace(' ','%20');
                #per capire qual e' il tipo di derivato prodotto
                t=TransformationDerivation.objects.filter(idDerivationProtocol=aliq_da_derivare[0].idDerivationProtocol.id)
                tipo=t[0].idTransformationChange.idToType.abbreviation
                tipoesteso=t[0].idTransformationChange.idToType.longName.replace(' ','%20')
                print 'tipo derivato prodotto',tipo
                #apro il file con dentro i parametri per la derivazione
                percorso=os.path.join(os.path.dirname(__file__),'tissue_media/File_Format/Regole_aliq_derivate.txt')
                print 'perc',percorso
                f=open(percorso)
                lines = f.readlines()
                f.close()
                riga=''
                
                #prendo il protocollo di derivazione
                dprot=aliq_da_derivare[0].idDerivationProtocol
                numal=FeatureDerivation.objects.get(name='number_Aliquot')
                volal=FeatureDerivation.objects.get(name='volume_Aliquot')
                concal=FeatureDerivation.objects.get(name='concentration_Aliquot')
                featnumal=FeatureDerProtocol.objects.get(idDerProtocol=dprot,idFeatureDerivation=numal)
                num_aliq=int(featnumal.value)
                featvolal=FeatureDerProtocol.objects.get(idDerProtocol=dprot,idFeatureDerivation=volal)
                vol=featvolal.value
                featconcal=FeatureDerProtocol.objects.get(idDerProtocol=dprot,idFeatureDerivation=concal)
                concen=featconcal.value
                riga+=tipo+';'+str(num_aliq)+';'+str(vol)+';'+str(concen)+';'
                for line in lines:
                    valori=line.split(';')
                    #se ho trovato la riga giusta che inizia con il nome del derivato
                    if valori[0]==tipo:
                        riga+=valori[1]+';'+valori[2]+';'+valori[3].strip()
                        break
                print 'riga',riga
                                
                lista=[]
                #riempio la lista con il giusto numero di aliquote
                for i in range (0,5):
                    lista.append(i+1)
                if 'stop' in request.POST:
                    #vuol dire che devo terminare qui la procedura
                    variables = RequestContext(request,{'fine':True})
                    return render_to_response('tissue2/derived/2.details.html',variables)
                if 'next' in request.POST:  
                    #aliq_da_derivare=AliquotDerivationSchedule.objects.filter(Q(derivationExecuted=0)&Q(operator=name)&~Q(idDerivationProtocol=None)&~Q(idKit=None)&~Q(loadQuantity=None)&~Q(initialDate=None)&~Q(volumeOutcome=None)&Q(measurementExecuted=1)&Q(deleteTimestamp=None)).order_by('id')
                    print 'volume',aliq_da_derivare[0].volumeOutcome
                    strgen=''
                    for alder in aliq_da_derivare:
                        strgen+=alder.idAliquot.uniqueGenealogyID+'&'
                    lgenfin=strgen[:-1]
                    diz=AllAliquotsContainer(lgenfin)
                    request.session['dizinfoaliqderivare']=diz
                    
                    valori=diz[al.uniqueGenealogyID]
                    val=valori[0].split('|')
                    barc=val[1]
                    pos=val[2]
                    print 'barc',barc
                    print 'pos',pos
                    
                    lisaliquote=[]
                    lisbarc=[]
                    lispos=[]
                    for alder in aliq_da_derivare:
                        valori=diz[alder.idAliquot.uniqueGenealogyID]
                        val=valori[0].split('|')
                        barcode=val[1]
                        position=val[2]
                        lisaliquote.append(alder)
                        lisbarc.append(barcode)
                        lispos.append(position)
                    
                    request.session['lista_al_der_sessione']=aliq_da_derivare
                    variables = RequestContext(request,{'aliquota':al,'a':a,'lista':lista,'barc':barc,'pos':pos,'volume':voleffettivo,'conc':conc,'derprot':derprot,'riga':riga,'aliq_da_derivare':zip(lisaliquote,lisbarc,lispos),'indice':1,'tipoesteso':tipoesteso,'dizcamb':{},'dizposauto':{}})
                    return render_to_response('tissue2/derived/end_derived.html',variables)
            else:    
                if 'stop' in request.POST:
                    #vuol dire che devo terminare qui la procedura
                    variables = RequestContext(request,{'vuota':True})
                    return render_to_response('tissue2/derived/2.details.html',variables)
                if 'next' in request.POST:
                    variables = RequestContext(request,{'vuota':True})
                    return render_to_response('tissue2/derived/end_derived.html',variables)
        except Exception,e:
            print 'errr',e
            transaction.rollback()
            errore=True
            variables = RequestContext(request, {'errore':errore})
            return render_to_response('tissue2/index.html',variables)

#per caricare la schermata per l'ultimo passo della derivazione
@laslogin_required
@login_required
#@user_passes_test(lambda u: u.has_perm('tissue.can_view_create_derivatives'),login_url=settings.BASE_URL+'/tissue/error/')
@permission_decorator('tissue.can_view_BBM_create_derivatives')
def LoadLastPartDerivedAliquots(request):
    request.session['indice']=1
    request.session['listapiastrealiqderivate']=[]
    request.session['dictaliqderivate']={}
    request.session['listaValAliqDer']=[]
    request.session['lista_al_der_sessione']=[]
    name=request.user.username
    featrobot=FeatureDerivation.objects.get(name='Robot')
    lisderprot=FeatureDerProtocol.objects.filter(idFeatureDerivation=featrobot).values_list('idDerProtocol',flat=True)
    aliq_da_derivare=AliquotDerivationSchedule.objects.filter(Q(derivationExecuted=0)&Q(Q(operator=name)|Q(operator=''))&~Q(idDerivationProtocol=None)&~Q(idDerivationProtocol__in=lisderprot)&~Q(initialDate=None)&Q(measurementExecuted=1)&Q(deleteTimestamp=None)).order_by('validationTimestamp','initialDate','id')
    #solo se c'e' qualche aliquota da derivare effettivamente
    print 'lung',len(aliq_da_derivare)
    print 'lista', aliq_da_derivare
    if len(aliq_da_derivare)!=0:
        request.session['lista_al_der_sessione']=aliq_da_derivare
        strgen=''
        for alder in aliq_da_derivare:
            strgen+=alder.idAliquot.uniqueGenealogyID+'&'
        al=aliq_da_derivare[0].idAliquot
        a=Collection()
        lista=[]
        argument_list = []
        #riempio la lista con il giusto numero di aliquote
        for i in range (0,5):
            lista.append(i+1)
            
        #prendo le concentrazioni esistenti
        misu=Measure.objects.filter(Q(name='concentration'))
        for m in misu:
            argument_list.append( Q(**{'idMeasure': m} ))
        #prendo il quality event
        lisqualev=QualityEvent.objects.filter(idAliquotDerivationSchedule=aliq_da_derivare[0].id).order_by('id')
        voltot=aliq_da_derivare[0].volumeOutcome
        if len(lisqualev)==0:
            #non ho salvato un qualev perche' non ho fatto misure, ad es per derivare dal sangue intero
            conc=[]
            volusato=0
        else:
            #prendo il qualev piu' recente
            qualev=lisqualev[len(lisqualev)-1]
            #prendo il valore della concentrazione
            conc=MeasurementEvent.objects.filter(Q(idQualityEvent=qualev)&Q(reduce(operator.or_, argument_list)))
            print 'conc',conc
            #per il volume dell'aliq madre. Devo sottrarre il volume usato per le misure
            volusato=qualev.quantityUsed
            if volusato==None:
                volusato=0
        
        voleffettivo=voltot-volusato
        
        derprot=aliq_da_derivare[0].idDerivationProtocol.name
        derprot=derprot.replace(' ','%20');
        #per capire qual e' il tipo di derivato prodotto
        t=TransformationDerivation.objects.filter(idDerivationProtocol=aliq_da_derivare[0].idDerivationProtocol.id)
        tipo=t[0].idTransformationChange.idToType.abbreviation
        tipoesteso=t[0].idTransformationChange.idToType.longName.replace(' ','%20')
        print 'tipo derivato prodotto',tipo
        #apro il file con dentro i parametri per la derivazione
        percorso=os.path.join(os.path.dirname(__file__),'tissue_media/File_Format/Regole_aliq_derivate.txt')
        print 'perc',percorso
        f=open(percorso)
        lines = f.readlines()
        f.close()
        riga=''
        #prendo il protocollo di derivazione
        dprot=aliq_da_derivare[0].idDerivationProtocol
        numal=FeatureDerivation.objects.get(name='number_Aliquot')
        volal=FeatureDerivation.objects.get(name='volume_Aliquot')
        concal=FeatureDerivation.objects.get(name='concentration_Aliquot')
        featnumal=FeatureDerProtocol.objects.get(idDerProtocol=dprot,idFeatureDerivation=numal)
        num_aliq=int(featnumal.value)
        featvolal=FeatureDerProtocol.objects.get(idDerProtocol=dprot,idFeatureDerivation=volal)
        vol=featvolal.value
        featconcal=FeatureDerProtocol.objects.get(idDerProtocol=dprot,idFeatureDerivation=concal)
        concen=featconcal.value
        riga+=tipo+';'+str(num_aliq)+';'+str(vol)+';'+str(concen)+';'
        for line in lines:
            valori=line.split(';')
            #se ho trovato la riga giusta che inizia con il nome del derivato
            if valori[0]==tipo:
                riga+=valori[1]+';'+valori[2]+';'+valori[3].strip()
                break
        print 'riga',riga
        
        lgenfin=strgen[:-1]
        diz=AllAliquotsContainer(lgenfin)
        request.session['dizinfoaliqderivare']=diz
        
        valori=diz[al.uniqueGenealogyID]
        val=valori[0].split('|')
        barc=val[1]
        pos=val[2]
        print 'barc',barc
        print 'pos',pos
        
        lisaliquote=[]
        lisbarc=[]
        lispos=[]
        for alder in aliq_da_derivare:
            valori=diz[alder.idAliquot.uniqueGenealogyID]
            val=valori[0].split('|')
            barcode=val[1]
            position=val[2]
            lisaliquote.append(alder)
            lisbarc.append(barcode)
            lispos.append(position)
        #dizposauto={0: {'pospezzi':'3', 'vertoriz':'oriz', 'automatic':'Yes', 'choose':'plate', 'barcode':'rna11'}, 1: {'pospezzi':'1', 'vertoriz':'vert', 'automatic': 'Yes', 'choose': 'plate', 'barcode':'rna13'}}
        variables = RequestContext(request,{'aliquota':al,'a':a,'lista':lista,'barc':barc,'pos':pos,'volume':voleffettivo,'conc':conc,'derprot':derprot,'riga':riga,'aliq_da_derivare':zip(lisaliquote,lisbarc,lispos),'indice':1,'tipoesteso':tipoesteso,'dizcamb':{},'dizposauto':{}})
        return render_to_response('tissue2/derived/end_derived.html',variables)  
    else:
        variables = RequestContext(request,{'vuota':True})
        return render_to_response('tissue2/derived/end_derived.html',variables)

#viene chiamata per ogni aliquota presente nella lista delle aliquote da derivare
@transaction.commit_on_success
@laslogin_required
@login_required
#@user_passes_test(lambda u: u.has_perm('tissue.can_view_create_derivatives'),login_url=settings.BASE_URL+'/tissue/error/')
@permission_decorator('tissue.can_view_BBM_create_derivatives')
def LastPartDerivedAliquots(request):
    lista_al_der=[]
    if request.session.has_key('listapiastrealiqderivate'):
        listapias=request.session.get('listapiastrealiqderivate')
    else:
        listapias=[]
    if request.session.has_key('indice'):
        indice_gen=request.session.get('indice')
    else:
        indice_gen=1
    if request.session.has_key('lista_aliquote_der'):
        lista_al_der=request.session.get('lista_aliquote_der') 
    if request.session.has_key('listaValAliqDer'):
        lista_val_aliq_der=request.session.get('listaValAliqDer') 
    else:
        lista_val_aliq_der=[]
    if request.session.has_key('dictaliqderivate'):
        dictnum=request.session.get('dictaliqderivate')
    else:
        dictnum={}
    
    if request.method=='POST':
        print request.POST
        try:
            #con javascript faccio una post che mi fa scattare questo if. Salvo i dati nella sessione
            #per poi riprenderli dopo quando clicco su confirm all
            if 'posizione' in request.POST:
                #posiznuova=request.POST.get('posnuova')
                #num=request.POST.get('numero')
                #piastradest=request.POST.get('barcodedest').strip()
                #dictnum[num]=posiznuova+'|'+piastradest
                dictnum=json.loads(request.POST.get('diz'))
                misconc=request.POST.get('misconc')
                dizcamb=json.loads(request.POST.get('dizcambiati'))
                request.session['dictaliqderivate']=dictnum
                request.session['unitaconcderivati']=misconc
                request.session['dizionarioderivaticambiati']=dizcamb
                print 'dictnum',dictnum
                print 'dizcamb',dizcamb
                return HttpResponse()
            #entra qui se l'utente ha cliccato su confirm all
            if 'conf' in request.POST or 'finish' in request.POST:
                name=request.user.username
                featrobot=FeatureDerivation.objects.get(name='Robot')
                lisderprot=FeatureDerProtocol.objects.filter(idFeatureDerivation=featrobot).values_list('idDerProtocol',flat=True)
                lista_aliqdersched=AliquotDerivationSchedule.objects.filter(Q(derivationExecuted=0)&Q(Q(operator=name)|Q(operator=''))&~Q(idDerivationProtocol=None)&~Q(idDerivationProtocol__in=lisderprot)&~Q(initialDate=None)&Q(measurementExecuted=1)&Q(deleteTimestamp=None)).order_by('validationTimestamp','initialDate','id')
                print 'lista',lista_aliqdersched
                #e' l'indice per numerare le serie di aliq derivate eseguite
                print 'ind_gen',indice_gen
                
                if request.session.has_key('dizinfoaliqderivare'):
                    dizinfo=request.session.get('dizinfoaliqderivare')
                else:
                    strgen=''
                    for qual in lista_aliqdersched:
                        strgen+=qual.idAliquot.uniqueGenealogyID+'&'
                    
                    lgenfin=strgen[:-1]
                    dizinfo=AllAliquotsContainer(lgenfin)
                    request.session['dizinfoaliqderivare']=dizinfo
                ind=0
                contatore=0
                listaaliqstorage=[]
                listatipialiq=[]
                lisbarclashub=[]
                #prendo il numero di aliquote derivate che ho creato
                num_aliq=request.POST.get('aliquots')
                gen=request.POST.get('gen')
                
                data_exec=request.POST.get('date_exec')
                datt=data_exec.split('-')
                data_esecuz=datetime.date(int(datt[0]),int(datt[1]),int(datt[2]))
                
                listaaliq=Aliquot.objects.filter(uniqueGenealogyID=gen,availability=1)
                #prendo l'aliquota madre
                if listaaliq.count()!=0:
                    aliq=listaaliq[0]

                #per trovare il tipo di derivato che ottengo
                pro=DerivationProtocol.objects.get(id=lista_aliqdersched[ind].idDerivationProtocol.id)
                t=TransformationDerivation.objects.filter(idDerivationProtocol=pro)
                tipo=t[0].idTransformationChange.idToType.abbreviation
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
                print 'genealogy   id',gen
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
                
                #prendo il derivation schedule
                alder=lista_aliqdersched[ind]                                
                
                #diminuisco la capacita' del kit usato
                idkit=lista_aliqdersched[ind].idKit
                if idkit!=None:
                    kit=Kit.objects.get(id=idkit.id)
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
                        ris=float(valore[0].value)-float(lista_aliqdersched[ind].loadQuantity)
                        print 'ris',ris
                        if ris<0:
                            ris=0.0
                        valore[0].value=float(ris)
                        valore[0].save()              
                
                tumore=ge.getOrigin()
                print 'tumore',tumore
                #caso=gen[3:7]
                caso=ge.getCaseCode()
                print 'caso',caso
                tipotum=CollectionType.objects.get(abbreviation=tumore)
                #prendo la collezione da associare al sampling event
                colle=Collection.objects.get(Q(itemCode=caso)&Q(idCollectionType=tipotum))
                print 'colle',colle
                #salvo la serie
                ser,creato=Serie.objects.get_or_create(operator=request.user.username,
                                                       serieDate=data_esecuz)
                #prendo la sorgente dalla tabella source
                sorg=Source.objects.get(id=colle.idSource.id)
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
                                         idAliqDerivationSchedule=lista_aliqdersched[ind],
                                         derivationDate=data_esecuz,
                                         operator=name)
                derev.save()
                print 'der',derev 
                
                request.session['data_derivazione']=data_esecuz
                request.session['operatore_derivazione']=name
                    
                derived_tipo=AliquotType.objects.get(abbreviation=tipo)
                
                unitamisconc=request.session.get('unitaconcderivati')
                print 'unita conc',unitamisconc
                #prendo la feature del volume
                featvol=Feature.objects.get(idAliquotType=derived_tipo,name='Volume')
                #prendo la feature della concentrazione
                featconc=None
                lfeatconc=Feature.objects.filter(idAliquotType=derived_tipo,name='Concentration',measureUnit=unitamisconc)
                if len(lfeatconc)!=0:
                    featconc=lfeatconc[0]
                print 'num',num_aliq
                piastra=-1
                data=""
                for i in range(0,int(num_aliq)):
                    #preparo i nomi con cui accedere alla request.post
                    vol='volume_'+str(i)
                    conc='conc_'+str(i)
                    v=request.POST.get(vol)
                    c=request.POST.get(conc)
                    print 'c',c
                    if c=='NaN' or c==0.0:
                        c=-1
                    vo=float(v)
                    co=float(c)
                    
                    #solo se il volume e' diverso da zero creo l'aliquota derivata
                    if vo!=0.0:
                        barcode=None
                        contatore=contatore+1
                        if contatore<10:
                            num_ordine='0'+str(contatore)
                        else:
                            num_ordine=str(contatore)
                        
                        if aliq.derived==0:
                            if derived_tipo.type!='Derived':
                                #nel caso di creazione di plasma o di PBMC
                                diz_dati={'archiveMaterial2':der,'aliqExtraction2':num_ordine,'2derivationGen':'00'}
                            else:
                                diz_dati={'archiveMaterial1':der,'aliqExtraction1':num_ordine,'2derivation':'0','2derivationGen':'00'}  
                            ge.updateGenID(diz_dati)
                            nuovo_gen=ge.getGenID()
                            #nuovo_gen=gen[0:19]+der+num_ordine+'000'    
                        elif aliq.derived==1:
                            diz_dati={'2derivation':der,'2derivationGen':num_ordine}  
                            ge.updateGenID(diz_dati)
                            nuovo_gen=ge.getGenID()
                            #nuovo_gen=gen[0:22]+der+num_ordine
                        
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
                                #print 'data',data
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
                        lfeatorigconc=Feature.objects.filter(idAliquotType=derived_tipo,name='OriginalConcentration',measureUnit=unitamisconc)
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
                          
                        #stringa per visualizzare poi la tabella riepilogativa finale
                        #diz[1] e' la piastra, diz[0] e' la posizione
                        stringa=nuovo_gen+'&'+barcode+'&'+piastra+'&'+posizi+'&'+str(co)+'&'+str(vo)
                        lista_val_aliq_der.append(stringa)
                        valori=nuovo_gen+','+str(piastra)+',,,'+barcode+','+derived_tipo.abbreviation+','+ffpe+',,,,,,'+str(data_esecuz)
                        listaaliqstorage.append(valori)
                        request.session['listaValAliqDer']=lista_val_aliq_der
                
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
    
                request.session['lista_aliquote_der']=lista_al_der    

                #salvo che la derivazione e' stata eseguita
                alder.derivationExecuted=1
                if alder.operator=='':
                    alder.operator=name
                alder.save()
                #se la madre e' esaurita
                if alder.aliquotExhausted==1:
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
                #request.session['aliqsvuotare']=aliq_da_svuotare
                #quando salvo mi viene tolto in automatico dalla lista delle aliq
                #da derivare quella che ho salvato adesso, quindi l'indice e' 
                #sempre 0
                print 'alder',alder
                print 'lista',lista_aliqdersched                
                #transaction.commit()                
                print 'ind',ind
                #se ho ancora campioni da derivare e non ho cliccato su 'Finish'
                if len(lista_aliqdersched)!=0 and 'finish' not in request.POST:                    
                    #vedo se devo aggiungere delle piastre
                    numpianuove=request.POST.get('numnuovepiastre')
                    print 'num',numpianuove
                    #preparo i nomi con cui accedere alla post
                    cod='piastra_'
                    piastipo='tipopiastra_'
                    for i in range(0,int(numpianuove)):
                        codpiastra=cod+str(i)
                        piastratipo=piastipo+str(i)
                        codpias=request.POST.get(codpiastra)
                        piastratip=request.POST.get(piastratipo).replace('%20',' ')
                        print 'c',codpias
                        print 'p',piastratip
                        valore=codpias+' '+piastratip
                        print 'valore',valore
                        if valore not in listapias:
                            listapias.append(valore)
                    print 'listapias',listapias
                    request.session['listapiastrealiqderivate']=listapias
                    #per trovare il tipo di derivato che ottengo
                    pro=DerivationProtocol.objects.get(id=lista_aliqdersched[ind].idDerivationProtocol.id)
                    t=TransformationDerivation.objects.filter(idDerivationProtocol=pro)
                    tipo=t[0].idTransformationChange.idToType.abbreviation
                    tipoesteso=t[0].idTransformationChange.idToType.longName.replace(' ','%20')
                    print 'tipo',tipo
                    
                    #apro il file con dentro i parametri per la derivazione
                    percorso=os.path.join(os.path.dirname(__file__),'tissue_media/File_Format/Regole_aliq_derivate.txt')
                    print 'perc',percorso
                    f=open(percorso)
                    lines = f.readlines()
                    f.close()
                    riga=''
                    
                    #prendo il protocollo di derivazione
                    numal=FeatureDerivation.objects.get(name='number_Aliquot')
                    volal=FeatureDerivation.objects.get(name='volume_Aliquot')
                    concal=FeatureDerivation.objects.get(name='concentration_Aliquot')
                    featnumal=FeatureDerProtocol.objects.get(idDerProtocol=pro,idFeatureDerivation=numal)
                    num_aliq=int(featnumal.value)
                    featvolal=FeatureDerProtocol.objects.get(idDerProtocol=pro,idFeatureDerivation=volal)
                    vol=featvolal.value
                    featconcal=FeatureDerProtocol.objects.get(idDerProtocol=pro,idFeatureDerivation=concal)
                    concen=featconcal.value
                    riga+=tipo+';'+str(num_aliq)+';'+str(vol)+';'+str(concen)+';'
                    for line in lines:
                        valori=line.split(';')
                        #se ho trovato la riga giusta che inizia con il nome del derivato
                        if valori[0]==tipo:
                            riga+=valori[1]+';'+valori[2]+';'+valori[3].strip()
                            break
                    print 'riga',riga
                    lista=[]
                    #riempio la lista con il giusto numero di aliquote
                    for i in range (0,5):
                        lista.append(i+1)
                                       
                    argument_list=[]
                    a=Collection()
    
                    #prendo le concentrazioni esistenti
                    misu=Measure.objects.filter(Q(name='concentration'))
                    for m in misu:
                        argument_list.append( Q(**{'idMeasure': m} ))
                    #prendo il quality event
                    lisqualev=QualityEvent.objects.filter(idAliquotDerivationSchedule=lista_aliqdersched[ind].id).order_by('id')
                    voltot=lista_aliqdersched[ind].volumeOutcome
                    if len(lisqualev)==0:
                        #non ho salvato un qualev perche' non ho fatto misure, ad es per derivare dal sangue intero
                        conc=[]
                        volusato=0
                    else:
                        #prendo il qualev piu' recente
                        qualev=lisqualev[len(lisqualev)-1]
                        #prendo il valore della concentrazione
                        conc=MeasurementEvent.objects.filter(Q(idQualityEvent=qualev)&Q(reduce(operator.or_, argument_list)))
                        print 'conc',conc
                        #per il volume dell'aliq madre. Devo sottrarre il volume usato per le misure
                        volusato=qualev.quantityUsed
                        if volusato==None:
                            volusato=0                    
                    voleffettivo=voltot-volusato
                    
                    #per passare l'aliquota
                    print 'lista',lista_aliqdersched
                    al=lista_aliqdersched[ind].idAliquot
                    print 'al dopo',al
                    derprot=lista_aliqdersched[ind].idDerivationProtocol.name
                    derprot=derprot.replace(' ','%20');
                    lista_al_da_der=request.session.get('lista_al_der_sessione')
                    lista_al_da_der[indice_gen-1].derivationExecuted=1
                    request.session['lista_al_der_sessione']=lista_al_da_der
                    indice_gen+=1
                    request.session['indice']=indice_gen
                    print 'ind_gen',indice_gen
                    
                    valori=dizinfo[al.uniqueGenealogyID]
                    print 'valori',valori
                    val=valori[0].split('|')
                    print 'val',val
                    barc=val[1]
                    pos=val[2]
                    print 'barc',barc
                    print 'pos',pos
                    
                    lisaliquote=[]
                    lisbarc=[]
                    lispos=[]
                    for alder in lista_al_da_der:
                        valori=dizinfo[alder.idAliquot.uniqueGenealogyID]
                        val=valori[0].split('|')
                        barcode=val[1]
                        position=val[2]
                        lisaliquote.append(alder)
                        lisbarc.append(barcode)
                        lispos.append(position)
                    dizcambiati=request.session['dizionarioderivaticambiati']
                    
                    dizposauto={}
                    #prendo tutti i valori impostati dall'utente per quanto riguarda il posizionamento
                    for jj in range (0,2):
                        duefinale=''
                        if jj==1:
                            duefinale='2'
                        diztemp={}
                        if 'automatic_'+str(jj) in request.POST:
                            diztemp['automatic']='Yes'
                            pezz=request.POST.get('pospezzi'+duefinale)
                            diztemp['pospezzi']=str(pezz)
                            vertt=request.POST.get('vertoriz'+duefinale)
                            diztemp['vertoriz']=str(vertt)
                        else:
                            diztemp['automatic']='No'
                            diztemp['pospezzi']=''
                            diztemp['vertoriz']='vert'
                        if 'choose'+duefinale in request.POST:
                            cho=request.POST.get('choose'+duefinale)
                            diztemp['choose']=str(cho)
                        else:
                            diztemp['choose']='plate'
                        bbb=request.POST.get('barcode_r'+duefinale)
                        diztemp['barcode']=str(bbb)
                        dizposauto[jj]=diztemp
                    print 'dizposauto',dizposauto      
                    print 'dizcambiati',dizcambiati        
                    variables = RequestContext(request,{'aliquota':al,'a':a,'lista':lista,'barc':barc,'pos':pos,'volume':voleffettivo,'conc':conc,'derprot':derprot,'listapiastre':listapias,'riga':riga,'aliq_da_derivare':zip(lisaliquote,lisbarc,lispos),'indice':indice_gen,'tipoesteso':tipoesteso,'dizcamb':dizcambiati,'dizposauto':dizposauto})
                    return render_to_response('tissue2/derived/end_derived.html',variables)
                else:                      
                    #prendo la lista con tutte le aliq salvate dentro e le converto 
                    #per la visualizzazione in html
                    listaaliquote=request.session.get('listaValAliqDer')
                    lista,intest,dizcsv,inte,dizsupervisori,unitamis=LastPartDerivation(request,'n',listaaliquote)
                    
                    email = LASEmail (functionality=get_functionality(), wgString=get_WG_string())
                    msg=['Derivation procedure executed','','Assigned to:\t'+name,'','Aliquots:','N\tGenealogy ID\tBarcode\tPlate\tPosition\tVolume(uL)\tConcentration('+unitamis+')']                    
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
                        print 'err derivation last step:',e
                        pass
                    
                    '''#mando l'e-mail
                    print 'dizfin',dizsupervisori
                    if len(dizsupervisori)!=0:
                        for key,value in dizsupervisori.items():
                            file_data = render_to_string('tissue2/derived/report_derived_finish.html', {'listafin':value,'esec':name}, RequestContext(request))
                            
                            subject, from_email = 'Created derived aliquots', settings.EMAIL_HOST_USER
                            text_content = 'This is an important message.'
                            html_content = file_data
                            msg = EmailMultiAlternatives(subject, text_content, from_email, [key])
                            msg.attach_alternative(html_content, "text/html")
                            msg.send()'''
                        
                    
                    variables = RequestContext(request,{'fine':True,'lista_der':lista,'intest':intest})
                    return render_to_response('tissue2/derived/end_derived.html',variables)
        except Exception,e:
            print 'err derivation last step:',e
            transaction.rollback()
            variables = RequestContext(request, {'errore':True})
            return render_to_response('tissue2/index.html',variables)

#@user_passes_test(lambda u: u.has_perm('tissue.can_view_create_derivatives'),login_url='/tissue/error/')  
@permission_decorator('tissue.can_view_BBM_create_derivatives')         
def createPDFDerivedAl(request):
    if request.session.get('listaValAliqDer'):
        lista=[]
        listaaliquote=request.session.get('listaValAliqDer')
        lista,intest,l,inte,dizsupervisori,unitamis=LastPartDerivation(request,'s',listaaliquote)
        #aliquots = request.session.get('listaValAliqDer')
        print 'createpdfder'
        '''for i in range(0,len(aliquots)):
            s=aliquots[i].split('&')
            lista.append(ReportDerivationToHtml(i+1,s[0],s[1],s[2],s[3],s[4],'s'))
        response=PDFMaker(request, 'Derived_Aliquots.pdf', 'tissue2/derived/pdf_AliquotsDer.html', lista)
        return response'''

        data=request.session.get('data_derivazione')
        print 'data',data
        ddd=str(data).split('-')
        print 'dd',ddd[0]
        data_def=datetime.date(int(ddd[0]),int(ddd[1]),int(ddd[2]))
        operatore=request.session.get('operatore_derivazione')
        file_data = render_to_string('tissue2/derived/pdf_AliquotsDer.html', {'list_report': lista,'intest':intest,'data_der':data_def,'operatore':operatore}, RequestContext(request))
        myfile = cStringIO.StringIO()
        pisa.CreatePDF(file_data, myfile)
        myfile.seek(0)
        response =  HttpResponse(myfile, mimetype='application/pdf')
        response['Content-Disposition'] = 'attachment; filename=Derived_Aliquots.pdf'
        #response=PDFMaker(request, 'Collected_Aliquots.pdf', 'tissue2/pdf_report.html', lista)
        return response
    else:
        return HttpResponseRedirect(reverse('tissue.views.index'))

#@user_passes_test(lambda u: u.has_perm('tissue.can_view_create_derivatives'),login_url='/tissue/error/')
@permission_decorator('tissue.can_view_BBM_create_derivatives')
def createCSVDerivedAl(request):
    if request.session.get('listaValAliqDer'):
        #aliquots = request.session.get('listaValAliqDer') 
        response = HttpResponse(mimetype='text/csv')
        response['Content-Disposition'] = 'attachment; filename=Derived_Aliquots.csv'
        #writer = csv.writer(response,delimiter='\t')
        writer = csv.writer(response)
        listaaliquote=request.session.get('listaValAliqDer')
        lista,intest,listacsv,intestcsv,dizsupervisori,unitamis=LastPartDerivation(request,'n',listaaliquote)
        writer.writerow([intestcsv[0]])
        for i in range(0,len(listacsv)):
            #csvString=str(i+1)+";"+str(val[0])+";"+str(val[3])+";"+val[1]+";"+val[2]
            writer.writerow([listacsv[i]])
        return response 
        '''writer.writerow(["N","GenealogyID","Plate","Position","Concentration(ng/uL)","Volume(uL)"])
        for i in range(0,aliquots.__len__()):
            val=aliquots[i].split('&')
            conc=str(val[3]).replace('.',',')
            vol=str(val[4]).replace('.',',')
            csvString=str(i+1)+"\t"+str(val[0])+"\t"+str(val[1])+"\t"+val[2]+"\t"+conc+"\t"+vol
            csvString=csvString.replace('\"','')
            writer.writerow([csvString])
        return response '''
    else:
        return HttpResponseRedirect(reverse('tissue.views.index'))

#per salvare il nuovo volume delle aliq derivate (o da dividere) quando il vecchio
#volume e' sotto zero
@transaction.commit_on_success
@laslogin_required
@login_required
def DerivedAliquotsChangeVolume(request):
    try:
        print request.POST
        gen=request.POST.get('gen').strip()
        val=request.POST.get('valore').strip()
        al=Aliquot.objects.get(Q(uniqueGenealogyID=gen)&Q(availability=1))
        print 'al',al
        featvol=Feature.objects.get(Q(idAliquotType=al.idAliquotType.id)&Q(name='Volume'))
        aliqfeatvol=AliquotFeature.objects.get(Q(idAliquot=al)&Q(idFeature=featvol))
        print 'val',val
        if val!='null':
            aliqfeatvol.value=float(val)
            aliqfeatvol.save()
            print 'aliqfeat',aliqfeatvol
            #solo se e' un'aliquota derivata esterna e quindi non ho inserito il volume
            #all'inizio
            #prendo la feature del volume originale
            featorigvol=Feature.objects.get(Q(idAliquotType=al.idAliquotType.id)&Q(name='OriginalVolume'))
            aliqorigfeat=AliquotFeature.objects.get(Q(idAliquot=al)&Q(idFeature=featorigvol))
            if aliqorigfeat.value==-1:
                aliqorigfeat.value=float(val)
                aliqorigfeat.save()
                print 'aliqorigfeat',aliqorigfeat
        return HttpResponse()
    except Exception,e:
        print 'err',e
        transaction.rollback()
        errore=True
        variables = RequestContext(request, {'errore':errore})
        return render_to_response('tissue2/index.html',variables)

#riprogramma la derivazione di un'aliquota nel caso la derivazione precedente sia fallita
@transaction.commit_on_success
@laslogin_required
@login_required
#@user_passes_test(lambda u: u.has_perm('tissue.can_view_perform_QC_QA'),login_url=settings.BASE_URL+'/tissue/error/')
@permission_decorator('tissue.can_view_BBM_perform_QC_QA')
def DerivedAliquotsReschedule(request):
    try:
        print request.POST
        gen=request.POST.get('gen').strip()
        val=request.POST.get('valore').strip()
        al=Aliquot.objects.get(Q(uniqueGenealogyID=gen)&Q(availability=1))
        print 'al',al
        featvol=Feature.objects.get(Q(idAliquotType=al.idAliquotType.id)&Q(name='Volume'))
        aliqfeatvol=AliquotFeature.objects.get(Q(idAliquot=al)&Q(idFeature=featvol))
        print 'aliqfeat',aliqfeatvol
        aliqfeatvol.value=float(val)
        aliqfeatvol.save()
        
        #solo se e' un'aliquota derivata esterna e quindi non ho inserito il volume
        #all'inizio
        #prendo la feature del volume originale
        featorigvol=Feature.objects.get(Q(idAliquotType=al.idAliquotType.id)&Q(name='OriginalVolume'))
        aliqorigfeat=AliquotFeature.objects.get(Q(idAliquot=al)&Q(idFeature=featorigvol))
        if aliqorigfeat.value==-1:
            aliqorigfeat.value=float(val)
            aliqorigfeat.save()
            print 'aliqorigfeat',aliqorigfeat
        return HttpResponse()
    except:
        transaction.rollback()
        errore=True
        variables = RequestContext(request, {'errore':errore})
        return render_to_response('tissue2/index.html',variables)

#per accedere alla schermata per calcolare i valori delle aliq derivate senza salvare
#niente nel DB
@transaction.commit_on_success
@laslogin_required
@login_required
#@user_passes_test(lambda u: u.has_perm('tissue.can_view_calculate_aliquot_values'),login_url=settings.BASE_URL+'/tissue/error/')
@permission_decorator('tissue.can_view_BBM_calculate_aliquot_values')
def DerivedAliquotsCalculateValues(request):
    try:
        print request.POST
        derprot=DerivationProtocol.objects.all()
        lista=[1,2,3,4,5,6]
        variables = RequestContext(request, {'derprot':derprot,'lista':lista})   
        return render_to_response('tissue2/derived/calculate.html',variables)
    except:
        transaction.rollback()
        errore=True
        variables = RequestContext(request, {'errore':errore})
        return render_to_response('tissue2/index.html',variables)



