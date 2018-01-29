from __init__ import *

#######################################
# Hybridization
#######################################

# plan the hybridization
@laslogin_required
@login_required
@permission_decorator('MMM.can_view_MMM_plan_hybridization')
@transaction.commit_manually
def plan_hybrid(request):
    resp = {}
    if request.method == 'POST':
        try:
            raw_data = simplejson.loads(request.raw_post_data)
            print '[MMM] - Raw Data: "%s"' % raw_data
            if not raw_data.has_key('sel_aliquots'):
                transaction.rollback()
                return HttpResponseBadRequest("Error")
            # operator info
            user = auth.get_user(request)
            operator = User.objects.get(username = user.username)
            # time of planning
            eventTime = datetime.datetime.now()
            # protocol and instrument
            protocol = HybProtocol.objects.get(name=raw_data['hybrid_prot']['protocol'])
            instrument = Instrument.objects.get(name=raw_data['hybrid_prot']['instrument'])
            # define planning
            plan = HybridPlan(idOperator=operator, timeplan=eventTime, idHybProtocol=protocol, idInstrument=instrument)
            plan.save()
            
            # update info aliquot with virtual chips
            for chip, infoChip in raw_data['chips'].items():
                i = 0
                for aliquot in infoChip['pos']:
                    al = Aliquot_has_Request.objects.get(id= aliquot)
                    al.idHybPlan = plan
                    al.virtual_chip = chip
                    al.virtual_order = i
                    al.save()
                    i += 1
            
            transaction.commit()
            if raw_data['status'] == 'continue':
                # the user continues with this session and schecks the aliquot preparation
                request.session['idplan'] = plan.id
                return HttpResponseRedirect(reverse('MMM.views.check_hybrid'))
            elif raw_data['status'] == 'stop':
                # if the user stops at the virtual plan
                request.session['chips'] = raw_data['chips']
                request.session['hybrid_prot'] = raw_data['hybrid_prot']
                request.session['sel_aliquots'] = raw_data['sel_aliquots']
                request.session['plan'] = plan
                return HttpResponseRedirect(reverse('MMM.views.plan_view'))
        except Exception, e:
            print e
            transaction.rollback()
            return HttpResponseBadRequest("Error")
        finally:
            transaction.rollback()
    else:
        try:            
            # GET method
            user = auth.get_user(request)
            user_name = User.objects.get(username = user.username)

            request_operator = Request.objects.filter(idOperator=user_name, pending=False) 
            request_null = Request.objects.filter(idOperator__isnull=True, pending=False)
            requests = list(chain(request_operator, request_null))

            alreq = Aliquot_has_Request.objects.filter(idHybPlan__isnull=True, request_id__in = requests).exclude(aliquot_id__in=Aliquot.objects.filter(exhausted=True)).order_by('request_id', 'id')

            hyb_form = HybrProtForm()
            
            resp['hyb_form'] = hyb_form
            resp['alreq'] = alreq            
            resp['protocol'] = HybProtocol.objects.all()
            
            transaction.commit()
            print resp
            return render_to_response('pre_hybrid.html',resp, context_instance=RequestContext(request))
        except:
            transaction.rollback()
            return HttpResponseBadRequest("Page not available")
        finally:
            transaction.rollback()


# report of hybridization plan
@laslogin_required
@login_required
@permission_decorator('MMM.can_view_MMM_plan_hybridization')
def plan_view(request):
    chips = request.session['chips']
    hybrid_prot = request.session['hybrid_prot']
    sel_aliquots = request.session['sel_aliquots']
    plan = request.session['plan']

    # build the data structure for the report
    for barcode, chipInfo in chips.items():
        posInfo = []
        for i in chipInfo['pos']:
            posInfo.append(sel_aliquots[i])
        chipInfo['pos'] = posInfo
    print chips
    
    if request.session.get('sel_aliquots'):
        del request.session['sel_aliquots']
    if request.session.get('hybrid_prot'):
        del request.session['hybrid_prot']
    if request.session.get('chips'):
        del request.session['chips']
    if request.session.get('plan'):
        del request.session['plan']

    return render_to_response('reportPlan.html', {'chips':chips, 'hybrid_prot':hybrid_prot, 'plan':plan }, RequestContext(request))


