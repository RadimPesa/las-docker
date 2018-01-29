from piston.handler import BaseHandler
from piston.handler import AnonymousBaseHandler
from piston.handler import BaseHandler
from django.core import serializers
from django.db import models
from django.http import HttpResponse, HttpResponseRedirect
from django.db.models import Q
import string
import operator,requests
from datetime import date, timedelta, datetime
import urllib, urllib2, json,ast
from django.views.decorators.csrf import csrf_exempt
from django.contrib import auth
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response
from django.template import loader, Context, RequestContext
from global_request_middleware import *
from api.utils import *
from cellLine.models import *
from cellLine.genealogyID import *
from django.utils.decorators import method_decorator
from apisecurity.decorators import *
from django.utils import timezone

class NewGenIDHandler(BaseHandler):
    allowed_methods = ('GET')
    @method_decorator(get_functionality_decorator)
    def read(self, request, oldG, typeA, counter, tissueType):
        print 'CLM API [get]: start handlers.NewGenIDHandler'
        print oldG, typeA, counter, tissueType
        counter = int(counter) + 1
        
        oldG = oldG.split(' ')[len(oldG.split(' '))-1]
        try:
            genIDObj = GenealogyID(oldG)
            #check on db --> increment counter to avoid duplicates
            
            print genIDObj.getPrefix() + genIDObj.getTissueType() + typeA
            counterDB = len(Aliquots.objects.filter(gen_id__istartswith = genIDObj.getPrefix() + genIDObj.getTissueType() + typeA ))
            print counterDB
            counter = str(counter + counterDB)
            counter = counter.zfill(2)
            print counterDB
            genIDObj.updateGenID({'archiveMaterial2': typeA, 'aliqExtraction2':counter})

            
            newG = genIDObj.getGenID()
            return newG
        except Exception,e:
            print 'CLM API [get]: handlers.NewGenIDHandler 1)', str(e)
            return 'err'


class ExternalRequest(BaseHandler):
    allowed_methods = ('POST')
    @method_decorator(get_functionality_decorator)
    def create(self, request):
        try:
            print 'CLM API [post]: start handlers.ExternaleRequest'
            print request.POST
            datijson=json.loads(request.POST['aliquots'])
            print 'datijson',datijson
            lisfin=[]
            for diz in datijson:
                print 'diz',diz
                diznuovo=dict(diz)
                print 'diznuovo',diznuovo
                diznuovo['done']=0
                lisfin.append(diznuovo)
            print 'datidopo',lisfin
            er = External_request(data = json.dumps(lisfin), username = request.POST['operator'], action = request.POST['experiment'], date_time = datetime.datetime.now(), assigner = request.POST['assigner'])
            er.save()
            return {'requestid' : er.pk}
        except Exception,e:
            print 'CLM API [get]: handlers.ExternaleRequest 1)', str(e)
            return {'requestid' : 'Error'}



#restituisce tutti gli elementi di una condizione di coltura strutturata ad hoc per il dict della schermata mod cc
class CcDetailsHandler(BaseHandler):
    allowed_methods = ('GET')
    @method_decorator(get_functionality_decorator)
    def read(self, request, cc_id):
        print 'CLM API [get]: start handlers.CcDetailsHandler'
        try:
            elements = {}
            cc = Condition_configuration.objects.get(id = cc_id)
            for chf in Condition_has_feature.objects.filter(condition_configuration_id = cc):
                if chf.condition_feature_id.condition_protocol_element_id != None:
                    temp = {}
                    temp['nameF'] = chf.condition_feature_id.name
                    temp['unity'] = chf.condition_feature_id.unity_measure
                    temp['value'] = chf.value
                    print chf.condition_feature_id.condition_protocol_element_id
                    print chf.condition_feature_id.name
                    print chf.condition_feature_id.unity_measure
                    print chf.value

                    if chf.condition_feature_id.condition_protocol_element_id.name not in elements.keys():
                        elements[chf.condition_feature_id.condition_protocol_element_id.name] = []
                    elements[chf.condition_feature_id.condition_protocol_element_id.name].append( temp )

            #return elements
            return json.dumps(elements)
        except Exception, e:
            print e
            return "err"


