from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import loader, Context, RequestContext
from piston.handler import BaseHandler
from ngs.models import *
from django.core import serializers
from django.db import models
from django.http import HttpResponse
from django.db.models import Q
from api.utils import *
from django.contrib import auth
import json, urllib2, urllib, simplejson, ast,os,string,operator,datetime
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from ngs.utils.biobank import *
from ngs.utils.storage import *
from ngs.utils.genealogyID import *
from ngs.utils.mdam import *
from apisecurity.decorators import get_functionality_decorator
from django.utils.decorators import method_decorator
from django.utils import timezone


class NewRequest(BaseHandler):
    allowed_methods = ('POST')
    @method_decorator(get_functionality_decorator)
    @transaction.commit_manually
    def create(self, request):
        try:
            postdata = self.flatten_dict(request.POST)
            # ensure that the worker field is present
            postdata['operator'] = postdata.get('operator','')
            postdata['aliquots'] = postdata.get('aliquots','')
            postdata['assigner'] = postdata.get('assigner','')
            postdata['notes'] = postdata.get('notes','')
            print 'adesso',datetime.datetime.now()
            newRequest = Request(timestamp=timezone.localtime(timezone.now()),owner=postdata['assigner'],description=postdata['notes'], title=postdata['notes'])
            '''try:
                operator = User.objects.get(username=postdata['operator'])
                newRequest.idOperator = operator
            except Exception, e:
                print 'err',e'''
            print 'newRequest',newRequest
            newRequest.save()
            featvol=Feature.objects.get(name='Used volume')
            for aliquotInfo in simplejson.loads(postdata['aliquots']):
                print 'gen',aliquotInfo['genid']
                print 'vol',float(aliquotInfo['vol'])
                print 'conc',float(aliquotInfo['conc'])
                print 'data',aliquotInfo['date']

                al = Aliquot.objects.filter(genId=aliquotInfo['genid'])
                if al:
                    al = al[0]
                else:
                    al = Aliquot(genId=aliquotInfo['genid'])
                al.concentration = float(aliquotInfo['conc'])
                al.volume = float(aliquotInfo['vol'])
                al.owner = postdata['operator']
                dateAl = aliquotInfo['date'].split('-')
                print 'dateAl',dateAl

                al.date = datetime.date(int(dateAl[0]), int(dateAl[1]), int(dateAl[2]))
                al.label_request=''
                al.description=''
                al.save()
                print 'al',al
                alreq = Aliquot_has_Request(aliquot_id = al, request_id= newRequest, feature_id=featvol, value=aliquotInfo['takenvol'] )
                alreq.save()

            transaction.commit()
            return {"requestid": newRequest.id}
        except Exception, e:
            transaction.rollback()
            print e
            return {"requestid": 'Error'}

        finally:
            transaction.rollback()

class DeleteRequest(BaseHandler):
    allowed_methods = ('POST')
    @method_decorator(get_functionality_decorator)
    @transaction.commit_manually
    def create(self, request):
        try:
            print 'delete request'
            raw_data = simplejson.loads(request.raw_post_data)
            plan = Request.objects.get(id=raw_data['idplan'])
            aliquots = Aliquot_has_Request.objects.filter(request_id=plan)
            bioAliquots = []
            for al in aliquots:
                bioAliquots.append(al.aliquot_id.genId)
            resetAliquotRequested(bioAliquots)
            aliquots.delete()
            plan.delete()
            transaction.commit()
            return {'status':'deleted'}
        except:
            transaction.rollback()
            return HttpResponseBadRequest("Error in saving data")
        finally:
            transaction.rollback()


class GetLayout(BaseHandler):
    allowed_methods = ('GET')
    @method_decorator(get_functionality_decorator)
    def read (self, request, layoutid):
        response = getGeometry(layoutid)
        return response

