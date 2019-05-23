from matplotlib import pyplot as plt

def pacmanAgentPerf(stepsPerGame, rewardPerGame, avgRewardPerStep):
    plt.plot(rewardPerGame)
    plt.plot(stepsPerGame)
    plt.plot(avgRewardPerStep)
    
    plt.titel("Performance: Pacman Agent")
    plt.xlabel("Game")
    plt.legend(["Total Reward", "Steps", "Avg. Reward per Step"])

    plt.show()