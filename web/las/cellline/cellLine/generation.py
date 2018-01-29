from __init__ import *
from django.http import HttpResponse

@laslogin_required
@login_required
@permission_decorator('cellLine.can_view_CLM_generation')
def generation_page_aliquots(request):
    print 'CLM view: start generation.generation_page_aliquots'
    try:
        protocols_list = []
        for cond_ft_name in Condition_feature.objects.filter(name="type_protocol"):
            for cond_has_ft in Condition_has_feature.objects.filter(condition_feature_id= cond_ft_name, value="generation"):
                if cond_has_ft.condition_configuration_id.version == 0:
                    print '1'
                    pId = cond_has_ft.condition_configuration_id.id
                    print '2'
                    pn = cond_has_ft.condition_configuration_id.condition_protocol_id.protocol_name
                    print '3'
                    print pId
                    print Condition_feature.objects.filter(name="type_process")
                    tp = Condition_has_feature.objects.get(condition_configuration_id = pId, condition_feature_id = Condition_feature.objects.filter(name="type_process")).value
                    print '4'
                    protocols_list.append({'id':pId, 'protocol_name':pn,'type_process':tp})
        if request.method == 'POST':
            print request.POST
            if "to_biobank" in request.POST:
                request.session['cellline_saving'] = request.POST
                return HttpResponseRedirect(reverse("cellLine.generation.to_biobank"))
        else:
            if "reqid" in request.GET:
                print 'from_biobank'
                reqId = request.GET['reqid']
                er1 = External_request.objects.filter(id = reqId, done = False, username = request.user,deleteTimestamp=None)
                er2 = External_request.objects.filter(id = reqId, done = False, username = '',deleteTimestamp=None)
                er=list(chain(er1,er2))
                if len(er) > 0:
                    data = json.loads(er[0].data)
                    print 'data',data
                    lisfin=[]
                    lisgen=[]
                    for diz in data:
                        print 'diz',diz
                        lisgen.append(diz['genid'])
                        if 'done' in diz:
                            if diz['done']==0:
                                lisfin.append(diz)
                        else:
                            lisfin.append(diz)
                    print 'lisfin',lisfin
                    print 'lisgen',lisgen
                    laliq=Aliquots.objects.filter(gen_id__in=lisgen)
                    print 'laliq',laliq
                    #chiave il gen e val il nick della linea
                    diznick={}
                    for al in laliq:
                        #l'aliquota arriva da un'archiviazione
                        if al.archive_details_id!=None:
                            nick=al.archive_details_id.events_id.cell_details_id.cells_id.nickname
                            diznick[al.gen_id]=nick
                        elif al.experiment_details_id!=None:
                            nick=al.experiment_details_id.events_id.cell_details_id.cells_id.nickname
                            diznick[al.gen_id]=nick
                    print 'diznick',diznick
                    return render_to_response('generation/generation.html',{'user': request.user,'protocols_list': protocols_list, "plate":Plate(), 'typeOperation':'Generation', 'data':json.dumps(lisfin), 'reqId':reqId,'diznick':json.dumps(diznick)}, RequestContext(request))
                else:
                    u = External_request.objects.get(id = reqId).username
                    return render_to_response('error_page.html', {'name':'Generation', 'err_message': "All data saved. Warning: you can't manage this request. It is assigned to " + u}, RequestContext(request))
            return render_to_response('generation/generation.html',{'user': request.user,'protocols_list': protocols_list, "plate":Plate(), 'typeOperation':'Generation','diznick':json.dumps({})}, RequestContext(request))
    except Exception, e:
        print 'CLM view: generation.generation_page_aliquots 1)', str(e)
        return render_to_response('error_page.html', {'name':'Generation', 'err_message': "Error: something went wrong" }, RequestContext(request))

@transaction.commit_manually
@laslogin_required
@login_required
@permission_decorator('cellLine.can_view_CLM_generation')
def to_biobank(request):
    print 'CLM view: start generation.to_biobank'
    try:
        cellline_saving = request.session['cellline_saving']
        typeOperation = cellline_saving['typeOperation']
        print typeOperation
        generation_tobiobank(cellline_saving)
        print '1-------'
        cells,als = generation_report_save(cellline_saving, request.user)
        print '2-------'
        if 'cellline_tobiobank' in request.session:
            del request.session['cellline_tobiobank']
        print '3-------'
        transaction.commit()
        return render_to_response('generation/report.html',{'list_celllines_generated':cells, 'list_aliquot_used': als, 'typeOperation':typeOperation}, RequestContext(request))
    except Exception, e:
        print 'CLM VIEW generation.to_biobank : 1)' + str(e)
        transaction.rollback()
        if 'cellline_tobiobank' in request.session:
            del request.session['cellline_tobiobank']
        return render_to_response('error_page.html', {'name':'Generation', 'err_message': "Error: something went wrong" }, RequestContext(request))

