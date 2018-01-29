from __init__ import *


#per far vedere la pagina di selezione della richiesta in caso di convalida dei campioni
@laslogin_required
@login_required
@permission_decorator('ngs.can_view_NGS_validate_aliquots')
def select_request(request):
    if request.method == "GET":
        try:
            user_name = request.user
            request_operator = Request.objects.filter(idOperator=user_name, pending=False, timechecked__isnull =True).exclude(source='Internal')
            request_null = Request.objects.filter(idOperator__isnull=True, pending=False, timechecked__isnull =True).exclude(source='Internal')
            plans = list(chain(request_operator, request_null))
            return render_to_response('select_request.html', {'plans':plans}, RequestContext(request))
        except Exception, e:
            print 'err',e
            variables = RequestContext(request, {'errore':True})
            return render_to_response('home.html',variables)
    else:
        print request.POST
        raw_data = simplejson.loads(request.raw_post_data)
        print '[LBM] - Raw Data: "%s"' % raw_data
        idplan = ''
        if raw_data.has_key('idplan'):
            idplan = raw_data['idplan']
        request.session['idplan'] = idplan
        return HttpResponseRedirect(reverse('ngs.views.validate_samples'))

#vista per la convalida classica dei campioni pianificati tramite biobanca
@laslogin_required
@login_required
@permission_decorator('ngs.can_view_NGS_validate_aliquots')
@transaction.commit_manually
def validate_samples(request):
    if request.method == "GET":
        try:
            resp = {}
            user = auth.get_user(request)
            idplan = request.session['idplan']
            print 'idplan',idplan
            #if request.session.get('idplan'):
            #    del request.session['idplan']
            plan = Request.objects.get(id=idplan)
            resp['plan_session'] = plan
            print 'plan',plan

            resp['instruments'] = Instrument.objects.all()
            resp['kits'] = Kit.objects.all()
            resp['assay'] = Assay.objects.all()
            featvol=Feature.objects.get(name='Used volume')
            
            aliquots = Aliquot_has_Request.objects.filter(request_id=plan,feature_id=featvol)
            print 'aliquots',aliquots
            resp['aliquots'] = []
            aliq_biobank = ''
            aliquotBio = {}       
            
            for al in aliquots:
                print 'al',al
                position = {'barcode':'-', 'father_container':'-', 'pos':'-'}
                aliq_biobank += al.aliquot_id.genId +'&'
                aliquotBio[al.aliquot_id.genId] = {'idaliquot': al.aliquot_id.id, 'genId':al.aliquot_id.genId, 'sample_features':'', 'owner':al.aliquot_id.owner, 'volume':al.aliquot_id.volume, 'concentration':al.aliquot_id.concentration, 'barcode':position['barcode'], 'father_container':position['father_container'], 'pos':position['pos'], 'volumetaken': al.value}
            try:
                # update info of the aliquot
                res = retrieveAliquots (aliq_biobank[:-1], user.username)
                for d in res['data']:
                    print 'd',d
                    values = d.split("&")
                    aliquotBio[values[0]]['volume'] = values[1]
                    aliquotBio[values[0]]['concentration'] = values[2]
                    aliquotBio[values[0]]['date'] = values[3]
                    aliquotBio[values[0]]['barcode'] = values[4]
                    aliquotBio[values[0]]['father_container'] = values[5]
                    aliquotBio[values[0]]['pos'] = values[6]
                    resp['aliquots'].append(aliquotBio[values[0]])
            except Exception, e:
                print e
                transaction.rollback()
                variables = RequestContext(request, {'errore':True})
                return render_to_response('home.html',variables)
            transaction.commit()
            print resp
            return render_to_response('validate_samples.html', resp, RequestContext(request))
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
            print '[NGS] - Raw Data: "%s"' % raw_data
            if not raw_data.has_key('val_aliquots'):
                transaction.rollback()
                return HttpResponseBadRequest("Error")
            # operator info
            user = auth.get_user(request)
            operator = User.objects.get(username = user.username)
            print 'operator',operator
            # time of planning
            eventTime = timezone.localtime(timezone.now())
            # retrieve plan
            plan = Request.objects.get(id=raw_data['sessionid'])
            plan.timechecked = eventTime
            if plan.idOperator==None:
                plan.idOperator=operator
            plan.save()
            print 'plan',plan
            #e = Experiment(time_creation = eventTime, idInstrument = Instrument.objects.get(id=raw_data['instrumentid']),  idKit= Kit.objects.get(id=raw_data['kitid']), idAssay=Assay.objects.get(id=raw_data['assayid']), idOperator = operator, title= plan.title, description=plan.title)
            e = Experiment(time_creation = eventTime, idOperator = operator, title= plan.title, description=plan.description,request_id=plan)
            e.save()
            print 'e',e

            aliquotExp = []
            featfailed=Feature.objects.get(name='Failed')
            featvol=Feature.objects.get(name='Used volume')
            featfinish=Feature.objects.get(name='Finished experiment')
            for alIdentifier, aliquot in raw_data['val_aliquots'].items():
                al = Aliquot.objects.get(id=aliquot['idaliquot'])
                
                alexp=Aliquot_has_Experiment(aliquot_id=al,
                                             idExperiment=e,
                                             feature_id=featfailed,
                                             value='False')
                alexp.save()
                print 'alexp',alexp
                alexp=Aliquot_has_Experiment(aliquot_id=al,
                                             idExperiment=e,
                                             feature_id=featvol,
                                             value=str(aliquot['volumetaken']))
                alexp.save()
                print 'alexp',alexp
                alexp=Aliquot_has_Experiment(aliquot_id=al,
                                             idExperiment=e,
                                             feature_id=featfinish,
                                             value='True')
                alexp.save()
                aliquotExp.append(al.genId)
            
            #update info for the aliquots (set only experiment finished)
            try: 
                setExperiment(aliquotExp)
            except:
                print "[NGS] - Biobank Unreachable"
                transaction.rollback()
                return HttpResponseBadRequest('Biobank Unreachable')

            transaction.commit()
            if raw_data['status'] == 'continue':
                # the user continues with this session and checks the aliquot preparation
                request.session['idplan'] = e.id
                print request.session['idplan']
                return HttpResponseRedirect(reverse('ngs.views.read_measures'))
            elif raw_data['status'] == 'stop':
                # if the user stops at the virtual plan
                request.session['val_aliquots'] = raw_data['val_aliquots']
                request.session['plan'] = plan
                return HttpResponseRedirect(reverse('ngs.views.validated_request'))
        except Exception, e:
            print e
            transaction.rollback()
            variables = RequestContext(request, {'errore':True})
            return render_to_response('home.html',variables)
        finally:
            transaction.rollback()


