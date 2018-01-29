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
from xenopatients import markup
from xenopatients.forms import *
from xenopatients.models import *
from xenopatients.utils import *
from xenopatients.views import *
from xenopatients.externalAPIhandler import *
from LASAuth.decorators import laslogin_required
from django.core.mail import send_mail, EmailMultiAlternatives
from django.contrib.auth.decorators import user_passes_test
import os, cStringIO, csv, time, urllib, urllib2
from apisecurity.decorators import *
from global_request_middleware import *
import django.utils.html as duh

#per avere la struttura vuota di una piastra prima del load, tipo espianti
class ImplantEmptyPlate():
    def plate(self):
        page = markup.page()
        page.table(id='vital',align='center')
        page.tr()
        page.td()
        page.td.close()
        for i in range(1,7):
            page.td(align='center')
            page.strong(i)
            page.td.close()
        page.tr.close()
        for i in range (1,5):
            page.tr()
            page.td()
            page.br()
            page.strong(str(i).translate(trasftab)) #trasftab nelle utils
            page.td.close()
            for j in range(1,7):
                page.td(style="background-color: grey;width:36px;height:36px;")
                page.td.close()
            page.tr.close()
        page.table.close()
        return page

#funzione che fornisce la schermata degli impianti e salva i dati quando sottomessi
@laslogin_required
@login_required
@permission_decorator('xenopatients.can_view_XMM_implant_xenografts')
def startImplant(request):
    print 'XMM VIEW: start implant.startImplant'
    return render_to_response('implants/start.html', {'name':request.user.username, 'formS':StartImplantForm(), 'formI':ImplantForm(), 'skeletonPlate':ImplantEmptyPlate()}, RequestContext(request))

@laslogin_required
@login_required
@permission_decorator('xenopatients.can_view_XMM_implant_xenografts')
def implantGroups(request):
    print 'XMM VIEW: start implant.implantGroups'
    name = request.user.username
    try:
        if 'implants' in request.POST:
            implants = request.POST['implants']
            implData = json.loads(request.POST['implData'])
            request.session['implants'] = implants
            request.session['implData'] = request.POST['implData']
            string = getHTML(implants, duh.escape(implData['prot']), 12, duh.escape(implData['date'])) #'12' e' il valore di default; indica che si considerano i primi 12 caratteri dei genID per i gruppi da proporre all'utente
            request.session['code'] = string
            return HttpResponseRedirect(reverse("xenopatients.implants.redirectG"))
    except Exception, e:
        print 'XMM VIEW implant.implantGroups: 1)' + str(e)
        return  HttpResponse(str(e))

@laslogin_required
@login_required
@permission_decorator('xenopatients.can_view_XMM_implant_xenografts')
def redirectG(request):
    print 'XMM VIEW: start implant.redirectG'
    name = request.user.username
    string = request.session['code']
    protocol = duh.escape(json.loads(request.session['implData'])['prot'])
    date = duh.escape(json.loads(request.session['implData'])['date'])
    notes = duh.escape(json.loads(request.session['implData'])['notes'])
    implants = request.session['implants']
    try:
        return render_to_response('implants/groups.html', {'name':name, 'table':string, 'implants':implants, 'protocol':protocol,'notes':notes, 'date':date},RequestContext(request))
    except Exception,e:
        print 'XMM VIEW implant.redirectG: 1)' + str(e)
        return render_to_response('implants/start.html', {'name':name, 'formS':StartImplantForm(), 'formI':ImplantForm(), 'skeletonPlate':ImplantEmptyPlate()}, RequestContext(request))

@laslogin_required
@login_required
@permission_decorator('xenopatients.can_view_XMM_implant_xenografts')
def loadG(request):
    print 'XMM VIEW: start implant.loadG'
    return render_to_response('implants/loadG.html', {'name':request.user.username, 'groups':activeGroups(), }, RequestContext(request))

@laslogin_required
@login_required
@permission_decorator('xenopatients.can_view_XMM_implant_xenografts')
def rImplants(request):
    print 'XMM VIEW: start implant.rImplants'
    request.session['implants'] =  request.POST['implants']
    request.session['date'] = request.POST['date']
    request.session['protocol'] = request.POST['protocol']
    request.session['notes'] = request.POST['notes']
    request.session['dataTable'] = request.POST['dataTable'] #non c'entra niente con il plugin di jQuery dataTable
    return HttpResponseRedirect(reverse("xenopatients.implants.reportImplant"))

