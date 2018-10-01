from rest_framework import viewsets, mixins
from rest_framework import status
from rest_framework.response import Response
from py2neo import *#Graph, Node, Relationship
from django.conf import settings
from django.http import Http404
from coreProject.api.utils import *
from coreProject.models import Project
from coreProject.api.serializers import *
import json
import requests
from django.utils import timezone
# guest cores:
from coreInstitution.models import Institution
from corePatient.models import Patient
from global_request_middleware import *
from rest_framework.authentication import BasicAuthentication
from appUtils.csrf_exempt import *


class IcViewSet(viewsets.ViewSet):
    """
    A simple API about ICs...
    """

    def list(self, request):
        #queryset = None #Patient.objects.all()
        iCcode      = request.query_params.get('ICcode', None)
        project     = request.query_params.get('project', None)
        icGlobal    = request.query_params.get('icGlobal', None)

        if None not in (iCcode, project):
            print '[coreProject] getting data for ICcode', iCcode,'and project',project
            graph = getGraphInstance(settings.GRAPH_DB_URL)
            ic = getIC(graph, iCcode, project)
            if ic == 0:
                raise Http404('[coreProject] no matching data')
            else:
                return Response(ic, status=status.HTTP_200_OK)

        if icGlobal is not None:
            return_list = []
            print '[coreProject] getting GLOBAL data for ICcode', icGlobal
            graph = getGraphInstance(settings.GRAPH_DB_URL)
            query = neo4j.CypherQuery(graph,"MATCH (ic:IC {{icCode:'{}'}})-[:belongs]-(p:Project) return p".format(icGlobal))
            r = query.execute()
            if len(r.data) == 0:
                raise Http404('[coreProject] no GLOBAL matching data')
            else:
                for i in r.data:
                    return_list.append(i['p']['identifier'])
            return Response(return_list, status=status.HTTP_200_OK)


        else:
            print ('[coreProject] no or unexpected params in GET')
            raise Http404('[coreProject] no or unexpected params in GET')



    def create(self, request):
        print '[coreProject/POST] - incoming request...\n', json.dumps(request.data, sort_keys=True, indent=4, separators=(',', ': '))
        noEmptyValueDict = {k:v for k,v in request.data.items() if v}
        timeToSave = timezone.localtime(timezone.now())
        try:
            graph = getGraphInstance(settings.GRAPH_DB_URL)
            batch = neo4j.WriteBatch(graph)
            # request from BioBank
            if 'patientUuid' not in noEmptyValueDict:
                # Check if each node has been created
                query = neo4j.CypherQuery(graph,"MATCH (t:Project), (c:Collection), (ic:IC), (ic)-[:belongs]-(t) where t.identifier='"+noEmptyValueDict['project']+"' AND c.identifier='"+noEmptyValueDict['collection']+"' AND ic.icCode=~'(?i)"+noEmptyValueDict['ICcode']+"' return t,c,ic")
                r = query.execute()
                if len(r.data)==0:  # if nodes are not aligned
                    raise Exception('[coreProject] graph nodes are not aligned')
                #print r
                icNode = r.data[0]['ic']
                cNode  = r.data[0]['c']

                query = neo4j.CypherQuery(graph,"match (wg:WG)-[r]-(ic:IC) where ic.icCode=~'(?i)"+noEmptyValueDict['ICcode']+"' return wg")
                r = query.execute()
                if len(r) == 0:
                    raise Exception('[coreProject] Error: no social data')

                oldSocial = []

                for item in r:
                    oldSocial.append(item['wg']['identifier'])

                newSharings = list(set(noEmptyValueDict['sharings']) - set(oldSocial))
                if newSharings:
                    socialData = updateSharing(graph, batch, icNode, newSharings, timeToSave)
                else:
                    socialData = {'newSharings':None}
                cNode_belongs_icNode = rel(cNode,'belongs' , icNode)
                batch.create(cNode_belongs_icNode)
                batch.submit()
                batch.clear()
                returnDict = {
                                'ICcode':noEmptyValueDict['ICcode'],
                                'project': noEmptyValueDict['project'],
                                'collection':noEmptyValueDict['collection']
                              }
                returnDict.update(socialData)
                return Response(returnDict,status=status.HTTP_201_CREATED)


            # request from appEnrollment
            elif 'collection' in noEmptyValueDict: # appEnrollment/BioBank
                query = neo4j.CypherQuery(graph,"MATCH (p:Patient), (t:Project), (m:Institution), (c:Collection) where p.identifier='"+noEmptyValueDict['patientUuid']+"' AND t.identifier='"+noEmptyValueDict['project']+"' AND m.identifier='"+noEmptyValueDict['medicalCenter']+"' AND c.identifier='"+noEmptyValueDict['collection']+"'  return p,t,m,c")
                r = query.execute()
                if len(r.data)==0:   # if nodes are not aligned
                    raise Exception('[coreProject] graph nodes are not aligned')

                pNode = r.data[0]['p']
                tNode = r.data[0]['t']
                mNode = r.data[0]['m']
                cNode = r.data[0]['c']


                # check if IC already exists for the project
                query = neo4j.CypherQuery(graph,"MATCH (ic:IC)-[]-(t:Project) where ic.icCode='"+noEmptyValueDict['ICcode']+"' AND t.identifier='"+noEmptyValueDict['project']+"' return ic")
                r = query.execute()
                if len(r.data)>0: # IC exists
                    raise Exception('[coreProject] IC already exists')

                # check if WG exists (ownership)
                query = neo4j.CypherQuery(graph,"MATCH (wg:WG) where wg.identifier='"+noEmptyValueDict['ownership']+"' return wg ")
                r = query.execute()
                if len(r.data) == 0:
                    raise Exception('[coreProject] Error: owner WG does not exists',str(noEmptyValueDict['ownership']))

                ownsNode = r.data[0]['wg']
                if 'sharings' in noEmptyValueDict: # Sharing exists
                    #icNode = Node("IC", icCode=noEmptyValueDict['ICcode'])
                    icNode = batch.create(node(icCode=noEmptyValueDict['ICcode']))
                    batch.add_labels(icNode, 'IC')
                    returnDict = updateSharing(graph, batch, icNode, noEmptyValueDict['sharings'], timeToSave)
                    pNode_signed_icNode  = rel(pNode, 'signed'  , icNode)
                    icNode_belongs_tNode = rel(icNode,'belongs' , tNode, {'startDate': timeToSave})
                    icNode_belongs_mNode = rel(icNode,'belongs' , mNode)
                    cNode_belongs_icNode = rel(cNode ,'belongs'  , icNode)
                    ownsRel = rel(ownsNode,'OwnsData', icNode, {'startDate': timeToSave})
                    batch.create(pNode_signed_icNode)
                    batch.create(icNode_belongs_tNode)
                    batch.create(icNode_belongs_mNode)
                    batch.create(cNode_belongs_icNode)
                    batch.create(ownsRel)
                    socialData = {'ownership':noEmptyValueDict['ownership'],'sharings':returnDict['newSharings']}

                else: # NO Sharing
                    #icNode = Node("IC", icCode=noEmptyValueDict['ICcode'])
                    icNode = batch.create(node(icCode=noEmptyValueDict['ICcode']))
                    batch.add_labels(icNode, 'IC')
                    pNode_signed_icNode  = rel(pNode, 'signed'  , icNode)
                    icNode_belongs_tNode = rel(icNode,'belongs' , tNode, {'startDate': timeToSave})
                    icNode_belongs_mNode = rel(icNode,'belongs' , mNode)
                    cNode_belongs_icNode = rel(cNode,'belongs'  , icNode)
                    ownsRel = rel(ownsNode,'OwnsData', icNode, {'startDate': timeToSave})
                    batch.create(pNode_signed_icNode)
                    batch.create(icNode_belongs_tNode)
                    batch.create(icNode_belongs_mNode)
                    batch.create(cNode_belongs_icNode)
                    batch.create(ownsRel)
                    socialData = {'ownership':noEmptyValueDict['ownership'],'sharings':None}

                #check alias BRAND NEW add-on for enrollment from Biobank
                if 'newLocalId' in noEmptyValueDict: # add a relation for local id
                    #print 'aiooooooooooooooooooooooooooooooooooooooooooooooaisodiaosidoas'
                    newLocalId = noEmptyValueDict['newLocalId']
                    pNode_hasAlias_tNode = rel(pNode, 'hasAlias', tNode, {'localId': newLocalId, 'startDate': timeToSave})
                    batch.create(pNode_hasAlias_tNode)
                else:
                    newLocalId = None
                    #print 'nonc eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee'

                batch.submit()
                batch.clear()

                returnDict = {
                                'patientUuid':noEmptyValueDict['patientUuid'],
                                'localId':newLocalId,
                                'ICcode':noEmptyValueDict['ICcode'],
                                'project': noEmptyValueDict['project'],
                                'medicalCenter':noEmptyValueDict['medicalCenter'],
                                'collection':noEmptyValueDict['collection']
                              }
                returnDict.update(socialData)
                return Response(returnDict, status=status.HTTP_201_CREATED)


            elif 'collection' not in noEmptyValueDict: # appEnrollment/GeneSender

                query = neo4j.CypherQuery(graph,"MATCH (p:Patient), (t:Project), (m:Institution)  where p.identifier='"+noEmptyValueDict['patientUuid']+"' AND t.identifier='"+noEmptyValueDict['project']+"' AND m.identifier='"+noEmptyValueDict['medicalCenter']+"' return p,t,m")
                r = query.execute()
                if len(r.data)==0:   # if nodes are not aligned
                    raise Exception('[coreProject] graph nodes are not aligned')

                pNode = r.data[0]['p']
                tNode = r.data[0]['t']
                mNode = r.data[0]['m']

                # check if IC already exists for the project
                query = neo4j.CypherQuery(graph,"MATCH (ic:IC)-[]-(t:Project) where ic.icCode='"+noEmptyValueDict['ICcode']+"' AND t.identifier='"+noEmptyValueDict['project']+"' return ic")
                r = query.execute()
                if len(r.data)>0: # IC exists
                    raise Exception('[coreProject] IC already exists')

                # check if WG exists (ownership)
                query = neo4j.CypherQuery(graph,"MATCH (wg:WG) where wg.identifier='"+noEmptyValueDict['ownership']+"' return wg ")
                r = query.execute()
                if len(r.data) == 0:
                    raise Exception('[corePatient] Error: owner WG does not exists',str(noEmptyValueDict['ownership']))

                ownsNode = r.data[0]['wg']
                if 'sharings' in noEmptyValueDict: # Sharing exists
                    #icNode = Node("IC", icCode=noEmptyValueDict['ICcode'])
                    icNode = batch.create(node(icCode=noEmptyValueDict['ICcode']))
                    batch.add_labels(icNode, 'IC')
                    returnDict = updateSharing(graph, batch, icNode, noEmptyValueDict['sharings'], timeToSave)
                    pNode_signed_icNode  = rel(pNode, 'signed'  , icNode)
                    icNode_belongs_tNode = rel(icNode,'belongs' , tNode, {'startDate': timeToSave})
                    icNode_belongs_mNode = rel(icNode,'belongs' , mNode)
                    ownsRel = rel(ownsNode,'OwnsData', icNode, {'startDate': timeToSave})
                    batch.create(pNode_signed_icNode)
                    batch.create(icNode_belongs_tNode)
                    batch.create(icNode_belongs_mNode)
                    batch.create(ownsRel)
                    socialData = {'ownership':noEmptyValueDict['ownership'],'sharings':returnDict['newSharings']}
                else: # NO Sharing
                    #icNode = Node("IC", icCode=noEmptyValueDict['ICcode'])
                    icNode = batch.create(node(icCode=noEmptyValueDict['ICcode']))
                    batch.add_labels(icNode, 'IC')
                    pNode_signed_icNode  = rel(pNode, 'signed'  , icNode)
                    icNode_belongs_tNode = rel(icNode,'belongs' , tNode, {'startDate': timeToSave})
                    icNode_belongs_mNode = rel(icNode,'belongs' , mNode)
                    ownsRel = rel(ownsNode,'OwnsData', icNode, {'startDate': timeToSave})
                    batch.create(pNode_signed_icNode)
                    batch.create(icNode_belongs_tNode)
                    batch.create(icNode_belongs_mNode)
                    batch.create(ownsRel)
                    socialData = {'ownership':noEmptyValueDict['ownership'],'sharings':None}


                #check alias
                query = neo4j.CypherQuery(graph,"MATCH (p:Patient)-[h:hasAlias]-(t:Project) where p.identifier='"+noEmptyValueDict['patientUuid']+"' and t.identifier='"+noEmptyValueDict['project']+"' return h")
                r = query.execute()
                if len(r.data)==0: #create new alias
                    pNode_hasAlias_tNode = rel(pNode, 'hasAlias', tNode, {'localId': noEmptyValueDict['ICcode'], 'startDate': timeToSave})
                    batch.create(pNode_hasAlias_tNode)
                    localId = noEmptyValueDict['ICcode']
                else: #alias already exists. (No new alias) It should never happen
                    localId = None

                batch.submit()
                batch.clear()

                returnDict = {
                                'patientUuid':noEmptyValueDict['patientUuid'],
                                'ICcode':noEmptyValueDict['ICcode'],
                                'project': noEmptyValueDict['project'],
                                'medicalCenter':noEmptyValueDict['medicalCenter'],
                                'localId':localId
                             }

                returnDict.update(socialData)
                return Response(returnDict, status=status.HTTP_201_CREATED)


            else:
                raise Exception('[coreProject] No or unexpected data')


        except Exception,e:
            print '[coreProject] Exception in coreProject API',e
            #returnDict={'status':'error','patientsList':request.data['patientsList']}
            return Response({'detail':'something went wrong','exception':str(e)},status=status.HTTP_400_BAD_REQUEST)






    def delete(self, request, format = None):
        print '[coreProject/DELETE] deleting data'
        try:
            graph = getGraphInstance(settings.GRAPH_DB_URL)

            iCcode          = request.query_params.get('ICcode', None)
            project         = request.query_params.get('project', None)
            collection      = request.query_params.get('collection', None)
            patientUuid     = request.query_params.get('patientUuid', None)
            medicalCenter   = request.query_params.get('medicalCenter', None)
            localId         = request.query_params.get('localId', None)
            sharings        = request.query_params.get('sharings', None)
            print '[coreProject/DELETE] received data \n iCcode={0}\n project={1}\n collection={2}\n patientUuid={3}\n medicalCenter={4}\n localId={5}\n sharings={6}\n'.format(iCcode,project,collection,patientUuid,medicalCenter,localId,sharings)


            if patientUuid == None: # delete request from BioBank # project,iCcode,collection,sharings[]
                #check WG connections
                wgList = sharings.split(',')
                for item in wgList: #check if data exist (waiting for batch...)
                    print 'checking',item
                    query = neo4j.CypherQuery(graph,"MATCH (ic:IC)-[:belongs]-(t:Project), (wg:WG)-[r:SharesData]-(ic:IC) where t.identifier='"+project+"' AND ic.icCode='"+iCcode+"' and wg.identifier='"+item+"' return r")
                    r = query.execute()
                    if len(r.data) == 0:
                        raise Exception('[corePatient] Error: data are not aligned',str(item))

                # check and delete connections from collection
                query = neo4j.CypherQuery(graph,"MATCH (t:Project), (c:Collection), (ic:IC), (ic)-[:belongs]-(t), (c:Collection)-[b:belongs]-(ic:IC) where t.identifier='"+project+"' AND c.identifier='"+collection+"' AND ic.icCode='"+iCcode+"' delete b return 'ok' as c")
                r = query.execute()
                if len(r.data)==0:   # if graph not aligned
                    raise Exception('[coreProject] data do not match delete criteria')

                #delete WG connections
                for item in wgList:
                    #print item
                    query = neo4j.CypherQuery(graph,"MATCH (ic:IC)-[:belongs]-(t:Project), (wg:WG)-[r:SharesData]-(ic:IC) where t.identifier='"+project+"' AND ic.icCode='"+iCcode+"' and wg.identifier='"+item+"' delete r return 'ok' as c")
                    r = query.execute()
                    if len(r.data) == 0:
                        raise Exception('[corePatient] Error while deleting relations of IC',str(iCcode),',', str(item),'. Perform manual rollback!')


            elif collection != None: # delete request from appEnrollment (BioBank) # patientUuid,project,iCcode,medicalCenter,collection,localId*
                #print 'data',iCcode,project,collection,patientUuid,medicalCenter,localId,sharings
                if localId != None: # localId provided from Biobank
                    query = neo4j.CypherQuery(graph,"MATCH (p:Patient)-[r1:signed]-(i:IC), (i:IC)-[r2:belongs]-(t:Project), (i:IC)-[r3:belongs]-(in:Institution), (c:Collection)-[b:belongs]-(i:IC), (wg:WG)-[rs]->(i:IC), (p:Patient)-[h:hasAlias]-(t:Project)  where i.icCode='"+iCcode+"' and t.identifier='"+project+"' and p.identifier='"+patientUuid+"' and c.identifier='"+collection+"' and in.identifier='"+medicalCenter+"' delete r1,r2,r3,rs,i,b,h return 'ok' as c")
                    r = query.execute()
                else: # no localId from Biobank
                    query = neo4j.CypherQuery(graph,"MATCH (p:Patient)-[r1:signed]-(i:IC), (i:IC)-[r2:belongs]-(t:Project), (i:IC)-[r3:belongs]-(in:Institution), (c:Collection)-[b:belongs]-(i:IC), (wg:WG)-[rs]->(i:IC)  where i.icCode='"+iCcode+"' and t.identifier='"+project+"' and p.identifier='"+patientUuid+"' and c.identifier='"+collection+"' and in.identifier='"+medicalCenter+"' delete r1,r2,r3,rs,i,b return 'ok' as c")
                    r = query.execute()
                if len(r.data)==0:   # if nodes are not aligned
                    raise Exception('[coreProject] data do not match delete criteria')


            elif collection == None:  # delete request from appEnrollment (Gene Sender) # patientUuid,project,iCcode,medicalCenter,localId*
                if localId != None:
                    query = neo4j.CypherQuery(graph,"MATCH (p:Patient)-[r1:signed]-(i:IC), (i:IC)-[r2:belongs]-(t:Project), (i:IC)-[r3:belongs]-(in:Institution), (p:Patient)-[h:hasAlias]-(t:Project), (wg:WG)-[rs]->(i) where i.icCode= '"+iCcode+"' and t.identifier='"+project+"' and h.localId='"+localId+"'and p.identifier='"+patientUuid+"' and in.identifier='"+medicalCenter+"' delete r1,r2,r3,rs,i,h return 'ok' as c")
                    r = query.execute()
                else:
                    query = neo4j.CypherQuery(graph,"MATCH (p:Patient)-[r1:signed]-(i:IC), (i:IC)-[r2:belongs]-(t:Project), (i:IC)-[r3:belongs]-(in:Institution), (wg:WG)-[rs]->(i) where i.icCode= '"+iCcode+"' and t.identifier='"+project+"' and p.identifier='"+patientUuid+"' and in.identifier='"+medicalCenter+"' delete r1,r2,r3,rs,i return 'ok' as c")
                    r = query.execute()
                if len(r.data)==0:   # if nodes are not aligned
                    raise Exception('[coreProject] data do not match delete criteria')

            else:
                raise Exception('[coreProject] No or unexpected data')

            return Response(status=status.HTTP_200_OK)

        except Exception,e:
            print '[coreProject] Exception in coreProject API while deleting',e
            #returnDict={'status':'error','patientsList':request.data['patientsList']}
            return Response({'detail':'something went wrong','exception':str(e)},status=status.HTTP_400_BAD_REQUEST)







