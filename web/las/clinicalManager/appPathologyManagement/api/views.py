from rest_framework import viewsets, status
from rest_framework.response import Response
from django.contrib.auth.models import User
from django.utils import timezone
from django.db import transaction
from coreOncoPath.models import OncoPath
from appPathologyManagement.models import Entity, UPhaseEntity
from appPathologyManagement.api.utils import *
from uuid import uuid4
import json
from rest_framework.authentication import BasicAuthentication
from appUtils.csrf_exempt import *


class OncoPathViewSet(viewsets.ViewSet):
    """
    [appPathologyManagement] Endpoint for managing OncoPath
    """
    # payload example: { "operator" : "andrea.mignone", "name" : "patologia test", "status": True,  "patient" : "1"}
    # requests.post("https://lastest.polito.it/clinical/appPathologyManagement/api/oncoPathManagement/", data= json.dumps(payload),verify = False, headers=headers)

    authentication_classes = (SessionCsrfExemptAuthentication, BasicAuthentication) # manager both session and non-session based authentication to the same views

    """
    @transaction.commit_on_success
    If the function returns successfully, then Django will commit all work done within the function at that point.
    If the function raises an exception, though, Django will roll back the transaction.
    """
    @transaction.commit_on_success
    def create(self, request):
        incomingData = request.data
        timeToSave = timezone.localtime(timezone.now())
        print '\n\n-------------|||START|||-------------'
        print '[appPathologyManagement/POST] - incoming request at {0}...\n'.format(timeToSave), json.dumps(incomingData, sort_keys=True, indent=4, separators=(',', ': '))
        try:
            # oncoPath Data
            n = incomingData['name']
            p = incomingData['patient']
            s = incomingData.get('status') # get status or return None (status is optional)

            # create uPhaseData for this App
            identifier = uuid4().hex
            operator = User.objects.get(username = incomingData['operator'])
            entity = Entity(identifier = identifier, belongingCore = 'coreOncoPath')
            entity.save()
            uPhaseEntity = UPhaseEntity(entity=entity, uPhase = 'Generate', startTimestamp = timeToSave, endTimestamp = timeToSave, startOperator = operator, endOperator = operator)
            uPhaseEntity.save()

            # uPhaseData for coreOncoPath
            uPhaseDataDict = createUPhaseData(uPhaseType = 'Generate', time = timeToSave, operator = operator, uPhaseId = uPhaseEntity, dictionary = incomingData)
            print uPhaseDataDict

            # create new OncoPath obj
            o = OncoPath(name = n, status = s, identifier = identifier)

            # save obj
            o.save(patient = p, uPhaseData = uPhaseDataDict)
        except Exception, e:
            return Response({'exception' : str(e)}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'id': o.id, 'identifier': o.identifier, 'name': o.name, 'status':o.status}, status=status.HTTP_200_OK)

    """
    @transaction.commit_on_success
    If the function returns successfully, then Django will commit all work done within the function at that point.
    If the function raises an exception, though, Django will roll back the transaction.
    """
    @transaction.commit_on_success
    def update(self, request, pk = None):
        #request example: r = requests.put("https://lastest.polito.it/clinical/appPathologyManagement/api/oncoPathManagement/p1/", data= json.dumps(payload),verify = False, headers=headers)
        incomingData = request.data
        timeToSave = timezone.localtime(timezone.now())
        print '\n\n-------------|||START|||-------------'
        print '[appPathologyManagement/PUT] - incoming request for patient {0} at {1}...\n'.format(pk, timeToSave), json.dumps(incomingData, sort_keys=True, indent=4, separators=(',', ': '))
        try:
            # get existing OncoPath
            o = OncoPath.objects.get(identifier = pk)

            n = incomingData.get('name') # get name or return None
            if n is not None:
                print "preparing name update from {0} to {1}".format(o.name,n)
                o.name = n

            s = incomingData.get('status') # get status or return None
            if s is not None:
                print "preparing status update from {0} to {1}".format(o.status,s)
                o.status = s


            entity = Entity.objects.get(identifier = pk)
            operator = User.objects.get(username = incomingData['operator'])

            # create uPhaseData for this App
            uPhaseEntity = UPhaseEntity(entity=entity, uPhase = 'Update', startTimestamp = timeToSave, endTimestamp = timeToSave, startOperator = operator, endOperator = operator)
            uPhaseEntity.save()

            # uPhaseData for coreOncoPath
            uPhaseDataDict = createUPhaseData(uPhaseType = 'Update', time = timeToSave, operator = operator, uPhaseId = uPhaseEntity, dictionary = incomingData)
            print uPhaseDataDict

            # update obj
            o.save(uPhaseData = uPhaseDataDict)

        except OncoPath.DoesNotExist:
            return Response({'exception' : 'OncoPath "{0}" DoesNotExist'.format(pk)}, status=status.HTTP_404_NOT_FOUND)

        except Exception, e:
            return Response({'exception' : str(e)}, status=status.HTTP_400_BAD_REQUEST)

        else:
            return Response({'status':'200'}, status=status.HTTP_200_OK)
        pass
