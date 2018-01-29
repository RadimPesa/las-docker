from __init__ import *
import requests

#######################################
#Experiments views
#######################################

### constants
# for upload_results view
UNDETERMINED_VALUES = set(['undetermined'])
NA = 'na'
FILE_FORMATS = {1: {"name": "7900HT (Applied Biosystems)", "num_fields": 6, "mapping": {"genid": 1, "probe": 2, "value": 5}},
                2: {"name": "LC480 (ROCHE)", "num_fields": 4, "mapping": {"genid": 1, "probe": 2, "value": 3}}}

#view for upload file and get of the initial page of new request
@laslogin_required
@login_required
@permission_decorator('rtpcr.can_view_RTM_run_experiment')
@transaction.commit_manually
def select_experiment(request):
    if request.method == "GET":
        # GET method
        try:
            user = auth.get_user(request)
            user_name = User.objects.get(username = user.username)
            plans = Experiment.objects.filter(idOperator=user_name, time_executed__isnull=True)
            print 'RTM view: views_experiment.select_experiment'
            print plans
            transaction.commit()
            return render_to_response('select_experiment.html', {'plans':plans}, RequestContext(request))
        except Exception, e:
            print e
            transaction.rollback()
            return HttpResponseBadRequest("Page not available")
        finally:
            transaction.rollback()
    else:
        try:
            raw_data = simplejson.loads(request.raw_post_data)
            print '[RTM] -- Raw Data: "%s"' % raw_data
            idplan = ''
            if raw_data.has_key('idplan'):
                idplan = raw_data['idplan']
            request.session['idplan'] = idplan
            return HttpResponseRedirect(reverse('rtpcr.views.upload_results'))
        except Exception, e:
            print 'RTM view: views_experiment.select_experiment 2)', + str(e)


