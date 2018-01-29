from __init__ import *


@laslogin_required 
@login_required
@permission_decorator('cellLine.can_view_CLM_protocol')
def generation_page_prot_change_cc(request):
    print 'CLM view: start protocol.generation_page_prot_change_cc'
    try:
        #print request.GET
        listTypeProtocol, listTypeProcess,listPlates = [],[],[]
        storageHost = Urls_handler.objects.get(name = 'storage').url
        url = storageHost + '/api.info/containertype/'
        print url
        u = urllib2.urlopen(url)
        plates = ast.literal_eval(u.read())
        print plates
        for p in plates:
            listPlates.append((p, p))
        typeProtocol = Allowed_values.objects.filter(condition_feature_id = Condition_feature.objects.get(name = 'type_protocol'))
        for t in typeProtocol:
            listTypeProtocol.append((t.allowed_value, t.allowed_value))
        typeProcess = Allowed_values.objects.filter(condition_feature_id = Condition_feature.objects.get(name = 'type_process'))
        for t in typeProcess:
            listTypeProcess.append((t.allowed_value, t.allowed_value))
        form = NewProtocolForm(listPlates, listTypeProtocol, listTypeProcess)
        if request.method == 'POST':
            print request.POST
            print request.FILES
            #se c'e' il campo description nella post, vuol dire che l'utente ha inviato le info base del protocollo
            if 'description' in request.POST:
                form = NewProtocolForm(listPlates, listTypeProtocol, listTypeProcess, request.POST)
                if form.is_valid():
                    print 'here1'
                    request.session['newProtPost'] = request.POST #informazioni generali del protocollo
                    print request.session['newProtPost']
                    if len(request.FILES) > 0:
                        f = request.FILES['fileName']
                        fn = os.path.basename(f.name)
                        print settings.TEMP_URL
                        filePath = os.path.join(os.path.dirname(__file__).rsplit('/', 1)[0],settings.TEMP_URL+fn)
                        open(filePath, 'wb').write(f.read())
                        request.session['fileInfo'] = fn
                    types = Condition_protocol_element.objects.filter(condition_protocol_element_id__isnull = True)
                    return render_to_response('protocol/createProtocol.html',{'user': request.user,'type_el':types,'selectComponent':'selectComponent',},context_instance=RequestContext(request))

            if 'elementsDict' in request.POST:
                request.session['elementsDict'] = request.POST
                print 'asd'
                return HttpResponseRedirect(reverse("cellLine.protocol.saveNewProtocol"))
        if request.method == 'GET' and 'namecc' in request.GET:
            print 'namecc'
            idcc = request.GET['namecc']#.rsplit('_', 1)[0]
            namecc = Condition_configuration.objects.get(id = idcc).condition_protocol_id.protocol_name
            print namecc
            #protocols_list = []     
            #for cc in Condition_protocol.objects.all():
            #    protocols_list.append({'id':cc.id, 'conf_name':cc.protocol_name})


            protocols_list = []
            for cond_ft_name in Condition_feature.objects.filter(name="type_protocol"):
                for cond_has_ft in Condition_has_feature.objects.filter(condition_feature_id= cond_ft_name, value="expansion"):
                    if cond_has_ft.condition_configuration_id.version == 0:
                        pId = cond_has_ft.condition_configuration_id.id
                        pn = cond_has_ft.condition_configuration_id.condition_protocol_id.protocol_name + '_' + str(cond_has_ft.condition_configuration_id.version)
                        tp = Condition_has_feature.objects.get(condition_configuration_id = pId, condition_feature_id = Condition_feature.objects.filter(name="type_process")).value
                        typeP = Condition_has_feature.objects.get(condition_configuration_id = pId, condition_feature_id = Condition_feature.objects.get(name = 'type_plate')).value
                        protocols_list.append({'id':pId, 'protocol_name':pn,'type_process':tp,'type_plate':typeP})
            print protocols_list



            types = Condition_protocol_element.objects.filter(condition_protocol_element_id__isnull = True)
            return render_to_response('protocol/mod_culturing_condition.html',
                {'user': request.user, 'form': form, 'namecc':namecc, 'cc_id':idcc, 'selectComponent':'selectComponent', 'protocols_list':protocols_list, 'type_el':types, }, 
                context_instance=RequestContext(request))
        return render_to_response('protocol/createProtocol.html',
            {'user': request.user, 'form': form, 'start':'start', }, context_instance=RequestContext(request))
    except Exception, e:
        print 'CLM VIEW protocol.generation_page_prot_change_cc : 1)' + str(e)
        return render_to_response('error_page.html', {'user': request.user,'name':'Protocol Manager', 'err_message': "Something went wrong! " + str(e)  })

