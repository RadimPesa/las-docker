import string, json, time
from pprint import pprint
from string import maketrans
from xenopatients import markup
from django.db import transaction
import os, urllib, urllib2, cStringIO
from xenopatients.utils import *
from xenopatients.treatments import *

class Simple:
    def __init__(self, m, select):
       self.attributes={}
       for f in m._meta.fields:
           if len(select) == 0:
                self.attributes[f.name] = str(m.__getattribute__(f.name))
           elif f.name in select:
                self.attributes[f.name] = str(m.__getattribute__(f.name))
    def toStr(self):
        output = ''
        a = []
        for k, v in self.attributes.items():
            b = {k:str(v)}
            a.append(b)
        return json.dumps(a)
    def getAttributes(self):
        return self.attributes
        
'''
def is_number(s):
    print 'XMM API: start utils.is_number'
    try:
        float(s)
        return True
    except ValueError:
        return False
'''

def getMeasure(mice, operators, dateList):#, measure):
    print 'XMM API: start utils.getMeasure'
    dateList = Measurements_series.objects.filter(    Q(id_series__in=Quantitative_measure.objects.filter(id_mouse__in = mice).values_list('id_series').distinct()) |  Q(id_series__in=Qualitative_measure.objects.filter(id_mouse__in = mice).values_list('id_series').distinct())   ).values_list('date', 'id_operator__username').distinct()
    #qualitative = Measurements_series.objects.filter(id_series__in=Qualitative_measure.objects.filter(id_mouse__in = mice).values_list('id_series').distinct()).values_list('date', 'id_operator__username').distinct()
    # from itertools import chain
    # dateList = list(chain(quantitative, qualitative))
    # dateList = quantitative
    # print dateList
    print '1'
    operators = [str(t) for t in set([t1[1] for t1 in dateList])]
    print '2'
    dateList = [str(t) for t in set([t1[0] for t1 in dateList])]
    print '3'
    return operators, dateList#, measure

def truncDateWrapper(mha):
    #print 'XMM API: start utils.truncDateWrapper'
    startDate = mha.start_date
    if startDate == None:
        if mha.id_prT:
            startDate = mha.id_prT.expectedStartDate
        else:
            startDate = datetime.now()
    endDate = ""
    if mha.end_date:
        endDate = mha.end_date
    typeTime =  mha.id_protocols_has_arms.id_arm.type_of_time
    return truncDate(startDate, endDate, typeTime)

def truncDate(startDate, endDate, typeTime):
    #   print 'XMM API: start utils.truncDate'
    #'minutes','hours','days','months'
    if typeTime == 'hours':
        if startDate != "" and startDate != None:
            startDate = str(startDate.year) + '-' + str(startDate.month) + '-' + str(startDate.day) + '-' + str(startDate.hour)
        if endDate != "" and endDate != None:
            endDate = str(endDate.year) + '-' + str(endDate.month) + '-' + str(endDate.day) + '-' + str(endDate.hour)
    elif typeTime == 'days':
        if startDate != "" and startDate != None:
            startDate = str(startDate.year) + '-' + str(startDate.month) + '-' + str(startDate.day)
        if endDate != "" and endDate != None:
            endDate = str(endDate.year) + '-' + str(endDate.month) + '-' + str(endDate.day)
    elif typeTime == 'months':
        if startDate != "" and startDate != None:
            startDate = str(startDate.year) + '-' + str(startDate.month)
        if endDate != "" and endDate != None:
            endDate = str(endDate.year) + '-' + str(endDate.month)
    return startDate, endDate

def makeLabel(listT):
    #print 'XMM API: start utils.makeLabel'
    label = ""
    for l in listT:
        if label == "":
            label = str(l[0]) + ': ' + str(l[1]) + '->' + str(l[2])
        else:
            label += ', ' + str(l[0]) + ': ' + str(l[1]) + '->' + str(l[2])
    return label

def makeLabelComment(listT):
    label = ""
    for l in listT:
        sec=l[1]
        if sec=='':
            sec='  '
        label += str(l[0]) + ': ' + str(sec) + '; '
    print 'label',label
    if label=="":
        return label
    return label[:len(label)-2]


