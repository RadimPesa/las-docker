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
from django.contrib.auth.decorators import user_passes_test
from apisecurity.decorators import *
from django.conf import settings
from lasEmail import *
def getG():
    print 'XMM VIEW: start treatments.getG'
    groups = []
    idList = []
    mha = Mice_has_arms.objects.filter(start_date__isnull = True, end_date__isnull = True)
    for m in mha:
        if m.id_mouse.id_group.id not in idList:
            idList.append(m.id_mouse.id_group.id)
            groups.append({'id': m.id_mouse.id_group.id, 'name':m.id_mouse.id_group.name})
    return groups

def getMha(g):
    print 'XMM VIEW: start treatments.getMha'
    mhaList = []
    group = Groups.objects.get(name = g)
    mice = BioMice.objects.filter(id_group = group)
    for m in mice:
        if len(Mice_has_arms.objects.filter(start_date__isnull = True, end_date__isnull = True, id_mouse = m)) > 0:
            mha = Mice_has_arms.objects.filter(start_date__isnull = True, end_date__isnull = True, id_mouse = m).order_by('-id')[0]
            if getNameT(mha) not in mhaList:
                mhaList.append(getNameT(mha))
    return mhaList

def getMhaDetail(g):
    print 'XMM VIEW: start treatments.getMhaDetail'
    try:
        mhaList = []
        checkList = []
        group = Groups.objects.get(name = g)
        mice = BioMice.objects.filter(id_group = group)
        for m in mice:
            if len(Mice_has_arms.objects.filter(start_date__isnull = True, end_date__isnull = True, id_mouse = m)) > 0:
                mha = Mice_has_arms.objects.filter(start_date__isnull = True, end_date__isnull = True, id_mouse = m).order_by('-id')[0]
                if getNameT(mha) not in checkList:
                    checkList.append(getNameT(mha))
                    mhaList.append({'nameA': mha.id_protocols_has_arms.id_arm.name, 
                                    'nameP': mha.id_protocols_has_arms.id_protocol.name, 
                                    'duration': str(mha.id_protocols_has_arms.id_arm.duration) + ' [' + mha.id_protocols_has_arms.id_arm.type_of_time + ']',
                                    'longName': getNameT(mha) })
        return mhaList
    except Exception, e:
        print 'XMM VIEW treatments.getG: 1) ', str(e)
        pass


def getMice(nameT, g):
    print 'XMM VIEW: start treatments.getMice'
    nameP, nameA = splitNameT(nameT)
    group = Groups.objects.get(name = g)
    mice = BioMice.objects.filter(id_group = group)
    pha = Protocols_has_arms.objects.get(id_protocol = Protocols.objects.get(name = nameP), id_arm = Arms.objects.get(name = nameA))
    miceList = []
    for m in mice:
        mha =  Mice_has_arms.objects.filter(start_date__isnull = True, end_date__isnull = True, id_protocols_has_arms = pha, id_mouse = m)
        if len(mha) > 0:
            try:
                dt = str(mha[0].id_prT.expectedStartDate)
            except Exception:
                dt = str(datetime.datetime.now())
            dateMha = dt.split(' ')[0]
            timeMha = dt.split(' ')[1]
            miceList.append({'genID':m.id_genealogy, 'barcode':m.phys_mouse_id.barcode})
    return miceList, dateMha, timeMha

@laslogin_required
@login_required
@permission_decorator('xenopatients.can_view_XMM_finalize_treatments')
def confirmTreat(request):
    print 'XMM VIEW: start treatments.confirmTreat'
    name = request.user.username
    #ottenere elenco dei gruppi con trattamenti da approvare
    try:
        if "groupSelected" in request.GET:
            #e' stato selezionato il gruppo, fornisco la lista dei trattamenti 
            g = Groups.objects.get(id = request.GET['groupSelected'])
            request.session['g'] = g.name
            mhaList = getMhaDetail(g.name)
            return HttpResponse(json.dumps(mhaList))
        if "armSelected" in request.GET:
            #trattamento selezionato, fornisco la lista dei topi associati a quel trattamento
            g = request.session['g']
            nameT = request.GET['armSelected']
            miceList, dateMha, timeMha = getMice(nameT, g)
            return HttpResponse(json.dumps({'miceList':miceList, 'date':dateMha, 'time':timeMha[:5]}))
    except Exception, e:
        print 'XMM VIEW treatments.confirmTreat: 1) ', str(e)
        pass
    groups = getG()
    if request.method == 'POST':
        if "toSave" in request.POST:
            request.session['post'] = request.POST
            return HttpResponseRedirect(reverse("xenopatients.treatments.saveConfirm"))
        if "abort" in request.POST:
            request.session['post'] = request.POST
            return HttpResponseRedirect(reverse("xenopatients.treatments.abortT"))
    else:
        message = ""
        if len(groups) == 0:
            message = "There aren't treatments ready to start."
        return render_to_response('treatments/confirmTreat.html', {'name':name, 'groups':groups, 'message':message},RequestContext(request))

