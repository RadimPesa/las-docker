from __init__ import *

#######################################
#Request views
#######################################

@laslogin_required
@login_required
@permission_decorator('ngs.can_view_NGS_upload_request')
@transaction.commit_manually
def pending_request(request):
    if request.method == "GET":
        # GET method
        try:
            user = auth.get_user(request)
            user_name = User.objects.get(username = user.username)
            plans = Request.objects.filter(pending=True, timechecked__isnull =True)
            transaction.commit()
            return render_to_response('pending_request.html', {'plans':plans}, RequestContext(request))
        except:
            transaction.rollback()
            return HttpResponseBadRequest("Page not available")
        finally:
            transaction.rollback()
    else:
        try:
            raw_data = simplejson.loads(request.raw_post_data)
            print '[NGS] - Raw Data: %s' % raw_data['idplan']
            return HttpResponseRedirect(reverse('ngs.views.upload_request', kwargs={'request_id':raw_data['idplan']}) )
        except:
            return HttpResponseBadRequest("Page not available")

#per far comparire la schermata con la richiesta pendente appena pianificata dalla biobanca
@laslogin_required
@login_required
@permission_decorator('ngs.can_view_NGS_upload_request')
@transaction.commit_manually
def upload_request(request, request_id):
    resp ={}
    if request.method == "GET":
        # GET method
        try:
            print 'GET upload_request'
            print 'request_id',request_id
            resp['users'] =  User.objects.all()
            requestPending = Request.objects.get (id=request_id)
            if not requestPending.pending:
                raise Exception('Not pending request')
            featvol=Feature.objects.get(name='Used volume')
            lisreq=Aliquot_has_Request.objects.filter(request_id=requestPending,feature_id=featvol)
            print 'lisreq',lisreq
            resp['requested_aliquots'] = lisreq
            resp['request_session'] = requestPending
            resp['idplan'] = request_id
            transaction.commit()
            return render_to_response('request_definition.html', resp, RequestContext(request))
        except Exception, e:
            print e
            transaction.rollback()
            return HttpResponseBadRequest("Page not available! " + e.args[0])
        finally:
            transaction.rollback()

#per salvare la richiesta pendente proveniente dalla biobanca
@laslogin_required
@login_required
@permission_decorator('ngs.can_view_NGS_upload_request')
@transaction.commit_manually
def confirm_request(request):
    if request.method == "POST":
        try:
            raw_data = simplejson.loads(request.raw_post_data)
            print 'raw_data',raw_data
            user = auth.get_user(request)
            requestPending = Request.objects.get (id=raw_data['idplan'])
            requestPending.pending = False
            requestPending.title = raw_data['title']
            requestPending.description = raw_data['description']
            if raw_data['operator']!='':
                operator = User.objects.get(username = raw_data['operator'])
                print 'operator',operator
                requestPending.idOperator = operator
            requestPending.save()
            print 'requestPending',requestPending
            request.session['plan'] = requestPending
            aliquotBio = {}
            aliquotExp = []
            aliq_biobank = ''
            featvol=Feature.objects.get(name='Used volume')
            aliquots = Aliquot_has_Request.objects.filter(request_id=requestPending,feature_id=featvol)
            for al in aliquots:
                print 'al req',al
                position = {'barcode':'-', 'father_container':'-', 'pos':'-'}
                aliq_biobank += al.aliquot_id.genId +'&'
                aliquotBio[al.aliquot_id.genId] = {'idaliquot': al.aliquot_id.id, 'genId':al.aliquot_id.genId, 'sample_features':'', 'owner':al.aliquot_id.owner, 'volume':al.aliquot_id.volume, 'concentration':al.aliquot_id.concentration, 'barcode':position['barcode'], 'father_container':position['father_container'], 'pos':position['pos'], 'volumetaken': al.value}
                aliquotExp.append(al.aliquot_id.genId)
            try:
                # update info of the aliquot
                res = retrieveAliquots (aliq_biobank[:-1], user.username)
                for d in res['data']:
                    values = d.split("&")
                    print 'values',values
                    if len(values) <6:
                        return HttpResponseBadRequest("Error: sample "+values[0]+" is not available")
                    aliquotBio[values[0]]['volume'] = values[1]
                    aliquotBio[values[0]]['concentration'] = values[2]
                    aliquotBio[values[0]]['date'] = values[3]
                    aliquotBio[values[0]]['barcode'] = values[4]
                    aliquotBio[values[0]]['father_container'] = values[5]
                    aliquotBio[values[0]]['pos'] = values[6]
            except Exception, e:
                print e
                transaction.rollback()
                return HttpResponseBadRequest("Error in saving data")
            request.session['aliquots'] = aliquotBio
            transaction.commit()
            return HttpResponseRedirect(reverse('ngs.views.create_request'))
        except Exception, e:
            print e
            transaction.rollback()
            return HttpResponseBadRequest("Error in saving data")
        finally:
            transaction.rollback()