def rawTruncDateWrapper(mha):
    #print 'XMM API: start utils.rawTruncDateWrapper'
    startDate = mha.start_date
    endDate = mha.end_date
    typeTime =  mha.id_protocols_has_arms.id_arm.type_of_time
    return truncDate(startDate, endDate, typeTime)
    #return str(startDate), str(endDate)


def defineG(mice, dateList):
    #print 'XMM API: start utils.defineG'
    miceDict = {}
    noteDict={}
    for m in mice:  
        tempList = []
        tempcomment=[]
        #trattamenti in corso e/o terminati
        mhas = Mice_has_arms.objects.filter(id_mouse = m)
        for mha in mhas:
            #troncare i datetime in base al tipo di braccio!
            startDate, endDate = rawTruncDateWrapper(mha)
            #print "XMM utils.defineG:",str(startDate), str(endDate)
            if startDate != None or endDate == None:
                #print "XMM utils.defineG:",m.id_genealogy
                if startDate == None:
                    #print '1'
                    startDate = mha.id_prT.expectedStartDate
                    #print '2'
                if endDate == None:
                    endDate = ""
                tempList.append( (getNameT(mha), startDate, endDate) )
                if mha.id_prT !=None:
                    if mha.id_prT.id_event != None:                    
                        notes=mha.id_prT.id_event.checkComments
                        tempcomment.append((getNameT(mha),notes))
            else:
                print 'XMM utils.defineG: not in label, aborted'
        #trattamenti eventualmente proposti dall'operatore
        proposedMha = Pr_treatment.objects.filter(id_event__in = ProgrammedEvent.objects.filter(id_mouse = m, id_status = EventStatus.objects.get(name = 'pending')))
        for pMha in proposedMha:
           startDate, endDate = truncDate(pMha.expectedStartDate, "", pMha.id_pha.id_arm.type_of_time)
           tempList.append( (getNamePT(pMha), startDate, endDate) )
           notes=pMha.id_event.checkComments
           tempcomment.append((getNamePT(pMha),notes))
        print 'tempComment',tempcomment
        #se la lista e' formata da un solo elemento e non ci sono note, non faccio vedere niente
        if len(tempcomment)==1 and (tempcomment[0][1]=='' or tempcomment[0][1]==None):
            del tempcomment[:]
        noteDict.update({m.id_genealogy:makeLabelComment(tempcomment)})
        miceDict.update({m:makeLabel(tempList)})
    print 'micedict',miceDict
    print 'notedict',noteDict
    groupsDict = {}
    for m in miceDict:
        label = miceDict[m]
        if label == "":
            label = 'Waste'
        if label not in groupsDict.keys():
            groupsDict[label] = []
        groupsDict[label].append(m)
    if len(groupsDict.keys()) == 1:
        try:
            groupsDict[mice[0].id_group.name] = groupsDict['Waste']
            del groupsDict['Waste']
        except:
            pass
    print 'groupsdict',groupsDict
    dateList = sorted(dateList)
    return dateList, groupsDict, noteDict

def history(mice, dateList, groups, groupsNote):
    print 'XMM API: start utils.history'
    tableDictW, tableDict = {}, {}
    for d in dateList:
        for m in mice:
            tableDict[m.id_genealogy] = {}
            tableDict[m.id_genealogy][d] = "<td>N.A.</td>"
            tableDictW[m.id_genealogy] = {}
            tableDictW[m.id_genealogy][d] = "<td>N.A.</td>"
    for m in mice:
        q = Quantitative_measure.objects.filter(id_mouse = m).order_by('id_series__date').values_list('id_series__date', 'weight', 'volume')
        q1 =  set([(x[0], x[1]) for x in q])
        q2 = set(Qualitative_measure.objects.filter(id_mouse = m).order_by('id_series__date').values_list('id_series__date', 'weight'))
        q3 =  set([(x[0], x[2]) for x in q])
        res = list(q1 | q2)
        valuesW = {}
        for r in res:
            if valuesW.has_key(str(r[0])) == False:
                valuesW[str(r[0])] = []
            print str(r[1])
            if str(r[1]) != '0.0' and r[1] != None:
                valuesW[str(r[0])].append(r[1])
            else:
                valuesW[str(r[0])].append("N.A.")
        values = {}
        for q in q3:
            if values.has_key(str(q[0])) == False:
                values[str(q[0])] = []
            values[str(q[0])].append(q[1])
        for d in dateList:
            temp = 'N.A.'
            if valuesW.has_key(d):
                temp = '<br> '.join((str(w) for w in valuesW[d]))
            tableDictW[m.id_genealogy][d] = "<td align='center'>"+str(temp)+"</td>"
            temp = 'N.A.'
            if values.has_key(d):
                temp = '<br> '.join((str(m) for m in values[d]))
            #print temp,m.id_genealogy, d
            tableDict[m.id_genealogy][d] = "<td align='center'>"+str(temp)+"</td>"
    table = writeTable(dateList, groups, tableDict, mice, groupsNote)
    wTable = writeWTable(dateList, groups, tableDictW, mice, groupsNote)
    return  table, wTable