#restituisce il nome della coppia protocollo braccio partendo dal program treatment
def getNamePT(pt):
    print 'XMM VIEW: start treatments.getNamePT'
    return pt.id_pha.id_protocol.name.lstrip() + ' --- ' + pt.id_pha.id_arm.name.lstrip()

#restituisce il nome della coppia protocollo braccio partendo dal mice has arms
def getNameT(mha):
    print 'XMM VIEW: start treatments.getNameT'
    return mha.id_protocols_has_arms.id_protocol.name.lstrip() + ' --- ' + mha.id_protocols_has_arms.id_arm.name.lstrip()

#prende il nome della coppia protocollo braccio e la splitta, restituendo il nome del protocollo e del braccio
def splitNameT(nameT):
    print 'XMM VIEW: start treatments.splitNameT'
    return nameT.split(' --- ')[0].lstrip(), nameT.split(' --- ')[1].lstrip()

@transaction.commit_manually   
@laslogin_required 
@login_required
@permission_decorator('xenopatients.can_view_XMM_finalize_treatments')
def saveConfirm(request):
    print 'XMM VIEW: start treatments.saveConfirm'
    name = request.user.username
    group = request.session['post']['group']
    nameT = request.session['post']['pha']
    d = request.session['post']['date']
    t = request.session['post']['time']
    message = ""

    try:
        g = Groups.objects.get(name = group)
        nameP, nameA = splitNameT(nameT)
        pha = Protocols_has_arms.objects.get(id_protocol = Protocols.objects.get(name = nameP), id_arm = Arms.objects.get(name = nameA))
        mice = BioMice.objects.filter(id_group = g)
        operators = []
        email = LASEmail (functionality=get_functionality(), wgString=get_WG_string())
        wgMouse=[]
        wgMouse = BioMice_WG.objects.filter(biomice__in=mice).values_list('WG__name', flat=True)
        for m in mice:
            quant = Quantitative_measure.objects.filter(id_mouse = m)
            qual = Qualitative_measure.objects.filter(id_mouse = m)
            string = "" 
            print 'quant',quant
            print 'qual',qual
            print 'm',m
            if len(quant) > 0:
                for q in quant:
                    operator = q.id_series.id_operator
                    email.addRoleEmail(wgMouse, 'Planner', [q.id_series.id_operator.username])
                    if operator.email not in operators:
                        operators.append(operator.email)
            if len(qual) > 0:
                for q in qual:
                    operator = q.id_series.id_operator
                    email.addRoleEmail(wgMouse, 'Planner', [q.id_series.id_operator.username])
                    if operator.email not in operators:
                        operators.append(operator.email)
            if len(Mice_has_arms.objects.filter(start_date__isnull = True, end_date__isnull = True, id_mouse = m, id_protocols_has_arms = pha)) == 1:
                mha = Mice_has_arms.objects.get(start_date__isnull = True, end_date__isnull = True, id_mouse = m, id_protocols_has_arms = pha)
                print 'mha',mha
                dt = d + ' ' + t + ':00'
                struct = time.strptime(dt, "%Y-%m-%d %H:%M:%S") 
                start = datetime.datetime.fromtimestamp(mktime(struct))
                mha.start_date = start
                #calcolare la fine trattamento
                finalStep = mha.id_protocols_has_arms.id_arm.duration
                type_of_time = mha.id_protocols_has_arms.id_arm.type_of_time
                if type_of_time == "minutes":
                    end_date = start + datetime.timedelta(minutes = finalStep)
                if type_of_time == "hours":
                    end_date = start + datetime.timedelta(hours = finalStep)
                if type_of_time == "days":
                    end_date = start + datetime.timedelta(days = finalStep)
                if type_of_time == "months":
                    end_date = start + datetime.timedelta(days = 30*finalStep)
                mha.expected_end_date = end_date
                print mha.start_date
                print mha.expected_end_date
                mha.save()
        groups = getG()
        mhaList = getMha(group)
        message = 'Data correctly saved for the arm "' + nameA + '" of the group "' + group + '".'
        email.addMsg(wgMouse, 'Data correctly saved for the arm "' + nameA + '" of the group "' + group + '".')
        email.addRoleEmail(wgMouse, 'Executor', [request.user.username])
  
        try:
            #text_content = 'Data correctly saved for the arm "' + nameA + '" of the group "' + group + '".'
            #subject, from_email = 'Finalized treatment(s)', settings.EMAIL_HOST_USER
            #msg = EmailMultiAlternatives(subject, text_content, from_email, operators)
            email.send()
            print 'XMM VIEW treatments.saveConfirm: send mail'
        except Exception, e:
            print 'XMM VIEW treatments.saveConfirm: 1) ', str(e)
            transaction.rollback()
            return render_to_response('treatments/confirmTreat.html', {'message':str(e),'name':name, 'selectA':True, 'groups':getG(), 'mhaList':getMha(group),},RequestContext(request))
        transaction.commit()
        return render_to_response('treatments/confirmTreat.html', {'name':name, 'selectA':True, 'groups':groups, 'mhaList':mhaList, 'message':message},RequestContext(request))
    except Exception, e:
        print 'XMM VIEW treatments.saveConfirm: 2) ', str(e)
        transaction.rollback()
        return render_to_response('treatments/confirmTreat.html', {'message':str(e),'name':name, 'selectA':True, 'groups':getG(), 'mhaList':getMha(group),},RequestContext(request))
    finally:
        transaction.rollback()
    
    
    
