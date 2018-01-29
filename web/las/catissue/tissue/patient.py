from __init__ import *
from catissue.tissue.utils import *

#per far vedere la schermata orientata al codice del paziente
@laslogin_required
@login_required
#@user_passes_test(lambda u: u.has_perm('tissue.can_view_patients'),login_url=settings.BASE_URL+'/tissue/error/')
@permission_decorator('tissue.can_view_BBM_patients')
def PatientView(request):
    name=request.user.username
    userList=[]
    if settings.USE_GRAPH_DB == True:        
        #non prendo solo gli utenti ancora attivi perche' magari voglio vedere cosa ha collezionato in passato un utente che non c'e' piu'.
        #Questa riga va bene per far vedere solo gli utenti appartenenti al gruppo dell'utente loggato.
        #userList=User.objects.filter(~Q(username='admin')&~Q(first_name='')).filter(id__in=WG_User.objects.filter(WG__name__in=get_WG()).values_list("user",flat=True)).order_by('last_name')
        #Con questa riga si vedono tutti gli utenti
        userList=User.objects.filter(~Q(username='admin')&~Q(first_name='')).order_by('last_name')
    else:
        userList=User.objects.filter(~Q(username='admin')&~Q(first_name='')).order_by('last_name')
    
    print 'user list',userList    
    utente=User.objects.get(username=name)
    #prendo la lista delle maschere di quell'utente
    listamasch=MaskOperator.objects.filter(operator=utente)
    form = PatientForm()
    form2=PatientForm2()
    #prendo la lista di tutti i consensi informati
    liscons=list(Collection.objects.filter(collectionEvent__isnull=False).values_list('collectionEvent',flat=True).distinct())
    variables = RequestContext(request, {'form': form,'form2': form2,'listamasch':listamasch,'userlist':userList,'liscons':json.dumps(liscons)})
    return render_to_response('tissue2/patient/view_patient.html',variables)

def createPDFPatient(request):
    if request.method=='POST':
        print request.POST
        try:
            if 'salva' in request.POST:              
                listaaliq=json.loads(request.POST.get('dati'))
                listacol=json.loads(request.POST.get('colonne'))
                request.session['listaaliqpatientpdf']=listaaliq
                request.session['listacolonnepatientpdf']=listacol
                return HttpResponse('ok')
            if 'final' in request.POST:
                lista,intest,l,inte=LastPartPatient(request,'s')
                data_def=datetime.date.today()
                operatore=request.user.username
                file_data = render_to_string('tissue2/patient/pdf_patient.html', {'list_report': lista,'intest':intest,'data_coll':data_def,'operatore':operatore}, RequestContext(request))
                myfile = cStringIO.StringIO()
                pisa.CreatePDF(file_data, myfile)
                myfile.seek(0)
                response =  HttpResponse(myfile, mimetype='application/pdf')
                response['Content-Disposition'] = 'attachment; filename=Patient_Aliquots.pdf'
                return response
        except Exception, e:
            print 'err',e
            variables = RequestContext(request, {'errore':True})
            return render_to_response('tissue2/index.html',variables)

def createCSVPatient(request):
    if request.method=='POST':
        print request.POST
        try:
            if 'salva' in request.POST:              
                listaaliq=json.loads(request.POST.get('dati'))
                listacol=json.loads(request.POST.get('colonne'))
                request.session['listaaliqpatientpdf']=listaaliq
                request.session['listacolonnepatientpdf']=listacol
                return HttpResponse('ok')
            if 'final' in request.POST:
                response = HttpResponse(mimetype='text/csv')
                response['Content-Disposition'] = 'attachment; filename=Patient_Aliquots.csv'
                #writer = csv.writer(response,delimiter='\t')
                writer = csv.writer(response)
                lista,intest,listacsv,intestcsv=LastPartPatient(request,'n')
                writer.writerow([intestcsv[0]])
                for i in range(0,len(listacsv)):
                    #csvString=str(i+1)+";"+str(val[0])+";"+str(val[3])+";"+val[1]+";"+val[2]
                    writer.writerow([listacsv[i]])
                return response 
        except Exception, e:
            print 'err',e
            variables = RequestContext(request, {'errore':True})
            return render_to_response('tissue2/index.html',variables)

