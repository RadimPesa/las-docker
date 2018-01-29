from pprint import pprint
from string import maketrans
from xenopatients import markup
from xenopatients.genealogyID import *
from django.db import transaction
import os, urllib, urllib2, cStringIO, string, json
from xenopatients.forms import *
from xenopatients.models import *
from xenopatients.utils import *
from xenopatients.views import *
from datetime import date, datetime
from django.http import HttpResponse, HttpResponseRedirect
import os, cStringIO, csv


#per creare il PDF
def updateExplantedStatus(list_report2, m, typeE, series, now, parsedMice):
    print 'XMM VIEW: start moreUtils.updateExplantedStatus'
    if typeE == 'N':
        m.id_status = Status.objects.get(name = 'explanted')
        m.death_date = series.date
        m.save()
        #segno come 'fatti' i vari programmed_explant
        parsedMice.append(m.barcode)
        for biomouse in BioMice.objects.filter(phys_mouse_id = m):
            stopTreat(biomouse, now)
            try:
                pe = Programmed_explant.objects.filter(id_mouse = biomouse, done = '0')
                for p in pe:
                    p.done = '1'
                    p.save()
                list_report2.append(tableReport([biomouse.id_genealogy, m.arrival_date, pe[0].id_scope.description, pe[0].scopeNotes, series.notes]))
            except Exception, e:
                print 'XMM VIEW moreUtils.updateExplantedStatus: 1) ', str(e)
                list_report2.append(tableReport([biomouse.id_genealogy,  m.arrival_date,'', '', series.notes]))
                pass
    if typeE == 'L':
        m.id_status = Status.objects.get(name = 'implanted') #riporto lo status a impl dopo l'espianto leggero
        m.save()
        for biomouse in BioMice.objects.filter(phys_mouse_id = m):
            list_report2.append(tableReport([biomouse.id_genealogy, m.arrival_date, "explant without sacrifice", "", series.notes]))
    return list_report2, parsedMice
    
#restituisce la lista dei nomi dei gruppi attivi (con almeno un topo vivo)
def activeGroups():
    print 'XMM VIEW: start moreUtils.activeGroups'
    '''
    filter_list = [Status.objects.get(name = 'implanted'), 
                    Status.objects.get(name = 'ready for explant'), 
                    Status.objects.get(name = 'explantLite'), 
                    Status.objects.get(name = 'toSacrifice'), 
                    Status.objects.get(name = 'waste')]
    '''
    filter_list = Status.objects.filter( name__in = ['implanted', 'ready for explant', 'explantLite', 'toSacrifice', 'waste'])
    groups = []
    groups = BioMice.objects.filter(phys_mouse_id__in = Mice.objects.filter(id_status__in = filter_list).values_list('id', flat=True)).values_list('id_group__name', flat=True)
    return list(set(groups))

def nonActiveGroups():
    print 'XMM VIEW: start moreUtils.nonActiveGroups'
    allGroups = BioMice.objects.all().values_list('id_group__name', flat=True)
    return list(set(allGroups) - set(activeGroups()))
