import numpy as np
import matplotlib.pyplot as plt
from random import shuffle
from mpl_toolkits.mplot3d import Axes3D
from tqdm import *
from sklearn.cluster import KMeans
from pymongo import MongoClient
from scipy.spatial import distance
from sklearn.metrics import silhouette_score
from sklearn.decomposition import PCA
from pydub import AudioSegment

numClusters = 10
estimator = KMeans(n_clusters=numClusters)

#Gather grains into numpy array
client = MongoClient()
db = client.audiograins
grainEntries = db.grains
query = grainEntries.find({ "hratio02" : { "$exists" : True }})
numFeatures = 20
dataIndex = 0
indexToFilename = [None] * query.count()
data = np.empty([query.count(), numFeatures])

#Only consider 10 harmonic ratios
numRatios = 2

for grain in tqdm(query):
    for binNum in range(0, numRatios):
        if data[dataIndex][binNum] < 0:
            print("Ratio less than 0! " + str(binNum) + " its " + str(data[dataIndex][binNum]))
            np.delete(data, dataIndex)
            break
        data[dataIndex][binNum] = grain['hratio' + format(binNum, '02')]
#    data[dataIndex][0] = grain["mfcc00"]
#    data[dataIndex][1] = grain["mfcc01"]
#    data[dataIndex][2] = grain["mfcc02"]
#    data[dataIndex][3] = grain["mfcc03"]
#    data[dataIndex][4] = grain["mfcc04"]
#    data[dataIndex][5] = grain["mfcc05"]
#    data[dataIndex][6] = grain["mfcc06"]
#    data[dataIndex][7] = grain["mfcc07"]
#    data[dataIndex][8] = grain["mfcc08"]
#    data[dataIndex][9] = grain["mfcc09"]
#    data[dataIndex][10] = grain["mfcc10"]
#    data[dataIndex][11] = grain["mfcc11"]
#    data[dataIndex][12] = grain["mfcc12"]
#    data[dataIndex][13] = grain["energy"]
#    data[dataIndex][14] = grain["kurtosis"]
#    data[dataIndex][15] = grain["skewness"]
#    data[dataIndex][16] = grain["spread"]
#    data[dataIndex][17] = grain["centroid"]
    indexToFilename[dataIndex] = grain["file"]
    dataIndex += 1

print("Data pulled")
## Fit data, label, and put files in buckets
estimator.fit(data)
buckets = [None] * numClusters
dataIndex = 0
for label in estimator.labels_:
    print("Label: " + str(label))
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
            song = song.append(grain, crossfade=15)
    song.export("soundGroups/grouping" + str(bucketIndex) + ".wav", format="wav")
    bucketIndex += 1

