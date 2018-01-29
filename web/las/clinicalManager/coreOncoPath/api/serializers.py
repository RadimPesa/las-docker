from coreOncoPath.models import OncoPath
from rest_framework import serializers

class OncoPathSerializer(serializers.ModelSerializer):

    # model fields
    class Meta:
        model = OncoPath
