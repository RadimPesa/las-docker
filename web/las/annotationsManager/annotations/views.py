# Create your views here.

from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseServerError, HttpResponseRedirect
from django.conf import settings
from django.contrib.auth.decorators import login_required
from LASAuth.decorators import laslogin_required

from annotations.models import *
from annotations.utils import *

from subprocess import call
import tempfile
import os
import json
import ast

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
	return HttpResponseRedirect(settings.LAS_AUTH_SERVER_URL)


#######################################
#Create Target Sequence view
#######################################

@laslogin_required
@login_required
def create_targetseq(request):

	if request.method == 'GET':
		dic = {}
		if 'ref' in request.GET and request.GET['ref'] == 'newsp':
			dic['ref'] = 'newsp'
		
		# request to perform sequence alignment
		if 'tsname' in request.GET and 'sequence' in request.GET:
			name = request.GET['tsname']
			sequence = request.GET['sequence']

			al = getAlignments([(name, sequence)])[0][2]
	
			request.session['alignments'] = al
			request.session['tsname'] = name
			request.session['sequence'] = sequence

			#dic['alignments'] = al
			#dic['tsname'] = name
			#dic['sequence'] = sequence

			alignments = []
			
			for x in al:
				alignments.append((x.tx, x.start, x.end, x.strand, x.gene_name))

			return HttpResponse(json.dumps(alignments))#render_to_response("primers.html", dic, RequestContext(request))

		else:

			if 'just_saved' in request.session:
				dic['just_saved'] = request.session['just_saved']
				del request.session['just_saved']
			return render_to_response("primers.html", dic, RequestContext(request))

	elif request.method == 'POST':
		#try:
		if 'alignments' in request.POST:
			sel_alignments = request.POST.getlist('alignments')
			alignments = request.session['alignments']

			name = request.session['tsname']
			sequence = request.session['sequence']

			ts = TargetSequence()
			ts.name = name
			ts.sequence = sequence
			ts.save()

			for x in sel_alignments:
				al = alignments[int(x)]
				tsa = TargetSequenceAlignment()
				tsa.chromosome = Chromosome.objects.get(name=al.tx)
				tsa.strand = al.strand
				tsa.alignStart = al.start
				tsa.alignEnd = al.end
				tsa.targetSequence = ts
				tsa.gene = al.gene
				tsa.save()

			del request.session['alignments']
			del request.session['tsname']
			del request.session['sequence']

			if "ref" not in request.POST or request.POST['ref'] != 'newsp':
				request.session['just_saved'] = 'Target sequence saved'
			return HttpResponse(json.dumps((ts.id, ts.name)))
		
		elif 'seqfile' in request.FILES:
		
			f = request.FILES['seqfile']
			sequences = []
			for line in f:
				try:
					name, sequence = line.split('\t')
				except:
					continue
				sequences.append((name, sequence))

			alignments = getAlignments(sequences)

			for x in alignments:
				if len(x[2]) == 0:
					continue
				ts = TargetSequence()
				ts.name = x[0]
				ts.sequence = x[1]
				ts.save()

				for y in x[2]:
					tsa = TargetSequenceAlignment()
					tsa.chromosome = Chromosome.objects.get(name=y.tx)
					tsa.strand = y.strand
					tsa.alignStart = y.start
					tsa.alignEnd = y.end
					tsa.targetSequence = ts
					tsa.gene = getGene(y.tx, y.start, y.end)[0]
					tsa.save()

			not_found = [s for s in alignments if len(s[2]) == 0]

			num_total = len(sequences)
			num_found = num_total - len(not_found)

			return render_to_response("alignReport.html", {'num_found': num_found, 'num_total': num_total, 'not_found': not_found, 'alignments': alignments}, RequestContext(request))
		
		
		#except Exception,e:
		#	return HttpResponse(str(e))





#######################################
#Create Sequence Pair view
#######################################

