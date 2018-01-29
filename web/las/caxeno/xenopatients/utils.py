from pprint import pprint
from string import maketrans
from xenopatients import markup
from xenopatients.genealogyID import *
from django.db import transaction
import os, urllib, urllib2, cStringIO, string, json
from xenopatients.models import *
from xenopatients.views import *
#from datetime import date, datetime
from django.http import HttpResponse, HttpResponseRedirect
import os, cStringIO, csv
import requests
import settings

#elimina i doppioni da una lista
def uniq(input):
    print 'XMM VIEW: start utils.uniq'
    output = []
    for x in input:
        if x not in output:
            output.append(x)
    return output

#semplice check sulla lunghezza della stringa in input
def isGenID(identifier):
    print 'XMM VIEW: start utils.isGenID'
    if len(identifier) == 26:
        return True
    return False


#per creare il CSV
def CSVMaker(request, nameSession, nameFile, columns):
    print 'XMM VIEW: start utils.CSVMaker'
    csvString = ''
    if request.session.get(nameSession):
        list_report = request.session.get(nameSession)
    else:
        #return HttpResponseRedirect(reverse("xenopatients.views.index"))
        list_report = []
    response = HttpResponse(mimetype='text/csv')
    response['Content-Disposition'] = 'attachment; filename=' + nameFile
    writer = csv.writer(response, delimiter='\t')
    if len(columns) > 0:
        writer.writerow(columns)
    if nameSession == 'table':
        #caso particolare di csv (tabella con le misure storiche nel check)
        csvString = list_report.replace('<table id="measureLong">','').replace('<thead><tr><th></th>','\t').replace('<br>',' - ').replace('</td>','\t').replace('<tr>','').replace('</tr>','\n').replace('</thead>','').replace('<tbody>','').replace('</tbody>','').replace('</thead>','').replace('<th>','').replace('</th>','\t').replace('<td>','').replace('</table>','').replace('<tr class="minigroup0">','').replace('<tr class="minigroup1">','').replace('<tr class="minigroup2">','').replace('<tr class="minigroup3">','').replace('<tr class="minigroup4">','').replace('<tr class="minigroup5">','').replace('<tr class="minigroup6">','').replace('<tr class="minigroup7">','').replace('<tr class="minigroup8">','').replace('<tr class="minigroup9">','').replace('<tr class="minigroup10">','').replace('<tr class="waste">','')
    elif nameSession == 'graph':
        #caso particolare di csv (esportazione grafico del check)
        graph = request.session.get('graph')
        groups = request.session['groups']
        dateList = request.session['dateList']
        dateList =  sorted(dateList)
        for d in dateList:
            csvString += '\t' + d
        csvString += '\n'
        for g in groups:
            csvString += g
            for d in dateList:
                try:
                    if graph[d].has_key(g):
                        csvString += '\t' + str(graph[d][g]).replace('.',',')
                    else:
                        csvString += '\t-'
                except:
                    csvString += '\t' + str(0)
                    pass
            csvString += '\n'
    else:
        for i in list_report:
            csvString += i.replace('<td align="center">','').replace('<br>','').replace('</td>','\t').replace('<tr>','').replace('</tr>','\n')
    csvString = csvString[:-1]
    for l in csvString.split('\n'):
        writer.writerow(l.split('\t'))
    return response

#controlla se un trattamento comporta un espianto dopo lo stop; se si, lo programma
def forceExpl(m,treatment):
    print 'XMM VIEW: start utils.forceExpl'
    if treatment.forces_explant:
        m.id_status = Status.objects.get(name = "ready for explant")
        try: #se esiste gia', la sovrascrivo
            pe = Programmed_explant.objects.get(id_mouse= m.id, done=0) #qui va nella except se non esiste un programmed_explant non fatto per quel topo
            pe.id_scope = Scope_details.objects.get(description = "Archive (end of experiment)")
            pe.scopeNotes = scopeNotes = "end of acute arm"
        except: #altrimenti la creo
            pe = Programmed_explant(id_scope = Scope_details.objects.get(description = "Archive (end of experiment)"), id_mouse = m, scopeNotes = "end of acute arm")
        m.save()
        pe.save()
    return

