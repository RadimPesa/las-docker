from __init__ import *

#######################################
# Scan protocol
#######################################

@laslogin_required
@login_required
@permission_decorator('MMM.can_view_MMM_scan_protocol')
@transaction.commit_manually
def scan_protocols(request):
    resp = {}
    if request.method == 'POST':
        try:
            raw_data = simplejson.loads(request.raw_post_data)
            print "[MMM] - JSON: %s" % raw_data
            protocol = raw_data['protocol']
            parameters = raw_data['params']
            software = Software.objects.get(id = protocol['idSoftware'])
            instrument = Instrument.objects.get(id=protocol['idInstrument'])
            qc = False
            if protocol['qc'] == "true":
                qc = True
            scanProt = ScanProtocol (name = protocol['name'], idSoftware = software, tobevalidated=qc, idInstrument=instrument)
            scanProt.save()
            request.session['protocol'] = scanProt
            request.session['instrument'] = instrument
            request.session['params'] = []
            for pId, value in parameters.items():
                param = Parameter.objects.get(id = pId)
                new_value = Protocol_has_Parameter_value( idProtocol = scanProt, idParameter = param, value = value)
                new_value.save()
                request.session['params'].append(new_value)
            
            transaction.commit()
            return HttpResponseRedirect(reverse('MMM.views.scanprot_info'))
        except:
            transaction.rollback()
            return HttpResponseBadRequest('Error in saving data')
        finally:
            transaction.rollback()
    else:
        try:
            resp['instruments'] = Instrument.objects.filter(scan=True)
            resp['softwares'] = Software.objects.all()
            print resp
            transaction.commit()
            return render_to_response('scan_protocols.html', resp, RequestContext(request))
        except:
            transaction.rollback()
            return HttpResponseBadRequest('Page not available')
        finally:
            transaction.rollback()


#view for request information
@laslogin_required
@login_required
@permission_decorator('MMM.can_view_MMM_scan_protocol')
def scanprot_info(request):
    resp = {}
    resp['protocol'] = request.session['protocol']
    resp['params'] = request.session['params']
    resp['instrument'] = request.session['instrument']
    print resp
    if request.session.get('protocol'):
        del request.session['protocol']
    if request.session.get('params'):
        del request.session['params']
    if request.session.get('instrument'):
        del request.session['instrument']
    return render_to_response('scanprot_info.html', resp, RequestContext(request))

#######################################
# Scan
#######################################

@laslogin_required
@login_required
@permission_decorator('MMM.can_view_MMM_scan')
@transaction.commit_manually
def pre_scan(request):
    resp = {}
    print 'pre_scan'
    if request.method == 'GET':
        try:
            prot_choices = [(p.pk, p.name) for p in ScanProtocol.objects.exclude(idInstrument__in=[s.idProtocol.idInstrument for s in ScanEvent.objects.filter(endScanTime__isnull = True)])]
            scan_form = ScanProtocolForm()
            scan_form.fields['Protocol'] = forms.CharField(widget=forms.Select(choices = prot_choices))
            resp['notes'] = NotesScanForm()
            resp['scan_form'] = scan_form              
            print "[MMM] - rendering...pre scan"
            transaction.commit()
            return render_to_response('pre_scan.html', resp, RequestContext(request))  
        except Exception, e:
            print e
            transaction.rollback()
            return HttpResponseBadRequest('Page not available')
        finally:
            transaction.rollback()
    else:
        try:
            raw_data = simplejson.loads(request.raw_post_data)
            print raw_data
            protocol = ScanProtocol.objects.get(id=raw_data['protocol'])
            user = auth.get_user(request)
            operator = User.objects.get(username = user.username)
            scanEvent = ScanEvent(startScanTime = datetime.datetime.now(), idProtocol = protocol, idOperator = operator, notes = raw_data['notes'], validated=False)
            scanEvent.save()
            print scanEvent
            request.session['scan_event'] = scanEvent
            request.session['scanAssign'] = []
            for barcodeChip, pos in raw_data['chips_to_scan'].items():
                chip = Chip.objects.get(barcode=barcodeChip)
                geometry = ast.literal_eval(chip.idChipType.layout.rules)
                chip_scanned = Chip_has_Scan(idChip = chip, idScanEvent = scanEvent, posonscanner = pos)
                chip_scanned.save()
                assign = Assignment.objects.filter(idChip = chip).order_by('position')
                for a in assign:
                    print a
                    scanAssign = Assignment_has_Scan (idAssignment = a, idScanEvent = scanEvent)
                    scanAssign.save()
                    request.session['scanAssign'].append({'posonchip':geometry[a.position], 'chipbarcode': barcodeChip, 'chippos':pos, 'genealogy': a.idAliquot_has_Request.aliquot_id.genId, 'sample_identifier': a.idAliquot_has_Request.aliquot_id.sample_identifier})
            transaction.commit()
            return HttpResponseRedirect(reverse('MMM.views.scan'))
        except Exception, e:
            print e
            transaction.rollback()
            return HttpResponseBadRequest('Error in saving data')
        finally:
            transaction.rollback()



@laslogin_required
@login_required
@permission_decorator('MMM.can_view_MMM_scan')
@transaction.commit_manually
def scan(request):
    try:
        scanEvent =  request.session['scan_event']
        scanAssigns = request.session['scanAssign']
        if request.session.get('scan_event'):
            del request.session['scan_event']
        if request.session.get('scanAssign'):
            del request.session['scanAssign']
        transaction.commit()
        return render_to_response('end_scan.html', {'scanevent':scanEvent, 'assign':scanAssigns}, RequestContext(request))
    except:
        transaction.rollback()
        return HttpResponseBadRequest('Error in saving data')
    finally:
        transaction.rollback()





