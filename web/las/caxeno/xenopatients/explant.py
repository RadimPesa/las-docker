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

#funzione per gestire la prima interfaccia degli espianti
@laslogin_required
@login_required
@permission_decorator('xenopatients.can_view_XMM_explant_xenografts')
def startExplant(request):
    print 'XMM VIEW: start explant.startExplant'
    name = request.user.username
    tessuti, idinput, miceInput = {}, [], []
    a = Collection() #oggetto di supporto per creare le varie tabelle della seconda schermata
    miceReady = Programmed_explant.objects.filter(done = '0')
    miceFlag = True
    form = CollectionForm()
    formT = TissueForm()
    formT.fields['tissue'].choices=CASI
    formPE = ProgrammedExplantForm()
    if not miceReady:
        miceFlag = False
    if request.method == 'POST':
        if 'delete' in request.POST:
            try:
                stringMice = request.POST['miceList']
                for m in stringMice.split(','):
                    biomouse = BioMice.objects.get(id_genealogy = m)
                    mouse = biomouse.phys_mouse_id
                    mouse.id_status = Status.objects.get(name = 'implanted')
                    mouse.save()
                    pe = Programmed_explant.objects.filter(id_mouse = biomouse, done = '0')
                    for p in pe:
                        p.delete()
                return HttpResponseRedirect(reverse("xenopatients.explant.startExplant"))
            except Exception, e:
                print "XMM VIEW explant.startExplant: 1) " + str(e)
        if 'reload' in request.POST:
            try:
                miceList, tissueList = [], []
                for t in request.POST['tissueList'].split(','):
                    tissueList.append(t)
                for m in request.POST['miceList'].split(','):
                    miceList.append(m)
                formT = TissueForm()
                variables = {'name':name, 'a':a,'secondo':True, 'miceInput':miceList, 'idinput':tissueList, 'date':request.POST['date'], 'notes':request.POST['notes'], 'formT':formT}
                request.session['restoreE'] = variables
                return HttpResponseRedirect(reverse("xenopatients.explant.restoreExpl"))
            except Exception, e:
                print "XMM VIEW explant.startExplant: 1) " + str(e)
        form = CollectionForm(request.POST)
        formT = TissueForm(request.POST)
        formPE = ProgrammedExplantForm(request.POST)
        if form.is_valid() and formT.is_valid() and formPE.is_valid():
            #ho premuto il pulsante submit della prima schermata 
            #'start' e' il valore dell'attributo name del pulsante di submit
            if 'start' in request.POST:
                fase = 'start'
                secondo = True
                r = formT.cleaned_data.get('tissue')
                notes = request.POST['notes']
                try:
                    date = request.POST.get('date')
                    notes = request.POST.get('notes')
                    s = Series( id_operator = User.objects.get(username = name), id_type = Type_of_serie.objects.get(description = 'explant'), date = date, notes = notes) #creo la nuova serie
                    request.session['series'] = s
                except Exception, e:
                    print "XMM VIEW explant.startExplant: 3) " + str(e)
                for i in range(0,r.__len__()): #vedo i tessuti selezioni
                    tissueT = TissueType.objects.get(id = r[i])
                    idinput.append(str(int(r[i]) ))
                r = formPE.cleaned_data.get('mice')
                for i in range(0,r.__len__()): #vedo i topi selezionati
                    barcode = BioMice.objects.get(id_genealogy = r[i]).phys_mouse_id.barcode
                    for biomouse in BioMice.objects.filter( phys_mouse_id = Mice.objects.get(barcode = barcode) ):
                        implant = Implant_details.objects.get( id_mouse = biomouse )
                        miceInput.append('N' + barcode + implant.site.shortName ) #normal explant
                #oltre ai topi selezionati, aggiungo anche i topi 'explant without sacrifice'
                mice = Mice.objects.filter(id_status = Status.objects.get(name = "explantLite"))
                for m in mice:
                    barcode = m.barcode
                    for biomouse in BioMice.objects.filter( phys_mouse_id = Mice.objects.get(barcode = barcode) ):
                        implant = Implant_details.objects.get( id_mouse = biomouse )
                        miceInput.append('L' + barcode + implant.site.shortName ) #lite explant
                mice = Mice.objects.filter(id_status = Status.objects.get(name = "waste"))
                for m in mice:
                    barcode = m.barcode
                    for biomouse in BioMice.objects.filter( phys_mouse_id = Mice.objects.get(barcode = barcode) ):
                        implant = Implant_details.objects.get( id_mouse = biomouse )
                        miceInput.append('N' + barcode + implant.site.shortName ) #lite explant #waste (as normal) explant
                variables = RequestContext(request, {'date':date, 'notes': notes, 'name':name, 'form': form,'formT':formT,'a':a,'secondo':True,"tissueT":tissueT,"idinput":idinput, "miceInput":miceInput, 'miceFlag':miceFlag, 'site':SiteForm() })
                return render_to_response('explants/start.html',variables)
    variables = RequestContext(request, {'name':name, 'form': form, 'formT':formT, 'formPE':formPE, 'a':a, 'secondo':False, 'miceFlag':miceFlag})
    return render_to_response('explants/start.html',variables)

