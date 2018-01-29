from __init__ import *
import requests

#######################################
#Experiments views
#######################################

class ErrorAliquot(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

#per far comparire la prima pagina in cui selezionare la richiesta che contiene i campioni su cui voglio fare l'esperimento
@laslogin_required
@login_required
@permission_decorator('ngs.can_view_NGS_run_experiment')
def execute_experiment(request):
    try:
        if request.method == "GET":
            if request.session.has_key('idplan_execute_experiment'):
                del request.session['idplan_execute_experiment']            
            user_name = request.user
            #featcapture=Feature.objects.filter(name='Capture type')
            request_operator = Request.objects.filter(idOperator=user_name, pending=False, timechecked__isnull =True,source='Internal')
            request_null = Request.objects.filter(idOperator__isnull=True, pending=False, timechecked__isnull =True,source='Internal')
            plans = list(chain(request_operator, request_null))
            featurefinish=Feature.objects.get(name='Finished experiment')
            #per ogni richiesta devo prendere i campioni collegati            
            lisfin=[]
            listalabel=[]
            #chiave l'aliquota e valore un dizionario con tutti i suoi dati relativi alla richiesta
            dizaliqreq={}
            liscamp=[]
            for req in plans:
                dizgen={}
                lisdiz=[]
                #filtro anche sul capture per avere un solo record, altrimenti mi riempie il dizionario di doppioni per la stessa aliquota
                lisaliq=Aliquot_has_Request.objects.filter(request_id=req)
                #print 'lisaliq',lisaliq
                for alreq in lisaliq:
                    al=alreq.aliquot_id
                    if al.label_request in dizaliqreq:
                        diztemp=dizaliqreq[al.label_request]
                    else:
                        diztemp={}
                    unitmis=''
                    if alreq.feature_id.measureUnit!='':
                        unitmis=' ('+alreq.feature_id.measureUnit+')'
                    diztemp[alreq.feature_id.name+unitmis]=alreq.value    
                    dizaliqreq[al.label_request]=diztemp
                print 'diztemp',diztemp
                #metto filter e non get, cosi' se non trova niente non mi da' errore
                lisexp=Experiment.objects.filter(request_id=req).values_list('id',flat=True)
                for alreq in lisaliq:
                    #di quelle della richiesta devo prendere solo quelle che non sono ancora state inserite in un esperimento, ossia non hanno 
                    #valori in aliquot_has_experiment
                    al=alreq.aliquot_id
                    inserisci=False
                    if al.label_request not in liscamp:
                        lalexp=Aliquot_has_Experiment.objects.filter(aliquot_id=al,idExperiment__in=lisexp)
                        print 'lalexp',lalexp
                        if len(lalexp)==0:
                            inserisci=True
                        else:
                            #altrimenti se ci sono dei valori devo vedere se l'esperimento e' finito o no
                            for alex in lalexp:
                                print 'alex',alex
                                if alex.feature_id.name=='Finished experiment' and alex.value=='False':
                                    inserisci=True
                        if inserisci:
                            diztemp={}
                            diztemp['label']=al.label_request
                            listalabel.append(al.label_request)
                            diztemp['description']=al.description
                            diztemp['owner']=al.owner
                            lisdiz.append(diztemp)
                        liscamp.append(al.label_request)
                        print 'lisdiz',lisdiz
                dizgen['aliquots']=lisdiz
                dizgen['description']=req.description
                dizgen['owner']=req.owner
                dizgen['title']=req.title
                dizgen['id']=req.id
                lisfin.append(dizgen)
            print 'lisfin',lisfin
            return render_to_response('select_request_for_run.html', {'data':lisfin,'lislabel':json.dumps(listalabel),'dizdatialiq':json.dumps(dizaliqreq)}, RequestContext(request))
        
        else:
            print request.POST
            raw_data = json.loads(request.raw_post_data)
            idplan = ''
            if raw_data.has_key('idplan'):
                idplan = raw_data['idplan']
                request.session['idplan_execute_experiment']=idplan
            return HttpResponseRedirect(reverse('ngs.views.views_experiment.execute_experiment_insertdata'))
    except Exception, e:
        print 'err',e
        variables = RequestContext(request, {'errore':True})
        return render_to_response('home.html',variables)
 
 
#per far comparire la pagina in cui associare i dati dell'esperimento ai campioni selezionati in precedenza
@laslogin_required
@login_required
@permission_decorator('ngs.can_view_NGS_run_experiment')
def execute_experiment_insertdata(request):
    try:
        if request.method == "GET":
            if 'dizExperimentSaveData' in request.session:
                del request.session['dizExperimentSaveData']
            if 'listGenealogyExperimentSaveData' in request.session:
                del request.session['listGenealogyExperimentSaveData']
            if 'reportExecuteExperiment' in request.session:
                del request.session['reportExecuteExperiment']
            if 'titleExpExperimentSaveData' in request.session:
                del request.session['titleExpExperimentSaveData']
            if 'descriptionExpExperimentSaveData' in request.session:
                del request.session['descriptionExpExperimentSaveData']
            lisfin=[]
            #chiave la label e val un diz con tutte le feature di un campione all'interno di un esperimento
            dizvalexp={}
            featcapture=Feature.objects.filter(name='Capture type')
            featvolume=Feature.objects.filter(name='Provided volume')
            idplan=request.session['idplan_execute_experiment']
            print 'idplan',idplan
            plan = Request.objects.get(id=idplan)
    
            aliquots = Aliquot_has_Request.objects.filter(request_id=plan,feature_id=featcapture)
            lisaliquots2 = Aliquot_has_Request.objects.filter(request_id=plan,feature_id=featvolume)
            print 'aliquots',aliquots
            lisexp=Experiment.objects.filter(request_id=plan).values_list('id',flat=True)
            for alreq in aliquots:
                inserisci=False
                al=alreq.aliquot_id
                lalexp=Aliquot_has_Experiment.objects.filter(aliquot_id=al,idExperiment__in=lisexp)
                if len(lalexp)==0:
                    inserisci=True
                else:                    
                    #altrimenti se ci sono dei valori devo vedere se l'esperimento e' finito o no
                    for alex in lalexp:
                        print 'alex',alex
                        if alex.feature_id.name=='Finished experiment' and alex.value=='False':
                            inserisci=True
                            break
                    if inserisci:
                        #solo se ho trovato dei campioni con "Finished experiment"=False inserisco i valori nel dizionario
                        dizionario={}
                        for val in lalexp:
                            dizionario[val.feature_id.name]=val.value
                        dizvalexp[al.label_request]=dizionario
                if inserisci:
                    diztemp={}
                    diztemp['label']=al.label_request
                    diztemp['genid']=al.genId
                    diztemp['description']=al.description
                    diztemp['owner']=al.owner
                    diztemp['capture']=alreq.value
                    for alr in lisaliquots2:
                        al2=alr.aliquot_id
                        if al.id==al2.id:
                            diztemp['takenvolume']=alr.value
                            break
                    lisfin.append(diztemp)                    
            print 'lisfin',lisfin
            print 'dizvalexp',dizvalexp            
            return render_to_response('execute_experiment.html', {'data':lisfin,'title':plan.title,'description':plan.description,'expvalue':json.dumps(dizvalexp)}, RequestContext(request))
    except Exception, e:
        print 'err',e
        variables = RequestContext(request, {'errore':True})
        return render_to_response('home.html',variables)
    
#per salvare i dati degli esperimenti
@transaction.commit_on_success
@laslogin_required
@login_required
@permission_decorator('ngs.can_view_NGS_run_experiment')
def execute_experiment_save(request):
    try:
        print request.POST
        print request.FILES
        if 'salva' in request.POST:
            diztot=json.loads(request.POST['dizdata'])
            print 'diztot',diztot
            listgenealogy=json.loads(request.POST['lisgen'])
            request.session['dizExperimentSaveData']=diztot
            request.session['listGenealogyExperimentSaveData']=listgenealogy
            request.session['titleExpExperimentSaveData']=request.POST['titleexp']
            request.session['descriptionExpExperimentSaveData']=request.POST['description']
            return HttpResponse()
        if 'conferma' in request.POST:
            diztot=request.session['dizExperimentSaveData']
            lisgen=request.session['listGenealogyExperimentSaveData']
            titoloexp=request.session['titleExpExperimentSaveData']
            descrexp=request.session['descriptionExpExperimentSaveData']
            idplan=request.session['idplan_execute_experiment']
            print 'idplan',idplan
            requestngs = Request.objects.get(id=idplan)
            #lista di dizionari con chiave l'utente e valore una lista di dizionari che rappresentano le aliquote di esperimenti falliti 
            lisfalliti=[]
            ownerrequest=''
            lisfilefalliti=[]
            lisfilecaricati=[]
            listareport=[]
            values_to_biobank = {'info':[], 'exhausted':[]}
            
            featcapture=Feature.objects.get(name='Capture type')
            featfinished=Feature.objects.get(name='Finished experiment')            
            dizfeat={}
            listafeature=Feature.objects.all()
            for feat in listafeature:
                dizfeat[feat.name]=feat
                        
            #non devo sempre creare un esperimento nuovo ma devo prendere quello gia' esistente se sto trattando
            #un campione che avevo gia' inserito                        
            lesp=Experiment.objects.filter(request_id=requestngs)
            print 'lesp',lesp
            if len(lesp)!=0:
                esp=lesp[0]
                esp.time_creation=timezone.localtime(timezone.now())
                esp.title=titoloexp
                esp.description=descrexp
                esp.idOperator=request.user
                esp.save()
            else:
                esp=Experiment(time_creation=timezone.localtime(timezone.now()),
                               title=titoloexp,
                               description=descrexp,
                               idOperator=request.user,
                               request_id=requestngs)
                esp.save()
            print 'esp',esp
            listamail=[]
            oggettomail=''
            i=1
            #scandisco i gen in base all'ordine con cui ho inserito i dati nella schermata
            for gen in lisgen:
                diztemp=diztot[gen]
                print 'diztemp',diztemp
                failed=diztemp['Failed']
                label=diztemp['label']
                lisal=Aliquot.objects.filter(genId=gen,label_request=label)
                al=lisal[0]
                print 'al',al                            
                
                if 'volrimanente' in diztemp:
                    values_to_biobank['info'].append(al.genId+"&"+ request.user.username + "&" + str(diztemp['volrimanente']))
                
                #se e' fallita non ha un volume usato
                if 'Used volume' in diztemp:    
                    alexp,creato=Aliquot_has_Experiment.objects.get_or_create(aliquot_id=al,
                                             idExperiment=esp,
                                             feature_id=dizfeat['Used volume'])
                    if not creato:
                        if alexp.value!=diztemp['Used volume']:
                            alexp.value=diztemp['Used volume']
                            alexp.save()
                    else:
                        alexp.value=diztemp['Used volume']
                        alexp.save()
                #rendo esaurita l'aliquota solo se anche l'esperimento e' finito
                if diztemp['Exhausted']=='True' and diztemp['Finished experiment']:
                    values_to_biobank['exhausted'].append(al.genId)
 
                if 'labelfinale' in diztemp:
                    alexp,creato=Aliquot_has_Experiment.objects.get_or_create(aliquot_id=al,
                                                 idExperiment=esp,
                                                 feature_id=dizfeat['Label experiment'])
                    if not creato:
                        if alexp.value!=diztemp['labelfinale']:
                            alexp.value=diztemp['labelfinale']
                            alexp.save()
                    else:
                        alexp.value=diztemp['labelfinale']
                        alexp.save()
                                
                for key,val in diztemp.items():
                    print 'key',key
                    print 'val',val
                    if key in dizfeat and val!='' and val!='---------':
                        #prendo la feature e se non c'e' la creo
                        alexp,creato=Aliquot_has_Experiment.objects.get_or_create(aliquot_id=al,
                                                                         idExperiment=esp,
                                                                         feature_id=dizfeat[key])
                        if not creato:
                            if alexp.value!=val:
                                alexp.value=val
                                alexp.save()
                        else:
                            alexp.value=val
                            alexp.save()
                        
                        print 'alexp',alexp
                
                if 'files' in diztemp:
                    lisfile=json.loads(diztemp['files'])
                    if len(lisfile)!=0:
                        for f in lisfile:
                            uploaded_file = [upfile for upfile in request.FILES.getlist('file') if upfile.name == f][0]
                            print 'nome file',uploaded_file.name
                            destination = handle_uploaded_file(uploaded_file)
                            print 'destination',destination
                            
                            responseUpload = uploadRepFile({'operator':request.user.username}, destination)
                            print responseUpload
                            if responseUpload == 'Fail':
                                raise Exception
                            lisfilecaricati.append(destination)                            
                            
                            if failed=='True':
                                lisfilefalliti.append(destination)
                            
                            alexp=Aliquot_has_Experiment(aliquot_id=al,
                                                 idExperiment=esp,
                                                 feature_id=dizfeat['File'],
                                                 value=responseUpload)
                            alexp.save()
                            
                if failed=='True':
                    #solo se ho concluso l'esperimento
                    if diztemp['Finished experiment']=='True':
                        #E' la persona titolare della richiesta a cui mandare l'e-mail per il fallimento. Sara' sempre un utente del LAS perche'
                        #rappresenta l'utente loggato che ha inserito la richiesta. Invece il proprietario dell'aliquota puo' essere 
                        #fuori dal LAS
                        ownerrequest=requestngs.owner
                        #per avere poi la chiave da leggere nel template dell'email 
                        diztemp['Fragmentdistribution']=diztemp['Fragment distribution']
                        lisfalliti.append(diztemp)
                        
                        #salvo anche il fatto che ho inserito i file cosi' concludo tutta la procedura per questo campione
                        alexp=Aliquot_has_Experiment(aliquot_id=al,
                                             idExperiment=esp,
                                             feature_id=Feature.objects.get(name='File inserted'),
                                             value='True')
                        alexp.save()
                        
                        #Se tutti i campioni dell'esperimento sono falliti allora devo mettere come eseguito l'esperimento impostando la data di esecuzione.
                        #Cosi' tutta la procedura finisce qui
                        if len(lisfalliti)==len(lisgen):
                            esp.time_executed=timezone.localtime(timezone.now())
                            esp.save()
                else:
                    #solo se l'esperimento e' concluso
                    if diztemp['Finished experiment']=='True':
                        #solo se l'esperimento e' riuscito mando l'e-mail
                        #prendo l'ultimo valore del run tanto dovrebbe essere uguale per tutti i campioni
                        #oggettomail=diztemp['Run name']
                        
                        testomail=str(i)+'\t'+diztemp['labelfinale']+'\t'+diztemp['Library name']+'\t'+diztemp['Instrument']+'\t'+diztemp['Run chemistry']+'\t'+diztemp["Run name"]+'\t'+diztemp["Assay"]
                        if 'Sample ID BSO' in diztemp:
                            testomail+='\t'+diztemp['Sample ID BSO']
                        print 'testomail',testomail
                        listamail.append(testomail)
                        i+=1
                
                diztemp['finishedexperiment']=diztemp['Finished experiment']
                listareport.append(diztemp)
                    
            print 'lisfilefalliti',lisfilefalliti
            if len(lisfalliti)!=0:
                #devo mandare l'e-mail all'utente che ha inserito la richiesta per dirgli che e' fallito l'esperimento                
                file_data = render_to_string('report_experiment_fail_email.html', {'listafin':lisfalliti})
                loperator = User.objects.filter(username = ownerrequest)
                if len(loperator)!=0:
                    mailOperator = loperator[0].email
                    if mailOperator!='':
                        text_content = 'This is an important message'
                        subject='[LAS] NGS experiment failed'
                        msg = EmailMultiAlternatives(subject, text_content, '', [mailOperator])
                        msg.attach_alternative(file_data, "text/html")
                        for percorso in lisfilefalliti:                            
                            msg.attach_file(percorso)
                        print 'msg',msg
                        msg.send()
            
            #prendo il numero di aliquote che c'erano in quella richiesta per sapere se le ho fatte tutte
            lisaliq=Aliquot_has_Request.objects.filter(request_id=requestngs,feature_id=featcapture).values_list('aliquot_id',flat=True)
            print 'lisaliq',lisaliq            
            #metto filter cosi' non mi da' errore se non trova dati
            lisexper=Experiment.objects.filter(request_id=requestngs).values_list('id',flat=True)
            print 'lisexper',lisexper
            #devo vedere quante di queste hanno la feature "finish experiment" (che viene salvata sempre per tutti i campioni) in Aliquot_has_experiment
            lalexp=Aliquot_has_Experiment.objects.filter(idExperiment__in=lisexper,aliquot_id__in=lisaliq,feature_id=featfinished,value='True').values_list('aliquot_id',flat=True)
            print 'lalexp',lalexp
            #se le ho fatte tutte, allora imposto come terminata la richiesta
            if len(lisaliq)==len(set(lalexp)):
                requestngs.timechecked=timezone.localtime(timezone.now())
                requestngs.save()
                                                                        
            #biobank interaction
            print 'values to biobank',values_to_biobank
            if len(values_to_biobank['info']) != 0 or len(values_to_biobank['exhausted']) != 0:
                data = urllib.urlencode(values_to_biobank)
                #update info for the aliquots (volume and exhausted)
                risultato=updateAliquots(data)
                print 'res',risultato
                if risultato!='ok':
                    raise Exception
                        
            remove_uploaded_files(lisfilecaricati)
            
            #mando l'e-mail al gruppo del BIG solo se un esperimento e' riuscito
            if len(listamail)!=0:
                email = LASEmail (functionality=get_functionality(), wgString=get_WG_string())
                
                #mettere i componenti del BIG
                user1=User.objects.get(username='michela.buscarino')
                user2=User.objects.get(username='alice.bartolini')
                user3=User.objects.get(username='giuseppe.rospo')
                user4=User.objects.get(username='crisagi')                
                #user1=User.objects.get(username='eugenia.zanella')
                #user2=User.objects.get(username='eugenia.zanella')
                #user3=User.objects.get(username='eugenia.zanella')
                #user4=User.objects.get(username='eugenia.zanella')
                
                oggetto='[LAS-NGS] Terminata run'#+oggettomail
                msg=['Experiment executor: '+request.user.username,'Request planner: '+requestngs.owner+'\n']
                msg.append('Analyzed samples:\n')
                msg.append('N\tLabel\tLibrary name\tInstrument\tRun chemistry\tRun name\tAssay\tSample ID BSO')
                msg.extend(listamail)
                wgList1=WG.objects.filter(id__in=WG_User.objects.filter(user=user1).values_list('WG',flat=True).distinct())
                wgList2=WG.objects.filter(id__in=WG_User.objects.filter(user=user2).values_list('WG',flat=True).distinct())
                wglistot=list(set(wgList1)|set(wgList2))
                print 'wgtot',wglistot
                for wg in wglistot:
                    print 'wg',wg.name
                    email.addMsg([wg.name], msg)
                    email.appendSubject([wg.name],oggetto)
                
                    email.addRoleEmail([wg.name], 'Planner', [user1.username,user2.username,user3.username,user4.username])
                    email.addRoleEmail([wg.name], 'Executor', [request.user.username])

                try:
                    email.send()
                except Exception, e:
                    print 'errore',e
                    #raise Exception
            
            request.session['reportExecuteExperiment']=listareport
            return HttpResponseRedirect(reverse('ngs.views.views_experiment.execute_experiment_final'))
    except Exception, e:
        print 'err',e
        transaction.rollback()
        variables = RequestContext(request, {'errore':True})
        return render_to_response('home.html',variables)

#Per far comparire la schermata finale dell'esecuzione esperimento
@laslogin_required
@login_required
@permission_decorator('ngs.can_view_NGS_run_experiment')
def execute_experiment_final(request):
    lissample=request.session['reportExecuteExperiment']
    print 'lissample',lissample
    variables = RequestContext(request,{'lissample':lissample})
    return render_to_response('report_execute_experiment.html',variables)

@laslogin_required
@login_required
@permission_decorator('ngs.can_view_NGS_run_experiment')
@transaction.commit_manually
def select_experiment(request):
    if request.method == "GET":
        # GET method
        try:
            user = auth.get_user(request)
            user_name = User.objects.get(username = user.username)

            #plans1 = Experiment.objects.filter(idOperator=user_name, time_creation__isnull = False, time_executed__isnull =True)
            #plans_null = Experiment.objects.filter(idOperator=None, time_creation__isnull = False, time_executed__isnull =True)
            #plans = list(chain(plans1, plans_null))
            plans = Experiment.objects.filter(time_creation__isnull = False, time_executed__isnull =True)
            print 'plans',plans
            transaction.commit()
            return render_to_response('select_experiment.html', {'plans':plans}, RequestContext(request))
        except Exception, e:
            print e
            transaction.rollback()
            variables = RequestContext(request, {'errore':True})
            return render_to_response('home.html',variables)
        finally:
            transaction.rollback()
    else:
        try:
            raw_data = simplejson.loads(request.raw_post_data)
            print '[NGS] -- Raw Data: "%s"' % raw_data
            idplan = ''
            if raw_data.has_key('idplan'):
                idplan = raw_data['idplan']
            request.session['idplan'] = idplan
            return HttpResponseRedirect(reverse('ngs.views.read_measures'))
        except Exception, e:
            print e

#per far comparire la schermata di caricamento file di un certo esperimento
@laslogin_required
@login_required
@permission_decorator('ngs.can_view_NGS_run_experiment')
@transaction.commit_manually
def read_measures(request):
    print 'NGS view: start views_experiment.read_measures'
    print request.POST
    featfail=Feature.objects.get(name='Failed')    
    featvol=Feature.objects.get(name='Used volume')
    if request.method == "GET":
        try:
            user = auth.get_user(request)
            #e' l'id dell'esperimento
            idplan = request.session['idplan']
            plan = Experiment.objects.get(id=idplan)
            print 'plan',plan
            aliqexpiniziale = Aliquot_has_Experiment.objects.filter(idExperiment=plan)
            print 'aliqexpiniziale',aliqexpiniziale
            #chiave il gen e valore un dizionario con tutti i dati di quel campione per quell'esperimento
            dizaliqexp={}
            #lista per mantenere l'ordine dei campioni inseriti
            lisaliqexp=[]
            for alexp in aliqexpiniziale:
                al=alexp.aliquot_id
                if al.genId in dizaliqexp:
                    diztemp=dizaliqexp[al.genId]
                else:
                    diztemp={}                
                diztemp[alexp.feature_id.name]=alexp.value    
                dizaliqexp[al.genId]=diztemp
                if al not in lisaliqexp:
                    lisaliqexp.append(al)
            print 'dizaliqexp',dizaliqexp
            resp = {'plan':plan, 'aliquots':[]}
            aliq_biobank = ''
            aliquotBio = {}
                        
            for al in lisaliqexp:
                gen=al.genId
                #se c'e' la chiave "File inserted" vuol dire che ho gia' inserito i file per quel campione e non devo piu' farlo comparire
                if dizaliqexp[gen]['Failed']=='False' and dizaliqexp[gen]['Finished experiment']=='True' and 'File inserted' not in dizaliqexp[gen]:                     
                    valdiz=dizaliqexp[gen]
                    position = {'barcode':'-', 'father_container':'-', 'pos':'-'}
                    aliq_biobank += gen +'&'
                    volpreso=dizaliqexp[gen]['Used volume']
                    
                    label=''
                    if 'Label experiment' in dizaliqexp[gen]:
                        label=dizaliqexp[gen]['Label experiment']
                    cluster=''
                    if 'Cluster density' in dizaliqexp[gen]:
                        cluster=dizaliqexp[gen]['Cluster density']
                    runname=''
                    if 'Run name' in dizaliqexp[gen]:
                        runname=dizaliqexp[gen]['Run name']
                    aliquotBio[al.genId] ={'idaliquot': al.id, 'experimentid':plan , 'genId':gen, 'sample_features':'', 'owner':al.owner, 'volume':al.volume, 'concentration':al.concentration, 'barcode':position['barcode'], 'father_container':position['father_container'], 'pos':position['pos'], 'volumetaken': volpreso,'label':label,'run':runname,'cluster':cluster}
            
            # update info of the aliquot
            res = retrieveAliquots (aliq_biobank[:-1], user.username)
            for d in res['data']:
                print 'd',d
                values = d.split("&")
                if values[1]=='notavailable':
                    raise ErrorAliquot('Error: sample "'+dizaliqexp[gen]['Label experiment']+'" is not available')
                #se il campione e' esaurito non ho nessun valore, ma devo comunque far comparire il campione perche' devo poter inserire i suoi file
                elif values[1]=='notexist':
                    aliquotBio[values[0]]['volume'] = 'None'
                    aliquotBio[values[0]]['concentration'] = 'None'
                    aliquotBio[values[0]]['date'] = 'None'
                    aliquotBio[values[0]]['barcode'] = 'None'
                    aliquotBio[values[0]]['father_container'] = 'None'
                    aliquotBio[values[0]]['pos'] = 'None'
                else:
                    aliquotBio[values[0]]['volume'] = values[1]
                    aliquotBio[values[0]]['concentration'] = values[2]
                    aliquotBio[values[0]]['date'] = values[3]
                    aliquotBio[values[0]]['barcode'] = values[4]
                    aliquotBio[values[0]]['father_container'] = values[5]
                    aliquotBio[values[0]]['pos'] = values[6]
                resp['aliquots'].append(aliquotBio[values[0]])
            
            source=plan.request_id.source
            internal=False
            if source=='Internal':
                internal=True
            transaction.commit()
            return render_to_response('read_measures.html', resp, RequestContext(request,{'internal':internal}))
        except ErrorAliquot as e:
            print 'My exception occurred, value:', e.value
            transaction.rollback()
            variables = RequestContext(request, {'errore':e.value})
            return render_to_response('read_measures.html',variables)
        except Exception, e:
            print e
            transaction.rollback()
            variables = RequestContext(request, {'errore':True})
            return render_to_response('home.html',variables)
        finally:
            transaction.rollback()
    else:
        try:
            print request.FILES
            raw_data = json.loads(request.POST['aliquots_list'])
            featfinexp=Feature.objects.get(name='Finished experiment')
            featfileins=Feature.objects.get(name='File inserted')
            exp = Experiment.objects.get(id=request.session['idplan'])            

            values_to_send = {'info':[], 'exhausted':[]}
            aliquotExp = []

            filesUploaded = {}
            summary_aliquots =[]
            for aliquot_info in raw_data:

                al = Aliquot.objects.get(id=aliquot_info['idAliquot'])
                
                #imposto che per questa aliquota ho inserito i file, anche se non ho inserito nessun file realmente, ma e' solo 
                #per concludere la procedura di caricamento file per quel campione
                alexp=Aliquot_has_Experiment(aliquot_id=al,
                                             idExperiment=exp,
                                             feature_id=featfileins,
                                             value='True')
                alexp.save()
                fallito=False
                if 'failed' in request.POST:
                    if aliquot_info['failed']==True:
                        print aliquot_info['idAliquot'], 'failed'
                        fallito=True
                if not fallito:
                    for f in json.loads(aliquot_info['files']):
                        if not filesUploaded.has_key(f):
                            uploaded_file = [upfile for upfile in request.FILES.getlist('file') if upfile.name == f][0]
                            print 'namefile',uploaded_file.name
                            
                            destination = handle_uploaded_file(uploaded_file)
                            print destination
                            responseUpload = uploadRepFile({'operator':request.user.username}, destination)
                            print responseUpload
                            if responseUpload == 'Fail':
                                transaction.rollback()
                                return HttpResponseBadRequest("Error in reading the additional file/s.")
                            filesUploaded[f] = responseUpload
                            remove_uploaded_files([destination])
                                                        
                        me = MeasurementEvent(aliquot_id=al,experiment_id=exp, link_file=filesUploaded[f], namefile=f)
                        me.save()
                #lo devo fare solo se la sorgente e' esterna, cioe' e' la biobanca
                if exp.request_id.source!='Internal':
                    vol = float(aliquot_info['volume'])-float(aliquot_info['takenvol'])
                    if vol<0:
                        vol=0
                    #devo aggiornare il volume usato dell'aliquota
                    lalexp=Aliquot_has_Experiment.objects.filter(aliquot_id=al,idExperiment=exp,feature_id=featvol)
                    if len(lalexp)!=0:
                        lalexp[0].value=aliquot_info['takenvol']
                        lalexp[0].save()
                    values_to_send['info'].append(al.genId+"&"+ request.user.username + "&" + str(vol))
                    if aliquot_info['exhausted']:
                        values_to_send['exhausted'].append(al.genId)
                    if aliquot_info['failed']==True:
                        #devo aggiornare il valore del fail
                        lalexp=Aliquot_has_Experiment.objects.filter(aliquot_id=al,idExperiment=exp,feature_id=featfail)
                        if len(lalexp)!=0:
                            lalexp[0].value='True'
                            lalexp[0].save()
                    print 'values_to_send biobank',values_to_send
                    
                summary_aliquots.append({'aliquot':al.genId, 'nfiles':len(json.loads(aliquot_info['files'])), 'volumetaken': aliquot_info['takenvol'], 'barcode': aliquot_info['barcode'],'label':aliquot_info['label'],'cluster':aliquot_info['cluster'],'run':aliquot_info['run']})
            
            print 'filesUploaded',filesUploaded
            
            aliqexpfiniti = Aliquot_has_Experiment.objects.filter(idExperiment=exp,feature_id=featfinexp,value='True')
            print 'aliqexpfiniti',aliqexpfiniti
            aliqexpfileinseriti = Aliquot_has_Experiment.objects.filter(idExperiment=exp,feature_id=featfileins)
            print 'aliqexpfileinseriti',aliqexpfileinseriti
            #solo se il numero delle aliquote per cui e' stato inserito il file eguaglia il numero delle aliquote di quell'esperimento
            if len(aliqexpfiniti)==len(aliqexpfileinseriti):
                exp.time_executed = timezone.localtime(timezone.now())
                exp.save()
            
            # biobank interaction
            if len(values_to_send['info']) != 0:
                data = urllib.urlencode(values_to_send)
                try: #update info for the aliquots (volume and exhausted)
                    updateAliquots(data)
                except:
                    print "[NGS] - Biobank Unreachable"
                    transaction.rollback()
                    return HttpResponseBadRequest('Biobank Unreachable')
                
            request.session['summary_aliquots'] = summary_aliquots
            print 'summary aliquots', request.session['summary_aliquots']

            if request.session.has_key('idplan'):
                del request.session['idplan']
            request.session['measureserie'] = exp            
            
            transaction.commit()
            return HttpResponseRedirect(reverse('ngs.views.measure_event'))
        except Exception, e:
            print 'err',e
            transaction.rollback()
            variables = RequestContext(request, {'errore':True})
            return render_to_response('home.html',variables)
        finally:
            transaction.rollback()

@laslogin_required
@login_required
@permission_decorator('ngs.can_view_NGS_run_experiment')
def measure_event(request):
    resp = {}
    if request.session.has_key('summary_aliquots'):
        resp['summary_aliquots'] = request.session['summary_aliquots']
        del request.session['summary_aliquots']
    if request.session.has_key('measureserie'):
        resp['measureserie'] = request.session['measureserie']
        del request.session['measureserie']
    return render_to_response('measurementevent.html',resp, RequestContext(request))
