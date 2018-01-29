# Create your views here.

from django.shortcuts import render_to_response
from django.core.urlresolvers import reverse
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseServerError, HttpResponseRedirect
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.servers.basehttp import FileWrapper
from LASAuth.decorators import laslogin_required

from annotations.models import *
import annotations.tasks as tasks
from annotations.lib.utils import *
from annotations.lib.graph_utils import *
from annotations.lib.genomic_models import *
from annotations.lib.SequenceAligner import *
from annotations.lib.query_utils import *
from annotations.lib.report_utils import *

from subprocess import call
import tempfile
import os
import json
import ast
import urlparse
import mimetypes
import datetime
mimetypes.init()

#to redirect user to home page
@laslogin_required
@login_required
def start_redirect(request):
    return HttpResponseRedirect(reverse("annotations.views.home"))

#######################################
# home view
#######################################

@laslogin_required
@login_required
def home(request):
    print 'home'
    return render_to_response('home.html', RequestContext(request))

#######################################
#logout view
#######################################

@laslogin_required
@login_required
def logout_view(request):
    print "LOGOUT REDIRECT TO:", settings.LAS_AUTH_SERVER_URL
    return HttpResponseRedirect(settings.LAS_AUTH_SERVER_URL)

#######################################
#Insert new AnnotationFeature value
#######################################

@laslogin_required
@login_required
def new_annotation_feature_value(request):
    return render_to_response('new_annotation_feature_value.html', {'annotationFeatures': AnnotationFeature.objects.all(), 'annotationSubtypes': AnnotationFeature_Subtype.objects.all()}, RequestContext(request))


def getSAResults(request):
    return HttpResponse("")


#######################################
#Create Target Sequence view
#######################################

@laslogin_required
@login_required
def create_targetseq(request):
    ref_remap = {'genome': 'genome', 'transcriptome': 'transcript'}
    if request.method == 'GET':
        print request.GET

        dic = {}
        if 'ref' in request.GET and request.GET['ref'] == 'newsp':
            dic['ref'] = 'newsp'

        # request to perform sequence alignment
        if 'tsname' in request.GET and 'sequence' in request.GET and 'profile' in request.GET:
            name = request.GET['tsname']
            sequence = request.GET['sequence']

            try:
                TargetSequence.objects.get(name=name)
                return HttpResponseServerError("Name is already in use, please choose a different one")
            except:
                pass

            s = SequenceAligner()
            try:
                al_genome = s.align(sequence, "genome")
            except Exception as e:
                return HttpResponseServerError("An error occurred while trying to run external aligner on genome:\n" + e.output)
            try:
                al_transcriptome = s.align(sequence, "transcriptome")
            except Exception as e:
                return HttpResponseServerError("An error occurred while trying to run external aligner on transcriptome:\n" + e.output)
    
            request.session['alignments'] = al_genome + al_transcriptome
            request.session['tsname'] = name
            request.session['sequence'] = sequence

            #dic['alignments'] = al
            #dic['tsname'] = name
            #dic['sequence'] = sequence

            alignments = []
            
            ggu = GenomeGraphUtility()
            
            for x in al_genome:
                try:
                    gene_symbol = ggu.getGenomicLocationAnnotation(x.reference, int(x.start))[0]['gene.symbol']
                except:
                    gene_symbol = ""
                alignments.append((ref_remap[x.alignerProfile], x.reference, x.start, x.end, x.strand, gene_symbol, None))

            for x in al_transcriptome:
                try:
                    tx_info = ggu.getTranscriptInfo(ac=x.reference)[0]
                    gene_symbol = tx_info['gene.symbol']
                    tx_is_default = tx_info['tx.is_default']
                except:
                    gene_symbol = ""
                    tx_is_default = False
                alignments.append((ref_remap[x.alignerProfile], x.reference, x.start, x.end, x.strand, gene_symbol, tx_is_default))

            return HttpResponse(json.dumps(alignments))#render_to_response("primers.html", dic, RequestContext(request))

        else:
            scope = {}
            if 'biobank' in request.GET and request.GET['biobank'] == 'yes':
                print "redirect to biobank"
                scope['redirectToBiobank'] = True
                try:
                    base_url = WebService.objects.get(name="BioBank").urls_set.filter(available=True)[0].url
                    scope['biobankUrl'] = urlparse.urljoin(base_url, "label/newProbe/") # ?name=...&uuid=...
                except:
                    scope['biobankUrl'] = None
            else:
                scope['redirectToBiobank'] = False

            if 'just_saved' in request.session:
                dic['just_saved'] = request.session['just_saved']
                del request.session['just_saved']

            experimentType = ExperimentType.objects.filter(hasTargetSequence=True).order_by('name')
            scope['technologies'] = experimentType
            print "scope:", scope
            return render_to_response("primers.html", scope, RequestContext(request))

    elif request.method == 'POST':
        print "ricevuta POST:", request.POST
        #try:
        if 'alignments' in request.POST:
            sel_alignments = request.POST.getlist('alignments')
            alignments = request.session['alignments']

            name = request.session['tsname']
            sequence = request.session['sequence']

            ts = TargetSequence()
            ts.name = name
            ts.sequence = sequence
            
            p = Primer(name=name,length=len(sequence))

            for x in sel_alignments:
                al = alignments[int(x)]
                p.addAlignment(al.reference, al.start, al.end, al.strand, al.alignerProfile)

            p.save()
            ts.uuid = p.uuid
            ts.save()

            tech = [int(x.split('_')[1]) for x in request.POST.keys() if x.startswith('tech_')]
            labelsYes = [x.technologyLabel for x in ExperimentType.objects.filter(id__in=tech)]
            labelsNo = [x.technologyLabel for x in ExperimentType.objects.exclude(id__in=tech).exclude(technologyLabel=None)]
            print labelsYes, labelsNo
            p.setTechnologies(labelsYes, labelsNo)

            del request.session['alignments']
            del request.session['tsname']
            del request.session['sequence']

            if "ref" not in request.POST or request.POST['ref'] != 'newsp':
                request.session['just_saved'] = 'Target sequence saved'
            return HttpResponse(json.dumps((ts.id, ts.name, ts.uuid)))
        
        elif 'seqfile' in request.FILES:
        
            f = request.FILES['seqfile']
            sequences = []
            for line in f:
                try:
                    name, sequence = line.split('\t')
                    name = name.strip()
                    sequence = sequence.strip()
                    if len(name) == 0 or len(sequence) == 0:
                        continue
                except:
                    continue
                sequences.append({'name': name, 'seq': sequence})

            s = SequenceAligner()
            ggu = GenomeGraphUtility()

            not_found = []
            sequence_alignments = []
            for sequence in sequences:
                al_genome = s.align(sequence['seq'], "genome")
                al_transcriptome = s.align(sequence['seq'], "transcriptome")
                alignments = al_genome + al_transcriptome

                ts = TargetSequence()
                ts.name = sequence['name']
                ts.sequence = sequence['seq']
                print "Processing primer: ", ts.name

                thisSeq = {'name': sequence['name'], 'seq': sequence['seq'], 'alignments': []}

                p = Primer(name=sequence['name'],length=len(sequence['seq']))
                for al in alignments:
                    p.addAlignment(al.reference, al.start, al.end, al.strand, al.alignerProfile)
                    if al.alignerProfile == "genome":
                        try:
                            gene_symbol = ggu.getGenomicLocationAnnotation(al.reference, int(al.start))[0]['gene.symbol']
                        except Exception, e:
                            print str(e)
                            gene_symbol = ""
                    elif al.alignerProfile == "transcriptome":
                        try:
                            gene_symbol = ggu.getTranscriptInfo(ac=al.reference)[0]['gene.symbol']
                        except Exception, e:
                            print str(e)
                            gene_symbol = ""
                    else:
                        gene_symbol = ""
                    
                    print "gene_symbol", gene_symbol
                    thisSeq['alignments'].append({'type': ref_remap[al.alignerProfile], 'reference': al.reference, 'start': al.start, 'end': al.end, 'strand': al.strand, 'gene_symbol': gene_symbol})
                    #
                    #for y in x[2]:
                    #   tsa = TargetSequenceAlignment()
                    #   tsa.chromosome = Chromosome.objects.get(name=y.tx)
                    #   tsa.strand = y.strand
                    #   tsa.alignStart = y.start
                    #   tsa.alignEnd = y.end
                    #   tsa.targetSequence = ts
                    #   tsa.gene = getGene(y.tx, y.start, y.end)[0]
                    #   tsa.save()
                if len(alignments) == 0:
                    not_found.append(sequence)

                p.save()
                ts.uuid = p.uuid
                ts.save()
                sequence_alignments.append(thisSeq)

            num_total = len(sequences)
            num_found = num_total - len(not_found)
            
            request.session['alignmentsDone'] = {'sequence_alignments': sequence_alignments, 'num_found': num_found, 'num_total': num_total, 'not_found': not_found}
            return HttpResponseRedirect(reverse(annotations.views.displayAlignReport))
        
        #except Exception,e:
        #   return HttpResponse(str(e))
        
        else:
            return HttpResponseServerError("Invalid request")

