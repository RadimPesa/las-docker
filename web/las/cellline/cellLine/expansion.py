from __init__ import *

@laslogin_required
@login_required
@permission_decorator('cellLine.can_view_CLM_expansion')
def expansion_page(request):
    print 'CLM view: start expansion.expansion_page'
    #lista delle linee cellulari ed eventuali modifiche fatte in precedenza
    if request.method == 'POST':
        #print request.POST
        request.session['expansionData'] = request.POST['cellsDict']
        return HttpResponseRedirect(reverse("cellLine.expansion.saveExpansion"))

    cdList = Cell_details.objects.filter(end_date_time__isnull = True)
    cell_list, idnamecc, usersList = initialCells(cdList)
    #print cell_list
    #lista dei protocolli di espansione
    #print json.dumps(cell_list)
    #print json.dumps(cell_list).replace("'", "")
    message = request.session.get('message', '')
    print '-----------'

    if message != '':
        print request.session['message']
        del request.session['message']
    forFile = request.session.get('forFile', [])
    if forFile != []:
        del request.session['forFile']

    if len(message) > len("Data correctly saved. "):
        bbUrl = 'err'
    else:
        bbUrl = Urls_handler.objects.get(name = 'biobank').url

    usersWG = ['']
    usersWG.extend(usersList)

    return render_to_response('expansion/expansion.html',{'user': request.user,'cdDict':json.dumps(cell_list).replace("'", ""),'cdList':cell_list, 'idnamecc':idnamecc, 'message':message, 'forFile':json.dumps(forFile), 'bbUrl':bbUrl, 'usersWG':usersWG },context_instance=RequestContext(request))


