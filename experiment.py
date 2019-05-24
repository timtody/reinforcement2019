import numpy as np

from library import inout, config, models
from default_configs import defaultConfig, pacmanNetConfig
import plotter

from envs import mazewandererenv

import os
os.environ['KMP_DUPLICATE_LIB_OK']='True' # work around for my broken install

def runExp(*args, **kwargs):
    # Setup Config
    conf = defaultConfig()
    conf.addConfig(config.RapidConfig(*args, **kwargs))
    conf.generateDynamicEntries()
    inout.makeDir(conf.log_dir)
    inout.makeDir(conf.image_dir)
    print(conf)
    if conf.write_conf:
        conf.writeConfigToDisk(conf.log_dir)

    # Setup Models
    pacModel, pacOptimizer = models.definePacmanTestModel1(pacmanNetConfig())
    pacModel.compile(optimizer=pacOptimizer, loss='mse')
    #pacModel.summary()

    # Q-Learning Params
    y = 0.95
    eps = 0.5
    decay_factor = 0.999

    # Init Logs # Todo: replace with preallocated arrays 
    logRewardPerGame = []
    logAvgRewardPerStep = []
    logStepsPerGame = []
    
    # Init Game Env
    env = mazewandererenv.Env(levelName=conf.level_name)

    # Run
    for episodeNum in range(conf.num_episodes):
        # Print Status
        if episodeNum % 10 == 0:
            print("Episode {} of {}".format(episodeNum, conf.num_episodes))

        # Reset Game Env
        env.reset()

        # Get initial state
        obs, _, _, _ = env.render()
        obspac = np.array(obs["pacman"])
        state = np.reshape(obspac, (1,obspac.shape[0],obspac.shape[1],1))
        
        # Decay Epsilon
        eps *= decay_factor
        
        # (Re-)set game vars
        done = False
        rewardSum = 0
        numSteps = 0

        # One Game
        while not done:
            # Select Action (Epsilon-Greedy)
            if np.random.random() < eps:
                action = np.random.randint(0, 5)
            else:
                action = np.argmax(pacModel.predict(state))
            
            # Set action in Env
            env.player.action = env.player.ActionSpace(action+1)
            
            # Step game and collect reward
            reward = 0
            for _ in range(9):
                _, rewardRaw, _,_ = env.render()
                reward += rewardRaw['pacman']
            nextObs, rewardRaw, done, info = env.render()
            reward += rewardRaw["pacman"]

            # Unpack, Reshape & Set new state
            nextObs = np.array(nextObs["pacman"])
            newState = np.reshape(nextObs, (1,nextObs.shape[0], nextObs.shape[1],1))

            # Train Model
            target = reward + y * np.max(pacModel.predict(newState))
            target_vec = pacModel.predict(state)[0]
            target_vec[action] = target
            pacModel.fit(state, target_vec.reshape(-1, 5), epochs=1, verbose=0)

            # Prepare for next round
            state = newState
            numSteps += 1
            rewardSum += reward
        
        # Log
        logStepsPerGame.append((numSteps))
        logRewardPerGame.append(rewardSum)
        logAvgRewardPerStep.append(rewardSum/numSteps)
    
    # Plot Results
    plotter.pacmanAgentPerf(conf, 
                            logStepsPerGame,
                            logRewardPerGame,
                            logAvgRewardPerStep)
    
    # Return Model
    return pacModel



if __name__ == "__main__":
    runExp()