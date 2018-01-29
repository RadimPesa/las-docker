from datetime import date, timedelta, datetime
from django import forms
from django.db import transaction
from django.db.models import Q, Max
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import auth
from django.contrib.auth.models import User
from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import loader, Context, RequestContext
from django.template.loader import render_to_string
from django.utils import simplejson
from django.views.decorators.csrf import csrf_protect
from time import mktime
from xenopatients.forms import *
from xenopatients.models import *
from xenopatients.utils import *
from xenopatients.moreUtils import *
from LASAuth.decorators import laslogin_required
from django.core.mail import send_mail, EmailMultiAlternatives
from django.conf import settings
from apisecurity.apikey import *
import os, cStringIO, csv, time, urllib, urllib2, hmac, hashlib, ast
from apisecurity.decorators import get_functionality_decorator
from global_request_middleware import *
from django.utils.decorators import method_decorator


#@method_decorator(@get_functionality_decorator)
def checkBarcodeT(request):
    print 'XMM VIEW: start externalAPIhandler.checkBarcodeT'
    if request.method == 'POST':
        address = UrlStorage.objects.get(default = '1').address
        barcodeT = request.POST.get('barcodeT')
        url = address + "/api/biocassette/" + barcodeT + "/tube"
        h = getApiKey()
        values = {'api_key' : h }
        data = urllib.urlencode(values)
        url += "?"+data
        req = urllib2.Request(url, headers={"workingGroups" : get_WG_string()})
        try:
            u = urllib2.urlopen(req)
            res =  u.read()
            return HttpResponse(res,mimetype='application/json')
        except urllib2.HTTPError,e:
            if str(e.code)=='403':
                return_dict = {"message":str(e.code)}
                json_response = json.dumps(return_dict)
                return HttpResponse(json_response,mimetype='application/json')

#@method_decorator(@get_functionality_decorator)
def loadExplantPlate(barcode, typeP, typeC):  #aliquot ---> typeA
    print 'XMM VIEW: start externalAPIhandler.loadExplantPlate'
    try:
        url = Urls.objects.get(default = '1')
        urlString = url.url + "/api/generic/load/" + barcode + "/" + typeP + "/" +  typeC 
        print "qui", urlString
        req = urllib2.Request(urlString, headers={"workingGroups" : get_WG_string()})
        #u = urllib2.urlopen()
        print urlString
        u = urllib2.urlopen(req)
        res = u.read()
        print res
        return ast.literal_eval(res)
    except Exception, e:
        print 'XMM VIEW externalAPIhandler.loadExplantPlate: 1) ' + str(e)
        return 'err'