#funzione per salvare i dati e visualizzare il report degli impianti appena fatti
@transaction.commit_manually
@laslogin_required
@login_required
@permission_decorator('xenopatients.can_view_XMM_implant_xenografts')
def reportImplant(request):
    print 'XMM VIEW: start implant.reportImplant'
    name = request.user.username
    try:
        implants =  json.loads(request.session['implants'])
        print 'implants',implants
        #parameters = createList(listImpl) #anche, creo una lista di parametri
        list_report=[]
        err_message = ""
        address = ""
        addressB = ""
        address = UrlStorage.objects.get(default = '1').address
        addressB = Urls.objects.get(default = '1').url
        transaction.commit()
    except Exception, e:
        transaction.rollback()
        print 'XMM VIEW implant.reportImplant: 1)' + str(e)
    try:
        date = duh.escape(request.session['date'])
        scope = duh.escape(request.session['protocol'])
        notes = duh.escape(request.session['notes'])
        dataTable = request.session['dataTable']
        print 'table',dataTable
        s = Series( id_operator = User.objects.get(username = name), id_type = Type_of_serie.objects.get(description = 'implant'), date = date, notes = notes)
        if scope != "":
            s.id_protocol = Protocols.objects.get(pk = scope)
        s.save()
        id_series = s 
        barcodeString = ""
        listB, listGen, listOldG, listFlag, listSite = [], [], [], [], []
        for barcodeP in implants:
            for key in implants[barcodeP]:
                if key != 'emptyFlag':
                    oldG = implants[barcodeP][key]['aliquot']
                    for mouse in implants[barcodeP][key]['listMice']:
                        barcode = mouse['barcode']
                        newG = mouse['newGenID']
                        badFlag = mouse['badflag']
                        site = mouse['site']
                        try:
                            a = Aliquots(id_genealogy = oldG)
                            a.save()
                        except:
                            pass
                        #setto il bad_flag_quality a 0 o a 1
                        bad = 0
                        if badFlag == 'true':
                            bad = 1
                        m = Mice.objects.get(barcode = barcode)
                        m.id_status = Status.objects.get(name='implanted')
                        m.save()
                        bm = BioMice(phys_mouse_id = m, id_genealogy = newG)
                        bm.save()
                        #creo l'oggetto implant_details
                        i_d = Implant_details(id_mouse = bm, id_series = id_series, aliquots_id = Aliquots.objects.get(id_genealogy = oldG), bad_quality_flag = bad, site = Site.objects.get(longName = site))
                        i_d.save()
                        #cambio lo status al topo 
                        listB.append(barcode)
                        listGen.append(newG)
                        listOldG.append(oldG)
                        listFlag.append(bad)
                        listSite.append(site)
                        #appendo i dati alla lista per il report
        #BRC0122NLX0J.2012-12-20.0|BRC0122NLX0J02002000000000&OVR0005THX0E.2012-12-20.0|OVR0005THX0E02006000000000
        for dt in dataTable.split('&'):
            first = True
            if len(dt.split('|')) > 1:
                #entro qui se e' stato associato almeno un topo a questo gruppo
                for d in dt.split('|'):
                    if first:
                        first = False
                        try:
                            #se non riesce a salvare, vuol dire che il gruppo esiste gia'
                            if scope != "":
                                g = Groups(name = d, creationDate = date, id_protocol = Protocols.objects.get(id = scope))
                            else:
                                g = Groups(name = d, creationDate = date)
                            g.save()
                        except Exception, e:
                            print 'XMM VIEW implant.reportImplant: 2)' + str(e)
                            g = Groups.objects.get(name = d)
                            pass
                    else:
                        index = listGen.index(str(d))
                        barcode = listB[index]
                        newG = listGen[index]
                        oldG = listOldG[index]
                        badFlag = str(listFlag[index])
                        site = listSite[index]
                        if settings.USE_GRAPH_DB==True and 'admin' not in get_WG():
                            disable_graph()
                            bm = BioMice.objects.get(id_genealogy = newG)
                            enable_graph()
                        else:
                            bm = BioMice.objects.get(id_genealogy = newG)
                        bm.id_group = g
                        bm.save()
                        list_report.append(tableReport([barcode, oldG, newG, g.name, site, badFlag]))
        try:
            #mandare alla biobanca i barcode delle provette utilizzate
            url = addressB + "/api/aliquot/canc/"
            values = {'implants' : json.dumps(implants)}
            data = urllib.urlencode(values)
            req = urllib2.Request(url, data=data, headers={"workingGroups" : get_WG_string()})
            u = urllib2.urlopen(req)
            #u = urllib2.urlopen(url, data)
        except Exception, e:
            print 'XMM VIEW implant.reportImplant: 3)' + str(e)
        transaction.commit()
    except Exception, e:
        print 'XMM VIEW implant.reportImplant: 4)' + str(e)
        transaction.rollback()
        return render_to_response('implants/continue.html', {'name':name, 'err_message': "Something gone wrong." })
    request.session['list_report']=list_report
    print "XMM: end implant session"
    return render_to_response('implants/implantsReport.html', {'list_report':list_report, 'message':'Implants correctly saved','name':name, 'formS':StartImplantForm()}, RequestContext(request))

#ridirezione dopo il tasto 'continue' nella pagina del report
@laslogin_required
@login_required
@permission_decorator('xenopatients.can_view_XMM_implant_xenografts')
def continueImplant(request):
    print 'XMM VIEW: start implant.continueImplant'
    return HttpResponseRedirect(reverse("xenopatients.views.index"))
