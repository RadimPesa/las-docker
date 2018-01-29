import sys
sys.path.append('/home/alessandro/LAS/uArray/trunk/src/uAMM/')
#sys.path.append('/srv/www/uarray/')
from django.core.management import setup_environ 
import settings 
setup_environ(settings)
import shutil
import argparse
from __init__ import *
import json
import ast
import datetime


@transaction.commit_manually
def insertChip(barcode, ctype, toscan):
    try:
        chip = Chip.objects.filter(barcode=barcode)
        if chip:
            chip = chip[0]
            if toscan:
                toscan = False
        else:
            chip = Chip(barcode=barcode, expirationDate=datetime.date.today(), idChipType=ctype)
            chip.save()
        transaction.commit()
        return chip, toscan
    except Exception, e:
        print 'Exception insertChip ', e
        transaction.rollback()
        return None
    finally:
        transaction.rollback()


def readMetrics(scaneventInfo, resource):
    fin = open (resource, 'r')
    fin.readline()
    i = 0
    endtime = None
    for line in fin:
        tokens = line.strip().split('\t')
        try:
            timestamp = datetime.datetime.strptime(tokens[0], '%m/%d/%Y %I:%M:%S %p')
        except:
            try:
                timestamp = datetime.datetime.strptime(tokens[0], '%d/%m/%Y %H:%M:%S')
            except:
                raise Exception
        if i == 0:
            scaneventInfo['starttime'] = timestamp
        i += 1
        endtime = timestamp
    scaneventInfo['endtime'] = endtime
    fin.close()
    return 


@transaction.commit_manually
def insertScanevent (fMetrics, chipScanned, operator, PMFactor):
    try:
        scaneventInfo = {}
        readMetrics(scaneventInfo, fMetrics)
        #print scaneventInfo
        #print 'ScanProtocol '+ str(PMFactor)
        protocol = ScanProtocol.objects.get(name = 'ScanProtocol '+ str(PMFactor))
        #print protocol
        scanevent = ScanEvent(idProtocol = protocol, startScanTime=scaneventInfo['starttime'], endScanTime=scaneventInfo['endtime'], idOperator=operator, validated=True)
        scanevent.save()
        chipScan = Chip_has_Scan(idChip=chipScanned, idScanEvent=scanevent, posonscanner=1)
        chipScan.save()
        assignmentAl = Assignment.objects.filter(idChip=chipScanned)
        for al in assignmentAl:
            alScanned = Assignment_has_Scan(idAssignment = al, idScanEvent = scanevent)
            alScanned.save()
        #raise Exception('no save')
        transaction.commit()
        return
    except Exception, e:
        print 'Exception insertScanevent ', e
        transaction.rollback()
        return None
    finally:
        transaction.rollback()


def searchProt (chipScanned, prot):
    chipscans = Chip_has_Scan.objects.filter(idChip=chipScanned)
    protName = ''
    for cs in chipscans:
        if 'ScanProtocol ' + prot == cs.idScanEvent.idProtocol.name:
            protName = prot
            print chipScanned.barcode, ' -> hybevent ', chipScanned.idHybevent
            break
    return protName


def createChip(operator, ifolder):
    justScanned = {}
    for chip_type in os.listdir(ifolder):
        ctype = ChipType.objects.get(title=chip_type)
        #print ctype
        for chip in os.listdir(os.path.join(ifolder, chip_type)):
            chipScanned, toscan = insertChip(chip.strip().split('_')[0], ctype, True)
            if not toscan:
                prot = searchProt (chipScanned, chip.strip().split('_')[1])
                if prot != '':
                    if not justScanned.has_key(chipScanned.barcode):
                        justScanned[chipScanned.barcode] = []
                    justScanned[chipScanned.barcode].append(prot)
    print justScanned
    return justScanned


def scanChip(operator, ifolder, justScanned):
    for chip_type in os.listdir(ifolder):
        ctype = ChipType.objects.get(title=chip_type)
        #print ctype
        for chip in os.listdir(os.path.join(ifolder, chip_type)):
            #print chip
            chipScanned, toscan = insertChip(chip.strip().split('_')[0], ctype, False)
            if chipScanned:
                #print 'chip in db: ', chipScanned
                if justScanned.has_key(chipScanned.barcode):
                    if chip.strip().split('_')[1] in justScanned[chipScanned.barcode]:
                        print 'Not scanned ' , chipScanned.barcode, chip.strip().split('_')[1]
                        toscan = True
                if not toscan:
                    insertScanevent (os.path.join(ifolder, chip_type, chip, 'Metrics.txt'), chipScanned, operator, chip.strip().split('_')[1])


