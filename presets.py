"""
A number of helper functions to handle reading and writing to presets.
"""


from genetics import *
import json
import os
import glob
import numpy as np

PRESETS_DIR_PATH = "data/presets/"
MASTER_CONFIG_PATH = "data/master_"
DEFAULT_CONFIG_DIR_PATH = PRESETS_DIR_PATH + "default_old/"


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
        print("Error creating directory: " + directory)


def create_preset(preset_name, config_path=DEFAULT_CONFIG_DIR_PATH):
    preset_path = "data/presets/" + preset_name + os.sep
    config = load_config(config_path)
    create_data_structure(preset_path, config)
    save_config(preset_path, config)


def load_config(config_path=MASTER_CONFIG_PATH):

    # loads .json config file

    done = False
    while not done:
        try:
            with open(config_path + "config.json") as f:
                config = json.load(f)
            done = True
        except:
            print(f"loading from {config_path} failed.")

    return config


def save_config(path, config):

    # saves .json config file

    done = False
    while not done:
        try:
            with open(path + "config.json", "w") as fp:
                json.dump(config, fp)
            done = True
        except:
            print(f"saving under {path} failed.")


def create_data_structure(preset_path, config):
    create_folder(preset_path)
    create_folder(preset_path + "initial")
    for nature in config["natures"]:
        create_initial_genes(preset_path + "initial/", config, nature)
    create_folder(preset_path + "current")


def create_initial_genes(preset_path, config, name):
    df = make_genepool(config["pop_size"])  # pull size from config here if needed
    df.to_csv(preset_path + name + ".csv")


def initialize_current(preset_path):
    create_folder(f"{preset_path}current")

    for file in glob.glob(f"{preset_path}initial/*"):
        data = load_genepool(file)
        name = file.split(os.sep)[-1]
        save_genepool(data, f"{preset_path}current{os.sep}{name}")


def create_random_indices(instr_counts):

    # get configs
    preset_path = read_preset_path()
    preset_config = load_config(preset_path)

    result = []

    for count in instr_counts:
        choice = np.random.choice(preset_config["pop_size"], count, replace=False)
        result.append(choice.tolist())

    return result


def select_genes(preset_path):
    preset_config = load_config(preset_path)
    n_samples = read_n_available_samples(MASTER_CONFIG_PATH)
    phenotypes = []
    natures = preset_config["natures"]
    for i, nature in enumerate(natures):
        data = load_genepool(preset_path + f"current{os.sep}{nature.lower()}.csv")
        for j in range(int(preset_config["instr_count"][i])):
            gene = data.iloc[
                j,
            ]
            phenotype = make_phenotype(gene, i, preset_config, n_samples)
            phenotypes.append(phenotype)

    current_phenotypes = pd.DataFrame(phenotypes)

    current_phenotypes.to_csv(f"{preset_path}current/playing.csv")


def select_genes_old(preset_path):
    preset_config = load_config(preset_path)

    indices = [[x] for x in range(len(preset_config["natures"]))]
    print(indices)
    n_samples = read_n_available_samples(MASTER_CONFIG_PATH)

    phenotypes = []

    files = glob.glob(f"{preset_path}current/*.csv")

    try:
        files.remove(f"{preset_path}current/playing.csv")
    except:
        print()

    for i, index in enumerate(indices):
        if index == []:
            continue
        file = files[i]
        data = load_genepool(file)
        for j in index:
            # get configs
            preset_config = load_config(preset_path)

            gene = data.iloc[
                j,
            ]
            phenotype = make_phenotype(gene, i, preset_config, n_samples)
            phenotypes.append(phenotype)

    current_phenotypes = pd.DataFrame(phenotypes)
    current_phenotypes.to_csv(f"{preset_path}current/playing.csv")


def create_preset_from_puppetmaster(config_dict, name):
    """
    Create complete preset folder from puppetmaster dict object
    """

    new_preset_path = f"{PRESETS_DIR_PATH}{name}/"
    create_folder(new_preset_path)

    # place config.json in folder
    save_config(new_preset_path, config_dict)

    # now create initial folder
    create_folder(f"{new_preset_path}initial")

    natures = config_dict["natures"]

    for nature in natures:
        # create initial gene pools
        create_initial_genes(f"{new_preset_path}initial/", config_dict, f"{nature}")

    initialize_current(new_preset_path)
    # the following creates playing.csv
    select_genes(new_preset_path)


# config = {"pop_size": 10, "gen_length": 4, "bpm_base": 25, "refresh_rate": 2, "max_instr_count": [1, 1, 1, 1, 1, 1, 1], "instr_count": [1, 0, 1, 1, 1, 0, 4], "speed": 1.0, "mut_rate": [0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2], "mut_eta": 0.9, "mut_indpb": 0.1, "dist_weight": 30.0, "symm_weight": 10.0, "age_weight": 1.0, "manual_optimum": [3, 7]}
# config = {"pop_size": 100, "gen_length": 4, "bpm_base": 15, "refresh_rate": 1, "natures": ["SNARE", "KICK", "HAT"], "instr_count": [1, 0, 0, 0, 1, 1, 1], "speed": 1.0, "mut_rate": [0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.8], "mut_eta": 0.9, "mut_indpb": 0.4}
# print(config)
# create_preset_from_config_file(config, "default")

# create_preset_from_puppetmaster(config, 'pup_test')
