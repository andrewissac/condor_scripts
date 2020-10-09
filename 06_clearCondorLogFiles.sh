#!/bin/bash

echo "### Begin clearing condor log files"
cd err
rm *.err
cd -
echo "deleted err files"
cd log
rm *.log
cd -
echo "deleted log files"
cd out
rm *.out
cd -
echo "deleted out files"
echo "### End clearing condor log files"