@laslogin_required
@login_required
def displayAlignReport(request):
    try:
        alignmentsDone = request.session['alignmentsDone']
        return render_to_response("alignReport.html", {'num_found': alignmentsDone['num_found'], 'num_total': alignmentsDone['num_total'], 'not_found': alignmentsDone['not_found'], 'alignments': alignmentsDone['sequence_alignments']}, RequestContext(request))
    except Exception as e:
        print e
        return HttpResponseRedirect(reverse(annotations.views.home))


#######################################
#Create Sequence Pair view
#######################################

@laslogin_required
@login_required
def create_seqpair(request):
    experimentType = ExperimentType.objects.filter(hasTargetSequence=True).order_by('name')
    gu = GenomeGraphUtility()
    chrom = gu.getAllChromosomes()
    w = WebService.objects.get(name="Annotations Manager")
    try:
        u = w.urls_set.filter(available=True)[0].url
    except:
        u = ""
    scope = {}
    scope['technologies'] = experimentType
    scope['chrom'] = chrom
    scope['assembly'] = [('hg19', 'GRCh37/hg19', False), ('hg38', 'GRCh38/hg38', True)]
    scope['annotations_url'] = u
    scope['primers'] = TargetSequence.objects.all()

    if request.method == 'GET':
        
        if 'act' in request.GET:

            act = request.GET['act']

            # WARNING: this is obsolete!
            # target sequence search is now handled by the client
            # via the DataTable search field
            # so this server-side search is no longer used
            # search target sequences
            if act == 'searchts':
                try:
                    tsname = request.GET['tsname']
                    gsymbol = request.GET['gsymbol']
                except:
                    return render_to_response("seqpairs.html", RequestContext(request)) 

                if gsymbol:
                    g = GenesFromSymbol(geneSymbol=gsymbol, exactMatch=False)
                    ts_list = TargetSequenceAlignment.objects.values_list('targetSequence', flat=True).filter(gene__in=g).only('targetSequence')
                    ts = TargetSequence.objects.filter(name__icontains=tsname, id__in=ts_list)
                else:
                    ts = TargetSequence.objects.filter(name__icontains=tsname)
                
                primers = []
                for x in ts:
                    primers.append((x.id, x.name, x.sequence))

                return HttpResponse(json.dumps(primers))
            ### end obsolete

            # compute sequence combinations
            elif act == 'seqcombo':
                
                try:
                    ts1_id = request.GET['ts1_id']
                    ts2_id = request.GET['ts2_id']
                except:
                    return render_to_response("seqpairs.html", RequestContext(request))

                ts1 = TargetSequence.objects.get(pk=ts1_id)
                ts2 = TargetSequence.objects.get(pk=ts2_id)
                p1 = Primer()
                p2 = Primer()
                p1.byUuid(ts1.uuid)
                p2.byUuid(ts2.uuid)
                ts1_align = p1.getAlignments()
                ts2_align = p2.getAlignments()

                combos = []
                computed_combos = {}
                names = []

                for x in ts1_align:

                    for y in ts2_align:

                        if x['type'] != y['type'] or (x['type'] == 'transcriptome' and y['type'] == 'transcriptome' and x['reference'] != y['reference']):
                            continue
                        
                        if x['strand'] == '+' and y['strand'] == '-':

                            gnx = x['gene_symbol'] if x['gene_symbol'] else 'n/a'
                            gny = y['gene_symbol'] if y['gene_symbol'] else 'n/a'
                            
                            lblx = x['gene_symbol'] if x['gene_symbol'] else x['reference']
                            lbly = y['gene_symbol'] if y['gene_symbol'] else y['reference']
                            
                            if lblx == lbly:
                                name = lblx + '_' + ts1.name + '|' + ts2.name
                            else:
                                name = lblx + '_' + ts1.name + '|' + lbly + '_' + ts2.name
                            i = 1
                            while name in names:
                                name = name + '__' + str(i)
                                i += 1
                            names.append(name)

                            length = str(max(x['end'], y['end']) - min(x['start'], y['start']))  if x['reference'] == y['reference'] else '??'
                            combos.append((ts1.uuid, x['uuid'], ts2.uuid, y['uuid'], x['type'], ts1.name, ('chr' if x['type'] == 'genome' else '') + x['reference'], x['start'], x['end'], gnx, ts2.name, ('chr' if y['type'] == 'genome' else '') + y['reference'], y['start'], y['end'], gny, length, name))
                            computed_combos[(ts1.uuid, x['uuid'], ts2.uuid, y['uuid'])] = ('auto', x['type'])

                        elif x['strand'] == '-' and y['strand'] == '+':

                            gnx = x['gene_symbol'] if x['gene_symbol'] else 'n/a'
                            gny = y['gene_symbol'] if y['gene_symbol'] else 'n/a'
                            
                            lblx = x['gene_symbol'] if x['gene_symbol'] else x['reference']
                            lbly = y['gene_symbol'] if y['gene_symbol'] else y['reference']
                            
                            if lbly == lblx:
                                name = lbly + '_' + ts2.name + '|' + ts1.name
                            else:
                                name = lbly + '_' + ts2.name + '|' + lblx + '_' + ts1.name
                            i = 1
                            while name in names:
                                name = name + '__' + str(i)
                                i += 1
                            names.append(name)
                                
                            length = str(max(x['end'], y['end']) - min(x['start'], y['start'])) if x['reference'] == y['reference'] else '??'
                            combos.append((ts2.uuid, y['uuid'], ts1.uuid, x['uuid'], x['type'], ts2.name, ('chr' if y['type'] == 'genome' else '') + y['reference'], y['start'], y['end'], gny, ts1.name, ('chr' if x['type'] == 'genome' else '') + x['reference'], x['start'], x['end'], gnx, length, name))
                            computed_combos[(ts2.uuid, y['uuid'], ts1.uuid, x['uuid'])] = ('auto', x['type'])

                if 'combos' in request.session:
                    computed_combos.update(request.session['combos'])
                request.session['combos'] = computed_combos
                return HttpResponse(json.dumps(combos))

            # get alignments for manual definition of sequence combo
            elif act == 'getalign':

                try:
                    ts_id = request.GET['ts_id']
                except:
                    return render_to_response("seqpairs.html", RequestContext(request))

                ts = TargetSequence.objects.get(pk=ts_id)
                p = Primer()
                p.byUuid(ts.uuid)
                ts_align = p.getAlignments()

                aligns = []

                for x in ts_align:
                    aligns.append((x['uuid'], x['type'], ('chr' if x['type'] == 'genome' else '') + x['reference'], x['start'], x['end'], x['strand'], x['gene_symbol'] if x['gene_symbol'] else 'n/a'))

                return HttpResponse(json.dumps(aligns))

            elif act == 'newcombo':

                try:
                    al1_id = request.GET['al1_id']
                    al2_id = request.GET['al2_id']
                except:
                    return render_to_response("seqpairs.html", RequestContext(request))

                p1 = Primer()
                p2 = Primer()
                p1.byAlignmentUuid(al1_id)
                p2.byAlignmentUuid(al2_id)
                al1 = p1.getAlignments()[0]
                al2 = p2.getAlignments()[0]


                gn1 = al1['gene_symbol'] if al1['gene_symbol'] else 'n/a'
                gn2 = al2['gene_symbol'] if al2['gene_symbol'] else 'n/a'
                
                lbl1 = al1['gene_symbol'] if al1['gene_symbol'] else al1['reference']
                lbl2 = al2['gene_symbol'] if al2['gene_symbol'] else al2['reference']
                
                if lbl1 == lbl2:
                    name = lbl1 + '_' + p1.name + '|' + p2.name
                else:
                    name = lbl1 + '_' + p1.name + '|' + lbl2 + '_' + p2.name

                length = str(max(al1['end'], al2['end']) - min(al1['start'], al2['start']))  if al1['reference'] == al2['reference'] else '??'

                #(ts1.uuid, x['uuid'], ts2.uuid, y['uuid'], x['type'], ts1.name, ('chr' if x['type'] == 'genome' else '') + x['reference'], x['start'], x['end'], gnx, ts2.name, ('chr' if y['type'] == 'genome' else '') + y['reference'], y['start'], y['end'], gny, length, name)
                newcombo = (p1.uuid, al1['uuid'], p2.uuid, al2['uuid'], al1['type'], p1.name, ('chr' if al1['type'] == 'genome' else '') + al1['reference'], al1['start'], al1['end'], gn1, p2.name, ('chr' if al2['type'] == 'genome' else '') + al2['reference'], al2['start'], al2['end'], gn2, length, name)

                computed_combos = {(p1.uuid, al1['uuid'], p2.uuid, al2['uuid']): ('manual', al1['type'] if al1['type'] == al2['type'] else 'other')}
                if 'combos' in request.session:
                    computed_combos.update(request.session['combos'])
                request.session['combos'] = computed_combos

                return HttpResponse(json.dumps(newcombo))

            else:
                return render_to_response("seqpairs.html", RequestContext(request)) 
        else:
            return render_to_response("seqpairs.html", scope, RequestContext(request))

    elif request.method == 'POST':
        print request.POST
        coord_params = ['tsname1', 'tsgene', 'tsasbl', 'tschrom', 'tsstart', 'tsend', 'tslength', 'tsexclintr', 'txid']
        if 'combos-list' in request.POST:
            try:
                # get selected combinations from query dict
                combos = json.loads(request.POST['combos-list'])
            except:
                return HttpResponseRedirect(reverse("annotations.views.create_seqpair"))

            # for each combination:
            #   check if it's in the session
            #   if so, check if name and length are in query dict
            #   if so, go ahead and save it

            computed_combos = request.session['combos']
            for x in combos:
                if (x['pr1'], x['al1'], x['pr2'], x['al2']) not in computed_combos:
                    err = "Invalid sequence combo"
                    break
                else:
                    def_mode, align_type = computed_combos[(x['pr1'], x['al1'], x['pr2'], x['al2'])]
                    if def_mode == 'manual':
                        #### TbD!!!!!!!: logic to define PCR_product region when manual amplicon definition
                        pass
                    elif def_mode == 'auto':
                        pcr = PCRProduct()
                        pcr.name = x['name']
                        pcr.length = x['length']
                        pcr.primer1_uuid = x['pr1']
                        pcr.reg1_uuid = x['al1']
                        pcr.primer2_uuid = x['pr2']
                        pcr.reg2_uuid = x['al2']
                        pcr.alignmentType = align_type
                        pcr.createSimpleProduct()
                        pcr.save()

                        tsac = TSACombination()
                        tsac.name = x['name']
                        tsac.length = x['length']
                        tsac.uuid = pcr.uuid
                        tsac.save()

                        err = "Sequence pair(s) saved"

            del request.session['combos']
            
            return HttpResponseRedirect(reverse("annotations.views.create_seqpair"))

        elif len([x for x in coord_params if x in request.POST]) == len(coord_params):
            # create seqpair by coordinates
            print "create seqpair from coordinates"
            
            # retrieve all parameters
            name = request.POST['tsname1']
            geneuuid = request.POST['tsgene']
            assembly = request.POST['tsasbl']
            chrom = request.POST['tschrom']
            start = int(request.POST['tsstart'])
            end = int(request.POST['tsend'])
            length = int(request.POST['tslength'])
            exclude_intron = request.POST['tsexclintr']
            tx_id = request.POST['txid']
            
            gu = GenomeGraphUtility()
            # check if name is available, else -> error
            try:
                TSACombination.objects.get(name=name)
                return HttpResponseServerError("Name is already in use, please choose a different one")
            except:
                pass
            
            # if Hg38, convert to Hg19 (conversion implicitly checks coordinates: if coordinates are invalid, conversion fails)
            if assembly == 'hg38':
                try:
                    print "trying to map to hg38:", chrom, start, end
                    l = LiftOver('hg38ToHg19')
                    hg19 = l.convert(chrom, start, end)
                except Exception as e:
                    print "Exception:", str(e)
                    return HttpResponseServerError("Could not convert the specified coordinates from Hg38 to Hg19, please check and retry")
                start = hg19['start']
                end = hg19['end']
            # if Hg19, just check coordinates
            elif assembly == 'hg19':
                allchroms = gu.getAllChromosomes()
                chrominfo = filter(lambda x:x[1] == chrom, allchroms)[0]
                if start >= end or start < chrominfo[2] or start > chrominfo[3] or end < chrominfo[2] or end > chrominfo[3]:
                    return HttpResponseServerError("Invalid coordinates for assembly Hg19, please check and retry")
            # if other assembly, raise error
            else:
                return HttpResponseServerError("Invalid assembly")

            # create seqpair
            pcr = PCRProduct()
            pcr.name = name
            pcr.length = length
            pcr.primers_unknown = True
        
            if exclude_intron != "include":
                # introns must be excluded

                if exclude_intron == "excludeauto":
                    # automatically pick a transcript

                    # get default tx, if any
                    default_tx = gu.getDefaultTranscriptForGene(gene_uuid=geneuuid)
                    all_tx = []
                    if default_tx is not None:
                        all_tx.append(default_tx['ac'])
                    # enqueue all other txs
                    # sort them as follows: RefSeq txs come first, then sort by decreasing no. of exons
                    # RefSeq == True  => -1
                    # RefSeq == False => +1
                    all_tx.extend (map(lambda t: t[1], sorted ( filter(lambda t: t[1] != default_tx, gu.getTranscriptsForGene(geneuuid)), cmp=lambda a, b: 1-2*int(a[3]) if a[3] != b[3] else b[2]-a[2]) ))
                    selected_tx = None
                    for t in all_tx:
                        tx_info = gu.getTranscriptInfo(ac=t)[0]
                        if gu.transcriptContainsCoordinate(chrom=chrom, pos=start, tx_info=tx_info) and gu.transcriptContainsCoordinate(chrom=chrom, pos=end, tx_info=tx_info):
                            selected_tx = t
                            break
                    if selected_tx is None:
                        return HttpResponseServerError("No appropriate transcript was found")
                
                elif exclude_intron == "excludeenst":
                    try:
                        tx_info = gu.getTranscriptInfo(uuid=tx_id)[0]
                        selected_tx = tx_info['tx.ac']
                    except:
                        return HttpResponseServerError("Transcript not found")

                    if tx_info['gene.uuid'] != geneuuid:
                        return HttpResponseServerError("Selected transcript and gene do not match")

                elif exclude_intron == "excluderefseq":
                    try:
                        remap = EnsemblTranscriptXref.objects.get(pk=tx_id)
                        selected_tx = remap.ensembl_id.split('.')[0]
                        tx_info = gu.getTranscriptInfo(ac=selected_tx)[0]
                    except:
                        return HttpResponseServerError("Transcript not found")

                    if tx_info['gene.uuid'] != geneuuid:
                        return HttpResponseServerError("Selected transcript and gene do not match")

                else:
                    return HttpResponseServerError("An error has occurred: invalid option")
                    
                strand = tx_info['strand']
                try:
                    start_tx = gu.mapGenomicCoordinateToTranscript(chrom=chrom, pos=start, tx_info=tx_info)
                    end_tx = gu.mapGenomicCoordinateToTranscript(chrom=chrom, pos=end, tx_info=tx_info)
                except:
                    return HttpResponseServerError("Cannot map specified coordinates to the selected transcript")
                if strand == '-':
                    start_tx, end_tx = end_tx, start_tx
                print start_tx, end_tx
                
                pcr.alignmentType = "transcriptome"
                pcr.ampl_reg_ref = selected_tx
                pcr.ampl_reg_start = start_tx['pos']
                pcr.ampl_reg_end = end_tx['pos']
                pcr.createSimpleProduct()
                pcr.save()

                tsa = TSACombination()
                tsa.uuid = pcr.uuid
                tsa.name = name
                tsa.length = length
                tsa.save()

            else:
                try:
                    gene_info = gu.getGeneInfo(uuid=geneuuid)[0]
                except:
                    return HttpResponseServerError("Gene not found")

                pcr.alignmentType = "genome"
                pcr.ampl_reg_ref = chrom
                pcr.ampl_reg_start = start
                pcr.ampl_reg_end = end
                pcr.createSimpleProduct()
                pcr.save()

                tsa = TSACombination()
                tsa.uuid = pcr.uuid
                tsa.name = name
                tsa.length = length
                tsa.save()

            if "ref" not in request.POST or request.POST['ref'] != 'newsp':
                request.session['just_saved'] = 'Target sequence saved'

            return HttpResponse("ok")


