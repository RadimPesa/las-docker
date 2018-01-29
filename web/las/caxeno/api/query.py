from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import loader, Context, RequestContext
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
from django.views.decorators.csrf import csrf_exempt
import ast
from global_request_middleware import *

# api per trovare ghost mice naive
class GhostMiceNaiveH(BaseHandler):
    allowed_methods = ('POST')
    @csrf_exempt
    def create(self, request):
        disable_graph()
        try:
            startdate = request.POST['startdate']
            m = Mice.objects.filter(id_status_id=2,available_date__lte=startdate)
            res = [{'barcode': x.barcode, 'available_date': x.available_date, 'status': x.status} for x in m]
            return {'objects': res}
        except Exception as e:
            print e
            return {"code": 'err'}

#API per fornire i dati relativi ai topi
class MiceH(BaseHandler):
    allowed_methods = ('GET','POST')
    def read(self, request):
        disable_graph()
        try:
            return {'data':'ok'}
        except Exception, e:
            print e
            return {"data": 'err'}
    @csrf_exempt
    def create(self, request): 
        disable_graph()
        translate = {'Barcode':'barcode', 'Availability Date':'available_date'}
        successorDict = {'AND':'AND', 'OR':'OR', 'NOT IN':'NOT IN', 'Mice':'Mice', 'Implants':'Implants', 'Explants':'Explants', 'Qual. Measures':'Qual. Measures', 'Quant. Measures':'Quant. Measures', 'Treatment Arms':'Treatment Arms', 'Treatment Protocols':'Treatment Protocols', 'Treatments':'Treatments','Experimental Groups':'Experimental Groups'}
        try:
            print request.POST
            predecessor = request.POST['predecessor']
            successor = request.POST['successor']
            listID = request.POST['list']
            parameter = request.POST['parameter']
            values = request.POST['values'] #to split
            argument_list = []
            first = True
            if predecessor == 'start':
                if values == "":
                    query = BioMice.objects.all()
                else:
                    if parameter == 'Availability Date':
                        phys = Mice.objects.all()
                        if len(values.split('|')) == 1:
                            value = values.split('_')
                            if value[0] == '>':
                                phys = phys.filter(available_date__gte = value[1])
                            elif value[0] == '=':
                                phys = phys.filter(available_date = value[1])
                            elif value[0] == '<':
                                phys = phys.filter(available_date__lte = value[1])
                        else:
                            for v in values.split('|'):
                                value = v.split('_')
                                if value[0] == '>':
                                    phys = phys.filter(available_date__gte = value[1])
                                elif value[0] == '=':
                                    phys = query.filter(available_date = value[1])
                                elif value[0] == '<':
                                    phys = phys.filter(available_date__lte = value[1])
                        option = "phys_mouse_id"
                        argument_list = []
                        for p in phys:
                            argument_list.append( Q(**{option: p} ))
                        query = BioMice.objects.filter(reduce(operator.or_, argument_list))
                    elif parameter == 'Death Date':
                        phys = Mice.objects.all()
                        if len(values.split('|')) == 1:
                            value = values.split('_')
                            if value[0] == '>':
                                phys = phys.filter(death_date__gte = value[1])
                            elif value[0] == '=':
                                phys = phys.filter(death_date = value[1])
                            elif value[0] == '<':
                                phys = phys.filter(death_date__lte = value[1])
                        else:
                            for v in values.split('|'):
                                value = v.split('_')
                                if value[0] == '>':
                                    phys = phys.filter(death_date__gte = value[1])
                                elif value[0] == '=':
                                    phys = phys.filter(death_date = value[1])
                                elif value[0] == '<':
                                    phys = phys.filter(death_date__lte = value[1])
                        option = "phys_mouse_id"
                        argument_list = []
                        for p in phys:
                            argument_list.append( Q(**{option: p} ))
                        query = BioMice.objects.filter(reduce(operator.or_, argument_list))
                    elif parameter == 'Birth Date':
                        phys = Mice.objects.all()
                        if len(values.split('|')) == 1:
                            value = values.split('_')
                            if value[0] == '>':
                                phys = phys.filter(birth_date__gte = value[1])
                            elif value[0] == '=':
                                phys = phys.filter(birth_date = value[1])
                            elif value[0] == '<':
                                phys = phys.filter(birth_date__lte = value[1])
                        else:
                            for v in values.split('|'):
                                value = v.split('_')
                                if value[0] == '>':
                                    phys = phys.filter(birth_date__gte = value[1])
                                elif value[0] == '=':
                                    phys = phys.filter(birth_date = value[1])
                                elif value[0] == '<':
                                    phys = phys.filter(birth_date__lte = value[1])
                        option = "phys_mouse_id"
                        argument_list = []
                        for p in phys:
                            argument_list.append( Q(**{option: p} ))
                        query = BioMice.objects.filter(reduce(operator.or_, argument_list))
                    elif parameter == 'Lineage':
                        query = BioMice.objects.all()
                        for m in query:
                            if str(m.id_genealogy) != "None":
                                for value in values.split('|'):
                                    option = 'id_genealogy'
                                    value = str(value)
                                    if len(value) == 1:
                                        value = '0' + value
                                    classGen = GenealogyID(m.id_genealogy)
                                    lineage = classGen.getLineage()
                                    if lineage == value:
                                        argument_list.append( Q(id_genealogy__icontains = value ))
                        query = BioMice.objects.filter(reduce(operator.or_, argument_list))
                    elif parameter == 'Cancer Research Group':
                        for v in values.split('|'):
                            argument_list.append( Q(id_cancer_research_group = Cancer_research_group.objects.get(name = v) ))
                        query = Mice.objects.filter(reduce(operator.or_, argument_list))
                    elif parameter == 'Experimental Group':
                        for v in values.split('|'):
                            argument_list.append( Q(id_group = Groups.objects.get(name = v) ))
                        query = BioMice.objects.filter(reduce(operator.or_, argument_list))
                    elif parameter == 'Passage':
                        if len(values.split('|')) == 1:
                            value = values.split('_')
                            if len(value[1]) == 1:
                                p = '0' + value[1]
                            else:
                                p = int(value[1])
                            query = BioMice.objects.all()
                            for m in query:
                                if str(m.id_genealogy) != "None":
                                    classGen = GenealogyID(m.id_genealogy)
                                    passage = classGen.getSamplePassagge()
                                    if value[0] == '>':
                                        if passage >= p:
                                            argument_list.append( Q(id_genealogy = m.id_genealogy ))
                                    elif value[0] == '=':
                                        if passage == p:
                                            argument_list.append( Q(id_genealogy = m.id_genealogy ))
                                    elif value[0] == '<':
                                        if passage <= p:
                                            argument_list.append( Q(id_genealogy = m.id_genealogy ))
                            query = BioMice.objects.filter(reduce(operator.or_, argument_list))
                        else:
                            v = values.split('|')
                            valueF = v[0].split('_')
                            valueT = v[1].split('_')
                            if len(valueF[1]) == 1:
                                valueF[1] = '0' + valueF[1]
                            if len(valueT[1]) == 1:
                                valueT[1] = '0' + valueT[1]
                            valueF = int(valueF[1])
                            valueT = int(valueT[1])
                            #print valueF
                            #print valueT
                            query = BioMice.objects.all()
                            for m in query:
                                if str(m.id_genealogy) != "None":
                                    classGen = GenealogyID(m.id_genealogy)
                                    passage = classGen.getSamplePassagge()
                                    #print passage
                                    if valueF <= int(passage) and valueT >= int(passage):
                                        argument_list.append( Q(id_genealogy = m.id_genealogy ))
                            #print argument_list
                            query = BioMice.objects.filter(reduce(operator.or_, argument_list))
                    else:
                        print values.split('|')
                        for value in values.split('|'):
                            if parameter in translate.keys():
                                option = translate.get(parameter)
                                argument_list.append( Q(**{option: value} ))
                            elif parameter == 'Supplier':
                                option = 'id_source'
                                v = Source.objects.get(name = value)
                                argument_list.append( Q(**{option: v} ))
                            elif parameter == 'Strain':
                                option = 'id_mouse_strain'
                                v = Mouse_strain.objects.get(mouse_type_name = value)
                                argument_list.append( Q(**{option: v} ))
                            elif parameter == 'Status':
                                option = 'id_status'
                                v = Status.objects.get(name = value)
                                argument_list.append( Q(**{option: v} ))
                        phys = Mice.objects.filter(reduce(operator.or_, argument_list))
                        option = "phys_mouse_id"
                        argument_list = []
                        for p in phys:
                            argument_list.append( Q(**{option: p} ))
                        query = BioMice.objects.filter(reduce(operator.or_, argument_list))
            else:
                if len(ast.literal_eval(listID)) > 0:
                    listID = ast.literal_eval(listID)
                    dataList = []
                    filter_list = []
                    print successorDict.keys()
                    if predecessor in successorDict.keys():
                        listID = listID['id']
                    else:
                        listID = listID['genID']
                        print 'genID pred'
                        filter_list = []
                        if predecessor == "Genealogy ID":
                            for l in listID:
                                filter_list.append( Q(id_genealogy = l))
                            dataList = BioMice.objects.filter(reduce(operator.or_, filter_list))
                        elif predecessor == "Genealogy ID_":
                            allMice = BioMice.objects.all()
                            for m in allMice:
                                if str(m.id_genealogy) != "None":
                                    for l in listID:
                                        #print l
                                        classGen = GenealogyID(l)
                                        if classGen.compareGenIDs(GenealogyID(m.id_genealogy)):
                                            filter_list.append( Q(id_genealogy = m.id_genealogy))
                            dataList = BioMice.objects.filter(reduce(operator.or_, filter_list))
                        else:
                            for l in listID:
                                filter_list.append( Q(id_genealogy__startswith = l[0:9] ))
                            dataList = BioMice.objects.filter(reduce(operator.or_, filter_list))
                    if predecessor == 'Mice':
                        for l in listID:
                            option = 'id'
                            filter_list.append(  Q(**{option: l} ))
                        print '3'
                        dataList = BioMice.objects.filter(reduce(operator.or_, filter_list))
                        print '4'
                    elif predecessor == 'Implants':
                        if parameter == 'GROUP BY':
                            temp = []
                            for l in listID:
                                temp.append(Implant_details.objects.get(id = l).id_mouse)
                            dataList = temp
                        else:
                            for l in listID:
                                option = 'id'
                                mouseID = Implant_details.objects.get(id = l).id_mouse.id
                                filter_list.append(  Q(**{option: mouseID} ))
                            dataList = BioMice.objects.filter(reduce(operator.or_, filter_list))
                    elif predecessor == "Explants":
                        if parameter == 'GROUP BY':
                            temp = []
                            for l in listID:
                                temp.append(Explant_details.objects.get(id = l).id_mouse)
                            dataList = temp
                        else:
                            for l in listID:
                                option = 'id'
                                mouseID = Explant_details.objects.get(id = l).id_mouse.id
                                filter_list.append(  Q(**{option: mouseID} ))
                            dataList = BioMice.objects.filter(reduce(operator.or_, filter_list))
                    elif predecessor == "Qual. Measures":
                        if parameter == 'GROUP BY':
                            temp = []
                            for l in listID:
                                temp.append(Qualitative_measure.objects.get(id = l).id_mouse)
                            dataList = temp
                        else:
                            for l in listID:
                                option = 'id'
                                mouseID = Qualitative_measure.objects.get(id = l).id_mouse.id
                                filter_list.append(  Q(**{option: mouseID} ))
                            dataList = BioMice.objects.filter(reduce(operator.or_, filter_list))
                    elif predecessor == "Quant. Measures":
                        if parameter == 'GROUP BY':
                            temp = []
                            for l in listID:
                                temp.append(Quantitative_measure.objects.get(id = l).id_mouse)
                            dataList = temp
                        else:
                            for l in listID:
                                option = 'id'
                                mouseID = Quantitative_measure.objects.get(id = l).id_mouse.id
                                filter_list.append(  Q(**{option: mouseID} ))
                            dataList = BioMice.objects.filter(reduce(operator.or_, filter_list))
                    elif predecessor == "Treatment Arms":
                        print 'treat arms pred'
                        for l in listID:
                            option = 'id'
                            a = Arms.objects.get(id = l)
                            print l
                            print a
                            pha = Protocols_has_arms.objects.filter(id_arm = a)
                            print pha
                            for p in pha:
                                mouseIDs = Mice_has_arms.objects.filter(id_protocols_has_arms = p)
                                for mouseID in mouseIDs:
                                    filter_list.append(  Q(**{option: mouseID.id_mouse.id} ))
                            print filter_list
                        dataList = BioMice.objects.filter(reduce(operator.or_, filter_list))
                        print dataList
                    elif predecessor == "Treatment Protocols":
                        for l in listID:
                            option = 'id'
                            a = Protocols.objects.get(id = l)
                            pha = Protocols_has_arms.objects.filter(id_protocol = a)
                            for p in pha:
                                mouseIDs = Mice_has_arms.objects.filter(id_protocols_has_arms = p)
                                for mouseID in mouseIDs:
                                    filter_list.append(  Q(**{option: mouseID.id_mouse.id} ))
                        dataList = BioMice.objects.filter(reduce(operator.or_, filter_list))
                    elif predecessor == 'Treatments':
                        if parameter == 'GROUP BY':
                            temp = []
                            for l in listID:
                                temp.append(Mice_has_arms.objects.get(id = l).id_mouse)
                            dataList = temp
                        else:
                            for l in listID:
                                filter_list.append( Q(id = Mice_has_arms.objects.get(id = l).id_mouse.id ) )
                            dataList = BioMice.objects.filter(reduce(operator.or_, filter_list))
                    elif predecessor == 'Experimental Groups':
                        for l in listID:
                            filter_list.append( Q(id_group = Groups.objects.get(id = l).id ) )
                        dataList = BioMice.objects.filter(reduce(operator.or_, filter_list))
                    if values == "":
                        query = dataList
                    else:
                        first = True
                        physList = []
                        if parameter == 'Availability Date':
                            for d in dataList:
                                physList.append(d.phys_mouse_id)
                            if len(values.split('|')) == 1:
                                value = values.split('_')
                                if value[0] == '>':
                                    phys = physList.filter(available_date__gte = value[1])
                                elif value[0] == '=':
                                    phys = physList.filter(available_date = value[1])
                                elif value[0] == '<':
                                    phys = physList.filter(available_date__lte = value[1])
                            else:
                                phys = physList
                                for v in values.split('|'):
                                    value = v.split('_')
                                    if value[0] == '>':
                                        phys = phys.filter(available_date__gte = value[1])
                                    elif value[0] == '=':
                                        phys = phys.filter(available_date = value[1])
                                    elif value[0] == '<':
                                        phys = phys.filter(available_date__lte = value[1])
                            option = "phys_mouse_id"
                            argument_list = []
                            for p in phys:
                                argument_list.append( Q(**{option: p} ))
                            query = dataList.filter(reduce(operator.or_, argument_list))
                        elif parameter == 'Death Date':
                            if len(values.split('|')) == 1:
                                value = values.split('_')
                                if value[0] == '>':
                                    phys = physList.filter(death_date__gte = value[1])
                                elif value[0] == '=':
                                    phys = physList.filter(death_date = value[1])
                                elif value[0] == '<':
                                    phys = physList.filter(death_date__lte = value[1])
                            else:
                                phys = physList
                                for v in values.split('|'):
                                    value = v.split('_')
                                    if value[0] == '>':
                                        phys = phys.filter(death_date__gte = value[1])
                                    elif value[0] == '=':
                                        phys = phys.filter(death_date = value[1])
                                    elif value[0] == '<':
                                        phys = phys.filter(death_date__lte = value[1])
                            option = "phys_mouse_id"
                            argument_list = []
                            for p in phys:
                                argument_list.append( Q(**{option: p} ))
                            query = dataList.filter(reduce(operator.or_, argument_list))
                        elif parameter == 'Birth Date':
                            if len(values.split('|')) == 1:
                                value = values.split('_')
                                if value[0] == '>':
                                    phys = physList.filter(birth_date__gte = value[1])
                                elif value[0] == '=':
                                    phys = physList.filter(birth_date = value[1])
                                elif value[0] == '<':
                                    phys = physList.filter(birth_date__lte = value[1])
                            else:
                                phys = physList
                                for v in values.split('|'):
                                    value = v.split('_')
                                    if value[0] == '>':
                                        phys = phys.filter(birth_date__gte = value[1])
                                    elif value[0] == '=':
                                        phys = phys.filter(birth_date = value[1])
                                    elif value[0] == '<':
                                        phys = phys.filter(birth_date__lte = value[1])
                            option = "phys_mouse_id"
                            argument_list = []
                            for p in phys:
                                argument_list.append( Q(**{option: p} ))
                            query = dataList.filter(reduce(operator.or_, argument_list))
                        elif parameter == 'Cancer Research Group':
                            for v in values.split('|'):
                                argument_list.append( Q(id_cancer_research_group = Cancer_research_group.objects.get(name = v) ))

                            query = dataList.filter(reduce(operator.or_, argument_list))
                        elif parameter == 'Experimental Group':
                            print 'exp g'
                            #print dataList
                            for v in values.split('|'):
                                #print 'group name', v
                                argument_list.append( Q(id_group = Groups.objects.get(name = v) ))
                            query = dataList.filter(reduce(operator.or_, argument_list))
                        elif parameter == 'Lineage':
                            query = BioMice.objects.all()
                            for m in query:
                                if str(m.id_genealogy) != "None":
                                    for value in values.split('|'):
                                        option = 'id_genealogy'
                                        value = str(value)
                                        if len(value) == 1:
                                            value = '0' + value
                                        classGen = GenealogyID(m.id_genealogy)
                                        lineage = classGen.getLineage()
                                        if lineage == value:
                                            argument_list.append( Q(id_genealogy__icontains = value ))
                            query = dataList.filter(reduce(operator.or_, argument_list))
                        elif parameter == 'Passage':
                            print values
                            if len(values.split('|')) == 1:
                                value = values.split('_')
                                if len(value[1]) == 1:
                                    p = '0' + value[1]
                                else:
                                    p = int(value[1])
                                query = BioMice.objects.all()
                                for m in query:
                                    if str(m.id_genealogy) != "None":
                                        classGen = GenealogyID(m.id_genealogy)
                                        passage = int(classGen.getSamplePassagge())
                                        p = int(p)
                                        if value[0] == '>':
                                            if passage >= p:
                                                argument_list.append( Q(id_genealogy = m.id_genealogy ))
                                        elif value[0] == '=':
                                            if passage == p:
                                                argument_list.append( Q(id_genealogy = m.id_genealogy ))
                                        elif value[0] == '<':
                                            if passage <= p:
                                                argument_list.append( Q(id_genealogy = m.id_genealogy ))
                                query = dataList.filter(reduce(operator.or_, argument_list))
                            else:
                                #print 'aaaaaaaa'
                                v = values.split('|')
                                valueF = v[0].split('_')
                                valueT = v[1].split('_')
                                if len(valueF[1]) == 1:
                                    valueF[1] = '0' + valueF[1]
                                if len(valueT[1]) == 1:
                                    valueT[1] = '0' + valueT[1]
                                valueF = int(valueF[1])
                                valueT = int(valueT[1])
                                #print 'f'
                                #print valueF
                                #print 't'
                                #print valueT
                                query = BioMice.objects.all()
                                for m in query:
                                    if str(m.id_genealogy) != "None":
                                        classGen = GenealogyID(m.id_genealogy)
                                        passage = int(classGen.getSamplePassagge())
                                        if valueF <= passage and valueT >= passage:
                                            argument_list.append( Q(id_genealogy = m.id_genealogy ))
                                query = dataList.filter(reduce(operator.or_, argument_list))
                        else:
                            print values
                            argument_list = []
                            for value in values.split('|'):
                                print value
                                arg_list = []
                                if parameter in translate.keys():
                                    option = translate.get(parameter)
                                    argument_list.append( Q(**{option: value} ))
                                elif parameter == 'Supplier':
                                    option = 'id_source'
                                    v = Source.objects.get(name = value)
                                    arg_list.append( Q(**{option: v} ))
                                    phys = Mice.objects.all()
                                    phys = phys.filter(reduce(operator.or_, arg_list))
                                    option = "phys_mouse_id"
                                    #argument_list = []
                                    for p in phys:
                                        argument_list.append( Q(**{option: p} ))
                                elif parameter == 'Strain':
                                    option = 'id_mouse_strain'
                                    v = Mouse_strain.objects.get(mouse_type_name = value)
                                    arg_list.append( Q(**{option: v} ))
                                    phys = Mice.objects.all()
                                    phys = phys.filter(reduce(operator.or_, arg_list))
                                    option = "phys_mouse_id"
                                    #argument_list = []
                                    for p in phys:
                                        argument_list.append( Q(**{option: p} ))
                                elif parameter == 'Status':
                                    option = 'id_status'
                                    v = Status.objects.get(name = value)
                                    arg_list.append( Q(**{option: v} ))
                                    phys = Mice.objects.all()
                                    phys = phys.filter(reduce(operator.or_, arg_list))
                                    option = "phys_mouse_id"
                                    #argument_list = []
                                    for p in phys:
                                        argument_list.append( Q(**{option: p} ))
                            print '1'
                            query = dataList.filter(reduce(operator.or_, argument_list))
                            print '2'
                else:
                    return {'objects':[]}
            print query
            if successor in successorDict.keys():
                result = []
                if len(query) > 0:
                    for q in query:
                        result.append(q.id)
                    return {'id':result}
                else:
                    return{'id':[]}
            elif successor == 'End':
                result = []
                print 'END'
                print len(query)
                if len(query) > 0:
                    for q in query:
                        physmouse = q.phys_mouse_id
                        status = physmouse.id_status.name
                        avl_date = physmouse.available_date
                        elem = Simple(q, []).getAttributes()
                        elem.update({'status': status, 'available_date': avl_date, 'arrival_date':physmouse.arrival_date, 'death_date': physmouse.death_date})
                        #elem.update({'status': status, 'available_date': avl_date})
                        result.append(elem)
                    return {'objects':result}
                else:
                    return{'objects':[]}
            else:
                result = []
                if len(query) > 0:
                    for q in query:
                        if str(q.id_genealogy) != "None":
                            result.append(q.id_genealogy)
                    return {'genID':result}
                else:
                    return {'genID':[]}
        except Exception, e:
            print e
            if str(e) == 'reduce() of empty sequence with no initial value':
                if successor in successorDict.keys():
                    return{'id':[]}
                elif successor == 'End':
                    return{'objects':[]}
                else:
                    return {'genID':[]}
            else:
                return {"code": 'err'}
            
