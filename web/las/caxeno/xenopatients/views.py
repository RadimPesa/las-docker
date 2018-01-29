from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import auth
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import loader, Context, RequestContext
from LASAuth.decorators import laslogin_required
from django.conf import settings
from global_request_middleware import *
from xenopatients.models import *
from django.conf import settings

def error(request):
    print 'XMM VIEW: start views.error'
    return render_to_response('error.html', RequestContext(request))

#semplice view per portare l'utente alla home page
@laslogin_required
@login_required
def index(request):
    print 'XMM VIEW: start views.index'
    return render_to_response('index.html', {'name':request.user.username}, RequestContext(request))

#view usata per redirigire l'utente se digita non digita anche "/xenopatients" nell'url
@laslogin_required
@login_required
def start_redirect(request):
    print 'XMM VIEW: start views.start_redirect'
    return HttpResponseRedirect(reverse("xenopatients.views.index"))

def check_bio_mice(request):
    try:
	print get_WG()
        BioMice.objects.get(id_genealogy='CRC0202LMX0B05025SCR000000')
        #Mice.objects.get(barcode='000728C910')
        #enable_graph()
        return HttpResponse("ok")
    except Exception,e:
	print e
        return HttpResponse("not ok")


@laslogin_required
@login_required
def lasHome(request):
    #lasloginUrl = Urls.objects.get(id_webservice=WebService.objects.get(name='las').id, available=True)
    lasloginUrl=settings.LAS_URL
    return HttpResponseRedirect(lasloginUrl + "/index/")
