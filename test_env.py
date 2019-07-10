from envs import mazewandererenv
from default_configs import defaultConfig
conf = defaultConfig()

env = mazewandererenv.Env(conf)
print(env.grid_level)

obs, reward, done, info, display = env.render()

while 1:
    env.player.action = env.action_space.DOWN
    obs, reward, done, info, display = env.render()