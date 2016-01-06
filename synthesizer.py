from sklearn.neighbors import BallTree
from sklearn import preprocessing
from sklearn.neighbors import LSHForest
from tqdm import *
from pymongo import MongoClient
from pydub import AudioSegment
import redis
from nearpy.storage import RedisStorage
from nearpy import Engine
from nearpy.hashes import RandomBinaryProjections
import wave
import argparse
import subprocess
import sys
import numpy as np
import pickle
import granulizer
import analyzer

def main():
    args = __parseArgs()

    if(args.build):
        if(args.classifier == "ball"):
            buildTree()
        elif(args.classifier == "LSH"):
            buildLSH()


    if(args.synthesize):
        if(args.classifier == "ball"):
            process(args.template)
        elif(args.classifier == "LSH"):
            processLSH(args.template)
        
def buildLSH():
    client = MongoClient()
    db = client.audiograins
    grainEntries = db.grains

    query = grainEntries.find({})
    indexToIds = [None] * query.count()    
    data = np.empty([query.count(), 16])
    dataIndex = 0
    print("Building tree")
    for grain in tqdm(query):
        data[dataIndex][0] = grain["mfcc00"] 
        data[dataIndex][1] = grain["mfcc01"] 
        data[dataIndex][2] = grain["mfcc02"] 
        data[dataIndex][3] = grain["mfcc03"]
        data[dataIndex][4] = grain["mfcc04"]
        data[dataIndex][5] = grain["mfcc05"]
        data[dataIndex][6] = grain["mfcc06"]
        data[dataIndex][7] = grain["mfcc07"]
        data[dataIndex][8] = grain["mfcc08"]
        data[dataIndex][9] = grain["mfcc09"]
        data[dataIndex][10] = grain["mfcc10"] 
        data[dataIndex][11] = grain["mfcc11"]
        data[dataIndex][12] = grain["mfcc12"]
        data[dataIndex][13] = grain["pitch"]
        #data[dataIndex][14] = grain["energy"]
        #data[dataIndex][15] = grain["kurtosis"]
        #data[dataIndex][16] = grain["skewness"]
        #data[dataIndex][17] = grain["spread"]
        #data[dataIndex][18] = grain["centroid"]
        data[dataIndex][15] = grain["zcr"]
        indexToIds[dataIndex] = grain["_id"]
        dataIndex += 1
    
    normalizer = preprocessing.Normalizer().fit(data) 
    data = normalizer.transform(data)
    tree = LSHForest(random_state=42)
    tree.fit(data)
    f = open('classifier.pickle', 'wb')
    pickle.dump(normalizer, open('normalizer.pickle', 'wb'))
    pickle.dump(indexToIds, open('indexToIds.pickle', 'wb'))
    pickle.dump(tree, f)

def processLSH(fileName):
    client = MongoClient()
    db = client.audiograins
    grainEntries = db.grains
    song = None
    songFile = open(fileName)
    logfile = open('logfile.log', 'w')
    print("converting to mono")
    monoFilename = "mono" + fileName
    subprocess.check_call(["ffmpeg -i " + fileName + " -ac 1 -threads 2 " + monoFilename], close_fds=True, shell=True)

    grains = granulizer.chopSound(monoFilename, 20, "inputGrains")
    print("Loading pickled files into memory...")
    normalizer = pickle.load(open("normalizer.pickle"))
    classifier = pickle.load(open("classifier.pickle"))
    indexToIds = pickle.load(open("indexToIds.pickle"))    
    print("Matching grains...")
    for grain in tqdm(grains):
        #Analyze all stats for grain
        dataPoint = np.empty([1, 16])
        mfccs = analyzer.analyzeMFCC(grain)
        dataPoint[0][0] = mfccs[0]
        dataPoint[0][1] = mfccs[1]
        dataPoint[0][2] = mfccs[2]
        dataPoint[0][3] = mfccs[3]
        dataPoint[0][4] = mfccs[4]
        dataPoint[0][5] = mfccs[5]
        dataPoint[0][6] = mfccs[6]
        dataPoint[0][7] = mfccs[7]
        dataPoint[0][8] = mfccs[8]
        dataPoint[0][9] = mfccs[9]
        dataPoint[0][10] = mfccs[10]
        dataPoint[0][11] = mfccs[11]
        dataPoint[0][12] = mfccs[12]
        dataPoint[0][13] = analyzer.analyzePitch(grain)
        dataPoint[0][14] = analyzer.analyzeEnergy(grain)
        #dataPoint[15] = kurtosis
        #dataPoint[16] = skewness
        #dataPoint[17] = spread
        #dataPoint[18] = centroid
        dataPoint[0][15] = analyzer.analyzeZeroCrossingRate(grain)
        dist, ind = classifier.kneighbors(normalizer.transform(dataPoint), n_neighbors=1) 
        logfile.write('DataPoint: ' + str(ind[0][0]) + ' at Dist: ' + str(dist[0][0]))
        grainId = indexToIds[ind[0][0]]
        query = grainEntries.find({"_id" : grainId})
        grain = AudioSegment.from_wav(query[0]["file"])
        if song is None:
            song = grain
        else:
            song = song.append(grain, crossfade=0)

    song.export("remix.wav", format='wav')

