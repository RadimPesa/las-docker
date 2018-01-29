#from datetime import date, timedelta, datetime
from django import forms
from django.db import transaction
from django.db.models import Q, Max
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import auth
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
from LASAuth.decorators import laslogin_required
from django.core.mail import send_mail, EmailMultiAlternatives
from django.contrib.auth.decorators import user_passes_test
import os, cStringIO, csv, time, urllib, urllib2, datetime, ast
from django.conf import settings
from apisecurity.decorators import *
from lasEmail import *


#funzione per caricare i topi tramite la funzione Mice Loading
@laslogin_required
@login_required
@permission_decorator('xenopatients.can_view_XMM_register_mice')
def miceLoading (request):
    print 'XMM VIEW: start miceManage.miceLoading'
    phase, age, group, source, strain = "", "", "", "", ""
    first, second_step = True, False
    name = request.user.username #recupero il nome di chi e' loggato in questo momento
    if request.method == 'POST': # If the form has been submitted..
        #salvo i dati generali di tutti gli N inserimenti nella sessione, prendendoli dalla post
        if "age_in_weeks" in request.POST:
            request.session['age_in_weeks'] = request.POST['age_in_weeks']
        if "mouse_strain" in request.POST:
            request.session['mouse_strain'] = request.POST['mouse_strain']
        if "source" in request.POST:
            request.session['source'] = request.POST['source']
        if "status" in request.POST:
            request.session['status'] = request.POST['status']
        if "arrival_date" in request.POST:
            request.session['arrival_date'] = request.POST['arrival_date']
        if "newMice" in request.POST:
            #entra qui se e' stato ricevuta la stringa da ajax contenente i dati della tabella dei topi da inserire nel DB
            request.session['newMice'] = request.POST['newMice']
            return HttpResponseRedirect(reverse("xenopatients.miceManage.finishListing"))
        if "start" in request.POST:
            #se c'e' 'start' nella post, vuol dire che ho appena cliccato dopo aver inserito i primi dati della serie di inserimento e devo portare l'utente alla pagina successiva
            form = FirstStartMiceForm(name, request.POST) # A form bound to the POST data
            if form.is_valid(): # All validation rules pass
                dict_value = {'Strain': form.cleaned_data['mouse_strain'], 'Source': form.cleaned_data['source'], 'Age': request.POST['age_in_weeks'], 'Status': form.cleaned_data['status'], 'Arrival date':request.POST['arrival_date']}
                return render_to_response('mice/mice_loading.html', {'second_step':True,'name':name, 'dict_value': dict_value, 'form': WritingMiceForm()}, RequestContext(request))
        elif "finish" in request.POST:
            #se entro qui, vuol dire che ho finito l'inserimento dei dati e che voglio salvare i dati
            form = WritingMiceForm(request.POST) # A form bound to the POST data
    else:
        form = FirstStartMiceForm(name) # An unbound form
    return render_to_response('mice/mice_loading.html', {'name':name, 'form': form}, RequestContext(request))

@transaction.commit_manually #disabilitato commit automatico
@permission_decorator('xenopatients.can_view_XMM_register_mice')
def finishListing (request):
    print 'XMM VIEW: start miceManage.finishListing'
    name = request.user.username
    #prelevo i dati necessari per il salvataggio dati nel DB dalla sessione
    age_in_weeks =  request.session['age_in_weeks']
    id_strain = request.session['mouse_strain']
    id_source = request.session['source']
    id_status = request.session['status']
    arrival_date = request.session['arrival_date']
    newMice = json.loads(request.session['newMice'])
    #la funziona createList prende la stringa load come input e restituisce una lista di parametri
    list_report = []
    err_message = ""
    #metto tutto in un try/except per poter fare il rollback della transazione in caso di errore
    try:
        for barcode in newMice:
            b = barcode.upper()
            gender = newMice[barcode]
            g = 2
            if gender == 'male':
                g = 1
            #calcolo la data di nascita presunta
            arr_date=arrival_date.split('-')
            d = datetime.date(int(arr_date[0]),int(arr_date[1]),int(arr_date[2])) - timedelta(weeks = int(age_in_weeks))
            #qui sotto faccio delle query per recuperare i dati che mi servono
            strain = Mouse_strain.objects.get(id_strain = id_strain)
            source = Source.objects.get(id_source = id_source)
            status = Status.objects.get(id = id_status)
            m = Mice(id_mouse_strain = strain, id_source = source, barcode=barcode,  id_status= status, available_date = datetime.date.today(), gender = g, birth_date = d, arrival_date = arrival_date)  
            m.save()
            #qui sotto creo una lista per il report, composta da N elementi, uno per ogni topo inserito, composto da strighe che al loro interno hanno gia' del codice HTML
            list_report.append(tableReport([barcode, d, arrival_date, datetime.date.today(), strain, gender, status, source])) 
        transaction.commit()
    except Exception, e:    
        print 'XMM VIEW miceManage.miceLoading: 1) ', str(e)
        transaction.rollback()
        return render_to_response('mice/mice_loading.html', {'name':name, 'err_message': "Something gone wrong." }, RequestContext(request))   
    #salvo la lista per il report nei dati della sessione
    request.session['list_report']=list_report
    print "XMM: end mice loading phase"
    return render_to_response('mice/report.html', {'name':name, 'list_report': list_report,'message':'Xenopatients correctly saved'}, RequestContext(request))

