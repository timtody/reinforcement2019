import experiment
import default_configs

# Note: Copy this file and name it ****_launch.py
#       to create a local copy with your user settings that is ignored by GIT

print('About to run an experiments...')

# Load one of the default config files
rc = default_configs.myConfig()

# Changes some parameters to fit your environment
rc.exp_base_dir = '/home/user/your/exp/dir/' # Base directory for result data, make sure it exists.

# Change any other parameter that exists in default_configs.defaultConfig() as needed.
# Create new configs and new parameters in the default_configs.py module.
rc.num_episodes = 10
rc.plot_after_training = False
rc.show_plots = False
rc.level_name = 'Race'
rc.display_game = True

# Setup for loading pacman model weights
rc.use_trained_pacman = True
rc.use_trained_ghost_master = False # Not implemented yet
rc.log_dir = "/complete/path/to/experiment/folder/you/want/to/load/from/"

# Run the experiment
model, conf = experiment.runExp(rc)

print('Done.')
