import sys
sys.path.append('/srv/www/caquery/') #sys.path.append('/srv/www/caquery')
from django.core.management import setup_environ 
import settings 
setup_environ(settings)
#from django.db import transaction
import urllib, urllib2
#from _caQuery.models import Button, graph_db_update
from django.core.mail import EmailMultiAlternatives
import json
#from _caQuery.views import MiceNode
from _caQuery.genealogyID import *
import os
#from datetime import datetime

from py2neo import neo4j, node, rel
from math import ceil
import copy
import argparse
import datetime

neo4j._add_header('X-Stream', 'true;format=pretty')
gdb = neo4j.GraphDatabaseService('http://192.168.122.9:7474/db/data')

nodes = {}
relationships = {}
rootNodes = {}
workingGroup = {'name':None, 'nodeid':None}


def find_parent_thru_transf_event(a_genid,a_values):
    genid = GenealogyID(a_genid).getGenID()
    values_to_send = {'template_id':6, 'parameters':json.dumps([{'id':'0', 'values':[genid]}])} # change
    url = settings.DOMAIN_URL +  '/mdam/api/runtemplate/'
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
        g = GenealogyID(x[0]) # genid cambiare
        return g.getGenID()

    return None


    '''
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
        result=json.loads(res)
        
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
            result=json.loads(res)
            #print 'Transform'
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
    '''


def find_src_aliquot_thru_split(a_genid, a_values):
    genid = GenealogyID(a_genid).getGenID()
    values_to_send = {'template_id':7, 'parameters':json.dumps([{'id':'0', 'values':[genid]}])} # change
    url = settings.DOMAIN_URL +  '/mdam/api/runtemplate/'
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
        g = GenealogyID(x[0]) # genid cambiare
        return g.getGenID()

    return None


    '''
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
    result=json.loads(res)
    #print 'Split'
    #print result
    # the result already contains the genID of the originating aliquot
    if 'objects' in result.keys() and len(result['objects'])>0 and 'idAliquot' in result['objects'][0]:
        return result['objects'][0]['idAliquot']
    else:
        return None
    '''


def find_parent_thru_explant(a_genid):
    genid = GenealogyID(a_genid).getGenID()
    values_to_send = {'template_id':12, 'parameters':json.dumps([{'id':'0', 'values':[genid]}])} # change
    url = settings.DOMAIN_URL +  '/mdam/api/runtemplate/'
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
        g = GenealogyID(x[0]) # genid cambiare
        return g.getGenID()

    return None

    '''
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
    result=json.loads(res)
    

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
        result=json.loads(res)
        #print 'Explant'
        #print result

        if 'genID' in result.keys() and len(result['genID'])>0:
            return result['genID'][0]
        else:
            return None
    else:
        return None
    '''

def find_parent_thru_implant(m_genid, m_values):
    genid = GenealogyID(m_genid).getGenID()
    values_to_send = {'template_id':11, 'parameters':json.dumps([{'id':'0', 'values':[genid]}])} #change
    url = settings.DOMAIN_URL +  '/mdam/api/runtemplate/'
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
    '''
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
    result=json.loads(res)
    #print 'Implant'
    #print result

    if 'genID' in result.keys() and len(result['genID'])>0:
        return result['genID'][0]
    else:
        return None
    '''


# get cases using MDAM
def getCases():
    values_to_send = {'template_id':4} # 'parameters':json.dumps([])}
    url = settings.DOMAIN_URL +  '/mdam/api/runtemplate/'
    data = urllib.urlencode(values_to_send)

    try:
        u = urllib2.urlopen(url, data)
    except Exception, e:
        print e
        print "An error occurred while trying to retrieve data from "+str(url)   

    res=u.read()
    result=json.loads(res)
    
    #print result
    cases = {}
    for c in result['body']:
        if c[7] != 'None': #'Collection Date'
            cases[c[0]] = str(datetime.datetime.strptime(c[7], '%Y-%m-%d')) # c[0] = 'Genealogy (7 cifre)', c[7] = 'collection date' 
        else:
            print 'Case without aliquots ', c[0]
    
    
    print '['+str(datetime.datetime.now())+'] ' + str(len(cases)) + ' cases found'
    return cases

