from py2neo import *#Graph, rewrite, Relationship
from django.conf import settings


def getGraphInstance(url):
    #rewrite(('http', '0.0.0.0', 7474), ('http', '192.168.122.9', 7474))
    #graph = Graph(settings.GRAPH_DB_URL)
    #graph = neo4j.GraphDatabaseService(settings.GRAPH_DB_URL)
    graph = neo4j.GraphDatabaseService(settings.GRAPH_DB_URL)
    return graph


def getIC(graph, iCcode, project):
    query = neo4j.CypherQuery(graph,"MATCH (ic:IC)-[]-(pa:Patient), (ic:IC)-[]-(pr:Project), (ic:IC)-[]-(in:Institution) where ic.icCode=~ '(?i)"+iCcode+"' and pr.identifier='"+project+"' OPTIONAL MATCH (pa:Patient)-[h:hasAlias]-(pr:Project) return pa.identifier as pa, in.identifier as in, h.localId as h")
    resultset = query.execute()

    if len(resultset.data)>0:
        patient     = resultset.data[0]['pa']
        institution = resultset.data[0]['in']
        localId     = resultset.data[0]['h']

        # Social data
        query = neo4j.CypherQuery(graph,"MATCH (wg:WG)-[rOwns:OwnsData]->(ic:IC) where ic.icCode=~ '(?i)"+iCcode+"' return wg.identifier as wg")
        r = query.execute()
        if len(r.data)==0:
            raise Exception('[corePatient] no owner')
        ownership = r.data[0]['wg']

        query = neo4j.CypherQuery(graph,"MATCH (wg:WG)-[rShares:SharesData]->(ic:IC) where ic.icCode=~ '(?i)"+iCcode+"' return wg.identifier as wg")
        r = query.execute()
        if len(r.data)>0:
            sharingList = []
            for item in r:
                sharingList.append(item['wg'])
            socialData = {'ownership':ownership,'sharings':sharingList}
        else:
            socialData = {'ownership':ownership,'sharings':None}

        returnDict = {'iCcode':iCcode, 'project':project, 'patientUuid':patient, 'localId':localId, 'institution':institution}
        returnDict.update(socialData)
        return returnDict
    else:
        return 0


def updateSharing(graph, batch, icNode, newSharings, timeToSave):
    newSharingsNodes = []
    for item in newSharings:
        print item
        query = neo4j.CypherQuery(graph,"match (wg:WG) where wg.identifier='"+item+"' return wg")
        r = query.execute()
        if len(r.data) == 0:
            raise Exception('[corePatient] Error: some sharing WG does not exist',str(item))
        newSharingsNodes.append(r[0]['wg'])
    for item in newSharingsNodes:
        sharesRel = rel(item,'SharesData', icNode, {'startDate': timeToSave})
        batch.create(sharesRel)
    returnDict = {'newSharings':newSharings}
    return returnDict
