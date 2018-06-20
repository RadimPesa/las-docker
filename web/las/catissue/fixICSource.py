#!/usr/bin/python

# make IC sources coherent across biobank database, clinical database, and graph

import sys
import site
import os
site.addsitedir('~/.virtualenvs/venvdj1.4/local/lib/python2.7/site-packages')

sys.path.append('/srv/www/biobank')

activate_env=os.path.expanduser("~/.virtualenvs/venvdj1.4/bin/activate_this.py")
execfile(activate_env, dict(__file__=activate_env))

from django.core.management import setup_environ 
import settings
setup_environ(settings)

from catissue.tissue.models import *
from django.conf import settings

from py2neo import neo4j, node, rel
neo4j._add_header('X-Stream', 'true;format=pretty')

gdb = neo4j.GraphDatabaseService(settings.GRAPH_DB_URL)

def getSourceFromGraph():
    query_text = "match (i:IC)-[:belongs]->(ii:Institution) return i.icCode, ii.identifier"
    query = neo4j.CypherQuery(gdb, query_text)
    res = query.execute()
    return {r[0]: r[1] for r in res}

def getSourceFromDb(remapIC):
    res = {}
    for c in Collection.objects.all():
        try:
            res[remapIC[c.collectionEvent]] = c.idSource.internalName
        except:
            res[c.collectionEvent] = c.idSource.internalName
    return res

def deleteSourceOnGraph(ic):
    query_text = "match (i:IC {icCode: { ic }})-[b:belongs]->(ii:Institution) delete b"
    query = neo4j.CypherQuery(gdb, query_text)
    res = query.execute(ic=ic)

def updateSourceOnGraph(ic, src):
    query_text = "match (i:IC {icCode: { ic }}), (ii:Institution {identifier: { src }}) create (i)-[:belongs]->(ii)"
    query = neo4j.CypherQuery(gdb, query_text)
    res = query.execute(ic=ic, src=src)

def getICFromGraph():
    query_text = "match (i:IC)-[:belongs]->(p:Project) return i.icCode, p.identifier"
    query = neo4j.CypherQuery(gdb, query_text)
    res = query.execute()
    return set([(r[0], r[1]) for r in res])

def getICNoCollFromGraph():
    query_text = "match (i:IC)-[:belongs]->(p:Project) optional match (i)<-[:belongs]-(c:Collection) with i, p, c where c is null return i.icCode, p.identifier"
    query = neo4j.CypherQuery(gdb, query_text)
    res = query.execute()
    return set([(r[0], r[1]) for r in res])

def getICFromDb():
    return set([(c.collectionEvent, c.idCollectionProtocol.project) for c in Collection.objects.all()])

def checkIC():
    print "N.B. IC = (icCode, Project.identifier)"
    print ""

    icG_all = getICFromGraph()
    print "# ICs in graph:", len(icG_all)
    icD_all = getICFromDb()
    print "# ICs in db:", len(icD_all)
    icG_noColl = getICNoCollFromGraph()
    print "# ICs w/out coll. in graph:", len(icG_noColl)
    
    icD_all_ok = {}
    for icG in icG_all:
        for icD in icD_all:
            if icD[0].startswith(icG[0]) and icD[1] == icG[1]:
                icD_all_ok[icD] = icG
    print ""
    print "# ICs in db matching graph:", len(icD_all_ok.keys())
    print "# not matching:"
    print "\n".join(map(lambda z: z[0] + "\t" + z[1], icD_all.difference(icD_all_ok.keys())))
    print ""
    icG_notInD = set(icG_all).difference(icD_all_ok.values())
    print "# ICs in graph not matching db:", len(icG_notInD)
    print ""
    print "IC_no_coll minus IC_not_in_db = "
    print "\n".join(map(lambda z: z[0] + "\t" + z[1], icG_noColl.difference(icG_notInD)))
    print ""
    print "IC_not_in_db minus IC_no_coll = "
    print "\n".join(map(lambda z: z[0] + "\t" + z[1], icG_notInD.difference(icG_noColl)))

    exit(0)


    srcGraph = getSourceFromGraph()
    srcDb = getSourceFromDb(icD_all_ok)
    cnt = 0
    missing = []
    
    for ic, src in srcDb.iteritems():
        try:
            srcG = srcGraph[ic]
            if src != srcG:
                cnt += 1
                #updateSourceOnGraph(ic, src)
        except:
            missing.append(ic)
            continue
    
    print cnt
    print missing



if __name__=='__main__':
    checkIC()
    
