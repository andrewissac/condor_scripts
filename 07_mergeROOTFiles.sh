#!/bin/bash

echo "### Begin Merge ROOT Files"

OUTPUTDIR=$1
OUTPUTFILENAME=$2

hadd $OUTPUTFILENAME *.root

# create output directory if it doesn't exist
mkdir -p $OUTPUTDIR
mv $OUTPUTFILENAME $OUTPUTDIR/$OUTPUTFILENAME

echo "### End Merge ROOT Files"