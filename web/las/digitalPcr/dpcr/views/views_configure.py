from __init__ import *

@laslogin_required
@login_required
@permission_decorator('dpcr.can_view_DPCR_define_assay')
@transaction.commit_manually
def defineAssay(request):
    print 'Start DPCR view: views_configure.defineAssay'
    if request.method == "GET":
        # GET method
        try:
            if 'assayLabel' in request.GET:
                print "assayLabel", request.GET['assayLabel']
                assay = Assay.objects.get(pk=request.GET['assayLabel'])
                print "assay", assay
                jsonData = {'name': assay.name, 'targets': assay.getAssayMutations(), 'assayTypes': assay.getAssayTypes()}
                print jsonData
                return HttpResponse(json.dumps(jsonData))

            user = auth.get_user(request)
            user_name = User.objects.get(username = user.username)
            print get_WG()
            assays = Assay.objects.all()
            print 'DPCR view: views_configure.defineAssay'

            urlAnnot = Urls.objects.get(id_webservice=WebService.objects.get(name='annotation'))
            
            transaction.commit()

            return render_to_response('defineAssay.html', {'assays':assays, 'urlAnnot':urlAnnot.url, 'expTypes': ExperimentType.objects.all()}, RequestContext(request))

        except Exception, e:
            print 'DPCR view: views_configure.defineAssay 1)', str(e)
            transaction.rollback()
            return HttpResponseBadRequest("Page not available")
        
        finally:
            transaction.rollback()

    else:
        if "action" in request.POST:
            action = request.POST['action']

            if action == 'newAssay':
                assayName = request.POST['name']
                edit = True if request.POST['edit'] == 'true' else False
                expType = json.loads(request.POST['assayType'])
                knownError = False
                try:
                    user = auth.get_user(request)
                    user_name = User.objects.get(username = user.username)

                    refs = json.loads(request.POST['targets'])
                    print refs

                    if edit == False:
                        # not editing current assay -- if a namesake assay exists, raise an error
                        newAssay = Assay(name=assayName)
                        try:
                            newAssay.save()
                        except:
                            knownError = True
                            raise Exception('Assay already exists')
                        for e in expType:
                            Assay_has_ExpType(assay=newAssay,exp_type=ExperimentType.objects.get(pk=e)).save()
                        for r in refs:
                            print r
                            Assay_has_Mutation(mut_description=json.dumps(r), id_assay=newAssay).save()
                    else:
                        # editing current assay -- update mutations
                        try:
                            assay = Assay.objects.get(name=assayName)
                            assay.save()
                        except:
                            knownError = True
                            raise Exception('Assay not found')
                        # delete old types
                        for e in assay.assay_has_exptype_set.all():
                            e.delete()
                        # create updated types
                        for e in expType:
                            Assay_has_ExpType(assay=assay,exp_type=ExperimentType.objects.get(pk=e)).save()
                        # delete old mutations
                        for m in assay.assay_has_mutation_set.all():
                            m.delete()
                        # create updated mutations
                        for r in refs:
                            print r
                            m = Assay_has_Mutation(mut_description=json.dumps(r), id_assay=assay)
                            m.save()
                        
                    jsonData = {'assays':[]}

                    assays = Assay.objects.all().values('pk', 'name')
                    for a in assays:
                        print a
                        jsonData['assays'].append({'label': a['pk'], 'name': a['name']})
                    transaction.commit()
                    return HttpResponse(json.dumps(jsonData))
                
                except Exception, e:
                    transaction.rollback()
                    print 'Error: ',  e
                    errorText = str(e) if knownError else "An error has occurred"
                    return HttpResponseServerError(errorText)
            
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

