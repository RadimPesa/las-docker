from django.db.models import *

class CellLine(Model):
    name = CharField(max_length=255, db_column='name', unique=True)
    source = CharField(max_length=255, db_column='source', blank=True, null=True)
    class Meta:
        db_table='CELL_LINE'
    def names(self):
        return [self.name] + [x.name for x in self.celllinealias_set.all()]

class CellLineAlias(Model):
    name = CharField(max_length=255, db_column='name')
    cellLine = ForeignKey('CellLine', db_column='id_cellLine')
    class Meta:
        db_table='CELL_LINE_ALIAS'

class TargetSequence(Model):
    name = CharField(max_length=128, db_column='NAME')
    sequence = CharField(max_length=8192, db_column='SEQUENCE')
    class Meta:
        db_table='TARGET_SEQUENCE'

class Chromosome(Model):
    name = CharField(max_length=255, db_column='name')
    chrom = CharField(max_length=10)
    size = IntegerField()
    class Meta:
        db_table = u'CHROMOSOME'

class TargetSequenceAlignment(Model):
    chromosome = ForeignKey('Chromosome', db_column='ID_CHROMOSOME')
    strand = CharField(max_length=1, db_column='STRAND')
    alignStart = IntegerField(db_column='ALIGN_START')
    alignEnd = IntegerField(db_column='ALIGN_END')
    targetSequence = ForeignKey('TargetSequence', db_column='ID_TARGET_SEQ')
    gene = ForeignKey('Gene', blank=True, null=True, db_column='ID_GENE')
    class Meta:
        db_table='TARGET_SEQ_ALIGNMENT'

class TargetSequenceAlignmentCombo(Model):
    name = CharField(max_length=128, db_column='NAME')
    length = BigIntegerField(null=True, blank=True, db_column='LENGTH')
    class Meta:
        db_table='TARGET_SEQ_ALIGN_COMBO'

class TargetSequenceAlignmentCombo_has_TargetSequenceAlignment(Model):
    target_seq_align_combo = ForeignKey('TargetSequenceAlignmentCombo', db_column='ID_TARGET_SEQ_ALIGN_COMBO')
    target_seq_align = ForeignKey('TargetSequenceAlignment', db_column='ID_TARGET_SEQ_ALIGN')
    class Meta:
        db_table='TARGET_SEQ_ALIGN_COMBO_HAS_TARGET_SEQ_ALIGN'
        unique_together = ('target_seq_align_combo', 'target_seq_align')

class Census(Model):
    id_census = AutoField(primary_key=True, db_column='ID_CENSUS')
    id_gene = ForeignKey('Gene', db_column='ID_GENE', blank=True, null=True)
    gene_name = CharField(max_length=200, db_column='GENE_NAME', null=True, blank=True)
    full_name = CharField(max_length=300, db_column='FULL_NAME', null=True, blank=True)
    entrez_gene_id = BigIntegerField(db_column='ENTREZ_GENE_ID', null=True, blank=True)
    chromosome = CharField(max_length=10, db_column='CHROMOSOME', null=True, blank=True)
    chrom_band = CharField(max_length=20, db_column='CHROM_BAND', null=True, blank=True)
    somatic_mut = CharField(max_length=3, db_column='SOMATIC_MUT', null=True, blank=True)
    germline_mut = CharField(max_length=3, db_column='GERMLINE_MUT', null=True, blank=True)
    tumour_somatic = CharField(max_length=300, db_column='TUMOUR_SOMATIC', null=True, blank=True)
    tumour_germline = CharField(max_length=300, db_column='TUMOUR_GERMLINE', null=True, blank=True)
    cancer_syndrome = CharField(max_length=300, db_column='CANCER_SYNDROME', null=True, blank=True)
    tissue_type = CharField(max_length=50, db_column='TISSUE_TYPE', null=True, blank=True)
    cancer_mol_gen = CharField(max_length=50, db_column='CANCER_MOL_GEN', null=True, blank=True)
    mutation_type = CharField(max_length=100, db_column='MUTATION_TYPE', null=True, blank=True)
    translocation_partner = CharField(max_length=300, db_column='TRANSLOCATION_PARTNER', null=True, blank=True)
    other_germline_mut = CharField(max_length=5, db_column='OTHER_GERMLINE_MUT', null=True, blank=True)
    other_syndrome = CharField(max_length=300, db_column='OTHER_SYNDROME', null=True, blank=True)
    in_translocation = CharField(max_length=2, db_column='IN_TRANSLOCATION', null=True, blank=True)
    in_missense = CharField(max_length=2, db_column='IN_MISSENSE', null=True, blank=True)
    in_nonsense = CharField(max_length=2, db_column='IN_NONSENSE', null=True, blank=True)
    in_amplification = CharField(max_length=2, db_column='IN_AMPLIFICATION', null=True, blank=True)
    in_deletion = CharField(max_length=2, db_column='IN_DELETION', null=True, blank=True)
    in_frame = CharField(max_length=2, db_column='IN_FRAME', null=True, blank=True)
    in_splice = CharField(max_length=2, db_column='IN_SPLICE', null=True, blank=True)
    in_other = CharField(max_length=2, db_column='IN_OTHER', null=True, blank=True)
    class Meta:
        db_table='CENSUS'

