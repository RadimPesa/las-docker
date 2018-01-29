import optparse, os, sys
from openpyxl.reader.excel import load_workbook
import xlrd
import json

#python historyimplants.py -f implants

def insertError (aliquots, errors, keyErr, mistake):
    if errors.has_key(keyErr) == False:
        errors[keyErr] = [aliquots[keyErr]]
    errors[keyErr].append(mistake)

def addChar(string):
    return string[:9] + '0' + string[9:]

def implantTransformCSVxls (fileName, aliquots, errors, outputFile):
    print 'start history impl'
    #print fileName
    #print aliquots
    #print errors
    #print outputFile
    miceList, sh1List,sh2List = [],[],[]
    wb = xlrd.open_workbook(fileName)
    sh = wb.sheet_by_index(0)
    sh2 = wb.sheet_by_index(1)
    noBarcode,withB = 0,0
    for rownum in range(sh.nrows):
        values = sh.row_values(rownum)
        #print values
        if values[0][0:4] == "IMPL":
            sh1List.append({'seriesID':values[0], 'operator':values[1],  'date':str(make_date(float(values[2]) ) )} )
    for rownum in range(sh2.nrows):
        values = sh2.row_values(rownum)
        if str(values[1]) != "":
            if values[0][0:6] == "IMPLdt": # and values[2][0:3] == "000":
                #se il topo non era chippato, usare il genID come barcode ---> if.. else...
                barcode = values[2].upper()
                if barcode == "":
                    noBarcode += 1
                    barcode = values[4].upper() #addChar(values[10].upper())
                else:
                    withB += 1
                sh2List.append({'seriesID':values[1].replace('-',''),'detailID':values[0],'barcodeMouse':barcode,'idExpl':values[5], 'site':values[9], 'newGen':values[4],'oldG':values[7]})
                #"".join(values[6].upper().split())
    print 'sh1',len(sh1List)
    print 'sh2',len(sh2List)
    for m in sh2List:
        index = sh2List.index(m)
        seriesID = m['seriesID']
        idI = m['detailID']
        flag = False
        site = m['site']
        if site == "LIVER":
            site = "LI"
        for value in sh1List:
            if value['seriesID'] == seriesID:
                flag = True
                operator = value['operator']
                date = value['date']
                #print site
                miceList.append({'barcodeMouse':m['barcodeMouse'], 'oldG':m['oldG'], 'dateI':date, 'idI':idI, 'operatorI':operator,'site':site, 'newG':addZeros(m['newGen']), 'idExpl':m['idExpl'].replace('-','')})
        if not flag:
            print seriesID
    print len(miceList)
    return miceList, noBarcode, withB
    
def explantTransformCSVxls (fileName, aliquots, errors, outputFile):
    print 'start history expl'
    #print fileName
    #print aliquots
    #print errors
    #print outputFile
    sh1List = []
    sh2List = []
    explList = []
    wb = xlrd.open_workbook(fileName)
    sh = wb.sheet_by_index(0)
    sh2 = wb.sheet_by_index(1)
    for rownum in range(sh.nrows):
        values = sh.row_values(rownum)
        if values[0][0:4] == "EXPL":
            sh1List.append({'seriesID':values[0], 'operator':values[1], 'date':str(make_date(float(values[2]))), 'nMice':values[3], 'scope':values[4]} )
    for rownum in range(sh2.nrows):
        values = sh2.row_values(rownum)
        if str(values[1]) != "":
            if values[0][0:6] == "EXPLdt": # and values[2][0:3] == "000":
                #se il topo non era chippato, usare il genID come barcode ---> if.. else...
                #mouseID = "".join(values[5].upper().split())
                mouseID = values[3]
                sh2List.append({'seriesID':values[1].replace('-',''),'detailID':values[0],'idGen':values[3],'barcode':mouseID,'notes':values[7], 'FF':values[9], 'VT':values[10], 'RL':values[11], 'SF':values[12], 'OF':values[13], 'idE':values[0] })
                
    print 'sh1',len(sh1List)
    print 'sh2',len(sh2List)
    for m in sh2List:
        index = sh2List.index(m)
        seriesID = m['seriesID']
        idGen = m['idGen']
        notes = m['notes']
        idE = m['idE']
        FF, VT, RL, SF, OF = m['FF'], m['VT'], m['RL'], m['SF'], m['OF']
        for value in sh1List:
            if value['seriesID'] == seriesID:
                operator = value['operator']
                date = value['date']
                nMice = value['nMice']
                scope = value['scope']
                #print FF, VT, RL, SF, OF
                if not RL:
                    RL = 0
                if not FF:
                    FF = 0
                if not VT:
                    VT = 0
                if not SF:
                    SF = 0
                if not OF:
                    OF = 0
                #,'FF':int(FF), 'VT':int(VT), 'RL':int(RL), 'SF':int(SF), 'OF':int(OF)
                explList.append({'barcode':m['barcode'], 'operatorE':operator, 'dateE':date, 'nMice':nMice,'scope':scope, 'idGen':addZeros(idGen), 'notes':notes, 'idE': idE})

    return explList

