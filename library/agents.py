import numpy as np
from envs.replaybuffer import ReplayBuffer

class Agent():
    def __init__(self, conf, agentConf, model, name, loadWeights=False):
        self.conf = conf
        self.agentConf = agentConf
        self.name = name
        self.__setupModel(model, loadWeights=loadWeights)
        self.__initBuffers()
        self.__initLoggers()

    def __setupModel(self, model, printSummary=False, loadWeights=False):
        self.agentConf.input_x_dim = self.conf.screen_x_comp
        self.agentConf.input_y_dim = self.conf.screen_y_comp
        self.agentConf.input_shape = (self.conf.screen_y_comp, self.conf.screen_x_comp, 1)
        self.model, optimizer = model(self.agentConf)
        self.model.compile(optimizer=optimizer, loss='mse')
        self.eps = self.agentConf.eps
        if loadWeights:
            print('Loaded Weights for {0}.'.format(self.name))
            print('weights at: ', self.conf.log_dir + self.name + self.conf.weights_save_name)
            self.model.load_weights(self.conf.log_dir + self.name + self.conf.weights_save_name)
            self.eps = 0.05

        if printSummary:
            self.model.summary()
        
        if self.conf.write_conf:
            self.agentConf.writeConfigToDisk(self.conf.log_dir+self.name+"_")

    
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
    
    def storeExperience(self, oldState, newState, action, rewardIn, rewardType=0):
        self.rewardSum += rewardIn
        
        if rewardType == 0: # Regular reward
            reward = rewardIn
        elif rewardType == 1: # Current Score as reward
            reward = self.rewardSum 
        elif rewardType == 2: # "Normaized" Score
            reward = self.rewardSum / self.conf.pacman_max_reward_per_game

        self.trainBuffer.append(oldState, newState, action, reward)

    def prepForNextGame(self):
        self.rewardLog.append(self.rewardSum)
        self.rewardSum = 0
    
    def train(self, shuffle=True):
        # while True:
        # shuffle the batch 
        # Get next batch
        
        # Decay Epsilon
        if self.eps > self.conf.test_eps:
            self.eps = self.agentConf.decay_factor* self.eps
        
        stateBatch, newStateBatch, actionBatch, rewardBatch = \
            self.trainBuffer.get_random_batch(self.agentConf.train_batch_size)

        if stateBatch.size == 0:
            pass
        # make batched predicitons
        # here the rewards per state are predicted, not the states. Hence the renaming
        predRewards = self.model.predict(stateBatch)
        predNewRewards = self.model.predict(newStateBatch)

        # calculate Targets
        # note that Q(s, a) = r + alph * max(Q(s', a'))
        targetRewards = rewardBatch + self.agentConf.y * np.max(predNewRewards, axis=1)
        trainTargets = predRewards
        for i in range(0,len(actionBatch)):
            trainTargets[i,int(actionBatch[i])] = targetRewards[i]

        # Train model
        history = self.model.fit(stateBatch, trainTargets, epochs=1, verbose=0)
        loss = history.history['loss']
        self.lossLog.append(loss)

        # Reset Buffers
        #self.trainBuffer.reset()

    def saveAgentState(self):
        if self.conf.save_models:
            self.model.save((self.conf.log_dir + self.name + self.conf.model_save_name))
        if self.conf.save_weights:
            self.model.save_weights((self.conf.log_dir + self.name + self.conf.weights_save_name))