class LoadResults(BaseHandler):
    allowed_methods = ('POST')
    @method_decorator(get_functionality_decorator)
    def create(self, request):
        try:
            print request.POST
            #tutti i campi dei filtri sono in AND
            raw_data = simplejson.loads(request.raw_post_data)
            wg = list(get_WG())
            resSetColl = None
            resSetCont = None
            resSetGenid = None 
            resSet = {}
            
            mdamUrl = Urls.objects.get(id_webservice=WebService.objects.get(name='mdam').id, available=True)
            url = mdamUrl.url + "api/runtemplate/"
            print 'url',url
    
            featlabel=Feature.objects.get(name='Label experiment')
            lislabel=raw_data['label']
            lisaliq=[]
            procedi=True
            #faccio il filtro anche sulla label experiment
            if len(lislabel)!=0:
                lisexpaliq=Aliquot_has_Experiment.objects.filter(feature_id=featlabel,value__in=lislabel).values_list('aliquot_id',flat=True)
                lisaliq=Aliquot.objects.filter(id__in=lisexpaliq).values_list('genId',flat=True)
                print 'lisaliq label',lisaliq
                if len(lisaliq)==0:
                    procedi=False
            #solo se nella label l'utente ha scritto qualcosa e ci sono dei risultati        
            if procedi:
                for template_id, params in raw_data['search'].items():
                    if template_id == '41':
                        print 'template 41'
                        print 'val',[len(pvalues) for pid, pvalues in params.items()]
                        if sum([len(pvalues) for pid, pvalues in params.items()]):
                            resSetColl = getAlColl(params, wg, url)
                            #resSet.update(resSetColl)
                    if template_id == '44':
                        print 'template 44'
                        print [len(pvalues) for pid, pvalues in params.items()]
                        if sum([len(pvalues) for pid, pvalues in params.items()]):
                            resSetCont = getAlCont(params, wg, url)
                            #resSet.update(resSetCont)
                    if template_id == '45':
                        print 'template 45'
                        print 'params',params
                        if len(params['0']) or len(lisaliq)!=0:
                            genidsQuery = []
                            for g in params['0']:
                                genidsQuery.append(GenealogyID(g).getGenID())
                            for aliq in lisaliq:
                                genidsQuery.append(GenealogyID(aliq).getGenID())
                            print 'genquery',genidsQuery
                            resSetGenid = getAllGenid(genidsQuery, wg, url)
                            print 'resSetGenid',resSetGenid
                            #resSet.update(resSetGenid)
        
            #se voglio che in caso di nessun risultato mi dia tutti i campioni
            #if resSetCont == None and resSetColl == None and resSetGenid == None:
            #    resSetColl = getAlColl({}, wg, url)
            #    resSet.update(resSetColl)
            
            #print 'resSetColl', resSetColl
            #print 'resSetCont', resSetCont
            #print 'resSetGenid', resSetGenid
            if resSetColl!=None:
                resSet=resSetColl
                if resSetCont!=None:
                    #faccio l'intersezione di questi due
                    resSet=dictIntersect(resSet, resSetCont)
                    if resSetGenid!=None:
                        resSet=dictIntersect(resSet, resSetGenid)
                else:
                    if resSetGenid!=None:
                        resSet=dictIntersect(resSet, resSetGenid)
            elif resSetCont!=None:
                resSet=resSetCont
                if resSetGenid!=None:
                    resSet=dictIntersect(resSet, resSetGenid)            
            elif resSetGenid!=None:
                resSet=resSetGenid
            print 'resSet', resSet
            
            samplesToViz = {}
            #filesSample = MeasurementEvent.objects.filter( idSample__in = Sample.objects.filter(idAliquot_has_Request__in= Aliquot_has_Request.objects.filter(aliquot_id__in = Aliquot.objects.filter(genId__in= resSet.keys() ) ) ) )
            filesSample = MeasurementEvent.objects.filter(aliquot_id__in = Aliquot.objects.filter(genId__in= resSet.keys()))
            for f in filesSample:
                s = f.aliquot_id
                label=''
                featexp=Aliquot_has_Experiment.objects.filter(aliquot_id=s,feature_id=featlabel)
                if len(featexp)!=0:
                    label=featexp[0].value
                if not samplesToViz.has_key(s.id):
                    samplesToViz[s.id] = {'genid': s.genId, 'barcode': resSet[s.genId], 'label':label , 'runs':{}}
                if not samplesToViz[s.id]['runs'].has_key(f.experiment_id.id):
                    samplesToViz[s.id]['runs'][f.experiment_id.id] = {'time_executed': str(f.experiment_id.time_executed), 'title': f.experiment_id.title, 'description': f.experiment_id.description, 'operator':f.experiment_id.idOperator.username, 'files': {}}
                samplesToViz[s.id]['runs'][f.experiment_id.id]['files'][f.id] = {'link': f.link_file, 'name':f.namefile}
    
            return samplesToViz
        except Exception,e:
            print 'err',e

#serve per fare l'autocompletamento nel form di inserimento dei campioni. Completa il genealogyID nel caso di inserimento di
#aliquote gia' presenti nel LAS che vengono richiamate
class AutocompleteInsertSample (BaseHandler):
    allowed_methods = ('GET')
    @method_decorator(get_functionality_decorator)
    def read (self, request):
        biobankUrl = Urls.objects.get(id_webservice=WebService.objects.get(name='biobank').id, available=True)
        url = biobankUrl.url + 'ajax/revalue/autocomplete/?term='+request.GET['term']
        print 'url autocomplete',url
        req = urllib2.Request(url, headers={"workingGroups" : get_WG_string()})
        u = urllib2.urlopen(req)
        res=u.read()
        print 'res',res
        return json.loads(res)

#Per caricare un campione gia' presente nel LAS chiedendo alla biobanca i valori di quel campione
class LoadSampleFromBiobank (BaseHandler):
    allowed_methods = ('GET')
    @method_decorator(get_functionality_decorator)
    def read (self, request,cod,operator):
        biobankUrl = Urls.objects.get(id_webservice=WebService.objects.get(name='biobank').id, available=True)
        url = biobankUrl.url + 'api/facility/loadaliquots/'+cod+'/'+operator
        print 'url',url
        req = urllib2.Request(url, headers={"workingGroups" : get_WG_string()})
        print 'wg ngs',get_WG_string()
        u = urllib2.urlopen(req)
        res=u.read()
        print 'res 2',res
        return json.loads(res)

