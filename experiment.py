import numpy as np
from time import time

from library import inout, config, agents
from default_configs import defaultConfig, pacmanNetConfig
import plotter

from envs import mazewandererenv, replaybuffer

import os
os.environ['KMP_DUPLICATE_LIB_OK']='True' # work around for my broken install
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3' 

def runExp(*args, **kwargs):
    # Setup Config
    conf = defaultConfig()
    conf.addConfig(config.RapidConfig(*args, **kwargs))
    conf.generateDynamicEntries()
    inout.makeDir(conf.log_dir)
    inout.makeDir(conf.image_dir)
    inout.makeDir(conf.video_dir)

    # Init Logs # Todo: replace with preallocated arrays 
    logStepsPerGame = []
    logAvgStepTime = []
    logAvgTrainTime = []
    sumExperiences = 0

    if conf.record_games:
        videoLog = inout.VideoWriter(conf.video_dir, 'ep_000000')
    
    # Init Game Env
    env = mazewandererenv.Env(conf, levelName=conf.start_level_name)
    conf.pacman_max_reward_per_game =  env.numCoins * conf.pacman_reward_coin
    trainLevel = conf.start_level_name

    # Init Agents
    pacman = agents.Agent(conf, pacmanNetConfig(), 'pacman', conf.use_trained_pacman)

    # Write conf to disk
    if conf.write_conf:
        conf.writeConfigToDisk(conf.log_dir)

    # Run
    print("Training...")
    statusOut = "Game {0:05d}/{1:05d}: steps={2:07d} rewardTotal={3:04.1f} timeStepGame={4:3.4f}s timeTrainNet={5:3.4f}s"
    for episodeNum in range(conf.num_episodes):

        if conf.run_validation:
            if episodeNum % conf.test_every == 0:
                testPacman(pacman, conf, episodeNum)
            if episodeNum in conf.switch_levels:
                env = mazewandererenv.Env(conf, levelName=conf.switch_levels[episodeNum])
                conf.pacman_max_reward_per_game =  env.numCoins * conf.pacman_reward_coin

        # Reset Game Env
        env.reset()

        # Get initial state
        state, _, _, info, display = stepEnv(conf, env)
        
        # (Re-)set game vars
        done = False
        sumGameSteps = 0
        timeStepGame = 0
        timeTrain = 0

        # One Game (Training)
        while not done:
            # Select Action (Epsilon-Greedy)
            action = pacman.getAction(state)
            env.player.action = env.player.ActionSpace(action)
            
            # Random Ghosts
            env.ghost.action = env.ghost.ActionSpace(np.random.randint(0, 4))
            env.ghost2.action = env.ghost.ActionSpace(np.random.randint(0, 4))
            env.ghost3.action = env.ghost.ActionSpace(np.random.randint(0, 4))

            # Write Video Data / Debug Images
            if episodeNum % 100 == 0 and conf.save_debug_images:
                recordFrameName = "screen_ep{0:07d}_frame{1:05d}.jpg".format(episodeNum, sumGameSteps)
                env.writeScreen(conf.image_dir + recordFrameName)
            if episodeNum % 100 == 0 and conf.record_games:
                frameTag = "ep {0:06d} frame{1:04d}".format(episodeNum, sumGameSteps)
                gameInfo = "lives {0} score {1:05d}".format(info['player']['lives'], 1234)
                videoLog.appendFrame(display, gameInfo, frameTag)

            # Step game and collect reward
            startTime = time()
            newState, reward, done, info, display = stepEnv(conf, env)
            timeStepGame += time()-startTime
            
            # Train Model
            startTime = time()
            pacman.storeExperience(state, newState, action, reward, conf.pacman_reward_type)
            if pacman.trainBuffer.full():
                pacman.train()
                print('Performed a training step in',time()-startTime,'seconds.')
            
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
        
        if (episodeNum-1) % 100 == 0 and conf.record_games:
            print('cutting now', episodeNum, 'ep_{0:06d}'.format(episodeNum+99))
            videoLog.cutHere('ep_{0:06d}'.format(episodeNum+99))

        # Print some Status info
        print(statusOut.format(episodeNum+1,
                               conf.num_episodes,
                               sumGameSteps,
                               pacman.rewardSum,
                               timeStepGame/sumGameSteps,
                               timeTrain/sumGameSteps))
        
        # Prepare agents for next game round
        pacman.prepForNextGame()

        # Occasionally plot intemediate Results
        if (episodeNum + 1) % 100 == 0:
             plotTraining(conf, pacman, logStepsPerGame, logAvgStepTime, logAvgTrainTime)


    # Plot Results
    plotTraining(conf, pacman, logStepsPerGame, logAvgStepTime, logAvgTrainTime)
    videoLog.finalize()

    # Save Models
    pacman.saveAgentState()
    
    # Return Handles for Debugging
    return pacman, conf

def testPacman(pacman, conf, episodeNum):
    # Save Training Params
    trainEps = pacman.eps
    print('testing ...eps ',trainEps, conf.test_eps)
    pacman.eps = conf.test_eps

    for level in conf.test_levels:
        testEnv = mazewandererenv.Env(conf, levelName=level)

        # Get initial state
        state, _, _, _, display = stepEnv(conf, testEnv)
        
        # (Re-)set game vars
        done = False
        sumGameSteps = 0
        sumReward = 0

        while not done:
            # Select Action (Epsilon-Greedy)
            action = pacman.getAction(state)
            testEnv.player.action = testEnv.player.ActionSpace(action)
            
            # Random Ghosts
            testEnv.ghost.action = testEnv.ghost.ActionSpace(np.random.randint(0, 4))
            testEnv.ghost2.action = testEnv.ghost.ActionSpace(np.random.randint(0, 4))
            testEnv.ghost3.action = testEnv.ghost.ActionSpace(np.random.randint(0, 4))

            newState, reward, done, info, display = stepEnv(conf, testEnv)

            sumReward += reward
            sumGameSteps += 1

            if sumGameSteps > conf.max_test_steps:
                done = True

        print('Test Result ({0}): {1} reward in {2} steps.'.format(level, sumReward, sumGameSteps))

    # Restore Training Params
    pacman.eps = trainEps
    testEnv = None

def stepEnv(conf, env):
    obs, rewardRaw, done, info, display = env.render(update_display=conf.display_game)
    reward = rewardRaw["pacman"]
    state = np.reshape(obs["pacman"], (obs["pacman"].shape[0],obs["pacman"].shape[1],1))
    return state, reward, done, info, display

def plotTraining(conf, pacman, logStepsPerGame, logAvgStepTime, logAvgTrainTime):
    plotter.pacmanAgentPerf(conf, 
                            logStepsPerGame,
                            pacman.rewardLog)
    plotter.times(conf,
                  logAvgStepTime, 
                  logAvgTrainTime)
    
    plotter.modelLoss(conf,
                      pacman.lossLog,
                      pacman.name)

if __name__ == "__main__":
    runExp()