import numpy as np
from time import time

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
    if conf.write_conf:
        conf.writeConfigToDisk(conf.log_dir)

    # Setup Models
    pacNetConf = pacmanNetConfig()
    pacModel, pacOptimizer = models.definePacmanTestModel1(pacNetConf)
    pacModel.compile(optimizer=pacOptimizer, loss='mse')
    #pacModel.summary()

    # Q-Learning Params
    y = 0.95
    eps = 0.5
    decay_factor = 0.999

    # Init Logs # Todo: replace with preallocated arrays 
    logRewardPerGame = []
    logStepsPerGame = []
    logAvgStepTime = []
    logAvgTrainTime = []
    
    # Init Game Env
    env = mazewandererenv.Env(levelName=conf.level_name)

    # Run
    print("Training...")
    statusOut = "Game {0:05d}/{1:05d}: steps={2:07d} rewardTotal={3:04.1f} timeStepGame={4:3.4f}s timeTrainNet={5:3.2f}s"
    for episodeNum in range(conf.num_episodes):
        # Reset Game Env
        env.reset()

        # Get initial state
        obs, _, _, _ = env.render(update_display=conf.display_game)
        obspac = np.array(obs["pacman"])
        state = np.reshape(obspac, (1,obspac.shape[0],obspac.shape[1],1))
        
        # Decay Epsilon
        eps *= decay_factor
        
        # (Re-)set game vars
        done = False
        rewardSum = 0
        numSteps = 0
        timeStepGame = 0
        timeTrain = 0

        # One Game
        while not done:
            # Select Action (Epsilon-Greedy)
            if np.random.random() < eps:
                action = np.random.randint(0, pacNetConf.num_actions)
            else:
                action = np.argmax(pacModel.predict(state))
            
            # Set actions in Env
            env.player.action = env.player.ActionSpace(action)
            # Random Ghosts
            env.ghost.action = env.ghost.ActionSpace(np.random.randint(0, 4))
            env.ghost2.action = env.ghost.ActionSpace(np.random.randint(0, 4))
            env.ghost3.action = env.ghost.ActionSpace(np.random.randint(0, 4))
            
            # Step game and collect reward
            startTime = time()
            reward = 0
            #for _ in range(9):
            #    _, rewardRaw, _,_ = env.render(update_display=conf.display_game)
            #    reward += rewardRaw['pacman']
            nextObs, rewardRaw, done, info = env.render(update_display=conf.display_game)
            reward += rewardRaw["pacman"]
            timeStepGame += time()-startTime

            # Unpack, Reshape & Set new state
            nextObs = nextObs["pacman"]
            newState = np.reshape(nextObs, (1,nextObs.shape[0], nextObs.shape[1],1))

            # Train Model
            startTime = time()
            target = reward + y * np.max(pacModel.predict(newState))
            target_vec = pacModel.predict(state)[0]
            target_vec[action] = target
            pacModel.fit(state, target_vec.reshape(-1, pacNetConf.num_actions), epochs=1, verbose=0)
            timeTrain += time()-startTime

            # Prepare for next round
            state = newState

            # Logging
            numSteps += 1
            rewardSum += reward
        
        # Log
        logStepsPerGame.append((numSteps))
        logRewardPerGame.append(rewardSum)
        logAvgStepTime.append(timeStepGame/numSteps)
        logAvgTrainTime.append(timeTrain/numSteps)

        # Print some Status info
        print(statusOut.format(episodeNum+1,
                               conf.num_episodes,
                               numSteps,
                               rewardSum,
                               timeStepGame/numSteps,
                               timeTrain/numSteps))


    
    # Plot Results
    plotter.pacmanAgentPerf(conf, 
                            logStepsPerGame,
                            logRewardPerGame)
    plotter.times(conf,
                  logAvgStepTime, 
                  logAvgTrainTime)
    
    # Return Model
    return pacModel



if __name__ == "__main__":
    runExp()