def initialCells(cdList):
    print 'CLM view: start expansion.initialCells'
    cell_list = {}
    idnamecc = {}
    usersList = []
    tipoespansion=Type_events.objects.get(type_name='expansion')
    condfeatpiastra=Condition_feature.objects.get(name = 'type_plate')
    lisfeat=Feature.objects.all()
    #Prendo le feature delle cellule per sapere quali operazioni sono state pianificate su ognuna
    lisidcelldetails=[]
    for cd in cdList:        
        lisidcelldetails.append(cd.id)
    lcellfeat=Cell_details_feature.objects.filter(cell_details_id__in=lisidcelldetails,end_date_time__isnull=True)
    print 'lcellfeat',lcellfeat
    #chiave l'id del cell details e valore
    dizfeaturecell={}
    for celldet in lcellfeat:
        idcelldetail=celldet.cell_details_id.id
        if idcelldetail in dizfeaturecell:
            listemp=dizfeaturecell[idcelldetail]
        else:
            listemp=[]
        listemp.append(celldet.feature_id.name)
        dizfeaturecell[idcelldetail]=listemp
    print 'dizfeaturecell',dizfeaturecell
    for cd in cdList:
        temp = {}
        temp['id'] = cd.cells_id.id

        #print str(cd.start_date_time)[0:19]
        temp['startDate'] = str(timezone.localtime(cd.start_date_time))[0:19]
        temp['nPlates'] = cd.num_plates
        temp['genID'] = cd.cells_id.genID
        temp['nickname'] = cd.cells_id.nickname
        temp['username'] = ''

        #temp['cc'] = Simple(cd.condition_configuration_id, ['id','conf_name']).getAttributes()
        temp['cc'] = {}
        temp['cc']['id'] = cd.condition_configuration_id.id
        temp['cc']['conf_name'] = cd.condition_configuration_id.condition_protocol_id.protocol_name + '_' + str(cd.condition_configuration_id.version)
        typeP = Condition_has_feature.objects.get(condition_configuration_id=cd.condition_configuration_id, condition_feature_id=condfeatpiastra ).value
        temp['cc']['typeP'] = typeP

        temp['mods'] = {}
        toTrash, toExperiment, toArchive, inputA, reduction, outputA, newProt, newProtID = 0, 0, 0, 0, 1, 0, '', ''
        print 'cell',cd.cells_id
        idcc = ""
        tempSlot = {'':''}
        if cd.cells_id.expansion_details_id is not None:
            cdFather = cd.cells_id.expansion_details_id.events_id.cell_details_id
            expansionEvents = Events.objects.filter(cell_details_id = cdFather,type_event_id =tipoespansion).order_by('-date_time_event')
            if len(expansionEvents) > 0:
                print 'event',expansionEvents
                #temp['username'] = expansionEvents[0].cellline_users_id.username
                temp['username']=cd.cells_id.expansion_details_id.events_id.cellline_users_id.username
                usersList.append(temp['username'])
                #expansionDetails = Expansion_details.objects.get(events_id = expansionEvents.latest('date_time_event'))
                #lastdate = expansionEvents.latest('date_time_event').date_time_event
                #expansionDetails = cd.cells_id.expansion_details_id
                #expansionDetails = expansionEvents.filter(date_time_event = lastdate)
                #cc = Cell_details.objects.filter(cells_id = Cells.objects.get(expansion_details_id = expansionDetails))[0].condition_configuration_id
                print 'len expansionevents', str(len(expansionEvents))
                for ee in expansionEvents:
                    exp = Expansion_details.objects.get(events_id = ee)
                    outputA = exp.output_area
                    print 'expansion details',exp
                    expansionedCell = Cells.objects.filter(expansion_details_id = exp)
                    if len(expansionedCell)!=0:
                        cc = Cell_details.objects.filter(cells_id = expansionedCell[0])[0].condition_configuration_id
                        newProtID = cc.id
                        #inputA, reduction, outputA  = expansionDetails.input_area, expansionDetails.reduction_factor, expansionDetails.output_area
                        inputA = exp.input_area
                        reduction = exp.reduction_factor
                        newProt = cc.condition_protocol_id.protocol_name + '_' + str(cc.version)
                        print 'newProt',newProt
                        idnamecc[newProtID] = newProt
                        tempSlot[newProtID] = outputA
                        if '' in tempSlot:
                            del tempSlot['']
            if cd.num_plates < toTrash+toExperiment+toArchive+inputA:
                toTrash, toExperiment, toArchive, inputA, reduction, outputA, newProt, newProtID = 0, 0, 0, 0, 1, 0, '', ''
        else:
            try:
                temp['username'] = cd.generation_user.username
                usersList.append(temp['username'])
            except:
                pass
        temp['mods']['toTrash'] = []
        temp['mods']['toTrash'].append({'amount': toTrash, 'applied':False})
        temp['mods']['toExperiment'] = []
        temp['mods']['toExperiment'].append({'amount': toExperiment, 'applied':False})
        temp['mods']['toArchive'] = []
        temp['mods']['toArchive'].append({'amount': toArchive, 'applied':False})
        temp['mods']['expansion'] = {}
        #temp['mods']['expansion'].append({'inputA':inputA, 'reduction':reduction, 'outputA':outputA, 'applied':False, 'newGenID':'', 'cc':newProt, 'cc_id':newProtID, 'rowID':'', 'toSave':True})
        temp['mods']['expansion']['generic'] = {'applied':False, 'newGenID':'', 'rowID':'', 'toSave':True, 'inputA':inputA, 'reduction':reduction}
        temp['mods']['expansion']['outputs'] = tempSlot
        ## questi non servono per avere il popolamento inziale ma solo per non dovere aggiungere voci al dict dal lato js ##
        temp['mods']['toReset'] = {}
        #temp['mods']['toReset'].append({'amount': 0, 'applied':False, 'cc':'', 'rowID':'', 'toSave':True})
        temp['mods']['toReset']['generic'] = {'applied':False, 'rowID':'', 'toSave':True}
        temp['mods']['toReset']['outputs'] = {}
        temp['plan'] = {}
        #now indica se l'azione e' stata programmata o meno. Quindi se e' True dovro' spuntare il check nella schermata
        for f in lisfeat:
            temp['plan'][f.name]={'now':False}
        if cd.id in dizfeaturecell:            
            listemp=dizfeaturecell[cd.id]
            for val in listemp: 
                temp['plan'][val] = {'now':True}
                
        key = cd.id
        cell_list[key] = temp
    print 'cell_list',cell_list
    usersList = list(set(usersList))
    return cell_list, idnamecc, usersList


def getIndex(featureList, nameF):
    print 'CLM view: start expansion.getIndex'
    #input example:
    #[{"nameF":"No feature","unity":null,"value":"-"}],"medicina2":[{"nameF":"dose","unity":"mg/g","value":"5"},{"nameF":"timeForDay","unity":"int","value":"66"}]
    for f in featureList:
        if nameF == f['nameF']:
            #print f
            return featureList.index(f)


