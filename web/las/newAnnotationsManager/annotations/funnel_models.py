from django.db.models import *
from annotations.lib.file_utils import *
import models as ann_models
import api.funnel_schemas as funnel_schemas
import logging

from enum import Enum
import json, tarfile, urllib2, os, tempfile, urlparse, posixpath, shutil, jsonschema

DATA_FILE_SCHEMA = {
    'GeneticLab': funnel_schemas.geneticlab_data
}

class FileStatus(Enum):
    to_be_fetched = 0
    fetching = 1
    fetched = 2
    saving = 3
    saved = 4
    remote_url_not_available = 5
    error_fetching_url = 6
    error_saving_in_repo = 7
    invalid_format = 8

class FileType(Enum):
    raw = 1
    data = 2

class FunnelExperimentType(Model):
    name = CharField(max_length=255, db_column='name', unique=True)
    class Meta:
        db_table = 'FunnelExperimentType'
    def __unicode__(self):
        return self.name

class FunnelSourceLab(Model):
    name = CharField(max_length=255, db_column='name', unique=True)
    class Meta:
        db_table = 'FunnelSourceLab'
    def __unicode__(self):
        return self.name

class FunnelExperimentResult(Model):
    source = ForeignKey('FunnelSourceLab')
    sampleBarcode = CharField(max_length=255, db_column='barcode')
    experimentType = ForeignKey('FunnelExperimentType', db_column='expType_id')
    reportId = CharField(max_length=255, db_column='reportId', blank=True, null=True)
    submitTimestamp = DateTimeField(auto_now_add=True)
    rawObjectId = CharField(max_length=255, blank=True, null=True)
    dataObjectId = CharField(max_length=255, blank=True, null=True)
    class Meta:
        db_table = 'FunnelExperimentResult'

    def downloadFiles(self):
        try:
            files = self.funnelexperimentfile_set.all()
            success = True
            for f in files:
                ret = f.download_and_save()
                success = success and ret
        except Exception as e:
            logging.error("downloadFiles: " + str(e))
        return success

    def deleteFiles(self):
        try:
            files = self.funnelexperimentfile_set.all()
            for f in files:
                f.deleteLocal()
        except Exception as e:
            logging.error("deleteFiles: " + str(e))

    def createTarballs(self):
        try:
            rawFiles = self.funnelexperimentfile_set.filter(fileType=FileType.raw.value,status=FileStatus.saved.value)
            dataFiles = self.funnelexperimentfile_set.filter(fileType=FileType.data.value,status=FileStatus.saved.value)

            if len(rawFiles) > 0:
                try:
                    raw_archive_created = False
                    raw_archive = tarfile.open(os.path.join(settings.TEMP_ROOT,"{0}_{1}_{2}_raw.tar.gz".format(self.source, self.sampleBarcode.replace('/', '-'), self.experimentType)),mode='w:gz')
                    raw_archive_created = True
                    for f in rawFiles:
                        try:
                            raw_archive.add(name=f.localURL, arcname=posixpath.basename(f.localURL))
                        except Exception as e:
                            logging.error("[createTarballs] Error saving file %s : %s" % (f.localURL, str(e)))
                            f.status = FileStatus.error_saving_in_repo.value
                            f.save()
                    raw_archive.close()
                except Exception as e:
                    logging.error("[createTarballs] An error occurred: %s" % str(e))
                    if raw_archive_created == False:
                        for f in rawFiles:
                            print "setting file status to 7"
                            f.status = FileStatus.error_saving_in_repo.value
                            f.save()
                
            if len(dataFiles) > 0:
                try:
                    data_archive_created = False
                    data_archive = tarfile.open(os.path.join(settings.TEMP_ROOT,"{0}_{1}_{2}_data.tar.gz".format(self.source, self.sampleBarcode.replace('/', '-'), self.experimentType)),mode='w:gz')
                    data_archive_created = True
                    for f in dataFiles:
                        try:
                            data_archive.add(name=f.localURL, arcname=posixpath.basename(f.localURL))
                        except Exception as e:
                            logging.error("[createTarballs] Error saving file %s : %s" % (f.localURL, str(e)))
                            f.status = FileStatus.error_saving_in_repo.value
                            f.save()
                    data_archive.close()
                except Exception as e:
                    logging.error("[createTarballs] An error occurred: %s" % str(e))
                    if data_archive_created == False:
                        for f in dataFiles:
                            f.status = FileStatus.error_saving_in_repo.value
                            f.save()
        except Exception as e:
            logging.error("[createTarballs] error: " + str(e))

    def deleteTarballs(self):
        try:
            name_raw = os.path.join(settings.TEMP_ROOT,"{0}_{1}_{2}_raw.tar.gz".format(self.source, self.sampleBarcode.replace('/', '-'), self.experimentType))
            name_data = os.path.join(settings.TEMP_ROOT,"{0}_{1}_{2}_data.tar.gz".format(self.source, self.sampleBarcode.replace('/', '-'), self.experimentType))
            try:
                os.unlink(name_raw)
            except:
                pass
            try:
                os.unlink(name_data)
            except:
                pass
        except Exception as e:
            logging.error("deleteTarballs: " + str(e))

    def archiveTarballs(self):
        try:
            repositoryUrl = ann_models.Urls.objects.get(id_webservice__name='Repository',available=True).url
            data = {'source': self.source, 'sampleBarcode': self.sampleBarcode, 'experimentType': self.experimentType.name, 'reportId': self.reportId, 'submitTimestamp': self.submitTimestamp}

            if self.funnelexperimentfile_set.filter(fileType=FileType.raw.value).count() > 0:
                name_raw = os.path.join(settings.TEMP_ROOT,"{0}_{1}_{2}_raw.tar.gz".format(self.source, self.sampleBarcode.replace('/', '-'), self.experimentType))
                data['fileType'] = "raw"
                ret = uploadRepFile(data, name_raw, repositoryUrl)
                if ret == 'Fail':
                    pass
                else:
                    self.rawObjectId = ret

            if self.funnelexperimentfile_set.filter(fileType=FileType.data.value).count() > 0:            
                name_data = os.path.join(settings.TEMP_ROOT,"{0}_{1}_{2}_data.tar.gz".format(self.source, self.sampleBarcode.replace('/', '-'), self.experimentType))
                data['fileType'] = "data"
                ret = uploadRepFile(data, name_data, repositoryUrl)
                if ret == 'Fail':
                    pass
                else:
                    self.dataObjectId = ret

            self.save()

        except Exception as e:
            logging.error("archiveTarballs: " + str(e))

    def validateDataFiles(self):
        print "Validating experiment data files"
        try:
            schema = DATA_FILE_SCHEMA[self.source.name]
        except:
            logging.warning("WARNING: Schema not found for source '{0}', ignoring validation!".format(self.source.name))
            return True
        dataFiles = self.funnelexperimentfile_set.filter(fileType=FileType.data.value,status=FileStatus.saved.value)
        success = True
        for f in dataFiles:
            if f.localURL is None:
                print "WARNING: File {0} not downloaded ??".format(f.remoteURL)
                continue
            try:
                ret = jsonschema.validate(json.load(open(f.localURL, "r")), schema)
            except Exception as e:
                logging.error("Validation failed: " + str(e))
                success = False
                f.status = FileStatus.invalid_format.value
                f.notes = str(e)
                f.save()
        return success


