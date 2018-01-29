#from datetime import date, timedelta, datetime
from django import forms
from django.db import transaction
from django.db.models import Q, Max
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import auth
from django.contrib.auth.models import User
from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import loader, Context, RequestContext
from django.template.loader import render_to_string
from django.utils import simplejson
from django.views.decorators.csrf import csrf_protect
from time import mktime
from xenopatients.forms import *
from xenopatients.models import *
from xenopatients.utils import *
from django.core.mail import send_mail, EmailMultiAlternatives
import os, cStringIO, csv, time, urllib, urllib2, datetime
from LASAuth.decorators import laslogin_required
from xenopatients.treatments import splitNameT, getNameT, getNamePT
from xenopatients.measure import removeOldExpl
from django.contrib.auth.decorators import user_passes_test
from apisecurity.decorators import *
from django.conf import settings
from lasEmail import *

@laslogin_required
@login_required
@permission_decorator('xenopatients.can_view_XMM_new_measurements')
def check(request):
    print 'XMM VIEW: start check.check'
    name = request.user.username
    groups = []
    event = ProgrammedEvent.objects.filter(id_status = EventStatus.objects.get(name = 'pending'))
    for e in event:
        groups.append(e.id_mouse.id_group)
    groups = uniq(groups)
    if request.method == 'POST':
        if "cancList" in request.POST:
            request.session['post'] = request.POST
            return HttpResponseRedirect(reverse("xenopatients.check.checkSave"))
    return render_to_response('check/check.html', {'name':name, 'groups':groups, 'formSD':ScopeForm()}, RequestContext(request))
    
@laslogin_required
@login_required
@permission_decorator('xenopatients.can_view_XMM_new_measurements')
def checkTreat(request):
    print 'XMM VIEW: start check.checkTreat'
    return render_to_response('check/startT.html', {'name':request.user.username, 'form': ExisistingProtocolsForm(),'date':str(datetime.date.today()+ datetime.timedelta(days=1))}, RequestContext(request))

def parseExpl(wasteList, mailDict, newExplList, forReport, operator, now):
    print 'wasteList',wasteList
    print 'mailDict',mailDict
    print 'newExplList',newExplList
    print 'forReport', forReport
    print 'operator', operator
    print 'now', now
    print 'XMM VIEW: start check.parseExpl'
    mList = []
    for newExpl in newExplList.split('|'):
        idEvent = newExpl.split('&')[0]
        print 'idEvent',idEvent
        scopeExplant = newExpl.split('&')[1]
        notesExplant = newExpl.split('&')[2]
        status = newExpl.split('&')[3]
        checkNotes = newExpl.split('&')[4]
        biomice = BioMice.objects.filter(id_genealogy = idEvent)
        if len(biomice) > 0:
            #azione eredita da un 'fratello', questo topo non aveva un suo evento in questo gruppo
            #rifiutare eventuali altri eventi pendenti su questo topo (?)
            biomouse = biomice[0]
            events = ProgrammedEvent.objects.filter(id_mouse = biomouse, id_status = EventStatus.objects.get(name = 'pending'))
            for e in events:
                e.id_status = EventStatus.objects.get(name = 'modified')
                e.save()
            newEvent = ProgrammedEvent(insertionDate = datetime.date.today(), 
                                       id_mouse = biomouse,
                                       measureOperator = operator,
                                       id_status = EventStatus.objects.get(name = 'accepted'),
                                       checkDate = datetime.date.today(),
                                       checkComments = checkNotes,
                                       checkOperator = operator)
            newEvent.save()
            id_event = newEvent
            forReport['acc'].append(biomouse.id_genealogy)
        else:
            #aggiungere l'evento nella lista di liste con i dati per il report
            forReport['mod'].append(idEvent)
            #rifiutare l'evento precedentemente programmato
            event = ProgrammedEvent.objects.get(id = idEvent)
            event.id_status = EventStatus.objects.get(name = 'modified')
            event.checkOperator = operator
            event.checkComments = checkNotes
            event.checkDate = datetime.date.today()
            event.save()
            mailDict.update({event.measureOperator.username:[[],[]]})
            biomouse = event.id_mouse
            #crearne uno nuovo gia' approvato con un riferimento al precedente
            newEvent = ProgrammedEvent(insertionDate = datetime.date.today(), 
                                       id_mouse = biomouse,
                                       measureOperator = operator,
                                       id_status = EventStatus.objects.get(name = 'accepted'),
                                       id_quant = event.id_quant,
                                       id_qual = event.id_qual,
                                       checkDate = datetime.date.today(),
                                       checkComments = checkNotes,
                                       checkOperator = operator,
                                       id_parent = event)
            newEvent.save()
            try:
                wasteList.pop(wasteList.index(biomouse))
            except:
                pass
        if status == 'ready for explant':
            try:
                mList.index(biomouse)
            except Exception:
                removeOldExpl(biomouse)
                prE = Pr_explant(id_event = newEvent, id_scope = Scope_details.objects.get(description = scopeExplant), scopeNotes = notesExplant)
                prE.save()
                mList.append(biomouse)
                pass
        elif status == 'explantLite':
            prS = Pr_changeStatus(id_event = newEvent, newStatus = Status.objects.get(name = 'explantLite'))
            prS.save()
    return wasteList, mailDict,forReport

