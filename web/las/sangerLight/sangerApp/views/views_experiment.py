from __init__ import *
import requests

#######################################
#Experiments views
#######################################


#view for upload file and get of the initial page of new request
@laslogin_required
@login_required
@permission_decorator('sangerApp.can_view_SAM_run_experiment')
@transaction.commit_manually
def select_experiment(request):
    print 'Start SAM view: views_experiment.select_experiment'
    if request.method == "GET":
        # GET method
        try:
            user = auth.get_user(request)
            user_name = User.objects.get(username = user.username)
            plans = Experiment.objects.filter(idOperator=user_name, time_executed__isnull=True)
            #plans = Request.objects.filter(idOperator=user_name, pending=False, timechecked__isnull =False, time_executed__isnull =True)
            print 'SAM view: views_experiment.select_experiment'
            print plans
            transaction.commit()
            return render_to_response('select_experiment.html', {'plans':plans}, RequestContext(request))
        except Exception, e:
            print 'SAM view: views_experiment.select_experiment 1)', str(e)
            transaction.rollback()
            return HttpResponseBadRequest("Page not available")
        finally:
            transaction.rollback()
    else:
        try:
            raw_data = simplejson.loads(request.raw_post_data)
            print '[SAM] -- Raw Data: "%s"' % raw_data
            idplan = ''
            if raw_data.has_key('idplan'):
                idplan = raw_data['idplan']
            request.session['idplan'] = idplan
            return HttpResponseRedirect(reverse('sangerApp.views.upload_results'))
        except Exception, e:
            print 'SAM view: views_experiment.select_experiment 2)', + str(e)



#view for upload file and get of the initial page of new request
@laslogin_required
@login_required
@permission_decorator('sangerApp.can_view_SAM_run_experiment')
@transaction.commit_manually
def upload_results(request):
    print 'Start SAM view: sangerApp.views_experiment.upload_results'
    if request.method == "GET":
        try:
            idplan = request.session['idplan']
            plan = Experiment.objects.get(id=idplan)
            transaction.commit()

            return render_to_response('upload_results.html', {'plan':plan}, RequestContext(request))
        except Exception, e:
            print 'SAM view: views_experiment.upload_results 1)',  str(e)
            transaction.rollback()
            return HttpResponseBadRequest("Page not available")
        finally:
            transaction.rollback()
    else:
        try:
            now = datetime.datetime.now()
            user = auth.get_user(request)
            operator = User.objects.get(username = user.username)
            archiveName = request.POST['archive_name']
            idplan = request.session['idplan']

            nextFlag = request.POST['flagNext']

            plan = Experiment.objects.get(id=idplan)

            plan.time_executed = now
            plan.save()
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


            aliquots = Sample.objects.filter(idExperiment = plan)

            genIds = list(set(aliquots.values_list('idAliquot_has_Request__aliquot_id__genId', flat=True)))

            genids_not_found = genAn.addRawDataTargetGenid_batch(raw_uuid, genIds)

            print 'genids_not_found: ', genids_not_found

            refs = list(set(aliquots.values_list('probe', flat=True)))

            payload = {'params': {'uuid_list': refs}, 'exp_type':'Sanger sequencing'}

            plan.save()


            transaction.commit()

            if nextFlag == 'true':
                request.session['idplan'] = idplan
                return HttpResponseRedirect(reverse('sangerApp.views.read_measures'))
            else:
                request.session['measureserie'] = plan
                request.session['archiveName'] = archiveName
                request.session['files'] = uploadedFileList
                return HttpResponseRedirect(reverse('sangerApp.views.experiment_event'))


        except Exception, e:
            print 'SAM view: views_experiment.upload_results 1)',  str(e)
            transaction.rollback()
            return HttpResponseBadRequest("Error in saving data")
        finally:
            transaction.rollback()



@login_required
@permission_decorator('sangerApp.can_view_SAM_run_experiment')
@transaction.commit_manually
def select_analysis(request):
    print 'Start SAM view: views_experiment.select_analysis'
    if request.method == "GET":
        # GET method
        try:
            user = auth.get_user(request)
            user_name = User.objects.get(username = user.username)
            exps = Experiment.objects.filter(idOperator=user_name, time_executed__isnull=False)

            plans = []

            for e in exps:
                an = Analysis.objects.filter(id_experiment=e)
                if not len(an):
                    plans.append({'id':e.id, 'time_creation':e.time_creation, 'title':e.title, 'description':e.description, 'analysis':len(an)})

            print 'SAM view: views_experiment.select_analysis'
            print plans
            transaction.commit()
            return render_to_response('select_analysis.html', {'plans':plans}, RequestContext(request))
        except Exception, e:
            print 'SAM view: views_experiment.select_analysis 1)', str(e)
            transaction.rollback()
            return HttpResponseBadRequest("Page not available")
        finally:
            transaction.rollback()
    else:
        try:
            raw_data = simplejson.loads(request.raw_post_data)
            print '[SAM] -- Raw Data: "%s"' % raw_data
            idplan = ''
            if raw_data.has_key('idplan'):
                idplan = raw_data['idplan']
            request.session['idplan'] = idplan
            return HttpResponseRedirect(reverse('sangerApp.views.read_measures'))
        except Exception, e:
            print 'SAM view: views_experiment.select_experiment 2)', + str(e)