def process(fileName):
    client = MongoClient()
    db = client.audiograins
    grainEntries = db.grains
    song = None
    songFile = open(fileName)
    print("converting to mono")
    monoFilename = "mono" + fileName
    subprocess.check_call(["ffmpeg -i " + fileName + " -ac 1 -threads 2 " + monoFilename], close_fds=True, shell=True)

    grains = granulizer.chopSound(monoFilename, 20, "inputGrains")
    print("Loading pickled files into memory...")
    normalizer = pickle.load(open("normalizer.pickle"))
    classifier = pickle.load(open("classifier.pickle"))
    indexToIds = pickle.load(open("indexToIds.pickle"))    
    print("Matching grains...")
    for grain in tqdm(grains):
        #Analyze all stats for grain
        dataPoint = np.empty([1, 16])
        mfccs = analyzer.analyzeMFCC(grain)
        #dataPoint[0][0] = mfccs[0]
        #dataPoint[0][1] = mfccs[1]
        #dataPoint[0][2] = mfccs[2]
        #dataPoint[0][3] = mfccs[3]
        #dataPoint[0][4] = mfccs[4]
        #dataPoint[0][5] = mfccs[5]
        #dataPoint[0][6] = mfccs[6]
        #dataPoint[0][7] = mfccs[7]
        #dataPoint[0][8] = mfccs[8]
        #dataPoint[0][9] = mfccs[9]
        #dataPoint[0][10] = mfccs[10]
        #dataPoint[0][11] = mfccs[11]
        #dataPoint[0][12] = mfccs[12]
        #dataPoint[0][13] = analyzer.analyzePitch(grain)
        #dataPoint[0][14] = analyzer.analyzeEnergy(grain)
        #dataPoint[15] = kurtosis
        #dataPoint[16] = skewness
        #dataPoint[17] = spread
        #dataPoint[18] = centroid
        #dataPoint[0][15] = analyzer.analyzeZeroCrossingRate(grain)
        dataPoint[0][0] = analyzer.analyzePitch(grain)
        dist, ind = classifier.query(normalizer.transform(dataPoint), k=2) 
        grainId = indexToIds[ind[0][0]]
        query = grainEntries.find({"_id" : grainId})
        grain = AudioSegment.from_wav(query[0]["file"])
        if song is None:
            song = grain
        else:
            song = song.append(grain, crossfade=0)

    song.export("G_Scale_Pitch_Only_0msfade.wav", format='wav')


def buildTree():
    client = MongoClient()
    db = client.audiograins
    grainEntries = db.grains

    query = grainEntries.find({})
    indexToIds = [None] * query.count()    
    data = np.empty([query.count(), 16])
    dataIndex = 0
    print("Building tree")
    for grain in tqdm(query):
        #data[dataIndex][0] = grain["mfcc00"] 
        #data[dataIndex][1] = grain["mfcc01"] 
        #data[dataIndex][2] = grain["mfcc02"] 
        #data[dataIndex][3] = grain["mfcc03"]
        #data[dataIndex][4] = grain["mfcc04"]
        #data[dataIndex][5] = grain["mfcc05"]
        #data[dataIndex][6] = grain["mfcc06"]
        #data[dataIndex][7] = grain["mfcc07"]
        #data[dataIndex][8] = grain["mfcc08"]
        #data[dataIndex][9] = grain["mfcc09"]
        #data[dataIndex][10] = grain["mfcc10"] 
        #data[dataIndex][11] = grain["mfcc11"]
        #data[dataIndex][12] = grain["mfcc12"]
        #data[dataIndex][13] = grain["pitch"]
        #data[dataIndex][14] = grain["energy"]
        #data[dataIndex][15] = grain["kurtosis"]
        #data[dataIndex][16] = grain["skewness"]
        #data[dataIndex][17] = grain["spread"]
        #data[dataIndex][18] = grain["centroid"]
        #data[dataIndex][15] = grain["zcr"]
        data[dataIndex][0] = grain["pitch"]
        indexToIds[dataIndex] = grain["_id"]
        dataIndex += 1
    
    normalizer = preprocessing.Normalizer().fit(data) 
    data = normalizer.transform(data)
    tree = BallTree(data, leaf_size=2)
    f = open('classifier.pickle', 'wb')
    pickle.dump(normalizer, open('normalizer.pickle', 'wb'))
    pickle.dump(indexToIds, open('indexToIds.pickle', 'wb'))
    pickle.dump(tree, f)

def __parseArgs():
    parser = argparse.ArgumentParser(description='Classify a set of grains from a mongodb repository')
    parser.add_argument('--build', dest="build", action="store_true", help="Build the nearest neighbor ball tree")
    parser.add_argument('--synthesize', dest="synthesize", action="store_true", 
help="Reproduce an audio file using grains")
    parser.add_argument("-template", dest="template") 
    parser.add_argument("-grainSize", dest="grainSize")
    parser.add_argument("-classifier", dest="classifier")
    parser.set_defaults(classifier="LSH")
    parser.set_defaults(grainSize=20)
    parser.set_defaults(build=False)
    parser.set_defaults(synthesize=False) 

    return parser.parse_args()

if __name__ == "__main__":
    main()
