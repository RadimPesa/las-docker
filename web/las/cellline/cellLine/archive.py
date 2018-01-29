from __init__ import *

@laslogin_required 
@login_required
@permission_decorator('cellLine.can_view_CLM_archive')
def archive_page(request):
    print 'CLM view: start archive.archive_page'
    try:
        if request.method == 'POST':
            print request.POST
            if 'action' in request.POST:
                with transaction.commit_manually():
                    try:
                        idEvent = request.POST['idEvent']
                        nTrash = request.POST['nTrash']                        
                        now = datetime.datetime.now()
                        cd = Cell_details.objects.get(id = Events.objects.get(id=idEvent).cell_details_id.pk)
                        archiveDetail = Archive_details.objects.get(events_id = idEvent)

                        if nTrash > 0:
                            print idEvent, cd
                            eT = Events(date_time_event = now, cellline_users_id = request.user, cell_details_id = cd, type_event_id = Type_events.objects.get(type_name = 'elimination'))
                            eT.save()
                            print eT.id
                            trashEvent = Eliminated_details(amount = nTrash, events_id = eT)
                            trashEvent.save()
                            print trashEvent.id
                            archiveDetail.amount = archiveDetail.amount - int(nTrash)
                            if archiveDetail.amount == 0:
                                archiveDetail.application_date = now
                            archiveDetail.save()                            
                        
                        jsonData = {'nTrash': nTrash}
                        transaction.commit()
                        return HttpResponse(json.dumps(jsonData))
                    except Exception, e:
                        print e
                        transaction.rollback()
                        HttpResponseServerError(str(e))
            else:
                print 'AAA'
                request.session['archive'] = request.POST
                print 'BBB'
                return HttpResponseRedirect(reverse("cellLine.archive.save"))
        else:
            listTypeAliquot = []
            biobankHost = Urls_handler.objects.get(name = 'biobank').url
            url = biobankHost + '/api/info/aliquottype'
            print 'url',url
            req = urllib2.Request(url, headers={"workingGroups" : get_WG_string()})
            u = urllib2.urlopen(req)
            #u = urllib2.urlopen(url)
            types = ast.literal_eval(u.read())
            for t in types:
                listTypeAliquot.append(t)

            archive_genID_list = []
            
            lisarchive=Archive_details.objects.filter(application_date__isnull = True)
            for ad in lisarchive:
                #devo fare la filter su cells per non far vedere a tutti tutte le linee
                lcell=Cells.objects.filter(id=ad.events_id.cell_details_id.cells_id.id)
                if len(lcell)!=0:
                    cell=lcell[0]
                    cellDet = ad.events_id.cell_details_id
                    archive_genID_list.append((ad.events_id.id, cell.nickname, cell.genID, ad.amount, cellDet.start_date_time, ad.events_id.date_time_event, cellDet.condition_configuration_id))
            '''for ad in Archive_details.objects.filter(application_date__isnull = True):#.annotate(totalAmount=Sum('amount')):
                cell = ad.events_id.cell_details_id.cells_id
                cellDet = ad.events_id.cell_details_id
                archive_genID_list.append((ad.events_id.id, cell.nickname, cell.genID, ad.amount, cellDet.start_date_time, ad.events_id.date_time_event, cellDet.condition_configuration_id))'''
            return render_to_response( 'archive/archive.html',{
                'user': request.user, 'data': datetime.datetime.now(), 'archive_genID_list': archive_genID_list, 'plate':Plate(), 'listTypeAliquot':listTypeAliquot }
                ,RequestContext(request))
    except Exception, e:
        print 'CLM view: archive.archive_page 1)', str(e)
        return render_to_response('error_page.html', {'name':'Archive', 'err_message': "Something went wrong!" }) 


