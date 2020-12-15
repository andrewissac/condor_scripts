import os
import math
import shutil
import argparse

# ATTENTION:
# use python3 else math.floor/ceil will return floats and lead to problems on splitting datasets!

def floatsAreEqual(a: float, b: float):
    epsilon = 0.00001
    return True if abs(a - b) < epsilon else False

def mkdir(path):
    if not os.path.exists(path):
        os.mkdir(path)

def initJobDir(jobdir_):
    print("Initialized job directory by creating out, log, err folders in:\n", jobdir_)
    mkdir(os.path.join(jobdir_, "out"))
    mkdir(os.path.join(jobdir_, "log"))
    mkdir(os.path.join(jobdir_, "err"))

def stringIsNoneOrEmpty(s):
    return not bool(s and s.strip())

def writeJobFiles(outputdir: str, datamode: str):
    print("Writing job.sh file to job-{} directory.".format(datamode))
    with open(os.path.join(outputdir, "job.sh"), "w") as jsh:
        jsh.write(jobsh.format(OUTPUTDIR=outputdir))
    print("Writing job.jdl file to job-{} directory.".format(datamode))
    with open(os.path.join(outputdir, "job.jdl"), "w") as jobjdl:
        jobjdl.write(jdl.format(JOBSH="job.sh", ARGUMENTSTXT="arguments.txt"))

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    ORANGE = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def printHeadline(myStr):
    print(bcolors.OKGREEN + bcolors.BOLD + myStr + bcolors.ENDC)

def coloredPrint(myStr, bcolor):
    print(bcolor + myStr + bcolors.ENDC)

jdl = """universe = docker
docker_image = mschnepf/slc7-condocker
executable = {JOBSH}
output = out/$(cluster).$(Process).out
error = err/$(cluster).$(Process).err
log = log/$(cluster).$(Process).log
x509userproxy = /home/aissac/.globus/x509up
use_x509userproxy = true
Requirements = ( (Target.ProvidesIO == True) && (TARGET.ProvidesEKPResources == True ) )
+RequestWalltime = 1200
RequestMemory = 2000
RequestCpus = 1
max_retries = 3
accounting_group = cms
queue arguments from {ARGUMENTSTXT}"""

jobsh = """#!/bin/bash

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
OUTPUTDIR={OUTPUTDIR}/
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
"""


currentDirectory =os.getcwd()
parser = argparse.ArgumentParser()
parser.add_argument("--argumentstxt", required=True, type=str, help="Filepath of arguments.txt")
parser.add_argument("--jobsh", required=False, type=str, help="Filepath of job.sh - only interesting if no splits specified.")
parser.add_argument("--jobdir", required=False, type=str, default=currentDirectory, help="Job directory. Is set to be the current directory if not specified.")
parser.add_argument("--train", required=False, type=float, default=None, help="Specify train split (between 0.0-1.0).")
parser.add_argument("--test", required=False, type=float, default=None, help="Specify test split (between 0.0-1.0).")
parser.add_argument("--valid", required=False, type=float, default=None, help="Specify validation split (between 0.0-1.0).")
args = parser.parse_args()

trainSplit = 0.0 if args.train == None else args.train
testSplit = 0.0 if args.test == None else args.test
validSplit = 0.0 if args.valid == None else args.valid
sumSplits = trainSplit + testSplit + validSplit

printHeadline("###### BEGIN CREATING JOBS ######")

jobdir = args.jobdir
argumentsTXTList = []
if(jobdir == currentDirectory):
    with open(args.argumentstxt) as a:
        argumentsTXTList = a.readlines()
        datasetName = ""
        if len(argumentsTXTList) > 0:
            datasetName = argumentsTXTList[0].split(" ")[2].rstrip()
        jobdir = os.path.join(jobdir, "job" + datasetName)
        mkdir(jobdir)
        print("job directory: ")
        print(jobdir)
        print("Number of total jobs: ", len(argumentsTXTList))

# copy arguments.txt for debugging
print("Copying arguments.txt file to job directory.")
shutil.copy(args.argumentstxt, jobdir)

