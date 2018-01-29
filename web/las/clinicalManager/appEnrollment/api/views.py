from rest_framework import viewsets
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.response import Response
from rest_framework import status
#from py2neo import *#Graph
from django.conf import settings
from appEnrollment.api.utils import *
from appEnrollment.models import *
from appUtils.lasEmail import *
from django.core.mail import EmailMessage
import json
import requests
from django.utils import timezone
from py2neo import *
#from clinical.models import *
from rest_framework.authentication import BasicAuthentication
from appUtils.csrf_exempt import *



class EnrollmentViewSet(viewsets.ViewSet):
    """
    A simple API about Enrollment...
    """
    authentication_classes = (SessionCsrfExemptAuthentication, BasicAuthentication) # manager both session and non-session based authentication to the same views

    def create(self, request, format=None):
        print '\n\n-------------|||START|||-------------'
        print '[appEnrollment/POST] - incoming request...\n', json.dumps(request.data, sort_keys=True, indent=4, separators=(',', ': '))

        try:
            patientUrl = settings.DOMAIN_URL+'/clinical/corePatient/api/patient/'
            projectUrl = settings.DOMAIN_URL+'/clinical/coreProject/api/informedConsent/'
            headers = {'Content-type': 'application/json'}
            sessionLog = []
            mailingList = []
            #requests.packages.urllib3.disable_warnings() #ignore warning messages in log
            #load features for attaches
            ft=Feature.objects.get(identifier='Informed Consent')
            pr=Feature.objects.get(identifier='Project')


            for item in request.data['patients']:
                #patientLog={}
                #patient = None
                timeToSave = timezone.localtime(timezone.now())
                item = {k:v for k,v in item.items() if v} # remove empty keys from a dictionary
                try:
                    operator = User.objects.get (username = item['operator'])
                except ObjectDoesNotExist:
                    raise Exception('[appEnrollment] user does not exist')

                payload = {'ICcode': item['ICcode'], 'project': item['project'] }
                r = requests.get(projectUrl, params=payload, verify=False)
                sc = r.status_code
                print 'Does IC exist?',sc

                if sc == 200:
                    print 'skipping', item
                    # update social data
                    # - only for requests from Gene Sender
                    # - (rollback for this operation is not available)
                    try:
                        user = User.objects.get(username=operator)
                        wg = WG_User.objects.get(user = user, permission = Permission.objects.get(codename = 'can_view_CMM_patient_enrollment'))
                        wgName = wg.WG.name
                    except WG_User.DoesNotExist:
                        raise Exception('user not allowed')
                    except WG_User.MultipleObjectsReturned:
                        #LOGICA DI UNIVOCITA WG
                        wg=AppEnrollmentUserWG.objects.get(user=User.objects.get(username=operator),projectID=item['project'])
                        wgName = wg.WG.name

                    try:
                        graph = getGraphInstance(settings.GRAPH_DB_URL)

                        query = neo4j.CypherQuery(graph,"MATCH (i:IC)-[]-(pr:Project),(i)-[]-(p:Patient) where i.icCode=~ '(?i)"+item['ICcode']+"' and pr.identifier='"+item['project']+"' return i as ic, p as patient")
                        r_social = query.execute()
                        ic_node = r_social.data[0]['ic']
                        pat_node = r_social.data[0]['patient']
                        print ic_node
                        print pat_node

                        query = neo4j.CypherQuery(graph,"MATCH (w:WG) where w.identifier='"+wgName+"' return w as wg")
                        r_social = query.execute()
                        wg_node = r_social.data[0]['wg']

                        batch = neo4j.WriteBatch(graph)
                        # update social data for IC
                        ic_old_rel = graph.match_one(start_node = wg_node, end_node = ic_node)
                        if ic_old_rel is None:
                            icRel = rel(wg_node,'SharesData', ic_node, {'startDate': timeToSave})
                            batch.create(icRel)
                        else:
                            pass

                        # update social data for Patient
                        pat_old_rel = graph.match_one(start_node = wg_node, end_node = pat_node)
                        if pat_old_rel is None:
                            patRel = rel(wg_node,'SharesData', pat_node, {'startDate': timeToSave})
                            batch.create(patRel)
                        else:
                            pass

                        batch.submit()
                        batch.clear()
                        with open(settings.TEMP_URL+'appEnrollment_skipLog.txt', 'a') as myfile:
                            myfile.write('\n')
                            myfile.write('\n')
                            myfile.write('Properly skipped on: ')
                            myfile.write(timeToSave.strftime('%d/%m/%Y %H:%M:%S'))
                            myfile.write('\n')
                            myfile.write(json.dumps(item, sort_keys=True, indent=4, separators=(',', ': ')))
                            print 'appEnrollment_skipLog: file ok'

                    except Exception,e:
                        print '[appEnrollment] - Error in social update of existing IC (no rollback available)',e

                        subject="[LAS/ClinicalManager/AppEnrollment] Error while updating social data for Patient (i.e., skipping procedure)"
                        message="Dear All,\n\n\tI'm so sorry but I had a problem during social update of an existing IC (no rollback available).\n\nData received:\n\n"+json.dumps(item, sort_keys=True, indent=4, separators=(',', ': '))+"\n\nMy Exception is: "+str(e)+".\n(Further details in ../clinical_media/tempFiles/appEnrollment_skipLog.txt.)\n\nBest,\n\n--\nAppEnrollment"
                        message=message.encode('utf-8')
                        print "[appEnrollment] - skipping exception - sending mail..."
                        email = EmailMessage(subject,message,"",mailingList,"","","","","")
                        email.send(fail_silently=False)
                        print "[appEnrollment] - skipping exception - mail sent..."

                        with open(settings.TEMP_URL+'appEnrollment_skipLog.txt', 'a') as myfile:
                            myfile.write('\n')
                            myfile.write('\n')
                            myfile.write('Error while skipping on: ')
                            myfile.write(timeToSave.strftime('%d/%m/%Y %H:%M:%S'))
                            myfile.write('\n')
                            myfile.write('Details: '+str(e))
                            myfile.write('\n')
                            myfile.write(json.dumps(item, sort_keys=True, indent=4, separators=(',', ': ')))


                elif sc == 404:
                    # >>>>>> Generate or create Patient
                    # enrollment from BioBank
                    if 'collection' in item:
                        wgName = item['wg']
                        graph = getGraphInstance(settings.GRAPH_DB_URL)
                        socialDict = getSocialRels(graph, item['project'], wgName)
                        print 'SocialDict',socialDict
                        item.update(socialDict)
                        if 'localId' in item: # data from BioBank for a specific patient
                            payload = {'localId': item['localId'], 'project': item['project']}
                            r = requests.get(patientUrl, params=payload, verify=False)

                            if r.status_code == 200: # existing patient
                                responseData = r.json()
                                patient = responseData['identifier']
                                e=Entity.objects.get(identifier=patient, belongingCore='corePatient')
                                patientLog = {'patient': None}

                                #<<<<<<<<<<< SOCIAL UPDATE
                                wgList = []
                                if socialDict['sharings'] != None:
                                    wgList = list(socialDict['sharings'])
                                wgList.append(socialDict['ownership']) # a flat list of WG for the Project + current user's WG
                                socialQuery = requests.put(patientUrl + patient + '/', data=json.dumps({'sharings' : wgList }), verify=False, headers=headers)
                                print 'response of socialQuery for existing patient',socialQuery.json()
                                if socialQuery.status_code == 200:
                                    if socialQuery.json()['newSharings'] != None:
                                        patientLog.update( {'newSharings' : {'patientUUIDRef' : patient, 'sharings': socialQuery.json()['newSharings'] } } )
                                    else:
                                        patientLog.update( {'newSharings' : None })
                                else:
                                    raise Exception('[appEnrollment] error while creating new social relationship for existing Patient')
                            else:
                                raise Exception('[appEnrollment] patient does not exist or his/her data are not aligned')

                        else: # new Patient
                            print socialDict
                            r = requests.post(patientUrl, data=json.dumps(socialDict), headers=headers, verify=False)
                            print '[appEnrollment] response from corePatient',r.status_code
                            if r.status_code == 201:
                                responseData = r.json()
                                patient = responseData['identifier']

                                e=Entity(identifier=patient, belongingCore='corePatient')
                                e.save()
                                upe=UPhaseEntity(entity=e, uPhase='Generate', startTimestamp = timeToSave, endTimestamp = timeToSave, startOperator = operator, endOperator= operator)
                                upe.save()
                                patientLog = {'patient': {'uuid':patient,'generateId':upe.id}, 'newSharings':None }
                            else:
                                raise Exception('[appEnrollment] error while creating new patient')
                        print 'patient---------------------------->',patient

                        # update Log
                        sessionLog.append(patientLog)
                        # >>>>>> Create IC
                        responseData = createIc(projectUrl, headers, patient, item)
                        print 'updating uPhase data for',item['ICcode']
                        upe=UPhaseEntity(entity=e,uPhase='Attach', startTimestamp = timeToSave, endTimestamp = timeToSave, startOperator = operator, endOperator = operator )
                        upe.save()
                        upeft=UPhaseEntityFeature(feature=ft, uPhaseEntity=upe, value = item['ICcode'])
                        upeft.save()
                        upepr=UPhaseEntityFeature(feature=pr, uPhaseEntity=upe, value = item['project'])
                        upepr.save()
                        # update Log
                        responseData.update({'attachId':upe.id})
                        sessionLog[-1].update({'IC':responseData})

                    # enrollment from Gene Sender
                    else:
                        graph = getGraphInstance(settings.GRAPH_DB_URL)
                        #TODO API
                        try:
                            user = User.objects.get(username=operator)
                            wg = WG_User.objects.get(user = user, permission = Permission.objects.get(codename = 'can_view_CMM_patient_enrollment'))
                            wgName = wg.WG.name
                        except WG_User.DoesNotExist:
                            raise Exception('user not allowed')
                        except WG_User.MultipleObjectsReturned:
                            #LOGICA DI UNIVOCITA WG
                            wg=AppEnrollmentUserWG.objects.get(user=User.objects.get(username=operator),projectID=item['project'])
                            wgName = wg.WG.name
                        socialDict = getSocialRels(graph, item['project'], wgName)
                        print 'SocialDict',socialDict
                        item.update(socialDict)
                        #if 'localId' in item: # data from BioBank for a specific patient
                        payload = {'firstName': item['firstName'], 'lastName': item['lastName'], 'fiscalCode': item['fiscalCode'] }
                        r = requests.get(patientUrl, params=payload, verify=False)
                        sc = r.status_code
                        print 'sc',sc
                        if sc == 200:
                            responseData = r.json()
                            patient = responseData['identifier']
                            e=Entity.objects.get(identifier=patient, belongingCore='corePatient')
                            patientLog = {'patient': None}

                            #<<<<<<<<<<< SOCIAL UPDATE
                            wgList = []
                            if socialDict['sharings'] != None:
                                wgList = list(socialDict['sharings'])
                            wgList.append(socialDict['ownership']) # a flat list of WG for the Project + current user's WG
                            socialQuery = requests.put(patientUrl + patient + '/', data=json.dumps({'sharings' : wgList }), verify=False, headers=headers)
                            print 'response of socialQuery for existing patient',socialQuery.json()
                            if socialQuery.status_code == 200:
                                if socialQuery.json()['newSharings'] != None:
                                    patientLog.update( {'newSharings' : {'patientUUIDRef' : patient, 'sharings': socialQuery.json()['newSharings'] } } )
                                else:
                                    patientLog.update( {'newSharings' : None })
                            else:
                                raise Exception('[appEnrollment] error while creating new social relationship for existing Patient')

                        elif sc == 404:
                            r = requests.post(patientUrl, data=json.dumps(item), headers=headers, verify=False)
                            print '[appEnrollment] response from corePatient',r.status_code
                            if r.status_code == 201:
                                responseData = r.json()
                                patient = responseData['identifier']
                                e=Entity(identifier=patient, belongingCore='corePatient')
                                e.save()
                                upe=UPhaseEntity(entity=e, uPhase='Generate', startTimestamp = timeToSave, endTimestamp = timeToSave, startOperator = operator, endOperator= operator)
                                upe.save()
                                patientLog = {'patient': {'uuid':patient,'generateId':upe.id}, 'newSharings':None }
                            else:
                                raise Exception('[appEnrollment] error while creating new patient')
                        else:
                            raise Exception('[appEnrollment] generic error')
                        print 'patient---------------------------->',patient
                        # update Log
                        sessionLog.append(patientLog)
                        # >>>>>> Create IC
                        responseData = createIc(projectUrl, headers, patient, item)
                        print 'updating uPhase data for',item['ICcode']
                        upe=UPhaseEntity(entity=e,uPhase='Attach', startTimestamp = timeToSave, endTimestamp = timeToSave, startOperator = operator, endOperator = operator )
                        upe.save()
                        upeft=UPhaseEntityFeature(feature=ft, uPhaseEntity=upe, value = item['ICcode'])
                        upeft.save()
                        upepr=UPhaseEntityFeature(feature=pr, uPhaseEntity=upe, value = item['project'])
                        upepr.save()
                        # update Log
                        responseData.update({'attachId':upe.id})
                        sessionLog[-1].update({'IC':responseData})
                else: # sc != 200 and sc != 400
                    raise Exception('[appEnrollment] generic error')

            print '[appEnrollment] --LOG--\n'
            for item in sessionLog:
                print json.dumps(item, sort_keys=True, indent=4, separators=(',', ': '))
            print '-------------|||END|||-------------'
            return Response({'status':'200'}, status=status.HTTP_200_OK)

        except Exception,e:
            #TODO send the following error via mail
            print'[appEnrollment] - exception in appEnrollment API:',e
            # save error in local log

            subject="[LAS/ClinicalManager/AppEnrollment] Error while enrolling new Patient"
            message="Dear All,\n\n\tI'm so sorry but I had a problem during Patient enrollment.\n\nData:\n\n"+json.dumps(request.data, sort_keys=True, indent=4, separators=(',', ': '))+"\n\nMy Exception is: "+str(e)+".\n(Further details in ../clinical_media/tempFiles/appEnrollment_errorLog.txt.)\nI'm going to try to rollback.\n\nBest,\n\n--\nAppEnrollment"
            message=message.encode('utf-8')
            print "[appEnrollment] - exception in appEnrollment API - sending mail..."
            email = EmailMessage(subject,message,"",mailingList,"","","","","")
            email.send(fail_silently=False)
            print "[appEnrollment] - exception in appEnrollment API - mail sent..."

            with open(settings.TEMP_URL+'appEnrollment_errorLog.txt', 'a') as myfile:
                myfile.write('\n')
                myfile.write('\n')
                myfile.write('Error on: ')
                myfile.write(timeToSave.strftime('%d/%m/%Y %H:%M:%S'))
                myfile.write('\n')
                myfile.write('Details: ')
                myfile.write(str(e))
                myfile.write('\n')
                myfile.write('Input: ')
                myfile.write(json.dumps(request.data, sort_keys=True, indent=4, separators=(',', ': ')))
                myfile.write('\n')
                myfile.write('-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.')


            print '[appEnrollment] - rollback using sessionLog:'
            count = 0
            for item in sessionLog:
                print 'rollback',count
                print json.dumps(item, sort_keys=True, indent=4, separators=(',', ': '))
                count += 1
            try:
                for item in sessionLog:
                    if 'IC' in item: # if an IC has been created, then delete it
                        rbData = item['IC']
                        if 'collection' in rbData: # BioBank
                            payload = {'ICcode':rbData['ICcode'], 'project': rbData['project'], 'patientUuid': rbData['patientUuid'], 'collection': rbData['collection'], 'medicalCenter': rbData['medicalCenter'], 'localId': rbData['localId']}

                        elif rbData['localId'] != None: # GeneSender: first enrollment for the patient in the project
                            payload = {'ICcode':rbData['ICcode'], 'project': rbData['project'], 'patientUuid': rbData['patientUuid'], 'localId': rbData['localId'], 'medicalCenter': rbData['medicalCenter']}

                        else: # GeneSender: further enrollment for the patient in the project
                            payload = {'ICcode':rbData['ICcode'], 'project': rbData['project'], 'patientUuid': rbData['patientUuid'], 'medicalCenter': rbData['medicalCenter']}

                        r = requests.delete(projectUrl, params=payload, verify = False)
                        if r.status_code != 200:
                            raise Exception('[appEnrollment] - error during rollback (coreProject)')
                        u = UPhaseEntity.objects.get(pk=rbData['attachId'])
                        upeft = UPhaseEntityFeature.objects.filter(uPhaseEntity=rbData['attachId']) # retrive all the features attached in this session
                        upeft.delete()
                        u.delete()
                        print '[appEnrollment] IC data deleted',rbData['ICcode']

                    #<<<<<<<<<<< Rollback of PUT (social only for existing Patient)
                    if item['newSharings'] != None: # if extra relationship(s) has been created for new  WG(s), then delete it
                        rbsData = item['newSharings']['patientUUIDRef']
                        wgRollbackList = item['newSharings']['sharings']
                        print 'removing sharings data {0} for patient {1}'.format(rbsData, wgRollbackList)
                        for w in wgRollbackList:
                        # PUT the following code into a Core
                            graph = neo4j.GraphDatabaseService(settings.GRAPH_DB_URL)
                            query = neo4j.CypherQuery(graph,"match (wg:WG)-[s:SharesData]->(p:Patient) where wg.identifier='"+w+"' and p.identifier='"+rbsData+"' delete s")
                            r = query.execute()
                            print '[appEnrollment] Social data removed: patient {0}, sharings {1}'.format(rbsData, w)
                        print 'All social relationship(s) for existing patient {0} has been removed'.format(rbsData)

                    if item['patient'] != None: # if a Patient has been created, then delete it
                        rbData = item['patient']
                        r = requests.delete(patientUrl+rbData['uuid'], verify = False)
                        if r.status_code != 200:
                            raise Exception('[appEnrollment] - error during rollback (corePatient)')
                        e=Entity.objects.get(identifier=rbData['uuid'], belongingCore='corePatient')
                        u = UPhaseEntity.objects.get(pk=rbData['generateId'])
                        u.delete()
                        e.delete()
                        print '[appEnrollment] patient data deleted',rbData['uuid']

                print '-------------|||END: Rollback ok|||-------------'
            except Exception,e:
                print '[AppEnrollment] error during rollback',e

                subject="[LAS/ClinicalManager/AppEnrollment] Error during rollback"
                message="Dear All,\n\n\tunfortunately there was an error during rollback of this transaction log:\n\n"+json.dumps(sessionLog, sort_keys=True, indent=4, separators=(',', ': '))+"\n\nMy Exception is: "+str(e)+".\n(Further details in ../clinical_media/tempFiles/appEnrollment_failedRollbackLog.txt.)\nI'm sorry.\n\nBest,\n\n--\nAppEnrollment"
                message=message.encode('utf-8')
                print "[appEnrollment] - error during rollback - sending mail..."
                email = EmailMessage(subject,message,"",mailingList,"","","","","")
                email.send(fail_silently=False)
                print "[appEnrollment] - error during rollback - mail sent..."

                with open(settings.TEMP_URL+'appEnrollment_failedRollbackLog.txt', 'a') as myfile:
                    myfile.write('\n')
                    myfile.write('\n')
                    myfile.write('Rollback failed on: ')
                    myfile.write(timeToSave.strftime('%d/%m/%Y %H:%M:%S'))
                    myfile.write('\n')
                    myfile.write('Details: ')
                    myfile.write(str(e))
                    myfile.write('\n')
                    myfile.write(json.dumps(sessionLog, sort_keys=True, indent=4, separators=(',', ': ')))

            return Response({'status': '400'}, status=status.HTTP_400_BAD_REQUEST)




    def put(self, request):
        patientUrl = settings.DOMAIN_URL+'/clinical/corePatient/api/patient/'
        #requests.packages.urllib3.disable_warnings() #ignore warning messages in log
        print '[appEnrollment/PUT] - incoming request...\n', json.dumps(request.data, sort_keys=True, indent=4, separators=(',', ': '))
        try:
            for item in request.data['patientEdits']:
                try:
                    operator = User.objects.get (username = item['operator'])
                except ObjectDoesNotExist:
                    raise Exception('[appEnrollment] user does not exist')
                payload = {'localId': item['ICcode'], 'project': item['project'] }
                print 'payload',payload
                r = requests.get(patientUrl, params=payload, verify=False)
                sc = r.status_code
                if sc != 200:
                    raise Exception('Patient does not exist')
                returnDict = r.json()
                graph = neo4j.GraphDatabaseService(settings.GRAPH_DB_URL)
                query = neo4j.CypherQuery(graph,"match (wg:WG)-[:OwnsData]->(pr:Project) where pr.identifier='"+item['project']+"' return wg.identifier as wg")
                r = query.execute()
                if len(r.data)==1:
                    ownerWG = r.data[0]['wg']
                else:
                    raise Exception('No or multiple owners for the project')



                email = LASEmail (functionality='can_view_CMM_patient_enrollment', wgString=ownerWG)
                email.addMsg([ownerWG], [json.dumps(item, sort_keys=True, indent=4, separators=(',', ': '))]) #json.dumps(item, sort_keys=True, indent=4, separators=(',', ': '))
                email.addRoleEmail([ownerWG], 'Executor', [WG.objects.get(name=ownerWG).owner.username])
                try:
                    email.send()
                    print json.dumps(item, sort_keys=True, indent=4, separators=(',', ': '))
                except Exception, e:
                    print 'Error while sending mail!',e
                    raise Exception('Error while sending mail!')
                return Response(returnDict, status=status.HTTP_200_OK)
        except Exception,e:
            return Response({'detail':'Something went wrong', 'exception':str(e)}, status=status.HTTP_400_BAD_REQUEST)
