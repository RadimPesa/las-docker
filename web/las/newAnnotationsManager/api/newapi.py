from django.db import transaction
from rest_framework import status as http_status
from rest_framework.decorators import api_view, parser_classes
from rest_framework.response import Response
from annotations.models import *
from annotations.lib.graph_utils import *
from annotations.lib.genomic_models import *
from parsers import *
import json
from django.utils import timezone

# TECHNOLOGY-SPECIFIC APIs

@api_view(['GET'])
def sequenomPlates(request):
    """
    Get sequenom plate barcodes
    """
    print "[annotationsAPI: sequenomPlates]"
    if request.method == 'GET':
        try:
            l = Annotation_ShortGeneticVariation.objects.filter(plate_id__icontains=request.GET['term'].strip()).values_list('plate_id').distinct()
            plates = [x[0] for x in l]
            resp = Response(plates, status=http_status.HTTP_200_OK)
            #resp['Access-Control-Allow-Headers'] = 'origin, content-type, accept'
            return resp
        except:
            return Response([], status=http_status.HTTP_200_OK)

compl_bases = {'A': 'T', 'T': 'A', 'G': 'C', 'C': 'G'}

# multiple technologies
@api_view(['GET'])
def geneInfo(request):
    """
    Get gene information (autocomplete)
    """
    print "[annotationsAPI: geneInfo]"
    if request.method == 'GET':
        try:
            searchGene = request.query_params['q']
        except Exception as error:
            print error
            return Response(str(error), status=http_status.HTTP_400_BAD_REQUEST)
        
        gu = GenomeGraphUtility()
        genes = gu.getGenesByPrefix(searchGene)
        genes = [{'id': x[0], 'symbol': x[1], 'ac': x[2], 'chrom': x[3]} for x in genes]
       
        resp = Response(genes, status=http_status.HTTP_200_OK)
        resp['Access-Control-Allow-Headers'] = 'origin, content-type, accept'
        return resp

@api_view(['GET'])
def transcriptInfo(request):
    """
    Get Ensembl transcript information (autocomplete)
    """
    print "[annotationsAPI: transcriptInfo]"
    if request.method == 'GET':
        try:
            searchTx = request.query_params['q']
        except Exception as error:
            print error
            return Response(str(error), status=http_status.HTTP_400_BAD_REQUEST)
        
        gu = GenomeGraphUtility()
        transcripts = gu.getTranscriptsByPrefix(searchTx)
        transcripts = [{'id': x[0], 'ac': x[1], 'chrom': x[2], 'start': x[3], 'end': x[4], 'strand': x[5], 'is_refseq': x[6], 'length': x[7], 'is_default': x[8]} for x in transcripts]
       
        resp = Response(transcripts, status=http_status.HTTP_200_OK)
        resp['Access-Control-Allow-Headers'] = 'origin, content-type, accept'
        return resp

@api_view(['GET'])
def refSeqInfo(request):
    """
    Get RefSeq transcript information (autocomplete)
    """
    print "[annotationsAPI: refSeqInfo]"
    if request.method == 'GET':
        try:
            searchTx = request.query_params['q']
        except Exception as error:
            print error
            return Response(str(error), status=http_status.HTTP_400_BAD_REQUEST)
        
        transcripts = map(lambda r: {'id': r.id, 'ac': r.external_id}, EnsemblTranscriptXref.objects.filter(external_id__istartswith=searchTx)[:10])
               
        resp = Response(transcripts, status=http_status.HTTP_200_OK)
        resp['Access-Control-Allow-Headers'] = 'origin, content-type, accept'
        return resp

@api_view(['GET'])
def getGeneDefaultTx(request):
    """
    Get default transcript for a given gene
    """
    print "[annotationsAPI: getGeneDefaultTx]"
    if request.method == 'GET':
        gene_uuid = request.query_params.get('uuid', None)
        gene_ac = request.query_params.get('ac', None)
        gene_symbol = request.query_params.get('symbol', None)
        if not (gene_uuid or gene_ac or gene_symbol):
            return Response("Mandatory parameter missing: uuid or ac or symbol", status=http_status.HTTP_400_BAD_REQUEST)
        
        gu = GenomeGraphUtility()
        tx = gu.getDefaultTranscriptForGene(gene_uuid=gene_uuid, gene_ac=gene_ac, gene_symbol=gene_symbol)
        if tx:
            r = {'uuid': tx[0], 'ac': tx[1], 'isRefSeq': tx[2]}
        else:
            r = {}
       
        resp = Response(r, status=http_status.HTTP_200_OK)
        resp['Access-Control-Allow-Headers'] = 'origin, content-type, accept'
        return resp

# Sequenom
@api_view(['GET'])
def snpInfo(request):
    """
    Get gene information (autocomplete)
    """
    print "[annotationsAPI: snpInfo]"
    if request.method == 'GET':
        try:
            searchSnp = request.query_params['q']
        except Exception as error:
            print error
            return Response(str(error), status=http_status.HTTP_400_BAD_REQUEST)
        
        gu = GenomeGraphUtility()
        snps = gu.getSGVByPrefix(searchSnp)
        snps = [{'uuid': x[0], 'name': x[1], 'allele': x[2], 'alt': x[3], 'chrom': x[4], 'start': x[5], 'end': x[6], 'strand': x[7]} for x in snps]
       
        resp = Response(snps, status=http_status.HTTP_200_OK)
        resp['Access-Control-Allow-Headers'] = 'origin, content-type, accept'
        return resp

