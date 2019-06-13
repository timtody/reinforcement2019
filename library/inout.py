#!/usr/bin/python3

'''This module provides io- and dataset-related methods.'''

import pickle
from os import path, makedirs, listdir
from tensorflow.keras.preprocessing import image
from imageio import imwrite, get_writer, read
from PIL import ImageDraw, Image, ImageFont
import numpy as np

from library import preprocessing as prep

def getFreeDir(pathToFolder):
    postfix = 1
    currentPath = pathToFolder + str(postfix) + '/'
    while (path.isdir(currentPath)):
        postfix += 1
        currentPath = pathToFolder + str(postfix) + '/'
    return currentPath

def makeDir(directory):
    if not path.exists(directory):
        makedirs(directory)
        return True
    else:
        return False

def saveHistory(conf, history, fileName = 'history'):
    savePath = conf.log_dir + fileName + '.pickle'
    pickle.dump(history, open(savePath,"wb"))

def loadHistory(filePath):
    try:
        history = pickle.load( open( (filePath), "rb" ) )
        return history
    except FileNotFoundError:
        return None

def saveImage(filePath, data):
    try:
        imwrite(filePath, prep.denormalizeImageData(data))
    except:
        print("Saving image to '{0}' failed.".format(filePath))

def convertScreenFramesToVideo(sourceFolder, destPath):
    fileNames = listdir(sourceFolder)
    fileNames.sort()

    writer = get_writer(destPath, fps=24)
    for name in fileNames:
        currentImage = read(sourceFolder+name)
        currentFrame = currentImage.get_data(0)
        writer.append_data(currentFrame)
    writer.close()

class VideoWriter():
    def __init__(self, destFolder, name, fps=24):
        self.writer = get_writer(destFolder + name + '.mp4', fps=fps)
        self.fps = fps
        self.destFolder = destFolder

    def appendFrame(self, image, gameInfo, tag=None):
        if tag != None:
            image = Image.fromarray(image)#.convert('RGB')
            drawer = ImageDraw.Draw(image)
            drawer.text((10,10), tag, fill=(255,255,0))
            drawer.text((360,576-40), gameInfo, fill=(255,255,0), font=ImageFont.truetype("./resources/8-BIT_WONDER.ttf", 16))

        image = np.array(image, dtype='uint8')
        self.writer.append_data(image)

    def cutHere(self, nextName):
        self.finalize()
        self.writer = get_writer(self.destFolder + nextName + '.mp4', fps=self.fps)

    def finalize(self):
        self.writer.close()

    def __del__(self):
        self.writer.close()
