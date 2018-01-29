from __init__ import *

def retrieveTargets (targets):
    annotUrl = Urls.objects.get(id_webservice=WebService.objects.get(name='annotation').id, available=True)
    url = annotUrl.url + 'newapi/rtpcrAmpliconInfo/?amplicon_uuid=["' + '","'.join(targets) +'"]'
    print url
    req = urllib2.Request(url)
    u = urllib2.urlopen(req)
    res=u.read()
    res = yaml.safe_load(res)

    results = []
    for t in res:
        primerrv = None
        primerfw = None
        
        for p in t['primers']:
            if primerfw == None:
                primerfw = p['name']
            else:
                primerrv = p['name']
        results.append({'uuid':t['uuid'], 'name':t['name'], 'gene_symbol':t['gene_symbol'], 'start_base':t['start_base'], 'end_base':t['end_base'], 'length':t['length'], 'primerfw': primerfw, 'primerrv': primerrv, 'ref':t['ref'], 'type': t['type'] })
  
    return results


def retrieveMutations (targets):
    annotUrl = Urls.objects.get(id_webservice=WebService.objects.get(name='annotation').id, available=True)
    url = annotUrl.url + 'newapi/alterationsInAmplicon/?amplicon_uuid=["' + '","'.join(targets) +'"]'
    print url
    req = urllib2.Request(url)
    u = urllib2.urlopen(req)
    res=u.read()
    res = yaml.safe_load(res)
    print res

    results = []
    geneMut = {}

    for r in res:
        print r
        tDict = {'id': str(r['uuid']), 'gene': '', 'name': str(r['name']) , 'mutations':[], 'regions':[] }
        genes = []
        for reg in r['regions']:
            tDict['regions'].append(str(reg['uuid']))
            for a in reg['alterations']:
                tDict['mutations'].append({'id': str(a['uuid']), 'value': str(reg['gene_symbol'] + ' ' + str(a['hgvs_p'].split(':')[1]) + ' (' + str(a['hgvs_c'].split(':')[1]) + ')' )  })
                genes.append(str(reg['gene_symbol']))

                if not geneMut.has_key(str(reg['gene_symbol'])):
                    geneMut[str(reg['gene_symbol'])] = {}
                if not geneMut[str(reg['gene_symbol'])].has_key(str(a['hgvs_p'].split(':')[1])):
                    geneMut[str(reg['gene_symbol'])][str(a['hgvs_p'].split(':')[1])] = {'target': str(r['uuid']), 'mut':str(a['uuid']) }
                if not geneMut[str(reg['gene_symbol'])].has_key(str(a['hgvs_c'].split(':')[1])):
                    geneMut[str(reg['gene_symbol'])][str(a['hgvs_c'].split(':')[1])] = {'target': str(r['uuid']), 'mut':str(a['uuid']) }

        tDict['gene'] = str(','.join(list(set(genes))))
        tDict['gene_list'] = [ str(g) for g in set(genes)]

        results.append(tDict)

    print geneMut

    return results, geneMut


def getMutations(label):
    annotUrl = Urls.objects.get(id_webservice=WebService.objects.get(name='annotation').id, available=True)
    url = annotUrl.url + 'newapi/refset/?label=' + label
    print url
    
    req = urllib2.Request(url)
    u = urllib2.urlopen(req)
    res=u.read()
    res=yaml.safe_load(res)
    print res
    

    '''
    res = {
        "sequence_alteration": [
            {
                "end": 115256530, 
                "uuid": "6facb3945bee47829e86eeef1c16571b", 
                "gene_symbol": "NRAS", 
                "gene_uuid": "cc214f87b7ea4796b197582ee70966d4", 
                "hgvs_p": "unknown:p.Q61K", 
                "tx_ac": "ENST00000369535", 
                "start": 115256530, 
                "gene_ac": "ENSG00000213281", 
                "hgvs_g": "chr1:g.115256530G>T", 
                "chrom": "1", 
                "ref": "chr1",
                "hgvs_c": "ENST00000369535:c.181C>A",
            }, 
            {
                "end": 25378647, 
                "uuid": "f0484374cb874ca0bdeb4e1c59846ead", 
                "gene_symbol": "KRAS", 
                "gene_uuid": "b71fde9df8f7400689f9ee5f5ad4fceb", 
                "hgvs_p": "unknown:p.K117N", 
                "tx_ac": "ENST00000256078", 
                "start": 25378647, 
                "gene_ac": "ENSG00000133703", 
                "hgvs_g": "chr12:g.25378647T>G", 
                "chrom": "12", 
                "ref": "chr12",
                "hgvs_c": "ENST00000256078:c.351A>C",
            }, 
            {
                "end": 25378647, 
                "uuid": "869eab1547954be1b0601175f665c358", 
                "gene_symbol": "KRAS", 
                "gene_uuid": "b71fde9df8f7400689f9ee5f5ad4fceb", 
                "hgvs_p": "unknown:p.K117N", 
                "tx_ac": "ENST00000256078", 
                "start": 25378647, 
                "gene_ac": "ENSG00000133703", 
                "hgvs_g": "chr12:g.25378647T>A", 
                "chrom": "12", 
                "ref": "chr12",
                "hgvs_c": "ENST00000256078:c.351A>T",
            }
        ]
    }
    '''


    targets = aggregateTargets(res['sequence_alteration'], 'gene_symbol')
    
    return targets


def getTargets (targets):
    annotUrl = Urls.objects.get(id_webservice=WebService.objects.get(name='annotation').id, available=True)
    url = annotUrl.url + 'newapi/rtpcrAmpliconInfo/?amplicon_uuid=["' + '","'.join(targets) +'"]'
    print url
    req = urllib2.Request(url)
    u = urllib2.urlopen(req)
    #u = urllib2.urlopen()
    res=u.read()
    res = yaml.safe_load(res)
    #targets = aggregateTargets(res, 'name')
    #return targets
    return res


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
    url = annotUrl.url + 'newapi/refsetParameters/?exp_type=Real-Time%20PCR&labels=["' + '","'.join(labels) +'"]'
    #print url
    req = urllib2.Request(url)
    u = urllib2.urlopen(req)
    #u = urllib2.urlopen()
    res=u.read()
    res = yaml.safe_load(res)
    results = []
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
        res = yaml.safe_load(r.text)
        print res
        return res['refset_label']
    else:
        print r.status_code, r.text
        raise Exception('BAD REQUEST in label analysis')
