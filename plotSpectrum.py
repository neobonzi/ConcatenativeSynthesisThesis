import matplotlib.pyplot as plt
import matplotlib
from scipy import signal
import wave
import wavefile
import math
from pylab import plot, show, title, xlabel, ylabel, subplot
import numpy as np
from scipy.io import wavfile
from scipy import fft, arange

plt.clf()
rawSignal = wavefile.load('grains/rainforestambience_2960-2980.wav')
data = rawSignal[1][0]
fs = rawSignal[0]
#Normalize data between -1 and 1
#data = pcm2float(data, 'float32')
#Window the data
print(str(data.size))
print(str(np.hanning(data.size).size))
data = data * np.hanning(data.size)
#Print the windowed data
#Square half of the Abs FFT

freq, sp = signal.periodogram(data, fs)
#print(len(freq))
#print(len(sp))
print(freq)
#print(sp)
plt.semilogy(freq, sp)
#plt.psd(data, NFFT=len(data), pad_to=len(data), Fs=fs, window=matplotlib.mlab.window_hanning)
plt.xlabel('frequency [Hz]')
plt.ylabel('')

mostEnergy = max(sp)
mostEnergyIndex = np.where(sp == mostEnergy)[0][0]
print("Bin with most energy: \tIndex: " + str(mostEnergyIndex) + " \tValue: " + str(mostEnergy))
print("Frequency: " + str(freq[mostEnergyIndex]))

#plt.plot(freq[:(data.size / 2)], sp)
harm = freq[mostEnergyIndex]
plt.axvline(harm, color='r', linestyle='--')
harm = harm*2
plt.axvline(harm, color='r', linestyle='--')
harm = harm*2
plt.axvline(harm, color='r', linestyle='--')
#harm = harm*2
#plt.axvline(harm, color='r', linestyle='--')
#harm = harm*2
#plt.axvline(harm, color='r', linestyle='--')
#harm = harm*2
#plt.axvline(harm, color='r', linestyle='--')
#harm = harm*2
#plt.axvline(harm, color='r', linestyle='--')
#plt.show()
plt.savefig("plot.pdf")
