import sys
sys.path.append('/home/alessandro/LAS/fingerprintingManager/trunk/fingerprinting/')
#sys.path.append('/srv/www/fingerprinting/')
from django.core.management import setup_environ 
import fingerprinting.settings 
setup_environ(fingerprinting.settings)
import shutil
import argparse
from __init__ import *
import locale
locale.setlocale( locale.LC_ALL, 'en_US.UTF-8' ) 



def readMeasures (exp):
    header = True
    listMeasure = []
    positions = {}
    mutations = {}
    aliquots = {}

    fin = open(exp)
    for line in fin:
        tokens = line.strip().split('\t')
        print tokens, len(tokens)
        if len(tokens) == 1: # line between samples
            header = True
        else:
            if header: # retrieve the header of the measures and the sample info
                sample_info = tokens[0].split(':')[1].strip().split()
                print sample_info
                # remove zeros after letters
                posParsed = ''
                firstZero = True
                for i in sample_info[0]:
                    if not i.isdigit():
                        posParsed += i
                    elif int(i) == 0 and firstZero == True:
                        pass
                    else:
                        firstZero = False
                        posParsed += i
                if positions.has_key(posParsed):
                    raise Exception
                positions[posParsed] = {}
                positions[posParsed]['acquired'] = True
                sampleData = tokens[0].split(':')[2].strip().split()[0]
                genId = sampleData.split('|')[0]
                if not aliquots.has_key(genId):
                    aliquots[genId] = {'samples':{}}
                aliquots[genId]['samples'][posParsed] = {'measures':[], 'gene':sampleData.split('|')[1], 'mut':sampleData.split('|')[2]}
                if not mutations.has_key(sampleData.split('|')[1]):
                    mutations[sampleData.split('|')[1]] = {'mut':{}}
                mutations[sampleData.split('|')[1]]['mut'][sampleData.split('|')[2]] = ''
                print sampleData
                for t in tokens[1:]:
                    mType = Measure.objects.get(name=t)
                    listMeasure.append(mType)
                header = False
            else:
                i = 1
                for m in listMeasure: # identify all the measure for which there is a value (missing value at the end are discarded)
                    if len(tokens) > i:
                        mvalue = tokens[i]
                        if m.unity_measure != '':
                            mvalue = mvalue.replace(m.unity_measure,'')
                        try:
                            region = Region.objects.get(code=tokens[0].upper())
                        except:
                            aliasreg = AliasRegion.objects.get(name=tokens[0].upper())
                            region = aliasreg.idRegion
                        mt = MeasureType.objects.get(idMeasure=m.id, region=region.id)
                        measure = {'mtypeid':mt.id, 'mtype':m.name, 'munity': m.unity_measure, 'mvalue': locale.atof(mvalue), 'mregionid': region.id, 'mregion': region.code}
                        measure.update(positions[posParsed])
                        aliquots[genId]['samples'][posParsed]['measures'].append(measure)
                    else:
                        break
                    i += 1
    print positions
    pos = [v for k, v in positions.items() if v == False]
    if len(pos):
        raise Exception
    '''
    for genid, samples in aliquots.items():
        print genid
        for k, v in samples['samples'].items():
            print k, v
            print '------'
    '''
    return aliquots, mutations




