from envs import mazewandererenv
from matplotlib import pyplot as plt

env = mazewandererenv.Env()

i = 0
while 1:
    i += 1
    # render the env, get observations and rewards
    obs, reward, done, info = env.render()

    # display what MazeWanderer sees
    # print((info["ghosts"][0]))
    #plt.show()
    
    # pacman und ghosts have  ActionSpace = IDLE, UP, DOWN, LEFT, RIGHT
    # do some RL stuff
    if i % 2 == 0:
        env.player.action = env.player.ActionSpace.DOWN
    else:
        env.player.action = env.player.ActionSpace.RIGHT
    env.ghost.action = env.ghost.ActionSpace.DOWN
    env.ghost2.action = env.ghost2.ActionSpace.UP
    env.ghost3.action = env.ghost3.ActionSpace.IDLE
    print(reward["pacman"])
    if i == 10:
        exit(1)