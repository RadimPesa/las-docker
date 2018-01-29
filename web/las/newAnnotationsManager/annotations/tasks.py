from __future__ import absolute_import
from celery import shared_task
from annotations.models import *

@shared_task
def runFingerPrinting(report, notify=False):
    if report is None:
        return
    report.fingerPrinting()
    if request.author is not None and notify == True:
        # send email to user
        # report.filename will be attached to the message
        pass

@shared_task
def foo():
    import time
    time.sleep(3)
    return

@shared_task(bind=True)
def runUpdateAnnotations(self, batches):
    print "[runUpdateAnnotations] task_id=%s, # batches received=%d" % (self.request.id, len(batches))
    for batch in batches:
        print "batch_id=%d, type=%s" % (batch.id, batch.updateType.title())
        batch.task_id = self.request.id
        batch.save()

        try:
            batch.run()
        except Exception as e:
            print e
            batch.status = annotations.models.AnnotationUpdateBatch.ERROR
            batch.dateEnd = timezone.now()
            batch.save()
    print "[runUpdateAnnotations] Finished"