class ProjectViewSet(viewsets.ViewSet):
    """
    A simple ViewSet for viewing projects.
    """
    #queryset = Project.objects.list()
    #serializer_class = ProjectSerializer

    def list(self, request):
        queryset = Project.objects.all().order_by('name')
        serializer = ProjectSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)





class LocalIdViewSet(viewsets.ViewSet):
    """
    A simple ViewSet for viewing localId related to projects.
    """
    #queryset = Project.objects.list()
    #serializer_class = ProjectSerializer
    authentication_classes = (SessionCsrfExemptAuthentication, BasicAuthentication) # manager both session and non-session based authentication to the same views

    def list(self, request):
        #queryset = None #Patient.objects.all()
        list      = request.query_params.get('list', None)

        if list != None:
            graph = getGraphInstance(settings.GRAPH_DB_URL)
            returnDict = {}
            projectList = list.split(',')
            for item in projectList:
                print '[coreProject] getting data for project', item
                query = neo4j.CypherQuery(graph,"MATCH (p:Patient)-[alias:hasAlias]->(pr:Project) where pr.identifier='"+item+"' return alias.localId as alias")
                r = query.execute()
                if len(r.data)==0:
                    returnDict[item] = None
                else:
                    localIdList = []
                    for l in r.data:
                        localIdList.append(l['alias'])
                    returnDict[item] = localIdList
            return Response(returnDict, status=status.HTTP_200_OK)
        else:
            print ('[coreProject] no or unexpected params in GET')
            raise Http404('[coreProject] no or unexpected params in GET')


    def put(self, request):
        print request.data
        graph = neo4j.GraphDatabaseService(settings.GRAPH_DB_URL)
        patientId   = request.data['patientId']
        newAlias    = request.data['alias'].upper()
        project     = request.data['project']

        # get project_node
        try:
            project_node = next(graph.find('Project', 'identifier', project)) # graph.find() returns a generator object
        except StopIteration:
            print "Project '{0}' does not exist in graph".format(project)
            raise

        # check if Alias already exists for the project
        # TODO check if there is a best way for using py2neo (use cypher query instead)
        existing_aliases = graph.match(rel_type="hasAlias", end_node = project_node)
        for ea in existing_aliases:
            if ea['localId'].upper() == newAlias:
                return Response('Alias {0} already exists in {1}'.format(newAlias, project_node['identifier']), status = status.HTTP_400_BAD_REQUEST)
            else:
                pass

        # get patient_node
        try:
            patient_node = next(graph.find('Patient', 'identifier', patientId)) # graph.find() returns a generator object
        except StopIteration:
            print "Patient '{0}' does not exist in graph".format(patientId)
            raise

        paitient_alias = graph.match_one(start_node = patient_node, rel_type="hasAlias", end_node = project_node)

        if paitient_alias is None: # create new alias

            # get all ICs for biobank
            cypher = """
                        match (p:Patient {{identifier:'{}'}})-[:signed]->(i:IC), (i)-[:belongs]->(:Project {{identifier:'{}'}})
                        return i
                     """

            query = neo4j.CypherQuery(graph,cypher.format(patientId,project))
            r = query.execute()
            ic_biobank_list = []
            for ic in r.data:
                ic_biobank_list.append(ic['i']['icCode'])


            # update in biobank
            biobank_dict = {'dictalias' : {project:{'_|ic|_':ic_biobank_list,'_|alias|_':newAlias}} }
            print 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'
            print biobank_dict

            headers = {'Content-type': 'application/json'}
            r = requests.post(settings.DOMAIN_URL+'/biobank/api/alias/change/', data=json.dumps(biobank_dict), headers=headers, verify=False)
            responseData = r.json()
            #print responseData
            if responseData['message'] != 'ok':
                raise Exception('[corePatient_Merging/PUT] error while updating Biobank')


            # update in graph
            timeToSave = timezone.localtime(timezone.now())
            graph.create(rel(patient_node,("hasAlias", {"localId": newAlias, "startDate":timeToSave}), project_node))

            return Response('Patient {0} has alias {1} for project {2}'.format(patient_node['identifier'], newAlias, project_node['identifier']), status=status.HTTP_200_OK)


        else: # modify existing alias

            # update in biobank
            biobank_dict = {'dictalias' : {project:{paitient_alias['localId']:newAlias}} }
            print 'oooooooooooooooooooooooooooooooooooooooooooooo'
            print biobank_dict

            headers = {'Content-type': 'application/json'}
            r = requests.post(settings.DOMAIN_URL+'/biobank/api/alias/change/', data=json.dumps(biobank_dict), headers=headers, verify=False)
            responseData = r.json()
            #print responseData
            if responseData['message'] != 'ok':
                raise Exception('[corePatient_Merging/PUT] error while updating Biobank')

            # update in graph
            paitient_alias.update_properties({"localId": newAlias})

            return Response('Patient {0} has a alias {1} for project {2} (updated)'.format(patient_node['identifier'], newAlias, project_node['identifier']), status=status.HTTP_200_OK)






