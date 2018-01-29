from __init__ import *

#view for upload file and get of the initial page of new request
@laslogin_required
@login_required
@permission_decorator('rtpcr.can_view_RTM_review_analysis')
def select_analysis_for_review(request):
    if request.method == "GET":
        # GET method
        try:
            user = auth.get_user(request)
            #user_name = User.objects.get(username = user.username)
            analyses = Analysis.objects.filter(idOperator=user)#_name)
            print 'RTM view: views_review.select_analysis_for_review'
            print analyses
            return render_to_response('select_analysis_for_review.html', {'analyses': analyses}, RequestContext(request))
        except Exception, e:
            print e
            return HttpResponseBadRequest("Page not available")
    else:
            return HttpResponseBadRequest("Invalid method")

@laslogin_required
@login_required
@permission_decorator('rtpcr.can_view_RTM_review_analysis')
def review_analysis(request):
    if request.method == "GET":
        # GET method
        try:
            id_analysis = request.GET['id']
            print 'RTM view: views_review.review_analysis'
            
            a = Analysis.objects.get(pk=id_analysis)
            ad = AnalysisDescription.objects.get(analysis_id=id_analysis)
            f = Formula.objects.get(pk=ad.formula_id)
            
            # retrieve targets
            targets = getTargets (ad.probe_var_mapping.keys())
            targets_dict = {}
            for x in targets:
                x['var'] = ad.probe_var_mapping[x['uuid']]
                targets_dict[x['uuid']] = x

            print "targets_dict", targets_dict
            sorted_targets = sorted(targets_dict.keys(),key=lambda uuid: targets_dict[uuid]['name'])
            
            # retrieve inputs
            inputs = {}
            for s in a.id_experiment.sample_set.all():
                if not inputs.has_key(s.idAliquot_has_Request.aliquot_id.genId):
                    inputs[s.idAliquot_has_Request.aliquot_id.genId] = {k:[] for k in sorted_targets}
                inputs[s.idAliquot_has_Request.aliquot_id.genId][s.probe].append(s)

            # retrieve outputs
            outputs = AnalysisOutput.objects.filter(analysis_id=id_analysis)

            remap_aggregation_labels = {'all': 'Across all probes', 'probe': 'By probe'}
            
            scope = {"formula": f, "analysis": a, "targets": targets_dict, "aggregation_criteria": ad.aggregation_criteria, "inputs": inputs, "sorted_targets": sorted_targets, "outputs": outputs, "remap_aggregation_labels": remap_aggregation_labels}
            return render_to_response('review_analysis.html', scope, RequestContext(request))
        
        except Exception, e:
            print str(e)
            # TODO: notify gently!!!
            return HttpResponseBadRequest("Page not available")
    
    else:
            return HttpResponseBadRequest("Invalid method")
