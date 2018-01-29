# Create your views here.
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.contrib.auth.decorators import login_required
from LASAuth.decorators import laslogin_required
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse


#######################################
# home view
#######################################

@laslogin_required
@login_required
def index(request):
    print 'home'
    return render_to_response('home/index.html', RequestContext(request))

def error(request):
    return render_to_response('error.html', RequestContext(request))


@login_required
def start_redirect(request):
    return HttpResponseRedirect(reverse(index))
