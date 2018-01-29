from __init__ import *
from catissue.tissue.utils import *
from catissue.api.handlers import *

def RepresentsInt(s):
    try: 
        int(s)
        return True
    except ValueError:
        return False

@get_functionality_decorator
def ajaxDrugAutocomplete(request):
    if 'term' in request.GET:
        treat = Drug.objects.filter(name__icontains=request.GET.get('term'))[:10]
        res=[]
        for p in treat:
            p = {'id':p.id, 'label':p.__unicode__(), 'value':p.__unicode__()}
            res.append(p)
        return HttpResponse(simplejson.dumps(res))
    return HttpResponse()

@laslogin_required
@login_required
@permission_decorator('tissue.can_view_BBM_institutional_collection')
def CollectionInit(request):
    forminiziale=ExternFormInit()
    a=SchemiPiastre()
    if request.method=='POST':
        print request.POST
        if 'tipi' in request.POST:
            forminiziale = ExternFormInit(request.POST)
            tipo=request.POST.get('tipi')
            print tipo
            if tipo=='0':
                #sto facendo un nuovo collezionamento quindi rimando alla schermata classica di collezione
                form = CollectionForm()
                form.fields['date'].initial=date.today()
                formT = TissueForm()
                variables = RequestContext(request, {'form': form,'formT':formT,'t':True,'a':a,'secondo':False})   
                return render_to_response('tissue2/collection/collection.html',variables)
            elif tipo=='1':
                #sto facendo un assegnamento ad una collezione esistente
                mdamTemplates = getMdamTemplates([41,44,45])
                print 'mdamTemplates',mdamTemplates
                mdamurl=Urls.objects.get(idWebService=WebService.objects.get(name='MDAM').id).url
                listot=getGenealogyDict()
                variables = RequestContext(request, {'mdamTemplates':json.dumps(mdamTemplates), 'mdam_url':mdamurl,'secondo':True,'genid':json.dumps(listot)})
                return render_to_response('tissue2/collection/collection_reopen.html',variables)      
    else:
        forminiziale = ExternFormInit()
    variables = RequestContext(request, {'form':forminiziale,'primo':True})
    return render_to_response('tissue2/collection/collection_reopen.html',variables)

@laslogin_required
@login_required
#@user_passes_test(lambda u: u.has_perm('tissue.can_view_institutional_collection'),login_url=settings.BASE_URL+'/tissue/error/')
@permission_decorator('tissue.can_view_BBM_institutional_collection')
def collection(request):    
    idinput=[]
    t=True
    secondo=False
    a=Collection()
    
    if request.method=='POST':
        print request.POST
        form = CollectionForm(request.POST)
        formT = TissueForm(request.POST)
        if form.is_valid()and formT.is_valid():
            #ho premuto il pulsante submit della prima schermata 
            #'start' e' il valore dell'attributo name del pulsante di submit
            #if 'start' in request.POST:
            secondo=True
            #data ha la notazione anno-mese-giorno, come richiede il DB
            data=request.POST.get('date')
            #d=dat.split('-')
            
            #data=d[2]+'-'+d[1]+'-'+d[0]
            #request.session['dat']=data
            #mi ritorna l'abbreviazione del tumore
            tumore=CollectionType.objects.get(id=request.POST['Tumor_Type'])
            #guardo se sono arrivato a questa schermata riaprendo una collezione o se e' un nuovo campionamento
            reopen=request.POST.get('reopen_caso')
            if reopen=='':
                casuale=False
                if 'randomize' in request.POST:
                    casuale=True 
                
                #faccio la chiamata al LASHub per farmi dare il codice del caso
                val=LasHubNewCase(request, casuale, tumore.abbreviation)
                print 'r.text',val
                
                caso=NewCase(val, casuale, tumore)
            else:
                caso=reopen    
            
            print 'caso',caso
            request.session['caso']=caso
            
            posto=request.POST.get('Place')
            workgr=request.POST.get('workgr')
            cons_esist=request.POST.get('cons_exists')
            localid=request.POST.get('localid')
            local_exists=request.POST.get('local_exists')
            collectionEvent=request.POST['barcode'].strip()
            paziente=request.POST['patient'].strip()

            proto=request.POST['protocol']

            r=formT.cleaned_data.get('tissue')
            for i in range(0,len(r)):
                print 'tess selezionati: '+str(TissueType.objects.get(id=r[i]))
                tissueT=TissueType.objects.get(id=r[i])
                idinput.append(r[i])
                #idinput.append('id_tissue_'+str(int(r[i])-1))
               
            variables = RequestContext(request, {'form': form,'formT':formT,'t':t,'a':a,'secondo':secondo,"tissueT":tissueT,"idinput":idinput,"tumore":tumore.abbreviation,"tumid":tumore.id,"caso":caso,'posto':posto,'dat':data,'coll_ev':collectionEvent,'patient':paziente,'study_prot':proto,'workgr':workgr,'reopen':reopen,'ic_exists':cons_esist,'localid':localid,'local_exists':local_exists})
            return render_to_response('tissue2/collection/collection.html',variables)
            #except:
                #err_message = "Error"
        else:
            t=False
    else:
        form = CollectionForm()
        form.fields['date'].initial=date.today()
        formT = TissueForm()
        #formT.fields['tissue'].choices=CASI
    variables = RequestContext(request, {'form': form,'formT':formT,'t':t,'a':a,'secondo':secondo})   
    return render_to_response('tissue2/collection/collection.html',variables)

