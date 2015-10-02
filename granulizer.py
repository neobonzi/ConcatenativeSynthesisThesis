import argparse
import yaafe
import eyed3
import audioop
import librosa
from pymongo import MongoClient
from pydub import AudioSegment

def main():
    args = parseArgs()
    #grainFiles = chopSound(args)
    zeroCrossingAnalysis(args)
    #analyzeGrains(grainFiles, sampleRate)

def zeroCrossingAnalysis(args):
    y, sampleRate = librosa.load(args.source)
    print("loaded")
    print(librosa.feature.zero_crossing_rate(y=y,hop_length=sampleRate * args.grainSize))
    print("done")

def storeGrains(grainFiles):
    client = MongoClient()
    db = client.audiograins
    collection = db.grains
        

def chopSound(args):
    grains = []
    audio = AudioSegment.from_mp3(args.source)
    eyed3AudioFile = eyed3.load(args.source)
    audioInfo = eyed3AudioFile.info
    audioTag = eyed3AudioFile.tag
    
    for audioIndex in xrange(0,len(audio), args.grainSize):
        #if the grain would go past the end of the sound file, just take what's left
        if audioIndex + args.grainSize > len(audio):
            grainEnd = len(audio)
            sample = audio[audioIndex:grainEnd]
        else:
            grainEnd = audioIndex + args.grainSize
            sample = audio[audioIndex:grainEnd]
 
        grainName = audioTag.title + '_' + str(audioIndex) + '-' + str(grainEnd) + '.mp3'
        tags = {"title": audioTag.title, "artist": audioTag.artist} 
        grains.append(sample.export(args.destination + '/' + grainName, format="mp3",
            tags=tags))
        print(grains[len(grains) - 1])

    return files

def parseArgs():
    parser = argparse.ArgumentParser(description='Chop up a sound file into grains and label each with appropriate id3 tag')
    parser.add_argument('source', type=str, help='The audio file to parse')
    parser.add_argument('destination', type=str, help='Where the grains should be saved')
    parser.add_argument('grainSize', type=int, help='Length of grains in mS')
    return parser.parse_args()

main()
