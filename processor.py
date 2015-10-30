#!/usr/bin/python
import os 
import datetime
import granulizer
import subprocess
import synthesizer

downloadFiles = ["chorus.txt", "hip-hop.txt", "latin.txt", "orchestra.txt", "pop.txt", "rock.txt", "country.txt", "jazz.txt", "opera.txt", "piano.txt", "reggae.txt", "techno.txt"]
downloadsPath = "Downloads/"

for downloadFile in downloadFiles:
    f = open(downloadsPath + downloadFile)    
    filename = "tmpDownload.mp3"
    urllib.urlretrieve(url=f.readline(), filename=filename)
    songFile = open(filename)
    subprocess.call(["ffmpeg", "-i tmpDownload.mp3", "-ac 1", "tmpDownloadMono.mp3"], shell=True)
    subprocess.call(["rm", "tmpDownload.mp3"])
    
