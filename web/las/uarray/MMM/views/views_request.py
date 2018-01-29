from __init__ import *

#######################################
#Request views
#######################################
#view for upload file and get of the initial page of new request
@laslogin_required
@login_required
@permission_decorator('MMM.can_view_MMM_upload_request')
@transaction.commit_manually
def pending_request(request):
    if request.method == "GET":
        # GET method
        try:
            user = auth.get_user(request)
            user_name = User.objects.get(username = user.username)
            plans = Request.objects.filter(pending=True, owner=user_name) 
            print plans
            transaction.commit()
            return render_to_response('pending_request.html', {'plans':plans}, RequestContext(request))
        except:
            transaction.rollback()
            return HttpResponseBadRequest("Page not available")
        finally:
            transaction.rollback()
    else:
        try:
            raw_data = simplejson.loads(request.raw_post_data)
            print '[MMM] - Raw Data: %s' % raw_data['idplan']
            return HttpResponseRedirect(reverse('MMM.views.upload_request', kwargs={'request_id':raw_data['idplan']}) ) 
        except:
            return HttpResponseBadRequest("Page not available")

@laslogin_required
@login_required
@permission_decorator('MMM.can_view_MMM_upload_request')
@transaction.commit_manually
def upload_request(request, request_id):
    resp ={}
    if request.method == "GET":
        # GET method
        try:
            print 'GET upload_request'
            print request_id
            resp['users'] =  User.objects.filter(id__in=WG_User.objects.filter(user__is_active=1,WG__name__in=list(get_WG()),permission__codename=get_functionality()))
            requestPending = Request.objects.get (id=request_id)
            assignUsersList=[]
            for g in get_WG():
                assignUsersDict={}
                assignUsersDict['wg']=WG.objects.get(name=g)
                assignUsersDict['usersList']=list()
                for u in User.objects.filter(~Q(username='admin')&~Q(first_name='')).filter(id__in=WG_User.objects.filter(user__is_active=1,WG__name=g,permission__codename=get_functionality()).values_list("user",flat=True)).order_by('last_name'):
                    assignUsersDict['usersList'].append(u)
                assignUsersList.append(assignUsersDict)

            resp['assignUsersList']=assignUsersList

            if not requestPending.pending:
                raise Exception('Not pending request')
            resp['requested_aliquots'] = Aliquot_has_Request.objects.filter(request_id=requestPending).values('aliquot_id__genId', 'aliquot_id__date','aliquot_id__owner', 'aliquot_id', 'aliquot_id__volume','aliquot_id__concentration').annotate(tech_replicates=Count('id')).order_by('id')
            resp['request_session'] = requestPending
            resp['idplan'] = request_id
            transaction.commit()
            return render_to_response('finalize_request.html', resp, RequestContext(request))
        except Exception, e:
            print e
            transaction.rollback()
            return HttpResponseBadRequest("Page not available! " + e.args[0])
        finally:
            transaction.rollback()


