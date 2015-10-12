import argparse
import eyed3
from tqdm import *
from pymongo import MongoClient
from pydub import AudioSegment

def main():
    args = parseArgs()
    analyzeGrains()

def analyzeGrains():
    client = MongoClient()
    db = client.audiograins
    grainEntries = db.grains
    
    for grain in grainEntries.find({ "processed" : "false"}):
        print(grain)

def parseArgs():
    parser = argparse.ArgumentParser(description='Analyze a set of grains to extract features and label them')
    return parser.parse_args()

main()
