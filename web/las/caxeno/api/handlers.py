from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import loader, Context, RequestContext
from piston.handler import BaseHandler
from xenopatients.models import *
from django.core import serializers
from django.db import models
from django.http import HttpResponse
from django.db.models import Q
import string
import operator
from datetime import date, timedelta, datetime
from api.utils import *
from xenopatients.utils import *
from xenopatients.externalAPIhandler import *
from xenopatients.treatments import splitNameT, getNameT, getNamePT
from django.contrib import auth
from django.db.models import Max
import time  
from apisecurity.decorators import get_functionality_decorator
from django.utils.decorators import method_decorator
from django.utils import timezone

class FromPhysToBio(BaseHandler):
    allowed_methods = ('GET')
    @method_decorator(get_functionality_decorator)
    def read(self, request, barcode):
        try:
            print 'XMM API: start FromPhysToBio'
            data = []
            for m in BioMice.objects.filter(phys_mouse_id = Mice.objects.get(barcode = barcode)):
                try:
                    site = Implant_details.objects.get(id_mouse = m).site.shortName
                except:
                    genid = GenealogyID(m.id_genealogy)
                    site = genid.getImplantSite()
                data.append({'group': m.id_group.name, 'genID':m.id_genealogy, 'site':site})
            return data
        except Exception, e:
            print 'XMM API error:', str(e)
            return 'err'


class DurationA(BaseHandler):
    allowed_methods = ('GET')
    @method_decorator(get_functionality_decorator)
    def read(self, request, nameA):
        try:
            print 'XMM API: start durationA'
            arm = Arms.objects.get(name = nameA)
            return str(arm.duration) + ' [' + arm.type_of_time + ']'
        except Exception, e:
            print 'XMM API error:', str(e)
            return 'err'

#chiamata dalla schermata 'confirm treat', serve per autorizzare o meno l'assegnamento del topo a quel treat
#deve restituire l'elenco dei genID associati a quel barcode
class MouseForTreatment(BaseHandler):
    allowed_methods = ('GET')
    @method_decorator(get_functionality_decorator)
    def read(self, request, barcode, group, nameT):
        try:
            print 'XMM API: start MouseForTreatment'
            print barcode
            mouse = Mice.objects.get(barcode = barcode)
        except Exception, e:
            print 'XMM API error:', str(e)
            return json.dumps({'response': 'bad', 'message' : "You can't finalize this mouse. Its barcode doesn't exist."})
        try:
            status = mouse.id_status.name
            rightMice = []
            wrongMice = []
            if status == 'implanted' or status == 'ready for explant' or status == 'explantLite' or status == 'waste' or status == 'transferred':
                biomice = BioMice.objects.filter(phys_mouse_id = mouse)
                nameP, nameA = splitNameT(nameT)
                expProtocol = Protocols.objects.get(name = nameP)
                expArm = Arms.objects.get(name = nameA)
                for biomouse in biomice:
                    groupMouse = biomouse.id_group.name
                    if groupMouse == group:
                        if len(Mice_has_arms.objects.filter(start_date__isnull = True, end_date__isnull = True, id_mouse = biomouse)) > 0:
                            mha = Mice_has_arms.objects.filter(start_date__isnull = True, end_date__isnull = True, id_mouse = biomouse)[0]
                            if mha.id_protocols_has_arms.id_protocol == expProtocol:
                                if mha.id_protocols_has_arms.id_arm == expArm:
                                    rightMice.append(biomouse.id_genealogy)
                                else:
                                    wrongMice.append({'genID':biomouse.id_genealogy, 'info': 'not assigned to this arm (right treatment: ' + getNameT(mha) +')', 'pha':getNameT(mha)})
                            else:
                                wrongMice.append({'genID':biomouse.id_genealogy, 'info': 'not assigned to this protocol (right treatment: '+getNameT(mha)+')', 'pha':getNameT(mha)})
                        else:
                            wrongMice.append({'genID':biomouse.id_genealogy, 'info': 'no treatment assigned'})
                    else:   
                        wrongMice.append({'genID':biomouse.id_genealogy, 'info': 'mouse not of this group (right group: ' + groupMouse +')', 'group':groupMouse})
                    
                message = ""
                if len(rightMice) > 0 and len(wrongMice) > 0:
                    message += "Genealogy ID assigned: "
                    for r in rightMice:
                        message += ' ' + r
                    message += "<br/>"
                    message += "Other Genealogy ID, not assigned to this treatment: "
                    for w in wrongMice:
                        message += ' ' + w["genID"] + ' (' + w["info"] + ')'
                    message += "<br/>"
                    return json.dumps({'response':'ok', 'message':message, 'mice':rightMice})
                if len(rightMice) > 0:
                    message += "Genealogy ID assigned: "
                    for r in rightMice:
                        message += ' ' + r
                    message += "<br/>"
                    return json.dumps({'response':'ok', 'message':message, 'mice':rightMice})
                if len(wrongMice) > 0:
                    message += "Genealogy ID not assigned to this treatment: "
                    for w in wrongMice:
                        message += ' ' + w["genID"] + ' (' + w["info"] + ')'
                    message += "<br/>"
                    return json.dumps({'response':'bad', 'message':message})
            else:
                return json.dumps({'response':"bad", 'message':"This mouse is " + status + ". You can't start a treatment on it."})
        except Exception, e:
            print 'XMM API error:', str(e)
            return str(e)
    
