from __init__ import *
from catissue.tissue.utils import *

@transaction.commit_on_success
@laslogin_required
@login_required
@permission_decorator('tissue.can_view_BBM_plan_aliquots_to_slide')
def InsertSlideAliquots(request):
    #PARTE SHARING
    assignUsersList=[]
    addressUsersList=[]
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
            addressUsersList.append(addressUsersDict)  
    else:
        assignUsersDict={}
        assignUsersDict['wg']=''
        assignUsersDict['usersList']=list()
        for u in User.objects.filter(~Q(username='admin')&~Q(first_name='')&Q(is_active=1)).order_by('last_name'):
            assignUsersDict['usersList'].append(u)
        assignUsersList.append(assignUsersDict)
        addressUsersList.append(assignUsersDict)
        
    if request.session.has_key('prepvetrini'):
        da_dividere=request.session.get('prepvetrini')
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
                print 'lis da dividere',lisgen
                request.session['prepvetrini']=lisgen
                request.session['opervetrini']=operat
                request.session['noteslide']=note
                return HttpResponse()
            #ho cliccato sul tasto 'add file'
            if 'aggiungi_file' in request.POST:
                lisaliq=[]
                lisbarc=[]
                lispos=[]
                operat=request.session.get('opervetrini')
                note=request.session.get('noteslide').strip()
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
                    
                    #prendo tutti gli aliquot type da cui si puo' partire per creare delle fette (in genere FF e OF) 
                    ltrasf=TransformationSlide.objects.all()
                    listapartenza=[]
                    for tr in ltrasf:
                        listapartenza.append(tr.idTransformationChange.idFromType.abbreviation)
                    print 'lista partenza',listapartenza
                    
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
                                    alsplisched=AliquotSlideSchedule.objects.filter(idAliquot=al,executed=0,deleteTimestamp=None)
                                    print 'alqual',alsplisched
                                    if len(alsplisched)!=0:
                                        raise ErrorRevalue('Error: aliquot '+gen+' is already scheduled for this procedure')
                                    
                                    #devo vedere se l'aliq puo' essere pianificata per essere tagliata                
                                    if al.idAliquotType.abbreviation not in listapartenza:
                                        raise ErrorRevalue('Error: aliquot type of '+gen+' is incompatible with this procedure')
                                da_dividere.append(lista)
                                    
                    print 'slide',da_dividere
                    variables = RequestContext(request,{'rivalutare':zip(lisaliq,lisbarc,lispos),'form':form,'t':operat,'note':note,'assignUsersList':assignUsersList,'addressUsersList':addressUsersList})
                    return render_to_response('tissue2/slide/slide.html',variables)
            
            if 'conferma' in request.POST:
                print 'da dividere',da_dividere
                name=request.user.username
                note=request.session.get('noteslide').strip()
                lisaliq=[]
                lisbarc=[]
                lispos=[]
                
                esec=request.session.get('opervetrini')
                print 'esec',esec
                if esec!='':
                    esecutore=User.objects.get(id=esec)
                else:
                    esecutore=None
                print 'esecutore',esecutore
                pianificatore=User.objects.get(username=name)
                #salvo lo slidesched
                schedule=SlideSchedule(scheduleDate=date.today(),
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
                        rev_aliq=AliquotSlideSchedule(idAliquot=a,
                                                      idSlideSchedule=schedule,
                                                      operator=esecutore,
                                                      executed=0,
                                                      notes=note
                                                      )
                        rev_aliq.save()
                        listal.append(rev_aliq)
                        lisaliq.append(gen)
                        lisbarc.append(barc)
                        lispos.append(pos)
                        dizaliqgen[gen]=barc+'|'+pos
                request.session['listafinaleslidereport']=zip(lisaliq,lisbarc,lispos)
                if esecutore!=None:
                    print 'dizaliqgen',dizaliqgen
                    email = LASEmail (functionality=get_functionality(), wgString=get_WG_string())
                    msg=['You have been designated to prepare slides from the following aliquots:','','Assigner:\t'+name,'Description:\t'+note,'','Aliquots:','N\tGenealogy ID\tBarcode\tPosition']
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
                '''mailOperator = esecutore.email
                print 'mail',mailOperator
                if mailOperator!='' and name!=esecutore.username:
                    #mando l'e-mail all'esecutore per dirgli che deve preparare quei campioni
                    file_data = render_to_string('tissue2/slide/report_insert_slide.html', {'listafin':zip(lisaliq,lisbarc,lispos),'assigner':name,'note':note}, RequestContext(request))
                    
                    subject, from_email = 'Scheduled slides preparation', settings.EMAIL_HOST_USER
                    text_content = 'This is an important message.'
                    html_content = file_data
                    msg = EmailMultiAlternatives(subject, text_content, from_email, [mailOperator])
                    msg.attach_alternative(html_content, "text/html")
                    msg.send()'''
                
                
                urlfin=settings.DOMAIN_URL+settings.HOST_URL+'/slide/insert/final/'
                print 'urlfin',urlfin
                return HttpResponseRedirect(urlfin)
                
            
        except ErrorRevalue as e:
            print 'My exception occurred, value:', e.value
            variables = RequestContext(request, {'errore':e.value,'assignUsersList':assignUsersList,'addressUsersList':addressUsersList})
            return render_to_response('tissue2/slide/slide.html',variables)
        except Exception, e:
            print 'err',e
            transaction.rollback()
            variables = RequestContext(request, {'errore':True,'assignUsersList':assignUsersList,'addressUsersList':addressUsersList})
            return render_to_response('tissue2/index.html',variables)
        
    variables = RequestContext(request, {'rivalutare':da_dividere,'form':form,'assignUsersList':assignUsersList,'addressUsersList':addressUsersList})
    return render_to_response('tissue2/slide/slide.html',variables)

#per far vedere il report finale dell'inserimento delle fettine
@transaction.commit_on_success
@laslogin_required
@login_required
@permission_decorator('tissue.can_view_BBM_plan_aliquots_to_slide')
def InsertSlideAliquotsFinal(request):
    liste=request.session.get('listafinaleslidereport')
    variables = RequestContext(request,{'fine':True,'rivalutare':liste})
    return render_to_response('tissue2/slide/slide.html',variables)

#per far comparire la prima pagina delle aliquote da dividere in cui l'utente sceglie,
#fra quelle assegnate a lui, quelle da fare oggi
@laslogin_required
@login_required
@permission_decorator('tissue.can_view_BBM_execute_slide_aliquots')
def ChooseSlideAliquots(request):
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
                laliq=[]
                lgen=''
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
                        lista1=AliquotSlideSchedule.objects.filter(idAliquot=aliq,executed=0,operator=operatore,deleteTimestamp=None)
                        lista2=AliquotSlideSchedule.objects.filter(idAliquot=aliq,executed=0,operator=None,deleteTimestamp=None)
                        listaaldersched=list(chain(lista1,lista2))
                        print 'listaslidesched',listaaldersched
                        if len(listaaldersched)!=0:
                            lgen+=gen+'&'
                            aldersched=listaaldersched[0]
                            print 'slide',aldersched
                            #cancello la pianificazione
                            #aldersched.deleteTimestamp= datetime.datetime.now()
                            aldersched.deleteTimestamp=timezone.localtime(timezone.now())
                            aldersched.deleteOperator=operatore
                            aldersched.save()
                            lista_canc.append(aldersched)
                            laliq.append(gen)
                            
                lgenfin=lgen[:-1]
                diz=AllAliquotsContainer(lgenfin)
                 
                print 'listaaliq',lista_canc
                
                email = LASEmail (functionality=get_functionality(), wgString=get_WG_string())
                msg=['Slides preparation deleted','','Assigned to:\t'+name,'','Aliquots:','N\tGenealogy ID\tBarcode\tPosition\tAssignment date']
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
                                email.addMsg([wg.name],[str(i)+'\t'+al.uniqueGenealogyID+'\t'+barc+'\t'+pos+'\t'+str(alder.idSlideSchedule.scheduleDate)])
                                i=i+1                                
                                if alder.idSlideSchedule.operator.username not in lisplanner:
                                    lisplanner.append(alder.idSlideSchedule.operator.username)
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
                    data=alder.idSlideSchedule.scheduleDate
                    valori=diz[alder.idAliquot.uniqueGenealogyID]
                    val=valori[0].split('|')
                    barc=val[1]
                    pos=val[2]
                    lista.append(ReportToHtml([i+1,alder.idAliquot.uniqueGenealogyID,barc,pos,alder.idSlideSchedule.operator,data]))
                    
                    '''#creo un dizionario con dentro come chiave il nome del supervisore e come valore una lista con le procedure che lo
                    #riguardano
                    if assegnatario.email !='' and assegnatario.username!=name:
                        diztemp={}
                        diztemp['gen']=alder.idAliquot.uniqueGenealogyID
                        diztemp['barc']=barc
                        diztemp['pos']=pos
                        diztemp['dat']=data
                        if dizsupervisori.has_key(assegnatario.email):
                            listatemp=dizsupervisori[assegnatario.email]
                        else:
                            listatemp=[]
                        listatemp.append(diztemp)
                        dizsupervisori[assegnatario.email]=listatemp
                   
                    
                print 'lista',lista
                print 'dizfin',dizsupervisori
                if len(dizsupervisori)!=0:
                    for key,value in dizsupervisori.items():
                        file_data = render_to_string('tissue2/slide/report_slide_canc.html', {'listafin':value,'esec':name}, RequestContext(request))
                        
                        subject, from_email = 'Cancel slides preparation', settings.EMAIL_HOST_USER
                        text_content = 'This is an important message.'
                        html_content = file_data
                        msg = EmailMultiAlternatives(subject, text_content, from_email, [key])
                        msg.attach_alternative(html_content, "text/html")
                        msg.send()'''
                
                variables = RequestContext(request,{'fine':True,'lista_der':lista})
                return render_to_response('tissue2/slide/choose.html',variables) 
            #prendo il protocollo
            pro=request.POST.get('prot')
            protoc=SlideProtocol.objects.get(id=pro)
            print 'pr',protoc
            for i in range(0,int(num)):
                #preparo la stringa per accedere alla post
                sel='sele_'+str(i)
                print 'sel',sel
                if sel in request.POST:
                    ge='gen_'+str(i)
                    gen=request.POST.get(ge)
                    print 'gen',gen
                    #adesso ho il genealogy id e prendo la relativa aliquota
                    aliq=Aliquot.objects.get(uniqueGenealogyID=gen,availability=1)
                    print 'aliq',aliq
                    lista1=AliquotSlideSchedule.objects.filter(idAliquot=aliq,executed=0,operator=operatore,deleteTimestamp=None)
                    lista2=AliquotSlideSchedule.objects.filter(idAliquot=aliq,executed=0,operator=None,deleteTimestamp=None)
                    listaaldersched=list(chain(lista1,lista2))
                    print 'listaslidesched',listaaldersched
                    if len(listaaldersched)!=0:
                        aldersched=listaaldersched[0]
                        print 'slide',aldersched
                        aldersched.idSlideProtocol=protoc                    
                        aldersched.save()
                        lista_aliq.append(aldersched)           
            
            request.session['listaaliqvetrini']=lista_aliq
            print 'listaaliq',lista_aliq     
            variables = RequestContext(request,{'lista':lista_aliq})
            return render_to_response('tissue2/slide/execute.html',variables)               
        else:    
            print 'name',name
            operat=User.objects.get(username=name)
            lista1=AliquotSlideSchedule.objects.filter(executed=0,operator=operat,deleteTimestamp=None)
            lista2=AliquotSlideSchedule.objects.filter(executed=0,operator=None,deleteTimestamp=None)
            lista=list(chain(lista1,lista2))
            print 'lista aliq slide',lista
            stringat=''
            for alder in lista:
                stringat+=alder.idAliquot.uniqueGenealogyID+'&'
            stringtotale=stringat[:-1]
            diz=AllAliquotsContainer(stringtotale)
            lisaliq=[]
            lisbarc=[]
            lispos=[]
            listaprot=[]
            for al in lista:
                listatemp=diz[al.idAliquot.uniqueGenealogyID]
                for val in listatemp:
                    ch=val.split('|')
                    lisaliq.append(al)
                    lisbarc.append(ch[1])
                    lispos.append(ch[2])
            
            listatrasf=[]
            lisder=[]
            for l in lista:
                listatrasf.append( Q(**{'idFromType': l.idAliquot.idAliquotType.id} ))
                #prendo i trasfChange che hanno come tipo iniziale i tipi delle alquote
                #pianificate per essere affettate
                if len(listatrasf)!=0:
                    listr=TransformationChange.objects.filter(Q(reduce(operator.or_, listatrasf)))
                    if len(listr)!=0:
                        for lis in listr:
                            lisder.append( Q(**{'idTransformationChange': lis.id} ))
                        if len(lisder)!=0:
                            listatrasfslide=TransformationSlide.objects.filter(Q(reduce(operator.or_, lisder)))
                            print 'li',listatrasfslide
                            #prendo i protocolli
                            if len(listatrasfslide)!=0:
                                del lisder[:]
                                for l in listatrasfslide:
                                    lisder.append( Q(**{'id': l.idSlideProtocol.id} ))
                                    if len(lisder)!=0:
                                        listaprot=SlideProtocol.objects.filter(Q(reduce(operator.or_, lisder)))            
            print 'lista',listaprot
            print 'l',lista
            
            variables = RequestContext(request,{'lista':listaprot,'listaliq':zip(lisaliq,lisbarc,lispos)})
            return render_to_response('tissue2/slide/choose.html',variables) 
    except Exception,e:
        print 'err',e
        variables = RequestContext(request,{'errore':True})
        return render_to_response('tissue2/index.html',variables)
    
#per gestire la schermata di convalida dei campioni
@laslogin_required
@login_required
@permission_decorator('tissue.can_view_BBM_execute_slide_aliquots')
def ExecEffectiveSlideAliquots(request):
    try:
        if request.method=='POST':
            name=request.user.username
            operatore=User.objects.get(username=name)
            print request.POST
            if 'salva' in request.POST:
                listagen=json.loads(request.POST.get('lgen'))
                print 'listagen',listagen
                request.session['listaaliquotevetrini']=listagen
                return HttpResponse()
            if 'conferma' in request.POST:
                lisfin=[]
                listagen=request.session.get('listaaliquotevetrini')
                lisaliq=Aliquot.objects.filter(uniqueGenealogyID__in=listagen,availability=1)
                print 'lisaliq',lisaliq
                lis1=AliquotSlideSchedule.objects.filter(Q(idAliquot__in=lisaliq)&Q(executed=0)&Q(operator=operatore)&~Q(idSlideProtocol=None)&Q(deleteTimestamp=None))
                lis2=AliquotSlideSchedule.objects.filter(Q(idAliquot__in=lisaliq)&Q(executed=0)&Q(operator=None)&~Q(idSlideProtocol=None)&Q(deleteTimestamp=None))
                lisqual=list(chain(lis1,lis2))
                lgen=[]
                strgen=''
                for qual in lisqual:
                    lgen.append(qual.idAliquot.uniqueGenealogyID)
                    strgen+=qual.idAliquot.uniqueGenealogyID+'&'
                    print 'aliquota_slide',qual.idAliquot
                #devo ordinare la lista degli aliquot der sched in base a come sono state convalidate le aliquote
                for gen in listagen:
                    for qual in lisqual:
                        if qual.idAliquot.uniqueGenealogyID==gen:
                            lisfin.append(qual)
                
                request.session['aliquotevetrini']=lisfin
                
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
                
                aliq=lisfin[0].idAliquot                
                lgenfin=strgen[:-1]
                diz=AllAliquotsContainer(lgenfin)
                request.session['dizinfoaliqvetrini']=diz
                request.session['indice_vetrini']=0
                request.session['listapiastrevetrini']=[]
                request.session['dictaliqvetrini']={}
                
                valori=diz[aliq.uniqueGenealogyID]
                val=valori[0].split('|')
                barc=val[1]
                pos=val[2]
                print 'barc',barc
                print 'pos',pos
                
                lisbarc=[]
                lispos=[]                
                
                for alqual in lisfin:
                    valori=diz[alqual.idAliquot.uniqueGenealogyID]
                    val=valori[0].split('|')
                    barcode=val[1]
                    position=val[2]
                    lisbarc.append(barcode)
                    lispos.append(position)
                
                prot=lisfin[0].idSlideProtocol
                #devo prendere le feature del protocollo
                featgeom=FeatureDerivation.objects.get(name='Geometry')
                featspess=FeatureDerivation.objects.get(name='Thickness')
                feattipo=FeatureDerivation.objects.get(name='SlideType')
                geometria=FeatureSlideProtocol.objects.get(idSlideProtocol=prot,idFeatureDerivation=featgeom).value
                spess=FeatureSlideProtocol.objects.get(idSlideProtocol=prot,idFeatureDerivation=featspess)
                tipovetr=FeatureSlideProtocol.objects.get(idSlideProtocol=prot,idFeatureDerivation=feattipo).value.replace(' ','%20')
                print 'geometria',geometria
                gg=geometria.split('x')
                geom=str(int(gg[0])*int(gg[1]))
                
                trasfslide=TransformationSlide.objects.filter(idSlideProtocol=prot)
                #il tipo di aliq che ottengo dalla trasformazione
                tiporis=trasfslide[0].idTransformationChange.idToType.abbreviation
                print 'tiporis',tiporis
                   
                variables = RequestContext(request,{'geom':geom,'spess':spess,'tipovetr':tipovetr,'lista_divid':zip(lisfin,lisbarc,lispos),'aliquota':aliq,'barcode':barc,'position':pos,'tipo':tiporis,'indice':1,'pezziblocco':0})
                return render_to_response('tissue2/slide/end_slide.html',variables)
    except Exception,e:
        print 'err',e
        variables = RequestContext(request, {'errore':True})
        return render_to_response('tissue2/index.html',variables)

#viene chiamata per ogni aliquota presente nella lista delle aliquote da dividere
@transaction.commit_on_success
@laslogin_required
@login_required
@permission_decorator('tissue.can_view_BBM_execute_slide_aliquots')
def LastPartSlideAliquots(request):
    lista_al_divi=[]
    if request.session.has_key('aliquotevetrini'):
        aliq_da_dividere=request.session.get('aliquotevetrini')
    if request.session.has_key('indice_vetrini'):
        ind=request.session.get('indice_vetrini')
    if request.session.has_key('lista_aliquote_vetrini'):
        lista_al_divi=request.session.get('lista_aliquote_vetrini') 
    if request.session.has_key('listaValAliqSlide'):
        lista_val_aliq_split=request.session.get('listaValAliqSlide') 
    else:
        lista_val_aliq_split=[]
    if request.session.has_key('dictaliqvetrini'):
        dictnum=request.session.get('dictaliqvetrini')
    if request.session.has_key('dizinfoaliqvetrini'):
        dizinfo=request.session.get('dizinfoaliqvetrini')
    else:
        strgen=''
        for qual in aliq_da_dividere:
            strgen+=qual.idAliquot.uniqueGenealogyID+'&'
        
        lgenfin=strgen[:-1]
        dizinfo=AllAliquotsContainer(lgenfin)
        request.session['dizinfoaliqvetrini']=dizinfo
    if request.method=='POST':
        print request.POST
        try:         
            #con javascript faccio una post che mi fa scattare questo if. Salvo i dati nella sessione
            #per poi riprenderli dopo quando clicco su confirm all
            if 'posizione' in request.POST:
                dictnum=json.loads(request.POST.get('diz'))
                request.session['dictaliqvetrini']=dictnum
                print 'dictnum slide',dictnum
                return HttpResponse()
            #entra qui se l'utente ha cliccato su confirm all
            if 'conf' in request.POST or 'finish' in request.POST:
                contatore=0
                listatipialiq=[]
                lisbarclashub=[]
                listaaliqstorage=[]
                feattipo=FeatureDerivation.objects.get(name='SlideType')
                
                gen=request.POST.get('gen')
                listaaliq=Aliquot.objects.filter(uniqueGenealogyID=gen,availability=1)
                #prendo l'aliquota madre
                if len(listaaliq)!=0:
                    aliq=listaaliq[0]
                
                #per trovare il tipo di aliq che ottengo (PS o OS)
                tipo=request.POST.get('protocollo')
                print 'tipo',tipo
                ge = GenealogyID(gen)
                fine='00'                
                #prendo l'inizio dell'aliquota che sto dividendo
                #e' un derivato quindi prendo tutti i caratteri fino alla fine dei 10 zeri
                #piu' i caratteri che indicano il tipo
                stringa=ge.getPartForDerAliq()+tipo
                #stringa=gen[0:21]
                print 'stringa',stringa
                #guardo se quell'inizio di genealogy ce l'ha gia' qualche aliquota
                disable_graph()
                lista_aliquote_derivate=Aliquot.objects.filter(uniqueGenealogyID__startswith=stringa,uniqueGenealogyID__endswith=fine).order_by('-uniqueGenealogyID')
                enable_graph()
                print 'lista_aliquote',lista_aliquote_derivate
                if len(lista_aliquote_derivate)!=0:
                    #prendo il primo oggetto che e' quello che ha il contatore piu' alto
                    maxgen=lista_aliquote_derivate[0].uniqueGenealogyID
                    print 'maxgen',maxgen
                    nuovoge=GenealogyID(maxgen)
                    maxcont=nuovoge.getAliquotExtraction()
                    print 'maxcont',maxcont
                    contatore=int(maxcont)              
                print 'contatore',contatore
                
                #salvo che la divisione e' stata eseguita
                alsplit=AliquotSlideSchedule.objects.get(idAliquot=aliq,executed=0,deleteTimestamp=None)
                alsplit.executed=1
                #il .save() avviene dopo
                print 'alslide',alsplit                        
                    
                tumore=ge.getOrigin()
                #tumore=gen[0:3]
                print 'tumore',tumore
                caso=ge.getCaseCode()
                #caso=gen[3:7]
                print 'caso',caso
                tipotum=CollectionType.objects.get(abbreviation=tumore)
                #prendo la collezione da associare al sampling event
                colle=Collection.objects.get(itemCode=caso,idCollectionType=tipotum)
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
                alsplit.executionDate=datetime.date.today()
                if alsplit.operator==None:
                    alsplit.operator=request.user
                alsplit.save()
                
                name=request.user.username
                request.session['data_slide']=date.today()
                request.session['operatore_slide']=name
                
                slide_tipo=AliquotType.objects.get(abbreviation=tipo)
                featspess=Feature.objects.get(Q(idAliquotType=slide_tipo)&Q(name='Thickness'))
                tipo_slide=AliquotType.objects.get(abbreviation=tipo)

                piastra=-1
                data=""
                for dizionario in dictnum:
                    contatore=contatore+1
                    num_ordine=str(contatore).zfill(2)
                    print 'num ordine',num_ordine
                    
                    diz_dati={'archiveMaterial2':tipo,'aliqExtraction2':num_ordine,'2derivation':'0','2derivationGen':'00'}
                    ge.updateGenID(diz_dati)
                    nuovo_gen=ge.getGenID()
                    print 'nuovo gen',nuovo_gen   
                        
                    #in diz[0] ho la posizione, in diz[1] ho il vetrino e in diz[2] lo spessore
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
                            res =  u.read()
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
                    posizi=diz[0]
                    if not 'children' in data:
                        #vuol dire che sto salvando un nuovo vetrino e quindi il barcode 
                        #risulta essere cio' che e' salvato nella variabile piastra
                        if piastra not in lisbarclashub:
                            lisbarclashub.append(piastra)

                    al_der=Aliquot(barcodeID=piastra+'|'+posizi,
                                  uniqueGenealogyID=nuovo_gen,
                                  idSamplingEvent=campionamento,
                                  idAliquotType=tipo_slide,
                                  availability=1,
                                  timesUsed=0,
                                  derived=0)
                    al_der.save()
                    
                    lista_al_divi.append(al_der)
                    listatipialiq.append(tipo_slide.abbreviation)                    
                    
                    #salvo lo spessore
                    spess=float(diz[2])
                    print 'spess',spess
                    aliqfeaturevol=AliquotFeature(idAliquot=al_der,
                                       idFeature=featspess,
                                       value=spess)
                    aliqfeaturevol.save()                                        
                    
                    valor=dizinfo[aliq.uniqueGenealogyID]
                    val=valor[0].split('|')
                    barcmadre=val[1]
                    posmadre=val[2]
                    print 'barc',barcmadre
                    print 'pos',posmadre
                    
                    prot=alsplit.idSlideProtocol
                    #e' il cont type del vetrino
                    tipovetr=FeatureSlideProtocol.objects.get(idSlideProtocol=prot,idFeatureDerivation=feattipo).value                    
                    print 'tipovetr',tipovetr
                    geome=diz[3]
                    #stringa per visualizzare poi la tabella riepilogativa finale
                    stringa=nuovo_gen+'&'+piastra+'&'+posizi+'&'+aliq.uniqueGenealogyID+'&'+barcmadre+'&'+posmadre
                    lista_val_aliq_split.append(stringa)
                    valori=nuovo_gen+','+piastra+','+tipo_slide.abbreviation+','+str(date.today())+','+tipovetr+','+geome+','+posizi
                    listaaliqstorage.append(valori)
                    request.session['listaValAliqSlide']=lista_val_aliq_split
                    
                #salvo le nuove aliquote nello storage
                url1 = Urls.objects.get(default = '1').url + "/api/save/slide/"
                val1={'lista':json.dumps(listaaliqstorage),'user':request.user.username}
                if len(listaaliq)!=0:
                    print 'url1',url1
                    data = urllib.urlencode(val1)
                    req = urllib2.Request(url1,data=data, headers={"workingGroups" : get_WG_string()})
                    u = urllib2.urlopen(req)
                    res1 =  json.loads(u.read())
                    print 'res1',res1
                    if res1['data']=='err':
                        raise Exception
                    
                if len(lisbarclashub)!=0:
                    indir=settings.DOMAIN_URL+settings.HOST_URL
                    url = indir + '/clientHUB/saveAndFinalize/'
                    print 'url',url
                    values2 = {'typeO' : 'container', 'listO': str(lisbarclashub)}
                    requests.post(url, data=values2, verify=False, headers={"workingGroups" : get_WG_string()})
    
                request.session['lista_aliquote_vetrini']=lista_al_divi    
                lista_al_da_div=request.session.get('aliquotevetrini')
                lista_al_da_div[ind].executed=1
                lista_al_da_div[ind].idSamplingEvent=campionamento
                request.session['aliquotevetrini']=lista_al_da_div
                
                ind=ind+1
                request.session['indice_vetrini']=ind
                
                #vedo se la madre e' finita
                if 'exhausted' in request.POST:
                    aliq.availability=0
                    aliq.save()
                    alsplit.aliquotExhausted=1
                    alsplit.save()
                    #mi collego allo storage per svuotare le provette contenenti le aliq
                    #esaurite
                    address=Urls.objects.get(default=1).url
                    url = address+"/full/"
                    print url
                    values = {'lista' : json.dumps([aliq.uniqueGenealogyID]), 'tube': 'empty','canc':True,'operator':name}
                    data = urllib.urlencode(values)
                    req = urllib2.Request(url,data=data, headers={"workingGroups" : get_WG_string()})
                    urllib2.urlopen(req)
                 
                if ind<len(aliq_da_dividere) and 'finish' not in request.POST:
                    #mi occupo delle piastre
                    #prendo le piastre caricate dall'utente
                    listapias=request.session.get('listapiastrevetrini')
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
                    request.session['listapiastrevetrini']=listapias

                    aliq=aliq_da_dividere[ind].idAliquot                                            
                        
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
                    
                    prot=aliq_da_dividere[ind].idSlideProtocol
                    #devo prendere le feature del protocollo
                    featgeom=FeatureDerivation.objects.get(name='Geometry')
                    featspess=FeatureDerivation.objects.get(name='Thickness')
                    
                    geometria=FeatureSlideProtocol.objects.get(idSlideProtocol=prot,idFeatureDerivation=featgeom).value
                    spess=FeatureSlideProtocol.objects.get(idSlideProtocol=prot,idFeatureDerivation=featspess)
                    tipovetr=FeatureSlideProtocol.objects.get(idSlideProtocol=prot,idFeatureDerivation=feattipo).value.replace(' ','%20')
                    print 'geometria',geometria
                    gg=geometria.split('x')
                    geom=str(int(gg[0])*int(gg[1]))
                    
                    trasfslide=TransformationSlide.objects.filter(idSlideProtocol=prot)
                    #il tipo di aliq che ottengo dalla trasformazione
                    tiporis=trasfslide[0].idTransformationChange.idToType.abbreviation
                    print 'tiporis',tiporis                                                                                        
                    print 'listapias',listapias
                    pezziblocco=request.POST.get('p_blocco')
                                        
                    variables = RequestContext(request,{'geom':geom,'spess':spess,'tipovetr':tipovetr,'aliquota':aliq,'barcode':barc,'position':pos,'tipo':tiporis,'listapiastre':listapias,'indice':(ind+1),'lista_divid':zip(lisaliquote,lisbarc,lispos),'pezziblocco':pezziblocco})
                    return render_to_response('tissue2/slide/end_slide.html',variables)
                else:                  
                    fine=True
                    lista=[]
                    #prendo la lista con tutte le aliq salvate dentro e le converto 
                    #per la visualizzazione in html
                    if request.session.has_key('listaValAliqSlide'):
                        lista_split=request.session.get('listaValAliqSlide')
                    else:
                        lista_split=[]
                    print 'listaaliq',lista_split
                    dizvalori={}
                    for i in range(0,len(lista_split)):
                        s=lista_split[i].split('&')
                        lista.append(ReportToHtml([i+1,s[0],s[1],s[2],s[3],s[4],s[5]]))
                        #dizionario con chiave il gen e valore barc|pos
                        dizvalori[s[0]]=s[1]+'|'+s[2]
                    print 'lista',lista
                    
                    lista_vetrini=request.session.get('lista_aliquote_vetrini')
                    email = LASEmail (functionality=get_functionality(), wgString=get_WG_string())
                    msg=['Slides preparation executed','','Assigned to:\t'+name,'','Aliquots:','N\tGenealogy ID\tBarcode\tPosition']                    
                    print 'lista_vetrini',lista_vetrini
                    lisgen=[]
                    dizmadri={}
                    #lista_vetrini ha dentro le aliq create
                    for al in lista_vetrini:
                        #devo risalire alle madri dei vetrini, perche' la divisione fra wg proprietari la faccio sulle madri
                        #e non sulle figlie che non esistono ancora nell'Aliquot_wg, visto che vengono create alla fine di tutto
                        alder=AliquotSlideSchedule.objects.get(idSamplingEvent=al.idSamplingEvent,operator=User.objects.get(username=name))
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
                        for aliqder in lista_vetrini:
                            for al in aliq:
                                #guardo nel dizionario delle madri se il loro rapporto e' corretto
                                madre=dizmadri[aliqder.uniqueGenealogyID]
                                print 'madre',madre
                                if madre==al.uniqueGenealogyID:
                                    lval=dizvalori[aliqder.uniqueGenealogyID]
                                    vv=lval.split('|')                                    
                                    email.addMsg([wg.name],[str(i)+'\t'+aliqder.uniqueGenealogyID+'\t'+vv[0]+'\t'+vv[1]])
                                    i=i+1
                                    alsched=AliquotSlideSchedule.objects.get(idSamplingEvent=aliqder.idSamplingEvent,operator=User.objects.get(username=name))
                                    if alsched.idSlideSchedule.operator.username not in lisplanner:
                                        lisplanner.append(alsched.idSlideSchedule.operator.username)
                        print 'lisplanner',lisplanner
                        #mando l'e-mail al pianificatore
                        email.addRoleEmail([wg.name], 'Planner', lisplanner)
                        email.addRoleEmail([wg.name], 'Executor', [request.user.username])
                    try:
                        email.send()
                    except Exception, e:
                        print 'err slide last step:',e
                        pass
                    
                    variables = RequestContext(request,{'fine':fine,'lista_der':lista})
                    return render_to_response('tissue2/slide/end_slide.html',variables)
        except Exception,e:
            print 'err',e
            transaction.rollback()
            variables = RequestContext(request, {'errore':True})
            return render_to_response('tissue2/index.html',variables)

