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
from xenopatients.moreUtils import *
from django.core.mail import send_mail, EmailMultiAlternatives
import os, cStringIO, csv, time, urllib, urllib2, datetime
from LASAuth.decorators import laslogin_required
from xenopatients.treatments import splitNameT, getNameT, getNamePT
from django.contrib.auth.decorators import user_passes_test
from itertools import chain
from apisecurity.decorators import *
from django.conf import settings
from lasEmail import *
#controller per la schermata archive. Messa qui perche' fare un file solo per questa era uno spreco.
@laslogin_required
@login_required
@permission_decorator('xenopatients.can_view_XMM_archive')
def archive(request):
    print 'XMM VIEW: start ongoing.archive'
    return render_to_response('check/archive.html', {'name':request.user.username, 'groups':nonActiveGroups() }, RequestContext(request))

@laslogin_required
@login_required
@permission_decorator('xenopatients.can_view_XMM_ongoing')
def ongoing(request):
    print 'XMM VIEW: start ongoing.ongoing'
    if request.method == 'POST':
        if "actions" in request.POST:
            request.session['actions'] = request.POST['actions']
            return HttpResponseRedirect(reverse("xenopatients.ongoing.ongoingSave"))
    return render_to_response('check/ongoing.html', {'name':request.user.username, 'form':GroupForm(), 'groups':activeGroups(), 'formSD':ScopeForm() }, RequestContext(request))
    
@laslogin_required
@login_required
@permission_decorator('xenopatients.can_view_XMM_ongoing')
def treatment(request):
    print 'XMM VIEW: start ongoing.treatment'
    return render_to_response('check/ongoingT.html', {'name':request.user.username, 'form': ExisistingProtocolsForm(),'date':str(datetime.date.today()+ datetime.timedelta(days=1))}, RequestContext(request))

