#######################################
#Choose annotation targets and samples to generate report
#######################################

NA = 'n'
WT = 'W'
MUT = 'M'
CFT = 'C'
MULTI = '*'

def getDisplayItem(matrix_val, matrix_mut_val, tx_ac, sa_cache):
    if matrix_val == NA:
        return {'type': 'single', 'class': 'na', 'text': ['n/a', 'n/a', 'n/a']}
    elif matrix_val == WT:
        return {'type': 'single', 'class': 'wt', 'text': ['wt', 'wt', 'wt']}
    elif matrix_val == MUT:
        return {'type': 'single', 'class': 'mut', 'text': sa_cache.getHGVS(matrix_mut_val[0], tx_ac)}
    elif matrix_val == CFT:
        # conflict
        h_g = []
        h_c = []
        h_p = []
        for v in matrix_mut_val:
            if v == WT:
                h_g.append('wt')
                h_c.append('wt')
                h_p.append('wt')
            else:
                h = sa_cache.getHGVS(v, tx_ac)
                h_g.append(h[0])
                h_c.append(h[1])
                h_p.append(h[2])
        h_g = ' | '.join(h_g)
        h_c = ' | '.join(h_c)
        h_p = ' | '.join(h_p)
        return {'type': 'single', 'class': 'conflict', 'text': [h_g, h_c, h_p]}
    elif matrix_val == MULTI:
        return {'type': 'multiple', 'cells': [getDisplayItem(it['type'], it['mut'], tx_ac, sa_cache) for it in matrix_mut_val]}

def getSiteLabel(site_uuid, site_type, tx_ac, gene_symbol):
    if site_type == 'region':
        gu = GenomeGraphUtility()
        res = gu.getGeneRegionInfo_byUuid([site_uuid])[0]
        site_info = [res[0], res[3], res[4], res[5], res[2], None, res[1], tx_ac, res[8], res[9], res[10], res[11]]
        altsite = AlterationSite(site_info)
        h_g = altsite.getLoc_g()
        c = altsite.getLoc_c()
        h_c = gene_symbol + ':' + c if tx_ac and c else h_g
        p = altsite.getLoc_p()
        h_p = gene_symbol + ':' + p if tx_ac and p else h_g
        return [h_g, h_c, h_p]
    elif site_type == 'gene':
        return [gene_symbol, gene_symbol, gene_symbol]

SITE_MANDATORY_KEYS = ["id", "tx"]
SITE_OPTIONAL_KEYS = ["chrom", "gene", "locg", "locc", "locp"]
SITE_KEYS = SITE_MANDATORY_KEYS + SITE_OPTIONAL_KEYS