@laslogin_required
@login_required
@permission_decorator('xenopatients.can_view_XMM_explant_xenografts')
def restoreExpl(request):
    print 'XMM VIEW: start explant.restoreExpl'
    variables = request.session.get('restoreE')
    return render_to_response('explants/start.html',variables, RequestContext(request))

#associato al tasto submit finale
#salvo le aliquote create, la serie, i dettagli dell'espianti, le modifiche a Mice e Programmed_explant e poi mando i dati alla biobanca
@transaction.commit_manually
@laslogin_required
@login_required
@permission_decorator('xenopatients.can_view_XMM_explant_xenografts')
def explantSubmit(request):
    print 'XMM VIEW: start explant.explantSubmit'
    try:
        i = 0
        name = request.user.username
        aliquotList = ""
        if request.method == 'POST':
            if 'explants' in request.POST:
                explants = json.loads(request.POST['explants'])
                print '[XMM] received data for explants'
                print request.POST
                now = datetime.datetime.now()
                #recupero l'URL della biobanca
                try: 
                    url = Urls.objects.get(default = '1').url + "/explants/"
                    #print url
                    transaction.commit()
                except Exception, e:
                    print 'XMM VIEW explant.explantSubmit: 1) ' +  str(e)
                    transaction.rollback()
                date = request.POST['date']
                notes = request.POST['notes']
                operator = request.user.username
                miceList = request.POST['miceList']
                explantsString = request.POST['explants']
                values = {'explants' : explantsString, 'date': date, 'operator': operator}
                res = ""
                #invio i dati alla biobanca
                try:
                    data = urllib.urlencode(values)
                    req = urllib2.Request(url, data=data, headers={"workingGroups" : get_WG_string()})
                    u = urllib2.urlopen(req)
                    #u = urllib2.urlopen(url, data)
                    res =  u.read() #mi dice se il salvataggio su biobank/storage e' andato a buon fine o meno
                    print 'XMM VIEW explant.explantSubmit: biobank response ' +  str(res)
                except Exception, e: #in caso di timeout di catissue o nel caso non sia online
                    print 'XMM VIEW explant.explantSubmit: 2) ' +  str(e)
                    request.session['message'] = "Something gone wrong while linking with the BioBank."
                    return HttpResponseRedirect(reverse("xenopatients.views.index"))    
                #res contiene il responso alla precedente richiesta. Indica se la biobanca ha salvato correttamente i dati o meno
                if res == 'err':
                    request.session['message'] = "Something gone wrong while linking with the BioBank."
                    return HttpResponseRedirect(reverse("xenopatients.views.index"))
                #se ha salvato, salvo anche io
                if res == 'ok':
                    try:
                        list_report2, parsedMice = [],[]
                        #crea serie
                        s = Series(id_operator = User.objects.get(username = operator), id_type = Type_of_serie.objects.get(description = 'explant'), date = date, notes = notes)
                        s.save()
                        id_series = s
                        #aggiorna (eventualmente) status topo ---> espiantato o ritorna a impiantato per expl_lite
                        mice = string.split(miceList, '|')
                        print 'mice', mice
                        for mouse in mice:
                            #salvo cambio status di tutti i topi espiantati
                            print 'mouse',mouse
                            if len(string.split(mouse, '_')) > 1:
                                data = string.split(mouse, '_')
                                if data[1] == '1': #if used this mouse
                                    mouse = data[0]
                                    barcode = mouse[1:len(mouse) - 3].upper()
                                    siteImpl = mouse[-3:].upper()
                                    print 'sito',siteImpl
                                    print 'parsedmice',parsedMice
                                    if barcode not in parsedMice:
                                        print 'barcode', barcode
                                        typeE = mouse[0:1]
                                        m = Mice.objects.get(barcode = barcode)
                                        list_report2, parsedMice = updateExplantedStatus(list_report2, m, typeE, s, now, parsedMice)
                                        biomice = BioMice.objects.filter(phys_mouse_id=m)
                                        print 'biomice',biomice
                                        for bm in biomice:
                                            print 'bm',bm
                                            try:
                                                #impl = Implant_details.objects.get(id_mouse=bm, site= Site.objects.get(shortName = siteImpl))
                                                explD = Explant_details(id_mouse = bm, id_series = id_series )
                                                explD.save()
                                            except Exception, e:
                                                print 'Error in creating explant detail ', e
                                                continue

                                        
                        #crea gli oggetti expl_det
                        #salva anche le aliquote ottenute
                        #creare una stringa con tutte le aliquote separate da ','
                        print 'explants ', explants
                        tempList = []
                        for typeA in explants:
                            print 'typeA', typeA
                            for genID in explants[typeA]:
                                print 'genid', genID
                                biomouse = BioMice.objects.get(id_genealogy = genID)
                                ed = Explant_details.objects.get(id_mouse = BioMice.objects.get(id_genealogy = genID), id_series = id_series )
                                for barcodeP in explants[typeA][genID]:
                                    for tube in explants[typeA][genID][barcodeP]:
                                        newG = tube['genID']
                                        pos = tube['pos']
                                        quant = tube['qty']
                                        classGen = GenealogyID(newG)
                                        typeAl = classGen.getTissueType()
                                        #if Aliquots.objects.filter(id_genealogy = newG).count() == 0:
                                        a = Aliquots( id_explant = ed, idType = TissueType.objects.get(abbreviation = typeAl), id_genealogy = newG )
                                        a.save()
                                        #esempio della lista: BRC0027NBXA01001LIVVT01|VT|87|B6|1,BRC0027NBXA01001LNGFF01|FF|0|0|1,BRC0035TRXA01001LIVVT01|VT|87|C4|3,BRC0035TRXA01001LNGVT01|VT|87|D4|4
                                        newA = newG + '|' +  typeA + '|' + barcodeP  + '|' + str(pos) + '|'  + str(quant)
                                        if aliquotList == "":
                                            aliquotList = newA
                                        else:
                                            aliquotList += ',' + newA
                        transaction.commit()
                    except Exception, e:
                        print 'XMM VIEW explant.explantSubmit: 3) ' +  str(e)
                        #se si sono verificati errori, lo comunico alla biobanca che effettua il rollback
                        transaction.rollback()
                        url = Urls.objects.get(default = '1').url + "/explants/end/"
                        #transaction.commit()
                        values = {'aliquots' : explantsString, 'user': name, 'response':'err'}
                        res = ""
                        data = urllib.urlencode(values)
                        req = urllib2.Request(url, data=data, headers={"workingGroups" : get_WG_string()})
                        u = urllib2.urlopen(req)
                        #u = urllib2.urlopen(url, data)
                        request.session['message'] = "Something gone wrong."
                        return HttpResponseRedirect(reverse("xenopatients.views.index"))   
                    #se invece e' andato tutto ok, lo dico alla biobanca e preparo il report
                    try: 
                        url = Urls.objects.get(default = '1').url + "/explants/end/"
                        transaction.commit()
                    except Exception, e:
                        print 'XMM VIEW explant.explantSubmit: 4) ' +  str(e)
                        transaction.rollback()
                    values = {'user': name, 'response':'ok'}
                    res = ""
                    try:
                        data = urllib.urlencode(values)
                        req = urllib2.Request(url, data=data, headers={"workingGroups" : get_WG_string()})
                        u = urllib2.urlopen(req)
                        #u = urllib2.urlopen(url, data)
                    except Exception, e:
                        print 'XMM VIEW explant.explantSubmit: 5) ' +  str(e)
                    list_report = []
                    #preparo il report
                    #esempio della lista: BRC0027NBXA01001LIVVT01|VT|87|B6|1,BRC0027NBXA01001LNGFF01|FF|0|0|1,BRC0035TRXA01001LIVVT01|VT|87|C4|3,BRC0035TRXA01001LNGVT01|VT|87|D4|4
                    data = string.split(aliquotList, ',')
                    for d in data:
                        aliquot = string.split(d, '|')
                        parameters = []
                        for a in aliquot:
                            if len(a):
                                parameters.append(str(a))
                        list_report.append( tableReport( parameters ) ) #parameters[0], parameters[2], parameters[3], parameters[4])
                    request.session['list_report'] = list_report
                    request.session['list_report2'] = list_report2
                    return HttpResponseRedirect(reverse("xenopatients.explant.explantReport"))
    except Exception,e:
        print 'XMM VIEW explant.explantSubmit: 6) ' +  str(e)
        return HttpResponse()

