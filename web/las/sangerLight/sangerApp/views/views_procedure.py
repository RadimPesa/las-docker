from __init__ import *

#######################################
#Experiments views
#######################################


#view for upload file and get of the initial page of new request
@laslogin_required
@login_required
@permission_decorator('sangerApp.can_view_SAM_validate_aliquots')
@transaction.commit_manually
def select_request(request):

    if request.method == "GET":
        # GET method
        try:
            user = auth.get_user(request)
            user_name = User.objects.get(username = user.username)
            request_operator = Request.objects.filter(idOperator=user_name,  pending=False, timechecked__isnull =True, time_executed__isnull =True)
            request_null = Request.objects.filter(idOperator__isnull=True,  pending=False, timechecked__isnull =True, time_executed__isnull =True)
            plans = list(chain(request_operator, request_null))
            transaction.commit()
            return render_to_response('select_request.html', {'plans':plans}, RequestContext(request))
        except Exception, e:
            print e
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
        return HttpResponseRedirect(reverse('sangerApp.views.validate_samples'))



#view for upload file and get of the initial page of new request
@laslogin_required
@login_required
@permission_decorator('sangerApp.can_view_SAM_validate_aliquots')
@transaction.commit_manually
def validate_samples(request):
    if request.method == "GET":
        try:
            resp = {}
            user = auth.get_user(request)
            idplan = request.session['idplan']
            #if request.session.get('idplan'):
            #    del request.session['idplan']
            plan = Request.objects.get(id=idplan)
            resp['plan_session'] = plan
            print plan

            aliquots = Aliquot_has_Request.objects.filter(request_id=plan)
            print aliquots
            resp['aliquots'] = []
            aliq_biobank = ''
            aliquotBio = {}

            for al in aliquots:
                print al
                position = {'barcode':'-', 'father_container':'-', 'pos':'-'}
                aliq_biobank += al.aliquot_id.genId +'&'
                aliquotBio[al.aliquot_id.genId] = {'idaliquot': al.aliquot_id.id, 'genId':al.aliquot_id.genId, 'sample_features':al.sample_features, 'owner':al.aliquot_id.owner, 'volume':al.aliquot_id.volume, 'concentration':al.aliquot_id.concentration, 'barcode':position['barcode'], 'father_container':position['father_container'], 'pos':position['pos'], 'volumetaken': al.volumetaken}
            try:
                # update info of the aliquot
                res = retrieveAliquots (aliq_biobank[:-1], user.username)
                for d in res['data']:
                    print d
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
                return HttpResponseBadRequest('Aliquots not available')
            transaction.commit()
            print resp
            return render_to_response('validate_samples.html', resp, RequestContext(request))
        except Exception, e:
            print e
            transaction.rollback()
            return HttpResponseBadRequest('Page not available')
        finally:
            transaction.rollback()
    else:
        try:
            raw_data = simplejson.loads(request.raw_post_data)
            print '[LBM] - Raw Data: "%s"' % raw_data
            if not raw_data.has_key('val_aliquots'):
                transaction.rollback()
                return HttpResponseBadRequest("Error")
            # operator info
            user = auth.get_user(request)
            operator = User.objects.get(username = user.username)
            # time of planning
            eventTime = datetime.datetime.now()
            # retrieve plan
            plan = Request.objects.get(id=raw_data['sessionid'])
            plan.timechecked = eventTime
            plan.save()
            values_to_send = {'info':[], 'exhausted':[]}
            aliquotExp = []
            print plan
            # update info aliquot with virtual chips
            for alIdentifier, aliquot in raw_data['val_aliquots'].items():
                al = Aliquot.objects.get(id=aliquot['idaliquot'])
                al.volume = float(aliquot['volume'])-float(aliquot['volumetaken'])
                al.concentration = float(aliquot['concentration'])
                al.exhausted = aliquot['exhausted']
                al.save()  # update data to send to biobank
                values_to_send['info'].append(al.genId+"&"+ user.username + "&" + str(al.volume))
                aliquotExp.append(al.genId)
                if al.exhausted == True:
                    values_to_send['exhausted'].append(al.genId)
            # biobank interaction only for internal aliquots    
            if len(values_to_send['info']) != 0:
                data = urllib.urlencode(values_to_send)
                try: #update info for the aliquots
                    updateAliquots(data)
                    setExperiment(aliquotExp)
                except:
                    print "[LBM] - Biobank Unreachable"
                    transaction.rollback()
                    return HttpResponseBadRequest('Biobank Unreachable')
            transaction.commit()
            if raw_data['status'] == 'continue':
                # the user continues with this session and schecks the aliquot preparation
                request.session['idplan'] = plan.id
                print request.session['idplan']
                return HttpResponseRedirect(reverse('sangerApp.views.define_experiment'))
            elif raw_data['status'] == 'stop':
                # if the user stops at the virtual plan
                request.session['val_aliquots'] = raw_data['val_aliquots']
                request.session['plan'] = plan
                return HttpResponseRedirect(reverse('sangerApp.views.validated_request'))
        except Exception, e:
            print e
            transaction.rollback()
            return HttpResponseBadRequest("Error")
        finally:
            transaction.rollback()