@transaction.commit_manually  
@laslogin_required  
@login_required
@permission_decorator('xenopatients.can_view_XMM_finalize_treatments')
def abortT(request):
    print 'XMM VIEW: start treatments.abortT'
    try:
        name = request.user.username
        group = request.session['post']['group']
        g = Groups.objects.get(name = group)
        mice = BioMice.objects.filter(id_group = g)
        now = datetime.datetime.now()
        operators = []
        email = LASEmail (functionality=get_functionality(), wgString=get_WG_string())
        wgMouse=[]
        wgMouse = BioMice_WG.objects.filter(biomice__in=mice).values_list('WG__name', flat=True)

        for m in mice:
            mhas = Mice_has_arms.objects.filter(start_date__isnull = True, end_date__isnull = True, id_mouse = m)
            for mha in mhas:
                mha = Mice_has_arms.objects.get(start_date__isnull = True, end_date__isnull = True, id_mouse = m)
                mha.end_date = now
                mha.save()
                quant = Quantitative_measure.objects.filter(id_mouse = m)
                qual = Qualitative_measure.objects.filter(id_mouse = m)
                string = "" 
                if len(quant) > 0:
                    for q in quant:
                        email.addRoleEmail(wgMouse, 'Planner', [q.id_series.id_operator.username])
                        operators.append(q.id_series.id_operator.email)
                if len(qual) > 0:
                    for q in qual:
                        operators.append(q.id_series.id_operator.email)
                        email.addRoleEmail(wgMouse, 'Planner', [q.id_series.id_operator.username])
                if len(Programmed_explant.objects.filter(id_mouse = m, done = 0)) > 0:
                    m.id_status = Status.objects.get(name = 'ready for explant')
                    m.save()
                else:
                    m.id_status = Status.objects.get(name = 'implanted')
                    m.save()
        message = 'All treatments of the group ' + group + ' are now aborted.'
        operators = list(set(operators))
        email.addMsg(wgMouse, 'All not finalized treatments of the group ' + group + ' are now aborted.')
        email.addRoleEmail(wgMouse, 'Executor', [request.user.username])

        try:
            #text_content = 'All not finalized treatments of the group ' + group + ' are now aborted.'
            #subject, from_email = 'Aborted treatment(s)', settings.EMAIL_HOST_USER
            #msg = EmailMultiAlternatives(subject, text_content, from_email, operators)
            email.send()
            print 'XMM VIEW treatments.abortT: send'
        except Exception, e:
            print 'XMM VIEW treatments.abortT: 1) ', str(e)
            pass
        rtr = render_to_response('treatments/confirmTreat.html', {'name':name, 'selectG':True, 'groups':getG(), 'message':message},RequestContext(request))
        transaction.commit()
    except Exception,e:
        print 'XMM VIEW treatments.abortT: 2) ', str(e)
        transaction.rollback()
        return render_to_response('treatments/confirmTreat.html', {'name':name, 'message':e},RequestContext(request))
    return rtr

