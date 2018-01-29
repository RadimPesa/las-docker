from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import loader, Context, RequestContext
from piston.handler import BaseHandler
from sangerApp.models import *
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
from sangerApp.utils.biobank import *
from sangerApp.utils.storage import *
from apisecurity.decorators import get_functionality_decorator
from django.utils.decorators import method_decorator
from uuid import uuid4

def getNewUUID():
    return uuid4().hex

class NewRequest(BaseHandler):
    allowed_methods = ('POST')
    @method_decorator(get_functionality_decorator)
    @transaction.commit_manually
    def create(self, request):
        try:
            print 'stat new req'
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
            print 'end new request'
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



class NewMutation(BaseHandler):
    allowed_methods = ('POST')
    @method_decorator(get_functionality_decorator)
    @transaction.commit_manually
    def create(self, request):
        try:
            print 'new mutation'
            print request.raw_post_data
            raw_data = simplejson.loads(request.raw_post_data)
            print raw_data
            mutInfo = raw_data['mut']
            print request.user.username
            mutInfo['uuid'] = str(request.user.username) + '_' + str(getNewUUID())
            mut = Mutation(user = request.user, mutation = json.dumps(mutInfo))
            mut.save()
            transaction.commit()
            return {'status':'insert'}
        except Exception, e:
            print 'error new mut', e
            transaction.rollback()
            return HttpResponseBadRequest("Error in saving data")
        finally:
            transaction.rollback()
