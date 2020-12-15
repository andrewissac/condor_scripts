#!/bin/bash

echo "Arguments: " $@

N=$1
SOURCEDIR=$2
DESTINATIONDIR=$3

cd $SOURCEDIR

echo "### Begin copy files to $DESTINATIONDIR"

for FILE in $(ls *.root | head -$N); do
    cp $FILE $DESTINATIONDIR;
    echo "Copied $FILE" 
done

echo "### Finished copying files"