def generation_report_save(cellline_saving,user):
    print 'CLM view: start generation.generation_report_save'
    to_generation = json.loads(cellline_saving['to_generation'])
    tableCL, tableA = '', ''
    print 'cellline_saving',cellline_saving
    print 'to_generation',to_generation
    aliquots = []    
    if cellline_saving['reqId'] != "":
        er = External_request.objects.get(id = cellline_saving['reqId'])
        data=json.loads(er.data)
        print 'data',data
        lisfin=[]
        contatore=0
        for d in data:
            gendata=d['genid']
            print 'gendata',gendata
            diznuovo=dict(d)
            for genid in to_generation.keys():
                for gen_source in to_generation[genid]['genid_source']:
                    print 'gen source',gen_source
                    if gen_source==gendata:
                        diznuovo['done']=1                    
                        if gen_source not in aliquots:                        
                            aliquots.append(gen_source)
            if diznuovo['done']==1:
                contatore+=1
            lisfin.append(diznuovo)
        print 'lisfin',lisfin
        #se il numero di oggetti messi a done=1 adesso sommato a quelli che lo erano gia' e' uguale alla lunghezza della lista iniziale
        print 'contatore',contatore
        print 'len data',len(data)
        if contatore==len(data):
            er.done = True
            if er.username=='':
                er.username=user.username
        er.data=json.dumps(lisfin)
        er.save()
        try:
            name = 'biobank'            
            experiment = er.action
            url = Urls_handler.objects.get(name = name).url + '/api/experiment/confirm'
            print 'aliquots',aliquots
            data = urllib.urlencode({'aliquots':json.dumps(aliquots), 'experiment':experiment, 'operator':user.username})
            req = urllib2.Request(url, data=data, headers={"workingGroups" : get_WG_string()})
            u = urllib2.urlopen(req)
        except urllib2.HTTPError,e:
            if str(e.code)=='403':
                print 'CLM view: generation.generation_report_save: 403 NON VALIDO'
                #return_dict = {"message":str(e.code)}
                #json_response = json.dumps(return_dict)
                #return HttpResponse(json_response,mimetype='application/json')
    for genid in to_generation.keys():
        genid_source = to_generation[genid]['genid_source']
        for p in to_generation[genid]['prot']:
            print p
            nickname = p['nickname']
            num_plates = p['num_plates']
            prot_name = p['name']
            prot_id = p['id']
            nickid = p['nickid']
            print 'num plates',num_plates
            if int(num_plates)>0:
                generation_save(genid_source, genid, nickname, num_plates,prot_name, user, prot_id, nickid)
                tableCL += '<tr><td>'+genid+'</td><td>'+prot_name+'</td><td>'+nickname+'</td><td>'+str(num_plates)+'</td></tr>'

    print '##########'
    aliquots = json.loads(cellline_saving['to_biobank'])
    print aliquots
    for plate in aliquots:
        for position in aliquots[plate]:
            if position != 'emptyFlag':
                sourceG = aliquots[plate][position]['aliquot']
                if aliquots[plate][position]['actualQ']==None:
                    pieces=''
                else:
                    pieces = int(aliquots[plate][position]['iniQ']) - int(aliquots[plate][position]['actualQ'])
                tableA += '<tr><td>' + sourceG + '</td><td>' + plate + '</td><td>' + position + '</td><td>'+str(pieces)+'</td></tr>'
    print tableCL, tableA
    return tableCL, tableA

def generation_tobiobank(cellline_saving):
    print 'CLM view: start generation.generation_tobiobank'
    try:
        name = 'biobank'
        implants = cellline_saving['to_biobank']
        url = Urls_handler.objects.get(name = name).url + '/api/aliquot/canc/'
        data = urllib.urlencode({'implants':implants})
        req = urllib2.Request(url, data=data, headers={"workingGroups" : get_WG_string()})
        u = urllib2.urlopen(req)
        return HttpResponse(u.read(),mimetype='application/json')
    except urllib2.HTTPError,e:
        if str(e.code)=='403':
            print 'CLM view: generation.generation_tobiobank: 403 NON VALIDO'
            return_dict = {"message":str(e.code)}
            json_response = json.dumps(return_dict)
            return HttpResponse(json_response,mimetype='application/json')

