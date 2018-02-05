FASTA_FILE_NAME = 'gencode.v19.pc_transcripts.fa'

def loadRefSeqSequences():
    sequences = {}
    with open(FASTA_FILE_NAME, "r") as fin:
        seq = ''
        for line in fin:
            if line.startswith('>'):
                cnt += 1
                if len(seq) > 0:
                    sequences[tx_accession] = seq
                    seq = ''
                tx_accession = line[1:].split('|')[0]
            else:
                seq += line.strip()
        sequences[tx_accession] = seq
    return sequences
