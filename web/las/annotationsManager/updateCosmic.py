import cx_Oracle
odb=cx_Oracle.connect('cosmic66/cosmic66@127.0.0.1/xe')
ocur=odb.cursor()

import MySQLdb
mdb=MySQLdb.connect(user="annotusr",passwd="annotpwd2013",db="lasannotations")
mcur=mdb.cursor()

########## (1) table: GENE_SOM ##########

list_census = []
cnt1=0
cnt2=0

cnt3=0

print "Updating GENE_SOM. . ."

#update existing genes by setting/unsetting link to cosmic
mcur.execute("select * from GENE_SOM")
ocur.prepare('select ID_GENE from GENE_SOM where CHROMOSOME=:chr and GENE_NAME=:gene')
for x in mcur:
    ocur.execute(None, {'chr': x[2], 'gene': x[1]})
    y = ocur.fetchone()
    if y:
        if x[12] != y[0]:
            cnt1 += 1
            cnt3 += 1
            mcur.execute("update GENE_SOM set COSMIC_GENE_ID=%s where ID_GENE=%s", (y[0], x[0]))
    else:
        if x[12]:
            mcur.execute("update GENE_SOM set COSMIC_GENE_ID=null where ID_GENE=%s", x[0])
            mcur.execute("update TRANSCRIPT set COSMIC_TRANS_ID=null where ID_GENE=%s", x[0])
            cnt1 += 1
            cnt3 += 1
    
    if cnt3 == 2000:
        mcur.execute('commit')
        cnt3 = 0

        
