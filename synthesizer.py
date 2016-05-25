import numpy as np
import matplotlib.pyplot as plt
import argparse
from random import shuffle
from mpl_toolkits.mplot3d import Axes3D
from tqdm import *
from sklearn.cluster import KMeans
from sklearn.preprocessing import normalize
from pymongo import MongoClient
from scipy.spatial import distance
from sklearn.metrics import silhouette_score
from sklearn.decomposition import PCA
from pydub import AudioSegment

def main():
    args = parseArgs()

    numClusters = args.numClusters
    estimator = KMeans(n_clusters=numClusters, n_jobs=-1, n_init=20, precompute_distances='auto')
    print("Num Clusters: " + str(numClusters))
    #Gather grains into numpy array
    client = MongoClient()
    db = client.audiograins
    grainEntries = db.grains
    query = grainEntries.find({})
    dataIndex = 0
    indexToFilename = [None] * query.count()

    numXBins = args.numXBins
    numBinergies = args.numBinergies
    numLogBinergies = args.numLogBinergies
    numMFCCs = args.numMFCCs
    numRatios = args.numRatios

    features=[]

    if args.rolloff:
        features.extend(["rolloff"])

    if args.energy:
        features.extend(["energy"])

    if args.zcr:
        features.extend(["zcr"])

    if args.centroid:
        features.extend(["centroid"])

    if args.spread:
        features.extend(["spread"])

    if args.skewness:
        features.extend(["skewness"])

    if args.kurtosis:
        features.extend(["kurtosis"])


    nameFormat = "binergy%0" + str(len(str(numBinergies))) + "d"
    for binNum in range(numBinergies):
        features.append(nameFormat % binNum)

    nameFormat = "xBin%0" + str(len(str(numXBins))) + "d"
    for binNum in range(numXBins):
        features.append(nameFormat % binNum)

    nameFormat = "logbinergies%0" + str(len(str(numLogBinergies))) + "d"
    for binNum in range(numLogBinergies):
        features.append(nameFormat % binNum)

    nameFormat = "hratio%02d"
    for binNum in range(numRatios):
        features.append(nameFormat % binNum)

    nameFormat = "mfcc%02d"
    for binNum in range(0,numMFCCs):
        features.append(nameFormat % binNum)

    numFeatures = len(features)

    data = np.empty([query.count(), numFeatures])

    dataIndex = 0
    for grain in tqdm(query):
        featureNum = 0
        for feature in features:
            data[dataIndex][featureNum] = grain[feature]
            featureNum += 1
        indexToFilename[dataIndex] = grain["file"]
        dataIndex += 1

    print("Data pulled")
    ## Fit data, label, and put files in buckets
    print("Normalizing Data")
    if np.any(np.isnan(data)):
        print("Some data is NaN")
    if not np.all(np.isfinite(data)):
        print("Some data is infinite")
    normalize(data)

    estimator.fit(data)
    buckets = [None] * numClusters
    dataIndex = 0
    for label in estimator.labels_:
        if buckets[label] is None:
            buckets[label] = []
        buckets[label].append(indexToFilename[dataIndex])
        dataIndex += 1

    bucketIndex = 0
    for bucket in buckets:
        song = None
        shuffle(bucket)
        print("Writing sound file for bucket " + str(bucketIndex) + " With " + str(len(bucket)) + "samples")
        for grainFile in tqdm(bucket):
            grain = AudioSegment.from_wav(grainFile)
            if song is None:
                song = grain
            else:
                song = song.append(grain, crossfade=10)
        song.export("soundGroups/grouping" + str(bucketIndex) + ".wav", format="wav")
        bucketIndex += 1

    print("Silhouette score:" + str(silhouette_score(data, estimator.labels_, metric='euclidean'))) 

def parseArgs():
    parser = argparse.ArgumentParser(description='Cluster grains based on values computed using an analyzer whose results are available in a mongo database')
    parser.add_argument('-numClusters', '--numClusters', nargs='?', default=10, type=int)
    parser.add_argument('-numXBins', '--numXBins', nargs='?', default=0, type=int)
    parser.add_argument('-numBinergies', '--numBinergies', nargs='?', default=0, type=int)
    parser.add_argument('-numLogBinergies', '--numLogBinergies', nargs='?', default=0, type=int)
    parser.add_argument('-numMFCCs', '--numMFCCs', nargs='?', default=0, type=int)
    parser.add_argument('-numRatios', '--numRatios', nargs='?', default=0, type=int)
    parser.add_argument('--rolloff', dest='rolloff', action='store_true', help='use spectral rolloff in clustering')
    parser.add_argument('--energy', dest='energy', action='store_true', help='use signal energy in clustering')
    parser.add_argument('--zcr', dest='zcr', action='store_true', help='use signal zero crossing rate in clustering')
    parser.add_argument('--centroid', dest='centroid', action='store_true', help='use the spectral centroid in clustering')
    parser.add_argument('--spread', dest='spread', action='store_true', help='use the spectral spread in clustering')
    parser.add_argument('--skewness', dest='skewness', action='store_true', help='use the spectral skewness in clustering')
    parser.add_argument('--kurtosis', dest='kurtosis', action='store_true', help='use the spectral kurtosis in clustering')

    #Arg defaults
    parser.set_defaults(rolloff=False)
    parser.set_defaults(energy=False)
    parser.set_defaults(zcr=False)
    parser.set_defaults(centroid=False)
    parser.set_defaults(spread=False)
    parser.set_defaults(skewness=False)
    parser.set_defaults(kurtosis=False)

    return parser.parse_args()

if __name__ == "__main__":
    main()
