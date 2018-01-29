from rest_framework import viewsets
from rest_framework.response import Response
from corePatient.api.serializers import PatientSerializer
from corePatient.api.utils import *
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.db.models import Q
from uuid import uuid4
from rest_framework.parsers import JSONParser
from corePatient.models import Patient, MergedPatient
from django.http import Http404
from py2neo import *#Graph, Node, Relationship
from django.conf import settings
import json
import requests
from django.utils import timezone
from global_request_middleware import *
from rest_framework.authentication import BasicAuthentication
from appUtils.csrf_exempt import *




class PatientViewSet(viewsets.ViewSet):
    """
    A viewset for viewing, creating and deleting patient instances.
    """
    #serializer_class = PatientSerializer
    queryset = Patient.objects.all()




    def retrieve(self, request, pk=None):
        print '[corePatient] get patient by UUID:', pk
        graph = getGraphInstance(settings.GRAPH_DB_URL)
        p = getPatientByIdentifier(graph, pk)
        if p == -1: #graph and DBMS are not aligned
            return Response({'detail':'Conflict beetwen DBMS and Graph'},status=status.HTTP_409_CONFLICT)
        elif p == 0:
            raise Http404('No matching patient')
        else:
            returnDict = getPatientDetails(graph, p)
            return Response(returnDict, status=status.HTTP_200_OK)




    # workaround: this function should return a list of patients but it looks for a specific patient, parsing GET params (firstName, lastName, fiscalCode) or (localId, project)
    # e.g. ../clinical/corePatient/api/patient?firstName=Mario&lastName=Rossi&fiscalCode=MMMRRRK11212L123
    def list(self, request):
        queryset = None #Patient.objects.all()
        firstName   = request.query_params.get('firstName', None)
        lastName    = request.query_params.get('lastName', None)
        fiscalCode  = request.query_params.get('fiscalCode', None)
        localId     = request.query_params.get('localId', None)
        project     = request.query_params.get('project', None)
        details     = request.query_params.get('details', None)
        disableGraph= request.query_params.get('disableGraph', None)

        #try:
        if None not in (firstName, lastName, fiscalCode):
            # return data or raise Http404 (from Django.http)
            print '[corePatient] get("list") patient by personal data:', firstName,',',lastName,',',fiscalCode
            queryset = get_object_or_404(Patient, firstName = firstName, lastName = lastName, fiscalCode = fiscalCode)
            graph = getGraphInstance(settings.GRAPH_DB_URL)
            c = checkInGraph(graph, queryset.identifier)
            if c != 1:
                return Response({'detail':'Conflict beetwen DBMS and Graph'},status=status.HTTP_409_CONFLICT)

        elif None not in (localId, project):
            print '[corePatient] get("list") patient by localId in graph:', localId,'for project',project
            graph = getGraphInstance(settings.GRAPH_DB_URL)
            query = neo4j.CypherQuery(graph,"MATCH (pa:Patient)-[h:hasAlias]-(pr:Project) where h.localId='"+localId+"' and pr.identifier='"+project+"' return pa.identifier as pa")
            resultset = query.execute()
            if len(resultset.data)>0:
                try:
                    identifier = resultset.data[0]['pa']
                    queryset = checkInDBMS(identifier)
                except Patient.DoesNotExist: #data exist in graph but do not exist in DBMS
                    return Response({'detail':'Conflict beetwen DBMS and Graph'},status=status.HTTP_409_CONFLICT)
            else:
                raise Http404('[corePatient] No matching patient')

        elif details is not None:
            print "looking for '"'{0}'"' in patients' firstName, lastName or fiscalCode".format(details)
            searchKeywords = details.split()
            args = []

            if disableGraph:
                disable_graph()

            for item in searchKeywords:
                key = ( Q(firstName__icontains = item) | Q(lastName__icontains = item) | Q(fiscalCode__icontains = item) )
                args.append(key)

            if disableGraph:
                enable_graph()

            patientList = Patient.objects.filter(*args)[:10]
            serializer = PatientSerializer(patientList, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        else:
            return Response({'detail':'Something went wrong','exception':'No or unexpected params in GET'}, status=status.HTTP_400_BAD_REQUEST)

            """#No or generic params in GET
            if not request.query_params: #no params
                return Response({'detail':'Something went wrong','exception':'No params in GET'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                kwargs = {}
                for item in request.query_params:
                    key = '{0}__{1}'.format(item, 'icontains')
                    kwargs[key] = request.query_params[item]
                patientList = Patient.objects.filter(**kwargs)[:10]
                serializer = PatientSerializer(patientList, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK) """


        returnDict = getPatientDetails(graph, queryset)
        return Response(returnDict, status=status.HTTP_200_OK)

        #except Exception,e:
        #    print '[corePatient] Exception',e
        #    return Response({'detail':'Something went wrong', 'exception':str(e)}, status=status.HTTP_400_BAD_REQUEST)




    def create(self, request):
        print '[corePatient/POST] - incoming request...\n', json.dumps(request.data, sort_keys=True, indent=4, separators=(',', ': '))
        noEmptyValueDict = {k:v for k,v in request.data.items() if v}
        timeToSave = timezone.localtime(timezone.now())
        try:
            p = checkPostData(noEmptyValueDict)
            if p == -1: # Conflict with existing data
                raise Exception('[corePatient] Patient already exists')

            u = uuid4()
            newIdentifier = u.hex # create universally unique identifier for the patient
            noEmptyValueDict['identifier'] = newIdentifier
            noEmptyValueDict['vitalStatus'] = 'ok'
            serializer = PatientSerializer(data=noEmptyValueDict, partial=True) #many=True
            if serializer.is_valid(raise_exception=True): #rise Exception if serializer fails (e.g. bad data format)
                #Save in relational DB
                serializer.save()
                print '[corePatient] patient',newIdentifier,'created in DBMS'
            try:
                graph = getGraphInstance(settings.GRAPH_DB_URL)
                batch = neo4j.WriteBatch(graph)
                # check if WG exists (ownership)
                query = neo4j.CypherQuery(graph,"MATCH (wg:WG) where wg.identifier='"+noEmptyValueDict['ownership']+"' return wg ")
                r = query.execute()
                if len(r.data) == 0:
                    raise Exception('[corePatient] Error: owner WG does not exists',str(noEmptyValueDict['ownership']))
                ownsNode = r.data[0]['wg']

                if 'sharings' in noEmptyValueDict: # Sharing exists
                    #pNode = Node("Patient", identifier=newIdentifier)
                    pNode = batch.create(node(identifier=newIdentifier))
                    batch.add_labels(pNode, 'Patient')
                    sharingDict = updateSharing(graph, batch, pNode, noEmptyValueDict['sharings'], timeToSave)
                    ownsRel = rel(ownsNode,'OwnsData', pNode, {'startDate': timeToSave})
                    batch.create(ownsRel)
                    batch.submit()
                    batch.clear()
                    socialData = {'ownership':noEmptyValueDict['ownership'],'sharings':sharingDict['newSharings']}


                else: # NO Sharing
                    #pNode = Node("Patient", identifier=newIdentifier)
                    pNode = batch.create(node(identifier=newIdentifier))
                    batch.add_labels(pNode, 'Patient')
                    ownsRel = rel(ownsNode,'OwnsData', pNode, {'startDate': timeToSave})
                    batch.create(ownsRel)
                    batch.submit()
                    batch.clear()
                    socialData = {'ownership':noEmptyValueDict['ownership'],'sharings':None}

                print '[corePatient] patient',newIdentifier,'created in Graph'
                returnDict = serializer.data
                returnDict.update(socialData)
                return Response(returnDict, status=status.HTTP_201_CREATED)
            except Exception,e:
                print '[corePatient] patient',newIdentifier,'encountered an error in creating Graph node',e
                p = Patient.objects.get(identifier = newIdentifier)
                p.delete()
                print '[corePatient] patient',newIdentifier,'deleted from DBMS'
                raise Exception('[corePatient] error while creating patient in Graph',e)

        except Exception,e:
            return Response({'detail':'Something went wrong', 'exception':str(e)}, status=status.HTTP_400_BAD_REQUEST)




    def put(self, request, pk=None):
        print '[corePatient/PUT] - incoming request...\n', json.dumps(request.data, sort_keys=True, indent=4, separators=(',', ': '))
        timeToSave = timezone.localtime(timezone.now())
        try:
            graph = getGraphInstance(settings.GRAPH_DB_URL)
            batch = neo4j.WriteBatch(graph)
            p = getPatientByIdentifier(graph, pk)
            if p == -1: #graph and DBMS are not aligned
                return Response({'detail':'Conflict beetwen DBMS and Graph'},status=status.HTTP_409_CONFLICT)
            elif p == 0:
                raise Http404('No matching patient')
            else:
                query = neo4j.CypherQuery(graph,"match (wg:WG)-[r]-(p:Patient) where p.identifier='"+pk+"' return wg, p")
                r = query.execute()
                if len(r.data) == 0:
                    raise Exception('[corePatient] Error: no social data')

                pNode = r.data[0]['p']
                oldSocial = []

                for item in r.data:
                    oldSocial.append(item['wg']['identifier'])

                newSharings = list(set(request.data['sharings']) - set(oldSocial))
                print newSharings
                if newSharings:
                    returnDict = updateSharing(graph, batch, pNode, newSharings, timeToSave)
                    batch.submit()
                    batch.clear()
                else:
                    returnDict = {'newSharings':None}
                return Response(returnDict, status=status.HTTP_200_OK)
        except Exception,e:
            return Response({'detail':'Something went wrong', 'exception':str(e)}, status=status.HTTP_400_BAD_REQUEST)





    def destroy(self, request, pk=None):
        print '[corePatient] delete patient by UUID:', pk
        #print '[corePatient] incoming data   ---------->', request.data
        sharings = request.query_params.get('sharings', None)
        print '[corePatient] additional data   ---------->', sharings
        try:
            graph = getGraphInstance(settings.GRAPH_DB_URL)

            if sharings != None: #delete some sharing relationships
                wgList = sharings.split(',')
                print 'wgList',wgList
                for item in wgList: #check if data exist (waiting for batch...)
                    print pk,item
                    #print item
                    query = neo4j.CypherQuery(graph,"match (wg:WG)-[r:SharesData]-(p:Patient) where p.identifier='"+pk+"' and wg.identifier='"+item+"' return r")
                    if len(r.data) == 0:
                        raise Exception('[corePatient] Error: data are not aligned',str(item))

                for item in wgList: #delete
                    #print item
                    query = neo4j.CypherQuery(graph,"match (wg:WG)-[r:SharesData]-(p:Patient) where p.identifier='"+pk+"' and wg.identifier='"+item+"' delete r return 'ok' as c")
                    r = query.execute()
                    if len(r.data) == 0:
                        raise Exception('[corePatient] Error while deleting relations of patient',str(pk),',', str(item),'. Perform manual rollback!')
                returnDict = {'deletedSharings':wgList}
                return Response(status=status.HTTP_200_OK)


            else: #delete patient

                p = getPatientByIdentifier(graph, pk)

                #print p
                if p == -1: # graph and DBMS are not aligned
                    return Response({'detail':'Conflict beetwen DBMS and Graph'},status=status.HTTP_409_CONFLICT)
                elif p == 0:
                    raise Http404('No matching patient')
                else:

                        serializer = PatientSerializer(p)
                        p.delete()
                        print '[corePatient] patient',pk,'deleted from DBMS'
                        try:
                            # Delete node with all social relations
                            query = neo4j.CypherQuery(graph,"MATCH (pa:Patient), (wg:WG)-[r]->(pa) where pa.identifier='"+pk+"'delete r,pa return 'ok' as c")
                            r = query.execute()
                            if len(r.data)==0:
                                raise Exception('[corePatient] data do not match delete criteria')
                            print '[corePatient] patient',pk,'deleted from Graph'
                            return Response(serializer.data, status=status.HTTP_200_OK)
                        except:
                            serializer = PatientSerializer(data=serializer.data, partial=True)
                            serializer.is_valid()
                            # rollback in DBMS
                            serializer.save()
                            print '[corePatient] error while deleting patient in Graph. Rollback...'
                            raise Exception('error while deleting patient in Graph')
        except Exception,e:
            return Response({'detail':'Something went wrong', 'exception':str(e)}, status=status.HTTP_400_BAD_REQUEST)



# TODO This ViewSet should be merged with PatientViewSet. This new one does exist just to avoid backward compatibility problems for server side requests

class PatientMergingViewSet(viewsets.ViewSet):
    """
    #A viewset for merging patient instances.
    """

    authentication_classes = (SessionCsrfExemptAuthentication, BasicAuthentication) # manager both session and non-session based authentication to the same views


    def retrieve(self, request, pk=None):
        print '[corePatient] get patient by UUID:', pk
        graph = getGraphInstance(settings.GRAPH_DB_URL)
        p = getPatientByIdentifier(graph, pk)
        if p == -1: #graph and DBMS are not aligned
            return Response({'detail':'Conflict beetwen DBMS and Graph'},status=status.HTTP_409_CONFLICT)
        elif p == 0:
            raise Http404('No matching patient')
        else:
            returnDict = getPatientDetails(graph, p)

            mergedList = MergedPatient.objects.filter(patient = p).order_by('-mergingDate')
            if len(mergedList) >0:
                returnDict['mergedList'] = []
                for m in mergedList:
                    returnDict['mergedList'].append({'mergedWith':m.identifier,'mergedOn':m.mergingDate})
            else:
                returnDict['mergedList'] = None


            return Response(returnDict, status=status.HTTP_200_OK)


    def list(self, request):

        details     = request.query_params.get('details', None)
        disableGraph= request.query_params.get('disableGraph', None)


        if details is not None:

            print "[PatientMergingViewSet] looking for '"'{0}'"' in patients' firstName, lastName or fiscalCode".format(details)
            searchKeywords = details.split()
            args = []

            if disableGraph:
                disable_graph()

            for item in searchKeywords:
                key = ( Q(firstName__icontains = item) | Q(lastName__icontains = item) | Q(fiscalCode__icontains = item) )
                args.append(key)

            if disableGraph:
                enable_graph()

            patientList = Patient.objects.filter(*args)[:10]
            returnList = []
            for p in patientList:
                pat = {}
                pat['id'] = p.id
                pat['identifier'] = p.identifier
                pat['firstName'] = p.firstName
                pat['lastName'] = p.lastName
                pat['birthDate'] = p.birthDate
                pat['birthNation'] = p.birthNation
                pat['birthPlace'] = p.birthPlace
                pat['fiscalCode'] = p.fiscalCode
                pat['race'] = p.race
                pat['residenceNation'] = p.residenceNation
                pat['residencePlace'] = p.residencePlace
                pat['sex'] = p.sex
                pat['vitalStatus'] = p.vitalStatus
                mergedList = MergedPatient.objects.filter(patient = p).order_by('-mergingDate')
                if len(mergedList) >0:
                    pat['mergedList'] = []
                    for m in mergedList:
                        pat['mergedList'].append({'mergedWith':m.identifier,'mergedOn':m.mergingDate})
                else:
                    pat['mergedList'] = None


                returnList.append(pat)
            #serializer = PatientSerializer(patientList, many=True)
            return Response(returnList, status=status.HTTP_200_OK)

        else:
            return Response({'detail':'Something went wrong','exception':'No or unexpected params in GET'}, status=status.HTTP_400_BAD_REQUEST)



    def put(self, request):

        class Relationship(object):

          def __init__(self, rel_type, node, rel_direction, properties):
            self.rel_type = rel_type
            self.node = node
            self.rel_direction = rel_direction
            self.properties = properties

          def __repr__(self):
            return "Relationship(%s, %s, %s)" % (self.rel_type, self.node, self.rel_direction)

          def __eq__(self, other):
            if isinstance(other, Relationship):
              return ((self.rel_type == other.rel_type) and (self.node == other.node) and (self.rel_direction == other.rel_direction))
            else:
              return False

          def __ne__(self, other):
            return not self == other

          def __hash__(self):
            return hash(self.__repr__())


        print '[corePatient_Merging/PUT] - incoming request...\n', json.dumps(request.data, sort_keys=True, indent=4, separators=(',', ': '))

        timeToSave = timezone.localtime(timezone.now())
        print timeToSave

        try:

            old_patient = request.data['old']
            new_patient = request.data['new']

            p_old = Patient.objects.get(identifier=old_patient)
            print '[corePatient_Merging/PUT] old patient UUID',p_old.identifier
            p_new = Patient.objects.get(identifier=new_patient)
            print '[corePatient_Merging/PUT] new patient UUID',p_new.identifier






            # merging the graph
            graph = getGraphInstance(settings.GRAPH_DB_URL)


            cypher = """
                        match (p:Patient {{identifier:'{}'}})-[rel]-(node)
                        return rel,node, CASE WHEN STARTNODE(rel) = p THEN 'outgoing' ELSE 'incoming' END AS direction
                     """

            query = neo4j.CypherQuery(graph,cypher.format(old_patient))
            r = query.execute()

            old = set()

            for item in r.data:
                r = Relationship(item['rel'].type, item['node']._id, item['direction'], item['rel'].get_properties())
                old.add(r)


            query = neo4j.CypherQuery(graph,cypher.format(new_patient))
            r = query.execute()

            new = set()

            for item in r.data:
                r = Relationship(item['rel'].type, item['node']._id, item['direction'], item['rel'].get_properties())
                new.add(r)


            # batch here
            batch = neo4j.WriteBatch(graph)
            # delete old patient
            batch.append_cypher( """match (p:Patient {{identifier:'{}'}})-[rel]-() delete p,rel""".format(old_patient) )
            # copy differential relations
            for rel in old-new:
                if rel.rel_direction == 'outgoing':
                    cypher = """
                                match (p:Patient {{identifier:'{new_patient}'}}),(n) WHERE ID(n) = {node}
                                create (p)-[:{rel_type} {properties}]->(n)
                             """
                else:
                    cypher = """
                                match (p:Patient {{identifier:'{new_patient}'}}),(n) WHERE ID(n) = {node}
                                create (n)-[:{rel_type} {properties}]->(p)
                             """


                c =  cypher.format(new_patient=new_patient, node=rel.node, rel_type=rel.rel_type, properties="{" + ",".join(["%s : \"%s\"" % (k,v) for k,v in rel.properties.iteritems()]) + "}")
                # print c
                batch.append_cypher(c)

            batch.submit()
            batch.clear()


            # update merging on mysql
            new_merged = MergedPatient()

            new_merged.identifier = p_old.identifier
            new_merged.firstName = p_old.firstName
            new_merged.lastName = p_old.lastName
            new_merged.birthDate = p_old.birthDate
            new_merged.birthNation = p_old.birthNation
            new_merged.birthPlace = p_old.birthPlace
            new_merged.fiscalCode = p_old.fiscalCode
            new_merged.race = p_old.race
            new_merged.residenceNation = p_old.residenceNation
            new_merged.residencePlace = p_old.residencePlace
            new_merged.sex = p_old.sex
            new_merged.vitalStatus = p_old.vitalStatus
            new_merged.patient = p_new
            new_merged.mergingDate = timeToSave

            new_merged.save()
            p_old.delete()


            # update biobank
            print "[corePatient_Merging/PUT] updating Biobank"
            biobank_dict = {'dictalias' : {} }
            for item in new.intersection(old):
                if item.rel_type == 'hasAlias':

                    # get project
                    cypher = """
                                match (p:Project) where ID(p)={} return p
                             """
                    query = neo4j.CypherQuery(graph,cypher.format(item.node))
                    r = query.execute()
                    project = r.data[0]['p']['identifier']

                    for rel in old:
                        if rel.rel_type == 'hasAlias' and rel.node == item.node:
                            old_alias = rel.properties['localId']
                    for rel in new:
                        if rel.rel_type == 'hasAlias' and rel.node == item.node:
                            new_alias = rel.properties['localId']

                    biobank_dict['dictalias'][project] = {old_alias:new_alias}

            # call the biobank just if necessary
            if bool(biobank_dict['dictalias']) != False: # Empty dictionaries evaluate to False in Python:

                print "Updates:\n", json.dumps(biobank_dict, sort_keys=True, indent=4, separators=(',', ': '))

                headers = {'Content-type': 'application/json'}
                r = requests.post(settings.DOMAIN_URL+'/biobank/api/alias/change/', data=json.dumps(biobank_dict), headers=headers, verify=False)
                responseData = r.json()
                #print responseData
                if responseData['message'] != 'ok':
                    raise Exception('[corePatient_Merging/PUT] error while updating Biobank')
            else:
                print "No updates in biobank"





            # log the merge
            with open(settings.TEMP_URL+'corePatient_merging.txt', 'a') as myfile:
                myfile.write('\n\n')
                myfile.write('Merging on: ')
                myfile.write(timeToSave.strftime('%d/%m/%Y %H:%M:%S\n'))
                myfile.write('old_patient: {}\n'.format(old_patient))
                for rel in old:
                    myfile.write('{}, {}, {}, {}\n'.format(rel.rel_direction, rel.rel_type, rel.node, rel.properties))
                myfile.write('new_patient: {}\n'.format(new_patient))
                for rel in new:
                    myfile.write('{}, {}, {}, {}\n'.format(rel.rel_direction, rel.rel_type, rel.node, rel.properties))
                myfile.write('Added to new:\n')
                for rel in old-new:
                    myfile.write('{}, {}, {}, {}\n'.format(rel.rel_direction, rel.rel_type, rel.node, rel.properties))
                myfile.write('\n\n\n')



            # return new patient
            pat = {}
            pat['id'] = p_new.id
            pat['identifier'] = p_new.identifier
            pat['firstName'] = p_new.firstName
            pat['lastName'] = p_new.lastName
            pat['birthDate'] = p_new.birthDate
            pat['birthNation'] = p_new.birthNation
            pat['birthPlace'] = p_new.birthPlace
            pat['fiscalCode'] = p_new.fiscalCode
            pat['race'] = p_new.race
            pat['residenceNation'] = p_new.residenceNation
            pat['residencePlace'] = p_new.residencePlace
            pat['sex'] = p_new.sex
            pat['vitalStatus'] = p_new.vitalStatus
            mergedList = MergedPatient.objects.filter(patient = p_new).order_by('-mergingDate')
            if len(mergedList) >0:
                pat['mergedList'] = []
                for m in mergedList:
                    pat['mergedList'].append({'mergedWith':m.identifier,'mergedOn':m.mergingDate})
            else:
                pat['mergedList'] = None


            return Response(pat, status=status.HTTP_200_OK)

        except Exception,e:
            return Response({'detail':'Something went wrong', 'exception':str(e)}, status=status.HTTP_400_BAD_REQUEST)
