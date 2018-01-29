from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import loader, Context, RequestContext
from piston.handler import BaseHandler
from MMM.models import *
from django.core import serializers
from django.db import models
from django.http import HttpResponse
from django.db.models import Q
import string
import operator
import datetime
from api.utils import *
from django.contrib import auth
import json
import urllib2, urllib
import ast
from django.db import transaction

from MMM.utils.biobank import *
from MMM.utils.repository import *

from apisecurity.decorators import get_functionality_decorator
from django.utils.decorators import method_decorator



class AliquotFindHandler(BaseHandler):
    allowed_methods = ('GET')
    @method_decorator(get_functionality_decorator)
    def read(self, request, label, date, owner):
        print label.upper(), date, owner.lower()
        if Aliquot.objects.filter(sample_identifier=label.upper(), date=date, owner=owner.lower(), exhausted=True):
            return 'True'
        elif Aliquot.objects.filter(sample_identifier=label.upper(), date=date, owner=owner.lower()):
            return 'Warning'
        else:
            return 'False'


class GenealogyFindHandler(BaseHandler):
    allowed_methods = ('GET')
    @method_decorator(get_functionality_decorator)
    def read(self, request, genid, username):
        resp = {}
        if Aliquot.objects.filter(genId=genid.upper()):
            resp['existFlag'] = 'Warning'
        else:
            resp['existFlag'] = 'False'
        try:
            res = retrieveAliquots (genid.upper(), username)
            
            values = res['data'][0].split("&")
            if values[1] == "errore":
                return {'response':'Bad request'}
            else:
                resp['genealogy'] = genid.upper()
                resp['volume'] = values[1]
                resp['concentration'] = values[2]
                resp['date'] = values[3]
                print resp
                return resp
        except:  
            print "[MMM] - an error occurr in data retrieving"
            return {'response':'Bad request'}
        



class HybProtocolFindHandler(BaseHandler):
    allowed_methods = ('GET')
    @method_decorator(get_functionality_decorator)
    def read(self, request, protocol, instrument):
        prot = HybProtocol.objects.get(name=protocol)
        return {'instrument': instrument, 'protocol': prot.name, 'loadQuantity': prot.loadQuantity, 'hybridTemp':prot.hybridTemp, 'hybTime':prot.hybTime, 'hybBuffer':prot.hybBuffer, 'totalVolume':prot.totalVolume, 'denTemp':prot.denTemp, 'denTime':prot.denTime}