#crea il report html degli espianti
@laslogin_required
@login_required
@permission_decorator('xenopatients.can_view_XMM_explant_xenografts')
def explantReport(request):
    print 'XMM VIEW: start explant.explantReport'
    name = request.user.username
    list_report = request.session['list_report']
    list_report2 = request.session['list_report2']

    email = LASEmail (functionality=get_functionality(), wgString=get_WG_string())   
    msgItem=dict()
    for row in list_report: 
        listItem=row.split("<td align='center'>")
        listItem.pop(0)
        item=listItem[0].split('</td>')[0]+'\t'+listItem[1].split('</td>')[0]+'\t'+listItem[2].split('</td>')[0]+'\t'+listItem[3].split('</td>')[0]+'\t'+listItem[4].split('</td>')[0]+'\t'
        genid=listItem[0].split('</td>')[0]
        bm=BioMice.objects.filter(id_genealogy__startswith=str(genid[:-9]))
        wgMouse = BioMice_WG.objects.filter(biomice__in=bm).values_list('WG__name', flat=True)
        for wgName in wgMouse:
            if wgName not in msgItem:
                msgItem[wgName]=list()
                msgItem[wgName].append('Genealogy ID\tType\tPlate\tPosition\t# of pieces\n')
            msgItem[wgName].append(item)
    for wgName,msg in msgItem.items():
        email.addMsg([wgName], msg)
        email.addRoleEmail([wgName], 'Executor', [request.user.username])

    if request.session.get('restoreE'):
        del request.session['restoreE']

    try:
        email.send()
    except Exception,e:
        print 'XMM VIEW explant.explantReport: 1) ' +  str(e)        
        pass

    return render_to_response('explants/report.html', {'name':name, 'list_report':list_report, 'list_report2':list_report2 }, RequestContext(request)) 

#questa semplice view serve a ridirezionare la pagina dopo aver cliccato su 'continue' nella pagina con il report
@laslogin_required
@login_required
@permission_decorator('xenopatients.can_view_XMM_explant_xenografts')
def explantContinue(request):
    print 'XMM VIEW: start explant.explantContinue'
    return HttpResponseRedirect(reverse("xenopatients.explant.startExplant"))

#questa semplice view serve a ridirezionare la pagina dopo aver cliccato su 'continue' nella pagina che notifica l'errore
@laslogin_required
@login_required
@permission_decorator('xenopatients.can_view_XMM_explant_xenografts')
def explantContinueErr(request):
    print 'XMM VIEW: start explant.explantContinueErr'
    name = request.user.username
    return render_to_response('explants/continue.html', {'name':name}) 