def checkForTissue(explList, tissueList, miceList):
    bad, ok, = 0,0
    test = 0
    for e in explList:
        genID = e['idGen']
        found = False
        for t in tissueList:
            if t['genID'] == genID:
                found = True
                break
        if found:
            ok += 1
        else:
            '''
            #print e['idGen'], e['idE']
            for m in miceList:
                #if m['oldG']==e['idGen']:
                if m['idExpl'] == e['idE']:
                    test += 1
                    break
            '''
            bad += 1
    print 'explants with output aliquots: ', ok
    print test
    print 'explants without output aliquots: ', bad


def tissueTransformCSVxls (fileName, aliquots, errors, outputFile):
    print 'start history tissue'
    tissueList, sh1List,sh2List = [],[],[]
    wb = xlrd.open_workbook(fileName)
    sh = wb.sheet_by_index(0)
    sh2 = wb.sheet_by_index(1)
    for rownum in range(sh2.nrows):
        values = sh2.row_values(rownum)
        if str(values[0]) != "Genealogy_15":
            tissueList.append({'genID':addZeros(values[0]), 'aliquot':addZeros(values[5])})
    print 'tissueList', str(len(tissueList))
    return tissueList


def checkExplD(explList, miceList):
    ok, err, noE, explOk, noImpl = 0,0,0,0,0

    for m in miceList:
        idE = m['idExpl']
        flag = False
        for e in explList:
            if e['idE'] == idE:
                flag = True
                if m['oldG'] == e['idGen']:
                    ok += 1
                else:
                    err += 1
        if not flag:
            noE += 1
    
    for e in explList:
        idE = e['idE']
        flag = False
        for m in miceList:
            if m['idExpl'] == idE:
                explOk += 1
                flag = True
        if not flag:
            noImpl += 1
    
    print 'impl - expl associazione ok: ', ok
    print 'impl - expl no match genID: ', err
    print 'impl senza expl: ',noE
    
    print 'expl con impl: ', explOk
    print 'expl senza impl: ', noImpl
        
def addZeros(aliquot):
    if len(aliquot) == 15:
        aliquot = aliquot[:3] + '0' + aliquot[3:9] + '0' + aliquot[9:] + '000000000'
        #print aliquot
    elif len(aliquot) == 22:
        aliquot = aliquot[:3] + '0' + aliquot[3:9] + '0' + aliquot[9:] + '00'
        #print aliquot    
    else:
        print 'achtung!!', str(aliquot)
    return aliquot
        
