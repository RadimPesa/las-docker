from __init__ import *
from basic import *
from queryClass import *
from views_admin import *


def run_query(g, sesskey):
    import time
    start = time.time()

    qt = QTree()
    qt.sesskey = sesskey
    print "starting to parse graph"
    outputEntityId = qt.parse_query_graph(g)

    print "graph parsed"
    print "starting tree traversal"
    header, body, trans_meta, trans_body = qt.traverse_tree()
    print len(body), " records"
    print "time: ", time.time() - start
    qt.cleanup()
    return header, body, trans_meta, trans_body, outputEntityId

@laslogin_required
@login_required
def report(request):
    try:
        ent=request.session['entity']
            
        if "jsonStr" in request.POST:
            selected_ = request.POST['jsonStr']
            selected = json.loads(selected_)
            #print selected
            
            request.session['selected']=selected
            return HttpResponse()
                
         
        elif "jsonStr2" in request.POST:
            selected_ = request.POST['jsonStr2']
            selected = json.loads(selected_)
            #print selected
            
            request.session['selected']=selected
            
            return HttpResponse()
            
        else:
            name =  request.user.username
            report=request.session['bigObject']
            report = report.replace('\\n', ' ')
            return render_to_response('report.html', {'name':name, 'report':report, 'entity':ent}, RequestContext(request))
    except Exception, e:
        print "[MDAM] - ERRORE: "
        print e
        return HttpResponseRedirect(reverse("_caQuery.views.logout"))

