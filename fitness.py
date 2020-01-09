"""
File that contains functions to be used in evolution2.py.
"""

import numpy as np
import pandas as pd
from math import *
from presets import *

preset_path = read_preset_path()
preset_config = load_config(preset_path)


def distance(a, b, method="euclidian"):
    """distance fitness function
    Inputs: two matching numpy arrays
    Output: a fitness value"""

    if len(b) > 1:
        dif = 100
        for i in b:
            if abs(a - i) < dif:
                dif = abs(a - i)
                nearest_b = i
        b = [nearest_b]


    if method == 'euclidian':
        fitness = sqrt(np.sum((a - b)**2))
    elif method == 'chebyshev':
        fitness = np.max(abs(a - b))
    elif method == 'taxicab':
        fitness = np.sum((a - b))

    #print('fit dist:', fitness)

    return fitness

def compute_optimum(playing, phen_cols, method="mean"):
    """
    Input: a dataframe of playing.csv containing phenes(vars) as rows(cols)
    Output: an optimum of the same dimensionality

    This function should be placed in a loop later to reinitialize the optimum.
    """

    natures = playing.loc[:, 'nature']  # save the instrument types for the instr_optima method

    playing.loc[:, ['nature', 'pitch']] = 0

    # convert pd to np
    if isinstance(playing, pd.DataFrame):
        playing = playing.values

    # compute a mean value for these that functions as an optimum
    if method == "mean":
        current_optimum = np.mean(playing, axis=0)

    elif method == "bounding_box":
        raise NotImplementedError()

    elif method == "instr_optima":
        raise NotImplementedError()

    df = pd.DataFrame([current_optimum.tolist()], columns=phen_cols)
    return df

'''
def update_age(age, next_play, verbose=False):
    """Update the age values based on comparison between the previous and current playing.csv. Returns updated ages.
    NOTE: make sure preset_path is being read correctly."""

    old_play = pd.read_csv(f'{preset_path}current/playing.csv').drop('Unnamed: 0', axis=1)
    play_changed = - next_play.eq(old_play.iloc[:len(next_play),]).all(axis=1)

    # if new items are added, extend the age list
    age = pd.concat([age, pd.DataFrame({'age': [0] * (len(next_play) - len(old_play))})])

    age[play_changed] = 0
    age += 1

    if verbose is True:
        print(age)

    return age
'''

def symmetry(ind_order, playing):

    ind_order = int(ind_order)

    play_orders = playing.loc[:, 'order']

    tuples = [(min(x, ind_order), max(x, ind_order)) for x in play_orders]
    scores = rhythm_eval(tuples)
    fitness_symm = sum(scores)/len(playing)
    #print("fit sym:", fitness_symm)

    return fitness_symm


def rhythm_eval(tuples):
    """
    Types of polyrhythms (higher score -> worse):
    - whole: score 0
    - half: score 1
    - quarter/third: score 2
    - eight/tenth: score 5
    - worse: score 10
    """

    scores = []

    for a, b in tuples:
        if (a/b) % 1 == 0:  # if whole
            score = 0
        elif (a/b) % 0.5 == 0:  # if half
            score = -3
        elif ((a/b) % 0.25 == 0) or (float(int((a/b)*100)) % 0.33 == 0):  # if quarter or third
            score = -5
        elif (a/b) % 0.125 == 0 or (a/b) % 0.1 == 0:  # if eighth or tenth
            score = 5
        else:  # everything else
            score = 10

        scores.append(score)
    #print(scores)
    return scores


def proportion(playing, pops):
    """
    proportion of specific subset (i.e. order) to what is currently playing.
    could also be seen as symmetry of this proportion

    """
    raise NotImplementedError()
    return proportion


def scramble_all(preset_path, subset=['order']):
    """Testing function that scrambles all populations and playing.csv"""

    files = [file.replace('\\', '/') for file in glob.glob(preset_path + 'current/*.csv') if 'playing' not in file]
    for file in files:
        new = scramble(pd.read_csv(file), subset).drop('Unnamed: 0', axis=1)
        new.to_csv(file)

    new = scramble_playing(pd.read_csv(f'{preset_path}current/playing.csv'), subset).drop('Unnamed: 0', axis=1)
    new.to_csv(f'{preset_path}current/playing.csv')


def scramble(population, subset):
    """Function for testing, scrambles the order numbers in the population"""

    population.loc[:, subset] = np.random.uniform(0, 1, len(population.loc[:, subset]))

    return population


def scramble_playing(playing, subset):
    """same as above but for playing.csv.
    NOTE: this only works for order right now."""

    playing.loc[:, subset] = np.random.randint(3, 12, len(playing.loc[:, subset]))

    return playing

