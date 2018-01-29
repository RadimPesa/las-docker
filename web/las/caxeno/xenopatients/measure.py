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
from xenopatients.treatments import *
from LASAuth.decorators import laslogin_required
from django.core.mail import send_mail, EmailMultiAlternatives
from django.contrib.auth.decorators import user_passes_test
import os, cStringIO, csv, time, urllib, urllib2, datetime
from apisecurity.decorators import *
from django.conf import settings
from lasEmail import *

def sendMailMeasure(name, gList, typeM, onlyForQual,wgDict,functionality ,request):
    print 'XMM VIEW: start measure.sendMailMeasure'
    #try:
    #    operator = User.objects.get(username = "andrea.bertotti")
    #except:
    email = LASEmail (functionality=get_functionality(), wgString=get_WG_string())
    wgMouse=wgDict.keys()
    email.addRoleEmail(wgMouse, 'Executor', [request.user.username])
    operator = User.objects.get(username = request.user.username)
    mailOperator = operator.email
    subject, from_email = 'Measure Alert', settings.EMAIL_HOST_USER
    string = ""
    qualS = ""
    text_content = 'There are new ' + typeM + ' measures made by ' + name + ' ready to be evaluate.\nThe involved group/s is/are:\n'
    for wg in wgMouse:
        for g in gList:
            if g in wgDict[wg]:
                if string == "":
                    string = g
                else:
                    string = string + '\n' + g
        email.addMsg([wg],[text_content+ string])
        #email.appendSubject([wg],string)
        if typeM == 'qualitative':
            for g in onlyForQual:
                if g in wgDict[wg]:
                    if qualS == "":
                        qualS = g
                    else:
                        qualS = qualS + '\n' + g
            if qualS != "":
                email.addMsg([wg],["\nThe group/s to be checked is/are:\n" + qualS])
    try:
        email.send()
    except Exception,e:
        print 'error in send mail measure'
    return

def stopTreatment(m, now):
    print 'XMM VIEW: start measure.stopTreatment'
    try:
        mhtStop = Mice_has_arms.objects.filter(id_mouse = m,  start_date__isnull = False, end_date__isnull = True)[0]
        treatment = Arms.objects.get(pk = mhtStop.id_protocols_has_arms.id_arm.id)
        mhtStop.end_date = now
        mhtStop.save()
        forceExpl(m, treatment) #l'if per vedere se si deve fare l'espianto forzato e' all'interno di questa chiamata
    except:
        try:
            mhtStop = Mice_has_arms.objects.filter(id_mouse = m, end_date__isnull = True)[0]
            treatment = Arms.objects.get(pk = mhtStop.id_protocols_has_arms.id_arm.id)
            mhtStop.end_date = now
            mhtStop.save()
            forceExpl(m, treatment)
        except:
            pass
    return

def programTreat(startD, m, name, typeM, id_measure, treat_name, id_pev):
    print 'XMM VIEW: start measure.programTreat'
    nameP, nameA = splitNameT(treat_name)
    if startD != "":
        struct = time.strptime(startD, "%Y-%m-%d %H:%M:%S")
        start = datetime.datetime.fromtimestamp(mktime(struct))
        if typeM == 'qual':
            if id_measure != None:
                pEv = ProgrammedEvent(insertionDate = datetime.date.today(),
                                      id_mouse = m,
                                      measureOperator = User.objects.get(username = name),
                                      id_qual = id_measure,
                                      id_status = EventStatus.objects.get(name = 'accepted'))
            else:
                pEv = ProgrammedEvent(insertionDate = datetime.date.today(),
                                      id_mouse = m,
                                      measureOperator = User.objects.get(username = name),
                                      id_status = EventStatus.objects.get(name = 'accepted'))
            pEv.save()
            pT = Pr_treatment(id_event = pEv,
                              id_pha = Protocols_has_arms.objects.get(id_arm = Arms.objects.get(name = nameA), id_protocol = Protocols.objects.get(name = nameP)),
                              expectedStartDate = start)
            pT.save()
        elif typeM == 'quant':
            pT = Pr_treatment(id_event = id_pev,
                              id_pha = Protocols_has_arms.objects.get(id_arm = Arms.objects.get(name = nameA), id_protocol = Protocols.objects.get(name = nameP)),
                              expectedStartDate = start)
            pT.save()
    return

