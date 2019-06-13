from matplotlib import pyplot as plt
import numpy as np

def pacmanAgentReward(conf, rewardPerGame):
    x = list(range(1,len(rewardPerGame)+1))
    
    fig = plt.figure()
    fig, ax1 = plt.subplots()
    
    ax1.plot(x, rewardPerGame)
    ax1.set_ylabel('Reward')
    ax1.set_xlabel("Game")
    
    plt.title("Reward: Pacman Agent")
    plt.xlim((1,len(rewardPerGame)))

    if conf.save_plots:
        plt.savefig(conf.log_dir + 'pacmanReward.png')

    if conf.show_plots:
        plt.show()
    
    plt.close(fig)

def pacmanAgentSteps(conf, stepsPerGame):
    x = list(range(1,len(stepsPerGame)+1))
    
    fig = plt.figure()
    fig, ax1 = plt.subplots()
    
    ax1.plot(x, stepsPerGame, 'orangered')
    ax1.set_ylabel('Steps')
    
    plt.title("Steps per Game")
    plt.xlim((1,len(stepsPerGame)))

    if conf.save_plots:
        plt.savefig(conf.log_dir + 'gameSteps.png')

    if conf.show_plots:
        plt.show()
    
    plt.close(fig)
    
def times(conf, avgStepTime, avgTrainTime):
    x = list(range(1,len(avgStepTime)+1))

    fig = plt.figure()

    plt.plot(avgStepTime)
    plt.plot(avgTrainTime)
    plt.legend(["Avg. Time per Game Step", "Avg. Time per Fit"])
    plt.title("Times")
    plt.ylabel("time[s]")
    plt.xlabel("Game")

    if conf.save_plots:
        plt.savefig(conf.log_dir + 'times.png')

    if conf.show_plots:
        plt.show()
    
    plt.close(fig)

def modelLoss(conf, loss, modelName):
    fig = plt.figure()
    plt.plot(loss)
    plt.title(modelName)
    plt.ylabel("loss")
    plt.xlabel("train step")

    if conf.save_plots:
        plt.savefig(conf.log_dir + modelName + '_model_loss.png')

    if conf.show_plots:
        plt.show()
    
    plt.close(fig)

def pacmanTestReward(conf, log):
    fig = plt.figure()
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


def pacmanTestSteps(conf, log):
    fig = plt.figure()
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