#view for upload file and get of the initial page of new request
@laslogin_required
@login_required
@permission_decorator('MMM.can_view_MMM_upload_request')
@transaction.commit_manually
def upload_request_file(request):
    resp = {}
    print "[MMM] - upload_request_file"
    if request.method == 'POST':
        if request.is_ajax():
            try:
                #prendo i dati con codifica json relativi alla tabella html
                json = simplejson.loads(request.raw_post_data)
                print "[MMM] - JSON: %s" % json
                aliquots = json.__getitem__('aliquots')
                operator_ = json.__getitem__('operator')
                if operator_ != "":
                    operator = User.objects.get(id = operator_)
                else:
                    operator = None
                print operator
                req_descr = json.__getitem__('description')
                req_title = json.__getitem__('title')
                req_owner = json.__getitem__('owner')
                if req_owner == "":
                    req_owner = auth.get_user(request).username
                now = datetime.datetime.now()
                # create new request
                new_request = Request(idOperator = operator, timestamp = now, description = req_descr, title = req_title, owner=req_owner.lower(), pending =False)
                new_request.save()
                print "[MMM] - new request %s" % new_request
                #empty list case
                if not aliquots:
                    transaction.rollback()
                    return HttpResponseBadRequest("ERROR: No aliquots.")
                #for each aliquot in the request
                print "[MMM] - LIST %s" % aliquots
                aliquots = sorted(aliquots.items(), key=lambda x: int(x[1]['counter']))
                print aliquots
                al_req = []
                for item, aliquotInfo in aliquots:
                    #aliquot=""
                    print "[MMM] - ITEM %s" % item
                    # management of aliquot presence in the db
                    if aliquotInfo['present'] == 'Warning':    
                        # external aliquot can be duplicated in the system excpet if they are exhausted. This aliquots are not submitted by the web interface
                        al = Aliquot.objects.get(sample_identifier=aliquotInfo['sample_identifier'].upper(), date=aliquotInfo['date'], owner=aliquotInfo['owner'].lower())
                        al.volume = float(aliquotInfo['volume'])
                        al.concentration = float(aliquotInfo['concentration'])
                        al.save()
                    else:
                        al = Aliquot(sample_identifier=aliquotInfo['sample_identifier'].upper(), date=aliquotInfo['date'], owner=aliquotInfo['owner'].lower(), volume=float(aliquotInfo['volume']), concentration=float(aliquotInfo['concentration']))
                        al.save()
                    # save aliquot infor related to the request
                    alRequest = Aliquot_has_Request(aliquot_id=al, request_id=new_request)
                    # optional fields
                    if aliquotInfo['sample_features'] != "":
                        alRequest.sample_featues = aliquotInfo['sample_features']
                    if aliquotInfo['exp_group'] != "":
                        alRequest.exp_group=aliquotInfo['exp_group']
                    # save the aliquot info of the request
                    alRequest.save()
                    if aliquotInfo['tech_replicates'] != "":
                        for i in range(1,int(aliquotInfo['tech_replicates'])):
                            alRequest.pk = None
                            alRequest.tech_replicates = True
                            alRequest.save()
                    al_req.append(aliquotInfo)
                    print "[MMM] - REQ ALIQUOT SAVED"
                request.session['al_req'] = al_req
                request.session['request'] = new_request           
                transaction.commit()
                return HttpResponseRedirect(reverse('MMM.views.confirm_request'))
            except Exception, e:
                print "[MMM] - Error:"
                print e
                transaction.rollback()
                return HttpResponseBadRequest("ERROR: Error in saving the request")
            finally:
                transaction.rollback()
        try:
            # file upload
            form = UploadFileForm(request.POST, request.FILES)
            if (form.is_valid() == False):
                return HttpResponseBadRequest("Form not valid")
            f = request.FILES['file']
            
            filenamefortitle = str(f).split(".")[0]

            # user initialize
            user = auth.get_user(request)
            owner = user.username

            listAliquots = {}
            requestedAl = []
            lineN = 0
            dataColumns = []
            #read of input file
            for line in f:
                if lineN == 0:
                    if line.strip() != '': #retrieve owner
                        owner = line.strip()
                        print owner
                elif lineN == 1: #retrieve data columns
                    dataColumns = line.strip().split('\t')
                    if set(['sample_identifier', 'date', 'volume', 'concentration']) - set(dataColumns):
                        raise Exception
                    print dataColumns
                else: # for each line (i.e., sample)
                    data = line.strip().split('\t')
                    print data
                    if len(data) == 0:
                        continue
                    item = {'owner':owner}
                    # manage not well formatted files
                    for i in range(len(dataColumns)):
                        if i < len(data):
                            item[dataColumns[i]] = data[i].strip()
                        else:
                            item[dataColumns[i]] = ''
                    print item
                    if item.has_key('sample_identifier'):
                        if item['sample_identifier'] == '': # if no identifier is available
                            continue
                    else:
                        continue
                    if Aliquot.objects.filter(sample_identifier=item['sample_identifier'], date=item['date'], owner=item['owner'], exhausted=True):
                        item['present']='True'
                    elif Aliquot.objects.filter(sample_identifier=item['sample_identifier'], date=item['date'], owner=item['owner']):
                            item['present']='Warning'
                    # false if it is the first presence of this aliquot in the microarray system, otherwise true
                    if item.has_key('present') == False:
                        item['present']='False'
                    requestedAl.append(item['sample_identifier'])
                    print item
                    listAliquots[item['sample_identifier']] = (item)
                lineN += 1
            print 'end file'
            # end of reading file
            print listAliquots
            # define the response after reading a file
            alList = []
            for al in requestedAl:
                alList.append(listAliquots[al])
            resp['requested_aliquots'] = alList
            resp['filenamefortitle'] = filenamefortitle
            resp['request_owner'] = owner
            transaction.commit()
            resp['form'] = form
            manual_form = ManualRequestDefinitionForm()
            resp['manual_form'] = manual_form
            resp['users'] = User.objects.filter(id__in=WG_User.objects.filter(user__is_active=1,WG__name__in=list(get_WG()),permission__codename=get_functionality()))
            print resp
            transaction.commit()
            return render_to_response('request_definition.html', resp, RequestContext(request))
        except:
            transaction.rollback()
            return HttpResponseBadRequest("Error in reading file. Please check the structure or download the template.")
        finally:
            transaction.rollback()
    else:
        # GET method
        try:
            resp['requested_aliquots'] = []
            form = UploadFileForm()
            resp['form'] = form
            manual_form = ManualRequestDefinitionForm()
            resp['manual_form'] = manual_form
            resp['users'] = User.objects.filter(id__in=WG_User.objects.filter(user__is_active=1,WG__name__in=list(get_WG()),permission__codename=get_functionality()))
            assignUsersList=[]
            for g in get_WG():
                assignUsersDict={}
                assignUsersDict['wg']=WG.objects.get(name=g)
                assignUsersDict['usersList']=list()
                for u in User.objects.filter(~Q(username='admin')&~Q(first_name='')).filter(id__in=WG_User.objects.filter(user__is_active=1,WG__name=g,permission__codename=get_functionality()).values_list("user",flat=True)).order_by('last_name'):
                    assignUsersDict['usersList'].append(u)
                assignUsersList.append(assignUsersDict)

            resp['assignUsersList']=assignUsersList
            transaction.commit()
            return render_to_response('request_definition.html', resp, RequestContext(request))
        except:
            transaction.rollback()
            return HttpResponseBadRequest("Page not available")
        finally:
            transaction.rollback()