#API per fornire i dati relativi agli espianti   
class ExplantsH(BaseHandler):
    allowed_methods = ('GET','POST')
    def read(self, request):
        disable_graph()
        try:
            return {'data':'ok'}
        except Exception, e:
            print e
            return {"data": 'err'}
    @csrf_exempt
    def create(self, request):
        disable_graph()
        print request.POST
        try:
            successorDict = {'AND':'AND', 'OR':'OR', 'NOT IN':'NOT IN','Mice':'Mice', 'Implants':'Implants', 'Explants':'Explants', 'Qual. Measures':'Qual. Measures', 'Quant. Measures':'Quant. Measures', 'Treatment Arms':'Treatment Arms', 'Treatment Protocols':'Treatment Protocols'}
            #{'predecessor': 'start', 'list': '', 'parameter': 'Supplier', 'values': 'aaa|bbb', 'successor': 'End'}
            predecessor = request.POST['predecessor']
            successor = request.POST['successor']
            listID = request.POST['list']
            parameter = request.POST['parameter']
            values = request.POST['values'] #to split
            argument_list = []
            first = True
            series = Series.objects.filter(id_type = Type_of_serie.objects.get(description = 'explant'))
            if predecessor == 'start':
                if values == "":
                    query = Explant_details.objects.all()
                else:
                    filter_list = []
                    if parameter == 'Date':
                        if len(values.split('|')) == 1:
                            value = values.split('_')
                            if value[0] == '>':
                                query = series.filter(date__gte = value[1])
                            elif value[0] == '=':
                                query = series.filter(date = value[1])
                            elif value[0] == '<':
                                query = series.filter(date__lte = value[1])
                        else:
                            query = series
                            for v in values.split('|'):
                                value = v.split('_')
                                if value[0] == '>':
                                    query = query.filter(date__gte = value[1])
                                elif value[0] == '=':
                                    query = query.filter(date = value[1])
                                elif value[0] == '<':
                                    query = query.filter(date__lte = value[1])
                    elif parameter == 'Operator':
                        option = 'id_operator'
                        for v in values.split('|'):
                            filter_list.append( Q(**{option: User.objects.get(username = v)} ))
                        query = series.filter(reduce(operator.or_, filter_list))
                    filter_list = []
                    for q in query:
                        option = 'id_series'
                        filter_list.append(  Q(**{option: q.id} ))
                    query = Explant_details.objects.filter(reduce(operator.or_, filter_list))
            else:
                print '0'
                print listID
                print len(ast.literal_eval(listID))
                if len(ast.literal_eval(listID)) > 0:
                    print '1'
                    listID = ast.literal_eval(listID)
                    
                    filter_list = []
                    dataList = []

                    if predecessor == 'Aliquots':
                        listID = listID['genID']
                        if parameter == 'GROUP BY':
                            temp = []
                            for l in listID:
                                a  = Aliquots.objects.get(id_genealogy = l)
                                if a.id_explant:
                                    temp.append(a.id_explant)
                            dataList = temp
                        else:
                            for l in listID:
                                filter_list.append( Q(id_genealogy = l ))
                            dataList = Aliquots.objects.filter(id_explant__isnull = False)
                            dataList = dataList.filter(reduce(operator.or_, filter_list))
                            filter_list = []
                            for d in dataList:
                                filter_list.append( Q(id = d.id_explant.id ))
                            dataList = Explant_details.objects.filter(reduce(operator.or_, filter_list))
                            print '4'
                    else:                     
                        listID = listID['id']

                    if predecessor == 'Mice':
                        print 'mice'
                        for l in listID:
                            option = 'id_mouse'
                            mouseID = BioMice.objects.get(id = l)
                            filter_list.append(  Q(**{option: mouseID} ))
                        dataList = Explant_details.objects.filter(reduce(operator.or_, filter_list))
                    elif predecessor == 'Explants':
                        for l in listID:
                            option = 'id'
                            filter_list.append(  Q(**{option: l} ))
                        dataList = Explant_details.objects.filter(reduce(operator.or_, filter_list))

                    if values == "":
                        print 'vuoto'
                        query = dataList
                    else:
                        print 'no vuoto'
                        if parameter == 'Date':
                            if len(values.split('|')) == 1:
                                value = values.split('_')
                                if value[0] == '>':
                                    query = dataList.filter(id_series__date__gte = value[1])
                                elif value[0] == '=':
                                    query = dataList.filter(id_series__date = value[1])
                                elif value[0] == '<':
                                    query = dataList.filter(id_series__date__lte = value[1])
                            else:
                                query = dataList
                                for v in values.split('|'):
                                    value = v.split('_')
                                    if value[0] == '>':
                                        query = query.filter(id_series__date__gte = value[1])
                                    elif value[0] == '=':
                                        query = query.filter(id_series__date = value[1])
                                    elif value[0] == '<':
                                        query = query.filter(id_series__date__lte = value[1])
                        elif parameter == 'Operator':
                            filter_list = []
                            for v in values.split('|'):
                                filter_list.append( Q(id_series__id_operator = User.objects.get(username = v) ))
                            query = dataList.filter(reduce(operator.or_, filter_list))
                else:
                    return {'objects':[]}
            print 'successor: ',successor
            if successor in successorDict.keys():
                result = []
                if len(query) > 0:
                    for q in query:
                        result.append(q.id)
                    print 'result'
                    return {'id':result}
                else:
                    return{'id':[]}
            elif successor == 'End':
                result = []
                print 'obj'
                if len(query) > 0:
                    for q in query:
                        result.append(Simple(q, []).getAttributes())
                        result[-1].update({'date':q.id_series.date, 'operator':q.id_series.id_operator.username}) #add series info
                    return {'objects':result}
                else:
                    return{'objects':[]}
            else:
                result = []
                print 'genid'
                if len(query) > 0:
                    filter_list = []
                    for q in query:
                        filter_list.append( Q(id_explant = q ))
                    query = Aliquots.objects.filter(reduce(operator.or_, filter_list))
                    for q in query:
                        if str(q.id_genealogy) != "None":
                            result.append(q.id_genealogy)
                    return {'genID':result}
                else:
                    return {'genID':[]}
                return {'genID':result}
        except Exception, e:
            print e
            if str(e) == 'reduce() of empty sequence with no initial value':
                if successor in successorDict.keys():
                    return{'id':[]}
                elif successor == 'End':
                    return{'objects':[]}
                else:
                    return {'genID':[]}
            return {"code": 'err'}
            
