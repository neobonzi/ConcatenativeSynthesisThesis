#!/usr/bin/python
import sys
import urllib3.contrib.pyopenssl
import urllib
import subprocess
import soundcloud
import os 
import datetime

urllib3.contrib.pyopenssl.inject_into_urllib3()

CLIENT_ID = os.environ["SOUNDCLOUD_CID"]
DOWNLOAD_PATH = os.getcwd() + '/Downloads/' 
GENRES = ['piano']
#GENRES = ['piano', 'orchestra', 'opera', 'chorus', 'rock', 'country', 'pop', 'techno', 'hip-hop', 'reggae', 'jazz', 'latin']
#GENRES = ['rock']

def fetch_urls(track) :
   return track.download_url + '?client_id=' + CLIENT_ID

client = soundcloud.Client(client_id=CLIENT_ID)
page_size = 100

if not os.path.isdir(DOWNLOAD_PATH) :
   os.mkdir(DOWNLOAD_PATH)

for genre in GENRES :
   print "Scraping for genre: " + genre

   download_file = open(DOWNLOAD_PATH + genre, 'w')

   tracks = client.get('/tracks', genres=genre, order='created_at', limit=page_size, linked_partitioning=1)

   while 1 :
      trackNum = 0
      for track in tracks.collection:
         if ( track.downloadable ) :
            download_url = fetch_urls(track)
            print("download url: " + download_url)
            download_file.write(download_url + '\n')
            filename = "tmpDownload.mp3"
            urllib.urlretrieve(url=download_url, filename=filename)
            songFile = open(filename)
            subprocess.call("ffmpeg -i tmpDownload.mp3 -ac 1 samples/" + genre + str(trackNum) + ".mp3", shell=True)
            subprocess.call("rm tmpDownload.mp3", shell=True)
            trackNum += 1
            print(tracknum)
      try:
         tracks = client.get(tracks.next_href, genres=genre, order='created_at', limit=page_size, linked_partitioning=1)
      except Exception, e:
         print 'At the end of pagination'
         download_file.close()
         break