# Sanger
@api_view(['GET'])
def ampliconInfo(request):
    """
    Get amplicon information
    """
    print "[annotationsAPI: ampliconInfo]"
    if request.method == 'GET':
        if 'amplicon_uuid' in request.query_params:
            try:
                pcrProduct_uuid = json.loads(request.query_params['amplicon_uuid'])
                gene_uuid = None
            except:
                return Response("Incorrect call format", status=http_status.HTTP_400_BAD_REQUEST)
        elif 'gene_uuid' in request.query_params:
            gene_uuid = request.query_params['gene_uuid']
            pcrProduct_uuid = None
        else:
            return Response("Incorrect call format", status=http_status.HTTP_400_BAD_REQUEST)
        
        gu = GenomeGraphUtility()
        if pcrProduct_uuid:
            pcrProduct = gu.getPCRProductByUuidList(pcrProduct_uuid)
        else:
            label = ExperimentType.objects.get(name='Sanger sequencing').technologyLabel
            pcrProduct = gu.getPCRProductInGene(gene_uuid, label)
        res = []
        for r in pcrProduct:
            res.append({
                'uuid': r[0],
                'name': r[1],
                'length': int(r[2]),
                'region_uuid': r[19],
                'ref': r[3],
                'start_base': r[4],
                'end_base': r[5],
                'gene_uuid': r[6],
                'gene_symbol': r[7],
                'type': r[18],
                'primers': [{
                    'name': r[8],
                    'length': r[9],
                    'ref': r[10],
                    'start_base': r[11],
                    'end_base': r[12],
                    },{
                    'name': r[13],
                    'length': r[14],
                    'ref': r[15],
                    'start_base': r[16],
                    'end_base': r[17],
                    }
                ]
            })
         
        return Response(res, status=http_status.HTTP_200_OK)

# In-situ hybridization
@api_view(['GET'])
def probeInfo(request):
    """
    Get probe information
    """
    print "[annotationsAPI: probeInfo]"
    if request.method == 'GET':
        if 'probe_uuid' in request.query_params:
            try:
                probe_uuid = json.loads(request.query_params['probe_uuid'])
                gene_uuid = None
            except:
                return Response("Incorrect call format", status=http_status.HTTP_400_BAD_REQUEST)
        elif 'gene_uuid' in request.query_params:
            gene_uuid = request.query_params['gene_uuid']
            probe_uuid = None
        else:
            return Response("Incorrect call format", status=http_status.HTTP_400_BAD_REQUEST)
        
        gu = GenomeGraphUtility()
        if probe_uuid:
            probe = gu.getPrimerByUuidList(probe_uuid)
        else:
            label = ExperimentType.objects.get(name='In-situ hybridization').technologyLabel
            probe = gu.getPrimerInGene(gene_uuid, label)
        res = []
        remap = {'transcriptome': 'cDNA', 'genome': 'gDNA'}
        for r in probe:
            for al in r[3]:
                res.append({
                    'uuid': r[0],
                    'name': r[1],
                    'length': int(r[2]),
                    'region_uuid': al[0],
                    'ref': al[1],
                    'start_base': al[2],
                    'end_base': al[3],
                    'strand': al[4],
                    'gene_symbol': al[5],
                    'type': remap[al[6]]
                })
         
        return Response(res, status=http_status.HTTP_200_OK)

# RT-PCR
@api_view(['GET'])
def rtpcrAmpliconInfo(request):
    """
    Get amplicon information
    """
    print "[annotationsAPI: rtpcrAmpliconInfo]"
    if request.method == 'GET':
        if 'amplicon_uuid' in request.query_params:
            try:
                pcrProduct_uuid = json.loads(request.query_params['amplicon_uuid'])
                gene_uuid = None
            except:
                return Response("Incorrect call format", status=http_status.HTTP_400_BAD_REQUEST)
        elif 'gene_uuid' in request.query_params:
            gene_uuid = request.query_params['gene_uuid']
            pcrProduct_uuid = None
        else:
            return Response("Incorrect call format", status=http_status.HTTP_400_BAD_REQUEST)
        
        gu = GenomeGraphUtility()
        if pcrProduct_uuid:
            pcrProduct = gu.getPCRProductByUuidList(pcrProduct_uuid)
        else:
            label = ExperimentType.objects.get(name='Real-Time PCR').technologyLabel
            pcrProduct = gu.getPCRProductInGene(gene_uuid, label)
        res = []
        for r in pcrProduct:
            res.append({
                'uuid': r[0],
                'name': r[1],
                'length': int(r[2]),
                'region_uuid': r[19],
                'ref': r[3],
                'start_base': r[4],
                'end_base': r[5],
                'gene_uuid': r[6],
                'gene_symbol': r[7],
                'type': r[18],
                'primers': [{
                    'name': r[8],
                    'length': r[9],
                    'ref': r[10],
                    'start_base': r[11],
                    'end_base': r[12],
                    },{
                    'name': r[13],
                    'length': r[14],
                    'ref': r[15],
                    'start_base': r[16],
                    'end_base': r[17],
                    }
                ]
            })
         
        return Response(res, status=http_status.HTTP_200_OK)

