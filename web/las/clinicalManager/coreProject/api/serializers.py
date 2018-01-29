from coreProject.models import Project
from rest_framework import serializers

class ProjectSerializer(serializers.ModelSerializer):

    class Meta:
        model = Project


class IcListClass(object):
    def __init__(self, icCode, medicalCenter):
        self.icCode        = icCode
        self.medicalCenter  = medicalCenter


class PatientsByProjectClass(object):
    def __init__(self, firstName, lastName, fiscalCode, gender, vitalStatus, patientId, alias):
        self.icList      = []
        self.patientId   = patientId
        self.firstName   = firstName
        self.lastName    = lastName
        self.fiscalCode  = fiscalCode
        self.gender      = gender
        self.vitalStatus = vitalStatus
        self.alias       = alias

    def addIc(self, ic):
        self.icList.append(ic)


class IcListSerializer(serializers.Serializer):
    icCode         = serializers.CharField(max_length=200)
    medicalCenter  = serializers.CharField(max_length=200)


class PatientsByProjectClassSerializer(serializers.Serializer):
    icList      = IcListSerializer(many=True, read_only=True)
    patientId   = serializers.CharField(max_length=200)
    firstName   = serializers.CharField(max_length=200)
    lastName    = serializers.CharField(max_length=200)
    fiscalCode  = serializers.CharField(max_length=200)
    gender      = serializers.CharField(max_length=200)
    vitalStatus = serializers.CharField(max_length=200)
    alias       = serializers.CharField(max_length=200)
