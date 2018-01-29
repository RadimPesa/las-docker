import sys
sys.path.append('/srv/www/fingerPrinting/')
from django.core.management import setup_environ 
import fingerprinting.settings 
setup_environ(fingerprinting.settings)
import shutil
import argparse
from __init__ import *
import json
import ast
import datetime

# remove the folder of scanned chip
def removeFiles(f):
    print 'Removing file ', str(f)
    #shutil.rmtree(f)

@transaction.commit_manually
def insertRequest(operator):
    try:
        req = Request(idOperator= operator, timestamp=datetime.datetime.now(), title='Recover data', pending = False, owner = operator.username)
        #raise Exception('interruzione volontaria')
        req.save()
        transaction.commit()
        print req
        return req
    except Exception, e:
        print e
        transaction.rollback()
        return None


@transaction.commit_manually
def insertAliquot(genId, request):
    try:
        print 'Insert Aliquot_has_Request', genId, request
        al = Aliquot.objects.filter(genId=genId)
        if al:
            al = al[0]
        else:
            al = Aliquot(genId=genId)
            al.save()
        al_req = Aliquot_has_Request(aliquot_id=al, request_id=request)
        al_req.save()
        transaction.commit()
        return al_req
    except Exception, e:
        print e
        transaction.rollback()
        return None
    finally:
        transaction.rollback()


@transaction.commit_manually
def retrieveData(fileRes, operator):
    try:
        wb = load_workbook(fileRes, use_iterators = True)

        plates = [x.replace('24SNP_', '') for x in wb.get_sheet_names()]
        print 'Analyzing plates ', plates
        samples = {}
        results = []
        serviceAnn = Service.objects.get(name='annotation SNP')
        alleleA = {'cat': DataCategory.objects.get(name='Allele A'), 'call': DataType.objects.get(idCategory = DataCategory.objects.get(name='Allele A'), name='Sequence'), 'freq': DataType.objects.get(idCategory = DataCategory.objects.get(name='Allele A'), name='Frequency')}
        alleleB = {'cat': DataCategory.objects.get(name='Allele B'), 'call': DataType.objects.get(idCategory = DataCategory.objects.get(name='Allele B'), name='Sequence'), 'freq': DataType.objects.get(idCategory = DataCategory.objects.get(name='Allele B'), name='Frequency')}

        for ws in wb:
            header = 0
            currPlate = ws.title.replace('24SNP_', '')
            request = insertRequest(operator)
            print currPlate
            #samplePlate = []
            for row in ws.iter_rows():
                cells = [cell.internal_value for cell in row]
                print cells
                if len(row)- cells.count(None) == 0:
                    break
                if header < 2:
                    header += 1
                    continue
                if cells[0] == cells[3]:
                    continue
                if not samples.has_key(cells[0]):
                    print samples.has_key(cells[0]), cells[0], cells[3]
                    try:
                        samples[cells[0]] = insertAliquot(cells[0], request)
                        print samples[cells[0]]
                    except Exception, e:
                        print 'Error', e
                        continue
                print 'End row'
                
                alleles = evaluateAllele (alleleA, alleleB, cells[1])
                position = normalizePosition(cells[3])
                for al in alleles:
                    results.append([samples[cells[0]].id, currPlate, position, cells[0]] + al + [serviceAnn.id, cells[2] ] )
                print 'End append results'
                #samplePlate.append( (cells[0], position) )

        print 'Experiment definition'
        plan = Experiment(time_creation=datetime.datetime.now(), time_executed=datetime.datetime.now(), idOperator=operator)
        plan.save()
        
        
        
        'Init save data'
        for aliquot_info in results:
            print aliquot_info
            alReq = Aliquot_has_Request.objects.get(id=aliquot_info[0])
            try:
                aliquot = Sample.objects.get(idAliquot_has_Request=alReq, position=aliquot_info[2], plate=aliquot_info[1])
            except Exception, e:
                print 'Error query', e 
                aliquot = Sample(idAliquot_has_Request=alReq, position=aliquot_info[2], plate=aliquot_info[1])
                aliquot.save()
            print alReq
            alReq.time_executed = datetime.datetime.now()
            alReq.save()
                
            dataType = DataType.objects.get(id=aliquot_info[5])
            dataSample = DataSample(value = aliquot_info[7], idSample = aliquot, idDataType = dataType, idExperiment = plan)
            dataSample.save()
            dataAssociated = Datasample_has_Service(idDataSample=dataSample, idService=Service.objects.get(id=aliquot_info[8]), param=aliquot_info[9])
            dataAssociated.save()
        
        transaction.commit()
    except Exception, e:
        print 'General exception', e
        transaction.rollback()
    finally:
        transaction.rollback()

    return True

def normalizePosition(position):
    # remove zeros after letters
    posParsed = ''
    firstZero = True
    for i in position:
        if not i.isdigit():
            posParsed += i
        elif int(i) == 0 and firstZero == True:
            pass
        else:
            firstZero = False
            posParsed += i  
    return posParsed


def evaluateAllele (alleleA, alleleB, call):
    #print call
    try:
        call = call.strip()
    except:
        call = 'failed'

    if call.lower() == 'failed':
        return [ [ alleleA['cat'].name, alleleA['call'].id, alleleA['call'].name, 'N/A'], [ alleleA['cat'].name, alleleA['freq'].id, alleleA['freq'].name, 0]  ]
    if len(call) == 1:
        return [ [ alleleA['cat'].name, alleleA['call'].id, alleleA['call'].name, call], [ alleleA['cat'].name, alleleA['freq'].id, alleleA['freq'].name, 1]  ]
    if len(call) == 2:
        return [ [ alleleA['cat'].name, alleleA['call'].id, alleleA['call'].name, call[0]], [ alleleA['cat'].name, alleleA['freq'].id, alleleA['freq'].name, 0.5], [ alleleB['cat'].name, alleleB['call'].id, alleleB['call'].name, call[1]], [ alleleB['cat'].name, alleleB['freq'].id, alleleB['freq'].name, 0.5] ]
    if len(call) > 2:
        tokens = call.split('/')
        callA = tokens[0].strip()
        callB = tokens[1].strip().replace(callA, '')
        return [ [ alleleA['cat'].name, alleleA['call'].id, alleleA['call'].name, callA], [ alleleA['cat'].name, alleleA['freq'].id, alleleA['freq'].name, 0.66], [ alleleB['cat'].name, alleleB['call'].id, alleleB['call'].name, callB], [ alleleB['cat'].name, alleleB['freq'].id, alleleB['freq'].name, 0.33] ]

    return []

# scan the folder of uploaded chips, update links and remove the folder if all the files are saved in the repository
if __name__=='__main__':
    parser = argparse.ArgumentParser(description='Load fingerPrinting experiments')
    parser.add_argument('--ifolder', type=str, help='Input folder with fingerPrinting experiments')
    parser.add_argument('--operator', type=str, help='Operator username')
    args = parser.parse_args()
    
    operator = User.objects.get (username = args.operator)
    fileRecovered = []
    print '-------------------------------'
    for fileRes in os.listdir(args.ifolder):
        print fileRes
        if retrieveData(os.path.join(args.ifolder, fileRes), operator):
            fileRecovered.append(fileRes)

    print '-------------------------------'
    for f in fileRecovered:
        removeFiles(os.path.join(os.path.abspath(args.ifolder),f))


    
    