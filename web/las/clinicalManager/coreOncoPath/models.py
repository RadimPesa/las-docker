from django.db import models
from django.db import transaction
from django.conf import settings
from django.contrib.auth.models import User
from appPathologyManagement.models import UPhaseEntity
from py2neo import *


class OncoPath(models.Model):
    identifier      =   models.CharField(max_length = 32, unique = True)
    name            =   models.CharField(max_length = 40, null = True)
    status          =   models.NullBooleanField(null=True)

    # override save() to manage node and relationship in graph
    """
    @transaction.commit_on_success
    If the function returns successfully, then Django will commit all work done within the function at that point.
    If the function raises an exception, though, Django will roll back the transaction.
    """
    @transaction.commit_on_success
    def save(self, *args, **kwargs):
        patient = kwargs.pop('patient', None) # preserving proper *args, **kwargs for passing to te super method
        uPhaseData = kwargs.pop('uPhaseData')
        try:
            print "Preparing transaction for saving or updatig OncoPath '{0}' in DBMS".format(self.identifier)
            super(OncoPath, self).save(*args, **kwargs) # call legacy save() of the super method
            # saving OncoPathUPhaseLog
            uPhaseData['oncoPath'] = self
            log = OncoPathUPhaseLog(**uPhaseData)
            log.save()

            graph = neo4j.GraphDatabaseService(settings.GRAPH_DB_URL)
            if patient is not None: # create new OncoPath and link it to the Patient
                # Save in graph
                batch = neo4j.WriteBatch(graph)
                oncoNode = batch.create(node(identifier = self.identifier, name = self.name))
                batch.add_labels(oncoNode, 'OncoPath')
                try:
                    patientNode = next(graph.find('Patient', 'identifier', patient)) # graph.find() returns a generator object
                except StopIteration:
                    print "Patient '{0}' does not exist in graph".format(patient)
                    raise Exception("Patient '{0}' does not exist in graph".format(patient))
                else:
                    oncoRel = rel(patientNode,'affectedBy', oncoNode)
                    batch.create(oncoRel)
                    # Clone social rels of patient node in oncoPath node
                    socialRelationships = patientNode.match() # returns a generator object
                    for sr in socialRelationships:
                        if sr.type in ("OwnsData","SharesData"):
                            socialRel = rel(sr.start_node, sr.type, oncoNode)
                            batch.create(socialRel)
                        else:
                            pass
                    batch.submit()
                    batch.clear()
                print "OncoPath '{0}' saved in graph and linked to patient '{1}'".format(self.identifier, patient)
            else: # update existing OncoPath
                try:
                    oncoNode = next(graph.find('OncoPath', 'identifier', self.identifier)) # graph.find() returns a generator object
                except StopIteration:
                    print "OncoPath '{0}' does not exist in graph".format(self.identifier)
                    raise
                else:
                    if oncoNode['name'] != self.name:
                        oncoNode.update_properties({'name':self.name})
                        print "Pathology name updated in graph"
                    else:
                        print "Nothing to do in graph..."
        except:
            print "Exception while saving or updatig OncoPath '{0}', rollbacking...".format(self.identifier)
            raise
        else:
            print "Transaction successfully committed (DBMS)"

    # TODO: properly override delete with transaction.commit_on_success
    """@transaction.commit_manually
    def delete(self, *args, **kwargs):
        try:
            # Call the "real" del() method:
            super(OncoPath, self).delete(*args, **kwargs)
            print "Preparing transaction for deleting OncoPath '{0}' from DBMS".format(self.identifier)
            # Delete from graph
            graph = neo4j.GraphDatabaseService(settings.GRAPH_DB_URL)
            batch = neo4j.WriteBatch(graph)
            try:
                oncoNode = next(graph.find('OncoPath', 'identifier', self.identifier))
            except StopIteration:
                print "OncoPath '{0}' does not exist in graph".format(self.identifier)
                raise
            try:
                oncoRel = next(graph.match(rel_type='affectedBy', end_node = oncoNode))
            except:
                print "No relationship with any patient node"
                raise
            batch.delete(oncoRel)
            batch.delete(oncoNode)
            batch.submit()
            batch.clear()
            print "OncoPath '{0}' deleted from graph".format(self.identifier)
        except:
            print "Exception while deleting OncoPath, rollbacking..."
            transaction.rollback()
            raise
        else:
            transaction.commit()
            print "Transaction successfully committed (DBMS)"
    """