#API per fornire i dati relativi ai bracci
class ArmH(BaseHandler):
    allowed_methods = ('GET','POST')
    def read(self, request):
        disable_graph()
        try:
            return {'data':'ok'}
        except Exception, e:
            print e
            return {"data": 'err'}
    @csrf_exempt
    def create(self, request):
        disable_graph()
        try:
            filter_list = []
            successorDict = {'AND':'AND', 'OR':'OR', 'NOT IN':'NOT IN','Mice':'Mice', 'Implants':'Implants', 'Explants':'Explants', 'Qual. Measures':'Qual. Measures', 'Quant. Measures':'Quant. Measures', 'Treatment Arms':'Treatment Arms', 'Treatment Protocols':'Treatment Protocols'}
            predecessor = request.POST['predecessor']
            successor = request.POST['successor']
            listID = request.POST['list']
            parameter = request.POST['parameter']
            values = request.POST['values'] #to split
            argument_list = []
            if predecessor == 'start':
                if values == "":
                    query = Arms.objects.all()
                else:
                    if parameter == 'Name':
                        for v in values.split('|'):
                            filter_list.append( Q(name = v ))
                        query = Arms.objects.filter(reduce(operator.or_, filter_list))
                    elif parameter == 'Drug':
                        for v in values.split('|'):
                            filter_list.append( Q(name = v ))
                        query = Drugs.objects.filter(reduce(operator.or_, filter_list))
                        filter_list = []
                        for q in query:
                            filter_list.append( Q(drugs_id = q.id ))
                        query = Details_arms.objects.filter(reduce(operator.or_, filter_list))
                        filter_list = []
                        for q in query:
                            filter_list.append( Q(id = q.arms_id.id ))
                        query = Arms.objects.filter(reduce(operator.or_, filter_list))           
            else:
                if len(ast.literal_eval(listID)) > 0:
                    listID = ast.literal_eval(listID)
                    listID = listID['id']
                    dataList = []
                    filter_list = []
                    if predecessor == 'Treatment Arms':
                        for l in listID:
                            filter_list.append( Q(id = l ))
                        dataList = Arms.objects.filter(reduce(operator.or_, filter_list))
                    elif predecessor == 'Treatment Protocols':
                        for l in listID:
                            filter_list.append( Q(id_protocol = Protocols.objects.get(id = l) ))
                        dataList = Protocols_has_arms.objects.filter(reduce(operator.or_, filter_list))
                        print len(dataList)
                        filter_list = []
                        for d in dataList:
                            filter_list.append( Q(id = d.id_arm.id ))
                        dataList = Arms.objects.filter(reduce(operator.or_, filter_list))
                        print len(dataList)
                        filter_list = []
                    elif predecessor == 'Mice':
                        if parameter == 'GROUP BY':
                            temp = []
                            for l in listID:
                                for mha in Mice_has_arms.objects.filter(id_mouse = BioMice.objects.get(id = l)):
                                    temp.append(mha.id_protocols_has_arms.id_arm)
                            dataList = temp
                        else:
                            for l in listID:
                                filter_list.append( Q(id_mouse = BioMice.objects.get(id = l) ))
                            dataList = Mice_has_arms.objects.filter(reduce(operator.or_, filter_list))
                            filter_list = []
                            if len(dataList) > 0:
                                for d in dataList:
                                    filter_list.append( Q(id = d.id_protocols_has_arms.id_arm.id ))
                                dataList = Arms.objects.filter(reduce(operator.or_, filter_list))
                    if values == "":
                        query = dataList
                    else:
                        filter_list = []
                        if parameter == 'Name':
                            for v in values.split('|'):
                                filter_list.append( Q(name = v ))
                            query = dataList.filter(reduce(operator.or_, filter_list))
                        elif parameter == 'Drug':
                            for v in values.split('|'):
                                filter_list.append( Q(name = v ))
                            query = Drugs.objects.filter(reduce(operator.or_, filter_list))
                            filter_list = []
                            for q in query:
                                filter_list.append( Q(drugs_id = q.id ))
                            query = Details_arms.objects.filter(reduce(operator.or_, filter_list))
                            filter_list = []
                            for q in query:
                                filter_list.append( Q(id = q.arms_id.id ))
                            query = dataList.filter(reduce(operator.or_, filter_list))   
                else:
                    return {'objects':[]}  
            if successor in successorDict.keys():
                result = []
                if len(query) > 0:
                    for q in query:
                        result.append(q.id)
                    return {'id':result}
                else:
                    return{'id':[]}
            elif successor == 'End':
                result = []
                if len(query) > 0:
                    for q in query:
                        result.append(Simple(q, []).getAttributes())
                    return {'objects':result}
                else:
                    return{'objects':[]}

        except Exception, e:
            print e
            if str(e) == 'reduce() of empty sequence with no initial value':
                if successor in successorDict.keys():
                    return{'id':[]}
                elif successor == 'End':
                    return{'objects':[]}
                else:
                    return {'genID':[]}
            return {"code": 'err'}
            