def parseTreat(wasteList, mailDict, newTreatList,forReport, operator, toWaste, now):
    print 'XMM VIEW: start check.parseTreat'
    toWaste = True
    mList = []
    #rifiutare l'evento precedentemente programmato
    for newTreat in newTreatList.split('|'):
        idEvent = newTreat.split('&')[0]
        nameT = newTreat.split('&')[1]
        startDate = newTreat.split('&')[2]
        checkNotes = newTreat.split('&')[3]
        biomice = BioMice.objects.filter(id_genealogy = idEvent)
        if len(biomice) > 0:
            biomouse = biomice[0]
            qual = None
            quant = None
            event = None
        else:
            event = ProgrammedEvent.objects.get(id = idEvent)
            biomouse = event.id_mouse
            qual = event.id_qual
            quant = event.id_quant
            #rifiutare l'evento precedentemente programmato
            event = ProgrammedEvent.objects.get(id = idEvent)
            event.id_status = EventStatus.objects.get(name = 'modified')
            event.checkOperator = operator
            event.checkComments = checkNotes
            event.checkDate = datetime.date.today()
            event.save()
            mailDict.update({event.measureOperator.username:[[],[]]})
        if nameT == 'STOPPED':
            #stopMicehasArms
            try:
                mhas = Mice_has_arms.objects.filter(id_mouse = biomouse, end_date__isnull = True)
                for mha in mhas:
                    mha.end_date = datetime.datetime.now()
                    mha.save()
            except Exception, e:
                pass
            if len(biomice) > 0:
                forReport['acc'].append(biomouse.id_genealogy)
            else:
                event.id_status = EventStatus.objects.get(name = 'accepted')
                event.save()
                forReport['acc'].append(idEvent)
        else:
            #aggiungere l'evento nella lista di liste con i dati per il report
            if len(biomice) > 0:
                forReport['acc'].append(idEvent)
            else:
                forReport['mod'].append(idEvent)
            stopTreat(biomouse, now)
            #crearne uno nuovo gia' approvato con un riferimento al precedente
            newEvent = ProgrammedEvent(insertionDate = datetime.date.today(), 
                                       id_mouse = biomouse,
                                       measureOperator = operator,
                                       id_status = EventStatus.objects.get(name = 'accepted'),
                                       id_quant = quant,
                                       id_qual = qual,
                                       checkDate = datetime.date.today(),
                                       checkComments = checkNotes,
                                       checkOperator = operator,
                                       id_parent = event)
            newEvent.save()
            try:
                wasteList.pop(wasteList.index(biomouse))
            except:
                pass
            nameP, nameA = splitNameT(nameT)
            struct = time.strptime(startDate+ ':00', "%Y-%m-%d %H:%M:%S")
            start = datetime.datetime.fromtimestamp(mktime(struct))
            try:
                mList.index(biomouse)
            except Exception,e:
                prT = Pr_treatment(id_event = newEvent, 
                                   id_pha = Protocols_has_arms.objects.get(id_arm = Arms.objects.get(name = nameA), id_protocol = Protocols.objects.get(name = nameP)), 
                                   expectedStartDate = start)
                mList.append(biomouse)
                prT.save()
                pass
            physM = biomouse.phys_mouse_id
            if physM.id_status == Status.objects.get(name = 'waste'):
                physM.id_status = Status.objects.get(name = 'implanted')
                physM.save()
    return wasteList, mailDict, toWaste,forReport

def parseCanc(wasteList, mailDict, cancList,forReport, operator, now):
    print 'XMM VIEW: start check.parseCanc'
    for canc in cancList.split('|'):
        idEvent = canc.split('&')[0]
        checkNotes = canc.split('&')[1]
        biomice = BioMice.objects.filter(id_genealogy = idEvent)
        if len(biomice) > 0:
            biomouse = biomice[0]
            #qui in realta' non faccio niente
            #non cancello gli eventuali eventi dei sibling, in questo caso il tasto cancella solo quelle appena
            #assegnate dal client, quindi dal server non devo fare niente
        else:
            #aggiungere l'evento nella lista di liste con i dati per il report
            forReport['rej'].append(idEvent)                
            #rifiutare l'evento precedentemente programmato
            event = ProgrammedEvent.objects.get(id = idEvent)
            event.id_status = EventStatus.objects.get(name = 'rejected')
            event.checkOperator = operator
            event.checkComments = checkNotes
            event.checkDate = datetime.date.today()
            event.save()
            pr_explant = Pr_explant.objects.filter(id_event=event)
            if len(pr_explant):
                phys_mice = Mice.objects.get(pk= event.id_mouse.phys_mouse_id.id )
                phys_mice.id_status = Status.objects.get(name='implanted')
                phys_mice.save()   
            mailDict.update({event.measureOperator.username:[[],[]]})
    return wasteList, mailDict,forReport