# report of hybridization plan
@laslogin_required
@login_required
#@user_passes_test(lambda u: u.has_perm('sangerApp.can_view_SAM_validate_aliquots'),login_url=reverse_lazy('sangerApp.views.error'))
@permission_decorator('sangerApp.can_view_SAM_validate_aliquots')
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
@permission_decorator('sangerApp.can_view_SAM_run_experiment')
@transaction.commit_manually
def select_validated_session(request):

    if request.method == "GET":
        # GET method
        try:
            user = auth.get_user(request)
            user_name = User.objects.get(username = user.username)
            request_operator = Request.objects.filter(idOperator=user_name, pending=False, timechecked__isnull =False, time_executed__isnull=True)
            request_null = Request.objects.filter(idOperator__isnull=True, pending=False, timechecked__isnull =False, time_executed__isnull=True)
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
        return HttpResponseRedirect(reverse('sangerApp.views.define_experiment'))


#view for define the experiment and the layout
@laslogin_required
@login_required
@permission_decorator('sangerApp.can_view_SAM_run_experiment')
@transaction.commit_manually
def define_experiment(request):
    if request.method == 'GET':
        try:
            if 'assayLabel' in request.GET:
                assay = Assay.objects.get(pk=request.GET['assayLabel'])
                jsonData = {'name':assay.name, 'targets':[]}
                jsonData['targets'] = retrieveTargets(list(Assay_has_Probe.objects.filter(id_assay=assay).values_list('probe', flat=True)))
                return HttpResponse(json.dumps(jsonData))

            user = auth.get_user(request)
            operator = User.objects.get(username = user.username)

            planid = request.session['idplan']
            plan = Request.objects.get(id=planid)

            urlAnnot = Urls.objects.get(id_webservice=WebService.objects.get(name='annotation'))
            # get aliquots for this session
            aliquots = Aliquot_has_Request.objects.filter(request_id=plan).order_by('id')
            # get gene and probes in the DB
            print Sample.objects.filter( idExperiment__in = Experiment.objects.filter(idOperator=operator), probe__isnull=False).values('probe').annotate(count_used=Count('id')).order_by('count_used')
            try:
                targets = Sample.objects.filter( idExperiment__in = Experiment.objects.filter(idOperator=operator), probe__isnull=False).values('probe').annotate(count_used=Count('id')).order_by('-count_used')
            except:
                targets = []

            print targets
            
            targets = retrieveTargets ([t['probe'] for t in targets[:10]])

            # get the instruments
            instruments = Instrument.objects.all()
            assays = Assay.objects.filter(WG__name__in=get_WG()).values('pk', 'name', 'WG__name' ).distinct()

            # TODO get the layouts from the storage
            #layouts = retrieveLayouts()
            #print layouts
            transaction.commit()
            return render_to_response('define_experiment.html', {'plan':plan, 'aliquots':aliquots, 'targets':targets, 'instruments':instruments, 'urlAnnot':urlAnnot.url, 'assays':assays}, RequestContext(request))
        except Exception, e:
            print e
            transaction.rollback()
            return HttpResponseBadRequest("Page not available")
        finally:
            transaction.rollback()
    else:
        try:
            raw_data = simplejson.loads(request.raw_post_data)
            print raw_data
            now = datetime.datetime.now()
            user = auth.get_user(request)
            operator = User.objects.get(username = user.username)
            # create new experiment

            instrument = Instrument.objects.get(id=raw_data['experiment']['idinstrument'])
            print instrument
            
            # update request
            plan = Request.objects.get(id=raw_data['experiment']['idplan'])
            plan.time_executed = datetime.datetime.now()
            plan.save()
            print plan

            exp = Experiment (time_creation = datetime.datetime.now(), idOperator = operator, idInstrument=instrument, description=plan.description, title=plan.title )
            print exp
            exp.save()
            savedSamples = []
            #define samples

            aliquots = Aliquot_has_Request.objects.filter(request_id=plan)

            res = retrieveTargets(raw_data['targets'])
            targets = {}
            for r in res:
                targets[r['uuid']] = r

            for al in aliquots:
                for targetUUID in raw_data['targets']:
                    sample = Sample(idAliquot_has_Request = al, probe = targetUUID, idExperiment=exp, time_creation=now)
                    sample.save()
                    summary = {'genid': al.aliquot_id.genId}
                    summary.update( targets[targetUUID] )
                    savedSamples.append(summary)

            request.session['samples'] = savedSamples
            request.session['plan'] = exp
            transaction.commit()
            return HttpResponseRedirect(reverse('sangerApp.views.layoutExperiment'))
        except Exception, e:
            print e
            transaction.rollback()
            return HttpResponseBadRequest("Bad request")
        finally:
            transaction.rollback()


#view for define the experiment and the layout
@laslogin_required
@login_required
@permission_decorator('sangerApp.can_view_SAM_run_experiment')
def layoutExperiment(request):
    samples = request.session['samples']
    plan = request.session['plan']

    if request.session.get('samples'):
        del request.session['samples']
    if request.session.get('plan'):
        del request.session['plan']

    return render_to_response('layout_experiment.html', {'plan':plan, 'samples':samples }, RequestContext(request))

