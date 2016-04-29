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

numClusters = 100

#Gather grains into numpy array
client = MongoClient()
db = client.audiograins
grainEntries = db.grains
query = grainEntries.find({ "hratio09" : { "$exists" : True }})
numFeatures = 20
dataIndex = 0
indexToFilename = [None] * query.count()
data = np.empty([query.count(), numFeatures])

#Only consider 10 harmonic ratios
numRatios = 10

for grain in tqdm(query):
    for binNum in range(2, numRatios):
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

maxClusters = 100

for curNumClusters in xrange(2, maxClusters, 10):
    estimator = KMeans(n_clusters=curNumClusters)
    estimator.fit(data)
    silhouette_avg = silhouette_score(data, estimator.labels_)
    print("For n_clusters = ", curNumClusters, "The average silhouette_score is :", silhouette_avg) 



