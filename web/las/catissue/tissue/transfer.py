from __init__ import *
from catissue.tissue.utils import *

#per inserire le richieste di trasferimento di aliquote
@transaction.commit_on_success
@laslogin_required
@login_required
#@user_passes_test(lambda u: u.has_perm('tissue.can_view_plan_transfer'),login_url=settings.BASE_URL+'/tissue/error/')
@permission_decorator('tissue.can_view_BBM_plan_transfer')
def InsertTransferAliquots(request):
    name=request.user.username
    
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

    if request.session.has_key('aliqTrasferire'):
        da_trasf=request.session.get('aliqTrasferire')
    else:
        da_trasf=[]  
    if request.method=='POST':
        print request.POST
        print request.FILES  
        try:      
            if 'salva' in request.POST:
                listaaliq=json.loads(request.POST.get('dati'))
                esec=request.POST.get('exec')
                dat=request.POST.get('dat')
                addr=request.POST.get('addr')
                lisgen=[]
                if len(listaaliq)!=0:
                    for val in listaaliq:
                        print 'val',val
                        listemp=[]
                        listemp.append(val)
                        if listemp not in lisgen:
                            lisgen.append(listemp)
                print 'lis da trasferire',lisgen
                request.session['aliqTrasferire']=lisgen
                request.session['exectransfer']=esec
                request.session['dattransfer']=dat
                request.session['addrtransfer']=addr
                return HttpResponse()   
            
            #ho cliccato sul tasto 'add file'
            if 'aggiungi_file' in request.POST:
                form=TransferForm1(request.POST,request.FILES)
                esec=request.session.get('exectransfer')
                dat=request.session.get('dattransfer')
                addr=request.session.get('addrtransfer')
                lisaliq=[]
                lisbarc=[]
                lispos=[]
                if 'file' in request.FILES:
                    print 'da_trasf',da_trasf
                    for lis in da_trasf:
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
                            raise ErrorRevalue('Error: aliquot '+gen+' doesn\'t exist in storage')
                        else:
                            lisgen=[]
                            if lista not in da_trasf:                                
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
                                for gg in lisgen:
                                    #per controllare se l'aliquota e' di questo wg
                                    lisali=Aliquot.objects.filter(uniqueGenealogyID=gg,availability=1)
                                    if len(lisali)==0:
                                        raise ErrorRevalue('Error: aliquot '+gen+' does not exist in storage')
                                    listaliq.append(lisali[0])
                                
                                for al in listaliq:
                                    print 'al',al
                                    #vedo se l'aliquota e' gia' stata programmata per il trasferimento
                                    listatrasf=Transfer.objects.filter(deliveryExecuted=0,deleteTimestamp=None,deleteOperator=None)
                                    altrasfsched=AliquotTransferSchedule.objects.filter(idAliquot=al,idTransfer__in=listatrasf)
                                    if(altrasfsched.count()!=0):
                                        raise ErrorRevalue('Error: aliquot '+gen+' is already scheduled for transferring')
                                da_trasf.append(lista)
                                    
                    print 'trasf',da_trasf
                    print 'lisaliq',lisaliq
                    variables = RequestContext(request,{'posizionare':zip(lisaliq,lisbarc,lispos),'exec':esec,'dat':dat,'addr':addr,'assignUsersList':assignUsersList,'addressUsersList':addressUsersList})
                    return render_to_response('tissue2/transfer/transfer.html',variables) 
            
            if 'final' in request.POST or 'next' in request.POST:
                lisaliq=[]
                lisbarc=[]
                lispos=[]
                dat=request.session.get('dattransfer').strip()
                if dat!='':
                    ddd=dat.split('-')
                    data_fin=datetime.date(int(ddd[0]),int(ddd[1]),int(ddd[2]))
                else:
                    data_fin=None
                    
                esec=request.session.get('exectransfer').strip()
                if esec!='':
                    esecutore=User.objects.get(id=esec)
                else:
                    esecutore=None
                    
                addr=request.session.get('addrtransfer').strip()
                address=User.objects.get(id=addr)
                
                operat=User.objects.get(username=name)
                print 'utente',esecutore
                print 'da trasf',da_trasf
                
                #salvo la transfschedule
                schedule=TransferSchedule(scheduleDate=date.today(),
                                          operator=operat)
                schedule.save()
                
                #creo l'oggetto Transfer
                trans=Transfer(idTransferSchedule=schedule,
                              operator=esecutore,
                              addressTo=address,
                              plannedDepartureDate=data_fin,
                              )
                trans.save()
                print 'trans',trans
                listal=[]
                #mi serve dopo per riempire il corpo del messaggio dell'e-mail
                dizaliqgen={}
                for lis in da_trasf:
                    for valori in lis:
                        val=valori.split('|')
                        gen=val[0]
                        barc=val[1]
                        pos=val[2]
                        a=Aliquot.objects.get(availability=1,uniqueGenealogyID=gen)

 
                        altrans=AliquotTransferSchedule(idAliquot=a,
                                                        idTransfer=trans)
                        altrans.save()
                        print 'aliqTrasferire',altrans
                        listal.append(altrans)
                        
                        lisaliq.append(gen)
                        lisbarc.append(barc)
                        lispos.append(pos)
                        dizaliqgen[gen]=barc+'|'+pos
                print 'dizaliqgen',dizaliqgen
                if 'final' in request.POST:
                    esecut=esecutore
                    diztemp={}
                    diztemp['liste']=zip(lisaliq,lisbarc,lispos)
                    diztemp['esec']=esecut
                    diztemp['data']=data_fin
                    diztemp['addr']=address
                    request.session['listafinaletransferreport']=diztemp
                    if esecut!=None:
                        email = LASEmail (functionality=get_functionality(), wgString=get_WG_string())
                        msg=['You have been designated to execute a transfer procedure','','Assigner:\t'+operat.username,'Shipment date:\t'+str(data_fin),'Address to:\t'+address.username,'','Aliquots to transfer:','N\tGenealogy ID\tBarcode\tPosition']
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
                            #devo mandare l'e-mail all'operatore incaricato di eseguire il trasferimento
                            email.addRoleEmail([wg.name], 'Assignee', [esecutore.username])
                            email.addRoleEmail([wg.name], 'Executor', [request.user.username])
                        try:
                            email.send()
                        except Exception, e:
                            print 'err',e
                            transaction.rollback()
                            variables = RequestContext(request, {'errore':True,'assignUsersList':assignUsersList,'addressUsersList':addressUsersList})
                            return render_to_response('tissue2/index.html',variables)
                            '''item=dict()
                            item['Executor']=[assigner.username]
                            item['Recipient']=[addre.username]
                            item['Assignee']=[esecutore.username]
                            lisaliqWG=aliq.values_list('uniqueGenealogyID',flat=True)
                            #mando l'e-mail all'esecutore per dirgli che deve trasferire quei campioni
                            item['msg'] = [render_to_string('tissue2/transfer/report_transfer.html', {'listafin':zip(lisaliqWG,lisbarc,lispos),'assigner':assigner,'data':data,'addr':addre}, RequestContext(request))]
                            mailDict[wg.name]=item
                        mailDict={'mailDict':json.dumps(mailDict),'functionality':get_functionality()}
                        data = urllib.urlencode(mailDict)
                        req = urllib2.Request(settings.DOMAIN_URL+'/las/sendLASMail/',data=data, headers={"workingGroups" : get_WG_string()})
                        u = urllib2.urlopen(req)
                        res1 =  u.read()
    
                        if res1=='errore':
                            raise Exception'''
                        
                        
                        #vecchio modo per le e-mail
                        '''if mailOperator!='' and assigner.username!=operator.username:
                            #mando l'e-mail all'esecutore per dirgli che deve trasferire quei campioni
                            file_data = render_to_string('tissue2/transfer/report_transfer.html', {'listafin':zip(lisaliq,lisbarc,lispos),'assigner':assigner,'data':data,'addr':addre}, RequestContext(request))
                            
                            subject, from_email = 'Scheduled transfer aliquots', settings.EMAIL_HOST_USER
                            text_content = 'This is an important message.'
                            html_content = file_data
                            msg = EmailMultiAlternatives(subject, text_content, from_email, [mailOperator])
                            msg.attach_alternative(html_content, "text/html")
                            msg.send()'''
                    else:
                        #altrimenti non riesce ad impostarmi i valori nella sessione
                        time.sleep(1)
                    
                    urlfin=settings.DOMAIN_URL+settings.HOST_URL+'/transfer/insert/final/'
                    print 'urlfin',urlfin
                    return HttpResponseRedirect(urlfin)
                                        
                if 'next' in request.POST:
                    print 'listal',listal
                    idtrasf=listal[0].idTransfer.id
                    #prendo la lista dei corrieri
                    liscorr=Courier.objects.all()
                    variables = RequestContext(request,{'listainiz':listal,'liscorr':liscorr,'idtrasf':idtrasf,'assignUsersList':assignUsersList,'addressUsersList':addressUsersList})
                    return render_to_response('tissue2/transfer/confirm_request.html',variables)
        except ErrorRevalue as e:
            print 'My exception occurred, value:', e.value
            variables = RequestContext(request, {'errore':e.value,'assignUsersList':assignUsersList,'addressUsersList':addressUsersList})
            return render_to_response('tissue2/transfer/transfer.html',variables)
        except Exception,e:
            print 'errore',e
            transaction.rollback()
            variables = RequestContext(request, {'errore':True,'assignUsersList':assignUsersList,'addressUsersList':addressUsersList})
            return render_to_response('tissue2/index.html',variables)
    #else:
    #    form = TransferForm1()
    variables = RequestContext(request, {'assignUsersList':assignUsersList,'addressUsersList':addressUsersList})
    return render_to_response('tissue2/transfer/transfer.html',variables)