# select virtual plan
@laslogin_required
@login_required
@permission_decorator('MMM.can_view_MMM_validate_hybridization')
@transaction.commit_manually
def select_plan(request):
    if request.method =='GET':
        try:
            user = auth.get_user(request)
            operator = User.objects.get(username = user.username)
            plans = HybridPlan.objects.filter(idOperator=operator, timecheck__isnull=True).order_by('timeplan')
            print plans
            transaction.commit()
            return render_to_response('select_plan.html', {'plans':plans}, RequestContext(request))
        except:
            transaction.rollback()
            return HttpResponseBadRequest('Page not available')
        finally:
            transaction.rollback()
    elif request.method == 'POST':
        raw_data = simplejson.loads(request.raw_post_data)
        print '[MMM] - Raw Data: "%s"' % raw_data
        idplan = ''
        if raw_data.has_key('idplan'):
            idplan = raw_data['idplan']
        request.session['idplan'] = idplan
        return HttpResponseRedirect(reverse('MMM.views.check_hybrid'))



# check hybridization of aliquots
@laslogin_required
@login_required
@permission_decorator('MMM.can_view_MMM_validate_hybridization')
@transaction.commit_manually
def check_hybrid(request):
    if request.method =='GET':
        try:
            resp = {}
            user = auth.get_user(request)
            idplan = request.session['idplan']
            '''
            if request.session.get('idplan'):
                del request.session['idplan']
            '''
            plan = HybridPlan.objects.get(id=idplan)
            resp['plan_session'] = plan
            print plan
    
            aliquots = Aliquot_has_Request.objects.filter(idHybPlan=plan).values('aliquot_id__genId', 'aliquot_id__sample_identifier','aliquot_id__owner', 'aliquot_id','sample_features','exp_group','aliquot_id__volume','aliquot_id__concentration').annotate(count=Count('id'))
            print aliquots
            resp['aliquots'] = []
            aliq_biobank = ''
            aliquotBio = {}

            for al in aliquots:
                position = {'barcode':'-', 'father_container':'-', 'pos':'-', 'rack_pos':'-', 'rack':'-', 'freezer':'-'}
                
                if al['aliquot_id__genId']:
                    aliq_biobank += al['aliquot_id__genId'] +'&'
                    aliquotBio[al['aliquot_id__genId']] = {'idaliquot': al['aliquot_id'], 'genId':al['aliquot_id__genId'], 'sample_features':al['sample_features'], 'owner':al['aliquot_id__owner'], 'exp_group':al['exp_group'], 'volume':al['aliquot_id__volume'], 'concentration':al['aliquot_id__concentration'], 'barcode':position['barcode'], 'father_container':position['father_container'], 'pos':position['pos'], 'rack_pos':position['rack_pos'], 'rack':position['rack'], 'freezer':position['freezer'], 'replicates':al['count']}
                else:
                    resp['aliquots'].append({'idaliquot': al['aliquot_id'], 'genId':al['aliquot_id__genId'], 'sample_features':al['sample_features'], 'owner':al['aliquot_id__owner'], 'exp_group':al['exp_group'], 'volume':al['aliquot_id__volume'], 'concentration':al['aliquot_id__concentration'], 'barcode':al['aliquot_id__sample_identifier'], 'father_container':position['father_container'], 'pos':position['pos'], 'rack_pos':position['rack_pos'], 'rack':position['rack'], 'freezer':position['freezer'], 'replicates':al['count']})
            try:
                # update info of the aliquot
                if len(aliq_biobank) > 0:
                    res = retrieveAliquots (aliq_biobank[:-1], user.username) 
                    print res
                    for d in res['data']:
                        values = d.split("&")
                        aliquotBio[values[0]]['volume'] = values[1]
                        aliquotBio[values[0]]['concentration'] = values[2]
                        aliquotBio[values[0]]['date'] = values[3]
                        aliquotBio[values[0]]['barcode'] = values[4]
                        aliquotBio[values[0]]['father_container'] = values[5]
                        aliquotBio[values[0]]['pos'] = values[6]
                        aliquotBio[values[0]]['rack_pos'] = values[7]
                        aliquotBio[values[0]]['rack'] = values[8]
                        aliquotBio[values[0]]['freezer'] = values[9]
                        resp['aliquots'].append(aliquotBio[values[0]])
            except Exception, e:
                print e
                transaction.rollback()
            transaction.commit()
            print 'render page'
            print resp
            return render_to_response('check_hybrid.html', resp, RequestContext(request))
        except Exception, e:
            print e
            transaction.rollback()
            return HttpResponseBadRequest('Page not available')
        finally:
            transaction.rollback()
    else:
        try:
            raw_data = simplejson.loads(request.raw_post_data)
            print '[MMM] - Raw Data: "%s"' % raw_data
            if not raw_data.has_key('val_aliquots'):
                transaction.rollback()
                return HttpResponseBadRequest("Error")
            # operator info
            user = auth.get_user(request)
            operator = User.objects.get(username = user.username)
            # time of planning
            eventTime = datetime.datetime.now()
            # retrieve plan
            plan = HybridPlan.objects.get(id=raw_data['sessionid'])
            plan.timecheck = eventTime
            plan.save()
            values_to_send = {'info':[], 'exhausted':[]}
            aliquotExp = []
            print plan
            # update info aliquot with virtual chips
            for alIdentifier, aliquot in raw_data['val_aliquots'].items():
                al = Aliquot.objects.get(id=aliquot['idaliquot'])
                al.volume -= float(aliquot['cRNAVolume'])
                al.exhausted = aliquot['exhausted']
                al.save()  # update data to send to biobank
                if al.genId:
                    aliquotExp.append(al.genId)
                    values_to_send['info'].append(al.genId+"&"+ user.username + "&" + str(al.volume))
                    if al.exhausted == True:
                        values_to_send['exhausted'].append(al.genId)

            # biobank interaction only for internal aliquots
            if len(values_to_send['info']) != 0:
                data = urllib.urlencode(values_to_send)
                try: #update info for the aliquots
                    updateAliquots(data)
                    setExperiment(aliquotExp)
                except:
                    print "[MMM] - Biobank Unreachable"
                    transaction.rollback()
                    return HttpResponseBadRequest('Biobank Unreachable')
            transaction.commit()
            if raw_data['status'] == 'continue':
                # the user continues with this session and schecks the aliquot preparation
                request.session['idplan'] = plan.id
                print request.session['idplan']
                return HttpResponseRedirect(reverse('MMM.views.hybridize'))
            elif raw_data['status'] == 'stop':
                # if the user stops at the virtual plan
                request.session['val_aliquots'] = raw_data['val_aliquots']
                request.session['plan'] = plan
                return HttpResponseRedirect(reverse('MMM.views.check_view'))
        except Exception, e:
            print e
            transaction.rollback()
            return HttpResponseBadRequest("Error")
        finally:
            transaction.rollback()