#calcola il nuovo lineage per l genID degli impianti
def newLineage(n):
    print 'XMM VIEW: start utils.newLineage'
    try:
        n = n + 1
        #print n
        first = n / 36
        print 'first',first
        second = n % 36
        print 'second',second
        base = 64
        if first > 26:
            first = first - 26
        elif first > 0:
            first = chr(base + first)
        else:
            first = 0
        print 'first dopo',first
        if second > 26:
            second = second - 26
        elif second > 0:
            second = chr(base + second)
        else:
            second = 0
        #print str(first) + str(second)
        return str(first) + str(second)
    except Exception, e:
        print e
        pass
    return

def translateLineage(lineage):
    print 'XMM VIEW: start utils.translateLineage'
    try:
        print 'lineage',lineage
        result = 0
        if lineage[0].isdigit():
            first = int(lineage[0])
            print 'first lin',first
            if first:
                result += (26 + first) * 36
                print 'res1',result
        else:
            result += (ord(lineage[0]) - 64 )  * 36
            print 'res2',result
        if lineage[1].isdigit():
            second = int(lineage[1])
            print 'sec',second
            if second:
                result += 26 + second
                print 'res3',result
        else:
            result += ord(lineage[1]) - 64
            print 'res3',result
        print 'res finale',result
        return result
    except Exception, e:
        print e
        pass
    return

#per calcolare il lineage massimo all'interno di una lista
def maxLineage(listlineage):
    print 'XMM VIEW: start utils.maxLineage'
    print 'lista',listlineage
    #nel lineage la prima cifra e' 0 poi A fino a Z e poi da 1 a 9, mentre la seconda cifra va da A a Z e poi da 1 a 9
    dictdigit1={}
    dictdigit2={}
    #chiave il valore originale e valore il mio valore arbitrario
    dictval1={}
    #chiave il mio valore arbitrario e valore il valore originale 
    dictval2={}
    j=65
    dictdigit1['0']=0    
    for i in range (1,27):
        dictdigit1[chr(j+i-1)]=i        
    for i in range (27,36):
        dictdigit1[str(i-26)]=i
    
    for i in range (0,26):
        dictdigit2[chr(j+i)]=i
    for i in range (1,10):
        dictdigit2[str(i)]=25+i
    dictdigit2['0']=0
    print 'dictdig1',dictdigit1
    print 'dictdig2',dictdigit2
    for val in listlineage:
        val=str(val)
        if len(val)==1:
            val='0'+val
        firstdig=dictdigit1[val[0]]
        seconddig=dictdigit2[val[1]]
        tot=firstdig*36+seconddig
        dictval1[val]=tot
        dictval2[tot]=val
    print 'dictval1',dictval1
    max1=max(dictval1.values())
    print 'max1',max1
    return max1+1
    '''val2=dictval2[max1]
    try:
        return int(val2)
    except:
        return val2'''
    

def getHTML(implants, protocol, n, dateT):
    print 'XMM VIEW: start utils.getHTML'
    listG = []
    i = 0
    implants = json.loads(implants)
    for barcodeP in implants:
        for key in implants[barcodeP]:
            if key != 'emptyFlag':
                for m in implants[barcodeP][key]['listMice']:
                    listG.append(barcode_genID(barcode = m['barcode'], genID = m['newGenID']))
    dictG, nGroups, nMice = countGenID(listG, n)
    x = int(nMice)
    y = int(nGroups)
    #inizializzo la tabella. Qui verra' scritto il codice HTML per creare le singole celle della tabella visualizzata dall'utente
    codeList = []
    i, j = 0, 0
    if protocol != "":
        p = Protocols.objects.get(pk = protocol)
        protocol = p.name
    while i <= int(y):
        codeList.append([])
        j = 0
        while j < int(x):
            codeList[i].append('<td></td>')
            j = j + 1
        i = i + 1
    i = 0
    for k in dictG.keys():
        if k != "" and dateT != "" and protocol != "":
            name = str(k) + '.' + str(dateT) + '.' + str(protocol)
            codeList[0][i] = groupCellCode( name, i)
        elif k != "" and protocol != "":
            name = str(k) +  '.' + str(protocol)
            codeList[0][i] = groupCellCode( name, i)
        elif k != "" and dateT != "":
            name = str(k) + '.' + str(dateT)
            codeList[0][i] = groupCellCode( name, i)

        elif k != "":
            name = str(k)
            codeList[0][i] = groupCellCode( name, i)
        j = 1
        for v in dictG[k]:
            codeList[j][i] = "<td><div class='drag'>" + str(v.genID) + "</div></td>"
            j = j + 1
        i = i + 1
    string = "<table id='table1'>"
    i = 0
    for code in codeList:
        string += '<tr>'
        for c in code:
            if c != "":
                string += str(c)
        string += '</tr>'
        i = i + 1
    string += "</table>"     
    return string

