#!/usr/bin/python3

'''Configure parameters for the experiments'''

from library.config import RapidConfig

#### Network Configs
def pacmanNetConfig():
    rc = RapidConfig()

    # Network input/output shape
    rc.input_x_dim = 576
    rc.input_y_dim = 640
    rc.c_channels = 1
    rc.num_actions = 5

    rc.optimizer = 'adadelta' # other options: 'sgd', 'adam', 'adagrad'
    rc.learning_rate = 1.0

    return rc

#### Experiment Configs
def defaultConfig():
    rc = RapidConfig()
    
    rc.timestamp = rc.getTimestamp()

    # Training parameters
    rc.num_episodes = 20

    # Random seed
    rc.random_seed = 1

    # Logs & Result visualization
    rc.exp_base_dir = '/Users/jm/Experiments/'
    rc.log_dir = ['prio', "getFreeDir(self.exp_base_dir + '/rl_pacman_' + self.timestamp + '_')"]
    rc.plot_after_training = True
    rc.save_plots = True
    rc.show_plots = False
    rc.write_conf = True

    # Load & Safe
    rc.load_weights = False
    rc.save_weights = True
    rc.enable_checkpoints = True
    rc.save_model = True
    rc.save_history = True
    rc.save_debug_images = True

    # Dynamic folder- and filenames
    rc.weights_load_path = ['dynamic', "self.log_dir + 'best_weights.h5'"]
    rc.weights_save_path = ['dynamic', "'{0}model_at_{1}_epochs_weights.h5'.format(self.log_dir, self.num_episodes)"]
    rc.weights_checkpoint_path = ['dynamic', "self.log_dir + 'best_weights.h5'"]
    rc.model_checkpoint_path = ['dynamic', "self.log_dir + 'best_model.h5'"]
    rc.image_dir = ['dynamic', "self.log_dir + 'images/'"]
    rc.model_save_name = 'model.h5'
    
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
