from envs.replaybuffer import ReplayBuffer
from library import models
import numpy as np

class Agent():
    def __init__(self,conf, agentConf, name, loadWeights=False):
        self.conf = conf
        self.agentConf = agentConf
        self.name = name
        self.__setupModel(loadWeights=loadWeights)
        self.__initBuffers()
        self.__initLoggers()

    def __setupModel(self, printSummary=False, loadWeights=False):
        self.model, optimizer = models.definePacmanTestModel1(self.agentConf)
        self.model.compile(optimizer=optimizer, loss='mse')
        self.eps = self.agentConf.eps
        if loadWeights:
            print('Loaded Weights for {0}.'.format(self.name))
            self.model.load_weights(self.conf.log_dir + self.name + self.conf.weights_save_name)
            self.eps = 0

        if printSummary:
            self.model.summary()

        self.trainDelay = self.agentConf.num_train_after_experiences
    
    def __initBuffers(self):
        self.trainBuffer = ReplayBuffer(self.agentConf.input_shape, self.agentConf.replay_buffer_size)

    def __initLoggers(self):
        # Todo: replace with preallocated arrays 
        self.lossLog = []
        self.actionLog = []
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
        self.trainBuffer.append(oldState, newState, action, reward)

    def prepForNextGame(self):
        self.rewardLog.append(self.rewardSum)
        self.rewardSum = 0
        # Decay Epsilon
        self.eps *= self.agentConf.decay_factor
    
    def trainWithSinglePair(self, state, newState, action, reward):
        # Reshape states to fit network
        state = np.reshape(state, (1,state.shape[0],state.shape[1],1))
        newState = np.reshape(state, (1,newState.shape[0], newState.shape[1],1))
        reward = self.rewardSum / self.conf.pacman_max_reward_per_game
        target = reward + self.agentConf.y * np.max(self.model.predict(newState))
        targetVec = self.model.predict(state)[0]

        targetVec[action] = target
        trainTarget = targetVec.reshape(-1, self.agentConf.num_actions) # shape from (num_action,) to (1,num_action)
        history = self.model.fit(state, trainTarget, epochs=1, verbose=0)
        loss = history.history['loss']
        self.lossLog.append(loss)


    def train(self):
        done = False
        while not done:
            # Workaround for broken buffer / Get next batch
            stateBatch, newStateBatch, actionBatch, rewardBatch = self.trainBuffer.next_batch(self.agentConf.train_batch_size)
            done = True
            
            # Make batched predicitons
            predStates = self.model.predict(stateBatch)
            predNewStates = self.model.predict(newStateBatch)

            # Calculate Targets
            targetRewards = rewardBatch + self.agentConf.y * np.max(predNewStates, axis=1)
            trainTargets = predStates
            for i in range(0,len(actionBatch)):
                trainTargets[i,actionBatch[i]] = targetRewards[i]

            # Train model
            self.model.fit(stateBatch, trainTargets, epochs=1, verbose=0)
        # Reset Buffers
        self.trainBuffer.reset()

    def saveAgentState(self):
        if self.conf.save_models:
            self.model.save((self.conf.log_dir + self.name + self.conf.model_save_name))
        if self.conf.save_weights:
            self.model.save_weights((self.conf.log_dir + self.name + self.conf.weights_save_name))