def changeStatus(biom, id_pev, status, scope, scopeNotes):
    try:
        print 'XMM VIEW: start measure.changeStatus ->', str(status), str(scope)
        isNew = '0'
        m = biom.phys_mouse_id
        if status == "explant without sacrifice": #aggiorno lo status se si vuole espiantare questo topo senza sacrificarlo
            if m.id_status != Status.objects.get(name = 'explantLite'):
                isNew = '1'
                newStatus = Status.objects.get(name = 'explantLite')
                pS = Pr_changeStatus(id_event = id_pev, newStatus = newStatus )
                pS.save()
        elif status == "sacrifice without explant": #aggiorno lo status se si e' sacrificato questo topo
            if m.id_status != Status.objects.get(name = 'toSacrifice'):
                isNew = '1'
                newStatus = Status.objects.get(name = 'toSacrifice')
                status = "to sacrifice"
                pS = Pr_changeStatus(id_event = id_pev, newStatus = newStatus )
                pS.save()
        elif status == "ready for explant": #aggiorno lo status se si e' programmato un espianto per questo topo
            #if m.id_status != Status.objects.get(name = 'ready for explant'):
            isNew = '1'
            removeOldExpl(biom)
            print scope
            if scope != "" and scope != " ":
                pT = Pr_explant(id_event = id_pev, id_scope = Scope_details.objects.get(description = str(scope)), scopeNotes = scopeNotes )
            else:
                pT = Pr_explant(id_event = id_pev, id_scope = Scope_details.objects.get(id_scope_details = 1), scopeNotes = scopeNotes )
            pT.save()
    except:
        pass
    return isNew


def removeOldExpl(m):
    print 'XMM VIEW: start measure.removeOldExpl'
    peList = Programmed_explant.objects.filter(id_mouse = m, done = '0')
    if len(peList) > 0:
        for pe in peList:
            pe.delete()

#funzione per visualizzare la pagina delle misure qualitative e, se si ricevono dati da ajax, inoltrarli alla funzione che li salva e visualizza il report
@laslogin_required
@login_required
@permission_decorator('xenopatients.can_view_XMM_perform_qualitative')
def qualMeasure(request):
    print 'XMM VIEW: start measure.qualMeasure'
    name = request.user.username
    if request.method == 'POST':
        if "obj" in request.POST: #ricevuti dati da ajax
            request.session['qual'] = request.POST['obj']
            return HttpResponseRedirect(reverse("xenopatients.measure.qualReport"))
    return render_to_response('measure/qual.html', {'name':name, 'formValue': QualMeasureForm(), 'formSD':ScopeForm(), 'formSite':SiteForm()}, RequestContext(request))

@laslogin_required
@login_required
@permission_decorator('xenopatients.can_view_XMM_perform_qualitative')
def qualMeasureWeight(request):
    print 'XMM VIEW: start measure.qualMeasureWeight'
    name = request.user.username
    if request.method == 'POST':
        if "obj" in request.POST: #ricevuti dati da ajax
            request.session['qual'] = request.POST['obj']
            return HttpResponseRedirect(reverse("xenopatients.measure.qualReport"))
    return render_to_response('measure/qual_weight.html', {'name':name, 'formValue': QualMeasureForm(), 'formSD':ScopeForm(), 'formSite':SiteForm()}, RequestContext(request))