#view for upload file and get of the initial page of new request
@laslogin_required
@login_required
@permission_decorator('rtpcr.can_view_RTM_run_experiment')
@transaction.commit_manually
def upload_results(request):
    print 'Start RTM view: rtpcr.views_experiment.upload_results'
    if request.method == "GET":
        try:
            idplan = request.session['idplan']
            print idplan
            plan = Experiment.objects.get(id=idplan)

            sExp = Sample.objects.filter(idExperiment=plan).order_by('idAliquot_has_Request__aliquot_id__genId', 'probe')

            targets = getTargets( list(set(Sample.objects.filter(idExperiment=plan).values_list('probe', flat=True)) ) )

            targets = sorted(targets, key=lambda k: k['uuid'])

            #print targets

            samples = {}
            for s in sExp:
                genid = s.idAliquot_has_Request.aliquot_id.genId
                if not samples.has_key(genid):
                    samples[genid] = {}
                if not samples[genid].has_key(s.probe):
                    samples[genid][s.probe] = []
                samples[genid][s.probe].append(s)

            print samples
            matrixData = []

            for al, probes in samples.items():
                nRows = []
                for t in targets:
                    nRows.append( len( probes[t['uuid']] ) )
                nRows = max(nRows) if len(nRows) else 0
                print nRows

                for r in range(nRows):
                    row = []
                    for t in targets:
                        if r >= len(probes[t['uuid']]):
                            row.append(None)
                        else:
                            print '---'
                            print probes[t['uuid']], r
                            row.append( probes[t['uuid']][r] )
                    matrixData.append(row)


            print samples
            print matrixData
            transaction.commit()
            return render_to_response('upload_results.html', {'plan':plan, 'samples':matrixData, 'targets':targets, 'NA': NA, 'file_formats': FILE_FORMATS}, RequestContext(request))
        except Exception, e:
            print 'RTM view: views_experiment.upload_results 1)',  str(e)
            transaction.rollback()
            return HttpResponseBadRequest("Page not available")
        finally:
            transaction.rollback()
    else:
        try:
            if 'actionForm' in request.POST:
                try:
                    print request.POST
                    targets = json.loads(request.POST['targets'])
                    idplan = json.loads(request.POST['idplan'])
                    fileformat_id = json.loads(request.POST['fileformat'])
                    samples = {}
                    als = Sample.objects.filter(idExperiment = idplan)

                    try:
                        fileformat = FILE_FORMATS[fileformat_id]
                        print "Selected file format:", fileformat['name']
                    except:
                        return HttpResponseServerError("Unknown file format")

                    targetsMap = {}
                    for t in targets:
                        targetsMap[t['name']] = t['uuid']

                    print targetsMap
                    print idplan

                    for uploaded_file in request.FILES.getlist('file'):
                        print uploaded_file
                        destination = handle_uploaded_file(uploaded_file)
                        print destination
                        fin = open(destination)
                        measures = {}
                        for line in fin:
                            print "line:", line
                            tokens = line.strip().split('\t')
                            #print tokens, len(tokens)
                            if len(tokens) != fileformat['num_fields']:
                                print "wrong number of fields in line, skipping"
                                continue
                            try:
                                genid = tokens[fileformat['mapping']['genid']]
                                probe = targetsMap[ tokens[fileformat['mapping']['probe']] ]
                                value = tokens[fileformat['mapping']['value']]
                            except Exception as e:
                                print "exception parsing tokens:", tokens
                                print e
                                continue
                            if not measures.has_key(genid):
                                measures[genid] = {}
                            if not measures[genid].has_key(probe):
                                measures[genid][probe] = []

                            measures[genid][probe].append(value)

                        #print measures
                        for al in als:
                            genid = al.idAliquot_has_Request.aliquot_id.genId
                            samples[al.id] = []
                            try:
                                for val in measures[genid][al.probe]:
                                    try:
                                        samples[al.id].append(float(val.replace(',', '.')))
                                    except Exception, e:
                                        if val.strip().lower() in UNDETERMINED_VALUES:
                                            samples[al.id].append(NA)
                            except:
                                print "Exception:", e
                                continue

                        fin.close()
                        remove_uploaded_files([destination])
                        print "samples:", samples
                    return HttpResponse(json.dumps(samples))
                except Exception, e:
                    remove_uploaded_files([destination])
                    return HttpResponseServerError('Error' + str(e))

            now = datetime.datetime.now()
            user = auth.get_user(request)
            operator = User.objects.get(username = user.username)
            archiveName = request.POST['archive_name']
            idplan = request.session['idplan']

            nextFlag = request.POST['flagNext']

            samples = json.loads(request.POST['measures'])
            
            plan = Experiment.objects.get(id=idplan)

            plan.time_executed = now
            plan.save()


            aliquots = Sample.objects.filter(idExperiment = plan)

            for al in aliquots:
                try:
                    for index, value in enumerate(samples[str(al.id)]):
                        if index > 0:
                            # create new instances after first measure
                            al.id = None
                        al.value = value if value != 'bs' else None
                        al.save()
                except Exception, e:
                    print 'Error ', e

            responseUpload = None

            uploadedFileList = []

            if len(request.FILES.getlist('file')) > 0:
                print TEMP_URL
                archiveFile = tarfile.open(path.join(TEMP_URL,archiveName + '.tar.gz'),mode='w:gz')
                #print '2'
                listFiles = [path.join(TEMP_URL, archiveName + '.tar.gz')]
                for uploaded_file in request.FILES.getlist('file'):
                    destination = handle_uploaded_file(uploaded_file)
                    archiveFile.add(destination, arcname=uploaded_file.name)
                    listFiles.append(destination)
                    uploadedFileList.append(uploaded_file.name)
                archiveFile.close()
                responseUpload = uploadRepFile({'operator':user.username}, path.join(TEMP_URL, archiveName + '.tar.gz'))
                remove_uploaded_files(listFiles)
                if responseUpload == 'Fail':
                    transaction.rollback()
                    return HttpResponseBadRequest("Error in reading the additional file/s.")


            genAn = GenomicAnalysis()

            # responseUpload = file raw id in mongo

            raw_uuid = genAn.createRawData(data_link=responseUpload)
            print 'raw_uuid ', raw_uuid
            plan.raw_id = raw_uuid

            # reload samples to include newly created ones
            aliquots = Sample.objects.filter(idExperiment = plan)
            genIds = list(set(aliquots.values_list('idAliquot_has_Request__aliquot_id__genId', flat=True)))

            genids_not_found = genAn.addRawDataTargetGenid_batch(raw_uuid, genIds)

            print 'genids_not_found: ', genids_not_found

            refs = list(set(aliquots.values_list('probe', flat=True)))

            payload = {'params': {'uuid_list': refs}, 'exp_type':'Real-Time PCR'}
            plan.save()


            transaction.commit()

            if nextFlag == 'true':
                request.session['idplan'] = idplan
                return HttpResponseRedirect(reverse('rtpcr.views.read_measures'))
            else:
                request.session['measureserie'] = plan
                request.session['archiveName'] = archiveName
                request.session['files'] = uploadedFileList
                return HttpResponseRedirect(reverse('rtpcr.views.experiment_event'))


        except Exception, e:
            print 'RTM view: views_experiment.upload_results 1)',  str(e)
            transaction.rollback()
            return HttpResponseBadRequest("Error in saving data")
        finally:
            transaction.rollback()