def parsePending(wasteList, mailDict, pendingList,forReport, operator, toWaste, now):
    print 'XMM VIEW: start check.parsePending'
    for pending in pendingList.split('|'):
        idEvent = pending.split('&')[0]
        checkNotes = pending.split('&')[1]
        #aggiungere l'evento nella lista di liste con i dati per il report
        forReport['acc'].append(idEvent)
        #accettare l'evento precedentemente programmato
        event = ProgrammedEvent.objects.get(id = idEvent)
        event.id_status = EventStatus.objects.get(name = 'accepted')
        event.checkOperator = operator
        event.checkComments = checkNotes
        event.checkDate = datetime.date.today()
        event.save()
        m = event.id_mouse
        physM = m.phys_mouse_id
        if len(Pr_changeStatus.objects.filter(id_event = event)) == 1:
            if Pr_changeStatus.objects.get(id_event = event).newStatus.name == 'toSacrifice':
                stopTreat(event.id_mouse, now)
                cancelProgrammedExpl(event.id_mouse)
        if len(Pr_treatment.objects.filter(id_event = event)) == 1:
            toWaste = True
            if physM.id_status == Status.objects.get(name = 'waste'):
                physM.id_status = Status.objects.get(name = 'implanted')
                physM.save()
        mailDict.update({event.measureOperator.username:[[],[]]})
        if len(Pr_changeStatus.objects.filter(id_event = event)) == 1 or len(Pr_treatment.objects.filter(id_event = event)) == 1 or len(Pr_explant.objects.filter(id_event = event)) == 1:
            try:
                wasteList.pop(wasteList.index(biomouse))
            except:
                pass
    return wasteList, mailDict, toWaste,forReport
    
def parseSacr(wasteList, mailDict, sacrificeList, forReport, operator, now):
    print 'XMM VIEW: start check.parseSacr'
    for sacrifice in sacrificeList.split('|'):
        idEvent = sacrifice.split('&')[0]
        checkNotes = sacrifice.split('&')[1]
        biomice = BioMice.objects.filter(id_genealogy = idEvent)
        if len(biomice) > 0:
            biomouse = biomice[0]
            qual = None
            quant = None
            forReport['acc'].append(biomouse.id_genealogy)
            event = None
        else:
            #aggiungere l'evento nella lista di liste con i dati per il report
            forReport['mod'].append(idEvent)
            #rifiutare l'evento precedentemente programmato
            event = ProgrammedEvent.objects.get(id = idEvent)
            event.id_status = EventStatus.objects.get(name = 'rejected')
            event.checkOperator = operator
            event.checkComments = checkNotes
            event.checkDate = datetime.date.today()
            event.save()
            biomouse = event.id_mouse
            quant = event.id_quant
            qual = event.id_qual
            mailDict.update({event.measureOperator.username:[[],[]]})
        stopTreat(biomouse, now)
        cancelProgrammedExpl(biomouse)
        #crearne uno nuovo gia' approvato con un riferimento al precedente
        newEvent = ProgrammedEvent(insertionDate = datetime.date.today(), 
                                   id_mouse = biomouse,
                                   measureOperator = operator,
                                   id_status = EventStatus.objects.get(name = 'accepted'),
                                   id_quant = quant,
                                   id_qual = qual,
                                   checkDate = datetime.date.today(),
                                   checkComments = checkNotes,
                                   checkOperator = operator,
                                   id_parent = event)
        newEvent.save()
        try:
            wasteList.pop(wasteList.index(biomouse))
        except:
            pass
        prS = Pr_changeStatus(id_event = newEvent, newStatus = Status.objects.get(name = 'toSacrifice'))
        prS.save()
    return wasteList, mailDict,forReport

def parseNA(notApplicableList, forReport, operator, now, mailDict, wasteList):
    print 'XMM VIEW: start check.parseNA'
    for idEvent in notApplicableList.split('|'):
        #aggiungere l'evento nella lista di liste con i dati per il report
        forReport['nap'].append(idEvent)
        #accettare l'evento precedentemente programmato
        event = ProgrammedEvent.objects.get(id = idEvent)
        event.id_status = EventStatus.objects.get(name = 'not applicable')
        event.checkOperator = operator
        #event.checkComments = checkNotes
        event.checkDate = datetime.date.today()
        event.save()
        mailDict.update({event.measureOperator.username:[[],[]]})
        event = ProgrammedEvent.objects.get(id = idEvent)
        try:
            wasteList.pop(wasteList.index(event.id_mouse))
        except:
            pass
    return mailDict,forReport