@transaction.commit_manually
@laslogin_required 
@login_required
@permission_decorator('cellLine.can_view_CLM_archive')
def save(request):
    print 'CLM view: start archive.save'
    try:
        aliquots = json.loads(request.session['archive']['aliquots'])
        date=request.session['archive']['date']
        print 'date',date        
        
        #today = datetime.datetime.today()
        try:
            url = Urls_handler.objects.get(name = 'biobank').url + "/explants/"
            print 'url',url
            transaction.commit()
        except Exception, e:
            print 'CLM VIEW explant.explantSubmit: 0) ' +  str(e)
            transaction.rollback()
        try:
            print url
            values = {'explants' : request.session['archive']['aliquots'], 'date': date, 'operator': request.user.username, 'source':'cellline'}
            data = urllib.urlencode(values)
            req = urllib2.Request(url, data=data, headers={"workingGroups" : get_WG_string()})
            u = urllib2.urlopen(req)
            #u = urllib2.urlopen(url, data)
            res =  u.read() #mi dice se il salvataggio su biobank/storage e' andato a buon fine o meno
            print 'CLM VIEW archive.save: biobank response ' +  str(res)
        except Exception, e: #in caso di timeout di catissue o nel caso non sia online
            print 'CLM VIEW archive.save: 1) ' +  str(e)
            request.session['message'] = "Something gone wrong while linking with the BioBank."
            return HttpResponseRedirect(reverse("cellLine.views.home"))    
        #res contiene il responso alla precedente richiesta. Indica se la biobanca ha salvato correttamente i dati o meno
        if res == 'err':
            transaction.rollback()
            request.session['message'] = "Something gone wrong while linking with the BioBank."
            return HttpResponseRedirect(reverse("cellLine.views.home"))
        #se ha salvato, salvo anche io
        if res == 'ok':
            reportList = []
            oggi=str(datetime.datetime.utcnow().date())
            print 'oggi',oggi
            #se la data e' oggi metto il timestamp corretto, altrimenti lascio solo l'indicazione della data
            if date==oggi:
                print 'uguali'
                date=timezone.localtime(timezone.now())            
            print 'date dopo',date
            for typeA in aliquots:
                #print '1'
                print typeA
                for genID in aliquots[typeA]:
                    #print '2'
                    for barcodeP in aliquots[typeA][genID]:
                        #print '3'
                        for tube in aliquots[typeA][genID][barcodeP]:
                            #print '4'
                            newG = tube['genID']
                            pos = tube['pos']
                            count = tube['conta']
                            volume = tube['volume']
                            idEvent = tube['idEvent']
                            print newG
                            print idEvent
                            #salvare data esecuzione archivio in archive details
                            e = Events.objects.get(id = idEvent)
                            ad = Archive_details.objects.get(events_id = e)
                            ad.application_date = date
                            ad.save()
                            #salvare aliquote create in aliquots
                            aliquot = Aliquots(gen_id = newG, archive_details_id = ad)
                            aliquot.save()

                            cellDet = e.cell_details_id
                            cell = cellDet.cells_id
                            reportList.append([cell.nickname, cell.genID, cellDet.num_plates, cellDet.start_date_time, cellDet.condition_configuration_id, newG, barcodeP, pos, volume,count])

        print 'reportList',reportList
        rtr =  render_to_response('archive/report.html', {'reportList':reportList},RequestContext(request))
        transaction.commit()
        return rtr
    except Exception, e:
        print 'CLM view: archive.save 2)', str(e)
        transaction.rollback()
        url = Urls_handler.objects.get(name = 'biobank').url + "/explants/end/"
        values = {'aliquots' : request.session['archive']['aliquots'], 'user': request.user.username, 'response':'err'}
        res = ""
        data = urllib.urlencode(values)
        req = urllib2.Request(url, data=data, headers={"workingGroups" : get_WG_string()})
        u = urllib2.urlopen(req)
        #u = urllib2.urlopen(url, data)
        request.session['message'] = "Something gone wrong."
        return HttpResponseRedirect(reverse("cellLine.views.home"))
    
    