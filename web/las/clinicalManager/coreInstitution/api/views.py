from coreInstitution.api.serializers import InstitutionSerializer
from coreInstitution.models import Institution
from rest_framework import viewsets
from rest_framework import status
from rest_framework.response import Response
from py2neo import *
from django.conf import settings
from operator import itemgetter



class InstitutionViewSet(viewsets.ViewSet):
    """
    A simple ViewSet for viewing projects.
    """
    #queryset = Project.objects.list()
    #serializer_class = ProjectSerializer
    
    def list(self, request):
        queryset = Institution.objects.all()
        serializer = InstitutionSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def retrieve(self, request, pk=None):
        #print 'debugggggggggggggggggggggggggggggggggggggggggggggggggg',pk
        graph = neo4j.GraphDatabaseService(settings.GRAPH_DB_URL)  
        query = neo4j.CypherQuery(graph, "MATCH (in:Institution)-[:participates]->(pr:Project) where pr.identifier='"+pk+"' return in.identifier as in")
        r = query.execute()
        if len(r.data)==0:
            return Response({'detail':'Not Found'}, status=status.HTTP_404_NOT_FOUND)
        else:
            queryset = []
            try:
                for item in r.data:
                    print item['in']
                    i = Institution.objects.get(identifier=item['in'])
                    queryset.append(i)
                serializer = InstitutionSerializer(queryset, many=True)
                sortedData = sorted(serializer.data, key=itemgetter('name'))
                return Response(sortedData, status=status.HTTP_200_OK)
            except Institution.DoesNotExist:
                return Response({'detail':'Conflict beetwen DBMS and Graph'},status=status.HTTP_409_CONFLICT)
