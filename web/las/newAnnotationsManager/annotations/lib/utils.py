from itertools import chain
from django.conf import settings
import tempfile
from subprocess import call
import os
import os.path
import requests
import json

TWOBITTOFA_BIN = settings.KENT_UTILS_BIN_PATH + "/twoBitToFa"
LIFTOVER_BIN = settings.KENT_UTILS_BIN_PATH + "/liftOver"

BLATSRV_URL = 'localhost'
BLATSRV_PORT = '1515'
BLATCLIENT_BIN = "/srv/www/annotationsManager/aligntools/bin/gfClient"
SEQPATH = ""#/srv/www/annotationsManager/aligntools/seq/"
#HG19_SEQ = "/srv/www/annotationsManager/aligntools/seq/hg19.2bit"
HG19_SEQ = "hg19.2bit"


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

class LiftOver(object):
    def __init__(self, profile):
        try:
            self.__profiles = {x['name'] : x['path'] for x in settings.LIFTOVER_PROFILES}
        except:
            raise Exception("LIFTOVER_PROFILES not defined in settings!")
        if profile not in self.__profiles:
            raise Exception("Unknown profile '{0}'".format(profile))
        self.__profile = profile

    def convert(self, chrom, start, end):
        #import subprocess
        from subprocess import call
        import tempfile
        import os

        if not isinstance(chrom, basestring):
            raise Exception("'chrom' must be a string")
        if not chrom.startswith('chr'):
            chrom = 'chr' + chrom
        with tempfile.NamedTemporaryFile(mode='w',bufsize=0) as src, tempfile.NamedTemporaryFile(mode='r') as dest, tempfile.NamedTemporaryFile(mode='r') as unmapped, open(os.devnull, "w") as stdnull:
            src.write("{chrom}\t{start}\t{end}\t{name}\n".format(chrom=chrom,start=start,end=end,name='temp'))
            chain_path = self.__profiles[self.__profile]
            ret = call([LIFTOVER_BIN, src.name, chain_path, dest.name, unmapped.name], stdout=stdnull, stderr=stdnull)
            x = dest.readline().strip().split()
            if len(x) == 0:
                try:
                    x = 'Mapping did not succeed. Liftover returned the following:\n'
                    for l in unmapped:
                        x += l
                except:
                    raise Exception("An unknown error occurred")
                raise Exception(x)

        return {'chrom': x[0], 'start': int(x[1]), 'end': int(x[2])}

class RefSequence(object):
	def __init__(self, profile):
		try:
			self.__profiles = {x['name'] : x['path'] for x in settings.REFSEQ_PROFILES}
		except:
			raise Exception("REFSEQ_PROFILES not defined in settings!")
		if profile not in self.__profiles:
			raise Exception("Unknown profile '{0}'".format(profile))
		self.__profile = profile
		if self.__profile == 'genome':
			self.getRefSequence = self.__getGenomeRefSequence
		elif self.__profile == 'transcriptome':
			self.getRefSequence = self.__getTxRefSequence
		else:
			self.__profile = self.__not_implemented

	def __not_implemented(self, *args, **kwargs):
		raise Exception("Not implemented")

	def __getTxRefSequence(self, tx_ac, start=None, length=None):
		tx_ac = tx_ac.strip()
		if start != None and length != None:
			start = start-1
			end = start + length
			db_file = "{0}:{1}:{2}-{3}".format(self.__profiles[self.__profile], tx_ac, start, end)
		elif start is None and length is None:
			db_file = "{0}:{1}".format(self.__profiles[self.__profile], tx_ac)
		else:
			raise Exception("Either both coordinates or no coordinates must be specified")
		with tempfile.NamedTemporaryFile() as tmp:
			ret = call([TWOBITTOFA_BIN, db_file, tmp.name])
			tmp.readline() # read fasta header line
			seq = ''
			for line in tmp:
				seq += line.strip()

		return seq

	def __getGenomeRefSequence(self, chrom, start, length, strand):
		if type(chrom) != str:
			chrom = str(chrom)
		chrom = chrom.strip()
		if not chrom.startswith('chr'):
			chrom = 'chr' + chrom
		#if strand == '+':
		start = start-1
		end = start + length
		#else:
		#	end = start - 1
		#	start = end + length
		db_file = "{0}:{1}:{2}-{3}".format(self.__profiles[self.__profile], chrom, start, end)

		with tempfile.NamedTemporaryFile() as tmp:
			#print TWOBITTOFA_BIN, db_file
			ret = call([TWOBITTOFA_BIN, db_file, tmp.name])
			tmp.readline() # read fasta header line
			seq = ''
			for line in tmp:
				seq += line.strip()

		if strand == '+':
			return seq
		else:
			from Bio import Seq
			return Seq.reverse_complement(seq)
