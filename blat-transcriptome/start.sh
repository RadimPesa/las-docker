#!/bin/sh

# This script will start the gfServer instance
echo "Starting blat server transcriptome"
cd /blat/seq/
/blat/bin/gfServer -stepSize=3 start 0.0.0.0 11516 gencode.v19.pc_transcripts.simple.2bit