@laslogin_required      
@login_required
@permission_decorator('_caQuery.can_view_MDAM_query_generator')
def querygen(request):
    if request.method == 'GET':
        title = None
        description = None
        g = None
        q = None
        template = None
        tparams = None
        if 'tqid' in request.GET or 'transid' in request.GET:
            try:
                if 'tqid' in request.GET:
                    template = QueryTemplate.objects.get(pk=request.GET['tqid'])
                else:
                    template = QueryTemplate.objects.get(pk=request.GET['transid'])
                title = template.name
                description = template.description
                templateparams = json.loads(template.parameters)
                templateConf = json.loads(template.configuration)
                

                tparams = {}
                for p in templateparams:
                    print p
                    i = 0
                    if not tparams.has_key( p['src_block_id'] ):
                        tparams[ p['src_block_id'] ] = {}
                    if p.has_key('src_f_id'):
                        tparams[ p['src_block_id'] ] [ str(p['bq_par_id']) ] = int(p['src_f_id'])
                    
                    else:
                        if p['type'] == 4:
                            tparams[ p['src_block_id'] ] [ str(p['bq_par_id']) ] = 'genid'
                        elif p['type'] == 3:
                            tparams[ p['src_block_id'] ] [ str(p['bq_par_id']) ] = i
                            i+=1




                tconf = {}

                print tparams
                
                for bid, c in templateConf.items():
                    tconf[bid] = {'inputs':c['inputs'], 'parameters':{}}
                    for pid, pconf in c['parameters'].items():
                        print pid, pconf
                        if tparams.has_key(bid):
                            if tparams[bid].has_key(pid):
                                #if pconf['opt'] != '2':
                                print 'insert ',  pconf
                                tconf[bid]['parameters'][ tparams[bid][pid] ] = pconf
                print 'tconf ', tconf

                query_dict = {
                    "start":
                        {
                            "parameters":None,
                            "query_path_id":[None],
                            "w_out":[], # fill
                            "offsetX":0,
                            "offsetY":0
                        },
                    "end":
                        {
                            "parameters":None,
                            "query_path_id":[None],
                            "w_in":[ unicode(template.outputBlockId)],
                            "offsetX":0,
                            "offsetY":0,
                            "translators": json.loads(template.outputTranslatorsList)
                        }
                    }

                g = json.loads(template.baseQuery)
                maxBid = max([int(k) for k in g.keys()] ) +1
                print maxBid
                g.update(query_dict)

                
                if 'transid' in request.GET:
                    newBlock = { unicode(maxBid):
                        {
                            "parameters":[],
                            "button_cat": "qent",
                            "query_path_id":None,
                            "outputs":[],
                            "w_out":[], # fill
                            "offsetX":50,
                            "offsetY":50, 
                            "w_in": ["start"], 
                            "button_id": template.translatorInputType.id,
                            "output_type_id": template.translatorInputType.id,
                        }
                    }

                    print 'newBlock ', newBlock
                    
                    for bid, bInfo in g.items():
                        print bid, bInfo
                        if bInfo.has_key('w_in'):
                            if bInfo['w_in'][0] == 'start':
                                bInfo['w_in'] = [unicode(maxBid)]
                                newBlock[unicode(maxBid)]['w_out'] = [ unicode(bid) +'.0']
                                newBlock[unicode(maxBid)]["query_path_id"] = bInfo['query_path_id']
                                print newBlock[unicode(maxBid)]['w_out']
                    print 'newBlock ',newBlock
                    
                    g['start']['w_out'] = [unicode(maxBid) +'.0']

                    g.update(newBlock)

                    print g
                 
                    

            except Exception, e:
                print e
                print "Template not found"

        if 'qid' in request.GET:
            try:
                q = SubmittedQuery.objects.get(pk=request.GET['qid'])
                title = q.title
                description = q.description
                g = q.query_graph
            except:
                print "Query not found: ", request.GET['qid']
        try:
            last_query_id = str(SubmittedQuery.objects.filter(author=request.user.id).order_by("-timestamp").only("id").first().id)
        except:
            last_query_id = None
        ds = []
        qe = []
        for x in DataSource.objects.all().order_by('name'):
            ds.append((x.name.lower().replace(' ', '_'), x))
            qe.append((x.name.lower().replace(' ', '_'), QueryableEntity.objects.filter(enabled=True,dsTable__in=DSTable.objects.filter(dataSource=x))))
        
        resp = {'ds': ds, 'qe': qe, 'ops': Operator.objects.exclude(pk=5).order_by('no'), 'genidtype': GenIDType.objects.all(), 'title': title, 'description': description, 'graph_nodes': json.dumps(g) if g else None, 'last_query_id': last_query_id}

        print 'final graph', g

        if q:
            resp['qid'] = q.pk

        if 'tqid' in request.GET:
        #if template:
            resp['tqid'] = template.pk
            resp['tparams'] = json.dumps(tconf)
            #print resp['tparams']
        if 'transid' in request.GET:
            resp['transid'] = template.pk
        
            
        response =  render_to_response('querygen.html', resp, RequestContext(request))
        # da verificare se funziona appena si crea un template/entita
        response["Cache-Control"] = "no-cache, no-store, must-revalidate"
        return response

    elif request.method == 'POST':
        print "Query received:"
        print request.POST
        queryTime = datetime.datetime.now()

        title = request.POST['title']
        description = request.POST['description']
        g = request.POST['graph_nodes']
        g = json.loads(g)
        
        qid = request.POST['qid']
        print 'qid', qid
        if qid != '':
            qOld = SubmittedQuery.objects.get(pk=qid)
            query_graph = qOld.query_graph
            print 'compare query_graph', query_graph != g
            print query_graph
            print g
            if not compareQueryGraph(query_graph, g):
                print 'generate new subquery'
                q = createQuery(title, description, queryTime, g, request.user.id)
            else:
                print 'use old query ', qOld.pk
                q = qOld
        else:
            q = createQuery(title, description, queryTime, g, request.user.id)
        
        print g
        
        for x in ['query_headers', 'query_results', 'query_results_global_search', 'query_results_col_search', 'aaData_indices', 'query_results_sort_keys']:
            if x in request.session:
                del request.session[x]

        h, b, trans_meta, trans_b, outputEntityId = run_query(g, request.session.session_key)

        #save query
        q.headers = h
        q.translators_meta = trans_meta
        q.has_translators = trans_meta != None
        q.outputEntityId = outputEntityId
        q.save()
        run = QueryRun()
        run.timestamp = queryTime
        run.user = request.user.id

        run.results.new_file()
        run.results.write(json.dumps(b))
        run.results.close()
        
        run.translators_results.new_file()
        run.translators_results.write(json.dumps(trans_b))
        run.translators_results.close()
        
        

        # update reference fields
        try:
            run.save()
            print 'save run 1'
            run.update(set__query = q)
            run.save()
            print 'update run'
            q.update(push__runs=run)
            q.save()
            print 'update q'
        except Exception, e:
            print 'Error ', e
        
        
        
        return HttpResponse(json.dumps({'qid': str(q.pk), 'rid': str(run.pk)}))