def writeFileMice(outputFile, explList, miceList, tissueList):
    noExpl, noImpl, both = 0,0,0
    finalData = []
    #newG (impl) -----> idGen (expl)
    finalList = []
    for m in miceList:
        #index = miceList.index(m)
        #print m
        flag = False
        mouse = {}
        for e in explList:
            if e['idGen'] == m['newG']:
                k = explList.index(e)
                flag = True
                tempE = e
                explList.pop(k)
        if flag:
            #match!!
            finalData.append(m)
            i = finalData.index(m)
            finalData[i].update(tempE)
            aliquots = []
            for t in tissueList:
                if t['genID'] == tempE['idGen']:
                    aliquots.append(t['aliquot'])
            mouse.update( {'info': {'barcode': m['barcodeMouse'], 'genID':m['newG'] },
                           'implant': {'operator': m['operatorI'], 'date': m['dateI'], 'oldG': m['oldG'] , 'site': m['site']} , 
                           'explant': {'operator': tempE['operatorE'], 'date': tempE['dateE'], 'notes': tempE['notes'], 'outputAliquots': aliquots} 
                        } )
            both += 1
        else:
            #mouse with implant but no explant
            finalData.append(m)
            mouse.update( {'info': {'barcode': m['barcodeMouse'], 'genID':m['newG'] },
                           'implant': {'operator': m['operatorI'], 'date': m['dateI'], 'oldG': m['oldG'] , 'site': m['site']} , 
                           'explant': {} } )
            #print m
            noExpl += 1
        finalList.append(mouse)
    mouse = {}
    for e in explList:
        #print e
        finalData.append(e)
        aliquots = []
        for t in tissueList:
            if t['genID'] == tempE['idGen']:
                aliquots.append(t['aliquot'])
        mouse.update( {'info': {'barcode': e['barcode'], 'genID':e['idGen'] },
                       'implant': {} , 
                       'explant': {'operator': e['operatorE'], 'date': e['dateE'], 'notes': e['notes'], 'outputAliquots': aliquots} 
                    } )
        noImpl += 1
        finalList.append(mouse)
    #print len(miceList)
    #print len(finalList)
    print finalList[0]
    print 'total mice: ', str(noExpl + noImpl + both)
    print 'mice with only implant: ', str(noExpl)
    print 'mice with only explant: ', str(noImpl)
    print 'mice with both: ', str(both)


    fout = open (outputFile, 'w')
    '''
    for f in finalData:
        string = ""
        #for key in f:
        #    if string == "":
        #        string = str(f[key])
        #    else:
        #        string += '\t' + str(f[key] )
        string = json.dumps(f)
        fout.write (string + '\n')
    '''
    fout.write(json.dumps(finalList))
    fout.close()
        
def make_date(xlnum):
    from datetime import date
    from datetime import timedelta
    year = timedelta(days=xlnum)
    my_date = date(1899, 12, 30)
    return my_date + year

def checkIE(explList, miceList):
    E, noE, humans, other, warning, withChip, err = 0,0,0,0,0,0,0
    for m in miceList:
        idExpl = m['idExpl']
        if idExpl != "/":
            #print idExpl
            E += 1
        else:
            noE +=1
            oldG = m['oldG']
            if len(oldG) >= 9:
                if oldG[8] == 'H':
                    humans += 1
                elif oldG[8] == 'X':
                    if m['barcodeMouse'] != "":
                        withChip += 1
                    else:
                        warning += 1
                else:
                    other += 1
                    #print m['newG'][11:14]
                    if m['newG'][11:14] == "000":
                        print m['newG']
                        err += 1
            else:
                other += 1
                if m['newG'][11:14] == "000":
                    #print m['newG'], m['oldG']
                    err += 1

    print 'implants with no expl: ', noE
    print '---- from humans: ', humans
    print '---- from other: ', other
    print '---- new mice with chip: ', withChip
    print 'implants with expl: ', E
    print 'implants with too many zeros: ', err

def main():
    opt = optparse.OptionParser()
    opt.add_option('--folder', '-f', default='./', help="Folder of input plates")
    opt.add_option('--output', '-o', default='output.txt', help="Output file for aliquots")
    #opt.add_option('--error', '-e', default='errors.txt', help="error file for aliquots")
    #opt.add_option('--tanomy', '-t', default='tax_gen.txt', help='source taxonomy of previous steps')

    option, arguments = opt.parse_args()
    aliquots = {}
    errors = {}
    print "start"
    #print option.folder
    miceList, explList, tissueList = [], [], []
    for fileName in os.listdir(option.folder):
        #print fileName
        fileN = os.path.join (option.folder, fileName)
        #print fileN
        if os.path.isfile (fileN):
            nameF = (os.path.splitext(fileN)[0]).split('/')[1]
            #print nameF
            #print nameF[4]
            ext = os.path.splitext(fileN)[1]
            if str(ext) == '.xls':
                if nameF[4] == 'I':
                    miceList, noBarcode, withB = implantTransformCSVxls (fileN, aliquots, errors, option.output)
                elif nameF[4] == 'E':
                    explList = explantTransformCSVxls (fileN, aliquots, errors, option.output)
                elif nameF[4] == 'A':
                    tissueList = tissueTransformCSVxls (fileN, aliquots, errors, option.output)
                        
    checkIE(explList, miceList)
    checkExplD(explList, miceList)
    checkForTissue(explList, tissueList, miceList)
    writeFileMice(option.output, explList, miceList, tissueList)
    print 'mice without barcode: ', noBarcode
    print 'mice with barcode: ', withB
    #print aliquots


if __name__=='__main__':
    main()
