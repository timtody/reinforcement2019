from matplotlib import pyplot as plt

def pacmanAgentPerf(conf, stepsPerGame, rewardPerGame, avgRewardPerStep):
    x = list(range(1,len(stepsPerGame)+1))
    
    fig, ax1 = plt.subplots()
    
    ax1.plot(x, rewardPerGame)
    ax1.plot(x, avgRewardPerStep)
    ax1.set_ylabel('Reward')
    plt.legend(["Total Reward", "Avg. Reward per Step"])

    ax2 = ax1.twinx()
    ax2.plot(x, stepsPerGame, 'b')
    ax2.set_ylabel('Steps', color='b')
    ax2.tick_params('y', colors='b')
    
    plt.title("Performance: Pacman Agent")
    plt.xlabel("Game")
    plt.xlim((1,len(stepsPerGame)))
    
    if conf.save_plots:
        plt.savefig(conf.log_dir + 'pacmanPerf.png')

    if conf.show_plots:
        plt.show()
    