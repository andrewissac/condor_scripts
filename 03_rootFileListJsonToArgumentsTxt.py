import json
import argparse
import sys

parser = argparse.ArgumentParser()
parser.add_argument("-f", "--filename", required=True, type=str)
args = parser.parse_args()

def convertJsonROOTFileListToArgumentsTxt(jsonFilePath):
    rootFilesPaths = []
    with open(jsonFilePath, 'r') as jsonFile:
        try:
            rootFiles = json.load(jsonFile)
            #print(json.dumps(parsed, indent=4, sort_keys=True))

            i = 0
            for rootFile in rootFiles:
                for data in rootFile['file']:
                    rootFilesPaths.append(str(i) + " " + data['name'] + " " + data['dataset'].replace('/','_')  + "\n")
                    i += 1
        except json.JSONDecodeError:
            print("JSONDecodeError: Invalid JSON format.")

    with open('arguments.txt', 'w') as argumentsFile:
        argumentsFile.writelines(rootFilesPaths)

convertJsonROOTFileListToArgumentsTxt(args.filename)
