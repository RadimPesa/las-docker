from coreInstitution.models import Institution
from rest_framework import serializers

class InstitutionSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Institution
