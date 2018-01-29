from __init__ import *

#######################################
# start redirect
#######################################

@laslogin_required
@login_required
def start_redirect(request):
    return HttpResponseRedirect(reverse('datamanager.views.home'))

#######################################
# home view
#######################################

@laslogin_required
@login_required
def home(request):
    print 'home'
    return render_to_response('home.html', RequestContext(request))


#######################################
#logout view
#######################################

@laslogin_required
@login_required
def logout_view(request):
    auth.logout(request)
    for sesskey in request.session.keys():
        del request.session[sesskey]
    lasloginkUrl = Urls.objects.get(id_webservice=WebService.objects.get(name='lashome').id, available=True)
    return HttpResponseRedirect(lasloginkUrl.url + "laslogin/")
    
#######################################
#error view
#######################################

@laslogin_required
@login_required
def error(request):
    return render_to_response('error.html', RequestContext(request))