@laslogin_required
@login_required
@permission_decorator('xenopatients.can_view_XMM_manage_treatments')
def manageTreatments(request):
    print 'XMM VIEW: start treatments.manageTreatments'    
    return render_to_response('treatments/manage.html', {'name':request.user.username, 'form': ExisistingProtocolsForm()}, RequestContext(request)) 

@laslogin_required
@login_required
@permission_decorator('xenopatients.can_view_XMM_manage_treatments')
def newProtocol(request):
    print 'XMM VIEW: start treatments.newProtocol'
    try:
        print request.POST
        name = request.user.username
        if request.method == 'POST':
            #se mi arriva la richiesta di salvare tutto il protocollo appena creato
            if "nameP" in request.POST:
                request.session['nameP'] = request.POST['nameP']
                request.session['descrP'] = request.POST['descrP']
                return HttpResponseRedirect(reverse("xenopatients.treatments.saveProtocol"))
            #se c'e' statusGantt, e' arrivato un arm nuovo da salvare
            if "statusGantt" in request.POST:
                #salvo un nuovo braccio appena creato con i suoi vari step (arm_details)
                gantt = request.POST['statusGantt']
                drugs = request.POST['drugs']
                nameA = request.POST['nameA']
                description = request.POST['description']
                typeTime = request.POST['typeTime']
                forcesExplant = request.POST['forcesExplant']
                duration = request.POST['duration']
                typeA = request.POST['type']
                #request.session['flagArm'] = True
                #togli l'ultimo carattere alle stringa (un separatore superfluo)
                gantt = gantt[0:len(gantt)-1]
                drugs = drugs[0:len(drugs)-1]
                #splitta gantt e drugs -> creo due liste lunghe uguali, uno per drugs e una per gantt
                fe = 0
                if forcesExplant == 'true':
                    fe = 1
                arm = Arms( name=nameA, description=description, duration=duration, type_of_time=typeTime, forces_explant=fe)
                list_drugs = []
                list_gantt = []
                list_newStep = []
                list_newArm = []
                list_indexArm = []
                list_s = [] #per creare una serie di liste dentro list_newStep
                if request.session.get('list_newArm'):
                   list_newArm = request.session.get('list_newArm')
                if request.session.get('list_newStep'):
                   list_newStep = request.session.get('list_newStep')
                if request.session.get('list_indexArm'):
                   list_indexArm = request.session.get('list_indexArm')
                list_newArm.append(arm)
                list_indexArm.append(typeA)
                #parsing stringhe e conversione in liste
                tuplas = string.split(drugs, '#')
                for tupla in tuplas:
                    list_drugs.append(drugInfo(tupla))
                tuplas = string.split(gantt, '#')
                for tupla in tuplas:
                    list_gantt.append(tupla)
                #scorri le due liste in parallelo
                #analizza la stringa di 0 e 1
                list_steps = []
                for k in list_gantt:
                    list_steps.append(adjacencies(k))
                i = 0
                for ll in list_steps:
                    for l in ll:
                        s = step(list_drugs[i].via, list_drugs[i].drug, start_step = l[0], end_step = l[1]+1, dose = list_drugs[i].dose, schedule = list_drugs[i].schedule )
                        print i
                        list_s.append(s)
                    i = i + 1
                list_newStep.append(list_s)
                request.session['list_newStep'] =  list_newStep
                request.session['list_indexArm'] =  list_indexArm
                request.session['list_newArm'] =  list_newArm
                #sessione da pulire quando si salva tutto il protocollo
                return HttpResponse()
            #si fa riferimento a un arm gia' esistente, devo solo salvarmi un riferimento per poi salvarlo nel protocollo
            else:
                if "type" in request.POST:
                    typeA = request.POST['type']
                    if typeA == '1':
                        #prelevo i dati dalla POST
                        nameA = request.POST['nameA']
                        print 'select old arm'
                        list_oldArm = []
                        list_indexArm = []
                        if request.session.has_key('list_oldArm'):
                            list_oldArm = list(request.session.get('list_oldArm'))
                        if request.session.has_key('list_indexArm'):
                            list_indexArm = list(request.session.get('list_indexArm'))
                        list_oldArm.append(Arms.objects.get(name = nameA))
                        list_indexArm.append(typeA)
                        print 'listoldarm',list_oldArm
                        request.session['list_indexArm'] =  list_indexArm
                        request.session['list_oldArm'] =  list_oldArm
                    return HttpResponse()
        armHtml = listArmHtml()
        #pulisco la sessione
        if request.session.get('list_newArm'):
            del request.session['list_newArm']
        if request.session.get('list_newStep'):
            del request.session['list_newStep']
        if request.session.get('list_indexArm'):
            del request.session['list_indexArm']
        if request.session.get('list_oldArm'):
            del request.session['list_oldArm']
        if request.session.get('nameP'):
            del request.session['nameP']
        if request.session.get('descrP'):
            del request.session['descrP']
        return render_to_response('treatments/newProt.html', {'name':name, 'formO':DetailsTreatmentForm(), 'formT': CreateTreatmentForm(), 'armHtml':armHtml}, RequestContext(request))
    except Exception,e:
        print 'err',e
        pass

