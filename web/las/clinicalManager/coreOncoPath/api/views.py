# Create your views here.
from rest_framework import status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from coreOncoPath.api.serializers import OncoPathSerializer
from coreOncoPath.models import OncoPath, Feature
from py2neo import *
from django.conf import settings



class OncoPathViewSet(viewsets.ModelViewSet):
    """
    [CoreOncoPath API]
    """
    #serializer_class = PatientSerializer
    #queryset = OncoPath.objects.all()
    serializer_class = OncoPathSerializer
    lookup_field = 'identifier'

    def get_queryset(self):
        queryset = OncoPath.objects.all()
        patient = self.request.query_params.get('patient', None)

        if patient is not None:

            graph = neo4j.GraphDatabaseService(settings.GRAPH_DB_URL)
            try:
                patient_node = next(graph.find('Patient', 'identifier', patient)) # graph.find() returns a generator object
            except StopIteration:
                print "Patient '{0}' does not exist in graph".format(pk)
                raise
            pass

            rel_affectedBy_generator = graph.match(start_node = patient_node, rel_type = "affectedBy")
            affectedBy_list = list(x.end_node['identifier'] for x in rel_affectedBy_generator if 'OncoPath' in x.end_node.get_labels())
            queryset = queryset.filter(identifier__in = affectedBy_list)


        return queryset



class OncoPathDictsViewSet(viewsets.ViewSet):
    """
    [CoreOncoPath API] - Get dicts
    """

    def retrieve(self, request, pk = None):

        def buildDict(fatherName, fatherId):
            returnDict = {}
            childrenList = []
            children = Feature.objects.filter(fatherFeatureId = fatherId)

            for item in children:
                #print "{0} in analisi".format(item.name)
                if item.dataType == 'complex':
                    subdict = buildDict(item.name, item.id)
                    childrenList.append(subdict)
                else:
                    childrenList.append({'id':item.id, 'name' : item.name})

            returnDict[fatherName] = childrenList
            return returnDict

        level0 = get_object_or_404(Feature, shortName = pk)
        queryset = buildDict(level0.name, level0.id)
        return Response(queryset, status=status.HTTP_200_OK)