class IcBatchViewSet(viewsets.ViewSet):
    """
    A simple API about ICs (batch)...
    """
    #queryset = Project.objects.list()
    #serializer_class = ProjectSerializer

    def list(self, request):
        #queryset = None #Patient.objects.all()
        list      = request.query_params.get('list', None)

        if list != None:
            graph = getGraphInstance(settings.GRAPH_DB_URL)
            returnDict = {}
            projectList = list.split(',')
            for item in projectList:
                itemList = item.split('|')
                iCcode = itemList[0]
                project = itemList[1]
                print '[coreProject] getting data for ICcode', iCcode,'and project',project
                graph = getGraphInstance(settings.GRAPH_DB_URL)
                ic = getIC(graph, iCcode, project)
                if ic == 0:
                    returnDict[item] = None
                else:
                    returnDict[item] = ic
            return Response(returnDict, status=status.HTTP_200_OK)
        else:
            print ('[coreProject] no or unexpected params in GET')
            raise Http404('[coreProject] no or unexpected params in GET')





class EnrollmentsListViewSet(viewsets.ViewSet):
    """
    A simple API to list patient enrollments
    """
    def list(self, request): # method to visualize this endpoint in the api root (maybe there is something better)
        pass
        return Response(status=status.HTTP_200_OK)

    def retrieve(self, request, pk=None):
        graph = neo4j.GraphDatabaseService(settings.GRAPH_DB_URL)
        return_list = []
        """
        Target: getting all enrollment details for a patient
        Rationale: since some patients couldn't have all aliases for each project, the way is getting data starting from each IC
        """
        try:
            patient_node = next(graph.find('Patient', 'identifier', pk)) # graph.find() returns a generator object
        except StopIteration:
            print "Patient '{0}' does not exist in graph".format(pk)
            raise

        rel_signed_generator = graph.match(start_node = patient_node, rel_type = "signed")
        ic_list = list(x.end_node for x in rel_signed_generator if 'IC' in x.end_node.get_labels())

        for ic in ic_list:
            rel_belongs_generator = graph.match(start_node = ic, rel_type = "belongs")
            inst_name = None # to prevent error when institution is not defined (anyway, it should not happen)
            for rel in rel_belongs_generator:
                n = rel.end_node

                if 'Project' in n.get_labels():
                    project_node = n
                    rel_alias = graph.match_one(start_node = patient_node, rel_type = "hasAlias", end_node = project_node) # A patient has 0 or 1 alias for each project
                    print type(rel_alias)
                    if rel_alias is None: # hasAlias rel does not exist
                        alias = None
                    else: #hasAlias rel exists
                        alias = rel_alias['localId']

                elif 'Institution' in n.get_labels():
                    inst = Institution.objects.get(identifier=n['identifier'])
                    inst_name = inst.name
                else:
                    pass

            # check if the project already exists in return list
            recent_project = next((item for item in return_list if item['project'] == project_node['identifier']), None)
            if recent_project is None: # the project does not exist
                data = {'project': project_node['identifier'] ,'alias': alias ,'ic': [{'icCode' : ic['icCode'],  'institution' : inst_name} ]}
                return_list.append(data)
            else: # the project already exists (more than one IC for a project for this patient)
                recent_project['ic'].append({'icCode' : ic['icCode'], 'institution' : inst_name})

            #print "{0} {1} {2}".format(project_node['identifier'], ic['icCode'], alias)
        return Response(return_list,status=status.HTTP_200_OK)




