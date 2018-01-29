from __init__ import *

#######################################
#Request views
#######################################

#view for upload file and get of the initial page of new request
@laslogin_required
@login_required
@permission_decorator('biopsy.can_view_LBM_upload_request')
@transaction.commit_manually
def pending_request(request):
    if request.method == "GET":
        # GET method
        try:
            user = auth.get_user(request)
            user_name = User.objects.get(username = user.username)
            plans = Request.objects.filter(pending=True, timechecked__isnull =True, abortTime__isnull=True) 
            transaction.commit()
            return render_to_response('pending_request.html', {'plans':plans}, RequestContext(request))
        except Exception, e:
            print e
            transaction.rollback()
            return HttpResponseBadRequest("Page not available")
        finally:
            transaction.rollback()
    else:
        try:
            raw_data = simplejson.loads(request.raw_post_data)
            print '[LBM] - Raw Data: %s' % raw_data['idplan']
            return HttpResponseRedirect(reverse('biopsy.views.upload_request', kwargs={'request_id':raw_data['idplan']}) ) 
        except:
            return HttpResponseBadRequest("Page not available")



#view for upload file and get of the initial page of new request
@laslogin_required
@login_required
@permission_decorator('biopsy.can_view_LBM_upload_request')
@transaction.commit_manually
def upload_request(request, request_id):
    resp ={}
    if request.method == "GET":
        # GET method
        try:
            print 'GET upload_request'
            print request_id
            resp['users'] =  User.objects.all()
            requestPending = Request.objects.get (id=request_id)
            if not requestPending.pending:
                raise Exception('Not pending request')
            resp['requested_aliquots'] = Aliquot_has_Request.objects.filter(request_id=requestPending)
            resp['request_session'] = requestPending
            resp['idplan'] = request_id
            transaction.commit()
            return render_to_response('request_definition.html', resp, RequestContext(request))
        except Exception, e:
            print e
            transaction.rollback()
            return HttpResponseBadRequest("Page not available! " + e.args[0])
        finally:
            transaction.rollback()
          


@laslogin_required
@login_required
@permission_decorator('biopsy.can_view_LBM_upload_request')
@transaction.commit_manually
def confirm_request(request):
    if request.method == "POST":
        try:
            raw_data = simplejson.loads(request.raw_post_data)
            print raw_data
            user = auth.get_user(request)
            requestPending = Request.objects.get (id=raw_data['idplan'])
            requestPending.pending = False
            requestPending.title = raw_data['title']
            operator = User.objects.get(username = raw_data['operator'])
            print operator
            requestPending.idOperator = operator
            requestPending.save()
            print requestPending
            request.session['plan'] = requestPending
            aliquotBio = {}
            aliquotExp = []
            aliq_biobank = ''
            aliquots = Aliquot_has_Request.objects.filter(request_id=requestPending)
            for al in aliquots:
                print al
                position = {'barcode':'-', 'father_container':'-', 'pos':'-'}
                aliq_biobank += al.aliquot_id.genId +'&'
                aliquotBio[al.aliquot_id.genId] = {'idaliquot': al.aliquot_id.id, 'genId':al.aliquot_id.genId, 'sample_features':al.sample_features, 'owner':al.aliquot_id.owner, 'volume':al.aliquot_id.volume, 'concentration':al.aliquot_id.concentration, 'barcode':position['barcode'], 'father_container':position['father_container'], 'pos':position['pos'], 'volumetaken': al.volumetaken}
                aliquotExp.append(al.aliquot_id.genId)
            try:
                # update info of the aliquot
                res = retrieveAliquots (aliq_biobank[:-1], user.username) 
                for d in res['data']:
                    values = d.split("&")
                    if len(values) <6:
                        continue
                    print values
                    aliquotBio[values[0]]['volume'] = values[1]
                    aliquotBio[values[0]]['concentration'] = values[2]
                    aliquotBio[values[0]]['date'] = values[3]
                    aliquotBio[values[0]]['barcode'] = values[4]
                    aliquotBio[values[0]]['father_container'] = values[5]
                    aliquotBio[values[0]]['pos'] = values[6]
            except Exception, e:
                print e
                transaction.rollback()
                return HttpResponseBadRequest("Error in saving data")
            request.session['aliquots'] = aliquotBio
            transaction.commit()
            return HttpResponseRedirect(reverse('biopsy.views.create_request'))
        except Exception, e:
            print e
            transaction.rollback()
            return HttpResponseBadRequest("Error in saving data")
        finally:
            transaction.rollback()        


#view for upload file and get of the initial page of new request
@laslogin_required
@login_required
@permission_decorator('biopsy.can_view_LBM_upload_request')
@transaction.commit_manually
def create_request(request):
    resp = {}
    if request.method == "GET":
        try:
            if request.session.has_key('aliquots'):
                resp['aliquots'] = request.session['aliquots']
            if request.session.has_key('plan'):
                resp['plan'] = request.session['plan']
            transaction.commit()
            return render_to_response('request.html', resp, RequestContext(request))
        except:
            transaction.rollback()
            return HttpResponseBadRequest("Page not available")
        finally:
            transaction.rollback()