def createQuery(title, description, queryTime, g, author):
    q = SubmittedQuery()
    q.title = title
    q.description = description
    q.query_graph = deepcopy(g)
    q.author = author
    q.timestamp = queryTime
    return q

@laslogin_required  
@login_required
@gzip_page
@permission_decorator('_caQuery.can_view_MDAM_query_generator')
def displayresults(request):
    if 'qid' in request.GET and 'rid' in request.GET:
        qid = request.GET['qid']
        rid = request.GET['rid']
        q = SubmittedQuery.objects.get(pk=qid)
        if 'queries' not in request.session:
            print "displayresults: queries not in request.session"
            request.session['queries'] = {}
        queries = request.session['queries']
        queries[qid] = {}
        request.session.modified = True
        
        outputEntity= QueryableEntity.objects.get(id=q.outputEntityId)

        return render_to_response("displayresults.html", {'headers': zip(q.headers, q.column_keys), 'qid': qid, 'rid':rid, 'trans': q.has_translators, 'shareableOutput': outputEntity.shareable, 'canshare':request.user.has_perm('_caQuery.can_view_MDAM_share_data')}, RequestContext(request))
        

    else:
        return render_to_response("displayresults.html", RequestContext(request))

@csrf_exempt
def getresults(request):
    if request.method == 'GET' and 'qid' in request.GET and 'action' in request.GET and 'queries' in request.session and request.GET['qid'] in request.session['queries'] and 'rid' in request.GET:
        qid = request.GET['qid']
        rid = request.GET['rid']
        action = request.GET['action']
        print action, qid, rid
        if action == 'results':
            
            query_info = request.session['queries'][qid]

            nCols = int(request.GET['iColumns'])
            start = int(request.GET['iDisplayStart'])
            nRows = int(request.GET['iDisplayLength'])
            globalSearch = request.GET['sSearch'].lower()
            searchable = [json.loads(request.GET['bSearchable_' + str(x)]) for x in xrange(0,nCols)]
            colSearch = [request.GET['sSearch_' + str(x)].lower() for x in xrange(0,nCols)]
            colSearch_yes = len(filter(lambda x: x != '',colSearch)) > 0
            sortable = [json.loads(request.GET['bSortable_' + str(x)]) for x in xrange(0,nCols)]
            nSortCols = int(request.GET['iSortingCols'])
            sortingCols = [int(request.GET['iSortCol_' + str(x)]) for x in xrange(0,nSortCols)]
            sortingDirs = [True if request.GET['sSortDir_' + str(x)] == 'asc' else False for x in xrange(0,nSortCols)]
            echo = int(request.GET['sEcho'])
            
            q = SubmittedQuery.objects.get(pk=qid)
            run = QueryRun.objects.get(pk=rid)
            results = json.loads(run.results.read())
            iTotalRecords = len(results)

            # filter results
            def mySearchGlobalLocal(x):
                for i,f in enumerate(x):
                    f_lower = f.lower()
                    if globalSearch in f_lower or colSearch[i] in f_lower:
                        return True
                return False
            def mySearchGlobal(x):
                for i,f in enumerate(x):
                    if globalSearch in f.lower():
                        return True
                return False
            def mySearchLocal(x):
                for i,f in enumerate(x):
                    if colSearch[i] in f.lower():
                        return True
                return False

            current_global_search = query_info.get('query_results_global_search', None)
            current_col_search = query_info.get('query_results_col_search', None)

            if current_global_search != globalSearch or current_col_search != colSearch:
                print "different search keys"
                if globalSearch != '':
                    if colSearch_yes:
                        aaData_indices = [i for i,x in enumerate(results) if mySearchGlobalLocal(x)]
                    else:
                        aaData_indices = [i for i,x in enumerate(results) if mySearchGlobal(x)]
                else:
                    if colSearch_yes:
                        aaData_indices = [i for i,x in enumerate(results) if mySearchLocal(x)]
                    else:
                        aaData_indices = [i for i in xrange(0, len(results))]
                query_info['query_results_global_search'] = globalSearch
                query_info['query_results_col_search'] = colSearch
                query_info['aaData_indices'] = aaData_indices
                request.session.modified = True
            else:
                print "same search keys"
                aaData_indices = query_info['aaData_indices']

            iTotalDisplayRecords = len(aaData_indices)

            # sort results if needed
            
            columns = [list(x) for x in zip(sortingCols, sortingDirs)]
            def myCmp(x,y):
                for i,asc in columns:
                    res = cmp(x[i],y[i]) if asc else -cmp(x[i],y[i])
                    if res:
                        return res
                return 0
            
            current_sort_keys = run.sort_keys


            if current_sort_keys != columns:
                print "different sort keys"
                results.sort(myCmp)
                run.sort_keys = columns
                run.results.delete()
                run.results.new_file()
                run.results.write(json.dumps(results))
                run.results.close()
                run.save()
            else:
                #pass
                print "same sort keys"
            

            nRows = iTotalRecords if nRows == -1 else nRows

            #aaData = [results[aaData_indices[i]] for i in xrange(start,min(start+nRows, len(aaData_indices)))]
            ##print results[aaData_indices[0]] 
            aaData = []
            print results
            for i in xrange(start,  min(start+nRows, len(aaData_indices)) ): 
                rowData = {}
                for r in xrange( len( results[aaData_indices[i]])):
                    rowData[q.column_keys[r]] = results[ aaData_indices[i] ] [r]
                aaData.append( rowData )
            
            #print aaData
            
            sEcho = str(echo)

            
            res = { 'iTotalRecords': iTotalRecords,
                    'iTotalDisplayRecords': iTotalDisplayRecords,
                    'sEcho': sEcho,
                    'aaData': aaData}
            
            #res = { 'data': aaData}
            #print res
            return HttpResponse(json.dumps(res))

        elif action == 'translators' and 'rowid' in request.GET:
            rowid = request.GET['rowid']
            print qid, rid
            q = SubmittedQuery.objects.get(pk=qid)
            run = QueryRun.objects.get(pk=rid)
            trans_meta = q.translators_meta
            trans_results = json.loads(run.translators_results.read())
            print trans_results[rowid]
            res = {'meta': trans_meta, 'data': trans_results[rowid]}
            return HttpResponse(json.dumps(res))
        elif action == 'getHeaders':
            q = SubmittedQuery.objects.get(pk=qid)
            run = QueryRun.objects.get(pk=rid)
            trans_meta = q.translators_meta
            queryHeader = q.headers
            columnKeys = q.column_keys
            res = {'queryHeader': queryHeader, 'columnKeys': columnKeys, 'meta': trans_meta}
            return HttpResponse(json.dumps(res))

        else:
            return HttpResponse()
    elif request.method == 'POST':
        print request.POST
        if 'action' in request.POST:
            action = json.loads(request.POST['action'])
            if action == 'download':
                print request.POST
                lasauthserverUrl = Urls.objects.get(idWebService=WebService.objects.get(name='LASAuthServer').id).url
                try:
                    fileTypes = json.loads(request.POST['fileTypes'])
                    headers = json.loads(request.POST['headers'])
                    qid = json.loads(request.POST['qid'])
                    rid = json.loads(request.POST['rid'])
                    
                
                    now = datetime.datetime.now()
                    tmpDir = str(request.user) + '-' + str(now)
                    start = datetime.datetime.now()
                    dataTable = prepareDataTable(qid, rid, headers, tmpDir)

                    print 'prepare data ', datetime.datetime.now() - start



                    if len(fileTypes) > 1:
                        os.mkdir ( os.path.join(settings.TEMP_URL, tmpDir) )
                        
                        for ft in fileTypes:
                            start = datetime.datetime.now()
                            writeReport(dataTable, ft, os.path.join(settings.TEMP_URL, tmpDir), tmpDir)
                            print datetime.datetime.now() - start

                        archiveFile = tarfile.open(path.join(settings.TEMP_URL, tmpDir + '.tar.gz'), mode='w:gz')
                        archiveFile.add( os.path.join(settings.TEMP_URL, tmpDir) , arcname=tmpDir)
                        archiveFile.close()
                        print 'archive file created'

                        fout = open( path.join(settings.TEMP_URL, tmpDir + '.tar.gz') )
                        response = HttpResponse(fout, content_type='application/octet-stream')
                        response['Content-Disposition'] = 'attachment; filename=' + tmpDir + '.tar.gz'
                        shutil.rmtree( os.path.join(settings.TEMP_URL, tmpDir) )
                        os.remove(path.join(settings.TEMP_URL, tmpDir + '.tar.gz'))    
                    else:
                        start = datetime.datetime.now()
                        fileName = writeReport(dataTable, fileTypes[0], settings.TEMP_URL, tmpDir)
                        print datetime.datetime.now() - start                        
                        print 'fileName ', fileName, path.join(settings.TEMP_URL, fileName)
                        fout = open (path.join(settings.TEMP_URL, fileName) )
                        response = HttpResponse(fout, content_type='application/octet-stream')
                        response['Content-Disposition'] = 'attachment; filename=' + fileName
                        os.remove(path.join(settings.TEMP_URL, fileName))    
                                        
                    return response
                except Exception, e:
                    print e
                    return HttpResponseBadRequest("Error in retrieving data")

    else:
        return HttpResponse()