#questa semplice view serve a ridirezionare la pagina dopo aver cliccato su 'continue' nella pagina con il report
@laslogin_required
@login_required
@permission_decorator('xenopatients.can_view_XMM_register_mice')
def continueReport(request):
    print 'XMM VIEW: start miceManage.continueReport'
    return HttpResponseRedirect(reverse("xenopatients.views.index"))

#questa funzione e' usata per la schermata 'Change Status of a Mouse'
@laslogin_required
@login_required
@permission_decorator('xenopatients.can_view_XMM_change_status')
def changeStatus(request):
    print 'XMM VIEW: start miceManage.changeStatus'
    name = request.user.username
    second_step = False
    phase = ""
    form = ChangeForm() # An unbound form
    if request.method == 'POST': # If the form has been submitted..
        if "Start" in request.POST: #prima fase: ho inserito il nuovo status desiderato e clicco su 'go'
            form = ChangeForm(request.POST) # A form bound to the POST data
            status = form.data['target_status']
            request.session['status'] = status
            #verifico se il nuovo status richiede informazioni supplementarie
            data = Status_info_has_status.objects.filter(id_status = Status.objects.get(name = status))
            if len(data) > 0:
                return render_to_response('mice/mice_status.html', {'target_status' : status, 'name':name, 'form':  CustomForm((status)),  'extra':True}, RequestContext(request))
            toSacr = []
            if status == "sacrified":
                miceToSacr = Mice.objects.filter(id_status = Status.objects.get(name = 'toSacrifice'))
                for m in BioMice.objects.filter(phys_mouse_id__in = miceToSacr):
                #for m in miceToSacr:
                    toSacr.append({'nameG' : m.id_genealogy + ' - ' + m.id_group.name, 'genID' : m.id_genealogy})
            print '1'
            return render_to_response('mice/mice_status.html', {'target_status' : status, 'name':name, 'form':  CustomForm((status)),'second_step':True, 'toSacr':toSacr}, RequestContext(request))
        if "go" in request.POST: #l'utente ha aggiunto info supplementari
            extra_info = []
            status = request.session.get('status')
            request.session['status'] = status
            form = CustomForm(status, request.POST) # A form bound to the POST data
            if form.is_valid(): # All validation rules pass
                #recuperare, se serve, la lista dei topi da sacrificare
                toSacr = []
                if form.data.has_key('death_date'):
                    request.session['death_date'] = form.data['death_date']

                if form.data.has_key('notes'):
                    request.session['notes'] = form.data['notes']

                print request.session

                if status == "sacrified":
                    miceToSacr = Mice.objects.filter(id_status = Status.objects.get(name = 'toSacrifice'))
                    for m in BioMice.objects.filter(phys_mouse_id__in = miceToSacr):
                        toSacr.append({'nameG' : m.id_genealogy + ' - ' + m.id_group.name, 'genID' : m.id_genealogy})
                #mette in sessione le varie info per il savataggio
                
                print '2'
                return render_to_response('mice/mice_status.html', {'target_status' : status, 'name':name,  'second_step':True, 'extra_info' : extra_info, 'toSacr':toSacr}, RequestContext(request))
            else:
                data = Status_info_has_status.objects.filter(id_status = Status.objects.get(name = status))
                if data:
                    return render_to_response('mice/mice_status.html', {'target_status' : status, 'name':name, 'form':  form,  'extra':True}, RequestContext(request))
                else:
                    toSacr = []
                    if status == "sacrified":
                        miceToSacr = Mice.objects.filter(id_status = Status.objects.get(name = 'toSacrifice'))
                        for m in BioMice.objects.filter(phys_mouse_id__in = miceToSacr):
                            toSacr.append({'nameG' : m.id_genealogy + ' - ' + m.id_group.name, 'genID' : m.id_genealogy})
                    print '3'
                    return render_to_response('mice/mice_status.html', {'target_status' : status, 'name':name,  'second_step':True, 'toSacr':toSacr}, RequestContext(request))
        if "newStatus" in request.POST: #ricevuti dati da js, dalla chiamata ajax, che mi invia i dati da salvare
            request.session['newStatus'] = request.POST['newStatus']
            print '4'
            return HttpResponseRedirect(reverse("xenopatients.miceManage.finishChange"))
        
    return render_to_response('mice/mice_status.html', {'name':name, 'form': form}, RequestContext(request))