def reportAcc(mailDict, forReport, email, msgItem , request):
    #eventi accettati senza modifiche
    print 'XMM VIEW: start check.reportAcc'
    accList = []
    for ev in forReport['acc']:
        if len(BioMice.objects.filter(id_genealogy = ev)) > 0:
            genID = ev
            event = ProgrammedEvent.objects.filter(id_mouse = BioMice.objects.get(id_genealogy = ev), 
                                                insertionDate = datetime.date.today()).order_by('-id')[0]
        else:
            event = ProgrammedEvent.objects.get(pk = ev)
            genID = event.id_mouse.id_genealogy
        dateM = ""
        value = ""
        notes = "-"
        scopeExplant = "-"
        wgMouse=BioMice_WG.objects.filter(biomice=BioMice.objects.get(id_genealogy=genID)).values_list('WG__name', flat=True)
        try:
            if event.id_qual:
                dateM = str(event.id_qual.id_series.date)
                value = event.id_qual.id_value.value
                if event.id_qual.notes:
                    notes = event.id_qual.notes
            elif event.id_quant:
                dateM = str(event.id_quant.id_series.date)
                value = str(event.id_quant.volume)
                if event.id_quant.notes:
                    notes = event.id_quant.notes
        except:
            pass
        checkNotes = "-"
        if event.checkComments:
            checkNotes = event.checkComments
        status = event.id_mouse.phys_mouse_id.id_status.name
        explant = "-"
        try:
            p = Programmed_explant.objects.get(id_mouse = event.id_mouse, done = '0')
            explant = "ready for explant"
            scopeExplant = p.id_scope.description
        except:
            explant = "not programmed for explant"
            pass
        treatment,startDate, duration = "-", "-", "-"
        try:
            t = Mice_has_arms.objects.get(id_mouse = event.id_mouse, start_date__isnull = True, end_date__isnull = True)
            treatment = getNameT(t)
            startDate = str(t.id_prT.expectedStartDate)
            duration = str(t.id_protocols_has_arms.id_arm.duration) + ' [' + str(t.id_protocols_has_arms.id_arm.type_of_time) + ']'
        except Exception, e:
            if len(Mice_has_arms.objects.filter(id_mouse = event.id_mouse, end_date__isnull = True)) > 0:
                t = Mice_has_arms.objects.filter(id_mouse = event.id_mouse, end_date__isnull = True)[0]
                treatment = getNameT(t)
                startDate = str(t.start_date)
                duration = str(t.id_protocols_has_arms.id_arm.duration)+ ' [' + str(t.id_protocols_has_arms.id_arm.type_of_time) + ']'
            pass
        string = "<tr><td>" + genID + "</td><td>" + dateM + "</td><td>" + value + "</td><td>" + notes + "</td><td>" + checkNotes + "</td><td>" + status + "</td><td>" + explant + "</td><td>" + scopeExplant + "</td><td>" + treatment + "</td><td>" + startDate + "</td><td>" + duration + "</td></tr>"
        accList.append(string)
        for wgName in wgMouse:
            if wgName not in msgItem:
                msgItem[wgName]=dict()
                msgItem[wgName]['Accepted']=list()
                msgItem[wgName]['Modified']=list()
                msgItem[wgName]['Accepted'].append('Genealogy ID\tDate\tValue\tNotes\tCheck notes\tStatus\tExplant\tScopeExplant\tTreatment\tStart treatment\tDuration')
                msgItem[wgName]['Modified'].append('Genealogy ID\tDate\tValue\tNotes\tCheck notes\tStatus\tExplant\tScopeExplant\tTreatment\tStart treatment\tDuration')
            msgItem[wgName]['Accepted'].append(genID+'\t'+dateM+'\t'+value+'\t'+notes+'\t'+checkNotes+'\t'+status+'\t'+explant+'\t'+scopeExplant+'\t'+treatment+'\t'+startDate+'\t'+duration)
            msgItem[wgName]['Modified'].append(genID+'\t'+dateM+'\t'+value+'\t'+notes+'\t'+checkNotes+'\t'+status+'\t'+explant+'\t'+scopeExplant+'\t'+treatment+'\t'+startDate+'\t'+duration)
        for wgName,msg in msgItem.items():
            if wgName in wgMouse:
                email.addRoleEmail([wgName], 'Executor', [request.user.username])
                email.addRoleEmail([wgName], 'Planner', [event.measureOperator.username])
        mailDict[event.measureOperator.username][0].append(string)
        mailDict[event.measureOperator.username][1].append(string) 
    
    return mailDict,  accList, email, msgItem

