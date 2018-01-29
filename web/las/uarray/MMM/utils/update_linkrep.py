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


def retrieveData(fileOut):
    print fileOut
    chips = Chip_has_Scan.objects.filter(link__isnull= False)
    print len(chips)
    data = {}
    for c in chips:
        print c.id, c.idScanEvent.id, c.idChip.barcode
        geometry = ast.literal_eval(c.idChip.idChipType.layout.rules)
        #print geometry,  c.idScanEvent.id
        data[c.link] = {'barcode':c.idChip.barcode, 'hybevent':c.idChip.idHybevent.id, 'scan':c.idScanEvent.id, 'samples':[]}
        samples = Assignment_has_Scan.objects.filter(idScanEvent=c.idScanEvent, idAssignment__in =Assignment.objects.filter(idChip=c.idChip))
        for s in samples:
            genid = ''
            if s.idAssignment.idAliquot_has_Request.aliquot_id.genId:
                genid = s.idAssignment.idAliquot_has_Request.aliquot_id.genId
            print c.link, genid, s.idAssignment, geometry
            data[c.link]['samples'].append({s.link:{'genid':genid, 'pos':geometry[s.idAssignment.position]}})

    print data
    with open(fileOut, 'w') as outfile:
        json.dump(data, outfile)


# scan the folder of uploaded chips, update links and remove the folder if all the files are saved in the repository
if __name__=='__main__':
    parser = argparse.ArgumentParser(description='Update link of repository')
    parser.add_argument('--output', type=str, help='Output file')
    args = parser.parse_args()
    retrieveData (args.output)
        