def groupCellCode(name, i):
    print 'XMM VIEW: start utils.groupCellCode'
    count = 0
    names = Groups.objects.filter(name__istartswith = name)
    data = []
    if len(names) > 0:
        count =  len(names)
    name = name + '.' + str(count)
    return "<th class='mark'><input class='edit' id='"+str(i)+"'type='button' value='Edit' style='text-align:right;'/> <input id='text"+str(i)+"'type='text' onpaste='return false;' onkeypress='validate(event)' size='"+str(len(name))+"' disabled='true' value='" + name + "'/></th>"

class barcode_genID:
    def __init__(self, barcode, genID):
        self.barcode = barcode.upper()
        self.genID = genID
    def toStr(self):
        return self.barcode + ' ' + self.genID

#restituisce un dizionario contenente i barcode dei topi impiantati suddivisi per genID (le prime x lettere); inoltre, restituisce anche il numero di raggruppamenti fatti e il numero di topi nel dict
#contiene anche il nuovo genID completo di ogni topo
def countGenID(listG, n):
    print 'XMM VIEW: start utils.countGenID'
    dictG = {}
    for g in listG: 
        genID = g.genID[0:int(n)]
        t = list()
        if dictG.has_key(genID):
            oldValue = dictG[genID]
            for o in oldValue:
                t.append(o)
            t.append(g)
            dictG[genID] = t
        else:
            t.append(g)
            dictG[genID] = t
    k = 0
    for vL in dictG.values():
        for v in vL:
            k = k + 1
    return dictG, k, len(dictG.keys())

#annullo un espianto programmato su un topo
def cancelProgrammedExpl(m):    
    print 'XMM VIEW: start utils.cancelProgrammedExpl'
    try:
        pe = Programmed_explant.objects.get(id_mouse= m, done=0)
        pe.delete()
    except:
        pass
    return
    
#termino un trattamento su un topo
def stopTreat(m, timestamp):    
    print 'XMM VIEW: start utils.stopTreat'
    try:
        mhas = Mice_has_arms.objects.filter(id_mouse= m, end_date__isnull = True)
        for mha in mhas:
            mha.end_date = timestamp
            mha.save()
    except:
        pass
    return

#funzione che converte la stringa con i parametri, ricevuta da ajax, in un lista di parametri
def createList(data):
    print 'XMM VIEW: start utils.createList'
    parameters=[]
    tuplas = string.split(data, '&')
    for tupla in tuplas:
       values = string.split(tupla, '|')
       for v in values:
          parameters.append(string.strip(str(v)))
    return parameters

def tableReport(infoList):
    print 'XMM VIEW: start utils.tableReport'
    if len(infoList):
        tr = "<tr>"
        for info in infoList:
            tr += "<td align='center'>" + str(info) + "</td>"
        return tr +  "</tr>"
    else:
        return ""

#sostituisce gli underscore con gli spazi e mette la prima lettera maiuscola e anche tutte le lettere successive ad un underscore
def convertString (s):
    print 'XMM VIEW: start utils.convertString'
    s = s.title()
    s = s.replace('_',' ')
    return s

#restituisce il codice HTML per visualizzare l'elenco di tutti gli arm del db, anche quelli senza protocollo assegnato
def listArmHtml():
    print 'XMM VIEW: start utils.listArmHtml'
    list_arm = Arms.objects.all().order_by('name')
    dict_arm = {}
    i = 0
    armHtml = '<table id="oldArmTable"><tbody>'
    for p in list_arm:
        name = p.name
        typeTime = p.type_of_time
        armHtml = armHtml + '<tr id="row' + str(i) + '"><td id="oldArm_cell' + str(i) + '" onclick="getArm(event)"class="defCursor" style="border:4px outset lightgrey;background-color:silver;" armname="' + str(name) + '" unitTime = "' + str(typeTime) + '">' + str(name) + ' - ' + str(typeTime) + '</td><td id="info_cell'+str(i)+'"onclick="loadOldStep(event)" class="defCursor" style="border:4px outset lightgrey;background-color:silver;" armname="'+str(name)+ '"><img id="img_cell'+str(i)+'" armname="' + str(name) + '" src="/xeno_media/img/admin/selector-search.gif"></img></td></tr>'
        i = i + 1
    armHtml = armHtml + '</tbody></table>'
    return armHtml