def getAliquots(case):
    # retrieve all aliquots in collection
    genidCase = GenealogyID(case).getGenID()
    values_to_send = {'template_id': 10, 'parameters':json.dumps([{'id':'0', 'values':[genidCase]}])}
    url = settings.DOMAIN_URL +  '/mdam/api/runtemplate/'
    data = urllib.urlencode(values_to_send)

    try:
        u = urllib2.urlopen(url, data)
    except Exception, e:
        print e
        print "An error occurred while trying to retrieve data from "+str(url)   

    res=u.read()
    result=json.loads(res)
    print 'Aliquot'
    print result
    
    for x in result['body']:
        g = GenealogyID(x[0]) # x[0] genid
        altype = 'c'+g.get2Derivation() if g.is2Derivation() else g.getArchivedMaterial()
        #print altype
        dateAl = datetime.datetime.strptime(x[2], '%Y-%m-%d') #  x[2] 'Sampling Date'
        print g.getGenID(), dateAl
        nodes[g.getGenID()] = {'type':'Aliquot', 'altype': altype, 'id':x[6], 'relationships':{}, 'nodeid': None, 'date':str(dateAl)} # x[6]= idaliquot
        buildSemanticNode(g.getGenID(), 'Aliquot', None)



def getMice(case):
    genidCase = GenealogyID(case).getGenID()
    values_to_send = {'template_id':8, 'parameters':json.dumps([{'id':'0', 'values':[genidCase]}])}
    url = settings.DOMAIN_URL +  '/mdam/api/runtemplate/'
    data = urllib.urlencode(values_to_send)

    try:
        u = urllib2.urlopen(url, data)
    except Exception, e:
        print e
        print "An error occurred while trying to retrieve data from "+str(url)   

    res=u.read()
    result=json.loads(res)
    print 'Mouse'
    #print result
    for x in result['body']:
        g = GenealogyID(x[0])# x[0] genealogy
        if x[11] == '': # x[11] implant_date
            dateMouse = datetime.datetime.strptime(x[3], '%Y-%m-%d') # x[3] = 'available_date'
        else:
            dateMouse = datetime.datetime.strptime(x[11], '%Y-%m-%d') # x[11] = 'implant_date'
        print g.getGenID(), dateMouse
        nodes[g.getGenID()] = {'type':'Biomouse', 'altype': None, 'id':x[12],  'relationships':{}, 'nodeid': None, 'date':str(dateMouse)} # x[12] = id_biomouse
        buildSemanticNode(g.getGenID(), 'Biomouse', None)



def getAliquotProcParent(a_genid, a_values):
    
    if __debug__:
        print "Aliquot: " + a_genid
    
    g = GenealogyID(a_genid)

    flagParent = False

    if g.getArchivedMaterial() == 'R' or g.getArchivedMaterial() == 'D':
        # derivative aliquot, either 1st level or 2nd level
        # query for transformation event and find parent aliquot
        p = find_parent_thru_transf_event(a_genid, a_values)
        if p:
            flagParent = True
            nodes[a_genid]['relationships'][p] = {'type': 'generates', 'app':'derivation'}
            if __debug__:
                print "   parent from transf event = " + p
        else:
            # if none found, query for split aliquot and find original aliquot
            #   => the current one is a sibling of the original one, so they have the same parent
            #   => add key 'split_src'=genid of the original one
            o = find_src_aliquot_thru_split(a_genid, a_values)
            if o:
                flagParent = True
                nodes[a_genid]['relationships'][o] = {'type': 'generates', 'app':'split'}
                #aliquots[a_genid]['split_src'] = o
                if __debug__:
                    print "   original from split = " + o
                #split_aliquots.append(a_genid)
            
            
            
    elif g.getSampleVector() == 'X':
        # query for explant and find parent mouse
        p = find_parent_thru_explant(a_genid)
        if p:
            flagParent = True
            nodes[a_genid]['relationships'][p] = {'type': 'generates', 'app':'explant'}
            if __debug__:
                print "   parent from explant = " + p
        else:
            # if none found, query for split aliquot and find original aliquot
            #   => the current one is a sibling of the original one, so they have the same parent
            #   => add key 'split_src'=genid of the original one
            o = find_src_aliquot_thru_split(a_genid, a_values)
            if o:
                flagParent = True
                nodes[a_genid]['relationships'][o] = {'type':'generates', 'app':'split'}
                if __debug__:
                    print "   original from split = " + o


    if not flagParent:
            newLabel = g.getCase()
            newLabel = padGenid(newLabel)
            if __debug__:
                print "   collection event = " + newLabel
            nodes[a_genid]['relationships'][newLabel] = {'type': 'generates', 'app':'collection'}

                
    #else:
        # other vectors to handle in the future
        #pass