#######################################
#View to define new mutations
#######################################

@laslogin_required
@login_required
def newMutation(request):
    g = GenomeGraphUtility()
    if request.method == 'POST':
        try:
            assembly = request.POST['assembly']
            method = request.POST['method']
            gene_uuid = request.POST['gene']
            syntax = request.POST['syntax']
            sa_type = request.POST['type']
            chrom = request.POST['chrom']
            start = request.POST['start']
            params = request.POST['params']
            ignoreNoGene = request.POST['ignoreNoGene']
            noSave = request.POST['noSave']
            xref = request.POST['xref']

            gene_uuid = gene_uuid if gene_uuid != "" else None
            # TODO: handle different assemblies

            s = SequenceAlteration()
            
            if method == '0':
                tx = g.getDefaultTranscriptForGene(gene_uuid=gene_uuid)
                tx_ac = tx['ac']
                print "[newMutation] method=syntax, tx_ac=%s, syntax=%s" % (tx_ac, syntax)
                s.set(tx_accession=tx_ac,cds_syntax=syntax)
                if xref != "":
                    s.setXref(xref)
                s._checkReference()
                exists = s.exists()
                if noSave != "true":
                    s.save()
                    k = KBReferenceHistory(uuid=s.getUUID(),data=json.dumps(s.getExtendedInfo()),labelTerm=LabelTerm.objects.get(name='sequence_alteration'),action=KBReferenceHistory.ADD)
                    k.save()
                    resp = {'uuid': s.getUUID(), 'done': True, 'hgvsg': s.getHGVS_g(), 'hgvsc': s.getHGVS_c(), 'hgvsp': s.getHGVS_p_1L(), 'exists': exists, 'genes': [{'uuid': gene_uuid, 'symbol': tx['gene_symbol']}]}
                else:
                    resp = {'done': True, 'exists': exists, 'info': s.getExtendedInfo()}

            
            elif method == '1':
                print "[newMutation] method=wizard, type=%s, chrom=%s, start=%s, gene_uuid=%s, params=%s" % (sa_type, chrom, start, gene_uuid, str(params))
                params = json.loads(params)
                if gene_uuid is not None:
                    # a gene has been specified by the user
                    gene_symbol = g.getGeneInfo(uuid=gene_uuid)[0].symbol
                    s.set(type=sa_type, chrom=chrom, start=start, gene_symbol=gene_symbol, gene_uuid=gene_uuid, **params)
                    if xref != "":
                        s.setXref(xref)
                    s._checkReference()
                    exists = s.exists()
                    if noSave != "true":
                        s.save()
                        k = KBReferenceHistory(uuid=s.getUUID(),data=json.dumps(s.getExtendedInfo()),labelTerm=LabelTerm.objects.get(name='sequence_alteration'),action=KBReferenceHistory.ADD)
                        k.save()
                        resp = {'uuid': s.getUUID(), 'done': True, 'hgvsg': s.getHGVS_g(), 'hgvsc': s.getHGVS_c(), 'hgvsp': s.getHGVS_p_1L(), 'exists': exists, 'genes': [{'uuid': gene_uuid, 'symbol': gene_symbol}]}
                    else:
                        resp = {'done': True, 'exists': exists, 'info': s.getExtendedInfo()}
                else:
                    # no gene has been specified by the user
                    # the sequence alteration "set" method will try to find the corresponding gene
                    # and return the number of matching genes found
                    n_genes = s.set(type=sa_type, chrom=chrom, start=start, gene_uuid=gene_uuid, **params)
                    if n_genes == 1:
                        if xref != "":
                            s.setXref(xref)
                        s._checkReference()
                        exists = s.exists()
                        if noSave != "true":
                            s.save()
                            k = KBReferenceHistory(uuid=s.getUUID(),data=json.dumps(s.getExtendedInfo()),labelTerm=LabelTerm.objects.get(name='sequence_alteration'),action=KBReferenceHistory.ADD)
                            k.save()
                            resp = {'uuid': s.getUUID(), 'done': True, 'hgvsg': s.getHGVS_g(), 'hgvsc': s.getHGVS_c(), 'hgvsp': s.getHGVS_p_1L(), 'exists': exists, 'genes': [{'uuid': s._params['gene_uuid'], 'symbol': s._params['gene_symbol']}]}
                        else:
                            resp = {'done': True, 'exists': exists, 'info': s.getExtendedInfo()}
                    elif n_genes == 0:
                        if xref != "":
                            s.setXref(xref)
                        s._checkReference()
                        exists = s.exists()
                        if ignoreNoGene == "1":
                            if noSave != "true":
                                s.save()
                                k = KBReferenceHistory(uuid=s.getUUID(),data=json.dumps(s.getExtendedInfo()),labelTerm=LabelTerm.objects.get(name='sequence_alteration'),action=KBReferenceHistory.ADD)
                                k.save()
                                resp = {'uuid': s.getUUID(), 'done': True, 'hgvsg': s.getHGVS_g(), 'hgvsc': s.getHGVS_c(), 'hgvsp': s.getHGVS_p_1L(), 'exists': exists, 'genes': []}
                            else:
                                resp = {'done': True, 'exists': exists, 'info': s.getExtendedInfo()}
                        else:
                            resp = {'uuid': s.getUUID(), 'done': False, 'hgvsg': s.getHGVS_g(), 'hgvsc': s.getHGVS_c(), 'hgvsp': s.getHGVS_p_1L(), 'exists': exists, 'genes': []}
                    else:
                        all_genes = s._graph_utils.getGenesInRegion(chrom=s._params['chrom'],start=s._params['start'],end=s._params['end'])
                        s._checkReference()
                        exists = s.exists()
                        gene_list = []
                        for gene in all_genes:
                            s = SequenceAlteration()
                            s.set(type=sa_type, chrom=chrom, start=start, gene_uuid=gene[0], gene_symbol=gene[1], **params)
                            if xref != "":
                                s.setXref(xref)
                            gene_list.append({'uuid': gene[0], 'symbol': gene[1], 'hgvsc': s.getHGVS_c(), 'hgvsp': s.getHGVS_p_1L()})
                        resp = {'uuid': s.getUUID(), 'done': False, 'hgvsg': s.getHGVS_g(), 'exists': exists, 'genes': gene_list}
            
            print "newMutation:", resp
            return HttpResponse(json.dumps(resp))

        except Exception as e:
            print "[newMutation] error: ", str(e)
            return HttpResponseServerError(str(e))

    elif request.method == 'GET':
        noSave = request.GET.get('noSave', '')
        noSave = noSave if noSave == 'true' else ''

        referer = request.GET.get('referer', '')
        referer = referer if referer in ['exploreKB'] else ''

        w = WebService.objects.get(name="Annotations Manager")
        try:
            u = w.urls_set.filter(available=True)[0].url
        except:
            u = ""

        assembly = [{'id': 0, 'name': 'hg19 (GRCh37.p13)'}]
        sa_types = [{'id': 'del', 'name': 'Deletion'},
                    {'id': 'delins', 'name': 'In-del'},
                    {'id': 'dup', 'name': 'Duplication'},
                    {'id': 'ins', 'name': 'Insertion'},
                    {'id': 'sub', 'name': 'Substitution'}]
        sa_params = [{'id': 'num_bases', 'name': 'Num. bases', 'rank': 2},
                     {'id': 'alt', 'name': 'Alt. base(s)', 'rank': 1},
                     {'id': 'ref', 'name': 'Ref. base(s)', 'rank': 0}]
        sa_types_params = {t: p['params'] for t, p in SequenceAlteration._seq_alt_types_params.items()}
        chrom = [x[1] for x in g.getAllChromosomes()]
        return render_to_response("newMutation.html", {'assembly': assembly, 'sa_types': sa_types, 'sa_params': sa_params, 'sa_types_params': sa_types_params, 'chrom': chrom, 'annotations_url': u, 'noSave': noSave, 'referer': referer}, RequestContext(request))