class PatientsByProject(viewsets.ReadOnlyModelViewSet):
    """
    Detailed list of patient in a given trial
    """
    #queryset = None # this line is probably not required
    serializer_class = PatientsByProjectClassSerializer

    def get_queryset(self):

        self.queryset = []
        graph = neo4j.GraphDatabaseService(settings.GRAPH_DB_URL)
        project = self.request.query_params.get('project', None)

        if project is None:
            return self.queryset

        # get med centers full name
        med_centers = {}
        for med in Institution.objects.all():
            med_centers[med.identifier] = med.name


        cypher = """
                    match (n:Patient)-[:signed]->(i:IC)-[:belongs]->(pr:Project {{identifier:'{}'}})
                    optional match (i:IC)-[:belongs]->(med:Institution)
                    optional match (n)-[alias:hasAlias]->(pr)
                    return distinct n.identifier, alias.localId, collect([i.icCode, med.identifier]) as ic_list
                 """

        query = neo4j.CypherQuery(graph,cypher.format(project))
        r = query.execute()

        for item in r.data:
            p = Patient.objects.get(identifier = item['n.identifier']) # get object in DBMS
            newPatient  = PatientsByProjectClass(
                                                    patientId   = p.identifier,
                                                    alias       = item['alias.localId'],
                                                    firstName   = p.firstName,
                                                    lastName    = p.lastName,
                                                    fiscalCode  = p.fiscalCode,
                                                    gender      = p.sex,
                                                    vitalStatus = p.vitalStatus
                                                )
            for ic in item['ic_list']:
                if ic[1] == None:
                    newPatient.addIc(IcListClass(icCode = ic[0], medicalCenter = None))
                else:
                    newPatient.addIc(IcListClass(icCode = ic[0], medicalCenter = med_centers[ic[1]]))




            self.queryset.append(newPatient)

        return self.queryset