#new genID after expansion
class ExpansionNewGenIDHandler(BaseHandler):
    allowed_methods = ('POST')
    @method_decorator(get_functionality_decorator)
    def create(self, request):
        try:
            print 'CLM API [get]: start handlers.ExpansionNewGenIDHandler'
            postdata = self.flatten_dict(request.POST)
            print postdata
            oldG = postdata['oldG']
            cc_id = postdata['id_cc']
            generatedList =  json.loads(postdata['generatedList'])

            oldGenID = GenealogyID(oldG)
            counter = int(oldGenID.getMouse()) + 1
            if len(str(counter)) == 2:
                counter = '0' + str(counter)
            if len(str(counter)) == 1:
                counter = '00' + str(counter)

            cc = Condition_configuration.objects.get(id = cc_id)
            print '1'
            cf = Condition_feature.objects.get(name = 'type_process')
            print '2'
            chf = Condition_has_feature.objects.get(condition_feature_id = cf, condition_configuration_id = cc)
            print '3'
            print chf.value
            #split value and get letter (A/S)
            vector = chf.value[chf.value.find("(")+1:chf.value.find(")")]
            print vector
            candidateGenid= GenealogyID(oldG)
            candidateGenid.updateGenID({'mouse':str(counter), 'sampleVector':vector})

            # da sostituire con il grafo
            disable_graph()
            cells = list(Cells.objects.filter(genID__istartswith=candidateGenid.getInstance()).values_list('genID', flat=True))
            enable_graph()
            print 'From db ', cells
            filteredGeneratedList = [c for c in generatedList if GenealogyID(c).getInstance() == candidateGenid.getInstance()]
            cells.extend(filteredGeneratedList)
            print 'Extend with session ', cells
            try:
                cellCounter = max([int(GenealogyID(c).getTissueType()) for c in cells]) + 1
            except:
                cellCounter = 1
            cellCounter = ''.join('0' for x in range(3 - len(str(cellCounter)))) + str(cellCounter)
            candidateGenid.updateGenID({'tissueType': cellCounter})
            print cellCounter
            print candidateGenid.getGenID()
            return candidateGenid.getGenID()
        except Exception, e:
            print e
            return "err"

#restituisce le info dei nodi figli di un condition_protocol_element con un flag per indicare se hanno figli
class ElementInfosHandler(BaseHandler):
    allowed_methods = ('GET')
    @method_decorator(get_functionality_decorator)
    def read(self, request, nameE):
        try:
            print 'CLM API [get]: start handlers.ElementInfosHandler'
            print 'CLM API:', nameE
            protEl = Condition_protocol_element.objects.get(name = nameE)
            children = Condition_protocol_element.objects.filter(condition_protocol_element_id = protEl).order_by('name')
            childrenList, tempList = [], []
            for c in children:
                if Condition_protocol_element.objects.filter(condition_protocol_element_id = c).count() > 0:
                    #il nodo ha figli
                    childrenList.append({'hasChildren': True, 'element':Simple(c, ['name', 'description', 'condition_protocol_element_id']).getAttributes() })
                else:
                    #il nodo non ha figli
                    featureList, tempFeatureList = [], []
                    tempDict={}
                    tempFeatureList = Condition_feature.objects.filter(condition_protocol_element_id = c).order_by('name')
                    aList = []
                    for f in tempFeatureList:
                        allowed_values = Allowed_values.objects.filter(condition_feature_id = f)
                        for a in allowed_values:
                            aList.append(Simple(a, ['allowed_value', 'condition_feature_id']).getAttributes())
                        featureList.append( { 'featureInfo':Simple(f, ['name', 'unity_measure', 'default_value']).getAttributes(), 'defValue': aList} )
                    tempDict[c.name]={'hasChildren': False, 'element':Simple(c, ['name', 'description', 'condition_protocol_element_id']).getAttributes(),'feature':featureList }
                    childrenList.append(tempDict)
                    #print childrenList  
            #print childrenList
            #return childrenList
            return json.dumps(childrenList)
        except Exception, e:
            print e
            return 'err'