class Feature(models.Model):
    name            =   models.CharField(max_length = 40, null = True)
    shortName       =   models.CharField(max_length = 10, null = True)
    fatherFeatureId =   models.ForeignKey('self', null = True)
    dataType        =   models.CharField(max_length = 40, null = True)


class OncoPathFeature(models.Model):
    oncoPath        =   models.ForeignKey(OncoPath)
    feature         =   models.ForeignKey(Feature)
    value           =   models.CharField(max_length = 200, null = True)
    lastUpdate      =   models.DateTimeField(null = True)
    operator        =   models.ForeignKey(User, null = True)#, related_name='coreOncoPath_operator')
    module          =   models.CharField(max_length = 40, null = True)
    uPhase          =   models.CharField(max_length = 40, null = True)


class OncoPathUPhaseLog(models.Model):
    oncoPath            =   models.ForeignKey(OncoPath)
    module              =   models.CharField(max_length = 40, null = True)
    uPhaseId            =   models.ForeignKey(UPhaseEntity)
    uPhase              =   models.CharField(max_length = 40, null = True)
    startTimestamp      =   models.DateTimeField(null = True)
    startNotes          =   models.TextField(null = True)
    startOperator       =   models.ForeignKey(User, null = True, related_name='coreOncoPath_startOperator')
    endTimestamp        =   models.DateTimeField(null = True)
    endNotes            =   models.TextField(null = True)
    endOperator         =   models.ForeignKey(User, null = True, related_name='coreOncoPath_endOperator')
    fatherUPhaseEntity  =   models.ForeignKey('self', null = True)
    lock                =   models.NullBooleanField(null = True)




    """@transaction.commit_manually
    def save(self, *args, **kwargs):
        patient = kwargs.pop('patient', None) # preserving proper *args, **kwargs for passing to te super method
        uPhaseData = kwargs.pop('uPhaseData')
        try:
            print "Preparing transaction for saving or updatig OncoPath '{0}' in DBMS".format(self.identifier)
            super(OncoPath, self).save(*args, **kwargs) # call legacy save() of the super method
            graph = neo4j.GraphDatabaseService(settings.GRAPH_DB_URL)
            if patient is not None: # create new OncoPath and link it to the Patient
                # Save in graph
                batch = neo4j.WriteBatch(graph)
                oncoNode = batch.create(node(identifier = self.identifier, name = self.name))
                batch.add_labels(oncoNode, 'OncoPath')
                try:
                    patientNode = next(graph.find('Patient', 'identifier', patient)) # graph.find() returns a generator object
                except StopIteration:
                    print "Patient '{0}' does not exist in graph".format(patient)
                    raise
                else:
                    oncoRel = rel(patientNode,'affectedBy', oncoNode)
                    batch.create(oncoRel)
                    batch.submit()
                    batch.clear()
                print "OncoPath '{0}' saved in graph and linked to patient '{1}'".format(self.identifier, patient)
            else: # update existing OncoPath
                try:
                    oncoNode = next(graph.find('OncoPath', 'identifier', self.identifier)) # graph.find() returns a generator object
                except StopIteration:
                    print "OncoPath '{0}' does not exist in graph".format(self.identifier)
                    raise
                else:
                    if oncoNode['name'] != self.name:
                        oncoNode.update_properties({'name':self.name})
                        print "Pathology name updated in graph"
                    else:
                        print "Nothing to do in graph..."
        except:
            print "Exception while saving or updatig OncoPath '{0}', rollbacking...".format(self.identifier)
            transaction.rollback()
            raise
        else:
            transaction.commit()
            # saving entry in OncoPathUPhaseLog
            uPhaseData['oncoPath'] = self
            log = OncoPathUPhaseLog(**uPhaseData)
            log.save()
            print "Transaction successfully committed (DBMS)" """
