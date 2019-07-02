#!/usr/bin/python3

'''Configure parameters for the experiments'''

from library.config import RapidConfig

#### Network Configs
def pacmanNetConfig():
    rc = RapidConfig()

    # Network input/output shape
    rc.input_x_dim = 72
    rc.input_y_dim = 80
    rc.input_shape = (72, 80, 1)
    rc.c_channels = 1
    rc.num_actions = 4

    rc.optimizer = 'adadelta' # other options: 'sgd', 'adam', 'adagrad'
    rc.learning_rate = 1.0

    # Q-Learning Parameters
    rc.y = 0.95
    rc.eps = 0.5
    rc.decay_factor = 0.9999

    rc.replay_buffer_size = 1500
    rc.train_batch_size = 1500
    rc.num_train_after_experiences = 1500

    return rc

#### Experiment Configs
def defaultConfig():
    rc = RapidConfig()
    
    rc.timestamp = rc.getTimestamp()

    # Training parameters
    rc.num_episodes = 5000
    rc.pacman_train_limit = 5000
    rc.n_games_per_agent = 5000
    rc.run_validation = False
    
    # Game Config
    rc.start_level_name = 'FullSingle' # Options: Full, FullSingle, Chaos, Race, Race2, Empty
    rc.switch_levels = {} # example: {5:'Chaos', 7:'FullSingle'} {<ep_num>:'<level>', <ep_num>:'<nextlevel>', ...}
    rc.pacman_start_poses=[(2,2), (15,2), (2,15),(15,15)]
    rc.display_game = True

    # Random seed
    rc.random_seed = 1

    # Test Config
    rc.test_levels = ['Race2','FullSingle', 'Chaos']
    rc.test_every = 100 # episodes
    rc.test_repetitions = 5
    rc.test_eps = 0.05
    rc.max_test_steps = 400

    # Logs & Result visualization
    rc.exp_base_dir = '/Users/jm/Experiments/'
    rc.log_dir = ['prio', "getFreeDir(self.exp_base_dir + '/rl_pacman_' + self.timestamp + '_')"]
    rc.plot_after_training = True
    rc.save_plots = True
    rc.show_plots = False
    rc.write_conf = True

    # Visual Output
    rc.save_debug_images = False
    rc.record_games = True
    rc.record_every = 100 # Episodes

    # Load & Save
    rc.load_weights = False
    rc.save_weights = True
    rc.enable_checkpoints = True
    rc.save_models = True
    rc.save_history = True
    rc.use_trained_pacman = False

    # Game Parameters
    rc.ghost_speed = 0
    rc.pacman_reward_type = 0 # Options: 0=reward, 1=rewardSum, 2=rewardsum/maxreward
    rc.pacman_lives = 3
    rc.pacman_reward_coin = 10
    rc.pacman_reward_no_coin = -1
    rc.pacman_reward_ghost = -10
    rc.pacman_max_reward_per_game = 1310 # Is overwritten by actual possible max reward
    rc.pacman_movespeed = 32
    rc.max_steps_per_game = 4000
    
    # Dynamic folder- and filenames
    rc.weights_load_path = ['dynamic', "self.log_dir + 'best_weights.h5'"]
    rc.weights_save_path = ['dynamic', "'{0}model_at_{1}_epochs_weights.h5'.format(self.log_dir, self.num_episodes)"]
    rc.weights_checkpoint_path = ['dynamic', "self.log_dir + 'best_weights.h5'"]
    rc.model_checkpoint_path = ['dynamic', "self.log_dir + 'best_model.h5'"]
    rc.image_dir = ['dynamic', "self.log_dir + 'images/'"]
    rc.video_dir = ['dynamic', "self.log_dir + 'videolog/'"]
    rc.model_save_name = '_model.h5'
    rc.weights_save_name = '_weights.h5'
    
    return rc

def myConfig():
    ## Init config object with all values from defaultConfig
    rc = defaultConfig()
    
    ## A few parameters that need to be overwritten

    # Base directory for logging data
    rc.exp_base_dir = '/home/jonasexp/MyExperiments/'

    ## Overwrite or add additional parameters as needed
    
    # rc.epoch = 42
    # rc.my_new_param = 'Always bring your towel!'

    ## Don't forget to return the config object!
    return rc
