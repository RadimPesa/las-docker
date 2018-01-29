from py2neo import *
from django.db.models import Max
from django.db import transaction
import ast
import urllib, urllib2
import pydot
import os
from datetime import datetime
from itertools import izip
from math import ceil
import copy
from catissue.tissue.genealogyID import *
import time
from catissue.tissue.models import *
from catissue.global_request_middleware import *
import json
'''
def find_parent_thru_explant(a_genid):
    values_to_send={'predecessor': 'Aliquots', 'list': "{'genID': ['"+a_genid+"']}",'parameter': '', 'values': '', 'successor': 'Mice'}
    data = urllib.urlencode(values_to_send)
    #btn=Button.objects.get(name="Explants")
    url=settings.DOMAIN_URL+"/xeno/api.query.explants"
    try:
        u = urllib2.urlopen(url, data)
    except:
        print "An error occurred while trying to retrieve data from "+str(url)

    res=u.read()
    result=ast.literal_eval(res)

    if 'id' in result.keys() and len(result['id']) > 0:
        # get the mouse involved in the explant
        values_to_send={'predecessor': 'Explants', 'list': "{'id': ["+str(result['id'][0])+"]}", 'parameter': '', 'values': '', 'successor': 'Aliquots'}
        data = urllib.urlencode(values_to_send)
        #btn=Button.objects.get(name="Mice")
        url=settings.DOMAIN_URL+"/xeno/api.query.mice"
        try:
            u = urllib2.urlopen(url, data)
        except:
            print "An error occurred while trying to retrieve data from "+str(url)

        res=u.read()
        result=ast.literal_eval(res)

        if 'genID' in result.keys() and len(result['genID'])>0:
            return result['genID'][0]
        else:
            return None
    else:
        return None

def find_parent_thru_transf_event(a_genid,a_values):
    if GenealogyID(a_genid).get2Derivation() in ['R', 'D']:
        # 2nd level derivative
        # no query needed because parent is found by truncating genid
        return GenealogyID(a_genid).zeroOutFieldsAfter('aliqExtraction1').getGenID()
    else:
        # 1st level derivative
        #print "->find_parent_thru_transf_event"
        # get transformation event
        values_to_send = {'predecessor': 'Aliquots', 'list': "{'id':["+a_values['id']+"]}", 'parameter': '', 'values': '', 'successor': 'Aliquots'}
        #print values_to_send
        data = urllib.urlencode(values_to_send)
        url=settings.DOMAIN_URL+"/biobank/api/query/events"
        try:
            u = urllib2.urlopen(url, data)
        except:
            print "An error occurred while trying to retrieve data from "+str(url)

        res=u.read()
        result=ast.literal_eval(res)
        #print result

        if 'id' in result.keys() and len(result['id']) > 0:
            # get aliquots involved in the transformation event
            values_to_send = {'predecessor': 'Transform. Events', 'list': "{'id': " +str(result['id']) +"}", 'parameter': '', 'values': '', 'successor': 'Mice'}
            data = urllib.urlencode(values_to_send)
            #btn=Button.objects.get(name="Aliquots")
            url=settings.DOMAIN_URL+"/biobank/api/query/aliquots"
            try:
                u = urllib2.urlopen(url, data)
            except:
                print "An error occurred while trying to retrieve data from "+str(url)

            res=u.read()
            result=ast.literal_eval(res)
            #print result

            if 'genID' in result.keys():
                g = GenealogyID(a_genid).clearFieldsAfter('mouse')
                for x in result['genID']:
                    # parent aliquot is the only one that has neither R nor D as archived material
                    # (because the current is a 1st level derivative)
                    xx = GenealogyID(x)
                    if xx.getArchivedMaterial() not in ['R', 'D'] and xx.clearFieldsAfter('mouse').compareGenIDs(g):
                        return x
                return None
            else:
                return None
        else:
            return None

def find_src_aliquot_thru_split(a_genid, a_values):
    # get the mother aliquot
    #print "->find_src_aliquot_thru_split"
    values_to_send={'predecessor': 'Aliquots', 'list': "{'id': ['"+a_values['id']+"']}",'parameter': '', 'values': '', 'successor': 'End'}
    data = urllib.urlencode(values_to_send)
    #btn=Button.objects.get(name="Split Event")
    url= settings.DOMAIN_URL+"/biobank/api/query/split"
    try:
        u = urllib2.urlopen(url, data)
    except:
        print "An error occurred while trying to retrieve data from "+str(url)

    res=u.read()
    result=ast.literal_eval(res)
    #print result
    # the result already contains the genID of the originating aliquot
    if 'objects' in result.keys() and len(result['objects'])>0 and 'idAliquot' in result['objects'][0]:
        return result['objects'][0]['idAliquot']
    else:
        print "non trovato cazz"
        return None


def find_parent(gen_id):
    disable_graph()
    aliquot=Aliquot.objects.get(uniqueGenealogyID=gen_id)
    enable_graph()
    a_values=dict()
    a_values['id']=str(aliquot.pk)
    #parent= find_parent_thru_explant(gen_id)
    print "cerco event..."
    parent=find_parent_thru_transf_event(gen_id,a_values)
    if parent is not None:
        print "event!",parent
        return parent
    else:
        print "cerco split, dovrebbe esserlo,altrimenti espianto, ma gia trattato...."
        source=find_src_aliquot_thru_split(gen_id,a_values)
        if source is None:
            return None
        #source_aliq=Aliquots.object.get_old(id=source)
        return find_parent_step2(source)

def find_parent_step2(gen_id):
    aliquot=Aliquot.objects.get(uniqueGenealogyID=gen_id)
    a_values=dict()
    a_values['id']=str(aliquot.pk)
    parent= find_parent_thru_explant(gen_id)
    if parent is not None:
        print parent
        return parent
    else:
        parent=find_parent_thru_transf_event(gen_id,a_values)
        if parent is not None:
            print parent
            return parent
        else:
            source=find_src_aliquot_thru_split(gen_id,a_values)
            print "SOURCE",source
            #source_aliq=Aliquots.object.get_old(id=source)
            return find_parent_step2(source)


#NUOVO

def find_parent_thru_transf_event(a_genid,a_values):
    genid = GenealogyID(a_genid).getGenID()
    values_to_send = {'template_id':6, 'parameters':json.dumps([{'id':'0', 'values':[genid]}])} # change
    
    url = Urls.objects.get(idWebService=WebService.objects.get(name='MDAM')).url +  '/api/runtemplate/'
    #url =  'http://skylark.polito.it/mdam/api/runtemplate/'
    data = urllib.urlencode(values_to_send)

    try:
        u = urllib2.urlopen(url, data)
    except Exception, e:
        print e
        print "An error occurred while trying to retrieve data from "+str(url)   
    #print res
    res=u.read()
    result=json.loads(res)
    
    print result,'eccolo'
    for x in result['body']:
        g = GenealogyID(x[0])
        return g.getGenID()

    return None


def find_src_aliquot_thru_split(a_genid, a_values):
    genid = GenealogyID(a_genid).getGenID()
    values_to_send = {'template_id':7, 'parameters':json.dumps([{'id':'0', 'values':[genid]}])} # change
    url = Urls.objects.get(idWebService=WebService.objects.get(name='MDAM')).url +  '/api/runtemplate/'
    #url =  'http://skylark.polito.it/mdam/api/runtemplate/'
    data = urllib.urlencode(values_to_send)

    try:
        u = urllib2.urlopen(url, data)
    except Exception, e:
        print e
        print "An error occurred while trying to retrieve data from "+str(url)   

    res=u.read()
    result=json.loads(res)
    
    #print result
    for x in result['body']:
        g = GenealogyID(x[0])
        return g.getGenID()

    return None

def find_parent_through_slide(a_genid, a_values):
    genid = GenealogyID(a_genid).getGenID()
    values_to_send = {'template_id':40, 'parameters':json.dumps([{'id':'0', 'values':[genid]}])} # change
    url = Urls.objects.get(idWebService=WebService.objects.get(name='MDAM')).url +  '/api/runtemplate/'
    data = urllib.urlencode(values_to_send)

    try:
        u = urllib2.urlopen(url, data)
    except Exception, e:
        print e
        print "An error occurred while trying to retrieve data from "+str(url)   

    res=u.read()
    result=json.loads(res)
    
    #print result
    for x in result['body']:
        g = GenealogyID(x[0])
        return g.getGenID()

    return None '''

