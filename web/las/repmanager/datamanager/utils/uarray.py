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


# update link field of all the assignments
def updateAssignment(scanevent, chip, samples, chipInfo):
    try:
        data = {'scanevent':scanevent, 'chip':chip, 'samples':samples, 'link':chipInfo}
        print data
        data = urllib.urlencode(data)
        uarrayUrl = Urls.objects.get(id_webservice=WebService.objects.get(name='uarray').id, available=True)
        u = urllib2.urlopen(uarrayUrl.url + "api.updatesamples", data)
        res=u.read()
        res=ast.literal_eval(res)
        if res['status'] == 'Failed':
            raise Exception('not saved')
        print res
    except Exception, e:
        print e
        return


# get the chip geometry
def getChipLayout(chip):
    try:
        uarrayUrl = Urls.objects.get(id_webservice=WebService.objects.get(name='uarray').id, available=True)
        print uarrayUrl.url + "api.getchip/"+ chip + "/scanevent"
        u = urllib2.urlopen(uarrayUrl.url + "api.getchip/"+ chip + "/scanevent")
        res=u.read()
        res=ast.literal_eval(res)
        print res
        return res
    except Exception, e:
        print e
        return


# read metrics file to retrieve the scanevent information
def readMetrics(scaneventInfo, resource):
    fin = open (resource, 'r')
    fin.readline()
    i = 0
    endtime = None
    sampleInfo = {}
    for line in fin:
        tokens = line.strip().split('\t')
        print tokens
        try:
            timestamp = datetime.datetime.strptime(tokens[0], '%m/%d/%Y %I:%M:%S %p')
        except:
            try:
                timestamp = datetime.datetime.strptime(tokens[0], '%d/%m/%Y %H:%M:%S')
            except:
                raise Exception
        if i == 0:

            scaneventInfo['starttime'] = timestamp
        sampleInfo[tokens[2]] = timestamp
        i += 1
        endtime = timestamp
    scaneventInfo['endtime'] = endtime
    print scaneventInfo
    fin.close()
    return sampleInfo


# set default sample info
def setSampleInfo(sampleInfo):
    for s in sampleInfo.keys():
        sampleInfo[s] = datetime.datetime.now()

# remove the folder of scanned chip
def removeChip(chip):
    print 'Removing folder ', str(chip)
    shutil.rmtree((os.path.join(UARRAY_TMP,chip)))


# return the scan event more correlated. If only one is available retunr it.
def identifyScanEvent(scanevents, scaneventInfo):
    scanEvent = None
    if len(scanevents) == 1:
        return scanevents[0]
    for s in scanevents:
        if datetime.datetime.strptime(s['start'], '%Y-%m-%dT%H:%M:%S') <= scaneventInfo['starttime'] and datetime.datetime.strptime(s['end'], '%Y-%m-%dT%H:%M:%S') >= scaneventInfo['endtime']:
            return s
    if scanEvent == None:
        return scanevents[-1]

def getGenId(chip):
    try:
        print 'genid'
        uarrayUrl = Urls.objects.get(id_webservice=WebService.objects.get(name='uarray').id, available=True)
        u = urllib2.urlopen(uarrayUrl.url + "api.getchip/"+ chip + "/repository")
        res=u.read()
        res=ast.literal_eval(res)
        print res
        pos = {}
        for a in res['assignments']:
            pos[a['position']] = a['sample']
        print pos
        return pos
    except Exception, e:
        print e
        return

def extractExpression(chip, raw, imputed):
    print os.path.join(UARRAY_TMP, chip, imputed)
    fimp = open (os.path.join(UARRAY_TMP, chip, imputed))
    try:
        
        header = []
        sample_imputed = {}
        samples = {}
        sample_imputedInit = False
        for line in fimp:
            tokens = line.strip().split('\t')
            print tokens
            if len(tokens) > 2 and len(header)==0:
                i = 0
                for t in tokens:
                    if t.lower() not in ['targetid', 'probeid', 'excluded/imputed']:
                        #print t
                        sample = t.split('.')[0].split('_')[1]
                        #print sample
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
    fimp.close()

    #print sample_imputed
    #print samples
    print os.path.join(UARRAY_TMP, chip, raw)
    fvalues = open (os.path.join(UARRAY_TMP, chip, raw))
    try:
        sample_value = {}
        sample_detection = {}
        header = []
        for line in fvalues:
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
    fvalues.close()
    return sample_value, sample_detection, sample_imputed



