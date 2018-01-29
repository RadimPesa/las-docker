#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
sys.path.append('/srv/www/catissue')


# activate venv
#activate_env=os.path.expanduser("~/.virtualenvs/venvdj1.4/bin/activate_this.py")
#execfile(activate_env, dict(__file__=activate_env))

# Set up the Django Enviroment
from django.core.management import setup_environ
import settings
from django.utils import timezone
setup_environ(settings)

# Neo4j driver
import py2neo

# Biobank module models
from catissue.tissue.models import Source, CollectionProtocol



# create a Medical Center in the Biobank
def createSource(src_name, src_type, src_internalName):
    s = Source()
    s.name = src_name
    s.type = src_type
    s.internalName = src_internalName
    s.save()

    print 'Medical Center created in biobank\n\tname: {}\n\ttype: {}\n\tinternalName: {}'.format(src_name, src_type, src_internalName)



# create a Protocol in the Biobank
def createCollectionProtocol(title, identifier):
    timeToSave = timezone.localtime(timezone.now())
    cp = CollectionProtocol()
    cp.title = title
    cp.name = identifier
    cp.project = identifier
    cp.projectDateRelease = timeToSave
    cp.informedConsent = ''
    cp.informedConsentDateRelease = timeToSave
    cp.ethicalCommittee = ''
    cp.approvalDocument = ''
    cp.approvalDate = timeToSave
    cp.save()

    print 'Project created in biobank'



def main():
    print "This is the Python script for dealing with LAS virtualenv 1.4"

if __name__ == "__main__":
    main()