# select virtual plan
@laslogin_required
@login_required
@permission_decorator('MMM.can_view_MMM_scanqc')
@transaction.commit_manually
def select_scan(request):
    if request.method =='GET':
        try:
            user = auth.get_user(request)
            operator = User.objects.get(username = user.username)
            plans = ScanEvent.objects.filter(idOperator=operator, endScanTime__isnull=True).order_by('startScanTime')
            plans_selected=[]
            for p in plans:
                plans_selected.append({'id': p.id, 'startScanTime': p.startScanTime, 'protocol': p.idProtocol.name, 'notes':p.notes, 'tobevalidated':p.idProtocol.tobevalidated})
            transaction.commit()
            return render_to_response('select_scan.html', {'plans':plans_selected}, RequestContext(request))
        except:
            transaction.rollback()
            return HttpResponseBadRequest('Page not available')
        finally:
            transaction.rollback()
    else:
        try:
            raw_data = simplejson.loads(request.raw_post_data)
            print '[MMM] - Raw Data: "%s"' % raw_data
            if raw_data.has_key('terminate'):
                for plan in raw_data['plans']:
                    scanEvent = ScanEvent.objects.get(id=plan)
                    scanEvent.endScanTime = datetime.datetime.now()
                    scanEvent.save()
                transaction.commit()
                return HttpResponseRedirect(reverse('MMM.views.select_scan'))
            idplan = ''
            if raw_data.has_key('idplan'):
                idplan = raw_data['idplan']
            request.session['idplan'] = idplan
            transaction.commit()
            return HttpResponseRedirect(reverse('MMM.views.scan_quality'))
        except Exception, e:
            print e
            transaction.rollback()
            return HttpResponseBadRequest('Page not available')
        finally:
            transaction.rollback()

@laslogin_required
@login_required
@permission_decorator('MMM.can_view_MMM_scanqc')
@transaction.commit_manually
def scan_quality(request):
    if request.method == "GET":
        try:
            scanEvent = ScanEvent.objects.get(id=request.session['idplan'])
            chipScanned = Chip_has_Scan.objects.filter(idScanEvent=scanEvent).order_by('posonscanner')
            resp = {'instrument':[]}
            for chip in chipScanned:
                if chip.posonscanner > (len(resp['instrument']) +1):
                    for i in xrange(len(resp['instrument']), chip.posonscanner - len(resp['instrument']) -1):
                        resp['instrument'].append({'pos': i+1, 'barcode':''})
                resp['instrument'].append({'pos':int(chip.posonscanner), 'barcode':chip.idChip.barcode})
                    
            for i in xrange(len(resp['instrument']), scanEvent.idProtocol.idInstrument.positions):
                resp['instrument'].append({'pos': i+1,'barcode':''})
            return render_to_response('scanqc.html', resp, RequestContext(request))
        except:
            transaction.rollback()
            return HttpResponseBadRequest('Page not available')
        finally:
            transaction.rollback()
    else:
        try:
            raw_data = simplejson.loads(request.raw_post_data)
            print raw_data, request.session['idplan']
            scanEvent = ScanEvent.objects.get(id=request.session['idplan'])
            chipScanned = Chip_has_Scan.objects.filter(idScanEvent=scanEvent)
            request.session['samples'] = []
            for chip in chipScanned:
                geometry = ast.literal_eval(chip.idChip.idChipType.layout.rules)
                assign = Assignment_has_Scan.objects.filter(idScanEvent=scanEvent, idAssignment__in = (Assignment.objects.filter(idChip=chip.idChip))).order_by('idAssignment__position')
                for sample in assign:
                    print sample.idAssignment
                    if raw_data.has_key(chip.idChip.barcode):
                        if raw_data[chip.idChip.barcode]['pos'][sample.idAssignment.position-1]['qc'] == "true":
                            sample.qc = True
                        else:
                            sample.qc = False
                    else:
                        sample.qc = True
                    sample.save()
                    request.session['samples'].append({'chipbarcode':chip.idChip.barcode, 'posonchip':geometry[sample.idAssignment.position], 'genealogy':sample.idAssignment.idAliquot_has_Request.aliquot_id.genId,'sample_identifier':sample.idAssignment.idAliquot_has_Request.aliquot_id.sample_identifier, 'qc': sample.qc })
            scanEvent.validated = True
            scanEvent.endScanTime = datetime.datetime.now()
            scanEvent.save()
            request.session['event'] = scanEvent
            transaction.commit()
            return HttpResponseRedirect(reverse('MMM.views.view_scanqc'))
        except Exception, e:
            print e
            transaction.rollback()
            return HttpResponseBadRequest('Error in saving data')
        finally:
            transaction.rollback()




@laslogin_required
@login_required
@permission_decorator('MMM.can_view_MMM_scanqc')
@transaction.commit_manually
def view_scanqc(request):
    try:
        samples = request.session['samples']
        scanEvent = request.session['event']
        if request.session.get('event'):
            del request.session['event']
        if request.session.get('samples'):
            del request.session['samples']
        transaction.commit()
        return render_to_response('end_scanqc.html', {'scanevent':scanEvent, 'samples':samples}, RequestContext(request))
    except:
        transaction.rollback()
        return HttpResponseBadRequest('Error in saving data')
    finally:
        transaction.rollback()