@transaction.commit_manually
@laslogin_required
@login_required
@permission_decorator('xenopatients.can_view_XMM_change_status')
def finishChange(request): 
    print 'XMM VIEW: start miceManage.finishChange'
    name = request.user.username
    #prelevo i dati necessari per il salvataggio dati nel DB dalla sessione
    notes = ""
    death_date = ""
    if request.session.has_key('notes'):
        notes = request.session.get('notes')
    if request.session.has_key('death_date'):
        death_date = request.session.get('death_date')

    print death_date

    newStatus = json.loads(request.session.get('newStatus'))
    list_report, operators = [], []
    err_message = ""
    sendEmailFlag = False
    now = datetime.datetime.now()
    print get_functionality()
    print get_WG_string()
    email = LASEmail (functionality=get_functionality(), wgString=get_WG_string())


    #metto tutto in un try/except per poter fare il rollback della transazione in caso di errore
    try:
        for identifier in newStatus:
            newS = newStatus[identifier]
            bm = None
            wgMouse = []
            if isGenID(identifier): 
                #get the bioMice
                bm = BioMice.objects.get(id_genealogy = identifier)
                m = bm.phys_mouse_id
                wgMouse = BioMice_WG.objects.filter(biomice=bm).values_list('WG__name', flat=True)
            else:
                #get the phys mouse
                m = Mice.objects.get(barcode = identifier)
            groupM = ""
            try:
                groupM = m.id_group.name
            except:
                pass
            oldStatus = m.id_status.name
            m.id_status = Status.objects.get(name = newS)
            if notes != "":
                m.notes = notes
            if death_date != "":
                m.death_date = death_date
            
            m.save()
            gender = "Female"
            if m.gender == 'm':
                gender = 'Male'   
            if newS == 'dead accidentally' or newS == 'sacrified' and bm is not None:
                stopTreat(bm, now)
                cancelProgrammedExpl(bm)

                if newS == 'sacrified':

                    email.addMsg(wgMouse, [identifier])
                    email.addRoleEmail(wgMouse, 'Executor', [request.user.username])

                    sendEmailFlag = True
                    quant = Quantitative_measure.objects.filter(id_mouse = bm)
                    qual = Qualitative_measure.objects.filter(id_mouse = bm)
                    if len(quant) > 0:
                        for q in quant:
                            email.addRoleEmail(wgMouse, 'Planner', [q.id_series.id_operator.username])

                            operators.append(q.id_series.id_operator.email)
                            u = User.objects.get(id=q.id_series.id_operator.id)
                            wg = WG.objects.filter(id__in=WG_User.objects.filter(user=u).values_list('WG', flat=True))
                            for w in wg:
                                operators.append(w.owner.email)
                    if len(qual) > 0:
                        for q in qual:
                            email.addRoleEmail(wgMouse, 'Planner', [q.id_series.id_operator.username])

                            operators.append(q.id_series.id_operator.email)
                            u = User.objects.get(id=q.id_series.id_operator.id)
                            wg = WG.objects.filter(id__in=WG_User.objects.filter(user=u).values_list('WG', flat=True))
                            for w in wg:
                                operators.append(w.owner.email)
            #qui sotto creo una lista per il report, composta da N elementi, uno per ogni topo inserito, composto da strighe che al loro interno hanno gia' del codice HTML
            list_report.append(tableReport([identifier, m.arrival_date, groupM, m.id_mouse_strain, gender, oldStatus, newS]))
        if sendEmailFlag:
            try:
                email.send()
                print 'XMM VIEW miceManage.finishChange: mail send'
            except Exception, e:
                print 'XMM VIEW miceManage.finishChange: 1) '
                print 'xeno: error mail'
                pass
        transaction.commit()
    except Exception, e:    
        print 'XMM VIEW miceManage.finishChange: 2) ', str(e)
        transaction.rollback()
        return render_to_response('mice/mice_loading.html', {'name':name, 'err_message': "Something gone wrong." }, RequestContext(request))
    #salvo la lista per il report nei dati della sessione
    request.session['list_report']=list_report
    if request.session.get('notes'):
        del request.session['notes']
    if request.session.get('death_date'):
        del request.session['death_date']
    if request.session.get('statusList'):
        del request.session['statusList']
    print "XMM: end change status session"
    return render_to_response('mice/reportStatus.html', {'name':name, 'list_report': list_report,'message':'Status correctly updated'}, RequestContext(request))

#questa semplice view serve a ridirezionare la pagina dopo aver cliccato su 'continue' nella pagina con il report
@laslogin_required
@login_required
@permission_decorator('xenopatients.can_view_XMM_change_status')
def continueStatusReport(request):
    print 'XMM VIEW: start miceManage.continueStatusReport'
    return HttpResponseRedirect(reverse("xenopatients.miceManage.changeStatus"))