#API per fornire i dati relativi ai protocolli
class ProtocolH(BaseHandler):
    allowed_methods = ('GET','POST')
    def read(self, request):
        disable_graph()
        try:
            return {'data':'ok'}
        except Exception, e:
            print e
            return {"data": 'err'}
    @csrf_exempt
    def create(self, request):
        disable_graph()
        try:
            filter_list = []
            successorDict = {'AND':'AND', 'OR':'OR', 'NOT IN':'NOT IN','Mice':'Mice', 'Implants':'Implants', 'Explants':'Explants', 'Qual. Measures':'Qual. Measures', 'Quant. Measures':'Quant. Measures', 'Treatment Arms':'Treatment Arms', 'Treatment Protocols':'Treatment Protocols'}
            predecessor = request.POST['predecessor']
            successor = request.POST['successor']
            listID = request.POST['list']
            parameter = request.POST['parameter']
            values = request.POST['values'] #to split
            argument_list = []
            if predecessor == 'start':
                if values == "":
                    query = Protocols.objects.all()
                else:
                    if parameter == 'Name':
                        for v in values.split('|'):
                            filter_list.append( Q(name = v ))
                        query = Protocols.objects.filter(reduce(operator.or_, filter_list))
                    elif parameter == 'Drug':
                        for v in values.split('|'):
                            filter_list.append( Q(name = v ))
                        query = Drugs.objects.filter(reduce(operator.or_, filter_list))
                        filter_list = []
                        for q in query:
                            filter_list.append( Q(drugs_id = q.id ))
                        query = Details_arms.objects.filter(reduce(operator.or_, filter_list))
                        filter_list = []
                        for q in query:
                            filter_list.append( Q(id_arm = q.arms_id ))
                        query = Protocols_has_arms.objects.filter(reduce(operator.or_, filter_list))
                        filter_list = []
                        for q in query:
                            filter_list.append( Q(id = q.id_protocol.id ))
                        query = Protocols.objects.filter(reduce(operator.or_, filter_list))           
            else:
                if len(ast.literal_eval(listID)) > 0:
                    listID = ast.literal_eval(listID)
                    listID = listID['id']
                    filter_list = []
                    dataList = []
                    if predecessor == 'Treatment Arms':
                        for l in listID:
                            filter_list.append( Q(id_arm = Arms.objects.get(id = l) ))
                        dataList = Protocols_has_arms.objects.filter(reduce(operator.or_, filter_list))
                        filter_list = []
                        for d in dataList:
                            filter_list.append( Q(id = d.id_protocol.id ))
                        dataList = Protocols.objects.filter(reduce(operator.or_, filter_list))
                    elif predecessor == 'Treatment Protocols':
                        if parameter == 'GROUP BY':
                            temp = []
                            for l in listID:
                                temp.append(Protocols.objects.get( id = l))
                            dataList = temp
                        else:
                            for l in listID:
                                filter_list.append( Q(id = l ))
                            dataList = Protocols.objects.filter(reduce(operator.or_, filter_list))
                    elif predecessor == 'Mice':
                        if parameter == 'GROUP BY':
                            temp = []
                            for l in listID:
                                for mha in Mice_has_arms.objects.filter(id_mouse = BioMice.objects.get(id = l)):
                                    temp.append(mha.id_protocols_has_arms.id_protocol)
                            dataList = temp
                        else:
                            for l in listID:
                                filter_list.append( Q(id_mouse = BioMice.objects.get(id = l) ))
                            dataList = Mice_has_arms.objects.filter(reduce(operator.or_, filter_list))
                            filter_list = []
                            if len(dataList) > 0:
                                for d in dataList:
                                    filter_list.append( Q(id = d.id_protocols_has_arms.id_protocol.id ))
                                dataList = Protocols.objects.filter(reduce(operator.or_, filter_list))
                    if values == "":                    
                        query = dataList
                    else:
                        filter_list = []
                        if parameter == 'Name':
                            for v in values.split('|'):
                                filter_list.append( Q(name = v ))
                            query = dataList.filter(reduce(operator.or_, filter_list))
                        elif parameter == 'Drug':
                            for v in values.split('|'):
                                filter_list.append( Q(name = v ))
                            query = Drugs.objects.filter(reduce(operator.or_, filter_list))
                            filter_list = []
                            for q in query:
                                filter_list.append( Q(drugs_id = q.id ))
                            query = Details_arms.objects.filter(reduce(operator.or_, filter_list))
                            filter_list = []
                            for q in query:
                                filter_list.append( Q(id_arm = q.arms_id.id ))
                            query = Protocols_has_arms.objects.filter(reduce(operator.or_, filter_list))
                            filter_list = []
                            for d in query:
                                filter_list.append( Q(id = d.id_protocol.id ))
                            query = dataList.filter(reduce(operator.or_, filter_list))
                else:
                    return {'objects':[]}
            if successor in successorDict.keys():
                result = []
                if len(query) > 0:
                    for q in query:
                        result.append(q.id)
                    return {'id':result}
                else:
                    return{'id':[]}
            elif successor == 'End':
                result = []
                if len(query) > 0:
                    for q in query:
                        result.append(Simple(q, []).getAttributes())
                    return {'objects':result}
                else:
                    return{'objects':[]}
        except Exception, e:
            print e
            if str(e) == 'reduce() of empty sequence with no initial value':
                if successor in successorDict.keys():
                    return{'id':[]}
                elif successor == 'End':
                    return{'objects':[]}
                else:
                    return {'genID':[]}
            return {"code": 'err'}
            
