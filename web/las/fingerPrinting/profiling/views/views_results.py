from __init__ import *

@laslogin_required
@login_required
@permission_decorator('profiling.can_view_FPM_filter_results')
@transaction.commit_manually
def filter_results(request, filter_id):
    resp ={}
    if request.method == "GET":
        # GET method
        try:
            resp['filter_id'] = filter_id
            
            print 'GET filter_session'
            print filter_id
            filterSession = FilterSession.objects.get (id=filter_id)
            resp['mask'] = json.loads(filterSession.features)
            request.session['mask'] = resp['mask']
            print resp['mask']
            resp['session'] = filterSession
            aliquots = Aliquot.objects.filter(pk__in=Aliquot_has_Filter.objects.filter(filter_id=filterSession).values('aliquot_id'))
            print aliquots
            nsamples = Aliquot_has_Request.objects.filter(aliquot_id__in= aliquots)
            print '#samples ' + str(len(nsamples))
            samples = Sample.objects.filter(idAliquot_has_Request__in=nsamples)
            print samples
            request.session['samples'] = samples
            pairs = samples.values('gene', 'probe').annotate(count_pairs=Count('id'))
            infoMut = getInfoFromId([x['gene'] for x in pairs], [x['probe'] for x in pairs])
            print infoMut
            request.session['infoMut'] = infoMut
            for p in pairs:
                p['genename'] = infoMut['genes'][p['gene']]
                p['mut_aa'] = infoMut['mutations'][p['probe']][0]
                p['mut_cds'] = infoMut['mutations'][p['probe']][1]

            resp['aliquots'] = samples
            request.session['samples'] = samples
            resp['mutations'] = pairs
            request.session['pairs'] = pairs
            resp['nsamples'] = len(nsamples)
            print samples
            measures = MeasurementEvent.objects.filter(idSample__in = samples)
            print measures
            mTypes = MeasureType.objects.filter(pk__in=measures.values('idMeasureType'))
            print mTypes
            resp['regions'] = Region.objects.filter(pk__in = mTypes.values('region'))
            print resp['regions']
            resp['measuretype'] = Measure.objects.filter(id__in=mTypes.values('idMeasure'))
            print resp
            transaction.commit()
            return render_to_response('filter_results.html', resp, RequestContext(request))
        except Exception, e:
            print e
            transaction.rollback()
            return HttpResponseBadRequest("Page not available! " + e.args[0])
        finally:
            transaction.rollback()
    else:
        try:
            print 'POST filter'
            rawdata = simplejson.loads(request.raw_post_data)
            print rawdata
            filterSession = FilterSession.objects.get (id=filter_id)
            mask = request.session['mask']
            samples = request.session['samples']
            pairs = request.session['pairs']
            prunedPairs = [p for p in pairs if [p['gene'], p['probe']] in rawdata['target']]
            print prunedPairs
            print samples
            print '---'
            measures = MeasurementEvent.objects.filter(idSample__in = samples.filter(gene__in = [p['gene'] for p in prunedPairs], probe__in =[p['probe'] for p in prunedPairs]).values('id'), idMeasureType__in = MeasureType.objects.filter( idMeasure__in = Measure.objects.filter( pk__in=rawdata['measure']).values('id'),region__in=Region.objects.filter(pk__in=rawdata['region']).values('id'))).order_by('idSample', 'idExperiment')
            data_resp = {}
            dictMeasure = {}
            dictMeasureBB = {}
            print measures
            for m in measures:
                currentSample = m.idSample.id
                currentAliquot = m.idSample.idAliquot_has_Request.aliquot_id.id
                currentExp = m.idExperiment.id
                if not data_resp.has_key(currentSample):
                    data_resp[currentSample] = {'mask':{}, 'bbmeasure':{}, 'experiments':{}, 'info':{}}
                    info = Aliquot_has_Filter.objects.get(filter_id=filter_id, aliquot_id=currentAliquot)
                    print info
                    print info.values
                    inforaw = json.loads(info.values)
                    print inforaw
                    for maskF in rawdata['mask']:
                        data_resp[currentSample]['mask'][maskF] = inforaw[maskF]
                    for mbb in rawdata['bbmeasure']:
                        data_resp[currentSample]['bbmeasure'][mbb] = inforaw[mbb]
                        dictMeasureBB[mbb] = mask[mbb]['name']
                    data_resp[currentSample]['info'] = {'genename': request.session['infoMut']['genes'][m.idSample.gene] , 'mut_cds': request.session['infoMut']['mutations'][m.idSample.probe][1], 'mut_aa': request.session['infoMut']['mutations'][m.idSample.probe][0], 'well': m.idSample.position}
                    print data_resp
                if not data_resp[currentSample]['experiments'].has_key(currentExp):
                    data_resp[currentSample]['experiments'][currentExp] = {'info':{'time_executed':str(m.idExperiment.time_executed), 'operator': str(m.idExperiment.idOperator)}, 'values':{}}
                measuretype = m.idMeasureType.lasmeasureId
                dictMeasure[measuretype] = m.idMeasureType.name
                data_resp[currentSample]['experiments'][currentExp]['values'][measuretype] =  m.value
            
            print 'dictMeasureBB'

            print dictMeasureBB
            print '----'
            stdMeasure = dictMeasure.keys()
            bbMeasures = dictMeasureBB.keys()
            dataFormula = {}
            idExp = []
            for f in rawdata['formula']:
                dataFormula[f]=[]
                print f
                for s, sampleData in data_resp.items():
                    measSampleBB = {}
                    for bb, value in sampleData['bbmeasure'].items():
                        measSampleBB[mask[bb]['measure']] = value
                    for exp, expInfo in sampleData['experiments'].items():
                        measSample = {}
                        for mid, value  in expInfo['values'].items():
                            measSample[mid] = value
                        idExp.append((s,exp))
                        z = dict(measSample.items() + measSampleBB.items())
                        dataFormula[f].append(z)
                print dataFormula[f]      
            print dataFormula
            print idExp
            resultsFormula = computeFormulas(dataFormula)
            if resultsFormula.has_key('status'):
                raise Exception(resultsFormula['description'])
            formulaDict = getFormulasByIds(rawdata['formula'])
            print formulaDict
            print resultsFormula
            if formulaDict.has_key('status'):
                raise Exception(formulaDict['description'])
            for f, res in resultsFormula.items():
                i = 0
                for r in res:
                    print idExp[i], idExp[i][0], idExp[i][1]
                    try:
                        val = '%.4f' % float(r) 
                    except Exception, e:
                        print e
                        val = r
                    print val
                    data_resp[idExp[i][0]]['experiments'][idExp[i][1]]['values']['formula'+str(f)] = val
                    i += 1
                dictMeasure['formula'+str(f)] = formulaDict[f]

            print data_resp
            print dictMeasure

            tableData = []
            headerTable = []
            print 'headerTable'
            for m in rawdata['mask']:
                headerTable.append(mask[m]['name'])
            for m in bbMeasures:
                headerTable.append(dictMeasureBB[m])
            headerTable.extend(['Exp. Id', 'Time', 'Operator', 'Sample Id', 'Well', 'Gene Symb', 'Mut_cds', 'Mut_aa',])
            for m in stdMeasure:
                headerTable.append(dictMeasure[m])
            for f in rawdata['formula']:
                headerTable.append(dictMeasure['formula'+str(f)])
            print headerTable
            print 'tableData'
            for s, sampleData in data_resp.items():
                print sampleData
                biobankInfo = []
                sampleInfo = [s, sampleData['info']['well'], sampleData['info']['genename'], sampleData['info']['mut_cds'], sampleData['info']['mut_aa']]
                bbMeas = []
                
                for m in rawdata['mask']:
                    biobankInfo.append(sampleData['mask'][m])
                for m in bbMeasures:
                    bbMeas.append(sampleData['bbmeasure'][m])
                print biobankInfo, bbMeas
                for exp, expData in sampleData['experiments'].items():
                    expValues = []
                    expInfo = [exp, expData['info']['time_executed'], expData['info']['operator'] ]
                    for m in stdMeasure:
                        print expData['values'][m]
                        expValues.append(expData['values'][m])
                    for f in rawdata['formula']:
                        expValues.append(expData['values']['formula'+str(f)])
                        print expData['values']['formula'+str(f)]
                    tableData.append(biobankInfo + bbMeas + expInfo + sampleInfo + expValues)

            request.session['headerTable'] = headerTable
            request.session['tableData'] = tableData

            transaction.commit()
            return HttpResponseRedirect(reverse('profiling.views.view_results'))
        except Exception, e:
            print 'error' + str(e)
            transaction.rollback()
            return HttpResponseBadRequest("Page not available! " + e.args[0])



@laslogin_required
@login_required
@permission_decorator('profiling.can_view_FPM_filter_results')
@transaction.commit_manually
def view_results(request):
    resp = {}
    if request.session.has_key('headerTable'):
        resp['headerTable'] = request.session['headerTable']
        del request.session['headerTable']
    if request.session.has_key('tableData'):
        resp['tableData'] = request.session['tableData']
        del request.session['tableData']
    return render_to_response('view_results.html', resp, RequestContext(request))