#@user_passes_test(lambda u: u.has_perm('tissue.can_view_patients'),login_url=settings.BASE_URL+'/tissue/error/')
@permission_decorator('tissue.can_view_BBM_patients')
def PatientExport(request):
    if request.method=='POST':
        print request.POST
        try:
            if 'salva' in request.POST:              
                listaaliq=json.loads(request.POST.get('dati'))
                listacol=json.loads(request.POST.get('colonne'))
                request.session['listaaliqpatientpdf']=listaaliq
                request.session['listacolonnepatientpdf']=listacol
                return HttpResponse('ok')
            if 'final' in request.POST:
                scopo=request.POST.get('esporta')
                #se scopo e' 0, allora devo mandare i campioni alla derivazione
                if scopo=='0':
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
                    
                    lisaliq=[]
                    lisbarc=[]
                    lispos=[]
                    listagen=request.session.get('listaaliqpatientpdf')
                    stringtot=''
                    for aliq in listagen:
                        print 'aliq',aliq
                        for val in aliq:
                            print 'val',val
                            stringtot+=val+'&'
                    stringtotale=stringtot[:-1]
                    diz=AllAliquotsContainer(stringtotale)
                    for gen in diz:
                        lista=diz[gen]
                        for val in lista:
                            ch=val.split('|')
                            lisaliq.append(ch[0])
                            lisbarc.append(ch[1])
                            lispos.append(ch[2])
                    print 'lisaliq',lisaliq
                    #request.session['derivare']=listafin
                    form = DerivedInit()
                    variables = RequestContext(request, {'form':form,'posizionare':zip(lisaliq,lisbarc,lispos),'assignUsersList':assignUsersList,'addressUsersList':addressUsersList})
                    return render_to_response('tissue2/derived/derived.html',variables)
                #se scopo e' 1, allora devo mandare i campioni alla schermata esperimenti
                elif scopo=='1':
                    listagen=request.session.get('listaaliqpatientpdf')
                    response = HttpResponse(mimetype='text/csv')
                    response['Content-Disposition'] = 'attachment; filename=Schedule_Value.las'
                    writer = csv.writer(response)
                    writer.writerow(['GenealogyID\tBarcode\tSchedule Volume(ul)\tSchedule Quantity(ug)\tGE/Vex(GE/ml)'])
                    listatemp=[]
                    stringtot=''
                    for aliq in listagen:
                        for val in aliq:
                            listatemp.append(val)
                            stringtot+=val+'&'
                            
                    stringtotale=stringtot[:-1]
                    diz=AllAliquotsContainer(stringtotale)
                    
                    lisaliq=Aliquot.objects.filter(uniqueGenealogyID__in=listatemp)
                    
                    mis=Measure.objects.get(name='GE/Vex')
                    for aliq in lisaliq:
                        valore=''
                        #se e' un derivato provo a vedere se c'e' il valore dei GE
                        if aliq.derived==1:
                            #dal campione risalgo al der event
                            lisderevent=DerivationEvent.objects.filter(idSamplingEvent=aliq.idSamplingEvent)
                            if len(lisderevent)!=0:
                                #prendo il qual event dall'aliqderivationschedule
                                lisqual=QualityEvent.objects.filter(idAliquotDerivationSchedule=lisderevent[0].idAliqDerivationSchedule)
                                if len(lisqual)!=0:
                                    #prendo l'evento di misura con il valore del GE associato
                                    liseventi=MeasurementEvent.objects.filter(idMeasure=mis,idQualityEvent=lisqual[0])
                                    if len(liseventi)!=0:
                                        valore=liseventi[0].value
                            #devo vedere se il campione e' stato rivalutato
                            lisriv=QualityEvent.objects.filter(idAliquot=aliq).order_by('-misurationDate','-id')
                            if len(lisriv)!=0:
                                lista=[]
                                for riv in lisriv:
                                    lista.append(riv.id)
                                #in lisriv[0] ho il valore piu' recente
                                #prendo l'evento di misura con il valore del GE associato
                                liseventi=MeasurementEvent.objects.filter(idMeasure=mis,idQualityEvent__in=lista).order_by('-id')
                                if len(liseventi)!=0:
                                    valore=liseventi[0].value
                        lista=diz[aliq.uniqueGenealogyID]
                        print 'lista',lista
                        if len(lista)==0:
                            barc=''
                        else:
                            for val in lista:
                                ch=val.split('|')
                                barc=ch[1]
                        csvString=aliq.uniqueGenealogyID+'\t'+barc+'\t\t\t'+str(valore)
                        writer.writerow([csvString])
                    return response
                #se scopo e' 2, allora devo mandare i campioni al modulo di beaming
                #se scopo e' 3, allora devo mandare i campioni al modulo di digitalPCR
                elif scopo=='2' or scopo=='3' or scopo=='4':
                    name=request.user.username
                    listagen=request.session.get('listaaliqpatientpdf')
                    listacolonne=request.session.get('listacolonnepatientpdf')
                    print 'listagen', listagen
                    print 'liscolonne',listacolonne
                    liscol=[]
                    dizcolonne={}
                    for col in listacolonne:
                        campo=MaskField.objects.get(name=col)
                        liscol.append(campo)
                        
                        dizval={}
                        dizval['name']=campo.name
                        dizval['measure']=campo.identifier
                        dizcolonne[campo.id]=dizval

                    dizgenerale={}
                    for diz in listagen:
                        for aliq in diz: 
                            print 'aliq',aliq
                            lisvalori=diz[aliq]
                            print 'lisvalori',lisvalori
                            diztemp={}
                            for i in range(0,len(lisvalori)):
                                val=lisvalori[i]
                                #print 'val',val
                                diztemp[liscol[i].id]=val
                            dizgenerale[aliq]=diztemp
                    if scopo=='2':
                        servizio=WebService.objects.get(name='Beaming')
                        urlmodul=Urls.objects.get(idWebService=servizio).url
                        #faccio la post al modulo di beaming dandogli la lista con dentro i dizionari
                        url=urlmodul+'/api.newbeamingFilter'
                    elif scopo=='3':
                        servizio=WebService.objects.get(name='DigitalPCR')
                        urlmodul=Urls.objects.get(idWebService=servizio).url
                        #faccio la post al modulo di digitalpcr dandogli la lista con dentro i dizionari
                        url=urlmodul+'/api.newdigitalpcrFilter'
                    elif scopo=='4':
                        servizio=WebService.objects.get(name='NextGenerationSequencing')
                        urlmodul=Urls.objects.get(idWebService=servizio).url
                        #faccio la post al modulo di digitalpcr dandogli la lista con dentro i dizionari
                        url=urlmodul+'/api.newngsFilter'
                        
                    lis=json.dumps(dizgenerale)
                    lcolonne=json.dumps(dizcolonne)
                    val2={'operator':name,'aliquots':lis,'filter':lcolonne}
                    print 'url',url
                    print 'val2',val2
                    data1 = urllib.urlencode(val2)
                    req = urllib2.Request(url,data=data1, headers={"workingGroups" : get_WG_string()})
                    u = urllib2.urlopen(req)
                    #u = urllib2.urlopen(url, data1)
                    res =  json.loads(u.read())
                    print 'res',res
                    reqid=res['filterid']
                    print 'reqid',reqid
                    #reindirizzo sulla pagina del modulo
                    if reqid!='Error':
                        urlfin=urlmodul+'/filter_results/'+str(reqid)+'/'
                        return HttpResponseRedirect(urlfin)
                    else:
                        raise Exception
        except Exception, e:
            print 'err',e
            variables = RequestContext(request, {'errore':True})
            return render_to_response('tissue2/index.html',variables)