class QualH(BaseHandler):
    allowed_methods = ('GET','POST')
    def read(self, request):
        disable_graph()
        try:
            return {'data':'ok'}
        except Exception, e:
            print e
            return {"data": 'err'}
    @csrf_exempt
    def create(self, request):
        disable_graph()
        try:
            print request.POST
            filter_list = []
            successorDict = {'AND':'AND', 'OR':'OR', 'NOT IN':'NOT IN','Mice':'Mice', 'Implants':'Implants', 'Explants':'Explants', 'Qual. Measures':'Qual. Measures', 'Quant. Measures':'Quant. Measures', 'Treatment Arms':'Treatment Arms', 'Treatment Protocols':'Treatment Protocols'}
            predecessor = request.POST['predecessor']
            successor = request.POST['successor']
            listID = request.POST['list']
            parameter = request.POST['parameter']
            values = request.POST['values'] #to split
            argument_list = []
            series = Measurements_series.objects.filter(id_type = Type_of_measure.objects.get(description = 'qualitative'))
            if predecessor == 'start':
                if values == "":
                    query = Qualitative_measure.objects.all()
                else:
                    if parameter == 'Date':
                        if len(values.split('|')) == 1:
                            value = values.split('_')
                            if value[0] == '>':
                                query = series.filter(date__gte = value[1])
                            elif value[0] == '=':
                                query = series.filter(date = value[1])
                            elif value[0] == '<':
                                query = series.filter(date__lte = value[1])
                        else:
                            query = series
                            for v in values.split('|'):
                                value = v.split('_')
                                if value[0] == '>':
                                    query = query.filter(date__gte = value[1])
                                elif value[0] == '=':
                                    query = query.filter(date = value[1])
                                elif value[0] == '<':
                                    query = query.filter(date__lte = value[1])
                        filter_list = []
                        for q in query:
                            filter_list.append( Q(id_series = q.id_series ))
                        query = Qualitative_measure.objects.filter(reduce(operator.or_, filter_list))
                    elif parameter == 'Operator':
                        for v in values.split('|'):
                            filter_list.append( Q(id_operator = User.objects.get(username = v) ))
                        query = series.filter(reduce(operator.or_, filter_list))
                        filter_list = []
                        for q in query:
                            filter_list.append( Q(id_series = q.id_series ))
                        query = Qualitative_measure.objects.filter(reduce(operator.or_, filter_list))

                    elif parameter == 'Value':
                        print 'value process'
                        for v in values.split('|'):
                            filter_list.append( Q(id_value = Qualitative_values.objects.get(value = v) ))
                        query = Qualitative_measure.objects.filter(reduce(operator.or_, filter_list))
            else:
                if len(ast.literal_eval(listID)) > 0:
                    filter_list = []
                    listID = ast.literal_eval(listID)
                    listID = listID['id']
                    if predecessor == 'Mice':
                        print 'mouse'
                        for l in listID:
                            filter_list.append( Q(id_mouse = BioMice.objects.get(id = l) ))
                        dataList = Qualitative_measure.objects.filter(reduce(operator.or_, filter_list))
                        print dataList
                        print len(dataList)
                    elif predecessor == 'Qual. Measures':
                        for l in listID:
                            filter_list.append( Q(id = l ))
                        dataList = Qualitative_measure.objects.filter(reduce(operator.or_, filter_list))
                    if values == "":                    
                        query = dataList
                    else:
                        filter_list = []
                        if parameter == 'Date':
                            if len(values.split('|')) == 1:
                                value = values.split('_')
                                if value[0] == '>':
                                    query = dataList.filter(id_series__date__gte = value[1])
                                elif value[0] == '=':
                                    query = dataList.filter(id_series__date = value[1])
                                elif value[0] == '<':
                                    query = dataList.filter(id_series__date__lte = value[1])
                            else:
                                query = dataList
                                for v in values.split('|'):
                                    value = v.split('_')
                                    if value[0] == '>':
                                        query = query.filter(id_series__date__gte = value[1])
                                    elif value[0] == '=':
                                        query = query.filter(id_series__date = value[1])
                                    elif value[0] == '<':
                                        query = query.filter(id_series__date__lte = value[1])
                        elif parameter == 'Operator':
                            for v in values.split('|'):
                                filter_list.append( Q(id_series__id_operator = User.objects.get(username = v) ))
                            query = dataList.filter(reduce(operator.or_, filter_list))
                        elif parameter == 'Value':
                            print 'value'
                            for v in values.split('|'):
                                print v
                                filter_list.append( Q(id_value = Qualitative_values.objects.get(value = v) ))                        
                            print len(filter_list)
                            query = dataList.filter(reduce(operator.or_, filter_list))
                            print len(query)
                else:
                    return {'objects':[]}
            if successor in successorDict.keys():
                result = []
                if len(query) > 0:
                    for q in query:
                        result.append(q.id)
                    return {'id':result}
                else:
                    return{'id':[]}
            elif successor == 'End':
                result = []
                if len(query) > 0:
                    for q in query:
                        result.append(Simple(q, []).getAttributes())
                        result[-1].update({'date':q.id_series.date, 'operator':q.id_series.id_operator.username}) #add series info
                    return {'objects':result}
                else:
                    return{'objects':[]}
        except Exception, e:
            print e
            if str(e) == 'reduce() of empty sequence with no initial value':
                if successor in successorDict.keys():
                    return{'id':[]}
                elif successor == 'End':
                    return{'objects':[]}
                else:
                    return {'genID':[]}
            return {"code": 'err'}

