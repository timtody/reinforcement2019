from matplotlib import pyplot as plt

def pacmanAgentPerf(conf, stepsPerGame, rewardPerGame):
    x = list(range(1,len(stepsPerGame)+1))
    
    fig, ax1 = plt.subplots()
    
    ax1.plot(x, rewardPerGame)
    ax1.set_ylabel('Reward')
    ax1.set_xlabel("Game")

    ax2 = ax1.twinx()
    ax2.plot(x, stepsPerGame, 'orangered')
    ax2.set_ylabel('Steps', color='orangered')
    ax2.tick_params(colors='orangered')
    
    plt.title("Performance: Pacman Agent")
    plt.xlim((1,len(stepsPerGame)))
    
    if conf.save_plots:
        plt.savefig(conf.log_dir + 'pacmanPerf.png')

    if conf.show_plots:
        plt.show()
    
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