#per far vedere il report finale dell'inserimento dei trasferimenti
@transaction.commit_on_success
@laslogin_required
@login_required
@permission_decorator('tissue.can_view_BBM_plan_transfer')
def InsertTransferAliquotsFinal(request):
    diztemp=request.session.get('listafinaletransferreport')
    variables = RequestContext(request,{'fine':True,'posizionare':diztemp['liste'],'esec':diztemp['esec'],'data':diztemp['data'],'addr':diztemp['addr']})
    return render_to_response('tissue2/transfer/transfer.html',variables)

#per far comparire le pianificazioni ancora da confermare con la lettura del codice delle provette
@transaction.commit_on_success
@laslogin_required
@login_required
#@user_passes_test(lambda u: u.has_perm('tissue.can_view_send_aliquots'),login_url=settings.BASE_URL+'/tissue/error/')
@permission_decorator('tissue.can_view_BBM_send_aliquots')
def PendingTransferAliquots(request):
    name=request.user.username
    operatore=User.objects.get(username=name)
    print request.POST
    try:    
        if 'final' in request.POST:
            idtrasf=request.session.get('idtrasferimento')
            trasf=Transfer.objects.get(id=idtrasf)
            print 'trasf',trasf
            #prendo le aliquote collegate a quel trasferimento
            lisaliq=AliquotTransferSchedule.objects.filter(idTransfer=trasf)
            print 'lisaliq',lisaliq
            #prendo la lista dei corrieri
            liscorr=Courier.objects.all()
            variables = RequestContext(request,{'listainiz':lisaliq,'liscorr':liscorr,'idtrasf':idtrasf})
            return render_to_response('tissue2/transfer/confirm_request.html',variables)
        if 'salva' in request.POST:
            idtrasf=request.POST.get('idtrasf')
            request.session['idtrasferimento']=idtrasf
            return HttpResponse()
        #cancello il trasferimento
        if 'canc' in request.POST:
            idtrasf=request.POST.get('idtrasf')
            trasf=Transfer.objects.get(id=idtrasf)
            #trasf.deleteTimestamp= datetime.datetime.now()
            trasf.deleteTimestamp=timezone.localtime(timezone.now())
            trasf.deleteOperator=operatore
            trasf.save()
            #mando l'e-mail al pianificatore per dirgli che quel trasferimento e' stato cancellato
            lisaliq=AliquotTransferSchedule.objects.filter(idTransfer=trasf)
            lgen=''
            laliq=[]
            for val in lisaliq:
                lgen+=val.idAliquot.uniqueGenealogyID+'&'
                laliq.append(val.idAliquot.uniqueGenealogyID)
            lgenfin=lgen[:-1]
            diz=AllAliquotsContainer(lgenfin)
            
            esec=trasf.operator
            data=trasf.plannedDepartureDate
            addr=trasf.addressTo
            assigner=trasf.idTransferSchedule.operator
            print 'assigner',assigner
            
            email = LASEmail (functionality=get_functionality(), wgString=get_WG_string())
            msg=['This transfer has been deleted','','Assigned to:\t'+esec.username,'Shipment date:\t'+str(data),'Address to:\t'+addr.username,'','Aliquots:','N\tGenealogy ID\tBarcode\tPosition\tAssignment date']
            aliquots=Aliquot.objects.filter(uniqueGenealogyID__in=laliq,availability=1)
            wgList=WG.objects.filter(id__in=Aliquot_WG.objects.filter(aliquot__in=aliquots).values_list('WG',flat=True).distinct())
            print 'wglist',wgList
            for wg in wgList:
                print 'wg',wg
                email.addMsg([wg.name], msg)
                aliq=aliquots.filter(id__in=Aliquot_WG.objects.filter(WG=wg).values_list('aliquot',flat=True).distinct())
                print 'aliq',aliq
                i=1
                #per mantenere l'ordine dei campioni anche nell'e-mail
                for aliqtr in lisaliq:
                    for al in aliq:   
                        if aliqtr.idAliquot.uniqueGenealogyID==al.uniqueGenealogyID:
                            lval=diz[al.uniqueGenealogyID]
                            val=lval[0].split('|')
                            barc=val[1]
                            pos=val[2]
                            email.addMsg([wg.name],[str(i)+'\t'+al.uniqueGenealogyID+'\t'+barc+'\t'+pos+'\t'+str(trasf.idTransferSchedule.scheduleDate)])
                            i=i+1
                #devo mandare l'e-mail al pianificatore del trasferimento
                email.addRoleEmail([wg.name], 'Planner', [assigner.username])
                email.addRoleEmail([wg.name], 'Executor', [request.user.username])
            try:
                email.send()
            except Exception, e:
                print 'errore',e
                transaction.rollback()
                variables = RequestContext(request, {'errore':True})
                return render_to_response('tissue2/index.html',variables)
            
            '''if mailOperator!='' and assigner.username!=operator.username:
                for trasf in lisaliq:
                    valori=diz[trasf.idAliquot.uniqueGenealogyID]
                    val=valori[0].split('|')
                    barc=val[1]
                    pos=val[2]
                    
                    diztemp={}
                    diztemp['gen']=trasf.idAliquot.uniqueGenealogyID
                    diztemp['barc']=barc
                    diztemp['pos']=pos
                    diztemp['dat']=trasf.idTransfer.idTransferSchedule.scheduleDate
                    if dizsupervisori.has_key(mailOperator):
                        listatemp=dizsupervisori[mailOperator]
                        listatemp.append(diztemp)
                    else:
                        listatemp=[]
                        listatemp.append(diztemp)
                    dizsupervisori[mailOperator]=listatemp
                print 'dizsupervisori',dizsupervisori
                
                for key,value in dizsupervisori.items():
                    file_data = render_to_string('tissue2/transfer/report_canc.html', {'listafin':value,'esec':esec,'data':data,'addr':addr}, RequestContext(request))                                
                    subject, from_email = 'Cancel transfer aliquots', settings.EMAIL_HOST_USER
                    text_content = 'This is an important message.'
                    html_content = file_data
                    msg = EmailMultiAlternatives(subject, text_content, from_email, [key])
                    msg.attach_alternative(html_content, "text/html")
                    msg.send()'''
            return HttpResponse()
        
        #per far comparire la lista dei trasferimenti ancora da fare
        #prendo tutte le richieste ancora da evadere assegnate a quell'utente o a nessuno
        lista1=Transfer.objects.filter(operator=operatore,deleteOperator=None,departureExecuted=0)
        lista2=Transfer.objects.filter(operator=None,deleteOperator=None,departureExecuted=0)        
        listafin = list(chain(lista1, lista2))
        print 'lista',listafin
        variables = RequestContext(request,{'trasferire':listafin})
        return render_to_response('tissue2/transfer/select_request.html',variables)
    except Exception,e:
        print 'errore',e
        transaction.rollback()
        variables = RequestContext(request, {'errore':True})
        return render_to_response('tissue2/index.html',variables)
    
