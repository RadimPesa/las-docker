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
from api.utils import *
from apisecurity.decorators import *

@laslogin_required
@login_required
@permission_decorator('xenopatients.can_view_XMM_manage_groups')
def manageG(request):
    print 'XMM VIEW: start groups.manageG'
    if request.method == 'POST':
        request.session['postGroup'] = request.POST
        try:
            return HttpResponseRedirect(reverse("xenopatients.groups.saveChange"))
        except Exception, e:
            print 'XMM VIEW groups.manageG: 1) ', str(e)
    return render_to_response('groups/manage.html', {'name':request.user.username,  'formDetails': DetailsGroupForm() }, RequestContext(request))
    #'groups':nonActiveGroups(),
    
@laslogin_required
@login_required
@permission_decorator('xenopatients.can_view_XMM_manage_groups')
def loadG(request):
    print 'XMM VIEW: start groups.loadG'
    return render_to_response('groups/loadG.html', {'name':request.user.username, 'form':GroupForm(), 'groups':activeGroups(), }, RequestContext(request))
    
def parseProperties(properties, groupName,listReportGroups, nMice):
    print 'XMM VIEW: start groups.parseProperties'
    typeG = ""
    if properties['type'] == 'new':
        typeG = 'New Group'
        if properties['protocol'] != '---------':
            g = Groups( name = properties['name'], creationDate = date.today(), id_protocol = Protocols.objects.get(name = properties['protocol']) )
        else:
            g = Groups( name = properties['name'], creationDate = date.today() )
        g.save()
    elif properties['type'] == 'mod':
        typeG = 'Modified Group' 
        g = Groups.objects.get(name = groupName)
        g.name = properties['name']
        if properties['protocol'] != '---------':
            g.id_protocol = Protocols.objects.get(name = properties['protocol'])
        g.save()
    elif properties['type'] == 'loaded':
        typeG = 'Modified Group'
        g = Groups.objects.get(name = groupName)
    if g.id_protocol is None:
        nameP = '-'
    else:
        nameP = g.id_protocol.name
    if nMice == 0:
        typeG = 'Deleted Group'
    listReportGroups.append(tableReport([g.name, str(g.creationDate), nameP, typeG]))
    return g
    
def parseNewMice(mice, g, listReportMice):
    print 'XMM VIEW: start groups.parseNewMice'
    print 'gfgf'
    print mice
    for genID in mice:
        print '1'
        if mice[genID]['new'] == True:
            print '.'+genID+'.'
            m = BioMice.objects.get(id_genealogy = genID)
            print m
            m.id_group = g
            print '2'
            if m.phys_mouse_id.id_status == Status.objects.get(name = 'waste'):
                m.phys_mouse_id.id_status = Status.objects.get(name = 'implanted')
            print '4'
            m.save()
            print '5'
            mha = Mice_has_arms.objects.filter(id_mouse = m, start_date__isnull = False, end_date__isnull= True)
            nameT, start, duration, endD, notes = getCurrentTreat(m,mha)
            print '6'
            listReportMice.append(tableReport([genID, g.name, m.phys_mouse_id.id_status.name, nameT, start, duration]))

@transaction.commit_manually
@laslogin_required
@login_required
@permission_decorator('xenopatients.can_view_XMM_manage_groups')
def saveChange(request):
    print 'XMM VIEW: start groups.saveChange'
    name = request.user.username
    listReportGroups,listReportMice = [], []
    toDelete = []
    try:
        actions = json.loads(request.session['postGroup']['actions'])
        del request.session['postGroup']
        for groupName in actions:
            mice = actions[groupName]['mice']
            properties = actions[groupName]['properties']
            #gestione edit properties e/o creazione new groups
            g = parseProperties(properties, groupName, listReportGroups, len( actions[groupName]['mice'] ))
            #gestione trasferimenti topi
            print len(mice)
            if len(mice) > 0:
                parseNewMice(mice, g, listReportMice)
            #cancellare gruppi svuotati e rimasti senza topi
            if len( actions[groupName]['mice'] ) == 0:
                toDelete.append(groupName)
                
        for groupName in toDelete:
            gr = Groups.objects.get(name = groupName)
            gr.delete()
        rtr = render_to_response('groups/reportChange.html', {'name':name, 'listReportGroups':listReportGroups, 'listReportMice':listReportMice }, RequestContext(request))
        transaction.commit()
        return rtr
    except Exception, e:
        print 'XMM VIEW groups.saveChange: 1) ' + str(e)
        transaction.rollback()
        return HttpResponseRedirect(reverse("xenopatients.views.index"))
