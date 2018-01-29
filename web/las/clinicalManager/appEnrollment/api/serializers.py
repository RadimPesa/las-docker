from collections import OrderedDict
from corePatient.models import Patient
from rest_framework import serializers
from uuid import uuid4
import json



class EnrollmentSerializer(serializers.Serializer):
    identifier      =   serializers.CharField(max_length=30) 
    operator        =   serializers.CharField(max_length=30)
    firstName       =   serializers.CharField(max_length=30)  
    lastName        =   serializers.CharField(max_length=30)
    fiscalCode      =   serializers.CharField(max_length=16)
    birthDate       =   serializers.DateField()
    birthPlace      =   serializers.CharField(max_length=30)
    sex             =   serializers.CharField(max_length=1)
    race            =   serializers.CharField(max_length=30)
    residencePlace  =   serializers.CharField(max_length=30)
    medicalCenter   =   serializers.CharField(max_length=30)
    urlIC           =   serializers.URLField(max_length=200)
    ICcode          =   serializers.CharField(max_length=30) 
    project         =   serializers.CharField(max_length=30)


#Dealing with nested objects
class PatientsSerializer(serializers.Serializer):  
    
    patients = EnrollmentSerializer(many=True)
    
    def create(self, validated_data):

        l = []
        fields = {
                    'firstName',
                    'lastName',
                    'fiscalCode',
                    'birthDate',
                    'birthPlace',
                    'sex',
                    'race',
                    'residencePlace'
        }

        for patient in validated_data['patients']:

            #Adding Patient Data
            if not ( Patient.objects.filter(fiscalCode=patient['fiscalCode'], firstName=patient['firstName'], lastName=patient['lastName']) ): 

                p = {key:value for key,value in patient.items() if key in fields}                        
                u = uuid4() 
                globalIdentifier = u.hex #universally unique identifier for the patient
                p['identifier'] = globalIdentifier
                p['vitalStatus']  = 'ok'
                #optional: convert dict into OrderedDict
                #p = OrderedDict(p)            
                l.append(p)
        print 'ciaosssssssssssssssss ' + l
        #pippo=json.dumps(l)
        #print pippo
        patientsList = [Patient(**item) for item in l]
   
        return Patient.objects.bulk_create(patientsList)
  



class PatientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient 
        fields = (
                    'identifier', 
                    'firstName',
                    'lastName',
                    'fiscalCode',
                    'birthDate',
                    'birthPlace',
                    'sex',
                    'race',
                    'residencePlace',
                    'vitalStatus'
        )