@login_required
@permission_decorator('rtpcr.can_view_RTM_run_experiment')
@transaction.commit_manually
def select_analysis(request):
    print 'Start RTM view: views_experiment.select_analysis'
    if request.method == "GET":
        # GET method
        try:
            user = auth.get_user(request)
            user_name = User.objects.get(username = user.username)
            exps = Experiment.objects.filter(idOperator=user_name, time_executed__isnull=False)

            plans = []

            for e in exps:
                an = Analysis.objects.filter(id_experiment=e)
                plans.append({'id':e.id, 'time_creation':e.time_creation, 'title':e.title, 'description':e.description, 'analysis':len(an)})

            print 'RTM view: views_experiment.select_analysis'
            print plans
            transaction.commit()
            return render_to_response('select_analysis.html', {'plans':plans}, RequestContext(request))
        except Exception, e:
            print 'RTM view: views_experiment.select_analysis 1)', str(e)
            transaction.rollback()
            return HttpResponseBadRequest("Page not available")
        finally:
            transaction.rollback()
    else:
        try:
            raw_data = simplejson.loads(request.raw_post_data)
            print '[RTM] -- Raw Data: "%s"' % raw_data
            idplan = ''
            if raw_data.has_key('idplan'):
                idplan = raw_data['idplan']
            request.session['idplan'] = idplan
            return HttpResponseRedirect(reverse('rtpcr.views.read_measures'))
        except Exception, e:
            print 'RTM view: views_experiment.select_experiment 2)', + str(e)




