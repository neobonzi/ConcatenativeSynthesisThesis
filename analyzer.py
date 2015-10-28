import sys
import argparse
import os
from yaafelib import *
from aubio import pitch
from aubio import source, pvoc, mfcc
import numpy as numpy
from numpy import array, vstack, zeros
from scipy.io import wavfile
from tqdm import *
from pymongo import MongoClient
from pydub import AudioSegment

def main():
    args = parseArgs()
    if(args.clear):
        clearData()
    
    #processing
    if(args.mfcc or args.all):
        analyzeAllMFCC()
    
    if(args.pitch or args.all):
        analyzeAllPitch()

    if(args.energy or args.all):
        analyzeAllEnergy()

    if(args.shape or args.all):
        analyzeAllSpectralShape()

    if(args.zcr or args.all):
        analyzeAllZeroCrossingRate()

def clearData():
    client = MongoClient()
    db = client.audiograins
    grainEntries = db.grains
    grains = grainEntries.find({})
    
    print("Clearing " + str(grains.count()) + " grains")

    for grain in tqdm(grains):
        os.remove(grain["file"])
        grainEntries.delete_one({"_id" : grain["_id"]})

def analyzeAllPitch():
    client = MongoClient()
    db = client.audiograins
    grainEntries = db.grains

    query = grainEntries.find({ "pitch" : { "$exists": False }})
    print("Analyzing Pitch for " + str(query.count()) + " grains")
    for grain in tqdm(query):
        update = {"pitch" : analyzePitch(grain)}
        grainEntries.update_one({"_id": grain["_id"]}, {"$set" : update})

def analyzePitch(grain):
    s = source(grain["file"], int(grain["sampleRate"]), int(float(grain["frameCount"])))
    samplerate = s.samplerate
    tolerance = 0.8
    pitch_out = pitch("yin", int(float(grain["frameCount"])), int(float(grain["frameCount"])), samplerate)
    samples, read = s()
    pitchFreq = pitch_out(samples)[0].item() 

    return pitchFreq

def analyzeAllZeroCrossingRate():
    client = MongoClient()
    db = client.audiograins 
    grainEntries = db.grains


    query = grainEntries.find({ "zcr" : { "$exists": False }})
    print("Analyzing Zero Crossing Rate for " + str(query.count()) + " grains")

    for grain in tqdm(query):
        update = {"zcr" : analyzeZeroCrossingRate(grain)}
        grainEntries.update_one({"_id": grain["_id"]}, {"$set" : update})

def analyzeZeroCrossingRate(grain):
    blockSize = grain["frameCount"]
    stepSize = grain["frameCount"]
    fp = FeaturePlan(sample_rate=int(grain["sampleRate"]))
    fp.addFeature('zcr: ZCR blockSize=' + blockSize + ' stepSize=' + stepSize)
    engine = Engine()
    engine.load(fp.getDataFlow())
    (rate, data) = wavfile.read(grain["file"])
    data = numpy.array([data.astype(numpy.float64)]);
    feats = engine.processAudio(data)
    return feats["zcr"][0][0]

def analyzeAllSpectralShape():
    client = MongoClient()
    db = client.audiograins 
    grainEntries = db.grains

    query = grainEntries.find({ "centroid" : { "$exists": False }})
    print("Analyzing Spectral Shape for " + str(query.count()) + " grains")

    for grain in tqdm(query):
        centroid, spread, skewness, kurtosis = analyzeSpectralShape(grain)
        update = {"centroid" : centroid,
                  "spread"   : spread,
                  "skewness" : skewness,
                  "kurtosis" : kurtosis}
        grainEntries.update_one({"_id": grain["_id"]}, {"$set" : update})

def analyzeSpectralShape(grain):
    blockSize = grain["frameCount"]
    stepSize = grain["frameCount"]
    fp = FeaturePlan(sample_rate=int(grain["sampleRate"]))
    fp.addFeature('spectralShape: SpectralShapeStatistics blockSize=' + blockSize + ' stepSize=' + stepSize)
    engine = Engine()
    engine.load(fp.getDataFlow())
    (rate, data) = wavfile.read(grain["file"])
    data = numpy.array([data.astype(numpy.float64)]);
    feats = engine.processAudio(data)
    return (feats["spectralShape"][0][0], feats["spectralShape"][0][1], feats["spectralShape"][0][2], feats["spectralShape"][0][3])

def analyzeAllEnergy():
    client = MongoClient()
    db = client.audiograins 
    grainEntries = db.grains


    query = grainEntries.find({ "energy" : { "$exists": False }})
    print("Analyzing Energy for " + str(query.count()) + " grains")

    for grain in tqdm(query):
        update = {"energy" : analyzeEnergy(grain)}
        grainEntries.update_one({"_id": grain["_id"]}, {"$set" : update})

def analyzeEnergy(grain):
    blockSize = grain["frameCount"]
    stepSize = grain["frameCount"]
    fp = FeaturePlan(sample_rate=int(grain["sampleRate"]))
    fp.addFeature('energy: Energy blockSize=' + blockSize + ' stepSize=' + stepSize)
    engine = Engine()
    engine.load(fp.getDataFlow())
    (rate, data) = wavfile.read(grain["file"])
    data = numpy.array([data.astype(numpy.float64)]);
    feats = engine.processAudio(data)
    return feats["energy"][0][0] 

def analyzeAllMFCC():
    client = MongoClient()
    db = client.audiograins
    grainEntries = db.grains

    query = grainEntries.find({ "mfcc00" : { "$exists": False }})
    print("Analyzing MFCC for " + str(query.count()) + " grains")

    for grain in tqdm(query):
        mfccs = analyzeMFCC(grain)
        for mfccIndex in range(0, len(mfccs)):
            update = {"mfcc" + format(mfccIndex, '02') : mfccs[mfccIndex]}
            grainEntries.update_one({"_id": grain["_id"]}, {"$set" : update})

def analyzeMFCC(grain):
    windowSize = int(float(grain["frameCount"]))
    s = source(grain["file"], int(grain["sampleRate"]), windowSize)
    sampleRate = s.samplerate
    p = pvoc(windowSize, windowSize)
    m = mfcc(windowSize, 40, 13, s.samplerate)
    samples, read = s()
    spec = p(samples)
    mfcc_out = m(spec)
    mfccs = mfcc_out.tolist()
    return mfccs 

def parseArgs():
    parser = argparse.ArgumentParser(description='Analyze a set of grains to extract features and label them')
    parser.add_argument('--clear', dest="clear", action="store_true", help="Delete all grains and clear all grain data.");
    parser.add_argument('--mfcc', dest="mfcc", action="store_true", help="Include to not compute Mel Frequency Cepstrum Coefficients");
    parser.add_argument('--pitch', dest="pitch", action="store_true", help="Include to not compute pitches");
    parser.add_argument('--energy', dest="energy", action="store_true", help="Compute RMS energy for grain");
    parser.add_argument('--shape', dest="shape", action="store_true", help="Compute the spectral shape data for grain");
    parser.add_argument('--all', dest="all", action="store_true", help="Compute all available features");
    parser.add_argument('--zcr', dest="zcr", action="store_true", help="Compute Zero Crossing Rate for grains");
    parser.set_defaults(clear=False)
    parser.set_defaults(mfcc=False)
    parser.set_defaults(shape=False)
    parser.set_defaults(zcr=False)
    parser.set_defaults(energy=False)
    parser.set_defaults(all=False)

    return parser.parse_args()

if __name__ == "__main__":
    main()