#insert new cosmic genes
ocur.execute("select * from GENE_SOM")
for x in ocur:
    if mcur.execute("select ID_GENE from GENE_SOM where COSMIC_GENE_ID=%s", x[0]) == 0:
        if mcur.execute("insert ignore into GENE_SOM (ID_GENE, GENE_NAME, CHROMOSOME, CHROM_ARM, CHROM_BAND, ENSEMBL_GENOME_START, ENSEMBL_GENOME_STOP, NARRATIVE, IS_MUTATED, CENSUS_NAME, IN_CENSUS, COSMIC_GENE_ID) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                                           (x[0],    x[1],      x[2],       x[3],      x[4],       x[6],                 x[7],                x[11],     x[14],      x[15],       x[9],      x[0])) == 0:
            mcur.execute("insert into GENE_SOM (GENE_NAME, CHROMOSOME, CHROM_ARM, CHROM_BAND, ENSEMBL_GENOME_START, ENSEMBL_GENOME_STOP, NARRATIVE, IS_MUTATED, CENSUS_NAME, IN_CENSUS, COSMIC_GENE_ID) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                                               (x[1],      x[2],       x[3],      x[4],       x[6],                 x[7],                x[11],     x[14],      x[15],       x[9],      x[0]))
        if x[9] == 'y':
            list_census.append(x)
        cnt2 += 1
        cnt3 += 1
        if cnt3 == 2000:
            mcur.execute('commit')
            cnt3 = 0


mcur.execute('commit')
print "%d row(s) updated, %d new row(s) inserted" % (cnt1, cnt2)


########## (2) table: CENSUS ##########

print "Updating CENSUS. . ."

cnt=0
ocur.execute("select * from CENSUS")
for x in ocur:
    if mcur.execute("select ID_CENSUS from CENSUS where ID_CENSUS=%s", x[0]) == 0:
        mcur.execute("insert into CENSUS (ID_CENSUS, ID_GENE, GENE_NAME, FULL_NAME, ENTREZ_GENE_ID, CHROMOSOME,CHROM_BAND, SOMATIC_MUT, GERMLINE_MUT, TUMOUR_SOMATIC, TUMOUR_GERMLINE, CANCER_SYNDROME, TISSUE_TYPE, CANCER_MOL_GEN, MUTATION_TYPE, TRANSLOCATION_PARTNER, OTHER_GERMLINE_MUT, OTHER_SYNDROME, IN_TRANSLOCATION, IN_MISSENSE, IN_NONSENSE, IN_AMPLIFICATION, IN_DELETION, IN_FRAME, IN_SPLICE, IN_OTHER) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)", x)
        cnt += 1
mcur.execute('commit')
print "%d new row(s) inserted" % cnt


########## (3) table: TRANSCRIPT ##########

print "Updating TRANSCRIPT. . ."

cnt=0
cnt1=0
ocur1 = odb.cursor()
ocur2 = odb.cursor()
mcur1 = mdb.cursor()
ocur1.prepare('select * from EXON where ID_EXON in (SELECT ID_EXON from TRANSCRIPT_EXONS where ID_TRANSCRIPT=:trans_id)')
ocur2.prepare('select * from TRANSCRIPT_EXONS where ID_TRANSCRIPT=:trans_id')
ocur.execute("select * from TRANSCRIPT")
exon_ids = {}
for x in ocur:
    mcur1.execute("select ID_GENE from GENE_SOM where COSMIC_GENE_ID=%s", x[1])
    gene_id = mcur1.fetchone()[0]
    if mcur.execute("select ID_TRANSCRIPT from TRANSCRIPT where COSMIC_TRANS_ID=%s", x[0]) == 0:
        if mcur.execute("insert ignore into TRANSCRIPT (ID_TRANSCRIPT, ID_GENE, ACCESSION_NUMBER, IS_REFERENCE, REMARK, GENOMIC_CDS_BUILD, GENOMIC_AA_BUILD, TRANSCRIPT_CDNA_SEQ, TRANSCRIPT_AA_SEQ, CDNA_SEQ_EQUALS_GENOMIC_CDS, CCDS_ACCESSION, COSMIC_TRANS_ID) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)", (x[0],gene_id)+x[2:]+(x[0],)) == 0:
            mcur.execute("insert into TRANSCRIPT (ID_GENE, ACCESSION_NUMBER, IS_REFERENCE, REMARK, GENOMIC_CDS_BUILD, GENOMIC_AA_BUILD, TRANSCRIPT_CDNA_SEQ, TRANSCRIPT_AA_SEQ, CDNA_SEQ_EQUALS_GENOMIC_CDS, CCDS_ACCESSION, COSMIC_TRANS_ID) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)", x[1:]+(x[0],))
        trans_id = mcur.lastrowid
        mcur.execute("update GENE_SOM set ID_REF_TRANSCRIPT='%s' where ID_GENE=%s and ID_REF_TRANSCRIPT is NULL", (trans_id, x[1]))
        cnt += 1
        cnt1 += 1
        #faccio una query preparata su ocur1 per recuperare i dati degli esoni del trascritto
        ocur1.execute(None, {'trans_id': x[0]})
        for y in ocur1:
            if y[0] not in exon_ids.keys():
                if mcur.execute("insert ignore into EXON(ID_EXON, PARENT_SEQUENCE, EXON_START, EXON_STOP, CDS_START, CDS_STOP, COSMIC_EXON_ID) VALUES(%s,%s,%s,%s,%s,%s,%s)", y+(y[0],)) == 0:
                    mcur.execute("insert into EXON(PARENT_SEQUENCE, EXON_START, EXON_STOP, CDS_START, CDS_STOP, COSMIC_EXON_ID) VALUES(%s,%s,%s,%s,%s,%s)", y[1:]+(y[0],))
                cnt1 += 1
                exon_ids[y[0]] = mcur.lastrowid
        #e poi una query preparata su ocur2 per recuperare la relazione trascritto-esoni
        ocur2.execute(None, {'trans_id': x[0]})
        for y in ocur2:
            mcur.execute("insert into TRANSCRIPT_EXONS(ID_TRANSCRIPT, ID_EXON, EXON_NUMBER, EXON_CDS_START, EXON_CDS_STOP, CONSECUTIVE_EXON_NUMBER) VALUES(%s,%s,%s,%s,%s,%s)", (trans_id,exon_ids[y[1]],y[2],y[3],y[4],y[5]))
            cnt1 += 1

    if cnt1 >= 2000:
        mcur.execute('commit')
        cnt1 = 0

mcur.execute('commit')
ocur1.close()
ocur2.close()
print "%d new row(s) inserted" % cnt

print "Updating stray exons in EXON. . ."
cnt=0
ocur.execute("select * from EXON")
for x in ocur:
    if mcur.execute("select ID_EXON from EXON where COSMIC_EXON_ID=%s", x[0]) == 0:
        if mcur.execute("insert ignore into EXON(ID_EXON, PARENT_SEQUENCE, EXON_START, EXON_STOP, CDS_START, CDS_STOP, COSMIC_EXON_ID) VALUES(%s,%s,%s,%s,%s,%s,%s)", x+(x[0],)) == 0:
            mcur.execute("insert into EXON(PARENT_SEQUENCE, EXON_START, EXON_STOP, CDS_START, CDS_STOP, COSMIC_EXON_ID) VALUES(%s,%s,%s,%s,%s,%s)", x[1:]+(x[0],))
        cnt += 1
print "%d new row(s) inserted" % cnt

########## (4) table: GENE_ALIAS ##########

print "Updating GENE_ALIAS. . ."

cnt=0
cnt1=0
ocur.execute("SELECT DISTINCT ID_GENE, LOWER(gene_synonym), id_annot_gene_name_type FROM GENE_ALIAS WHERE GENE_SYNONYM IS NOT NULL AND ID_GENE IN (SELECT ID_GENE FROM GENE_SOM) ORDER BY ID_GENE")
cosmic_id_gene = None
for x in ocur:
    if x[0] != cosmic_id_gene:
        mcur.execute("select ID_GENE from GENE_SOM where COSMIC_GENE_ID=%s", x[0])
        cosmic_id_gene = x[0]
        try:
            id_gene = mcur.fetchone()[0]
        except: #gene with given id is not in GENE_SOM - it should not occur
            continue
    r = mcur.execute("insert ignore into GENE_ALIAS (ID_GENE, GENE_SYNONYM, ID_ANNOT_GENE_NAME_TYPE) VALUES(%s, %s, %s)", (id_gene,x[1],x[2]))
    cnt += r
    cnt1 += r
    if cnt1 == 2000:
        mcur.execute('commit')
        cnt1 = 0

mcur.execute('commit')
print "%d new row(s) inserted" % cnt


########## (5) table: MUT_TYPE_DICT ##########
cnt=0
print "Updating MUT_TYPE_DICT. . ."
ocur.execute("SELECT * FROM MUT_TYPE_DICT")
for x in ocur:
    cnt += mcur.execute("insert ignore into MUT_TYPE_DICT (ID_MUT_TYPE, DESCRIPTION, ONTOLOGY_EVIDENCE_CODE, ONTOLOGY_MUTATION_CODE, ONTOLOGY_MUTATION_DESC, ONTOLOGY_EVIDENCE_DESC)"
                +" VALUES(%s,%s,%s,%s,%s,%s)", x)
                
mcur.execute("commit")
print "%d new row(s) inserted" % cnt


########## (6) table: SEQUENCE_MUTATION ##########

print "Updating SEQUENCE_MUTATION. . ."


# remove cosmic ID from mutations that are no longer in cosmic
cnt=0
mcur1 = mdb.cursor()
mcur.execute("select ID_MUTATION,COSMIC_MUT_ID from SEQUENCE_MUTATION where COSMIC_MUT_ID is not null")
ocur.prepare('select ID_MUTATION from SEQUENCE_MUTATION where ID_MUTATION=:id_mut')
for x in mcur:
    ocur.execute(None, {'id_mut': x[1]})
    y = ocur.fetchone()
    if not y:
        mcur1.execute("update SEQUENCE_MUTATION set COSMIC_MUT_ID=null where ID_MUTATION=%s", x[0])
        cnt += 1

print "%d row(s) updated (CosmicID removed)" % cnt        

cnt=0
cnt1=0
g=1
ocur.execute("SELECT * FROM SEQUENCE_MUTATION")

ocur2 = odb.cursor()
ocur2.prepare("select count(*) from SEQUENCE_MUTATION, GENE_SAMPLE_MUTATION where sequence_mutation.id_mutation=gene_sample_mutation.id_mutation and sequence_mutation.id_mutation=:id_mut")
for x in ocur:
    if mcur.execute("select COSMIC_MUT_ID from SEQUENCE_MUTATION where COSMIC_MUT_ID=%s", x[0]) == 0:
        mcur1.execute('select ID_TRANSCRIPT from TRANSCRIPT where COSMIC_TRANS_ID=%s', x[1])
        trans_id = mcur1.fetchone()[0]
        if x[9]:
            mcur1.execute("select ID_EXON from EXON where COSMIC_EXON_ID=%s", x[9])
            start_exon = mcur1.fetchone()[0]
        else:
            start_exon = None
        if x[10]:
            mcur1.execute("select ID_EXON from EXON where COSMIC_EXON_ID=%s", x[10])
            stop_exon = mcur1.fetchone()[0]
        else:
            stop_exon = None
        ocur2.execute(None, {'id_mut': x[0]})
        f = ocur2.fetchone()[0]
        if mcur.execute("insert ignore into SEQUENCE_MUTATION(ID_MUTATION, ID_TRANSCRIPT, ID_MUT_TYPE, AA_MUT_START, AA_MUT_STOP,"
                        +"AA_MUT_LENGTH, EXON_MUT_START, EXON_MUT_STOP, EXON_MUT_LENGTH, START_EXON, STOP_EXON, CDS_MUT_START,"
                        +" CDS_MUT_STOP, CDS_MUT_LENGTH, REMARK, AA_MUT_ALLELE_SEQ, AA_WT_ALLELE_SEQ, CDS_MUT_ALLELE_SEQ,"
                        +" CDS_WT_ALLELE_SEQ, GENOMIC_MUT_ALLELE_SEQ, GENOMIC_WT_ALLELE_SEQ, ID_MUT_TYPE_AA, ID_MUT_STATUS_CONSEQUENCE,"
                        +" CDS_MUT_SYNTAX, AA_MUT_SYNTAX, NARRATIVE, ID_MUT_TYPE_SPEC, SUB_CHANGE, IARC_P53_URL_LINK,"
                        +" PRESENT_IN_1000_GENOMES, GENOME_MUT_START, GENOME_MUT_STOP, FREQUENCY_IN_STUDIES, GENE_REL_SPEC_ID, COSMIC_MUT_ID)"
                        +" VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                        (x[0],trans_id)+x[2:9]+(start_exon,stop_exon)+x[11:]+(None, None, f, g, x[0])) == 0:
            mcur.execute("insert into SEQUENCE_MUTATION(ID_TRANSCRIPT, ID_MUT_TYPE, AA_MUT_START, AA_MUT_STOP,"
                        +"AA_MUT_LENGTH, EXON_MUT_START, EXON_MUT_STOP, EXON_MUT_LENGTH, START_EXON, STOP_EXON, CDS_MUT_START,"
                        +" CDS_MUT_STOP, CDS_MUT_LENGTH, REMARK, AA_MUT_ALLELE_SEQ, AA_WT_ALLELE_SEQ, CDS_MUT_ALLELE_SEQ,"
                        +" CDS_WT_ALLELE_SEQ, GENOMIC_MUT_ALLELE_SEQ, GENOMIC_WT_ALLELE_SEQ, ID_MUT_TYPE_AA, ID_MUT_STATUS_CONSEQUENCE,"
                        +" CDS_MUT_SYNTAX, AA_MUT_SYNTAX, NARRATIVE, ID_MUT_TYPE_SPEC, SUB_CHANGE, IARC_P53_URL_LINK,"
                        +" PRESENT_IN_1000_GENOMES, GENOME_MUT_START, GENOME_MUT_STOP, FREQUENCY_IN_STUDIES, GENE_REL_SPEC_ID, COSMIC_MUT_ID)"
                        +" VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,)",
                        (x[0],trans_id)+x[2:9]+(start_exon,stop_exon)+x[11:]+(None, None, f, g, x[0]))
        cnt += 1
        cnt1 += 1
        if cnt1 == 2000:
            mcur.execute('commit')
            cnt1 = 0
          
mcur.execute('commit')
ocur2.close()
mcur1.close()
print "%d new row(s) inserted" % cnt

ocur.close()
mcur.close()

