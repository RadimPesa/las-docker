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


def retrieveCall (sample):
    data = DataSample.objects.filter(idSample=sample, idDataType__in = DataType.objects.filter(name='Sequence')).exclude(value='N/A')
    snp = Datasample_has_Service.objects.filter(idDataSample__in=data).order_by('param')
    calls = {}
    for s in snp:
        if not calls.has_key(s.param):
            calls[s.param] = ''
        calls[s.param] += s.idDataSample.value
    if len(calls.keys()):
        print calls
    else:
        print 'No snp available'
    return calls



def cal_score(genotype, refGenotype):
    if len (set(genotype)-set(refGenotype))>0:
        return 1
    else:
        return 0  


def computeSimilarity(calls):
    i = 0
    scores = []
    for genotype in calls[i:len(calls)]:
        for refGenotype in calls[i+1:len(calls)]:
            score = 0
            for snp, genvalue in genotype.items():
                if refGenotype.has_key(snp):
                    score += cal_score(genvalue, refGenotype[snp])
            scores.append(score)
            score = 0
            for snp, genvalue in refGenotype.items():
                if genotype.has_key(snp):
                    score += cal_score(genvalue, genotype[snp])
            scores.append(score)
        i+=1
    return min(scores)




@transaction.commit_manually
def updateGenealogy(fileName):
    try:
        duplicated = 0
        mismatch = 0
        fin = open (fileName, 'r')
        for line in fin:
            tokens = line.strip().split('\t')
            aliquot = Aliquot.objects.get(genId=tokens[0].strip())
            aliquot.genId = tokens[1].strip()
            try:
                aliquot.save()
            except Exception, e:
                print 
                print tokens[1]
                samples = Sample.objects.filter(idAliquot_has_Request__in=Aliquot_has_Request.objects.filter(aliquot_id=aliquot))
                calls = []
                for s in samples:
                    print tokens[0] , s.id, s.plate ,  s.position
                    calls.append( retrieveCall(s) )
                
                samples = Sample.objects.filter(idAliquot_has_Request__in=Aliquot_has_Request.objects.filter(aliquot_id=Aliquot.objects.get(genId=tokens[1].strip()) ) )

                for s in samples:
                    print tokens[1] , s.id, s.plate , s.position
                    calls.append( retrieveCall(s) )
                    
                score = computeSimilarity(calls)
                if score:
                    print 'Mismatch fingerprinting with minimum score: ', score
                    mismatch += 1
                else: 
                    print 'Same aliquot'
                duplicated += 1
                continue

        print 
        print 'Duplicated entries: ', duplicated
        print 'Mismatched entries: ', mismatch
        transaction.rollback()
        #transaction.commit()
    except Exception, e:
        print e
        transaction.rollback()

    return

if __name__=='__main__':
    parser = argparse.ArgumentParser(description='Update fingerPrinting aliquots')
    parser.add_argument('--ifile', type=str, help='Input file')
    args = parser.parse_args()
    
    updateGenealogy(args.ifile)
    