# Restituisce la url per la biobanca (generation from aliquots)
class UrlLoadPlateGenerationAliquots(BaseHandler):
    allowed_methods = ('GET')
    @method_decorator(get_functionality_decorator)
    def read(self, request, name, codicePiastra, typeP):
        try:
            print 'CLM API [get]: start handlers.UrlLoadPlateGenerationAliquots'
            print get_WG_string()
            url = Urls_handler.objects.get(name = name).url + "/api/table/" + codicePiastra + "/" + typeP + "/"
            print 'url',url
            #url = Urls_handler.objects.get(name = 'storage').url + "/api/loadcellline/" + codicePiastra
            req = urllib2.Request(url, headers={"workingGroups" : get_WG_string()})
            u = urllib2.urlopen(req)            
            val=json.loads(u.read())
            print 'val',val
            #e' una lista con tutti i gen della piastra
            lisaliq=val['aliquote']
            laliq=Aliquots.objects.filter(gen_id__in=lisaliq)
            print 'laliq',laliq
            #chiave il gen e val il nick della linea
            diznick={}
            for al in laliq:
                #l'aliquota arriva da un'archiviazione
                if al.archive_details_id!=None:
                    nick=al.archive_details_id.events_id.cell_details_id.cells_id.nickname
                    diznick[al.gen_id]=nick
                elif al.experiment_details_id!=None:
                    nick=al.experiment_details_id.events_id.cell_details_id.cells_id.nickname
                    diznick[al.gen_id]=nick
            print 'diznick',diznick
            return json.dumps({'data':val['data'],'diznick':diznick})
        except Exception, e:
            print e
            return 'err'   

# Per la biobanca (archive)
class LoadPlateArchive(BaseHandler):
    allowed_methods = ('GET')
    @method_decorator(get_functionality_decorator)
    def read(self, request, barcode, aliquot, typeC): #aliquot ---> typeA
        try:
            print 'CLM API [get]: start handlers.LoadPlateArchive'
            print 'barcode',barcode
            print 'aliquot',aliquot
            print 'typeC',typeC
            #chiave il gen e val il nick della linea
            diznick={}
            print 'wg',get_WG_string()
            url = Urls_handler.objects.get(name = 'biobank').url + "/api/generic/load/" + barcode + "/" + aliquot +"/" + typeC
            req = urllib2.Request(url, headers={"workingGroups" : get_WG_string()})
            u = urllib2.urlopen(req)
            val=json.loads(u.read())
            print 'val',val
            if typeC == 'plate':                
                #e' una lista con tutti i gen della piastra
                lisaliq=val['aliquote']
                laliq=Aliquots.objects.filter(gen_id__in=lisaliq)
                print 'laliq',laliq
                
                for al in laliq:
                    #l'aliquota arriva da un'archiviazione
                    if al.archive_details_id!=None:
                        nick=al.archive_details_id.events_id.cell_details_id.cells_id.nickname
                        diznick[al.gen_id]=nick
                    elif al.experiment_details_id!=None:
                        nick=al.experiment_details_id.events_id.cell_details_id.cells_id.nickname
                        diznick[al.gen_id]=nick
                print 'diznick',diznick
            return json.dumps({'data':val['data'],'diznick':diznick})
        except Exception, e:
            print e
            return 'err' 