#view for upload file and get of the initial page of new request
@laslogin_required
@login_required
@permission_decorator('rtpcr.can_view_RTM_run_experiment')
@transaction.commit_manually
def read_measures(request):
    print 'Start RTM view: rtpcr.views_experiment.read_measures'
    analysis_uuid = None
    if request.method == "GET":
        try:
            idplan = request.session['idplan']
            plan = Experiment.objects.get(id=idplan)
            next_analysis = Analysis.objects.filter(id_experiment=plan).count() + 1
            print 'RTM view: views_experiment.read_measures'

            sExp = Sample.objects.filter(idExperiment=plan)

            samples = {}
            for s in sExp:
                genid = s.idAliquot_has_Request.aliquot_id.genId
                if not samples.has_key(genid):
                    samples[genid] = {}
                if not samples[genid].has_key(s.probe):
                    samples[genid][s.probe] = []
                samples[genid][s.probe].append({"id": s.id, "value": s.value})

            targets = getTargets( list(set(Sample.objects.filter(idExperiment=plan).values_list('probe', flat=True)) ) )
            print "targets:", targets


            formulas = Formula.objects.all()

            formulaStruct = {}

            for f in formulas:
                v = json.loads(f.variables)
                vf = v['input']
                vf.extend(v['output'])
                vf = list(set(vf))
                formulaStruct[f.id] = {'variables': vf, 'expression': f.expression, 'name': f.name, 'description': f.description, 'output': v['output'], 'analysis_type': f.analysisType.value}

            print formulaStruct

            transaction.commit()

            return render_to_response('read_measures.html', {'plan':plan, 'targets':targets, 'samples':json.dumps(samples), 'formulas': json.dumps(formulaStruct), 'a_types': AnalysisType.objects.all(), 'next_analysis': next_analysis}, RequestContext(request))

        except Exception, e:
            print 'RTM view: views_experiment.read_measures 1)',  str(e)
            transaction.rollback()
            return HttpResponseBadRequest("Page not available")
        finally:
            transaction.rollback()
    else:
        try:

            print request.POST
            ad = None
            ao = []
            outputs = []

            now = datetime.datetime.now()
            user = auth.get_user(request)
            operator = User.objects.get(username = user.username)
            idplan = request.POST['plan']
            analysis_descr = request.POST['analysis_descr']
            listTargets = yaml.safe_load(request.POST['targets'])
            raw_data = yaml.safe_load(request.POST['aliquots_list'])
            fid = request.POST['fid']
            analysis_type = request.POST['analysis_type']
            probe_var_mapping = yaml.safe_load(request.POST['probe-var-map']);
            aggr_crit = yaml.safe_load(request.POST['aggr-crit']);

            analysisType = AnalysisType.objects.get(value=analysis_type)
            plan = Experiment.objects.get(id=idplan)
            formula = Formula.objects.get(pk=fid)

            print "raw_data", raw_data

            ### create raw data file and store it in repository
            anFileName = 'RTPCR_' + now.strftime("%Y-%m-%d_%H:%M:%S") + '_' + user.username + '.las'

            with open(path.join(TEMP_URL, anFileName) , 'w') as outfile:
                json.dump(raw_data, outfile)

            respAnalysisFile = uploadRepFile({'operator':user.username}, path.join(TEMP_URL, anFileName))
            remove_uploaded_files([path.join(TEMP_URL, anFileName)])

            if respAnalysisFile == 'Fail':
                transaction.rollback()
                return HttpResponseBadRequest("Error in creating analysis file.")
            print 'id analysis file ', respAnalysisFile

            ### create analysis-related objects

            # create analysis object in database
            print "create analysis object in database"
            an = Analysis(time_executed=now, id_experiment=plan, idOperator=operator, analysisType_id=analysisType, description=analysis_descr)
            an.save()

            # create analysis description in doc database
            #ad = AnalysisDescription(analysis_id=an.id, formula={'analysis_type_label': formula.analysisType.value, 'description': formula.description, 'expression': formula.expression, 'id': formula.id, 'name': formula.name, 'value_type': formula.valueType,  'variables': json.loads(formula.variables)}, probe_var_mapping=probe_var_mapping, aggregation_criteria=aggr_crit)
            print "create analysis description in doc database"
            ad = AnalysisDescription(analysis_id=an.id, formula_id=formula.id, probe_var_mapping=probe_var_mapping, aggregation_criteria=aggr_crit)
            ad.save()

            # create analysis node in graph
            print "create analysis node in graph"
            genAn = GenomicAnalysis()
            analysis_uuid = genAn.createAnalysis(target_uuid=plan.raw_id, data_link=respAnalysisFile, description_uuid=str(ad.id))
            print 'analysis_uuid ', analysis_uuid
            
            # update analysis object with analysis node uuid
            an.analysis_id = analysis_uuid
            an.description_id = ad.id
            an.save()

            # create dictionary with target probes
            targets = {}
            for t in listTargets:
                targets[t['uuid']] = t

            # create analysis data dictionary
            genIds = raw_data.keys()
            analysisData = {'analysis_uuid':None, 'analysis_name':plan.title, 'samples': genIds, 'params': {'uuid_list': []}, 'annotations': [], 'failed': [], 'exp_type':'Real-Time PCR'}

            # loop through results
            refs = []
            for s, sInfo in raw_data.items():
                for t, tInfo in sInfo.items():
                    testT = t.split('|')[0]
                    refT = t.split('|')[1].split('_')
                    if len(tInfo):
                        refs.append(testT)
                    for v in tInfo:
                        if v['value'] == 'N/A':
                            ao = AnalysisOutput(analysis_id=an.id, value=None, variables=v['vars'], test_probe=testT, ref_probes=refT)
                            ao.save()
                            # edit: failed data now also include the test gene symbol and info about the ref gene(s)
                            analysisData['failed'].append( ( s, targets[testT]['ref'], targets[testT]['start_base'], targets[testT]['end_base'], targets[testT]['gene_symbol'], [{'ref': targets[x]['ref'], 'start': targets[x]['start_base'], 'end': targets[testT]['end_base'], 'gene_symbol': targets[x]['gene_symbol']} for x in refT], str(ao.id) ) )
                        else:
                            ao = AnalysisOutput(analysis_id=an.id, value=v['value'], variables=v['vars'], test_probe=testT, ref_probes=refT)
                            ao.save()
                            analysisData['annotations'].append( ( s, targets[testT]['ref'], targets[testT]['start_base'], targets[testT]['end_base'], targets[testT]['gene_symbol'], v['value'], [{'ref': targets[x]['ref'], 'start': targets[x]['start_base'], 'end': targets[testT]['end_base'], 'gene_symbol': targets[x]['gene_symbol']} for x in refT], formula.valueType, str(ao.id) ) )
                        outputs.append(ao)

            analysisData['params']['uuid_list'] = list(set(refs))
            print "analysisData", analysisData

            analysisData['analysis_uuid'] = analysis_uuid
            analysisData['raw_uuid'] = plan.raw_id

            # submit analysis data
            respLabelAnalysis = submitLabelAnalysis({'analysis_uuid':analysisData['analysis_uuid'], 'analysis_name':analysisData['analysis_name'], 'exp_type':analysisData['exp_type'], 'params':analysisData['params'], 'ref_type': analysis_type})
            # edit: the dictionary structure sent to the annotation manager has changed:
            # -'annotations' has become a list (previously a dict)
            # -each item in the list is a dict with a 'ref_type', a list of 'annotations' and a list of 'failed' data
            submitAnalysis({'analysis_uuid': analysisData['analysis_uuid'],
                            'raw_data_uuid': plan.raw_id,
                            'annotations': [
                                {'ref_type': analysis_type,
                                'annotations': analysisData['annotations'],
                                'failed': analysisData['failed']
                                }
                            ]})

            request.session['analysis'] = an

            transaction.commit()
            return HttpResponseRedirect(reverse('rtpcr.views.measure_event'))


        except Exception, e:
            print 'RTM view: views_experiment.read_measures 2)',  str(e)
            transaction.rollback()
            if ad:
                ad.delete()
            for ao in outputs:
                ao.delete()
            if analysis_uuid is not None:
                genAn.deleteAnalysis(uuid=analysis_uuid)
            return HttpResponseBadRequest("Error in saving data")
        finally:
            transaction.rollback()


#view for upload file and get of the initial page of new request
@laslogin_required
@login_required
@permission_decorator('rtpcr.can_view_RTM_run_experiment')
def measure_event(request):
    print 'Start RTM view: rtpcr.views_experiment.measure_event'
    resp = {}
    if request.session.has_key('analysis'):
        resp['analysis'] = request.session['analysis']
        del request.session['analysis']
    return render_to_response('measurmentevent.html',resp, RequestContext(request))




#view for upload file and get of the initial page of new request
@laslogin_required
@login_required
@permission_decorator('rtpcr.can_view_RTM_run_experiment')
def experiment_event(request):
    print 'Start RTM view: rtpcr.views_experiment.experiment_event'
    resp = {}
    if request.session.has_key('archiveName'):
        resp['archiveName'] = request.session['archiveName']
        del request.session['archiveName']

    if request.session.has_key('files'):
        resp['files'] = request.session['files']
        del request.session['files']

    if request.session.has_key('measureserie'):
        resp['measureserie'] = request.session['measureserie']
        del request.session['measureserie']
    return render_to_response('experimentevent.html',resp, RequestContext(request))