#vecchia versione sostituita dalla versione di Domenico    
class NewGenIDForImplantHandlerOLD(BaseHandler):
    allowed_methods = ('POST')
    @method_decorator(get_functionality_decorator)
    def create(self, request):
        try:
            print 'XMM API: start NewGenIDForImplantHandler'
            oldG = request.POST["oldG"]
            listG = request.POST["listG"]
            barcode = request.POST["barcode"]
            site = request.POST["site"]
	    
            print oldG
            dictG = {}
            if len(listG) > 0:
                dictG = json.loads(listG)
            #check su db per impianti su quel sito
            mouse = Mice.objects.get(barcode = barcode)
            biomice = BioMice.objects.filter(phys_mouse_id = mouse)
            for biomouse in biomice:
                if len(Implant_details.objects.filter(id_mouse = biomouse, site = Site.objects.get(shortName = site))) > 0:
                    print 'return1'
                    return {'status':'err', 'message':'This mouse has a previous implant on this site.'}
            #check su db per impianti precedenti con quella aliquota
            aliquots = Aliquots.objects.filter(id_genealogy__startswith = GenealogyID(oldG).getLongPrefix())
            if len(aliquots) > 0:
                for aliquot in aliquots:
                    for biomouse in biomice:
                        implants = Implant_details.objects.filter(id_mouse = biomouse, aliquots_id = aliquot)
                        if len(implants) > 0:
                            implant = implants[0]
                            genIDObject = GenealogyID(biomouse.id_genealogy)
                            dataDict = {'tissueType':site} #, 'archiveMaterial2': '00', 'aliqExtraction2':'00', '2derivation': '0', '2derivationGen':'00'}
                            genIDObject.updateGenID(dataDict)
                            print 'return1b'
                            return {'status':'ok', 'genID' : genIDObject.getGenID()}
            #check su sessione
            for genID in dictG:
                print dictG[genID]['barcode'], barcode
                if dictG[genID]['barcode'] == barcode:
                    print '##########################', GenealogyID(dictG[genID]['genID'][1:]).getLongPrefix(), GenealogyID(oldG).getLongPrefix()
                    if GenealogyID(dictG[genID]['genID'][1:]).getLongPrefix() == GenealogyID(oldG).getLongPrefix():
                        genIDObject = GenealogyID(genID)
                        dataDict = {'tissueType':site} #, 'archiveMaterial2': '00', 'aliqExtraction2':'00', '2derivation': '0', '2derivationGen':'00'}
                        genIDObject.updateGenID(dataDict)
                        print 'return2', genIDObject.getGenID()
                        return {'status':'ok', 'genID' : genIDObject.getGenID()}

            #count phys_mice with the same aliquot (db and session)
            physList = []
            aliquots = Aliquots.objects.filter(id_genealogy__startswith = GenealogyID(oldG).getTillPassage())
            print GenealogyID(oldG).getTillPassage()
            #print len(aliquots)
            #disable_graph()
            if len(aliquots) > 0:
                for aliquot in aliquots:
                    #print aliquot
                    #for biomouse in biomice:
                    implants = Implant_details.objects.filter(aliquots_id = aliquot)
                    #print len(implants)
                    if len(implants) > 0:
                        for i in implants:
                            physList.append(i.id_mouse.phys_mouse_id)
            dbCounter = len(list(set(physList)))
            print len(list(set(physList))), len(physList)
            physList = []
            for genID in dictG:
                print GenealogyID(dictG[genID]['genID'][1:]).getTillPassage(), GenealogyID(oldG).getTillPassage()
                if GenealogyID(dictG[genID]['genID'][1:]).getTillPassage() == GenealogyID(oldG).getTillPassage():
                    print 'one one one'
                    physList.append(dictG[genID]['barcode'])
            sessionCounter = len(list(set(physList)))

            newCounter = dbCounter + sessionCounter
            print dbCounter, sessionCounter, newCounter
            n = 0 
            passageTemp = "01"
            oldGObj = GenealogyID(oldG)
            try:
                vector = oldGObj.getSampleVector()
                if vector == 'H':
                    oldGI = oldGObj.getCaseTissue() +'X'
                    a = BioMice.objects.filter(id_genealogy__startswith = oldGI)
                    genIdNumber = []
                    for al in a:
                        genIdNumber.append( translateLineage( GenealogyID(al.id_genealogy).getLineage() ) )
                    if genIdNumber:
                        n = max(genIdNumber)
                    else:
                        n = 0
                    print 'Max lineage converted ' + str(n)
                    #lineage = newLineage(max(newCounter,n))
                    lineage = newLineage( newCounter + n )
                    newM = 1
                else:
                    print 'XMM: aliquot origin is X'
                    print oldGObj.getGenID()
                    genTemp = oldGObj.getCaseTissue() + oldGObj.getSampleVector() + oldGObj.getLineage()
                    passageTemp = int(oldGObj.getSamplePassagge()) + 1
                    if passageTemp < 10:
                        passageTemp = '0' + str(passageTemp)
                    genTemp += str(passageTemp)
                    
                    print 'temp'+genTemp+'...'
                    a = BioMice.objects.filter(id_genealogy__startswith = genTemp).order_by('id_genealogy')
                    print '---',str(len(a))
                    if len(a) > 0:
                        n = int(GenealogyID(a[len(a)-1].id_genealogy).getMouse())
                    lineage = oldGObj.getLineage()
                    #newM = max(n,k) + 1
                    print newCounter+1
                    print n+1
                    print '---------'
                    #newM = max(newCounter, n) + 1
                    newM = max(dbCounter, n) + 1 + sessionCounter
                    #newM = newCounter + n + 1
                #print 'max number mouse ', n
            except Exception, e:
                print 'XMM API error: 1)', str(e)
                pass
            print 'a'
            if len(str(newM)) < 3:
                print 'b'
                newM = "0" * (3-len(str(newM)))  + str(newM)
            print 'c', newM
            dataDict = {'sampleVector':'X', 'lineage':lineage, 'samplePassage':str(passageTemp), 'mouse':str(newM), 'tissueType':site, 'archiveMaterial2': '00', 'aliqExtraction2':'00', '2derivation': '0', '2derivationGen':'00'}
            classGen = GenealogyID(oldG)
            classGen.updateGenID(dataDict)
            genID = classGen.getGenID()
            print genID
            return {'status':'ok', 'genID' : genID}
            
        except Exception, e:
            print 'XMM API error: 2)', str(e)
            return {'status':'err', 'message' : str(e)}

class NewGenIDForImplantHandler(BaseHandler):
    allowed_methods = ('POST')
    @method_decorator(get_functionality_decorator)
    def create(self, request):
        try:
            print 'XMM API: start NewGenIDForImplantHandler'
            oldG = request.POST["oldG"]
            listG = request.POST["listG"]
            barcode = request.POST["barcode"]
            site = request.POST["site"]
            print 'oldG',oldG
            dictG = {}
            if len(listG) > 0:
                dictG = json.loads(listG)
            #check su db per impianti su quel sito
            mouse = Mice.objects.get(barcode = barcode)
            biomice = BioMice.objects.filter(phys_mouse_id = mouse)
            print 'biomice',biomice
            for biomouse in biomice:
                if len(Implant_details.objects.filter(id_mouse = biomouse, site = Site.objects.get(shortName = site))) > 0:
                    print 'return1'
                    return {'status':'err', 'message':'This mouse has a previous implant on this site.'}
            #check su db per impianti precedenti con quella aliquota
            print 'long prefix',GenealogyID(oldG).getLongPrefix()
            aliquots = Aliquots.objects.filter(id_genealogy__startswith = GenealogyID(oldG).getLongPrefix())
            print 'aliq',aliquots
            if len(aliquots) > 0:
                for aliquot in aliquots:
                    for biomouse in biomice:
                        implants = Implant_details.objects.filter(id_mouse = biomouse, aliquots_id = aliquot)
                        print 'implants',implants
                        if len(implants) > 0:
                            implant = implants[0]
                            genIDObject = GenealogyID(biomouse.id_genealogy)
                            dataDict = {'tissueType':site} #, 'archiveMaterial2': '00', 'aliqExtraction2':'00', '2derivation': '0', '2derivationGen':'00'}
                            genIDObject.updateGenID(dataDict)
                            print 'return1b'
                            return {'status':'ok', 'genID' : genIDObject.getGenID()}
            #check su sessione
            for genID in dictG:
                #print 'dictG[genID][barcode]', dictG[genID]['barcode']
                #print 'barcode',barcode
                if dictG[genID]['barcode'] == barcode:
                    print 'GenealogyID(dictG[genID][genID]).getLongPrefix()', GenealogyID(dictG[genID]['genID']).getLongPrefix() 
                    print 'GenealogyID(oldG).getLongPrefix()',GenealogyID(oldG).getLongPrefix()
                    if GenealogyID(dictG[genID]['genID']).getLongPrefix() == GenealogyID(oldG).getLongPrefix():
                        genIDObject = GenealogyID(genID)
                        dataDict = {'tissueType':site} #, 'archiveMaterial2': '00', 'aliqExtraction2':'00', '2derivation': '0', '2derivationGen':'00'}
                        genIDObject.updateGenID(dataDict)
                        print 'return2', genIDObject.getGenID()
                        return {'status':'ok', 'genID' : genIDObject.getGenID()}
            return newGenIDGraph(oldG,listG,site)
        except Exception, e:
            print 'XMM API error: 2)', str(e)
            return {'status':'err', 'message' : str(e)}