#salva i dati e visualizza la pagina con il report delle misure fatte
@transaction.commit_manually
@laslogin_required
@login_required
@permission_decorator('xenopatients.can_view_XMM_perform_qualitative')
def qualReport(request):
    print 'XMM VIEW: start measure.qualReport'
    name = request.user.username
    d = datetime.date.today()
    data = json.loads(request.session['qual'])
    list_report, report, gList, toCheckList = [], [], [], []
    try:
        ms = Measurements_series(id_operator = User.objects.get(username = name), date=d, id_type = Type_of_measure.objects.get(description = 'qualitative')) #creo la nuova serie di misure
        ms.save()
        id_series = ms
        print '1'
        now = datetime.datetime.now()
        print '2'
        wgDict={}
        functionality=get_functionality()
        for group in data:
            for genID in data[group]:
                singleMeasure = data[group][genID]
                id_measure = None
                m = BioMice.objects.get(id_genealogy = genID)
                wgMouse=BioMice_WG.objects.filter(biomice=m).values_list('WG__name',flat=True)
                for wgName in wgMouse:
                    if wgName not in wgDict:
                        wgDict[wgName]=set()
                    wgDict[wgName].add(m.id_group.name)
                if m.id_group.name not in gList:
                    gList.append( m.id_group.name )
                print 'measure --- ', singleMeasure
                barcode, size, status, scope, notes, weight, scopeNotes, treat_name, extra, startD, duration, check = singleMeasure[9], singleMeasure[2], singleMeasure[6], singleMeasure[7], singleMeasure[8], singleMeasure[3], singleMeasure[10], singleMeasure[11], singleMeasure[12], singleMeasure[14], singleMeasure[15], singleMeasure[16]
                print barcode, size, status, scope, notes, weight, scopeNotes, treat_name, extra, startD, duration, check
                onlyMeasure = True
                if weight == "":
                    weight = None
                if treat_name:
                    nameP, nameA = splitNameT(treat_name)
                if size != "":
                    measure = Qualitative_measure(id_series = id_series, id_mouse = m, id_value = Qualitative_values.objects.get(value = size.lstrip()), weight = weight, notes = notes)
                    measure.save()
                    id_measure = measure
                if check == "true":
                    if m.id_group.name not in toCheckList:
                        toCheckList.append(m.id_group.name)
                    if size != "":
                        pEv = ProgrammedEvent(insertionDate = datetime.date.today(),
                                              id_mouse = m,
                                              measureOperator = User.objects.get(username = name),
                                              id_qual = id_measure,
                                              id_status = EventStatus.objects.get(name = 'pending'))
                    else:
                        pEv = ProgrammedEvent(insertionDate = datetime.date.today(),
                                              id_mouse = m,
                                              measureOperator = User.objects.get(username = name),
                                              id_status = EventStatus.objects.get(name = 'pending'))
                    pEv.save()
                    id_pev = pEv
                    isNew = changeStatus(m, id_pev, status, scope, scopeNotes)
                    statusR = [status, isNew]
                    if extra == 'stop' or extra == 'new': #stop o new vuol dire che ho stoppato il trattamento (stop) o che l'ho stoppato e fatto un altro (new): devo stoppare il vecchio trattamento
                        try:
                            mhtStop = Mice_has_arms.objects.filter(id_mouse = m,  start_date__isnull = False, end_date__isnull = True)[0]
                            treatment = Arms.objects.get(pk = mhtStop.id_protocols_has_arms.id_arm.id)
                            forceExpl(m, treatment) #l'if per vedere se si deve fare l'espianto forzato e' all'interno di questa chiamata
                            pr_stop = Pr_stopTreatment(id_mha = mhtStop, id_event = id_pev, stopDate = now)
                            pr_stop.save()
                        except Exception, e:
                            try:
                                mhtStop = Mice_has_arms.objects.filter(id_mouse = m, end_date__isnull = True)[0]
                                treatment = Arms.objects.get(pk = mhtStop.id_protocols_has_arms.id_arm.id)
                                forceExpl(m, treatment)
                                pr_stop = Pr_stopTreatment(id_mha = mhtStop, id_event = id_pev, stopDate = now)
                                pr_stop.save()
                            except Exception, e:
                                print 'XMM VIEW measure.qualReport 1) ', str(e)
                                pass
                    #if treat_name != "": #se esiste un trattamento assegnato al topo
                    #    if startD != "":
                    if extra == 'new':
                        struct = time.strptime(startD, "%Y-%m-%d %H:%M:%S")
                        start = datetime.datetime.fromtimestamp(mktime(struct))
                        pT = Pr_treatment(id_event = id_pev,
                                          id_pha = Protocols_has_arms.objects.get(id_arm = Arms.objects.get(name = nameA), id_protocol = Protocols.objects.get(name = nameP)),
                                          expectedStartDate = start )
                        pT.save()

                else:
                    physMouse = m.phys_mouse_id
                    if status == "explant without sacrifice": #aggiorno lo status se si vuole espiantare questo topo senza sacrificarlo
                        physMouse.id_status = Status.objects.get(name = 'explantLite')
                        physMouse.save()
                    elif status == "sacrifice without explant": #aggiorno lo status se si e' sacrificato questo topo
                        physMouse.id_status = Status.objects.get(name = 'toSacrifice')
                        physMouse.save()
                        stopTreat(m, now)
                        #funzione diversa da stopTreatment
                        cancelProgrammedExpl(m)
                    elif status == "ready for explant": #se il topo e' stato programmato da espiantare, aggiorno il suo status
                        physMouse.id_status = Status.objects.get(name = "ready for explant")
                        physMouse.save()
                        removeOldExpl(m)
                        print scope
                        print '1'
                        if scope != '' and scope != " ":
                            pe = Programmed_explant(id_scope = Scope_details.objects.get(description = scope), id_mouse = m, scopeNotes = scopeNotes)
                        else:
                            pe = Programmed_explant(id_scope = Scope_details.objects.get(id_scope_details = 1), id_mouse = m, scopeNotes = scopeNotes)
                        pe.save()
                        print '2'

                    end_date, start = "",""
                    if extra == 'stop' or extra == 'new': #stop o new vuol dire che ho stoppato il trattamento (stop) o che l'ho stoppato e fatto un altro (new): devo stoppare il vecchio trattamento
                        stopTreatment(m, now)
                    #print treat_name, startD, extra
                    #if treat_name != "": #se esiste un trattamento assegnato al topo
                    #    if startD != "":
                    if extra == 'new':
                        programTreat(startD, m, name, 'qual', id_measure, treat_name, '')
                if treat_name == "" and status != "sacrifice without explant":
                    mha = Mice_has_arms.objects.filter(id_mouse = m, end_date__isnull = True)
                    if len(mha) > 0:
                        treat_name = getNameT(mha[0])
                        if mha[0].start_date != None:
                            startD = mha[0].start_date
                        else:
                            try:
                                startD = mha[0].id_prT.expectedStartDate
                            except:
                                pass
                        duration = str(mha[0].id_protocols_has_arms.id_arm.duration) + ' [' + str(mha[0].id_protocols_has_arms.id_arm.type_of_time) + ']'
                if scope == "":
                    pe = Programmed_explant.objects.filter(id_mouse = m, done = 0)
                    status = m.phys_mouse_id.id_status.name
                    if len(pe) > 0:
                        scope = pe[0].id_scope.description
                        scopeNotes = pe[0].scopeNotes
                list_report.append(tableReport([genID, m.phys_mouse_id.barcode, m.id_group.name, size, weight, status, scope, scopeNotes, treat_name, startD, duration, notes]))
        if len(toCheckList) > 0:
            sendMailMeasure(name, gList, 'qualitative', toCheckList,wgDict,functionality,request)
        transaction.commit()
    except Exception, e:
        transaction.rollback()
        print 'XMM VIEW measure.qualReport: 2)  ', str(e)
        return render_to_response('index.html', {'name':name, 'err_message': str(e) }, RequestContext(request))

    request.session['name'] = name
    request.session['list_report'] = list_report

    return HttpResponseRedirect(reverse("xenopatients.measure.measurequalReport"))
    #return render_to_response('measure/qualReport.html', {'name':name, 'list_report': list_report}, RequestContext(request))