#######################################
#View to define new short genetic variations
#######################################

@laslogin_required
@login_required
def newSGV(request):
    g = GenomeGraphUtility()
    if request.method == 'POST':
        print "POST:", request.POST
        if True:
            assembly = request.POST['assembly']
            method = request.POST['method']
            allele = request.POST['allele']
            sgv_name = request.POST['sgv_name']
            dbsnp_pk = request.POST['dbsnp_pk']
            sgv_type = request.POST['type']
            chrom = request.POST['chrom']
            start = request.POST['start']
            strand = request.POST['strand']
            params = request.POST['params']
            xref = request.POST['xref']
            hr = json.loads(request.POST['hr'])

            # TODO: handle different assemblies
            if method == '0':
                obj = UCSCSnp141.objects.get(pk=dbsnp_pk)
                alleles = [x.strip() for x in allele.split(',')]
                for a in alleles:
                    if not a.startswith('_'):
                        allele_name = chr(int(a) + ord('A'))
                        print "[newSGV] method=fromDbSnp, name=%s, allele=%s" % (obj.name, allele_name)
                        s = ShortGeneticVariation()
                        print "#1"
                        s.set(obj=obj,dbSnpLookup=True,allele=allele_name)
                        print "#2"
                    else:
                        dummy, allele_index, allele_content = a.split('_')
                        allele_name = chr(int(allele_index) + ord('A'))
                        print "[newSGV] method=fromDbSnp, name=%s, allele=(%s)" % (obj.name, allele_content)
                        s = ShortGeneticVariation()
                        s.set(obj=obj,dbSnpLookup=True,allele='A')
                        s.setNewAllele(allele_name, allele_content)

                    exists = s.exists()
                    print "#3"
                    s.save()
                    print "#4"
                    # set homologous regions
                    if len(hr) > 0:
                        info = s.getInfo()
                        length = info['end'] - info['start']
                        s.convertToMultiRegion(hr[0]['chrom'], long(hr[0]['start']), long(hr[0]['start']) + length, hr[0]['strand'])
                        print "#hr init ok"
                        for h in hr[1:]:
                            print h
                            s.addMultiRegion(h['chrom'], long(h['start']), long(h['start']) + length, h['strand'])
                            print "hr added"

                    k = KBReferenceHistory(uuid=s.getUUID(),data=json.dumps(s.getInfo()),labelTerm=LabelTerm.objects.get(name='short_genetic_variation'),action=KBReferenceHistory.ADD)
                    print "#5"
                    k.save()
                resp = {'done': True}
                
            elif method == '1':
                params = json.loads(params)
                if sgv_type in ['single', 'insertion']:
                    end = start
                else:
                    end = str(long(start) + len(params['ref']) - 1)
                
                if sgv_type in ['single', 'insertion']:
                    a = [x.strip() for x in params['alt'].split(',')]
                    # add "normal" variant
                    if sgv_type == 'single':
                        a.append(params['ref'])
                    else:
                        a.append("")

                    for i, x in enumerate(a):
                        params['alt'] = x
                        allele = chr(i + ord('A'))
                        print "[newSGV] method=manual, name=%s, allele=%s, type=%s, chrom=%s, start=%s, end=%s, strand=%s, params=%s, xref=%s" % (sgv_name, allele, sgv_type, chrom, start, end, strand, str(params), xref)
                        s = ShortGeneticVariation()
                        s.set(name=sgv_name,dbSnpLookup=False,allele=allele,var_type=sgv_type,chrom=chrom,start=long(start),end=long(end),strand=strand,**params)
                        if xref != "":
                            s.setXref(xref)
                        exists = s.exists()
                        s.save()
                        k = KBReferenceHistory(uuid=s.getUUID(),data=json.dumps(s.getInfo()),labelTerm=LabelTerm.objects.get(name='short_genetic_variation'),action=KBReferenceHistory.ADD)
                        k.save()

                elif sgv_type in ['microsatellite']:
                    r = params['num_repeats'].split(',')
                    for i, x in enumerate(r):
                        params['num_repeats'] = int(x.strip())
                        allele = chr(i + ord('A'))
                        print "[newSGV] method=manual, name=%s, allele=%s, type=%s, chrom=%s, start=%s, end=%s, strand=%s, params=%s, xref=%s" % (sgv_name, allele, sgv_type, chrom, start, end, strand, str(params), xref)
                        s = ShortGeneticVariation()
                        s.set(name=sgv_name,dbSnpLookup=False,allele=allele,var_type=sgv_type,chrom=chrom,start=long(start),end=long(end),strand=strand,**params)
                        if xref != "":
                            s.setXref(xref)
                        exists = s.exists()
                        s.save()
                        k = KBReferenceHistory(uuid=s.getUUID(),data=json.dumps(s.getInfo()),labelTerm=LabelTerm.objects.get(name='short_genetic_variation'),action=KBReferenceHistory.ADD)
                        k.save()
                    # there is no "normal" variant
                else:
                    # deletion
                    # add "normal" variant
                    r = [params['ref']]
                    r.append("")

                    for i, x in enumerate(r):
                        params['ref'] = x
                        allele = chr(i + ord('A'))
                        print "[newSGV] method=manual, name=%s, allele=%s, type=%s, chrom=%s, start=%s, end=%s, strand=%s, params=%s, xref=%s" % (sgv_name, allele, sgv_type, chrom, start, end, strand, str(params), xref)
                        s = ShortGeneticVariation()
                        s.set(name=sgv_name,dbSnpLookup=False,allele=allele,var_type=sgv_type,chrom=chrom,start=long(start),end=long(end),strand=strand,**params)
                        if xref != "":
                            s.setXref(xref)
                        exists = s.exists()
                        s.save()
                        k = KBReferenceHistory(uuid=s.getUUID(),data=json.dumps(s.getInfo()),labelTerm=LabelTerm.objects.get(name='short_genetic_variation'),action=KBReferenceHistory.ADD)
                        k.save()
                # set homologous regions
                if len(hr) > 0:
                    length = end - start
                    s.convertToMultiRegion(hr[0]['chrom'], long(hr[0]['start']), long(hr[0]['start']) + length, hr[0]['strand'])
                    for h in hr[1:]:
                        s.addMultiRegion(h['chrom'], long(h['start']), long(h['start']) + length, h['strand'])

                resp = {'done': True}
            
            print "newSGV:", resp
            return HttpResponse(json.dumps(resp))

        #except Exception as e:
        #    print "[newSGV] error: ", str(e)
        #    return HttpResponseServerError(str(e))

    elif request.method == 'GET':
        referer = request.GET.get('referer', '')
        referer = referer if referer in ['exploreKB'] else ''

        assembly = [{'id': 0, 'name': 'hg19 (GRCh37.p13)'}]

        sgv_types = [{'id': 'single', 'name': 'Single Nucleotide Polymorphism', 'rank': 0, 'help': [{'param': 'ref', 'text': 'Enter reference variant, e.g. G'}, {'param': 'alt', 'text': 'List all alternative observed/observable variants separated by commas, e.g. A, T, C'}], 'enabled': True},
                    {'id': 'in-del', 'name': 'In-del Polymorphism', 'rank': 3, 'enabled': False},
                    {'id': 'microsatellite', 'name': 'Microsatellite/Short Tandem Repeat', 'rank': 5, 'help': [{'param': 'ref', 'text': 'Enter repeat sequence'}, {'param': 'num_repeats', 'text': 'List all observed/observable numbers of repeats separated by commas, e.g. 12, 15, 18'}], 'enabled': True},
                    {'id': 'mnp', 'name': 'Multi-Nucleotide Polymorphism', 'rank': 4, 'enabled': False},
                    {'id': 'insertion', 'name': 'Insertion Polymorphism', 'rank': 1, 'help': [{'param': 'alt', 'text': 'List all observed/observable insert sequences separated by commas, e.g. ATTC, ATTCG, ATGG'}], 'enabled': True},
                    {'id': 'deletion', 'name': 'Deletion Polymorphism', 'rank': 2, 'help': [{'param': 'ref', 'text': 'Enter delete sequence, e.g. ATTC'}], 'enabled': True}]
        sgv_params = [{'id': 'num_repeats', 'name': 'Num. repeats', 'rank': 2, 'type': 'text'},
                     {'id': 'alt', 'name': 'Alt. base(s)', 'rank': 1, 'type': 'text'},
                     {'id': 'ref', 'name': 'Ref. base(s)', 'rank': 0, 'type': 'text'}]

        sgv_types_params = {t: p['params'] for t, p in ShortGeneticVariation._var_types_params.items()}
        
        chrom = [x[1] for x in g.getAllChromosomes()]
        return render_to_response("newSGV.html", {'assembly': assembly, 'sgv_types': sgv_types, 'sgv_params': sgv_params, 'sgv_types_params': sgv_types_params, 'chrom': chrom, 'referer': referer}, RequestContext(request))


