#!/bin/bash

echo "### Begin submitting condor jobs"

set -e

THIS_PWD=$PWD
JOBDIR=${1%/} # %/ removes trailing slash

function condorSubmit () {
    if test -d "$1"
    then
        echo "cd ${1}"
        cd $1
        echo "${PWD}"
        if test -f "job.jdl"
        then
            echo "condor_submit job.jdl"
            condor_submit job.jdl
            echo "cd .."
            cd ..
        fi
    fi
}

if test -d "$JOBDIR"
then
    echo "cd ${JOBDIR}"
    cd $JOBDIR
    if test -f "job.jdl" 
    then
        echo "Found job.jdl - begin submitting"
        # condor_submit job.jdl
        echo "cd .."
        cd ..
    else
        echo "Did not find job.jdl - continue looking for train, test or valid directories with job.jdl files"
        condorSubmit "train"
        condorSubmit "test"
        condorSubmit "valid"
    fi
else
    echo "${JOBDIR} does not exist."
fi

echo "cd ${THIS_PWD}"
cd $THIS_PWD

echo "### End submitting condor jobs"