@laslogin_required
@login_required
def report_annotations(request):

    if request.method == 'GET':
        print request.GET

        if 'searchGene' in request.GET:
            gu = GenomeGraphUtility()
            searchGene = request.GET['searchGene']
            genes = gu.getGenesByPrefix(searchGene)
            genes = [{'id': x[0], 'symbol': x[1], 'ac': x[2], 'chrom': x[3]} for x in genes]
            return HttpResponse(json.dumps(genes))

        elif 'getTranscripts' in request.GET:
            gu = GenomeGraphUtility()
            geneUuid = json.loads(request.GET['getTranscripts'])
    
            res = {}
            for uuid in geneUuid:
                defaultTx = gu.getDefaultTranscriptForGene(gene_uuid=uuid)['uuid']
                tx = gu.getTranscriptsForGene(uuid)
                tx = [{'id': x[0], 'tx_ac': x[1], 'num_exons': x[2], 'is_refseq': x[3]} for x in tx]
                res[uuid] = {'all': tx, 'default': defaultTx}
            
            return HttpResponse(json.dumps(res))
            # format: list of objects with 'id' and 'text'

        elif 'getExons' in request.GET:
            gu = GenomeGraphUtility()
            txUuid = request.GET['getExons']
            exons = gu.getExonsForTranscript(txUuid)
            exons = [{'id': x[0], 'cnt': x[1], 'length': x[2]} for x in exons]
            return HttpResponse(json.dumps(exons))
            # format: list of objects with 'id' and 'text'

        elif 'getAltLocInGene' in request.GET:
            print "getAltLocInGene"
            gu = GenomeGraphUtility()
            geneUuid = request.GET['getAltLocInGene']
            txUuid = request.GET['tx'] if request.GET['tx'] != '-1' else None
            exonUuid = request.GET['exon'] if request.GET['exon'] != '-1' else None
            cds_only = False
            alt_sites = gu.getAlterationSitesInGene(geneUuid, txUuid, exonUuid, cds_only)
            alt_sites = [AlterationSite(x) for x in alt_sites]
            if txUuid:
                alt_sites.sort(key=lambda x:x.start_c + x.offset_c)
            else:
                alt_sites.sort(key=lambda x:x.start)
            alt_sites_list = [{'id': x.uuid, 'locg': x.getLoc_g().split(':')[1], 'locc': x.getLoc_c() if txUuid else None, 'locp': x.getLoc_p() if txUuid else None, 'symbol': x.gene_symbol, 'chrom': x.chrom, 'tx_ac': x.tx_ac} for x in alt_sites]
            return HttpResponse(json.dumps(alt_sites_list)) 

        elif 'getGenesInRegion' in request.GET:
            chrom = request.GET['getGenesInRegion']
            start = int(request.GET['regionStart'])
            end = int(request.GET['regionEnd'])
            gu = GenomeGraphUtility()
            genes = gu.getGenesInRegion(chrom, start, end)
            genes = [{'id': x[0], 'text': '{0} ({1})'.format(x[1],x[2]),'symbol': x[1], 'ac': x[2], 'chrom': x[3]} for x in genes]
            return HttpResponse(json.dumps(genes))

    elif request.method == 'POST':
        if 'action' in request.POST and request.POST['action'] == 'getSitesFile':
            try:
                sitesList = request.POST['sitesList']
                sitesList = json.loads(sitesList)
            except:
                return HttpResponseServerError("sitesList not found in request")
            try:    
                now = datetime.datetime.now()
                fileName = "Custom sites-" + str(request.user) + '-' + str(now) + ".las"
                fullPath = os.path.join(settings.TEMP_ROOT, fileName)
                
                headers = "#" + '\t'.join(SITE_KEYS) + '\n'
                body = '\n'.join(['\t'.join([site[k] for k in SITE_MANDATORY_KEYS] + [site[k] for k in SITE_OPTIONAL_KEYS if site.hasKey(k)]) for site in sitesList])
                
                fout = open(fullPath, "w")
                fout.write(headers)
                fout.write(body)
                fout.close()
                
                fout = open(fullPath, "r")
                response = HttpResponse(fout, content_type='application/octet-stream')
                response['Content-Disposition'] = 'attachment; filename=' + fileName
                os.remove(fullPath)

                return response
            
            except Exception as e:
                return HttpResponseServerError(str(e))



        elif 'seqalt' in request.POST and 'samples' in request.POST:

            seqalt = json.loads(request.POST['seqalt'])
            sample_patterns = json.loads(request.POST['samples'])

            #print seqalt
            
            # region_groups[0] is the group of all single-region targets taken as a whole (if any)
            # region_groups[i], i > 0 are the groups of regions implied by gene targets (if any)
            region_groups = [[]]
            group_gene = []
            results = []

            gu = GenomeGraphUtility()
            # cache sequence alteration objects
            sa_cache = SequenceAlterationCache()

            print "annotations1"
            if len(seqalt) > 0:
                has_ref = True
                # split reference targets between genes and regions
                for k,v in seqalt.iteritems():
                    if v['type'] == 'region':
                        region_groups[0].append(k)
                    elif v['type'] == 'gene':
                        res = gu.getAlterationSitesInGene(k)
                        group_gene.append(k)
                        region_groups.append([x[0] for x in res])
                # retrieve gene symbol
                # for regions
                print "get gene symbol for regions"
                res = gu.getGeneRegionInfo_byUuid(region_groups[0])
                for x in res:
                    seqalt[x[0]]['gene_symbol'] = x[1]
                print "done"
                # for genes
                print "get gene symbol for genes"
                res = gu.getGeneInfo_byUuid(group_gene)
                for x in res:
                    seqalt[x[0]]['gene_symbol'] = x[1]
                print "done"

                if len(sample_patterns) > 0:
                    has_samples = True
                    #samples = gu.getGenidListFromGenidPatterns(sample_patterns)
                    
                    for group in region_groups:
                        r = gu.getAnnotationNew_fromSamplesAndAltSites(sample_patterns, group, ["sequence_alteration"])
                        results.append(r)

                else:
                    has_samples = False
                    print "get annotations for regions"
                    print region_groups[0]
                    for group in region_groups:
                        r = gu.getAnnotationNew_fromAltSites(group, ["sequence_alteration"])
                        results.append(r)
                    print "done"
            
            elif len(sample_patterns) > 0:
                has_ref = False
                has_samples = True
                #samples = gu.getGenidListFromGenidPatterns(sample_patterns)
                
                print "start: getAnnotationNew_fromSamples"
                r = gu.getAnnotationNew_fromSamples(sample_patterns, ["sequence_alteration"])
                print "end: getAnnotationNew_fromSamples"
                results.append(r)
            else:
                raise Exception("At least one alteration site or one sample must be provided")

            print "annotations2"

            sites = set()
            samples = set()

            # update samples with all samples found that match specified pattern
            for res in results:
                for an in res:
                    samples.update(an['samples'])

            # update sites with all single sites
            for an in results[0]:
                sites.update(an['refset'])
            # update sites with all full-gene sites
            sites = list(sites)
            sites = group_gene + sites


            samples = list(samples)

            if len(seqalt) == 0:
                res = gu.getGeneRegionInfo_byUuid(sites)
                site_geneinfo = {x[0]:(x[7], x[1]) for x in res}
                gene_tx = {}
                for g in list(set([x[7] for x in res])):
                    gene_tx[g] = gu.getDefaultTranscriptForGene(gene_uuid=g)['ac']
                for s in sites:
                    seqalt[s] = {'type': 'region', 'tx': gene_tx[site_geneinfo[s][0]], 'gene_symbol': site_geneinfo[s][1]}

                print "no ref provided, computed my own"
                
            sites_map = {x:i for i,x in enumerate(sites)}
            samples_map = {x:i for i,x in enumerate(samples)}

            print "matrix1"
            #matrix = [[[] for column in sites] for row in samples]
            from array import array
            n_samples = len(samples)
            n_sites = len(sites)
            print "n_samples = ", n_samples
            print "n_sites = ", n_sites
            # matrix is a C-like char-valued matrix
            # n -> not analysed
            # w -> wt in previous analyses
            # * -> wt in current/last analysis
            # m -> mut
            # c -> conflict

            matrix = array('c', [NA] * n_samples * n_sites)
            matrix_mut = {}
            

            print "matrix2"

            print "samples = ", samples
            print "sites = ", sites
            ### single-site targets
            for cnt, an in enumerate(results[0]):
                # make a list of non-wt entries
                non_wt = set()

                # fill non_wt with failed analysis points
                failedAnalysis_list = FailedAnalysis.objects.filter(analysis=Analysis.objects.get(graph_uuid=an['uuid']),ref_region_uuid__in=sites,sampleGenid__in=samples)
                for failedAnalysis in failedAnalysis_list:
                    i = samples_map[failedAnalysis.sampleGenid]
                    j = sites_map[failedAnalysis.ref_region_uuid]
                    non_wt.add((i,j))

                # set mutations
                for a in an['annotations']:
                    i = samples_map[a[2]]
                    j = sites_map[a[0]]
                    non_wt.add((i,j))
                    idx = i*n_sites + j
                    if matrix[idx] == NA:
                        matrix[idx] = MUT
                        matrix_mut[(i,j)] = [a[1]]
                        #matrix[i][j][cnt] = a[1]
                    elif matrix[idx] == WT:
                        matrix[idx] = CFT
                        matrix_mut[(i,j)] = [WT, a[1]]
                    elif matrix[idx] == MUT:
                        if matrix_mut[(i,j)][0] != a[1]:
                            matrix[idx] = CFT
                            matrix_mut[(i,j)].append(a[1])
                    elif matrix[idx] == CFT:
                        if a[1] not in matrix_mut[(i,j)]:
                            matrix_mut[(i,j)].append(a[1])
                    
                # set wt
                for sample in an['samples']:
                    i = samples_map[sample]
                    for site in an['refset']:
                        j = sites_map[site]
                        if (i,j) in non_wt:
                            continue
                        idx = i*n_sites + j
                        if matrix[idx] == NA:
                            matrix[idx] = WT
                        elif matrix[idx] == MUT:
                            matrix[idx] = CFT
                            matrix_mut[(i,j)].append(WT)
                        elif matrix[idx] == CFT:
                            if WT not in matrix_mut[(i,j)]:
                                matrix_mut[(i,j)].append(WT)
                        #matrix[i][j].append('wt')

                print "non_wt = ", non_wt

            print "matrix3"
        
            print "matrix4"
            ### gene targets
            for index, gene_an in enumerate(results[1:]):
                # build reference for gene
                sites_gene = set()
                for an in gene_an:
                    sites_gene.update(an['refset'])
                sites_gene_map = {x:i for i,x in enumerate(sites_gene)}
                n_sites_gene = len(sites_gene)
                
                # build matrix for gene
                print "matrix for gene:",group_gene[index]

                matrix_gene = array('c', [NA] * n_samples * n_sites_gene)
                matrix_mut_gene = {}

                # fill matrix for gene
                for cnt, an in enumerate(gene_an):
                    # make a list of non-wt entries
                    non_wt = set()
                    # set mutations
                    for a in an['annotations']:
                        i = samples_map[a[2]]
                        j = sites_gene_map[a[0]]
                        non_wt.add((i,j))
                        idx = i*n_sites_gene + j
                        if matrix_gene[idx] == NA:
                            matrix_gene[idx] = MUT
                            matrix_mut_gene[(i,j)] = [a[1]]
                        elif matrix_gene[idx] == WT:
                            matrix_gene[idx] = CFT
                            matrix_mut_gene[(i,j)] = [WT, a[1]]
                        elif matrix_gene[idx] == MUT:
                            if matrix_mut_gene[(i,j)][0] != a[1]:
                                matrix_gene[idx] = CFT
                                matrix_mut_gene[(i,j)].append(a[1])
                        elif matrix_gene[idx] == CFT:
                            if a[1] not in matrix_mut_gene[(i,j)]:
                                matrix_mut_gene[(i,j)].append(a[1])
                    
                    # set wt
                    for sample in an['samples']:
                        i = samples_map[sample]
                        for site in an['refset']:
                            j = sites_gene_map[site]
                            if (i,j) in non_wt:
                                continue
                            idx = i*n_sites_gene + j
                            if matrix_gene[idx] == NA:
                                matrix_gene[idx] = WT
                            elif matrix_gene[idx] == MUT:
                                matrix_gene[idx] = CFT
                                matrix_mut_gene[(i,j)].append(WT)
                            elif matrix_gene[idx] == CFT:
                                if WT not in matrix_mut_gene[(i,j)]:
                                    matrix_mut_gene[(i,j)].append(WT)

                # reduce gene matrix columns to a single column representing the whole gene
                j_full_matrix = sites_map[group_gene[index]]
                # for each sample
                for i in xrange(0, n_samples):
                    idx = i*n_sites_gene
                    idx_full_matrix = i*n_sites
                    # for each gene site
                    gene_summary = []
                    for j in xrange(0, n_sites_gene):
                        if matrix_gene[idx+j] in [MUT, CFT]:
                            gene_summary.append({'type': matrix_gene[idx+j], 'mut': matrix_mut_gene[(i,j)]})
                    if len(gene_summary) > 0:
                        matrix[idx_full_matrix + j_full_matrix] = MULTI
                        matrix_mut[(i,j_full_matrix)] = gene_summary
                    else:
                        matrix[idx_full_matrix + j_full_matrix] = WT

            print "Pruning"
            if has_samples == False:
                print "Prune samples"
                print "before:", len(samples)
                to_delete = []
                for i in xrange(0,len(samples)):
                    if matrix[i*n_sites:(i+1)*n_sites].tostring() == WT * n_sites:
                        to_delete.append(i)
                for i in reversed(to_delete):
                    del samples[i]
                print "after:", len(samples)

            elif has_ref == False:
                print "Prune sites"
                print "before:", len(sites)

                to_delete = []
                for j in xrange(0,len(sites)):
                    is_wt = True
                    for i in xrange(j,n_samples*n_sites,n_sites):
                        if matrix[i] != WT:
                            is_wt = False
                            break
                    if is_wt:
                        to_delete.append(j)

                for j in reversed(to_delete):
                    del sites[j]
                
                print "after:", len(sites)

            print "Build matrix for display"
            
            MAX_SAMPLES = 1000
            MAX_SITES = 20

            n_displ_samples = min(MAX_SAMPLES, len(samples))
            n_displ_sites = min(MAX_SITES, len(sites))

            print "displaying %d samples, %d sites" % (n_displ_samples, n_displ_sites)

            matrix_for_display = []
            for sample in samples[:n_displ_samples]:
                i = samples_map[sample]
                displ_row = []
                for site in sites[:n_displ_sites]:
                    j = sites_map[site]

                    matrix_val = matrix[i*n_sites+j]
                    matrix_mut_val = matrix_mut.get((i,j))
                    tx_ac = seqalt[site]['tx'] if site in seqalt else None

                    display_item = getDisplayItem(matrix_val, matrix_mut_val, tx_ac, sa_cache)
                    displ_row.append(display_item)

                matrix_for_display.append(displ_row)

            # build labels for x axis
            x_labels = []
            for s in sites[:n_displ_sites]:
                info = seqalt[s]
                l = getSiteLabel(s, info['type'], info['tx'], info['gene_symbol'])
                x_labels.append(l)

            matrix_for_display = [[l]+r for l,r in zip(list(samples[:n_displ_samples]), matrix_for_display)]
            return render_to_response('displayReport.html', {'x_labels': x_labels, 'matrix': matrix_for_display}, RequestContext(request))
                    

    gu = GenomeGraphUtility()
    chrom = gu.getAllChromosomes()

    def myCmp(x,y):
        if x.isdigit() == y.isdigit():
            if x.isdigit():
                return int(x) - int(y)
            else:
                return -1 if x < y else 1
        else:
            return -1 if x.isdigit() else 1
    chrom.sort(key=lambda k:k[1], cmp=myCmp)

    print "here"
    return render_to_response('report_annotations.html', {'chrom': chrom}, RequestContext(request))