def newGenIDGraph(oldG,listG,site):
    print 'XMM API method: newGenIDGraph start'
    gdb=neo4j.GraphDatabaseService(settings.GRAPH_DB_URL)
    physList = []
    dictG = {}
    if len(listG) > 0:
        dictG = json.loads(listG)
    oldGObj = GenealogyID(oldG)
    try:
        vector = oldGObj.getSampleVector()
        print 'vector',vector
        print 'dictG',dictG
        #se non e' X allora devo creare i topi ripartendo da capo dal passaggio 1 e dal primo lineage disponibile, perche' sto cambiando il vettore
        if vector == 'H':
            genIdNumber = []
            for genID in dictG:
                #PATCH ANCHE QUI!!
                if GenealogyID(dictG[genID]['genID']).getTillPassage() == GenealogyID(oldG).getTillPassage():
                    genIdNumber.append(GenealogyID(genID).getLineage())

            query=neo4j.CypherQuery(gdb,"START n=node:node_auto_index('identifier:"+str(oldGObj.getCaseTissue())+"*') MATCH (n:Biomouse) RETURN n.identifier")
            result=query.execute()
            
            for genid in result.data:
                #genIdNumber.append( translateLineage(GenealogyID(genid[0]).getLineage() ) )
                genIdNumber.append( GenealogyID(genid[0]).getLineage() )            
            #Questo serve se nella sessione faccio impianti con aliquote dello stesso caso, ma con vettori diversi.
            #Ad es. se prima ho impiantato da un A avro' gia' uno 0B, contando lo 0A del grafo. Quindi adesso devo usare lo 0C per questo impianto
            #il cui vettore di partenza e' H
            for genID in dictG:
                genclass=GenealogyID(genID)
                #inizio gen fino al vettore compreso
                iniziogen=genclass.getCase()+genclass.getTissue()
                oldgeneal=oldGObj.getCase()+oldGObj.getTissue()                
                if oldgeneal==iniziogen:
                    genIdNumber.append(genclass.getLineage())
                        
            print 'genIdNumber',genIdNumber
            if len(genIdNumber)>0:
                n = maxLineage(genIdNumber)
            else:
                n = 0
            print 'lin',n
            if isinstance(n, basestring):
                intN=ord(n[1])-64
                lineage = newLineage( intN )
            else:
                lineage = newLineage(n)
            print 'lineage finale',lineage
            passageTemp='01'            
            newM=1
        elif vector == 'X':
            print 'oldGObj',oldGObj
            #genTemp = oldGObj.getCaseTissue() + oldGObj.getSampleVector() + oldGObj.getLineage()
            genTemp = oldGObj.getCaseTissue() + 'X' + oldGObj.getLineage()
            passageTemp = int(oldGObj.getSamplePassagge()) + 1
            if passageTemp < 10:
                passageTemp = '0' + str(passageTemp)
            genTemp += str(passageTemp)
            lineage = oldGObj.getLineage()
            query=neo4j.CypherQuery(gdb,"START n=node:node_auto_index('identifier:"+str(genTemp)+"*') MATCH (n:Genid) RETURN n.identifier ORDER BY n.identifier")
            result=query.execute()
            if len(result) > 0:
                n = int(GenealogyID(result.data[len(result)-1][0]).getMouse())
                print "da grafo:",n
            else:
                n=0
            try:
                print 'gentemp', genTemp
                for genid in dictG.keys():
                    print GenealogyID(genid).getTillPassage()
                nSessionList = [ int(GenealogyID(genid).getMouse()) for genid in dictG.keys() if GenealogyID(genid).getTillPassage() == genTemp]
                print 'nSessionList',nSessionList
                nSession=max(nSessionList)
                print 'nSess',nSession
            except Exception,e:
                print e
                nSession = 0
                print 'nSess2',nSession
            
            newM= nSession +1 if nSession >  n else n+1
        #cioe' se il vettore e' A, S, O. Prendo il lineage nuovo e mantengo quello. Cambio poi solo il numero del topo
        else:
            #creo il nuovo lineage solo se non c'e' gia' nella sessione un lineage per quel vettore. Ad esempio se ho gia' creato lo 0C per il vettore
            #A di partenza, allora terro' sempre lo 0C
            lineage=''
            nummouse=0
            passageTemp='01'
            #oldgen=GenealogyID(oldG)
            oldgeneal=oldGObj.getCase()+oldGObj.getTissue()+oldGObj.getSampleVector()
            for genID in dictG:
                genclass=GenealogyID(dictG[genID]['genID'])
                #inizio gen fino al vettore compreso
                iniziogen=genclass.getCase()+genclass.getTissue()+genclass.getSampleVector()
                print 'iniziogen',iniziogen
                print 'oldgen',oldgeneal
                if iniziogen==oldgeneal:
                    lineage=GenealogyID(genID).getLineage()
                    break                
            if lineage=='':    
                genIdNumber = []
                query=neo4j.CypherQuery(gdb,"START n=node:node_auto_index('identifier:"+str(oldGObj.getCaseTissue())+"*') MATCH (n:Biomouse) RETURN n.identifier")
                result=query.execute()
    
                for genid in result.data:
                    #genIdNumber.append( translateLineage(GenealogyID(genid[0]).getLineage() ) )
                    genIdNumber.append( GenealogyID(genid[0]).getLineage() )
                #Questo serve se nella sessione faccio impianti con aliquote dello stesso caso, ma con vettori diversi.
                #Ad es. se prima ho impiantato da un H avro' gia' uno 0B, contando lo 0A del grafo. Quindi adesso devo usare lo 0C per questo impianto
                #il cui vettore di partenza e' magari una A
                for genID in dictG:
                    genclass=GenealogyID(genID)
                    #inizio gen fino al vettore compreso
                    iniziogen=genclass.getCase()+genclass.getTissue()
                    oldgeneal=oldGObj.getCase()+oldGObj.getTissue()
                    print 'iniziog',iniziogen
                    print 'oldg',oldgeneal
                    if oldgeneal==iniziogen:
                        genIdNumber.append(genclass.getLineage())
                    
                print 'genIdNumber',genIdNumber
                if len(genIdNumber)>0:
                    n = maxLineage(genIdNumber)
                else:
                    n = 0
                print 'lin',n
                if isinstance(n, basestring):
                    intN=ord(n[1])-64
                    lineage = newLineage( intN )
                else:
                    lineage = newLineage(n)                            
                
                #calcolo il gen fino al passaggio
                genTemp = oldGObj.getCaseTissue() + 'X' + lineage + passageTemp
                print 'gentemp',genTemp
                print 'result',result.data
                if len(result) > 0:                
                    #dai topi presi dal grafo guardo quelli che hanno genid iniziale uguale al gentemp e prendo il codice topo
                    nummouseList = [ int(GenealogyID(genid[0]).getMouse()) for genid in result.data if GenealogyID(genid[0]).getTillPassage() == genTemp]
                    print 'nummouseList',nummouseList
                    if len(nummouseList)==0:
                        nummouse=0
                    else:                                    
                        nummouse=max(nummouseList)
                else:
                    nummouse=0
            else:
                #calcolo il gen fino al passaggio
                genTemp = oldGObj.getCaseTissue() + 'X' + lineage + passageTemp
                
            print 'nummouse',nummouse
            print 'lineage finale',lineage
            #sono i topi gia' fatti nella sessione, di cui prendo il massimo del codice topo
            nSessionList = [ int(GenealogyID(genid).getMouse()) for genid in dictG.keys() if GenealogyID(genid).getTillPassage() == genTemp]
            print 'nSessionList',nSessionList
            if len(nSessionList)==0:
                nSession=0
            else:
                nSession=max(nSessionList)
            print 'nSess',nSession            
            
            newM= nSession +1 if nSession >  nummouse else nummouse+1
            
        if len(str(newM)) < 3:
            newM = "0" * (3-len(str(newM)))  + str(newM)

        dataDict = {'sampleVector':'X', 'lineage':lineage, 'samplePassage':str(passageTemp), 'mouse':str(newM), 'tissueType':site, 'archiveMaterial2': '00', 'aliqExtraction2':'00', '2derivation': '0', '2derivationGen':'00'}
        classGen = GenealogyID(oldG)
        classGen.updateGenID(dataDict)
        genIDFinal=classGen.getGenID()
        return {'status':'ok', 'genID' : genIDFinal}
    except Exception, e:
        print 'XMM API error: 1)', str(e)
        pass


class LoginHandler(BaseHandler):
    allowed_methods = ('POST')
    def create(self, request):
        print 'XMM API: start LoginHandler'
        username = request.POST['username']
        password = request.POST['password']
        user = auth.authenticate(username=username, password=password)
        if user is not None and user.is_active:
            auth.login(request, user)
            return {'sessionid' : str(request.session.session_key)}
        else:
            return {'sessionid' : 'none'}

class LogoutHandler(BaseHandler):
    allowed_methods = ('POST')
    def create(self, request):
        print 'XMM API: start LogoutHandler'
        auth.logout (request)