class Exon(Model):
    id_exon = AutoField(primary_key=True, db_column='ID_EXON')
    parent_sequence = TextField(db_column='PARENT_SEQUENCE')
    exon_start = IntegerField(db_column='EXON_START', null=True, blank=True)
    exon_stop = IntegerField(db_column='EXON_STOP', null=True, blank=True)
    cds_start = IntegerField(db_column='CDS_START', null=True, blank=True)
    cds_stop = IntegerField(db_column='CDS_STOP', null=True, blank=True)
    cosmic_exon_id = IntegerField(db_column='COSMIC_EXON_ID', null=True, blank=True)
    class Meta:
        db_table='EXON'

class GeneAlias(Model):
    id_alias = IntegerField(primary_key=True,db_column='ID_ALIAS')
    id_gene = ForeignKey('Gene',db_column='ID_GENE')
    gene_synonym = CharField(max_length=240,db_column='GENE_SYNONYM')
    id_annot_gene_name_type = ForeignKey('GeneAliasType',db_column='ID_ANNOT_GENE_NAME_TYPE', null=True, blank=True)
    class Meta:
        db_table='GENE_ALIAS'
        unique_together = ("id_gene", "gene_synonym", "id_annot_gene_name_type")

class GeneAliasType(Model):
    id_annot_gene_name_type = AutoField(primary_key=True,db_column='ID_ANNOT_GENE_NAME_TYPE')
    description = CharField(max_length=50,db_column='DESCRIPTION', null=True, blank=True)
    url = CharField(max_length=500,db_column='URL', null=True, blank=True)
    class Meta:
        db_table='GENE_ALIAS_TYPE_DICT'
        
class GeneRelationshipSpecification(Model):
    gene_rel_spec_id = AutoField(primary_key=True,db_column='GENE_REL_SPEC_ID')
    description = CharField(max_length=128,db_column='DESCRIPTION')
    class Meta:
        db_table='GENE_REL_SPEC'

class Gene(Model):
    id_gene = AutoField(primary_key=True,db_column='ID_GENE')
    gene_name = CharField(max_length=240,db_column='GENE_NAME',unique=True)
    chromosome = IntegerField(db_column='CHROMOSOME')
    chrom_arm = CharField(max_length=1,db_column='CHROM_ARM')
    chrom_band = CharField(max_length=6,db_column='CHROM_BAND')
    ensembl_genome_start = IntegerField(db_column='ENSEMBL_GENOME_START', null=True, blank=True)
    ensembl_genome_stop = IntegerField(db_column='ENSEMBL_GENOME_STOP', null=True, blank=True)
    narrative = TextField(db_column='NARRATIVE')
    is_mutated = CharField(max_length=1,db_column='IS_MUTATED')
    census_name = CharField(max_length=240,db_column='CENSUS_NAME', null=True, blank=True)
    in_census = CharField(max_length=1,db_column='IN_CENSUS')
    id_ref_transcript = ForeignKey('Transcript',db_column='ID_REF_TRANSCRIPT',unique=True, null=True, blank=True)
    cosmic_gene_id = IntegerField(db_column='COSMIC_GENE_ID',unique=True, null=True, blank=True)
    class Meta:
        db_table='GENE_SOM'