#funzione per visualizzare la pagina delle misure quantitative e, se si ricevono dati da ajax, inoltrarli alla funzione che li salva e visualizza il report
@laslogin_required
@login_required
@permission_decorator('xenopatients.can_view_XMM_perform_quantitative')
def quantMeasure(request):
    print 'XMM VIEW: start measure.quantMeasure'
    name = request.user.username
    if request.method == 'POST':
        if "obj" in request.POST:
            request.session['quant'] = request.POST['obj']
            #request.session['lastG'] = request.POST['lastG']
            return HttpResponseRedirect(reverse("xenopatients.measure.quantReport"))
    return render_to_response('measure/quant.html', {'name':name, 'formSD':ScopeForm(), 'formSite':SiteForm()}, RequestContext(request))


@laslogin_required
@login_required
@permission_decorator('xenopatients.can_view_XMM_perform_quantitative')
def quantMeasure3d(request):
    print 'XMM VIEW: start measure.quantMeasure3d'
    name = request.user.username
    if request.method == 'POST':
        if "obj" in request.POST:
            request.session['quant'] = request.POST['obj']
            #request.session['lastG'] = request.POST['lastG']
            return HttpResponseRedirect(reverse("xenopatients.measure.quantReport"))
    return render_to_response('measure/quant3d.html', {'name':name, 'formSD':ScopeForm(), 'formSite':SiteForm()}, RequestContext(request))


