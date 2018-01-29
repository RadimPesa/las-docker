from rest_framework import status
from rest_framework.decorators import api_view, parser_classes
from rest_framework.response import Response
from annotations.funnel_models import *
from parsers import FunnelResultParser
import logging
from django.conf import settings

from datetime import datetime

#FORMAT = '%(asctime)-15s %(clientip)s %(user)-8s %(message)s'
FORMAT = '%(asctime)-15s %(message)s'
logging.basicConfig(filename=settings.FUNNEL_LOG_FILE, level=logging.INFO, format=FORMAT)

@api_view(['POST'])
@parser_classes((FunnelResultParser,))
def submitExperimentResult(request):
    """
    Submit Funnel experiment result data
    """
    if request.method == 'POST':
        logging.info("New Funnel experiment data submission")
        logging.info("Data received:" + str(request.POST))
        #serializer = SnippetSerializer(data=request.data)
        #if serializer.is_valid():
        #    serializer.save()
        #    return Response(serializer.data, status=status.HTTP_201_CREATED)
        #return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        try:
            request.data
        except Exception as e:
            logging.error(str(e))
            return Response({"description" : str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        results = request.data['results']
        experiments = []

        # create objects
        for res in results:
            exp = FunnelExperimentResult()

            try:
                source = FunnelSourceLab.objects.get(name=res['source'])
            except:
                source = FunnelSourceLab(name=res['source'])
                source.save()

            exp.source = source
            exp.sampleBarcode = res['childBarcode']
            try:
                exp.experimentType = FunnelExperimentType.objects.get(name=res['experimentType'])
            except:
                logging.error("Invalid experiment type: %s" % res['experimentType'])
                error = {"description" : "Invalid experiment type: %s" % res['experimentType']}
                return Response(error, status=status.HTTP_400_BAD_REQUEST)

            exp.reportId = res['reportId']
            exp.save()
            
            for u in res['rawURLs']:
                f = FunnelExperimentFile()
                f.experimentResult = exp
                f.remoteURL = u
                f.fileType = FileType.raw.value
                f.save()
            for u in res['dataURLs']:
                f = FunnelExperimentFile()
                f.experimentResult = exp
                f.remoteURL = u
                f.fileType = FileType.data.value
                f.save()

            experiments.append(exp)

        # try and download files
        success = True
        failed = []
        for exp in experiments:
            ret1 = exp.downloadFiles()
            ret2 = exp.validateDataFiles()
            if (not ret1) or (not ret2):
                success = False
                failed.append(exp)
        
        # if download was unsuccessful for some files, entire process is aborted        
        if not success:
            logging.error("Error while downloading files (details follow)")
            error = {"description": "An error occurred with raw and/or data files (see results for details)", "results": []}
            for exp in failed:
                exp_info = {    "childBarcode": exp.sampleBarcode,
                                "experimentType": exp.experimentType.name,
                                "reportId": exp.reportId,
                                "rawURLs": [{"url": f.remoteURL, "status": FileStatus(f.status).name, "description": f.notes} for f in exp.funnelexperimentfile_set.filter(fileType=FileType.raw.value).exclude(status=FileStatus.saved.value)],
                                "dataURLs": [{"url": f.remoteURL, "status": FileStatus(f.status).name, "description": f.notes} for f in exp.funnelexperimentfile_set.filter(fileType=FileType.data.value).exclude(status=FileStatus.saved.value)]
                            }
                error["results"].append(exp_info)
            logging.error(error["results"])

            for exp in experiments:
                exp.deleteFiles()
                exp.delete()

            return Response(error, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        # download was successful for all files, create tarballs and archive them in repo, then delete local files and tarballs
        logging.info("Download successful")
        try:
            for exp in experiments:
                exp.createTarballs()
                exp.archiveTarballs()
                exp.deleteTarballs()
                exp.deleteFiles()
        except Exception as e:
            logging.error("An error occurred: " + str(e))
            
        return Response({'status': 200}, status=status.HTTP_200_OK)
        
