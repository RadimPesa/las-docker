# -*- coding: utf-8 -*-
from piston.handler import BaseHandler
from loginmanager.models import *
from django.core import serializers
from django.db import models
from django.http import HttpResponse
from django.db.models import Q
import operator,datetime
import urllib, urllib2, json,ast
from django.views.decorators.csrf import csrf_exempt
from django.utils import simplejson

#per autocompletamento        
class QueryModuleUserHandler(BaseHandler):
    allowed_methods = ('GET')
    def read(self, request):
        try:
            print request.GET
            if 'q' in request.GET and 'module' in request.GET:
                mulist = LASUser.objects.filter(modules__shortname=request.GET.get('module'),username__icontains=request.GET.get('q'))
                res=[]
                for mu in mulist:
                    res.append(mu.username)
                #print res
                return res
            return " "
        except Exception, e:
            print e
            print "[LASAuthServer][api query] - error ModuleUser autocomplete"
            
class AutocompleteUserHandler(BaseHandler):
    allowed_methods = ('GET')
    def read(self, request):
        try:
            print request.GET
            if 'q' in request.GET:
                mulist = LASUser.objects.filter(username__icontains=request.GET.get('q'))
                res=[]
                for mu in mulist:
                    res.append(mu.username)
                #print res
                return res
            return " "
        except Exception, e:
            print e
            print "[LASAuthServer][api AutocompleteUserHandler] - error"
