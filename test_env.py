from envs import mazewandererenv
from default_configs import defaultConfig
conf = defaultConfig()

env = mazewandererenv.Env(conf, manual_test=True)
print(env.grid_level)
#exit(1)

while 1:
    obs, reward, done, info, display = env.render(update_display=True)