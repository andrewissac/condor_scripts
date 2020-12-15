#!/bin/bash

echo "### Begin of job"

set -e

echo "Arguments:" $@

ID=$1
ROOTFILE=$2
DATASET=$3

echo "Job ID:" $ID
echo "Hostname:" `hostname`
echo "Who am I?" `id`
echo "Where am I?" `pwd`
echo "What is my system?" `uname -a`
echo "### Start working"

# Create output directory (if it's not there)
OUTPUTDIR=/ceph/aissac/condor_example/output_$DATASET/
mkdir -p $OUTPUTDIR

# Do something
OUTPUTFILE=output_$ID.txt
echo $@ > $OUTPUTFILE
mv $OUTPUTFILE $OUTPUTDIR/$OUTPUTFILE

export X509_USER_PROXY=/home/aissac/.globus/x509up
export VO_CMS_SW_DIR=/cvmfs/cms.cern.ch
source $VO_CMS_SW_DIR/cmsset_default.sh
cd /work/aissac/TauAnalyzer/CMSSW_10_2_18/src
echo $PWD
eval $(scram runtime -sh)
cd -
cmsRun /work/aissac/TauAnalyzer/CMSSW_10_2_18/src/Tau/TauAnalyzer/python/ConfFile_cfg.py $ID $ROOTFILE $DATASET $OUTPUTDIR

echo "### End of job"