#salvo il protocollo appena creato
@laslogin_required
@login_required
@permission_decorator('xenopatients.can_view_XMM_manage_treatments')
@transaction.commit_manually
def saveProtocol(request):
    print 'XMM VIEW: start treatments.saveProtocol'
    name = request.user.username
    #prendere i dati dalla sessione (liste e variabili varie)
    list_newArm = []
    list_newStep = []
    list_indexArm = []
    list_oldArm = []
    nameP = ""
    descrp = ""
    if request.session.get('list_newArm'):
       list_newArm = request.session.get('list_newArm')
    if request.session.get('list_newStep'):
       list_newStep = request.session.get('list_newStep')
    if request.session.get('list_indexArm'):
       list_indexArm = request.session.get('list_indexArm')
    if request.session.get('list_oldArm'):
        list_oldArm = request.session.get('list_oldArm')
    if request.session.get('nameP'):
        nameP = request.session.get('nameP')
    if request.session.get('descrP'):
        descrP = request.session.get('descrP')
    print 'listnewarm',list_newArm
    print 'listnewstep',list_newStep
    print 'listindexarm',list_indexArm
    print 'listoldarm',list_oldArm
    #ciclare sulle liste e salvare
    try:
        #salvo protocollo
        p = Protocols(name = nameP, description = descrP)
        p.save()
        last_protocol = p
        print 'protocol saved ', last_protocol, p.id
        indexNew = 0
        indexOld = 0
        for index in list_indexArm:
            #arm nuovo
            if index == '0':
                list_newArm[indexNew].save()
                #lastArm = Arms.objects.all().aggregate(Max('id'))
                last_arm = list_newArm[indexNew]#Arms.objects.get(id = lastArm["id__max"])
                print 'arm ', last_arm
                for step in list_newStep[indexNew]:
                    da = Details_arms(id_via = step.via, arms_id = last_arm, drugs_id = step.drug, start_step = step.start_step, end_step = step.end_step, dose = step.dose, schedule = step.schedule)
                    da.save()
                indexNew = indexNew + 1
                print 'protocol ', last_protocol, last_protocol.id
                pha = Protocols_has_arms(id_arm = last_arm, id_protocol = last_protocol)
                pha.save()
                print 'protocol has arm ', pha
            #arm gia' esistente
            else:
                pha = Protocols_has_arms(id_arm = list_oldArm[indexOld], id_protocol = last_protocol)
                pha.save()
                indexOld = indexOld + 1
        transaction.commit()
    except Exception, e:
        transaction.rollback()
        print 'XMM VIEW treatments.saveProtocol: 1) ', str(e)
        if request.session.get('list_newArm'):
            del request.session['list_newArm']
        if request.session.get('list_newStep'):
            del request.session['list_newStep']
        if request.session.get('list_indexArm'):
            del request.session['list_indexArm']
        if request.session.get('list_oldArm'):
            del request.session['list_oldArm']
        if request.session.get('nameP'):
            del request.session['nameP']
        if request.session.get('descrP'):
            del request.session['descrP']
        return render_to_response('treatments/manage.html', {'name':name, 'messaggio':'Error: protocol not saved','fine':True}, RequestContext(request))
    #pulisco la sessione
    if request.session.get('list_newArm'):
        del request.session['list_newArm']
    if request.session.get('list_newStep'):
        del request.session['list_newStep']
    if request.session.get('list_indexArm'):
        del request.session['list_indexArm']
    if request.session.get('list_oldArm'):
        del request.session['list_oldArm']
    if request.session.get('nameP'):
        del request.session['nameP']
    if request.session.get('descrP'):
        del request.session['descrP']
    return render_to_response('treatments/manage.html', {'name':name, 'messaggio':'Protocol correctly created','fine':True}, RequestContext(request))