def reportMod(mailDict,  forReport, email, msgItem, request):
    print 'XMM VIEW: start check.reportMod'
    #xeno: eventi modificati
    modMice = []
    modList = []
    mod = False

    for ev in forReport['mod']:
        mod = True
        event = ProgrammedEvent.objects.get(pk = ev)
        forMail = event.measureOperator.username
        genID = event.id_mouse.id_genealogy
        if genID not in modMice:
            wgMouse=BioMice_WG.objects.filter(biomice=BioMice.objects.get(id_genealogy=genID)).values_list('WG__name', flat=True)
            modMice.append(genID)
            dateM = ""
            value = ""
            notes = "-"
            scopeExplant = "-"
            if event.id_qual:
                dateM = str(event.id_qual.id_series.date)
                value = event.id_qual.id_value.value
                if event.id_qual.notes:
                    notes = event.id_qual.notes
            elif event.id_quant:
                dateM = str(event.id_quant.id_series.date)
                value = str(event.id_quant.volume)
                if event.id_quant.notes:
                    notes = event.id_quant.notes
            checkNotes = "-"
            if event.checkComments:
                checkNotes = event.checkComments
            status = event.id_mouse.phys_mouse_id.id_status.name
            explant = "-"
            try:
                p = Pr_explant.objects.get(id_event = event)
                explant = "ready for explant"
                scopeExplant = p.id_scope.description
            except:
                explant = "not programmed for explant"
                pass
            treatment = "-"
            startDate = "-"
            duration = "-"
            try:
                t = Pr_treatment.objects.get(id_event = event)
                treatment = getNmaePT(t)
                startDate = str(t.expectedstartDate)
                duration = str(t.id_pha.id_arm.duration) + ' [' + str(t.id_pha.id_arm.type_of_time) + ']'
            except Exception,e:
                pass
            stringOld = "<tr style='background-color:#E68080;'><td>" + genID + "</td><td>" + dateM + "</td><td>" + value + "</td><td>" + notes + "</td><td>-</td><td>" + status + "</td><td>" + explant + "</td><td>" + scopeExplant + "</td><td>" + treatment + "</td><td>" + startDate + "</td><td>" + duration + "</td></tr>"
            modList.append(stringOld)
            stringOldMail=genID+'\t'+dateM+'\t'+value+'\t'+notes+'\t-\t'+status+'\t'+explant+'\t'+scopeExplant+'\t'+treatment+'\t'+startDate+'\t'+duration
            try:
                event = ProgrammedEvent.objects.get(id_parent = ProgrammedEvent.objects.get( pk = ev))
            except Exception,e: 
                pass
            explant = "-"
            try:
                p = Programmed_explant.objects.get(id_mouse = event.id_mouse, done = '0')
                explant = "ready for explant"
                scopeExplant = p.id_scope.description
            except Exception, e:
                explant = "not programmed for explant"
                pass
            treatment = "-"
            startDate = "-"
            duration = "-"
            try:
                t = Mice_has_arms.objects.get(id_mouse = event.id_mouse, start_date__isnull = True, end_date__isnull = True)
                treatment = getNameT(t)
                startDate = str(t.id_prT.expectedStartDate)
                duration = str(t.id_protocols_has_arms.id_arm.duration) + ' [' + str(t.id_protocols_has_arms.id_arm.type_of_time) + ']'
            except Exception, e:
                if len(Mice_has_arms.objects.filter(id_mouse = event.id_mouse, end_date__isnull = True)) > 0:
                    t = Mice_has_arms.objects.filter(id_mouse = event.id_mouse, end_date__isnull = True)[0]
                    treatment = getNameT(t)
                    startDate = str(t.start_date)
                    duration = str(t.id_protocols_has_arms.id_arm.duration) + ' [' + str(t.id_protocols_has_arms.id_arm.type_of_time) + ']'
                pass
            stringNew = "<tr style='background-color:#85E085;'><td>" + genID + "</td><td>" + dateM + "</td><td>" + value + "</td><td>" + notes + "</td><td>" + checkNotes + "</td><td>" + status + "</td><td>" + explant + "</td><td>" + scopeExplant + "</td><td>" + treatment + "</td><td>" + startDate + "</td><td>" + duration + "</td></tr>"
            stringNewMail=genID+'\t'+dateM+'\t'+value+'\t'+notes+'\t'+checkNotes+'\t'+status+'\t'+explant+'\t'+scopeExplant+'\t'+treatment+'\t'+startDate+'\t'+duration
            modList.append(stringNew)
            for wgName in wgMouse:
                if wgName not in msgItem:
                    msgItem[wgName]=dict() 
                    msgItem[wgName]['Accepted']=list()
                    msgItem[wgName]['Modified']=list()
                    msgItem[wgName]['Accepted'].append('Genealogy ID\tDate\tValue\tNotes\tCheck notes\tStatus\tExplant\tScopeExplant\tTreatment\tStart treatment\tDuration')
                    msgItem[wgName]['Modified'].append('Genealogy ID\tDate\tValue\tNotes\tCheck notes\tStatus\tExplant\tScopeExplant\tTreatment\tStart treatment\tDuration')
                msgItem[wgName]['Accepted'].append(stringOldMail)
                msgItem[wgName]['Modified'].append(stringNewMail)
            for wgName,msg in msgItem.items():
                if wgName in wgMouse:
                    email.addRoleEmail([wgName], 'Executor', [request.user.username])
                    email.addRoleEmail([wgName], 'Planner', [forMail])
            mailDict[forMail][0].append(stringOld)
            mailDict[forMail][1].append(stringNew) 
    return mailDict, modList, mod, email, msgItem