# Sequenom
@api_view(['GET'])
def snpProbeInfo(request):
    """
    Get SNP information
    """
    print "[annotationsAPI: snpProbeInfo]"
    if request.method == 'GET':
        searchSnp = None
        snp_uuid = None
        if 'q' in request.query_params:
            searchSnp = request.query_params['q']
        elif 'uuid' in request.query_params:
            try:
                snp_probe_uuid = json.loads(request.query_params['uuid'])
            except Exception as e:
                return Response(str(e), status=http_status.HTTP_400_BAD_REQUEST)

        else:
            return Response("Incorrect call format", status=http_status.HTTP_400_BAD_REQUEST)

        gu = GenomeGraphUtility()
        if searchSnp:
            snps = gu.getSGVProbeBySGVPrefix(searchSnp)
        elif snp_probe_uuid:
            snps = gu.getSGVProbeByUuid_list(snp_probe_uuid)
        snps = [{'uuid': x['uuid'], 'name': x['name'], 'class': x['class'], 'allele': x['allele'], 'alt': x['alt'], 'chrom': x['chrom'], 'start': x['start'], 'end': x['end'], 'strand': x['strand']} for x in snps]

        resp = Response(snps, status=http_status.HTTP_200_OK)
        resp['Access-Control-Allow-Headers'] = 'origin, content-type, accept'
        return resp

#### N.B. this method is obsolete and must not be used!!!
@api_view(['GET'])
def snpInSnpProbe(request):
    """
    Get SNP information
    """
    print "[annotationsAPI: snpInSnpProbe]"
    if request.method == 'GET':
        if 'uuid' in request.query_params:
            try:
                snp_probe_uuid = json.loads(request.query_params['uuid'])
            except Exception as e:
                return Response(str(e), status=http_status.HTTP_400_BAD_REQUEST)
        else:
            return Response("Incorrect call format", status=http_status.HTTP_400_BAD_REQUEST)

        gu = GenomeGraphUtility()
        snps = gu.getSGVinSGVProbeByUuid_list(snp_probe_uuid)
        snps_list = []
        for x in snps:
            obj = ShortGeneticVariation()
            obj.byUuid(x['uuid'], x)
            i = obj.getInfo()
            y = {'probe_uuid': x['probe_uuid'], 'snp_uuid': x['uuid'], 'name': x['name'], 'class': i['type'], 'allele': x['allele'], 'alt': x['alt'] if x['strand'] == '+' else compl_bases[x['alt']], 'num_repeats': x['num_repeats'], 'chrom': x['chrom'], 'start': x['start'], 'end': x['end'], 'strand': x['strand']}
            snps_list.append(y)

        resp = Response(snps_list, status=http_status.HTTP_200_OK)
        resp['Access-Control-Allow-Headers'] = 'origin, content-type, accept'
        return resp

@api_view(['GET'])
def snpFromDbSnp(request):
    """
    Get SNP information
    """
    print "[annotationsAPI: snpFromDbSnp]"
    if request.method == 'GET':
        try:
            searchSnp = request.query_params['q']
        except:
            return Response("Missing parameter 'q'", status=http_status.HTTP_400_BAD_REQUEST)

        snps = UCSCSnp141.objects.filter(name__istartswith=searchSnp)
        snps = [{'id': x.id, 'name': x.name, 'num_alleles': (x.observed.count('/') + 1) if x.observed != "lengthTooLong" else 0, 'alleles': x.observed.split('/') if x.snpClass != "microsatellite" else [z for z in x.alleles.split(',')[:-1]], 'type': x.snpClass} for x in snps[:10]]

        resp = Response(snps, status=http_status.HTTP_200_OK)
        resp['Access-Control-Allow-Headers'] = 'origin, content-type, accept'
        return resp


#### N.B. this method is obsolete and must not be used!!!
'''@api_view(['GET'])
def alterationsInAmplicon(request):
    """
    Get alterations that fall within region amplified by amplicon
    """
    if request.method == 'GET':
        if 'amplicon_uuid' in request.query_params:
            try:
                pcrProduct_uuid = json.loads(request.query_params['amplicon_uuid'])
            except:
                return Response("Incorrect call format", status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response("Incorrect call format", status=status.HTTP_400_BAD_REQUEST)
        
        gu = GenomeGraphUtility()
        # get alterations for gDNA amplicons
        gene_alt_list_gdna = gu.getAlterationsIn_gDNAAmpliconList(pcrProduct_uuid)
        # get alterations for cDNA amplicons
        gene_alt_list_cdna = gu.getAlterationsIn_cDNAAmpliconList(pcrProduct_uuid)
        
        res = []
            
        for row in gene_alt_list_gdna:
            obj = {'uuid': row[0], 'name': row[1]}
            regions = {}
            gene_uuid = row[2]
            defaultTx = gu.getDefaultTranscriptForGene(gene_uuid=gene_uuid)
            for alt_info in row[4]:
                if alt_info[0] is None:
                    continue
                s = SequenceAlteration()
                s.byUuid(alt_info[4])
                region_uuid = alt_info[0]
                if region_uuid not in regions:
                    regions[region_uuid] = {
                        'uuid': region_uuid,
                        'gene_symbol': row[3],
                        'chrom': alt_info[1],
                        'start': alt_info[2],
                        'end': alt_info[3],
                        'alterations': []
                    }
                regions[region_uuid]['alterations'].append({
                    'uuid': alt_info[4],
                    'hgvs_g': s.getHGVS_g(),
                    'hgvs_c': s.getHGVS_c(),#defaultTx['ac']),
                    'hgvs_p': s.getHGVS_p_1L(),#defaultTx['ac']),
                    'tx': defaultTx['ac']
                })
            obj['regions'] = regions.values()
            res.append(obj)

        for row in gene_alt_list_cdna:
            obj = {'uuid': row[0], 'name': row[1]}
            regions = {}
            gene_uuid = row[2]
            defaultTx_ac = row[5]
            defaultTx_uuid = row[6]
            for alt_info in row[4]:
                if alt_info[0] is None:
                    continue
                s = SequenceAlteration()
                s.byUuid(alt_info[4])
                region_uuid = alt_info[0]
                if region_uuid not in regions:
                    regions[region_uuid] = {
                        'uuid': region_uuid,
                        'gene_symbol': row[3],
                        'chrom': alt_info[1],
                        'start': alt_info[2],
                        'end': alt_info[3],
                        'alterations': []
                    }
                regions[region_uuid]['alterations'].append({
                    'uuid': alt_info[4],
                    'hgvs_g': s.getHGVS_g(),
                    'hgvs_c': s.getHGVS_c(),#defaultTx),
                    'hgvs_p': s.getHGVS_p_1L(),#defaultTx),
                    'tx': defaultTx['ac']
                })
            obj['regions'] = regions.values()
            res.append(obj)

        return Response(res, status=status.HTTP_200_OK)        
'''
@api_view(['GET'])
def alterationsInAmplicon(request):
    """
    Get alterations that fall within region amplified by amplicon
    """
    print "[annotationsAPI: alterationsInAmplicon]"
    if request.method == 'GET':
        if 'amplicon_uuid' in request.query_params:
            try:
                pcrProduct_uuid = json.loads(request.query_params['amplicon_uuid'])
            except:
                return Response("Incorrect call format", status=http_status.HTTP_400_BAD_REQUEST)
        else:
            return Response("Incorrect call format", status=http_status.HTTP_400_BAD_REQUEST)
        
        gu = GenomeGraphUtility()
        # get alterations for gDNA amplicons
        uuid_list_gdna = gu.getAlterationsIn_gDNAAmpliconList(pcrProduct_uuid)
        # get alterations for cDNA amplicons
        uuid_list_cdna = gu.getAlterationsIn_cDNAAmpliconList(pcrProduct_uuid)
        
        uuid_list = list(set(uuid_list_gdna + uuid_list_cdna))

        res = []
        r = SequenceAlteration.byUuid_list(uuid_list)
        for y in r:
            res.extend(y.getExtendedInfo())

        return Response(res, status=http_status.HTTP_200_OK)        


