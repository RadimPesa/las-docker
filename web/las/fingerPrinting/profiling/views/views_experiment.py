from __init__ import *
import requests
#######################################
#Experiments views
#######################################


#view for upload file and get of the initial page of new request
@laslogin_required
@login_required
@permission_decorator('profiling.can_view_FPM_run_experiment')
@transaction.commit_manually
def select_experiment(request):
    print 'Start FPM view: views_experiment.select_experiment'
    if request.method == "GET":
        # GET method
        try:
            user = auth.get_user(request)
            user_name = User.objects.get(username = user.username)
            plans = Experiment.objects.filter(idOperator=user_name, time_executed__isnull=True)
            print 'FPM view: views_experiment.select_experiment'
            print plans
            transaction.commit()
            return render_to_response('select_experiment.html', {'plans':plans}, RequestContext(request))
        except Exception, e:
            print 'FPM view: views_experiment.select_experiment 1)', str(e)
            transaction.rollback()
            return HttpResponseBadRequest("Page not available")
        finally:
            transaction.rollback()
    else:
        try:
            raw_data = simplejson.loads(request.raw_post_data)
            print '[FPM] -- Raw Data: "%s"' % raw_data
            idplan = ''
            if raw_data.has_key('idplan'):
                idplan = raw_data['idplan']
            request.session['idplan'] = idplan
            return HttpResponseRedirect(reverse('profiling.views.upload_results'))
        except Exception, e:
            print 'FPM view: views_experiment.select_experiment 2)', + str(e)



#view for upload file and get of the initial page of new request
@laslogin_required
@login_required
@permission_decorator('profiling.can_view_FPM_run_experiment')
@transaction.commit_manually
def upload_results(request):
    print 'Start FPM view: profiling.views_experiment.upload_results'
    if request.method == "GET":
        try:
            idplan = request.session['idplan']
            plan = Experiment.objects.get(id=idplan)
            transaction.commit()

            return render_to_response('upload_results.html', {'plan':plan}, RequestContext(request))
        except Exception, e:
            print 'FPM view: views_experiment.upload_results 1)',  str(e)
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
                print "Files:", request.FILES.getlist('file')
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

            payload = {'params': {'uuid_list': refs}, 'exp_type':'Sequenom'}


            plan.save()


            transaction.commit()

            if nextFlag == 'true':
                request.session['idplan'] = idplan
                return HttpResponseRedirect(reverse('profiling.views.read_measures'))
            else:
                request.session['measureserie'] = plan
                request.session['archiveName'] = archiveName
                request.session['files'] = uploadedFileList
                return HttpResponseRedirect(reverse('profiling.views.experiment_event'))


        except Exception, e:
            print 'FPM view: views_experiment.upload_results 1)',  str(e)
            transaction.rollback()
            return HttpResponseBadRequest("Error in saving data")
        finally:
            transaction.rollback()



@login_required
@permission_decorator('profiling.can_view_FPM_run_experiment')
@transaction.commit_manually
def select_analysis(request):
    print 'Start FPM view: views_experiment.select_analysis'
    if request.method == "GET":
        # GET method
        try:
            user = auth.get_user(request)
            user_name = User.objects.get(username = user.username)
            exps = Experiment.objects.filter(idOperator=user_name, time_executed__isnull=False)
            print 'exps',exps
            plans = []

            for e in exps:
                an = Analysis.objects.filter(id_experiment=e)
                if not len(an):
                    plans.append({'id':e.id, 'time_creation':e.time_creation, 'title':e.title, 'description':e.description, 'analysis':len(an)})

            print 'FPM view: views_experiment.select_analysis'
            print 'plans',plans
            transaction.commit()
            return render_to_response('select_analysis.html', {'plans':plans}, RequestContext(request))
        except Exception, e:
            print 'FPM view: views_experiment.select_analysis 1)', str(e)
            transaction.rollback()
            return HttpResponseBadRequest("Page not available")
        finally:
            transaction.rollback()
    else:
        try:
            raw_data = simplejson.loads(request.raw_post_data)
            print '[FPM] -- Raw Data: "%s"' % raw_data
            idplan = ''
            if raw_data.has_key('idplan'):
                idplan = raw_data['idplan']
            request.session['idplan'] = idplan
            return HttpResponseRedirect(reverse('profiling.views.read_measures'))
        except Exception, e:
            print 'FPM view: views_experiment.select_experiment 2)', + str(e)