# report of hybridization plan
@laslogin_required
@login_required
@permission_decorator('MMM.can_view_MMM_validate_hybridization')
def check_view(request):
    val_aliquots = request.session['val_aliquots']
    plan = request.session['plan']
    print val_aliquots

    if request.session.get('val_aliquots'):
        del request.session['val_aliquots']
    if request.session.get('plan'):
        del request.session['plan']

    return render_to_response('reportCheck.html', {'plan':plan, 'val_aliquots':val_aliquots }, RequestContext(request))


# select hybridization plan
@laslogin_required
@login_required
@permission_decorator('MMM.can_view_MMM_hybridize')
@transaction.commit_manually
def select_hybrid(request):
    if request.method =='GET':
        try:
            user = auth.get_user(request)
            operator = User.objects.get(username = user.username)
            plans = HybridPlan.objects.filter(idOperator=operator, timehybrid__isnull=True, timecheck__isnull=False).order_by('timeplan')
            print plans
            transaction.commit()
            return render_to_response('select_hybplan.html', {'plans':plans}, RequestContext(request))
        except:
            transaction.rollback()
            return HttpResponseBadRequest('Page not available')
        finally:
            transaction.rollback()
    elif request.method == 'POST':
        raw_data = simplejson.loads(request.raw_post_data)
        print '[MMM] - Raw Data: "%s"' % raw_data
        idplan = ''
        if raw_data.has_key('idplan'):
            idplan = raw_data['idplan']
        print idplan
        request.session['idplan'] = idplan
        return HttpResponseRedirect(reverse('MMM.views.hybridize'))