#per salvare il fatto che i campioni sono stati spediti
@transaction.commit_on_success
@laslogin_required
@login_required
#@user_passes_test(lambda u: u.has_perm('tissue.can_view_send_aliquots'),login_url=settings.BASE_URL+'/tissue/error/')
@permission_decorator('tissue.can_view_BBM_send_aliquots')
def SendTransferAliquots(request):
    name=request.user.username
    operatore=User.objects.get(username=name)
    print request.POST
    try:    
        if 'salva' in request.POST:
            diz={}
            listagen=json.loads(request.POST.get('lgen'))
            print 'listagen',listagen
            #mi dice se trasferisco solo i campioni o anche la scatola collegata
            containertype=request.POST.get('containertype')
            print 'containertype',containertype
            listemp=[]
            if len(listagen)!=0:
                for val in listagen:
                    print 'val',val                    
                    listemp.append(val)
            print 'lis fin',listemp
            #devo vedere il tipo dell'aliq
            lisaliq=Aliquot.objects.filter(uniqueGenealogyID__in=listemp,availability=1)
            print 'lisaliq',lisaliq
            for gg in listemp:
                trovato=False
                for aliq in lisaliq:
                    if gg==aliq.uniqueGenealogyID:
                        diz[gg]=aliq.idAliquotType.abbreviation
                        trovato=True
                        break
                if not trovato:
                    diz[gg]=None
            print 'diz',diz
            url1 = Urls.objects.get(default = '1').url + "/api/canc/father/"
            val1={'dizgen':json.dumps(diz),'containermove':containertype}
            
            print 'url1',url1
            data = urllib.urlencode(val1)
            req = urllib2.Request(url1,data=data, headers={"workingGroups" : get_WG_string()})
            u = urllib2.urlopen(req)
            res1 =  u.read()
            if res1=='errore':
                raise Exception
            return HttpResponse()
        
        idtrasf=request.POST.get('idtransfer')
        transf=Transfer.objects.get(id=idtrasf)
        cor=request.POST.get('corr')
        convtutto=request.POST.get('convalidatutto')
        print 'convtutto',convtutto
        corriere=Courier.objects.get(id=cor)
        track=request.POST.get('number').strip()
        dat=request.POST.get('senddate').strip()
        ddd=dat.split('-')
        data_fin=datetime.date(int(ddd[0]),int(ddd[1]),int(ddd[2]))
        
        if convtutto=='true':
            #se ho selezionato il check per la convalida di tutti, allora vuol dire che non li ho convalidati uno a uno,
            #quindi il campo e' da mettere a Falso
            transf.departureValidated=False
        else:
            transf.departureValidated=True
        transf.departureDate=data_fin
        transf.departureExecuted=1
        transf.idCourier=corriere
        if track!='':
            transf.trackingNumber=track
        #salvo l'operatore che ha eseguito la spedizione, nel caso quel trasferimento non fosse stato assegnato a nessuno 
        transf.operator=operatore
        transf.save()
        listaliq=AliquotTransferSchedule.objects.filter(idTransfer=transf)
        request.session['listaaliqtrasferire']=listaliq
        #rendo indisponibili le provette per altri scopi
        print 'listaliq',listaliq
        lgen=[]
        strgen=''
        for aliqtr in listaliq:
            lgen.append(aliqtr.idAliquot.uniqueGenealogyID)
            strgen+=aliqtr.idAliquot.uniqueGenealogyID+'&'
        url1 = Urls.objects.get(default = '1').url + "/container/availability/"
        val1={'lista':json.dumps(lgen),'tube':'0','nome':'transfer'}
        
        print 'url1',url1
        data = urllib.urlencode(val1)
        req = urllib2.Request(url1,data=data, headers={"workingGroups" : get_WG_string()})
        u = urllib2.urlopen(req)
        #u = urllib2.urlopen(url1, data)
        res1 =  u.read()
        if res1=='err':
            raise Exception
        
        addr=listaliq[0].idTransfer.addressTo
        pianif=listaliq[0].idTransfer.idTransferSchedule.operator
            
        lgenfin=strgen[:-1]
        diction=AllAliquotsContainer(lgenfin)
        
        #la n indica che non faccio un pdf
        lista,intest,dizcsv,inte=LastPartTransfer(request,'n',diction,listaliq)
        #metto i dati nella sessione perche' mi servono poi per il PDF
        request.session['datatrasferimento']=data_fin
        request.session['destinatariotrasferimento']=addr
        request.session['corrieretrasferimento']=corriere
        request.session['tracktrasferimento']=track
        
        email = LASEmail (functionality=get_functionality(), wgString=get_WG_string())
        msg=['Samples transferring','','Sent to:\t'+addr.username,'Shipment date:\t'+str(data_fin),'Courier:\t'+corriere.name]
        if track!='':
            msg.append('Tracking N.:\t'+track)
        msg.append('')
        msg.append('These aliquots have been sent:')
        msg.append('N\tGenealogy ID\tBarcode\tPosition\tVolume(ul)\tPatient code\tCreation date')
        aliquots=Aliquot.objects.filter(uniqueGenealogyID__in=lgen,availability=1)
        wgList=WG.objects.filter(id__in=Aliquot_WG.objects.filter(aliquot__in=aliquots).values_list('WG',flat=True).distinct())
        print 'wglist',wgList
        for wg in wgList:
            print 'wg',wg
            email.addMsg([wg.name], msg)
            aliq=aliquots.filter(id__in=Aliquot_WG.objects.filter(WG=wg).values_list('aliquot',flat=True).distinct())
            print 'aliq',aliq
            i=1
            #per mantenere l'ordine dei campioni anche nell'e-mail
            for aliqtr in listaliq:
                for al in aliq:
                    if aliqtr.idAliquot.uniqueGenealogyID==al.uniqueGenealogyID:
                        stringatab=dizcsv[al.uniqueGenealogyID]
                        email.addMsg([wg.name],[str(i)+'\t'+stringatab])
                        i=i+1
            #mando l'e-mail al destinatario e al pianificatore
            email.addRoleEmail([wg.name], 'Recipient', [addr.username])
            email.addRoleEmail([wg.name], 'Planner', [pianif.username])
            email.addRoleEmail([wg.name], 'Executor', [request.user.username])
        try:
            email.send()
        except Exception, e:
            print 'errore',e
            transaction.rollback()
            variables = RequestContext(request, {'errore':True})
            return render_to_response('tissue2/index.html',variables)
        
        '''#mando l'e-mail al destinatario e al pianificatore
        file_data = render_to_string('tissue2/transfer/report_send_receive.html', {'aliq':lista,'intest':intest,'data':data_fin,'addr':addr,'corr':corriere,'track':track}, RequestContext(request))
        destinatario = User.objects.get(id = addr.id)
        pianificatore = User.objects.get(id = pianif.id)
        mailDest = destinatario.email
        mailPianif = pianificatore.email
        listaindir=[]
        if mailDest!='' and operatore.username!=destinatario.username:
            listaindir.append(mailDest)
        if mailPianif!='' and operatore.username!=pianificatore.username:
            listaindir.append(mailPianif)
        subject, from_email = 'Transferred aliquots', settings.EMAIL_HOST_USER
        text_content = 'This is an important message.'
        html_content = file_data
        if len(listaindir)!=0:
            msg = EmailMultiAlternatives(subject, text_content, from_email, listaindir)
            msg.attach_alternative(html_content, "text/html")
            msg.send()'''
       
        #aggiungere sharing qui
        genidToShare=set()
        for key in diction.keys():
            genidToShare.add(key)
        print 'genid da condividere',genidToShare
        url = Urls.objects.get(idWebService=WebService.objects.get(name='LASAuthServer')).url + "/shareEntities/"
        data={'entitiesList':json.dumps(list(genidToShare)),'user':addr.username}

        print 'urlLASAUTH',url
        data = urllib.urlencode(data)
        req = urllib2.Request(url,data=data, headers={"workingGroups" : get_WG_string()})
        u = urllib2.urlopen(req)
        res1 =  u.read()
        if res1=='error':
            print "error during sharing aliquots!"
            raise Exception

        variables = RequestContext(request,{'fine':True,'aliq':lista,'intest':intest,'data':data_fin,'addr':addr,'corr':corriere,'track':track})
        return render_to_response('tissue2/transfer/confirm_request.html',variables)
    except Exception,e:
        print 'errore',e
        transaction.rollback()
        variables = RequestContext(request, {'errore':True})
        return render_to_response('tissue2/index.html',variables)

