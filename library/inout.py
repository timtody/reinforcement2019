#!/usr/bin/python3

'''This module provides io- and dataset-related methods.'''

import pickle
from os import path, makedirs
from tensorflow.keras.preprocessing import image
from imageio import imwrite

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
