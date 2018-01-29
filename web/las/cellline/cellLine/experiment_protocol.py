from cellLine.forms import *
from cellLine.models import *
from cellLine.genealogyID import *
from datetime import date, timedelta, datetime
from django import forms
from django.db import transaction
from django.db.models import Q, Max
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import auth
from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import loader, Context, RequestContext
from django.template.loader import render_to_string
from django.utils import simplejson
from django.views.decorators.csrf import csrf_protect
from time import mktime
from LASAuth.decorators import laslogin_required
from django.core.mail import send_mail, EmailMultiAlternatives
from django.contrib.auth.decorators import user_passes_test
import os, cStringIO, csv, time, urllib, urllib2, ast, json
from django.conf import settings

@laslogin_required 
@login_required        
def experiment_prot(request):
    print 'CLM view: start experiment_protocol.experiment_prot'
    try:
        print request.GET
        listTypeProtocol, listTypeProcess,listPlates = [],[],[]
        storageHost = Urls_handler.objects.get(name = 'storage').url
        url = storageHost + '/api.info/containertype'
        print url
        req = urllib2.Request(url, headers={"workingGroups" : get_WG_string()})
        u = urllib2.urlopen(req)
        plates = ast.literal_eval(u.read())
        for p in plates:
            listPlates.append((p, p))
        typeProtocol = Allowed_values.objects.filter(condition_feature_id = Condition_feature.objects.get(name = 'type_protocol'))
        for t in typeProtocol:
            listTypeProtocol.append((t.allowed_value, t.allowed_value))
        typeProcess = Allowed_values.objects.filter(condition_feature_id = Condition_feature.objects.get(name = 'type_process'))
        for t in typeProcess:
            listTypeProcess.append((t.allowed_value, t.allowed_value))
        form = NewProtocolForm(listPlates, listTypeProtocol, listTypeProcess)
        if request.method == 'POST':
            print request.POST
            print request.FILES
            #se c'e' il campo description nella post, vuol dire che l'utente ha inviato le info base del protocollo
            if 'description' in request.POST:
                form = NewProtocolForm(listPlates, listTypeProtocol, listTypeProcess, request.POST)
                if form.is_valid():
                    print 'here1'
                    request.session['newProtPost'] = request.POST #informazioni generali del protocollo
                    print request.session['newProtPost']
                    if len(request.FILES) > 0:
                        f = request.FILES['fileName']
                        fn = os.path.basename(f.name)
                        filePath = os.path.join(os.path.dirname(__file__).rsplit('/', 1)[0],'CellLineSiteMedia/tempFiles/'+fn)
                        open(filePath, 'wb').write(f.read())
                        request.session['fileInfo'] = fn
                    types = Condition_protocol_element.objects.filter(condition_protocol_element_id__isnull = True)
                    return render_to_response(
                        'cell_line_generation/cell_line_generation_change_protocol_cc.html',{'user': request.user,'type_el':types,'selectComponent':'selectComponent',},context_instance=RequestContext(request))

            if 'elementsDict' in request.POST:
                request.session['elementsDict'] = request.POST
                return HttpResponseRedirect(reverse("cellLine.protocol.saveNewProtocol"))
        if request.method == 'GET' and 'namecc' in request.GET:
            namecc = request.GET['namecc'].rsplit('_', 1)[0]
            cc_id = Condition_protocol.objects.get(protocol_name = namecc).id
            protocols_list = []     
            for cc in Condition_protocol.objects.all():
                protocols_list.append({'id':cc.id, 'conf_name':cc.protocol_name})
            types = Condition_protocol_element.objects.filter(condition_protocol_element_id__isnull = True)
            return render_to_response('cell_line_generation/mod_culturing_condition.html',
                {'user': request.user, 'form': form, 'namecc':namecc, 'cc_id':cc_id, 'selectComponent':'selectComponent', 'protocols_list':protocols_list, 'type_el':types, }, 
                context_instance=RequestContext(request))
        return render_to_response('protocol_experiment/protocol_experiment.html',
            {'user': request.user, 'form': form, 'start':'start', }, context_instance=RequestContext(request))
    except Exception, e:
        print 'CLM VIEW experiment_protocol.experiment_prot : 1)' + str(e)
        return render_to_response('error_page.html', {'user': request.user,'name':'Protocol Manager', 'err_message': "Something went wrong! " + str(e)  })