def generation_save(gen_source, genid, nick, num_p, prot_name, user, pId, nickid):
    print 'CLM view: start generation.generation_save'
    print 'CLM view: generation.generation_save ',gen_source, genid, nick, num_p, prot_name, user, pId
    user_ = User.objects.get(username = user)
    #group = Cellline_users.objects.get(user_ptr_id = user_).cancer_research_group_id

    ##aliquots
    disable_graph()
    for g in gen_source:
        print g
        if  Aliquots.objects.filter(gen_id = g).exists():
            aliquot = Aliquots.objects.get(gen_id = g)
        else:
            aliquot = Aliquots(gen_id=g)
            aliquot.save()
    enable_graph()

    ##cells
    cell = Cells(genID = genid, nickname = nick, nickid = nickid)#, cancer_research_group_id = group)
    cell.save()

    # rel cell aliquots
    for g in gen_source:
        aliquot = Aliquots.objects.get(gen_id = g)
        cha = Cells_has_aliquots(cells_id = cell, aliquots_id = aliquot)
        cha.save()

    ##cell_details
    #protocol = Condition_protocol.objects.get(id = pId)
    protocol = Condition_configuration.objects.get(id = pId).condition_protocol_id
    configuration = Condition_configuration.objects.get(condition_protocol_id = protocol, version = 0)
    cell_details = Cell_details(num_plates=num_p,start_date_time=str(timezone.localtime(timezone.now())),cells_id=cell,condition_configuration_id=configuration, generation_user= user_)
    cell_details.save()


@laslogin_required
@login_required
@permission_decorator('cellLine.can_view_CLM_generation')
def manage_pending(request):
    print 'CLM view: start generation.manage_pending'
    pending1 = External_request.objects.filter(username = request.user, action = 'CellLineGeneration', done = False,deleteTimestamp=None)
    pending2 = External_request.objects.filter(username = '', action = 'CellLineGeneration', done = False,deleteTimestamp=None)
    pending=list(chain(pending1,pending2))
    pendingList = {}
    for p in pending:
        #pendingList.append({str(p.id):p.data})
        pendingList[str(p.id)] = p.data
    if len(pendingList) > 0:
        print pendingList
        return render_to_response('generation/pending.html', {'typeOperation':'Generation', 'pendingList':pending, 'pendingString': json.dumps(pendingList) }, RequestContext(request))
    else:
        return render_to_response('generation/pending.html', {'typeOperation':'Generation', 'message': "No pending generation found for current user." }, RequestContext(request))

@laslogin_required
@login_required
@permission_decorator('cellLine.can_view_CLM_generation')
def delete_pending(request):
    print 'CLM view: start generation.delete_pending'
    try:
        if 'delete' in request.POST:
            idplan=request.POST['idplan']
            print 'idplan',idplan
            experiment=request.POST['experiment']
            print 'exp',experiment
            if experiment=='Generation':
                exp='CellLineGeneration'
            elif experiment=='Thawing':
                exp='CellLineThawing'
            extreq=External_request.objects.get(id=idplan)
            extreq.deleteTimestamp=timezone.localtime(timezone.now())
            extreq.deleteOperator=request.user
            extreq.save()
            print 'extreq',extreq
            #comunico alla biobanca di cancellare quegli esperimenti. Passo la lista delle aliquote che compongono l'esperimento
            #Prendo solo quelle con done=0
            data=json.loads(extreq.data)
            print 'data',data
            lisfin=[]
            contatore=0
            for d in data:
                gendata=d['genid']
                print 'gendata',gendata
                if 'done' in d:
                    if d['done']==0:
                        lisfin.append(gendata)
                else:
                    lisfin.append(gendata)
            print 'lisfin',lisfin
            
            url = Urls_handler.objects.get(name = 'biobank').url + '/api/experiment/canc'
            data = urllib.urlencode({'aliquots':json.dumps(lisfin), 'experiment':exp,'operator':request.user.username,'notes':''})
            req = urllib2.Request(url, data=data, headers={"workingGroups" : get_WG_string()})
            u = urllib2.urlopen(req)
            res = u.read()
            res = json.loads(res)
            print res
            if res['data'] != 'OK':
                raise Exception()
                
        return HttpResponse("ok")
    except Exception,e:
        print 'err',e
        return HttpResponse("error")