'''
        elif 'getSeqAltInGene' in request.GET:
            gu = GenomeGraphUtility()
            #seq_utils_tx = RefSequence('transcriptome')
            #seq_utils_gen = RefSequence('genome')
            geneUuid = request.GET['getSeqAltInGene']
            txUuid = request.GET['tx'] if request.GET['tx'] != '-1' else None
            exonUuid = request.GET['exon'] if request.GET['exon'] != '-1' else None
            cds_only = False
            seqalt = gu.getSequenceAlterationsInGene(geneUuid,cds_only,txUuid,exonUuid)
            sa_list = []
            for x in seqalt:
                s = SequenceAlteration()
                s.byUuid(x[0], x)
                sa = {  'id': x[0],
                        'chrom': x[1],
                        'symbol': x[9],
                        'tx_ac': x[10],
                        'hgvsg': s.getHGVS_g().split(':')[1],
                        'hgvsc': s.getHGVS_c(x[10]).split(':')[1] if txUuid else None,
                        'hgvsp': s.getHGVS_p(x[10]).split(':')[1] if txUuid else None,
                    }
                sa_list.append(sa)
            return HttpResponse(json.dumps(sa_list))
'''

#######################################
#PGDX report evaluation view
#######################################

@laslogin_required
@login_required
def pgdxEvaluate(request):
    if request.method == 'GET':
        
        if 'geneSymbol' in request.GET and 'genMut' in request.GET and 'txMut' in request.GET and 'aaMut' in request.GET:
            geneSymbol = request.GET['geneSymbol']
            genMut = request.GET['genMut']
            txMut = request.GET['txMut']
            aaMut = request.GET['aaMut']
            
            chrom, rest = genMut.split(':')
            pos18 = int(rest[:-3])
            wtBase, mutBase = rest[-3], rest[-1]

            hg18 = tempfile.NamedTemporaryFile()
            hg18.delete = False
            hg18_name = hg18.name
            hg18.write(chrom + '\t' + str(pos18-3) + '\t' + str(pos18+2) + '\tpgdxmut\n')
            hg18.close()

            hg19 = tempfile.NamedTemporaryFile()
            hg19.delete = False
            hg19_name = hg19.name
            hg19.close()

            seq = tempfile.NamedTemporaryFile()
            seq.delete = False
            seq_name = seq.name
            seq.close()

            # call liftOver tool to convert Hg18 coordinate to Hg19
            ret = call(["/home/alberto/Lavoro/Downloads/kent/userApps/bin/liftOver", hg18_name, "/home/alberto/Lavoro/Downloads/kent/liftOver_chain_files/hg18ToHg19.over.chain", hg19_name, "/dev/null"])
            # call twoBitToFa tool to obtain the nucleotide sequence in the mutation whereabouts (2 bases backward + 2 bases forward)
            ret = call(["/home/alberto/Lavoro/Downloads/kent/userApps/bin/twoBitToFa", "-bed="+hg19_name, "-bedPos", "/home/alberto/Lavoro/Downloads/blat/seq/hg19.2bit", seq_name])

            with open(hg19_name, 'r') as f:
                pos19 = int(f.readline().split()[1])+2

            # find transcripts that contain pos19
            tx_list = UCSCrefFlat.objects.filter(geneName=geneSymbol)
            chosen_tx = []
            for tx in tx_list:
                es = loadJSONfield(tx, 'exonStarts')
                ee = loadJSONfield(tx, 'exonEnds')
                for j in xrange(0,tx.exonCount):
                    if pos19 in xrange(es[j], ee[j]):
                        chosen_tx.append((tx, j))
                        break

            if len(chosen_tx) == 0:
                return HttpResponse("No transcript found including position " + chrom + ":" + str(pos19+1))
            else:
                with open(seq_name, 'r') as f:
                    f.readline()
                    sequence = f.readline()

                from Bio.Seq import Seq
                response = ''
                
                for tx, exon in chosen_tx:
                    es = loadJSONfield(tx, 'exonStarts')
                    ee = loadJSONfield(tx, 'exonEnds')

                    if tx.strand == '+':
                        # find first exon that falls within coding region
                        first_exon = 0
                        while ee[first_exon] < tx.cdsStart:
                            first_exon += 1
                        if first_exon != exon:
                            #in the formula, "pos19+1" because pos19 is 0-based, but used here as right coordinate (the convention is 1-based for right coordinates)
                            offset = (ee[first_exon] - tx.cdsStart) + sum([(ee[i] - es[i]) for i in xrange(first_exon+1,exon)]) + (pos19+1 - es[exon])
                        else:
                            offset = (pos19+1) - tx.cdsStart
                        # "offset-1" is to simplify arithmetics for identifying codon
                        x = (offset-1) % 3
                        triplet = sequence[2-x:5-x]
                        mut_sequence = sequence[:2] + mutBase + sequence[3:]
                        mut_triplet = mut_sequence[2-x:5-x]
                        aa_position = (offset-1)/3 + 1
                        exon += 1 # changed here for visualization purposes
                    else:
                        # find last exon that falls within coding region
                        last_exon = tx.exonCount-1
                        while es[last_exon] > tx.cdsEnd:
                            last_exon -= 1
                        if last_exon != exon:
                            offset = (ee[exon] - pos19) + sum([(ee[i] - es[i]) for i in xrange(exon+1,last_exon)]) + (tx.cdsEnd - es[last_exon])
                        else:
                            offset = tx.cdsEnd - pos19
                        x = (offset-1) % 3
                        # triplet must be taken backwards because we are on the negative strand
                        triplet = sequence[x:x+3]
                        mut_sequence = sequence[:2] + mutBase + sequence[3:]
                        mut_triplet = mut_sequence[x:x+3]
                        aa_position = (offset-1)/3 + 1
                        x = 2 - x # changed here for visualization purposes
                        exon = tx.exonCount - exon # changed here for visualization purposes
    
                    triplet_seq = Seq(triplet)
                    mut_triplet_seq = Seq(mut_triplet)

                    if tx.strand == '+':
                        aa_seq = triplet_seq.translate()
                        mut_aa_seq = mut_triplet_seq.translate()
                    else:
                        aa_seq = triplet_seq.reverse_complement().translate()
                        mut_aa_seq = mut_triplet_seq.reverse_complement().translate()

                    response += "Transcript: " + tx.name + "<br>"
                    response += "Strand: " + tx.strand + "<br>"
                    response += "Position: " + chrom + ':' + str(pos19) + "<br>"
                    response += "Exon: " + str(exon) + "<br>"
                    response += "Context: " + sequence[:2] + "<font color='red'><b>" + sequence[2] + "</b></font>" + sequence[3:] + "<br>"
                    response += "Nucleotide position: " + str(offset) + "<br>"
                    response += "Nucleotide mutation: " + triplet[:x] + "<font color='red'><b>" + triplet[x] + "</b></font>" + triplet[x+1:]
                    response += " > "
                    response += mut_triplet[:x] + "<font color='red'><b>" + mut_triplet[x] + "</b></font>" + mut_triplet[x+1:]
                    response += "<br>"
                    response += "Amino acid position: " + str(aa_position) + "<br>"
                    response += "Amino acid mutation: <font color='red'><b>" + str(aa_seq) + "</b></font> > <font color='red'><b>" + str(mut_aa_seq) + "</b></font>"
                    response += "<br><hr><br>"

                os.remove(hg18_name)
                os.remove(hg19_name)
                os.remove(seq_name)

                return HttpResponse(response)

        else:
            return render_to_response("pgdxEvaluate.html", RequestContext(request))


#######################################
#Test view to display gene plot with exons
#######################################

@laslogin_required
@login_required
def plotGene(request):
    return render_to_response("plotGene.html", RequestContext(request))

