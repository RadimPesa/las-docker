### ANNOTATION-SPECIFIC SETTINGS

ANNOTATION_SOURCE_FILES_PATH = '/genomic/data-files'

KENT_UTILS_BIN_PATH = '/genomic/bin'
LIFTOVER_PROFILES = [
    {
        'name': 'hg18ToHg19',
        'path': '/genomic/liftOver/hg18ToHg19.over.chain'
    },
    {
        'name': 'hg19ToHg18',
        'path': '/genomic/liftOver/hg19ToHg18.over.chain'
    },
    {
        'name': 'hg38ToHg19',
        'path': '/genomic/liftOver/hg38ToHg19.over.chain'
    },
    {
        'name': 'hg19ToHg38',
        'path': '/genomic/liftOver/hg19ToHg38.over.chain'
    },
]
REFSEQ_PROFILES = [
    {
        'name': 'genome',
        'path': '/blat/seq/GRCh37.p13.chrom.2bit'
    },
    {
        'name': 'transcriptome',
        'path': '/blat/seq/gencode.v19.pc_transcripts.simple.2bit'
    },
]
ALIGNER_PATHS = {
    'BLAT_CLIENT': '/blat/bin/gfClient',
}
ALIGNER_PROFILES = [
    {
        'name': 'genome',
        'verboseName': 'GRCh37.p13 human genome assembly (Hg19)',
        'host': 'blat-genome',
        'port': '11515',
        'type': 'BLAT_CLIENT',
        'seqDir': '/blat/seq/'
    },
    {
        'name': 'transcriptome',
        'verboseName': 'Protein-coding transcript sequences (Gencode v.19)',
        'host': 'blat-transcriptome',
        'port': '11516',
        'type': 'BLAT_CLIENT',
        'seqDir': '/blat/seq/'
    },
]

ENSEMBL = {
    'HOST': 'ensembldb.ensembl.org',
    'USER': 'anonymous',
    'PASSWORD': '',
    'NAME': 'homo_sapiens_core_84_38'
}

UCSC = {
    'HOST': 'genome-mysql.soe.ucsc.edu',
    'USER': 'genome',
    'PASSWORD': '',
    'NAME': 'hg19'
}

### END ANNOTATION-SPECIFIC SETTINGS

