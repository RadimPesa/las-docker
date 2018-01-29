import sys
sys.path.append('/srv/www/repmanager/')
from django.core.management import setup_environ
from repmanager import settings
setup_environ(settings)
from datamanager.models import *
import datetime

SRC_FOLDER = "/mnt/exomes"
USERNAME = "alberto.grand"

files = []

import os
for filename in os.listdir(SRC_FOLDER):
    if filename.endswith(".bam"):
        try:
            rData = RepData (name=filename, created=datetime.datetime.now(), owner=USERNAME, extension=os.path.splitext(filename)[1] )
            rData.resource.put(open(os.path.join(SRC_FOLDER, filename)))
            rData.save()
            print "%s\t%s" % (filename, rData.id)
            files.append((filename, rData.id))
        except Exception as e:
            print "Error: file=%s, error=%s" % (filename, str(e))

with open("list.txt", "w") as f:
    for x in files:
        f.write("%s\t%s" % x)