#salva la creazione di un nuovo trattamento 
@laslogin_required
@login_required
@permission_decorator('xenopatients.can_view_XMM_manage_treatments')
@transaction.commit_manually
def saveTreatment(request):
    print 'XMM VIEW: start treatments.saveTreatment'
    name = request.user.username
    if request.session.get('gantt'):
        gantt = request.session.get('gantt')
    if request.session.get('drugs'):
        drugs = request.session.get('drugs')
    if request.session.get('nameT'):
        nameT = request.session.get('nameT')
    if request.session.get('description'):
        description = request.session.get('description')
    if request.session.get('duration'):
        duration = request.session.get('duration')
    if request.session.get('typeTime'):
        typeTime = request.session.get('typeTime')
    if request.session.get('forcesExplant'):
        forcesExplant = request.session.get('forcesExplant')
    #togli l'ultimo carattere alle stringa (un separatore superfluo)
    gantt = gantt[0:len(gantt)-1]
    drugs = drugs[0:len(drugs)-1]
    print 'drugs:',drugs
    #splitta gantt e drugs -> creo due liste lunghe uguali, uno per drugs e una per gantt
    try:
        fe = 0
        if forcesExplant == 'true':
            fe = 1
        t = Arms( name=nameT, description=description, duration=duration, type_of_time=typeTime, forces_explant=fe)
        t.save()
        id_treat = t
        list_drugs = []
        list_gantt = []
        tuplas = string.split(drugs, '#')
        for tupla in tuplas:
            list_drugs.append(drugInfo(tupla))
        tuplas = string.split(gantt, '#')
        for tupla in tuplas:
            list_gantt.append(tupla)
        #scorri le due liste in parallelo
        #analizza la stringa di 0 e 1
        list_steps = []
        for k in list_gantt:
            list_steps.append(adjacencies(k))
        i = 0
        for ll in list_steps:
            for l in ll:
                #treat_index = Arms.objects.all().aggregate(Max('id'))
                #id_treat = Arms.objects.get(id = treat_index["id__max"]) #cerco l'id dell'ultimo treatment creato per poi collegargli i vari step di detail_treatments
                dt = Details_arms(id_via = Via_mode.objects.get(description = list_drugs[i].via),arms_id = id_treat, drugs_id = Drugs.objects.get(name = list_drugs[i].drug), start_step = l[0], end_step = l[1]+1, dose = list_drugs[i].dose, schedule = list_drugs[i].schedule )
                dt.save()
            i = i + 1
        transaction.commit()
    except:    
        transaction.rollback()
        return render_to_response('treatments/continue.html', {'name':name, 'err_message':"An error occurred while creating the treatment."}, RequestContext(request))
    return render_to_response('treatments/continue.html', {'name':name, 'message':"Treatment correctly created."}, RequestContext(request))
