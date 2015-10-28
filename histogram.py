import matplotlib.pyplot as plt
from pymongo import MongoClient
from numpy import array, vstack, zeros
import matplotlib.pyplot as plt
import numpy as np

client = MongoClient()
db = client.audiograins
grainEntries = db.grains

query = grainEntries.find({})

mfcc00 = []
mfcc01 = []
mfcc02 = []
mfcc03 = []
mfcc04 = []
mfcc05 = []
mfcc06 = []
mfcc07 = []
mfcc08 = []
mfcc09 = []
mfcc10 = []
mfcc11 = []
mfcc12 = []
pitch = []
energy = []
kurtosis = []
skewness = []
spread = []
centroid = []
zcr = []

for grain in query:
    mfcc00.append(grain['mfcc00'])    
    mfcc01.append(grain['mfcc01'])    
    mfcc02.append(grain['mfcc02'])    
    mfcc03.append(grain['mfcc03'])    
    mfcc04.append(grain['mfcc04'])    
    mfcc05.append(grain['mfcc05'])    
    mfcc06.append(grain['mfcc06'])    
    mfcc07.append(grain['mfcc07'])    
    mfcc08.append(grain['mfcc08'])    
    mfcc09.append(grain['mfcc09'])    
    mfcc10.append(grain['mfcc10'])    
    mfcc11.append(grain['mfcc11'])    
    mfcc12.append(grain['mfcc12'])    
    pitch.append(grain['pitch'])    
    energy.append(grain['energy'])    
    kurtosis.append(grain['kurtosis'])    
    skewness.append(grain['skewness'])    
    spread.append(grain['spread'])    
    centroid.append(grain['centroid'])    
    zcr.append(grain['zcr'])    

#mfcc00
plt.title('Mel-Frequency Cepstral Coefficient 0 Feature Distribution')
mfcc00_hist = np.array(mfcc00)
hist, bins = np.histogram(mfcc00_hist)
width = 0.7 * (bins[1] - bins[0])
center = (bins[:-1] + bins[1:]) / 2
plt.bar(center, hist, align='center', width=width)
plt.savefig('featureHistograms/mfcc00_hist.png')
plt.close()

#mfcc01
plt.title('Mel-Frequency Cepstral Coefficient 1 Feature Distribution')
mfcc01_hist = np.array(mfcc01)
hist, bins = np.histogram(mfcc01_hist)
width = 0.7 * (bins[1] - bins[0])
center = (bins[:-1] + bins[1:]) / 2
plt.bar(center, hist, align='center', width=width)
plt.savefig('featureHistograms/mfcc01_hist.png')
plt.close()

#mfcc02
plt.title('Mel-Frequency Cepstral Coefficient 2 Feature Distribution')
mfcc02_hist = np.array(mfcc02)
hist, bins = np.histogram(mfcc02_hist)
width = 0.7 * (bins[1] - bins[0])
center = (bins[:-1] + bins[1:]) / 2
plt.bar(center, hist, align='center', width=width)
plt.savefig('featureHistograms/mfcc02_hist.png')
plt.close()

#mfcc03
plt.title('Mel-Frequency Cepstral Coefficient 3 Feature Distribution')
mfcc03_hist = np.array(mfcc03)
hist, bins = np.histogram(mfcc03_hist)
width = 0.7 * (bins[1] - bins[0])
center = (bins[:-1] + bins[1:]) / 2
plt.bar(center, hist, align='center', width=width)
plt.savefig('featureHistograms/mfcc03_hist.png')
plt.close()

#mfcc04
plt.title('Mel-Frequency Cepstral Coefficient 4 Feature Distribution')
mfcc04_hist = np.array(mfcc04)
hist, bins = np.histogram(mfcc04_hist)
width = 0.7 * (bins[1] - bins[0])
center = (bins[:-1] + bins[1:]) / 2
plt.bar(center, hist, align='center', width=width)
plt.savefig('featureHistograms/mfcc04_hist.png')
plt.close()

#mfcc05
plt.title('Mel-Frequency Cepstral Coefficient 5 Feature Distribution')
mfcc05_hist = np.array(mfcc05)
hist, bins = np.histogram(mfcc05_hist)
width = 0.7 * (bins[1] - bins[0])
center = (bins[:-1] + bins[1:]) / 2
plt.bar(center, hist, align='center', width=width)
plt.savefig('featureHistograms/mfcc05_hist.png')
plt.close()

#mfcc06
plt.title('Mel-Frequency Cepstral Coefficient 6 Feature Distribution')
mfcc06_hist = np.array(mfcc06)
hist, bins = np.histogram(mfcc06_hist)
width = 0.7 * (bins[1] - bins[0])
center = (bins[:-1] + bins[1:]) / 2
plt.bar(center, hist, align='center', width=width)
plt.savefig('featureHistograms/mfcc06_hist.png')
plt.close()

#mfcc07
plt.title('Mel-Frequency Cepstral Coefficient 7 Feature Distribution')
mfcc07_hist = np.array(mfcc07)
hist, bins = np.histogram(mfcc07_hist)
width = 0.7 * (bins[1] - bins[0])
center = (bins[:-1] + bins[1:]) / 2
plt.bar(center, hist, align='center', width=width)
plt.savefig('featureHistograms/mfcc07_hist.png')
plt.close()