@transaction.commit_manually
def hybridChips(operator, chipInfo, justScanned):
    try:
        request = Request (idOperator = operator, timestamp = datetime.datetime.now(), title = 'Recovery historical data', owner = 'andrea.bertotti', pending = False)
        request.save()
        for chipBarcode, chipData in chipInfo.items():
            if chipBarcode in justScanned.keys():
                continue
            chip = Chip.objects.get(barcode=chipBarcode)
            geometry = ast.literal_eval(chip.idChipType.layout.rules)
            hybprot = HybProtocol.objects.get(id=chipData['hybprot'])
            instrument = Instrument.objects.get(id=2)
            hyb_timestamp = datetime.datetime.strptime(chipData['hybDate'], '%d/%m/%Y')
            hybevent = HybridPlan(idHybProtocol = hybprot, idInstrument = instrument, idOperator = operator, timeplan = hyb_timestamp, timecheck=hyb_timestamp, timehybrid= hyb_timestamp)
            hybevent.save()
            chip.idHybevent = hybevent
            chip.save()
            for al, pos in chipData['samples'].items():
                aliquot = Aliquot.objects.filter(genId=al)
                replicate = False
                if aliquot:
                    aliquot = aliquot[0]
                else:
                    aliquot = Aliquot(genId=al, exhausted=False, volume=0, concentration=0) #disregard the vol and conc
                    aliquot.save()
                alReqExist = Aliquot_has_Request.objects.filter(aliquot_id=aliquot, request_id=request)
                if alReqExist:
                    print 'replicate', aliquot.genId
                    replicate = True
                alReq = Aliquot_has_Request(aliquot_id = aliquot, request_id = request, tech_replicates = replicate, idHybPlan=hybevent)
                alReq.save()
                numberPos = -1
                for idPos, label in geometry.items():
                    if label == pos:
                        numberPos = idPos
                        break
                if numberPos == -1:
                    raise Exception('error in converting the position')
                assignmentAl = Assignment(idChip = chip, position = numberPos, idAliquot_has_Request = alReq)
                assignmentAl.save()

        transaction.commit()
    except Exception, e:
        print 'Exception hybridChips ', e
        transaction.rollback()
    finally:
        transaction.rollback()
    return

def retrieveChipInfo (hybFile):
    fin = open (hybFile)
    i = 0
    chipInfo = {}

    try:
        for line in fin:
            if i==0:
                i+=1
                continue
            tokens = line.strip().split('\t')
            if len(tokens)<4:
                continue
            barcode = tokens[0].split('_')[0]
            sample = tokens[0].split('_')[1]
            genid = tokens[2]
            hybDate = tokens[3]
            if not chipInfo.has_key(barcode):
                chipInfo[barcode] = {'samples':{}, 'hybDate':hybDate}
            if chipInfo[barcode]['hybDate'] != hybDate:
                raise Exception('Hyb date for chip ' +  barcode + ' not coherent')
            chipInfo[barcode]['samples'][genid] = sample
        fin.close()
        return chipInfo

    except Exception, e:
        print 'Exception retrieveChipInfo ', e
        fin.close()
        return {}

    

def checkExist (chipInfo, ifolder):
    chipsScanned = {}
    chipsWithInfo = set(chipInfo.keys())
    for chip_type in os.listdir(ifolder):
        ctype = ChipType.objects.get(title=chip_type)
        sampleLabels = ast.literal_eval(ctype.layout.rules)
        for chip in os.listdir(os.path.join(ifolder, chip_type)):
            if not chipsScanned.has_key(chip.strip().split('_')[0]):
                chipsScanned[chip.strip().split('_')[0]] = sampleLabels
            if chipInfo.has_key(chip.strip().split('_')[0]):
                if not chipInfo[chip.strip().split('_')[0]].has_key('hybprot'):
                    if chip_type == 'MouseWG-6 V2':
                        prot = HybProtocol.objects.get(id=2)
                    else:
                        prot = HybProtocol.objects.get(id=1)
                    chipInfo[chip.strip().split('_')[0]]['hybprot'] = prot.id
    
    chipsScannedSet = set(chipsScanned.keys())
    print 'Check'
    print 'Chip scanned without information:'
    for i in chipsScannedSet.difference(chipsWithInfo):
        print i

    print 'Chip with information not scanned:'
    for i in chipsWithInfo.difference(chipsScannedSet):
        print i

    chipsOk = chipsScannedSet.intersection(chipsWithInfo)
    incoherentGeo = []

    print 'Chips without problems'
    for i in chipsOk:
        #print set(chipInfo[i]['samples'].values()).intersection(set(chipsScanned[i].values()))
        if set(chipInfo[i]['samples'].values()).difference(set(chipsScanned[i].values())):
            incoherentGeo.append(i)
    #    else:
    #        print i
    

    print 'No geometry match for chip '
    for i in incoherentGeo:
        print i



# scan the folder of uploaded chips, update links and remove the folder if all the files are saved in the repository
if __name__=='__main__':
    parser = argparse.ArgumentParser(description='Load beaming experiments')
    parser.add_argument('--ifolder', type=str, help='Input folder with uarray experiments')
    parser.add_argument('--hyb', type=str, help='Input file with hybridization event')
    parser.add_argument('--chips', type=bool, default=False, help='Create chips and scan event')
    args = parser.parse_args()
    
    operator = User.objects.get (username = 'roberta.porporato')
    chipInfo = retrieveChipInfo (args.hyb)
    checkExist (chipInfo, args.ifolder)
    print chipInfo
    print '-------------------------------'
    if args.chips:
        justScanned = createChip(operator, args.ifolder)
        hybridChips(operator, chipInfo, justScanned)
        scanChip(operator, args.ifolder, justScanned)

    
    



        