#per far comparire i trasferimenti di cui bisogna ancora confermare la ricezione
@transaction.commit_on_success
@laslogin_required
@login_required
#@user_passes_test(lambda u: u.has_perm('tissue.can_view_receive_aliquots'),login_url=settings.BASE_URL+'/tissue/error/')
@permission_decorator('tissue.can_view_BBM_receive_aliquots')
def ReceiveTransferAliquots(request):
    name=request.user.username
    operatore=User.objects.get(username=name)
    print request.POST
    try:    
        if 'final' in request.POST:
            idtrasf=request.session.get('idtrasferimento')
            trasf=Transfer.objects.get(id=idtrasf)
            print 'trasf',trasf
            #prendo le aliquote collegate a quel trasferimento
            lisaliq=AliquotTransferSchedule.objects.filter(idTransfer=trasf)
            print 'lisaliq',lisaliq
            variables = RequestContext(request,{'listainiz':lisaliq,'idtrasf':idtrasf,'ricevuto':True})
            return render_to_response('tissue2/transfer/confirm_request.html',variables)
        if 'salva' in request.POST:
            idtrasf=request.POST.get('idtrasf')
            request.session['idtrasferimento']=idtrasf
            print 'ricevuto',idtrasf
            return HttpResponse()
        
        #per far comparire la lista dei trasferimenti ancora da ricevere
        #prendo tutte le richieste ancora da evadere assegnate a quell'utente
        lista1=Transfer.objects.filter(addressTo=operatore,deleteOperator=None,departureExecuted=1,deliveryExecuted=0)

        print 'lista',lista1
        variables = RequestContext(request,{'trasferire':lista1,'ricevuto':True})
        return render_to_response('tissue2/transfer/select_request.html',variables)
    except Exception,e:
        print 'errore',e
        transaction.rollback()
        variables = RequestContext(request, {'errore':True})
        return render_to_response('tissue2/index.html',variables)
    
