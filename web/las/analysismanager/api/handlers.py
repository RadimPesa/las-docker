from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import loader, Context, RequestContext
from piston.handler import BaseHandler
from mining.models import *
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
from django.db.models import Count

import sympy
from sympy import *
from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application

import algo.randomizeGroup as randomizeGroup


class ComputeFormula(BaseHandler):
    allowed_methods = ('POST')
    def create (self, request):
        try:
            print 'ComputeFormula'
            transformations = (standard_transformations + (implicit_multiplication_application,))
            try:
                raw_data = simplejson.loads(request.raw_post_data)
                print raw_data
                computation_list  = raw_data['computationList']
            except:
                computation_list = []
            print computation_list
            results = {}
            for idFormula, comps in computation_list.items():
                formula = Formula.objects.get(id=idFormula)
                variables = Element.objects.filter(pk__in=FormulaHasElement.objects.filter(formula_id=idFormula).values('element_id')).order_by('id')
                symbolsDict = dict.fromkeys([str(v.id) for v in variables], None)
                symbols_string = ' '.join([v.alias for v in variables])
                print symbols_string
                symbols = sympy.symbols(symbols_string)
                i = 0
                for v in variables:
                    symbolsDict[str(v.id)] = symbols[i]
                    i+=1
                print symbolsDict

                expression = parse_expr(formula.expression, transformations=transformations)
                res = []
                for singlecomp in comps:
                    subs = {}
                    try:
                        for key, obj in symbolsDict.items():
                            subs[obj] = float(singlecomp[key])
                    except:
                        res.append('NA')
                        continue
                    print subs
                    res.append( expression.evalf(subs=subs) )
                    print res
                results[idFormula] = res
            print results
            return results
        except Exception, e:
            print e
            return {'status': 'Error', 'description': 'Error in retrieving data'}

class GetFormulas(BaseHandler):
    allowed_methods = ('GET')
    def read (self, request):
        try:
            print 'get Formulas'
            try:
                element_list  = json.loads(request.GET['elementList'])
            except :
                element_list = []
            if len(element_list)==0:
                return {'status': 'Error', 'description': 'Bad syntax'}
            formulas = Formula.objects.exclude(pk__in=FormulaHasElement.objects.exclude(element_id__in=Element.objects.filter(pk__in=element_list)).values('formula_id'))
            print formulas
            resp = [{'formulaid':f.id, 'expression':f.expression} for f in formulas]

            return resp
        except Exception, e:
            print e
            return {'status': 'Error', 'description': 'Error in retrieving data'}

class GetFormulaByIds(BaseHandler):
    allowed_methods = ('GET')
    def read (self, request):
        try:
            print 'GetFormulaByIds'
            try:
                formula_list  = json.loads(request.GET['formulaList'])
            except :
                formula_list = []
            if len(formula_list)==0:
                return {'status': 'Error', 'description': 'Bad syntax'}
            formulas = Formula.objects.filter(id__in=formula_list)
            resp = {}
            for f in formulas:
                resp[f.id] = f.expression
            return resp
        except Exception, e:
            print e
            return {'status': 'Error', 'description': 'Error in retrieving formulas by ids'}

class GetFormulaName(BaseHandler):
    allowed_methods = ('GET')
    def read (self, request):
        try:
            print 'GetFormulaByIds'
            try:
                formula_list  = json.loads(request.GET['formulaList'])
            except :
                formula_list = []
            if len(formula_list)==0:
                return {'status': 'Error', 'description': 'Bad syntax'}
            formulas = Formula.objects.filter(id__in=formula_list)
            resp = {}
            for f in formulas:
                resp[f.id] = f.name
            return resp
        except Exception, e:
            print e
            return {'status': 'Error', 'description': 'Error in retrieving formulas by ids'}


class ReadRandomize(BaseHandler):
    allowed_methods = ('POST')
    def create(self, request):
        print request.POST
        try:
            resp = {}
            print request.FILES['file']
            f = request.FILES['file']
            elems = []
            idsEl = {}
            for line in f:
                tokens = line.strip().split()
                if len(tokens) == 0:
                    continue
                if len(tokens) != 2:
                    raise Exception('File format error. Only two fields are required (identifier and value).')
                tokens[1] = tokens[1].replace(',', '.')
                k = tokens[1].rfind(".")
                tokens[1] = tokens[1][:k].replace('.', '') + tokens[1][k:]
                float(tokens[1])
                elems.append({'obj':tokens[0], 'val':tokens[1]})
                if idsEl.has_key(tokens[0]):
                    raise Exception('Not unique identifiers.')
                idsEl[tokens[0]] = tokens[1]
            print elems
            resp['elements'] = elems
            return resp
        except Exception, e:
            print e
            return {'response': e }


class RunRandomize(BaseHandler):
    allowed_methods = ('POST')
    def create (self, request):
        try:
            postdata = simplejson.loads(request.raw_post_data)
            print postdata
            resp = randomizeGroup.randomizeGroups(postdata['data'], postdata['th'], postdata['minr'], postdata['maxr'] , postdata['minavg'], postdata['maxavg'], postdata['ngroups'], postdata['nel'], postdata['optrun'])
            print resp
            if len(resp) == 0:
                raise Exception("Impossible to randomize elements. Please check the parameters before re-run the process.")
            return resp
        except Exception, e:
            print e
            return {'response':str(e)}
