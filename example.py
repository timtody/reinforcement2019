from envs import mazewandererenv
from replaybuffer import ReplayBuffer
from matplotlib import pyplot as plt

env = mazewandererenv.Env()
buf = ReplayBuffer(max_buffer_size = 3)

i = 0
while 1:
    # render the env, get observations and rewards
    obs, reward, done, info = env.render()
    
    # pacman und ghosts have  ActionSpace = IDLE, UP, DOWN, LEFT, RIGHT
    # do some RL stuff - choose actions
    if i % 2 == 0:
        env.player.action = env.player.ActionSpace.DOWN
    else:
        env.player.action = env.player.ActionSpace.RIGHT
    env.ghost.action = env.ghost.ActionSpace.DOWN
    env.ghost2.action = env.ghost2.ActionSpace.UP
    env.ghost3.action = env.ghost3.ActionSpace.IDLE

    # put observations into replay buffer
    # momentan nur die action vom player
    buf.append(obs["pacman"], reward, env.player.action)
    if i == 3:
        break

    i += 1
    if done:
        env.reset()

buf.shuffle()
obs, reward, action = buf.next_batch(2)
print(obs.shape, reward.shape, action)