# protocol infos in choosing-protocol page    
class Protocol_infos_getter(BaseHandler):
    allowed_methods = ('GET')
    @method_decorator(get_functionality_decorator)
    def read(self, request, conf_id):
        try:
            print 'CLM API [get]: start handlers.Protocol_infos_getter'
            root_ft_dictionary = {}
            ft_without_el_list = []
            for cond_has_ft in Condition_has_feature.objects.filter(condition_configuration_id= conf_id):
                feature_list = []
                #prendo la feature
                feature = cond_has_ft.condition_feature_id                
                #prendo l'elemento padre della feature
                father = feature.condition_protocol_element_id;
                if father != None:
                    #prendo l'elemento radice della feature
                    ancestor = father 
                    while ancestor.condition_protocol_element_id != None:
                        ancestor = ancestor.condition_protocol_element_id
                    root = ancestor
                    if root.name not in root_ft_dictionary.keys():
                        root_ft_dictionary.update({root.name:{}})
                    feature_list = {'name':feature.name,'unity_measure':feature.unity_measure, 'value': cond_has_ft.value}
                    if father.name not in root_ft_dictionary[root.name].keys():
                        root_ft_dictionary[root.name].update({father.name:[]})
                    root_ft_dictionary[root.name][father.name].append(feature_list)
                else:
                    #la feature in questione e senza elementi
                    ft_without_el_list.append({feature.name:cond_has_ft.value})              
                description = cond_has_ft.condition_configuration_id.condition_protocol_id.description
                creation_dtime = cond_has_ft.condition_configuration_id.condition_protocol_id.creation_date_time
                file_name = cond_has_ft.condition_configuration_id.condition_protocol_id.file_name
            print root_ft_dictionary
            return json.dumps({'root_ft_dictionary':root_ft_dictionary, 'ft_without_el_list': ft_without_el_list, 'description': description, 'creation_dtime':str(creation_dtime), 'file_name':file_name})
        except Exception, e:
            print e
            return 'err'

            
# genId generation-counter update in aliquot-selection page
class Genid_generation_getter(BaseHandler):
    allowed_methods = ('POST')
    @method_decorator(get_functionality_decorator)
    def create(self, request):
        try:
            print 'CLM API [get]: start handlers.Genid_generation_getter'
            print request.POST
            genid_received = request.POST['genid_received']
            sample_vector = request.POST['type_process_letter']
            generatedList =  json.loads(request.POST['generatedList'])
            protocolId = request.POST['protocol']
            #typeOperation =  request.POST['typeOperation']
            
            print genid_received, GenealogyID(genid_received).getCase() + GenealogyID(genid_received).getTissue() + sample_vector
            print generatedList
            lineage_int_max = 0
            genid_max = GenealogyID(genid_received)
            forGenerationVector = ['H', 'X']
            lastCounter = 0
            #vedo se l'ho gia' fatta con la stessa source in questa sessione
            #flagNewCounter = False
            for cell in generatedList:
                    for aliquot in generatedList[cell]['aliquots']:
                        if aliquot == genid_received[0:20]:
                            print protocolId, generatedList[cell]['protocol']
                            if protocolId == generatedList[cell]['protocol']:
                                print '------',genid_received[0:20], sample_vector, aliquot, GenealogyID(cell).getSampleVector()
                                if GenealogyID(cell).getSampleVector() == sample_vector:
                                    print 'returning'
                                    return cell
                            #else:
                            #    flagNewCounter = True
            '''
            if flagNewCounter:
                print 'update last counter'
                genid = GenealogyID(cell)
                lastCounter = int(genid.getTissueType()) +1
                genid.updateGenID({'tissueType':str(lastCounter).zfill(3)})
                return genid.getGenID()
            '''

            if (genid_max.getSampleVector() in forGenerationVector):
                disable_graph()
                cells = Cells.objects.filter(genID__istartswith= GenealogyID(genid_received).getCase() + GenealogyID(genid_received).getTissue() + sample_vector)
                enable_graph()
                print len(cells)
                #ricerca lato server
                for cell in cells:
                    genid = GenealogyID(cell.genID)
                    lineage = genid.getLineage()
                    lineage_int = translateLineage(lineage)
                    #ricerco tra tutti i genId quello che ha lineage maggiore
                    if lineage_int > lineage_int_max:
                        lineage_int_max = lineage_int
                        genid_max = genid
                #ricerca lato client, nella corrente sessione
                for cell in generatedList:
                    if cell.startswith( GenealogyID(genid_received).getCase() + GenealogyID(genid_received).getTissue() + sample_vector ):
                        genid = GenealogyID(cell)
                        lineage = genid.getLineage()
                        lineage_int = translateLineage(lineage)
                        #ricerco tra tutti i genId quello che ha lineage maggiore
                        if lineage_int > lineage_int_max:
                            lineage_int_max = lineage_int 
                            genid_max = genid                    
                #questa funzione restituisce il lineage subito superiore corrispondente al numero passato        
                lineage_updated = newLineage(lineage_int_max)
                genid_max.updateGenID({'lineage': lineage_updated, 'sampleVector': str(sample_vector).capitalize(), 'samplePassage': '01','mouse':'001','tissueType':str(lastCounter+1).zfill(3), 'archiveMaterial2': '00','aliqExtraction1':'00', 'aliqExtraction2':'00'}) 
            else:
                #only increment thawing counter
                p = int(genid_max.getSamplePassage()) + 1
                
                genid_max.updateGenID({'samplePassage': str(p).zfill(2),'sampleVector': str(sample_vector).capitalize(), 'archiveMaterial2': '00','aliqExtraction1':'00', 'aliqExtraction2':'00'}) 
            uniqueGID = False
            while (uniqueGID == False):
                #incrementare contatore al posto di 'TUM' per rendere univoci i genID
                lastCounter += 1
                genid_max.updateGenID({'tissueType':str(lastCounter).zfill(3)})
                #print genid_max.getGenID()
                disable_graph()
                if (len(Cells.objects.filter(genID = genid_max.getGenID()))) == 0 and genid_max.getGenID() not in generatedList.keys():
                    uniqueGID = True
                enable_graph()
            print genid_max.getGenID()
            return genid_max.getGenID()
        except Exception, e:
            print e
            return 'err'

