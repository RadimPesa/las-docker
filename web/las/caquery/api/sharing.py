from django.db import connection
import os
import inspect
import json
import zlib
import re
from math import ceil
from piston.handler import BaseHandler
from django.http import HttpResponse, HttpResponseServerError
from django.views.decorators.csrf import csrf_exempt
from apisecurity.decorators import get_functionality_decorator
from django.utils.decorators import method_decorator
from global_request_middleware import *
from py2neo import *
import urllib,urllib2
from _caQuery.models import *
from django.core.mail import EmailMessage
from django.utils import timezone

class ShareData(BaseHandler):
    allowed_methods = ('POST')
    @method_decorator(get_functionality_decorator)
    def create(self, request):
        try:
            import datetime
            qid = request.POST['qid']
            rid = request.POST['rid']
            entities = json.loads(request.POST['entities'])
            

            q = SubmittedQuery.objects.get(pk=qid)
            run = QueryRun.objects.get(pk=rid)
            results = json.loads(run.results.read())

            queryHeader = q.headers


            entityList=[]
            entityType=None

            outEntity = QueryableEntity.objects.get(pk=q.outputEntityId)

            hId = outEntity.outputShareable.name
            print q.headers
            pkIndex = q.headers.index('ID')
            idIndex = q.headers.index(hId)
            
            for row in results:
                if entities.has_key(row[pkIndex]):
                    entityList.append(row[idIndex])
                    if len(entityList) == len(entities):
                        break

            wgList=json.loads(request.POST['wgList'])
            #shareTime = datetime.datetime.now()
            shareTime=timezone.localtime(timezone.now())

            gdb=neo4j.GraphDatabaseService(settings.GRAPH_DB_URL)
            rBatch = neo4j.ReadBatch(gdb)
            wBatch = neo4j.WriteBatch(gdb)
           
            WGOwner = {}
            WGDest = {}
            
            user = User.objects.get(username=request.user.username)       
            for w in get_WG(): # da sostituire con get_WG()
                WGOwner[w] = {'users': [user.email], 'entities':[], 'shared':[], 'nodeid':None}
                WGOwner[w]['nodeid'] = gdb.get_indexed_node('node_auto_index','identifier',w)
                rBatch.append_cypher("START wg=node:node_auto_index(identifier='"+ w + "'), n=node:node_auto_index('identifier:(" + ' '.join(entityList) + ")') MATCH wg-[r:OwnsData]->n return n")
                res = rBatch.submit()
                if res[0] is not None:
                    if isinstance(res[0], list):
                        for r in res[0]:
                            WGOwner[w]['entities'].append(r[0])
                    else:
                        WGOwner[w]['entities'].append(res[0])

                rBatch.clear()
            for w in wgList:
                WGDest[w['WG']] = {'users':[], 'entities':[], 'shared':[], 'nodeid':None}
                WGDest[w['WG']]['nodeid'] = gdb.get_indexed_node('node_auto_index','identifier',w['WG'])
                for u in w['user']:
                    if u=='owner':
                        WGDest[w['WG']]['users'].append(WG.objects.get(name=w['WG']).owner.email)
                    else:
                        WGDest[w['WG']]['users'].append(User.objects.get(username=u).email)
                rBatch.append_cypher("START wg=node:node_auto_index(identifier='"+ w['WG'] + "'), n=node:node_auto_index('identifier:(" + ' '.join(entityList) + ")') MATCH wg-[r:OwnsData|SharesData]->n return n")
                res = rBatch.submit()
                if res[0] is not None:
                    if isinstance(res[0], list):
                        for r in res[0]:
                            WGDest[w['WG']]['entities'].append(r[0])
                    else:
                        WGDest[w['WG']]['entities'].append(res[0])

                rBatch.clear()
            for wOwn, ownInfo in WGOwner.items():

                for wDest, destInfo in WGDest.items():

                    toShare = list( set(ownInfo['entities']) - set(destInfo['entities']) )
                    print  wOwn, ' -->', wDest, ': ', toShare
                    for nShare in toShare:
                        wBatch.create( rel( destInfo['nodeid'], 'SharesData', nShare, {'startDate': shareTime, 'endDate':None} ) )
                        ownInfo['shared'].append(nShare['identifier'])
                        destInfo['shared'].append(nShare['identifier'])
                        if entityType == None:
                            entityType = nShare.get_labels()
            
            results = wBatch.submit()
            wBatch.clear()          

            for wDest, destInfo in WGDest.items():
                destInfo['shared'] = list(set(destInfo['shared'])) 
                if len(destInfo['shared']):
                    if 'Aliquot' in entityType:
                        url = Urls.objects.get(idWebService=WebService.objects.get(name='Biobank')).url+"/api/shareAliquots/"
                    elif 'Biomouse' in entityType:
                        url = Urls.objects.get(idWebService=WebService.objects.get(name='Xenopatients')).url+"/api.shareBiomice/"
                    elif 'Cellline' in entityType:
                        url = Urls.objects.get(idWebService=WebService.objects.get(name='CellLine')).url+"/api/shareCells/"
                    else:
                        continue

                    values = {'api_key' : '', 'genidList':json.dumps(destInfo['shared']),'wgList':json.dumps([wDest])}
                    data = urllib.urlencode(values)
                    
                    try:
                        
                        u = urllib2.urlopen(url,data)
                        res =  u.read()
                        res=json.loads(res)
                        if res['message']=='ok':
                            print "share OK"
                        else:
                            print "valutare! errore in biob/xeno per sharing"
                    except urllib2.HTTPError,e:
                        print e

                    # EMAIL
                    subject='[LAS] New data shared with ' + wDest
                    message='The user '+ user.first_name + " " + user.last_name+" has shared new data with your Working Group(s)\n\nPleas check the attached file\n"
                    
                    fileName = os.path.join(settings.TEMP_URL, "shareReport" + str(shareTime)  +".txt")
                    fout = open( fileName , "w")
                    fout.write( '\n'.join(destInfo['shared'] ) )
                    
                    subject=subject.encode('utf-8')
                    message=message.encode('utf-8')
                    
                    fout.close()

                    toList=set(destInfo['users'])
                    ccList=set()
                    print toList
                    print 'send email'
                    
                    try:
                        email = EmailMessage(subject,message,"",list(toList),[],"","","",list(ccList))
                        email.attach_file(fileName)
                        email.send(fail_silently=False)
                    except Exception,e:
                        print 'EmailError',e
                    
                    os.remove(fileName)


            
            #print WGOwner
            #print WGDest
            #print entityType



            sharedEntityList = []
            notSharedEntityList = []
            for w, wInfo in WGOwner.items():
                sharedEntityList.extend(wInfo['shared'])

            sharedEntityList = list(set(sharedEntityList))
            notSharedEntityList = list ( set(entityList) - set(sharedEntityList) )

            #print 'Time to share ', datetime.datetime.now() - shareTime

            return {'message': 'ok','sharedEntityList':sharedEntityList, 'notSharedEntityList': notSharedEntityList}
        except Exception,e:
            print 'Exception in sharing data',e
            return {'message': 'fail'} 





class GetWorkingGroups(BaseHandler):
    allowed_methods = ('GET')
    @method_decorator(get_functionality_decorator)
    def read(self, request):
        try:
            finalList=list()
            wgList=WG.objects.all()
            for x in wgList:
                wgDict={}
                wgDict[x.name]=WG_User.objects.filter(WG=x).values_list('user__username',flat=True).distinct()
                finalList.append(wgDict)
                print 'partial', wgDict
            print finalList
            return {'wgList': finalList}
        except Exception,e:
            print e
            return {'wgList': 'error'}
