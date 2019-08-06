import library.logger as lg

fullPathToHistoryPickle = "/home/mahn/Experiments/rl_pacman/rl_pacman_2019-8-6_4/history.pickle"

logs = lg.Logger(loadPath=fullPathToHistoryPickle)

print(logs.__dict__)