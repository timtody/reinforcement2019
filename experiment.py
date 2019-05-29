import numpy as np
from time import time

from library import inout, config, agents
from default_configs import defaultConfig, pacmanNetConfig
import plotter

from envs import mazewandererenv, replaybuffer

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

    # Init Logs # Todo: replace with preallocated arrays 
    logStepsPerGame = []
    logAvgStepTime = []
    logAvgTrainTime = []
    
    # Init Game Env
    env = mazewandererenv.Env(levelName=conf.level_name)

    # Init Agents
    pacman = agents.Agent(conf, pacmanNetConfig(), 'pacman')

    # Run
    print("Training...")
    statusOut = "Game {0:05d}/{1:05d}: steps={2:07d} rewardTotal={3:04.1f} timeStepGame={4:3.4f}s timeTrainNet={5:3.2f}s"
    for episodeNum in range(conf.num_episodes):
        # Reset Game Env
        env.reset()

        # Get initial state
        obs, _, _, _ = env.render(update_display=conf.display_game)
        obspac = np.array(obs["pacman"])
        state = np.reshape(obspac, (obspac.shape[0],obspac.shape[1],1))
        
        # (Re-)set game vars
        done = False
        numSteps = 0
        timeStepGame = 0
        timeTrain = 0

        # One Game
        while not done:
            # Select Action (Epsilon-Greedy)
            action = pacman.getAction(state)
            
            # Set actions in Env
            env.player.action = env.player.ActionSpace(action)
            # Random Ghosts
            env.ghost.action = env.ghost.ActionSpace(np.random.randint(0, 4))
            env.ghost2.action = env.ghost.ActionSpace(np.random.randint(0, 4))
            env.ghost3.action = env.ghost.ActionSpace(np.random.randint(0, 4))
            
            # Step game and collect reward
            startTime = time()
            nextObs, rewardRaw, done, info = env.render(update_display=conf.display_game)
            reward = rewardRaw["pacman"]
            timeStepGame += time()-startTime

            # Unpack, Reshape & Set new state
            nextObs = nextObs["pacman"]
            newState = np.reshape(nextObs, (nextObs.shape[0], nextObs.shape[1],1))

            # Train Model
            startTime = time()
            pacman.storeExperience(state, newState, action, reward)
            pacman.trainWithSinglePair(state, newState, action, reward)
            #trainModel(pacModel, trainBuffer,trainBufferB, state, newState, action, reward)
            timeTrain += time()-startTime

            # Prepare for next round
            state = newState

            # Logging
            numSteps += 1
        
        # Log
        logStepsPerGame.append((numSteps))
        logAvgStepTime.append(timeStepGame/numSteps)
        logAvgTrainTime.append(timeTrain/numSteps)

        # Print some Status info
        print(statusOut.format(episodeNum+1,
                               conf.num_episodes,
                               numSteps,
                               pacman.rewardSum,
                               timeStepGame/numSteps,
                               timeTrain/numSteps))
        
        # Prepare agents for next game round
        pacman.prepForNextGame()


    
    # Plot Results
    plotter.pacmanAgentPerf(conf, 
                            logStepsPerGame,
                            logRewardPerGame)
    plotter.times(conf,
                  logAvgStepTime, 
                  logAvgTrainTime)
    
    # Return Handles for Debugging
    return pacman, conf



if __name__ == "__main__":
    runExp()