# analyzing the scanned chip folder to get all files of each sample and global of the chip
def uarrayUpload(folder, chip):
    print 'Analyzing chip ' + str(chip) + ' in folder ' + str(folder)
    chipInfo = []
    samples = {}
    sample_value = {}
    sample_detection = {}
    scaneventInfo = {'starttime':datetime.datetime.now(), 'endtime':datetime.datetime.now()}
    response = getChipLayout(chip)
    print response
    #check if the chip has beeen scanned
    if response.has_key('response'):
        print 'Chip not available in the uarray DB'
        return False
    # copy geometry info
    sampleInfo = response['geometry'].copy()
    sampleGenId = getGenId(chip)
    geometry = {v:k for k, v in response['geometry'].items()}
    # init sample info
    setSampleInfo(sampleInfo)

    resourceDict = {chip + '_rawdata.txt': '', chip + '_imputeddata.txt':''}
    # explore the folder 
    for resource in os.listdir(os.path.join(UARRAY_TMP, folder)):
        filename, extension = os.path.splitext(resource)
        tokens = filename.split('_')
        if len(tokens) > 1:
            if tokens[1] in geometry.keys():
                # it is a sample
                if samples.has_key(tokens[1]) == False:
                    samples[tokens[1]] = []
                samples[tokens[1]].append(resource)
            else:
                # file associated to the scan event
                if filename.lower() == chip + '_rawdata':
                    resourceDict[chip + '_rawdata.txt'] = resource
                if filename.lower() == chip + '_imputeddata':
                    resourceDict[chip + '_imputeddata.txt'] = resource
                chipInfo.append(resource)    
        else:
            # read file metrics to retrieve the scan event and sample info
            if filename.lower() == 'metrics':
                try:
                    sampleInfo = readMetrics (scaneventInfo, os.path.join(UARRAY_TMP, folder, resource))
                except:
                    return False

            chipInfo.append(resource)
    # identify scan event based on time
    scanEvent = identifyScanEvent(response['scanevents'], scaneventInfo)
    print scanEvent
    #print chipInfo
    #print samples
    print resourceDict
    if scanEvent == None:
        return False

    if len([x for x in resourceDict.values() if x == '']):
        return False
    else:
        sample_value, sample_detection, sample_imputed = extractExpression(folder,  resourceDict[chip + '_rawdata.txt'], resourceDict[chip + '_imputeddata.txt'])
    #return
    #print sample_value, sample_detection
    samplesChip = []
    print 'save in the rep'
    try:
        #save in the repository
        repDataChip = []
        for res in chipInfo:
            rData = RepData (name=res, created=scaneventInfo['endtime'], owner=scanEvent['operator'], extension=os.path.splitext(res)[1] )
            rData.resource.put(open(os.path.join(UARRAY_TMP, folder, res)))
            rData.save()
            repDataChip.append(rData)
        print scanEvent
        chipRep = UArrayChip (barcode=str(chip), sources = repDataChip, scan=str(scanEvent['id']) , hybevent=str(response['hybevent'])) 
        chipRep.save()
        print chipRep
        samplesUarray = {}
        for pos, s in samples.items():
            if sampleGenId.has_key(pos):
                print pos, s, sampleGenId[pos]
                repDataSample = []
                for res in s:
                    rData = RepData (name=res, created=scaneventInfo['endtime'], owner=scanEvent['operator'], extension=os.path.splitext(res)[1] )
                    rData.resource.put(open(os.path.join(UARRAY_TMP, folder, res)))
                    rData.save()
                    repDataSample.append(rData)
                sampleChip = UArraySample (genid=sampleGenId[pos], sources = repDataSample, chip = chipRep, position=pos, expression=sample_value[pos], detection=sample_detection[pos])
                if sample_imputed.has_key(pos):
                    sampleChip.imputed = sample_imputed[pos]
                else:
                    sampleChip.imputed = []
                sampleChip.save()
                samplesChip.append(sampleChip)
                samplesUarray[pos] = str(sampleChip.id)
        print samplesUarray
        #raise
        # update the links in uarray DB
        updateAssignment(scanEvent['id'], response['chip_id'], samplesUarray, chipRep.id)
    except Exception, e:
        print e
        for s in samplesChip:
            print s.id
            for src in s.sources:
                print src.id
                src.resource.delete()
                src.delete()
            s.delete()
        for src in chipRep.sources:
            print src.id
            src.resource.delete()
            src.delete()
        print chipRep.id
        chipRep.delete()
        print ''
        return False
    print samples
    print chipInfo
    return True

# scan the folder of uploaded chips, update links and remove the folder if all the files are saved in the repository
if __name__=='__main__':
    parser = argparse.ArgumentParser(description='Load microarray scan')
    parser.add_argument('scan_folder', metavar='sc', type=str, nargs = '*', help='Folders of microarray scan')
    parser.add_argument('--all', type=bool, default=False, help='Load all chips')
    args = parser.parse_args()
    savedChips = []
    target_folder = []
    if args.all:
        target_folder = os.listdir(UARRAY_TMP)
    else:
        target_folder = args.scan_folder
    startLoad = datetime.datetime.now()
    for scanfolder in target_folder:
        print datetime.datetime.now()
        if uarrayUpload(scanfolder, scanfolder.split('_')[0]):
            savedChips.append(scanfolder)
    endLoad = datetime.datetime.now()
    print 'End load scans: ', str(endLoad-startLoad)
    for chip in savedChips:
        removeChip(chip)
    print 'End remove files: ', str(datetime.datetime.now()-endLoad)
    
    
