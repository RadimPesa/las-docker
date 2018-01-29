from functools import wraps
from django.http import HttpResponse
from django.conf import settings
import hmac
import hashlib
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseRedirect
from apisecurity.apikey import *
from django.core.urlresolvers import reverse
from global_request_middleware import *
from django.contrib.auth.models import User,Permission
from datamanager.models import *
from py2neo import neo4j, cypher
import ast

def required_parameters(parameters):
    def inner_decorator(fn):
        def wrapped(request, *args, **kwargs):
            http_method=request.method
            if parameters not in getattr(request, http_method):
                return HttpResponseRedirect(reverse("django.views.defaults.permission_denied"))
            else:
                if http_method=='POST':
                    received= request.POST.get('api_key')
                elif http_method=='GET':
                    received= request.GET.get('api_key')
                else:
                    return HttpResponseRedirect(reverse("django.views.defaults.permission_denied"))
                try:
                    key= ast.literal_eval(received)
                    if checkApiKey(key['digest'],key['timestamp'])==False:
                        return HttpResponseRedirect(reverse("django.views.defaults.permission_denied"))
                    else:
                        print "Permesso accordato"
                except:
                    return HttpResponseRedirect(reverse("django.views.defaults.permission_denied"))

            return fn(request, *args, **kwargs)
        return wraps(fn)(wrapped)
    return inner_decorator



def permission_decorator(parameters):
    def inner_decorator(fn):
        def wrapped(request, *args, **kwargs):
            user= User.objects.get(username=request.user.username)
            if not user.has_perm(parameters):
                return HttpResponseRedirect(reverse(settings.APPNAME+".views.error"))
            a, codename = str(parameters).split(".")
            perm=Permission.objects.get(codename=codename)
            WG_list=WG_User.objects.filter(user=user,permission=perm)
            wgList = [wg.WG.name for wg in WG_list]
            wgNameSet=set()
            for wg in wgList:
                wgNameSet.add(wg)
            namelist= ",".join(wgList)
            set_WG(wgNameSet)
            request.workingGroups=namelist
            return fn(request, *args, **kwargs)
        return wraps(fn)(wrapped)
    return inner_decorator




def get_functionality_decorator(fn):
    def wrapped(request, *args, **kwargs):
        #print request.META
        if 'HTTP_WORKINGGROUPS' in request.META:
            try:            
                if request.META['HTTP_WORKINGGROUPS'] !='':
                    groups=request.META['HTTP_WORKINGGROUPS'].split(",")
                    groupSet=set()
                    if len(groups)>0:
                        for g in groups:
                            groupSet.add(g)
                        set_WG(groupSet)   
                    else:
                        set_WG(set())
                else:
                    set_WG(set())
            except Exception,e:
                print e
        else:
            set_WG(set())
        '''
        if request.method=='POST':
            if 'workingGroups' in request.POST:
                groups=request.POST['workingGroups'].split(",")
                groupSet=set()
                for g in groups:
                    groupSet.add(g)
                set_WG(groupSet)
            elif 'workingGroups' in request:
                groups=request.workingGroups.split(",")
                groupSet=set()
                for g in groups:
                    groupSet.add(g)
                set_WG(groupSet)
            else:
                print "nessun WG"
        elif request.method=='GET':
            if 'workingGroups' in request.GET:
                groups=request.GET['workingGroups'].split(",")
                groupSet=set()
                for g in groups:
                    groupSet.add(g)
                set_WG(groupSet)
            elif 'workingGroups' in request:
                groups=request.workingGroups.split(",")
                groupSet=set()
                for g in groups:
                    groupSet.add(g)
                set_WG(groupSet)
            else:
                print "nessun WG"
        '''
        return fn(request, *args, **kwargs)
    return wraps(fn)(wrapped)