#restituisce le azioni pending di un gruppo
class CheckGroupHandler(BaseHandler):
    allowed_methods = ('GET')
    @method_decorator(get_functionality_decorator)
    def read(self, request, name):
        try:
            print 'XMM API: start CheckGroupHandler'
            a = datetime.datetime.now()
            print 'XMM API: start CheckGroupHandler', str(a)


            filter_list = []
            pending = {}
            name = name.upper()
            mice = BioMice.objects.filter(id_group = Groups.objects.get(name = name))
            prEvent = ProgrammedEvent.objects.filter(id_mouse__in = mice, id_status= EventStatus.objects.get(name = 'pending'))
            filter_list = []
            total, avg, counter, i = 0, 0, 0, 0
            oldPes = Programmed_explant.objects.filter(id_mouse__in = mice, done=0)
            mhasT = Mice_has_arms.objects.filter(id_mouse__in = mice, start_date__isnull = True, end_date__isnull = True)
            mhasF = Mice_has_arms.objects.filter(id_mouse__in = mice, start_date__isnull = False, end_date__isnull = True)
            impls = Implant_details.objects.filter(id_mouse__in = mice)
            quants = Quantitative_measure.objects.filter(id_mouse__in = mice)
            for p in prEvent:
                nameT, startD, exp_end, explant, dateMeasure, valueMeasure, measureNotes, scopeNotes, scopeExplant,treatNotes = "","","","","","","","","",""
                #prefissi:
                # 0 indica qualcosa di nuovo, diverso dalla situazione precedente
                # 1 indica che quell'attributo non cambia
                #carico le informazioni 'vecchie', gia' approvate in precedenze
                oldStatus = p.id_mouse.phys_mouse_id.id_status.name
                duration = ""
                oldScopeExplant = "Not programmed for explant"
                #oldPe = Programmed_explant.objects.filter(id_mouse = p.id_mouse, done=0)
                if len(oldPes.filter(id_mouse = p.id_mouse)) > 0:
                    oldScopeExplant = oldPes.filter(id_mouse = p.id_mouse)[0].id_scope.description
                oldNameT, oldStart, oldEnd = "","",""
                mha = mhasT.filter(id_mouse = p.id_mouse)
                if len(mha) <= 0:
                    mha = mhasF.filter(id_mouse = p.id_mouse)
                if len(mha) > 0:
                    mha = mha[0]
                    oldNameT = getNameT(mha)
                    oldStart = str(mha.start_date)
                    oldEnd = mha.expected_end_date
                    duration = str(mha.id_protocols_has_arms.id_arm.duration) + ' [' + str(mha.id_protocols_has_arms.id_arm.type_of_time) + ']'
                    if oldStart == 'None':
                        if mha.id_prT is not None:
                            oldStart = mha.id_prT.expectedStartDate
                        else:
                            oldStart = ""
                    if mha.id_prT !=None:
                        if mha.id_prT.id_event != None:
                            treatNotes=mha.id_prT.id_event.checkComments
                newStatus = ""
                w = 0
                if p.id_qual:
                    valueMeasure = p.id_qual.id_value.value
                    measureNotes = p.id_qual.notes
                    dateMeasure = p.id_qual.id_series.date
                    w = p.id_qual.weight
                elif p.id_quant:
                    valueMeasure = p.id_quant.volume
                    measureNotes = p.id_quant.notes
                    dateMeasure = p.id_quant.id_series.date
                    w = p.id_quant.weight
                if oldStatus != 'explanted' and oldStatus != 'dead accidentally' and oldStatus != 'sacrified': 
                    prcs = Pr_changeStatus.objects.filter(id_event = p)
                    if len(prcs) > 0:
                        newStatus = '0' + prcs[0].newStatus.name
                    else:
                        newStatus = '1' + oldStatus
                    pre = Pr_explant.objects.filter(id_event = p)
                    if len(pre) > 0:
                        pe = pre[0]
                        if oldScopeExplant != pe.id_scope.description:
                            scopeExplant = '0' + pe.id_scope.description
                            scopeNotes = pe.scopeNotes
                        else:
                            scopeExplant = '1' + oldScopeExplant
                            scopeNotes = Programmed_explant.objects.get(id_mouse = p.id_mouse, done=0).scopeNotes
                        
                        if oldStatus != 'ready for explant':
                            newStatus = '0' + 'ready for explant'
                        else:
                            newStatus = '1' + 'ready for explant'
                    else:
                        scopeExplant = '1' + oldScopeExplant
                    prt = Pr_treatment.objects.filter(id_event = p)
                    print 'prt',prt
                    if len(prt) > 0:
                        pt = prt[0]
                        print 'pt',pt
                        if oldNameT != getNamePT(pt): #pt.id_pha.id_protocol.name + ' - ' + pt.id_pha.id_arm.name:
                            nameT = '0' + getNamePT(pt)
                            startD = pt.expectedStartDate
                            duration = duration = str(pt.id_pha.id_arm.duration) + ' [' + str(pt.id_pha.id_arm.type_of_time) + ']'
                        else:
                            nameT = '1' + oldNameT
                            startD = oldStart
                            exp_end = oldEnd                        
                    else:
                        nameT = '1' + oldNameT
                        startD = oldStart
                        exp_end = oldEnd
                    try:
                        prst = Pr_stopTreatment.objects.filter(id_event = p)
                        pst = prst
                        duration = duration = str(pst.id_mha.id_protocols_has_arms.id_arm.duration) + ' [' + str(pst.id_mha.id_protocols_has_arms.id_arm.type_of_time) + ']'
                        nameT = '0STOPPED'
                        startD = pst.id_mha.start_date
                        if startD == None:
                            startD = pst.id_mha.id_prT.expectedStartDate
                    except:
                        print 'no get'

                    pending.update({i:{"id_mouse": p.id_mouse.id_genealogy,
                         "idEvent": p.id,
                         "barcode": p.id_mouse.phys_mouse_id.barcode,
                         "dateM":str(dateMeasure),
                         "value":valueMeasure, 
                         "weight":w, 
                         "notes":measureNotes,
                         "status":newStatus,
                         "scope":scopeExplant,
                         "scopeNotes":scopeNotes,
                         "treatment":nameT,
                         "dateS":str(startD),
                         "duration":str(duration),
                         'dateE':str(exp_end),
                         'treatNotes':treatNotes
                     }})
                else:
                    pending.update({i:{"id_mouse": p.id_mouse.id_genealogy,
                         "idEvent": p.id,
                         "barcode": p.id_mouse.phys_mouse_id.barcode,
                         "dateM":str(dateMeasure),
                         "value":valueMeasure, 
                         "weight":w, 
                         "notes":measureNotes,
                         "status":'1'+oldStatus,
                         "scope":'',
                         "scopeNotes":'',
                         "treatment":'',
                         "dateS":'',
                         "duration":'',
                         'dateE':'',
                         'treatNotes':''
                     }})
                try:
                    total = total + float(valueMeasure)
                    counter = counter + 1
                except ValueError:
                    pass
                i = i + 1
            if total > 0:
                avg = total / counter
            #measure = {}
            dateList, groups, propGroups, filter_list, operators = [], [], [], [], []
            print  'TIMING----->', str(datetime.datetime.now() - a)
            print mice
            if len(mice) > 0:
                #RESTITUZIONE DI TUTTE LE MISURE DI QUEL GRUPPO
                operators, dateList = getMeasure(mice, operators, dateList)#, measure)
                #creazione delle etichette dei sottogruppi
                dateList, groupsDict, groupsNote = defineG(mice, dateList)
                groups = groupsDict.keys()
                i = 0
                #CREAZIONE DELLA STRUTTURA DATI PER IL DISEGNO DEL GRAFICO DELLE MISURE
                graphDict = {}
                #se il gruppo e' gia' suddiviso in sottogruppi (ovvero, trattamenti gia' approvati)
                qs = quants.filter(id_series__date__in = dateList)
                if len(groupsDict.keys()) > 0: #########
                    print 'if'
                    for d in dateList:
                        dictG = {}
                        for label in groupsDict:
                            queryMeasure = qs.filter(id_mouse__in = groupsDict[label],id_series__date = d)
                            measures = []
                            for mouse in groupsDict[label]:
                                for q in queryMeasure:
                                    if q.id_mouse == mouse: 
                                        measures.append(q.volume)
                            if len(measures) > 0:
                                #selezionare la media delle misure di quel sottogruppo per quella data
                                dictG.update({ label : sum(i for i in measures) / len(measures) })
                        if len(dictG) > 0:
                            graphDict.update( { d : dictG } )
                else:
                    #nessun sottogruppo, trattamenti ne approvati ne proposti
                    print 'else'
                    for d in dateList:
                        dictG = {}
                        measures = []
                        for m in mice:
                            for v in Quantitative_measure.objects.filter(id_mouse = m,id_series__date = d):
                                if v != "":
                                    measures.append(v.volume)
                        if len(measures) > 0:
                            #selezionare la media delle misure di quel sottogruppo per quella data
                            dictG.update({ label : sum(i for i in measures) / len(measures) })
                        if len(dictG) > 0:
                            graphDict.update( { d : dictG } )
                    groups = name
                print 'XMM API: CheckGroupHandler: finish graph'
                #CREAZIONE DEL CODICE HTML PER LA TABELLA CON LO STORICO ORIZZONTALE DELLE MISURE
                #CREAZIONE DEL CODICE HTML PER LA TABELLA CON LO STORICO ORIZZONTALE DEI PESI DEI TOPI
                table, wTable = history(mice, dateList, groupsDict, groupsNote) #########
                request.session['table'] = table
                request.session['wTable'] = wTable
                request.session['graph'] = graphDict
                if len(groups):
                    request.session['groups'] = groups
                else:
                    request.session['groups'] = [name]
                request.session['dateList'] = dateList
                #measure: misure per la tabella
                #graph: dict di dict di dict per il grafico (scarti compresi)
                #groups: lista nomi dei/del sottogruppo (compresi gli eventuali scarti)
                #dateList: lista delle date ordinate
                #table: codice HTML per la tabella con le misure storiche
                #wTable: codice HTML per la tabella con i pesi storici
                tempList = []
                print  'TIMING i:', str(datetime.datetime.now() - a)
                for m in mice:
                    tempList.append(str(impls.filter(id_mouse = m)[0].id_series.date))
                tempList = sorted(tempList)
                dateList.append(tempList[0])
                dateList = sorted(dateList)
                print  'TIMING----->', str(datetime.datetime.now() - a)
            return {'list_quant':json.dumps(pending), 'avg':avg, 'operators':json.dumps(operators), 'groups':json.dumps(groups), 'graph': json.dumps(graphDict), 'dateList':json.dumps(dateList), 'table':table, 'wTable':wTable}
        except Exception, e:
            print 'XMM API error:', str(e)
            return 'err'

