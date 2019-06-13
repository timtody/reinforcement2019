from envs import mazewandererenv

env = mazewandererenv.Env()

obs, reward, done, info, display = env.render()

while 1:
    env.player.action = env.action_space.DOWN
    obs, reward, done, info, display = env.render()