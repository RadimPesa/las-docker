#!/usr/bin/python
# Set up the Django Enviroment
import sys
#sys.path.append('/srv/www/caxeno')
sys.path.append('/home/piero/Documenti/caXeno/trunk/caxeno')
from django.core.management import setup_environ 
import settings, os, cStringIO, string, json, csv, datetime
setup_environ(settings)
from django.contrib.auth import authenticate, login
from django.db import transaction
from xenopatients.models import *
from xenopatients.genealogyID import *

@transaction.commit_manually
def readFile(filePath):
    try:
        print 'start'
        today = datetime.date.today()
        print today
        with open(filePath, 'rb') as csvfile:
            reader = csv.reader(csvfile, delimiter=' ', quotechar='|')
            i = 0
            g = Groups(name = 'fakeGroup1')
            g.save()

            s = Series(id_operator=User.objects.get(username="piero.alberto") , id_type=Type_of_serie.objects.get(description='explant') , date=today, notes='fake serie')
            s.save()
            for row in reader:
                if len(row[0]) > 0:
                    print '#####new loop#####'
                    print row[0], len(Aliquots.objects.filter(id_genealogy = row[0]))
                    genID = row[0][:10] + '0' + row[0][10:]
                    #print genID
                    oGen = GenealogyID(genID)
                    mouse = int(oGen.getMouse()) + 200
                    #print oGen.getSample() + str(mouse)
                    oGen.updateGenID({'mouse':str(mouse)})
                    if len(Aliquots.objects.filter(id_genealogy = oGen.getGenID())) == 0:
                        print oGen.getGenID()
                        startMouse = oGen.getSample() + str(mouse)
                        #search for mouse
                        barcode = "B" + str(i).zfill(5)
                        #print barcode
                        if len(BioMice.objects.filter(id_genealogy__startswith = startMouse)) == 0:
                            pm = Mice(arrival_date=today, birth_date=today, death_date=today, available_date=today, barcode=barcode, gender='m', 
                                      id_status=Status.objects.get(name='explanted'), id_source=Source.objects.get(pk=1) ,
                                      id_mouse_strain=Mouse_strain.objects.get(pk=1), notes='fake mouse for historical aliquots')
                            pm.save()
                            bm = BioMice(phys_mouse_id = pm, id_genealogy=startMouse+('SCR000000'), id_group = g, notes='fake mouse for historical aliquots')
                            bm.save()
                        else:
                            bm = BioMice.objects.get(id_genealogy__startswith = startMouse)
                        print s.id
                        print g.id
                        ed = Explant_details(id_series = s, id_mouse = bm)
                        print 'b'
                        ed.save()
                        print 'c'
                        a = Aliquots(id_explant = ed, idType = TissueType.objects.get(abbreviation='TUM'), id_genealogy=oGen.getGenID())
                        a.save()
                        i += 1
        transaction.commit()
        print 'xeno script: all ok'
    except Exception,e:
        print 'error'
        transaction.rollback()
        print e
    return
if __name__=='__main__':
    readFile("FFPE_totali_Piero.csv")