def reportRej(mailDict,  forReport, email, msgItem, request):
    print 'XMM VIEW: start check.reportRej'
    #eventi rifiutati
    rejList = []
    try:
        for ev in forReport['rej']:
            event = ProgrammedEvent.objects.get(pk = ev)
            genID = event.id_mouse.id_genealogy
            dateM = ""
            value = ""
            notes = "-"
            wgMouse=BioMice_WG.objects.filter(biomice=BioMice.objects.get(id_genealogy=genID)).values_list('WG__name', flat=True)
           
            if event.id_qual:
                dateM = str(event.id_qual.id_series.date)
                value = event.id_qual.id_value.value
                if event.id_qual.notes:
                    notes = event.id_qual.notes
            elif event.id_quant:
                dateM = str(event.id_quant.id_series.date)
                value = str(event.id_quant.volume)
                if event.id_quant.notes:
                    notes = event.id_quant.notes
            checkNotes = "-"
            if event.checkComments:
                checkNotes = event.checkComments
            status = event.id_mouse.phys_mouse_id.id_status.name
            explant, scopeExplant = "-", "-"
            try:
                p = Pr_explant.objects.get(id_event = event)
                explant = "ready for explant"
                scopeExplant = p.id_scope.description
            except:
                explant = "not programmed for explant"
                pass
            treatment, startDate, duration, pTreatment, pStartDate, pDuration = "-", "-", "-","-", "-", "-"
            try:
                t = Pr_treatment.objects.get(id_event = event)
                pTreatment = getNamePT(t)
                pStartDate = str(t.expectedStartDate)
                pDuration = str(t.id_pha.id_arm.duration) + ' [' + str(t.id_pha.id_arm.type_of_time) + ']'
            except Exception,e:
                try:
                    t = Mice_has_arms.objects.get(id_mouse = event.id_mouse, start_date__isnull = True, end_date__isnull = True)
                    treatment = getNameT(t)
                    startDate = str(t.id_prT.expectedStartDate)
                    duration = str(t.id_protocols_has_arms.id_arm.duration) + ' [' + str(t.id_protocols_has_arms.id_arm.type_of_time) + ']'
                except Exception, e:
                    if len(Mice_has_arms.objects.filter(id_mouse = event.id_mouse, end_date__isnull = True)) > 0:
                        t = Mice_has_arms.objects.filter(id_mouse = event.id_mouse, end_date__isnull = True)[0]
                        treatment = getNameT(t)
                        startDate = str(t.start_date)
                        duration = str(t.id_protocols_has_arms.id_arm.duration) + ' [' + str(t.id_protocols_has_arms.id_arm.type_of_time) + ']'
                    pass
                pass
            stringOld = "<tr><td>" + genID + "</td><td>" + dateM + "</td><td>" + value + "</td><td>" + notes + "</td><td>" + checkNotes + "</td><td>" + status + "</td><td>" + explant + "</td><td>" + scopeExplant + "</td><td>" + pTreatment + "</td><td>" + pStartDate + "</td><td>" + pDuration + "</td></tr>"
            stringOldMail=genID+'\t'+dateM+'\t'+value+'\t'+notes+'\t'+checkNotes+'\t'+status+'\t'+explant+'\t'+scopeExplant+'\t'+pTreatment+'\t'+pStartDate+'\t'+pDuration
            rejList.append(stringOld)
            stringNew = "<tr><td>" + genID + "</td><td>" + dateM + "</td><td>" + value + "</td><td>" + notes + "</td><td>" + checkNotes + "</td><td>" + status + "</td><td>" + explant + "</td><td>" + scopeExplant + "</td><td>" + treatment + "</td><td>" + startDate + "</td><td>" + duration + "</td></tr>"
            stringNewMail=genID+'\t'+dateM+'\t'+value+'\t'+notes+'\t'+checkNotes+'\t'+status+'\t'+explant+'\t'+scopeExplant+'\t'+treatment+'\t'+startDate+'\t'+duration
            mailDict[event.measureOperator.username][0].append(stringOld)
            mailDict[event.measureOperator.username][1].append(stringNew)

            for wgName in wgMouse:
                if wgName not in msgItem:
                    msgItem[wgName]=dict() 
                    msgItem[wgName]['Accepted']=list()
                    msgItem[wgName]['Modified']=list()
                    msgItem[wgName]['Accepted'].append('Genealogy ID\tDate\tValue\tNotes\tCheck notes\tStatus\tExplant\tScopeExplant\tTreatment\tStart treatment\tDuration')
                    msgItem[wgName]['Modified'].append('Genealogy ID\tDate\tValue\tNotes\tCheck notes\tStatus\tExplant\tScopeExplant\tTreatment\tStart treatment\tDuration')
                msgItem[wgName]['Accepted'].append(stringOldMail)
                msgItem[wgName]['Modified'].append(stringNewMail)

            for wgName,msg in msgItem.items():
                if wgName in wgMouse:
                    email.addRoleEmail([wgName], 'Executor', [request.user.username])
                    email.addRoleEmail([wgName], 'Planner', [event.measureOperator.username])


    except Exception, e:
        print 'err', str(e)
    return mailDict, rejList, email, msgItem