#per salvare il fatto che i campioni sono stati ricevuti
@transaction.commit_on_success
@laslogin_required
@login_required
#@user_passes_test(lambda u: u.has_perm('tissue.can_view_receive_aliquots'),login_url=settings.BASE_URL+'/tissue/error/')
@permission_decorator('tissue.can_view_BBM_receive_aliquots')
def ReceiveFinalTransferAliquots(request):
    print request.POST
    try:    
        if 'salva' in request.POST:
            listagen=json.loads(request.POST.get('lgen'))
            print 'listagen',listagen
            listemp=[]
            if len(listagen)!=0:
                for val in listagen:
                    print 'val',val                    
                    listemp.append(val)
            #in listemp ho la lista dei gen convalidati
            print 'lis fin',listemp
            request.session['FinalReceiveValidatedAliquots']=listemp
            return HttpResponse()
            
        name=request.user.username
        idtrasf=request.POST.get('idtransfer')
        print 'idtransf',idtrasf
        transf=Transfer.objects.get(id=idtrasf)
        print 'transf',transf
        dat=request.POST.get('senddate').strip()
        ddd=dat.split('-')
        data_fin=datetime.date(int(ddd[0]),int(ddd[1]),int(ddd[2]))
        #e' la lista dei gen convalidati. Devo confrontarla con quella dei gen totali per avere quelli non convalidati.
        lisgen=request.session.get('FinalReceiveValidatedAliquots')
        
        transf.deliveryDate=data_fin
        transf.deliveryExecuted=1
        #per adesso metto sempre che il processo e' stato convalidato perche' la possibilita' di non convalidare si ha 
        #solo durante l'invio delle provette e non durante la ricezione
        transf.deliveryValidated=1
        
        transf.save()
        listaliq=AliquotTransferSchedule.objects.filter(idTransfer=transf)
        request.session['listaaliqtrasferire']=listaliq
        
        #rendo di nuovo disponibili i campioni per altri scopi visto che sono stati ricevuti
        lgen=[]
        strgen=''
        lgennonconvalidati=[]
        lconvalidati=[]
        diz2={}
        for aliqtr in listaliq:
            lgen.append(aliqtr.idAliquot.uniqueGenealogyID)
            strgen+=aliqtr.idAliquot.uniqueGenealogyID+'&'
            #se il gen non e' presente nella lisgen vuol dire che non e' stato convalidato e quindi
            #lo devo inserire nell'altra lista
            if aliqtr.idAliquot.uniqueGenealogyID not in lisgen:
                lgennonconvalidati.append(aliqtr)
                diz2[aliqtr.idAliquot.uniqueGenealogyID]=aliqtr.idAliquot.idAliquotType.abbreviation
            else:
                lconvalidati.append(aliqtr)
        print 'lconvalidati',lconvalidati
        print 'non convalidati',lgennonconvalidati
        url1 = Urls.objects.get(default = '1').url + "/container/availability/"
        val1={'lista':json.dumps(lgen),'tube':'1'}
        print 'url1',url1
        data = urllib.urlencode(val1)
        req = urllib2.Request(url1,data=data, headers={"workingGroups" : get_WG_string()})
        u = urllib2.urlopen(req)
        res1 =  u.read()
        if res1=='err':
            raise Exception
        
        pianificatore = User.objects.get(id = transf.idTransferSchedule.operator.id)
        
        lgenfin=strgen[:-1]
        diction=AllAliquotsContainer(lgenfin)
        #la n indica che non faccio un pdf
        lista1,intest1,dizcsv1,inte=LastPartTransfer(request,'n',diction,lconvalidati)
        if len(lgennonconvalidati)!=0:
            lista2,intest2,dizcsv2,inte=LastPartTransfer(request,'n',diction,lgennonconvalidati)            
        else:
            lista2=[]
            intest2=''
        #metto i dati nella sessione perche' mi servono poi per il PDF
        request.session['datatrasferimento']=data_fin
        request.session['destinatariotrasferimento']=''
        request.session['corrieretrasferimento']=transf.idCourier
        request.session['tracktrasferimento']=transf.trackingNumber
        
        email = LASEmail (functionality=get_functionality(), wgString=get_WG_string())
        aliquots=Aliquot.objects.filter(uniqueGenealogyID__in=lgen,availability=1)
        print 'aliquots',aliquots
        wgList=WG.objects.filter(id__in=Aliquot_WG.objects.filter(aliquot__in=aliquots).values_list('WG',flat=True).distinct())
        print 'wglist',wgList
        for wg in wgList:
            msg=['Samples transferring','','Received by:\t'+transf.addressTo.username,'Receiving date:\t'+str(transf.deliveryDate),'Courier:\t'+transf.idCourier.name]
            if transf.trackingNumber!='':
                msg.append('Tracking N.:\t'+transf.trackingNumber)
            msg.append('')
            if len(lista1)>0:                
                msg.append('These aliquots have been received:')
                msg.append('N\tGenealogy ID\tBarcode\tPosition\tVolume(ul)\tPatient code\tCreation date')           
                print 'wg',wg.name
                aliq=aliquots.filter(id__in=Aliquot_WG.objects.filter(WG=wg).values_list('aliquot',flat=True).distinct())
                print 'aliq',aliq
                i=1
                #per mantenere l'ordine dei campioni anche nell'e-mail
                for aliqtr in listaliq:
                    for al in aliq:
                        if aliqtr.idAliquot.uniqueGenealogyID==al.uniqueGenealogyID:
                            if al.uniqueGenealogyID in dizcsv1:
                                stringatab=dizcsv1[al.uniqueGenealogyID]
                                print 'stringatab ricevuti',stringatab
                                msg.append(str(i)+'\t'+stringatab)
                                i=i+1
                msg.append('')          
            if len(lista2)>0:
                msg.append('These aliquots have NOT been received:')
                msg.append('N\tGenealogy ID\tBarcode\tPosition\tVolume(ul)\tPatient code\tCreation date')
                print 'wg',wg.name
                aliq=aliquots.filter(id__in=Aliquot_WG.objects.filter(WG=wg).values_list('aliquot',flat=True).distinct())
                print 'aliq',aliq
                i=1
                #per mantenere l'ordine dei campioni anche nell'e-mail
                for aliqtr in listaliq:
                    for al in aliq:
                        print 'aliqtr',aliqtr
                        print 'al',al
                        if aliqtr.idAliquot.uniqueGenealogyID==al.uniqueGenealogyID:
                            if al.uniqueGenealogyID in dizcsv2:
                                stringatab=dizcsv2[al.uniqueGenealogyID]
                                print 'stringatab non ricevuti',stringatab
                                msg.append(str(i)+'\t'+stringatab)
                                i=i+1
                msg.append('')
                msg.append('Please execute a new transfer procedure to send right samples')
            email.addMsg([wg.name], msg)
            #mando l'e-mail al destinatario e al pianificatore
            email.addRoleEmail([wg.name], 'Assignee', [transf.operator.username])
            email.addRoleEmail([wg.name], 'Planner', [pianificatore.username])
            email.addRoleEmail([wg.name], 'Executor', [request.user.username])
        
        #lo faccio in fondo perche' se lo facessi prima cancellerei gia' la condivisione tra gruppi dei campioni
        #e quindi nella mail non avrei la segregazione giusta fra gruppi perche' non troverei certi dati associati
        #al gruppo. Questo vale per i campioni non convalidati, il cui wg viene riportato a quello originale
        if len(lgennonconvalidati)!=0:
            #devo fare la API per rimettere il container padre a queste provette
            #Uso il campo save per far capire che non devo cancellare il padre, ma salvarlo
            url1 = Urls.objects.get(default = '1').url + "/api/canc/father/"
            val1={'dizgen':json.dumps(diz2),'save':True}
            
            print 'url1',url1
            data = urllib.urlencode(val1)
            req = urllib2.Request(url1,data=data, headers={"workingGroups" : get_WG_string()})
            u = urllib2.urlopen(req)
            res1 =  u.read()
            if res1=='errore':
                raise Exception
            
            ris= togli_condivisione(lgennonconvalidati,pianificatore,transf.addressTo.username)
            if ris=='err':
                raise Exception
        
        
        try:
            email.send()
        except Exception, e:
            print 'errore',e
            transaction.rollback()
            variables = RequestContext(request, {'errore':True})
            return render_to_response('tissue2/index.html',variables)
        
        '''#mando l'e-mail al mittente e al pianificatore
        file_data = render_to_string('tissue2/transfer/report_send_receive.html', {'ricevuto':True,'aliq1':lista1,'intest1':intest1,'aliq2':lista2,'intest2':intest2,'trasf':transf,'esecutore':name}, RequestContext(request))
        
        mailDest = mittente.email
        mailPianif = pianificatore.email
        listaindir=[]
        if mailDest!='' and name!=mittente.username:
            listaindir.append(mailDest)
        if mailPianif!='' and name!=pianificatore.username:
            listaindir.append(mailPianif)
        subject, from_email = 'Transferred aliquots', settings.EMAIL_HOST_USER
        text_content = 'This is an important message.'
        html_content = file_data
        if len(listaindir)!=0:
            msg = EmailMultiAlternatives(subject, text_content, from_email, listaindir)
            msg.attach_alternative(html_content, "text/html")
            msg.send()'''
        
        variables = RequestContext(request,{'fine':True,'ricevuto':True,'aliq1':lista1,'intest1':intest1,'aliq2':lista2,'intest2':intest2,'trasf':transf})
        return render_to_response('tissue2/transfer/confirm_request.html',variables)
    except Exception,e:
        print 'errore',e
        transaction.rollback()
        variables = RequestContext(request, {'errore':True})
        return render_to_response('tissue2/index.html',variables)


