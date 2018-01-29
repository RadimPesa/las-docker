from django.conf.urls.defaults import *
from django.views.generic import DetailView, ListView
from xenopatients.models import *
from caxeno import settings
from django.conf.urls.static import static
from xenopatients.forms import *


urlpatterns = patterns('',
    (r'^$', 'xenopatients.views.index'),

    (r'^checkbiomice/$', 'xenopatients.views.check_bio_mice'),

    (r'^miceloading/$', 'xenopatients.miceManage.miceLoading'),
    (r'^finishListing/$', 'xenopatients.miceManage.finishListing'),
    (r'^finishListing/continue$', 'xenopatients.miceManage.continueReport'),

    (r'^miceStatus/$', 'xenopatients.miceManage.changeStatus'),
    (r'^miceStatus/finish$', 'xenopatients.miceManage.finishChange'),
    (r'^miceStatus/continueStatus$', 'xenopatients.miceManage.continueStatusReport'),

    (r'^measurement/qual$', 'xenopatients.measure.qualMeasure'),
    (r'^measurement/qual_weight$', 'xenopatients.measure.qualMeasureWeight'),
    (r'^measurement/qualmeasureReport$', 'xenopatients.measure.measurequalReport'),
    (r'^measurement/qualReport$', 'xenopatients.measure.qualReport'),

    (r'^measurement/quant$', 'xenopatients.measure.quantMeasure'),
    (r'^measurement/quant3d$', 'xenopatients.measure.quantMeasure3d'),
    (r'^measurement/quant_weight$', 'xenopatients.measure.quantMeasureWeight'),
    (r'^measurement/quant_weight3d$', 'xenopatients.measure.quantMeasureWeight3d'),
    (r'^measurement/quantmeasureReport$', 'xenopatients.measure.measurequantReport'),
    (r'^measurement/quantReport$', 'xenopatients.measure.quantReport'),
    (r'^measurement/continueQuant$', 'xenopatients.measure.continueReport'),


    (r'^treatments/start$', 'xenopatients.measure.startTreatment'),
    (r'^treatments/save$', 'xenopatients.treatments.saveTreatment'),
    (r'^treatments/manage$', 'xenopatients.treatments.manageTreatments'),
    (r'^treatments/manage/newProtocol$', 'xenopatients.treatments.newProtocol'),
    (r'^treatments/manage/newProtocol/save$', 'xenopatients.treatments.saveProtocol'),
    (r'^treatments/confirmTreatments$', 'xenopatients.treatments.confirmTreat'),
    (r'^treatments/saveStart$', 'xenopatients.treatments.saveConfirm'),
    (r'^treatments/abort$', 'xenopatients.treatments.abortT'),

    (r'^implants/start$', 'xenopatients.implants.startImplant'),
    (r'^implants/continue$', 'xenopatients.implants.reportImplant'),
    (r'^implants/continueImpl$', 'xenopatients.implants.continueImplant'),
    (r'^implants/rGroups$', 'xenopatients.implants.implantGroups'),
    (r'^implants/groups$', 'xenopatients.implants.redirectG'),
    (r'^implants/rImplants$', 'xenopatients.implants.rImplants'),
    (r'^implants/loadG$', 'xenopatients.implants.loadG'),

    (r'^explants/start$', 'xenopatients.explant.startExplant'),
    (r'^explants/submit$', 'xenopatients.explant.explantSubmit'),
    (r'^explants/report$', 'xenopatients.explant.explantReport'),
    (r'^explants/continue$', 'xenopatients.explant.explantContinue'),
    (r'^explants/continueErr$', 'xenopatients.explant.explantContinueErr'),
    (r'^explants/restoreExpl$', 'xenopatients.explant.restoreExpl'),

    (r'^explants/checkBarcodeT$', 'xenopatients.externalAPIhandler.checkBarcodeT'),

    (r'^error/$', 'xenopatients.views.error'),

    (r'^check/checking$', 'xenopatients.check.check'),
    (r'^check/checkTreat$', 'xenopatients.check.checkTreat'),
    (r'^check/save$', 'xenopatients.check.checkSave'),
    (r'^check/graphCSV$', 'xenopatients.check.graphCSV'),

    (r'^experiments/ongoing$', 'xenopatients.ongoing.ongoing'),
    (r'^experiments/ongoing/treatment$', 'xenopatients.ongoing.treatment'),
    (r'^experiments/ongoing/save$', 'xenopatients.ongoing.ongoingSave'),

    (r'^experiments/archive$', 'xenopatients.ongoing.archive'),

    (r'^groups/manage$', 'xenopatients.groups.manageG'),
    (r'^groups/loadGroup$', 'xenopatients.groups.loadG'),
    (r'^groups/saveChange$', 'xenopatients.groups.saveChange'),

    (r'^xenoAdmin/start$', 'xenopatients.xenoAdmin.start'),

    (r'^batch/start$', 'xenopatients.batch.start'),
    (r'^batch/read$', 'xenopatients.batch.read'),
    (r'^batch/save$', 'xenopatients.batch.save'),

    (r'^permission/', include('editpermission.urls')),

    (r'^lasHome', 'xenopatients.views.lasHome'),
)

#urlpatterns = patterns('xenopatients.treatments',
#    (r'^treatments/confirmTreatments$', confirmTreat),
#)

if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^xeno_media/(?P<path>.*)$', 'django.views.static.serve',
         {'document_root':     settings.MEDIA_ROOT}),
    )