class GetChipHandler(BaseHandler):
    allowed_methods = ('GET')
    @method_decorator(get_functionality_decorator)
    def read(self, request, barcode, status):
        try:
            if status == 'tohybrid':
                chip = Chip.objects.get(barcode=barcode, idHybevent__isnull=True )
                geometry = ast.literal_eval(chip.idChipType.layout.rules)
                return {'id': chip.id, 'barcode':chip.barcode, 'chip_type':chip.idChipType.title, 'npos': chip.idChipType.layout.npos, 'owner':chip.owner, 'expdate':chip.expirationDate, 'geometry':geometry}
            elif status == 'toscan':
                chip = Chip.objects.get(barcode=barcode, idHybevent__isnull=False)
                event = ScanEvent.objects.filter(id__in=Chip_has_Scan.objects.filter(idChip=chip), endScanTime__isnull=True)
                if event:
                    raise Exception
                geometry = ast.literal_eval(chip.idChipType.layout.rules)
                value_to_send = {'id': chip.id, 'barcode':chip.barcode, 'chip_type':chip.idChipType.title, 'npos': chip.idChipType.layout.npos, 'owner':chip.owner, 'expdate':chip.expirationDate, 'pos':[]}
                chipAssign = Assignment.objects.filter(idChip=chip).order_by('position')
                pos = 1
                for assign in chipAssign:
                    print assign
                    sample_identifier = ''
                    if  assign.idAliquot_has_Request.aliquot_id.genId == None:
                        sample_identifier = 'SmpID: ' + str(assign.idAliquot_has_Request.aliquot_id.sample_identifier)
                    else:
                        sample_identifier = 'GenId: ' + str(assign.idAliquot_has_Request.aliquot_id.genId)
                    for i in range(pos, assign.position):
                        value_to_send['pos'].append({'idPos':geometry[i], 'sample_identifier': ''})
                    value_to_send['pos'].append({'idPos':geometry[assign.position], 'sample_identifier': sample_identifier})
                    pos = assign.position+1
                    
                for i in range(pos, chip.idChipType.layout.npos+1):
                        value_to_send['pos'].append({'idPos':geometry[i], 'sample_identifier': ''})
                return value_to_send
            elif status == 'info':
                chip = Chip.objects.get(barcode=barcode)
                return {'id': chip.id, 'barcode':chip.barcode, 'chip_type':chip.idChipType.title, 'npos': chip.idChipType.layout.npos, 'owner':chip.owner, 'expdate':chip.expirationDate}
            elif status == 'scanqc':
                chip = Chip.objects.get(barcode=barcode, idHybevent__isnull=False)
                geometry = ast.literal_eval(chip.idChipType.layout.rules)
                value_to_send = {'id': chip.id, 'barcode':chip.barcode, 'chip_type':chip.idChipType.title, 'npos': chip.idChipType.layout.npos, 'owner':chip.owner, 'expdate':chip.expirationDate, 'pos':[]}
                chipAssign = Assignment.objects.filter(idChip=chip).order_by('position')
                pos = 1
                for assign in chipAssign:
                    print assign
                    sample_identifier = ''
                    if  assign.idAliquot_has_Request.aliquot_id.genId == None:
                        sample_identifier = 'SmpID: ' + str(assign.idAliquot_has_Request.aliquot_id.sample_identifier)
                    else:
                        sample_identifier = 'GenId: ' + str(assign.idAliquot_has_Request.aliquot_id.genId)
                    for i in range(pos, assign.position):
                        value_to_send['pos'].append({'idPos':geometry[i], 'sample_identifier': ''})
                    value_to_send['pos'].append({'idPos':geometry[assign.position], 'sample_identifier': sample_identifier})
                    pos = assign.position+1
                    
                for i in range(pos, chip.idChipType.layout.npos+1):
                        value_to_send['pos'].append({'idPos':geometry[i], 'sample_identifier': ''})
                return value_to_send
            elif status == 'scanevent':
                chip = Chip.objects.get(barcode=barcode, idHybevent__isnull=False)
                print chip    
                scanevent = ScanEvent.objects.filter(endScanTime__isnull=False, id__in=Chip_has_Scan.objects.filter(link__isnull=True, idChip=chip).values('idScanEvent')).order_by('startScanTime')
                print scanevent
                if scanevent:
                    value_to_send = {'chip_id': chip.id, 'geometry':ast.literal_eval(chip.idChipType.layout.rules), 'hybevent': chip.idHybevent.id, 'scanevents':[]}
                    for s in scanevent:
                        value_to_send['scanevents'].append({'id':s.id, 'start':s.startScanTime, 'end': s.endScanTime, 'operator': s.idOperator.username})
                    print value_to_send
                    return value_to_send
                else: 
                    raise Exception
            elif status == 'explore':
                resp = getUarraychip(barcode)
                if len(resp['scanevents'])==0:
                    raise Exception
                print resp
                for scan in resp['scanevents']:
                    event = ScanEvent.objects.get(id=scan['id'])
                    print event
                    scan['startScanTime'] = str(event.startScanTime)
                    scan['endScanTime'] = str(event.endScanTime)
                    scan['notes'] = event.notes
                    scan['protocol'] = event.idProtocol.name
                return resp
            elif status == 'repository':
                print status
                chip = Chip.objects.get(barcode=barcode, idHybevent__isnull=False)
                geometry = ast.literal_eval(chip.idChipType.layout.rules)
                eventInfo = {'assignments':[]}
                assignments = Assignment.objects.filter(idChip=chip).order_by('position')
                for a in assignments:
                    eventInfo['assignments'].append({'position':geometry[a.position], 'sample': a.idAliquot_has_Request.aliquot_id.genId if a.idAliquot_has_Request.aliquot_id.genId != None else ""})
                print eventInfo
                return eventInfo
        except Exception, e:
            print e
            if status == 'tohybrid':
                return {'response':'Chip not available for hybridization'}
            if status == 'toscan':
                return {'response':'Chip not available for scan'}
            if status == 'scanqc':
                return {'response':'Error in retrieving chip. Please contact the administrator.'}
            if status == 'info':
                return {'response':'Chip does not exist'}
            if status == 'scanevent':
                return {'response':'Chip not scanned'}
            if status == 'explore':
                return {'response': 'Chip without scan information'}
        return {'response':'Bad request'}



class ScanProtocolFindHandler(BaseHandler):
    allowed_methods = ('GET')
    @method_decorator(get_functionality_decorator)
    def read(self, request, protocol, instrument):
        prot = ScanProtocol.objects.filter(name=protocol.lower())
        params = Parameter.objects.filter(idInstrument=instrument)
        print prot, params
        resp = {'protocolcheck': False, 'params':[]}
        if prot:
            resp['protocolcheck'] =  True
        for p in params:
            resp['params'].append({'id':p.id, 'name': p.name, 'default_value': p.default_value, 'unity':p.unity_measure})
        print resp
        return resp


class ScanProtocolGetHandler(BaseHandler):
    allowed_methods = ('GET')
    @method_decorator(get_functionality_decorator)
    def read(self, request, protocol):
        print protocol
        prot = ScanProtocol.objects.get(id=protocol)
        params = Protocol_has_Parameter_value.objects.filter(idProtocol=prot)
        print prot
        resp = {'protocolid':prot.id, 'protocol': prot.name, 'software': prot.idSoftware.name, 'instrument': prot.idInstrument.name,'instrument_pos': prot.idInstrument.positions,'params':[]}
        for p in params:
            resp['params'].append({'name': p.idParameter.name, 'value': p.value, 'unity':p.idParameter.unity_measure})
        print resp
        return resp

