import argparse
import eyed3
import datetime
from tqdm import *
from pymongo import MongoClient
from pydub import AudioSegment

def main():
    args = parseArgs()
    grainMongoObjects = chopSound(args)
    storeGrains(grainMongoObjects)

def storeGrains(grains):
    client = MongoClient()
    db = client.audiograins
    collection = db.grains
    storedCount = 0    

    print("Storing " + str(len(grains)) + " grains")
    for grain in tqdm(grains):
        collection.insert_one(grain)       
        storedCount += 1

    print("Successfully stored " + str(storedCount) + " grains")

def chopSound(args):
    grains = []
    audio = AudioSegment.from_mp3(args.source)
    #convert to mono!
    audio.set_channels(1)
    eyed3AudioFile = eyed3.load(args.source)
    audioInfo = eyed3AudioFile.info
    audioTag = eyed3AudioFile.tag
    print("Chopping up " + str(len(audio)) + " mS audio file into " + str(args.grainSize) + " mS grains")  

    for audioIndex in tqdm(xrange(0,len(audio), args.grainSize)):
        #if the grain would go past the end of the sound file, just take what's left
        if audioIndex + args.grainSize > len(audio):
            grainEnd = len(audio)
            sample = audio[audioIndex:grainEnd]
        else:
            grainEnd = audioIndex + args.grainSize
            sample = audio[audioIndex:grainEnd]
 
        grainName = audioTag.title + '_' + str(audioIndex) + '-' + str(grainEnd) + '.mp3'
        tags = {"title": audioTag.title, "artist": audioTag.artist} 
        sample.export(args.destination + '/' + grainName, format="mp3",
            tags=tags, bitrate=str(audio.frame_rate))
        grains.append(buildGrainMongoObject(args.destination + '/' + grainName, 
            audioTag.title, audioTag.artist, args.grainSize, audio.frame_rate, sample.frame_count()))
    return grains

def buildGrainMongoObject(fileName, title, artist, length, sampleRate, frameCount):
    returnObject = {}
    if (fileName != None):
        returnObject["file"] = fileName
    
    if (title != None):
        returnObject["title"] = title
    
    if (artist != None):
        returnObject["artist"] = artist

    if (sampleRate != None):
        returnObject["sampleRate"] = sampleRate

    if (length != None):
        returnObject["length"] = str(length)

    if (frameCount != None):
        returnObject["frameCount"] = str(frameCount)

    returnObject["processed"] = False
    returnObject["date"] = datetime.datetime.utcnow()
    return returnObject


def parseArgs():
    parser = argparse.ArgumentParser(description='Chop up a sound file into grains and label each with appropriate id3 tag')
    parser.add_argument('source', type=str, help='The audio file to parse')
    parser.add_argument('destination', type=str, help='Where the grains should be saved')
    parser.add_argument('grainSize', type=int, help='Length of grains in mS')
    return parser.parse_args()

main()
