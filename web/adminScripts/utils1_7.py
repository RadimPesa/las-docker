#!/usr/bin/env python
# -*- coding: utf-8 -*-


import os
import sys
sys.path.append('/srv/www/clinicalManager')


# activate venv
#activate_env=os.path.expanduser("~/.virtualenvs/venvdj1.7/bin/activate_this.py")
#execfile(activate_env, dict(__file__=activate_env))

# Set up the Django Enviroment
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "clinicalManager.settings")
django.setup()

# Neo4j driver
from py2neo import *


# Clinical module models
#from appUtils.models import *
from coreInstitution.models import Institution
from coreProject.models import Project
from django.conf import settings
from django.utils import timezone



# create a Medical Center in the clinicalManager
def createInstitution(ins_name, ins_type, ins_internalName):
    # dbms
    i = Institution()
    i.name = ins_name
    i.institutionType = ins_type
    i.identifier = ins_internalName
    i.save()

    # graph
    graph = neo4j.GraphDatabaseService(settings.GRAPH_DB_URL)
    cypher = """
                CREATE (n:Institution {{identifier:'{}'}})
             """
    query = neo4j.CypherQuery(graph,cypher.format(ins_internalName))
    query.execute()
    #print r.data

    print 'Medical Center created in clinicalManager\n\tname: {}\n\tinstitutionType: {}\n\tidentifier: {}'.format(ins_name, ins_type, ins_internalName)


# create a Project in the clinicalManager
def createProject(title, identifier, wg):
    timeToSave = timezone.localtime(timezone.now())
    # dbms
    p = Project()
    p.name = title
    p.identifier = identifier
    p.save()

    # graph
    graph = neo4j.GraphDatabaseService(settings.GRAPH_DB_URL)

    query = neo4j.CypherQuery(graph, "MATCH (wg:WG) where wg.identifier='"+wg+"' return wg")
    r = query.execute()
    wgNode = r.data[0]['wg']

    batch = neo4j.WriteBatch(graph)
    projectNode = batch.create(node(identifier=identifier))
    batch.add_labels(projectNode, 'Project')
    batch.create(rel(wgNode,'OwnsData', projectNode,{'startDate': timeToSave}))
    batch.submit()
    batch.clear()

    print 'Project created in clinicalManager'





def centersToProjects(*args):
    '''
    this function map medical centers to projects creating "participates" relations
        - usage: pass as first arg the list medical centers identifiers, then the list of projects identifiers. Nodes must already exist on graph
            - e.g., centersToProjects(['ZZ'],['The_new_proj'])
        - outcome on graph: this function crate an edge on graph for each couple (medical center, project)
    '''

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
    print 'Project(s) linked to hospital(s)'





def main():
    print "This is the Python script for dealing with LAS virtualenv 1.7"

if __name__ == "__main__":
    main()