@laslogin_required
@login_required
@permission_decorator('cellLine.can_view_CLM_expansion')
@transaction.commit_manually
def saveExpansion(request):
    print 'CLM view: start expansion.saveExpansion'
    #toArchive expansion toTrash toReset toExperiment
    #print request.session.keys()
    expansionData = json.loads(request.session['expansionData'])
    print 'expansionData',expansionData
    try:
        listGBio = []
        w = ''
        now = timezone.localtime(timezone.now())
        for cell_line in expansionData:
            print 'cell_line',cell_line
            cd = Cell_details.objects.get( pk = cell_line)
            print 'cd',cd
            processingArchive(expansionData[cell_line]['mods']['toArchive'], cd, now, request)
            processingTrash(expansionData[cell_line]['mods']['toTrash'], cd, now, request)
            processingExperiment(expansionData[cell_line]['mods']['toExperiment'], cd, now, request, listGBio)
            processingReset(expansionData[cell_line]['mods'], cd, now, request) #change media
            processingExpansion(expansionData[cell_line], cd, now, request)
            processingPlan(expansionData[cell_line]['plan'], cd, now, request)

        #transaction.commit()
        if len(listGBio) > 0:
            url = Urls_handler.objects.get(name = 'biobank').url + '/api/save/cell/'
            print url
            data = urllib.urlencode({'user':request.user, 'genIDList':json.dumps(listGBio)})
            req = urllib2.Request(url, data=data, headers={"workingGroups" : get_WG_string()})
            u = urllib2.urlopen(req)
            response = u.read()
            print '...'+response+'...'
            if response == '"err"':
                print '#################################################################'
                w = "Warning: error while linking with the biobank. The aliquots for experiments haven't been saved in Biobank Module."
        request.session['forFile'] = listGBio

        del request.session['expansionData']
        cdList = Cell_details.objects.filter(end_date_time__isnull = True)
        print 'commit'
        transaction.commit()
        #cell_list = initialCells(cdList)
        print '#####'
        request.session['message'] = 'Data correctly saved. ' + w
        return HttpResponseRedirect(reverse("cellLine.expansion.expansion_page"))
        #return render_to_response('expansion/expansion.html',{'user': request.user,'cdDict':json.dumps(cell_list).replace("'", ""),'cdList':cell_list, 'message':'Data correctly saved.' },context_instance=RequestContext(request))
    except Exception, e:
        transaction.rollback()
        print 'CLM view: expansion.saveExpansion: ', str(e)
        return HttpResponse(e)

#decrementa il num_plates della linea cellulare utilizzata. Se arriva a zero, mette la end_data a now.
def updateCellDetails(cd, amount, now):
    print 'CLM view: start expansion.updateCellDetails'
    print cd.num_plates, amount
    cd.num_plates = cd.num_plates - amount
    #print cd.num_plates, amount
    if cd.num_plates == 0:
        #print now
        cd.end_date_time = now
        #print '----'
    cd.save()
    return 0

def processingPlan(plandict, cd, now, request):
    print 'CLM view: start expansion.processingPlan'
    for key in plandict.keys():
        diztemp=plandict[key]
        print 'diztemp',diztemp
        if 'toSave' in diztemp:
            print 'diztemp now',diztemp['now']
            print 'diztemp toSave',diztemp['toSave']
            if diztemp['now']!=diztemp['toSave']:
                feat=Feature.objects.get(name=key)
                if diztemp['toSave']==True:                    
                    #devo aggiungere una feature di pianificazione per questa linea
                    cdf=Cell_details_feature(cell_details_id=cd,
                                             feature_id=feat,
                                             start_date_time=now,
                                             operator_id=request.user)
                    cdf.save()
                    print 'cdf',cdf
                if diztemp['toSave']==False:
                    #devo impostare l'end time per la cell details feature in questione
                    liscdf=Cell_details_feature.objects.filter(cell_details_id=cd,feature_id=feat,end_date_time__isnull=True)
                    print 'liscdf',liscdf
                    if len(liscdf)!=0:
                        liscdf[0].end_date_time=now
                        liscdf[0].save()
    return 0