#######################################
#View to define new gene copy number variations
#######################################

@laslogin_required
@login_required
def newCNV(request):
    g = GenomeGraphUtility()
    if request.method == 'POST':
        try:
            assembly = request.POST['assembly']
            method = request.POST['method']
            gene = request.POST['gene']
            cnv_class = request.POST['class']
            chrom = request.POST['chrom']
            start = request.POST['start']
            end = request.POST['end']
            xref = request.POST['xref']

            # TODO: handle different assemblies

            c = CopyNumberVariation()
            
            if method == '0':
                print "[newCNV] method=gene, gene_uuid=%s, cnv_class=%s, xref=%s" % (gene, cnv_class, xref)
                c.set(geneUuid=gene,type=cnv_class)
                
            elif method == '1':
                print "[newCNV] method=region, chrom=%s, start=%s, end=%s, cnv_class=%s, xref=%s" % (chrom, start, end, cnv_class, xref)
                c.set(chrom=chrom,start=long(start),end=long(end),type=cnv_class)

            if xref != "":
                c.setXref(xref)
            exists = c.exists()
            c.save()
            k = KBReferenceHistory(uuid=c.getUUID(),data=json.dumps(c.getInfo()),labelTerm=LabelTerm.objects.get(name='copy_number_variation'),action=KBReferenceHistory.ADD)
            k.save()
            resp = {'uuid': c.getUUID(), 'done': True, 'exists': exists}
            
            print "newCNV:", resp
            return HttpResponse(json.dumps(resp))

        except Exception as e:
            print "[newCNV] error: ", str(e)
            return HttpResponseServerError(str(e))

    elif request.method == 'GET':
        referer = request.GET.get('referer', '')
        referer = referer if referer in ['exploreKB'] else ''

        assembly = [{'id': 0, 'name': 'hg19 (GRCh37.p13)'}]

        cnv_types = [{'id': 'amplification', 'name': 'CN Amplification', 'rank': 4},
                    {'id': 'gain', 'name': 'CN Gain', 'rank': 3},
                    {'id': 'neutral', 'name': 'CN Neutral', 'rank': 2},
                    {'id': 'loss', 'name': 'CN Loss', 'rank': 1},
                    {'id': 'deletion', 'name': 'CN Deletion', 'rank': 0}]

        chrom = [x[1] for x in g.getAllChromosomes()]
        return render_to_response("newGCN.html", {'assembly': assembly, 'cnv_types': cnv_types, 'chrom': chrom, 'referer': referer}, RequestContext(request))


