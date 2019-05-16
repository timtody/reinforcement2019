from envs import MazeWandererEnv
from matplotlib import pyplot as plt

env = MazeWandererEnv.Env()

while 1:
    # render the env, get observations and rewards
    obs, reward, done, info = env.render()

    # display what MazeWanderer sees
    plt.imshow(obs["pacman"])
    plt.show()

    # pacman und ghosts have  ActionSpace = IDLE, UP, DOWN, LEFT, RIGHT
    # do some actions which will be executed the next time env.render() gets called 
    env.player.action = env.player.ActionSpace.DOWN
    env.ghost.action = env.ghost.ActionSpace.DOWN
    env.ghost2.action = env.ghost2.ActionSpace.UP
    env.ghost3.action = env.ghost3.ActionSpace.IDLE