class LayoutGetHandler(BaseHandler):
    allowed_methods = ('GET')
    @method_decorator(get_functionality_decorator)
    def read(self,request, positions):
        print positions
        resp = {'layouts':[]}
        geom = Geometry.objects.filter(npos=positions)
        for g in geom:
            resp['layouts'].append({'idg':g.id, 'rules':ast.literal_eval(g.rules)})
        return resp


class UpdateSamples(BaseHandler):
    allowed_methods = ('POST')
    @method_decorator(get_functionality_decorator)
    def create(self, request):
        try:
            postdata = self.flatten_dict(request.POST)
            print postdata
            samples = ast.literal_eval(request.POST.get('samples', ""))
            scanEvent = ScanEvent.objects.get(id=postdata['scanevent'])
            chip = Chip.objects.get(id=postdata['chip'])
            geometry = ast.literal_eval(chip.idChipType.layout.rules)
            chipAssign = Assignment.objects.filter(idChip=chip).order_by('position')
            for assignement in chipAssign:
                scanned = Assignment_has_Scan.objects.get(idAssignment=assignement, idScanEvent=scanEvent)
                link = samples[geometry[assignement.position]]
                scanned.link = link
                scanned.save()
            chipScanned = Chip_has_Scan.objects.get(idChip=chip, idScanEvent=scanEvent)
            chipScanned.link = postdata['link']
            chipScanned.save()
            return {'status':'Ok'}
        except Exception, e:
            print e
            return {'status':'Failed'}

class NewRequest(BaseHandler):
    allowed_methods = ('POST')
    @method_decorator(get_functionality_decorator)
    @transaction.commit_manually
    def create(self, request):
        try:
            postdata = self.flatten_dict(request.POST)
            # ensure that the worker field is present
            postdata['operator'] = postdata.get('operator','')
            postdata['assigner'] = postdata.get('assigner','')
            postdata['aliquots'] = postdata.get('aliquots','')
            postdata['notes'] = postdata.get('notes','')
            print '--------'
            print datetime.datetime.now()
            print postdata['operator']
            print postdata['assigner']
            print '---------'
            
            newRequest = Request(timestamp = datetime.datetime.now(), owner=postdata['assigner'], description=postdata['notes'])
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
                alreq = Aliquot_has_Request(aliquot_id = al, request_id= newRequest) 
                alreq.save()
                for i in range(1,int(aliquotInfo['replicates'])):
                    alreq = Aliquot_has_Request(aliquot_id = al, request_id= newRequest, tech_replicates=True)
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
            resetAliquotRequested(bioAliquots, raw_data['operator'])
            aliquots.delete()
            plan.delete()
            transaction.commit()
            return {'status':'deleted'}
        except Exception,e:
	    print 'exception in delete request micro:',e
            transaction.rollback()
            return HttpResponseBadRequest("Error in saving data")
        finally:
            transaction.rollback()

class DeleteHybPlan(BaseHandler):
    allowed_methods = ('POST')
    @method_decorator(get_functionality_decorator)
    @transaction.commit_manually
    def create(self, request):
        try:
            print 'delete hybridization plan'
            raw_data = simplejson.loads(request.raw_post_data)
            plan = HybridPlan.objects.get(id=raw_data['idplan'])
            aliquots = Aliquot_has_Request.objects.filter(idHybPlan = plan)
            for al in aliquots:
                al.virtual_chip = None
                al.virtual_order = None
                al.save()
            plan.delete()
            transaction.commit()
            return {'status':'deleted'}
        except Exception, e:
            print e
            transaction.rollback()
            return HttpResponseBadRequest("Error in deleting plan")
        finally:
            transaction.rollback()

class GetLink(BaseHandler):
    allowed_methods = ('GET')
    @method_decorator(get_functionality_decorator)
    def read (self, request, link, typeO):
        print link, typeO
        resp = getLink(link, typeO)
        return resp

class GetSample(BaseHandler):
    allowed_methods = ('GET')
    @method_decorator(get_functionality_decorator)
    def read (self, request, genid):
        try:
            print genid
            resp = getUarrayNodeData([str(genid)])
            print {'samples':resp}
            return {'samples':resp}
        except Exception, e:
            print e
            return {'response': 'Bad request'}

class ReadSamples(BaseHandler):
    allowed_methods = ('POST')
    @method_decorator(get_functionality_decorator)
    def create(self, request):
        print request.POST
        try:
            resp = {}
            f = request.FILES['file']
            alList = []
            for line in f:
                alList.append(line.strip())
            samples = getUarrayNodeData(alList)
            print samples
            filename = str(f).split(".")[0]
            resp['samples'] = samples
            return resp
        except Exception, e:
            print e
            return {'response':'Bad request'}