def getMiceProcParent(m_genid, m_values):
    if __debug__:
        print "Mouse: " + m_genid
    # query for implant and find VT aliquot
    p = find_parent_thru_implant(m_genid, m_values)
    if p:
        nodes[m_genid]['relationships'][p] = {'type': 'generates', 'app':'implant'}
        if __debug__:
            print "   parent from implant = " + p



def getParent():
    for n, nInfo in nodes.items():
        if nInfo['type'] == 'Aliquot':
            getAliquotProcParent(n, nInfo)
        elif nInfo['type'] == 'Biomouse':
            getMiceProcParent(n, nInfo)



def padGenid (genid):
    newgenid = genid + ''.join('0' for x in range(26 - len(genid)))
    return newgenid

def buildSemanticNode(label, nodeType, nextSemanticLevel):
    genid = GenealogyID(label)
    if nodeType == 'Aliquot':
        if genid.getSampleVector() == 'H':
            newLabel = genid.getCase() + genid.getTissue() + genid.getSampleVector() + genid.getTissueType()
            newLabel = padGenid(newLabel)
            if not nodes.has_key(newLabel):
                nodes[newLabel] = {'type':'Genid', 'altype': None, 'id':None,  'relationships':{}, 'nodeid': None}
            nodes[genid.getGenID()]['relationships'][newLabel] = {'type':'hasInstance', 'app':None}
            buildSemanticNode(newLabel, 'Genid', 'Tissue')
        elif genid.getSampleVector() == 'X':
            newLabel = genid.getCase() + genid.getTissue() + genid.getGeneration() + genid.getMouse() + genid.getTissueType()
            newLabel = padGenid(newLabel)
            if not nodes.has_key(newLabel):
                nodes[newLabel] = {'type':'Genid', 'altype': None, 'id':None,  'relationships':{}, 'nodeid': None}
            nodes[genid.getGenID()]['relationships'][newLabel] = {'type':'hasInstance', 'app':None}
            buildSemanticNode(newLabel, 'Genid', 'Sample')
    elif nodeType == 'Biomouse':
        newLabel = genid.getCase() + genid.getTissue() + genid.getGeneration() + genid.getMouse()
        newLabel = padGenid(newLabel)
        if not nodes.has_key(newLabel):
            nodes[newLabel] = {'type':'Genid', 'altype': None, 'id':None,  'relationships':{}, 'nodeid': None}
        nodes[genid.getGenID()]['relationships'][newLabel] = {'type':'hasInstance', 'app':None}
        buildSemanticNode(newLabel, 'Genid', 'SamplePassage')
    elif nodeType == 'Genid':
        if nextSemanticLevel == 'Sample':
            newLabel = genid.getCase() + genid.getTissue() + genid.getGeneration() + genid.getMouse()
            newLabel = padGenid(newLabel)
            if not nodes.has_key(newLabel):
                nodes[newLabel] = {'type':'Genid', 'altype': None, 'id':None,  'relationships':{}, 'nodeid': None}
            nodes[genid.getGenID()]['relationships'][newLabel] = {'type':'hasSuffix', 'app':None}
            buildSemanticNode(newLabel, 'Genid', 'SamplePassage')
        if nextSemanticLevel == 'SamplePassage':
            newLabel = genid.getCase() + genid.getTissue() + genid.getGeneration()
            newLabel = padGenid(newLabel)
            if not nodes.has_key(newLabel):
                nodes[newLabel] = {'type':'Genid', 'altype': None, 'id':None,  'relationships':{}, 'nodeid': None}
            nodes[genid.getGenID()]['relationships'][newLabel] = {'type':'hasSuffix', 'app':None}
            buildSemanticNode(newLabel, 'Genid', 'Lineage')
        if nextSemanticLevel == 'Lineage':
            newLabel = genid.getCase() + genid.getTissue() + genid.getSampleVector() + genid.getLineage()
            newLabel = padGenid(newLabel)
            if not nodes.has_key(newLabel):
                nodes[newLabel] = {'type':'Genid', 'altype': None, 'id':None,  'relationships':{}, 'nodeid': None}
            nodes[genid.getGenID()]['relationships'][newLabel] = {'type':'hasSuffix', 'app':None}
            buildSemanticNode(newLabel, 'Genid', 'SampleVector')
        if nextSemanticLevel == 'SampleVector':
            newLabel = genid.getCase() + genid.getTissue() + genid.getSampleVector()
            newLabel = padGenid(newLabel)
            if not nodes.has_key(newLabel):
                nodes[newLabel] = {'type':'Genid', 'altype': None, 'id':None,  'relationships':{}, 'nodeid': None}
            nodes[genid.getGenID()]['relationships'][newLabel] = {'type':'hasSuffix', 'app':None}
            buildSemanticNode(newLabel, 'Genid', 'Tissue')
        if nextSemanticLevel == 'Tissue':
            newLabel = genid.getCase() + genid.getTissue()
            newLabel = padGenid(newLabel)
            if not nodes.has_key(newLabel):
                nodes[newLabel] = {'type':'Genid', 'altype': None, 'id':None,  'relationships':{}, 'nodeid': None}
            nodes[genid.getGenID()]['relationships'][newLabel] = {'type':'hasSuffix', 'app':None}
            buildSemanticNode(newLabel, 'Genid', 'Case')
        if nextSemanticLevel == 'Case':
            newLabel = genid.getCase()
            newLabel = padGenid(newLabel)
            if not nodes.has_key(newLabel):
                nodes[newLabel] = {'type':'Collection', 'altype': None, 'id':None,  'relationships':{}, 'nodeid': None}
            nodes[genid.getGenID()]['relationships'][newLabel] = {'type':'hasSuffix', 'app':None}
            buildSemanticNode(newLabel, 'Genid', 'Origin')
        if nextSemanticLevel == 'Origin': # TODO valutare se inserire o meno visto che sarebbe duplicato per il numero di casi con stessa origine
            newLabel = genid.getOrigin()
            newLabel = padGenid(newLabel)
            if not nodes.has_key(newLabel):
                nodes[newLabel] = {'type':'Genid', 'altype': None, 'id':'Root',  'relationships':{}, 'nodeid': None}
            nodes[genid.getGenID()]['relationships'][newLabel] = {'type':'hasSuffix', 'app':None}
            return
        return