# hybridization of chips
@laslogin_required
@login_required
@permission_decorator('MMM.can_view_MMM_hybridize')
@transaction.commit_manually
def hybridize(request):
    # after the planning in the pre_hybrid view
    if request.method =='GET':
        try:
            resp = {}
            idplan = request.session['idplan']
            
            if request.session.get('idplan'):
                del request.session['idplan']

            # load plan
            plan = HybridPlan.objects.get(id=idplan)
            resp['plan'] = plan
            print plan

            # load aliquots
            aliquots = Aliquot_has_Request.objects.filter(idHybPlan=plan)
            resp['selected_aliquots'] = aliquots

            print "[MMM] - rendering...hyb view"
            print resp

            return render_to_response('hybrid.html', resp, RequestContext(request))
        except:
            transaction.rollback()
            return HttpResponseBadRequest('Page not available')
        finally:
            transaction.rollback()

    else: 
        # POST method
        raw_data = simplejson.loads(request.raw_post_data)
        print '[MMM] - Raw Data for hybrization event: "%s"' % raw_data
        try:
            user = auth.get_user(request)
            user_name = User.objects.get(username = user.username)
            print user_name
            eventTime = datetime.datetime.now()
            plan = HybridPlan.objects.get(id=raw_data['planid'])
            #hybevent = HybEvent(idHybProtocol= plan.idHybProtocol , idInstrument= plan.idInstrument, idOperator = user_name , timestamp = eventTime)
            #hybevent.save()
            plan.timehybrid = eventTime
            plan.save()
            print plan

            data = []

            # for each chip set hybridization event
            for barcode, infoChip in raw_data['chips_tohyb'].items():
                chip = Chip.objects.get(barcode=barcode)
                geometry = ast.literal_eval(chip.idChipType.layout.rules)
                chip.idHybevent = plan
                print chip
                for pos, aliquot in infoChip.items():
                    print pos, aliquot
                    requestAliq = Aliquot_has_Request.objects.get(id=aliquot['sample_id'])
                    chipPosAssign = Assignment(idChip = chip, position = int(pos), idAliquot_has_Request = requestAliq)
                    chipPosAssign.save()
                    print chipPosAssign
                    data.append( (barcode, geometry[int(pos)], str(requestAliq.aliquot_id) ) )
                chip.save()
            data = sorted(data, key=operator.itemgetter(0, 1))
            request.session['samples'] = data
            request.session['plan'] = plan
            transaction.commit()
            return HttpResponseRedirect(reverse('MMM.views.hybrization_view'))
        except:
            transaction.rollback()
            return HttpResponseBadRequest('Error in saving data')


# report of hybridization
@laslogin_required
@login_required
@permission_decorator('MMM.can_view_MMM_hybridize')
def hybrization_view(request):
    samples = ''
    plan = ''
    
    if request.session.get('samples'):
        samples = request.session['samples']
        del request.session['samples']
    if request.session.get('plan'):
        plan = request.session['plan']
        del request.session['plan']

    return render_to_response('reportHybridization.html', {'plan':plan, 'samples':samples}, RequestContext(request))



@laslogin_required
@login_required
@permission_decorator('MMM.can_view_MMM_hybridization_protocol')
@transaction.commit_manually
def hybrid_protocols(request):
    if request.method == "POST":
        try:
            form = HybProtForm(request.POST)
            if form.is_valid():
                hybprot = form.save()
                print hybprot
                transaction.commit()
                request.session['hybprot'] = hybprot
                return HttpResponseRedirect(reverse('MMM.views.hybridprot_info'))
            else:
                raise
        except:
            transaction.rollback()
            return render_to_response('hybrid_protocol.html', {'form':form}, RequestContext(request)) 
        finally:
            transaction.rollback()
    else:
        form = HybProtForm()
        print form
        return render_to_response('hybrid_protocol.html', {'form':form}, RequestContext(request))    


@laslogin_required
@login_required
@permission_decorator('MMM.can_view_MMM_hybridization_protocol')
def hybridprot_info(request):
    hybprot = request.session['hybprot']
    if request.session.get('hybprot'):
        del request.session['hybprot']
    return render_to_response('hybprot_info.html', {'protocol':hybprot}, RequestContext(request))