#per la schermata ongoing, restituisce tutte le info per la tabella ex-pending
class MiceOfGroupHandler(BaseHandler):
    allowed_methods = ('GET')
    @method_decorator(get_functionality_decorator)
    def read(self, request, name):
        try:
            a = datetime.datetime.now()
            print 'XMM API: start MiceOfGroupHandler', str(a)
            filter_list, miceDict = [], {}
            table, wTable = "", ""
            name = name.upper()
            try:
                group = Groups.objects.get(name = name)
            except:
                return 'wrong name'
            mice = BioMice.objects.filter(id_group = group)
            print 'start'
            quant = Quantitative_measure.objects.filter(id_mouse__in = mice)
            qual = Qualitative_measure.objects.filter(id_mouse__in = mice)
            expl = Programmed_explant.objects.filter(id_mouse__in = mice)
            mha = Mice_has_arms.objects.filter(id_mouse__in = mice, start_date__isnull = False, end_date__isnull= True)
            print  'TIMING:', str(datetime.datetime.now() - a)
            impls = Implant_details.objects.filter(id_mouse__in = mice)
            total, avg, counter, i = 0, 0, 0, 0
            for m in mice:
                date, value, weight, notes = getLastMeasure(m, quant, qual)
                scopeExpl, scopeNotes = getProgrammedExpl(m, expl)
                nameT, start, duration, end, treatNotes = getCurrentTreat(m, mha)
                miceDict.update({i:{
                     "id_mouse": m.id_genealogy,
                     "barcode": m.phys_mouse_id.barcode,
                     "dateM":str(date),
                     "value":value, 
                     "weight":weight, 
                     "notes":notes,
                     "status":m.phys_mouse_id.id_status.name,
                     "scope":scopeExpl,
                     "scopeNotes":scopeNotes,
                     "treatment":nameT,
                     "dateS":str(start),
                     "duration":str(duration),
                     "dateE":str(end),
                     "treatNotes":treatNotes
                 }})

                try:
                    total = total + float(value)
                    counter = counter + 1
                except ValueError:
                    pass
                i = i + 1
            if total > 0:
                avg = total / counter
            print 'avg',avg
            print  'TIMING----->', str(datetime.datetime.now() - a)
        #try:
            #measure = {}
            dateList, groups, propGroups, filter_list, operators = [], [], [], [], []
            #mice = BioMice.objects.filter(id_group = Groups.objects.get(name = name))
            #print mice
            graphDict = {}
            print 'lennn', str(len(mice))
            if len(mice) > 0:
                #RESTITUZIONE DI TUTTE LE MISURE DI QUEL GRUPPO
                print '1'
                operators, dateList = getMeasure(mice, operators, dateList)#, measure)
                print '2'
                #creazione delle etichette dei sottogruppi
                dateList, groupsDict, groupsNote = defineG(mice, dateList)
                groups = groupsDict.keys()
                i = 0
                #CREAZIONE DELLA STRUTTURA DATI PER IL DISEGNO DEL GRAFICO DELLE MISURE
                
                #se il gruppo e' gia' suddiviso in sottogruppi (ovvero, trattamenti gia' approvati)
                if len(groupsDict.keys()) > 0: #########
                    for d in dateList:
                        dictG = {}
                        for label in groupsDict:
                            queryMeasure = Quantitative_measure.objects.filter(id_mouse__in = groupsDict[label],id_series__date = d)
                            measures = []
                            for mouse in groupsDict[label]:
                                for q in queryMeasure:
                                    if q.id_mouse == mouse: 
                                        measures.append(q.volume)
                            if len(measures) > 0:
                                #selezionare la media delle misure di quel sottogruppo per quella data
                                dictG.update({ label : sum(i for i in measures) / len(measures) })
                        if len(dictG) > 0:
                            graphDict.update( { d : dictG } )
                else:
                    #nessun sottogruppo, trattamenti ne approvati ne proposti
                    for d in dateList:
                        dictG = {}
                        measures = []
                        for m in mice:
                            for v in Quantitative_measure.objects.filter(id_mouse = m,id_series__date = d):
                                if v != "":
                                    measures.append(v.volume)
                        if len(measures) > 0:
                            #selezionare la media delle misure di quel sottogruppo per quella data
                            dictG.update({ label : sum(i for i in measures) / len(measures) })
                        if len(dictG) > 0:
                            graphDict.update( { d : dictG } )
                    groups = name
                print 'finish graph'
                
                #CREAZIONE DEL CODICE HTML PER LA TABELLA CON LO STORICO ORIZZONTALE DELLE MISURE
                #CREAZIONE DEL CODICE HTML PER LA TABELLA CON LO STORICO ORIZZONTALE DEI PESI DEI TOPI
                table, wTable = history(mice, dateList, groupsDict, groupsNote) #########
                request.session['table'] = table
                request.session['wTable'] = wTable
                request.session['graph'] = graphDict
                if len(groups):
                    request.session['groups'] = groups
                else:
                    request.session['groups'] = [name]
                request.session['dateList'] = dateList
                #measure: misure per la tabella
                #graph: dict di dict di dict per il grafico (scarti compresi)
                #groups: lista nomi dei/del sottogruppo (compresi gli eventuali scarti)
                #dateList: lista delle date ordinate
                #table: codice HTML per la tabella con le misure storiche
                #wTable: codice HTML per la tabella con i pesi storici
                tempList = []
                print  'TIMING i:', str(datetime.datetime.now() - a)
                for m in mice:
                    tempList.append(str(impls.filter(id_mouse = m)[0].id_series.date))
                tempList = sorted(tempList)
                dateList.append(tempList[0])
                dateList = sorted(dateList)
            print  'TIMING:', str(datetime.datetime.now() - a)
            return {'miceDict':json.dumps(miceDict), 'avg':avg, 'operators':json.dumps(operators),'groups':json.dumps(groups), 'graph': json.dumps(graphDict), 'dateList':json.dumps(dateList), 'table':table, 'wTable':wTable}
        except Exception, e:
            print 'XMM API error:', str(e)
            return 'err'

#restituisce le azioni gia' approvate di un singolo topo
class ActionsMouse(BaseHandler):
    allowed_methods = ('GET')
    @method_decorator(get_functionality_decorator)
    def read(self, request, genID):
        try:
            print 'XMM API: start ActionsMouse'
            #barcode = barcode.upper()
            mouse = BioMice.objects.get(id_genealogy = genID)
            print mouse
            status = mouse.phys_mouse_id.id_status.name
            print status
            print mouse.phys_mouse_id
            scopeExplant = "Not programmed for explant"
            scopeNotes, nameT, dateS, duration = "-","-","-","-"
            pes = Programmed_explant.objects.filter(id_mouse = mouse, done=0)
            if len(pes) > 0:
                scopeExplant = pes[0].id_scope.description
                scopeNotes = pes[0].scopeNotes
            duration, nameT, start, end = "","","",""
            mhas = Mice_has_arms.objects.filter(id_mouse = mouse, start_date__isnull = False, end_date__isnull = True)
            if len(mhas) > 0:
                mha = mhas[0]
                nameT = getNameT(mha)
                start = str(mha.start_date)
                if start == 'None':
                    if mha.id_prT is not None:
                        start = str(mha.id_prT.expectedStartDate)
                    else:
                        start = ""
                duration = str(mha.id_protocols_has_arms.id_arm.duration) + ' [' + str(mha.id_protocols_has_arms.id_arm.type_of_time) + ']'
            return {"status":status, "scope":scopeExplant, "scopeNotes":scopeNotes, "treatment":nameT, "dateS":start, "duration":duration}
        except Exception, e:
            print 'XMM API error:', str(e)
            return 'err'

