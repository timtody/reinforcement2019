import plotter
import numpy as np
from time import time
from library import inout, config, agents, models
from default_configs import defaultConfig, pacmanNetConfig
from envs import mazewandererenv, replaybuffer

class Experiment():
    def __init__(self, *args, **kwargs):
        # Setup Config
        self.conf = defaultConfig()
        self.conf.addConfig(config.RapidConfig(*args, **kwargs))
        self.conf.generateDynamicEntries()
        if self.conf.write_conf:
            self.conf.writeConfigToDisk(self.conf.log_dir)
        
        self.statusOut = "Game {0:05d}/{1:05d}: steps={2:07d} rewardTotal={3:04.1f}\
                          timeStepGame={4:3.4f}s"
        
        # Init Experiment Environment
        self.__createLogDirs__()
        self.__createLoggers__()

        # Init Game Environment
        self.gameRunner = mazewandererenv.Env(self.conf, levelName=self.conf.start_level_name)
        self.conf.pacman_max_reward_per_game =  self.gameRunner.numCoins * self.conf.pacman_reward_coin

        # Init Agents
        self.__initAgents__()
    
    def __createLogDirs__(self):
        inout.makeDir(self.conf.log_dir)
        inout.makeDir(self.conf.image_dir)
        inout.makeDir(self.conf.video_dir)
    
    def __createLoggers__(self):
        # Init Logs # Todo: replace with preallocated arrays 
        self.logStepsPerGame = []
        self.logAvgStepTime = []
        self.sumExperiences = 0

        self.logTestAvgReward = []
        self.logTestAvgSteps = []

        if self.conf.record_games:
            self.videoLog = inout.VideoWriter(self.conf.video_dir, 'ep_000000')

    def __initAgents__(self):
        self.pacman = agents.Agent(self.conf,
                                   pacmanNetConfig(),
                                   models.definePacmanTestModel1,
                                   'pacman', 
                                   self.conf.use_trained_pacman)
        self.ghost1 = agents.Agent(self.conf,
                                   pacmanNetConfig(),
                                   models.definePacmanTestModel1,
                                   'ghost1', 
                                   False)
        
    def stepEnv(self, recordScreen):
        obs, reward, done, info, display = self.gameRunner.render(update_display=self.conf.display_game, recording=recordScreen)
        state = np.reshape(obs["pacman"], (obs["pacman"].shape[0],obs["pacman"].shape[1],1))
        return state, reward, done, info, display

    def plotTraining(self):
        plotter.pacmanAgentReward(self.conf, 
                                  self.pacman.rewardLog)

        plotter.pacmanAgentSteps(self.conf, 
                                 self.logStepsPerGame)

        plotter.times(self.conf,
                      self.logAvgStepTime)

        plotter.modelLoss(self.conf,
                          self.pacman.lossLog,
                          self.pacman.name)

    def plotTesting(self):
        plotter.pacmanTestReward(self.conf, self.logTestAvgReward)
        plotter.pacmanTestSteps(self.conf, self.logTestAvgSteps)
    
    def finalize(self):
        # Plot Results
        self.plotTraining()
        self.videoLog.finalize()

        # Save Models
        self.pacman.saveAgentState()
    
    def preTrainingEpisode(self):
        # Run Test Procedure in specified Interval
        if self.conf.run_validation and self.episodeNum % self.conf.test_every == 0:
            testAvgReward, testAvgSteps = self.testPacman(self.episodeNum)
            self.logTestAvgReward.append(testAvgReward)
            self.logTestAvgSteps.append(testAvgSteps)
            self.plotTesting()
        
        # Switch levels as specified in config
        if self.episodeNum in self.conf.switch_levels:
            self.gameRunner = mazewandererenv.Env(self.conf, levelName=self.conf.switch_levels[self.episodeNum])
            self.conf.pacman_max_reward_per_game =  self.gameRunner.numCoins * self.conf.pacman_reward_coin
        
        # Reset Game Env
        self.gameRunner.reset()

        # Get initial state
        recordScreen = self.episodeNum % self.conf.record_every == 0 and self.conf.record_games
        state, _, _, info, display = self.stepEnv(recordScreen)

        # (Re-)set game vars
        self.gameDone = False
        self.sumGameSteps = self.timeStepGame = 0
        
        # Record first frame
        if recordScreen:
            self.videoLog.setTags(self.episodeNum, self.sumGameSteps, self.pacman.eps, info)
            self.videoLog.appendFrame(display)
        
        return recordScreen, state
    
    def postTrainingEpisode(self):
        # Log
        self.logStepsPerGame.append((self.sumGameSteps))
        self.logAvgStepTime.append(self.timeStepGame/self.sumGameSteps)

        if (self.episodeNum-1) % self.conf.record_every == 0 and self.conf.record_games:
            print('cutting now', self.episodeNum, 'ep_{0:06d}'.\
                format(self.episodeNum+self.conf.record_every-1))
            videoLog.cutHere('ep_{0:06d}'.format(self.episodeNum+self.conf.record_every-1))
        
        # Print some Status info
        print(self.statusOut.format(self.episodeNum+1,
                               self.conf.num_episodes,
                               self.sumGameSteps,
                               pacman.rewardSum,
                               self.timeStepGame/self.sumGameSteps))
        
        # Prepare agents for next game round
        if self.trainingPacman:
            self.pacman.prepForNextGame()
            self.ghost1.prepForNextGame(decayEps=False)
        else:
            self.pacman.prepForNextGame(decayEps=False)
            self.ghost1.prepForNextGame()
        
        # Occasionally plot intermediate Results
        if (self.self.episodeNum + 1) % 100 == 0:
             self.plotTraining()
        
        self.episodeNum += 1
        
    def run(self):
        print("Training...")
        for episodeNum in range(self.conf.num_episodes):
            recordScreen, state = self.preTrainingEpisode()

            # One Game (Training)
            while not self.gameDone:
                # Select Action (Epsilon-Greedy)
                action = self.pacman.getAction(state)
                self.gameRunner.player.action = self.gameRunner.player.ActionSpace(action)

                # Non Random Ghosts
                actionGhost1 = self.ghost1.getAction(state)
                self.gameRunner.ghost.action = self.gameRunner.ghost.ActionSpace(actionGhost1)

                # Step game and collect reward
                startTime = time()
                newState, reward, self.gameDone, info, display = self.stepEnv(recordScreen)
                self.timeStepGame += time()-startTime

                if (episodeNum // self.conf.n_games_per_agent) % 2 == 0:
                    #training pac man for n_games_per_agent episodes
                    self.trainingPacman = True       
                    self.pacman.storeExperience(
                        state,
                        newState, 
                        action, 
                        reward["pacman"], 
                        self.conf.pacman_reward_type)
                    # dirty: log experience for ghost here
                    # todo: find a better way of designing 
                    # the adversarial architecture
                    self.ghost1.rewardSum += reward["ghosts"][0]
                    if self.pacman.trainBuffer.full():
                        self.pacman.train()
                        print('Performed a Pacman training\
                             step in',time()-startTime,'seconds.')
                else:
                    # train ghost for n_games_per_agent episodes   
                    self.trainingPacman = False 
                    self.ghost1.storeExperience(
                        state, 
                        newState, 
                        actionGhost1, 
                        reward["ghosts"][0])
                    # dirty: log experience for pacman here
                    # todo: find a better way of designing
                    # the adversarial architecture
                    self.pacman.rewardSum += reward["pacman"]
                    if self.ghost1.trainBuffer.full():
                        self.ghost1.train()
                        print('Performed a Ghost training\
                             step in',time()-startTime,'seconds.')

                # Prepare for next round
                state = newState

                # Logging
                self.sumGameSteps += 1
                self.sumExperiences += 1

                # Write Video Data / Debug Images
                if episodeNum % self.conf.record_every == 0 and self.conf.save_debug_images:
                    recordFrameName = "screen_ep{0:07d}_frame{1:05d}.jpg"\
                        .format(episodeNum, self.sumGameSteps)
                    self.gameRunner.writeScreen(self.conf.image_dir + recordFrameName)
                if recordScreen:
                    self.videoLog.setTags(episodeNum, self.sumGameSteps, self.pacman.eps, info)
                    self.videoLog.appendFrame(display)

                # Break if max steps reached
                if self.sumGameSteps == self.conf.max_steps_per_game:
                    self.gameDone = True

            self.postTrainingEpisode()

        self.finalize()

def testPacman(pacman, self.conf, episodeNum):
    # Save Training Params
    trainEps = pacman.eps
    print(f'testing... (current train eps {trainEps:0.3f},\
         test eps {self.conf.test_eps})')
    pacman.eps = self.conf.test_eps

    # Init Logs
    videoLog = inout.VideoWriter(self.conf.video_dir, f'test_ep{episodeNum}')
    logAvgRewardPerLevel = []
    logAvgStepsPerLevel = []

    for level in self.conf.test_levels:
        
        perLevelSumReward = 0
        perLevelSumSteps = 0
        
        for currentIteration in range(0, self.conf.test_repetitions):
            testEnv = mazewandererenv.Env(self.conf, levelName=level)

            # Get initial state
            state, _, _, info, display = self.stepEnv(testEnv, recordScreen=True)

            # (Re-)set game vars
            self.gameDone = False
            self.sumGameSteps = 0
            sumReward = 0

            # Record Frame
            frameTag = "Test at ep {0:06d} frame {1:04d} (eps={2:0.3f})".format(episodeNum, self.sumGameSteps, pacman.eps)
            gameInfo = "lives {0} score {1:05d}".format(info['player']['lives'], info["player"]["score"])
            videoLog.appendFrame(display, gameInfo, frameTag)

            while not self.gameDone:
                # Select Action (Epsilon-Greedy)
                action = pacman.getAction(state)
                testEnv.player.action = testEnv.player.ActionSpace(action)

                # Random Ghosts
                testEnv.ghost.action = testEnv.ghost.ActionSpace(np.random.randint(0, 4))
                #testEnv.ghost2.action = testEnv.ghost.ActionSpace(np.random.randint(0, 4))
                #testEnv.ghost3.action = testEnv.ghost.ActionSpace(np.random.randint(0, 4))

                newState, reward, self.gameDone, info, display = stepEnv(testEnv, recordScreen=True)

                sumReward += reward["pacman"]
                self.sumGameSteps += 1
                
                # Record Frame
                frameTag = "Test at ep {0:06d} frame {1:04d} (eps={2:0.3f})".format(episodeNum, self.sumGameSteps, pacman.eps)
                gameInfo = "lives {0} score {1:05d}".format(info['player']['lives'], info["player"]["score"])
                videoLog.appendFrame(display, gameInfo, frameTag)

                if self.sumGameSteps > self.conf.max_test_steps:
                    self.gameDone = True
            
            perLevelSumReward += sumReward
            perLevelSumSteps += self.sumGameSteps

            print('Test Result ({0}): {1} reward in {2} steps.'.format(level, sumReward, self.sumGameSteps))

        logAvgRewardPerLevel.append(perLevelSumReward/self.conf.test_repetitions)
        logAvgStepsPerLevel.append(perLevelSumSteps/self.conf.test_repetitions)
    # Handle Logs
    videoLog.finalize()

    # Restore Training Params
    pacman.eps = trainEps
    testEnv = None

    return logAvgRewardPerLevel, logAvgStepsPerLevel

if __name__ == "__main__":
    runExp()