def prepareDataTable(qid, rid, headers, fileName):
    dataTable = {}
    dataTable['filename'] = fileName

    q = SubmittedQuery.objects.get(pk=qid)
    print 'q.headers', q.headers
    run = QueryRun.objects.get(pk=rid)
    results = json.loads(run.results.read())
    trans_meta = q.translators_meta
    trans_results = json.loads(run.translators_results.read())
    
    tableHead = []

    tableBody = {}
    translators = {}

    
    for k in headers.keys():
        tableBody[k] = []
        if k != '-1':
            translators[k] = []
    
    print translators

    for row in results:
        pk = row[0]
        rowTable = []
        for cellid in headers['-1']:
            rowTable.append( row[int(cellid)] )
        tableBody['-1'].append(rowTable)
        if trans_results != None:
            for transId, tData in trans_results[pk].items():
                rowTable = []
                for transData in tData:
                    for cellid in headers[transId]:
                        rowTable.append( transData[int(cellid)] )

                tableBody[str(transId)].append(rowTable)
                translators[str(transId)].append(len(tData))

    
    for tid, tval in translators.items():
        translators[tid] = max(tval)

    for cellid in headers['-1']:
        tableHead.append(q.headers[int(cellid)])

    listTrans = []
    print trans_meta
    for transId, tVal in translators.items():
        listTrans.append(transId)
        for i in xrange(tVal):
            suffix = ''
            if tVal > 1:
                suffix = '_'+ str(i)
            for cellid in headers[transId]:
                tableHead.append( trans_meta[transId]['title'] + ' - ' + trans_meta[transId]['headers'][int(cellid)] + suffix )

    tableData = []

    listTrans.insert(0, '-1')

    nRows = len(tableBody['-1'])
    print nRows
    for i in xrange(nRows):
        trow = []
        for tid in listTrans:
            if tid == '-1':
                trow.extend(tableBody[tid][i])
            else:
                trowPad = []
                if len(tableBody[tid][i]) != (len(headers[tid]) * translators[tid]):
                    ncol = (len(headers[tid]) * translators[tid]) - len(tableBody[tid][i])
                    trowPad = [ ''  for x in xrange(ncol) ]
                trow.extend(tableBody[tid][i])
                trow.extend(trowPad)

        tableData.append(trow)





        

    dataTable['header'] = tableHead
    dataTable['body'] = tableData
    #print dataTable
    return dataTable