#restituisce le azioni pending di un singolo topo
class PendingMouse(BaseHandler):
    allowed_methods = ('GET')
    @method_decorator(get_functionality_decorator)
    def read(self, request, idEvent):
        try:
            print 'XMM API: start PendingMouse'
            event = ProgrammedEvent.objects.get(id = idEvent)
            mouse = event.id_mouse

            status = '1' + mouse.phys_mouse_id.id_status.name
            scopeExplant = '1' + "Not programmed for explant"
            scopeNotes = ""
            if len(Programmed_explant.objects.filter(id_mouse = mouse, done=0)) > 0:
                scopeExplant = '1' + Programmed_explant.objects.get(id_mouse = mouse, done=0).id_scope.description
                scopeNotes = Programmed_explant.objects.get(id_mouse = mouse, done=0).scopeNotes
                status = '1' + 'ready for explant'

            duration, nameT, start, end = "","","",""
            if len(Mice_has_arms.objects.filter(id_mouse = mouse, end_date__isnull = True)) > 0:
                mha = Mice_has_arms.objects.filter(id_mouse = mouse, end_date__isnull = True)[0]
                nameT = '1' + getNameT(mha)
                start = mha.start_date
                duration = str(mha.id_protocols_has_arms.id_arm.duration) + ' [' + str(mha.id_protocols_has_arms.id_arm.type_of_time) + ']'

            changeS = Pr_changeStatus.objects.filter(id_event = event)
            if len(changeS) > 0:
                status = '0' + changeS[0].newStatus.name

            explant = Pr_explant.objects.filter(id_event = event)
            if len(explant) > 0:
                scopeExplant = '0' + explant[0].id_scope.description
                scopeNotes = explant[0].scopeNotes
                status = '0' + 'ready for explant'

            treatment = Pr_treatment.objects.filter(id_event = event)
            if len(treatment) > 0:
                nameT = '0' + getNamePT(treatment[0])#.id_pha.id_protocol.name + ' - ' + treatment[0].id_pha.id_arm.name
                start = str(treatment[0].expectedStartDate)
                duration = str(treatment[0].id_pha.id_arm.duration) + ' [' + str(treatment[0].id_pha.id_arm.type_of_time) + ']'

            return {"status":status, "scope":scopeExplant, "scopeNotes":scopeNotes, "treatment":nameT, "dateS":str(start), "duration":str(duration)}
        except Exception, e:
            print 'XMM API error:', str(e)
            return 'err'


#restituisce alcune informazioni di un gruppo
class InfoGroupHandler(BaseHandler):
    allowed_methods = ('GET')
    @method_decorator(get_functionality_decorator)
    def read(self, request, name):
        try:
            print 'XMM API: start InfoGroupHandler'
            name = name.upper()
            g = Groups.objects.get(name = name)
            mice = 0
            if len(BioMice.objects.filter(id_group = g)):
                biomice = len(BioMice.objects.filter(id_group = g))
            if g.id_protocol == None:
                return {'name':g.name, 'date':g.creationDate, 'protocol':'No protocol assigned to this group', 'mice':biomice}
            else:    
                return {'name':g.name, 'date':g.creationDate, 'protocol':g.id_protocol.name, 'mice':biomice}
        except Exception, e:
            print 'XMM API error:', str(e)
            return 'err'


#fornisce al chiamante il numero da concatenare al fondo di un nome per un nuovo gruppo di topi
class CheckGroupNameHandler(BaseHandler):
    allowed_methods = ('GET')
    @method_decorator(get_functionality_decorator)
    def read(self, request, name):
        print 'XMM API: start CheckGroupNameHandler'
        try:
            #ATTENZIONE: non e' case sensitive
            names = Groups.objects.filter(name__istartswith = name)
            print names
            data = []
            if len(names) > 0:
                return len(names)
            else:
                return 0
        except Exception, e:
            print 'XMM API error:', str(e)
            return 'err'

#restituisce il codiece HTML per generare la tabella per raggruppare i topi dopo gli impianti
class OrganizeGroupsHandler(BaseHandler):
    allowed_methods = ('GET','POST')
    @method_decorator(get_functionality_decorator)
    def read(self, request):
        print 'XMM API: start OrganizeGroupsHandler'
        try:
            return {'data':'ok'}
        except Exception, e:
            print 'XMM API error:', str(e)
            return {"data": 'err'}
    def create(self, request):
        try:
            print 'XMM API: start OrganizeGroupsHandler [POST]'
            print request.POST
            dateT = ""
            if request.POST['dateC'] == 'true':
                dateT = str(date.today())
                dateT = dateT.replace('-','')
            n = request.POST['cypher']
            protocol = ""
            if request.POST['protocolC'] == 'true':
                print '1'
                protocol = request.POST['scope']
                print protocol
            implants = request.POST['implants']
            #parameters = createList(obj)
            #print 'par',parameters
            print 'prot',protocol
            print 'n',n
            print 'dT',dateT
            string = getHTML(implants, protocol, n, dateT)
            print '1'
            return string
        except Exception, e:
            print 'XMM API error:', str(e)
            return {"code": 'err'}

class ExplTableHandler(BaseHandler):
    allowed_methods = ('GET')
    @method_decorator(get_functionality_decorator)
    def read(self, request, barcodeP, typeP, typeC):
        try:
            print 'XMM API: start ExplTableHandler'
            long_name, abbr, name = "", "", ""
            if typeP == 'VT':
                abbr = 'v'
                name = 'vital'
                long_name = 'VITAL'
            if typeP == 'SF':
                abbr = 's'
                name = 'sf'
                long_name = 'SNAP FROZEN'
            if typeP == 'RL':
                abbr = 'r'
                name = 'rna'
                long_name = 'RNA'
            string = ""
            data = loadExplantPlate(barcodeP, typeP, typeC)
            return {'data':data['data']}
        except Exception, e:
            print 'XMM API error:', str(e)
            return {"data": 'err'}

#restituisce tutti i tipi di tessuto collezionabili
class TissueHandler(BaseHandler):
    #print 'tissue chiamata'
    allowed_methods = ('GET')
    @method_decorator(get_functionality_decorator)
    def read(self, request):
        try:
            print 'XMM API: start TissueHandler'
            tissueDict = {}
            for t in TissueType.objects.all():
                tissueDict[t.id] = t.name
            return json.dumps(tissueDict)
        except Exception, e:
            print 'XMM API error:', str(e)
            return 'errore'

#restituisce true o false, in risposta alla richiesta di ammissibilita' di un cambio status
class CheckDestinationStatusHandler(BaseHandler):
    allowed_methods = ('GET',)
    @method_decorator(get_functionality_decorator)
    def read(self, request, oldS, newS, barcode):
        flag = False 
        print 'XMM API: start CheckDestinationStatusHandler'
        try:
            data = ChangeStatus.objects.filter(from_status = Status.objects.get(name = oldS)).filter(to_status = Status.objects.get(name = newS))
            if data:
                flag = True
        except:
            pass
        '''
        genID = ""
        try:
            genID = BioMice.objects.get(id_genealogy = barcode).id_genealogy
        except Exception, e:
            print e
            pass
        '''
        return { 'flag': flag, 'genID':barcode }

#restituisce lo status di un topo, avendo in input il suo barcode
class StatusHandler(BaseHandler):
    allowed_methods = ('GET',)
    @method_decorator(get_functionality_decorator)
    def read(self, request, barcode):
        try:
            print 'XMM API: start StatusHandler'
            print 'received barcode',barcode
            mouse = Mice.objects.get(barcode = barcode)
            bm = BioMice.objects.filter(phys_mouse_id = mouse)
            if len(bm) > 0:
                response = []
                for biomouse in bm:
                    response.append({ biomouse.id_genealogy : mouse.id_status.name })
                #print response
                return response
            else:
                disable_graph()
                if len(BioMice.objects.filter(phys_mouse_id = mouse)):
                    #raise Exception ('mice not belonging to the current wg')
                    return 'otherwg'
                enable_graph()
                return [{ barcode : mouse.id_status.name }]
        except:
            return 'newbarcode'


#restituisce la durata di un trattamento
class DurationTreatmentHandler(BaseHandler):
    allowed_methods = ('GET',)
    @method_decorator(get_functionality_decorator)
    def read(self, request, nameA):
        print 'XMM API: start DurationTreatmentHandler'
        return { 'duration': Arms.objects.get(name = nameA).duration, 'typeTime': Arms.objects.get(name = nameA).type_of_time }