# GENERAL APIs
@api_view(['GET'])
def getAmpliconTech(request):
    print "[annotationsAPI: getAmpliconTech]"
    if request.method == 'GET':
        try:
            uuid = request.query_params['uuid']
        except Exception as e:
            return Response("Incorrect call format: {0}".format(str(e)), status=http_status.HTTP_400_BAD_REQUEST)
        g = GenomeGraphUtility()
        res = g.getPCRProductTechnologies(uuid)
        if len(res) > 0:
            res = [{'id': x.id, 'name': x.name, 'label': x.technologyLabel} for x in ExperimentType.objects.filter(technologyLabel__in=res[0][0])]
            return Response(res, status=http_status.HTTP_200_OK)
        else:
            return Response("Object not found", status=http_status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
def getRefsetParameters(request):
    """
    Describe the parameters of a given refset.

    Parameters:

    * *exp_type* : name of experiment type, string; mandatory

    * *labels* : a list of refset labels, belonging to the specified experiment type; optional

    Returns:

    * A list of refset labels that match the request, with their parameters and the corresponding values. If one or more labels have been provided through the *label* argument, then only those labels will be returned. Otherwise, all refset labels matching the specified experiment type will be returned.
    """
    print "[annotationsAPI: getRefsetParameters]"
    if request.method == 'GET':
        print request.query_params
        try:
            experiment_type = request.query_params['exp_type']
        except Exception as e:
            print "error1"
            return Response("Incorrect call format: {0}".format(str(e)), status=http_status.HTTP_400_BAD_REQUEST)
        
        label_list = json.loads(request.query_params.get('labels', "[]"))
        
        try:
            expType = ExperimentType.objects.get(name=experiment_type)
        except:
            print "error3"
            return Response("Unknown experiment type: {0}".format(experiment_type), status=http_status.HTTP_400_BAD_REQUEST)


        et_has_lt_list = expType.experimenttype_has_analysedlabelterm_set.all()
        if label_list:
            refsets = RefSet.objects.filter(fullLabel__in=label_list,expTypeHasLabelTerm__in=et_has_lt_list)
        else:
            refsets = RefSet.objects.filter(expTypeHasLabelTerm__in=et_has_lt_list)

        results = []
        for r in refsets:
            r_label = r.fullLabel
            r_parameters = json.loads(r.expQParamValues)
            r_labelTerm = r.expTypeHasLabelTerm.labelTerm.name
            results.append({'label': r_label, 'parameters': r_parameters, 'type': r_labelTerm})

        return Response(results, status=http_status.HTTP_200_OK)

@api_view(['GET'])
def getRefset(request):
    """
    Describe a given refset by returning the set of reference nodes, grouped by reftype label.

    Parameters:

    * *label* : a refset label; mandatory
    
    Returns:

    * The set of target nodes making up the refset, each with additional relevant information

    """
    print "[annotationsAPI: getRefset]"
    if request.method == 'GET':

        try:
            label = request.query_params['label']
        except Exception as e:
            print "error1"
            return Response("Incorrect call format: {0}".format(str(e)), status=http_status.HTTP_400_BAD_REQUEST)
        try:
            gq = RefSet.objects.get(fullLabel=label)
        except:
            return Response("Label not found", status=http_status.HTTP_400_BAD_REQUEST)

        results = gq.getReferenceNodes()
        return Response(results, status=http_status.HTTP_200_OK)

@api_view(['POST'])
@transaction.commit_on_success
def createRefset(request):
    """
    Create a new refset in annotation database. The API creates a new label to identify the set of reference nodes (either an existing or a new one)
    N.B. If a refset with the same experiment type and the same parameter values already exists, then the label of that refset is returned rather than creating a new one.

    Parameters:

    * *exp_type* : name of experiment type, string

    * *ref_type* : label identifying the type of phenomenon (e.g. sequence_alteration)

    * *params* : dictionary of parameters, used internally by the API when running the queries to obtain reference region nodes. Parameters must match those in the queries. Note that each parameter has a name that is unique within *all* queries associated with the given experiment type, so all parameters can be passed to this API as a single dictionary without causing any conflicts. The queries always return region nodes, corresponding to regions of interest (e.g. regions encompassing an alteration).
        
        [Optional] If the set of associated queries does not have any parameters, *params* can be omitted (however, an error will be raised if the set of queries has at least one parameter but none are provided to the API).

    Returns:

    * *label* : it defines the set of reference region nodes for the analysis

    """
    print "[annotationsAPI: createRefset]"
    if request.method == 'POST':
        print request.data
        try:
            experiment_type = request.data['exp_type']
            ref_type = request.data['ref_type']
            param_dict = request.data['params'] if 'params' in request.data else {}
        except Exception as e:
            print "error1"
            return Response("Incorrect call format: {0}".format(str(e)), status=http_status.HTTP_400_BAD_REQUEST)
        
        try:
            expType = ExperimentType.objects.get(name=experiment_type)
        except:
            print "error3"
            return Response("Unknown experiment type: {0}".format(experiment_type), status=http_status.HTTP_400_BAD_REQUEST)

        try:
            labelTerm = LabelTerm.objects.get(name=ref_type)
        except:
            print "error6"
            return Response("Unknown reference type: {0}".format(ref_type), status=http_status.HTTP_400_BAD_REQUEST)

        try:
            etHasLt = ExperimentType_has_AnalysedLabelTerm.objects.get(expType=expType, labelTerm=labelTerm)
        except:
            print "error7"
            return Response("Reference type {0} is currently not supported by technology {1}".format(labelTerm, expType), status=http_status.HTTP_400_BAD_REQUEST)

        try:
            querysets = RefSet.objects.filterByQueryParamValues(etHasLt, param_dict)
        except Exception as e:
            print "error4"
            return Response(str(e), status=http_status.HTTP_400_BAD_REQUEST)

        if len(querysets) > 0:
            print "using existing query set"
            qs = querysets[0]
        else:
            print "creating new query set"
            try:
                qs = RefSet.objects.createNew(etHasLt, param_dict)
                #qs.applyLabel(force=True)
            except Exception as e:
                print "error5"
                return Response(str(e), status=http_status.HTTP_400_BAD_REQUEST)
                    
        return Response({'refset_label': qs.fullLabel}, status=http_status.HTTP_200_OK)

@api_view(['POST'])
@transaction.commit_on_success
def createAnalysis(request):
    """
    Create analysis in annotation database. The API creates the analysis object and labels the set of reference nodes with an appropriate label, either an existing or a new one.

    Parameters:

    * *analysis_uuid* : uuid of analysis node, string

    * *analysis_name* : a name for the current analysis

    * *exp_type* : name of experiment type, string

    * *ref_type* : label of reference type (e.g. sequence_alteration)

    * *params* : dictionary of parameters, used internally by the API when running the queries to obtain reference region nodes. Parameters must match those in the queries. Note that each parameter has a name that is unique within *all* queries associated with the given experiment type, so all parameters can be passed to this API as a single dictionary without causing any conflicts. The queries always return region nodes, corresponding to regions of interest (e.g. regions encompassing an alteration).
        
        [Optional] If the set of associated queries does not have any parameters, *params* can be omitted (an error will be raised if the set of queries has at least one parameter but none is provided to the API).

    Returns:

    * *label* : it defines the set of reference region nodes for the analysis

    """
    print "[annotationsAPI: createAnalysis]"
    if request.method == 'POST':
        print request.data
        try:
            analysis_uuid = request.data['analysis_uuid']
            analysis_name = request.data['analysis_name']
            experiment_type = request.data['exp_type']
            ref_type = request.data['ref_type']
            param_dict = request.data['params'] if 'params' in request.data else {}
        except Exception as e:
            print "error1"
            return Response("Incorrect call format: {0}".format(str(e)), status=http_status.HTTP_400_BAD_REQUEST)
        
        gu = GenomeGraphUtility()
        # check if analysis node exists
        try:
            gu._getNodeByUUID("analysis", analysis_uuid)
        except Exception as e:
            print "error2"
            return Response(str(e), status=http_status.HTTP_400_BAD_REQUEST)
        # TODO: check if raw data node is linked to analysis node?

        try:
            expType = ExperimentType.objects.get(name=experiment_type)
        except:
            print "error3"
            return Response("Unknown experiment type: {0}".format(experiment_type), status=http_status.HTTP_400_BAD_REQUEST)

        try:
            labelTerm = LabelTerm.objects.get(name=ref_type)
        except:
            print "error5"
            return Response("Unknown reference type: {0}".format(ref_type), status=http_status.HTTP_400_BAD_REQUEST)

        try:
            etHasLt = ExperimentType_has_AnalysedLabelTerm.objects.get(expType=expType, labelTerm=labelTerm)
        except:
            print "error7"
            return Response("Reference type {0} is not supported by technology {1}".format(labelTerm, expType), status=http_status.HTTP_400_BAD_REQUEST)

        a = Analysis()
        a.graph_uuid = analysis_uuid
        a.name = analysis_name
        a.save()

        # assign query set to analysis (model method takes care of checking whether an existing label describes the same set of reference regions)
        try:
            a.assignQuerySet(etHasLt, param_dict)
            print "a.refSet:", a.refSet
            
        except Exception as e:
            print "error4"
            transaction.rollback()
            return Response(str(e), status=http_status.HTTP_400_BAD_REQUEST)
        
        # once reftype labels have been assigned, we can update the label
        #a.refSet.applyLabel()

        # update refset label and reftype labels on analysis node
        gu.setAnalysisRefsetLabel(analysis_uuid, a.refSet.fullLabel)
        gu.setAnalysisReftypeLabel(analysis_uuid, a.refSet.getReftypeLabel())

        return Response({'refset_label': a.refSet.fullLabel}, status=http_status.HTTP_200_OK)

@api_view(['POST'])
@transaction.commit_on_success
def deleteAnalysis(request):
    """
    Delete analysis in annotation database
    Parameters:

    * *analysis_uuid* : uuid of analysis node, string

    Returns:

    * boolean response

    """
    print "[annotationsAPI: deleteAnalysis]"
    if request.method == 'POST':
        print request.data
        try:
            analysis_uuid = request.data['analysis_uuid']
        except Exception as e:
            print "error1"
            return Response("Incorrect call format: {0}".format(str(e)), status=http_status.HTTP_400_BAD_REQUEST)
        
        try:
            a = Analysis.objects.get(graph_uuid=analysis_uuid)
            a.delete()
            return Response({'deleted': True}, status=http_status.HTTP_200_OK)
        except:
            return Response({'deleted': False}, status=http_status.HTTP_200_OK)

@api_view(['POST'])
@transaction.commit_on_success
def submitResults(request):
    '''
    Submit results related to an analysis.
    
    * *analysis_uuid* : uuid of analysis node, string

    * *raw_data_uuid* : uuid of raw data node, string

    * *annotations* : list of annotations, as tuples (sample_id, reference_id, **values)

    * *failed* : list of failed analysed points, as tuples (sample_id, region_uuid)
    '''
    print "[annotationsAPI: submitResults]"
    if request.method == 'POST':
        print "Annotations API: ", request.data
        try:
            analysis_uuid = request.data['analysis_uuid']
            raw_data_uuid = request.data['raw_data_uuid']
            annotations_list = request.data['annotations']
            ##failed_list = request.data['failed']
        except Exception as e:
            return Response("Incorrect call format: {0}".format(str(e)), status=http_status.HTTP_400_BAD_REQUEST)

        # record annotations in the appropriate relational table
        # N.B. this operation varies according to the type of analysed phenomenon
        # e.g. sequence alterations and copy number variations must be handled differently and stored in different tables
        # To do so, the LabelTerm model (i.e., the reftype label object) has been equipped with
        # a getAnnotationModel method, which returns the model manager of the appropriate model

        try:
            analysis = Analysis.objects.get(graph_uuid=analysis_uuid)
        except:
            return Response("Analysis with UUID={0} not found".format(analysis_uuid), status=http_status.HTTP_400_BAD_REQUEST)

        print "annotations_list", annotations_list
        for ann in annotations_list:
            label = ann['ref_type']
            try:
                labelTerm = LabelTerm.objects.get(name=label)
                annotationModel = labelTerm.getAnnotationModel()
            except Exception as e:
                print "error1"
                return Response(str(e), status=http_status.HTTP_400_BAD_REQUEST)
            if not annotationModel:
                return Response("Cannot handle annotation for label {0}".format(label), status=http_status.HTTP_400_BAD_REQUEST)
            try:
                created_annotations = []
                for annot in ann['annotations']:
                    a = annotationModel(id_sample=annot[0], id_experimental_data=raw_data_uuid, id_analysis=analysis)
                    a.setAnnotationContent(*annot) # sets model-specific information
                    created_annotations.append(a)
                annotationModel.objects.bulk_create(created_annotations)
                print "[annotationsAPI: submitResults] (%d) %s (type=%s): annotations saved ok" % (analysis.id, analysis.name, label)

                created_annotations = []
                for annot in ann['failed']:
                    a = annotationModel(id_sample=annot[0], id_experimental_data=raw_data_uuid, id_analysis=analysis)
                    a.setFailedContent(*annot) # sets model-specific information for failed data
                    created_annotations.append(a)
                annotationModel.objects.bulk_create(created_annotations)
                print "[annotationsAPI: submitResults] (%d) %s (type=%s): failed entries saved ok" % (analysis.id, analysis.name, label)

                print "[annotationsAPI: submitResults] (%d) %s (type=%s): running post-save handlers" % (analysis.id, analysis.name, label) # runs actions that must be performed after each analysis is saved (e.g. fingerprinting)
                annotationModel.objects.runPostSaveHandlers(analysis_obj=analysis)

            except Exception as e:
                transaction.rollback()
                print "error2"
                return Response(str(e), status=http_status.HTTP_400_BAD_REQUEST)

        return Response({"status": "ok"}, )

@api_view(['GET'])
def experimentTypeInfo(request):
    """
    Get experiment type info
    """
    print "[annotationsAPI: experimentTypeInfo]"
    if request.method == 'GET':
        if 'id' in request.query_params:
            params = {'id': request.query_params['id']}
        elif 'name' in request.query_params:
            params = {'name': request.query_params['name']}
        else:    
            return Response("Incorrect call format", status=http_status.HTTP_400_BAD_REQUEST)
        
        try:
            e = ExperimentType.objects.get(**params)
        except Exception as exc:
            print str(exc)
            return Response("Experiment was either not found or provided parameter was not unique", status=http_status.HTTP_400_BAD_REQUEST)

        labels = {}
        etHasLt = e.experimenttype_has_analysedlabelterm_set.all()
        refsets = []
        for x in etHasLt:
            labels[x.labelTerm.id] = x.labelTerm.displayName
            refsets.extend(x.refset_set.all())
        
        analyses = {x.id: x.name for x in Analysis.objects.filter(refSet__in=refsets)}
        
        data = {'labels': labels, 'analyses': analyses}
        resp = Response(data, status=http_status.HTTP_200_OK)
        resp['Access-Control-Allow-Headers'] = 'origin, content-type, accept'
        return resp

@api_view(['GET'])
def allLabelTerms(request):
    """
    Get all labelTerms
    """
    print "[annotationsAPI: allLabelTerms]"
    if request.method == 'GET':
        labels = {x.id : x.displayName for x in LabelTerm.objects.filter(fatherLabel=None).order_by('id')}
        resp = Response(labels, status=http_status.HTTP_200_OK)
        resp['Access-Control-Allow-Headers'] = 'origin, content-type, accept'
        return resp

@api_view(['GET'])
def genesInRegion(request):
    """
    Get all genes in region
    """
    print "[annotationsAPI: genesInRegion]"
    if request.method == 'GET':
        print request.query_params
        try:
            chrom = request.query_params['chrom']
            start = int(request.query_params['start'])
            end = int(request.query_params['end'])
        except:
            return Response("Incorrect call format", status=http_status.HTTP_400_BAD_REQUEST)
        gu = GenomeGraphUtility()
        genes = gu.getGenesInRegion(chrom, start, end)
        genes = [{'id': x[0], 'symbol': x[1], 'ac': x[2], 'chrom': x[3]} for x in genes]
        resp = Response(genes, status=http_status.HTTP_200_OK)
        resp['Access-Control-Allow-Headers'] = 'origin, content-type, accept'
        return resp

@api_view(['GET'])
def transcriptsForGene(request):
    """
    Get all transcripts for a given gene
    """
    print "[annotationsAPI: transcriptsForGene]"
    if request.method == 'GET':
        print request.query_params
        try:
            gene_uuid = request.query_params['gene_uuid']
        except:
            return Response("Incorrect call format", status=http_status.HTTP_400_BAD_REQUEST)
        gu = GenomeGraphUtility()
        transcripts = gu.getTranscriptsForGene(gene_uuid)
        transcripts = [{'id': x[0], 'ac': x[1], 'num_exons': x[2], 'is_refseq': x[3]} for x in transcripts]
        resp = Response(transcripts, status=http_status.HTTP_200_OK)
        resp['Access-Control-Allow-Headers'] = 'origin, content-type, accept'
        return resp

@api_view(['GET'])
def predefinedGenomicLists(request):
    """
    Get all predefined genomic target lists
    """
    print "[annotationsAPI: predefinedGenomicLists]"
    if request.method == 'GET':
        try:
            print request.user
        except:
            print "Cannot detect user"
            return Response("Not logged in", status=http_status.HTTP_403_FORBIDDEN)
        lists = [{'id': x.id, 'name': x.name, 'data': json.loads(x.data)} for x in PredefinedGenomicTargetList.objects.filter(user=request.user)]
        resp = Response(lists, status=http_status.HTTP_200_OK)
        resp['Access-Control-Allow-Headers'] = 'origin, content-type, accept'
        return resp

@api_view(['POST'])
def newPredefinedGenomicList(request):
    """
    Create new predefined genomic target list. Receives:

    * *name* of the list
    * the *uuid lists*
    
    Returns:

    The ID of the list if the creation was successful, -1 if a list with the same name already exists, -2 and the exception text for other types of errors.

    """
    print "[annotationsAPI: newPredefinedGenomicList]"
    if request.method == 'POST':
        print request.data
        try:
            print request.user
        except:
            print "not logged in"
            return Response("Not logged in", status=http_status.HTTP_403_FORBIDDEN)
        
        try:
            name = request.data['name']
            uuid_list = json.loads(request.data['uuid_list'])
        except Exception as e:
            print "error1"
            return Response("Incorrect call format: {0}".format(str(e)), status=http_status.HTTP_400_BAD_REQUEST)
        try:
            PredefinedGenomicTargetList.objects.get(user=request.user,name=name)
            print "error2"
            return Response({'status': -1, 'description': 'Duplicate entry'}, status=http_status.HTTP_500_INTERNAL_SERVER_ERROR)
        except:
            pass
        
        try:
            g = GenomeGraphUtility()
            info = g.getGeneInfo_byUuid(uuid_list)
            l = PredefinedGenomicTargetList()
            l.name = name
            l.data = json.dumps([{'id': x[0], 'symbol': x[1], 'chrom': x[3]} for x in info])
            l.user = request.user
            l.save()
            return Response(l.id, status=http_status.HTTP_200_OK)
        except Exception as e:
            print "error3"
            return Response({'status': -2, 'description': str(e)}, status=http_status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def deletePredefinedGenomicList(request):
    """
    Delete existing predefined genomic target list. The list will only be deleted if it belongs to the current user. Receives:

    * the *id* of the list
    
    Returns:

    Nothing

    """
    print "[annotationsAPI: deletePredefinedGenomicList]"
    if request.method == 'POST':
        print request.data
        try:
            print request.user
        except:
            print "not logged in"
            return Response("Not logged in", status=http_status.HTTP_403_FORBIDDEN)
        
        try:
            l_id = request.data['id']
        except Exception as e:
            print "error1"
            return Response("Incorrect call format: {0}".format(str(e)), status=http_status.HTTP_400_BAD_REQUEST)
        try:
            l = PredefinedGenomicTargetList.objects.get(pk=l_id,user=request.user)
            l.delete()
            return Response({'status': 0, 'description': 'OK'})
        except:
            return Response({'status': -1, 'description': str(e)}, status=http_status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def searchReferences(request):
    """
    Get references that match search criteria
    """
    print "[annotationsAPI: searchReferences]"
    max_results = 250
    if request.method == 'GET':
        if 'annot_type' not in request.query_params:
            return Response("Incorrect call format", status=http_status.HTTP_400_BAD_REQUEST)
        annot_type = request.query_params['annot_type']
        try:
            annot_labelTerm = LabelTerm.objects.get(fatherLabel=None,name=annot_type)
        except:
            return Response("Unsupported annotation type", status=http_status.HTTP_400_BAD_REQUEST)
        try:
            graph_model = annot_labelTerm.getGraphModel()
        except:
            return Response("An error occurred", status=http_status.HTTP_500_INTERNAL_SERVER_ERROR)

        params = ['chrom', 'start', 'end', 'gene_uuid', 'tx_uuid']
        args = {k: request.query_params[k] for k in params if k in request.query_params and request.query_params[k] not in (None, '')}
        print "[annotationsAPI: searchReferences] args = ", args
        res = [x.getInfo() for x in graph_model.filter(**args)]
        return Response(res, status=http_status.HTTP_200_OK)        

@api_view(['POST'])
def deleteReferences(request):
    """
    Delete references whose UUIDs has been provided as a parameter
    """
    print "[annotationsAPI: deleteReferences]"
    if request.method == 'POST':
        print request.data
        try:
            uuid_list = json.loads(request.data['uuid_list'])
        except:
            return Response("Missing parameter 'uuid_list'", status=http_status.HTTP_400_BAD_REQUEST)
        errors = []
        b = AnnotationUpdateBatch(dateStart=timezone.now(),status=AnnotationUpdateBatch.RUNNING)
        b.save()
        for u in uuid_list:
            obj = KBReference.byUuid(u)
            print "Delete", obj.getInfo()
            model = obj.getAnnotationModel()
            try:
                # look for stale entries i.e. entries for this reference whose update didn't suceed (e.g. we're deleting a reference because annotation won't go through)
                to_delete = KBReferenceHistory.objects.filter(uuid=u,annotationUpdateBatch=None)
                for x in to_delete:
                    x.delete()
                model.objects.autoAnnotate(refObj=obj, willExist=False)
                k = KBReferenceHistory(uuid=obj.getUUID(),data=json.dumps(obj.getInfo()),labelTerm=LabelTerm.objects.get(name=obj.getGraphLabel()),action=KBReferenceHistory.DELETE,annotationUpdateBatch=b)
            except:
                k = KBReferenceHistory(uuid=obj.getUUID(),data=json.dumps(obj.getInfo()),labelTerm=LabelTerm.objects.get(name=obj.getGraphLabel()),action=KBReferenceHistory.DELETE)
            k.save()
            try:
                obj.delete()
            except Exception, e:
                info = obj.getInfo()
                info['error'] = str(e)
                errors.append(info)

        b.status = AnnotationUpdateBatch.COMPLETED
        b.dateEnd = timezone.now()
        b.save()

        if len(errors) == 0:
            return Response("Ok", status=http_status.HTTP_200_OK)
        else:
            return Response(errors, status=http_status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def checkAnnotUpdateStatus(request):
    """
    Check if there are any pending references in KBReferenceHistory, and if any partial or full updates are currently running
    """
    print "[annotationsAPI: checkAnnotUpdateStatus]"
    if request.method == 'GET':
        pendingRefs = KBReferenceHistory.objects.pendingReferences()
        runningPartial = AnnotationUpdateBatch.objects.filter(status=AnnotationUpdateBatch.RUNNING,updateType=AnnotationUpdateBatch.PARTIAL).count() > 0
        runningFull = AnnotationUpdateBatch.objects.filter(status=AnnotationUpdateBatch.RUNNING,updateType=AnnotationUpdateBatch.FULL).count() > 0
        return Response({'pendingRefs': pendingRefs, 'runningPartial': runningPartial, 'runningFull': runningFull}, status=http_status.HTTP_200_OK)

@api_view(['POST'])
def updateAnnotations(request):
    """
    Update annotations with pending references found in KBReferenceHistory
    """
    print "[annotationsAPI: updateAnnotations]"
    if request.method == 'POST':
        try:
            updateType = request.data['type']
        except:
            return Response("Missing parameter 'type'.", status=http_status.HTTP_400_BAD_REQUEST)

        # prevent a new update from running if another one is already running, whether partial or full
        cnt = AnnotationUpdateBatch.objects.filter(status=AnnotationUpdateBatch.RUNNING).count()
        if cnt > 0:
            return Response("Another update is currently running, please try again later.", status=http_status.HTTP_500_INTERNAL_SERVER_ERROR)

        if updateType == 'part':
            # also run any pending partial update
            backlog = list(AnnotationUpdateBatch.objects.filter(status=AnnotationUpdateBatch.WAITING,updateType=AnnotationUpdateBatch.PARTIAL))
            # create a new batch for pending references
            batch = KBReferenceHistory.objects.createBatchForPendingReferences()
            if batch is not None:
                print "[annotationsAPI: updateAnnotations] New pending reference batch"
                backlog.append(batch)

        elif updateType == 'full':
            # create a new FULL batch for pending references (also includes all pending references from pending partial updates)
            batch = KBReferenceHistory.objects.createBatchForPendingReferences(updateType=AnnotationUpdateBatch.FULL)
            backlog = [batch]
        else:
            return Response("Invalid value for parameter 'type'.", status=http_status.HTTP_400_BAD_REQUEST)

        req = tasks.runUpdateAnnotations.delay(backlog)
        return Response("Ok", status=http_status.HTTP_200_OK)
