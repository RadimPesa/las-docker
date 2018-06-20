import sys
sys.path.append('../')
from django.core.management import setup_environ
from catissue import settings
setup_environ(settings)

from tissue.models import *

import os, urllib, urllib2, json, requests

CLINICAL_URL = Urls.objects.get(idWebService__name='Clinical').url
OUTPUT_SHEET_1 = "sheet_1.txt"

def getClinicalPatientId(projectName, icCode):
    url = CLINICAL_URL + "/coreProject/api/informedConsent"
    values_to_send = {  "ICcode": icCode,
                        "project": projectName}
    try:
        res = requests.get(url,params=values_to_send)
    except Exception, e:
        print e
        print "An error occurred while trying to retrieve data from " + str(url)   

    if res.status_code == 200:
        result = res.json()
        return result["patientUuid"]
    else:
        return None

def getClinicalInfo(patientId):
    url = CLINICAL_URL + "/corePatient/api/patient_classic_rest/" + patientId
    try:
        res = requests.get(url)
    except Exception, e:
        print e
        print "An error occurred while trying to retrieve data from " + str(url)   

    result = res.json()
    try:
        result['birthDate'] = datetime.datetime.strptime(result['birthDate'], "%Y-%m-%d")
    except:
        result['birthDate'] = None

    return result

def writeSheet1(patient_gender):
    headers = ["patient ID", "gender", "history", "Ethnicity/Race"]
    with open(OUTPUT_SHEET_1, "w") as f:
        f.write("\t".join(headers) + "\n")
        for pid, gender in patient_gender.iteritems():
            f.write("\t".join([pid, gender, "", ""]) + "\n")


if __name__ == '__main__':

    print "Start exporting sheet1..."
    startTime = datetime.datetime.now()

    print "Read model ids"
    all_patient_ids = {}
    with open("all_model_ids.csv", "r") as f:
        f.readline() # skip headers
        for line in f:
            pid, mid = line.strip().split('\t')
            all_patient_ids[pid] = mid[:7]

    patient_gender = {}
    patient_gender_from_file = {}

    with open("all_patient_gender.csv", "r") as f:
        f.readline() # skip headers
        for line in f:
            pid, gender = line[:-1].split("\t")
            patient_gender_from_file[pid] = gender

    for pid, mid in all_patient_ids.iteritems():
        try:
            c = Collection.objects.get(idCollectionType__abbreviation=mid[:3],itemCode=mid[3:])
        except Exception, e:
            print e
            print "non existing:", mid
            continue

        icCode = c.collectionEvent
        projectName = c.idCollectionProtocol.project

        puuid = getClinicalPatientId(projectName, icCode)
        if puuid is None:
            print mid, "not in clinical db, defaulting to null"
            patient_gender[pid] = patient_gender_from_file.get(pid, "")
        else:
            clinInfo = getClinicalInfo(puuid)
            try:
                patient_gender[pid] = clinInfo['sex'] or patient_gender_from_file.get(pid, "")
            except:
                patient_gender[pid] = patient_gender_from_file.get(pid, "")

    writeSheet1(patient_gender)

    print "END"