def writeTable(dateList, groups, tableDict, mice, groupsNote):
    print 'XMM API: start utils.writeTable'
    print 'groupsNote',groupsNote
    tempM = []
    table = '<table id="measureLong"><thead><tr><th>Genealogy ID</th><th>Barcode</th><th>Group</th><th>Label</th><th>Treatment</th><th>Start Info</th><th>End Info</th><th>Treatment notes</th>'
    for d in dateList:
        table += '<th>' + d + '</th>'
    table += '</tr></thead><tbody>'
    if len(groups.keys()) > 0:
        for m in mice:
            tempM.append(m.id_genealogy)
        i = 0
        for label in groups:
            for genID in groups[label]:
                mouse = BioMice.objects.get(id_genealogy = genID)
                barcode = mouse.phys_mouse_id.barcode
                group = mouse.id_group.name
                genID = str(genID.id_genealogy)                
                labelnotes=''
                if genID in groupsNote:
                    labelnotes=groupsNote[genID]
                    
                if label != "Waste":
                    mha = Mice_has_arms.objects.filter(id_mouse = mouse, end_date__isnull = True)
                    #se c'e' un trattamento in corso
                    if len(mha) == 1:
                        nameT = getNameT(mha[0])
                        nameP, nameA = splitNameT(nameT)
                        dateS = str(mha[0].start_date)
                        dateE = str(mha[0].expected_end_date)
                        if mha[0].id_prT is not None:
                            dateP = str(mha[0].id_prT.expectedStartDate)
                        else:
                            dateP = ""
                        #sottogruppo ----> label                        
                            
                        if dateS != "None" and dateE != "None":
                            table+='<tr class="minigroup'+str(i)+'"><td>'+genID+'</td><td>'+barcode+'</td><td>'+group+'</td><td>'+label+'</td><td>'+nameT+'</td><td>Started the '+dateS+'</td><td>Ending the '+dateE+'</td><td>'+labelnotes+'</td>'
                        elif dateS != "None":
                            table +='<tr class="minigroup'+str(i)+'"><td>'+genID+'</td><td>'+barcode+'</td><td>'+group+'</td><td>'+label+'</td><td>'+nameT+'</td><td>Started the '+dateS+'</td><td></td><td>'+labelnotes+'</td>'
                        elif dateE != "None":
                            table +='<tr class="minigroup'+str(i)+'"><td>'+genID+'</td><td>'+barcode+'</td><td>'+group+'</td><td>'+label+'</td><td>'+nameT+'</td><td>Aborted the '+dateE+'</td><td></td><td>'+labelnotes+'</td>'
                        elif dateP != "None":
                            table +='<tr class="minigroup'+str(i)+'"><td>'+str(genID)+'</td><td>'+barcode+'</td><td>'+group+'</td><td>'+label+'</td><td>'+nameT+'</td><td>Starting the '+dateP+'</td><td></td><td>'+labelnotes+'</td>'
                    else:
                        #no waste e nessun trattamento attualmente in corso
                        table +='<tr class="minigroup'+str(i)+'"><td>'+genID+'</td><td>'+barcode+'</td><td>'+group+'</td><td>'+label+'</td><td></td><td></td><td></td><td>'+labelnotes+'</td>'
                    for d in dateList:
                        table += tableDict[genID][d]
                    table += '</tr>'
                else:
                    table += '<tr class="waste"><td>' + genID + '</td><td>'+barcode+'</td><td>' + group + '</td><td>'+label+'</td><td></td><td></td><td></td><td>'+labelnotes+'</td>'
                    for d in dateList:
                        table += tableDict[genID][d]
                    table += '</tr>'
            i = i + 1
    else:
        for m in mice:
            table += '<tr><td>' + m.id_genealogy + '</td><td>'+m.phys_mouse_id.barcode+'</td><td>' + m.id_group.name + '</td><td></td><td></td><td></td><td></td><td></td>'
            for d in dateList:
                table += tableDict[m.id_genealogy][d]
            table += '</tr>'
    return table + '</tbody></table>'

