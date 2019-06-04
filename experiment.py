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
    sumExperiences = 0
    
    # Init Game Env
    env = mazewandererenv.Env(levelName=conf.level_name)

    # Init Agents
    pacman = agents.Agent(conf, pacmanNetConfig(), 'pacman', conf.use_trained_pacman)

    # Run
    print("Training...")
    statusOut = "Game {0:05d}/{1:05d}: steps={2:07d} rewardTotal={3:04.1f} timeStepGame={4:3.4f}s timeTrainNet={5:3.4f}s"
    for episodeNum in range(conf.num_episodes):
        # Reset Game Env
        env.reset()

        # Get initial state
        state, _, _, _ = stepEnv(conf, env)
        
        # (Re-)set game vars
        done = False
        sumGameSteps = 0
        timeStepGame = 0
        timeTrain = 0

        # One Game
        while not done:
            # Select Action (Epsilon-Greedy)
            action = pacman.getAction(state)
            env.player.action = env.player.ActionSpace(action)
            
            # Random Ghosts
            env.ghost.action = env.ghost.ActionSpace(np.random.randint(0, 4))
            env.ghost2.action = env.ghost.ActionSpace(np.random.randint(0, 4))
            env.ghost3.action = env.ghost.ActionSpace(np.random.randint(0, 4))
            
            # Step game and collect reward
            startTime = time()
            newState, reward, done, info = stepEnv(conf, env)
            timeStepGame += time()-startTime

            # Train Model
            startTime = time()
            pacman.trainWithSinglePair(state, newState, action, reward)
            pacman.storeExperience(state, newState, action, reward)
            #if (sumExperiences +1) % pacman.trainDelay == 0:
            #    pacman.train()
            #    print('Performed a training step in',time()-startTime,'seconds.')
            
            timeTrain += time()-startTime

            # Prepare for next round
            state = newState

            # Logging
            sumGameSteps += 1
            sumExperiences += 1

            # Break if max steps reached
            if sumGameSteps == conf.max_steps_per_game:
                done = True
        
        # Log
        logStepsPerGame.append((sumGameSteps))
        logAvgStepTime.append(timeStepGame/sumGameSteps)
        logAvgTrainTime.append(timeTrain/sumGameSteps)

        # Print some Status info
        print(statusOut.format(episodeNum+1,
                               conf.num_episodes,
                               sumGameSteps,
                               pacman.rewardSum,
                               timeStepGame/sumGameSteps,
                               timeTrain/sumGameSteps))
        
        # Prepare agents for next game round
        pacman.prepForNextGame()


    
    # Plot Results
    plotter.pacmanAgentPerf(conf, 
                            logStepsPerGame,
                            pacman.rewardLog)
    plotter.times(conf,
                  logAvgStepTime, 
                  logAvgTrainTime)
    
    # Save Models
    pacman.saveAgentState()
    
    # Return Handles for Debugging
    return pacman, conf

def stepEnv(conf, env):
    obs, rewardRaw, done, info, display = env.render(update_display=conf.display_game)
    #from matplotlib import pyplot as plt
    #plt.imshow(display)
    #plt.show()
    reward = rewardRaw["pacman"]
    state = np.reshape(obs["pacman"], (obs["pacman"].shape[0],obs["pacman"].shape[1],1))
    return state, reward, done, info

if __name__ == "__main__":
    runExp()