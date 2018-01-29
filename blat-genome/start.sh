#!/bin/sh

# This script will start the gfServer instance
echo "Starting blat server genome"
cd /blat/seq/
/blat/bin/gfServer -stepSize=3 start 0.0.0.0 11515 GRCh37.p13.chrom.2bit