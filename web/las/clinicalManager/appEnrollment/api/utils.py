import requests, json
from py2neo import *#Graph, rewrite
from django.conf import settings




def getGraphInstance(url):
    #rewrite(('http', '0.0.0.0', 7474), ('http', '192.168.122.9', 7474))
    #graph = Graph(settings.GRAPH_DB_URL)
    #graph = neo4j.GraphDatabaseService(settings.GRAPH_DB_URL)
    graph = neo4j.GraphDatabaseService(settings.GRAPH_DB_URL)
    return graph



def getSocialRels(graph, project, wg):
    query = neo4j.CypherQuery(graph,"MATCH (wg:WG)-[sr]-(pr:Project) where pr.identifier='"+project+"' return wg.identifier as wg, type(sr) as sr")
    r = query.execute()
    if len(r.data) == 0:
        raise Exception('[AppEnrollment] No social data for the project')
    else:
        ownership = ''
        sharingList = []
        for item in r:
            if item['sr']=='SharesData':
                sharingList.append(item['wg'])
            elif item['sr']=='OwnsData':
                ownership = item['wg']
            else: #unexpected social relationship
                pass

        if wg == ownership or wg in sharingList:
            if len(sharingList) == 0: # wg is the owner
                socialData = {'ownership':ownership,'sharings':None}
            else:
                socialData = {'ownership':ownership,'sharings':sharingList}
        else:
            sharingList.append(wg)
            socialData = {'ownership':ownership,'sharings':sharingList}
        
    return socialData


def createIc(projectUrl, headers, patient, item):
    item['patientUuid'] = patient
    r = requests.post(projectUrl, data=json.dumps(item), headers=headers, verify=False)
    print '[appEnrollment] response from coreProject',r.status_code
    if r.status_code == 201:
        responseData = r.json()
        return responseData
        #itemLog['IC'] = responseData
    else:
        raise Exception('[appEnrollment] error while creating InformedConsent')   


        