'''
def getReport(lasauthserverUrl, dataTable, fileformat, pathDir, fileName):
    dataTable['fileformat'] = fileformat

    extension = {'las':'.las', 'data':'.data', 'excel':'.xls', 'pdf':'.pdf'}
    print lasauthserverUrl + "/generate_report/"
    r = requests.post(lasauthserverUrl + "/generate_report/", data={'tabledata':json.dumps(dataTable)}, verify=False, stream=True)
    with open(os.path.join(pathDir, fileName + extension[fileformat]) , 'wb') as f:
        for chunk in r.iter_content(chunk_size=1024): 
            if chunk: # filter out keep-alive new chunks
                f.write(chunk)
                f.flush()
    return fileName + extension[fileformat]
'''




@laslogin_required  
@login_required
@gzip_page
@permission_decorator('_caQuery.can_view_MDAM_query_generator')
def historyQuery(request):
    if request.method == 'GET':
        print request.GET
        queriesRuns = QueryRun.objects.filter(user=request.user.id)

        historyRuns = {}
        dateQueries = {}

        for r in queriesRuns:
            try:
                if not historyRuns.has_key(str(r.query.pk)):
                    historyRuns[str(r.query.pk)] = {'qid': str(r.query.pk), 'title':r.query.title, 'description': r.query.description, 'author': User.objects.get(pk=r.query.author).username, 'creation':r.query.timestamp.strftime('%Y-%m-%d %H:%M:%S'), 'runs':[] , 'nruns': len(r.query.runs)  }
                    dateQueries[str(r.query.pk)] = []
                historyRuns[str(r.query.pk)]['runs'].append({'timestamp': r.timestamp.strftime('%Y-%m-%d %H:%M:%S'), 'rid': str(r.pk), 'qid': str(r.query.pk)})
                dateQueries[str(r.query.pk)].append(r.timestamp)
            except Exception, e:
                continue

        history = []
        for k, v in historyRuns.items():
            v['lastrun'] = max(dateQueries[k]).strftime('%Y-%m-%d %H:%M:%S')
            history.append( v )

        return render_to_response("historyquery.html", {'history': json.dumps(history)}, RequestContext(request))

    else:
        qid = request.POST['qid']
        print qid
        try:
            qOld = SubmittedQuery.objects.get(pk=request.POST['qid'])
            print 'get qOld'
            g = qOld.query_graph
            print g
            queryTime = datetime.datetime.now()

            run = QueryRun()
            run.timestamp = queryTime
            run.user = request.user.id

            
            for x in ['query_headers', 'query_results', 'query_results_global_search', 'query_results_col_search', 'aaData_indices', 'query_results_sort_keys']:
                if x in request.session:
                    del request.session[x]

            h, b, trans_meta, trans_b, outputEntityId = run_query(g, request.session.session_key)
            
            run.results.new_file()
            run.results.write(json.dumps(b))
            run.results.close()
            
            run.translators_results.new_file()
            run.translators_results.write(json.dumps(trans_b))
            run.translators_results.close()
            run.save()
            run.update(set__query = qOld)
            run.save()
            qOld.update(push__runs=run)
            qOld.save()

            return HttpResponse(json.dumps({'qid': str(qOld.pk), 'rid': str(run.pk)})) 
        except Exception, e:
            print e
            return HttpResponseServerError(str(e))