@laslogin_required
@login_required
def create_seqpair(request):
	if request.method == 'GET':

		if 'act' in request.GET:

			act = request.GET['act']

			# search target sequence
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

			# compute sequence combinations
			elif act == 'seqcombo':
				
				try:
					ts1_id = request.GET['ts1_id']
					ts2_id = request.GET['ts2_id']
				except:
					return render_to_response("seqpairs.html", RequestContext(request))

				try:
					ts1_align = TargetSequence.objects.get(pk=ts1_id).targetsequencealignment_set.all()
					ts2_align = TargetSequence.objects.get(pk=ts2_id).targetsequencealignment_set.all()
				except:
					return HttpResponse(json.dumps([]))

				combos = []
				computed_combos = []
				names = []

				for x in ts1_align:

					for y in ts2_align:
						
						if x.strand == '+' and y.strand == '-':

							gnx = x.gene.gene_name if x.gene else 'n/a'
							gny = y.gene.gene_name if y.gene else 'n/a'
							
							lblx = x.gene.gene_name if x.gene else x.chromosome.name
							lbly = y.gene.gene_name if y.gene else y.chromosome.name
							
							if lblx == lbly:
							 	name = lblx + '_' + x.targetSequence.name + '|' + y.targetSequence.name
							else:
							 	name = lblx + '_' + x.targetSequence.name + '|' + lbly + '_' + y.targetSequence.name
							i = 1
							while name in names:
								name = name + '__' + str(i)
								i += 1
							names.append(name)

							length = str(max(x.alignEnd, y.alignEnd) - min(x.alignStart, y.alignStart))  if x.chromosome == y.chromosome else '??'
							combos.append((x.id, y.id, x.targetSequence.name, x.chromosome.name, x.alignStart, x.alignEnd, gnx, y.targetSequence.name, y.chromosome.name, y.alignStart, y.alignEnd, gny, length, name))
							computed_combos.append((x.id, y.id))

						elif x.strand == '-' and y.strand == '+':

							gnx = x.gene.gene_name if x.gene else 'n/a'
							gny = y.gene.gene_name if y.gene else 'n/a'
							
							lblx = x.gene.gene_name if x.gene else x.chromosome.name
							lbly = y.gene.gene_name if y.gene else y.chromosome.name
							
							if lbly == lblx:
							 	name = lbly + '_' + y.targetSequence.name + '|' + x.targetSequence.name
							else:
							 	name = lbly + '_' + y.targetSequence.name + '|' + lblx + '_' + x.targetSequence.name
							i = 1
							while name in names:
								name = name + '__' + str(i)
								i += 1
							names.append(name)
								
							length = str(max(x.alignEnd, y.alignEnd) - min(x.alignStart, y.alignStart)) if x.chromosome == y.chromosome else '??'
							combos.append((y.id, x.id, y.targetSequence.name, y.chromosome.name, y.alignStart, y.alignEnd, gny, x.targetSequence.name, x.chromosome.name, x.alignStart, x.alignEnd, gnx, length, name))
							computed_combos.append((y.id, x.id))

				if 'combos' in request.session:
					del request.session['combos']
				request.session['combos'] = computed_combos
				return HttpResponse(json.dumps(combos))

			# get alignments for manual definition of sequence combo
			elif act == 'getalign':

				try:
					ts_id = request.GET['ts_id']
				except:
					return render_to_response("seqpairs.html", RequestContext(request))

				try:
					ts_align = TargetSequence.objects.get(pk=ts_id).targetsequencealignment_set.all()
				except:
					return HttpResponse(json.dumps([]))

				aligns = []

				for x in ts_align:
					aligns.append((x.id, x.chromosome.name, x.alignStart, x.alignEnd, x.strand, x.gene.gene_name if x.gene else 'n/a'))

				return HttpResponse(json.dumps(aligns))

			elif act == 'newcombo':

				try:
					al1_id = request.GET['al1_id']
					al2_id = request.GET['al2_id']
				except:
					return render_to_response("seqpairs.html", RequestContext(request))

				try:
					al1 = TargetSequenceAlignment.objects.get(pk=al1_id)
					al2 = TargetSequenceAlignment.objects.get(pk=al2_id)
				except:
					return HttpResponse(json.dumps(None))


				gn1 = al1.gene.gene_name if al1.gene else 'n/a'
				gn2 = al2.gene.gene_name if al2.gene else 'n/a'
				
				lbl1 = al1.gene.gene_name if al1.gene else al1.chromosome.name
				lbl2 = al2.gene.gene_name if al2.gene else al2.chromosome.name
				
				if lbl1 == lbl2:
				 	name = lbl1 + '_' + al1.targetSequence.name + '|' + al2.targetSequence.name
				else:
				 	name = lbl1 + '_' + al1.targetSequence.name + '|' + lbl2 + '_' + al2.targetSequence.name

				length = str(max(al1.alignEnd, al2.alignEnd) - min(al1.alignStart, al2.alignStart))  if al1.chromosome == al2.chromosome else '??'
				newcombo = (al1.id, al2.id, al1.targetSequence.name, al1.chromosome.name, al1.alignStart, al1.alignEnd, gn1, al2.targetSequence.name, al2.chromosome.name, al2.alignStart, al2.alignEnd, gn2, length, name)

				computed_combos = request.session['combos']
				computed_combos.append((al1.id, al2.id))
				request.session['combos'] = computed_combos

				return HttpResponse(json.dumps(newcombo))

			else:
				return render_to_response("seqpairs.html", RequestContext(request))	

		else:
			return render_to_response("seqpairs.html", RequestContext(request))

	elif request.method == 'POST':
		try:
			# get selected combinations from query dict
			combos = request.POST.getlist('combos')
		except:
			return render_to_response("seqpairs.html", RequestContext(request))

		# for each combination:
		#   check if it's in the session
		#   if so, check if name and length are in query dict
		#   if so, go ahead and save it

		err = ''
		computed_combos = request.session['combos']
		for x in combos:
			if tuple([int(y) for y in x.split('_')]) not in computed_combos:
				err = "Invalid sequence combo"
			elif 'name_' + x not in request.POST or 'length_' + x not in request.POST:
				err = "Invalid sequence combo name or length"
			else:
				err = "Sequence combo saved"
				tsac = TargetSequenceAlignmentCombo()
				tsac.name = request.POST['name_'+x]
				tsac.length = request.POST['length_'+x]
				tsac.save()
				tsachtsa1 = TargetSequenceAlignmentCombo_has_TargetSequenceAlignment()
				tsachtsa1.target_seq_align_combo = tsac
				tsachtsa1.target_seq_align = TargetSequenceAlignment.objects.get(pk=x.split('_')[0])
				tsachtsa1.save()
				tsachtsa2 = TargetSequenceAlignmentCombo_has_TargetSequenceAlignment()
				tsachtsa2.target_seq_align_combo = tsac
				tsachtsa2.target_seq_align = TargetSequenceAlignment.objects.get(pk=x.split('_')[1])
				tsachtsa2.save()

		return render_to_response("seqpairs.html", {'just_saved': err}, RequestContext(request))


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