class MutationType(Model):
    id_mut_type = AutoField(primary_key=True, db_column='ID_MUT_TYPE')
    description = CharField(max_length=240, db_column='DESCRIPTION')
    ontology_evidence_code = CharField(max_length=50, db_column='ONTOLOGY_EVIDENCE_CODE')
    ontology_mutation_code = CharField(max_length=50, db_column='ONTOLOGY_MUTATION_CODE')
    ontology_mutation_desc = CharField(max_length=100, db_column='ONTOLOGY_MUTATION_DESC')
    ontology_evidence_desc = CharField(max_length=100, db_column='ONTOLOGY_EVIDENCE_DESC')
    class Meta:
        db_table='MUT_TYPE_DICT'
   
class Mutation(Model):
    id_mutation = AutoField(primary_key=True,db_column='ID_MUTATION')
    id_transcript = ForeignKey('Transcript',db_column='ID_TRANSCRIPT')
    gene_rel_spec_id = ForeignKey('GeneRelationshipSpecification',db_column='GENE_REL_SPEC_ID')
    id_mut_type = ForeignKey('MutationType', db_column='ID_MUT_TYPE', null=True, blank=True)
    aa_mut_start = IntegerField(db_column='AA_MUT_START', null=True, blank=True)
    aa_mut_stop = IntegerField(db_column='AA_MUT_STOP', null=True, blank=True)
    aa_mut_length = IntegerField(db_column='AA_MUT_LENGTH', null=True, blank=True)
    exon_mut_start = IntegerField(db_column='EXON_MUT_START', null=True, blank=True)
    exon_mut_stop = IntegerField(db_column='EXON_MUT_STOP', null=True, blank=True)
    exon_mut_length = IntegerField(db_column='EXON_MUT_LENGTH', null=True, blank=True)
    start_exon = ForeignKey('Exon', related_name='start_exon_set', db_column='START_EXON', null=True, blank=True)
    stop_exon = ForeignKey('Exon', related_name='stop_exon_set', db_column='STOP_EXON', null=True, blank=True)
    cds_mut_start = IntegerField(db_column='CDS_MUT_START', null=True, blank=True)
    cds_mut_stop = IntegerField(db_column='CDS_MUT_STOP', null=True, blank=True)
    cds_mut_length = IntegerField(db_column='CDS_MUT_LENGTH', null=True, blank=True)
    genome_mut_start = IntegerField(db_column='GENOME_MUT_START', null=True, blank=True)
    genome_mut_stop = IntegerField(db_column='GENOME_MUT_STOP', null=True, blank=True)
    remark = CharField(max_length=4000,db_column='REMARK', null=True, blank=True)
    aa_mut_allele_seq = TextField(db_column='AA_MUT_ALLELE_SEQ', null=True, blank=True)
    aa_wt_allele_seq = TextField(db_column='AA_WT_ALLELE_SEQ', null=True, blank=True)
    cds_mut_allele_seq = TextField(db_column='CDS_MUT_ALLELE_SEQ', null=True, blank=True)
    cds_wt_allele_seq = TextField(db_column='CDS_WT_ALLELE_SEQ', null=True, blank=True)
    genomic_mut_allele_seq = TextField(db_column='GENOMIC_MUT_ALLELE_SEQ', null=True, blank=True)
    genomic_wt_allele_seq = TextField(db_column='GENOMIC_WT_ALLELE_SEQ', null=True, blank=True)
    id_mut_type_aa = IntegerField(db_column='ID_MUT_TYPE_AA', null=True, blank=True)
    id_mut_status_consequence = IntegerField(db_column='ID_MUT_STATUS_CONSEQUENCE', null=True, blank=True)
    cds_mut_syntax = CharField(max_length=300,db_column='CDS_MUT_SYNTAX', null=True, blank=True)
    aa_mut_syntax = CharField(max_length=200,db_column='AA_MUT_SYNTAX', null=True, blank=True)
    narrative = TextField(db_column='NARRATIVE', null=True, blank=True)
    id_mut_type_spec = IntegerField(db_column='ID_MUT_TYPE_SPEC', null=True, blank=True)
    sub_change = CharField(max_length=100,db_column='SUB_CHANGE', null=True, blank=True)
    iarc_p53_url_link = CharField(max_length=100,db_column='IARC_P53_URL_LINK', null=True, blank=True)
    present_in_1000_genomes = CharField(max_length=1,db_column='PRESENT_IN_1000_GENOMES', null=True, blank=True)
    frequency_in_studies = IntegerField(db_column='FREQUENCY_IN_STUDIES', null=True, blank=True)
    cosmic_mut_id = IntegerField(db_column='COSMIC_MUT_ID', null=True, blank=True)
    class Meta:
        db_table='SEQUENCE_MUTATION'

