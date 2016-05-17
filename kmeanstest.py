import numpy as np
import matplotlib.pyplot as plt
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

numClusters = 10
estimator = KMeans(n_clusters=numClusters, n_jobs=-1, n_init=20, precompute_distances='auto')

#Gather grains into numpy array
client = MongoClient()
db = client.audiograins
grainEntries = db.grains
query = grainEntries.find({})
dataIndex = 0
indexToFilename = [None] * query.count()

numXBins = 100
numBinergies = 20
numLogBinergies = 13
numMFCCs = 13
numRatios = 4

features=[]
#features.extend(["rolloff", "spread"])
#features.extend([ "rolloff", "skewness", "spread"])


#nameFormat = "binergy%0" + str(len(str(numBinergies))) + "d"
#for binNum in range(numBinergies):
#    features.append(nameFormat % binNum)

#nameFormat = "xBin%0" + str(len(str(numXBins))) + "d"
#for binNum in range(numBinergies):
#    features.append(nameFormat % binNum)

#nameFormat = "logbinergies%0" + str(len(str(numLogBinergies))) + "d"
#for binNum in range(numLogBinergies):
#    features.append(nameFormat % binNum)


nameFormat = "hratio%02d"
for binNum in range(numRatios):
    features.append(nameFormat % binNum)

#nameFormat = "mfcc%02d"
#nameFormat = "mfcc%0" + str(len(str(numMFCCs))) + "d"
#for binNum in range(0,numMFCCs):
#    features.append(nameFormat % binNum)

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
            song = song.append(grain, crossfade=10)
    song.export("soundGroups/grouping" + str(bucketIndex) + ".wav", format="wav")
    bucketIndex += 1

## Perform PCA
#reduced_data = PCA(n_components=2).fit_transform(data)
#kmeans = KMeans(init='k-means++', n_clusters=20, n_init=10)
#kmeans.fit(reduced_data)
#fig = plt.figure("a", figsize=(10, 8))
#plt.clf()
#ax = Axes3D(fig, rect=[0, 0, .95, 1], elev=48, azim=134)
#ax.autoscale_view()
#plt.cla()
#labels = kmeans.labels_
#ax.scatter(reduced_data[:, 0], reduced_data[:, 1], c=labels.astype(np.float))

#ax.w_xaxis.set_ticklabels([])
#ax.w_yaxis.set_ticklabels([])
#ax.w_zaxis.set_ticklabels([])
#ax.set_xlabel('Petal width')
#ax.set_ylabel('Sepal length')
#ax.set_zlabel('Petal length')

#fig.savefig('hi.png')
## Test the silhouette score
#k_range = range(300, 301)
#k_means_var = [KMeans(n_clusters=k, random_state=10) for k in k_range]
#print("Fitting data")
#k_labels = [clusterer.fit_predict(data) for clusterer in k_means_var]
#print("Computing averages")
#k_silhouette_avg = [silhouette_score(data, X) for X in k_labels]

#curNumClusters = k_range[0]
#for silhouette_score in k_silhouette_avg:
#    print("For n_clusters=" + str(curNumClusters) + " The average silhouette_score is : " + str(silhouette_score))
#    curNumClusters += 1
