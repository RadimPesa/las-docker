from __init__ import *

def retrieveTargets (targets):
    annotUrl = Urls.objects.get(id_webservice=WebService.objects.get(name='annotation').id, available=True)
    url = annotUrl.url + 'newapi/snpProbeInfo/?uuid=["' + '","'.join(targets) +'"]'
    print url
    req = urllib2.Request(url)
    u = urllib2.urlopen(req)
    #u = urllib2.urlopen()
    res=u.read()
    res=json.loads(res)


    results = []
    for t in res:
        results.append({'uuid':t['uuid'], 'name':t['name'], 'allele':t['allele'], 'alt':t['alt'], 'chrom':t['chrom'], 'class': t['class'], 'start':t['start'], 'end':t['end'], 'strand':t['strand'] })
  
    return results



def submitAnalysis(payload):
    annotUrl = Urls.objects.get(id_webservice=WebService.objects.get(name='annotation').id, available=True)
    url = annotUrl.url + 'newapi/submitAnalysisResults/'
    r = requests.post(url, data=json.dumps(payload), headers={'content-type': 'application/json'}, verify=False)
    if r.status_code == requests.codes.ok:
        print r.text
        return
    else:
        print r.status_code, r.text
        raise Exception('BAD REQUEST in submit analysis')
    
    

def submitLabelAnalysis(payload):
    annotUrl = Urls.objects.get(id_webservice=WebService.objects.get(name='annotation').id, available=True)
    url = annotUrl.url + 'newapi/createAnalysis/'

    r = requests.post(url, data=json.dumps(payload), headers={'content-type': 'application/json'}, verify=False)

    if r.status_code == requests.codes.ok:
        res=json.loads(r.text)
        print res
        return res['refset_label']
    else:
        print r.status_code, r.text
        raise Exception('BAD REQUEST in label analysis')
    

def getLabelAnalysis(labels):
    annotUrl = Urls.objects.get(id_webservice=WebService.objects.get(name='annotation').id, available=True)
    url = annotUrl.url + 'newapi/refsetParameters/?exp_type=Sequenom&labels=["' + '","'.join(labels) +'"]'
    #print url
    req = urllib2.Request(url)
    u = urllib2.urlopen(req)
    #u = urllib2.urlopen()
    res=u.read()
    res=json.loads(res)
    results = []
    print res
    for r in res:
        if r.has_key('parameters'):
            print r['parameters']
            if r['parameters'].has_key('uuid_list'):
                print r['parameters']['uuid_list']
                results.extend(r['parameters']['uuid_list'])
    return list(set(results))


def createLabelAnalysis(payload):
    annotUrl = Urls.objects.get(id_webservice=WebService.objects.get(name='annotation').id, available=True)
    url = annotUrl.url + 'newapi/createRefset/'

    r = requests.post(url, data=json.dumps(payload), headers={'content-type': 'application/json'}, verify=False)

    if r.status_code == requests.codes.ok:
        res=json.loads(r.text)
        print res
        return res['refset_label']
    else:
        print r.status_code, r.text
        raise Exception('BAD REQUEST in label analysis')





def getMutations(label):
    annotUrl = Urls.objects.get(id_webservice=WebService.objects.get(name='annotation').id, available=True)
    url = annotUrl.url + 'newapi/refset/?label=' + label
    print url
    
    req = urllib2.Request(url)
    u = urllib2.urlopen(req)
    res=u.read()
    res=yaml.safe_load(res)
    print res


    targets = aggregateTargets(res['short_genetic_variation'], 'name')
    
    return targets

def getProbes (targets):
    annotUrl = Urls.objects.get(id_webservice=WebService.objects.get(name='annotation').id, available=True)
    url = annotUrl.url + 'newapi/snpInProbe/?uuid=["' + '","'.join(targets) +'"]'

    req = urllib2.Request(url)
    u = urllib2.urlopen(req)
    #u = urllib2.urlopen()
    res=u.read()
    res = yaml.safe_load(res)
    targets = aggregateTargets(res, 'name')

    return targets



def aggregateTargets(res, key):
    targets = {}
    print res
    for r in res:
        print r
        if not targets.has_key(r[key]):
            targets[r[key]] = []
        targets[r[key]].append(r) 

    print targets
    return targets