#serve per fare l'autocompletamento nella schermata di esecuzione dell'esperimento. Completa la label dei campioni gia' analizzati precedentemente
class AutocompleteLoadSample (BaseHandler):
    allowed_methods = ('GET')
    @method_decorator(get_functionality_decorator)
    def read (self, request):
        term=request.GET['term']
        print 'term',term
        lisaliq=Aliquot.objects.filter(label_request__icontains=term)[:10]
        res=[]
        for p in lisaliq:
            p = {'id':p.id, 'label':p.label_request}
            res.append(p)        
        print 'res',res
        return res
    
#serve per fare l'autocompletamento nella schermata di scaricamento file. Cerca in base alla label completa comprendente anche i dati dell'esperimento
class AutocompleteLabelExperiment (BaseHandler):
    allowed_methods = ('GET')
    @method_decorator(get_functionality_decorator)
    def read (self, request):
        term=request.GET['term']
        print 'term',term
        featlabel=Feature.objects.get(name='Label experiment')
        lisexp=Aliquot_has_Experiment.objects.filter(feature_id=featlabel,value__icontains=term)[:10]
        res=[]
        for p in lisexp:
            p = {'id':p.id, 'label':p.value}
            res.append(p)        
        print 'res',res
        return res
    
#per richiamare campioni gia' analizzati data la label
class SampleReanalyze (BaseHandler):
    allowed_methods = ('GET')
    @method_decorator(get_functionality_decorator)
    def read (self, request, label):
        try:
            featfail=Feature.objects.get(name='Failed')
            #label e' una serie di stringhe separate da |
            vettlab=label.split('|')
            dizfin={}
            #chiave l'aliquota e valore un dizionario con tutti i suoi dati relativi alla richiesta
            dizaliqreq={}
            for lab in vettlab:
                lisal=Aliquot.objects.filter(label_request=lab)
                print 'lisal',lisal
                diztemp={}
                if len(lisal)!=0:
                    al=lisal[0]
                    diztemp['labelaliq']=al.label_request
                    diztemp['descriptionaliq']=al.description
                    diztemp['owneraliq']=al.owner
                    #ordino gli aliqreq inversamente in base all'id
                    aliqreq=Aliquot_has_Request.objects.filter(aliquot_id=al).order_by('-id')
                    #prendo il valore piu' recente
                    req=aliqreq[0].request_id
                    #diztemp['capturealiq']=aliqreq[0].value                    
                    diztemp['descriptionreq']=req.description
                    diztemp['ownerreq']=req.owner
                    diztemp['titlereq']=req.title                    
                    diztemp['exists']='yes'                    
                    
                    for alr in aliqreq:
                        al=alr.aliquot_id
                        if al.label_request in dizaliqreq:
                            diztempinterno=dizaliqreq[al.label_request]
                        else:
                            diztempinterno={}
                        unitmis=''
                        if alr.feature_id.measureUnit!='':
                            unitmis=' ('+alr.feature_id.measureUnit+')'
                        diztempinterno[alr.feature_id.name+unitmis]=alr.value    
                        dizaliqreq[al.label_request]=diztempinterno
                    print 'dizaliqreq',dizaliqreq
                    
                    #creo una nuova richiesta con le stesse feature di quella vecchia solo se la richiesta e' gia' stata confermata
                    #Puo' anche capitare che la richiesta in toto non sia stata ancora confermata, ma il campione in questione si', perche'
                    #magari e' stato eseguito l'esperimento solo per lui e non per gli altri della stessa richiesta. In questo caso devo creare una
                    #nuova richiesta per lui
                    salvareq=False
                    lisexp=Experiment.objects.filter(request_id=req)
                    print 'lisexp',lisexp
                    if len(lisexp)!=0:
                        aliqexp=Aliquot_has_Experiment.objects.filter(aliquot_id=al,idExperiment=lisexp[0],feature_id=featfail)
                        print 'aliqexp',aliqexp
                        if len(aliqexp)!=0:
                            salvareq=True
                    
                    if req.timechecked!=None or salvareq==True:
                        reqnuova=Request(idOperator=req.idOperator,
                                  timestamp=timezone.localtime(timezone.now()),
                                  title=req.title,
                                  description=req.description,
                                  owner=req.owner,
                                  pending=req.pending,
                                  source=req.source)
                        reqnuova.save()
                        diztemp['idreq']=reqnuova.id
                        
                        lisfeatreq=Aliquot_has_Request.objects.filter(aliquot_id=al,request_id=req)
                        for feat in lisfeatreq:
                            alr=Aliquot_has_Request(aliquot_id=feat.aliquot_id,
                                                    request_id=reqnuova,
                                                    feature_id=feat.feature_id,
                                                    value=feat.value)
                            alr.save()
                            print 'alr nuova',alr
                            
                    dizfin[lab]=diztemp
                else:
                    dizfin[lab]={'exists':'no'}
            print 'dizfin',dizfin
            return {'data': json.dumps(dizfin),'dizdatialiq':json.dumps(dizaliqreq)}
        except Exception,e:
            print 'errore',e
            return {'data':'errore'}    
    