@laslogin_required
@login_required
@permission_decorator('ngs.can_view_NGS_upload_request')
@transaction.commit_manually
def create_request(request):
    resp = {}
    if request.method == "GET":
        try:
            if request.session.has_key('aliquots'):
                resp['aliquots'] = request.session['aliquots']
            if request.session.has_key('plan'):
                resp['plan'] = request.session['plan']
            request.session['idplan'] = request.session['plan'].id
            transaction.commit()
            return render_to_response('request.html', resp, RequestContext(request))
        except:
            transaction.rollback()
            return HttpResponseBadRequest("Page not available")
        finally:
            transaction.rollback()
            
#Per far comparire il form in cui inserire i valori della procedura
@transaction.commit_on_success
@laslogin_required
@login_required
@permission_decorator('ngs.can_view_NGS_upload_request')
def insert_sample(request):
    try:
        if request.method == "GET":
            if 'reportInsertSample' in request.session:
                del request.session['reportInsertSample']
            #mi da' una lista di dizionari che devo ordinare alfabeticamente in base al nome
            lista=retrieveSources()
            #lista con i nomi delle sorgenti ordinati alfabeticamente
            lisnomi=[]
            #diz con chiave il nome e valore le due lettere maiuscole
            diznomi={}
            for diz in lista:
                #prendo solo le sorgenti di tipo Hospital
                if diz['type']=='Hospital':
                    if diz['name'] not in lisnomi:            
                        lisnomi.append(diz['name'])
                        diznomi[diz['name']]=diz['internalName']
            lisnomi=sorted(lisnomi, key=str.lower)
            print 'diznomi',diznomi
            
            listessuti=json.loads(retrieveTissue())
            #lista con i nomi dei tessuti ordinati alfabeticamente
            listess=[]
            #diz con chiave il nome e valore le due lettere maiuscole di abbreviazione
            diztess={}
            listessuti=listessuti['data']
            for val in listessuti:
                if val['type']=='Metastasis':
                    listess.append(str(val['longName']))
                    diztess[val['longName']]=val['abbreviation']
            listess=sorted(listess, key=str.lower)
            print 'listess',listess
            
            listum=json.loads(retrieveCollectionType())
            #lista con i nomi dei tumori ordinati alfabeticamente
            listumfin=[]
            #diz con chiave il nome e valore le tre lettere maiuscole di abbreviazione
            diztum={}
            listum=listum['data']
            for val in listum:
                if val['type']!='Internal':
                    listumfin.append(str(val['longName']))
                    diztum[val['longName']]=val['abbreviation']
            listumfin=sorted(listumfin, key=str.lower)
            print 'listumfin',listumfin
            variables = RequestContext(request,{'diznomi':diznomi,'lisnomi':lisnomi,'diztess':diztess,'listess':listess,'diztum':diztum,'listumfin':listumfin })
            return render_to_response('insertSample.html',variables)
        elif request.method=='POST':
            print request.POST
            if 'salva' in request.POST:
                try:
                    lissample=json.loads(request.POST['sample'])
                    print 'lissample',lissample
                    titoloreq=request.POST['titlereq']
                    description=request.POST['description']
                    dizdescription=json.loads(request.POST['dizdescr'])
                    print 'dizdescr',dizdescription
                    #devo comunicare i dati alla biobanca che salva i nuovi campioni inseriti
                    #devo per forza salvare prima nella biobanca perche' ho bisogno di sapere il genid creato ex-novo
                    res=json.loads(saveExternAliquots(lissample,request.user.username))
                    dizfin=res['dictlabelgen']
                    print 'dizfin',dizfin
                    featvolfornito=Feature.objects.get(name='Provided volume')
                    featcapture=Feature.objects.get(name='Capture type')
                    #devo creare una richiesta e le aliquote collegate con la loro label
                    #metto l'operatore a null perche' e' quello che dovra' eseguire l'esperimento e non so chi sara'.
                    #Invece l'utente loggato inserisce solo la richiesta che verra' eseguita poi da un altro
                    req=Request(idOperator=None,
                              timestamp=timezone.localtime(timezone.now()),
                              title=titoloreq,
                              description=description,
                              owner=request.user.username,
                              pending=False,
                              source='Internal')
                    req.save()
                    print 'req',req
                    
                    dizfeat={}
                    listafeature=Feature.objects.all()
                    for feat in listafeature:
                        dizfeat[feat.name]=feat
                    
                    #dizfin ha chiave la label e valore un dizionario
                    for s in lissample:
                        label=s['label']
                        print 'label',label
                        val=dizfin[label]
                        print 'val',val
                        descr=dizdescription[label]
                        a=Aliquot(genId=val['gen'],
                                  date=datetime.date.today(),
                                  owner=s['user'],
                                  exhausted=False,
                                  label_request=label,
                                  description=descr)
                        a.save()
                        print 'a',a
                        #salvo il volume fornito per l'esperimento. Nella schermata dopo lo faro' comparire nel campo apposta.
                        volume=None
                        if 'volumefornito' in s:
                            volume=float(s['volumefornito'])
                        alr=Aliquot_has_Request(aliquot_id=a,
                                                request_id=req,
                                                feature_id=featvolfornito,
                                                value=volume)
                        alr.save()
                        alr=Aliquot_has_Request(aliquot_id=a,
                                                request_id=req,
                                                feature_id=featcapture,
                                                value=s['capture'])
                        alr.save()
                        
                        for k,v in s.items():
                            print 'k',k
                            #print 'v',v
                            if k in dizfeat and v!='' and v!='---------':                      
                                alreq=Aliquot_has_Request(aliquot_id=a,
                                                          request_id=req,
                                                          feature_id=dizfeat[k],
                                                          value=v)
                                alreq.save()
                                print 'alreq',alreq
                    
                    email = LASEmail (functionality=get_functionality(), wgString=get_WG_string())
                    
                    #user1=User.objects.get(username='emanuele.geda')
                    #user2=User.objects.get(username='eugenia.zanella')
                    user1=User.objects.get(username='michela.buscarino')
                    user2=User.objects.get(username='alice.bartolini')
                    
                    msg=['Planned samples:']
                    msg.append('N\tLabel\tSample name\tCapture type')
                    wgList1=WG.objects.filter(id__in=WG_User.objects.filter(user=user1).values_list('WG',flat=True).distinct())
                    wgList2=WG.objects.filter(id__in=WG_User.objects.filter(user=user2).values_list('WG',flat=True).distinct())
                    wglistot=list(set(wgList1)|set(wgList2))
                    print 'wgtot',wglistot
                    for wg in wglistot:
                        print 'wg',wg.name
                        email.addMsg([wg.name], msg)
                        i=1
                        for samp in lissample:
                            email.addMsg([wg.name],[str(i)+'\t'+samp['label']+'\t'+samp['Sample name']+'\t'+samp['capture']])
                            i+=1
                    
                        email.addRoleEmail([wg.name], 'Planner', [user1.username,user2.username])
                        email.addRoleEmail([wg.name], 'Executor', [request.user.username])
                                        
                    try:
                        email.send()
                    except Exception, e:
                        print 'errore',e
                        return HttpResponse(json.dumps({'data':'errore'}))
                    request.session['reportInsertSample']=lissample
                    return HttpResponse(json.dumps(res))
                except Exception, e:
                    print 'err',e
                    transaction.rollback()
                    return HttpResponse(json.dumps({'data':'errore'}))
    except Exception, e:
        print 'err',e
        transaction.rollback()
        variables = RequestContext(request, {'errore':True})
        return render_to_response('home.html',variables)
        
#Per far comparire la schermata finale dell'inserimento dei campioni
@laslogin_required
@login_required
@permission_decorator('ngs.can_view_NGS_upload_request')
def insert_sample_final(request):
    lissample=request.session['reportInsertSample']
    print 'lissample',lissample
    variables = RequestContext(request,{'lissample':lissample})
    return render_to_response('report_insert_samples.html',variables)
