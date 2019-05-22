import numpy as np

from library import inout, config, models
from default_configs import defaultConfig, pacmanNetConfig

from envs import mazewandererenv

import os
os.environ['KMP_DUPLICATE_LIB_OK']='True' # work around for my broken install

def runExp(*args, **kwargs):
    # Setup Config
    conf = defaultConfig()
    conf.addConfig(config.RapidConfig(*args, **kwargs))
    conf.generateDynamicEntries()
    #inout.makeDir(conf.log_dir)
    #inout.makeDir(conf.image_dir)
    print(conf)
    #if conf.write_conf:
    #    conf.writeConfigToDisk(conf.log_dir)

    # Setup Models
    pacModel, pacOptimizer = models.definePacmanTestModel1(pacmanNetConfig())
    pacModel.compile(optimizer=pacOptimizer, loss='mse')
    #pacModel.summary()

    # now execute the q learning
    y = 0.95
    eps = 0.5
    decay_factor = 0.999
    r_avg_list = []
    env = mazewandererenv.Env()
    for i in range(conf.num_episodes):
        env.reset()
        obs, _, _, _ = env.render()
        obspac = np.array(obs["pacman"])
        s = np.reshape(obspac, (1,obspac.shape[0],obspac.shape[1],1))
        eps *= decay_factor
        if i % 100 == 0:
            print("Episode {} of {}".format(i + 1, conf.num_episodes))
        done = False
        r_sum = 0
        while not done:
            if np.random.random() < eps:
                a = np.random.randint(0, 5)
            else:
                a = np.argmax(pacModel.predict(s))
                print('pred action', a)
            #act here
            if a == 0:
                action = env.player.ActionSpace.IDLE
            elif a == 1:
                action = env.player.ActionSpace.UP
            elif a == 2:
                action = env.player.ActionSpace.DOWN
            elif a == 3:
                action = env.player.ActionSpace.LEFT
            elif a == 4:
                action = env.player.ActionSpace.RIGHT
            env.player.action = action
            currentReward = 0
            for _ in range(9):
                _, reward, _,_ = env.render()
                currentReward += reward['pacman']
            obs, reward, done, info = env.render()
            currentReward += reward["pacman"]
            #print(currentReward)
            r = currentReward
            obspac = np.array(obs["pacman"])
            new_s = np.reshape(obspac, (1,obspac.shape[0],obspac.shape[1],1))
            target = r + y * np.max(pacModel.predict(new_s))
            target_vec = pacModel.predict(s)[0]
            target_vec[a] = target
            pacModel.fit(s, target_vec.reshape(-1, 5), epochs=1, verbose=0)
            s = new_s
            r_sum += r
        r_avg_list.append(r_sum / 1000)



if __name__ == "__main__":
    runExp()