class QuantH(BaseHandler):
    allowed_methods = ('GET','POST')
    def read(self, request):
        disable_graph()
        try:
            return {'data':'ok'}
        except Exception, e:
            print e
    @csrf_exempt
    def create(self, request):
        disable_graph()
        try:
            filter_list = []
            successorDict = {'AND':'AND', 'OR':'OR', 'NOT IN':'NOT IN','Mice':'Mice', 'Implants':'Implants', 'Explants':'Explants', 'Qual. Measures':'Qual. Measures', 'Quant. Measures':'Quant. Measures', 'Treatment Arms':'Treatment Arms', 'Treatment Protocols':'Treatment Protocols'}
            predecessor = request.POST['predecessor']
            successor = request.POST['successor']
            listID = request.POST['list']
            parameter = request.POST['parameter']
            values = request.POST['values'] #to split
            argument_list = []
            series = Measurements_series.objects.filter(id_type = Type_of_measure.objects.get(description = 'quantitative'))
            if predecessor == 'start':
                if values == "":
                    query = Quantitative_measure.objects.all()
                else:
                    if parameter == 'Date':
                        if len(values.split('|')) == 1:
                            value = values.split('_')
                            if value[0] == '>':
                                query = series.filter(date__gte = value[1])
                            elif value[0] == '=':
                                query = series.filter(date = value[1])
                            elif value[0] == '<':
                                query = series.filter(date__lte = value[1])
                        else:
                            query = series
                            for v in values.split('|'):
                                value = v.split('_')
                                if value[0] == '>':
                                    query = query.filter(date__gte = value[1])
                                elif value[0] == '=':
                                    query = query.filter(date = value[1])
                                elif value[0] == '<':
                                    query = query.filter(date__lte = value[1])
                        filter_list = []
                        for q in query:
                            filter_list.append( Q(id_series = q.id_series ))
                        query = Quantitative_measure.objects.filter(reduce(operator.or_, filter_list))
                    elif parameter == 'Operator':
                        for v in values.split('|'):
                            filter_list.append( Q(id_operator = User.objects.get(username = v) ))
                        query = series.filter(reduce(operator.or_, filter_list))
                        filter_list = []
                        for q in query:
                            filter_list.append( Q(id_series = q.id_series ))
                        query = Quantitative_measure.objects.filter(reduce(operator.or_, filter_list))
                    elif parameter == 'Volume (mm3)':
                        print values
                        for v in values.split('|'):
                            print 'vvvvvS',v
                            threshold = v.split('_')
                            print threshold[0]
                            print threshold[1]                            
                            if threshold[0] == '=':
                                filter_list.append( Q(volume = threshold[1] ))
                            elif threshold[0] == '>':
                                filter_list.append( Q(volume__gte = threshold[1] ))
                            elif threshold[0] == '<':
                                filter_list.append( Q(volume__lte = threshold[1] ))
                        print filter_list
                        query = Quantitative_measure.objects.filter(reduce(operator.and_, filter_list))
            else:
                if len(ast.literal_eval(listID)) > 0:
                    listID = ast.literal_eval(listID)
                    listID = listID['id']
                    filter_list = []
                    if predecessor == 'Mice':
                        for l in listID:
                            filter_list.append( Q(id_mouse = BioMice.objects.get(id = l) ))
                        dataList = Quantitative_measure.objects.filter(reduce(operator.or_, filter_list))
                    elif predecessor == 'Quant. Measures':
                        for l in listID:
                            filter_list.append( Q(id = l ))
                        dataList = Quantitative_measure.objects.filter(reduce(operator.or_, filter_list))
                    if values == "":                    
                        query = dataList
                    else:
                        if parameter == 'Date':
                            if len(values.split('|')) == 1:
                                value = values.split('_')
                                if value[0] == '>':
                                    query = dataList.filter(id_series__date__gte = value[1])
                                elif value[0] == '=':
                                    query = dataList.filter(id_series__date = value[1])
                                elif value[0] == '<':
                                    query = dataList.filter(id_series__date__lte = value[1])
                            else:
                                query = dataList
                                for v in values.split('|'):
                                    value = v.split('_')
                                    if value[0] == '>':
                                        query = query.filter(id_series__date__gte = value[1])
                                    elif value[0] == '=':
                                        query = query.filter(id_series__date = value[1])
                                    elif value[0] == '<':
                                        query = query.filter(id_series__date__lte = value[1])
                        elif parameter == 'Operator':
                            for v in values.split('|'):
                                filter_list.append( Q(id_series__id_operator = User.objects.get(username = v) ))
                            query = dataList.filter(reduce(operator.or_, filter_list))
                        elif parameter == 'Volume (mm3)':
                            print 'vvaa'
                            for v in values.split('|'):
                                threshold = v.split('_')
                                if threshold[0] == '=':
                                    filter_list.append( Q(volume = threshold[1] ))
                                elif threshold[0] == '>':
                                    filter_list.append( Q(volume__gte = threshold[1] ))
                                elif threshold[0] == '<':
                                    filter_list.append( Q(volume__lte = threshold[1] ))
                            query = dataList.filter(reduce(operator.and_, filter_list))
                            print query
                else:
                    return {'objects':[]}
            if successor in successorDict.keys():
                result = []
                if len(query) > 0:
                    for q in query:
                        result.append(q.id)
                    return {'id':result}
                else:
                    return{'id':[]}
            elif successor == 'End':
                result = []
                if len(query) > 0:
                    for q in query:
                        result.append(Simple(q, []).getAttributes())
                        result[-1].update({'date':q.id_series.date, 'operator':q.id_series.id_operator.username}) #add series info
                    return {'objects':result}
                else:
                    return{'objects':[]}
        except Exception, e:
            print e
            if str(e) == 'reduce() of empty sequence with no initial value':
                if successor in successorDict.keys():
                    return{'id':[]}
                elif successor == 'End':
                    return{'objects':[]}
                else:
                    return {'genID':[]}
            return {"code": 'err'}