'''#funzione per creare il PDF per le aliquote trasferite
@laslogin_required
@login_required
def createPDFTransfer(request):
    if request.session.get('listaaliqtrasferire'):
        lista=[]
        lista,intest,l,inte=LastPartTransfer(request,'s')
        dat=request.session.get('datatrasferimento')
        addr=request.session.get('destinatariotrasferimento')
        corriere=request.session.get('corrieretrasferimento')
        track=request.session.get('tracktrasferimento')
        file_data = render_to_string('tissue2/transfer/pdf_transfer.html', {'list_report': lista,'intest':intest,'data':dat,'addr':addr,'corr':corriere,'track':track}, RequestContext(request))
        myfile = cStringIO.StringIO()
        pisa.CreatePDF(file_data, myfile)
        myfile.seek(0)
        response =  HttpResponse(myfile, mimetype='application/pdf')
        response['Content-Disposition'] = 'attachment; filename=Transferred_Aliquots.pdf'
        return response
    else:
        return HttpResponseRedirect(reverse('tissue.views.index'))
    
#funzione per creare il CSV per le aliquote trasferite
@laslogin_required
@login_required
def createCSVTransfer(request):
    if request.session.get('listaaliqtrasferire'):
        #aliquots = request.session.get('aliquots') 
        response = HttpResponse(mimetype='text/csv')
        response['Content-Disposition'] = 'attachment; filename=Transferred_Aliquots.csv'
        writer = csv.writer(response)
        lista,intest,listacsv,intestcsv=LastPartTransfer(request,'s')
        writer.writerow([intestcsv[0]])
        for i in range(0,len(listacsv)):
            writer.writerow([listacsv[i]])
        return response 
    else:
        return HttpResponseRedirect(reverse('tissue.views.index'))'''
    
