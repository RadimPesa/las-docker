from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import auth
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import loader, Context, RequestContext
from LASAuth.decorators import laslogin_required
from django.conf import settings
from global_request_middleware import *
from xenopatients.models import *
from api.handlers import newGenIDGraph
from django.db.models import get_model
import xlrd, tempfile, datetime, json
from django.db import transaction
from django.db.models import Max
from apisecurity.decorators import *
import os
import math

@laslogin_required
@login_required
@permission_decorator('xenopatients.can_view_XMM_batch')
def start(request):
    print 'XMM VIEW: start batch.start'
    typeAction = [ {'action': 'miceload', 'name':'Register mice', 'template': 'batch/mice_loading.txt'}, {'action': 'impl', 'name':'Implant Xenografts', 'template': 'batch/impl.txt'},  {'action': 'expl', 'name':'Explant Xenografts', 'template': 'batch/expl.txt'}, {'action': 'qual', 'name':'Observation', 'template': 'batch/qual.txt'}, {'action': 'quant', 'name':'Tumor Volume', 'template': 'batch/quant.txt'}, {'action': 'explOpen', 'name':'Add aliquots to explant', 'template': 'batch/explOpen.txt'} ]

    #{'miceload':'Mice Loading','qual':'Qualitative Measurements','quant':'Quantitative Measurements', 'impl':'Implant', 'expl':'Explant'}
    print typeAction
    return render_to_response('batch/start.html', {'typeAction':typeAction},RequestContext(request))
    
    
@laslogin_required
@login_required
@permission_decorator('xenopatients.can_view_XMM_batch')
def read(request):
    print 'XMM VIEW: start batch.read'
    data = []
    action = ''
    try:
        if request.method == 'POST':
            if 'aggiungi_file' in request.POST:
                action = request.POST['action']
                f = request.FILES['file']
                if f.name.split('.')[1] == 'xls' or f.name.split('.')[1] == 'xlsx':
                    #sudo apt-get install python-xlrd
                    try:
                        fd, tmp = tempfile.mkstemp()
                        with os.fdopen(fd, 'w') as out:
                            out.write(f.read())
                        wb = xlrd.open_workbook(tmp)
                        # do what you have to do
                        print wb.sheet_names()
                        worksheet = wb.sheet_by_name(wb.sheet_names()[0])
                        for i in range (0,worksheet.nrows):
	                        print worksheet.row_values(i)
	                        data.append(worksheet.row_values(i))
                    		#for j in range(0,worksheet.ncols):
			                #    sh.write(i,j,worksheet.row_values(i)[j])
                    finally:
                        os.unlink(tmp)  # delete the temp file no matter what
                else:
                    lines = f.readlines()
                    for i in range(0,len(lines)):
                        print lines[i].split('\t')
                        #c = lines[i].strip()
                        data.append(lines[i].strip().split('\t'))
    except Exception, e:
        print e
    print data
    return render_to_response('batch/read.html', {'data':json.dumps(data), 'action':action} ,RequestContext(request))
    
