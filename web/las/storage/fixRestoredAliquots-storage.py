#!/usr/bin/python
import sys
import site
import os
site.addsitedir('~/.virtualenvs/venvdj1.4/local/lib/python2.7/site-packages')

sys.path.append('/srv/www/storage')

activate_env=os.path.expanduser("~/.virtualenvs/venvdj1.4/bin/activate_this.py")
execfile(activate_env, dict(__file__=activate_env))

from django.core.management import setup_environ
import settings
setup_environ(settings)

from archive.models import *
import json

if __name__ == '__main__':

    if len(sys.argv) != 2:
        print ("Usage: %s <json_file_with_genid_list>" % sys.argv[0])
        exit(0)

    try:
        f = open(sys.argv[1], "r")
    except:
        print "Couldn't open %s, terminating" % sys.argv[1]

    restored_aliquots = json.load(f)
    for a in Aliquot.objects.filter(genealogyID__in=restored_aliquots):
        a.endTimestamp = None
        #a.save()

    f.close()