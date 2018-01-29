from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import loader, Context, RequestContext
from piston.handler import BaseHandler
from profiling.models import *
from django.core import serializers
from django.db import models
from django.http import HttpResponse
from django.db.models import Q
import string
import operator
import datetime
from api.utils import *
from django.contrib import auth
import json, urllib2, urllib, simplejson, ast
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from profiling.utils.biobank import *
from profiling.utils.storage import *
from profiling.utils.annotation import *
from profiling.utils.analysis import *


from apisecurity.decorators import get_functionality_decorator
from django.utils.decorators import method_decorator


class NewRequest(BaseHandler):
    allowed_methods = ('POST')
    @transaction.commit_manually
    @method_decorator(get_functionality_decorator)
    def create(self, request):
        try:
            postdata = self.flatten_dict(request.POST)
            # ensure that the worker field is present
            postdata['operator'] = postdata.get('operator','')
            postdata['aliquots'] = postdata.get('aliquots','')
            print '--------'
            print datetime.datetime.now()
            print '---------'
            newRequest = Request(timestamp = datetime.datetime.now(), owner=postdata['assigner'])
            if postdata['operator'] != '':
                operator = User.objects.get(username = postdata['operator'])
                print operator
                newRequest.idOperator = operator
            print newRequest
            newRequest.save()
            for aliquotInfo in simplejson.loads(postdata['aliquots']):
                print aliquotInfo
            
                al = Aliquot.objects.filter(genId=aliquotInfo['genid'])
                if al:
                    al = al[0]
                else:
                    al = Aliquot(genId=aliquotInfo['genid'])
                al.concentration = float(aliquotInfo['conc'])
                al.volume = float(aliquotInfo['vol'])
                dateAl = aliquotInfo['date'].split('-')
                print dateAl
            
                al.date = datetime.date(int(dateAl[0]), int(dateAl[1]), int(dateAl[2]))
                print al.date
                al.save()
                
                alreq = Aliquot_has_Request(aliquot_id = al, request_id= newRequest, volumetaken=float(aliquotInfo['takenvol']) )
                alreq.plate = aliquotInfo['father']
                alreq.well = aliquotInfo['pos']
                alreq.save()
            
            transaction.commit()
            return {"requestid": newRequest.id}
        except Exception, e:
            transaction.rollback()
            print e
            return {"requestid": 'Error'}
        
        finally:
            transaction.rollback()
        
class DeleteRequest(BaseHandler):
    allowed_methods = ('POST')
    @transaction.commit_manually
    @method_decorator(get_functionality_decorator)
    def create(self, request):
        try:
            print 'delete request'
            raw_data = simplejson.loads(request.raw_post_data)
            user = User.objects.get(username = raw_data['user'])
            plan = Request.objects.get(id=raw_data['idplan'])
            aliquots = Aliquot_has_Request.objects.filter(request_id=plan)
            for al in aliquots:
                al.abortTime = datetime.datetime.now()
                al.abortUser = user
                al.save()
            plan.pending = False
            plan.save()
            bioAliquots = []
            for al in aliquots:
                bioAliquots.append(al.aliquot_id.genId)
            resetAliquotRequested(bioAliquots)
            transaction.commit()
            return {'status':'deleted'}
        except:
            transaction.rollback()
            return HttpResponseBadRequest("Error in saving data")
        finally:
            transaction.rollback()


class GetLayout(BaseHandler):
    allowed_methods = ('GET')
    @method_decorator(get_functionality_decorator)
    def read (self, request, layoutid):
        response = getGeometry(layoutid)
        return response

class GetGenes(BaseHandler):
    allowed_methods = ('GET')
    @method_decorator(get_functionality_decorator)
    def read (self, request, gene):
        response = retrieveGeneSymbols(gene)
        listGenes = []
        print response
        for k, v in response.items():
            for gene in v:
                listGenes.append(gene)
        print listGenes
        return listGenes

class GetMutations(BaseHandler):
    allowed_methods = ('GET')
    @method_decorator(get_functionality_decorator)
    def read (self, request, gene):
        print '[FINGER-api]: GetMutations'
        response = retrieveMutations(gene)
        return response

class GetFormulas(BaseHandler):
    allowed_methods = ('GET')
    @method_decorator(get_functionality_decorator)
    def read (self, request):
        print request.GET
        try:
            regions = json.loads(request.GET['regions'])
        except:
            regions = []
        try:
            bmeasures = json.loads(request.GET['measures'])
        except: 
            bmeasures = []
        try:
            measures = json.loads(request.GET['general_measures'])
        except:
            measures =[]
        measBiopsy = MeasureType.objects.filter(idMeasure__in=Measure.objects.filter(pk__in=bmeasures), region__in=Region.objects.filter(pk__in=regions))
        measures.extend([m.lasmeasureId for m in measBiopsy])
        print measures
        resp =  getFormulas (measures)
        print resp
        return resp


class NewFilter(BaseHandler):
    allowed_methods = ('POST')
    @transaction.commit_manually
    @method_decorator(get_functionality_decorator)
    def create(self, request):
        try:
            postdata = self.flatten_dict(request.POST)
            # ensure that the worker field is present
            postdata['operator'] = postdata.get('operator','')
            postdata['filter'] = postdata.get('filter','')
            postdata['aliquots'] = postdata.get('aliquots','')
            print '--------'
            print datetime.datetime.now()
            print '---------'
            operator = User.objects.get(username = postdata['operator'])
            newFilter = FilterSession (timestamp = datetime.datetime.now(), operator=operator, features=postdata['filter'])
            print newFilter
            newFilter.save()
            aliquotInfo = simplejson.loads(postdata['aliquots'])
            for al, alFilter in aliquotInfo.items():
                print al, alFilter
                aliquot = Aliquot.objects.get(genId=al)
                alfilt = Aliquot_has_Filter(aliquot_id = aliquot, filter_id= newFilter, values=json.dumps(alFilter))
                alfilt.save()
            
            transaction.commit()
            return {"filterid": newFilter.id}
        except Exception, e:
            transaction.rollback()
            print e
            return {"requestid": 'Error'}
        
        finally:
            transaction.rollback()