# report of hybridization plan
@laslogin_required
@login_required
@permission_decorator('ngs.can_view_NGS_validate_aliquots')
def validated_request(request):
    val_aliquots = request.session['val_aliquots']
    plan = request.session['plan']
    print val_aliquots

    if request.session.get('val_aliquots'):
        del request.session['val_aliquots']
    if request.session.get('plan'):
        del request.session['plan']

    return render_to_response('reportValidation.html', {'plan':plan, 'val_aliquots':val_aliquots }, RequestContext(request))

#view for upload file and get of the initial page of new request
@laslogin_required
@login_required
@permission_decorator('ngs.can_view_NGS_define_experiment')
@transaction.commit_manually
def select_validated_session(request):

    if request.method == "GET":
        # GET method
        try:
            user = auth.get_user(request)
            user_name = User.objects.get(username = user.username)
            request_operator = Request.objects.filter(idOperator=user_name, pending=False, timechecked__isnull =False, time_executed__isnull=True).exclude(source='Internal')
            request_null = Request.objects.filter(idOperator__isnull=True, pending=False, timechecked__isnull =False, time_executed__isnull=True).exclude(source='Internal')
            plans = list(chain(request_operator, request_null))
            transaction.commit()
            return render_to_response('select_experimental_session.html', {'plans':plans}, RequestContext(request))
        except:
            transaction.rollback()
            return HttpResponseBadRequest("Page not available")
        finally:
            transaction.rollback()
    else:
        raw_data = simplejson.loads(request.raw_post_data)
        print '[LBM] - Raw Data: "%s"' % raw_data
        idplan = ''
        if raw_data.has_key('idplan'):
            idplan = raw_data['idplan']
        request.session['idplan'] = idplan
        return HttpResponseRedirect(reverse('ngs.views.define_experiment'))

