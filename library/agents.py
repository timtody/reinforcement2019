from envs.replaybuffer import ReplayBuffer
from library import models
import numpy as np

class Agent():
    def __init__(self,conf, agentConf, name):
        self.conf = conf
        self.agentConf = agentConf
        self.name = name
        self.__setupModel()
        self.__initBuffers()
        self.__initLoggers()

    def __setupModel(self, printSummary=False):
        self.model, optimizer = models.definePacmanTestModel1(self.agentConf)
        self.model.compile(optimizer=optimizer, loss='mse')
        if printSummary:
            self.model.summary()
        self.eps = self.agentConf.eps
    
    def __initBuffers(self):
        self.trainBuffer = ReplayBuffer(self.agentConf.replay_buffer_size)
        self.trainBufferB = ReplayBuffer(self.agentConf.replay_buffer_size)

    def __initLoggers(self):
        # Todo: replace with preallocated arrays 
        self.rewardLog = []
        self.rewardSum = 0
    
    def getAction(self, state):
        if np.random.random() < self.eps:
                action = np.random.randint(0, self.agentConf.num_actions)
        else:
            singleState = np.reshape(state, (1,state.shape[0],state.shape[1],1))
            action = np.argmax(self.model.predict(singleState))
        return action
    
    def storeExperience(self, oldState, newState, action, reward):
        self.rewardSum += reward
        self.trainBuffer.append(oldState, reward, action)
        self.trainBufferB.append(newState, reward, action)

    def prepForNextGame(self):
        self.rewardLog.append(self.rewardSum)
        self.rewardSum = 0
        # Decay Epsilon
        self.eps *= self.agentConf.decay_factor
    
    def trainWithSinglePair(self, state, newState, action, reward):
        state = np.reshape(state, (1,state.shape[0],state.shape[1],1))
        newState = np.reshape(state, (1,newState.shape[0], newState.shape[1],1))
        target = reward + self.agentConf.y * np.max(self.model.predict(newState))
        target_vec = self.model.predict(state)[0]

        target_vec[action] = target
        self.model.fit(state, target_vec.reshape(-1, self.agentConf.num_actions), epochs=1, verbose=0)

