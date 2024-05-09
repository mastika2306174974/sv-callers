#!/usr/bin/env python

# for tgi cluster:
#/gapp/x64linux/opt/pythonbrew/venvs/Python-2.7.6/gemini/bin/python
# for uva cluster:

import pysam
import sys
import argparse
from argparse import RawTextHelpFormatter
import string
from string import *

__author__ = "Ira Hall (ihall@genome.wustl.edu) and Colby Chiang (cc2qe@virginia.edu)"
__version__ = "$Revision: 0.0.1 $"
__date__ = "$Date: 2014-09-04 14:31 $"

def bamtofastq(bamlist, is_sam, readgroup, rename, header):
    for bamfile in bamlist:
        # get file and header
        if bamfile == None: 
            if is_sam:
                bam = pysam.Samfile("-", "r", check_sq=False)
            else:
                bam = pysam.Samfile('-', 'rb', check_sq=False)
        else:
            if is_sam:
                bam = pysam.Samfile(bamfile, 'r', check_sq=False)
            else:
                bam = pysam.Samfile(bamfile, "rb", check_sq=False)
        # parse readgroup string
        try:
            rg_list = readgroup.split(',')
        except AttributeError:
            rg_list = None

        d = {}
        counter = 0
        header_written = False

        for al in bam:
            # print the header to file if requested
            if (header is not None
                and not header_written):
                header.write(bam.text)
                header.close()
                header_written = True

            # must be primary read alignment
            if (al.is_secondary):
                continue

            # skip unpaired reads
            if (not al.is_paired):
                continue

            # must be in a user specified readgroup
            if rg_list and al.opt('RG') not in rg_list:
                continue

            # ensures the read is not hard-clipped. important
            # when the BAM doesn't have shorter hits flagged as
            # secondary
            if 5 in [x[0] for x in al.cigar]:
                continue

            # add read name to dictionary if not already there
            key = al.qname
            if key not in d:
                d.setdefault(key,al)
            # print matched read pairs
            else:
                # RG:Z:ID
                RG1 = d[key].opt('RG')
                RG2 = al.opt('RG')

                counter += 1
                if rename:
                    al.qname = RG2 + '.' + str(counter)
                    d[key].qname = RG1 + '.' + str(counter)

                if al.is_read1:
                    printfastq_rg(al,1,RG2)
                    printfastq_rg(d[key],2,RG1)
                else:
                    printfastq_rg(d[key],1,RG1)
                    printfastq_rg(al,2,RG2)
                del d[key]
        if len(d) != 0:
            sys.stderr.write('Warning: %s unmatched name groups\n' % len(d))

#===================================================================================================================================================
# functions
#===================================================================================================================================================

def get_args():
    parser = argparse.ArgumentParser(formatter_class=RawTextHelpFormatter, description="\
bamtofastq.py\n\
author: " + __author__ + "\n\
version: " + __version__ + "\n\
description: Convert a coordinate sorted BAM file to FASTQ\n\
             (ignores unpaired reads)")
    # parser.add_argument('-i', '--input', metavar='BAM', required=False, help='Input BAM file')
    parser.add_argument('-r', '--readgroup', metavar='STR', default=None, required=False, help='Read group(s) to extract (comma separated)')
    parser.add_argument('-n', '--rename', required=False, action='store_true', help='Rename reads')
    parser.add_argument('-S', '--is_sam', required=False, action='store_true', help='Input is SAM format')
    parser.add_argument('-H', '--header', metavar='FILE', type=argparse.FileType('w'), default=None, required=False,
                        help='Write BAM header to file')
    parser.add_argument('input', metavar='BAM', nargs='*', type=str,
                        help='Input BAM file(s). If absent then defaults to stdin.')

    # parse the arguments
    args = parser.parse_args()

    # bail if no BAM file
    if len(args.input) == 0:
        if sys.stdin.isatty():
            parser.print_help()
            exit(1)
        else:
            args.input = [None]
    
    # send back the user input
    return args

def printfastq(al,read):
    if(al.is_reverse):
        print "@" + str(al.qname) + "/" + str(read) + "\n" + str(revcomp(al.seq)) + "\n" + "+" + "\n" + str(al.qual[::-1])
    else: 
        print "@" + str(al.qname) + "/" + str(read) + "\n" + str(al.seq) + "\n" + "+" + "\n" + str(al.qual)

def printfastq_rg(al,read, rg):
    if(al.is_reverse):
        print "@" + str(al.qname) + "/" + str(read) + " " + "RG:Z:" + str(rg) + "\n" + str(revcomp(al.seq)) + "\n" + "+" + "\n" + str(al.qual[::-1])
    else: 
        print "@" + str(al.qname) + "/" + str(read) + " " + "RG:Z:" + str(rg) + "\n" + str(al.seq) + "\n" + "+" + "\n" + str(al.qual)

def revcomp(seq):
    seq1 = seq.translate(maketrans("AGCTagct", "TCGAtcga"))
    seq2 = seq1[::-1]
    return seq2

#===================================================================================================================================================
# driver
#===================================================================================================================================================

class Usage(Exception):
    def __init__(self, msg):
        self.msg = msg

def main():
    args = get_args()

    bamtofastq(args.input,
               args.is_sam,
               args.readgroup,
               args.rename,
               args.header)

if __name__ == "__main__":
    try:
        sys.exit(main())
    except IOError, e:
        if e.errno != 32:  # ignore SIGPIPE
            raise
    
# new features needed
# don't forget to select for primary alignments before using on bwa-mem files - DONE
# query memory usage to print out
# write output files based on library name
# include sample name as part of output file
# include sequencing center as part of output file
# stop opening and closing file the whole time - DONE
# close files at end
# add strict error checking ; need to catch all mistakes!!!!
# option for interleaved versus two fastq formats
# option for compressed versus uncompressed
# write out sequencing center - DONE
# need to make read-group based
# need to actually align output:
# need to have output directory prefix - default blank