@transaction.commit_manually
def insertExperiment(exp,absPath, operator, alVolume, instrument):
    try:
        expDate, extension = os.path.splitext(exp)
        print expDate
        timestampExp = datetime.datetime.strptime(expDate + 'T00:00:00', '%Y-%m-%dT%H:%M:%S')
        aliquots, mutations = readMeasures (os.path.join(absPath, exp))
        request = Request (idOperator = operator, timestamp = timestampExp, title = 'Request_' + str(expDate), owner = 'giulia.siravegna', pending = False, timechecked = timestampExp, time_executed = timestampExp)
        request.save()

        experiment = Experiment(time_creation = timestampExp, time_executed = timestampExp, idInstrument = instrument, idOperator = operator)
        experiment.save()


        # retrieve info of aliquots
        aliq_biobank = '&'.join(aliquots.keys())
        res = retrieveAliquots (aliq_biobank, operator.username) 
        print res
        for d in res['data']:
            values = d.split("&")
            if values[1] != 'notexist':
                aliquots[values[0]]['volume'] = values[1]
                aliquots[values[0]]['concentration'] = values[2]
                aliquots[values[0]]['date'] = values[3]
            else:
                raise Exception('aliquot non present: ' + str(values[0]))
        
        #retrieve gene and mutations

        geneSymbols =  mutations.keys()
        genes = retrieveGeneSymbols (geneSymbols)
        i = 0
        for g in geneSymbols:
            mutations[g]['id_gene'] = genes[i]['id_gene']
            for mut in mutations[g]['mut'].keys():
                resp = mutationFromCDSSyntax (g, 'c.'+ mut)
                if len(resp) == 1:
                    mutations[g]['mut'][mut] = resp[0]['id_mutation']
                else:
                    raise Exception('No mutation ' + mut + ' found for gene ' + g )
            i+=1
        print mutations    

        # insert experimtn samples
        values_to_send = {'info':[], 'exhausted':[]}
        for genid, values in aliquots.items():
            print values
            al = Aliquot.objects.filter(genId=genid)
            if al:
                al = al[0]
            else:
                al = Aliquot(genId=genid)
            al.concentration = float(values['concentration'])
            al.volume = float(values['volume'])-float(alVolume[genid])
            al.date = values['date']
            al.save()
            values_to_send['info'].append(al.genId+"&"+ operator.username + "&" + str(al.volume))
            al_req = Aliquot_has_Request (aliquot_id = al, request_id = request, volumetaken = float(alVolume[genid]))
            al_req.save()
            for pos, sampleInfo in values['samples'].items():
                s = Sample (position = pos, probe = mutations[sampleInfo['gene']]['mut'][sampleInfo['mut']] , gene = mutations[sampleInfo['gene']]['id_gene'], idAliquot_has_Request = al_req, idExperiment = experiment )
                s.save()
                for measure in sampleInfo['measures']:
                    mevent = MeasurementEvent (value = measure['mvalue'], idSample = s, idMeasureType = MeasureType.objects.get(id = measure['mtypeid']),  idExperiment = experiment)
                    mevent.save()
        if len(values_to_send['info']) != 0:
            data = urllib.urlencode(values_to_send)
            try: #update info for the aliquots
                updateAliquots(data)
                setExperiment(alVolume.keys())
            except:
                print "[LBM] - Biobank Unreachable"
                transaction.rollback()
                return False
        #raise Exception ('No save')
        
        transaction.commit()
    except Exception, e:
        print 'Exception', e
        transaction.rollback()
        return False
    finally:
        transaction.rollback()
    return True


def removeExp(exp, absPath):
    os.remove( os.path.join(absPath,exp) )
    return


def readVolumes (alFile):
    fin = open (alFile)
    alVolume = {}
    for line in fin:
        tokens = line.strip().split('\t')
        alVolume[tokens[0]] = float(tokens[1])

    fin.close()
    return alVolume


# scan the folder of uploaded chips, update links and remove the folder if all the files are saved in the repository
if __name__=='__main__':
    parser = argparse.ArgumentParser(description='Load fingerprinting experiments')
    parser.add_argument('--ifolder', type=str, help='Input folder with fingerprinting experiments')
    parser.add_argument('--aliquots', type=str, help='Input file with aliquot taken volume')
    args = parser.parse_args()
    
    savedExperiments = []
    absPath = os.path.abspath(args.ifolder)

    operator = User.objects.get (username = 'giulia.siravegna')
    instrument = Instrument.objects.get(id=1)
    print absPath
    alVolume = readVolumes (args.aliquots)
    for exp in os.listdir(args.ifolder):
        print datetime.datetime.now()
        if insertExperiment(exp, absPath, operator, alVolume, instrument):
            savedExperiments.append(exp)
    '''
    for exp in savedExperiments:
        removeExp(exp,absPath)
    ''