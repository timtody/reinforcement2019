from envs import mazewandererenv
from default_configs import defaultConfig
conf = defaultConfig()

env = mazewandererenv.Env(conf, manual_test=True)

while 1:
    obs, reward, done, info, display = env.render(update_display=True)
    print(env.ghost.reward)