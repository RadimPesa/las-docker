from annotations.models import *
from itertools import chain

BLATSRV_URL = 'localhost'
BLATSRV_PORT = '1515'
BLATCLIENT_BIN = "/srv/www/annotationsManager/aligntools/bin/gfClient"
SEQPATH = ""#/srv/www/annotationsManager/aligntools/seq/"
#HG19_SEQ = "/srv/www/annotationsManager/aligntools/seq/hg19.2bit"
HG19_SEQ = "hg19.2bit"
LIFTOVER_BIN = "/srv/www/annotationsManager/aligntools/bin/liftOver"
LIFTOVER_HG18toHG19_CHAIN = "/srv/www/annotationsManager/aligntools/chains/hg18ToHg19.over.chain"
TWOBITTOFA_BIN = "/srv/www/annotationsManager/aligntools/bin/twoBitToFa"

def GenesFromSymbol(geneSymbol, exactMatch):
        if exactMatch:
            gene_ids1 = Gene.objects.values_list('id_gene', flat=True).filter(gene_name=geneSymbol).only('id_gene')
            gene_ids2 = GeneAlias.objects.values_list('id_gene', flat=True).filter(gene_synonym=geneSymbol).only('id_gene')
        else:
            gene_ids1 = Gene.objects.values_list('id_gene', flat=True).filter(gene_name__icontains=geneSymbol).only('id_gene')
            gene_ids2 = GeneAlias.objects.values_list('id_gene', flat=True).filter(gene_synonym__icontains=geneSymbol).only('id_gene')

        gene_ids = list(chain(gene_ids1, gene_ids2))
        gene_objs = Gene.objects.filter(id_gene__in=gene_ids).only('id_gene')

        return gene_objs

def loadJSONfield(obj, field):
	import json
	if field not in obj._meta.get_all_field_names():
		return None
	value = obj.__getattribute__(field)
	if value[-1] == ',':
		value = value[:-1]
	return json.loads('[' + value + ']')


class SequenceAlignment(object):
	def __init__(self, seq, strand, tx, start, end, gene, gene_name):
		self.seq = seq
		self.strand = strand
		self.tx = tx
		self.start = start
		self.end = end
		self.gene = gene
		self.gene_name = gene_name

def getAlignments(sequences):
	import subprocess
	from subprocess import call
	import tempfile
	import os

	alignments = []

	DEVNULL = open(os.devnull, 'w')

	for x in sequences:

		name = x[0]
		seq  = x[1].strip()
		
		with tempfile.NamedTemporaryFile() as in_f:
			in_f.delete = False
			in_f_name = in_f.name
			in_f.write(">" + name + "\n")
			in_f.write(seq + "\n")

		with tempfile.NamedTemporaryFile() as out_f:
			out_f.delete = False
			out_f_name = out_f.name

		ret = call([BLATCLIENT_BIN, "-nohead", "-minScore="+str(len(seq)), "-minIdentity=100", BLATSRV_URL, BLATSRV_PORT, SEQPATH, in_f_name, out_f_name], stdout=DEVNULL)

		with open(out_f_name, "r") as out_f:

			curr_align = []
			for l in out_f:
				l = l.split()
				g,gn = getGene(l[13], l[15], l[16])
				a = SequenceAlignment(seq=seq, strand=l[8], tx=l[13], start=l[15], end=l[16], gene=g, gene_name=gn)
				curr_align.append(a)

			alignments.append((name, seq, curr_align))

		os.remove(in_f_name)
		os.remove(out_f_name)
	
	DEVNULL.close()

	return alignments

def getGene(tx, start, end):
	#	g = Gene.objects.filter(chromosome=int(tx[3:]),ensembl_genome_start__lte=int(start), ensembl_genome_stop__gte=int(end))[0]
	#	gene_name = g.gene_name
	try:
		g_ucsc = UCSCrefFlat.objects.filter(chrom=tx,txStart__lte=int(start),txEnd__gte=int(end))[0]
		gene_name = g_ucsc.geneName
		try:
			g = Gene.objects.filter(gene_name=g_ucsc.geneName)[0]
		except:
			g = None
	except:
		g = None
		gene_name = 'n/a'

	return (g, gene_name)

def hg18_to_hg19(chrom, start, end, name=None, keepfile=False):
	#import subprocess
	from subprocess import call
	import tempfile
	import os

	DEVNULL = open(os.devnull, 'w')
	
	if not name:
		name = 'pgdxmut'
	
	with tempfile.NamedTemporaryFile() as hg18f:
		hg18f.delete = False
		hg18_name = hg18f.name
		hg18f.write(chrom + '\t' + str(start) + '\t' + str(end) + '\t' + name + '\n')
	
	with tempfile.NamedTemporaryFile() as hg19f:
		hg19f.delete = False
		hg19_name = hg19f.name

	# call liftOver tool to convert Hg18 coordinate to Hg19
	ret = call([LIFTOVER_BIN, hg18_name, LIFTOVER_HG18toHG19_CHAIN, hg19_name, "/dev/null"], stderr=DEVNULL)

	DEVNULL.close()

	if keepfile:
		return hg19_name
	else:
		with open(hg19_name, 'r') as f:
			x = f.readline().split()
		os.remove(hg19_name)
		if len(x) == 4:
			return (x[0], int(x[1]), int(x[2]))

def getSequence(bedfile=None,chrom=None,start=None,end=None):
	from subprocess import call
	import tempfile
	import os

	DEVNULL = open(os.devnull, 'w')

	ret = call([TWOBITTOFA_BIN, "-bed="+bedfile, "-bedPos", HG_19, seq_name], stderr=DEVNULL)
