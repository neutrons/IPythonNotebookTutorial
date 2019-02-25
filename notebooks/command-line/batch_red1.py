#!/usr/bin/env python

import sys, os, subprocess as sp
# add Mantid to python path
sys.path.append("/opt/Mantid/bin")
# get mantid
import mantid

# runs to process
runs=range(114565, 114606+1) # last one not included

# it is preferred that the output directory is in a shared IPTS directory
# outputdir="/SNS/SEQ/IPTS-16076/shared/batchreduceRRM/"
# here for the demo purpose, we leave it in user's home dir
outputdir= os.path.expanduser("~/notebooks/IPythonNotebookTutorial-notebooks/command-line/out-batchreduction" )

# create output dir if needed
if not os.path.exists(outputdir):
    os.makedirs(outputdir)

# path to autoreduce script
arscript = "/SNS/SEQ/IPTS-16076/shared/autoreduce/reduce_SEQ_2016.11.22_11.25.28.py"

# path to autoreduce library
seq_ar_path = "/SNS/SEQ/shared/autoreduce"

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
    continue