if floatsAreEqual(sumSplits, 0.0): # don't split dataset
    initJobDir(jobdir)
    if(not stringIsNoneOrEmpty(args.jobsh)):
        print("Copying job.sh file to job directory.")
        shutil.copy(args.jobsh, jobdir)
    else:
        print("Writing job.sh file to job directory.")
        with open(os.path.join(jobdir, "job.sh"), "w") as jsh:
            jsh.write(jobsh.format(OUTPUTDIR=jobdir, DATAMODE=""))

    print("Writing job.jdl file to job directory.")
    with open(os.path.join(jobdir, "job.jdl"), "w") as jobjdl:
        if not stringIsNoneOrEmpty(args.jobsh):
            jobjdl.write(jdl.format(JOBSH=args.jobsh, ARGUMENTSTXT=args.argumentstxt))
        else:
            jobjdl.write(jdl.format(JOBSH="job.sh", ARGUMENTSTXT=args.argumentstxt))

elif not floatsAreEqual(sumSplits,1.0):
    raise Exception("sum of train, test and validation splits must equal 1, but equals " + str(sumSplits))

else: # sum of splits == 1.0
    trainDir = os.path.join(jobdir, "train")
    testDir = os.path.join(jobdir, "test")
    validDir = os.path.join(jobdir, "valid")

    trainDatasetSize = 0 # number of rootfiles for training
    validDatasetSize = 0 # number of rootfiles for validation
    testDatasetSize = 0 # number of rootfiles for testing

    if trainSplit > 0.0:
        mkdir(trainDir)
        initJobDir(trainDir)
    if testSplit > 0.0:
        mkdir(testDir)
        initJobDir(testDir)
    if validSplit > 0.0:
        mkdir(validDir)
        initJobDir(validDir)

    if floatsAreEqual(trainSplit, 1.0):
        trainDatasetSize = len(argumentsTXTList)
    elif floatsAreEqual(testSplit, 1.0):
        testDatasetSize = len(argumentsTXTList)
    elif floatsAreEqual(validSplit, 1.0):
        validDatasetSize = len(argumentsTXTList)
    elif floatsAreEqual(trainSplit, 0.0):
        validDatasetSize = math.ceil(len(argumentsTXTList) * validSplit)
        testDatasetSize = len(argumentsTXTList) - validDatasetSize
    elif floatsAreEqual(testSplit, 0.0):
        validDatasetSize = math.ceil(len(argumentsTXTList) * validSplit)
        trainDatasetSize = len(argumentsTXTList) - validDatasetSize
    elif floatsAreEqual(validSplit, 0.0):
        trainDatasetSize = math.ceil(len(argumentsTXTList) * trainSplit)
        testDatasetSize = len(argumentsTXTList) - trainDatasetSize
    else:
        trainDatasetSize = math.floor(len(argumentsTXTList) * trainSplit)
        validDatasetSize = math.ceil(len(argumentsTXTList) * validSplit)
        testDatasetSize = math.floor(len(argumentsTXTList) * testSplit)

    if trainDatasetSize > 0:
        with open(os.path.join(trainDir, "arguments.txt"), 'w') as a:
            a.writelines(argumentsTXTList[:trainDatasetSize])
            coloredPrint("----- train split -----", bcolors.ORANGE)
            print("Number of jobs in train split: ", len(argumentsTXTList[:trainDatasetSize]))
            del argumentsTXTList[:trainDatasetSize]
            writeJobFiles(trainDir, "train")
    if testDatasetSize > 0:
        with open(os.path.join(testDir, "arguments.txt"), 'w') as a:
            a.writelines(argumentsTXTList[:testDatasetSize])
            coloredPrint("----- test split -----", bcolors.ORANGE)
            print("Number of jobs in test split: ", len(argumentsTXTList[:testDatasetSize]))
            del argumentsTXTList[:testDatasetSize]
            writeJobFiles(testDir, "test")
    if validDatasetSize > 0:
        with open(os.path.join(validDir, "arguments.txt"), 'w') as a:
            a.writelines(argumentsTXTList[:validDatasetSize])
            coloredPrint("----- validation split -----", bcolors.ORANGE)
            print("Number of jobs in validation split: ", len(argumentsTXTList[:validDatasetSize]))
            del argumentsTXTList[:validDatasetSize]
            writeJobFiles(validDir, "valid")
    print("-----------------------------")
    print("Sum of jobs in splits: ", str(trainDatasetSize + validDatasetSize + testDatasetSize))
printHeadline("###### END CREATING JOBS ######")