def processingExpansion(expansionDict, cd, now, request):
    print 'CLM view: start expansion.processingExpansion'
    totAmount = 0
    expansionList=expansionDict['mods']
    print expansionList
    #cc = expansionList['new_cc']
    #cc_id = expansionList['new_ccID']
    #for toExpansion in expansionList['expansion']:
    inputA = 0
    expansionList = expansionList['expansion']
    if expansionList['generic']['applied'] == True and expansionList['generic']['toSave'] == True:
        for idcc in expansionList['outputs']:
            #{'inputA':inputA, 'reduction':reduction, 'outputA':outputA, 'applied':False, 'newGenID':'', 'cc':'', 'rowID':''}
            #if int(idcc):
            if str(expansionList['outputs'][idcc]).isdigit():
                outputA = int(expansionList['outputs'][idcc])
                if outputA > 0:
                    inputA = expansionList['generic']['inputA']
                    print outputA
                    totAmount += outputA
                    print expansionList
                    print '###'
                    #print expansionList['cc'] + 'dsds'
                    print '------'
                    #print cc
                    #nameP, version = cc.rpartition('_')[0], cc.rpartition('_')[2]
                    #print nameP, 'dksdkskds', version
                    #print cc_id
                    #cc = Condition_configuration.objects.get(version = version, condition_protocol_id = Condition_protocol.objects.get(pk = cc_id))
                    cc = Condition_configuration.objects.get(pk = idcc)

                    print 'a'
                    eE = Events(date_time_event = now, cellline_users_id = request.user, cell_details_id = cd, type_event_id = Type_events.objects.get(type_name = 'expansion'))
                    print 'b'
                    eE.save()
                    print 'c'
                    ed = Expansion_details(events_id = eE, input_area = inputA, reduction_factor = expansionList['generic']['reduction'], output_area =  int(expansionList['outputs'][idcc]))
                    print 'd'
                    ed.save()
                    print 'e'
                    u = User.objects.get(username = request.user.username)
                    print u
                    print '1'
                    newCell = Cells(genID = expansionList['outputs'][idcc+'genid'], expansion_details_id = ed, nickname = cd.cells_id.nickname, nickid = cd.cells_id.nickid) #, cancer_research_group_id = u.cancer_research_group_id,
                    print newCell
                    print '2'
                    newCell.save()
                    print '3'

                    newCD = Cell_details(num_plates = outputA, start_date_time = now, cells_id = newCell, condition_configuration_id = cc)
                    newCD.save()
                    
                    #se la linea era pianificata per l'espansione devo togliere la pianificazione
                    if 'Expansion' in expansionDict['plan']:
                        salva=expansionDict['plan']['Expansion']['now']
                        print 'salva',salva
                        if salva:
                            #devo impostare l'end time per la cell details feature in questione
                            feat=Feature.objects.get(name='Expansion')
                            liscdf=Cell_details_feature.objects.filter(cell_details_id=cd,feature_id=feat,end_date_time__isnull=True)
                            print 'liscdf',liscdf
                            if len(liscdf)!=0:
                                liscdf[0].end_date_time=now
                                liscdf[0].save()
    if totAmount > 0:
        updateCellDetails(cd, int(inputA), now)
    return 0


def processingReset(resetList, cd, now, request):
    print 'CLM view: start expansion.processingReset'
    totAmount = 0
    #cc = resetList['new_cc']
    #cc_id = resetList['new_ccID']
    #for toReset in resetList['toReset']:
    resetList = resetList['toReset']
    if resetList['generic']['applied'] == True and resetList['generic']['toSave'] == True:
        for idcc in resetList['outputs']:
            #{'amount': 0, 'applied':False, 'cc':'', 'toSave':True}
            totAmount += int(resetList['outputs'][idcc])
            #nameP, version = cc.rpartition('_')[0], cc.rpartition('_')[2]
            #print cc_id
            #ccL = Condition_configuration.objects.filter( condition_protocol_id = Condition_configuration.objects.get(pk = cc_id).condition_protocol_id)
            #cc = ccL[len(ccL - 1]
            cc = Condition_configuration.objects.get(pk = idcc)
            cellDet = Cell_details(num_plates = int(resetList['outputs'][idcc]), start_date_time = now, cells_id = cd.cells_id, condition_configuration_id = cc,generation_user=request.user)
            cellDet.save()
    if totAmount > 0:
        updateCellDetails(cd, totAmount, now)
    return 0