def protocolReport(nameE, nameF, value, unity):
    return "<tr><td>"+nameE+"</td><td>"+nameF+"</td><td>"+value+"</td><td>"+unity+"</td></tr>"

@transaction.commit_manually
@laslogin_required 
@login_required
@permission_decorator('cellLine.can_view_CLM_protocol')
def saveNewProtocol(request):
    print 'CLM view: start protocol.saveNewProtocol'
    try:
        print request.session['newProtPost']
        protocolInfo = request.session['newProtPost']
        selectedElement = request.session['elementsDict']
        nameF = ""
        listReport = []
        nameP = protocolInfo['name_protocol']
        descrP = protocolInfo['description']
        print request.session.keys()
        print "kkkkkkk"
        responseUpload = ""
        if 'fileInfo' in request.session.keys():
            print 'file'
            nameF =  request.session['fileInfo']
            responseUpload = uploadRepFile({'operator':request.user.username}, os.path.join(settings.TEMP_URL, nameF))
            oldFilePath = os.path.join(os.path.dirname(__file__).rsplit('/', 1)[0],'cell_media/tempFiles/'+nameF)
            #oldFile = open(oldFilePath, 'rb')
            #oldFile.close()
            os.remove(oldFilePath)
            print 'file nuovo caricato', str(nameF), str(responseUpload)
            
            
        cp = Condition_protocol(creation_date_time = datetime.datetime.now(), protocol_name = nameP, description = descrP, file_name = responseUpload)
        cp.save()
        cc = Condition_configuration(version = 0, condition_protocol_id = cp)
        cc.save()
        typePlate = protocolInfo['plate']
        typeProcess = protocolInfo['type_process']
        typeProtocol = protocolInfo['type_of_protocol']
        cf = Condition_feature.objects.get(name = 'type_plate')
        chf = Condition_has_feature(value = typePlate, condition_feature_id = cf, condition_configuration_id = cc)
        chf.save()
        cf = Condition_feature.objects.get(name = 'type_process')
        chf = Condition_has_feature(value = typeProcess, condition_feature_id = cf, condition_configuration_id = cc)
        chf.save()
        cf = Condition_feature.objects.get(name = 'type_protocol')
        chf = Condition_has_feature(value = typeProtocol, condition_feature_id = cf, condition_configuration_id = cc)
        chf.save()        
        infoString = "Protocol Name: " + nameP + ", description: " + descrP + ".\n Type plate: "+typePlate + ", type process: "+typeProcess + " type protocol: " + typeProtocol
        #test: vediamo se va bene anche senza usare il meccanismo del max id
        print selectedElement
        selectedJson = json.loads(selectedElement['elementsDict'])
        for se in selectedJson:
            print 'key',str(se)
            print selectedJson[se]
            cpe = Condition_protocol_element.objects.get(name = str(se))
            #if len(selectedJson[se]) > 0:
            for feature in selectedJson[se]:
                print cpe
                print feature['nameF']
                print feature['unity']
                fu = feature['unity']
                if feature['unity'] == "":
                    fu = None

                cf = Condition_feature.objects.get(condition_protocol_element_id = cpe, name = feature['nameF'], unity_measure = fu)
                chf = Condition_has_feature(value = feature['value'], condition_feature_id = cf, condition_configuration_id = cc)
                chf.save()
                listReport.append(protocolReport(str(se), feature['nameF'], feature['value'], feature['unity']))
            #else:
            #    cf = Condition_feature.objects.get(condition_protocol_element_id = cpe, name = 'No feature')
            #    chf = Condition_has_feature(value = '-', condition_feature_id = cf, condition_configuration_id = cc)
            #    chf.save()
            #    listReport.append(protocolReport(str(se), 'No feature', '-', '-'))


        if 'newProtPost' in request.session:
            del request.session['newProtPost']
        if 'fileInfo' in request.session:
            del request.session['fileInfo']
        if 'elementsDict' in request.session:
            del request.session['elementsDict']


        transaction.commit()
        return render_to_response('protocol/report_new_protocol.html', {'user': request.user, 'listReport': listReport, 'infoString': infoString}, context_instance=RequestContext(request))
    except Exception, e:
        print 'CLM VIEW protocol.saveNewProtocol : 1)' + str(e)
        if 'newProtPost' in request.session:
            del request.session['newProtPost']
        if 'fileInfo' in request.session:
            del request.session['fileInfo']
        if 'elementsDict' in request.session:
            del request.session['elementsDict']
        transaction.rollback()
        
        return render_to_response('error_page.html', {'user': request.user,'name':'Protocol Manager', 'err_message': "Something went wrong! " + str(e)  })