@laslogin_required
@login_required
@permission_decorator('xenopatients.can_view_XMM_perform_quantitative')
def quantMeasureWeight(request):
    print 'XMM VIEW: start measure.quantMeasureWeight'
    name = request.user.username
    if request.method == 'POST':
        if "obj" in request.POST:
            request.session['quant'] = request.POST['obj']
            #request.session['lastG'] = request.POST['lastG']
            return HttpResponseRedirect(reverse("xenopatients.measure.quantReport"))
    return render_to_response('measure/quant_weight.html', {'name':name, 'formSD':ScopeForm(), 'formSite':SiteForm()}, RequestContext(request))


@laslogin_required
@login_required
@permission_decorator('xenopatients.can_view_XMM_perform_quantitative')
def quantMeasureWeight3d(request):
    print 'XMM VIEW: start measure.quantMeasureWeight3d'
    name = request.user.username
    if request.method == 'POST':
        if "obj" in request.POST:
            request.session['quant'] = request.POST['obj']
            #request.session['lastG'] = request.POST['lastG']
            return HttpResponseRedirect(reverse("xenopatients.measure.quantReport"))
    return render_to_response('measure/quant_weight_3d.html', {'name':name, 'formSD':ScopeForm(), 'formSite':SiteForm()}, RequestContext(request))



