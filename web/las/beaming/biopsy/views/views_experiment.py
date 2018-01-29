from __init__ import *
#######################################
#Experiments views
#######################################


#view for upload file and get of the initial page of new request
@laslogin_required
@login_required
@permission_decorator('biopsy.can_view_LBM_run_experiment')
@transaction.commit_manually
def select_experiment(request):

    if request.method == "GET":
        # GET method
        try:
            user = auth.get_user(request)
            user_name = User.objects.get(username = user.username)
            plans = Experiment.objects.filter(idOperator=user_name, time_executed__isnull=True) 
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
        raw_data = simplejson.loads(request.raw_post_data)
        print '[LBM] - Raw Data: "%s"' % raw_data
        idplan = ''
        if raw_data.has_key('idplan'):
            idplan = raw_data['idplan']
        request.session['idplan'] = idplan
        return HttpResponseRedirect(reverse('biopsy.views.read_measures'))



#view for upload file and get of the initial page of new request
@laslogin_required
@login_required
@permission_decorator('biopsy.can_view_LBM_run_experiment')
@transaction.commit_manually
def read_measures(request):
    if request.method == "GET":
        try:
            idplan = request.session['idplan']
            plan = Experiment.objects.get(id=idplan)
            print idplan
            transaction.commit()
            return render_to_response('read_measures.html', {'plan':plan, 'form':UploadFileForm()}, RequestContext(request))
        except:
            transaction.rollback()
            return HttpResponseBadRequest("Page not available")
        finally:
            transaction.rollback()
    else:
        try:
            resp = {}
            user = auth.get_user(request)
            operator = User.objects.get(username = user.username)
            idplan = request.session['idplan']
            plan = Experiment.objects.get(id=idplan)
            # file upload
            form = UploadFileForm(request.POST, request.FILES)
            if (form.is_valid() == False):
                return HttpResponseBadRequest("Form not valid")
            f = request.FILES['file']
            resp['measures'] = []
            header = True
            listMeasure = []
            positions = {}
            mutations = {}
            genesSymb = {}
            for s in Sample.objects.filter(idExperiment = plan):
                positions[s.position] = {'position':s.position, 'mut':s.probe, 'gene': s.gene, 'genealogy':s.idAliquot_has_Request.aliquot_id.genId, 'aliquot':s.id, 'genename':'', 'mut_aa':'', 'mut_cds':'', 'acquired':False}
                genesSymb[s.gene] = ''
                mutations[s.probe] = []
            print positions
            infoMut = getInfoFromId(genesSymb.keys(), mutations.keys())
            for k, s in positions.items():
                s['genename'] = infoMut['genes'][s['gene']]
                s['mut_aa'] = infoMut['mutations'][s['mut']][0]
                s['mut_cds'] = infoMut['mutations'][s['mut']][1]

            import locale
            locale.setlocale( locale.LC_ALL, 'en_US.UTF-8' ) 
            for line in f:
                tokens = line.strip().split('\t')
                print tokens, len(tokens)
                if len(tokens) == 1: # line between samples
                    header = True
                else:
                    if header: # retrieve the header of the measures and the sample info
                        sample_info = tokens[0].split(':')[1].strip().split()
                        print sample_info
                        # remove zeros after letters
                        posParsed = ''
                        firstZero = True
                        for i in sample_info[0]:
                            if not i.isdigit():
                                posParsed += i
                            elif int(i) == 0 and firstZero == True:
                                pass
                            else:
                                firstZero = False
                                posParsed += i                        
                        positions[posParsed]['acquired'] = True
                        for t in tokens[1:]:
                            mType = Measure.objects.get(name=t)
                            listMeasure.append(mType)
                        header = False
                    else:
                        i = 1
                        for m in listMeasure: # identify all the measure for which there is a value (missing value at the end are discarded)
                            if len(tokens) > i:
                                mvalue = tokens[i]
                                if m.unity_measure != '':
                                    mvalue = mvalue.replace(m.unity_measure,'')
                                try:
                                    region = Region.objects.get(code=tokens[0].upper())
                                except:
                                    aliasreg = AliasRegion.objects.get(name=tokens[0].upper())
                                    region = aliasreg.idRegion
                                mt = MeasureType.objects.get(idMeasure=m.id, region=region.id)
                                measure = {'mtypeid':mt.id, 'mtype':m.name, 'munity': m.unity_measure, 'mvalue': locale.atof(mvalue), 'mregionid': region.id, 'mregion': region.code}
                                measure.update(positions[posParsed])
                                resp['measures'].append(measure)
                            else:
                                break
                            i += 1
            pos = [v for k, v in positions.items() if v == False]
            if len(pos):
                raise Exception
            resp['filename'] = True
            resp['archivename'] = 'plot_' + user.username + '_' + datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
            print resp['archivename']
            transaction.commit()
            return render_to_response('read_measures.html', resp, RequestContext(request))
        except Exception, e:
            print e
            transaction.rollback()
            return HttpResponseBadRequest("Error in reading the file. Please verify if all the wells are inserted.")
        finally:
            transaction.rollback()


