from __init__ import *


@laslogin_required
@login_required
@permission_decorator('rtpcr.can_view_RTM_run_experiment')
@transaction.commit_manually
def defineAssay(request):
    print 'Start RTM view: views_configure.defineAssay'
    if request.method == "GET":
        # GET method
        try:
            if 'assayLabel' in request.GET:
                assay = Assay.objects.get(pk=request.GET['assayLabel'])
                jsonData = {'name':assay.name, 'targets':[]}
                jsonData['targets'] = retrieveTargets(list(Assay_has_Probe.objects.filter(id_assay=assay).values_list('probe', flat=True)))
                print jsonData
                return HttpResponse(json.dumps(jsonData))

            user = auth.get_user(request)
            user_name = User.objects.get(username = user.username)
            print get_WG()
            assays = Assay.objects.filter(WG__name__in=get_WG())
            print 'RTM view: views_configure.defineAssay'

            urlAnnot = Urls.objects.get(id_webservice=WebService.objects.get(name='annotation'))
            
            transaction.commit()

            return render_to_response('defineAssay.html', {'assays':assays, 'urlAnnot':urlAnnot.url}, RequestContext(request))
        except Exception, e:
            print 'RTM view: views_configure.defineAssay 1)', str(e)
            transaction.rollback()
            return HttpResponseBadRequest("Page not available")
        finally:
            transaction.rollback()
    else:
        if "action" in request.POST:
            action = request.POST['action']
            if action == 'newAssay':
                try:
                    user = auth.get_user(request)
                    user_name = User.objects.get(username = user.username)
                    assays = Assay.objects.filter(WG__name__in=get_WG())

                    refs = json.loads(request.POST['targets'])
                    print refs
                    payload = {'params': {'uuid_list': refs}, 'exp_type':'Real-Time PCR'}

                    flagCreated = True
                    for wg in get_WG():
                        try:
                            newAssay = Assay(WG=WG.objects.get(name= wg), name= request.POST['name'])
                            newAssay.save()
                            for r in refs:
                                print r
                                assProbe = Assay_has_Probe(probe=r, id_assay=newAssay)
                                assProbe.save()
                        except Exception, e:
                            print e
                            flagCreated = False
                            continue

                    if not flagCreated:
                        transaction.rollback()
                        raise Exception('Assay already exists')
                    jsonData = {'assays':[]}

                    assays = Assay.objects.filter(WG__name__in=get_WG()).values('pk', 'name', 'WG__name' ).distinct()
                    for a in assays:
                        print a
                        jsonData['assays'].append({'label':a['pk'], 'name':a['name'], 'wg': a['WG__name']})
                    transaction.commit()
                    return HttpResponse(json.dumps(jsonData))
                except Exception, e:
                    transaction.rollback()
                    print 'Error: ',  e
                    return HttpResponseServerError(e)
            if action == 'delAssay':
                try:
                    user = auth.get_user(request)
                    user_name = User.objects.get(username = user.username)
                    assay = Assay.objects.get(pk=request.POST['assayName'])
                    assay.delete()

                    transaction.commit()
                    return HttpResponse("OK")
                except Exception, e:
                    transaction.rollback()
                    print 'Error: ',  e
                    return HttpResponseServerError(e)

