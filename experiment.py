import numpy as np
from time import time

from library import inout, config, agents, models
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

    logTestAvgReward = []
    logTestAvgSteps = []

    if conf.record_games:
        videoLog = inout.VideoWriter(conf.video_dir, 'ep_000000')
    
    # Init Game Env
    env = mazewandererenv.Env(conf, levelName=conf.start_level_name)
    conf.pacman_max_reward_per_game =  env.numCoins * conf.pacman_reward_coin
    trainLevel = conf.start_level_name

    # Init Agents
    pacman = agents.Agent(conf,
                          pacmanNetConfig(),
                          models.definePacmanTestModel1,
                          'pacman', 
                          conf.use_trained_pacman)
    ghost1 = agents.Agent(conf,
                          pacmanNetConfig(),
                          models.definePacmanTestModel1,
                          'ghost1', 
                          False)

    # Write conf to disk
    if conf.write_conf:
        conf.writeConfigToDisk(conf.log_dir)

    # Run
    print("Training...")
    statusOut = "Game {0:05d}/{1:05d}: steps={2:07d} rewardTotal={3:04.1f} timeStepGame={4:3.4f}s timeTrainNet={5:3.4f}s"
    for episodeNum in range(conf.num_episodes):

        if conf.run_validation and episodeNum % conf.test_every == 0:
            testAvgReward, testAvgSteps = testPacman(pacman, conf, episodeNum)
            logTestAvgReward.append(testAvgReward)
            logTestAvgSteps.append(testAvgSteps)
            plotTesting(conf, logTestAvgReward, logTestAvgSteps)
        
        if episodeNum in conf.switch_levels:
            env = mazewandererenv.Env(conf, levelName=conf.switch_levels[episodeNum])
            conf.pacman_max_reward_per_game =  env.numCoins * conf.pacman_reward_coin

        # Reset Game Env
        env.reset()

        # Get initial state
        recordScreen = episodeNum % conf.record_every == 0 and conf.record_games
        state, _, _, info, display = stepEnv(conf, env, recordScreen)

        # Record first frame
        if recordScreen:
            frameTag = "Training ep {0:06d} frame {1:04d} (eps={2:0.3f})".format(episodeNum, 0, pacman.eps)
            gameInfo = "lives {0} score {1:05d}".format(info['player']['lives'], info["player"]["score"])
            videoLog.appendFrame(display, gameInfo, frameTag)
        
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
            
            # Non Random Ghosts
            actionGhost1 = ghost1.getAction(state)
            env.ghost.action = env.ghost.ActionSpace(actionGhost1)

            # Random Ghosts
            #env.ghost2.action = env.ghost.ActionSpace(np.random.randint(0, 4))
            #env.ghost3.action = env.ghost.ActionSpace(np.random.randint(0, 4))

            # Step game and collect reward
            startTime = time()
            newState, reward, done, info, display = stepEnv(conf, env, recordScreen)
            timeStepGame += time()-startTime
            
            # Train Model
            startTime = time()
            pacman.storeExperience(state, newState, action, reward["pacman"], conf.pacman_reward_type)

            if pacman.trainBuffer.full() and (episodeNum < conf.pacman_train_limit):
                pacman.train()
                print('Performed a Pacman training step in',time()-startTime,'seconds.')
            
            if episodeNum >= conf.pacman_train_limit:
                rewardGhost1 = (1000-info["ghosts"][0])/1000-0.2+reward["ghosts"][0]*0.02
                ghost1.storeExperience(state, newState, actionGhost1, rewardGhost1)
            
            if ghost1.trainBuffer.full():
                ghost1.train()
                print('Performed a Ghost training step in',time()-startTime,'seconds.')
            
            timeTrain += time()-startTime

            # Prepare for next round
            state = newState

            # Logging
            sumGameSteps += 1
            sumExperiences += 1

            # Write Video Data / Debug Images
            if episodeNum % conf.record_every == 0 and conf.save_debug_images:
                recordFrameName = "screen_ep{0:07d}_frame{1:05d}.jpg".format(episodeNum, sumGameSteps)
                env.writeScreen(conf.image_dir + recordFrameName)
            if recordScreen:
                frameTag = "Training ep {0:06d} frame {1:04d} (eps={2:0.3f})".format(episodeNum, sumGameSteps, pacman.eps)
                gameInfo = "lives {0} score {1:05d}".format(info['player']['lives'], info["player"]["score"])
                videoLog.appendFrame(display, gameInfo, frameTag)

            # Break if max steps reached
            if sumGameSteps == conf.max_steps_per_game:
                done = True
        
        # Log
        logStepsPerGame.append((sumGameSteps))
        logAvgStepTime.append(timeStepGame/sumGameSteps)
        logAvgTrainTime.append(timeTrain/sumGameSteps)
        
        if (episodeNum-1) % conf.record_every == 0 and conf.record_games:
            print('cutting now', episodeNum, 'ep_{0:06d}'.format(episodeNum+conf.record_every-1))
            videoLog.cutHere('ep_{0:06d}'.format(episodeNum+conf.record_every-1))

        # Print some Status info
        print(statusOut.format(episodeNum+1,
                               conf.num_episodes,
                               sumGameSteps,
                               pacman.rewardSum,
                               timeStepGame/sumGameSteps,
                               timeTrain/sumGameSteps))
        
        # Prepare agents for next game round
        if episodeNum < conf.pacman_train_limit:
            pacman.prepForNextGame()
            ghost1.prepForNextGame(decayEps=False)
        else:
            pacman.prepForNextGame(decayEps=False)
            ghost1.prepForNextGame()

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
    print(f'testing... (current train eps {trainEps:0.3f}, test eps {conf.test_eps}) ')
    pacman.eps = conf.test_eps

    # Init Logs
    videoLog = inout.VideoWriter(conf.video_dir, f'test_ep{episodeNum}')
    logAvgRewardPerLevel = []
    logAvgStepsPerLevel = []

    for level in conf.test_levels:
        
        perLevelSumReward = 0
        perLevelSumSteps = 0
        
        for currentIteration in range(0, conf.test_repetitions):
            testEnv = mazewandererenv.Env(conf, levelName=level)

            # Get initial state
            state, _, _, info, display = stepEnv(conf, testEnv, recordScreen=True)

            # (Re-)set game vars
            done = False
            sumGameSteps = 0
            sumReward = 0

            # Record Frame
            frameTag = "Test at ep {0:06d} frame {1:04d} (eps={2:0.3f})".format(episodeNum, sumGameSteps, pacman.eps)
            gameInfo = "lives {0} score {1:05d}".format(info['player']['lives'], info["player"]["score"])
            videoLog.appendFrame(display, gameInfo, frameTag)

            while not done:
                # Select Action (Epsilon-Greedy)
                action = pacman.getAction(state)
                testEnv.player.action = testEnv.player.ActionSpace(action)

                # Random Ghosts
                testEnv.ghost.action = testEnv.ghost.ActionSpace(np.random.randint(0, 4))
                #testEnv.ghost2.action = testEnv.ghost.ActionSpace(np.random.randint(0, 4))
                #testEnv.ghost3.action = testEnv.ghost.ActionSpace(np.random.randint(0, 4))

                newState, reward, done, info, display = stepEnv(conf, testEnv, recordScreen=True)

                sumReward += reward["pacman"]
                sumGameSteps += 1
                
                # Record Frame
                frameTag = "Test at ep {0:06d} frame {1:04d} (eps={2:0.3f})".format(episodeNum, sumGameSteps, pacman.eps)
                gameInfo = "lives {0} score {1:05d}".format(info['player']['lives'], info["player"]["score"])
                videoLog.appendFrame(display, gameInfo, frameTag)

                if sumGameSteps > conf.max_test_steps:
                    done = True
            
            perLevelSumReward += sumReward
            perLevelSumSteps += sumGameSteps

            print('Test Result ({0}): {1} reward in {2} steps.'.format(level, sumReward, sumGameSteps))

        logAvgRewardPerLevel.append(perLevelSumReward/conf.test_repetitions)
        logAvgStepsPerLevel.append(perLevelSumSteps/conf.test_repetitions)
    # Handle Logs
    videoLog.finalize()

    # Restore Training Params
    pacman.eps = trainEps
    testEnv = None

    return logAvgRewardPerLevel, logAvgStepsPerLevel

def stepEnv(conf, env, recordScreen):
    obs, reward, done, info, display = env.render(update_display=conf.display_game, recording=recordScreen)
    state = np.reshape(obs["pacman"], (obs["pacman"].shape[0],obs["pacman"].shape[1],1))
    return state, reward, done, info, display

def plotTraining(conf, pacman, logStepsPerGame, logAvgStepTime, logAvgTrainTime):
    plotter.pacmanAgentReward(conf, 
                            pacman.rewardLog)

    plotter.pacmanAgentSteps(conf, 
                            logStepsPerGame)

    plotter.times(conf,
                  logAvgStepTime, 
                  logAvgTrainTime)
    
    plotter.modelLoss(conf,
                      pacman.lossLog,
                      pacman.name)

def plotTesting(conf, logTestAvgReward, logTestAvgSteps):
    plotter.pacmanTestReward(conf, logTestAvgReward)
    plotter.pacmanTestSteps(conf, logTestAvgSteps)

if __name__ == "__main__":
    runExp()