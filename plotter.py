from matplotlib import pyplot as plt
import numpy as np

def pacmanAgentReward(conf, rewardPerGame):
    x = list(range(1,len(rewardPerGame)+1))
    
    plt.plot(x, rewardPerGame)
    plt.ylabel('Reward')
    plt.xlabel("Game")
    
    plt.title("Reward: Pacman Agent")
    plt.xlim((1,len(rewardPerGame)))

    if conf.save_plots:
        plt.savefig(conf.log_dir + 'pacmanReward.png')

    if conf.show_plots:
        plt.show()
    
    plt.close()

def ghostAgentReward(conf, rewardPerGame):
    x = list(range(1,len(rewardPerGame)+1))
    
    plt.plot(x, rewardPerGame)
    plt.ylabel('Reward')
    plt.xlabel("Game")
    
    plt.title("Reward: Ghost Agent")
    plt.xlim((1,len(rewardPerGame)))

    if conf.save_plots:
        plt.savefig(conf.log_dir + 'ghostReward.png')

    if conf.show_plots:
        plt.show()
    
    plt.close()

def pacmanAgentSteps(conf, stepsPerGame):
    x = list(range(1,len(stepsPerGame)+1))
    
    plt.plot(x, stepsPerGame, 'orangered')
    plt.ylabel('Steps')
    
    plt.title("Steps per Game")
    plt.xlim((1,len(stepsPerGame)))

    if conf.save_plots:
        plt.savefig(conf.log_dir + 'gameSteps.png')

    if conf.show_plots:
        plt.show()
    
    plt.close()
    
def times(conf, avgStepTime):
    x = list(range(1,len(avgStepTime)+1))

    plt.plot(avgStepTime)
    plt.legend(["Avg. Time per Game Step"])
    plt.title("Times")
    plt.ylabel("time[s]")
    plt.xlabel("Game")

    if conf.save_plots:
        plt.savefig(conf.log_dir + 'times.png')

    if conf.show_plots:
        plt.show()
    
    plt.close()

def modelLoss(conf, loss, modelName):
    plt.plot(loss)
    plt.title("Model loss: " + modelName)
    plt.ylabel("loss")
    plt.xlabel("train step")

    if conf.save_plots:
        plt.savefig(conf.log_dir + modelName + '_model_loss.png')

    if conf.show_plots:
        plt.show()
    
    plt.close()

def pacmanTestReward(conf, log):
    plt.title('Test Reward')
    plt.ylabel('Reward')
    plt.xlabel('Game')

    log = np.array(log)
    numTestLevels = log.shape[1]
    for i in range(numTestLevels):
        plt.plot(log[:,i])
    plt.legend(conf.test_levels)

    if conf.save_plots:
        plt.savefig(conf.log_dir + 'testing_reward.png')

    if conf.show_plots:
        plt.show()

    plt.close()


def pacmanTestSteps(conf, log):
    plt.title('Test Steps')
    plt.ylabel('Steps')
    plt.xlabel('Game')

    log = np.array(log)
    numTestLevels = log.shape[1]
    for i in range(numTestLevels):
        plt.plot(log[:,i])
    plt.legend(conf.test_levels)

    if conf.save_plots:
        plt.savefig(conf.log_dir + 'testing_steps.png')

    if conf.show_plots:
        plt.show()
    
    plt.close()