#view for upload file and get of the initial page of new request
@laslogin_required
@login_required
@permission_decorator('profiling.can_view_FPM_run_experiment')
@transaction.commit_manually
def read_measures(request):
    print 'Start FPM view: profiling.views_experiment.read_measures'
    print request.POST
    print request.FILES
    analysis_uuid = None
    if request.method == "GET":
        try:
            idplan = request.session['idplan']
            plan = Experiment.objects.get(id=idplan)
            print 'FPM view: views_experiment.read_measures'

            sExp = []
            for s in Sample.objects.filter(idExperiment=plan):
                sExp.append((s.idAliquot_has_Request.aliquot_id.genId, s.idAliquot_has_Request.plate, s.idAliquot_has_Request.well))
            sExp = list(set(sExp))

            targets = getProbes( list(set(Sample.objects.filter(idExperiment=plan).values_list('probe', flat=True)) ) )
            probes = targets

            transaction.commit()

            return render_to_response('read_measures.html', {'plan':plan, 'targets':targets, 'samples':sExp, 'probes':probes}, RequestContext(request))
        except Exception, e:
            print 'FPM view: views_experiment.read_measures 1)',  str(e)
            transaction.rollback()
            return HttpResponseBadRequest("Page not available")
        finally:
            transaction.rollback()
    else:
        try:
            if 'actionForm' in request.POST:
                idplan = request.session['idplan']
                plan = Experiment.objects.get(id=idplan)
                sExp = set(Sample.objects.filter(idExperiment=plan).values_list('idAliquot_has_Request__aliquot_id__genId', flat=True))
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
                                    headerLine[tokens[i]] = i
                                header = False
                                print 'headerLine',headerLine
                            else:
                                idSample = None
                                mut = {'mut':{}, 'bs':[]}
                                valuesAnn = {}
                                try:
                                    idSample = tokens[ headerLine['Sample'] ]
                                    read = tokens[ headerLine['Genotype'] ]
                                    rs = tokens[ headerLine['rs'] ]
                                except Exception, e:
                                    print 'Error', e
                                    continue
                                print 'geneMut',geneMut
                                print 'rs',rs
                                if not geneMut.has_key(rs):
                                    continue
                                if idSample not in sExp:
                                    print "sample %s not planned, skipping" % idSample
                                    continue
                                else:
                                    for t in  geneMut[rs]:
                                        if not valuesAnn.has_key(t['snp_uuid']):
                                            valuesAnn[t['snp_uuid']] = {'name': t['alt'] , 'val': 0}
                                if read.lower() == 'n/a' or read.lower() == 'failed':
                                    for p in probes[rs]:
                                        mut['bs'].append(p['snp_uuid'])
                                else:

                                    read = read.replace('/', '')
                                    print 'read',read
                                    for r in read:
                                        for t in  geneMut[rs]:
                                            if t['alt']  == r:
                                                valuesAnn[t['snp_uuid']]['val'] += 1
                                    print 'valuesAnn',valuesAnn
                                    for k, v in valuesAnn.items():
                                        if not mut['mut'].has_key(rs):
                                            mut['mut'][rs] = {}
                                        mut['mut'][rs][k] = {'name': v['name'] , 'val': round( float(v['val']) / len(read) , 2)}

                                print 'update samples'
                                if len(mut['bs']) != 0:
                                    if not samples.has_key(idSample):
                                        samples[idSample] = {}
                                    if not samples[idSample].has_key('bs'):
                                        samples[idSample]['bs'] = []
                                    samples[idSample]['bs'].extend(mut['bs'])
                                if len(mut['mut'].keys()) != 0:
                                    if not samples.has_key(idSample):
                                        samples[idSample] = {}
                                    if not samples[idSample].has_key('mut'):
                                        samples[idSample]['mut'] = {}

                                    samples[idSample]['mut'].update(mut['mut'])

                                print samples[idSample]


                        print 'samples',samples
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
            analysis_type = request.POST['analysis_type']


            probesDict = {}
            for pname, pList in probes.items():
                for p in pList:
                    probesDict[p['snp_uuid']] = p

            plan = Experiment.objects.get(id=idplan)

            summary_aliquots = []

            aliquots = Sample.objects.filter(idExperiment=plan)
            genIds = list(set(aliquots.values_list('idAliquot_has_Request__aliquot_id__genId', flat=True)))

            refs = list(set(aliquots.values_list('probe', flat=True)))

            analysisData = {'analysis_uuid':None, 'analysis_name':plan.title, 'samples': genIds, 'params': {'uuid_list': refs}, 'annotations': [], 'failed': [], 'exp_type':'Sequenom'}


            print 'probes',probes

            for s, sInfo in raw_data.items():
                print 'sInfo',sInfo
                for t, tInfo in sInfo.items():
                    if t == 'mut':
                        for mutations in tInfo.values():
                            for m, mInfo in mutations.items():
                                analysisData['annotations'].append( ( s, probesDict[m]['chrom'], probesDict[m]['start'], probesDict[m]['end'], probesDict[m]['strand'], probesDict[m]['alt'] if 'alt' in probesDict[m] else None, probesDict[m]['num_repeats'] if 'num_repeats' in probesDict[m] else None, probesDict[m]['class'], probesDict[m]['name'], probesDict[m]['allele'], mInfo['val'], sInfo['plate'], sInfo['well']) )

                    if t == 'bs':
                        # this fix avoids submitting a failed SNP multiple times for the same sample (it previously used to be submitted once for every allele, which obviously is pointless)
                        for p in set(map(lambda y:(probesDict[y]['chrom'], probesDict[y]['start'], probesDict[y]['end'], probesDict[y]['name']), tInfo)):
                            # edit: failed data now also include the snp name (rs...)
                            analysisData['failed'].append( ( s, p[0], p[1], p[2], p[3], sInfo['plate'], sInfo['well']) )

            print 'analysisData',analysisData


            anFileName = 'Sequenom_' + now.strftime("%Y-%m-%d_%H:%M:%S") + '_' + user.username + '.las'

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
            print 'plan.raw_id',plan.raw_id
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
            submitAnalysis({'analysis_uuid': analysisData['analysis_uuid'],
                            'raw_data_uuid': plan.raw_id,
                            'annotations': [
                                {'ref_type': analysis_type,
                                'annotations': analysisData['annotations'],
                                'failed':analysisData['failed']
                                }
                            ]})

            request.session['analysis'] = an
            #transaction.rollback()

            transaction.commit()
            return HttpResponseRedirect(reverse('profiling.views.measure_event'))


        except Exception, e:
            print 'FPM view: views_experiment.read_measures 1)',  str(e)
            transaction.rollback()
            if analysis_uuid is not None:
                genAn.deleteAnalysis(uuid=analysis_uuid)
            return HttpResponseBadRequest("Error in saving data")
        finally:
            transaction.rollback()



#view for upload file and get of the initial page of new request
@laslogin_required
@login_required
@permission_decorator('profiling.can_view_FPM_run_experiment')
def measure_event(request):
    print 'Start FPM view: profiling.views_experiment.measure_event'
    resp = {}
    if request.session.has_key('analysis'):
        resp['analysis'] = request.session['analysis']
        del request.session['analysis']
    return render_to_response('measurmentevent.html',resp, RequestContext(request))

#view for upload file and get of the initial page of new request
@laslogin_required
@login_required
@permission_decorator('profiling.can_view_FPM_run_experiment')
def experiment_event(request):
    print 'Start FPM view: profiling.views_experiment.experiment_event'
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