def processingArchive(archiveList, cd, now, request):
    print 'CLM view: start expansion.processingArchive'
    amount = 0
    for toArchive in archiveList:
        if toArchive['applied'] == True:
            amount += int(toArchive['amount'])
    if amount > 0:
        eA = Events(date_time_event = now, cellline_users_id = request.user, cell_details_id = cd, type_event_id = Type_events.objects.get(type_name = 'archive'))
        eA.save()
        firstA = False
        print 'archive'
        print toArchive
        archiveEvent = Archive_details(amount = amount, events_id = eA)
        archiveEvent.save()
        updateCellDetails(cd, amount, now) #aggiorna il num_plates della linea e pone la end_date a today se si azzera
    return 0

def processingTrash(trashList, cd, now, request):
    print 'CLM view: start expansion.processingTrash'
    amount = 0
    for toTrash in trashList:
        if toTrash['applied'] == True:
            amount += int(toTrash['amount'])
    if amount > 0:
        eT = Events(date_time_event = now, cellline_users_id = request.user, cell_details_id = cd, type_event_id = Type_events.objects.get(type_name = 'elimination'))
        eT.save()
        firstA = False
        print 'trash'
        print toTrash
        trashEvent = Eliminated_details(amount = amount, events_id = eT)
        trashEvent.save()
        updateCellDetails(cd, amount, now)
    return 0

def processingExperiment(experimentList, cd, now, request, listG):
    print 'CLM view: start expansion.processingExperiment'
    amount = 0
    for toExperiment in experimentList:
        if toExperiment['applied'] == True:
            amount += int(toExperiment['amount'])
    if amount > 0:
        eE = Events(date_time_event = now, cellline_users_id = request.user, cell_details_id = cd, type_event_id = Type_events.objects.get(type_name = 'experiment'))
        eE.save()
        firstA = False
        print 'experiment'
        print toExperiment
        experimentEvent = Experiment_details(amount = amount, events_id = eE)
        experimentEvent.save()
        updateCellDetails(cd, amount, now)
        listTemp = []
        for counter in range(0,amount):
            createGenID(cd, counter, listG, listTemp)
        print listG
        for g in listTemp:
            a = Aliquots(gen_id = g, experiment_details_id = experimentEvent)
            a.save()

    return 0

def createGenID(cd, counter, listG, listTemp):
    print 'CLM view: start expansion.createGenID'
    cellGenID = GenealogyID(cd.cells_id.genID)
    print cellGenID.getTillVT() + 'VT'
    dbCounter = len(Aliquots.objects.filter(gen_id__istartswith = cellGenID.getTillVT() + 'VT'))
    print dbCounter
    print counter
    totCounter = str(counter + dbCounter + 1).zfill(2)
    print totCounter
    newG = cellGenID.getTillVT() + 'VT'  + totCounter + '00'
    print newG
    listG.append(newG)
    listTemp.append(newG)

