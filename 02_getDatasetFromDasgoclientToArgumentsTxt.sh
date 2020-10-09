#!/bin/bash

GREEN='\033[1;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # no color

echo -e "${YELLOW}------------ Begin GetDataset from dasgoclient query ------------${NC}"

export X509_USER_PROXY=/home/aissac/.globus/x509up
export VO_CMS_SW_DIR=/cvmfs/cms.cern.ch
source $VO_CMS_SW_DIR/cmsset_default.sh

# Arguments that user has to pass to this script
OUTPUTJSONFILENAME=$1
DATASET=$2

echo -e "${YELLOW}------------ Using dasgoclient query -------------${NC}"
echo -e "${GREEN}>>start query on dataset: ${NC}" $DATASET

dasgoclient --query="file dataset=/$DATASET" -json  > $OUTPUTJSONFILENAME
echo -e "${GREEN}>>output json file containing ROOT file paths: ${NC}" $OUTPUTJSONFILENAME
echo -e "${YELLOW}------------ Finished dasgoclient query -------------${NC}"

echo -e "\n${YELLOW}------------ Begin parsing JSON file -------------${NC}"
# be careful: make python script executable with chmod +x myscript.py
python rootFileListJsonToArgumentsTxt.py -f $OUTPUTJSONFILENAME
echo -e "${GREEN}>>arguments.txt has been created. ${NC}"
echo -e "${YELLOW}------------ End parsing JSON file -------------${NC}"

echo -e "${YELLOW}------------ End GetDataset from dasgoclient query ------------${NC}"