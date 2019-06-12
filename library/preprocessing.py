#!/usr/bin/python3

'''This module contains methods for image-manipulation and data-preprocessing in general.'''

import numpy as np

def normalizeImageData(data):
    if type(data) == type(()):
        inputData = data[0].astype('float32') / 255.
        targetData = data[1].astype('float32') / 255.
        return (inputData, targetData)
    else:
        return data.astype('float32') / 255.

def denormalizeImageData(data):
    if np.any(data > 1):
        print('Warning: Trying to denormalize unnormalized data')
        return data.astype('uint8')
    else:
        return (data * 255).astype('uint8')

def convertToGrayscale(data):
    return np.dot(data[...,:3], [0.299, 0.587, 0.114])
