from piston.handler import BaseHandler
from xenopatients.models import *
from django.core import serializers
from django.db import models
from django.http import HttpResponse
from django.db.models import Q
import string
import operator
from datetime import date, timedelta, datetime
from api.utils import *
from xenopatients.utils import *
from xenopatients.genealogyID import *

#restituisce tutte i gruppi presenti nel database
class ExGroupList(BaseHandler):
    allowed_methods = ('GET')
    def read(self, request):
        try:
            print request.GET
            if 'q' in request.GET:
                groups = Groups.objects.filter(name__icontains = request.GET.get('q'))[:10]
                res = []
                for g in groups:
                    if g.name not in res:
                        res.append(g.name)
                return res
            return " "
        except Exception, e:
            print e
            print "error groups autocomplete"

#restituisce tutte i gruppi presenti nel database
class CancGroupList(BaseHandler):
    allowed_methods = ('GET')
    def read(self, request):
        try:
            print request.GET
            if 'q' in request.GET:
                groups = Cancer_research_group.objects.filter(name__icontains = request.GET.get('q'))[:10]
                res = []
                for g in groups:
                    if g.name not in res:
                        res.append(g.name)
                return res
            return " "
        except Exception, e:
            print e
            print "error canc groups autocomplete"
            
#restituisce tutte i gruppi presenti nel database
class ArmNameList(BaseHandler):
    allowed_methods = ('GET')
    def read(self, request):
        try:
            print request.GET
            if 'q' in request.GET:
                arms = Arms.objects.filter(name__icontains = request.GET.get('q'))[:10]
                res = []
                for a in arms:
                    if a.name not in res:
                        res.append(a.name)
                return res
            return " "
        except Exception, e:
            print e
            print "error arms autocomplete"

#restituisce tutte i protocolli presenti nel database
class ProtocolList(BaseHandler):
    allowed_methods = ('GET')
    def read(self, request):
        try:
            list = []
            values = Protocols.objects.values()
            for v in values:
                list.append(v['name'])
            return {'Name': list}
        except Exception, e:
            print e
            return {"Name":'errore'}

#restituisce tutte i protocolli presenti nel database
class ProtocolList2(BaseHandler):
    allowed_methods = ('GET')
    def read(self, request):
        try:
            list = []
            values = Protocols.objects.values()
            for v in values:
                list.append(v['name'])
            return {'Protocol': list}
        except Exception, e:
            print e
            return {"Protocol":'errore'}

#restituisce tutte gli username degli operatori presenti nel database
class OperatorList(BaseHandler):
    allowed_methods = ('GET')
    def read(self, request):
        try:
            list = []
            values = User.objects.values()
            for v in values:
                list.append(v['username'])
            return {'Operator': list}
        except Exception, e:
            print e
            return {"Operator":'errore'}

#restituisce tutte le razze presenti nel database
class StrainList(BaseHandler):
    allowed_methods = ('GET')
    def read(self, request):
        try:
            list = []
            values = Mouse_strain.objects.values()
            for v in values:
                list.append(v['mouse_type_name'])
            return {'Strain': list}
        except Exception, e:
            print e
            return {"Strain":'errore'}

#restituisce tutti i fornitori presenti nel database
class SourceList(BaseHandler):
    allowed_methods = ('GET')
    def read(self, request):
        try:
            list = []
            values = Source.objects.values()
            for v in values:
                list.append(v['name'])
            return {'Supplier': list}
        except Exception, e:
            print e
            return {"Supplier":'errore'}
            
#restituisce tutti gli status presenti nel database
class StatusList(BaseHandler):
    allowed_methods = ('GET')
    def read(self, request):
        try:
            list = []
            values = Status.objects.values()
            for v in values:
                list.append(v['name'])
            return {'Status': list}
        except Exception, e:
            print e
            return {"Status":'errore'}

#restituisce tutti i lineage dei genID nel database
class LineageList(BaseHandler):
    allowed_methods = ('GET')
    def read(self, request):
        try:
            dictL = {}
            values = Mice.objects.values()
            for v in values:
                if v['id_genealogy'] > 0:
                    classGen = GenealogyID(v['id_genealogy'])
                    lineage = classGen.getLineage()
                    #print lineage
                    dictL.update({lineage:lineage})
                    #da testare con piu' dati
            return {'Lineage': dictL}
        except Exception, e:
            print e
            return {"Lineage":'errore'}
            
#restituisce tutti i siti per gli impianti presenti nel database
class SiteList(BaseHandler):
    allowed_methods = ('GET')
    def read(self, request):
        try:
            list = []
            values = Site.objects.values()
            for v in values:
                list.append(v['longName'])
            return {'Site': list}
        except Exception, e:
            print e
            return {"Site":'errore'}

#restituisce tutti gli scopi presenti nel database
class ScopeList(BaseHandler):
    allowed_methods = ('GET')
    def read(self, request):
        try:
            list = []
            values = Scope_details.objects.values()
            for v in values:
                list.append(v['description'])
            return {'Scope': list}
        except Exception, e:
            print e
            return {"Scope":'errore'}

#restituisce tutti i valori qualitativi presenti nel database
class ValueList(BaseHandler):
    allowed_methods = ('GET')
    def read(self, request):
        try:
            list = []
            values = Qualitative_values.objects.values()
            for v in values:
                list.append(v['value'])
            return {'Value': list}
        except Exception, e:
            print e
            return {"Value":'errore'}
            
#restituisce tutti i farmaci presenti nel database
class DrugList(BaseHandler):
    allowed_methods = ('GET')
    def read(self, request):
        try:
            list = []
            values = Drugs.objects.values()
            for v in values:
                list.append(v['name'])
            return {'Drug': list}
        except Exception, e:
            print e
            return {"Drug":'errore'}
