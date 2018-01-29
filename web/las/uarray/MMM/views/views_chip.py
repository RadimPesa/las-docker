from __init__ import *

#######################################
# View for the insertion of chip and chip type
#######################################

@laslogin_required
@login_required
@permission_decorator('MMM.can_view_MMM_insert_chip_type')
@transaction.commit_manually
def new_chip_type(request):
    if request.method == 'GET':
        resp = {}
        if request.session.get('message'):
            resp['message'] = request.session['message']
            del request.session['message']

        return render_to_response('new_chip_type.html', resp, context_instance=RequestContext(request))
    else:
        print '[MMM] - Raw Data: "%s"' % request.raw_post_data
        try:
            jsonData = simplejson.loads(request.raw_post_data)
            if jsonData['newlayout'] != -1:
                print 'no new layout'
                geometry = Geometry.objects.get(id=jsonData['newlayout'])
                print geometry
            else:
                rules = str(jsonData['layout'])
                npos = len(jsonData['layout'].keys())
                geometry = Geometry(rules=rules, npos=npos)
                geometry.save()

            cType = ChipType(title=jsonData['title'], manufacter=jsonData['manufacturer'], organism=jsonData['organism'], probesNumber=jsonData['probes'], GeoPlatformId=jsonData['geoplatformid'], manifestFile=jsonData['manifest'], notes=jsonData['notes'], layout=geometry)
            cType.save()
            request.session['message'] = 'New chip type available'
            transaction.commit()
            return HttpResponseRedirect(reverse('MMM.views.new_chip_type'))
        except Exception, e:
            print e
            transaction.rollback()
        finally:
            transaction.rollback()
        


@laslogin_required
@login_required
@permission_decorator('MMM.can_view_MMM_insert_chip')
@transaction.commit_manually
def new_chip(request):
    resp = {}
    if request.method == 'POST':
        print '[MMM] - Raw Data: "%s"' % request.raw_post_data
        try:
            jsonData = simplejson.loads(request.raw_post_data)
            for barcode, chipInfo in jsonData.items():
                chipType = ChipType.objects.get(id=chipInfo['idType'])
                chip = Chip (barcode=barcode, idChipType=chipType, expirationDate=chipInfo['exp_date'], dmapFile=chipInfo['dmap'], owner=chipInfo['owner'], batchNumber=chipInfo['lot'], notes=chipInfo['notes'])
                chip.save()
            print 'save in session'
            request.session['chips_insert'] = jsonData
            print request.session['chips_insert']
            transaction.commit()
            return HttpResponseRedirect(reverse('MMM.views.chips_view'))
        except Exception, e:
            print e
            transaction.rollback()
            return HttpResponseBadRequest("Chip request failed due to malformed data")
    else:
        try:
            chip_choices = ChipType.objects.all()
            resp['chip_choices'] = chip_choices
            transaction.commit()
            print resp
            return render_to_response('new_chip.html',resp, context_instance=RequestContext(request))
        except:
            transaction.rollback()
            return HttpResponseBadRequest("Page not available")
        finally:
            transaction.rollback()


#view for request information
@laslogin_required
@login_required
@permission_decorator('MMM.can_view_MMM_insert_chip')
def chips_view(request):
    resp = {}
    resp['chips'] = request.session['chips_insert']
    print resp
    if request.session.get('chips_insert'):
        del request.session['chips_insert']
    return render_to_response('chips_insert.html', resp, RequestContext(request))