#view for upload file and get of the initial page of new request
@laslogin_required
@login_required
@permission_decorator('sangerApp.can_view_SAM_run_experiment')
@transaction.commit_manually
def read_measures(request):
    print 'Start SAM view: sangerApp.views_experiment.read_measures'
    analysis_uuid = None
    if request.method == "GET":
        try:
            idplan = request.session['idplan']
            plan = Experiment.objects.get(id=idplan)
            print 'SAM view: views_experiment.read_measures'

            sExp = set(Sample.objects.filter(idExperiment=plan).values_list('idAliquot_has_Request__aliquot_id__genId', flat=True))

            targets = retrieveMutations( list(set(Sample.objects.filter(idExperiment=plan).values_list('probe', flat=True)) ), request.user )
            print targets
            print "[1]"
            probes = getTargets( list(set(Sample.objects.filter(idExperiment=plan).values_list('probe', flat=True)) ) )
            print "[2]"
            transaction.commit()
            annotUrl = Urls.objects.get(id_webservice=WebService.objects.get(name='annotation').id, available=True)
            url = annotUrl.url + 'newMutation/?noSave=true'


            return render_to_response('read_measures.html', {'plan':plan, 'targets':targets, 'targetJson':json.dumps(targets), 'samples':sExp, 'probes':probes, 'annotUrl': url}, RequestContext(request))
        except Exception, e:
            print 'SAM view: views_experiment.read_measures 1)',  str(e)
            transaction.rollback()
            return HttpResponseBadRequest("Page not available")
        finally:
            transaction.rollback()
    else:
        try:
            if 'actionForm' in request.POST:
                # read file to load in the corresponding table
                try:
                    geneMut = json.loads(request.POST['geneMut'])
                    probes = json.loads(request.POST['probes'])
                    samples = {}

                    for uploaded_file in request.FILES.getlist('file'):
                        destination = handle_uploaded_file(uploaded_file)
                        fin = open(destination)
                        header = True
                        headerLine = {}
                        for line in fin:
                            tokens = line.strip().split('\t')
                            if header:
                                for i in range(len(tokens)):
                                    headerLine[i] = tokens[i]
                                header = False
                            else:
                                idSample = None
                                mut = {'mut':{}, 'bs':[]}
                                for i in range(len(tokens)):
                                    if headerLine[i] == 'Sample':
                                        idSample = tokens[i]
                                    else:
                                        if tokens[i].lower() == 'wt':
                                            continue
                                        elif tokens[i].lower() == 'n/a':
                                            if geneMut.has_key(headerLine[i]):
                                                for p in probes[headerLine[i]]:
                                                    mut['bs'].append(p['uuid'])
                                        else:
                                            if geneMut.has_key(headerLine[i]):
                                                annotations = tokens[i].split('|')
                                                for a in annotations:
                                                    meas = a.split()
                                                    for t in  geneMut[headerLine[i]]:
                                                        if t['hgvs_c'] == meas[0]:
                                                            if not mut['mut'].has_key(headerLine[i]):
                                                                mut['mut'][ headerLine[i]] = {}
                                                            mut['mut'][ headerLine[i]][t['uuid']] = {'name': t['hgvs_c'], 'val':meas[1]}
                                if idSample:
                                    if len(mut['bs']) == 0:
                                        del mut['bs']
                                    if len(mut['mut'].keys()) == 0:
                                        del mut ['mut']
                                    if len(mut.keys()) != 0:
                                        samples[idSample] = mut

                        fin.close()
                        remove_uploaded_files([destination])
                    return HttpResponse(json.dumps(samples))
                except Exception, e:
                    remove_uploaded_files([destination])
                    return HttpResponseServerError('Error' + str(e))

            now = datetime.datetime.now()
            user = auth.get_user(request)
            operator = User.objects.get(username = user.username)
            idplan = request.POST['plan']
            raw_data = yaml.safe_load(request.POST['aliquots_list'])
            probes = yaml.safe_load(request.POST['probes'])
            targets = yaml.safe_load(request.POST['targets'])
            analysis_type = request.POST['analysis_type']


            probesDict = {}
            for pname, pList in probes.items():
                for p in pList:
                    probesDict[p['uuid']] = p

            targetsDict = {}
            for geneName, tList in targets.items():
                for t in tList:
                    targetsDict[t['uuid']] = t

            plan = Experiment.objects.get(id=idplan)

            print raw_data
            summary_aliquots = []

            aliquots = Sample.objects.filter(idExperiment=plan)
            genIds = list(set(aliquots.values_list('idAliquot_has_Request__aliquot_id__genId', flat=True)))

            refs = list(set(aliquots.values_list('probe', flat=True)))

            analysisData = {'analysis_uuid':None, 'analysis_name':plan.title, 'samples': genIds, 'params': {'uuid_list': refs}, 'annotations': [], 'failed': [], 'exp_type':'Sanger sequencing'}

            for s, sInfo in raw_data.items():
                print sInfo
                for t, tInfo in sInfo.items():
                    if t == 'mut':
                        for mutations in tInfo.values():
                            for m, mInfo in mutations.items():
                                analysisData['annotations'].append( ( s, targetsDict[m]['chrom'], targetsDict[m]['start'], targetsDict[m]['end'], targetsDict[m]['strand'], targetsDict[m]['ref'], targetsDict[m]['alt'], targetsDict[m]['num_bases'], targetsDict[m]['type'], targetsDict[m]['gene_symbol'], mInfo['val']) )

                    if t == 'bs':
                        for p in tInfo:
                            analysisData['failed'].append( ( s, probesDict[p]['ref'], probesDict[p]['start_base'], probesDict[p]['end_base'] ) )




            anFileName = 'Sanger_' + now.strftime("%Y-%m-%d_%H:%M:%S") + '_' + user.username + '.las'

            with open(path.join(TEMP_URL, anFileName) , 'w') as outfile:
                json.dump(raw_data, outfile)


            respAnalysisFile = uploadRepFile({'operator':user.username}, path.join(TEMP_URL, anFileName))
            remove_uploaded_files([path.join(TEMP_URL, anFileName)])

            if respAnalysisFile == 'Fail':
                transaction.rollback()
                return HttpResponseBadRequest("Error in creating analysis file.")
            print 'id analysis file ', respAnalysisFile

            genAn = GenomicAnalysis()

            # respAnalysisFile = file analysis id in mongo
            print plan.raw_id
            analysis_uuid = genAn.createAnalysis(target_uuid=plan.raw_id, data_link=respAnalysisFile)
            print 'analysis_uuid ', analysis_uuid

            an = Analysis(time_executed=now, id_experiment=plan, idOperator=operator, analysis_id=analysis_uuid)
            an.save()

            analysisData['analysis_uuid'] = analysis_uuid
            analysisData['raw_uuid'] = plan.raw_id

            respLabelAnalysis = submitLabelAnalysis({'analysis_uuid':analysisData['analysis_uuid'], 'analysis_name':analysisData['analysis_name'], 'exp_type':analysisData['exp_type'], 'params':analysisData['params'], 'ref_type': analysis_type})
            # edit: the dictionary structure sent to the annotation manager has changed:
            # -'annotations' has become a list (previously a dict)
            # -each item in the list is a dict with a 'ref_type', a list of 'annotations' and a list of 'failed' data
            submitAnalysis( {   'analysis_uuid': analysisData['analysis_uuid'],
                                'raw_data_uuid': plan.raw_id,
                                'annotations': [
                                    {   'ref_type': 'sequence_alteration',
                                        'annotations': analysisData['annotations'],
                                        'failed': analysisData['failed']
                                    }
                                ]
                            })

            request.session['analysis'] = an
            #transaction.rollback()

            transaction.commit()
            return HttpResponseRedirect(reverse('sangerApp.views.measure_event'))


        except Exception, e:
            print 'SAM view: views_experiment.read_measures 1)',  str(e)
            transaction.rollback()
            if analysis_uuid is not None:
                genAn.deleteAnalysis(uuid=analysis_uuid)
            return HttpResponseBadRequest("Error in saving data")
        finally:
            transaction.rollback()



#view for upload file and get of the initial page of new request
@laslogin_required
@login_required
@permission_decorator('sangerApp.can_view_SAM_run_experiment')
def measure_event(request):
    print 'Start SAM view: sangerApp.views_experiment.measure_event'
    resp = {}
    if request.session.has_key('analysis'):
        resp['analysis'] = request.session['analysis']
        del request.session['analysis']
    return render_to_response('measurmentevent.html',resp, RequestContext(request))




#view for upload file and get of the initial page of new request
@laslogin_required
@login_required
@permission_decorator('sangerApp.can_view_SAM_run_experiment')
def experiment_event(request):
    print 'Start SAM view: sangerApp.views_experiment.experiment_event'
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
