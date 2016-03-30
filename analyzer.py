#!/usr/bin/env python
import sys
import argparse
import os
import fpectl
import math
from features import logfbank
from features import fbank
from yaafelib import *
from aubio import pitch
from aubio import source, pvoc, mfcc 
import struct
import numpy as numpy
from numpy import array, vstack, zeros
from scipy import signal
import scipy.io.wavfile as wav
from tqdm import *
from pymongo import MongoClient
from pydub import AudioSegment

def main():
    fpectl.turnoff_sigfpe()
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

    if(args.binergy or args.all):
        analyzeAllBinergies()

    if(args.xbins or args.all):
        analyzeAllXBins()

    if(args.logbinergy or args.all):
        analyzeAllLogBinergy()

    if(args.ratios or args.all):
        analyzeAllHarmonicRatios()

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
    (rate, data) = wav.read(grain["file"])
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
        try:
            print(grain["_id"])
            centroid, spread, skewness, kurtosis = analyzeSpectralShape(grain)
        except Exception:
            grainEntries.remove({_id : grain["_id"]})
            continue
        update = {"centroid" : centroid,
                  "spread"   : spread,
                  "skewness" : skewness,
                  "kurtosis" : kurtosis}
        grainEntries.update_one({"_id": grain["_id"]}, {"$set" : update})

def analyzeSpectralShape(grain):
    blockSize = grain["frameCount"]
    stepSize = grain["frameCount"]
    #print(str(grain))
    try:
        fp = FeaturePlan(sample_rate=int(grain["sampleRate"]))
        fp.addFeature('spectralShape: SpectralShapeStatistics blockSize=' + blockSize + ' stepSize=' + stepSize)
        engine = Engine()
        engine.load(fp.getDataFlow())
        (rate, data) = wavfile.read(grain["file"])
        data = numpy.array([data.astype(numpy.float64)]);
        feats = engine.processAudio(data)
        return (feats["spectralShape"][0][0], feats["spectralShape"][0][1], feats["spectralShape"][0][2], feats["spectralShape"][0][3])
    except Exception:
        print "cannot process " + str(grain)

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

def analyzeAllXBins():
    client = MongoClient()
    db = client.audiograins
    grainEntries = db.grains
    query = grainEntries.find({ "xBin000" : { "$exists" : False }})

    for grain in tqdm(query):
        xBins = analyzeXBins(grain)[0]
        for xBinIndex in range(0, len(xBins)):
            update = {"xBin" + format(xBinIndex, '03') : xBins[xBinIndex]}
            grainEntries.update_one({"_id": grain["_id"]}, {"$set" : update})

def analyzeXBins(grain):
    windowSize = int(float(grain["frameCount"]))
    (rate,sig) = wav.read(grain["file"])
    windowedSignal = numpy.multiply(signal.hamming(windowSize), sig)
    energies = logfbank(signal=sig, samplerate=rate, winlen=.020, winstep=.020, nfilt=100, nfft=windowSize)   
    return energies.tolist()

def analyzeAllLogBinergy():
    client = MongoClient()
    db = client.audiograins
    grainEntries = db.grains

    query = grainEntries.find({"logbinergies00" : { "$exists" : False}})
    print("Analyzing Log Binergies for " + str(query.count()) + " grains")

    for grain in tqdm(query):
        energies = analyzeLogBinergy(grain)
        energyIndex = 0
        if energies is None:
            continue

        for energy in energies:
            update = {"logbinergies" + format(energyIndex, '02') : energy}
            grainEntries.update_one({"_id": grain["_id"]}, {"$set" : update})
            energyIndex += 1

def analyzeLogBinergy(grain):
    rate, data = wav.read(grain["file"])
    numBins = 20
    data = numpy.array(data, dtype=float)
    f, Pxx_den = signal.periodogram(data, fs=rate, window='hanning', return_onesided=True, scaling='spectrum', axis=-1)

    energies = [0] * numBins

    if(len(Pxx_den) < 50):
        return None

    bins = getLogBins(numBins, rate / 2, 0)


    for binNum in range(numBins):
        for index in range(len(f)):
            #print("Freq: " + str(f[index]))
            binWeight = getLogBinWeight(f[index], bins, binNum + 1)
            #print("Bin Weight: " + str(binWeight))
            energies[binNum] += Pxx_den[index] * binWeight
            #print("Energy: " + str(energies[binNum]))

        #print("Energy in bin " + str(binNum) + ": " + str(energies[binNum]))
    return energies


def getLogBinWeight(index, bins, binNum):

    #print("index: " + str(index) + " binIndex: " + str(binNum) + " binValue: " + str(bins[binNum]))
    if(index < bins[binNum - 1]):
        return 0
    elif(bins[binNum - 1] <= index and index <= bins[binNum]):
        #return ((index - bins[binNum-1]) / float((bins[binNum] - bins[binNum - 1])))
        slope = (1 / float((bins[binNum] - bins[binNum - 1])))
        return (slope * (index - bins[binNum - 1]))
    elif(bins[binNum] <= index and index <= bins[binNum + 1]):
        print("Bin num: " + str(binNum))
        #return ((bins[binNum + 1] - index) / float((bins[binNum + 1] - bins[binNum])))
        slope = (-1 / float((bins[binNum + 1] - bins[binNum])))
        return 1 + (slope * (index - bins[binNum]))
    else:
        return 0

def getLogBins(numBins, maxFreq, minFreq):
    logMax = math.log1p(maxFreq + 1)
    logMin = math.log1p(minFreq + 1)
    logStep = (logMax - logMin) / float(numBins)

    bins = []


    for bindex in numpy.arange(logMin, logMax, logStep):
        bins.append(math.floor(math.exp(bindex) - 1))

    bins.append(math.floor(math.exp(logMax) - 1))

    return bins