#mfcc08
plt.title('Mel-Frequency Cepstral Coefficient 8 Feature Distribution')
mfcc08_hist = np.array(mfcc08)
hist, bins = np.histogram(mfcc08_hist)
width = 0.7 * (bins[1] - bins[0])
center = (bins[:-1] + bins[1:]) / 2
plt.bar(center, hist, align='center', width=width)
plt.savefig('featureHistograms/mfcc08_hist.png')
plt.close()

#mfcc09
plt.title('Mel-Frequency Cepstral Coefficient 9 Feature Distribution')
mfcc09_hist = np.array(mfcc09)
hist, bins = np.histogram(mfcc09_hist)
width = 0.7 * (bins[1] - bins[0])
center = (bins[:-1] + bins[1:]) / 2
plt.bar(center, hist, align='center', width=width)
plt.savefig('featureHistograms/mfcc09_hist.png')
plt.close()

#mfcc10
plt.title('Mel-Frequency Cepstral Coefficient 10 Feature Distribution')
mfcc10_hist = np.array(mfcc10)
hist, bins = np.histogram(mfcc10_hist)
width = 0.7 * (bins[1] - bins[0])
center = (bins[:-1] + bins[1:]) / 2
plt.bar(center, hist, align='center', width=width)
plt.savefig('featureHistograms/mfcc10_hist.png')
plt.close()

#mfcc11
plt.title('Mel-Frequency Cepstral Coefficient 11 Feature Distribution')
mfcc11_hist = np.array(mfcc11)
hist, bins = np.histogram(mfcc11_hist)
width = 0.7 * (bins[1] - bins[0])
center = (bins[:-1] + bins[1:]) / 2
plt.bar(center, hist, align='center', width=width)
plt.savefig('featureHistograms/mfcc11_hist.png')
plt.close()

#mfcc12
plt.title('Mel-Frequency Cepstral Coefficient 12 Feature Distribution')
mfcc12_hist = np.array(mfcc12)
hist, bins = np.histogram(mfcc12_hist)
width = 0.7 * (bins[1] - bins[0])
center = (bins[:-1] + bins[1:]) / 2
plt.bar(center, hist, align='center', width=width)
plt.savefig('featureHistograms/mfcc12_hist.png')
plt.close()

#pitch
plt.title("Pitch Feature Distribution")
pitch_hist = np.array(pitch)
hist, bins = np.histogram(pitch_hist)
width = 0.7 * (bins[1] - bins[0])
center = (bins[:-1] + bins[1:]) / 2
plt.bar(center, hist, align='center', width=width)
plt.savefig('featureHistograms/pitch_hist.png')
plt.close()

#energy
plt.title("Energy Feature Distribution")
energy_hist = np.array(energy)
hist, bins = np.histogram(energy_hist)
width = 0.7 * (bins[1] - bins[0])
center = (bins[:-1] + bins[1:]) / 2
plt.bar(center, hist, align='center', width=width)
plt.savefig('featureHistograms/energy_hist.png')
plt.close()

#kurtosis
plt.title("Kurtosis Feature Distribution")
kurtosis_hist = np.array(kurtosis)
hist, bins = np.histogram(kurtosis_hist)
width = 0.7 * (bins[1] - bins[0])
center = (bins[:-1] + bins[1:]) / 2
plt.bar(center, hist, align='center', width=width)
plt.savefig('featureHistograms/kurtosis_hist.png')
plt.close()


#skewness
plt.title("Skewness Feature Distribution")
skewness_hist = np.array(skewness)
hist, bins = np.histogram(skewness_hist)
width = 0.7 * (bins[1] - bins[0])
center = (bins[:-1] + bins[1:]) / 2
plt.bar(center, hist, align='center', width=width)
plt.savefig('featureHistograms/skewness_hist.png')
plt.close()

#spread
plt.title("Spread Feature Distribution")
spread_hist = np.array(spread)
hist, bins = np.histogram(spread_hist)
width = 0.7 * (bins[1] - bins[0])
center = (bins[:-1] + bins[1:]) / 2
plt.bar(center, hist, align='center', width=width)
plt.savefig('featureHistograms/spread_hist.png')
plt.close()

#centroid
plt.title("Centroid Feature Distribution")
centroid_hist = np.array(centroid)
hist, bins = np.histogram(centroid_hist)
width = 0.7 * (bins[1] - bins[0])
center = (bins[:-1] + bins[1:]) / 2
plt.bar(center, hist, align='center', width=width)
plt.savefig('featureHistograms/centroid_hist.png')
plt.close()

#zcr
plt.title("ZCR Feature Distribution")
zcr_hist = np.array(zcr)
hist, bins = np.histogram(zcr_hist)
width = 0.7 * (bins[1] - bins[0])
center = (bins[:-1] + bins[1:]) / 2
plt.bar(center, hist, align='center', width=width)
plt.savefig('featureHistograms/zcr_hist.png')
plt.close()