#controlla se un protocollo esiste
class ProtocolHandler(BaseHandler):
    allowed_methods = ('GET',)
    @method_decorator(get_functionality_decorator)
    def read(self, request, nameP):
        try:
            print 'XMM API: start ProtocolHandler'
            protocol = Protocols.objects.get(name = nameP)
            return { 'exist': '0'}
        except:
            return { 'exist': '1'}

#restitiusce i vari bracci di un protocollo, ricevendone il nome in input
class ArmsHandler(BaseHandler):
    allowed_methods = ('GET',)
    @method_decorator(get_functionality_decorator)
    def read(self, request, protocol):
        print 'XMM API: start ArmsHandler'
        arms = {}
        if protocol == "ALL":
            pha = Protocols_has_arms.objects.all()
        else:
            pha = Protocols_has_arms.objects.filter(id_protocol = Protocols.objects.get(name = protocol))
        i = 0
        for p in pha:
            arms.update({i:Arms.objects.get(id = p.id_arm.id).name +' --- ' + Arms.objects.get(id = p.id_arm.id).type_of_time})
            i = i + 1
        return { 'list_arm': json.dumps(arms) }

class GiveMeStepHandler(BaseHandler):
    allowed_methods = ('GET',)
    @method_decorator(get_functionality_decorator)
    def read(self, request, statusGantt, drugs):
        print 'XMM API: start GiveMeStepHandler'
        print 'g: ' + statusGantt +' d: ' + drugs
        list_steps = []
        list_drugs = []
        list_gantt = []
        step = {}
        drugs = drugs.replace(' ', '#')
        tuplas = string.split(drugs, '&')
        print tuplas
        for tupla in tuplas:
            if len(tupla) > 0:
                print tupla
                list_drugs.append(drugInfo(tupla))
                print list_drugs
        tuplas = string.split(statusGantt, '&')
        for tupla in tuplas:
            list_gantt.append(tupla)

        #scorri le due liste in parallelo
        #analizza la stringa di 0 e 1
        list_steps = []
        print '----'

        for k in list_gantt:
            print k
            list_steps.append(adjacencies(k))

        i = 0
        j = 0
        for ll in list_steps:
            print ll
            for l in ll:
                print l
                line = {'via':list_drugs[i].via, 'drug':list_drugs[i].drug, 'start':l[0], 'end':l[1]+1, 'dose':list_drugs[i].dose, 'schedule':list_drugs[i].schedule}
                step.update({j:line})
                j = j + 1
            i = i + 1
        return {'list_step':json.dumps(step)}

#restitiusce i vari step di un braccio, ricevendone il nome in input
class StepHandler(BaseHandler):
    allowed_methods = ('GET',)
    @method_decorator(get_functionality_decorator)
    def read(self, request, arm):
        print 'XMM API: start StepHandler'
        select = ['schedule', 'id_via', 'drugs_id', 'end_step', 'dose', 'start_step']
        i = 0
        list_step = []
        step = {}

        da = Details_arms.objects.filter(arms_id = Arms.objects.get(name = arm))

        for d in da:
            detail = Details_arms.objects.get(id = d.id)
            step.update({i:Simple(detail, select).getAttributes()})
            i = i + 1

        return { 'list_step': json.dumps(step) }

           
class NewGenIDExplant(BaseHandler):
    allowed_methods = ('GET')
    @method_decorator(get_functionality_decorator)
    def read(self, request, oldG, tissue, typeA, counter):
        try:
            print 'XMM API: start NewGenIDExplant'
            classOld = GenealogyID(oldG)
            classOld.setTissueType(tissue)
            classOld.setArchivedMaterial(typeA)
            counter = int(counter)  + 1
            print counter
            pattern = classOld.getGenID()[:22]
            al = Aliquots.objects.filter(id_genealogy__startswith=pattern)
            listAl = [int(GenealogyID(x.id_genealogy).getAliquotExtraction()) for x in al]
            maxAl = 0
            if len(listAl):
                maxAl = max(listAl)

            counter = counter + maxAl
            if len(str(counter)) == 1:
                counter = '0' + str(counter)
            #classOld.updateGenID({'tissueType':tissue, 'archiveMaterial2': typeA, 'aliqExtraction2':str(counter), '2derivationGen':'00'})
            #done = False
            #while not done:
            #    if len(Aliquots.objects.filter(id_genealogy = classOld.getGenID())) == 0:
            #        done = True
            #    else:
            #        counter = int(counter)  + 1
            #        if len(str(counter)) == 1:
            #            counter = '0' + str(counter)
            classOld.updateGenID({'aliqExtraction2':str(counter), '2derivationGen':'00'})
            return classOld.getGenID()
        except Exception, e:
            print 'XMM API error:', str(e)
            return 'err'

#restituisce i dati necessari per la il popolamento delle righe delle tabelle per le misurazioni
class MouseForMeasure(BaseHandler):
    allowed_methods = ('GET',)
    @method_decorator(get_functionality_decorator)
    def read(self, request, barcode, site):
        try:
            print 'XMM API: start MouseForMeasure'
            print get_WG_string()
            mouse = Mice.objects.get(barcode = barcode)
            print barcode
            print mouse
            biomice = BioMice.objects.filter(phys_mouse_id = mouse)
            print biomice
            if len(biomice) == 0:
                return {'status':'err', 'message':"Warning: this mouse is not implanted." }
            for biomouse in biomice:
                if len( Implant_details.objects.filter(id_mouse = biomouse, site = Site.objects.get( shortName = site )) ) > 0:
                    tempGeneral = { 'status':mouse.id_status.name, 'genID':biomouse.id_genealogy, 'group':biomouse.id_group.name, 'barcode':barcode}
                    tempExpl = {}
                    tempTreat = {}
                    tempW = {}

                    se, s = "", ""
                    if len(Programmed_explant.objects.filter(id_mouse= biomouse, done=0)) > 0:
                        scopeExplant = Programmed_explant.objects.filter(id_mouse=biomouse, done=0)[0]
                        se = scopeExplant.scopeNotes
                        scope = Scope_details.objects.get(id_scope_details = scopeExplant.id_scope_id)
                        s = scope.description
                    tempExpl['scope'] = s
                    tempExpl['scopeNotes'] = se

                    nameP, nameA, exp_start, expEnd, duration, typeT, forces_explant = "", "", "", "", "", "", ""
                    mhas = Mice_has_arms.objects.filter(id_mouse = biomouse, start_date__isnull = True, end_date__isnull = True)
                    if len(mhas) > 0:
                        mha = mhas[0]
                        nameP = mha.id_protocols_has_arms.id_protocol.name
                        nameA = mha.id_protocols_has_arms.id_arm.name
                        expEnd = str(mha.expected_end_date)
                        duration = mha.id_protocols_has_arms.id_arm.duration
                        typeT = mha.id_protocols_has_arms.id_arm.type_of_time
                        exp_start = str(mha.start_date)
                        if exp_start == 'None':
                            if mha.id_prT is not None:
                                exp_start = mha.id_prT.expectedStartDate
                            else:
                                exp_start = ""
                    else:
                        mhas = Mice_has_arms.objects.filter(id_mouse = biomouse, end_date__isnull = True)
                        if len(mhas) > 0:
                            mha = mhas[0]
                            nameP = mha.id_protocols_has_arms.id_protocol.name
                            nameA = mha.id_protocols_has_arms.id_arm.name
                            expEnd = str(mha.expected_end_date)
                            duration = mha.id_protocols_has_arms.id_arm.duration
                            typeT = mha.id_protocols_has_arms.id_arm.type_of_time
                            exp_start = str(mha.start_date)

                    if nameA != "":
                        a = Arms.objects.get(name = nameA)
                        forces_explant = a.forces_explant
                    tempTreat.update({ 'nameP': nameP, 'nameA': nameA, 'start': str(exp_start), 'exp_end': expEnd, 'duration': duration, 'typeTime': typeT, 'forces_explant': forces_explant })

                    quant = Quantitative_measure.objects.filter(id_mouse = biomouse, weight__gt = 0)
                    qual = Qualitative_measure.objects.filter(id_mouse = biomouse, weight__gt = 0)
                    series = []
                    maxQ = 0
                    if len(quant) > 0:
                        for q in quant:
                            series.append(q.id_series.id_series)
                    if len(qual) > 0:
                        for q in qual:
                            series.append(q.id_series.id_series)
                    if len(series) > 0:
                        maxQ = max(series)
                        s = Measurements_series.objects.get(pk = maxQ)
                        w = 0
                        dateW = ""
                        if s.id_type.description == 'qualitative':
                            try:
                                w = Qualitative_measure.objects.get(id_mouse = biomouse, id_series = s).weight
                                dateW = s.date
                            except:
                                pass
                        else:
                            try:
                                w = Quantitative_measure.objects.get(id_mouse = biomouse, id_series = s).weight
                                dateW = s.date
                            except:
                                pass
                        tempW.update({'w':str(w) + ' [g]', 'dateW':dateW})
                    else:
                        tempW.update( {'w':'-', 'dateW':'-'} )
                    return  {'status':'ok', 'generalInfo':tempGeneral, 'expl':tempExpl, 'treat':tempTreat, 'weight': tempW} 
            return {'status':'err', 'message':"Warning: this mouse hasn't an implant " + Site.objects.get(shortName = site).longName + ' [' + site + '].' }
        except Exception, e:
            print 'XMM API error:', str(e)
            return { "status":'err', 'message':str(e) }






