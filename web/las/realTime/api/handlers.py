from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import loader, Context, RequestContext
from piston.handler import BaseHandler
from rtpcr.models import *
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
from rtpcr.utils.biobank import *
from rtpcr.utils.storage import *
from apisecurity.decorators import get_functionality_decorator
from django.utils.decorators import method_decorator

class NewRequest(BaseHandler):
    allowed_methods = ('POST')
    @method_decorator(get_functionality_decorator)
    @transaction.commit_manually
    def create(self, request):
        try:
            postdata = self.flatten_dict(request.POST)
            # ensure that the worker field is present
            postdata['operator'] = postdata.get('operator','')
            postdata['aliquots'] = postdata.get('aliquots','')
            postdata['assigner'] = postdata.get('assigner','')
            postdata['notes'] = postdata.get('notes','')
            print '--------'
            print datetime.datetime.now()
            print '---------'
            newRequest = Request(timestamp=datetime.datetime.now(),owner=postdata['assigner'],description=postdata['notes'])
            try:
                operator = User.objects.get(username=postdata['operator'])
                newRequest.idOperator = operator
            except Exception, e:
                print e
            print newRequest
            newRequest.save()
            for aliquotInfo in simplejson.loads(postdata['aliquots']):
                print aliquotInfo['genid']
                print float(aliquotInfo['vol'])
                print float(aliquotInfo['conc'])
                print aliquotInfo['date']

                al = Aliquot.objects.filter(genId=aliquotInfo['genid'])
                if al:
                    al = al[0]
                else:
                    al = Aliquot(genId=aliquotInfo['genid'])
                al.concentration = float(aliquotInfo['conc'])
                al.volume = float(aliquotInfo['vol'])
                al.owner = postdata['operator']
                dateAl = aliquotInfo['date'].split('-')
                print dateAl

                al.date = datetime.date(int(dateAl[0]), int(dateAl[1]), int(dateAl[2]))
                print al.date
                al.save()

                alreq = Aliquot_has_Request(aliquot_id = al, request_id= newRequest, volumetaken=float(aliquotInfo['takenvol']) )
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
    @method_decorator(get_functionality_decorator)
    @transaction.commit_manually
    def create(self, request):
        try:
            print 'delete request'
            raw_data = simplejson.loads(request.raw_post_data)
            plan = Request.objects.get(id=raw_data['idplan'])
            aliquots = Aliquot_has_Request.objects.filter(request_id=plan)
            bioAliquots = []
            for al in aliquots:
                bioAliquots.append(al.aliquot_id.genId)
            resetAliquotRequested(bioAliquots)
            aliquots.delete()
            plan.delete()
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

from rest_framework import status
from rest_framework.decorators import api_view, parser_classes
from rest_framework.response import Response

@api_view(['GET'])
def analysisDescription(request):
    """
    Get analysis description (by analysisDescription_id)
    """
    print "[RT-PCR API: analysisDescription]"
    if request.method == 'GET':
        try:
            ad_id = request.query_params['id']
        except Exception as error:
            print error
            return Response(str(error), status=status.HTTP_400_BAD_REQUEST)
        
        try:
            ad = AnalysisDescription.objects.get(pk=ad_id)
            ad =  {'id': ad_id, 'analysis_id': ad.analysis_id, 'formula_id': ad.formula_id, 'probe_var_mapping': ad.probe_var_mapping, 'aggregation_criteria': ad.aggregation_criteria}
        except Exception as e:
            print "[RT-PCR API: analysisDescription] Exception:", str(e)
            ad = {}
        resp = Response(ad, status=status.HTTP_200_OK)
        resp['Access-Control-Allow-Headers'] = 'origin, content-type, accept'
        return resp

@api_view(['GET'])
def analysisInput(request):
    """
    Get analysis input dataset (by analysis_id)
    """
    print "[RT-PCR API: analysisInput]"
    if request.method == 'GET':
        try:
            a_id = request.query_params['a_id']
        except Exception as error:
            print error
            return Response(str(error), status=status.HTTP_400_BAD_REQUEST)

        r_id = request.query_params['r_id'] if request.query_params.has_key('r_id') else None

        if r_id is not None:
            try:
                r_id = json.loads(r_id)
                assert(isinstance(r_id, list))
            except:
                return Response("'r_id' must be a list", status=status.HTTP_400_BAD_REQUEST)

        try:
            a = Analysis.objects.get(pk=a_id)
            dataset = []
            if r_id:
                records = a.id_experiment.sample_set.filter(pk__in=r_id)
            else:
                records = a.id_experiment.sample_set.all()
            for s in records:
                record = {'id': s.id, 'genid': s.idAliquot_has_Request.aliquot_id.genId, 'probe_id': s.probe, 'value': s.value}
                dataset.append(record)
        except:
            dataset = []
        resp = Response(dataset, status=status.HTTP_200_OK)
        resp['Access-Control-Allow-Headers'] = 'origin, content-type, accept'
        return resp

@api_view(['GET'])
def analysisOutput(request):
    """
    Get analysis output value (by analysisOutput_id)
    """
    print "[RT-PCR API: analysisInput]"
    if request.method == 'GET':
        params = {}
        try:
            a_id = request.query_params['a_id']
            params['analysis_id'] = a_id
        except:
            a_id = None
        try:
            o_id = json.loads(request.query_params['o_id'])
            params['pk__in'] = o_id
        except:
            o_id = None            
        
        if a_id is None and o_id is None:
            return Response("At least one of the following must be specified: 'a_id', 'o_id'", status=status.HTTP_400_BAD_REQUEST)

        try:
            ao = AnalysisOutput.objects.filter(**params)
            results = []
            for r in ao:
                results.append({'id': str(r.id), 'value': r.value, 'variables': r.getVariableValues(), 'sampleGenid': r.getSampleGenid()})
            resp = Response(results, status=status.HTTP_200_OK)
            resp['Access-Control-Allow-Headers'] = 'origin, content-type, accept'
            return resp
        except Exception as e:
            return Response(str(e), status=status.HTTP_500_SERVER_ERROR)