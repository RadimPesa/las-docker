from corePatient.models import Patient
from py2neo import *#Graph, rewrite, Relationship
from django.conf import settings
from corePatient.api.serializers import PatientSerializer
import json

def getGraphInstance(url):
    #rewrite(('http', '0.0.0.0', 7474), ('http', '192.168.122.9', 7474))
    #graph = Graph(settings.GRAPH_DB_URL)
    #graph = neo4j.GraphDatabaseService(settings.GRAPH_DB_URL)
    graph = neo4j.GraphDatabaseService(settings.GRAPH_DB_URL)
    return graph


def checkInDBMS(identifier):
    try:
        print '[corePatient] checking', identifier,'in DBMS...'
        p = Patient.objects.get(identifier = identifier)
        return p
    except Patient.DoesNotExist:
        raise Patient.DoesNotExist


def checkInGraph(graph, identifier):
    print '[corePatient] checking', identifier,'in Graph...'
    #graph = Graph(settings.GRAPH_DB_URL)
    query = neo4j.CypherQuery(graph,"MATCH (pa:Patient) where pa.identifier='"+identifier+"' return pa.identifier as pa")
    r = query.execute()
    #print settings.GRAPH_DB_URL
    return len(r.data)


def getPatientByIdentifier(graph, identifier):
    try:
        p = checkInDBMS(identifier)
        if checkInGraph(graph, identifier) == 1:
            return p
        else:
            return -1
    except Patient.DoesNotExist:
        if checkInGraph(graph, identifier) > 0:
            return -1
        else:
            return 0


def checkPostData(incomingData):
    try:
        p = Patient.objects.get(firstName = incomingData['firstName'], lastName = incomingData['lastName'], fiscalCode = incomingData['fiscalCode'])
        return -1
    except: # Patient.DoesNotExist or anonymous     Patient.DoesNotExist
        return 0


def getPatientDetails(graph, p):
    serializer = PatientSerializer(p)
    identifier = serializer.data['identifier']
    query = neo4j.CypherQuery(graph,"MATCH (wg:WG)-[rOwns:OwnsData]->(pa:Patient) where pa.identifier='"+identifier+"' return wg.identifier as wg")
    r = query.execute()
    if len(r.data)==0:
        raise Exception('[corePatient] no owner')
    ownership = r.data[0]['wg']

    query = neo4j.CypherQuery(graph,"MATCH (wg:WG)-[rShares:SharesData]->(pa:Patient) where pa.identifier='"+identifier+"' return wg.identifier as wg")
    r = query.execute()
    if len(r.data)>0:
        sharingList = []
        for item in r.data:
            sharingList.append(item['wg'])
        socialData = {'ownership':ownership,'sharings':sharingList}
    else:
        socialData = {'ownership':ownership,'sharings':None}


    returnDict = serializer.data
    returnDict.update(socialData)
    return returnDict


def updateSharing(graph, batch, pNode, newSharings, timeToSave):
    newSharingsNodes = []

    for item in newSharings:
        #print item
        query = neo4j.CypherQuery(graph,"match (wg:WG) where wg.identifier='"+item+"' return wg")
        r = query.execute()
        if len(r.data) == 0:
            raise Exception('[corePatient] Error: a sharing WG does not exist',str(item))
        newSharingsNodes.append(r.data[0]['wg'])


    for item in newSharingsNodes:
        sharesRel = rel(item,'SharesData', pNode, {'startDate': timeToSave})
        batch.create(sharesRel)
    returnDict = {'newSharings':newSharings}
    return returnDict