#salva i dati e visualizza la pagina con il report delle misure fatte
@transaction.commit_manually
@laslogin_required
@login_required
@permission_decorator('xenopatients.can_view_XMM_perform_quantitative')
def quantReport(request):
    print 'XMM VIEW: start measure.quantReport'
    try:
        name = request.user.username
        d = datetime.date.today()
        data = json.loads(request.session['quant'])
        list_report, report, gList = [], [], []
        ms = Measurements_series(id_operator = User.objects.get(username = name), date=d, id_type = Type_of_measure.objects.get(description = 'quantitative')) #creo la nuova serie di misure
        ms.save()
        id_series = ms
        now = datetime.datetime.now()
        print data
        wgDict={}
        functionality=get_functionality()
        for group in data:
            for genID in data[group]:
                print genID
                singleMeasure = data[group][genID]
                id_measure = None
                m = BioMice.objects.get(id_genealogy = genID)

                wgMouse=BioMice_WG.objects.filter(biomice=m).values_list('WG__name',flat=True)
                for wgName in wgMouse:
                    if wgName not in wgDict:
                        wgDict[wgName]=set()
                    wgDict[wgName].add(m.id_group.name)

                if m.id_group.name not in gList:
                    gList.append( m.id_group.name )
                print 'measure --', singleMeasure
                genID, x, y, z, v, status, scope, notes, weight, scopeNotes, treat_name, extra, startD, duration = singleMeasure[1], singleMeasure[2], singleMeasure[3], singleMeasure[4], singleMeasure[5], singleMeasure[9], singleMeasure[10], singleMeasure[11], singleMeasure[6], singleMeasure[13], singleMeasure[14], singleMeasure[15], singleMeasure[17], singleMeasure[18]
                print str(genID), str(x), str(y), str(v), str(status), str(scope), str(notes), str(weight), str(scopeNotes), str(treat_name), str(extra), str(startD), str(duration)
                if weight == "":
                    weight = None
                if treat_name:
                    nameP, nameA = splitNameT(treat_name)
                if v != "":
                    measure = Quantitative_measure(id_series = id_series, id_mouse = m, x_measurement= x, y_measurement= y, volume= v , notes = notes, weight = weight, z_measurement= z)
                    print '1'
                    measure.save()
                    print '2'
                    id_measure = measure
                    print '3'
                    pEv = ProgrammedEvent(insertionDate = datetime.date.today(),
                                          id_mouse = m,
                                          measureOperator = User.objects.get(username = name),
                                          id_quant = id_measure,
                                          id_status = EventStatus.objects.get(name = 'pending'))
                    print '4'
                else:
                    pEv = ProgrammedEvent(insertionDate = datetime.date.today(),
                                          id_mouse = m,
                                          measureOperator = User.objects.get(username = name),
                                          id_status = EventStatus.objects.get(name = 'pending'))
                pEv.save()
                id_pev = pEv

                print '1'
                changeStatus(m, id_pev, status, scope, scopeNotes)
                print '2'
                end_date,start = "",""
                print 'extra', extra
                if extra == 'stop' or extra == 'new': #se e' stato stoppato o stoppato e riassegnato un trattamento, devo stoppare il trattamento vecchio
                    try:
                        mhtStop = Mice_has_arms.objects.filter(id_mouse = m,  start_date__isnull = False, end_date__isnull = True)[0]
                        treatment = Arms.objects.get(pk = mhtStop.id_protocols_has_arms.id_arm.id)
                        forceExpl(m, treatment) #l'if per vedere se si deve fare l'espianto forzato e' all'interno di questa chiamata
                        pr_stop = Pr_stopTreatment(id_mha = mhtStop, id_event = id_pev, stopDate = now)
                        pr_stop.save()
                    except Exception, e:
                        try:
                            mhtStop = Mice_has_arms.objects.filter(id_mouse = m, end_date__isnull = True)[0]
                            treatment = Arms.objects.get(pk = mhtStop.id_protocols_has_arms.id_arm.id)
                            forceExpl(m, treatment)
                            pr_stop = Pr_stopTreatment(id_mha = mhtStop, id_event = id_pev, stopDate = now)
                            pr_stop.save()
                            print 'end except'
                        except Exception, e:
                            print 'XMM VIEW measure.quantReport: 1) ', str(e)
                            pass
                #if treat_name != "":
                #    if startD != "":
                if extra == 'new':
                    programTreat(startD, m, name, 'quant', id_measure, treat_name, pEv)
                if treat_name == "" and status != "sacrifice without explant":
                    mha = Mice_has_arms.objects.filter(id_mouse = m, end_date__isnull = True)
                    if len(mha) > 0:
                        treat_name = getNameT(mha[0])
                        if mha[0].start_date != None:
                            startD = mha[0].start_date
                        else:
                            try:
                                startD = mha[0].id_prT.expectedStartDate
                            except:
                                pass
                        duration = str(mha[0].id_protocols_has_arms.id_arm.duration) + ' [' + str(mha[0].id_protocols_has_arms.id_arm.type_of_time) + ']'
                if scope == "":
                    pe = Programmed_explant.objects.filter(id_mouse = m, done = 0)
                    status = m.phys_mouse_id.id_status.name
                    if len(pe) > 0:
                        scope = pe[0].id_scope.description
                        scopeNotes = pe[0].scopeNotes

                list_report.append(tableReport([genID, m.phys_mouse_id.barcode, m.id_group.name, str(x).replace('.',','), str(y).replace('.',','), str(z).replace('.',','), str(v).replace('.',','), weight, status, scope, scopeNotes, treat_name, startD, duration, notes]))
        request.session['quantRep'] = list_report #salvo nella sessione i dati per il report
        sendMailMeasure(name, gList, 'quantitative', [],wgDict,functionality,request)
        transaction.commit()
    except Exception, e:
        print 'XMM VIEW measure.quantReport: 2) ', str(e)
        transaction.rollback()
        return render_to_response('index.html', {'name':name, 'err_message': str(e) }, RequestContext(request))

    request.session['name'] = name
    request.session['list_report'] = list_report

    return HttpResponseRedirect(reverse("xenopatients.measure.measurequantReport"))
    #return render_to_response('measure/quantReport.html', {'name':name, 'list_report': list_report}, RequestContext(request))