#view for upload file and get of the initial page of new request
@laslogin_required
@login_required
@permission_decorator('biopsy.can_view_LBM_run_experiment')
@transaction.commit_manually
def save_measures(request):
    if request.method == "POST":
        try:
            user = auth.get_user(request)
            operator = User.objects.get(username = user.username)
            archiveName = request.POST['archive_name']
            idplan = request.session['idplan']
            plan = Experiment.objects.get(id=idplan)
            plan.time_executed = datetime.datetime.now()
            
            print archiveName
            print request.FILES
            responseUpload = 'Fail'
            if len(request.FILES.getlist('file')) > 0:
                tempFolder = path.join(TEMP_URL, user.username + str(datetime.datetime.now()) )
                os.mkdir(tempFolder) #archiveFile = tarfile.open(path.join(TEMP_URL,archiveName + '.tar.gz'),mode='w:gz')
                print tempFolder
                for uploaded_file in request.FILES.getlist('file'):
                    destination = handle_uploaded_file(uploaded_file,tempFolder)
                responseUpload = uploadExperiment({'operator':user.username, 'experiment':'beaming'}, tempFolder)
                #print responseUpload
                shutil.rmtree (tempFolder)


            raw_data = json.loads(request.POST['aliquots_list'])
            print raw_data 
            if responseUpload != 'Fail':
                plan.plot = responseUpload
            plan.save()
            

            summary_aliquots = {}
            for aliquot_info in raw_data:
                aliquot = Sample.objects.get(id=aliquot_info['aliquotid'])
                mType = MeasureType.objects.get(id=aliquot_info['mtype'])
                measure = MeasurementEvent(value = aliquot_info['value'], idSample = aliquot, idMeasureType = mType, idExperiment = plan)
                measure.save()
                if summary_aliquots.has_key(aliquot.id) == False:
                    summary_aliquots[aliquot.id] = {'position':aliquot.position, 'aliquot':aliquot.idAliquot_has_Request.aliquot_id.genId, 'nmeasures':0}
                summary_aliquots[aliquot.id]['nmeasures'] += 1
            
            request.session['summary_aliquots'] = []
            for k, v in summary_aliquots.items():
                request.session['summary_aliquots'].append(v)
            print request.session['summary_aliquots']
            
            if request.session.has_key('idplan'):
                del request.session['idplan']
            request.session['measureserie'] = plan
            transaction.commit()
            return HttpResponseRedirect(reverse('biopsy.views.measure_event'))
        except Exception, e:
            print e
            transaction.rollback()
            return HttpResponseBadRequest("Error in saving data")
        finally:
            transaction.rollback()

#view for upload file and get of the initial page of new request
@laslogin_required
@login_required
@permission_decorator('biopsy.can_view_LBM_run_experiment')
def measure_event(request):
    resp = {}
    if request.session.has_key('summary_aliquots'):
        resp['summary_aliquots'] = request.session['summary_aliquots']
        del request.session['summary_aliquots']
    if request.session.has_key('measureserie'):
        resp['measureserie'] = request.session['measureserie']
        del request.session['measureserie']
    return render_to_response('measurmentevent.html',resp, RequestContext(request))