import matplotlib.pyplot as plt
from pylab import plot, show, title, xlabel, ylabel, subplot
import numpy as np
from scipy.io import wavfile
from scipy import fft, arange

plt.clf()
fs, data = wavfile.read('grains/rainforestambience_38980-39000.wav')
print(data.size)
data = data * np.hanning(data.size)
sp = np.fft.fft(data)
freq = np.fft.fftfreq(data.size, d=1./fs)
print(freq)
plt.plot(freq[:(data.size / 2)], np.abs(sp[0:data.size / 2]))
plt.show()