#calcola le adiacenze del diagramma di gantt, usato per creare i nuovi trattamenti
def adjacencies (s):
    print 'XMM VIEW: start utils.adjacencies'
    adj = []
    j = 0
    start = -1
    stop = -1
    for k in s.strip():
        if int(k) == 1:
            if start == -1:
                start = j
                stop = j
            else:
                stop = j
        else:
            if start != -1:
                adj.append( (start,stop) ) 
                start = -1
                stop = -1            
        j = j+1
    if start != -1:
        adj.append( (start,stop) )
    return adj

#oggetto usato per immagazzinare le info della medicina selezionata quando si crea un nuovo trattamento. E' usat per salvare i details_treatments
class statusExtra:
    def __init__(self, extraName, extraData):
       self.extraName = extraName
       self.extraData = extraData

#oggetto usato per immagazzinare le info della medicina selezionata quando si crea un nuovo trattamento. E' usat per salvare i details_treatments
class drugInfo:
    def __init__(self, tupla):
       data = []
       values = string.split(tupla, '_')
       for v in values:
          data.append(string.strip(str(v)))
       self.drug = data[1]
       self.via = data[2]
       self.dose = data[3]
       self.schedule = data[4]

#classe di supporto utilizzata per gestire gli step nella fase di creazione di protocolli e arm
class step:
    def __init__(self, via, drug, start_step, end_step, dose, schedule):
        self.via = Via_mode.objects.get(description = via)
        self.drug = Drugs.objects.get(name = drug)
        self.start_step  = start_step
        self.end_step = end_step
        self.dose = dose
        self.schedule = schedule
    def toString():
        return str(self.via) + ' ' + str(self.drug) + ' ' +str(self.start_step) + ' ' + str(self.end_step) + ' ' + str(self.dose) + ' ' + str(self.schedule)

#classe di supporto per creare la lista delle aliquote create nella procedura degli espianti
class aliq:
    def __init__(self, genid, AliquotType, plateid, pos, numpezzi):
       self.genid = genid
       self.AliquotType = AliquotType
       self.plateid = plateid
       self.pos = pos
       self.numpezzi = numpezzi
    def toString(self):
        return str(self.genid) + '|' + str(self.AliquotType) + '|' + str(self.plateid) + '|' + str(self.pos) + '|' + str(self.numpezzi)


