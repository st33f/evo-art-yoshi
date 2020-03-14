from genetics import *
#from autopilot import *
import json
import os
import glob
import numpy as np
from pathlib import Path
from genetics import MappingFunction

# todo: might be prudent to move preset class into separate preset.py and rename this to utils
# todo: import path variables to various scripts from here? rename to DEFAULT_?

PRESETS_DIR_PATH = Path('data/presets/')
MASTER_CONFIG_PATH = Path('data/master_')
DEFAULT_CONFIG_DIR_PATH = PRESETS_DIR_PATH / 'default_old/'


class Preset:
    """
    Class containing references to files associated with a preset.

    ideas:
    Use preset manager functionality on startup.
    - can load an existing preset chosen from a list of names. This initializes a
    - can initiate and name a new preset, specifying the parameters or importing a json from another preset.
      Build the required folders and set up everything needed to run.
    - can also do this during operation, generate a new preset.
    - never lose the experiment path during.

    ^ most of this already supported in existing gui. Look at implementing a step for choosing a new preset etc.,
    or synthesizing with the gui. Should be easy, actually - it updates the jsons so just initialize and refresh?

    - write docstring
    """

    def __init__(self, master_config_path=MASTER_CONFIG_PATH):

        self.master = load_config(master_config_path)
        self.path = Path(self.master['preset_path'])

        self.config = load_config(self.path)
        self.config_features() # todo: integrate into config and remove
        self.mapper = MappingFunction()

        self.experiment = None

    def update(self, master_config_path=MASTER_CONFIG_PATH, setup=True):

        self.master = load_config(master_config_path)
        self.path = Path(self.master['preset_path'])
        self.config = load_config(self.path)

    def save_experiment(self):

        self.update()

        if self.master['save_data']:

            if not self.experiment:
                self.create_experiment()

            create_folder(self.experiment / f'gen_{g}')
            self.log_params()

        else:
            self.experiment = None

    def create_experiment(self): # todo: could move to utils

        preset_name = self.path.split('\\')[-1]

        if not glob.glob(f"experiments/{preset_name}_exp_*"):
            exp_number = 0
        else:
            exp_number = max([int(f.split("\\")[-1].split("_")[-1])
                              for f in glob.glob(f"experiments/{preset_name}*")]) + 1

        exp_path = Path(f'experiments\\{preset_name}_exp_{exp_number}\\')
        create_folder(self.experiment)

        return exp_path

    def log_params(self):
        filepath = self.experiment / "params.csv"
        with filepath.open("w", encoding="utf-8") as f:
            params = ",".join([str(param) for param in self.config if type(param) is float])
            f.write(params)

    def config_features(self):
        # todo: Implement these as options/settings in the UI, once this is done this function can be removed

        self.config['parent_selection'] = random.choice(['roulette', 'tournament', 'random', 'deterministic'])
        self.config['survivor_selection'] = random.choice(['roulette', 'tournament', 'random', 'deterministic'])  # NSGA2?
        self.config['playing_selection'] = 'deterministic'
        self.config['k_parents'] = 5
        self.config['mutation'] = True
        self.config['crossover'] = False


        self.master['save_data'] = True
        self.master['recovery'] = False
        self.master['from_csv'] = False

        return self

    def __repr__(self):
        return f'master: {self.master}\npreset: {self.path}\nconfig: \n{self.config}\n'

    # todo: write a string return for debug print?



def read_preset_path(master_config_path=MASTER_CONFIG_PATH):
    master_config = load_config(master_config_path)
    return master_config["preset_path"]


def read_scaling_factor(master_config_path=MASTER_CONFIG_PATH):
    master_config = load_config(master_config_path)
    return master_config["scaling_factor"]


def read_n_available_samples(master_config_path=MASTER_CONFIG_PATH):
    master_config = load_config(master_config_path)
    return master_config["n_available_samples"]

def read_available_samples(master_config_path=MASTER_CONFIG_PATH):
    master_config = load_config(master_config_path)
    return master_config["available_samples"]


def create_folder(directory):
    try:
        if not os.path.exists(directory):
            os.makedirs(directory)
    except OSError:
        print('Error creating directory: ' + directory)


def create_preset(preset_name, config_path=DEFAULT_CONFIG_DIR_PATH):
    preset_path = 'data/presets/' + preset_name + os.sep
    config = load_config(config_path)
    create_data_structure(preset_path, config) # todo: update
    save_config(preset_path, config)


def load_config(config_path=MASTER_CONFIG_PATH):

    # loads .json config file

    done = False
    while not done:
        try:
            with open(config_path / 'config.json') as f:

                # config = json.load(f)
                config = {**json.load(f),
                          'n_available_samples': read_n_available_samples(),
                }  # todo: Comment out this line once the button is implemented in the GUI. [still needed?]

            done = True
        except:
            print(f"loading from {config_path} failed.")

    return config


def save_config(path, config):

    # saves .json config file

    done = False
    while not done:
        try:
            with open(Path(path) / 'config.json', 'w') as fp:
                json.dump(config, fp)
            done = True
        except:
            print(f"saving under {path} failed.")


def create_preset_from_puppetmaster(config_dict, name):
    '''
    Create complete preset folder from puppetmaster dict object
    '''

    new_preset_path = f'{PRESETS_DIR_PATH}{name}/'
    create_folder(new_preset_path)

    # place config.json in folder
    save_config(new_preset_path, config_dict)

    # now create initial folder
    create_folder(f'{new_preset_path}initial')

    natures = config_dict['natures']

    for nature in natures:
        # create initial gene pools
        create_initial_genes(f"{new_preset_path}initial/", config_dict, f"{nature}") # todo: update

    initialize_current(new_preset_path)
    # the following creates playing.csv
    select_genes(new_preset_path)



#config = {"pop_size": 10, "gen_length": 4, "bpm_base": 25, "refresh_rate": 2, "max_instr_count": [1, 1, 1, 1, 1, 1, 1], "instr_count": [1, 0, 1, 1, 1, 0, 4], "speed": 1.0, "mut_rate": [0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2], "mut_eta": 0.9, "mut_indpb": 0.1, "dist_weight": 30.0, "symm_weight": 10.0, "age_weight": 1.0, "manual_optimum": [3, 7]}
#config = {"pop_size": 100, "gen_length": 4, "bpm_base": 15, "refresh_rate": 1, "natures": ["SNARE", "KICK", "HAT"], "instr_count": [1, 0, 0, 0, 1, 1, 1], "speed": 1.0, "mut_rate": [0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.8], "mut_eta": 0.9, "mut_indpb": 0.4}
#print(config)
#create_preset_from_config_file(config, "default10")

#create_preset_from_puppetmaster(config, 'pup_test')