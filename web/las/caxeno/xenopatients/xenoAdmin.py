from __init__ import *
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
from django.db.models import get_model
from apisecurity.decorators import *

@laslogin_required
@login_required
@permission_decorator('xenopatients.can_view_XMM_admin')
def start(request):
    print 'XMM VIEW: start xenoAdmin.start'
    if request.method == 'POST':
        try:
            req = json.loads(request.POST['d'])
            model = duh.escape(req['model'])
            dataR = req['dataR']
            for key,val in dataR.items():
                vnuovo=duh.escape(val)
                dataR[key]=vnuovo
            get_model('xenopatients', model).objects.create(**dataR)
            return HttpResponse('Added new record.')
        except Exception, e:
            print e
            return HttpResponse(e)
    if 'nameT' in request.GET:
        print 'get'
        nameT = request.GET['nameT']
        print "'"+nameT+"'"
        try:
            model_class = get_model('xenopatients', nameT)
            print model_class
            test = []
            for record in model_class.objects.all():
                temp = {}
                #for field in record._meta.get_all_field_names():
                for field in record._meta.fields:
                    f =  getattr(record, field.name)
                    if str(f) == "None":
                        f = ""
                    temp[field.name] = f
                test.append(temp)
            print test
            return HttpResponse(json.dumps(test), content_type="application/json")
        except Exception, e:
            print e
    tables = {
              'Drugs': {'nameT': 'Drugs', 'attrs':{'name':'string|y|45', 'description':'string|n|255', 'linkToDoc':'text|n', 'safetySheet':'text|n'}},
              'Mice strain': {'nameT': 'Mouse_strain', 'attrs':{'mouse_type_name':'string|y|45', 'officialName':'string|n|80', 'linkToDoc':'text|n'}},
              'Explant scope details': {'nameT': 'Scope_details', 'attrs': {'description':'string|y|45'}},
              'Site of implant': {'nameT': 'Site', 'attrs':{'shortName':'string|y|3', 'longName':'string|y|50'}},
              'Mice suppliers': {'nameT': 'Source', 'attrs':{'name':'string|y|45', 'description':'string|n|45'}},
              'Tissue type': {'nameT': 'TissueType', 'attrs':{'abbreviation':'string|y|3', 'name':'string|y|45', 'notes':'string|n|150'}},
              'Methods of administration': {'nameT': 'Via_mode', 'attrs':{'description':'string|y|255', 'longDescription':'text|n'}},
    }
    return render_to_response('admin/admin.html',{'tables':tables}, RequestContext(request))
