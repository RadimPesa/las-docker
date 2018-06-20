#!/usr/bin/python
import sys
import site
import os
site.addsitedir('~/.virtualenvs/venvdj1.4/local/lib/python2.7/site-packages')

sys.path.append('/srv/www/biobank')

activate_env=os.path.expanduser("~/.virtualenvs/venvdj1.4/bin/activate_this.py")
execfile(activate_env, dict(__file__=activate_env))

from django.core.management import setup_environ
import settings
setup_environ(settings)

from tissue.models import *
import json
import tempfile

STORAGE_PATH = "/srv/www/storage/"
STORAGE_SCRIPT_FILENAME = "fixRestoredAliquots-storage.py"

if __name__ == '__main__':
    
    if len(sys.argv) != 2:
        print ("Usage: %s <id_of_first_restore_procedure>" % sys.argv[0])
        exit(0)

    enable_graph()
    disable_graph()

    try:
        id_first_restore = int(sys.argv[1])
    except:
        print "Invalid primary key: %s" % sys.argv[1]
        exit(1)

    try:
        BlockProcedure.objects.get(pk=id_first_restore)
    except:
        print "BlockProcedure with pk=%d does not exist, terminating" % id_first_restore
        exit(1)
    
    restored_aliquots = set()

    for bp in BlockProcedure.objects.filter(pk__gte=id_first_restore).order_by('pk'):
        if bp.workGroup != "delete":
            restored_aliquots.update([bb.genealogyID for bb in bp.blockbioentity_set.all() if GenealogyID(bb.genealogyID).isAliquot()])
        else:
            restored_aliquots.difference_update([bb.genealogyID for bb in bp.blockbioentity_set.all() if GenealogyID(bb.genealogyID).isAliquot()])
    print "%d aliquots restored"
    print "Updating biobank availability"
    for a in Aliquot.objects.filter(uniqueGenealogyID__in=restored_aliquots):
        a.availability = 1
        #a.save()
    print "Updating storage endTimestamp"
    f = tempfile.NamedTemporaryFile()
    json.dump(list(restored_aliquots), f)
    f.close()
    # about to call storage script
    os.system("cd " + STORAGE_PATH + "; " + "./" + STORAGE_SCRIPT_FILENAME + " " + f.name)

    f.unlink()
    print "Done"