class Transcript(Model):
    id_transcript = AutoField(primary_key=True,db_column='ID_TRANSCRIPT')
    id_gene = ForeignKey('Gene',db_column='ID_GENE')
    accession_number = CharField(max_length=50,db_column='ACCESSION_NUMBER', null=True, blank=True)
    is_reference = CharField(max_length=1,db_column='IS_REFERENCE')
    remark = CharField(max_length=4000,db_column='REMARK', null=True, blank=True)
    genomic_cds_build = TextField(db_column='GENOMIC_CDS_BUILD', null=True, blank=True)
    genomic_aa_build = TextField(db_column='GENOMIC_AA_BUILD', null=True, blank=True)
    transcript_cdna_seq = TextField(db_column='TRANSCRIPT_CDNA_SEQ', null=True, blank=True)
    transcript_aa_seq = TextField(db_column='TRANSCRIPT_AA_SEQ', null=True, blank=True)
    cdna_seq_equals_genomic_cds = CharField(max_length=1,db_column='CDNA_SEQ_EQUALS_GENOMIC_CDS', null=True, blank=True)
    ccds_accession = CharField(max_length=20,db_column='CCDS_ACCESSION', null=True, blank=True)
    cosmic_trans_id = IntegerField(db_column='COSMIC_TRANS_ID', null=True, blank=True)
    class Meta:
        db_table='TRANSCRIPT'

class TranscriptExon(Model):
    id_te = AutoField(primary_key=True, db_column='ID_TE')
    id_transcript = ForeignKey('Transcript', db_column='ID_TRANSCRIPT')
    id_exon = ForeignKey('Exon', db_column='ID_EXON')
    exon_number = IntegerField(db_column='EXON_NUMBER')
    exon_cds_start = IntegerField(db_column='EXON_CDS_START')
    exon_cds_stop = IntegerField(db_column='EXON_CDS_STOP')
    consecutive_exon_number = IntegerField(db_column='CONSECUTIVE_EXON_NUMBER')
    class Meta:
        db_table='TRANSCRIPT_EXONS'
        unique_together = ('id_transcript', 'id_exon')

class UCSCrefFlat(Model):
    geneName = CharField(max_length=765, db_column='geneName') # Field name made lowercase.
    name = CharField(max_length=765)
    chrom = CharField(max_length=765)
    strand = CharField(max_length=3)
    txStart = IntegerField(db_column='txStart') # Field name made lowercase.
    txEnd = IntegerField(db_column='txEnd') # Field name made lowercase.
    cdsStart = IntegerField(db_column='cdsStart') # Field name made lowercase.
    cdsEnd = IntegerField(db_column='cdsEnd') # Field name made lowercase.
    exonCount = IntegerField(db_column='exonCount') # Field name made lowercase.
    exonStarts = TextField(db_column='exonStarts') # Field name made lowercase.
    exonEnds = TextField(db_column='exonEnds') # Field name made lowercase.
    class Meta:
        db_table = u'refFlat'

class Variation(Model):
    variation_id = IntegerField(primary_key=True)
    source_id = IntegerField()
    name = CharField(max_length=255, unique=True, blank=True)
    validation_status = CharField(max_length=255, blank=True)
    ancestral_allele = CharField(max_length=50, blank=True)
    flipped = IntegerField(null=True, blank=True)
    class_attrib_id = IntegerField(null=True, blank=True)
    somatic = IntegerField()
    minor_allele = CharField(max_length=3, blank=True)
    minor_allele_freq = FloatField(null=True, blank=True)
    minor_allele_count = IntegerField(null=True, blank=True)
    clinical_significance_attrib_id = IntegerField(null=True, blank=True)
    class Meta:
        db_table = u'variation'