@transaction.commit_manually
@laslogin_required
@login_required
@permission_decorator('cellLine.can_view_CLM_expansion')
def save_mods_cc(request):
    print 'CLM view: start expansion.save_mods_cc'
    try:
        #print request.POST
        elements = json.loads(request.POST['elementsDict'])
        nameP = request.POST['protocolName']
        #print elements
        #print nameP
        protocol = Condition_protocol.objects.get(protocol_name = nameP)
        #print protocol
        configurations = list(Condition_configuration.objects.filter(condition_protocol_id = protocol))
        toRemove = []
        eList = []
        print "configurations"
        print configurations
        for e in elements:
            print 'e', str(e)
            eList.append(e)
            cfList = Condition_feature.objects.filter(condition_protocol_element_id = Condition_protocol_element.objects.get(name = e))
            for cf in cfList:
                print 'cf', str(cf)
                #if len(configurations) == 0:
                #    break
                for cc in configurations:
                    print '---->', str(cc)
                    if Condition_has_feature.objects.filter(condition_feature_id = cf, condition_configuration_id = cc).count() > 0:
                        chf = Condition_has_feature.objects.get(condition_feature_id = cf, condition_configuration_id = cc)
                        index = getIndex(elements[e], cf.name)
                        print str(chf.value), str(elements[e][index]['value'])
                        if chf.value != elements[e][index]['value']:
                            #remove cc
                            print 'a'
                            #configurations.remove(cc)
                            toRemove.append(cc)
                            #continue
                    else:
                        #remove cc
                        print 'b'
                        #configurations.remove(cc)
                        toRemove.append(cc)
                        #continue
        print 'here 1'
        for tr in list(set(toRemove)):
            configurations.remove(tr)
        print len(configurations)
        print configurations

        eList = list(set(eList))
        toRemove = []
        for c in configurations:
            #print c
            for chf in Condition_has_feature.objects.filter(condition_configuration_id=c):
                if chf.condition_feature_id.condition_protocol_element_id:
                    print c, chf.condition_feature_id.condition_protocol_element_id.name
                    if chf.condition_feature_id.condition_protocol_element_id.name not in eList:
                        print 'inserting ', c
                        toRemove.append(c)
        for tr in list(set(toRemove)):
            configurations.remove(tr)
        print len(configurations)
        print configurations


        if len(configurations) == 1:
            print 'doppione trovato'
            nameConf = nameP + '_' + str(configurations[0].version)
            print nameConf
            typePlate = Condition_has_feature.objects.get(condition_configuration_id = configurations[0].id, condition_feature_id = Condition_feature.objects.get(name = 'type_plate')).value
        else:
            print 'new conf'
            version = Condition_configuration.objects.filter(condition_protocol_id = protocol).aggregate(Max('version'))['version__max'] + 1
            #salvare la nuova configurazione
            cc = Condition_configuration(version = version, condition_protocol_id = protocol)
            cc.save()
            print 'a1'
            for e in elements:
                element = Condition_protocol_element.objects.get(name = e)
                #print len(elements[e])
                for feature in elements[e]:
                    print feature
                    #cf = Condition_feature.objects.get(name=feature['nameF'],unity_measure=feature['unity'],condition_protocol_element_id=element)
                    cf = Condition_feature.objects.get(name=feature['nameF'], condition_protocol_element_id=element)
                    chf = Condition_has_feature(value = feature['value'], condition_feature_id = cf, condition_configuration_id = cc)
                    chf.save()

            #replicare le opzioni type_process, type_plate, type_protocol. Per ora replico, in un secondo momento saranno editabili anche queste
            print 'aaa'
            cc_zero = Condition_configuration.objects.get(version = 0, condition_protocol_id = protocol)
            print '1abc'
            cf = Condition_feature.objects.get(name = 'type_protocol')
            print '2'
            print cf, str(cf.id)
            print cc_zero, str(cc_zero.id)

            chfTemp = Condition_has_feature.objects.get(condition_feature_id=cf, condition_configuration_id = cc_zero)
            print '3'
            chf = Condition_has_feature(value = chfTemp.value, condition_feature_id = cf, condition_configuration_id = cc)
            chf.save()
            cf = Condition_feature.objects.get(name = 'type_plate')
            chfTemp = Condition_has_feature.objects.get(condition_feature_id=cf, condition_configuration_id = cc_zero)
            typePlate = chfTemp.value
            chf = Condition_has_feature(value = chfTemp.value, condition_feature_id = cf, condition_configuration_id = cc)
            chf.save()
            cf = Condition_feature.objects.get(name = 'type_process')
            chfTemp = Condition_has_feature.objects.get(condition_feature_id=cf, condition_configuration_id = cc_zero)
            chf = Condition_has_feature(value = chfTemp.value, condition_feature_id = cf, condition_configuration_id = cc)
            chf.save()
            nameConf = nameP + '_' + str(version)
        transaction.commit()
        print cc.id
        return HttpResponse(str(cc.id) + '|' + nameConf + '|' + typePlate)
    except Exception, e:
        transaction.rollback()
        print e
        return HttpResponse('err')



@laslogin_required
@login_required
@permission_decorator('cellLine.can_view_CLM_expansion')
def edit_nickname(request):
    print 'CLM view: start expansion.edit_nickname'
    try:
        print request.POST['cell_id']
        print request.POST['nick']
        cell_id = request.POST['cell_id']
        cell = Cell_details.objects.get(pk = cell_id).cells_id
        cell.nickname = request.POST['nick']
        cell.save()
        return HttpResponse('ok');
    except Exception, e:
        print 'CLM view expansion.edit_nickname 1)', str(e)
        return HttpResponse('err');