class FunnelExperimentFile(Model):
    STATUS_CHOICES = [(x.value, x.name) for x in FileStatus]
    FILE_TYPE_CHOICES = [(x.value, x.name) for x in FileType]
    experimentResult = ForeignKey('FunnelExperimentResult', db_column='expRes_id')
    remoteURL = CharField(max_length=1024, db_column='remoteURL')
    localURL = CharField(max_length=1024, db_column='localURL', blank=True, null=True)
    status = IntegerField(choices=STATUS_CHOICES, db_column='status', default=FileStatus.to_be_fetched.value)
    fileType = IntegerField(choices=FILE_TYPE_CHOICES, db_column='fileType')
    notes = CharField(max_length=2048, blank=True, null=True)
    class Meta:
        db_table = 'FunnelExperimentFile'

    def download_and_save(self):
        print "download and save"
        try:
            self.status = FileStatus.fetching.value
            self.save()
            try:
                response = urllib2.urlopen(self.remoteURL)
                downloadedFile = response.read()    
            except:
                logging.error("URL %s not found, cannot save file" % self.remoteURL)
                self.status = FileStatus.remote_url_not_available.value
                self.save()
                return False
            
            tempdir = tempfile.mkdtemp(dir=settings.TEMP_ROOT)
            #filename = posixpath.basename(urlparse.urlsplit(self.remoteURL).path.strip('/'))
            params = urlparse.parse_qs(urlparse.urlsplit(self.remoteURL).query)
            filename = "_".join(map(lambda x: "_".join(x), params.values()))
            print filename
            # alternatives:
            # 1) check if file name is in 'Content-Disposition' header
            # 2) generate file name from sample id + incremental counter
            self.localURL = handle_uploaded_file(downloadedFile,tempdir,filename)
            self.status = FileStatus.saved.value
            self.save()
            return True
        except Exception as e:
            logging.error("download_and_save: " + str(e))
            return False

    def deleteLocal(self):
        try:
            if self.localURL:
                shutil.rmtree(posixpath.dirname(self.localURL))
                self.localURL = None
        except Exception as e:
            logging.error("deleteLocal: " + str(e))

    def delete(self):
        try:
            self.deleteLocal()
            super(FunnelExperimentFile, self).delete()
        except Exception as e:
            logging.error("delete: " + str(e))