@laslogin_required
@login_required
@transaction.commit_manually
@permission_decorator('xenopatients.can_view_XMM_batch')
def save(request):
    print 'XMM VIEW: start batch.save'
    try:
        if request.method == 'POST':
            action = request.POST['action']
            records = json.loads(request.POST['data'])
            print action
            print records
            if action == 'miceload':
                translator = {"Arrival date": 'arrival_date', "Barcode": 'barcode', "Gender": 'gender'}
                for record in records:
                    m = Mice()
                    for t in translator:
                        setattr(m, translator[t], record[t])
                    setattr(m, 'id_source', Source.objects.get(name = record['Source']))
                    setattr(m, 'id_status', Status.objects.get(name = record['Status']))
                    setattr(m, 'id_mouse_strain', Mouse_strain.objects.get(mouse_type_name = record['Mouse strain']))
                    setattr(m, 'available_date', datetime.date.today())
                    print 'arrival',record['Arrival date']
                    arr_date=record['Arrival date'].split('-')
                    setattr(m, 'birth_date', datetime.date(int(arr_date[0]),int(arr_date[1]),int(arr_date[2])) - datetime.timedelta(weeks = int(record['Age in weeks'])) )
                    m.save()
            elif action == 'qual':
                for record in records:
                    pm = Mice.objects.get(barcode = record['Barcode'])
                    biomouse = Implant_details.objects.get( site = Site.objects.get(shortName = record['Site'] ), id_mouse__in  = BioMice.objects.filter(phys_mouse_id = pm) ).id_mouse
                    operator=User.objects.get(username=record['Operator'])
                    mserie = Measurements_series(id_operator = operator, id_type = Type_of_measure.objects.get(description = 'qualitative'), date = record['Date'])
                    mserie.save()
                    id_series = mserie
                    id_value = Qualitative_values.objects.get(value = record['Value'])
                    if record['Weight'] != "" and record['Weight'] is not None:
                        weight = float(record['Weight'])
                    else:
                        weight = None
                    q = Qualitative_measure(id_mouse=biomouse, id_value=id_value, weight=weight, id_series=id_series )
                    q.save()
            elif action == 'quant':
                for record in records:
                    pm = Mice.objects.get(barcode = record['Barcode'])
                    biomouse = Implant_details.objects.get( site = Site.objects.get(shortName = record['Site'] ), id_mouse__in  = BioMice.objects.filter(phys_mouse_id = pm) ).id_mouse
                    operator=User.objects.get(username=record['Operator'])
                    mserie = Measurements_series(id_operator = operator, id_type = Type_of_measure.objects.get(description = 'quantitative'), date = record['Date'])
                    mserie.save()
                    id_series = mserie

                    volume = 0
                    if float(record['X Measurement']) > float(record['Y Measurement']):
                        volume = (float(record['Y Measurement'])/2) * (float(record['Y Measurement'])/2) * (float(record['X Measurement'])/2) * 4/3 * math.pi
                    else:
                        volume = (float(record['X Measurement'])/2) * (float(record['X Measurement'])/2) * (float(record['Y Measurement'])/2) * 4/3 * math.pi
                    volume=round(volume,3)
                    if record['Weight'] != "" and record['Weight'] is not None:
                        weight = float(record['Weight'])
                    else:
                        weight = None
                    q = Quantitative_measure(id_mouse=biomouse, x_measurement=float(record['X Measurement']), y_measurement=float(record['Y Measurement']), volume=volume, weight=weight, id_series=id_series )
                    q.save()
            elif action == 'impl':
                print 'impl'
                toBiobank = []
                for record in records:
                    #check su quantita' --> invio dati a banca
                    toBiobank.append({ 'barcode': record['Container'] , 'pos': record['Position'] })
                    #send to biobank
                values = {'listBarcode' : json.dumps(toBiobank) }
                res = ""
                #invio i dati alla biobanca
                #res = {'response': 'ok', 'data': {'01|C5': {'qty':6, 'genID':'CRC0400LMX0A05031SCR000000'} , '01|C6': {'qty':6, 'genID':'CRC0525LMX0A04001SCR000000'}  } }
                try:
                    url = UrlStorage.objects.get(default = '1').address + "/api/info/aliquot/"
                    print url
                    data = urllib.urlencode(values)
                    req = urllib2.Request(url, data=data, headers={"workingGroups" : get_WG_string()})
                    u = urllib2.urlopen(req)
                    r =  u.read()
                    print r
                    print json.loads(r)
                    print json.loads(json.loads(r))
                    res = json.loads(json.loads(r))
                    
                    if res['res'] == 'ok':
                        print 'ok'
                    else:
                        print '1'
                        err = res['data']['err']
                        print '2'
                        c = res['data']['barcode']
                        if len( c.split('|') ) > 1:
                            container = "Plate " + c.split('|')[0] + " - position " + c.split('|')[1]
                        else:
                            container = "Plate " + c
                        if err == 'notexists':
                            transaction.rollback()
                            return HttpResponse(container + "-> doesn't exist.")
                        elif err == 'empty':
                            transaction.rollback()
                            return HttpResponse(container + "-> no aliquots for implant.")
                        elif err == 'type':
                            transaction.rollback()
                            return HttpResponse(container + "-> the aliquot in this container is not vital.")
                except Exception, e: 
                    print 'XMM VIEW batch.save: 1) ' +  str(e)
                    raise Exception("Something gone wrong while linking with the BioBank in the initialization phase.")
                #creazione genID
                dictG = {}
                forUpdateBiobank = {}
                for record in records:
                    newG = ''
                    container = record['Container']
                    pos = record['Position']
                    if pos != '-':
                        container += '|' + pos
                    print res
                    oldG = res['data'][container]['genID']
                    barcode = record['Barcode']
                    site = record["Site"]
                    done = False
                    if record['Container'] not in forUpdateBiobank:
                        forUpdateBiobank[record['Container']] = {}
                        forUpdateBiobank[record['Container']][record['Position']] = {}
                    if record['Position'] not in forUpdateBiobank[record['Container']]:
                        forUpdateBiobank[record['Container']][record['Position']] = {}

                    forUpdateBiobank[record['Container']][record['Position']]['aliquot'] = oldG
                    #check su db per impianti su quel sito
                    print '-----------------------------------------'
                    mouse = Mice.objects.get(barcode = barcode)
                    biomice = BioMice.objects.filter(phys_mouse_id = mouse)
                    print mouse
                    print biomice
                    for biomouse in biomice:
                        print biomouse
                        print site
                        if len(Implant_details.objects.filter(id_mouse = biomouse, site = Site.objects.get(shortName = site))) > 0:
                            print 'return1'
                            raise Exception('Mouse with barcode ' + barcode + ' has a previous implant on this site.')
                    #check su db per impianti precedenti con quella aliquota
                    aliquots = Aliquots.objects.filter(id_genealogy__startswith = GenealogyID(oldG).getLongPrefix())
                    print GenealogyID(oldG).getLongPrefix()
                    if len(aliquots) > 0:
                        for aliquot in aliquots:
                            for biomouse in biomice:
                                implants = Implant_details.objects.filter(id_mouse = biomouse, aliquots_id = aliquot)
                                if len(implants) > 0:
                                    if res['data'][container]['qty'] == 0:
                                        raise Exception("not enough pieces in tube of aliquot " + oldG)
                                    if res['data'][container]['qty'] > 0:
                                        print 'case a'
                                        res['data'][container]['qty'] -= 1
                                        
                                    forUpdateBiobank[record['Container']][record['Position']]['actualQ'] = res['data'][container]['qty']
                                    implant = implants[0]
                                    genIDObject = GenealogyID(biomouse.id_genealogy)
                                    dataDict = {'tissueType':site} #, 'archiveMaterial2': '00', 'aliqExtraction2':'00', '2derivation': '0', '2derivationGen':'00'}
                                    genIDObject.updateGenID(dataDict)
                                    print 'return1b'
                                    newG = genIDObject.getGenID()
                                    dictG[newG] = {}
                                    dictG[newG]['barcode'] = barcode
                                    dictG[newG]['genID'] = oldG
                                    done = True
                                    break
                    #check su sessione
                    if not done:
                        for genID in dictG:
                            print dictG[genID]['barcode'], barcode
                            if dictG[genID]['barcode'] == barcode:
                                print '##########################', GenealogyID(dictG[genID]['genID']).getLongPrefix(), GenealogyID(oldG).getLongPrefix()
                                if GenealogyID(dictG[genID]['genID']).getLongPrefix() == GenealogyID(oldG).getLongPrefix():
                                    if res['data'][container]['qty'] == 0:
                                        raise Exception("not enough pieces in tube of aliquot " + oldG)                                    
                                    if res['data'][container]['qty'] > 0:
                                        print 'case b'
                                        res['data'][container]['qty'] -= 1
                                    forUpdateBiobank[record['Container']][record['Position']]['actualQ'] = res['data'][container]['qty']
                                    genIDObject = GenealogyID(genID)
                                    dataDict = {'tissueType':site} #, 'archiveMaterial2': '00', 'aliqExtraction2':'00', '2derivation': '0', '2derivationGen':'00'}
                                    genIDObject.updateGenID(dataDict)
                                    print 'return2', genIDObject.getGenID()
                                    newG = genIDObject.getGenID()
                                    dictG[newG] = {}
                                    dictG[newG]['barcode'] = barcode
                                    dictG[newG]['genID'] = oldG
                                    done = True
                                    break
                    if not done:
                        listG = json.dumps(dictG)
                        if res['data'][container]['qty'] == 0:
                            raise Exception("not enough pieces in tube of aliquot " + oldG)
                        if res['data'][container]['qty'] > 0:
                            print 'case c'
                            res['data'][container]['qty'] -= 1
                        forUpdateBiobank[record['Container']][record['Position']]['actualQ'] = res['data'][container]['qty']
                        g = newGenIDGraph(oldG,listG,site)
                        newG = g['genID']
                        dictG[newG] = {}
                        dictG[newG]['barcode'] = barcode
                        dictG[newG]['genID'] = oldG
                            
            
                    print '##############################'
                    print 'oldG', oldG, 'barcode', barcode, 'site', site, 'newG', newG
            
                    #salvataggio serie, implant_details e aliquots
                    print '1'
                    s = Series(id_operator = request.user, id_type = Type_of_serie.objects.get(description='implant'), date = record['Date'])
                    s.save()
                    print '2'
                    
                    try:
                        al = Aliquots.objects.get(id_genealogy = oldG)
                    except:
                        al = Aliquots(id_genealogy = oldG) 
                        al.save()
                    print '3'
                    
                    if len(Groups.objects.filter(name = record['Experimental group'])) == 1:
                        g = Groups.objects.get(name = record['Experimental group'])
                    else:
                        g = Groups(name = record['Experimental group'], creationDate = datetime.datetime.now() )
                        g.save()
                    print '4'
                    bm = BioMice(id_group = g, id_genealogy = newG, phys_mouse_id = Mice.objects.get(barcode = barcode))
                    bm.save()
                    print '5'          
                    i = Implant_details(id_mouse = bm, id_series = s, aliquots_id = al, bad_quality_flag = False, site = Site.objects.get(shortName = site))
                    i.save()
                    print '6'
                    physm = Mice.objects.get(barcode = barcode)
                    physm.id_status = Status.objects.get(name='implanted')
                    physm.save()
                #comunicazione a biobanca
                print forUpdateBiobank
                try:
                    url = Urls.objects.get(default = '1').url + "/api/aliquot/canc/"
                    data = urllib.urlencode({'implants':json.dumps(forUpdateBiobank)})
                    req = urllib2.Request(url, data=data, headers={"workingGroups" : get_WG_string()})
                    u = urllib2.urlopen(req)
                    
                    res =  json.loads(u.read())
                    print res
                    if res['data'] != 'ok':
                        raise Exception("Something gone wrong in the Biobank while saving.")
                except Exception, e: 
                    print 'XMM VIEW batch.save: 1) ' +  str(e)
                    raise Exception("Something gone wrong while linking with the BioBank in saving phase.")
            elif action == 'expl':
                print 'expl'
                explants = {}
                forbidden_status = ['explanted', 'experimental', 'breeding']
                physMicelist = []
                for record in records:
                    barcode = record['Barcode mouse']
                    m = Mice.objects.get(barcode = barcode) 
                    physMicelist.append(m)
                    bm = Implant_details.objects.get(id_mouse__in = BioMice.objects.filter(phys_mouse_id = m), site = Site.objects.get(shortName = record['Site'])).id_mouse
                    print forbidden_status, m.id_status.name in forbidden_status
                    if m.id_status.name in forbidden_status:
                        print m.id_status.id, m
                        raise Exception("The mouse " + bm.id_genealogy + " is " + m.id_status.name + " and cannot be explanted.")
                    mouseGenID = bm.id_genealogy
                    tissue = record['Tissue type']
                    typeA = record['Plate type']
                    barcodeP = record['Barcode plate']
                    print '------------'
                    classOld = GenealogyID(bm.id_genealogy)
                    counter = '01'
                    classOld.updateGenID({'tissueType':tissue, 'archiveMaterial2': typeA, 'aliqExtraction2':str(counter), '2derivationGen':'00'})
                    done = False
                    while not done:
                        if len(Aliquots.objects.filter(id_genealogy = classOld.getGenID())) == 0:
                            done = True
                        else:
                            counter = int(counter)  + 1
                            if len(str(counter)) == 1:
                                counter = '0' + str(counter)
                            classOld.updateGenID({'tissueType':tissue, 'archiveMaterial2': typeA, 'aliqExtraction2':str(counter), '2derivationGen':'00'})
                    newG = classOld.getGenID()
                    print 'newGen',newG
                
                    s = Series(id_operator = request.user, id_type = Type_of_serie.objects.get(description='explant'), date = record['Date'])
                    s.save()
                    
                    m.death_date = record['Date']
                    m.save()
                    
                    e = Explant_details(id_series = s, id_mouse = bm)
                    e.save()
                    
                    a = Aliquots(id_genealogy = newG, id_explant = e, idType = TissueType.objects.get(abbreviation=record['Tissue type']))
                    a.save()
                    
                    pe = Programmed_explant.objects.filter(id_mouse = bm, done = '0')
                    print 'pe',pe
                    for p in pe:
                        p.done = '1'
                        p.save()
                    
                    #costruire struttura dati da mandare alla biobanca
                    if typeA not in explants:
                        explants[typeA] = {}
                        explants[typeA][mouseGenID] = {}
                        explants[typeA][mouseGenID][barcodeP] = []
                    elif mouseGenID not in explants[typeA]:
                        explants[typeA][mouseGenID] = {}
                        explants[typeA][mouseGenID][barcodeP] = []
                    elif barcodeP not in explants[typeA][mouseGenID]:
                        explants[typeA][mouseGenID][barcodeP] = []
                        
                    explants[typeA][mouseGenID][barcodeP].append({'genID':newG, 'pos': record['Position'], 'qty': record['Quantity'], 'tissueType': tissue,'date_expl':record['Date']})
                    
                    print 'explants',explants
                
                for m in physMicelist:
                    m.id_status = Status.objects.get(name = 'explanted')
                    m.save()

                url = Urls.objects.get(default = '1').url + "/api/save/batchexplant/"
                print url
                values = {'explants' : json.dumps(explants), 'date': record['Date'], 'operator': request.user.username}
                try:
                    data = urllib.urlencode(values)
                    req = urllib2.Request(url, data=data, headers={"workingGroups" : get_WG_string()})
                    u = urllib2.urlopen(req)
                    #u = urllib2.urlopen(url, data)
                    res =  json.loads(u.read())
                    print 'res',res
                    if res['res'] != 'ok':
                        raise Exception(res['data'])
                except Exception, e:
                    print e
                    raise Exception(e)
            elif action == 'explOpen':
                print 'explOpen'
                explants = {}
                ok_status = ['explanted']
                physMicelist = []
                for record in records:
                    barcode = record['Barcode mouse']
                    m = Mice.objects.get(barcode = barcode) 
                    physMicelist.append(m)
                    bm = Implant_details.objects.get(id_mouse__in = BioMice.objects.filter(phys_mouse_id = m), site = Site.objects.get(shortName = record['Site'])).id_mouse
                    if m.id_status.name not in ok_status:
                        print m.id_status.id, m
                        raise Exception("The mouse " + bm.id_genealogy + " is " + m.id_status.name + " and cannot be explanted.")
                    mouseGenID = bm.id_genealogy
                    tissue = record['Tissue type']
                    typeA = record['Plate type']
                    barcodeP = record['Barcode plate']
                    print '------------'
                    classOld = GenealogyID(bm.id_genealogy)
                    counter = '01'
                    classOld.updateGenID({'tissueType':tissue, 'archiveMaterial2': typeA, 'aliqExtraction2':str(counter), '2derivationGen':'00'})
                    done = False
                    while not done:
                        if len(Aliquots.objects.filter(id_genealogy = classOld.getGenID())) == 0:
                            done = True
                        else:
                            counter = int(counter)  + 1
                            if len(str(counter)) == 1:
                                counter = '0' + str(counter)
                            classOld.updateGenID({'tissueType':tissue, 'archiveMaterial2': typeA, 'aliqExtraction2':str(counter), '2derivationGen':'00'})
                    newG = classOld.getGenID()
                    print 'newG',newG                
                    
                    try:
                        s = Series.objects.filter(id_operator = User.objects.get(username=record['User']), id_type = Type_of_serie.objects.get(description='explant'), date = record['Date'])
                        print 'serie',s, bm.id
                        e = Explant_details.objects.get(id_series__in = s, id_mouse = bm)
                        print 'e.id',e.id
                    except Exception, e:
                        print e
                        raise Exception("The mouse " + bm.id_genealogy + " is " + m.id_status.name + " and cannot be explanted.")
                                        
                    a = Aliquots(id_genealogy = newG, id_explant = e, idType = TissueType.objects.get(abbreviation=record['Tissue type']))
                    a.save()

                    #costruire struttura dati da mandare alla biobanca
                    if typeA not in explants:
                        explants[typeA] = {}
                        explants[typeA][mouseGenID] = {}
                        explants[typeA][mouseGenID][barcodeP] = []
                    elif mouseGenID not in explants[typeA]:
                        explants[typeA][mouseGenID] = {}
                        explants[typeA][mouseGenID][barcodeP] = []
                    elif barcodeP not in explants[typeA][mouseGenID]:
                        explants[typeA][mouseGenID][barcodeP] = []
                        
                    explants[typeA][mouseGenID][barcodeP].append({'genID':newG, 'pos': record['Position'], 'qty': record['Quantity'], 'tissueType': tissue,'date_expl':record['Date']})
                    
                    print 'explants',explants
                                
                url = Urls.objects.get(default = '1').url + "/api/save/batchexplant/"
                print url
                values = {'explants' : json.dumps(explants), 'date': record['Date'], 'operator': request.user.username}
                try:
                    data = urllib.urlencode(values)
                    req = urllib2.Request(url, data=data, headers={"workingGroups" : get_WG_string()})
                    u = urllib2.urlopen(req)
                    #u = urllib2.urlopen(url, data)
                    res =  json.loads(u.read())
                    print 'res',res
                    if res['res'] != 'ok':
                        raise Exception(res['data'])
                except Exception, e:
                    print e
                    raise Exception(e)
                
        transaction.commit()
        return HttpResponse("ok")
    except Exception, e:
        print 'XMM VIEW batch.save: 2) ' +  str(e)
        transaction.rollback()
        return HttpResponse(str(e))