class changeWGHandler(BaseHandler):
    allowed_methods = ('POST')
    @transaction.commit_on_success
    @method_decorator(get_functionality_decorator)
    def create(self, request):
        try:
            print request.POST
            #dizgen e' un dizionario con chiave il wg e valore una lista di gen da assegnare a quel wg            
            dizgen=json.loads(request.POST.get('genid'))
            print 'dizgen',dizgen            
            #lista di genid per sapere se i vecchi wg di quell'aliquota sono gia' stati cancellati
            cancwg=[]
            for workg,lisgen in dizgen.items():
                disable_graph()
                celllist=Cells.objects.filter(genID__in=lisgen)
                print 'celllist',celllist                
                #se il gruppo e' delete allora devo eliminare le linee in questione
                if workg=='delete':
                    for line in celllist:
                        disable_graph()
                        lisdetails=Cell_details.objects.filter(cells_id=line,end_date_time=None)
                        print 'lisdetails',lisdetails
                        if len(lisdetails)!=0:
                            lisdetails[0].num_plates=0
                            lisdetails[0].end_date_time=timezone.localtime(timezone.now())
                            lisdetails[0].save()
                else:
                    wgnuovo=WG.objects.get(name=workg)
                    print 'wgnuovo',wgnuovo
                    for line in celllist:
                        if line.genID not in cancwg:
                            #prendo i wg attuali
                            listacellWg=Cell_WG.objects.filter(cell=line)
                            for lcellwg in listacellWg:                    
                                #cancello i wg attuali
                                lcellwg.delete()
                        #assegno le aliquote al wg nuovo
                        nuovowg,creato=Cell_WG.objects.get_or_create(cell=line,
                                                                       WG=wgnuovo)
                        print 'nuovowg',nuovowg
                        cancwg.append(line.genID)
            enable_graph()
            return {'data':'ok'}
        except Exception,e:
            print 'err',e
            transaction.rollback()
            return {'data':'error'}


class ShareCells(BaseHandler):
    allowed_methods = ('POST')
    def create(self, request):
        try:
            genidList=json.loads(request.POST.get('genidList'))
            wgList=json.loads(request.POST.get('wgList'))
            disable_graph()
            for genid in genidList:
                cell=Cells.objects.get(genID=genid)
                for item in wgList:
                    wg=WG.objects.get(name=item)
                    if Cell_WG.objects.filter(cell=cell,WG=wg).count()==0:
                        m2m=Cell_WG(cell=cell,WG=wg)
                        m2m.save()
            enable_graph()
            return {'message':'ok'}
        except Exception,e:
            print 'err',e
            return {'message':'error'}