def reportNap(mailDict,  forReport, email, msgItem, request):
    print 'XMM VIEW: start check.reportNap'
    #eventi rifiutati
    napList = []
    try:
        for ev in forReport['nap']:
            event = ProgrammedEvent.objects.get(pk = ev)
            genID = event.id_mouse.id_genealogy
            dateM = ""
            value = ""
            notes = "-"
            wgMouse=BioMice_WG.objects.filter(biomice=BioMice.objects.get(id_genealogy=genID)).values_list('WG__name', flat=True)
            if event.id_qual:
                dateM = str(event.id_qual.id_series.date)
                value = event.id_qual.id_value.value
                if event.id_qual.notes:
                    notes = event.id_qual.notes
            elif event.id_quant:
                dateM = str(event.id_quant.id_series.date)
                value = str(event.id_quant.volume)
                if event.id_quant.notes:
                    notes = event.id_quant.notes
            checkNotes = "-"
            if event.checkComments:
                checkNotes = event.checkComments
            status = event.id_mouse.phys_mouse_id.id_status.name
            stringOld = "<tr><td>" + genID + "</td><td>" + dateM + "</td><td>" + value + "</td><td>" + notes + "</td><td>" + status + "</td></tr>"
            stringOldMail=genID+'\t'+dateM+'\t'+value+'\t'+notes+'\t-\t'+status+'\t-\t-\t-\t-\t-'
            napList.append(stringOld)
            stringNew = "<tr><td>" + genID + "</td><td>" + dateM + "</td><td>" + value + "</td><td>" + notes + "</td><td>" + status + "</td></tr>"
            stringNewMail=genID+'\t'+dateM+'\t'+value+'\t'+notes+'\t-\t'+status+'\t-\t-\t-\t-\t-'
            mailDict[event.measureOperator.username][0].append(stringOld)
            mailDict[event.measureOperator.username][1].append(stringNew)
            for wgName in wgMouse:
                if wgName not in msgItem:
                    msgItem[wgName]=dict()
                    msgItem[wgName]['Accepted']=list()
                    msgItem[wgName]['Modified']=list()
                    msgItem[wgName]['Accepted'].append('Genealogy ID\tDate\tValue\tNotes\tCheck notes\tStatus\tExplant\tScopeExplant\tTreatment\tStart treatment\tDuration')
                    msgItem[wgName]['Modified'].append('Genealogy ID\tDate\tValue\tNotes\tCheck notes\tStatus\tExplant\tScopeExplant\tTreatment\tStart treatment\tDuration')
                msgItem[wgName]['Accepted'].append(stringOldMail)
                msgItem[wgName]['Modified'].append(stringNewMail)
            for wgName,msg in msgItem.items():
                if wgName in wgMouse:
                    email.addRoleEmail([wgName], 'Executor', [request.user.username])
                    email.addRoleEmail([wgName], 'Planner', [event.measureOperator.username])

    except Exception, e:
        print 'err', str(e)
    return mailDict, napList, email, msgItem

