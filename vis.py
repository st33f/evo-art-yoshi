import numpy as np
import pandas as pd
from glob import glob
import matplotlib.pyplot as plt
import seaborn as sns
from config import load_config

sns.set()
sns.set_style('darkgrid')


def import_data():
    """Imports all data from all experiments by building keyed dictionaries."""

    pops, gens, experiments = {}, {}, {}

    for experiment_folder in glob(EXPERIMENTS_PATH + '\\*'):
        for gen_folder in glob(experiment_folder + "\\*"):
            for pop_file in glob(gen_folder + "\\*"):
                pop = pd.read_csv(pop_file).to_dict('index')
                pops[pop_file.split('\\')[-1].split('.')[0]] = pop
            gens[gen_folder.split('\\')[-1].split('_')[-1]] = pops
            pops = dict()
        experiments[experiment_folder.split('\\')[-1]] = gens
        gens = dict()

    return experiments


def load_experiment(data, experiment_number=None):
    """Construct a data frame from a keyed experiment dictionary."""

    print("Experiment set to highest index unless otherwise specified.")
    experiment = data[max(data.keys())] if experiment_number is None else experiment_number

    experiment = {(i, j, k): experiment[i][j][k] for i in experiment.keys()
                                                 for j in experiment[i].keys()
                                                 for k in experiment[i][j].keys()}
    df = pd.DataFrame.from_dict(experiment, orient='index')
    df.index.names = ['gen', 'nature', 'individual']
    df.columns = ['ind_number'] + list(df.columns[1:])
    df.index.set_levels(['ind{}'.format(i+1) for i in range(10)], level='individual', inplace=True)

    return df


def get_pop_keys(config):
    pop_keys = [pop_name.lower() for pop_name in config['natures']]
    pop_keys.insert(5, 'playing')
    return pop_keys


EXPERIMENTS_PATH = "experiments\\"
PRESET_PATH = "data\\presets\\default10\\"

preset_config = load_config(PRESET_PATH)

experiments = import_data()

df = load_experiment(experiments)

print(df.info())
print(df.describe())
print(df)

pop_means = df.mean(axis=0, level=['gen', 'nature']).unstack()['fitness']
gen_mean = df.mean(axis=0, level=['gen'])['fitness']

pop_means.plot()
plt.title("Mean fitness of populations")
plt.show()

gen_mean.plot()
plt.title("Mean fitness across populations")
plt.show()

pop_keys = get_pop_keys(preset_config)

for nature in pop_keys:
    for var in ['fitness', 'order']:
        data = df.swaplevel('gen','nature').xs(nature)[var].unstack()
        data.plot()
        plt.title('{} of individuals in population "{}"'.format(var, nature))
        plt.show()
