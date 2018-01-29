from __init__ import *


@laslogin_required
@login_required      
def mdam(request):
    return HttpResponseRedirect(reverse("_caQuery.views.home"))


@laslogin_required
@login_required    
def logout(request):
    lasloginUrl = Urls.objects.get(idWebService=WebService.objects.get(name='LASAuthServer').id)
    return HttpResponseRedirect(lasloginUrl.url + "/index/")


@laslogin_required
@login_required
def home(request):
    return render_to_response('home.html', RequestContext(request))


def error(request):
    return render_to_response('error.html', RequestContext(request))