def compareQueryGraph(graph1, graph2):
    any_in = lambda a, b: any(i in b for i in a)
    excludeList = ['offsetX', 'offsetY']

    graph1List = []
    graph2List = []

    graph1Ser = dict_generator(graph1)
    graph2Ser = dict_generator(graph2)

    for i in graph1Ser:
        if not any_in(i, excludeList):
            graph1List.append(i)

    for i in graph2Ser:
        if not any_in(i, excludeList):
            graph2List.append(i)

    graph1Set = set(map(tuple, graph1List))
    graph2Set = set(map(tuple, graph2List))

    print graph1Set
    print graph2Set

    print graph1Set.symmetric_difference(graph2Set)
    print len( graph1Set.symmetric_difference(graph2Set) )

    if len( graph1Set.symmetric_difference(graph2Set) ) > 0:
        print 'return False'
        return False
    else:
        print 'return True'
        return True

def dict_generator(indict, pre=None):
    pre = pre[:] if pre else []
    if isinstance(indict, dict):
        for key, value in indict.items():
            if isinstance(value, dict):
                for d in dict_generator(value, [key] + pre):
                    yield d
            elif isinstance(value, list) or isinstance(value, tuple):
                for v in value:
                    for d in dict_generator(v, [key] + pre):
                        yield d
            else:
                yield pre + [key, value]
    else:
        yield [indict]
