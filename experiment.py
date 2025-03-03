import plotter
import sys
import numpy as np
from time import time
from library import inout, config, agents, models, logger
from default_configs import defaultConfig, pacmanNetConfig
from envs import mazewandererenv, replaybuffer

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

    global_step = 0
    # Run
    print("Training...")
    statusOut = "Game {0:05d}/{1:05d}: steps={2:07d} rewardTotal={3:04.1f}\
                timeStepGame={4:3.4f}s rGhost={3:04.1f}"
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

        # (Re-)set game vars
        done = False
        sumGameSteps = timeStepGame = 0
        # Record first frame
        if recordScreen:
            videoLog.setTags(episodeNum, sumGameSteps, pacman.eps, info)
            videoLog.appendFrame(display)
        
        # One Game (Training)
        while not done:
            # Select Action (Epsilon-Greedy)
            action = pacman.getAction(state)
            if conf.pacman_active:
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

            # store experience
            pacman.storeExperience(
                    state,
                    newState, 
                    action, 
                    reward["pacman"], 
                    conf.pacman_reward_type)
            
            ghost1.storeExperience(
                    state, 
                    newState, 
                    actionGhost1, 
                    reward["ghosts"][0])
            
            # train agents
            if global_step >= conf.n_prewarm_steps:
                # we dont train before we don't have enough steps accumulated
                if conf.pacman_active and ((episodeNum // conf.n_games_per_agent) % 2 == 1):
                    # train pacman
                    if global_step % conf.train_every == 0:
                        pacman.train()
                        print("pacman eps: " + str(pacman.eps))
                        print('Performed a Pacman training\
                            step in',time()-startTime,'seconds.')
                else:
                    # train ghost
                    if global_step % conf.train_every == 0:
                        ghost1.train()
                        print("ghost eps: " + str(ghost1.eps))
                        print('Performed a Ghost training\
                            step in',time()-startTime,'seconds.')
                


            # Prepare for next round
            state = newState

            # global step out
            if global_step % 100000 == 0:
                print("Training for " + str(global_step) + " steps in total.")

            # Logging
            sumGameSteps += 1
            sumExperiences += 1
            global_step += 1

            # Write Video Data / Debug Images
            if episodeNum % conf.record_every == 0 and conf.save_debug_images:
                recordFrameName = "screen_ep{0:07d}_frame{1:05d}.jpg"\
                    .format(episodeNum, sumGameSteps)
                env.writeScreen(conf.image_dir + recordFrameName)
            if recordScreen:
                videoLog.setTags(episodeNum, sumGameSteps, pacman.eps, info)
                videoLog.appendFrame(display)

            # Break if max steps reached
            if sumGameSteps == conf.max_steps_per_game:
                done = True
        
        # Log
        logStepsPerGame.append((sumGameSteps))
        logAvgStepTime.append(timeStepGame/sumGameSteps)
        
        if (episodeNum-1) % conf.record_every == 0 and conf.record_games:
            print('cutting now', episodeNum, 'ep_{0:06d}'.\
                format(episodeNum+conf.record_every-1))
            videoLog.cutHere('ep_{0:06d}'.format(episodeNum+conf.record_every-1))

        # Print some Status info
        print(statusOut.format(episodeNum+1,
                               conf.num_episodes,
                               sumGameSteps,
                               pacman.rewardSum,
                               timeStepGame/sumGameSteps,
                               ghost1.rewardSum))
        
        # Prepare agents for next game round

        pacman.prepForNextGame()
        ghost1.prepForNextGame()

        # Occasionally plot intemediate Results
        if (episodeNum + 1) % 100 == 0:
             plotTraining(conf, pacman, ghost1, logStepsPerGame,\
                  logAvgStepTime)


    # Plot Results
    plotTraining(conf, pacman, logStepsPerGame, logAvgStepTime)
    videoLog.finalize()

    # Save Models
    pacman.saveAgentState()
    ghost1.saveAgentState()

    # Return Handles for Debugging
    return pacman, conf

def testPacman(pacman, conf, episodeNum):
    # Save Training Params
    trainEps = pacman.eps
    print('testing... (current train eps ' + str(trainEps) + 'test eps ' + str(conf.test_eps) + ')')
    pacman.eps = conf.test_eps

    # Init Logs
    videoLog = inout.VideoWriter(conf.video_dir, 'test_ep' + str(episodeNum))
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

def plotTraining(conf, pacman, ghost1, logStepsPerGame, logAvgStepTime):
    plotter.pacmanAgentReward(conf, 
                            pacman.rewardLog)
    plotter.ghostAgentReward(conf, 
                            ghost1.rewardLog)
    #rewardLogSmooth = np.convolve(pacman.rewardLog, np.ones((100,))/100, mode='valid')
    #plotter.pacmanAgentReward(conf, rewardLogSmooth)

    plotter.pacmanAgentSteps(conf, 
                            logStepsPerGame)

    plotter.times(conf,
                  logAvgStepTime)
    
    plotter.modelLoss(conf,
                      pacman.lossLog,
                      pacman.name)
    
    logDump = logger.Logger(logs=[
        ('pacmanReward', pacman.rewardLog),
        ('stepsPerGame', logStepsPerGame),
        ('avgStepTime', logAvgStepTime),
        ('pacmanModelLoss', pacman.lossLog),
        ('ghostReward', ghost1.rewardLog)
    ])
    logDump.saveToDisk(conf.log_dir + "history.pickle")

def plotTesting(conf, logTestAvgReward, logTestAvgSteps):
    plotter.pacmanTestReward(conf, logTestAvgReward)
    plotter.pacmanTestSteps(conf, logTestAvgSteps)

if __name__ == "__main__":
    runExp()
