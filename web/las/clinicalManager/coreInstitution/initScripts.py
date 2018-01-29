import requests
from appUtils.models import *
from coreInstitution.models import Institution
from coreProject.models import Project
import json
from py2neo import *
from django.conf import settings
from django.utils import timezone



def createProjects():
    timeToSave = timezone.localtime(timezone.now())
    graph = neo4j.GraphDatabaseService(settings.GRAPH_DB_URL)
    batch = neo4j.WriteBatch(graph)

    query = neo4j.CypherQuery(graph, "MATCH (wg:WG) where wg.identifier='Bardelli_WG' return wg")
    r = query.execute()
    bardelliNode = r.data[0]['wg']


    query = neo4j.CypherQuery(graph, "MATCH (wg:WG) where wg.identifier='Marsoni_WG' return wg")
    r = query.execute()
    marsoniNode = r.data[0]['wg']

    projectsList = Project.objects.all()

    for item in projectsList:
        query = neo4j.CypherQuery(graph, "MATCH (p:Project) where p.identifier='"+item.identifier+"'return p")
        r = query.execute()
        if len(r.data)==0:
            projectNode = batch.create(node(identifier=item.identifier))
            batch.add_labels(projectNode, 'Project')
            if item.identifier == 'Mercuric':
                batch.create(rel(bardelliNode,'OwnsData', projectNode,{'startDate': timeToSave}))
            else:
                batch.create(rel(marsoniNode,'OwnsData', projectNode,{'startDate': timeToSave}))
            print item.identifier,'created...'
    batch.submit()
    batch.clear()
    return 'done'


'''
this function map medical centers to project creating "participates" relations
    - usage: pass as first arg the list medical centers identifiers, then the list of projects identifiers. Nodes must already exist on graph
        - e.g., centersToProjects(['AA','AB'],['Funnel','Herlap'])
    - outcome on graph: this function crate an edge on graph for each couple (medical center, project)
    - author: Andrea M.
    - date: april 13th, 2016
'''
def centersToProjects(*args):
    hospitals   = args[0]
    projects    = args[1]
    timeToSave = timezone.localtime(timezone.now())
    graph = neo4j.GraphDatabaseService(settings.GRAPH_DB_URL)
    batch = neo4j.WriteBatch(graph)

    for h in hospitals:
        print 'linking hospital:',h
        #query = neo4j.CypherQuery(graph, "MATCH (in:Institution) where in.identifier='"+h+"' return in")
        #r = query.execute()
        #hNode = r.data[0]['in']
        for p in projects:
            print '\t\t...to project:',p
            # check if rel already exists
            query = neo4j.CypherQuery(graph, "MATCH (in:Institution)-[r:participates]->(pr:Project) where in.identifier='"+h+"' AND pr.identifier='"+p+"'return r")
            r = query.execute()
            if len(r.data)==0: # rel does not exist
                query = "MATCH (in:Institution),(pr:Project) WHERE in.identifier='"+h+"' AND pr.identifier='"+p+"' CREATE (in)-[r:participates {startDate: '"+str(timeToSave)+"'}]->(pr)"
                batch.append_cypher(query) #create(rel(h,'participates', v,{'startDate': timeToSave}))
            else:
                print 'relation (',h,')-[r:participates]->(',p,') already exists'


    batch.submit()
    batch.clear()
    return 'done'







def createInstitutions(dbms=False):
    #url = 'https://lasapp.polito.it/biobank/api/getSources/'
    url = Urls.objects.get(idWebService=WebService.objects.get(name='biobank').id).url+'/api/getSources/'
    print 'url',url

    r = requests.get(url, verify=False)
    dataList = r.json()
    graph = neo4j.GraphDatabaseService(settings.GRAPH_DB_URL)

    batch = neo4j.WriteBatch(graph)
    for item in dataList:
        ident = item['internalName']
        try:
            i = Institution.objects.get(identifier=ident)
        except Institution.DoesNotExist:
            if dbms:
                iNew = Institution(identifier=ident, name = item['name'], institutionType = 'Medical Center')
                iNew.save()
            inNode = batch.create(node(identifier=ident))
            batch.add_labels(inNode, 'Institution')
            print 'institution',item['name'],'with id',ident,'created'

    batch.submit()
    batch.clear()
    return 'done'






def setRels():
    #url = 'https://lasapp.polito.it/biobank/api/getSources/'
    url = Urls.objects.get(idWebService=WebService.objects.get(name='biobank').id).url+'/api/getSources/'
    print 'url',url
    r = requests.get(url, verify=False)
    dataList = r.json()
    timeToSave = timezone.localtime(timezone.now())
    graph = neo4j.GraphDatabaseService(settings.GRAPH_DB_URL)
    batch = neo4j.WriteBatch(graph)

    projectDict = {}
    query = neo4j.CypherQuery(graph, "MATCH (p:Project) return p")
    r = query.execute()
    for item in r.data:
        projectDict[item['p']['identifier']] = item['p']
    hospitalDict    = {k:v for (k,v) in projectDict.iteritems() if k not in ['Funnel','Mercuric']}
    funnelDict      = {k:v for (k,v) in projectDict.iteritems() if k in ['Funnel']}
    mercuricDict    = {k:v for (k,v) in projectDict.iteritems() if k in ['Mercuric']}
    print hospitalDict,'\n'
    print funnelDict,'\n'
    print mercuricDict,'\n'


    for item in dataList:
        print 'analyzing item',item['internalName']
        query = neo4j.CypherQuery(graph, "MATCH (in:Institution) where in.identifier='"+item['internalName']+"' return in")
        r = query.execute()
        inNode = r.data[0]['in']
        relType = item['type']

        if relType == 'Funnel':
            for k, v in funnelDict.iteritems():
                query = neo4j.CypherQuery(graph, "MATCH (in:Institution)-[r:participates]->(pr:Project) where in.identifier='"+item['internalName']+"' and pr.identifier='"+k+"'return in")
                r = query.execute()
                if len(r.data)==0:
                    batch.create(rel(inNode,'participates', v,{'startDate': timeToSave}))
                else:
                    print 'relation (',item['internalName'],')-[r:participates]->(',k,') already exists'
        elif relType == 'Mercuric':
            for k, v in mercuricDict.iteritems():
                query = neo4j.CypherQuery(graph, "MATCH (in:Institution)-[r:participates]->(pr:Project) where in.identifier='"+item['internalName']+"' and pr.identifier='"+k+"'return in")
                r = query.execute()
                if len(r.data)==0:
                    batch.create(rel(inNode,'participates', v,{'startDate': timeToSave}))
                else:
                    print 'relation (',item['internalName'],')-[r:participates]->(',k,') already exists'
        else:
            for k, v in hospitalDict.iteritems():
                query = neo4j.CypherQuery(graph, "MATCH (in:Institution)-[r:participates]->(pr:Project) where in.identifier='"+item['internalName']+"' and pr.identifier='"+k+"'return in")
                r = query.execute()
                if len(r.data)==0:
                    batch.create(rel(inNode,'participates', v,{'startDate': timeToSave}))
                else:
                    print 'relation (',item['internalName'],')-[r:participates]->(',k,') already exists'

    batch.submit()
    batch.clear()
    return 'done'
