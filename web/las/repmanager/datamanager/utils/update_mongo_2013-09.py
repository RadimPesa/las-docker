#!/usr/bin/python
import sys
#sys.path.append('/home/alessandro/LAS/repositoryManager/trunk/repmanager/')
sys.path.append('/srv/www/repmanager/')
from django.core.management import setup_environ 
import repmanager.settings 
setup_environ(repmanager.settings)
import shutil
import argparse
from __init__ import *



def extractExpression(fRaw, fImputed):
    try:
        
        header = []
        sample_imputed = {}
        samples = {}
        sample_imputedInit = False
        for line in fImputed.split('\n'):
            if len(line) == 0:
                continue
            tokens = line.strip().split('\t')
            if len(tokens) > 2 and len(header)==0:
                i = 0
                for t in tokens:
                    if t.lower() not in ['targetid', 'probeid', 'excluded/imputed']:
                        sample = t.split('.')[0].split('_')[1]
                        sample_imputed[sample] = []
                        sample_imputedInit = True
                        samples[i] = sample
                    i += 1
                header = tokens
            elif len(header):
                i = 0
                probe = ''
                for t in header:
                    if t.lower() == 'probeid':
                        probe = tokens[i]
                    elif t.lower() not in ['targetid', 'excluded/imputed']:
                        if int(tokens[i]) == 1:
                            sample_imputed[samples[i]].append(probe)
                    i += 1
        
    except Exception, e:
        print e

    #print sample_imputed
    #print samples
    try:
        sample_value = {}
        sample_detection = {}
        header = []
        for line in fRaw.split('\n'):
            if len(line) == 0:
                continue
            tokens = line.strip().split('\t')
            if len(tokens) > 2 and len(header)==0:
                i = 0
                for t in tokens:
                    if t.lower() not in ['targetid', 'probeid']:
                        sample = t.split('.')[0].split('_')[1]
                        typeM = t.split('.')[1].split()[0]
                        if typeM.lower() == 'avg_signal':
                            sample_value[sample] = {}
                        elif typeM.lower() == 'detection':
                            sample_detection[sample] = {}                    
                    i += 1
                header = tokens
            elif len(header):
                i = 0
                probe = ''
                for t in header:
                    if t.lower() == 'probeid':
                        probe = tokens[i]
                    elif t.lower() not in ['targetid']:
                        sample = t.split('.')[0].split('_')[1]
                        typeM = t.split('.')[1].split()[0]
                        if typeM.lower() == 'avg_signal':
                            sample_value[sample][probe] = tokens[i]
                        elif typeM.lower() == 'detection':
                            sample_detection[sample][probe] = tokens[i]
                    i += 1
    except Exception, e:
        print e
    return sample_value, sample_detection, sample_imputed



def updateMongo (dataFile):
    print dataFile
    json_data=open(dataFile)

    data = json.load(json_data)
    json_data.close()
    for chip, chipInfo in data.items():
        print chip, chipInfo
        chiprep = UArrayChip.objects.get(id=chip)
        chiprep.hybevent = str(chipInfo['hybevent'])
        chiprep.scan = str(chipInfo['scan'])
        chiprep.save()
        fRaw = None
        fImputed = None
        for fileSource in chiprep.sources:
            print fileSource
            if fileSource.name.lower() == chipInfo['barcode'] + '_imputeddata.txt':
                fImputed = fileSource.resource.read()
            if fileSource.name.lower() == chipInfo['barcode'] + '_rawdata.txt':
                fRaw = fileSource.resource.read()
        if fRaw != None and fImputed != None:
            sample_value, sample_detection, sample_imputed = extractExpression(fRaw, fImputed)
            print sample_imputed
        else:
            raise Exception('File not read')
        for sample in chipInfo['samples']:
            for s, sInfo in sample.items():
                srep = UArraySample.objects.get(id=s)
                print srep.sources
                srep.genid = str(sInfo['genid'])
                srep.position = str(sInfo['pos'])
                print srep.position
                #print sample_value[srep.position]
                #print sample_detection[srep.position]
                #print sample_imputed[srep.position]
                srep.expression = sample_value[srep.position]
                srep.detection = sample_detection[srep.position]
                if sample_imputed.has_key(srep.position):
                    srep.imputed = sample_imputed[srep.position]
                else:
                    srep.imputed = []
                srep.save()

if __name__=='__main__':
    parser = argparse.ArgumentParser(description='Update link of repository')
    parser.add_argument('--input', type=str, help='Input file')
    args = parser.parse_args()
    updateMongo (args.input)
