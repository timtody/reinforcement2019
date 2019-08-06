import pickle

class Logger():
    def __init__(self, loadPath=None, logs=[]):
        for log in logs:
            self.__dict__[log[0]] = log[1]
        if loadPath != None:
            self.loadFromDisk(loadPath)
            
    def saveToDisk(self, filePath):
        saveFile = open(filePath,'wb')
        pickle.dump(self, saveFile)
        saveFile.close()
    
    def loadFromDisk(self, loadPath):
        loadFile = open(loadPath,'rb')
        loadedLog = pickle.load(loadFile)
        self.__dict__ = loadedLog.__dict__
        loadFile.close()
