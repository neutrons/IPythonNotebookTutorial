#!/usr/bin/env python

# ./batch_red2.py 114565-114567,114580 .

import sys, os, subprocess as sp
# add Mantid to python path
sys.path.append("/opt/Mantid/bin")
# get mantid
import mantid

# path to autoreduce script
arscript = "/SNS/SEQ/IPTS-16076/shared/autoreduce/reduce_SEQ_2016.11.22_11.25.28.py"

# path to autoreduce library
seq_ar_path = "/SNS/SEQ/shared/autoreduce"

def batch_red(runs, outputdir):
    # tool to get experimental run file path
    alg = mantid.api.AlgorithmManager.createUnmanaged("Load")
    alg.initialize()
    # iterate over runs
    for r in runs:
        alg.setPropertyValue('Filename',"SEQ_{}".format(r))
        filename=alg.getProperty('Filename').value[0]
        print "* Processing {!r}".format(filename)
        cmd="python {} {} {}/".format(arscript, filename, outputdir)
        print "* Running {!r}".format(cmd)
        try:
            sp.check_call(cmd, shell=True, env=dict(PYTHONPATH=seq_ar_path))
        except sp.CalledProcessError as exc:
            print ("** Failed with code {}\n".format(exc.returncode,))
        break
    return

def str2runs(x):
    result = []
    for part in x.split(','):
        if '-' in part:
            a, b = part.split('-')
            a, b = int(a), int(b)
            result.extend(range(a, b + 1))
        else:
            a = int(part)
            result.append(a)
    return result


runs = str2runs(sys.argv[1])
print runs
outputdir= os.path.abspath(os.path.expanduser(sys.argv[2]))

# create output dir if needed
if not os.path.exists(outputdir):
    os.makedirs(outputdir)

# run
batch_red(runs, outputdir)
