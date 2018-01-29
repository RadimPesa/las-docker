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

## DEFINITIONS ##

# Dictionaries
sampleInfo = {}
cases = {}         # cases = {case:[samples]}
sample_cases = {}  # sample_cases = {sample:case}
analyses = {}      # analyses = {sample:{SNP:genotype}}
                   # result = {SNP:genotype}
refs = {}          # refs = {type:[sample]}
refs["germline"] = {}
refs["tumor"] = {}
summary_results = {}        # scores = {sample:{ref_type:{ref:score}}}
filtered_results = {}
mismatched_cases = []


scores_to_germlines = {}
scores_to_tumors = {}
scores_to_case = {}
scores_to_all = {}



GermlineTissues = ["NL","NM"]
CancerTissues = ["LM","PR"]

'''
GermlineTissues = ["NLH","NMH"]
CancerTissues = ["LMH","PRH"]
XenoTissues = ["LMX","PRX"]
'''


def gain_score(genotype, refGenotype):
    return sum([ len(set(genotype[i])-set(refGenotype[i])) for i in range(len(genotype))])

def loss_score(genotype, refGenotype):
    return sum([ len(set(refGenotype[i])-set(genotype[i])) for i in range(len(genotype))])

def QCscore(sample, QC_cutoff):
    qcScore = sum([ 1 for v in analyses[sample].values() if v == 'N/A' ])        
    if qcScore > QC_cutoff:
        print sample , ":"
        print "QCscore: ", qcScore
        print "*****"
        print
    return qcScore

def comparison (sample, references, snpsAvailable ):
    if len(references):
        score = dict((x,0) for x in references)
    else:
        return {}
    genotype = [ analyses[sample][snp] if analyses[sample].has_key(snp) else '-' for snp in snpsAvailable ]
    for ref in references:
        if ref != sample:
            ref_genotype = [ analyses[ref][snp] if analyses[ref].has_key(snp) else '-' for snp in snpsAvailable]
            score[ref] = gain_score(genotype, ref_genotype)
    return score

def score_summarization (sample, score_set):                            # summarizes the best matches for all the refs categories
    score_summary={}
    if sample in score_set.keys():
        try:
            min_value = min(score_set[sample].itervalues())
        except:
            min_value = 0
        min_keys = [k for k in score_set[sample] if score_set[sample][k] == min_value]
        score_summary = dict ((i, min_value) for i in min_keys)
    return score_summary

def mismatch_filter (sample, QC_cutoff):
    dsummary = summary_results[sample]
    good_match = 0
    bad_match = 0
    unmatch = 0
    for r in dsummary.keys():
        for ref, value in dsummary[r].items():
            if sample_cases[ref] == sample_cases[sample] and value <= QC_cutoff:
                good_match += 1
            elif sample_cases[ref] == sample_cases[sample] and value > QC_cutoff:
                unmatch += 1
            elif sample_cases[ref] != sample_cases[sample] and value == 0:
                bad_match += 1
    if good_match > 0 and bad_match == 0 and unmatch == 0:
        return "good"
    elif good_match > 0 and (bad_match > 0 or unmatch > 0):
        return "ambiguous"
    elif good_match == 0 and (bad_match > 0 or unmatch > 0):
        return "bad"
    else:
        return "undetermined"

def getSnp():
    snpsAvailable = Datasample_has_Service.objects.all().values_list('param', flat = True).distinct()
    return snpsAvailable


def retrieveData():
    counter = 0

    snps = Datasample_has_Service.objects.filter(idDataSample__in=DataSample.objects.filter(idDataType__in = DataType.objects.filter(name='Sequence'))).values('idDataSample__idSample', 'idDataSample__idSample__idAliquot_has_Request__aliquot_id__genId', 'idDataSample__value', 'param', 'idDataSample__idSample__plate', 'idDataSample__idSample__position')

    for snp in snps:
        sampleID = snp['idDataSample__idSample']           # defines unique samples
        sampleGenId = GenealogyID(snp['idDataSample__idSample__idAliquot_has_Request__aliquot_id__genId'])
        case = sampleGenId.getCase()                                                 # defines case
        if not cases.has_key(case):                                                # generate key for cases in case it doesn't exist
            cases[case] = {}

        if not analyses.has_key(sampleID):
            analyses[sampleID] = {}                                         # generate key for analyses in case it doesn't exist
            sampleInfo[sampleID] = {'genId': sampleGenId.getGenID(), 'plate': snp['idDataSample__idSample__plate'], 'position':snp['idDataSample__idSample__position'], 'id':sampleID}
            counter += 1

        if not sample_cases.has_key(sampleID):                                     # generate key and value for sample_cases
            sample_cases[sampleID] = case

        if not analyses[sampleID].has_key(snp['param']):
            analyses[sampleID][snp['param']] = ''
        analyses[sampleID][snp['param']] = snp['idDataSample__value']                    # assigns results to samples
        
        if  not cases[case].has_key(sampleID):
            cases[case][sampleID] = 1                                                # populates cases with samples
                         
        if sampleGenId.getTissue() in GermlineTissues and not refs["germline"].has_key(sampleID) :    # assingns references
            refs["germline"][sampleID] = 1
        elif sampleGenId.getTissue() in CancerTissues and not refs["tumor"].has_key(sampleID):
            refs["tumor"][sampleID] = 1
        
    return counter