#riceve in input un barcode e restituisce il genID del topo associato piu' altre info
class IdGenealogyHandler(BaseHandler):
    allowed_methods = ('GET',)
    @method_decorator(get_functionality_decorator)
    def read(self, request, barcode, site):
        try:
            print 'XMM API: start IdGenealogyHandler'
            site = Site.objects.get(shortName = site)
            mouse = Mice.objects.get(barcode = barcode.upper())
            biomice = BioMice.objects.filter(phys_mouse_id = mouse).order_by('-id')
            implants = Implant_details.objects.filter(site = site )
            #print implants
            for biomouse in biomice:
                if len(implants.filter(id_mouse = biomouse)) > 0:
                    measureFlag = False
                    supervisorNotes, supervisorDate, measureDate, measureNotes, explNotes = '','','','',''
                    #explNotes = Explant_details.objects.filter(id_mouse = mouse).aggregate(Max('rating'))
                    if len(Programmed_explant.objects.filter(id_mouse = biomouse)) > 0:
                        prExpl = Programmed_explant.objects.filter(id_mouse = biomouse).order_by("-id")[0]
                        explNotes = prExpl.scopeNotes
                    quant = Quantitative_measure.objects.filter(id_mouse = biomouse).order_by("-id")
                    qual = Qualitative_measure.objects.filter(id_mouse = biomouse).order_by("-id")
                    if len(quant) > 0 and len(qual) > 0:
                        measureFlag = True
                        if qual[0].id_series.date > quant[0].id_series.date:
                            measure = qual[0]
                        else:
                            measure = quant[0]
                    elif len(quant) > 0:
                        measure = quant[0]
                        measureFlag = True
                    elif len(qual) > 0:
                        measure = qual[0]
                        measureFlag = True
                    
                    if measureFlag == True:
                        measureDate = measure.id_series.date
                        measureNotes = measure.notes

                    if len(ProgrammedEvent.objects.filter(id_mouse = biomouse).order_by("-id")) > 0:
                        event = ProgrammedEvent.objects.filter(id_mouse = biomouse).order_by("-id")[0]
                        supervisorNotes = event.checkComments
                        supervisorDate = event.checkDate
                    return {'mouse_genealogy': biomouse.id_genealogy, 'explNotes': explNotes, 'measureNotes': measureNotes, 'measureDate':measureDate, 'supervisorNotes': supervisorNotes, "supervisorDate":supervisorDate, 'mouseStatus': mouse.id_status.name }
            return 0
        except Exception, e:
            print 'XMM API error:', str(e)
            return -1


#controlla se un braccio e' acuto (usato anche per verificarne l'esistenza)
class AcuteTreatmentHandler(BaseHandler):
    allowed_methods = ('GET',)
    @method_decorator(get_functionality_decorator)
    def read(self, request, nameT):
        print 'XMM API: start AcuteTreatmentHandler'
        if ' --- ' in nameT:
            nameP, nameA = splitNameT(nameT)
        else:
            nameA = nameT
        print nameA
        t = Arms.objects.get(name = nameA)
        print t.forces_explant
        return { 'forces_explant': t.forces_explant}


#restituisce l'ultimo peso di un topo con la relativa data
class LastWeight(BaseHandler):
    allowed_methods = ('GET')
    @method_decorator(get_functionality_decorator)
    def read(self, request, barcode):
        try:
            print 'XMM API: start LastWeight'
            listW = []
            m = Mice.objects.get(barcode = barcode)
            biomice = BioMice.objects.filter(phys_mouse_id = m)
            biomouse = biomice[0] #tanto i vari biomouse hanno lo stesso peso
            #for biomouse in biomice:
            quant = Quantitative_measure.objects.filter(id_mouse = biomouse, weight__gt = 0)
            qual = Qualitative_measure.objects.filter(id_mouse = biomouse, weight__gt = 0)
            series = []
            maxQ = 0
            if len(quant) > 0:
                for q in quant:
                    series.append(q.id_series.id_series)
            if len(qual) > 0:
                for q in qual:
                    series.append(q.id_series.id_series)
            if len(series) > 0:
                maxQ = max(series)
                s = Measurements_series.objects.get(pk = maxQ)
                w = 0
                dateW = ""
                if s.id_type.description == 'qualitative':
                    try:
                        w = Qualitative_measure.objects.get(id_mouse = biomouse, id_series = s).weight
                        dateW = s.date
                    except:
                        pass
                else:
                    try:
                        w = Quantitative_measure.objects.get(id_mouse = biomouse, id_series = s).weight
                        dateW = s.date
                    except:
                        pass
                return {'w':str(w) + ' [g]', 'dateW':dateW}
            else:
                print 't'
                return {'w':'-', 'dateW':'-'}
            return listW
        except Exception, e:
            print 'XMM API error:', str(e)
            return 'err'

class changeWGBiomiceH(BaseHandler):
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
                micelist=BioMice.objects.filter(id_genealogy__in=lisgen)
                print 'micelist',micelist                
                #se il gruppo e' delete allora devo sacrificare i topi in questione
                if workg=='delete':
                    sacrific=Status.objects.get(name='sacrified')
                    for mice in micelist:
                        #prendo il topo fisico
                        physmice = mice.phys_mouse_id
                        if physmice.death_date==None:
                            #imposto lo stato a sacrificato e la data di morte a oggi
                            physmice.id_status=sacrific
                            physmice.death_date=date.today()
                            physmice.save()
                            #devo fermare un eventuale trattamento sul topo
                            disable_graph()
                            mhas = Mice_has_arms.objects.filter(id_mouse= mice, end_date__isnull = True)
                            print 'treat',mhas
                            for mha in mhas:
                                mha.end_date = timezone.localtime(timezone.now())
                                mha.save()
                            #devo cancellare un eventuale espianto programmato sul topo
                            disable_graph()
                            lpe = Programmed_explant.objects.filter(id_mouse= mice, done=0)
                            print 'prog_expl',lpe
                            if len(lpe)!=0:
                                lpe[0].delete()

                else:
                    wgnuovo=WG.objects.get(name=workg)
                    print 'wgnuovo',wgnuovo
                    for mice in micelist:
                        if mice.id_genealogy not in cancwg:
                            #prendo i wg attuali
                            listamiceWg=BioMice_WG.objects.filter(biomice=mice)
                            for lmwg in listamiceWg:                    
                                #cancello i wg attuali
                                lmwg.delete()
                        #assegno le aliquote al wgnuovo
                        nuovowg,creato=BioMice_WG.objects.get_or_create(biomice=mice,
                                                                        WG=wgnuovo)
                        print 'nuovowg',nuovowg
                        cancwg.append(mice.id_genealogy)
            enable_graph()
            return {'data':'ok'}
        except Exception,e:
            print 'err',e
            transaction.rollback()
            return {'data':'error'}

class ShareBiomice(BaseHandler):
    allowed_methods = ('POST')
    def create(self, request):
        try:
            genidList=json.loads(request.POST.get('genidList'))
            wgList=json.loads(request.POST.get('wgList'))
            disable_graph()
            for genid in genidList:
                biom=BioMice.objects.get(id_genealogy=genid)
                for item in wgList:
                    wg=WG.objects.get(name=item)
                    if BioMice_WG.objects.filter(biomice=biom,WG=wg).count()==0:
                        m2m=BioMice_WG(biomice=biom,WG=wg)
                        m2m.save()
            enable_graph()
            return {'message':'ok'}
        except Exception,e:
            print 'err',e
            return {'message':'error'}
