#!/usr/bin/python

# Set up the Django Enviroment
import sys
sys.path.append('/srv/www/caquery/') #sys.path.append('/srv/www/caquery')
from django.core.management import setup_environ 
import settings 
setup_environ(settings)
#from django.db import transaction
import urllib, urllib2
from _caQuery.models import Button, graph_db_update
from django.core.mail import EmailMultiAlternatives
import ast
from _caQuery.views import MiceNode
from _caQuery.genealogyID import *
import os
from datetime import datetime

from py2neo import neo4j
from math import ceil
import copy

# current   -> father
# 1-4       -> 1
# 5-8       -> 2
# 9-12      -> 3
# 13-       -> 5
def parent_mouse(n):
    if n < 0:
        return None
    elif n < 13:
        return int(ceil(float(n)/4))
    else:
        return 5

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
        btn=Button.objects.get(name="Transform. Events")
        url=btn.query_api_url
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
            btn=Button.objects.get(name="Aliquots")
            url=btn.query_api_url
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

    
def find_parent_thru_explant(a_genid):
    # get the explant
    values_to_send={'predecessor': 'Aliquots', 'list': "{'genID': ['"+a_genid+"']}",'parameter': '', 'values': '', 'successor': 'Mice'}
    data = urllib.urlencode(values_to_send)
    btn=Button.objects.get(name="Explants")
    url=btn.query_api_url
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
        btn=Button.objects.get(name="Mice")
        url=btn.query_api_url
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

def find_parent_thru_implant(m_genid, m_values):
    # get the implant
    values_to_send={'predecessor': 'Mice', 'list': "{'id': ['"+m_values['id']+"']}",'parameter': '', 'values': '', 'successor': 'Aliquots'}
    data = urllib.urlencode(values_to_send)
    btn=Button.objects.get(name="Implants")
    url=btn.query_api_url
    try:
        u = urllib2.urlopen(url, data)
    except:
        print "An error occurred while trying to retrieve data from "+str(url)

    res=u.read()
    result=ast.literal_eval(res)
    # the result already contains the genID of the originating aliquot
    
    ## get the aliquot involved in the implant
    #values_to_send={'predecessor': 'Implants', 'list': "{'id': ["+result['id'][0]+"]}", 'parameter': '', 'values': '', 'successor': 'Aliquots'}
    #data = urllib.urlencode(values_to_send)
    #btn=Button.objects.get(name="Mice")
    #url=btn.query_api_url
    #try:
    #    u = urllib2.urlopen(url, data)
    #except:
    #    print "An error occurred while trying to retrieve data from "+str(url)   
    #res=u.read()
    #result=ast.literal_eval(res)

    if 'genID' in result.keys() and len(result['genID'])>0:
        return result['genID'][0]
    else:
        return None