#######################################
#View to define new gene fusions
#######################################

@laslogin_required
@login_required
def newGeneFusion(request):
    pass


#########################################
#Define criteria for querying annotations
#########################################
@laslogin_required
@login_required
def queryAnnotations(request):
    if request.method == 'GET':
        w = WebService.objects.get(name="Annotations Manager")
        try:
            u = w.urls_set.filter(available=True)[0].url
        except:
            u = ""
        labels = {l.id: l.displayName for l in LabelTerm.objects.filter(fatherLabel=None).order_by('displayName')}
        technologies = {0: {'name': 'Any', 'labels': labels.keys()}}
        for e in ExperimentType.objects.all():
            technologies[e.id] = {'name': e.name, 'labels': [l.labelTerm_id for l in e.experimenttype_has_analysedlabelterm_set.all()]}
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
        return render_to_response('queryAnnotations.html', {'labels_json': json.dumps(labels), 'technologies_json': json.dumps(technologies), 'technologies': ExperimentType.objects.all(), 'annotations_url': u, 'chrom': chrom}, RequestContext(request)) 

    elif request.method == 'POST':
        print "[AnnotationsManager.views.queryAnnotations] Query received: "
        print request.POST
        try:
            source = request.POST['source']
            criteria = json.loads(request.POST['criteria'])
            genes = json.loads(request.POST['genes'])
            samples = json.loads(request.POST['samples'])
        except Exception as e:
            print "[AnnotationsManager.views.queryAnnotations] Error: ", str(e)
            return HttpResponseServerError("An error has occurred.")

        results = runAnnotationQuery(source, criteria, genes, samples)
        r = QueryReport()
        for labelTerm_id, annot_list in results.iteritems():
            labelTerm = LabelTerm.objects.get(pk=labelTerm_id)
            annotationModel = labelTerm.getAnnotationModel()
            aggregates = annotationModel.objects.aggregateForReport(annot_list)
            headers, data = annotationModel.objects.formatForReport(aggregates)
            print "Adding sheet to report:", labelTerm.displayName
            print "Headers:", headers
            print "Data:", data
            r.generateReportSheet(labelTerm.displayName, headers, data)
        filename = r.save(request.user.username)
        resp = HttpResponse(FileWrapper(open(filename,"rb")), content_type=mimetypes.guess_type(filename)[0])
        resp['Content-Disposition'] = 'attachment; filename="%s"' % filename.split('/')[-1]
        r.remove()
        return resp

