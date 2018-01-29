from django import forms
from django.db import transaction
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.contrib import auth
from django.db.models import Q
import urllib, urllib2, os, json, ast
from django.utils import simplejson
from LASAuth.decorators import laslogin_required
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.models import User,Permission
from django.contrib.contenttypes.models import ContentType
from apisecurity.decorators import required_parameters
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings

@csrf_exempt
@required_parameters(parameters=('api_key'))
def editPermission(request):
    try:
        if request.method=='POST':
            lista_perm=request.POST.get('lista')
            username=request.POST.get('username')
            print request.POST
            
            p=lista_perm.split(",")
            u=User.objects.get(username=username)
            u.user_permissions.clear()
            for x in p:
                if x!="":
                    print "sto settando"
                    perm=Permission.objects.get(codename=x)
                    u.user_permissions.add(perm)
        return HttpResponse("ok")
    except Exception, e:
        print e
        return HttpResponse("err")


@csrf_exempt
@required_parameters(parameters=('api_key'))
def editModules(request):
    try:
        if request.method=='POST':
            enable=request.POST.get('enable')
            username=request.POST.get('username')
            password=request.POST.get('password')
            mail=request.POST.get('email')
            if enable=='yes':
                try:
                    u=User.objects.get(username=username)
                except User.DoesNotExist:
                    u = None
                if u is not None:
                    u.is_active=True;
                    u.save()
                else:
                    u = User()
                    u.username = username
                    u.password=password
                    u.email=mail
                    u.save()
            elif enable=='no':
                try:
                    u=User.objects.get(username=username)
                except User.DoesNotExist:
                    u = None
                if u is not None:
                    u.is_active=False;
                    u.save()
        return HttpResponse("ok")
    
    except Exception, e:
        print e
        return HttpResponse("err")
