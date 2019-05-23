import experiment
import default_configs

# Note: Copy this file and name it ****_launch.py
#       to create a local copy with your user settings that is ignored by GIT

print('About to run an experiments...')

# Load one of the default config files
rc = default_configs.myConfig()

# Changes some parameters to fit your environment
rc.exp_base_dir = '/home/mahn/Experiments/' # Base directory for result data, make sure it exists.

# Change any other parameter that exists in default_configs.defaultConfig() as needed.
# Create new configs and new parameters in the default_configs.py module.
rc.num_episodes = 2
rc.plot_after_training = True
rc.show_plots = True

# Run the experiment
model = experiment.train(rc)

print('Done.')