def find_parent_MDAM(a_genid, template_id):
    genid = GenealogyID(a_genid).getGenID()
    values_to_send = {'template_id':template_id, 'parameters':json.dumps([{'id':'0', 'values':[genid]}])}
    url = Urls.objects.get(idWebService=WebService.objects.get(name='MDAM')).url +  '/api/runtemplate/'
    data = urllib.urlencode(values_to_send)

    try:
        u = urllib2.urlopen(url, data)
    except Exception, e:
        print e
        print "An error occurred while trying to retrieve data from "+str(url)   

    res=u.read()
    result=json.loads(res)
    
    #print result
    for x in result['body']:
        g = GenealogyID(x[0])
        return g.getGenID()

    return None

def find_parent_through_label(aliquot):
    #ho l'oggetto aliquota del figlio e devo trovare il gen della madre
    print 'aliquot',aliquot
    print 'sampling',aliquot.idSamplingEvent
    #disable_graph()
    labelsched=AliquotLabelSchedule.objects.filter(idSamplingEvent=aliquot.idSamplingEvent)
    #enable_graph()
    print 'labelsched',labelsched
    if len(labelsched)!=0:
        return labelsched[0].idAliquot.uniqueGenealogyID
    return None
    

def find_parent(gen_id):
    disable_graph()
    aliquot=Aliquot.objects.get(uniqueGenealogyID=gen_id)
    enable_graph()
    a_values=dict()
    a_values['id']=str(aliquot.pk)
    print "cerco event..."
    parent=find_parent_MDAM(gen_id,6)
    if parent is not None:
        print "event!",parent
        return parent, 'derivation'
    else:
        print "cerco split"
        source=find_parent_MDAM(gen_id,7)        
        if source is None:
            print 'cerco slide'
            slide=find_parent_MDAM(gen_id,40)            
            if slide is None:
                print 'cerco label'
                label=find_parent_through_label(aliquot)
                if label is None:
                    return None, 'collection'
                else:
                    print 'trovato label',label
                    return label, 'label'
            else:
                print 'trovato slide',slide
                return slide, 'slide'
        else:
            print 'trovato split',source
            return source , 'split'
