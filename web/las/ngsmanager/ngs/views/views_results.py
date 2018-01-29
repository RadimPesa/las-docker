from __init__ import *

@laslogin_required
@login_required
@permission_decorator('ngs.can_view_NGS_run_experiment')
def get_results(request):
    mdamTemplates = getMdamTemplates([41,44,45])
    print 'mdamTemplates',mdamTemplates
    diz=retrievegenIDValues()
    return render_to_response('get_results.html', {'genid':json.dumps(diz),'mdamTemplates':json.dumps(mdamTemplates), 'mdam_url': Urls.objects.get(id_webservice=WebService.objects.get(name='mdam').id, available=True).url },  RequestContext(request))

@csrf_exempt
def downloadResults(request):
    try:
        sNodesJson = json.loads(request.POST['selectedNodes'])
        dataStruct = json.loads(request.POST['dataStruct'])

        sNodes = {}
        selectedNodes = [ s.strip().split('|') for s in sNodesJson  ]
        print sNodesJson, selectedNodes
        for pathNode in selectedNodes:
            current_level = sNodes
            for part in pathNode:
                if part not in current_level:
                    current_level[part] = {}
                current_level = current_level[part]
        
        print sNodes

        now = datetime.datetime.now()
        tmpDir = str(request.user) + '-' + str(now)
        os.mkdir ( os.path.join(settings.TEMP_URL, tmpDir) )

        repositoryUrl = Urls.objects.get(id_webservice=WebService.objects.get(name='repository').id, available=True)

        for sid, sample in dataStruct.items():
            print sid, sample
            if sNodes.has_key(sid):
                currPath = os.path.join(settings.TEMP_URL, tmpDir, sample['genid'] + '_' + sample['barcode'] )
                os.mkdir ( currPath )
                for rid, run in sample['runs'].items():
                    if sNodes[sid].has_key(rid):
                        print rid, run
                        currPath = os.path.join(settings.TEMP_URL, tmpDir, sample['genid'] + '_' + sample['barcode'], run['time_executed'] + '_' + run['title'] )
                        os.mkdir ( currPath )
                        for fid, fileSource in run['files'].items():
                            print fid, fileSource
                            if sNodes[sid][rid].has_key(fid):
                                link = fileSource['link']
                                r = requests.get(repositoryUrl.url + "get_file/"+ link, verify=False, stream=True)
                                with open(os.path.join(currPath, fileSource['name']) , 'wb') as f:
                                    for chunk in r.iter_content(chunk_size=1024): 
                                        if chunk: # filter out keep-alive new chunks
                                            f.write(chunk)
                                            f.flush()

        archiveFile = tarfile.open(path.join(TEMP_URL, tmpDir + '.tar.gz'),mode='w:gz')
        print 'archive file created'

        #listFiles = [path.join(TEMP_URL, archiveName + '.tar.gz')]
        archiveFile.add( os.path.join(settings.TEMP_URL, tmpDir) , arcname=tmpDir)
        print 'added folder'
        #listFiles.append(destination)
        archiveFile.close()

        print 'archiveFile closed'

        fout = open( path.join(TEMP_URL, tmpDir + '.tar.gz') )
        #print os.path.join(settings.TEMP_URL, 'tmp.txt')
        #fout = open ('/home/alessandro/poste_amazon.pdf', "rb")
        response = HttpResponse(fout, content_type='application/octet-stream')
        print 'response'
        response['Content-Disposition'] = 'attachment; filename=' + tmpDir + '.tar.gz'

        shutil.rmtree( os.path.join(settings.TEMP_URL, tmpDir) )
        os.remove(path.join(TEMP_URL, tmpDir + '.tar.gz'))
        return response
    except Exception, e:
        print e
        return HttpResponseBadRequest("Error in retrieving data")