def writeWTable(dateList, groups, tableDict, mice, groupsNote):
    print 'XMM API: start utils.writeWTable'
    tempM = []
    wTable = '<table id="allW"><thead><tr><th>Genealogy ID</th><th>Barcode</th><th>Group</th><th>Label</th><th>Treatment</th><th>Start Info</th><th>End Info</th><th>Treatment notes</th>'
    for d in dateList:
        wTable += '<th>' + d + '</th>'
    wTable += '</tr></thead><tbody>'
    if len(groups.keys()) > 0:
        for m in mice:
          tempM.append(m.id_genealogy)
        i = 0
        for label in groups:
            for genID in groups[label]:
                mouse = BioMice.objects.get(id_genealogy = genID)
                barcode = mouse.phys_mouse_id.barcode
                group = mouse.id_group.name
                genID = str(genID.id_genealogy)
                labelnotes=''
                if genID in groupsNote:
                    labelnotes=groupsNote[genID]
                if label != "Waste":
                    mha = Mice_has_arms.objects.filter(id_mouse = mouse, end_date__isnull = True)
                    #se c'e' un trattamento in corso
                    if len(mha) == 1:
                        nameT = getNameT(mha[0])
                        nameP, nameA = splitNameT(nameT)
                        dateS = str(mha[0].start_date)
                        dateE = str(mha[0].expected_end_date)
                        if mha[0].id_prT is not None:
                            dateP = str(mha[0].id_prT.expectedStartDate)
                        else:
                            dateP = ""
                        #sottogruppo ----> label
                        if dateS != "None" and dateE != "None":
                            wTable+='<tr class="minigroup'+str(i)+'"><td>'+genID+'</td><td>'+barcode+'</td><td>'+group+'</td><td>'+label+'</td><td>'+nameT+'</td><td>Started the '+dateS+'</td><td>Ending the '+dateE+'</td><td>'+labelnotes+'</td>'
                        elif dateS != "None":
                            wTable +='<tr class="minigroup'+str(i)+'"><td>'+genID+'</td><td>'+barcode+'</td><td>'+group+'</td><td>'+label+'</td><td>'+nameT+'</td><td>Started the '+dateS+'</td><td></td><td>'+labelnotes+'</td>'
                        elif dateE != "None":
                            wTable +='<tr class="minigroup'+str(i)+'"><td>'+genID+'</td><td>'+barcode+'</td><td>'+group+'</td><td>'+label+'</td><td>'+nameT+'</td><td>Aborted the '+dateE+'</td><td></td><td>'+labelnotes+'</td>'
                        elif dateP != "None":
                            wTable +='<tr class="minigroup'+str(i)+'"><td>'+genID+'</td><td>'+barcode+'</td><td>'+group+'</td><td>'+label+'</td><td>'+nameT+'</td><td>Starting the '+dateP+'</td><td></td><td>'+labelnotes+'</td>'
                    else:
                        #no waste e nessun trattamento attualmente in corso
                        wTable +='<tr class="minigroup'+str(i)+'"><td>'+genID+'</td><td>'+barcode+'</td><td>'+group+'</td><td>'+label+'</td><td></td><td></td><td></td><td>'+labelnotes+'</td>'
                    for d in dateList:
                        wTable += tableDict[genID][d]
                    wTable += '</tr>'
                else:
                    wTable += '<tr class="waste"><td>' + genID + '</td><td>'+barcode+'</td><td>' + group + '</td><td>'+label+'</td><td></td><td></td><td></td><td>'+labelnotes+'</td>'
                    for d in dateList:
                        wTable += tableDict[genID][d]
                    wTable += '</tr>'
            i = i + 1
    else:
        for m in mice:
            wTable += '<tr><td>' + m.id_genealogy + '</td><td>'+m.phys_mouse_id.barcode+'</td><td>' + m.id_group.name + '</td><td></td><td></td><td></td><td></td><td></td>'
            for d in dateList:
                wTable += tableDict[m.id_genealogy][d]
            wTable += '</tr>'
    return wTable + '</tbody></table>'

