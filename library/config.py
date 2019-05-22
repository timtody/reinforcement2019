#!/usr/bin/python3

'''Tools for simple config file generation. Jonas Mahn 2018'''

from types import SimpleNamespace
from datetime import datetime
from library.inout import getFreeDir

class RapidConfig(SimpleNamespace):
    def __init__(self, *args, **kwargs):
        SimpleNamespace.__init__(self)
        self.addConfig(*args, **kwargs)
    
    def __repr__(self):
        description = 'Model Parameters:\n'
        fieldNames = sorted(self.__dict__)
        for name in fieldNames:
            description = description + "field '{0}': {1}\n".format(name, str(self.__dict__[name]))
        return description 
    
    def addConfig(self, *args, **kwargs):
        for argument in args:
            if type(argument) is RapidConfig:
                fieldNames = list(argument.__dict__)
                for name in fieldNames:
                    self.__dict__[name] = argument.__dict__[name]
        
        self.__dict__.update(kwargs)

    def writeConfigToDisk(self,logDir):
        with open(logDir + "conf.txt", "w") as confFile:
            print('Model Configuration', file=confFile)
            fieldNames = sorted(self.__dict__)
            for name in fieldNames:
                print("field '" + name + "':",str(self.__dict__[name]), file=confFile)
    
    def getTimestamp(self, withTime = False):
        now = datetime.now()
        dateString = "%s-%s-%s" % (now.year,now.month,now.day)
        timeString = "%s-%s-%s" % (now.hour, now.minute, now.second)
        if withTime:
            return dateString + '-' + timeString
        else:
            return dateString

    def generateDynamicEntries(self):
        fieldNames = list(self.__dict__)
        for name in fieldNames:
            field = self.__dict__[name]
            if type(field) == type([]) and len(field) > 1 and field[0] == 'prio':
                self.__dict__[name] = eval(field[1])
        for name in fieldNames:
            field = self.__dict__[name]
            if type(field) == type([]) and len(field) > 1 and field[0] == 'dynamic':
                self.__dict__[name] = eval(field[1])
