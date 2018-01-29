from cellLine.forms import *
from django.http import HttpResponse, Http404
from django.template import Context
from django.template import RequestContext
from django.template.loader import get_template
from django.shortcuts import render_to_response, get_object_or_404, get_list_or_404
from django.core.urlresolvers import reverse
from cellLine.models import *
from cellLine.genealogyID import *
import datetime
from django.utils import simplejson
from django.contrib.auth.models import User
from LASAuth.decorators import laslogin_required
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.contrib.auth import logout
import webbrowser, os.path


laslogin_required
@login_required
def start_redirect(request):
    return HttpResponseRedirect(reverse('cellLine.views.home'))

#######################################
# home view
#######################################

@laslogin_required
@login_required
def home(request):
    print 'home'
    return render_to_response('main_page.html', RequestContext(request))


#######################################
#logout view
#######################################

@laslogin_required
@login_required
def logout_view(request):
    lasloginUrl = Urls_handler.objects.get(name='lashome')
    return HttpResponseRedirect(lasloginUrl.url + "index/")
    
#######################################
#error view
#######################################

@laslogin_required
@login_required
def error(request):
    return render_to_response('error.html', RequestContext(request))



@laslogin_required
@login_required
def open_file(request):
	print 'CLM view: start views.open_file'
	prot_name = request.POST.get('prot_name').replace(' ','_')
	file_name = ""
	for e in ConditionProtocolElement.objects.all():
		if e.name == str(prot_name):
			file_name = e.file_name
	path = os.path.dirname(__file__) + "/" + file_name
	if file_name != "":
		webbrowser.open(os.path.abspath(file_name))
	return HttpResponse("")

