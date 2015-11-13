from sklearn.neighbors import BallTree
from sklearn import preprocessing
from tqdm import *
from pymongo import MongoClient
from pydub import AudioSegment
import argparse
import sys
import numpy as np
import pickle
import granulizer
import analyzer

def main():
    args = __parseArgs()

    if(args.build):
        buildTree()

    if(args.synthesize):
        process(args.template)
        
def process(fileName):
    client = MongoClient()
    db = client.audiograins
    grainEntries = db.grains
    song = AudioSegment.empty()

    grains = granulizer.chopSound(fileName, 20, "inputGrains")

    normalizer = pickle.load(open("normalizer.pickle"))
    classifier = pickle.load(open("classifier.pickle"))
    indexToIds = pickle.load(open("indexToIds.pickle"))    
    for grain in tqdm(grains):
        #Analyze all stats for grain
        dataPoint = np.empty([14])
        print(str(grain))
        centroid, spread, skewness, kurtosis = analyzer.analyzeSpectralShape(grain)
        mfccs = analyzer.analyzeMFCC(grain)
        dataPoint[0] = mfccs[0]
        dataPoint[1] = mfccs[1]
        dataPoint[2] = mfccs[2]
        dataPoint[3] = mfccs[3]
        dataPoint[4] = mfccs[4]
        dataPoint[5] = mfccs[5]
        dataPoint[6] = mfccs[6]
        dataPoint[7] = mfccs[7]
        dataPoint[8] = mfccs[8]
        dataPoint[9] = mfccs[9]
        dataPoint[10] = mfccs[10]
        dataPoint[11] = mfccs[11]
        dataPoint[12] = mfccs[12]
        dataPoint[13] = analyzer.analyzePitch(grain)
        dataPoint[14] = analyzer.analyzeEnergy(grain)
        #dataPoint[15] = kurtosis
        #dataPoint[16] = skewness
        #dataPoint[17] = spread
        #dataPoint[18] = centroid
        #dataPoint[19] = analyzer.analyzeZeroCrossingRate(grain)
        dist, ind = classifier.query(normalizer.transform(dataPoint), k=2) 
        grainId = indexToIds[ind[0][0]]
        query = grainEntries.find({"_id" : grainId})
        grain = AudioSegment.from_wav(query[0]["file"])
        song = song.append(grain, crossfade=2)

    song.export("remix.wav", format='wav')

def buildTree():
    client = MongoClient()
    db = client.audiograins
    grainEntries = db.grains

    query = grainEntries.find({})
    indexToIds = [None] * query.count()    
    data = np.empty([query.count(), 14])
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
        #data[dataIndex][19] = grain["zcr"]
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
    parser.set_defaults(grainSize=20)
    parser.set_defaults(build=False)
    parser.set_defaults(synthesize=False) 

    return parser.parse_args()

if __name__ == "__main__":
    main()