@transaction.commit_manually 
@laslogin_required
@login_required
@permission_decorator('xenopatients.can_view_XMM_ongoing')
def ongoingSave(request):
    print 'XMM VIEW: start ongoing.ongoingSave'
    name = request.user.username
    user = User.objects.get(username = name)
    filter_list, operators, mails, list_report = [], [], [], []
    email = LASEmail (functionality=get_functionality(), wgString=get_WG_string())
    wgMouse=[]
    try:
        actions =  json.loads(request.session['actions'])
        print 'actions',actions
        group=''
        wgSet=set()
        for genID in actions:
            textMail=''
            mouse = BioMice.objects.get(id_genealogy = genID)
            wgMouse = BioMice_WG.objects.filter(biomice=mouse).values_list('WG__name', flat=True)
            wgSet.update(wgMouse)
            group = mouse.id_group.name
            explant = actions[genID]['explant']['type']
            scope = actions[genID]['explant']['scope']
            explNotes = actions[genID]['explant']['notes']
            actionTreatment = actions[genID]['treatment']['action']
            treatment = actions[genID]['treatment']['name']
            startP = actions[genID]['treatment']['dateP']
            comment = actions[genID]['comment']
            #per topo, creare un evento programmato gia' approvato in automatico
            newEvent = ProgrammedEvent(insertionDate = datetime.date.today(), 
                                       id_mouse = mouse,
                                       measureOperator = User.objects.get(username = name),
                                       id_status = EventStatus.objects.get(name = 'accepted'),
                                       checkDate = datetime.date.today(),
                                       checkComments = actions[genID]['comment'],
                                       checkOperator = User.objects.get(username = name))
            newEvent.save()
            print 'event',newEvent
            id_event = newEvent
            if explant == 'sacr':
                prS = Pr_changeStatus(id_event = id_event, newStatus = Status.objects.get(name = 'toSacrifice'))
                prS.save()
                textMail += '\n' + 'Mouse ' + genID + ' of group ' + group +' is now to sacrifice'
            elif explant == 'expl':
                prE = Pr_explant(id_event = id_event, id_scope = Scope_details.objects.get(description = scope), scopeNotes = explNotes)
                prE.save()
                textMail += '\n' + 'Mouse ' + genID + ' of group ' + group +' is now ready for explant. Scope: '+ scope +' . Notes (optional): ' + explNotes
            elif explant == 'explLite':
                prS = Pr_changeStatus(id_event = id_event, newStatus = Status.objects.get(name = 'explantLite'))
                prS.save()
                textMail += '\n' + 'Mouse ' + genID + ' of group ' + group +' is now ready for an explant without sacrifice.'
            if actionTreatment == 'start':
                mhas = Mice_has_arms.objects.filter(id_mouse = mouse, end_date__isnull = True)
                for mha in mhas:
                    mha.end_date = datetime.datetime.now()
                    mha.save()
                    textMail += '\n' + 'Stopped treatment for mouse ' + genID + ' of group ' + group +': ' + getNameT(mha)
                nameP, nameA = splitNameT(treatment)
                prT = Pr_treatment(id_event = id_event, 
                                   id_pha = Protocols_has_arms.objects.get(id_arm = Arms.objects.get(name = nameA), id_protocol = Protocols.objects.get(name = nameP)), 
                                   expectedStartDate = startP)
                prT.save()
                #dopo tramite un trigger viene salvato anche il mice has arms collegato
                textMail += '\n' + 'New treatment programmed for mouse ' + genID + ' of group ' + group +': ' + treatment + '. Proposed start: ' + startP
            elif actionTreatment == 'stop':
                try:
                    mhas = Mice_has_arms.objects.filter(id_mouse = mouse, end_date__isnull = True)
                    for mha in mhas:
                        mha.end_date = datetime.datetime.now()
                        mha.save()
                        textMail += '\n' + 'Stopped treatment for mouse ' + genID + ' of group ' + group +': ' + getNameT(mha)
                except:
                    pass
            if explant == 'sacr':
                explant = 'to sacrifice'
            elif explant == 'expl':
                explant = 'ready for explant'
            elif explant == 'explLite':
                explant = 'explant without sacrifice'
            if actionTreatment == 'stop':
                treatment = 'Stopped: ' + actions[genID]['treatment']['name']
            list_report.append(tableReport([genID, group, explant, scope, explNotes, treatment, startP, comment]))
      
            email.addMsg(wgMouse, [textMail])
            #mandare la mail a tutti quelli che hanno misurato i topi piu' supervisore/i
            operator_quant = Measurements_series.objects.filter(id_series__in = Quantitative_measure.objects.filter(id_mouse = mouse).values_list('id_series', flat=True) ).values_list('id_operator__username', flat=True) 
            operator_qual =  Measurements_series.objects.filter(id_series__in = Qualitative_measure.objects.filter(id_mouse = mouse).values_list('id_series', flat=True) ).values_list('id_operator__username', flat=True) 
            email.addRoleEmail(wgMouse,'Planner',operator_quant)
            email.addRoleEmail(wgMouse,'Planner',operator_qual)
            email.addRoleEmail(wgMouse,'Executor',[request.user.username])
        for wgName in wgSet:
            email.appendSubject([wgName],group)
        try:
            email.send()
            print 'XMM VIEW ongoing.ongoingSave: send'
        except Exception, e:
            print 'XMM VIEW ongoing.ongoingSave: 1) ', str(e)
            pass

        transaction.commit()
        return render_to_response('check/ongoingReport.html', {'name':name, 'list_report': list_report, 'message':'Data correctly saved'}, RequestContext(request))
    except Exception, e:
        transaction.rollback()
        print 'XMM VIEW ongoing.ongoingSave: 2) ', str(e)
        return render_to_response('index.html', {'name':name}, RequestContext(request))

@laslogin_required
@login_required
@permission_decorator('xenopatients.can_view_XMM_ongoing')
def graphCSV(request):
    print 'XMM VIEW: start ongoing.graphCSV'
    return CSVMaker(request, 'graph', 'graph.csv', [])
