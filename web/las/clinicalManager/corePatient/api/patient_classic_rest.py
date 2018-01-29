from rest_framework import viewsets
from corePatient.api.serializers import PatientSerializer
from corePatient.models import Patient
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authentication import BasicAuthentication
from appUtils.csrf_exempt import *

class PatientViewSet(viewsets.ModelViewSet):
    """
    A simple ViewSet for viewing and editing accounts.
    """
    authentication_classes = (SessionCsrfExemptAuthentication, BasicAuthentication) # manager both session and non-session based authentication to the same views
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer
    lookup_field = 'identifier'