'''
def newG(oldGObj, k, n, vector, oldG):
    print 'XMM API: start utils.newG'
    if oldGObj.getSampleVector() == 'H':
        lineage = newLineage(k + n)
    else:
        lineage = oldGObj.getLineage()
    passage = oldGObj.getSamplePassagge()
    passage = int(passage) + 1
    if passage < 10:
        passage = '0'+ str(passage)
    mouse = oldGObj.getMouse()
    mouse = int(mouse) + 1
    end = '000000000'
    if vector == "X":
        mouse = n + k + 1
        newM = ""
        if mouse < 100:
            newM = '0'+str(mouse)
        if mouse < 10:
            newM = '00'+str(mouse)
    newM = str(mouse)
    if mouse < 100:
        newM = '0'+str(mouse)
    if mouse < 10:
        newM = '00'+str(mouse)
    #creazione parametri e chiamata classe
    try:
        dataDict = {'sampleVector':'X', 'lineage':lineage, 'samplePassage':str(passage), 'mouse':str(newM), 'tissueType':'000', 'archiveMaterial2': '00', 'aliqExtraction2':'00', '2derivation': '0', '2derivationGen':'00'}
        classGen = GenealogyID(oldG)
        classGen.updateGenID(dataDict)
        genID = classGen.getGenID()
        return genID
    except Exception, err:   
        print 'XMM API utils.newG: 1) ', str(err)
        return 'err'
''' 
def getLastMeasure(m,quant, qual):
    #print 'XMM API: start utils.getLastMeasure'
    date, value, weight, notes = '-', '-', '-', '-'
    #quant = Quantitative_measure.objects.filter(id_mouse = m)
    if len(quant) > 0:
        for q in quant:
            if q.id_mouse == m:
                if date == '-':
                    date = q.id_series.date
                    value = q.volume
                    weight = q.weight
                    notes = q.notes
                else:
                    if q.id_series.date > date:
                        date = q.id_series.date
                        value = q.volume
                        weight = q.weight
                        notes = q.notes
    #qual = Qualitative_measure.objects.filter(id_mouse = m)
    if len(qual) > 0:
        for q in qual:
            if q.id_mouse == m:
                if date == '-':
                    date = q.id_series.date
                    value = q.id_value.value
                    weight = q.weight
                    notes = q.notes
                else:
                    if q.id_series.date > date:
                        date = q.id_series.date
                        value = q.id_value.value
                        weight = q.weight
                        notes = q.notes
    return date, value, weight, notes
    
def getProgrammedExpl(m, expl):
    #print 'XMM API: start utils.getProgrammedExpl'
    scopeExpl, scopeNotes = 'Not programmed for explant', '-'
    #expl = Programmed_explant.objects.filter(id_mouse = m, done = 0)
    for e in expl:
        if e.id_mouse == m:
            return e.id_scope.description, e.scopeNotes
    return scopeExpl, scopeNotes
    
def getCurrentTreat(m, mhas):
    #print 'XMM API: start utils.getCurrentTreat'
    nameT, start, duration, endD, notes = '-', '-', '-', '-', ''
    for mha in mhas:
        if mha.id_mouse == m:
            nameT = getNameT(mha)
            start = mha.start_date
            duration = str(mha.id_protocols_has_arms.id_arm.duration) + ' ' + mha.id_protocols_has_arms.id_arm.type_of_time
            endD = mha.expected_end_date
            #devo andare a prendere le eventuali note al trattamento leggendo nel programmed treatment e poi nel programmed event collegato
            if mha.id_prT !=None:
                if mha.id_prT.id_event != None:                    
                    notes=mha.id_prT.id_event.checkComments
            return nameT, start, duration, endD, notes
    return nameT, start, duration, endD, notes