class ErrorCollection(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

@laslogin_required    
@transaction.commit_on_success
@login_required
#@user_passes_test(lambda u: u.has_perm('tissue.can_view_institutional_collection'),login_url=settings.BASE_URL+'/tissue/error/')
@permission_decorator('tissue.can_view_BBM_institutional_collection')
def coll_save(request):
    if request.method=='POST':
        print request.POST
        try:           
            if 'final' in request.POST:
                #la n indica che non faccio un pdf
                lista,intest,l,inte=LastPartCollection(request,'n')
                collevent=request.session.get('collEventCollezione')
                if request.session.has_key('codPazienteCollezione'):
                    codpaz=request.session.get('codPazienteCollezione')
                else:
                    codpaz=''
                variables = RequestContext(request,{'fine2':True,'aliq':lista,'intest':intest,'collevent':collevent,'codpaz':codpaz})
                return render_to_response('tissue2/collection/collection.html',variables)
            if 'salva' in request.POST:
                listaal=[]
                lisbarclashub=[]
                piena=False
                pezziusati=0
                disponibile=1
                derivato=0
                
                posto=request.POST.get('ospedale')
                postovero=Source.objects.get(id=posto)
                tum=request.POST.get('tum')
                tumo=CollectionType.objects.get(abbreviation=tum)
                #e' il caso, ma senza gli zeri davanti per fare il genId
                item=request.POST.get('itemcode')
                collEvent=request.POST.get('collectevent')
                paz=request.POST.get('paziente')
                
                protoc=request.POST.get('protoc')
                pr=CollectionProtocol.objects.get(id=protoc)
                                
                workingGroup=request.POST.get('wg')
                print 'work group',workingGroup
                #se il protocollo e' della Marsoni allora devo mettere in share anche lei per le aliquote
                liscollinvestig=CollectionProtocolInvestigator.objects.filter(idCollectionProtocol=pr)
                trovato=False
                if len(liscollinvestig)!=0:
                    for coll in liscollinvestig:
                        if coll.idPrincipalInvestigator.surname=='Marsoni' and coll.idPrincipalInvestigator.name=='Silvia':
                            trovato=True
                            break
                listawg=[workingGroup]
                if trovato:
                    listawg.append('Marsoni_WG')
                print 'listawg',listawg
                set_initWG(listawg)
                
                cons_exists=request.POST.get('cons_exists')
                print 'cons_exists',cons_exists
                local_id=request.POST.get('local_id')
                print 'local_id',local_id
                local_exists=request.POST.get('local_exists')
                print 'local_exists',local_exists
                
                #se non e' stato inserito il codice paziente
                if paz=='/':
                    paz=''
                else:
                    #metto il cod paziente nella sessione per farlo vedere dopo nel PDF
                    request.session['codPazienteCollezione']=paz
                #metto il coll event nella sessione per farlo vedere dopo nel PDF
                request.session['collEventCollezione']=collEvent
                
                listaaliq=json.loads(request.POST.get('dati'))
                #devo vedere se ci sono delle aliquote da salvare per quella collezione
                for tipialiq in listaaliq:
                    if len(listaaliq[tipialiq])!=0:
                        piena=True
                        break
                
                if piena==True:        
                    #restituisce la collezione e un'indicazione per sapere se l'oggetto c'era gia' 
                    #o se e' stato creato apposta, che salvo in creato
                    collezione,creato=Collection.objects.get_or_create(itemCode=item,
                                 idSource=postovero,
                                 idCollectionType=tumo,
                                 collectionEvent=collEvent,
                                 patientCode=paz,
                                 idCollectionProtocol=pr)
                    print 'collezione',collezione
                    
                    data_coll=request.POST.get('dat')
                    #mi da' l'operatore
                    operatore=request.POST.get('operatore')
                    
                    request.session['data_collezionamento']=data_coll
                    request.session['operatore_collezionamento']=operatore
                    
                    #salvo gli eventuali parametri clinici per la collezione
                    if request.session.has_key('dizclinicalparameter'):
                        lisparam=request.session.get('dizclinicalparameter')
                        print 'lisparam',lisparam
                        #ogni valore della lista e' un dizionario con dentro i valori del parametro clinico in questione
                        for diz in lisparam:
                            idparamclin=diz['idfeat']
                            param=ClinicalFeature.objects.get(id=idparamclin)
                            print 'param',param
                            lisval=diz['value']
                            print 'lisval',lisval
                            #lisval e' una lista con dentro i valori da salvare
                            for v in lisval:
                                print 'v',v
                                #creo l'oggetto feature per la collezione
                                clinfeat=CollectionClinicalFeature(idCollection=collezione,
                                                               idClinicalFeature=param,
                                                               value=v)
                                clinfeat.save()
                                print 'clinfeat',clinfeat

                    #salvo la serie
                    ser,creato=Serie.objects.get_or_create(operator=operatore,
                                                           serieDate=data_coll)
                    
                    for tipialiq in listaaliq:
                        for barc in listaaliq[tipialiq]:
                            for prov in listaaliq[tipialiq][barc]:
                                genid=prov['genID']
                                tipoaliq=tipialiq
                                piastra=barc
                                pos=prov['pos']
                                numpezzi=prov['qty']
                                print 'gen',genid
                                print 'tipoaliq',tipoaliq
                                print 'piastra',piastra
                                print 'pos',pos
                                print 'numpezzi',numpezzi
                                
                                g = GenealogyID(genid)
                                tumore=g.getOrigin()
                                print 'tumore',tumore
                                caso=g.getCaseCode()
                                print 'caso',caso
                                
                                t=g.getTissue()
                                tessuto_esp=TissueType.objects.get(abbreviation=t)
                                print 'tessuto',tessuto_esp.id
                                
                                #salvo il campionamento
                                campionamento,creato=SamplingEvent.objects.get_or_create(idTissueType=tessuto_esp,
                                                             idCollection=collezione,
                                                             idSource=postovero,
                                                             idSerie=ser,
                                                             samplingDate=data_coll)
                                print 'camp',campionamento
                                
                                barcode=None
                                #se sto trattando vitale, rna e snap
                                if(tipoaliq!='FF')and(tipoaliq!='OF')and(tipoaliq!='CH'):#and(tipoaliq!='PL')and(tipoaliq!='PX')and not(prov.has_key('volume')): 
                                    barcodepiastraurl=piastra.replace('#','%23')
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
                                        print 'e',e
                                    #se la API mi restituisce dei valori perche' gli ho dato un codice
                                    #corretto per la piastra    
                                    if 'children' in data:    
                                        #per ottenere il barcode data la posizione    
                                        for w in data['children']:
                                            if w['position']==pos:
                                                barcode=w['barcode']
                                                print 'barc',barcode
                                                break;
                                        ffpe='false'
                                    else:
                                        #vuol dire che sto salvando una nuova provetta e quindi il barcode 
                                        #risulta essere cio' che e' salvato nella variabile piastra
                                        barcode=piastra
                                        piastra=''
                                        pos=''
                                        ffpe='true'
                                        lisbarclashub.append(barcode)
                                    #valori=str(genid)+','+str(piastra)+','+str(pos)+','+str(numpezzi)+','+barcode+','+tipoaliq+',false, , '
                                #se ho ffpe o of o ch o pl o px il barcode ce l'ho gia' e non devo andare a leggerlo
                                #il barcode e' salvato nella variabile piastra
                                else:
                                    barcode=piastra
                                    piastra=''
                                    pos=''
                                    ffpe='true'
                                    lisbarclashub.append(barcode)
                                    
                                conta=' '
                                volu=' '
                                if prov.has_key('volume'):
                                    numpezzi=''
                                    volu=prov['volume']
                                    if prov.has_key('cellcount'):
                                        conta=prov['cellcount']
                                valori=genid+','+str(piastra)+','+str(pos)+','+str(numpezzi)+','+barcode+','+tipoaliq+','+ffpe+','+volu+','+conta+',,,,'+str(data_coll)
                                
                                print 'barcode',barcode 
                                tipoaliquota= AliquotType.objects.get(abbreviation=tipoaliq)
                                print 'tipo aliquota',tipoaliq
                                a=Aliquot(barcodeID=barcode,
                                       uniqueGenealogyID=str(genid),
                                       idSamplingEvent=campionamento,
                                       idAliquotType=tipoaliquota,
                                       timesUsed=pezziusati,
                                       availability=disponibile,
                                       derived=derivato
                                       )
                                print 'a',a
                                a.save()
                                
                                listaal.append(valori)
                                print 'listaaliq',listaal
                                
                                #se sto salvando del sangue ho anche altre feature
                                if prov.has_key('volume'):
                                    vo=prov['volume']
                                    #ho il valore in ml e devo trasformarlo in ul
                                    volu=float(vo)*1000
                                    featvol=Feature.objects.get(Q(idAliquotType=tipoaliquota)&Q(name='Volume'))
                                    aliqfeaturevol=AliquotFeature(idAliquot=a,
                                                               idFeature=featvol,
                                                               value=volu)
                                    aliqfeaturevol.save()
                                    print 'featu volume',aliqfeaturevol
                                    if prov.has_key('cellcount'):
                                        conta=prov['cellcount']
                                        featconta=Feature.objects.get(Q(idAliquotType=tipoaliquota)&Q(name='Count'))
                                        aliqfeatureconta=AliquotFeature(idAliquot=a,
                                                                   idFeature=featconta,
                                                                   value=conta)
                                        aliqfeatureconta.save()
                                        print 'aliq',aliqfeatureconta
                                #salvo i campioni normali
                                else:
                                    #salvo il numero di pezzi
                                    fea=Feature.objects.get(Q(idAliquotType=tipoaliquota)&Q(name='NumberOfPieces'))
                                    aliqfeature=AliquotFeature(idAliquot=a,
                                                               idFeature=fea,
                                                               value=numpezzi)
                                    aliqfeature.save()
                                    print 'aliq',aliqfeature
                        
                    request,errore=SalvaInStorage(listaal,request)
                    print 'err', errore   
                    if errore==True:
                        raise Exception
                    #devo fare gia' il commit perche' devo passare al modulo clinico la collezione, che deve gia' esistere sul grafo
                    #altrimenti non si riesce a collegare il nodo collezione con il consenso informato
                    transaction.commit()
                    #faccio la API al modulo clinico per dirgli di salvare
                    #creo due liste e in una di queste inserisco la collezione, a seconda che il cons esista o meno
                    lisexist=[]
                    lisnotexist=[]
                    lislocalid=[]
                    #se ho riaperto una collezione il cons_exist sara' a null quindi non mi riempie le liste
                    #ed e' giusto cosi' perche' non devo dire niente al modulo clinico
                    if cons_exists=='True':
                        lisexist.append({'caso':collezione.itemCode,'tum':collezione.idCollectionType.abbreviation,'consenso':collezione.collectionEvent,'progetto':collezione.idCollectionProtocol.project,'wg':[workingGroup]})
                    elif cons_exists=='False':
                        diztemp={'caso':collezione.itemCode,'tum':collezione.idCollectionType.abbreviation,'consenso':collezione.collectionEvent,'progetto':collezione.idCollectionProtocol.project,'source':collezione.idSource.internalName,'wg':[workingGroup],'operator':operatore}
                        if local_exists=='True':
                            #il paziente esiste gia'
                            diztemp['paziente']=collezione.patientCode
                        else:
                            #il paziente inserito non esiste ancora
                            if collezione.patientCode=='':
                                #il paziente non e' stato inserito dall'utente, quindi non viene creato niente
                                diztemp['paziente']=''
                            else:
                                #il paziente e' stato inserito
                                diztemp['newLocalId']=collezione.patientCode
                        lisnotexist.append(diztemp)
                    if local_id!='None' and local_id!='/':
                        lislocalid.append(local_id)
                    #qui non passo Marsoni_WG nella lista dei working group perche' lei possiede gia' il nodo paziente e IC e non serve
                    #metterla in share 
                    errore=saveInClinicalModule(lisexist,lisnotexist,[workingGroup],operatore,lislocalid)
                    if errore:
                        raise Exception
                request.session['aliquots']=listaal   
                transaction.commit()
                return HttpResponse()
        except Exception,e:
            print 'err',e
            transaction.rollback()
            errore=True
            variables = RequestContext(request, {'errore':errore})
            return render_to_response('tissue2/index.html',variables)
    else:
        a=Collection()
        formT = TissueForm()
        variables = RequestContext(request, {'secondo':True,'a':a,'formT':formT})
        return render_to_response('tissue2/collection/collection.html',variables)

#questa semplice view serve a ridirezionare la pagina dopo aver cliccato su 'continue' nella pagina che notifica l'errore
@laslogin_required
@login_required
def CollErr(request):
    errore=True
    variables = RequestContext(request, {'errore':errore})
    return render_to_response('tissue2/index.html',variables)

#per far comparire la schermata in cui inserire i parametri clinici
@laslogin_required
@login_required
#@user_passes_test(lambda u: u.has_perm('tissue.can_view_institutional_collection'),login_url=settings.BASE_URL+'/tissue/error/')
@permission_decorator('tissue.can_view_BBM_institutional_collection')
def CollParam(request):
    if request.session.has_key('clinicalparamreopencollection'):
        diztot=request.session.get('clinicalparamreopencollection')
    else:
        diztot={}
    listapar=ClinicalFeature.objects.filter(type='Level1').order_by('name')
    if request.method=='POST':
        print request.POST
        
        if 'salva' in request.POST:
            lisfin=json.loads(request.POST.get('dati'))
            print 'lisfin',lisfin
            reopen=request.POST.get('reopen')
            if reopen=='Yes':
                tumore=request.POST.get('tumore')
                caso=request.POST.get('caso')
                diztot[tumore+'|'+caso]=lisfin
                request.session['clinicalparamreopencollection']=diztot
                print 'diztot',diztot
            else:
                request.session['dizclinicalparameter']=lisfin
            return HttpResponse()
        if 'final' in request.POST:
            variables = RequestContext(request,{'fine':True})
            return render_to_response('tissue2/collection/collection_param.html',variables)
    else:
        variables = RequestContext(request,{'lista':listapar})
        return render_to_response('tissue2/collection/collection_param.html',variables)

#funzione per creare il PDF per le aliquote inserite
@laslogin_required
@login_required
#@user_passes_test(lambda u: u.has_perm('tissue.can_view_institutional_collection'),login_url='/tissue/error/')
@permission_decorator('tissue.can_view_BBM_institutional_collection')
def createPDF(request):
    if request.session.get('aliquots'):
        lista=[]
        lista,intest,l,inte=LastPartCollection(request,'s')
        data=request.session.get('data_collezionamento')
        print 'data',data
        ddd=data.split('-')
        print 'dd',ddd[0]
        data_def=datetime.date(int(ddd[0]),int(ddd[1]),int(ddd[2]))
        operatore=request.session.get('operatore_collezionamento')
        collevent=request.session.get('collEventCollezione')
        if request.session.has_key('codPazienteCollezione'):
            codpaz=request.session.get('codPazienteCollezione')
        else:
            codpaz=''
        file_data = render_to_string('tissue2/pdf_report.html', {'list_report': lista,'intest':intest,'data_coll':data_def,'operatore':operatore,'collevent':collevent,'paziente':codpaz}, RequestContext(request))
        myfile = cStringIO.StringIO()
        pisa.CreatePDF(file_data, myfile)
        myfile.seek(0)
        response =  HttpResponse(myfile, mimetype='application/pdf')
        response['Content-Disposition'] = 'attachment; filename=Collected_Aliquots.pdf'
        #response=PDFMaker(request, 'Collected_Aliquots.pdf', 'tissue2/pdf_report.html', lista)
        return response
    else:
        return HttpResponseRedirect(reverse('tissue.views.index'))

#funzione per creare il CSV per le aliquote inserite
@laslogin_required
@login_required
#@user_passes_test(lambda u: u.has_perm('tissue.can_view_institutional_collection'),login_url='/tissue/error/')
@permission_decorator('tissue.can_view_BBM_institutional_collection')
def createCSV(request):
    if request.session.get('aliquots'):
        #aliquots = request.session.get('aliquots') 
        response = HttpResponse(mimetype='text/csv')
        response['Content-Disposition'] = 'attachment; filename=Collected_Aliquots.csv'
        writer = csv.writer(response)
        lista,intest,listacsv,intestcsv=LastPartCollection(request,'s')
        writer.writerow([intestcsv[0]])
        for i in range(0,len(listacsv)):
            #csvString=str(i+1)+";"+str(val[0])+";"+str(val[3])+";"+val[1]+";"+val[2]
            writer.writerow([listacsv[i]])
        return response 
    else:
        return HttpResponseRedirect(reverse('tissue.views.index'))
    
@laslogin_required
@login_required
#@user_passes_test(lambda u: u.has_perm('tissue.can_view_collaboration_collection'),login_url=settings.BASE_URL+'/tissue/error/')
@permission_decorator('tissue.can_view_BBM_collaboration_collection')
def ExternAliquots(request):
    forminiziale=ExternFormInit()
    a=SchemiPiastre()
    if request.method=='POST':
        print request.POST
        if 'tipi' in request.POST:
            forminiziale = ExternFormInit(request.POST)
            tipo=request.POST.get('tipi')
            print tipo
            if tipo=='1':
                print 'tipo1'
                secondo=True
                formfinale=ExternFormExistingCollection()
                variables = RequestContext(request, {'formfinale':formfinale,'secondo':secondo,'a':a,'tipo':tipo})
                return render_to_response('tissue2/collection/aliq_esterne.html',variables)
            elif tipo=='0':
                print 'tipo0'
                secondo=True
                formfinale=ExternFormNewCollectionPart1()
                formfinale.fields['date'].initial=date.today()
                variables = RequestContext(request, {'formfinale':formfinale,'secondo':secondo,'a':a,'tipo':tipo})
                return render_to_response('tissue2/collection/aliq_esterne.html',variables)        
    else:
        forminiziale = ExternFormInit()
    primo=True
    variables = RequestContext(request, {'form':forminiziale,'primo':primo})
    return render_to_response('tissue2/collection/aliq_esterne.html',variables)

@transaction.commit_on_success
@laslogin_required
@login_required
@permission_decorator('tissue.can_view_BBM_collaboration_collection')
def ExternAliquotsNewCollection(request):
    if request.method=='POST':
        print request.POST
        a=SchemiPiastre()
        try:
            formfinale=ExternFormNewCollectionPart1(request.POST)
            print 'form',formfinale.is_valid()
            if formfinale.is_valid():
                #mi ritorna l'abbreviazione del tumore
                tumore=CollectionType.objects.get(id=request.POST['Tumor_Type'])
                posto=request.POST.get('Hospital')
                workgr=request.POST.get('workgr')
                print 'worgr',workgr
                cons_esist=request.POST.get('cons_exists')
                localid=request.POST.get('localid')
                print 'localid',localid
                local_esist=request.POST.get('local_exists')
                casuale=False
                if 'randomize' in request.POST:
                    casuale=True 
                
                #faccio la chiamata al LASHub per farmi dare il codice del caso
                val=LasHubNewCase(request, casuale, tumore.abbreviation)
                print 'r.text',val
                
                caso=NewCase(val, casuale, tumore)
                
                print 'caso',caso
                geniniz=tumore.abbreviation+caso
                print 'geniniz',geniniz
                form2=ExternFormNewCollectionPart2()
                
                variables = RequestContext(request, {'formfinale': formfinale,'form2':form2,'secondo':True,'a':a,'tipo':'0','gen':geniniz,'caso':caso,'wgroup':workgr,'ic_exists':cons_esist,'local_id':localid,'local_exists':local_esist,'ospedale':posto})
                return render_to_response('tissue2/collection/aliq_esterne.html',variables)
            else:
                variables = RequestContext(request, {'formfinale':formfinale,'secondo':True,'a':a,'tipo':'0'})
                return render_to_response('tissue2/collection/aliq_esterne.html',variables)
        except Exception, e:
            transaction.rollback()
            print 'except',e
            errore=True
            variables = RequestContext(request, {'errore':errore})
            return render_to_response('tissue2/index.html',variables)

@transaction.commit_on_success
@laslogin_required
@login_required
#@user_passes_test(lambda u: u.has_perm('tissue.can_view_collaboration_collection'),login_url=settings.BASE_URL+'/tissue/error/')
@permission_decorator('tissue.can_view_BBM_collaboration_collection')
def SaveExternAliquots(request):
    if request.method=='POST':
        print request.POST
        try:
            listaal=[]
            lisbarclashub=[]
            piena=False
            pezziusati=0
            disponibile=1
            derivato=0
            lisexist=[]
            lisnotexist=[]
            lislocalid=[]
            workingGroup=request.POST.get('wg')
            print 'work group',workingGroup
            listawg=[workingGroup]
            
            if 'final' in request.POST:
                #la n indica che non faccio un pdf
                lista,intest,l,inte=LastPartExternAliquot(request,'n')
                variables = RequestContext(request,{'fine':True,'aliq':lista,'intest':intest})
                return render_to_response('tissue2/collection/aliq_esterne.html',variables)
            #sto salvando una nuova collezione
            if 'salva_nuova' in request.POST:
                posto=request.POST.get('ospedale')
                postovero=Source.objects.get(id=posto)
                tum=request.POST.get('tum')
                tumo=CollectionType.objects.get(id=tum)
                #e' il caso gia' con gli zeri davanti
                item=request.POST.get('itemcode')
                collEvent=request.POST.get('collectevent').strip()
                paz=request.POST.get('paziente').strip()
                #se non e' stato inserito il codice paziente
                if paz!='':
                    #metto il cod paziente nella sessione per farlo vedere dopo nel PDF
                    request.session['codPazienteCollezioneEsterna']=paz
                #metto il coll event nella sessione per farlo vedere dopo nel PDF
                request.session['collEventCollezioneEsterna']=collEvent
                protoc=request.POST.get('protoc')
                pr=CollectionProtocol.objects.get(id=protoc)                
                
                listaaliq=json.loads(request.POST.get('dati'))
                
                data_coll=request.POST.get('dat')
                #datt=data_c.split('-')
                #data_coll=datt[2]+'-'+datt[1]+'-'+datt[0]
                #mi da' l'operatore
                operatore=request.POST.get('operatore')
                cons_exists=request.POST.get('cons_exists')
                print 'cons_exists',cons_exists
                local_id=request.POST.get('local_id')
                print 'local_id',local_id
                local_exists=request.POST.get('local_exists')
                print 'local_exists',local_exists
                                
                #devo vedere se ci sono delle aliquote da salvare per quella collezione
                for tipialiq in listaaliq:
                    if len(listaaliq[tipialiq])!=0:
                        piena=True
                        break
                
                if piena==True:
                    #restituisce la collezione e un'indicazione per sapere se l'oggetto c'era gia' 
                    #o se e' stato creato apposta, che salvo in creato
                    collezione,creato=Collection.objects.get_or_create(itemCode=item,
                                 idSource=postovero,
                                 idCollectionType=tumo,
                                 collectionEvent=collEvent,
                                 patientCode=paz,
                                 idCollectionProtocol=pr)
                    print 'collezione',collezione
                    #riempio le liste solo se sto facendo una nuova collezione. Se sto assegnando a una gia' esistente no
                    if cons_exists=='True':
                        lisexist.append({'caso':collezione.itemCode,'tum':collezione.idCollectionType.abbreviation,'consenso':collezione.collectionEvent,'progetto':collezione.idCollectionProtocol.project,'wg':[workingGroup]})
                    elif cons_exists=='False':
                        diztemp={'caso':collezione.itemCode,'tum':collezione.idCollectionType.abbreviation,'consenso':collezione.collectionEvent,'progetto':collezione.idCollectionProtocol.project,'source':collezione.idSource.internalName,'wg':[workingGroup],'operator':operatore}                    
                        if local_exists=='True':
                            #il paziente esiste gia'
                            diztemp['paziente']=collezione.patientCode
                        else:
                            #il paziente inserito non esiste ancora
                            if collezione.patientCode=='':
                                #il paziente non e' stato inserito dall'utente, quindi non viene creato niente
                                diztemp['paziente']=''
                            else:
                                #il paziente e' stato inserito
                                diztemp['newLocalId']=collezione.patientCode                        
                        
                        lisnotexist.append(diztemp)
                    if local_id!='None' and local_id!='/':
                        lislocalid.append(local_id)
            if 'esistente' in request.POST:
                tum=request.POST.get('tum')
                tumo=CollectionType.objects.get(id=tum)
                print 
                #e' il caso gia' con gli zeri davanti
                item=request.POST.get('itemcode')
                
                operatore=request.POST.get('operatore')
                
                listaaliq=json.loads(request.POST.get('dati'))
                #data_coll=str(date.today())
                data_coll=request.POST.get('dat')
                #devo vedere se ci sono delle aliquote da salvare per quella collezione
                for tipialiq in listaaliq:
                    if len(listaaliq[tipialiq])!=0:
                        piena=True
                        break
                
                if piena==True:
                    print 'tum',tumo
                    print 'item',item
                    collezione=Collection.objects.get(idCollectionType=tumo,itemCode=item)
                    print 'collezione',collezione
                    postovero=collezione.idSource
                    if collezione.patientCode!='' and collezione.patientCode!=None:
                        request.session['codPazienteCollezioneEsterna']=collezione.patientCode
                    request.session['collEventCollezioneEsterna']=collezione.collectionEvent
                    pr=collezione.idCollectionProtocol
            
            #se il protocollo e' della Marsoni allora devo mettere in share anche lei per le aliquote
            liscollinvestig=CollectionProtocolInvestigator.objects.filter(idCollectionProtocol=pr)
            trovato=False
            if len(liscollinvestig)!=0:
                for coll in liscollinvestig:
                    if coll.idPrincipalInvestigator.surname=='Marsoni' and coll.idPrincipalInvestigator.name=='Silvia':
                        trovato=True
                        break
            if trovato:
                listawg.append('Marsoni_WG')
            print 'listawg',listawg
            set_initWG(listawg)
                    
            if piena==True:                
                request.session['data_collezionamento_esterno']=data_coll
                request.session['operatore_collezionamento_esterno']=operatore
                #salvo gli eventuali parametri clinici per la collezione
                if request.session.has_key('dizclinicalparameter'):
                    lisparam=request.session.get('dizclinicalparameter')
                    print 'lisparam',lisparam
                    #ogni valore della lista e' un dizionario con dentro i valori del parametro clinico in questione
                    for diz in lisparam:
                        idparamclin=diz['idfeat']
                        param=ClinicalFeature.objects.get(id=idparamclin)
                        print 'param',param
                        lisval=diz['value']
                        print 'lisval',lisval
                        #lisval e' una lista con dentro i valori da salvare
                        for v in lisval:
                            print 'v',v
                            #creo l'oggetto feature per la collezione
                            clinfeat=CollectionClinicalFeature(idCollection=collezione,
                                                           idClinicalFeature=param,
                                                           value=v)
                            clinfeat.save()
                            print 'clinfeat',clinfeat
                #salvo la serie
                ser,creato=Serie.objects.get_or_create(operator=operatore,
                                                       serieDate=data_coll)
                
                for tipialiq in listaaliq:
                    for barc in listaaliq[tipialiq]:
                        for prov in listaaliq[tipialiq][barc]:
                            genid=prov['genID']
                            tipoaliq=tipialiq
                            piastra=barc
                            pos=prov['pos']
                            numpezzi=prov['qty']
                            print 'gen',genid
                            print 'tipoaliq',tipoaliq
                            print 'piastra',piastra
                            print 'pos',pos
                            print 'numpezzi',numpezzi
                            
                            g = GenealogyID(genid)
                            tumore=g.getOrigin()
                            print 'tumore',tumore
                            caso=g.getCaseCode()
                            print 'caso',caso
                            
                            t=g.getTissue()
                            tessuto_esp=TissueType.objects.get(abbreviation=t)
                            print 'tessuto',tessuto_esp.id
                            
                            #salvo il campionamento
                            campionamento,creato=SamplingEvent.objects.get_or_create(idTissueType=tessuto_esp,
                                                         idCollection=collezione,
                                                         idSource=postovero,
                                                         idSerie=ser,
                                                         samplingDate=data_coll)
                            print 'camp',campionamento
                            
                            barcode=None
                            #se sto trattando vitale, rna e snap
                            if(tipoaliq!='FF')and(tipoaliq!='OF')and(tipoaliq!='CH'):#and(tipoaliq!='PL')and(tipoaliq!='PX')and not(prov.has_key('volume')): 
                                barcodepiastraurl=piastra.replace('#','%23')
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
                                    print 'e',e
                                #se la API mi restituisce dei valori perche' gli ho dato un codice
                                #corretto per la piastra    
                                if 'children' in data:    
                                    #per ottenere il barcode data la posizione    
                                    for w in data['children']:
                                        if w['position']==pos:
                                            barcode=w['barcode']
                                            print 'barc',barcode
                                            break;
                                    ffpe='false'
                                else:
                                    #vuol dire che sto salvando una nuova provetta e quindi il barcode 
                                    #risulta essere cio' che e' salvato nella variabile piastra
                                    barcode=piastra
                                    piastra=''
                                    pos=''
                                    ffpe='true'
                                    lisbarclashub.append(barcode)
                                #valori=str(genid)+','+str(piastra)+','+str(pos)+','+str(numpezzi)+','+barcode+','+tipoaliq+',false, , '
                            #se ho ffpe o of o ch o pl o px il barcode ce l'ho gia' e non devo andare a leggerlo
                            #il barcode e' salvato nella variabile piastra
                            else:
                                barcode=piastra
                                piastra=''
                                pos=''
                                ffpe='true'
                                lisbarclashub.append(barcode)
                                                                                   
                            print 'barcode',barcode 
                            tipoaliquota= AliquotType.objects.get(abbreviation=tipoaliq)
                            print 'tipo aliquota',tipoaliq
                            if tipoaliquota.type=='Derived':
                                derivato=1
                            else:
                                derivato=0
                            a=Aliquot(barcodeID=barcode,
                                   uniqueGenealogyID=str(genid),
                                   idSamplingEvent=campionamento,
                                   idAliquotType=tipoaliquota,
                                   timesUsed=pezziusati,
                                   availability=disponibile,
                                   derived=derivato
                                   )
                            print 'a',a
                            a.save()
      
                            volu=' '
                            conc=' '
                            pur1=' '
                            pur2=' '
                            ge=' '
                            vollinea=''
                            contalinea=''
                            if numpezzi=='-':
                                numpezzi=''
                                #salvo le feature
                                if prov.has_key('vollinea') or prov.has_key('conta'):
                                    #sto salvando delle linee cellulari
                                    #se ho il volume
                                    if prov.has_key('vollinea'):
                                        vollinea=prov['vollinea']
                                        featvol=Feature.objects.filter(Q(idAliquotType=tipoaliquota)&Q(name='Volume'))
                                        if len(featvol)!=0:
                                            aliqfeaturevol=AliquotFeature(idAliquot=a,
                                                                   idFeature=featvol[0],
                                                                   value=vollinea)
                                            aliqfeaturevol.save()
                                            print 'featu volume',aliqfeaturevol
                                    #se ho la conta
                                    if prov.has_key('conta'):
                                        contalinea=prov['conta']
                                        featconta=Feature.objects.filter(Q(idAliquotType=tipoaliquota)&Q(name='Count'))
                                        if len(featconta)!=0:
                                            aliqfeaturevol=AliquotFeature(idAliquot=a,
                                                                   idFeature=featconta[0],
                                                                   value=contalinea)
                                            aliqfeaturevol.save()
                                            print 'featu conta',aliqfeaturevol
                                else:
                                    if prov.has_key('volume'):
                                        volu=prov['volume']
                                    else:
                                        volu=-1
                                    #entra qui anche se e' un plasma, quindi non ha il volume originale
                                    featvol=Feature.objects.filter(Q(idAliquotType=tipoaliquota)&Q(name='Volume'))
                                    if len(featvol)!=0:
                                        aliqfeaturevol=AliquotFeature(idAliquot=a,
                                                               idFeature=featvol[0],
                                                               value=volu)
                                        aliqfeaturevol.save()
                                    
                                    featvol=Feature.objects.filter(Q(idAliquotType=tipoaliquota)&Q(name='OriginalVolume'))
                                    if len(featvol)!=0:
                                        aliqfeaturevol=AliquotFeature(idAliquot=a,
                                                               idFeature=featvol[0],
                                                               value=volu)
                                        aliqfeaturevol.save()
                                        print 'featu volume',aliqfeaturevol
                                        
                                    if prov.has_key('conc'):
                                        conc=prov['conc']
                                    else:
                                        conc=-1
                                        
                                    featconc=Feature.objects.filter(Q(idAliquotType=tipoaliquota)&Q(name='Concentration'))
                                    if len(featconc)!=0:
                                        aliqfeatureconc=AliquotFeature(idAliquot=a,
                                                               idFeature=featconc[0],
                                                               value=conc)
                                        aliqfeatureconc.save()
    
                                    featconc=Feature.objects.filter(Q(idAliquotType=tipoaliquota)&Q(name='OriginalConcentration'))
                                    if len(featconc)!=0:
                                        aliqfeatureconc=AliquotFeature(idAliquot=a,
                                                               idFeature=featconc[0],
                                                               value=conc)
                                        aliqfeatureconc.save()
                                        print 'feat conc',aliqfeatureconc

                                if prov.has_key('pur1') or prov.has_key('pur2') or prov.has_key('ge'):
                                    #devo creare il qual sched se non e' gia' presente
                                    qualsched,creato=QualitySchedule.objects.get_or_create(scheduleDate=data_coll,
                                                                                    operator=operatore)
                                    #prendo il primo qualityprotocol disponibile per quel tipo di aliquota, tanto e' un valore fittizio
                                    qualprot=QualityProtocol.objects.filter(idAliquotType=tipoaliquota)[0]
                                    #creo il quality event
                                    qualev,creato=QualityEvent.objects.get_or_create(idQualityProtocol=qualprot,
                                                                                     idQualitySchedule=qualsched,
                                                                                     idAliquot=a,
                                                                                     misurationDate=data_coll,
                                                                                     insertionDate=data_coll,
                                                                                     operator=operatore)
                                    if prov.has_key('pur1'):
                                        misura=Measure.objects.get(name='purity',measureUnit='260/280')
                                        pur1=prov['pur1']
                                        misevent=MeasurementEvent(idMeasure=misura,
                                                                  idQualityEvent=qualev,
                                                                  value=pur1)
                                        misevent.save()
                                        print 'misevent',misevent
                                    if prov.has_key('pur2'):
                                        misura=Measure.objects.get(name='purity',measureUnit='260/230')
                                        pur2=prov['pur2']
                                        misevent=MeasurementEvent(idMeasure=misura,
                                                                  idQualityEvent=qualev,
                                                                  value=pur2)
                                        misevent.save()
                                        print 'misevent',misevent
                                    if prov.has_key('ge'):
                                        misura=Measure.objects.get(name='GE/Vex',measureUnit='GE/ml')
                                        ge=prov['ge']
                                        misevent=MeasurementEvent(idMeasure=misura,
                                                                  idQualityEvent=qualev,
                                                                  value=ge)
                                        misevent.save()
                                        print 'misevent',misevent
                            #salvo i campioni normali
                            else:
                                #salvo il numero di pezzi
                                fea=Feature.objects.get(Q(idAliquotType=tipoaliquota)&Q(name='NumberOfPieces'))
                                aliqfeature=AliquotFeature(idAliquot=a,
                                                           idFeature=fea,
                                                           value=numpezzi)
                                aliqfeature.save()
                                print 'aliq',aliqfeature
                            if volu==-1:
                                volu=''
                            if conc==-1:
                                conc=''
                            valori=genid+','+str(piastra)+','+str(pos)+','+str(numpezzi)+','+barcode+','+tipoaliq+','+ffpe+','+str(volu)+','+str(conc)+','+pur1+','+pur2+','+ge+','+str(data_coll)+','+vollinea+','+contalinea
                            listaal.append(valori)
                            print 'listaaliq',listaal
                                
                request,errore=SalvaInStorage(listaal,request)
                print 'err', errore   
                if errore==True:
                    transaction.rollback()
                    variables = RequestContext(request, {'errore':errore})
                    return render_to_response('tissue2/index.html',variables)
                #devo fare gia' il commit perche' devo passare al modulo clinico la collezione, che deve gia' esistere sul grafo
                #altrimenti non si riesce a collegare il nodo collezione con il consenso informato
                transaction.commit()
                #faccio la API al modulo clinico per dirgli di salvare            
                errore=saveInClinicalModule(lisexist,lisnotexist,[workingGroup],operatore,lislocalid)
                if errore:
                    raise Exception
                    
            request.session['aliquotEsterne']=listaal   
            transaction.commit()
            return HttpResponse()
        except Exception, e:
            transaction.rollback()
            print 'except',e
            errore=True
            variables = RequestContext(request, {'errore':errore})
            return render_to_response('tissue2/index.html',variables)
        
#funzione per creare il PDF per le aliquote inserite
@laslogin_required
@login_required
#@user_passes_test(lambda u: u.has_perm('tissue.can_view_collaboration_collection'),login_url='/tissue/error/')
@permission_decorator('tissue.can_view_BBM_collaboration_collection')
def createPDFExtern(request):
    if request.session.get('aliquotEsterne'):
        lista=[]
        lista,intest,l,inte=LastPartExternAliquot(request,'s')
        data=request.session.get('data_collezionamento_esterno')
        print 'data',data
        ddd=data.split('-')
        print 'dd',ddd[0]
        print ddd[1]
        print ddd[2]
        data_def=datetime.date(int(ddd[0]),int(ddd[1]),int(ddd[2]))
        operatore=request.session.get('operatore_collezionamento_esterno')
        collevent=request.session.get('collEventCollezioneEsterna')
        if request.session.has_key('codPazienteCollezioneEsterna'):
            codpaz=request.session.get('codPazienteCollezioneEsterna')
        else:
            codpaz=''
        file_data = render_to_string('tissue2/pdf_report.html', {'list_report': lista,'intest':intest,'data_coll':data_def,'operatore':operatore,'collevent':collevent,'paziente':codpaz}, RequestContext(request))
        myfile = cStringIO.StringIO()
        pisa.CreatePDF(file_data, myfile)
        myfile.seek(0)
        response =  HttpResponse(myfile, mimetype='application/pdf')
        response['Content-Disposition'] = 'attachment; filename=Collected_Aliquots.pdf'
        #response=PDFMaker(request, 'Collected_Aliquots.pdf', 'tissue2/pdf_report.html', lista)
        return response
    else:
        return HttpResponseRedirect(reverse('tissue.views.index'))

#funzione per creare il CSV per le aliquote inserite
@laslogin_required
@login_required
#@user_passes_test(lambda u: u.has_perm('tissue.can_view_collaboration_collection'),login_url='/tissue/error/')
@permission_decorator('tissue.can_view_BBM_collaboration_collection')
def createCSVExtern(request):
    if request.session.get('aliquotEsterne'):
        #aliquots = request.session.get('aliquots') 
        response = HttpResponse(mimetype='text/csv')
        response['Content-Disposition'] = 'attachment; filename=Collected_Aliquots.csv'
        writer = csv.writer(response)
        lista,intest,listacsv,intestcsv=LastPartExternAliquot(request,'s')
        writer.writerow([intestcsv[0]])
        for i in range(0,len(listacsv)):
            #csvString=str(i+1)+";"+str(val[0])+";"+str(val[3])+";"+val[1]+";"+val[2]
            writer.writerow([listacsv[i]])
        return response 
    else:
        return HttpResponseRedirect(reverse('tissue.views.index'))
    
@laslogin_required
@login_required
#@user_passes_test(lambda u: u.has_perm('tissue.can_view_collaboration_collection'),login_url=settings.BASE_URL+'/tissue/error/')
@permission_decorator('tissue.can_view_BBM_collaboration_collection')
def CellLineNewCollection(request):
    try:
        form=CellLineNewCollectionPart1()
        if request.method=='POST':
            print request.POST
            print request.FILES
            a=SchemiPiastre()
        
            formfinale=CellLineNewCollectionPart1(request.POST)
            print 'form',formfinale.is_valid()
            if formfinale.is_valid():
                nomelinea=request.POST.get('name')
                #metto nella sessione gli altri dati che salvero' come clinical feature
                request.session['MaterialTransferAgreement']=request.POST.get('mta')
                request.session['LotNumberCell']=request.POST.get('lot')
                request.session['Mycoplasma']=request.POST.get('myco')
                
                workgr=request.POST.get('workgr')
                print 'worgr',workgr
                
                data_coll=request.POST.get('date')
                
                sorg=''
                tess=''
                vett=''
                #devo fare la chiamata al modulo per vedere se la linea e' gia' presente o no
                servizio=WebService.objects.get(name='Annotation')
                
                urlcell=Urls.objects.get(idWebService=servizio).url
                #faccio la get al modulo dandogli la lista con dentro i dizionari
                indir=urlcell+'/api/cellLineFromName/?name='+nomelinea
                req = urllib2.Request(indir, headers={"workingGroups" : get_WG_string()})
                u = urllib2.urlopen(req)
                #u = urllib2.urlopen(indir)
                
                da = u.read()
                data=json.loads(da)
                #print 'u.read',u.read()
                print 'data',data
                if len(data)!=0:
                    trovato=False
                    for val in data:
                        print 'val',val
                        if val['name']==nomelinea:
                            res=val['id']
                            trovato=True
                            break
                    if not trovato:
                        res='-1'
                    print 'res',res
                else:
                    res='-1'
                    print 'res',res
                
                #in res ho l'id della linea cellulare. Devo vedere se una collezione ha gia'quell'id come feature
                feat=ClinicalFeature.objects.get(name='idCellLine')
                lisfeat=CollectionClinicalFeature.objects.filter(idClinicalFeature=feat,value=res)
                print 'lisfeat',lisfeat
                                        
                if len(lisfeat)==0:
                    #vuol dire che devo creare un nuovo caso perche' quella linea e' nuova
                    #mi ritorna l'abbreviazione del tumore
                    tumore=CollectionType.objects.get(id=request.POST['Tumor_Type'])
                    casuale=False
                    if 'randomize' in request.POST:
                        casuale=True 
                    
                    val=LasHubNewCase(request, casuale, tumore.abbreviation)
                    print 'r.text',val
                    
                    caso=NewCase(val, casuale, tumore)                    
                    nomefile=tumore.abbreviation+caso+'_'+str(data_coll)
                    
                else:
                    coll=lisfeat[0].idCollection
                    caso=coll.itemCode
                    tumore=coll.idCollectionType
                    sorg=coll.idSource.id
                    lsamp=SamplingEvent.objects.filter(idCollection=coll)
                    #prendo il primo sampling event, tanto il tessuto della linea e' uguale per tutti i sampl
                    tess=lsamp[0].idTissueType.id
                    disable_graph()
                    laliq=Aliquot.objects.filter(idSamplingEvent=lsamp[0])
                    enable_graph()
                    #prendo la prima aliq, tanto il vettore e' uguale per tutte le altre
                    genid=GenealogyID(laliq[0].uniqueGenealogyID)
                    vett=genid.getSampleVector()
                    #devo disambiguare il nome file contando quanti samplingevent ha gia' quel caso e aggiungendolo in fondo
                    lissamp=SamplingEvent.objects.filter(idCollection=coll)
                    nomefile=tumore.abbreviation+caso+'_'+str(data_coll)+'_'+str(len(lissamp))
                
                print 'sorg',sorg
                print 'tess',tess
                print 'vett',vett
                print 'caso',caso
                geniniz=tumore.abbreviation+caso
                print 'geniniz',geniniz
                form2=CellLineNewCollectionPart2()
                
                #salvo i due file, se ci sono, in una cartella temporanea, perche' poi quando salvero' 
                #li trasferiro' nel repository
                if 'file_datasheet'in request.FILES or 'file_invoice' in request.FILES:
                    print 'TEMP_URL',settings.TEMP_URL
                    print 'basedir',settings.BASEDIR
                    print 'req',request.FILES.getlist('file_datasheet')
                    archiveFile = tarfile.open(os.path.join(settings.TEMP_URL,'CellLine_' + nomefile +'.tar.gz'),mode='w:gz')
                    print '2'
                    listFiles = [os.path.join(settings.TEMP_URL, 'CellLine_' + nomefile + '.tar.gz')]
                    listemp=[]
                    if 'file_datasheet'in request.FILES and len(request.FILES['file_datasheet']) > 0:
                        listemp.append(request.FILES.get('file_datasheet'))
                    if 'file_invoice' in request.FILES and len(request.FILES['file_invoice']) > 0:
                        listemp.append(request.FILES.get('file_invoice'))
                    print 'listemp',listemp    
                    for uploaded_file in listemp:
                        destination = handle_uploaded_file(uploaded_file,settings.TEMP_URL)
                        archiveFile.add(destination, arcname=uploaded_file.name)
                        listFiles.append(destination)
                    archiveFile.close()
                    request.session['nomefilecell']=nomefile
                    request.session['listfilecell']=listFiles
                    print 'listfiles',listFiles
                else:
                    request.session['nomefilecell']=''
                    request.session['listfilecell']=''
                
                variables = RequestContext(request, {'form': formfinale,'form2':form2,'a':a,'gen':geniniz,'caso':caso,'sorg':sorg,'tess':tess,'vett':vett,'res':res,'tumour':tumore.id,'linea':nomelinea,'wgroup':workgr})
                return render_to_response('tissue2/collection/cell_line.html',variables)
            else:
                variables = RequestContext(request, {'form':formfinale})
                return render_to_response('tissue2/collection/cell_line.html',variables)
        else:
            variables = RequestContext(request, {'form':form})
            return render_to_response('tissue2/collection/cell_line.html',variables)
    except Exception, e:
        print 'except',e
        errore=True
        variables = RequestContext(request, {'errore':errore})
        return render_to_response('tissue2/index.html',variables)
    
#per salvare nuove linee cellulari
@transaction.commit_on_success
@laslogin_required
@login_required
#@user_passes_test(lambda u: u.has_perm('tissue.can_view_collaboration_collection'),login_url=settings.BASE_URL+'/tissue/error/')
@permission_decorator('tissue.can_view_BBM_collaboration_collection')
def CellLineSave(request):
    if request.method=='POST':
        print request.POST
        try:
            listaal=[]
            lisbarclashub=[]
            piena=False
            lisexists=[]
            lisnotexists=[]
            lislocalid=[]
            pezziusati=0
            disponibile=1
            derivato=0
            if 'final' in request.POST:
                #la n indica che non faccio un pdf
                lista,intest,l,inte=LastPartCellLine(request,'n')
                variables = RequestContext(request,{'fine':True,'aliq':lista,'intest':intest})
                return render_to_response('tissue2/collection/cell_line.html',variables)
            
            crea=request.POST.get('crea')
            tum=request.POST.get('tum')
            tumo=CollectionType.objects.get(id=tum)
            #e' il caso gia' con gli zeri davanti
            item=request.POST.get('itemcode')
            #mi da' l'operatore
            operatore=request.POST.get('operatore')
            listaaliq=json.loads(request.POST.get('dati'))
            data_coll=request.POST.get('dat')
            
            #puo' essere -1 o un numero a seconda che esista gia' la linea nel DB generale
            idlinea=request.POST.get('cellid')
            #sto salvando una nuova collezione
            nomelinea=request.POST.get('linea')
            
            workingGroup=request.POST.get('wg')
            print 'work group',workingGroup
            listawg=[workingGroup]
            
            if crea=='true':
                protcoll=CollectionProtocol.objects.get(project='CellLines')
                posto=request.POST.get('sorg')
                postovero=Source.objects.get(id=posto)
                #restituisce la collezione e un'indicazione per sapere se l'oggetto c'era gia' 
                #o se e' stato creato apposta, che salvo in creato
                collezione,creato=Collection.objects.get_or_create(itemCode=item,
                             idSource=postovero,
                             idCollectionType=tumo,
                             #nel collevent metto il nome della linea
                             collectionEvent=nomelinea,
                             idCollectionProtocol=protcoll)
                print 'collezione',collezione
                if creato:
                    #solo se ho creato una nuova collezione comunico al modulo clinico le informazioni
                    handler=CheckPatientHandler()
                    valore=handler.read(request, nomelinea, collezione.patientCode, collezione.idSource.id,protcoll.id)
                    print 'val',valore
                    #nel valore c'e' scritto se il consenso esiste o no
                    ev=valore['event']
                    if ev=='new':
                        #vuol dire che l'ic non esiste ancora
                        diztemp={'caso':collezione.itemCode,'tum':collezione.idCollectionType.abbreviation,'consenso':collezione.collectionEvent,'progetto':collezione.idCollectionProtocol.project,'source':collezione.idSource.internalName,'wg':[workingGroup],'operator':operatore}
                        #il paziente non ci sara' mai e quindi e' sempre una stringa vuota
                        diztemp['paziente']=''
                        lisnotexists.append(diztemp)
                    else:
                        lisexists.append({'caso':collezione.itemCode,'tum':collezione.idCollectionType.abbreviation,'consenso':collezione.collectionEvent,'progetto':collezione.idCollectionProtocol.project,'wg':[workingGroup]})
                        localid=valore['idgrafo']
                        lislocalid.append(localid)
            else:
                print 'tum',tumo
                print 'item',item
                collezione=Collection.objects.get(idCollectionType=tumo,itemCode=item)
                print 'collezione',collezione
                postovero=collezione.idSource
                protcoll=collezione.idCollectionProtocol
              
            #se il protocollo e' della Marsoni allora devo mettere in share anche lei per le aliquote
            liscollinvestig=CollectionProtocolInvestigator.objects.filter(idCollectionProtocol=protcoll)
            trovato=False
            if len(liscollinvestig)!=0:
                for coll in liscollinvestig:
                    if coll.idPrincipalInvestigator.surname=='Marsoni' and coll.idPrincipalInvestigator.name=='Silvia':
                        trovato=True
                        break
            if trovato:
                listawg.append('Marsoni_WG')
            print 'listawg',listawg
            set_initWG(listawg)
            
            #salvo la serie
            ser,creato=Serie.objects.get_or_create(operator=operatore,
                                                   serieDate=data_coll)
            
            creatosamp=False
            campionamento=None
            for tipialiq in listaaliq:
                for barc in listaaliq[tipialiq]:
                    for prov in listaaliq[tipialiq][barc]:
                        genid=prov['genID']
                        tipoaliq=tipialiq
                        piastra=barc
                        pos=prov['pos']
                        print 'gen',genid
                        print 'tipoaliq',tipoaliq
                        print 'piastra',piastra
                        print 'pos',pos
                        
                        g = GenealogyID(genid)
                        tumore=g.getOrigin()
                        print 'tumore',tumore
                        caso=g.getCaseCode()
                        print 'caso',caso
                        
                        t=g.getTissue()
                        tessuto_esp=TissueType.objects.get(abbreviation=t)
                        print 'tessuto',tessuto_esp.id
                        
                        if not creatosamp:
                            #salvo il campionamento solo una volta per tutte le aliq
                            #non posso portarlo fuori dal ciclo perche' non saprei quale 
                            #sarebbe il tessuto
                            campionamento=SamplingEvent(idTissueType=tessuto_esp,
                                                         idCollection=collezione,
                                                         idSource=postovero,
                                                         idSerie=ser,
                                                         samplingDate=data_coll)
                            campionamento.save()
                            creatosamp=True
                            print 'camp',campionamento
                        
                        barcode=None
                         
                        barcodepiastraurl=piastra.replace('#','%23')
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
                            print 'e',e
                        #se la API mi restituisce dei valori perche' gli ho dato un codice
                        #corretto per la piastra    
                        if 'children' in data:    
                            #per ottenere il barcode data la posizione    
                            for w in data['children']:
                                if w['position']==pos:
                                    barcode=w['barcode']
                                    print 'barc',barcode
                                    break;
                            ffpe='false'
                        else:
                            #vuol dire che sto salvando una nuova provetta e quindi il barcode 
                            #risulta essere cio' che e' salvato nella variabile piastra
                            barcode=piastra
                            piastra=''
                            pos=''
                            ffpe='true'
                            lisbarclashub.append(barcode)
                            
                                                                               
                        print 'barcode',barcode 
                        tipoaliquota= AliquotType.objects.get(abbreviation=tipoaliq)

                        a=Aliquot(barcodeID=barcode,
                               uniqueGenealogyID=str(genid),
                               idSamplingEvent=campionamento,
                               idAliquotType=tipoaliquota,
                               timesUsed=pezziusati,
                               availability=disponibile,
                               derived=derivato
                               )
                        print 'a',a
                        a.save()
  
                        volu=' '
                        conta=' '
                        
                        #salvo le feature
                        if prov.has_key('volume'):
                            volu=prov['volume']
                            
                            featvol=Feature.objects.get(Q(idAliquotType=tipoaliquota)&Q(name='Volume'))
                            aliqfeaturevol=AliquotFeature(idAliquot=a,
                                                       idFeature=featvol,
                                                       value=volu)
                            aliqfeaturevol.save()                                   
                            print 'featu volume',aliqfeaturevol
                            
                        if prov.has_key('conta'):
                            conta=prov['conta']
                            featcont=Feature.objects.get(Q(idAliquotType=tipoaliquota)&Q(name='Count'))
                            aliqfeaturecont=AliquotFeature(idAliquot=a,
                                                       idFeature=featcont,
                                                       value=conta)
                            aliqfeaturecont.save()
                            print 'feat conc',aliqfeaturecont
                        
                        valori=genid+','+str(piastra)+','+str(pos)+',,'+barcode+','+tipoaliq+','+ffpe+','+volu+','+conta+',,,,'+str(data_coll)
                        listaal.append(valori)
                        print 'listaaliq',listaal
                                
            
            
            if idlinea=='-1':
                #vuol dire che la linea non c'e' nel DB delle annotazioni, quindi la devo creare
                #facendo una post al modulo
                servizio=WebService.objects.get(name='Annotation')
                
                urlcell=Urls.objects.get(idWebService=servizio).url
                #faccio la post al modulo dandogli la lista con dentro i dizionari
                indir=urlcell+'/api/newCellLine/'
                val2={'name':nomelinea}
                print 'url',url
                data1 = urllib.urlencode(val2)
                req = urllib2.Request(indir,data=data1, headers={"workingGroups" : get_WG_string()})
                u = urllib2.urlopen(req)
                #u = urllib2.urlopen(indir, data1)
                result =  json.loads(u.read())
                res=result['id']
            else:
                res=idlinea
            
            if crea=='true':    
                #salvo la feature per la collezione solo se l'ho creata
                feat=ClinicalFeature.objects.get(name='idCellLine')
                clinfeat=CollectionClinicalFeature(idCollection=collezione,
                                               idClinicalFeature=feat,
                                               value=res)
                clinfeat.save()
            
            #invece queste feature non sono della collezione ma del sampling
            mta=request.session['MaterialTransferAgreement']
            if mta!='':
                feat=ClinicalFeature.objects.get(name='MTA')
                clinfeat=CollectionClinicalFeature(idSamplingEvent=campionamento,
                                                   idClinicalFeature=feat,
                                                   value=mta)
                clinfeat.save()
                
            lotto=request.session['LotNumberCell']
            if lotto!='':
                feat=ClinicalFeature.objects.get(name='LotNumber')
                clinfeat=CollectionClinicalFeature(idSamplingEvent=campionamento,
                                                   idClinicalFeature=feat,
                                                   value=lotto)
                clinfeat.save()
                
            mico=request.session['Mycoplasma']
            print 'mico',mico
            if mico!=None:
                feat=ClinicalFeature.objects.get(name='MycoplasmaPositive')
                clinfeat=CollectionClinicalFeature(idSamplingEvent=campionamento,
                                                   idClinicalFeature=feat,
                                                   value=mico)
                clinfeat.save()
                
            nomefile=request.session.get('nomefilecell')
            listFiles=request.session.get('listfilecell')
            if nomefile!='' and listFiles!='':
                responseUpload = uploadRepFile({'operator':request.user.username}, os.path.join(TEMP_URL, 'CellLine_' + nomefile + '.tar.gz'))
                print 'response upload',responseUpload
                if responseUpload == 'Fail':
                    transaction.rollback()
                    raise Exception
                remove_uploaded_files(listFiles)      
                feat=ClinicalFeature.objects.get(name='RelatedFile')
                clinfeat=CollectionClinicalFeature(idSamplingEvent=campionamento,
                                                   idClinicalFeature=feat,
                                                   value=responseUpload)
                clinfeat.save()
            
            request,errore=SalvaInStorage(listaal,request)  
            print 'err', errore   
            if errore==True:
                transaction.rollback()
                variables = RequestContext(request, {'errore':errore})
                return render_to_response('tissue2/index.html',variables)
            #comunico al LASHub che quella collezione e' stata salvata e quei barcode sono stati utilizzati
            listacoll=[]
            iniziogen=collezione.idCollectionType.abbreviation+collezione.itemCode
            listacoll.append(iniziogen)
            print 'listacoll',listacoll
            
            #prefisso= 'https://' if settings.LAS_AUTH_USE_HTTPS else 'http://'
            #address=request.get_host()+settings.HOST_URL
            #indir=prefisso+address
            indir=settings.DOMAIN_URL+settings.HOST_URL
            url = indir + '/clientHUB/saveAndFinalize/'
            print 'url',url
            values = {'typeO' : 'aliquot', 'listO': str(listacoll)}
            requests.post(url, data=values, verify=False, headers={"workingGroups" : get_WG_string()})
            values2 = {'typeO' : 'container', 'listO': str(lisbarclashub)}
            requests.post(url, data=values2, verify=False, headers={"workingGroups" : get_WG_string()})
                    
            request.session['cellLineNuove']=listaal   
            transaction.commit()
            
            errore=saveInClinicalModule(lisexists,lisnotexists,[workingGroup],operatore,lislocalid)
            if errore:
                raise Exception
            
            return HttpResponse()
        except Exception, e:
            transaction.rollback()
            print 'except',e
            errore=True
            variables = RequestContext(request, {'errore':errore})
            return render_to_response('tissue2/index.html',variables)

#per gestire il menu' iniziale del batch in cui si puo' scegliere tra collezione fresh o archive
@laslogin_required
@login_required
@permission_decorator('tissue.can_view_BBM_collaboration_collection')
def BatchStart(request):
    forminiziale=BatchFormInit()
    if request.method=='POST':
        print request.POST
        if 'tipi' in request.POST:
            forminiziale = BatchFormInit(request.POST)
            tipo=request.POST.get('tipi')
            print tipo
            if tipo=='0':
                #sto facendo un batch per la biopsia liquida classica
                print 'tipo0'
                variables = RequestContext(request, {'secondo':True,'tipo':tipo})
                return render_to_response('tissue2/collection/batch.html',variables)
            elif tipo=='1':
                #batch per archive sample che prevede la possibilita' di inserire tutti i campioni
                print 'tipo1'
                variables = RequestContext(request, {'secondo':True,'tipo':tipo})
                return render_to_response('tissue2/collection/batch.html',variables)        
    else:
        forminiziale = BatchFormInit()
    variables = RequestContext(request, {'form':forminiziale,'primo':True})
    return render_to_response('tissue2/collection/batch.html',variables)

#per gestire il menu' di caricamento di piu' campioni in contemporanea
@laslogin_required
@login_required
#@user_passes_test(lambda u: u.has_perm('tissue.can_view_collaboration_collection'),login_url=settings.BASE_URL+'/tissue/error/')
@permission_decorator('tissue.can_view_BBM_collaboration_collection')
def BatchCollection(request):
    try:
        if request.method=='POST':
            print request.POST
            print request.FILES            
            if 'file_batch' in request.FILES:
                workgr=request.POST.get('workgr')
                if workgr!=None:
                    request.session['workgrBatchCollection']=workgr
                fil=request.FILES.get('file_batch')
                linee=fil.readlines()
                #la chiave e' consenso+paziente, mentre il valore e' una lista con gli indici delle righe che 
                #hanno quelle caratteristiche
                diztot={}
                #dizionario per memorizzare i consensi informati. La chiave e' il paziente e il valore e' il consenso
                #dizconsensi={}
                #dizpazienti={}
                #dizionario per memorizzare il contatore dei campioni di un certo tipo. La chiave e' caso+tipoaliq
                dizcontatori={}
                #dizionario con chiave il barc e valore piastra|posizione|tipoaliq
                dizprovette={}
                #diz con chiave consenso|prog e valore la risposta della API al modulo clinico
                #dizmoduloclinico={}
                #lista per evitare posizioni duplicate all'interno del file stesso.
                listaposdupl=[]
                lisgenerale=[]
                #per fare in modo di non accedere al DB ad ogni riga. Prima guardo se il valore e' gia' in lista
                listum=[]
                lissorg=[]
                lisprot=[]
                listess=[]
                lisbarc=[]
                lisparam=[]
                dizioclinparam={}
                lisvisualizz=[]
                
                lparam=ClinicalFeature.objects.all()
                
                for param in lparam:
                    if param.measureUnit=='':
                        lisparam.append(param.name)
                    else:
                        #concateno anche l'unita' di misura
                        lisparam.append(param.name+'('+param.measureUnit+')')
                    
                val_primariga=linee[0].strip().split('\t')
                k=0
                for titolo in val_primariga:
                    if titolo!='' :
                        if titolo in lisparam:
                            dizioclinparam[titolo]=k
                        k=k+1
                val_primariga.insert(0,'GenealogyID')
                        
                print 'dizio',dizioclinparam
                #la prima riga contiene le intestazioni delle colonne e quindi la salto
                #faccio prima un controllo totale per vedere la correttezza delle varie informazioni
                for i in range(1,len(linee)):
                    if linee[i]!='\n':
                        #per salvare tutti i dati del file e darli alla pagina html per visualizzarli
                        dizgenerale={}
                        #lista per inserire i valori e visualizzarli nell'html
                        lisv=[]
                        val=linee[i].split('\t')
                        print 'val',val
                       
                        #val[0] e' il tumore
                        tum=None
                        for t in listum:
                            if t.longName.lower()==val[0].strip().lower():
                                tum=t
                                break
                        if tum==None:
                            ltum=CollectionType.objects.filter(longName=val[0].strip())
                            if len(ltum)==0:
                                raise ErrorDerived('Error in line '+str(i+1)+': collection type unknown')
                            else:
                                tum=ltum[0]
                                listum.append(tum)
                        dizgenerale[val_primariga[1]]=tum.longName
                        lisv.append(tum.longName)
                        
                        #val[5] e' il protocollo di studio
                        prot=None
                        print 'val[5]',val[5]
                        for s in lisprot:
                            if s.name.lower()==val[5].strip().lower():
                                prot=s
                                break
                        if prot==None:
                            lprot=CollectionProtocol.objects.filter(name=val[5].strip())
                            print 'lprot',lprot
                            if len(lprot)==0:
                                raise ErrorDerived('Error in line '+str(i+1)+': study protocol unknown')
                            else:
                                prot=lprot[0]
                                lisprot.append(prot)
                        print 'prot',prot
                        
                        #val[1] e' la sorgente
                        sorg=None
                        for s in lissorg:
                            if s.name.lower()==val[1].strip().lower():
                                sorg=s
                                break
                        if sorg==None:
                            handler=GetHospital()
                            valore=handler.read(request,prot.id)
                            print 'valore',valore
                            lsorg=valore['data']
                            print 'lsorg',lsorg
                            #scandisco la lista dei posti
                            trovato=False
                            for posto in lsorg:
                                print 'posto',posto
                                #posto[0] ha l'id
                                print 'posto[1]',posto[1]
                                if posto[1].lower()==val[1].strip().lower():
                                    trovato=True
                                    break
                            if not trovato:
                                raise ErrorDerived('Error in line '+str(i+1)+': source unknown')
                            
                            sorg=Source.objects.get(name=val[1].strip(),type='Hospital')                        
                            lissorg.append(sorg)
                        print 'sorg',sorg
                        dizgenerale[val_primariga[2]]=sorg.name
                        lisv.append(sorg.name)
                        
                        #val[2] e' la data
                        data=val[2].strip()
                        dat=data.split('/')
                        if len(dat)==3:
                            datafin=dat[2]+'-'+dat[1]+'-'+dat[0]
                        else:
                            raise ErrorDerived('Incorrect data format in line '+str(i+1)+': it should be DD/MM/YYYY')
                        try:
                            datetime.datetime.strptime(datafin, '%Y-%m-%d')
                        except ValueError:
                            raise ErrorDerived('Incorrect data format in line '+str(i+1)+': it should be DD/MM/YYYY')
                        dizgenerale[val_primariga[3]]=data
                        lisv.append(data)
                        
                        #val[6] dice se creare casuale il codice del caso
                        if val[6].strip().lower()=='yes':
                            casuale=True
                        elif val[6].strip().lower()=='no':
                            casuale=False
                        else:
                            raise ErrorDerived('Error in line '+str(i+1)+': correct random code')
                        
                        print 'casuale',casuale                                                
                        
                        #val[3] e' il consenso informato
                        cons=val[3].strip()
                        
                        #val[4] e' il paziente
                        paz=val[4].strip()
                        print 'paz',paz
                        #devo decidere se dare l'errore di consenso gia' esistente, ma cosi' facendo l'utente mettera' 
                        #i _ per disambiguare e si creeranno dei consensi doppi nel grafo che in realta' si riferiscono 
                        #sempre a uno solo. Invece se non do' errore e quindi l'utente scrive un consenso uguale per tutte
                        #le collezioni, non so su cosa basarmi per decidere che e' una nuova collezione. Decido per la seconda
                        #e tolgo il _ eventualmente presente nel consenso
                        print 'cons prima',cons
                        cc=cons.split('_')
                        print 'len',len(cc)
                        if RepresentsInt(cc[len(cc)-1]):
                            cons=cc[0]+'_'
                            for jj in range(1,(len(cc)-1)):
                                print 'cc',cons
                                cons+=cc[jj]+'_'
                            cons=cons[0:len(cons)-1]
                        print 'cons dopo',cons
                        '''ch=cons+'|'+str(prot.id)
                        if ch not in dizmoduloclinico:
                            handler=CheckPatientHandler()
                            valore=handler.read(request, cons, paz, sorg.id,prot.id)
                            print 'val',valore
                            dizmoduloclinico[ch]=valore'''                        
                        
                        #if ris!='new':
                        #    raise ErrorDerived('Informed consent in line '+str(i)+' already present')
                        #non mi arriva piu' un cons creato dalla API, quindi tengo quello scritto nel file
                        '''else:                            
                            if ris!='':
                                print 'dizcons',dizconsensi
                                print 'dizpaz',dizpazienti
                                #se ris e' diverso da '' vuol dire che e' stato creato un consenso nuovo dal sistema
                                #con il numero seriale incrementale
                                consoriginale=cons
                                #se ho gia' incontrato una riga con questo paz+cons allora uso il vecchio cons
                                if dizpazienti.has_key(paz+consoriginale):
                                    cons=dizpazienti[paz+consoriginale]
                                else:
                                    if dizconsensi.has_key(paz):
                                        consenso=dizconsensi[paz].split('|')

                                        #devo aumentare di 1 il codice seriale creato
                                        cc=consenso[0].split('_')
                                        print 'cc',cc
                                        numero=cc[len(cc)-1]
                                        numero=int(numero)+1
                                        #ricostruisco la stringa
                                        consfin=''
                                        for j in range(0,len(cc)-1):
                                            consfin+=cc[j]+'_'
                                        
                                        cons=consfin+str(numero)
                                        print 'consnuovo',cons
                                    else:          
                                        cons=ris
                                
                                    dizconsensi[paz]=cons+'|'+consoriginale
                                    dizpazienti[paz+consoriginale]=cons'''

                        dizgenerale[val_primariga[4]]=cons
                        lisv.append(cons)
                        dizgenerale[val_primariga[5]]=paz
                        lisv.append(paz)
                        
                        #val[5] e' il protocollo di studio                        
                        dizgenerale[val_primariga[6]]=prot.name
                        lisv.append(prot.name)
                        lisv.append(casuale)
                        
                        #val[7] e' il tessuto
                        tess=None
                        for s in listess:
                            if s.longName.lower()==val[7].strip().lower():
                                tess=s
                                break
                        if tess==None:
                            ltess=TissueType.objects.filter(longName=val[7].strip())
                            print 'ltess',ltess
                            if len(ltess)==0:
                                raise ErrorDerived('Error in line '+str(i+1)+': tissue unknown')
                            else:
                                tess=ltess[0]
                                listess.append(tess)
                        print 'tess',tess
                        dizgenerale[val_primariga[8]]=tess.longName
                        lisv.append(tess.longName)
                        #val[8] e' il tipo
                        tip=val[8].strip().lower()
                        
                        if tip=='whole blood':
                            tipoal=AliquotType.objects.get(abbreviation='SF')
                        elif tip=='pbmc':
                            tipoal=AliquotType.objects.get(abbreviation='VT')
                        elif tip=='urine':
                            tipoal=AliquotType.objects.get(abbreviation='FR')
                        elif tip=='frozen sediments':
                            tipoal=AliquotType.objects.get(abbreviation='FS')
                        else:
                            ltipoal=AliquotType.objects.filter(longName=tip)
                            if len(ltipoal)==0:
                                raise ErrorDerived('Error in line '+str(i+1)+': aliquot type unknown')
                            else:
                                tipoal=ltipoal[0]
                        dizgenerale[val_primariga[9]]=val[8].strip().lower()
                        dizgenerale['Actual_aliquottype']=tipoal.abbreviation
                        lisv.append(val[8].strip())
                        
                        #riempio il dizionario
                        chiave=cons+'|'+paz+'|'+data
                        if diztot.has_key(chiave):
                            vv=diztot[chiave]
                            valor=vv.split('|')
                            caso=valor[0]
                            print 'caso',caso
                            tumor=valor[1]
                            print 'tum',tumor
                            if tum.abbreviation!=tumor:
                                raise ErrorDerived('Error in line '+str(i+1)+': collection type inconsistent with other lines')
                        else:
                            #guardo che non ci sia lo stesso consenso in altre righe
                            #Non mi serve piu' perche' adesso mi baso anche sulla data per vedere se fare una nuova collezione
                            '''if len(diztot.items())!=0:
                                for k,vv in diztot.items():
                                    kk=k.split('|')
                                    if cons==kk[0]:
                                        raise ErrorDerived('Informed consent in line '+str(i+1)+' already present')'''
                            #e' la prima volta che trovo questa combinazione di paz+cons+data, quindi devo creare un nuovo caso
                            valor=LasHubNewCase(request, casuale, tum.abbreviation)
                            print 'r.text',valor
                            caso=NewCase(valor, casuale, tum)
                            
                            #se il lashub non e' attivo
                            if valor=='not active' and len(diztot.items())!=0:
                                #se voglio un valore casuale allora devo andare a vedere se c'e' gia' quel valore nel dizionario
                                if casuale:
                                    trovato=False
                                    while not trovato:
                                        pres=False
                                        for k,valori in diztot.items(): 
                                            v=valori.split('|')
                                            if tum.abbreviation==v[1]:
                                                if caso==v[0]:
                                                    #vuol dire che devo ricreare un nuovo caso
                                                    caso=NewCase(valor, casuale, tum)
                                                    print 'caso nuovo',caso
                                                    pres=True
                                        #termino il ciclo while perche' non ho trovato doppioni per il codice del caso
                                        print 'pres',pres
                                        if not pres:
                                            trovato=True
                                        
                                else:
                                    cas=int(caso)
                                    #non voglio un valore casuale quindi devo aggiungere 1 al valore massimo trovato nel dizionario
                                    #pero' se non trovo niente nel dizionario, devo tenere il valore del caso restituito
                                    trovato=False
                                    for k,valori in diztot.items():
                                        v=valori.split('|')
                                        pres=False
                                        if tum.abbreviation==v[1]:
                                            trovato=True
                                            if int(v[0])>cas:
                                                cas=int(v[0])
                                                print 'caso max',cas
                                    if trovato:
                                        cas=cas+1
                                    caso=str(cas).zfill(4)

                            diztot[chiave]=str(caso)+'|'+tum.abbreviation
                        print 'diztot',diztot
                        
                        chiave2=tum.abbreviation+caso+tess.abbreviation+tipoal.abbreviation
                        if dizcontatori.has_key(chiave2):
                            contatore=dizcontatori[chiave2]
                            contatore=int(contatore)+1
                        else:
                            contatore=1
                        dizcontatori[chiave2]=contatore
                        
                        print 'caso',caso
                        
                        barc=val[9].strip()
                        if barc=='':
                            raise ErrorDerived('Error in line '+str(i+1)+': please insert barcode')
                        
                        if barc not in lisbarc:
                            lisbarc.append(barc)
                        else:
                            raise ErrorDerived('Error in line '+str(i+1)+': barcode already exists')
                        dizgenerale[val_primariga[10]]=barc
                        lisv.append(barc)
                        
                        volume=val[10].strip()
                        dizgenerale[val_primariga[11]]=volume
                        lisv.append(volume)
                        print 'vol',volume
                        if len(val)>13:
                            pezzi=val[13].strip()
                        else:
                            pezzi=''
                        print 'pezzi',pezzi
                        dizgenerale[val_primariga[14]]=pezzi
                        
                        if tip=='whole blood' or tip=='pbmc' or tip=='plasma' or tip=='pax tube' or tip=='urine' or tip=='frozen sediments':
                            #per questi tipi di campioni ha senso mettere il volume
                            if volume=='':
                                raise ErrorDerived('Error in line '+str(i+1)+': please insert volume')
                        elif tip=='snap frozen' or tip=='rnalater' or tip=='viable' or tipoal.type=='Block':
                            #per questi tipi ha senso mettere il numero di pezzi
                            if pezzi=='':
                                raise ErrorDerived('Error in line '+str(i+1)+': please insert number of pieces')
                            else:
                                if not isfloat(pezzi):
                                    raise ErrorDerived('Error in line '+str(i+1)+': number of pieces allows only digits')
                        
                        if volume!='' and not isfloat(volume):
                            raise ErrorDerived('Error in line '+str(i+1)+': volume allows only digits')
                        
                        if len(val)>11:        
                            concentr=val[11].strip()
                        else:
                            concentr=''
                        if concentr!='' and not isfloat(concentr):
                            raise ErrorDerived('Error in line '+str(i+1)+': concentration allows only digits')
                        dizgenerale[val_primariga[12]]=concentr
                        lisv.append(concentr)
                        
                        #devo vedere la conta per il PBMC
                        if len(val)>12:
                            conta=val[12].strip()
                        else:
                            conta=''
                        if tip=='pbmc':
                            #if conta=='':
                            #    raise ErrorDerived('Error in line '+str(i+1)+': please insert "count"')
                            #else:
                            if conta!='':
                                if not isfloat(conta):
                                    raise ErrorDerived('Error in line '+str(i+1)+': "count" allows only digits')
                        dizgenerale[val_primariga[13]]=conta
                        lisv.append(conta)
                        lisv.append(pezzi)
                        
                        #mi occupo della piastra e della posizione
                        if len(val)>14:
                            piastra=val[14].strip()
                        else:
                            piastra=''
                        dizgenerale[val_primariga[15]]=piastra
                        lisv.append(piastra)
                        
                        if len(val)>15:
                            pos=val[15].strip().upper()
                        else:
                            pos=''
                        dizgenerale[val_primariga[16]]=pos
                        lisv.append(pos)
                        if piastra!='' and pos=='':
                            raise ErrorDerived('Error in line '+str(i+1)+': please insert position')
                        if piastra=='' and pos!='':
                            raise ErrorDerived('Error in line '+str(i+1)+': please insert plate')
                        #solo se i due campi sono stati compilati
                        if piastra!='' and pos!='':
                            valstr=piastra+'|'+pos
                            if valstr in listaposdupl:
                                raise ErrorDerived('Error in line '+str(i+1)+': duplicated position for container '+piastra)
                            else:
                                listaposdupl.append(valstr)
                            dizprovette[barc]=piastra+'|'+pos+'|'+tipoal.abbreviation
                            
                        #mi occupo dei parametri clinici. Se c'e' un'unita' di misura, vuol dire che il valore scritto nel file deve
                        #essere un numero
                        for key,indice in dizioclinparam.items():
                            #se c'e' un'unita' di misura allora la chiave contiene la (
                            k=key.split('(')
                            print 'k',k
                            if len(k)>1:
                                valor=val[indice]
                                print 'valor',valor
                                if not isfloat(valor) and valor!='':
                                    raise ErrorDerived('Error in line '+str(i+1)+': '+key+' allows only digits')
                            #print 'len',len(val)
                            if indice+1>len(val):
                                v=''
                            else:
                                v=val[indice]
                            dizgenerale[key]=v
                        
                        #aggiungo in lista gli altri campi che mancano
                        for k in range(16,len(val_primariga)-1):
                            if k >=len(val):
                                vv=''
                            else:
                                vv=val[k]
                            lisv.append(vv)
                        
                        #devo creare il genid del campione
                        genfin=tum.abbreviation+caso+tess.abbreviation+'H0000000000'
                        contt=str(contatore).zfill(2)
                        if tipoal.abbreviation=='DNA':
                            genfin+='D'+contt+'000'
                        elif tipoal.abbreviation=='RNA':
                            genfin+='R'+contt+'000'
                        elif tipoal.abbreviation=='cDNA':
                            genfin+='R01D'+contt
                        elif tipoal.abbreviation=='cRNA':
                            genfin+='R01R'+contt
                        else:
                            genfin+=tipoal.abbreviation+contt+'00'
                        print 'genfin',genfin
                        dizgenerale[val_primariga[0]]=genfin
                        lisv.insert(0, genfin)
                        print 'dizgenerale',dizgenerale
                        
                        lisgenerale.append(dizgenerale)
                        lisvisualizz.append(lisv)
                print 'lisgenerale',lisgenerale
                #print 'dizmoduloclinico',dizmoduloclinico
                request.session['listaBatchCollection']=lisgenerale
                request.session['dizProvetteBatchCollection']=dizprovette
                #request.session['dizmoduloclinico']=dizmoduloclinico
                
                #devo vedere se i barcode sono univoci
                print 'lisbarc',lisbarc
                if len(lisbarc)!=0:
                    #faccio una richiesta allo storage per vedere se questi barc esistono gia'
                    url1 = Urls.objects.get(default = '1').url + '/api/check/presence/'
                    val1={'lista':json.dumps(lisbarc),'dizprov':json.dumps(dizprovette)}
                    print 'url1',url1
                    data = urllib.urlencode(val1)
                    req = urllib2.Request(url1,data=data, headers={"workingGroups" : get_WG_string()})
                    u = urllib2.urlopen(req)
                    #u = urllib2.urlopen(url1, data)
                    re = json.loads( u.read())
                    print 're',re
                    res=re['data']
                    print 'res',res
                    #mi faccio dare dalla API la risposta gia' confezionata
                    if res!='ok':
                        raise ErrorDerived(res)
                    else:
                        lispias=json.loads(re['piastre'])
                        request.session['listaPiastreAssentiBatchCollection']=lispias
                        strpias=''
                        for pias in lispias:
                            strpias+='"'+pias+'",'
                        piasfin=strpias[:len(strpias)-1]
                        if len(lispias)!=0:
                            #vuol dire che qualche piastra segnata nel file non c'e' nel DB, allora devo avvisare l'utente
                            variables = RequestContext(request,{'secondo':True,'parte2':True,'tipo':'0','intest':val_primariga,'listot':lisvisualizz,'listapiastre':piasfin,'lung':len(lispias),'wgroup':workgr})
                            return render_to_response('tissue2/collection/batch.html',variables)
                
            variables = RequestContext(request,{'secondo':True,'parte2':True,'tipo':'0','intest':val_primariga,'listot':lisvisualizz,'wgroup':workgr})
            return render_to_response('tissue2/collection/batch.html',variables)
        else:
            variables = RequestContext(request, {'secondo':True,'tipo':'0'})
            return render_to_response('tissue2/collection/batch.html',variables)
    except ErrorDerived as e:
        print 'My exception occurred, value:', e.value
        variables = RequestContext(request, {'secondo':True,'errore':e.value})
        return render_to_response('tissue2/collection/batch.html',variables)
    except Exception, e:
        print 'except',e
        errore=True
        variables = RequestContext(request, {'errore':errore})
        return render_to_response('tissue2/index.html',variables)

#per gestire il menu' di caricamento nel caso di collezioni di archivio per qualsiasi campione
@laslogin_required
@login_required
@permission_decorator('tissue.can_view_BBM_collaboration_collection')
def BatchArchiveCollection(request):
    try:
        if request.method=='POST':
            print request.POST
            print request.FILES
            if 'file_batch' in request.FILES:
                workgr=request.POST.get('workgr')
                if workgr!=None:
                    request.session['workgrBatchCollection']=workgr
                fil=request.FILES.get('file_batch')
                linee=fil.readlines()
                #la chiave e' consenso+paziente, mentre il valore e' una lista con gli indici delle righe che 
                #hanno quelle caratteristiche
                diztot={}
                #dizionario per memorizzare il contatore dei campioni di un certo tipo. La chiave e' caso+tipoaliq
                dizcontatori={}
                #dizionario con chiave il barc e valore piastra|posizione|tipoaliq
                dizprovette={}
                #diz con chiave consenso|prog e valore la risposta della API al modulo clinico
                #dizmoduloclinico={}
                #diz con chiave il nome delle colonne e come valore l'indice
                dizcolonne={}
                #lista per evitare posizioni duplicate all'interno del file stesso
                listaposdupl=[]
                lisgenerale=[]
                #per fare in modo di non accedere al DB ad ogni riga. Prima guardo se il valore e' gia' in lista
                listum=[]
                listess=[]
                lisbarc=[]
                dizioclinparam={}
                lisvisualizz=[]
                lisvettori=AliquotVector.objects.all()
                topolineage=re.compile('([A-Za-z0-9]{2})$')
                topopassaggio=re.compile('(\d\d)$')
                toponumero=re.compile('(\d\d\d)$')
                listesstopi=MouseTissueType.objects.all()
                
                #devo fare la chiamata al modulo clinico per avere la lista degi progetti
                #servizio=WebService.objects.get(name='Clinical')
                #urlclin=Urls.objects.get(idWebService=servizio).url
                #faccio la get al modulo
                #indir=urlclin+'/coreProject/api/project/'
                #print 'indir',indir
            
                #req = urllib2.Request(indir, headers={"workingGroups" : get_WG_string()})
                #u = urllib2.urlopen(req)
                #res = json.loads(u.read())
                #print 'res',res
                #qui ho la lista di dizionari che rappresentano ciascuno un posto ed hanno delle chiavi
                #con le varie informazioni
                #lissorg=res['places']
                #print 'lissorg',lissorg
                #lissorg=[{'internalName':'AA','name':'Candiolo'},{'internalName':'AI','name':'Mauriziano'}]
                
                #faccio la get al modulo clinico per avere la lista dei progetti
                lisprogetti=carica_protocolli_collez()
                print 'lisprog',lisprogetti
                
                val_primariga=linee[0].strip().split('\t')
                ii=0
                for col in val_primariga:
                    dizcolonne[col]=ii
                    ii+=1
                
                val_primariga.insert(0,'GenealogyID')
                
                print 'dizio',dizioclinparam
                #la prima riga contiene le intestazioni delle colonne e quindi la salto
                #faccio prima un controllo totale per vedere la correttezza delle varie informazioni
                for i in range(1,len(linee)):
                    if linee[i]!='\n':
                        #diz con chiave l'intestazione della colonna e valore il valore di quella cella letto dal file
                        dizgenerale={}
                        val=linee[i].strip().split('\t')
                        print 'val',val
                        #se nelle ultime colonne ho dei campi senza valori la lunghezza di val sara' minore di
                        #quella di val_primariga, quindi aggiungo dei campi vuoti a val
                        #-1 perche' ho aggiunto il campo per il genid
                        if len(val)<len(val_primariga)-1:
                            differenza=(len(val_primariga)-1)-len(val)
                            for hh in range(0,differenza):
                                val.append('')
                        print 'val2',val
                        if 'Collection type' in dizcolonne:
                            indice=dizcolonne['Collection type']
                            tum=None
                            for t in listum:
                                if t.longName.lower()==val[indice].strip().lower():
                                    tum=t
                                    break
                            if tum==None:
                                ltum=CollectionType.objects.filter(longName=val[indice].strip())
                                if len(ltum)==0:
                                    raise ErrorDerived('Error in line '+str(i+1)+': collection type unknown')
                                else:
                                    tum=ltum[0]
                                    listum.append(tum)
                            dizgenerale[val_primariga[indice+1]]=tum.longName
                        else:
                            raise ErrorDerived('Error: missing "Collection type" column')
                        
                        #data
                        if 'Date' in dizcolonne:
                            indice=dizcolonne['Date']
                            data=val[indice].strip()
                            dat=data.split('/')
                            if len(dat)==3:
                                datafin=dat[2]+'-'+dat[1]+'-'+dat[0]
                            else:
                                raise ErrorDerived('Incorrect data format in line '+str(i+1)+': it should be DD/MM/YYYY')
                            try:
                                datetime.datetime.strptime(datafin, '%Y-%m-%d')
                            except ValueError:
                                raise ErrorDerived('Incorrect data format in line '+str(i+1)+': it should be DD/MM/YYYY')
                            dizgenerale[val_primariga[indice+1]]=data
                        else:
                            raise ErrorDerived('Error: missing "Date" column')
                        
                        #guardo se c'e' il caso, che vuol dire che sto facendo un assegnamento ad una collezione esistente
                        if 'Case' in dizcolonne:
                            indice=dizcolonne['Case']
                            caso=val[indice].upper()
                            dizgenerale[val_primariga[indice+1]]=caso
                        else:
                            caso=''
                            dizgenerale['Case']=''
                        print 'caso',caso
                        #se c'e' il caso allora prendo la collezione in questione dal DB
                        if caso!='':
                            caso=str(caso.zfill(4))
                            print 'cc',caso
                            lcoll=Collection.objects.filter(idCollectionType=tum,itemCode=caso)
                            print 'lcoll',lcoll
                            if len(lcoll)==0:
                                raise ErrorDerived('Error in line '+str(i+1)+': collection '+tum.abbreviation+caso+' does not exist')
                            dizgenerale['actual_collection']=lcoll[0]
                            dizgenerale['Source']=''
                            dizgenerale['Random code']=''
                            dizgenerale['Study protocol']=''
                            dizgenerale['Informed consent']=''
                            dizgenerale['Patient code']=''
                            print 'dizgen',dizgenerale
                            cons=lcoll[0].collectionEvent
                            paz=lcoll[0].patientCode
                            if paz==None:
                                paz=''
                            chiave=cons+'|'+paz+'|'+data
                            print 'chiave',chiave
                            diztot[chiave]=str(caso)+'|'+tum.abbreviation
                            print 'diztot',diztot
                        else:
                            #e' il protocollo di studio
                            if 'Study protocol' in dizcolonne:
                                indice=dizcolonne['Study protocol']
                                prot=None
                                print 'val[protocol]',val[indice]                                    
                                for s in lisprogetti:
                                    #s e' una lista con idprogetto, nome esteso del progetto
                                    if s[1].lower()==val[indice].strip().lower():
                                        prot=s
                                        break
                                if prot==None:
                                    raise ErrorDerived('Error in line '+str(i+1)+': study protocol unknown')                        
                                prot=CollectionProtocol.objects.get(name=prot[1])
                                print 'prot',prot
                                dizgenerale[val_primariga[indice+1]]=prot.name
                            else:
                                raise ErrorDerived('Error: missing "Study protocol" column')
                            
                            #centro medico
                            if 'Source' in dizcolonne:
                                indice=dizcolonne['Source']
                                sorg=None
                                print 'sorg',val[indice]
                                handler=GetHospital()
                                valore=handler.read(request,prot.id)
                                print 'valore',valore
                                lsorg=valore['data']
                                print 'lsorg',lsorg
                                for posto in lsorg:
                                    #posto[0] ha l'id
                                    print 'posto[1]',posto[1]
                                    if posto[1].lower()==val[indice].strip().lower():
                                        sorg=posto
                                        break
                                if sorg==None:
                                    raise ErrorDerived('Error in line '+str(i+1)+': source unknown')
                                    
                                print 'sorg',sorg
                                dizgenerale[val_primariga[indice+1]]=sorg[1]
                            else:
                                raise ErrorDerived('Error: missing "Source" column')
                            
                            #colonna che dice se creare casuale il codice del caso
                            if 'Random code' in dizcolonne:
                                indice=dizcolonne['Random code']
                                if val[indice].strip().lower()=='yes':
                                    casuale=True
                                elif val[indice].strip().lower()=='no':
                                    casuale=False
                                else:
                                    raise ErrorDerived('Error in line '+str(i+1)+': correct random code')
                                dizgenerale[val_primariga[indice+1]]=val[indice].strip()
                                print 'casuale',casuale
                            else:
                                raise ErrorDerived('Error: missing "Random code" column')                                                                
                            
                            #e' il consenso informato
                            if 'Informed consent' in dizcolonne:
                                indice=dizcolonne['Informed consent']
                                cons=val[indice].strip()
                                dizgenerale[val_primariga[indice+1]]=cons
                            else:
                                raise ErrorDerived('Error: missing "Informed consent" column')
                            
                            #e' il paziente
                            if 'Patient code' in dizcolonne:
                                indice=dizcolonne['Patient code']
                                paz=val[indice].strip()
                                print 'paz',paz
                                dizgenerale[val_primariga[indice+1]]=paz
                            else:
                                raise ErrorDerived('Error: missing "Patient code" column')
                            #devo decidere se dare l'errore di consenso gia' esistente, ma cosi' facendo l'utente mettera' 
                            #i _ per disambiguare e si creeranno dei consensi doppi nel grafo che in realta' si riferiscono 
                            #sempre a uno solo. Invece se non do' errore e quindi l'utente scrive un consenso uguale per tutte
                            #le collezioni, non so su cosa basarmi per decidere che e' una nuova collezione. Decido per la seconda
                            #e tolgo il _ eventualmente presente nel consenso
                            print 'cons prima',cons
                            cc=cons.split('_')
                            print 'len',len(cc)
                            if RepresentsInt(cc[len(cc)-1]):                                                        
                                cons=cc[0]+'_'
                                for jj in range(1,(len(cc)-1)):
                                    print 'cc',cons
                                    cons+=cc[jj]+'_'
                                cons=cons[0:len(cons)-1]
                            print 'cons dopo',cons
                            '''ch=cons+'|'+str(prot.id)
                            if ch not in dizmoduloclinico:
                                handler=CheckPatientHandler()
                                valore=handler.read(request, cons, paz, sorg,prot.id)
                                print 'val',valore
                                dizmoduloclinico[ch]=valore'''
                        
                        #e' il tessuto
                        if 'Tissue' in dizcolonne:
                            indice=dizcolonne['Tissue']
                            tess=None
                            for s in listess:
                                if s.longName.lower()==val[indice].strip().lower():
                                    tess=s
                                    break
                            if tess==None:
                                ltess=TissueType.objects.filter(longName=val[indice].strip())
                                print 'ltess',ltess
                                if len(ltess)==0:
                                    raise ErrorDerived('Error in line '+str(i+1)+': tissue unknown')
                                else:
                                    tess=ltess[0]
                                    listess.append(tess)
                            print 'tess',tess
                            dizgenerale[val_primariga[indice+1]]=tess.longName
                        else:
                            raise ErrorDerived('Error: missing "Tissue" column')
                        
                        #e' il vettore
                        if 'Vector' in dizcolonne:
                            indice=dizcolonne['Vector']
                            vett_orig=val[indice].strip()
                            print 'vett',vett_orig
                            vettore=None
                            for vv in lisvettori:
                                if vv.name.lower()==vett_orig.lower():
                                    vettore=vv
                            if vettore==None:
                                raise ErrorDerived('Error in line '+str(i+1)+': vector unknown')
                            print 'vettore',vettore
                            dizgenerale[val_primariga[indice+1]]=vettore.name
                        else:
                            raise ErrorDerived('Error: missing "Vector" column')
                                                
                        #e' il centro del genid che, se il campione e' H, e' formato da 10 zeri
                        gencentro='H0000000'
                        tesstopo='None'
                        dizgenerale['Lineage xeno']=''
                        dizgenerale['Passage xeno']=''
                        dizgenerale['Mouse']=''
                        dizgenerale['Mouse tissue']=''
                        dizgenerale['Lineage cell line']=''
                        dizgenerale['Thawing cycles']=''
                        dizgenerale['Passage cell line']=''
                        #se il vettore e' X devo leggere anche gli altri 3 campi per costruire il gen
                        if vettore.abbreviation=='X':
                            if 'Lineage xeno' in dizcolonne:
                                indice=dizcolonne['Lineage xeno']
                                linxeno=val[indice].strip().upper()
                                print 'linxeno',linxeno
                                if not topolineage.match(linxeno):
                                    raise ErrorDerived('Error in line '+str(i+1)+': lineage field only allows letters or numbers and has to have 2 characters')
                                dizgenerale[val_primariga[indice+1]]=linxeno
                            else:
                                raise ErrorDerived('Error: missing "Lineage xeno" column')
                            
                            if 'Passage xeno' in dizcolonne:
                                indice=dizcolonne['Passage xeno']
                                passxeno=val[indice].strip()
                                if passxeno=='':
                                    raise ErrorDerived('Error in line '+str(i+1)+': insert passage')
                                passxeno=passxeno.zfill(2)
                                print 'passxeno',passxeno
                                if not topopassaggio.match(passxeno):
                                    raise ErrorDerived('Error in line '+str(i+1)+': passage allows only digits')
                                dizgenerale[val_primariga[indice+1]]=passxeno
                            else:
                                raise ErrorDerived('Error: missing "Passage xeno" column')
                            
                            if 'Mouse' in dizcolonne:
                                indice=dizcolonne['Mouse']
                                mousexeno=val[indice].strip()
                                if mousexeno=='':
                                    raise ErrorDerived('Error in line '+str(i+1)+': insert mouse number')
                                mousexeno=mousexeno.zfill(3)
                                print 'mousexeno',mousexeno
                                if not toponumero.match(mousexeno):
                                    raise ErrorDerived('Error in line '+str(i+1)+': mouse number allows only digits')
                                dizgenerale[val_primariga[indice+1]]=mousexeno
                            else:
                                raise ErrorDerived('Error: missing "Mouse" column')                            
                            
                            #e' il tess del topo
                            if 'Mouse tissue' in dizcolonne:
                                indice=dizcolonne['Mouse tissue']
                                tesstop=val[indice].strip().upper()
                                print 'tesstop',tesstop
                                tessxeno=None
                                for vv in listesstopi:
                                    if vv.abbreviation.upper()==tesstop:
                                        tessxeno=vv
                                if tessxeno==None:
                                    raise ErrorDerived('Error in line '+str(i+1)+': mouse tissue unknown')
                                dizgenerale[val_primariga[indice+1]]=tessxeno
                                tesstopo=tessxeno.id
                            else:
                                raise ErrorDerived('Error: missing "Mouse tissue" column')
                                                                
                            gencentro=vettore.abbreviation+linxeno+passxeno+mousexeno
                                                        
                        elif vettore.abbreviation=='S' or vettore.abbreviation=='A' or vettore.abbreviation=='O':
                            if 'Lineage cell line' in dizcolonne:
                                indice=dizcolonne['Lineage cell line']
                                lincell=val[indice].strip().upper()
                                print 'lincell',lincell
                                if not topolineage.match(lincell):
                                    raise ErrorDerived('Error in line '+str(i+1)+': lineage field only allows letters or numbers and has to have 2 characters')
                                dizgenerale[val_primariga[indice+1]]=lincell
                            else:
                                raise ErrorDerived('Error: missing "Lineage cell line" column')
                            
                            if 'Thawing cycles' in dizcolonne:
                                indice=dizcolonne['Thawing cycles']
                                scongcell=val[indice].strip()
                                if scongcell=='':
                                    raise ErrorDerived('Error in line '+str(i+1)+': insert thawing cycles')
                                scongcell=scongcell.zfill(2)
                                print 'scongcell',scongcell
                                if not topopassaggio.match(scongcell):
                                    raise ErrorDerived('Error in line '+str(i+1)+': thawing cycles allow only digits')
                                dizgenerale[val_primariga[indice+1]]=scongcell
                            else:
                                raise ErrorDerived('Error: missing "Thawing cycles" column')
                            
                            if 'Passage cell line' in dizcolonne:
                                indice=dizcolonne['Passage cell line']
                                passcell=val[indice].strip()
                                if passcell=='':
                                    raise ErrorDerived('Error in line '+str(i+1)+': insert passage')
                                passcell=passcell.zfill(3)
                                print 'passcell',passcell
                                if not toponumero.match(passcell):
                                    raise ErrorDerived('Error in line '+str(i+1)+': passage allows only digits')
                                dizgenerale[val_primariga[indice+1]]=passcell
                            else:
                                raise ErrorDerived('Error: missing "Passage cell line" column')
                                
                            gencentro=vettore.abbreviation+lincell+scongcell+passcell

                        print 'gencentro',gencentro
                        
                        #e' il tipo del campione
                        if 'Aliquot type' in dizcolonne:
                            indice=dizcolonne['Aliquot type']
                            tip=val[indice].strip().lower()
                            if tip=='whole blood':
                                tipoal=AliquotType.objects.get(abbreviation='SF')
                            elif tip=='pbmc':
                                tipoal=AliquotType.objects.get(abbreviation='VT')
                            elif tip=='urine':
                                tipoal=AliquotType.objects.get(abbreviation='FR')
                            elif tip=='frozen sediments':
                                tipoal=AliquotType.objects.get(abbreviation='FS')
                            else:
                                ltipoal=AliquotType.objects.filter(longName=tip)
                                if len(ltipoal)==0:
                                    raise ErrorDerived('Error in line '+str(i+1)+': aliquot type unknown')
                                else:
                                    tipoal=ltipoal[0]
                            dizgenerale[val_primariga[indice+1]]=val[indice].strip().lower()
                            dizgenerale['Actual_aliquottype']=tipoal.abbreviation
                            print 'tip',tip
                        else:
                            raise ErrorDerived('Error: missing "Aliquot type" column')
                        
                        #riempio il dizionario
                        chiave=cons+'|'+paz+'|'+data
                        if diztot.has_key(chiave):
                            vv=diztot[chiave]
                            valor=vv.split('|')
                            caso=valor[0]
                            print 'caso',caso
                            tumor=valor[1]
                            print 'tum',tumor
                            if tum.abbreviation!=tumor:
                                raise ErrorDerived('Error in line '+str(i+1)+': collection type inconsistent with other lines')
                        else:
                            #e' la prima volta che trovo questa combinazione di paz+cons+data, quindi devo creare un nuovo caso
                            valor=LasHubNewCase(request, casuale, tum.abbreviation)
                            print 'r.text',valor
                            caso=NewCase(valor, casuale, tum)
                            
                            #se il lashub non e' attivo
                            if valor=='not active' and len(diztot.items())!=0:
                                #se voglio un valore casuale allora devo andare a vedere se c'e' gia' quel valore nel dizionario
                                if casuale:
                                    trovato=False
                                    while not trovato:
                                        pres=False
                                        for k,valori in diztot.items(): 
                                            v=valori.split('|')
                                            if tum.abbreviation==v[1]:
                                                if caso==v[0]:
                                                    #vuol dire che devo ricreare un nuovo caso
                                                    caso=NewCase(valor, casuale, tum)
                                                    print 'caso nuovo',caso
                                                    pres=True
                                        #termino il ciclo while perche' non ho trovato doppioni per il codice del caso
                                        print 'pres',pres
                                        if not pres:
                                            trovato=True
                                        
                                else:
                                    cas=int(caso)
                                    #non voglio un valore casuale quindi devo aggiungere 1 al valore massimo trovato nel dizionario
                                    #pero' se non trovo niente nel dizionario, devo tenere il valore del caso restituito
                                    trovato=False
                                    for k,valori in diztot.items():
                                        v=valori.split('|')
                                        pres=False
                                        if tum.abbreviation==v[1]:
                                            trovato=True
                                            if int(v[0])>cas:
                                                cas=int(v[0])
                                                print 'caso max',cas
                                    if trovato:
                                        cas=cas+1
                                    caso=str(cas).zfill(4)

                            diztot[chiave]=str(caso)+'|'+tum.abbreviation
                        print 'diztot',diztot
                        
                        chiave2=tum.abbreviation+caso+tess.abbreviation+vettore.abbreviation+gencentro+tipoal.abbreviation
                        if dizcontatori.has_key(chiave2):
                            contatore=dizcontatori[chiave2]
                            contatore=int(contatore)+1
                        else:
                            contatore=1
                        dizcontatori[chiave2]=contatore
                        
                        print 'casodopo',caso
                        
                        if 'Tube barcode' in dizcolonne:
                            indice=dizcolonne['Tube barcode']
                            print 'indice barc',indice
                            barc=val[indice].strip()
                            print 'barc',barc
                            if barc=='':
                                raise ErrorDerived('Error in line '+str(i+1)+': please insert barcode')
                            if ' ' in barc:
                                raise ErrorDerived('Error in line '+str(i+1)+': there is a space in barcode')
                            if barc not in lisbarc:
                                lisbarc.append(barc)
                            else:
                                raise ErrorDerived('Error in line '+str(i+1)+': barcode already exists')
                            dizgenerale[val_primariga[indice+1]]=barc
                        else:
                            raise ErrorDerived('Error: missing "Tube barcode" column')
                        print 'dizgennnnn',dizgenerale
                        dizgenerale['N. of pieces']=''
                        dizgenerale['Volume(ul)']=''
                        dizgenerale['Concentration(ng/ul)']=''
                        dizgenerale['Purity(260/280)']=''
                        dizgenerale['Purity(260/230)']=''
                        dizgenerale['GE/Vex(GE/ml)']=''
                        dizgenerale['Count(cell/ml)']=''
                        if (tip=='snap frozen' or tip=='rnalater' or tip=='viable' or tipoal.type=='Block') and (vettore.abbreviation=='H' or vettore.abbreviation=='X'):
                            #per questi tipi ha senso mettere il numero di pezzi
                            if 'N. of pieces' in dizcolonne:
                                indice=dizcolonne['N. of pieces']
                                pezzi=val[indice].strip()
                                print 'pezzi',pezzi
                                if pezzi=='':
                                    raise ErrorDerived('Error in line '+str(i+1)+': please insert number of pieces')
                                else:
                                    if not isfloat(pezzi):
                                        raise ErrorDerived('Error in line '+str(i+1)+': number of pieces allows only digits')
                                dizgenerale[val_primariga[indice+1]]=pezzi
                            else:
                                raise ErrorDerived('Error: missing "N. of pieces" column')
                        #entra qui anche per le linee cellulari di tipo vitale che hanno un volume                        
                        if tip=='whole blood' or tip=='pbmc' or tip=='plasma' or tip=='pax tube' or tip=='urine' or tip=='frozen sediments' or tipoal.type=='Derived' or ((vettore.abbreviation in ['A','S''O']) and tip=='viable'):
                            #per questi tipi di campioni ha senso mettere il volume
                            #non sollevo eccezioni se non c'e' il volume perche' non e' obbligatorio
                            if 'Volume(ul)' in dizcolonne:
                                indice=dizcolonne['Volume(ul)']
                                volume=val[indice].strip()                                                                
                                print 'vol',volume
                                if volume!='' and not isfloat(volume):
                                    raise ErrorDerived('Error in line '+str(i+1)+': volume allows only digits')
                                dizgenerale[val_primariga[indice+1]]=volume                            
                                
                            if tipoal.type=='Derived':
                                #ha senso guardare se ci sono anche gli altri campi
                                if 'Concentration(ng/ul)' in dizcolonne:
                                    indice=dizcolonne['Concentration(ng/ul)']
                                    concentr=val[indice].strip().replace(',','.')
                                    if concentr!='' and not isfloat(concentr):
                                        raise ErrorDerived('Error in line '+str(i+1)+': concentration allows only digits')
                                    dizgenerale[val_primariga[indice+1]]=concentr
                                if 'Purity(260/280)' in dizcolonne:
                                    indice=dizcolonne['Purity(260/280)']
                                    pur280=val[indice].strip().replace(',','.')
                                    if pur280!='' and not isfloat(pur280):
                                        raise ErrorDerived('Error in line '+str(i+1)+': purity (260/280) allows only digits')
                                    dizgenerale[val_primariga[indice+1]]=pur280
                                if 'Purity(260/230)' in dizcolonne:
                                    indice=dizcolonne['Purity(260/230)']
                                    pur230=val[indice].strip().replace(',','.')
                                    if pur230!='' and not isfloat(pur230):
                                        raise ErrorDerived('Error in line '+str(i+1)+': purity (260/230) allows only digits')
                                    dizgenerale[val_primariga[indice+1]]=pur230
                                if 'GE/Vex(GE/ml)' in dizcolonne:
                                    indice=dizcolonne['GE/Vex(GE/ml)']
                                    ge=val[indice].strip().replace(',','.')
                                    if ge!='' and not isfloat(ge):
                                        raise ErrorDerived('Error in line '+str(i+1)+': GE/Vex allows only digits')
                                    dizgenerale[val_primariga[indice+1]]=ge
                        
                        #devo vedere la conta per il PBMC o per le linee cellulari
                        if tip=='pbmc' or ((vettore.abbreviation in ['A','S''O']) and tip=='viable') or ((vettore.abbreviation in ['A','S''O']) and tip=='snap frozen'):
                            if 'Count(cell/ml)' in dizcolonne:
                                indice=dizcolonne['Count(cell/ml)']
                                conta=val[indice].strip().replace(',','.')
                                if conta!='' and not isfloat(conta):
                                    raise ErrorDerived('Error in line '+str(i+1)+': count allows only digits')
                                dizgenerale[val_primariga[indice+1]]=conta
                        print 'dizgggg',dizgenerale
                        #mi occupo della piastra e della posizione
                        piastra=''
                        dizgenerale['Plate']=piastra
                        if 'Plate' in dizcolonne:
                            indice=dizcolonne['Plate']
                            piastra=val[indice].strip()
                            dizgenerale[val_primariga[indice+1]]=piastra
                        
                        pos=''
                        dizgenerale['Position']=pos
                        if 'Position' in dizcolonne:
                            indice=dizcolonne['Position']
                            pos=val[indice].strip().upper()
                            dizgenerale[val_primariga[indice+1]]=pos
                                                
                        if piastra!='' and pos=='':
                            raise ErrorDerived('Error in line '+str(i+1)+': please insert position')
                        if piastra=='' and pos!='':
                            raise ErrorDerived('Error in line '+str(i+1)+': please insert plate')
                        #solo se i due campi sono stati compilati
                        if piastra!='' and pos!='':
                            valstr=piastra+'|'+pos
                            if valstr in listaposdupl:
                                raise ErrorDerived('Error in line '+str(i+1)+': duplicated position for container '+piastra)
                            else:
                                listaposdupl.append(valstr)
                            dizprovette[barc]=piastra+'|'+pos+'|'+tipoal.abbreviation
                        
                        request.META['HTTP_WORKINGGROUPS']=get_WG_string()
                        #devo creare il genid del campione
                        handler=ExternNewgenidHandler()
                        print 'tesstopo',tesstopo
                        valore=handler.read(request, tum.id,caso,tess.id,gencentro,tesstopo,tipoal.id,contatore,None)
                        print 'val',valore
                        genfin=valore['gen']
                        
                        '''genfin=tum.abbreviation+caso+tess.abbreviation+'H0000000000'
                        contt=str(contatore).zfill(2)
                        if tipoal.abbreviation=='DNA':
                            genfin+='D'+contt+'000'
                        elif tipoal.abbreviation=='RNA':
                            genfin+='R'+contt+'000'
                        elif tipoal.abbreviation=='cDNA':
                            genfin+='R01D'+contt
                        elif tipoal.abbreviation=='cRNA':
                            genfin+='R01R'+contt
                        else:
                            genfin+=tipoal.abbreviation+contt+'00'
                            '''
                        print 'genfin',genfin
                        dizgenerale[val_primariga[0]]=genfin
                        print 'dizgenerale',dizgenerale
                        
                        lisgenerale.append(dizgenerale)
                        lisv=[]
                        for valori in val_primariga:
                            lisv.append(dizgenerale[valori])
                        lisvisualizz.append(lisv)
                print 'lisgenerale',lisgenerale
                #print 'dizmoduloclinico',dizmoduloclinico
                request.session['listaBatchCollection']=lisgenerale
                request.session['dizProvetteBatchCollection']=dizprovette
                #request.session['dizmoduloclinico']=dizmoduloclinico
                
                #devo vedere se i barcode sono univoci
                print 'lisbarc',lisbarc
                if len(lisbarc)!=0:
                    #faccio una richiesta allo storage per vedere se questi barc esistono gia'
                    url1 = Urls.objects.get(default = '1').url + '/api/check/presence/'
                    val1={'lista':json.dumps(lisbarc),'dizprov':json.dumps(dizprovette)}
                    print 'url1',url1
                    data = urllib.urlencode(val1)
                    req = urllib2.Request(url1,data=data, headers={"workingGroups" : get_WG_string()})
                    u = urllib2.urlopen(req)
                    #u = urllib2.urlopen(url1, data)
                    risp = json.loads( u.read())
                    print 'risp',risp
                    res=risp['data']
                    print 'res',res
                    #mi faccio dare dalla API la risposta gia' confezionata
                    if res!='ok':
                        raise ErrorDerived(res)
                    else:
                        lispias=json.loads(risp['piastre'])
                        request.session['listaPiastreAssentiBatchCollection']=lispias
                        strpias=''
                        for pias in lispias:
                            strpias+='"'+pias+'",'
                        piasfin=strpias[:len(strpias)-1]
                        if len(lispias)!=0:
                            #vuol dire che qualche piastra segnata nel file non c'e' nel DB, allora devo avvisare l'utente
                            variables = RequestContext(request,{'secondo':True,'parte2':True,'tipo':'1','intest':val_primariga,'listot':lisvisualizz,'listapiastre':piasfin,'lung':len(lispias),'wgroup':workgr})
                            return render_to_response('tissue2/collection/batch.html',variables)
                
                
            variables = RequestContext(request,{'secondo':True,'parte2':True,'tipo':'1','intest':val_primariga,'listot':lisvisualizz,'wgroup':workgr})
            return render_to_response('tissue2/collection/batch.html',variables)
        else:
            variables = RequestContext(request, {'secondo':True,'tipo':'1'})
            return render_to_response('tissue2/collection/batch.html',variables)
    except ErrorDerived as e:
        print 'My exception occurred, value:', e.value
        variables = RequestContext(request, {'secondo':True,'errore':e.value})
        return render_to_response('tissue2/collection/batch.html',variables)
    except Exception, e:
        print 'except',e
        errore=True
        variables = RequestContext(request, {'errore':errore})
        return render_to_response('tissue2/index.html',variables)
    
#per salvare le collezioni in batch
@transaction.commit_on_success
@laslogin_required
@login_required
@permission_decorator('tissue.can_view_BBM_collaboration_collection')
def BatchCollectionSave(request):
    if request.method=='POST':
        print request.POST
        try:
            workgr=request.session.get('workgrBatchCollection')
            print 'work group',workgr
            set_initWG(set([workgr]))
            operatore=request.user.username
            listaal=[]
            lisbarclashub=[]
            lisexists=[]
            lisnotexists=[]
            lislocalid=[]
            pezziusati=0
            disponibile=1
            protprofiling=CollectionProtocol.objects.get(project='Profiling')
            #per capire se sto arrivando a salvare dalla vista archive o da quella fresh
            vistaarchive=False
            aliqdoppie=False
            if 'archive' in request.POST:
                vistaarchive=True
            if request.session.has_key('listaBatchCollection'):
                listot=request.session.get('listaBatchCollection')
                del request.session['listaBatchCollection']
                #e' una lista con le piastre che non ci sono in archivio 
                if request.session.has_key('listaPiastreAssentiBatchCollection'):
                    lispiastre=request.session.get('listaPiastreAssentiBatchCollection')
                else:
                    lispiastre=[]
                print 'lispiastre',lispiastre
                
                #e' un dizionario con i barc come chiave e come valore piastra|posizione|tipoaliquota
                if request.session.has_key('dizProvetteBatchCollection'):
                    dizprovette=request.session.get('dizProvetteBatchCollection')
                else:
                    dizprovette={}
                print 'dizprovette',dizprovette
                
                diztot={}
                #dizmoduloclinico=request.session.get('dizmoduloclinico')
                listum=[]
                lissorg=[]
                lisprot=[]
                listess=[]
                lisparam=[]                
                lparam=ClinicalFeature.objects.all()
                for param in lparam:
                    if param.measureUnit=='':
                        lisparam.append(param.name)
                    else:
                        #concateno anche l'unita' di misura
                        lisparam.append(param.name+'('+param.measureUnit+')')
                
                lisconsensi=[]
                #diz con chiave il nome del protocollo e come valore il project
                dizprot={}
                stringaid=''
                for diztemp in listot:
                    if 'actual_collection' not in diztemp:
                        prot=diztemp['Study protocol']
                        consenso=diztemp['Informed consent']
                        if prot not in dizprot.keys():
                            print 'prot',prot
                            protoc=CollectionProtocol.objects.get(name=prot)
                            stringaid+=str(protoc.id)+','
                            dizprot[prot]=protoc.project
                            progg=protoc.project
                        else:
                            progg=dizprot[prot]
                    else:
                        coll=diztemp['actual_collection']
                        if coll.idCollectionProtocol!=None:
                            collprot=coll.idCollectionProtocol
                        else:
                            collprot=protprofiling
                        prot=collprot.name
                        consenso=coll.collectionEvent
                        if prot not in dizprot.keys():
                            stringaid+=str(collprot.id)+','
                            dizprot[prot]=collprot.project
                        progg=collprot.project
                    #per avere la lista con i consensi e i progetti
                    val=consenso+'_'+progg
                    print 'val save batch',val
                    if val not in lisconsensi:
                        lisconsensi.append(val)
                    
                        
                stringaid=stringaid[0:len(stringaid)-1]
                print 'stringaid',stringaid
                #mi faccio dare la lista dei localid per i protocolli per sapere quali ci sono gia'
                hand=LocalIDListHandler()
                dizlocalid=hand.read(request,stringaid)
                print 'dizlocalid',dizlocalid
                    
                diztotconsensi=checkListInformedConsent(lisconsensi)
                print 'diztotcons',diztotconsensi
                lisaliqdoppie=[]
                for diz in listot:
                    #ogni aliquota ha i suoi dati nel dizionario
                    cons=diz['Informed consent']
                    paz=diz['Patient code']
                    genid=diz['GenealogyID']
                    #questo per evitare problemi
                    disable_graph()
                    laliquota=Aliquot.objects.filter(uniqueGenealogyID=genid,availability=1)
                    enable_graph()
                    if len(laliquota)==0:
                        g=GenealogyID(genid)
                        caso=g.getCaseCode()
                                            
                        #riempio il dizionario
                        chiave=cons+paz
                        if diztot.has_key(chiave):
                            coll=diztot[chiave]
                        else:
                            #e' la prima volta che trovo questa combinazione di paz+cons, quindi devo creare la collezione
                            #solo se non c'e' la chiave actual_collection nel dizionario, perche' in questo caso mi sto 
                            #riferendo ad una collezione gia' esistente
                            if 'actual_collection' not in diz:
                                sorgente=diz['Source']
                                sorg=None
                                for s in lissorg:
                                    if s.name.lower()==sorgente.lower():
                                        sorg=s
                                        break
                                if sorg==None:
                                    lsorg=Source.objects.filter(name=sorgente,type='Hospital')
                                    sorg=lsorg[0]
                                    lissorg.append(sorg)
                                
                                tumore=diz['Collection type']
                                tum=None
                                for t in listum:
                                    if t.longName.lower()==tumore.lower():
                                        tum=t
                                        break
                                if tum==None:
                                    ltum=CollectionType.objects.filter(longName=tumore)
                                    tum=ltum[0]
                                    listum.append(tum)
                                
                                protocollo=diz['Study protocol']
                                prot=None
                                for s in lisprot:
                                    if s.name.lower()==protocollo.lower():
                                        prot=s
                                        break
                                if prot==None:
                                    lprot=CollectionProtocol.objects.filter(name=protocollo)                    
                                    prot=lprot[0]
                                    lisprot.append(prot)
                                print 'prot',prot
                                
                                #restituisce la collezione e un'indicazione per sapere se l'oggetto c'era gia' 
                                #o se e' stato creato apposta, che salvo in creato
                                coll,creato=Collection.objects.get_or_create(itemCode=caso,
                                             idSource=sorg,
                                             idCollectionType=tum,
                                             collectionEvent=cons,
                                             patientCode=paz,
                                             idCollectionProtocol=prot)
                                                            
                                #se ho creato la collezione allora riempio le liste da passare poi al modulo clinico
                                #se sono nel caso in cui la collezione esisteva gia' non devo dire niente al modulo clinico
                                if creato:
                                    valore=diztotconsensi[cons+'_'+prot.project]
                                    print 'val',valore
                                    #valore=dizmoduloclinico[cons+'|'+str(prot.id)]
                                    #print 'valore',valore
                                    if valore==None:
                                        #vuol dire che l'ic non esiste ancora
                                        diztemp={'caso':coll.itemCode,'tum':coll.idCollectionType.abbreviation,'consenso':coll.collectionEvent,'progetto':coll.idCollectionProtocol.project,'source':coll.idSource.internalName,'wg':[workgr],'operator':operatore}
                                        lislocal=dizlocalid[prot.id]
                                        if paz in lislocal:
                                            diztemp['paziente']=coll.patientCode
                                        else:
                                            #il paziente inserito non esiste ancora
                                            if coll.patientCode=='':
                                                #il paziente non e' stato inserito dall'utente, quindi non viene creato niente
                                                diztemp['paziente']=''
                                            else:
                                                #il paziente e' stato inserito
                                                diztemp['newLocalId']=coll.patientCode
                                        lisnotexists.append(diztemp)
                                    else:
                                        lisexists.append({'caso':coll.itemCode,'tum':coll.idCollectionType.abbreviation,'consenso':coll.collectionEvent,'progetto':coll.idCollectionProtocol.project,'wg':[workgr]})
                                        localid=valore['patientUuid']
                                        lislocalid.append(localid)
                                
                                #salvo gli eventuali parametri clinici per la collezione
                                for param in lisparam:
                                    #print 'param',param
                                    if diz.has_key(param):
                                        val=diz[param].strip()
                                        print 'val',val
                                        if val!='':
                                            #devo spezzare in base a "(" per avere il nome della feature. In ogni caso,
                                            #che ci sia o meno la parentesi, prendo il primo elemento del vettore 
                                            par=param.split('(')
                                            feat=ClinicalFeature.objects.filter(name=par[0])
                                            #creo l'oggetto feature per la collezione
                                            clinfeat,creato=CollectionClinicalFeature.objects.get_or_create(idCollection=coll,
                                                                           idClinicalFeature=feat[0],
                                                                           value=val)
                                            print 'clinfeat',clinfeat
                            else:
                                coll=diz['actual_collection']
                                sorg=coll.idSource
                        data=diz['Date']
                        print 'data',data
                        dat=data.split('/')
                        datafin=dat[2]+'-'+dat[1]+'-'+dat[0]
                        
                        #salvo la serie
                        llserie=Serie.objects.filter(operator=operatore,serieDate=datafin)
                        if len(llserie)!=0:
                            ser=llserie[0]
                        else:
                            ser=Serie(operator=operatore,serieDate=datafin)
                            ser.save()
                        #ser,creato=Serie.objects.get_or_create(operator=operatore,
                        #                                       serieDate=datafin)
                        
                        t=g.getTissue()
                        tessval=None
                        for tess in listess:
                            if tess.abbreviation.lower()==t.lower():
                                tessval=tess
                                break
                        if tessval==None:
                            ltess=TissueType.objects.filter(abbreviation=t)                
                            tessval=ltess[0]
                            listess.append(tessval)
                        
                        print 'tessuto',tessval
                        
                        #il sampling lo creo per ogni aliquota con get or create perche' puo' cambiare il tessuto 
                        campionamento,creato=SamplingEvent.objects.get_or_create(idTissueType=tessval,
                                                     idCollection=coll,
                                                     idSource=sorg,
                                                     idSerie=ser,
                                                     samplingDate=datafin)
                        print 'camp',campionamento
                        
                        barc=diz['Tube barcode']
                        tipoa=diz['Actual_aliquottype']
                        piastraarchivio=diz['Plate']
                        #se la piastra si trova tra quelle assenti dallo storage o non c'e' la piastra, allora la 
                        #data di archiviazione e' nulla, altrimenti e' quella del campionamento inserita dall'utente
                        if piastraarchivio in lispiastre or piastraarchivio=='':
                            dataarch=None
                        else:
                            dataarch=datafin
                        print 'datarch',dataarch
                        tipoaliquota= AliquotType.objects.get(abbreviation=tipoa)
                        print 'tipo aliquota',tipoaliquota
                        if tipoaliquota.type=='Derived':
                            derivato=1
                        else:
                            derivato=0
                        a=Aliquot(barcodeID=barc,
                               uniqueGenealogyID=str(genid),
                               idSamplingEvent=campionamento,
                               idAliquotType=tipoaliquota,
                               timesUsed=pezziusati,
                               availability=disponibile,
                               derived=derivato,
                               archiveDate=dataarch)
                        print 'a',a
                        a.save()
                        lisbarclashub.append(barc)
                        vettore=g.getSampleVector()
                        numpezzi=diz['N. of pieces']
                        #tip e' il valore del tipo di campione effettivamente scritto nel file dall'utente
                        tip=diz['Aliquot type'].lower()
                        volu=diz['Volume(ul)']
                        print 'volu',volu
                        conc=diz['Concentration(ng/ul)']
                        conta=diz['Count(cell/ml)']
                        pur280=''
                        if 'Purity(260/280)' in diz:
                            pur280=diz['Purity(260/280)']
                        pur230=''
                        if 'Purity(260/230)' in diz:
                            pur230=diz['Purity(260/230)']
                        ge=''
                        if 'GE/Vex(GE/ml)' in diz:
                            ge=diz['GE/Vex(GE/ml)']
                        #e' un derivato
                        if derivato==1:
                            #salvo le feature
                            if volu=='':
                                volu=-1
                            #else:
                                #converto in ul
                                #vol=float(volu)*1000
                                                        
                            featvol=Feature.objects.get(idAliquotType=tipoaliquota,name='Volume')
                            aliqfeaturevol=AliquotFeature(idAliquot=a,
                                                       idFeature=featvol,
                                                       value=volu)
                            aliqfeaturevol.save()
                            
                            featvol=Feature.objects.get(idAliquotType=tipoaliquota,name='OriginalVolume')
                            aliqfeaturevol=AliquotFeature(idAliquot=a,
                                                       idFeature=featvol,
                                                       value=volu)
                            aliqfeaturevol.save()
                            print 'featu volume',aliqfeaturevol
                                
                            if conc=='':
                                conc=-1
                                
                            featconc=Feature.objects.get(idAliquotType=tipoaliquota,name='Concentration')
                            aliqfeatureconc=AliquotFeature(idAliquot=a,
                                                       idFeature=featconc,
                                                       value=conc)
                            aliqfeatureconc.save()
        
                            featconc=Feature.objects.get(idAliquotType=tipoaliquota,name='OriginalConcentration')
                            aliqfeatureconc=AliquotFeature(idAliquot=a,
                                                       idFeature=featconc,
                                                       value=conc)
                            aliqfeatureconc.save()
                            print 'feat conc',aliqfeatureconc
                            if pur280!='' or pur230!='' or ge!='':
                                #devo creare il qual sched se non e' gia' presente
                                qualsched,creato=QualitySchedule.objects.get_or_create(scheduleDate=datafin,
                                                                                operator=operatore)
                                #prendo il primo qualityprotocol disponibile per quel tipo di aliquota, tanto e' un valore fittizio
                                qualprot=QualityProtocol.objects.filter(idAliquotType=tipoaliquota)[0]
                                #creo il quality event
                                qualev,creato=QualityEvent.objects.get_or_create(idQualityProtocol=qualprot,
                                                                                 idQualitySchedule=qualsched,
                                                                                 idAliquot=a,
                                                                                 misurationDate=datafin,
                                                                                 insertionDate=datafin,
                                                                                 operator=operatore)
                                if pur280!='':
                                    misura=Measure.objects.get(name='purity',measureUnit='260/280')                                
                                    misevent=MeasurementEvent(idMeasure=misura,
                                                              idQualityEvent=qualev,
                                                              value=pur280)
                                    misevent.save()
                                    print 'misevent',misevent
                                if pur230!='':
                                    misura=Measure.objects.get(name='purity',measureUnit='260/230')
                                    misevent=MeasurementEvent(idMeasure=misura,
                                                              idQualityEvent=qualev,
                                                              value=pur230)
                                    misevent.save()
                                    print 'misevent',misevent
                                if ge!='':
                                    misura=Measure.objects.get(name='GE/Vex',measureUnit='GE/ml')
                                    misevent=MeasurementEvent(idMeasure=misura,
                                                              idQualityEvent=qualev,
                                                              value=ge)
                                    misevent.save()
                                    print 'misevent',misevent
                            
                            conta=''
                        elif tip=='whole blood' or tip=='pbmc' or tip=='plasma' or tip=='pax tube' or tip=='urine' or tip=='frozen sediments' or ((vettore in['A','S','O']) and tip=='viable') or ((vettore in['A','S','O']) and tip=='snap frozen'):
                            if volu!='':
                                featvol=Feature.objects.get(idAliquotType=tipoaliquota,name='Volume')
                                aliqfeaturevol=AliquotFeature(idAliquot=a,
                                                           idFeature=featvol,
                                                           value=volu)
                                aliqfeaturevol.save()
        
                                print 'featu volume',aliqfeaturevol
                            if conta!='' and (tip =='pbmc' or ((vettore in['A','S','O']) and tip=='viable') or ((vettore in['A','S','O']) and tip=='snap frozen')):
                                featconta=Feature.objects.get(Q(idAliquotType=tipoaliquota)&Q(name='Count'))
                                aliqfeatureconta=AliquotFeature(idAliquot=a,
                                                           idFeature=featconta,
                                                           value=conta)
                                aliqfeatureconta.save()
                                print 'aliq',aliqfeatureconta
                            else:
                                conta=''
                        elif (tipoaliquota.type=='Block' or tip=='snap frozen' or tip=='rnalater' or tip=='viable' ) and (vettore=='H' or vettore=='X'):
                            #salvo il numero di pezzi
                            fea=Feature.objects.get(Q(idAliquotType=tipoaliquota)&Q(name='NumberOfPieces'))
                            aliqfeature=AliquotFeature(idAliquot=a,
                                                       idFeature=fea,
                                                       value=numpezzi)
                            aliqfeature.save()
                            print 'aliq',aliqfeature
                            conta=''
                            volu=''
                            conc=''
                    
                        if volu==-1:
                            volu=''
                        if conc==-1:
                            conc=''                    
                        if vistaarchive:
                            valori=genid+',,,'+str(numpezzi)+','+barc+','+tipoaliquota.abbreviation+',true,'+str(volu)+','+str(conc)+','+pur280+','+pur230+','+ge+','+str(datafin)+','+volu+','+conta
                        else:
                            valori=genid+',,,'+str(numpezzi)+','+barc+','+tipoaliquota.abbreviation+',true,'+str(volu)+','+str(conc)+','+str(conta)+',,,'+str(datafin)
                        listaal.append(valori)
                        print 'listaaliq',listaal
                    else:
                        aliqdoppie=True
                        lisaliqdoppie.append(laliquota[0])
                print 'lisaliqdoppie',lisaliqdoppie
                        
                        
                if not aliqdoppie:                                           
                    #per controllare se nel lashub esistono gia' questi barc
                    print 'lisbarc',lisbarclashub
                    if len(lisbarclashub)!=0:
                        #faccio una richiesta allo storage per vedere se questi barc esistono gia'
                        url1 = Urls.objects.get(default = '1').url + '/api/check/presence/'
                        val1={'lista':json.dumps(lisbarclashub),'salva':True}
                        print 'url1',url1
                        data = urllib.urlencode(val1)
                        req = urllib2.Request(url1,data=data, headers={"workingGroups" : get_WG_string()})
                        u = urllib2.urlopen(req)
                        #u = urllib2.urlopen(url1, data)
                        re = json.loads(u.read())
                        print 're',re
                        res=re['data']
                        print 'res',res
                        if res!='ok':
                            raise ErrorDerived('Error: barcode '+res+' already exists')
                    
                    request,errore=SalvaInStorage(listaal,request)
                    print 'err', errore   
                    if errore==True:
                        transaction.rollback()
                        variables = RequestContext(request, {'errore':errore})
                        return render_to_response('tissue2/index.html',variables)
                    
                    if len(dizprovette)!=0:
                        #faccio il posizionamento delle provette create prima
                        url1 = Urls.objects.get(default = '1').url + '/api/check/presence/'
                        val1={'lista':json.dumps(dizprovette),'posiziona':True}
                        print 'url1',url1
                        data = urllib.urlencode(val1)
                        req = urllib2.Request(url1,data=data, headers={"workingGroups" : get_WG_string()})
                        u = urllib2.urlopen(req)
                        #u = urllib2.urlopen(url1, data)
                        re = json.loads(u.read())
                        print 're',re
                        
                else:
                    strgen=''
                    for aliquot in lisaliqdoppie:
                        strgen+=aliquot.uniqueGenealogyID+'&'
                    lgenfin=strgen[:-1]
                    diz=AllAliquotsContainer(lgenfin)
                    listval=[]
                    for al in lisaliqdoppie:
                        vol=''
                        lfeatvol=Feature.objects.filter(idAliquotType=al.idAliquotType,name='Volume')
                        if len(lfeatvol)!=0:
                            lvol=AliquotFeature.objects.filter(idAliquot=al,idFeature=lfeatvol[0])
                            if len(lvol)!=0:
                                vol=str(lvol[0].value)
                        conc=''
                        lfeatconc=Feature.objects.filter(idAliquotType=al.idAliquotType,name='Concentration')
                        if len(lfeatconc)!=0:
                            lconc=AliquotFeature.objects.filter(idAliquot=al,idFeature=lfeatconc[0])
                            if len(lconc)!=0:
                                conc=str(lconc[0].value)
                        conta=''
                        lfeatconta=Feature.objects.filter(idAliquotType=al.idAliquotType,name='Count')
                        if len(lfeatconta)!=0:
                            lconta=AliquotFeature.objects.filter(idAliquot=al,idFeature=lfeatconta[0])
                            if len(lconta)!=0:
                                conta=str(lconta[0].value)
                        valori=diz[al.uniqueGenealogyID]
                        val=valori[0].split('|')
                        barc=val[1]
                        print 'barc',barc
                        valori=al.uniqueGenealogyID+',,,,'+barc+','+al.idAliquotType.abbreviation+',true,'+str(vol)+','+str(conc)+','+str(conta)+',,,'
                        listval.append(valori)
                        print 'listval',listval
                        request.session['aliquotCollectionBatch']=listval
                    
            if vistaarchive:
                if not aliqdoppie:
                    request.session['aliquotEsterne']=listaal
                lista,intest,l,inte=LastPartExternAliquot(request,'n')
            else:
                if not aliqdoppie:
                    request.session['aliquotCollectionBatch']=listaal
                lista,intest,l,inte=LastPartCollectionBatch(request,'n')
                
            #devo fare gia' il commit perche' devo passare al modulo clinico la collezione, che deve gia' esistere sul grafo;
            #altrimenti non si riesce a collegare il nodo collezione con il consenso informato
            transaction.commit()
            #faccio la API al modulo clinico per dirgli di salvare            
            errore=saveInClinicalModule(lisexists,lisnotexists,[workgr],operatore,lislocalid)
            if errore:
                raise Exception     
            
            diztemp={}
            diztemp['lista']=lista
            diztemp['intest']=intest
            #if not aliqdoppie:
            request.session['listafinalecollectionbatchreport']=diztemp
                
            urlfin=settings.DOMAIN_URL+settings.HOST_URL+'/batch/save/final/'
            print 'urlfin',urlfin
            return HttpResponseRedirect(urlfin)
                
            variables = RequestContext(request,{'secondo':True,'fine':True,'aliq':lista,'intest':intest})
            return render_to_response('tissue2/collection/batch.html',variables)
        except ErrorDerived as e:
            transaction.rollback()
            print 'My exception occurred, value:', e.value
            variables = RequestContext(request, {'secondo':True,'errore':e.value})
            return render_to_response('tissue2/collection/batch.html',variables)
        except Exception, e:
            transaction.rollback()
            print 'except',e
            errore=True
            variables = RequestContext(request, {'errore':errore})
            return render_to_response('tissue2/index.html',variables)

#per far vedere il report finale del salvataggio delle collezioni in batch
@transaction.commit_on_success
@laslogin_required
@login_required
@permission_decorator('tissue.can_view_BBM_collaboration_collection')
def BatchCollectionSaveFinal(request):
    diztemp=request.session.get('listafinalecollectionbatchreport')
    variables = RequestContext(request,{'secondo':True,'fine':True,'aliq':diztemp['lista'],'intest':diztemp['intest']})
    return render_to_response('tissue2/collection/batch.html',variables)    

#per riaprire una vecchia collezione e inserire nuovi parametri dopo aver fatto una ricerca sulle collezioni esistenti   
@laslogin_required
@login_required
@permission_decorator('tissue.can_view_BBM_institutional_collection')
def AddParameters(request):
    mdamTemplates = getMdamTemplates([41,44,45])
    print 'mdamTemplates',mdamTemplates
    mdamurl=Urls.objects.get(idWebService=WebService.objects.get(name='MDAM').id).url
    listot=getGenealogyDict()
    variables = RequestContext(request, {'mdamTemplates':json.dumps(mdamTemplates), 'mdam_url':mdamurl,'genid':json.dumps(listot) })   
    return render_to_response('tissue2/collection/add_parameters.html',variables)

@laslogin_required    
@transaction.commit_on_success
@login_required
@permission_decorator('tissue.can_view_BBM_institutional_collection')
def SaveParameters(request):
    print request.POST
    if request.method=='POST':        
        try:
            #la schermata, con una POST, comunica un dizionario con le collezioni il cui paziente e' stato aggiornato
            if 'salva' in request.POST:
                listaaliq=json.loads(request.POST.get('dati'))
                request.session['clinicalParameterModifiedCollection']=listaaliq
                return HttpResponse()
            
            operatore=request.user.username
            print 'operatore',operatore
            lisfin=[]
            i=1
            #prendo il dizionario che contiene le collezioni con il paziente o il consenso modificato
            dizcoll=request.session.get('clinicalParameterModifiedCollection')
            print 'dizcoll',dizcoll
            #la chiave e' idtumore|caso, mentre il valore e' un dizionario con chiavi il paziente e il consenso
            for key,val in dizcoll.items():
                kk=key.split('|')
                tum=CollectionType.objects.get(id=kk[0])
                coll=Collection.objects.get(idCollectionType=tum,itemCode=str(kk[1]))
                paznuovo=val['paziente']
                consnuovo=val['consenso']
                coll.patientCode=paznuovo
                coll.collectionEvent=consnuovo
                coll.save()
                print 'coll',coll                
                if coll.idCollectionProtocol!=None:
                    prot=coll.idCollectionProtocol.name
                else:
                    prot=''
                lisfin.append(ReportToHtml([str(i),coll.idCollectionType.longName,coll.itemCode,coll.idSource.name,coll.collectionEvent,coll.patientCode,prot]))
                i=i+1
            
            #salvo i parametri clinici per le collezioni
            if request.session.has_key('clinicalparamreopencollection'):
                dizparam=request.session.get('clinicalparamreopencollection')
            else:
                dizparam={}            
            print 'dizparam',dizparam
            #la chiave e' idtumore|caso, mentre il valore e' la lista dei parametri
            for key,val in dizparam.items():
                kk=key.split('|')
                tum=CollectionType.objects.get(id=kk[0])
                coll=Collection.objects.get(idCollectionType=tum,itemCode=str(kk[1]))
                if len(val)!=0:
                    #salvo la serie
                    ser,creato=Serie.objects.get_or_create(operator=operatore,
                                                       serieDate=date.today())
                    
                    #creo un campionamento fittizio per salvare la data e l'operatore che hanno 
                    #riaperto la collezione 
                    campionamento=SamplingEvent(idCollection=coll,
                                         idSource=coll.idSource,
                                         idSerie=ser,
                                         samplingDate=date.today())
                    campionamento.save()
                    print 'camp',campionamento
                    
                    for diz in val:
                        idparamclin=diz['idfeat']
                        param=ClinicalFeature.objects.get(id=idparamclin)
                        print 'param',param
                        lisval=diz['value']
                        print 'lisval',lisval
                        #lisval e' una lista con dentro i valori da salvare
                        for v in lisval:
                            print 'v',v
                            #creo l'oggetto feature per la collezione
                            clinfeat=CollectionClinicalFeature(idCollection=coll,
                                                               idSamplingEvent=campionamento,
                                                               idClinicalFeature=param,
                                                               value=v)
                            clinfeat.save()
                            print 'clinfeat',clinfeat

                    diztemp={}
                    diztemp['tum']=coll.idCollectionType.longName
                    diztemp['case']=coll.itemCode
                    diztemp['source']=coll.idSource.name
                    diztemp['informed']=coll.collectionEvent
                    diztemp['patient']=coll.patientCode
                    if coll.idCollectionProtocol!=None:
                        prot=coll.idCollectionProtocol.name
                    else:
                        prot=''
                    #solo se non ho gia' aggiunto prima questa collezione; per evitare doppioni
                    if key not in dizcoll:
                        lisfin.append(ReportToHtml([str(i),coll.idCollectionType.longName,coll.itemCode,coll.idSource.name,coll.collectionEvent,coll.patientCode,prot]))
                        i=i+1            
            
            variables = RequestContext(request, {'fine':True, 'lisfin':lisfin })
            return render_to_response('tissue2/collection/add_parameters.html',variables)
        except Exception,e:
            print 'err',e
            transaction.rollback()
            variables = RequestContext(request, {'errore':True})
            return render_to_response('tissue2/index.html',variables)
