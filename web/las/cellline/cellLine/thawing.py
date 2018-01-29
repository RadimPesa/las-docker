from __init__ import *


@laslogin_required 
@login_required
@permission_decorator('cellLine.can_view_CLM_thawing')
def start(request):    
    print 'CLM view: start thawing.start'
    try: 
        print request.POST
        protocols_list = []
        for cond_ft_name in Condition_feature.objects.filter(name="type_protocol"):
            for cond_has_ft in Condition_has_feature.objects.filter(condition_feature_id= cond_ft_name, value="expansion"):
                if cond_has_ft.condition_configuration_id.version == 0:
                    pId = cond_has_ft.condition_configuration_id.id
                    pn = cond_has_ft.condition_configuration_id.condition_protocol_id.protocol_name
                    tp = Condition_has_feature.objects.get(condition_configuration_id = pId, condition_feature_id = Condition_feature.objects.filter(name="type_process")).value
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
                    return render_to_response('generation/generation.html',{'user': request.user,'protocols_list': protocols_list, "plate":Plate(), 'typeOperation':'Thawing', 'data':json.dumps(lisfin), 'reqId':reqId,'diznick':json.dumps(diznick)}, RequestContext(request))
                else:                    
                    u = External_request.objects.get(id = reqId).username
                    return render_to_response('error_page.html', {'name':'Generation', 'err_message': "All data saved. Warning: you can't manage this request. It is assigned to " + u}, RequestContext(request))
            return render_to_response('generation/generation.html',{'user': request.user,'protocols_list': protocols_list, "plate":Plate(), 'typeOperation':'Thawing','diznick':json.dumps({})}, RequestContext(request))
    except Exception, e:
        print 'CLM view: thawing.start 1)', str(e)
        return render_to_response('error_page.html', {'name':'Thawing', 'err_message': "Error: something went wrong" }, RequestContext(request))

@laslogin_required 
@login_required
@permission_decorator('cellLine.can_view_CLM_thawing')
def manage_pending(request):
    print 'CLM view: start thawing.manage_pending'
    pending1 = External_request.objects.filter(username = request.user, action = 'CellLineThawing', done = False,deleteTimestamp=None)
    pending2 = External_request.objects.filter(username = '', action = 'CellLineThawing', done = False,deleteTimestamp=None)
    pending=list(chain(pending1,pending2))
    pendingList = {}
    for p in pending:
        #pendingList.append({str(p.id):p.data})
        pendingList[str(p.id)] = p.data
    if len(pendingList) > 0:
        print 'pendingList',pendingList
        return render_to_response('generation/pending.html', {'typeOperation':'Thawing', 'pendingList':pending, 'pendingString': json.dumps(pendingList) }, RequestContext(request))
    else:
        return render_to_response('generation/pending.html', {'typeOperation':'Thawing', 'message': "No pending thawing found for current user." }, RequestContext(request))

###############################################
### LE ALTRE FUNZIONI PER SALVARE E GESTIRE ###
### ERRORI SONO NEL FILE GENERATION.PY		###
###############################################
