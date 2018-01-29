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
from cellLine.models import *
from LASAuth.decorators import laslogin_required
from django.core.mail import send_mail, EmailMultiAlternatives
from django.conf import settings
from apisecurity.apikey import *
import os, cStringIO, csv, time, urllib, urllib2, hmac, hashlib, ast, json, requests
from global_request_middleware import *

'''# Restituisce la url per la biobanca (generation - general case)
def UrlSendDataGeneration(request):
    if request.method == 'POST':
        print request.POST
        try:
            name = request.POST['name']
            implants = request.POST['implants']
            url = Urls_handler.objects.get(name = name).url
            data = urllib.urlencode({'implants':implants})
            u = urllib2.urlopen(url+'/api/aliquot/canc/', data)
            return HttpResponse(u.read(),mimetype='application/json')
        except urllib2.HTTPError,e:
            if str(e.code)=='403':
                print "NON VALIDO"
                return_dict = {"message":str(e.code)}
                json_response = json.dumps(return_dict)
                return HttpResponse(json_response,mimetype='application/json')'''

# Restituisce la url per la biobanca (archivio)
def UrlSendDataArchive(request):
    print 'CLM view: start externalApiHandler.UrlSendDataArchive'
    if request.method == 'POST':
        print request.POST
        try:
            name = request.POST['name']
            explants = request.POST['explants']
            url = Urls_handler.objects.get(name = name).url + '/explants/'
            data = urllib.urlencode({'explants':explants, 'operator': request.POST['operator'], 'date': request.POST['date'], 'source': request.POST['source']})
            req = urllib2.Request(url, data=data, headers={"workingGroups" : get_WG_string()})
            u = urllib2.urlopen(req)
            return HttpResponse(u.read(),mimetype='application/json')
        except urllib2.HTTPError,e:
            if str(e.code)=='403':
                print "NON VALIDO"
                return_dict = {"message":str(e.code)}
                json_response = json.dumps(return_dict)
                return HttpResponse(json_response,mimetype='application/json')


def searchCellNames(request):
    print 'CLM view: start externalApiHandler.searchCellNames'
    try:
        name = request.GET['name']
        url = Urls_handler.objects.get(name = 'annotations').url + "/api/cellLineFromName/" + "?name=" + name
        print url
        req = urllib2.Request(url, headers={"workingGroups" : get_WG_string()})
        u = urllib2.urlopen(req)
        res = u.read()
        print res
        #return ast.literal_eval(res)
        return HttpResponse(res,mimetype='application/json')
    except Exception, e:
        print 'CLM VIEW externalAPIhandler.searchCellNames: 1) ' + str(e)
        return 'err'


def newCellName(request):
    print 'CLM view: start externalApiHandler.newCellName'
    try:
        name = request.GET['name']
        #url: "http://skylark.polito.it:8000/api/newCellLine/",
        url = Urls_handler.objects.get(name = 'annotations').url + "/api/newCellLine/" 
        values = {'name' : name}
        #u = requests.post(url, data=values)
        data = urllib.urlencode(values)
        req = urllib2.Request(url, data=data, headers={"workingGroups" : get_WG_string()})
        u = urllib2.urlopen(req)
        #res = json.dumps(u.read())
        res = u.read()
        #print res
        #return ast.literal_eval(res)
        return HttpResponse(res,mimetype='application/json')
    except Exception, e:
        print 'CLM VIEW externalAPIhandler.newCellName: 1) ' + str(e)
        return 'err'