#Serve per caricare dallo storage i dati di ogni singola provetta
class StorageTubeHandler(BaseHandler):
    allowed_methods = ('GET')
    @method_decorator(get_functionality_decorator)
    def read(self, request, listagen,utente):
        try:
            indir=Urls_handler.objects.get(name = 'storage').url
            listagen=listagen.replace('#','%23')
            req = urllib2.Request(indir+"/api/tube/"+listagen + '/' + utente, headers={"workingGroups" : get_WG_string()})
            u = urllib2.urlopen(req)
            data = json.loads(u.read())
            print 'data',data
            return data
            
        except Exception,e:
            print 'err',e
            return {"data":'errore'}

#Dato una serie di container concatenati da & mi da' la lista delle provette contenute
class CheckChildrenHandler(BaseHandler):
    allowed_methods = ('POST')
    @method_decorator(get_functionality_decorator)
    def create(self, request):
        try:
            barcode=request.POST.get('lbarc')
            print 'barcode',barcode
            indir=Urls_handler.objects.get(name = 'storage').url
            barc=barcode.replace('#','%23')
            barc=barc.replace(' ','%20')
            values = {'lbarc' : barcode}
            url=indir+'/api/check/listcontainer/'
            r =requests.post(url, data=values, verify=False, headers={"workingGroups" : get_WG_string()})
            print 'data',json.loads(r.text)
            
            return {'data':json.loads(r.text)}            
        except Exception,e:
            print 'err',e
            return {"data":'errore'}

#Serve per far veder i dati legati al nome dei protocolli e ai farmaci
class getInfoProtocolHandler(BaseHandler):
    allowed_methods = ('GET')
    @method_decorator(get_functionality_decorator)
    def read(self, request):
        try:
            proctype=Condition_feature.objects.get(name='type_protocol')
            lisfeat=Condition_has_feature.objects.filter(condition_feature_id=proctype,value='Expansion').values_list('condition_configuration_id',flat=True)
            liscond=Condition_configuration.objects.filter(id__in=lisfeat).values_list('condition_protocol_id',flat=True)
            lispr=Condition_protocol.objects.filter(id__in=liscond)
            lisfinpr=[]
            for val in lispr:
                lisfinpr.append(str(val.id)+';'+val.protocol_name)
            print 'lisfinpr',len(lisfinpr)
            #prendo i farmaci
            element=Condition_protocol_element.objects.get(name='Drugs')
            lisdrug=Condition_protocol_element.objects.filter(condition_protocol_element_id=element)
            lisfindrug=[]
            for d in lisdrug:
                lisfindrug.append(str(d.id)+';'+d.name)
            return {'Protocols':lisfinpr,'Drugs':lisfindrug}
        except Exception,e:
            print 'err',e
            return {"data":'errore'}

#Serve per avere i nickname delle linee data una lista di genid
class GetNickNameHandler(BaseHandler):
    allowed_methods = ('GET')
    @method_decorator(get_functionality_decorator)
    def read(self, request,genid):
        try:
            #chiave il gen e val il nick della linea
            diznick={}
            #arriva una stringa con i gen separati da &
            lisgen=genid.split('&')
            laliq=Aliquots.objects.filter(gen_id__in=lisgen)
            print 'laliq',laliq
            for al in laliq:
                #l'aliquota arriva da un'archiviazione
                if al.archive_details_id!=None:
                    nick=al.archive_details_id.events_id.cell_details_id.cells_id.nickname
                    diznick[al.gen_id]=nick
                elif al.experiment_details_id!=None:
                    nick=al.experiment_details_id.events_id.cell_details_id.cells_id.nickname
                    diznick[al.gen_id]=nick
            print 'diznick',diznick
            return {'data':diznick}
        except Exception,e:
            print 'err',e
            return {"data":'errore'}
        
        