def setLabels(nodeId):
    labels = []
    alTypes = {'VT':'Viable', 'SF':'SnapFrozen', 'RL':'RNALater', 'D':'DNA', 'FF':'FormalinFixed', 'PL': 'PlasmaIsolation', 'OF': 'OCTFrozen', 'SI': 'SerumIsolation', 'CH':'ChinaBlack', 'PX':'PAXtube', 'R':'RNA', 'D':'DNA', 'P':'Protein', 'cR':'cRNA', 'cD':'cDNA','FR':'Frozen','FS':'FrozenSediment'}
    if nodes[nodeId]['type'] == 'Biomouse':
        labels = ['Bioentity', 'Biomouse']
    elif nodes[nodeId]['type'] == 'Aliquot':
        labels = ['Bioentity', 'Aliquot', alTypes[nodes[nodeId]['altype']]]
    elif nodes[nodeId]['type'] == 'Genid':
        labels = ['Genid']
    elif nodes[nodeId]['type'] == 'Collection':
        labels = ['Genid', 'Collection']
    return labels




def aliquotsretrieving():
    cases = getCases()
    #cases = {'CRC0078': '2012-01-01 00:00:00', 'CRC0166':'2012-01-01 00:00:00'}
    #cases = {'CRC0735': '2012-01-01 00:00:00'}
    
    case_cnt = 1
    tot_cases = str(len(cases))
    # iteration on cases
    for c, cDate in cases.items():
        # init variables
        global nodes
        global relationships
        nodes = {}
        relationships = {}
        cId = padGenid(c)
        nodes[cId] = {'type':'Collection', 'altype': None, 'id':None,  'relationships':{}, 'nodeid': None, 'date':cDate}
        print '['+str(datetime.datetime.now())+'] ' + "Case " + str(case_cnt) + "/" + str(tot_cases)+": " + c

        
        getAliquots(c)
        getMice(c)
        #return 
        getParent()

        batch = neo4j.WriteBatch(gdb)


        for n, nInfo in nodes.items():
            flagInsert = True
            if nInfo['id'] == 'Root':
                if not rootNodes.has_key(n):
                    nInfo['nodeid'] = batch.create(node(identifier=n))
                    labels = setLabels(n)
                    batch.add_labels(nInfo['nodeid'], *labels)
                    rootNodes[n] = nInfo
                else:
                    nInfo['nodeid'] = gdb.get_indexed_node('node_auto_index', 'identifier', n)
            else:
                nInfo['nodeid'] = batch.create(node(identifier=n))
                labels = setLabels(n)
                batch.add_labels(nInfo['nodeid'], *labels)
                if nInfo['type'] in ['Biomouse', 'Aliquot', 'Collection']:
                    #print nInfo, n
                    batch.create( rel( workingGroup['nodeid'], 'OwnsData', nInfo['nodeid'], {'startDate': nInfo['date'], 'endDate':None} ) )
            



        for dest, destInfo in nodes.items():
            for source, relInfo in destInfo['relationships'].items():
                if relInfo['app']:
                    #print nodes[source]['nodeid']
                    #print relInfo['type'] 
                    #print destInfo['nodeid']
                    #print relInfo['app']
                    batch.create( rel( nodes[source]['nodeid'], relInfo['type'], destInfo['nodeid'], {'app': relInfo['app']} ) )
                else:
                    batch.create( rel( nodes[source]['nodeid'], relInfo['type'], destInfo['nodeid'] ) )

        results = batch.submit()
        batch.clear()
        case_cnt += 1
    


def setWg(wg):
    workingGroup['name'] = wg
    labels = ['Social', 'WG']
    batch = neo4j.WriteBatch(gdb)
    wgNode = batch.create(node(identifier=workingGroup['name']))
    batch.add_labels(wgNode, *labels)
    results = batch.submit()
    batch.clear()
    workingGroup['nodeid'] = gdb.get_indexed_node('node_auto_index', 'identifier', wg)
    #print workingGroup
    return 



def main(args):
    # delete db
    gdb.clear()
    setWg(args.wg)
    # construct graph for all the cases
    aliquotsretrieving()
    #set wg for all the bioentities
    


if __name__=='__main__':
    parser = argparse.ArgumentParser(description='Check integrity db')
    parser.add_argument('--wg', default = 'Bertotti_WG',  help='Wg for all the instances')
    args = parser.parse_args()
    startTime = datetime.datetime.now()
    print '['+str(startTime)+'] ' + "Begin"
    main(args)
    endTime = datetime.datetime.now()
    print 'Execution time: ',  endTime -startTime
    print '['+str(endTime)+'] ' + "End"

    