def reconstruct_missing_genealogy(x, all_aliquots, all_mice, added_aliquots, added_mice):
    
    gid = GenealogyID(x)
    if (gid.isMouse() and (x in all_mice.keys() or x in added_mice.keys())) or (gid.isAliquot() and (x in all_aliquots.keys() or x in added_aliquots.keys())):
        # il topo/aliquota c'e' gia', quindi mi fermo qui perche' la ricostruzione della genealogia corrente viene trattata quando si gestisce quel topo/aliquota
        return
    # il topo/aliquota non c'e', quindi procedo a ricostruirne la genealogia
    if __debug__:
        print "   reconstructing genealogy:"
    par_gid = None
    while int(gid.getSamplePassage()) > 1 or gid.isAliquot():
    #continuo fintanto che NOT(ho raggiunto passaggio 1 AND si tratta di topo) => passaggio > 1 OR si tratta di aliquota

        if gid.isMouse():
            if gid.getGenID() in all_mice.keys() or gid.getGenID() in added_mice.keys():
                # il topo esiste gia', quindi mi fermo qui perche' la ricostruzione della genealogia corrente viene trattata quando si gestisce quel topo
                return

            # ricreo aliquota VT dummy di tipo TUM con cui e' stato impiantato il topo
            p = get_dummy_VT_from_mouse(gid.getGenID(), 'X')
            if __debug__:
                print "      parent (historical) = " + p
            added_mice[gid.getGenID()] = {'parent': p}
            gid = GenealogyID(p)
        
        elif gid.isAliquot():
            if gid.getGenID() in all_aliquots.keys() or gid.getGenID() in added_aliquots.keys():
                # l'aliquota esiste gia', quindi mi fermo qui perche' la ricostruzione della genealogia corrente viene trattata quando si gestisce quell'aliquota
                return

            # aliquota non esiste, ricreo il topo da cui e' stata espiantata
            par_gid = copy.deepcopy(gid)
            par_gid.zeroOutFieldsAfter('mouse').setImplantSite('SCR')
            added_aliquots[gid.getGenID()] = {'parent':par_gid.getGenID(), 'type': 'c'+gid.get2Derivation() if gid.is2Derivation() else gid.getArchivedMaterial()}
            if __debug__:
                print "      parent (historical) = " + par_gid.getGenID()
            gid = par_gid

    # ho raggiunto il topo di passaggio 1, completo la genealogia aggiungendo l'aliquota VT
    p = get_dummy_VT_from_mouse(gid.getGenID(), 'H')
    added_mice[gid.getGenID()] = {'parent': p}
    if __debug__:
        print "      parent (historical) = " + p
    if p not in all_aliquots.keys() and p not in added_aliquots.keys():
        case = GenealogyID(p)
        case.zeroOutFieldsAfter('sampleVector')
        added_aliquots[p] = {'parent':case.getGenID()}
        if __debug__:
            print "      parent (historical) = " + case.getGenID()
        if case.getGenID() not in added_aliquots.keys():
            added_aliquots[case.getGenID()] = {'parent':copy.deepcopy(GenealogyID(p)).zeroOutFieldsAfter('caseCode').getGenID(), 'isCase':True}
    return
        
def get_dummy_VT_from_mouse(m_genid, vector=None):

    gid = GenealogyID(m_genid)
    p_gid = GenealogyID(m_genid)

    if not vector:
        if gid.getSamplePassage() > 1:
            vector = 'X'
        else:
            vector = 'H';

    if vector == 'X':
        p_gid.setSamplePassage(int(gid.getSamplePassage())-1)
        mouse_no = int(gid.getMouse())
        delta=200 if mouse_no>200 else 0
        if gid.getSamplePassage() > 2:
            parent_no=delta + parent_mouse(mouse_no-delta)
        else:
            parent_no = delta + 1
        p_gid.setMouse(parent_no)
        p_gid.setTissueType('TUM')
    elif vector == 'H':
        p_gid.zeroOutFieldsAfter('tissue')
        p_gid.setSampleVector('H')
    else:
        return None
    p_gid.setArchivedMaterial('VT')
    p_gid.setAliquotExtraction(99)
    return p_gid.getGenID()

def find_src_aliquot_thru_split(a_genid, a_values):
    # get the mother aliquot
    #print "->find_src_aliquot_thru_split"
    values_to_send={'predecessor': 'Aliquots', 'list': "{'id': ['"+a_values['id']+"']}",'parameter': '', 'values': '', 'successor': 'End'}
    data = urllib.urlencode(values_to_send)
    btn=Button.objects.get(name="Split Event")
    url=btn.query_api_url
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
        return None