def analyzeAllBinergies():
    client = MongoClient()
    db = client.audiograins
    grainEntries = db.grains

    query = grainEntries.find({"binergies00" : { "$exists": False}})
    print("Analyzing Binergies for " + str(query.count()) + " grains")


    for grain in tqdm(query):
        energies = analyzeBinergy(grain)
        energyIndex = 0
        if energies is None:
            continue
        for energy in energies:
            update = {"binergy" + format(energyIndex, '02') : energy}
            grainEntries.update_one({"_id": grain["_id"]}, {"$set" : update})
            energyIndex += 1

def analyzeBinergy(grain):
    rate, data = wav.read(grain["file"])
    numBins = 20
    data = numpy.array(data, dtype=float)
    #data = data * numpy.hanning(float(grain["frameCount"]))
    f, Pxx_den = signal.periodogram(data, fs=rate, window='hanning', return_onesided=True, scaling='spectrum', axis=-1)
   
    if(len(Pxx_den) < 50):
        return None

    binWidth = len(Pxx_den) / numBins

    energy = [0] * numBins 

    for binNum in range(numBins):
        for binIndex in range(binWidth):
            if binIndex <= (binWidth / 2):
                slope = 1 / float((binWidth / 2))
                energy[binNum] += Pxx_den[binIndex + (binNum * binWidth)] * (slope * binIndex)
            else:
                slope = -1 / float(binWidth / 2)
                energy[binNum] += Pxx_den[binIndex + (binNum * binWidth)] * (slope * (binIndex - (binWidth / 2)))

    return energy


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

def analyzeAllHarmonicRatios():
    client = MongoClient()
    db = client.audiograins
    grainEntries = db.grains

    query = grainEntries.find({ "hratio00" : {"$exists" : False}})
    print("Analyzing Harmonic Ratios for " + str(query.count()) + " grains")

    for grain in tqdm(query):
        ratios = analyzeHarmonicRatios(grain)
        for ratioIndex in range(0, len(ratios)):
            update = {"hratio" + format(ratioIndex, '02') : ratios[ratioIndex]}
            grainEntries.update_one({"_id": grain["_id"]}, {"$set" : update})
    client.close()

def analyzeHarmonicRatios(grain):
    rate, data = wav.read(grain["file"])
    numHarmonics = 4
    data = numpy.array(data, dtype=float)
    #data = data * numpy.hanning(float(grain["frameCount"]))
    f, Pxx_den = signal.periodogram(data, fs=rate, window='hanning', return_onesided=True, scaling='spectrum', axis=-1)
   
    if(len(Pxx_den) < 50):
        return None

    numBins = len(Pxx_den)
    mostEnergy = 0
    mostEnergyBinIndex = 0

    #Find the bin with the most energy
    for binNum in range(1,numBins):
        if(mostEnergy < Pxx_den[binNum]):
            mostEnergy = Pxx_den[binNum]
            mostEnergyBinIndex = binNum

    # Sometimes the data is bad, skip
    if (mostEnergy == 0):
        return []
    #print("Most energy " + str(mostEnergy) + " at bin: " + str(mostEnergyBinIndex) + " of " + str(len(Pxx_den)) + " bins")
    
    ratios = []

    for harmonicBin in xrange(mostEnergyBinIndex + mostEnergyBinIndex, min([10,len(Pxx_den)]), mostEnergyBinIndex):
        #print("Looking at bin " + str(harmonicBin))
        curRatio = mostEnergy / float(Pxx_den[harmonicBin])
        #print("Bin: " + str(harmonicBin) + " with energy " + str(Pxx_den[harmonicBin]) + " ratio " + str(curRatio)) 
        ratios.append(curRatio)

    return ratios



def parseArgs():
    parser = argparse.ArgumentParser(description='Analyze a set of grains to extract features and label them')
    parser.add_argument('--clear', dest="clear", action="store_true", help="Delete all grains and clear all grain data.");
    parser.add_argument('--mfcc', dest="mfcc", action="store_true", help="Include to not compute Mel Frequency Cepstrum Coefficients");
    parser.add_argument('--pitch', dest="pitch", action="store_true", help="Include to not compute pitches");
    parser.add_argument('--energy', dest="energy", action="store_true", help="Compute RMS energy for grain");
    parser.add_argument('--shape', dest="shape", action="store_true", help="Compute the spectral shape data for grain");
    parser.add_argument('--all', dest="all", action="store_true", help="Compute all available features");
    parser.add_argument('--zcr', dest="zcr", action="store_true", help="Compute Zero Crossing Rate for grains");
    parser.add_argument('--xbins', dest='xbins', action="store_true", help="Compute X Bins for grains");
    parser.add_argument('--binergy', dest='binergy', action="store_true", help="Compute energy in X bins for garins")
    parser.add_argument('--logbinergy', dest='logbinergy', action="store_true", help="Compute energy in X logarithmically spaced bins for grains")
    parser.add_argument('--ratios', dest='ratios', action="store_true", help="Compute harmonic ratios of periodogram")
    parser.set_defaults(logbinergy=False)
    parser.set_defaults(binergy=False)
    parser.set_defaults(clear=False)
    parser.set_defaults(mfcc=False)
    parser.set_defaults(shape=False)
    parser.set_defaults(zcr=False)
    parser.set_defaults(energy=False)
    parser.set_defaults(xbins=False)
    parser.set_defaults(ratios=False)
    parser.set_defaults(all=False)

    return parser.parse_args()

if __name__ == "__main__":
    main()