class ImplantsH(BaseHandler):
    allowed_methods = ('GET','POST')
    def read(self, request):
        disable_graph()
        try:
            return {'data':'ok'}
        except Exception, e:
            print e
            return {"data": 'err'}
    @csrf_exempt
    def create(self, request):
        disable_graph()
        try:
            filter_list = []
            print request.POST
            successorDict = {'AND':'AND', 'OR':'OR', 'NOT IN':'NOT IN','Mice':'Mice', 'Implants':'Implants', 'Explants':'Explants', 'Qual. Measures':'Qual. Measures', 'Quant. Measures':'Quant. Measures', 'Treatment Arms':'Treatment Arms', 'Treatment Protocols':'Treatment Protocols'}
            predecessor = request.POST['predecessor']
            successor = request.POST['successor']
            listID = request.POST['list']
            parameter = request.POST['parameter']
            values = request.POST['values'] #to split
            argument_list = []
            series = Series.objects.filter(id_type = Type_of_serie.objects.get(description = 'implant'))
            if predecessor == 'start':
                if values == "":
                    query = Implant_details.objects.all()
                else:
                    if parameter == 'Date':
                        if len(values.split('|')) == 1:
                            value = values.split('_')
                            if value[0] == '>':
                                query = series.filter(date__gte = value[1])
                            elif value[0] == '=':
                                query = series.filter(date = value[1])
                            elif value[0] == '<':
                                query = series.filter(date__lte = value[1])
                        else:
                            query = series
                            for v in values.split('|'):
                                value = v.split('_')
                                if value[0] == '>':
                                    query = query.filter(date__gte = value[1])
                                elif value[0] == '=':
                                    query = query.filter(date = value[1])
                                elif value[0] == '<':
                                    query = query.filter(date__lte = value[1])
                        filter_list = []
                        for q in query:
                            filter_list.append( Q(id_series = q.id ))
                        query = Implant_details.objects.filter(reduce(operator.or_, filter_list))
                    elif parameter == 'Operator':
                        for v in values.split('|'):
                            filter_list.append( Q(id_operator = User.objects.get(username = v) ))
                        query = series.filter(reduce(operator.or_, filter_list))
                        filter_list = []
                        for q in query:
                            filter_list.append( Q(id_series = q.id ))
                            query = Implant_details.objects.filter(reduce(operator.or_, filter_list))
                    elif parameter == 'Site':
                        print 'site'
                        for v in values.split('|'):
                            print v
                            print Site.objects.get(longName = v)
                            filter_list.append( Q(site = Site.objects.get(longName = v) ))
                        query = Implant_details.objects.filter(reduce(operator.or_, filter_list))
                        print len(query)
                        filter_list = []
                    elif parameter == 'Bad Quality':
                        for v in values.split('|'):
                            if v == 'Yes':
                                filter_list.append( Q( bad_quality_flag = 1 ))
                            elif v == 'No':
                                filter_list.append( Q( bad_quality_flag = 0 ))
                        query = Implant_details.objects.filter(reduce(operator.or_, filter_list))                    
                    elif parameter == 'Protocol':
                        for v in values.split('|'):
                            filter_list.append( Q( id_protocol = Protocols.objects.get(name = v) ))
                        query = series.filter(reduce(operator.or_, filter_list))
                        filter_list = []
                        for q in query:
                            filter_list.append( Q(id_series = q.id ))
                        query = Implant_details.objects.filter(reduce(operator.or_, filter_list))
            else:
                if len(ast.literal_eval(listID)) > 0:
                    listID = ast.literal_eval(listID)
                    filter_list = []
                    if predecessor == 'Aliquots':
                        listID = listID['genID']
                        for l in listID:
                            filter_list.append( Q(id_genealogy = l ))
                        dataList = Aliquots.objects.filter(reduce(operator.or_, filter_list))
                        print '---', len(dataList)
                        filter_list = []
                        for d in dataList:
                            filter_list.append( Q(aliquots_id = d ))
                        dataList = Implant_details.objects.filter(reduce(operator.or_, filter_list))
                    if predecessor == 'Collection':
                        listID = listID['genID']
                        for l in listID:
                            filter_list.append( Q(id_genealogy__startswith = l[0:6] ))
                        dataList = Aliquots.objects.filter(reduce(operator.or_, filter_list))
                        filter_list = []
                        for d in dataList:
                            filter_list.append( Q(aliquots_id = d ))
                        dataList = Implant_details.objects.filter(reduce(operator.or_, filter_list))
                    elif predecessor == 'Mice':
                        listID = listID['id']
                        for l in listID:
                            filter_list.append( Q(id = l ))
                        print filter_list
                        dataList = BioMice.objects.filter(reduce(operator.or_, filter_list))
                        filter_list = []
                        for d in dataList:
                            filter_list.append( Q(id_mouse = d ))
                        dataList = Implant_details.objects.filter(reduce(operator.or_, filter_list))
                    elif predecessor == 'Implants':
                        listID = listID['id']
                        for l in listID:
                            filter_list.append( Q(id = l ))
                        dataList = Implant_details.objects.filter(reduce(operator.or_, filter_list))
                    print dataList
                    print len(dataList)
                    if values == "":                    
                        query = dataList
                    else:
                        filter_list = []
                        print parameter
                        if parameter == 'Date':
                            if len(values.split('|')) == 1:
                                value = values.split('_')
                                if value[0] == '>':
                                    query = dataList.filter(id_series__date__gte = value[1])
                                elif value[0] == '=':
                                    query = dataList.filter(id_series__date = value[1])
                                elif value[0] == '<':
                                    query = dataList.filter(id_series__date__lte = value[1])
                            else:
                                query = dataList
                                for v in values.split('|'):
                                    value = v.split('_')
                                    if value[0] == '>':
                                        query = query.filter(id_series__date__gte = value[1])
                                    elif value[0] == '=':
                                        query = query.filter(id_series__date = value[1])
                                    elif value[0] == '<':
                                        query = query.filter(id_series__date__lte = value[1])
                            for q in query:
                                filter_list.append( Q(id_series = q.id ))
                            query = dataList.filter(reduce(operator.or_, filter_list))
                        elif parameter == 'Operator':
                            for v in values.split('|'):
                                filter_list.append( Q(id_series__id_operator = User.objects.get(username = v) ))
                            query = dataList.filter(reduce(operator.or_, filter_list))
                        elif parameter == 'Site':
                            print 'site'
                            print filter_list
                            for v in values.split('|'):
                                filter_list.append( Q(site = Site.objects.get(longName = v) ))
                            query = dataList.filter(reduce(operator.or_, filter_list))
                        elif parameter == 'Bad Quality':
                            for v in values.split('|'):
                                if v == 'Yes':
                                    filter_list.append( Q( bad_quality_flag = 1 ))
                                elif v == 'No':
                                    filter_list.append( Q( bad_quality_flag = 0 ))
                            query = dataList.filter(reduce(operator.or_, filter_list))                    
                        elif parameter == 'Protocol':
                            for v in values.split('|'):
                                filter_list.append( Q( id_series__id_protocol = Protocols.objects.get(name = v) ))
                            query = dataList.filter(reduce(operator.or_, filter_list))
                else:
                    return {'objects':[]}
            if successor in successorDict.keys():
                result = []
                if len(query) > 0:
                    for q in query:
                        result.append(q.id)
                    return {'id':result}
                else:
                    return{'id':[]}
            elif successor == 'End':
                result = []
                if len(query) > 0:
                    for q in query:
                        result.append(Simple(q, []).getAttributes())
                        result[-1].update({'date':q.id_series.date, 'operator':q.id_series.id_operator.username}) #add series info
                    return {'objects':result}
                else:
                    return{'objects':[]}
            else:
                result = []
                print 'genid'
                if len(query) > 0:
                    for q in query:
                        if str(q.aliquots_id.id_genealogy) != "":
                            result.append(q.aliquots_id.id_genealogy)
                    return {'genID':result}
                else:
                    return {'genID':[]}
                return {'genID':result}
        except Exception, e:
            print e
            if str(e) == 'reduce() of empty sequence with no initial value':
                if successor in successorDict.keys():
                    return{'id':[]}
                elif successor == 'End':
                    return{'objects':[]}
                else:
                    return {'genID':[]}
            return {"code": 'err'}
            
            
