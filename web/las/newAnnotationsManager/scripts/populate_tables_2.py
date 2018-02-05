"""This module performs the initial import for the annotations EnsemblTranscriptXref and UCSCSnp141 models"""

import sys
sys.path.append('/srv/www/newAnnotationsManager/')
from django.core.management import setup_environ
from annotationsManager import settings
setup_environ(settings)
from annotations.models import *

if __name__ == '__main__':
    print "Starting to populate annotations tables"
    #EnsemblTranscriptXref.objects.populate()
    UCSCSnp141.objects.populate()
