#!/usr/bin/python

# Set up the Django Enviroment
import sys
sys.path.append('/home/alberto/Lavoro/svn/caQuery/caQuery/src/caquery/') #sys.path.append('/srv/www/caquery')
from django.core.management import setup_environ 
import settings 
setup_environ(settings)
from django.db.models import Max
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
from itertools import izip
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
    if x in all_mice.keys() or x in added_mice.keys() or x in all_aliquots.keys() or x in added_aliquots.keys() or gdb.get_indexed_node('node_auto_index','genid',x):
        # il topo/aliquota c'e' gia', quindi mi fermo qui perche' la ricostruzione della genealogia corrente viene trattata quando si gestisce quel topo/aliquota
        return
    # il topo/aliquota non c'e', quindi procedo a ricostruirne la genealogia
    if __debug__:
        print "   reconstructing genealogy:"
    par_gid = None
    while int(gid.getSamplePassage()) > 1 or gid.isAliquot():

        if gid.isMouse():
            if gid.getGenID() in all_mice.keys() or gid.getGenID() in added_mice.keys() or gdb.get_indexed_node('node_auto_index','genid',gid.getGenID()):
                # il topo esiste gia', quindi mi fermo qui perche' la ricostruzione della genealogia corrente viene trattata quando si gestisce quel topo
                return

            # ricreo aliquota VT dummy di tipo TUM con cui e' stato impiantato il topo
            p = get_dummy_VT_from_mouse(gid.getGenID(), 'X')
            if __debug__:
                print "      parent (historical) = " + p
            added_mice[gid.getGenID()] = {'parent': p}
            gid = GenealogyID(p)
        
        elif gid.isAliquot():
            if gid.getGenID() in all_aliquots.keys() or gid.getGenID() in added_aliquots.keys() or gdb.get_indexed_node('node_auto_index','genid',gid.getGenID()):
                # l'aliquota esiste gia', quindi mi fermo qui perche' la ricostruzione della genealogia corrente viene trattata quando si gestisce quell'aliquota
                return

            # aliquota non esiste, ricreo il topo da cui e' stata espiantata
            par_gid = copy.deepcopy(gid)
            par_gid.zeroOutFieldsAfter('mouse')
            added_aliquots[gid.getGenID()] = {'parent':par_gid.getGenID(), 'type':'Viable'}
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
        if gid.getSamplePassage() > 2:
            mouse_no = int(gid.getMouse())
            parent_no=parent_mouse((mouse_no-200) if (mouse_no>200) else mouse_no)
        else:
            parent_no = 1
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