#per mappare da numeri a lettere maiuscole
partenza = "12345678"
destinazione = "ABCDEFGH"
trasftab = maketrans(partenza, destinazione)
#classe usata per creare le varie tabelle della seconda schermata dell'interfaccia degli espianti
class Collection():
    def table_vital(self):
        page=markup.page()
        page.table(id='vital',align='center')
        page.th(colspan=7)
        page.add('VITAL')
        page.th.close()
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
            page.strong(str(i).translate(trasftab))
            page.td.close()
            for j in range(1,7):
                page.td(width="20px", style="background-color: grey;")
                #page.button(type='submit', id='v-'+str(i).translate(trasftab)+str(j))
                #page.add(str(0))
                #page.button.close()
                page.td.close()
            page.tr.close()
        page.table.close()
        return page
    def table_rna(self):
        page=markup.page()
        page.table(id='rna')
        page.th(colspan=13)
        page.add('RNA LATER')
        page.th.close()
        page.tr()
        page.td()
        page.td.close()
        for i in range(1,13):
            page.td(align='center')
            page.strong(i)
            page.td.close()
        page.tr.close()
        for i in range (1,9):
            page.tr()
            page.td()
            page.br()
            page.strong(str(i).translate(trasftab))
            page.td.close()
            for j in range(1,13):
                page.td(width="20px", style="background-color: grey;")
                #page.button(type='submit', id='r-'+str(i).translate(trasftab)+str(j))
                #page.add(str(0))
                #page.button.close()
                page.td.close()
            page.tr.close()
        page.table.close()
        return page
    def table_tubes(self):
        page = markup.page()
        page.table(align='center',id='tubes')

        page.th()
        page.td()
        page.td.close()
        page.td()
        page.td.close()
        page.td("Last successfully inserted aliquot: ")
        page.td.close()
        
        page.tr()
        page.td()
        page.strong('FFPE: ')
        page.td.close()
        page.td()
        page.button(type='submit', id='f-0')
        page.button.close()
        page.td.close()
        page.td()
        page.label('Barcode:')
        page.label.close()
        page.input(type='text', id='inputf0',maxlength=45, size=8,onkeyup="checkKeyForNoP(event)")
        page.td.close()
        page.td()
        page.p("-", id = 'f-output', align='center' )
        page.td.close()
        page.tr.close()
        
        page.tr()
        page.td()
        page.strong('OCT: ')
        page.td.close()
        page.td()
        page.button(type='submit', id='o-0')
        page.button.close()
        page.td.close()
        page.td()
        page.label('Barcode:')
        page.label.close()
        page.input(type='text', id='inputo0',maxlength=45, size='8', onkeyup="checkKeyForNoP(event)")
        page.td.close()
        page.td()
        page.p("-", id = 'o-output', align='center' )
        page.td.close()
        page.tr.close()

        page.tr()
        page.td()
        page.strong('CB: ')
        page.td.close()
        page.td()
        page.button(type='submit', id='c-0')
        page.button.close()
        page.td.close()
        page.td()
        page.label('Barcode:')
        page.label.close()
        page.input(type='text', id='inputc0',maxlength=45, size='8', onkeyup="checkKeyForNoP(event)")
        page.td.close()
        page.td()
        page.p("-", id = 'c-output', align='center' )
        page.td.close()
        page.tr.close()

        page.table.close()
        return page
    def table_sf(self):
        page = markup.page()
        page.table(id='sf')
        page.th(colspan=13)
        page.add('SNAP FROZEN')
        page.th.close()
        page.tr()
        page.td()
        page.td.close()
        for i in range(1,13):
            page.td(align='center')
            page.strong(i)
            page.td.close()
        page.tr.close()
        for i in range (1,9):
            page.tr()
            page.td()
            page.br()
            page.strong(str(i).translate(trasftab))
            page.td.close()
            for j in range(1,13):
                page.td(width="20px", style="background-color: grey;")
                #page.button(type='submit', id='s-'+str(i).translate(trasftab)+str(j))
                #page.add(str(0))
                #page.button.close()
                page.td.close()
            page.tr.close()
        page.table.close()
        return page
    def table_blood(self):
        page = markup.page()
        page.table(align='center',id='tab_blood')

        page.tr()
        page.td()
        page.td.close()
        page.td()
        page.td.close()
        page.td()
        page.td.close()
        page.td()
        page.td.close()
        page.td()
        page.td.close()
        page.td()
        page.td.close()
        page.td("Last inserted aliquot: ",style='padding-bottom:1.5em;')
        page.td.close()
        page.tr.close()
        
        page.tr()
        page.td()
        page.strong('Plasma: ')
        page.td.close()
        page.td()
        page.button(type='submit', id='plas')
        page.button.close()
        page.td.close()
        page.td(style='padding-left:2em;')
        page.label('Barcode:')
        page.label.close()
        page.input(type='text', id='barcplas',maxlength=45, size=8)
        page.td.close()
        page.td(style='font-size:15px;padding-left:1em;')
        page.input(type='radio', name='cho_PL', value='tube', style='display:inline;')
        page.span(style='display:inline;')
        page.add('Tube')
        page.span.close()
        page.input(type='radio', name='cho_PL', value='plate', style='display:inline;')
        page.span(style='display:inline;')
        page.add('Plate')
        page.span.close()
        page.td.close()
        page.td(style='padding-left:2em;')
        page.label('Volume(ml):')
        page.label.close()
        page.input(type='text', id='volplas',maxlength=10, size=6)
        page.td.close()
        page.td()
        page.td.close()
        page.td()
        page.p("-", id = 'plasoutput', align='center' )
        page.td.close()
        page.tr.close()
        
        page.tr()
        page.td()
        page.strong('Whole blood: ')
        page.td.close()
        page.td()
        page.button(type='submit', id='who')
        page.button.close()
        page.td.close()
        page.td(style='padding-left:2em;')
        page.label('Barcode:')
        page.label.close()
        page.input(type='text', id='barcwho',maxlength=45, size='8')
        page.td.close()
        page.td(style='font-size:15px;padding-left:1em;')
        page.input(type='radio', name='cho_SF', value='tube', style='display:inline;')
        page.span(style='display:inline;')
        page.add('Tube')
        page.span.close()
        page.input(type='radio', name='cho_SF', value='plate', style='display:inline;')
        page.span(style='display:inline;')
        page.add('Plate')
        page.span.close()
        page.td.close()
        page.td(style='padding-left:2em;')
        page.label('Volume(ml):')
        page.label.close()
        page.input(type='text', id='volwho',maxlength=10, size=6)
        page.td.close()
        page.td()
        page.td.close()
        page.td()
        page.p("-", id = 'whooutput', align='center' )
        page.td.close()
        page.tr.close()

        page.tr()
        page.td()
        page.strong('PAX tube: ')
        page.td.close()
        page.td()
        page.button(type='submit', id='pax')
        page.button.close()
        page.td.close()
        page.td(style='padding-left:2em;')
        page.label('Barcode:')
        page.label.close()
        page.input(type='text', id='barcpax',maxlength=45, size='8')
        page.td.close()
        page.td(style='font-size:15px;padding-left:1em;')
        page.input(type='radio', name='cho_PX', value='tube', style='display:inline;')
        page.span(style='display:inline;')
        page.add('Tube')
        page.span.close()
        page.input(type='radio', name='cho_PX', value='plate', style='display:inline;')
        page.span(style='display:inline;')
        page.add('Plate')
        page.span.close()
        page.td.close()
        page.td(style='padding-left:2em;')
        page.label('Volume(ml):')
        page.label.close()
        page.input(type='text', id='volpax',maxlength=10, size=6)
        page.td.close()
        page.td()       
        page.td.close()
        page.td()
        page.p("-", id = 'paxoutput', align='center' )
        page.td.close()
        page.tr.close()
        
        page.tr()
        page.td()
        page.strong('PBMC: ')
        page.td.close()
        page.td()
        page.button(type='submit', id='pbmc')
        page.button.close()
        page.td.close()
        page.td(style='padding-left:2em;')
        page.label('Barcode:')
        page.label.close()
        page.input(type='text', id='barcpbmc',maxlength=45, size='8')
        page.td.close()
        page.td(style='font-size:15px;padding-left:1em;')
        page.input(type='radio', name='cho_VT', value='tube', style='display:inline;')
        page.span(style='display:inline;')
        page.add('Tube')
        page.span.close()
        page.input(type='radio', name='cho_VT', value='plate', style='display:inline;')
        page.span(style='display:inline;')
        page.add('Plate')
        page.span.close()
        page.td.close()
        page.td(style='padding-left:2em;')
        page.label('Volume(ml):')
        page.label.close()
        page.input(type='text', id='volpbmc',maxlength=10, size=6)
        page.td.close()
        page.td(style='padding-left:2em;')
        page.label('Count(cell/ml):')
        page.label.close()
        page.input(type='text', id='contapbmc',maxlength=10, size=6)
        page.td.close()
        page.td()
        page.p("-", id = 'pbmcoutput', align='center' )
        page.td.close()
        page.tr.close()
        page.table.close()
        return page
    def table_urine(self):
        page = markup.page()
        page.table(align='center',id='tab_uri')
        page.tr()
        page.td()
        page.td.close()
        page.td()
        page.td.close()
        page.td()
        page.td.close()
        page.td()
        page.td.close()
        page.td()
        page.td.close()
        page.td()
        page.td.close()
        page.td("Last inserted aliquot: ",style='padding-bottom:1.5em;')
        page.td.close()
        page.tr.close()
        page.tr()
        page.td()
        page.strong('Urine: ')
        page.td.close()
        page.td()
        page.button(type='submit', id='uri')
        page.button.close()
        page.td.close()
        page.td(style='padding-left:2em;')
        page.label('Barcode:')
        page.label.close()
        page.input(type='text', id='barcuri',maxlength=45, size=8)
        page.td.close()
        page.td(style='font-size:15px;padding-left:1em;')
        page.input(type='radio', name='cho_FR', value='tube', style='display:inline;')
        page.span(style='display:inline;')
        page.add('Tube')
        page.span.close()
        page.input(type='radio', name='cho_FR', value='plate', style='display:inline;')
        page.span(style='display:inline;')
        page.add('Plate')
        page.span.close()
        page.td.close()
        page.td(style='padding-left:2em;')
        page.label('Volume(ml):')
        page.label.close()
        page.input(type='text', id='voluri',maxlength=10, size=6)
        page.td.close()
        page.td()
        page.td.close()
        page.td()
        page.p("-", id = 'urioutput', align='center' )
        page.td.close()
        page.tr.close()
        page.table.close()
        return page