#########################################
#Define technologies used with each amplicon
#########################################
@laslogin_required
@login_required
def defineAmpliconTechnologies(request):
    g = GenomeGraphUtility()
    if request.method == 'POST':
        if 'auuid' in request.POST:
            print "Request received:", request.POST
            tech = [int(x.split('_')[1]) for x in request.POST.keys() if x.startswith('tech_')]
            labelsYes = [x.technologyLabel for x in ExperimentType.objects.filter(id__in=tech)]
            labelsNo = [x.technologyLabel for x in ExperimentType.objects.exclude(id__in=tech).exclude(technologyLabel=None)]
            print labelsYes, labelsNo
            g.setPCRProductTechnologies(request.POST['auuid'], labelsYes, labelsNo)
    
    res = g.getAllPCRProducts()
    amplicons = {r['pcrp_uuid']: dict(zip(r.columns, r.values)) for r in res}
    experimentType = ExperimentType.objects.exclude(technologyLabel=None).order_by('name')
    return render_to_response('definetech.html', {'amplicons': amplicons, 'technologies': experimentType}, RequestContext(request))

#########################################
#Generate Sequenom data report
#########################################
@laslogin_required
@login_required
def sequenomReport(request):
    if request.method == 'GET':
        return render_to_response('sequenomReport.html', {}, RequestContext(request)) 
    elif request.method == 'POST':
        print "[AnnotationsManager.views.sequenomReport] Report generation request received from %s" % request.user.username
        plates = json.loads(request.POST['plates'])
        dates = json.loads(request.POST['dates'])
        samples = json.loads(request.POST['samples'])
        snps = json.loads(request.POST['snps'])
        print "[AnnotationsManager.views.sequenomReport] plates = ", plates
        print "[AnnotationsManager.views.sequenomReport] dates = ", dates
        print "[AnnotationsManager.views.sequenomReport] samples = ", samples
        print "[AnnotationsManager.views.sequenomReport] snps = ", snps
        params = {'plates': plates, 'dates': dates, 'samples': samples, 'snps': snps}
        
        filename = "SequenomDataReport_%s_%s.las" % (request.user.username, datetime.datetime.now())
        fullPath = settings.MEDIA_ROOT + 'reports/' + filename
        Annotation_ShortGeneticVariation.objects.generateExpDataReport(fullPath, params)
        #except Exception as e:
        #    print "[AnnotationsManager.views.sequenomReport] An exception occurred in generateExpDataReport:", str(e)
        #    return HttpResponse("An error occurred")
        resp = HttpResponse(FileWrapper(open(fullPath,"rb")), content_type='text/tab-separated-values')
        resp['Content-Disposition'] = 'attachment; filename="%s"' % filename
        return resp

