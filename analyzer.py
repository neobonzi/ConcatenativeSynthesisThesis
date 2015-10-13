import sys
import argparse
import os
from aubio import pitch
from aubio import source, pvoc, mfcc
from numpy import array, vstack, zeros
from tqdm import *
from pymongo import MongoClient
from pydub import AudioSegment

def main():
    args = parseArgs()
    if(args.clear):
        clearData()
    
    #processing
    if(args.mfcc):
        analyzeMFCC()
    
    if(args.pitch):
        analyzePitch()

def clearData():
    client = MongoClient()
    db = client.audiograins
    grainEntries = db.grains
    grains = grainEntries.find({})
    
    print("Clearing " + str(grains.count()) + " grains")

    for grain in tqdm(grains):
        os.remove(grain["file"])
        grainEntries.delete_one({"_id" : grain["_id"]})

def analyzePitch():
    client = MongoClient()
    db = client.audiograins
    grainEntries = db.grains

    query = grainEntries.find({ "pitch" : { "$exists": False }})
    print("Analyzing Pitch for " + str(query.count()) + " grains")
    for grain in tqdm(query):
        s = source(grain["file"], int(grain["sampleRate"]), int(float(grain["frameCount"])))
        samplerate = s.samplerate
        tolerance = 0.8
        pitch_out = pitch("yin", int(float(grain["frameCount"])), int(float(grain["frameCount"])), samplerate)
        samples, read = s()
        pitchFreq = pitch_out(samples)[0].item() 
        update = {"pitch" : pitchFreq}
        grainEntries.update_one({"_id": grain["_id"]}, {"$set" : update})
        

def analyzeMFCC():
    client = MongoClient()
    db = client.audiograins
    grainEntries = db.grains

    query = grainEntries.find({ "mfcc00" : { "$exists": False }})
    print("Analyzing MFCC for " + str(query.count()) + " grains")

    for grain in tqdm(query):
        windowSize = int(float(grain["frameCount"]))
        s = source(grain["file"], int(grain["sampleRate"]), windowSize)
        sampleRate = s.samplerate
        p = pvoc(windowSize, windowSize)
        m = mfcc(windowSize, 40, 13, s.samplerate)
        samples, read = s()
        spec = p(samples)
        mfcc_out = m(spec)
        mfccs = mfcc_out.tolist()
        for mfccIndex in range(0, len(mfccs)):
            update = {"mfcc" + format(mfccIndex, '02') : mfccs[mfccIndex]}
            grainEntries.update_one({"_id": grain["_id"]}, {"$set" : update})

def parseArgs():
    parser = argparse.ArgumentParser(description='Analyze a set of grains to extract features and label them')
    parser.add_argument('--clear', dest="clear", action="store_true", help="Delete all grains and clear all grain data.");
    parser.add_argument('--mfcc_off', dest="mfcc", action="store_false", help="Include to not compute Mel Frequency Cepstrum Coefficients");
    parser.add_argument('--pitch_off', dest="pitch", action="store_false", help="Include to not compute pitches");
    parser.set_defaults(clear=False)
    parser.set_defaults(mfcc=True)
    return parser.parse_args()

main()