def writeInfo(fout, results):
    if len(results):
        fout.write('{')
        for item, value in results.items():
            fout.write(sampleInfo[item]['genId'] + '-' + sampleInfo[item]['plate'] + '-' + sampleInfo[item]['position'] + ':' + str(value) + ' ')
        fout.write('}\t')


  
def main(args):
    startTime1 = datetime.datetime.now()
    file_out = open ("summary_results.txt", "w")
    file_out2 = open ("mismatch_samples.txt", "w")
    QC_cutoff = args.cutoff
    
    
    startTime = datetime.datetime.now()
    counter = retrieveData()
    snpsAvailable = getSnp()
    print datetime.datetime.now() -startTime
    startTime = datetime.datetime.now()
    print
    print "Total samples read: ", counter
    print len(analyses.keys()) , "GermlineRefs: ", len(refs["germline"]), "TumorRefs: ", len(refs["tumor"]), "Cases: ", len(cases.keys())
    print "------------------------------"

    QC_count = 0
    badQC_count = 0
    goodQC_count = 0

    for sample in analyses.keys():
        QC_value = QCscore(sample, QC_cutoff)
        QC_count += 1
        if QC_value > QC_cutoff :
            badQC_count += 1
            del analyses[sample]                                                    # elimintes low QC samples from analyses
            if refs["germline"].has_key(sample):
                del refs["germline"][sample]                                 # eliminates low QC samples from refs
            elif refs["tumor"].has_key(sample):
                del refs["tumor"][sample]
            del cases[sample_cases[sample]][sample]
                    
        else:
            goodQC_count += 1
        if QC_count % 500 == 0:
            print QC_count, " QC tests executed, "
            print "-------------"

    print datetime.datetime.now() -startTime
    startTime = datetime.datetime.now()

    print "Total number of Samples analyzed: ", (goodQC_count + badQC_count)
    print "Total number of Samples excluded from analysis: ", badQC_count
    print "Good QC samples: ", len(analyses) , "GermlineRefs: ", len(refs["germline"]), "TumorRefs: ", len(refs["tumor"]), "Cases: ", len(cases)
    print "--------------------------------"


    # mismatch calculations

    comparison_count = 0
    comparison_case = 0
    comparison_all = 0
    mismatch_count = 0

    setRefGermTum = set(refs["germline"].keys()) | set(refs["tumor"].keys())
    for sample in analyses.keys():
        
        scores_to_germlines[sample]={}                                           # defines a score for germline references
        scores_to_tumors[sample]={}                                              # defines a score for tumor references                                                  
                
        sample_case = sample_cases[sample]
            
        if ( setRefGermTum & set(cases[sample_case].keys()) == 0) or (refs["germline"].has_key(sample)) or (refs["tumor"].has_key(sample)):
            #print datetime.datetime.now() -startTime
            #startTime = datetime.datetime.now()
            if len(cases[sample_case]) > 1:
                scores_to_case[sample] = comparison(sample, cases[sample_case],snpsAvailable )
                comparison_case += 1
            else:
                scores_to_all[sample] = comparison(sample, analyses.keys(), snpsAvailable )
                comparison_all += 1
        
        #print '1st'
        #print datetime.datetime.now() -startTime
        #startTime = datetime.datetime.now()

        scores_to_germlines[sample] = comparison(sample, refs["germline"].keys(), snpsAvailable )
        
        #print '2nd'
        #print datetime.datetime.now() -startTime
        #startTime = datetime.datetime.now()
        
        scores_to_tumors[sample] = comparison(sample, refs["tumor"].keys(), snpsAvailable )
        
        #print '3rd'
        #print datetime.datetime.now() -startTime
        #startTime = datetime.datetime.now()

        comparison_count += 1
        if comparison_count % 100 == 0:
            print comparison_count , "comparisons executed"
        
        # if mismatches to references > admitted NAs (QC_cutoff) score_to_all is calculated   

        if sample not in scores_to_all.keys():
            if sample in scores_to_case.keys():
                listScoreCase = scores_to_case[sample].values()
                if len(listScoreCase):
                    if min(listScoreCase) > QC_cutoff:
                        mismatch_count += 1
                        comparison_all += 1
                        scores_to_all[sample] = comparison(sample, analyses.keys()) 
            listScoreGerm = scores_to_germlines[sample].values()
            listScoreTum = scores_to_tumors[sample].values()
            if len(listScoreGerm) and len(listScoreTum):
                if min(listScoreGerm) > QC_cutoff and min(listScoreTum) > QC_cutoff and sample not in scores_to_all.keys():
                    scores_to_all[sample] = comparison(sample, analyses.keys())
                    mismatch_count += 1
                    comparison_all += 1
        #print datetime.datetime.now() -startTime
        #startTime = datetime.datetime.now()


    print datetime.datetime.now() -startTime
    startTime = datetime.datetime.now()

    print "--------------------------------"                                    # summarizes aggreated results (maybe to be printed in file)
    print "****----DATA SUMMARY--------****"

    print "Total number of Samples analyzed: ", "\t",(goodQC_count + badQC_count)
    print "Total number of Samples excluded from analysis: ", "\t", badQC_count
    print "Good QC samples: ", "\t", len(analyses.keys()) , "\t", "GermlineRefs: ", "\t", len(refs["germline"]), "TumorRefs: ", len(refs["tumor"]), "Cases: ", len(cases.keys())
    print "--------------------------------"
    print "--------------------------------"
    print "Total number of comparisons computed: ", "\t",comparison_count, "\t"," - to case: ", "\t",comparison_case, "\t"," - to all: ", "\t",comparison_all
    print "--------------------------------"
    print "Number of mismatches found: ", "\t",mismatch_count


    # data summary, samples classification & reports

    print datetime.datetime.now() -startTime
    startTime = datetime.datetime.now()

    file_out.write("sample"+"\t"+"to_germline"+"\t"+"to_tumor"+"\t"+"to_case"+"\t"+"to_all"+"\n")

    for sample in analyses.keys():
        summary_results[sample]={}
        summ = summary_results[sample]
        file_out.write(str(sampleInfo[sample]['id']) + '-' + sampleInfo[sample]['genId'] + '-' + sampleInfo[sample]['plate'] + '-' + sampleInfo[sample]['position'] + "\t")
        summary_results[sample]["ref_germlines"] = score_summarization(sample, scores_to_germlines)
        writeInfo(file_out, summary_results[sample]["ref_germlines"])
        summary_results[sample]["ref_tumors"] = score_summarization(sample, scores_to_tumors)
        writeInfo(file_out, summary_results[sample]["ref_tumors"])
        summary_results[sample]["case_samples"] = score_summarization(sample, scores_to_case)
        writeInfo(file_out, summary_results[sample]["case_samples"])
        summary_results[sample]["all_samples"] = score_summarization(sample, scores_to_all)
        writeInfo(file_out, summary_results[sample]["all_samples"])
        file_out.write('\n')
        
    file_out2.write("sample"+"\t"+"to_tumor"+"\t"+"to_germline"+"\t"+"to_case"+"\t"+"to_all"+"\n")

    print datetime.datetime.now() -startTime
    startTime = datetime.datetime.now()

    filtered_results = {sample:results for sample, results in summary_results.items() if mismatch_filter(sample, QC_cutoff)== "bad"}
    # print filtered_results
    filtered_report = 0
    for sample in filtered_results.keys():
        if sample_cases[sample] not in mismatched_cases:
            mismatched_cases.append(sample_cases[sample])
        file_out2.write(str(sampleInfo[sample]['id']) + '-' +sampleInfo[sample]['genId'] +  '-' + sampleInfo[sample]['plate'] + '-' + sampleInfo[sample]['position'] + "\t")
        writeInfo(file_out2, filtered_results[sample]["ref_tumors"])
        writeInfo(file_out2, filtered_results[sample]["ref_germlines"])
        writeInfo(file_out2, filtered_results[sample]["case_samples"])
        writeInfo(file_out2, filtered_results[sample]["all_samples"])
        file_out2.write("\n")
        filtered_report += 1
        print "Mismatch n.", filtered_report, ": ", sampleInfo[sample]['genId'], '-', sampleInfo[sample]['plate'], '-', sampleInfo[sample]['position']
        
        
    print "number of mismatched samples: ", len(filtered_results.keys())
    print "number of mismatched cases: ", len(mismatched_cases)
    print "Analyses completed. Find results in: ", file_out.name, "and", file_out2.name
    file_out.close()
    file_out2.close()

    print datetime.datetime.now() - startTime
    print datetime.datetime.now() - startTime1


if __name__=='__main__':
    parser = argparse.ArgumentParser(description='Update fingerPrinting aliquots')
    parser.add_argument('--cutoff', type=int, help='QC cutoff')
    args = parser.parse_args()
    main(args)