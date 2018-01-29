from __init__ import *



@laslogin_required
@login_required
@user_passes_test(lambda u: u.has_perm('mining.can_view_AM_write_formulas'),login_url=reverse_lazy('mining.views.error'))
def writeformulas(request):
    print 'write formulas'

    return render_to_response('writeformulas.html', RequestContext(request))
