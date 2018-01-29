from corePatient.models import Patient
from rest_framework import serializers

class PatientSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Patient