def aliquotsretrieving():
    
    print '['+str(datetime.now())+'] ' + "Begin"

    aliquots=[]
    
    values_to_send={'predecessor':'start', 'list': '', 'parameter': '', 'values': '', 'successor': 'End'}
    data = urllib.urlencode(values_to_send)
    button_find=Button.objects.get(name="Collections")
    url=button_find.query_api_url 
    #print url 
    try:
        u = urllib2.urlopen(url, data)
    except:
        print "An error occurred while trying to retrieve data from "+str(url)   
    
    res=u.read()
    result=ast.literal_eval(res)
    cases = []
    for c in result['objects']:
        cases.append(c['Genealogy'])
    
    
    print '['+str(datetime.now())+'] ' + str(len(cases)) + ' cases found'
    gdb = neo4j.GraphDatabaseService(settings.NEO4J_URL)

    gdb.clear()
    
    #cases = ['CRC0323']
    #start_from_case = 'CRC0305'
    start_from_case = ''

    if start_from_case != '':
        start_index = cases.index(start_from_case)
    else:
        start_index = 0
    
    case_cnt = start_index
    tot_cases = str(len(cases))
    for c in cases[start_index:]:
        case_cnt += 1
        print '['+str(datetime.now())+'] ' + "Case " + str(case_cnt) + "/" + str(tot_cases)+": " + c
        aliquots = {}
        mice = {}
        
        # retrieve all aliquots in collection
        values_to_send={'predecessor': 'Genealogy ID_', 'list': "{'genID': ['"+GenealogyID(c).getGenID()+"']}", 'parameter': '', 'values': '', 'successor': 'End'}
        data = urllib.urlencode(values_to_send)
        
        btn=Button.objects.get(name="Aliquots")
        url=btn.query_api_url
        try:
            u = urllib2.urlopen(url, data)
        except:
            print "An error occurred while trying to retrieve data from "+str(url)   
    
        res=u.read()
        result=ast.literal_eval(res)
        
        for x in result['objects']:
            a = {}
            g = GenealogyID(x['uniqueGenealogyID'])
            a['type'] = 'c'+g.get2Derivation() if g.is2Derivation() else g.getArchivedMaterial()
            a['id'] = x['id']
            aliquots[x['uniqueGenealogyID']] = a

        # retrieve all mice in collection
        btn=Button.objects.get(name="Mice")
        url=btn.query_api_url
        try:
            u = urllib2.urlopen(url, data)
        except:
            print "An error occurred while trying to retrieve data from "+str(url)   
    
        res=u.read()
        result=ast.literal_eval(res)
        
        for x in result['objects']:
            m = {}
            m['id'] = x['id']
            mice[x['id_genealogy']] = m
        
        result = None

        added_aliquots = {}
        added_mice = {}
        split_aliquots = []
        # for each aliquot, find parent
        for a_genid,a_values in aliquots.iteritems():
            if __debug__:
                print "Aliquot: " + a_genid
            g = GenealogyID(a_genid)

            if g.getArchivedMaterial() == 'R' or g.getArchivedMaterial() == 'D':
                # derivative aliquot, either 1st level or 2nd level
                # query for transformation event and find parent aliquot
                p = find_parent_thru_transf_event(a_genid, a_values)
                if p:
                    aliquots[a_genid]['parent'] = p
                    if __debug__:
                        print "   parent from transf event = " + p
                else:
                    # if none found, query for split aliquot and find original aliquot
                    #   => the current one is a sibling of the original one, so they have the same parent
                    #   => add key 'split_src'=genid of the original one
                    o = find_src_aliquot_thru_split(a_genid, a_values)
                    if o:
                        aliquots[a_genid]['split_src'] = o
                        if __debug__:
                            print "   original from split = " + o
                        split_aliquots.append(a_genid)
                    else:
                        # if none found, aliquot is historical, parent is assumed to be the first RL aliquot
                        # N.B. at this point, aliquot can only be 1st level derivative, since 2nd level derivation is reconstructed from gen id and not from db, so it never fails
                        p = g.zeroOutFieldsAfter('tissueType').setArchivedMaterial('RL').setAliquotExtraction(1).getGenID()
                        if __debug__:
                            print "   parent from derivation (historical) = " + p
                        aliquots[a_genid]['parent'] = p
                        reconstruct_missing_genealogy(p, aliquots, mice, added_aliquots, added_mice)
                        
            elif g.getSampleVector() == 'H':
                # parent is dummy and comes from genid[0:9]
                p = g.zeroOutFieldsAfter('sampleVector').getGenID()
                aliquots[a_genid]['parent'] = p
                if p not in added_aliquots.keys():
                    added_aliquots[p] = {'parent' : GenealogyID(p).zeroOutFieldsAfter('caseCode').getGenID(), 'isCase':True}
                
                if __debug__:
                    print "   parent case = " + aliquots[a_genid]['parent']

            elif g.getSampleVector() == 'X':
                # query for explant and find parent mouse
                p = find_parent_thru_explant(a_genid)
                if p:
                    aliquots[a_genid]['parent'] = p
                    if __debug__:
                        print "   parent from explant = " + p
                else:
                    # if none found, query for split aliquot and find original aliquot
                    #   => the current one is a sibling of the original one, so they have the same parent
                    #   => add key 'split_src'=genid of the original one
                    o = find_src_aliquot_thru_split(a_genid, a_values)
                    if o:
                        aliquots[a_genid]['split_src'] = o
                        if __debug__:
                            print "   original from split = " + o
                        split_aliquots.append(a_genid)
                    else:
                        # if none found, aliquot is historical => parent is mouse with same genealogy
                        p = g.zeroOutFieldsAfter('mouse').setImplantSite('SCR').getGenID()
                        if __debug__:
                            print "   parent (historical) = " + p
                        aliquots[a_genid]['parent'] = p
                        reconstruct_missing_genealogy(p, aliquots, mice, added_aliquots, added_mice)
                        
            else:
                # other vectors to handle in the future
                pass

        for m_genid,m_values in mice.iteritems():
            if __debug__:
                print "Mouse: " + m_genid
            # query for implant and find VT aliquot
            p = find_parent_thru_implant(m_genid, m_values)
            if __debug__ and p:
                print "   parent from implant = " + p
            # if none found, parent is set to a fake one (VT99)
            if not p:
                p = get_dummy_VT_from_mouse(m_genid)
                if __debug__:
                    print "   parent (historical) = " + p
                reconstruct_missing_genealogy(p, aliquots, mice, added_aliquots, added_mice)
            mice[m_genid]['parent'] = p
            
        for k,v in added_aliquots.iteritems():
            aliquots[k] = v
        for k,v in added_mice.iteritems():
            mice[k] = v
        
        
        for a in split_aliquots:
            g = GenealogyID(a)
            aliquots[a]['parent'] = aliquots[aliquots[a]['split_src']]['parent']
        
        c_gid = GenealogyID(c).zeroOutFieldsAfter('caseCode').getGenID()
               
        to_insert = []
        
        
        to_insert.append({'genid': c_gid, 'entity': 'C'})
        
        bid = 1 #node identifiers within insertion batch, #0 is c_gid (already appended to list)
        for a_genid,a_values in aliquots.iteritems():
            if 'parent' not in a_values:
                print "missing parent key: " +a_genid + str(a_values)
            else:
                if a_values['parent'] not in mice.keys() and a_values['parent'] not in aliquots.keys() and a_values['parent'] != c_gid:
                    print "Aliquot " + a_genid + " has an unknown parent " + a_values['parent']
            g = GenealogyID(a_genid)
            
            am = 'c' + g.get2Derivation() if g.is2Derivation() else g.getArchivedMaterial()
            n= {'genid': a_genid}
            if 'isCase' in a_values:
                n['entity'] = 'C'
            else:
                n['entity'] = 'A'
                n['archived_material'] = am
            if a_genid in added_aliquots.keys():
                n['inferred'] = True
            to_insert.append(n)
            a_values['bid'] = bid
            bid += 1
            
        
        for m_genid,m_values in mice.iteritems():
            if m_values['parent'] not in aliquots.keys():
                print "Mouse " + m_genid + " has an unknown parent " + m_values['parent']
            n = {'genid': m_genid, 'entity': 'X'}
            if m_genid in added_mice.keys():
                n['inferred'] = True
            to_insert.append(n)
            m_values['bid'] = bid
            bid += 1
            
        for a_genid,a_values in aliquots.iteritems():
            if 'parent' in a_values:
                this_bid = a_values['bid']
                other_bid = mice[a_values['parent']]['bid'] if a_values['parent'] in mice.keys() else aliquots[a_values['parent']]['bid'] if a_values['parent'] in aliquots.keys() else 0
                to_insert.append((other_bid, 'hasChild', this_bid))
        
        for m_genid,m_values in mice.iteritems():
            if 'parent' in m_values:
                this_bid = m_values['bid']
                other_bid = aliquots[m_values['parent']]['bid']
                to_insert.append((other_bid, 'hasChild', this_bid))
                
        case_subtree = gdb.create(*to_insert)
        
    upd = graph_db_update()
    upd.description = 'Initial import'
    upd.timestamp = datetime.now()
    upd.save()
        
    return

if __name__=='__main__':
    #print 'main'
    aliquotsretrieving()