#API per fornire i dati relativi ai trattamenti (accoppiata topo - pha [protocols has arms])
class TreatmentsH(BaseHandler):
    allowed_methods = ('GET','POST')
    def read(self, request):
        disable_graph()
        try:
            return {'data':'ok'}
        except Exception, e:
            print e
            return {"data": 'err'}
    @csrf_exempt
    def create(self, request):
        disable_graph()
        try:
            filter_list = []
            successorDict = {'AND':'AND', 'OR':'OR', 'NOT IN':'NOT IN','Mice':'Mice', 'Treatments':'Treatments'}
            predecessor = request.POST['predecessor']
            successor = request.POST['successor']
            listID = request.POST['list']
            parameter = request.POST['parameter']
            values = request.POST['values'] #to split
            argument_list = []
            mha = Mice_has_arms.objects.all()
            if predecessor == 'start':
                if values == "":
                    query = mha
                else:
                    if parameter == 'Experimental Group':
                        for v in values.split('|'):
                            filter_list.append( Q(name = v ))
                        groups = Groups.objects.filter(reduce(operator.or_, filter_list))
                        filter_list = []
                        for g in groups:
                            filter_list.append( Q(id_group = g.id) )
                        mice = BioMice.objects.filter(reduce(operator.or_, filter_list))
                        filter_list = []
                        for m in mice:
                            filter_list.append( Q(id_mouse = m.id) )
                        query = mha.objects.filter(reduce(operator.or_, filter_list))
                    elif parameter == 'Operator':
                        option = 'id_operator'
                        for v in values.split('|'):
                            filter_list.append( Q(id_operator =  User.objects.get(username = v)) )
                        query = mha.filter(reduce(operator.or_, filter_list))
                    elif parameter == 'Start Date':
                        if len(values.split('|')) == 1:
                            value = values.split('_')
                            if value[0] == '>':
                                query = mha.filter(start_date__gte = value[1])
                            elif value[0] == '=':
                                query = mha.filter(start_date = value[1])
                            elif value[0] == '<':
                                query = mha.filter(start_date__lte = value[1])
                        else:
                            query = mha
                            for v in values.split('|'):
                                value = v.split('_')
                                if value[0] == '>':
                                    query = query.filter(start_date__gte = value[1])
                                elif value[0] == '=':
                                    query = query.filter(start_date = value[1])
                                elif value[0] == '<':
                                    query = query.filter(start_date__lte = value[1])
                    elif parameter == 'End Date':
                        if len(values.split('|')) == 1:
                            value = values.split('_')
                            if value[0] == '>':
                                query = mha.filter(expected_end_date__gte = value[1])
                            elif value[0] == '=':
                                query = mha.filter(expected_end_date = value[1])
                            elif value[0] == '<':
                                query = mha.filter(expected_end_date__lte = value[1])
                        else:
                            query = mha
                            for v in values.split('|'):
                                value = v.split('_')
                                if value[0] == '>':
                                    query = query.filter(expected_end_date__gte = value[1])
                                elif value[0] == '=':
                                    query = query.filter(expected_end_date = value[1])
                                elif value[0] == '<':
                                    query = query.filter(expected_end_date__lte = value[1])
                    elif parameter == 'Expected End Date':
                        query = mha
                        if len(values.split('|')) == 1:
                            value = values.split('_')
                            if value[0] == '>':
                                query = mha.filter(end_date__gte = value[1])
                            elif value[0] == '=':
                                query = mha.filter(end_date = value[1])
                            elif value[0] == '<':
                                query = mha.filter(end_date__lte = value[1])
                        else:
                            query = mha
                            for v in values.split('|'):
                                value = v.split('_')
                                if value[0] == '>':
                                    query = query.filter(end_date__gte = value[1])
                                elif value[0] == '=':
                                    query = query.filter(end_date = value[1])
                                elif value[0] == '<':
                                    query = query.filter(end_date__lte = value[1])
            else:
                if len(ast.literal_eval(listID)) > 0:
                    listID = ast.literal_eval(listID)
                    listID = listID['id']
                    dataList = []
                    filter_list = []
                    if predecessor == 'Treatments':
                        for l in listID:
                            filter_list.append( Q(id = l ))
                        dataList = Mice_has_arms.objects.filter(reduce(operator.or_, filter_list))
                    elif predecessor == 'Mice':
                        for l in listID:
                            filter_list.append( Q(id_mouse = BioMice.objects.get(id = l) ))
                        dataList = Mice_has_arms.objects.filter(reduce(operator.or_, filter_list))
                    if values == "":
                        query = dataList
                    else:
                        filter_list = []
                        if parameter == 'Experimental Group':
                            for v in values.split('|'):
                                filter_list.append( Q(name = v ))
                            groups = Groups.objects.filter(reduce(operator.or_, filter_list))
                            filter_list = []
                            for g in groups:
                                filter_list.append( Q(id_group = g.id) )
                            mice = BioMice.objects.filter(reduce(operator.or_, filter_list))
                            filter_list = []
                            for m in mice:
                                filter_list.append( Q(id_mouse = m.id) )
                            query = dataList.objects.filter(reduce(operator.or_, filter_list))
                        elif parameter == 'Operator':
                            option = 'id_operator'
                            for v in values.split('|'):
                                filter_list.append( Q(id_operator =  User.objects.get(username = v)) )
                            query = dataList.filter(reduce(operator.or_, filter_list))
                        elif parameter == 'Start Date':
                            if len(values.split('|')) == 1:
                                value = values.split('_')
                                if value[0] == '>':
                                    query = dataList.filter(start_date__gte = value[1])
                                elif value[0] == '=':
                                    query = dataList.filter(start_date = value[1])
                                elif value[0] == '<':
                                    query = dataList.filter(start_date__lte = value[1])
                            else:
                                query = dataList
                                for v in values.split('|'):
                                    value = v.split('_')
                                    if value[0] == '>':
                                        query = query.filter(start_date__gte = value[1])
                                    elif value[0] == '=':
                                        query = query.filter(start_date = value[1])
                                    elif value[0] == '<':
                                        query = query.filter(start_date__lte = value[1])
                        elif parameter == 'End Date':
                            if len(values.split('|')) == 1:
                                value = values.split('_')
                                if value[0] == '>':
                                    query = dataList.filter(expected_end_date__gte = value[1])
                                elif value[0] == '=':
                                    query = dataList.filter(expected_end_date = value[1])
                                elif value[0] == '<':
                                    query = dataList.filter(expected_end_date__lte = value[1])
                            else:   
                                query = dataList
                                for v in values.split('|'):
                                    value = v.split('_')
                                    if value[0] == '>':
                                        query = query.filter(expected_end_date__gte = value[1])
                                    elif value[0] == '=':
                                        query = query.filter(expected_end_date = value[1])
                                    elif value[0] == '<':
                                        query = query.filter(expected_end_date__lte = value[1])
                        elif parameter == 'Expected End Date':
                            if len(values.split('|')) == 1:
                                value = values.split('_')
                                if value[0] == '>':
                                    query = dataList.filter(end_date__gte = value[1])
                                elif value[0] == '=':
                                    query = dataList.filter(end_date = value[1])
                                elif value[0] == '<':
                                    query = dataList.filter(end_date__lte = value[1])
                            else:
                                query = dataList
                                for v in values.split('|'):
                                    value = v.split('_')
                                    if value[0] == '>':
                                        query = query.filter(end_date__gte = value[1])
                                    elif value[0] == '=':
                                        query = query.filter(end_date = value[1])
                                    elif value[0] == '<':
                                        query = query.filter(end_date__lte = value[1])
                else:
                    return {'objects':[]}

            if successor in successorDict.keys():
                result = []
                if len(query) > 0:
                    for q in query:
                        result.append(q.id)
                    return {'id':result}
                else:
                    return{'id':[]}
            elif successor == 'End':
                result = []
                if len(query) > 0:
                    for q in query:
                        data = Simple(q, ['id', 'id_mouse', 'id_protocols_has_arms', 'id_operator', 'start_date', 'expected_end_date', 'end_date']).getAttributes()
                        result.append(data)
                        index = result.index(data)
                        result[index].update( {'group': q.id_mouse.id_group.name} )
                    return {'objects':result}
                else:
                    return{'objects':[]}

        except Exception, e:
            print e
            if str(e) == 'reduce() of empty sequence with no initial value':
                if successor in successorDict.keys():
                    return{'id':[]}
                elif successor == 'End':
                    return{'objects':[]}
                else:
                    return {'genID':[]}
            return {"code": 'err'}
            
            
            
#API per fornire i dati relativi ai gruppi di topi
class GroupsH(BaseHandler):
    allowed_methods = ('GET','POST')
    def read(self, request):
        disable_graph()
        try:
            return {'data':'ok'}
        except Exception, e:
            print e
            return {"data": 'err'}
    @csrf_exempt
    def create(self, request):
        disable_graph()
        try:
            filter_list = []
            successorDict = {'AND':'AND', 'OR':'OR', 'NOT IN':'NOT IN','Mice':'Mice', 'Experimental Groups':'Experimental Groups'}
            predecessor = request.POST['predecessor']
            successor = request.POST['successor']
            listID = request.POST['list']
            parameter = request.POST['parameter']
            values = request.POST['values'] #to split
            argument_list = []
            groups = Groups.objects.all()
            if predecessor == 'start':
                if values == "":
                    query = groups
                else:
                    if parameter == 'Name':
                        for v in values.split('|'):
                            filter_list.append( Q(name =  v) )
                        query = groups.filter(reduce(operator.or_, filter_list))
                    elif parameter == 'Creation Date':
                        if len(values.split('|')) == 1:
                            value = values.split('_')
                            if value[0] == '>':
                                query = groups.filter(creationDate__gte = value[1])
                            elif value[0] == '=':
                                query = groups.filter(creationDate = value[1])
                            elif value[0] == '<':
                                query = groups.filter(creationDate__lte = value[1])
                        else:
                            query = groups
                            for v in values.split('|'):
                                value = v.split('_')
                                if value[0] == '>':
                                    query = query.filter(creationDate__gte = value[1])
                                elif value[0] == '=':
                                    query = query.filter(creationDate = value[1])
                                elif value[0] == '<':
                                    query = query.filter(creationDate__lte = value[1])
            else:
                if len(ast.literal_eval(listID)) > 0:
                    listID = ast.literal_eval(listID)
                    listID = listID['id']
                    dataList = []
                    filter_list = []
                    if predecessor == 'Experimental Groups':
                        for l in listID:
                            filter_list.append( Q(id = l ))
                        dataList = Groups.objects.filter(reduce(operator.or_, filter_list))
                    elif predecessor == 'Mice':
                        if parameter == 'GROUP BY':
                            temp = []
                            for l in listID:
                                m = BioMice.objects.get(id = l)
                                if m.id_group:
                                    temp.append( m.id_group )
                            dataList = temp
                        else:
                            for l in listID:
                                m = BioMice.objects.get(id = l)
                                if m.id_group:
                                    filter_list.append( Q(id = m.id_group.id ))
                            dataList = Groups.objects.filter(reduce(operator.or_, filter_list))
                    if values == "":
                        query = dataList
                    else:
                        filter_list = []
                        if parameter == 'Name':
                            for v in values.split('|'):
                                filter_list.append( Q(name =  v) )
                            query = dataList.filter(reduce(operator.or_, filter_list))
                        elif parameter == 'Creation Date':
                            if len(values.split('|')) == 1:
                                value = values.split('_')
                                if value[0] == '>':
                                    query = dataList.filter(creationDate__gte = value[1])
                                elif value[0] == '=':
                                    query = dataList.filter(creationDate = value[1])
                                elif value[0] == '<':
                                    query = dataList.filter(creationDate__lte = value[1])
                            else:
                                query = dataList
                                for v in values.split('|'):
                                    value = v.split('_')
                                    if value[0] == '>':
                                        query = query.filter(creationDate__gte = value[1])
                                    elif value[0] == '=':
                                        query = query.filter(creationDate = value[1])
                                    elif value[0] == '<':
                                        query = query.filter(creationDate__lte = value[1])
                else:
                    return {'objects':[]}

            if successor in successorDict.keys():
                result = []
                if len(query) > 0:
                    for q in query:
                        result.append(q.id)
                    return {'id':result}
                else:
                    return{'id':[]}
            elif successor == 'End':
                result = []
                if len(query) > 0:
                    for q in query:
                        data = Simple(q, []).getAttributes()
                        result.append(data)
                    return {'objects':result}
                else:
                    return{'objects':[]}

        except Exception, e:
            print e
            if str(e) == 'reduce() of empty sequence with no initial value':
                if successor in successorDict.keys():
                    return{'id':[]}
                elif successor == 'End':
                    return{'objects':[]}
                else:
                    return {'genID':[]}
            return {"code": 'err'}
