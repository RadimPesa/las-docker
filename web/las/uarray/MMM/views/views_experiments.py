from __init__ import *



# select virtual plan
@laslogin_required
@login_required
@permission_decorator('MMM.can_view_MMM_explore_scan')
@transaction.commit_manually
def explore_scan(request):
    if request.method =='GET':
        return render_to_response('explore_scan.html', RequestContext(request))


@laslogin_required
@login_required
@permission_decorator('MMM.can_view_MMM_experiment')
@transaction.commit_manually
def compose_data(request):
    resp ={}
    if request.method == "GET":
        # GET method
        try:
            user = auth.get_user(request)
            user_name = User.objects.get(username = user.username)
            form = UploadFileForm()
            resp['form'] = form
            print resp
            transaction.commit()
            return render_to_response('compose_data.html', resp, RequestContext(request))
        except Exception, e:
            print e
            transaction.rollback()
            return HttpResponseBadRequest("Page not available")
        finally:
            transaction.rollback()
    else:
        print 'POST'
        try:
            print request.POST
            raw_data = simplejson.loads(request.raw_post_data)
            request.session['samples'] = raw_data['samples']
            url = reverse('MMM.views.uarrayExperiment', kwargs={'experimentid': 1})
            return HttpResponseRedirect(url)
        except Exception, e:
            print e
            transaction.rollback()
            return HttpResponseBadRequest("Page not available")
        finally: 
            transaction.rollback()

@login_required
@user_passes_test(lambda u: u.has_perm('MMM.can_view_MMM_experiment'),login_url=reverse_lazy('MMM.views.error'))
@transaction.commit_manually
def uarrayExperiment (request, experimentid):
    print 'uarrayExperiment'
    resp = {}
    resp['samples'] = request.session['samples']
    return render_to_response('experiment.html', resp, RequestContext(request))