@laslogin_required
@login_required
@permission_decorator('xenopatients.can_view_XMM_perform_quantitative')
def measurequantReport(request):
    print 'XMM VIEW: start measure.measurequantReport'
    #pulisco la sessione
    name = None
    list_report = None
    if request.session.get('qual'):
        del request.session['qual']
    if request.session.get('stringsForSave'):
        del request.session['stringsForSave']
    if request.session.get('lastG'):
        del request.session['lastG']
    if request.session.get('quant'):
        del request.session['quant']
    if request.session.get('name'):
        name = request.session['name']
        del request.session['name']
    if request.session.get('list_report'):
        list_report = request.session['list_report']
        del request.session['list_report']


    return render_to_response('measure/quantReport.html', {'name':name, 'list_report': list_report}, RequestContext(request))




@laslogin_required
@login_required
def measurequalReport(request):
    print 'XMM VIEW: start measure.measurequalReport'
    #pulisco la sessione
    name = None
    list_report = None
    if request.session.get('qual'):
        del request.session['qual']
    if request.session.get('stringsForSave'):
        del request.session['stringsForSave']
    if request.session.get('lastG'):
        del request.session['lastG']
    if request.session.get('quant'):
        del request.session['quant']
    if request.session.get('name'):
        name = request.session['name']
        del request.session['name']
    if request.session.get('list_report'):
        list_report = request.session['list_report']
        del request.session['list_report']

    return render_to_response('measure/qualReport.html', {'name':name, 'list_report': list_report}, RequestContext(request))



#view per il tasto 'continue' della pagina con il report
@laslogin_required
@login_required
def continueReport(request):
    print 'XMM VIEW: start measure.continueReport'
    #pulisco la sessione
    if request.session.get('qual'):
        del request.session['qual']
    if request.session.get('stringsForSave'):
        del request.session['stringsForSave']
    if request.session.get('lastG'):
        del request.session['lastG']
    if request.session.get('quant'):
        del request.session['quant']
    return HttpResponseRedirect(reverse("xenopatients.views.index"))

#crea la schermata per avviare un trattamento su un topo(il fatto che si apre in una nuova finestra e' gestito da javascript)
@laslogin_required
@login_required
def startTreatment(request):
    print 'XMM VIEW: start measure.startTreatment'
    name = request.user.username
    if request.method == 'POST':
        if "statusGantt" in request.POST:
            response = request.POST['statusGantt']
            request.session['gantt'] =  response
            request.session['drugs'] = request.POST['drugs']
            request.session['nameT'] = request.POST['nameT']
            request.session['description'] = request.POST['description']
            request.session['typeTime'] = request.POST['typeTime']
            request.session['forcesExplant'] = request.POST['forcesExplant']
            request.session['duration'] = request.POST['duration']
            return HttpResponseRedirect(reverse("xenopatients.views.saveTreatment"))
    return render_to_response('treatments/start.html', {'name':name, 'form': ExisistingProtocolsForm(),'date':str(datetime.date.today()+ datetime.timedelta(days=1))}, RequestContext(request))
