import numpy as np
import math

from time import time

from envs.level import Level

# Grid Level Int Codes
# value = -1 (char 'P'): Wall
# value = -2 (char ' '): Coin
# value = -3 (char 'X'): Free Space
# value = -4 (char 'W'): Pacman
# value < -4 (char 'G'): Ghosts

maxX = 0
maxY = 0

def convertLevelFileToGrid(level, printLevel=False):
    level = level.string_representation
    
    xDim = len(level)
    yDim = len(level[0])

    levelGrid = np.zeros((xDim,yDim), dtype=int)

    ghostCounter = 0
    for x in range(xDim):
        for y in range(yDim):
            currentChar = level[x][y]
            if currentChar == 'P':
                fieldValue = -1
            elif currentChar == ' ':
                fieldValue = -2
            elif currentChar == 'X':
                fieldValue = -3
            elif currentChar == 'W':
                fieldValue = -4
            elif currentChar == 'G':
                fieldValue = -5 - ghostCounter
                ghostCounter += 1
            levelGrid[x, y] = fieldValue

    if printLevel:
        print(levelGrid)
    return levelGrid

def shortestPathDist(levelGrid, start, target):
    levelGrid[start] = -5
    levelGrid[target] = -4
    if start != target:
        return explore(levelGrid, start, target)
    else:
        return 0, levelGrid

def explore(levelGrid, currentPos, target, currentSteps = 1):
    minSteps = math.inf
    targetFound = False
    for delta in [(+1,0),(0,+1),(0,-1),(-1,0)]:
        expX = currentPos[0] + delta[0]
        expY = currentPos[1] + delta[1]
        try:
            valueOnNewPos = levelGrid[expX, expY]
            if target[0] == expX and target[1] == expY and minSteps > currentSteps:
                minSteps = currentSteps
                targetFound = True
                #print('Yeah', minSteps)
        except IndexError:
            print('Well, shit')
    
    if not targetFound:
        levelGrid[currentPos] = currentSteps -1
        for delta in [(+1,0),(0,+1),(0,-1),(-1,0)]:
            expX = currentPos[0] + delta[0]
            expY = currentPos[1] + delta[1]
            
            if (expX >= 0) and (expY >= 0):
                try:
                    valueOnNewPos = levelGrid[expX, expY]
                    if valueOnNewPos != -1 and (valueOnNewPos > currentSteps or valueOnNewPos < 0): # If Pos is not a Wall
                        steps, levelGrid = explore(levelGrid,
                                           (expX, expY),
                                           target,
                                           currentSteps=(currentSteps + 1))
                        if steps < minSteps:
                            minSteps = steps
                except IndexError:
                    "Wohoo"
    return minSteps, levelGrid

                

reps = 100
sumDuration = 0
for i in range(reps):
    level = Level("FullSingle")
    levelGrid = convertLevelFileToGrid(level)

    startTime = time()
    lenPath, levelGrid = shortestPathDist(levelGrid, (2,2), (8,13))
    duration = time() - startTime
    sumDuration += duration
avgDuration = duration / reps

print('Result:')
print('time', duration)
print(levelGrid)
print(lenPath)