#########################################
#Explore Knowledge Base
#########################################
@laslogin_required
@login_required
def exploreKB(request):
    if request.method == 'GET':
        w = WebService.objects.get(name="Annotations Manager")
        try:
            u = w.urls_set.filter(available=True)[0].url
        except:
            u = ""

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

        return render_to_response('exploreKB.html', {'annotations_url': u, 'chrom': chrom}, RequestContext(request)) 

    elif request.method == 'POST':
        print "[AnnotationsManager.views.exploreKB] new rquest from " % request.user.username
        return HttpResponse()

#########################################
#Run FingerPrinting procedure upon user request and download reports
#########################################
@laslogin_required
@login_required
def fingerPrinting(request):
    if request.method == 'POST':
        if "run" in request.POST:
            notifyViaEmail = True if request.POST.get('notify', None) else False
            if FingerPrintingReport.objects.filter(ready=False, error=False, author=request.user).count() == 0:
                report = FingerPrintingReport()
                report.initialize(user=request.user,description=request.POST.get('description'))
                report.run(notifyViaEmail)
            else:
                request.session['cannot_run'] = True
            return HttpResponseRedirect(reverse(annotations.views.fingerPrinting))
        elif "cancel" in request.POST:
            rid = request.POST['id']
            report = FingerPrintingReport.objects.get(pk=rid)
            if not report.ready:
                print "Cancelling execution"
                report.cancel()
            else:
                print "Deleting"
                report.delete()
            return HttpResponseRedirect(reverse(annotations.views.fingerPrinting))

    cannot_run = request.session.get('cannot_run', False)
    try:
        del request.session['cannot_run']
    except:
        pass
    reports = FingerPrintingReport.objects.all()
    return render_to_response('fingerPrinting.html', {'cannot_run': cannot_run, 'media_url': settings.MEDIA_URL, 'reports': reports, 'cannot_run': cannot_run}, RequestContext(request)) 