@laslogin_required
@login_required
@permission_decorator('MMM.can_view_MMM_upload_request')
@transaction.commit_manually
def finalize_request(request):
    if request.method == "POST":
        try:
            raw_data = simplejson.loads(request.raw_post_data)
            print raw_data
            user = auth.get_user(request)
            requestPending = Request.objects.get (id=raw_data['idplan'])
            requestPending.pending = False
            requestPending.title = raw_data['title']
            if raw_data['operator'] != "":
                try:
                    operator = User.objects.get(id = raw_data['operator'])
                    requestPending.idOperator = operator
                except Exception, e:
                    print e
            requestPending.save()
            print requestPending
            request.session['request'] = requestPending
            aliquotBio = {}
            aliquotExp = []
            aliq_biobank = ''
            aliquots = Aliquot_has_Request.objects.filter(request_id=requestPending).values('aliquot_id', 'aliquot_id__genId', 'sample_features', 'aliquot_id__date','aliquot_id__owner', 'aliquot_id__volume','aliquot_id__concentration').annotate(tech_replicates=Count('id')).order_by('id')
            for al in aliquots:
                print al
                position = {'barcode':'-', 'father_container':'-', 'pos':'-'}
                aliq_biobank += al['aliquot_id__genId'] +'&'
                aliquotBio[al['aliquot_id__genId']] = {'idaliquot': al['aliquot_id'], 'genId':al['aliquot_id__genId'], 'sample_features':al['sample_features'], 'owner':al['aliquot_id__owner'], 'volume':al['aliquot_id__volume'], 'concentration':al['aliquot_id__concentration'], 'barcode':position['barcode'], 'father_container':position['father_container'], 'pos':position['pos'], 'tech_replicates':al['tech_replicates']}
                aliquotExp.append(al['aliquot_id__genId'])
            try:
                # update info of the aliquot
                res = retrieveAliquots (aliq_biobank[:-1], user.username) 
                for d in res['data']:
                    values = d.split("&")
                    print values
                    if len(values) <10:
                        continue
                    aliquotBio[values[0]]['volume'] = values[1]
                    aliquotBio[values[0]]['concentration'] = values[2]
                    aliquotBio[values[0]]['date'] = values[3]
                    aliquotBio[values[0]]['barcode'] = values[4]
                    aliquotBio[values[0]]['father_container'] = values[5]
                    aliquotBio[values[0]]['pos'] = values[6]
                    aliquotBio[values[0]]['rack_pos'] = values[7]
                    aliquotBio[values[0]]['rack'] = values[8]
                    aliquotBio[values[0]]['freezer'] = values[9]
            except Exception, e:
                print e
                return HttpResponseBadRequest("Error in saving data")
                transaction.rollback()
            alList = []
            for al in aliquotExp:
                alList.append(aliquotBio[al])
            request.session['al_req'] = alList
            transaction.commit()
            return HttpResponseRedirect(reverse('MMM.views.confirm_request'))
        except Exception, e:
            print e
            transaction.rollback()
            return HttpResponseBadRequest("Error in saving data")
        finally:
            transaction.rollback()     

#view for request information
@laslogin_required
@login_required
@permission_decorator('MMM.can_view_MMM_upload_request')
def confirm_request(request):
    resp = {}
    resp['al_req'] = request.session['al_req']
    resp['request'] = request.session['request']
    print resp
    if request.session.get('al_req'):
        del request.session['al_req']
    if request.session.get('request'):
        del request.session['request']
    return render_to_response('request.html', resp, RequestContext(request))