@transaction.commit_manually 
@laslogin_required
@login_required
@permission_decorator('xenopatients.can_view_XMM_new_measurements')
def checkSave(request):
    print 'XMM VIEW: start check.checkSave'
    name = request.user.username
    operator = User.objects.get(username = name)
    data =  request.session['post']
    print 'sessionCheck',data
    newExplList = data['newExplList']
    newTreatList = data['newTreatList']
    cancList = data['cancList']
    pendingList = data['pendingList']
    sacrificeList = data['sacrificeList']
    notApplicableList = data['notApplicableList']
    groupName = data['group']
    toWaste = False
    wasteList = []
    #nelle 3 liste nella lista dichiarate qui di seguito, inserisco gli ID dei vari eventi accettati, rifiutati e modificati per costruire poi il report
    forReport = {'acc':[], 'mod':[], 'rej':[], 'nap':[]}
    mailDict = {} #dizionario per gestire i vari report pdf nelle mail organizzati per operatore

    print data
    try:
        g = Groups.objects.get(name = groupName)
        for m in BioMice.objects.filter(id_group = g):
            if not m.phys_mouse_id.death_date:                
                wasteList.append(m)
        mList = []
        now = datetime.datetime.now()
        #per ogni ramo dei vari if:
        #   - salvare gli eventuali commenti del check
        #   - mandare una mail a chi aveva programmato l'operazione e al suo supervisore
        if len(newExplList) > 0:
            wasteList, mailDict,forReport = parseExpl(wasteList, mailDict, newExplList,forReport, operator, now)
        if len(newTreatList) > 0:
            wasteList, mailDict, toWaste, forReport = parseTreat(wasteList, mailDict, newTreatList,forReport, operator, toWaste, now)
        if len(cancList) > 0:
            wasteList, mailDict,forReport = parseCanc(wasteList, mailDict, cancList,forReport, operator, now)
        if len(pendingList) > 0:
            wasteList, mailDict, toWaste, forReport = parsePending(wasteList, mailDict, pendingList,forReport, operator, toWaste, now)
        if len(sacrificeList) > 0:
            wasteList, mailDict,forReport = parseSacr(wasteList, mailDict, sacrificeList,forReport, operator, now)
        if len(notApplicableList) > 0:
            mailDict,forReport = parseNA(notApplicableList, forReport, operator, now, mailDict, wasteList)
        print forReport
        print '11'
        if toWaste:
            for w in wasteList:
                physW = w.phys_mouse_id
                if len(Mice_has_arms.objects.filter(id_mouse = w)) == 0:
                    #nessun trattamento pregresso
                    physW.id_status = Status.objects.get(name = 'waste')
                    physW.save()
                if len(Mice_has_arms.objects.filter(id_mouse = w, start_date__isnull = True, end_date__isnull = False)) > 0:
                    #trattamento proposto, approvato ma non finalizzato
                    physW.id_status = Status.objects.get(name = 'waste')
                    physW.save()
        request.session['forReport'] = forReport
        transaction.commit()
        #PREPARAZIONE DATI PER REPORT
        print "XMM: check.checkSave -> PREPARAZIONE DATI PER REPORT"
        print mailDict

        email = LASEmail (functionality=get_functionality(), wgString=get_WG_string())
        #PARSARE I VARI REPORTACC ecc. , CREARE FILE DISTINTI, TROVARE I WG E APPENDERE STI FILES, UNO PER FUNZIONE
        modMice = []
        mod = False
        msgItem={}
        #eventi accettati senza modifiche
        mailDict, accList, email , msgItem= reportAcc(mailDict, forReport, email, msgItem, request)
        print 'acc', mailDict
        #eventi modificati
        mailDict, modList, mod, email, msgItem = reportMod(mailDict, forReport, email, msgItem, request)
        #eventi rifiutati
        print 'mod', mailDict
        mailDict, rejList, email, msgItem = reportRej(mailDict, forReport, email, msgItem, request)
        print 'rej', mailDict
        mailDict, napList, email, msgItem = reportNap(mailDict, forReport, email, msgItem, request)
        print 'nap', mailDict
        print mailDict, accList, modList, mod, rejList, napList
        print 'XMM: check.checkSave -> mailing'
        wgSet=set()
        for wgName,msg in msgItem.items():
            email.addMsg([wgName], msg['Accepted'],'[Accepted actions]')
            email.addMsg([wgName], msg['Accepted'],'[Modified actions]')
            wgSet.add(wgName)
        for wgName in wgSet:
            email.appendSubject([wgName],groupName)       
        try:
            email.send()
        except Exception,e:
            print 'XMM VIEW explant.explantReport: 1) ' +  str(e)
            pass
    
        try:
            for k in mailDict.keys():
                operator = User.objects.get(username = k)
                mailOperator = operator.email
                wg = WG.objects.get(id= WG_User.objects.filter(user=operator).values_list('WG', flat=True).distinct()[0])
                mailSupervisor = wg.owner.email
                #qui deve ancora inviare un report via mail all'operatore che aveva misurato il topo
                #una mail per ogni operatore che ha lavorato nelle ultime azioni pending di quel gruppo
                file_data = render_to_string('check/reportPDF.html', {'accList': mailDict[k][0],'modList':mailDict[k][1]}, RequestContext(request))
                if mod:
                    subject, from_email = '[MODIFIED] Checked actions for group ' + groupName, settings.EMAIL_HOST_USER
                else:
                    subject, from_email = '[ACCEPTED] Checked actions for group ' + groupName, settings.EMAIL_HOST_USER
                text_content = 'This is an important message.'
                html_content = file_data
                msg = EmailMultiAlternatives(subject, text_content, from_email, [mailOperator, mailSupervisor])
                msg.attach_alternative(html_content, "text/html")
                #msg.send()
                print 'XMM: check.checkSave -> send'
        except Exception, e:
            print 'XMM: check.checkSave ->  error mail', str(e)
            pass
        transaction.commit()
        print forReport
        rtr = render_to_response('check/report.html', {'name':name, 'accList': accList,'rejList':rejList, 'modList':modList, 'napList':napList}, RequestContext(request))
        return rtr
    except Exception, e:
        rtr = render_to_response('index.html', {'name':name, 'form': ExisistingProtocolsForm(),'formD':DateForTreatmentsForm()}, RequestContext(request))
        transaction.rollback()
        print 'XMM: check.checkSave -> ', str(e)
        return rtr
    
@laslogin_required
@login_required
@permission_decorator('xenopatients.can_view_XMM_new_measurements')
def graphCSV(request):
    print 'XMM VIEW: start check.graphCSV'
    return CSVMaker(request, 'graph', 'graph.csv', [])
