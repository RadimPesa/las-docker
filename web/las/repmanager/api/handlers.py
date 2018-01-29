from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import loader, Context, RequestContext
from piston.handler import BaseHandler
from datamanager.models import *
from django.core import serializers
from django.db import models
from django.http import HttpResponse
from django.db.models import Q
import string, json, urllib2, urllib, ast, operator, datetime
from api.utils import *
from django.contrib import auth
from os import path
from datamanager.utils.repositoryUtils import *

from django.core.servers.basehttp import FileWrapper
import shutil

from bson.objectid import ObjectId


class NewFileRep(BaseHandler):
    allowed_methods = ('POST')
    def create(self, request):
        try:
            postdata = self.flatten_dict(request.POST)
            print postdata
            postdata['operator'] = postdata.get('operator','')
            postdata['genealogy'] = postdata.get('genealogy', '')
            timestamp = datetime.datetime.now()
            tempFolder = path.join(TEMP_URL, postdata['operator'] + str(timestamp) )
	    os.mkdir(tempFolder)
            fin = request.FILES['file']
            # save the uploaded file in a temporany directory
            destination = handle_uploaded_file(fin, tempFolder)
            # create the entry in mongo rep
            rData = RepData (genealogy=postdata['genealogy'], name=fin.name, created=timestamp, owner=postdata['operator'], extension=os.path.splitext(destination)[1])
            rData.resource.put(open(destination))
            rData.save()
            print rData.id
            # remove the files from the temporany dirctory
            shutil.rmtree (tempFolder)
            return {'status': 'Ok', 'objectId':str(rData.id)}
        except Exception, e:
            print e
            return {'status':'Failed'}

class NewExpRep(BaseHandler):
    allowed_methods = ('POST')
    def create(self, request):
        try:
            postdata = self.flatten_dict(request.POST)
            print postdata
            postdata['operator'] = postdata.get('operator','')
            postdata['experiment'] = postdata.get('experiment', '')
            timestamp = datetime.datetime.now()
            tempFolder = path.join(TEMP_URL, postdata['operator'] + str(timestamp) )
            os.mkdir(tempFolder)
            print 
            filelist = []
            for fname, fin in request.FILES.items():
                # save the uploaded file in a temporany directory
                destination = handle_uploaded_file(fin, tempFolder)
                # create the entry in mongo rep
                print os.path.splitext(destination)
                rData = RepData (genealogy = '', name=fin.name, created=timestamp, owner=postdata['operator'], extension=os.path.splitext(destination)[1])
                rData.resource.put(open(destination))
                print rData
                rData.save()
                print rData.id
                filelist.append(rData)

            exp = Experiment(experiment_type=postdata['experiment'], sources=filelist)
            exp.save()
            # remove the files from the temporany dirctory
            shutil.rmtree (tempFolder)
            return {'status': 'Ok', 'objectId':str(exp.id)}
        except Exception, e:
            for r in filelist:
                r.resource.delete()
                r.delete()
            exp.delete()
            shutil.rmtree (tempFolder)
            print e
            return {'status':'Failed'}

class GetLink(BaseHandler):
    allowed_methods = ('GET')
    def read (self, request, link, typeO):
        print link, typeO
        try:            
            if typeO == "uarraychip":
                chipInfo = UArrayChip.objects(id=link)[0]
                print chipInfo
                resp = {'info':{'barcode':chipInfo.barcode if chipInfo.barcode != None else "", 'sources':[]}}
                print resp
                for r in chipInfo.sources:
                    print r
                    resp['info']['sources'].append({'link': r.id, 'name': r.name, 'created': str(r.created), 'owner': r.owner, 'extension': r.extension})
                return resp
            if typeO == "uarraysample":
                sampleInfo = UArraySample.objects(id=link)[0]
                print sampleInfo
                resp = {'info':{'chip':sampleInfo.chip.barcode if sampleInfo.chip.barcode != None else "", 'position': sampleInfo.position if sampleInfo.position != None else "", 'genealogy':sampleInfo.genid if sampleInfo.genid else '', 'sources':[]}}
                for r in sampleInfo.sources:
                    resp['info']['sources'].append({'link': r.id, 'name': r.name, 'created': str(r.created), 'owner': r.owner, 'extension': r.extension})
                return resp
        except Exception, e:
            print e
            return {'response':'Bad request'}

class GetSampleInfo(BaseHandler):
    allowed_methods = ('GET')
    def read (self, request):
        print 'GetSampleInfo'
        print request.GET['genid']
        try:
            try:
                genids = json.loads(request.GET['genid'])
            except:
                genids = []
            print genids
            samples = UArraySample.objects(genid__in=genids)
            print samples
            resp = {'samples':[]}
            for s in samples:
                print s.chip
                resp['samples'].append({'genid':s.genid, 'chip':s.chip.barcode, 'position':s.position, 'link':s.id, 'hybevent':s.chip.hybevent, 'scan':s.chip.scan})
            print resp
            return resp
        except Exception, e:
            print e
            return {'response':'Bad request'}

class GetChipInfo(BaseHandler):
    allowed_methods = ('GET')
    def read (self, request):
        print 'GetChipInfo'
        print request.GET['barcode']
        try:
            try:
                barcode = json.loads(request.GET['barcode'])
            except:
                barcode = ''
            print barcode
            chips = UArrayChip.objects(barcode=str(barcode))
            print '----'
            print chips
            print '----'
            resp = {'scanevents':[]}
            for c in chips:
                assignments = []
                samples = UArraySample.objects(chip=c.id)
                #print len(samples)
                for s in samples:
                    print s.id
                    assignments.append({'position':s.position, 'link':s.id, 'sample': s.genid, 'qc':''})
                resp['scanevents'].append({'id':c.scan, 'startScanTime':'', 'endScanTime':'', 'link':c.id, 'protocol':'', 'notes':'','assignments':assignments })
            #print resp
            return resp
        except Exception, e:
            print e
            return {'response':'Bad request'}
