from __init__ import *



@laslogin_required
@login_required
@permission_decorator('mining.can_view_AM_randomize_groups')
def randomize(request):
    print 'Randomize groups'
    return render_to_response('randomize.html', RequestContext(request))