def updategraph():
    
    print '['+str(datetime.now())+'] ' + "Begin"
    
    last_update_date = graph_db_update.objects.aggregate(Max('timestamp'))['timestamp__max'].date().isoformat()
    
    print '['+str(datetime.now())+'] ' + "Last update on " + last_update_date
    print '['+str(datetime.now())+'] ' + "Searching for new aliquots/mice..."
    
    
    # get all aliquots created since last update
    values_to_send={'predecessor': 'start', 'parameter': 'Date', 'list': '', 'values': '>_'+last_update_date, 'successor': 'End'}
    data = urllib.urlencode(values_to_send)
    
    btn=Button.objects.get(name="Aliquots")
    url=btn.query_api_url

    try:
        u = urllib2.urlopen(url, data)
    except:
        print "An error occurred while trying to retrieve data from "+str(url)   

    res=u.read()
    result=ast.literal_eval(res)
    
    cases = {}
    for x in result['objects']:
        g = GenealogyID(x['uniqueGenealogyID'])
        g.zeroOutFieldsAfter('caseCode')
        a = {}
        a['type'] = x['idAliquotType']
        a['id'] = x['id']
        if g.getGenID() not in cases.keys():
            cases[g.getGenID()] = {}
            cases[g.getGenID()]['aliquots'] = {}
            cases[g.getGenID()]['mice'] = {}
        cases[g.getGenID()]['aliquots'][x['uniqueGenealogyID']] = a
        
    print '['+str(datetime.now())+'] ' + str(len(result['objects'])) + " aliquots"
        
    
    # get all mice implanted since last update
    values_to_send = {'predecessor': 'start', 'parameter': 'Date', 'list': '', 'values': '>_'+last_update_date, 'successor': 'Mice'}
    data = urllib.urlencode(values_to_send)
    
    btn=Button.objects.get(name="Implants")
    url=btn.query_api_url

    try:
        u = urllib2.urlopen(url, data)
    except:
        print "An error occurred while trying to retrieve data from "+str(url)   

    res=u.read()
    result=ast.literal_eval(res)

    values_to_send = {'predecessor': 'Implants', 'parameter': '', 'list': str(result), 'values': '', 'successor': 'End'}
    data = urllib.urlencode(values_to_send)
    
    btn=Button.objects.get(name="Mice")
    url=btn.query_api_url

    try:
        u = urllib2.urlopen(url, data)
    except:
        print "An error occurred while trying to retrieve data from "+str(url)   

    res=u.read()
    result=ast.literal_eval(res)
    
    for x in result['objects']:
        g = GenealogyID(x['id_genealogy'])
        g.zeroOutFieldsAfter('caseCode')
        m = {}
        m['id'] = x['id']
        if g.getGenID() not in cases.keys():
            cases[g.getGenID()] = {}
            cases[g.getGenID()]['aliquots'] = {}
            cases[g.getGenID()]['mice'] = {}
        cases[g.getGenID()]['mice'][x['id_genealogy']] = m

    print '['+str(datetime.now())+'] ' + str(len(result['objects'])) + " mice"

    result = None
       
    tot_cases = str(len(cases))

    print '['+str(datetime.now())+'] ' +  "in " + str(tot_cases) + " cases"

    gdb = neo4j.GraphDatabaseService(settings.NEO4J_URL)
    
    case_cnt = 0
    for c,v in cases.iteritems():
        case_cnt += 1
        print '['+str(datetime.now())+'] ' + "Case " + str(case_cnt) + "/" + str(tot_cases)+": " + c
        
        print str(len(v['aliquots'])) + " aliquots"
        
        #print str(v['aliquots'])
        
        print str(len(v['mice'])) + " mice"
        
        #print str(v['mice'])
        
        added_aliquots = {}
        deleted_aliquots = []
        added_mice = {}
        deleted_mice = []
        split_aliquots = []
        
        # for each aliquot, find parent
        for a_genid,a_values in v['aliquots'].iteritems():
            if __debug__:
                print "Aliquot: " + a_genid
            
            if gdb.get_indexed_node('node_auto_index','genid',a_genid):
                # aliquot is already in graph
                deleted_aliquots.append(a_genid)
                if __debug__:
                    print "already in graph"
                continue
                
            g = GenealogyID(a_genid)

            if g.getArchivedMaterial() == 'R' or g.getArchivedMaterial() == 'D':
                # derivative aliquot, either 1st level or 2nd level
                # query for transformation event and find parent aliquot
                p = find_parent_thru_transf_event(a_genid, a_values)
                if p:
                    v['aliquots'][a_genid]['parent'] = p
                    if __debug__:
                        print "   parent from transf event = " + p
                else:
                    # if none found, query for split aliquot and find original aliquot
                    #   => the current one is a sibling of the original one, so they have the same parent
                    #   => add key 'split_src'=genid of the original one
                    o = find_src_aliquot_thru_split(a_genid, a_values)
                    if o:
                        v['aliquots'][a_genid]['split_src'] = o
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
                        reconstruct_missing_genealogy(p, v['aliquots'], v['mice'], added_aliquots, added_mice)
                        
            elif g.getSampleVector() == 'H':
                # parent is dummy and comes from genid[0:9]
                p = g.zeroOutFieldsAfter('sampleVector').getGenID()
                v['aliquots'][a_genid]['parent'] = p
                if p not in added_aliquots.keys():
                    added_aliquots[p] = {'parent' : GenealogyID(p).zeroOutFieldsAfter('caseCode').getGenID(), 'isCase':True}
                
                if __debug__:
                    print "   parent case = " + v['aliquots'][a_genid]['parent']

            elif g.getSampleVector() == 'X':
                # query for explant and find parent mouse
                p = find_parent_thru_explant(a_genid)
                if p:
                    v['aliquots'][a_genid]['parent'] = p
                    if __debug__:
                        print "   parent from explant = " + p
                else:
                    # if none found, query for split aliquot and find original aliquot
                    #   => the current one is a sibling of the original one, so they have the same parent
                    #   => add key 'split_src'=genid of the original one
                    o = find_src_aliquot_thru_split(a_genid, a_values)
                    if o:
                        v['aliquots'][a_genid]['split_src'] = o
                        if __debug__:
                            print "   original from split = " + o
                        split_aliquots.append(a_genid)
                    else:
                        # if none found, aliquot is historical => parent is mouse with same genealogy
                        p = g.zeroOutFieldsAfter('mouse').getGenID()
                        if __debug__:
                            print "   parent (historical) = " + p
                        v['aliquots'][a_genid]['parent'] = p
                        reconstruct_missing_genealogy(p, v['aliquots'], v['mice'], added_aliquots, added_mice)
                        
            else:
                # other vectors to handle in the future
                pass

        #for each mouse, find parent
        for m_genid,m_values in v['mice'].iteritems():
            if __debug__:
                print "Mouse: " + m_genid
            
            if gdb.get_indexed_node('node_auto_index','genid',m_genid):
                # mouse is already in graph
                deleted_mice.append(m_genid)
                if __debug__:
                    print "already in graph"
                continue
            
            # query for implant and find VT aliquot
            p = find_parent_thru_implant(m_genid, m_values)
            if __debug__ and p:
                print "   parent from implant = " + p
            # if none found, parent is set to a fake one (VT99)
            if not p:
                p = get_dummy_VT_from_mouse(m_genid)
                if __debug__:
                    print "   parent (historical) = " + p
                reconstruct_missing_genealogy(p, v['aliquots'], v['mice'], added_aliquots, added_mice)
            v['mice'][m_genid]['parent'] = p
            
        for k,w in added_aliquots.iteritems():
            v['aliquots'][k] = w
        for x in deleted_aliquots:
            del v['aliquots'][x]
        for k,w in added_mice.iteritems():
            v['mice'][k] = w
        for x in deleted_mice:
            del v['mice'][x]
        
        for a in split_aliquots:
            g = GenealogyID(a)
            v['aliquots'][a]['parent'] = v['aliquots'][v['aliquots'][a]['split_src']]['parent']
        
        to_insert = []
        
        bid = 0 # bid = ID of current node within insertion Batch
        n = gdb.get_indexed_node('node_auto_index','genid',c)
        if not n:
            to_insert.append({'genid': c, 'entity': 'C'})
            bid += 1
        
        for a_genid,a_values in v['aliquots'].iteritems():
            if 'parent' not in a_values:
                print "missing parent key: " +a_genid + str(a_values)
            else:
                if a_values['parent'] not in v['mice'].keys() and a_values['parent'] not in v['aliquots'].keys() and not gdb.get_indexed_node('node_auto_index','genid',a_values['parent']) and a_values['parent'] != c:
                    print "Aliquot " + a_genid + " has an unknown parent " + a_values['parent']
                    continue
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
        
        for m_genid,m_values in v['mice'].iteritems():
            if m_values['parent'] not in v['aliquots'].keys() and not gdb.get_indexed_node('node_auto_index','genid',m_values['parent']):
                print "Mouse " + m_genid + " has an unknown parent " + m_values['parent']
                continue
            n = {'genid': m_genid, 'entity': 'X'}
            if m_genid in added_mice.keys():
                n['inferred'] = True
            to_insert.append()
            m_values['bid'] = bid
            bid += 1
            
        for a_genid,a_values in v['aliquots'].iteritems():
            if 'parent' in a_values:
                this_bid = a_values['bid']
                n = gdb.get_indexed_node('node_auto_index','genid',a_values['parent'])
                print a_values['parent'] + (" " if n else " not ") + "in graph"
                other_bid = n if n else v['mice'][a_values['parent']]['bid'] if a_values['parent'] in v['mice'].keys() else v['aliquots'][a_values['parent']]['bid'] if a_values['parent'] in v['aliquots'].keys() else 0
                to_insert.append((other_bid, 'hasChild', this_bid))
        
        for m_genid,m_values in v['mice'].iteritems():
            if 'parent' in m_values:
                this_bid = m_values['bid']
                n = gdb.get_indexed_node('node_auto_index','genid',m_values['parent'])
                print m_values['parent'] + (" " if n else " not ") + "in graph"
                other_bid = n if n else v['aliquots'][m_values['parent']]['bid']
                to_insert.append((other_bid, 'hasChild', this_bid))
                
        case_subtree = gdb.create(*to_insert)
        
    print '['+str(datetime.now())+'] ' + "End" 
    
    upd = graph_db_update()
    upd.description = 'Update'
    upd.timestamp = datetime.now()
    upd.save()   
        
    return

if __name__=='__main__':
    #print 'main'
    updategraph()
