"""
- start/stop functionality
- load functionality: user can load population, fitness and playing from csv and initialize from there instead
- variational optima functionality: enable different optimum for each nature.
- small optimization: concat pops and fits earlier?
- still not sure about script ordering.
- look at genetics script, can clean out a lot of those functions and possibly rename to representation.py
- could try to run SonicPi thru a docker container...

experiments
- adjust pop size and mut rates. Population shouldn't be too large, as the search space will be covered
  too densely. Mut rate (and step size) should be high to allow for large variation in solutions (we DON'T want
  fast convergence, the journey is what counts! Sparsely populate the search space and allow solutions to search
  inefficiently. Try to get the system to solve things creatively (high diversity of approach) instead of efficiently.)
- if there are other interesting fitness metrics, now would be a good time to try them. Can still take a look at
  related work for inspiration.

"""


import time
import glob as glob
import random
import numpy as np
import pandas as pd
from deap import base, creator, tools
from genetics import load_genepool, random_gene # probably unused
from presets import *  #load_config
import fitness as fit
from utils_rename import c

def initIndividual(icls, content): # todo: can be made redundant (lambda)
    return icls(content)


def initPopulation(pcls, ind_init, inds): # todo: can be made redundant (lambda)
    return [pcls(ind_init(ind)) for ind in inds]


def create_toolbox(params):

    creator.create("FitnessMax", base.Fitness,
                   weights=(params['dist_weight'], params['symm_weight'], params['age_weight']))
    creator.create("Individual", list, fitness=creator.FitnessMax)

    toolbox = base.Toolbox()

    toolbox.register("individual", initIndividual, creator.Individual)
    toolbox.register("population", initPopulation, list, toolbox.individual)

    toolbox.register("evaluate_dist", fit.distance)
    toolbox.register("evaluate_symm", fit.symmetry)
    toolbox.register("mate", tools.cxTwoPoint)
    toolbox.register("mutate", tools.mutPolynomialBounded, eta=params['mut_eta'],
                     low=0., up=1., indpb=params['mut_indpb']) # todo: passing these params to the toolbox method means these don't have to be updated every loop
    # toolbox.register("mutate", tools.mutGaussian, mu=0.5, sigma=0.1, indpb=0.05)
    # toolbox.register("select", tools.selNSGA2)

    toolbox.register("tournamentSelection", tools.selTournament,params['k_parents'])
    toolbox.register("rouletteSelection", tools.selRoulette, params['k_parents'])
    toolbox.register("randomSelection", tools.selRandom, params['k_parents'])
    toolbox.register("deterministicSelection", tools.selWorst, params['k_parents'])

    return toolbox


def init_dfs(natures, pop_size): # todo: could be moved to utils, preset arg

    index = pd.MultiIndex.from_product([natures, range(pop_size)],
                                       names=['pop', 'ind'])

    pops = pd.DataFrame([random_gene(preset.master['genotype'])
                         for _ in range(pop_size) for _ in natures],
                        index=index, columns=preset.master['genotype'])

    fits = pd.DataFrame([[0] * len(natures) * pop_size] * len(preset.master['fitness_metrics']),
                        index=index, columns=preset.master['fitness_metrics'])

    return pops, fits


def evolve(pops, ages, playing):

    pops = pops.copy().sample(frac=1)
    ages = ages.loc[pops.index]

    survivors = []

    for nature in pops.index.levels[0]: # todo: check slicing, could use .xs instead

        genes = toolbox.initPopulation(pops.xs(nature, level='pop', drop_level=False) # could set drop_level to True
                                           .reset_index(drop=False).tolist())
        pop_fits = evaluate(genes, playing, ages=ages.loc[nature])
        pop = fit.attach(genes, pop_fits)

        offspring = reproduce(pop, playing)
        survivors += select(pop + offspring, preset.config['survivor_selection'])

    # todo: check if fits saving works
    index = pd.MultiIndex.from_tuples([tuple(ind[:2]) for ind in c(survivors)], names=['pop', 'ind'])
    pops = pd.DataFrame(survivors, index=index, columns=pops.columns)
    fits = pd.DataFrame([ind.fitness.values for ind in c(survivors)],
                        index=index, columns=preset.master['fitness_metrics'])

    # todo: implement crossover as an optional feature?

    return pops, fits


def evaluate(pop, playing, ages=False):
    """
    :param genes: a list of individual genes
    :param playing: DataFrame of currently playing individuals
    :param ages: If filled, an ordered age column. Else, age is assumed to be 0 for all individuals
    :return: a list of individual genes with attached fitness values, fit_df entries
    """
    distance = [fit.distance(gene, preset.config['optimum']) for gene in pop]
    symmetry = [fit.symmetry(gene, playing) for gene in pop]

    if ages: #todo: check
        ages = (ages + 1).values()
    else:
        ages = [0] * len(pop)

    fits = zip([distance, symmetry, ages])

    return fits


def reproduce(pop, playing):

    pop_indices = [ind[0] for ind in pop]
    mut_indices = [i + 1 for i in range(preset.config['pop_size'] + preset.config['k_offspring'])
                   if i + 1 not in pop_indices] # todo: check if index starts from 1

    selected = select(pop, preset.config['parent_selection'])
    parents = [toolbox.clone(ind) for ind in selected]

    offspring = [[ind[0], mut_indices[i]] + toolbox.mutate(ind[2:])
                 for i, ind in enumerate(parents)]

    return evaluate(offspring, playing)


def select(pop, selection_method):
    # todo: check indexing of these dfs.
    # todo: implement weights for fitness, check how deap does multi objective.

    if selection_method == 'random':
        return toolbox.randomSelection(pop)

    elif selection_method == 'tournament':
        return toolbox.tournamentSelection(pop)

    elif selection_method == 'roulette':
        return toolbox.rouletteSelection(pop)

    elif selection_method == 'deterministic':
        return toolbox.deterministicSelection(pop)


def playing_selection(pops):
    counts = preset.config['instr_counts']


def main():

    input('Evolution module loaded. Set parameters and hit enter/return to continue.')
    # todo: Replace with a selection screen / time in the UI.

    global preset
    global toolbox
    preset = Preset()
    toolbox = create_toolbox(**preset.config)

    if preset.master['from_csv']:
        raise NotImplementedError()
        # load stuff from csv
        # will just start a new experiment

    else:
        pops, fits = init_dfs(**preset.config)
        playing = playing_selection(pops, fits)

    g = 1
    done = False

    while not done:
        print(f'--- Generation {g} ---')

        # add fitdf metrics, weights

        pd.to_csv(pd.concat([pops, fits], axis=1), preset.path) # can do concat earlier, or not at all
        pd.to_csv(playing, preset.path)

        preset.save_experiment()

        time.sleep(preset.config['gen_length'])

        preset.update() # todo: implement UI buttons
        toolbox = create_toolbox(**preset.config)

        pops, fits = evolve(pops, fits.loc['age'], playing)
        playing = playing_selection(pops, fits)
        # todo: left off at implementing playing selection. DF sorting and slicing.

        g += 1


if __name__ == '__main__':
    main()

'''
        for i, pop in enumerate(pops):

            # n = preset_config['pop_size']
            # Select the next generation individuals
            offspring = toolbox.parent_select(shuffle(pop), n)

            # Clone the selected individuals
            offspring = list(map(toolbox.clone, offspring))

            children = []
            for mutant in offspring:
                if random.random() < mutpb[i]:
                    toolbox.mutate(mutant)
                    #del mutant.fitness.values
                    children.append(mutant)

            new_pop = pop + children

            # fitness assignment for each population // reworked
            pop_fit = pd.DataFrame(new_pop, columns=params['gen_cols'])
            pop_dict = pop_fit.to_dict(orient="records")

            pop_phenotypes = []

            for ind in pop_dict:
                pop_phenotypes.append(make_phenotype(ind, i, preset_config, n_available_samples))

            pop_phenotypes_df = pd.DataFrame(pop_phenotypes, columns=phen_cols)

            fitnesses = evaluate(load_genepool(playing_path), ages.iloc[:,i],
                                           pop_phenotypes_df, optimum, toolbox,
                                           dist_weight=preset_config['dist_weight'],
                                           symm_weight=preset_config['symm_weight'],
                                           age_weight=preset_config['age_weight'],
                                           manual_optimum=preset_config['manual_optimum'])

            for j, ind in enumerate(new_pop):
                ind.fitness.values = (fitnesses[j],)

            new_pop = toolbox.survivor_select(shuffle(new_pop), n)  # implementation without AGE

            surv_fits = [ind.fitness.values for ind in new_pop]

            # save new populations to respective csv file
            pop_genes = pd.DataFrame(new_pop, columns=gen_cols)
            pop_phenes = gen2phen(pop_genes, phen_cols, i, preset_config, n_available_samples)

            save_complete = False
            while not save_complete:
                try:
                    pop_genes.to_csv(files[i])
                    save_data(pop_phenes, surv_fits, gen_path, files[i])
                    save_complete = True
                except:
                    print(f"saving {files[i]} failed.")

            # selection for next_play
            best_genes = toolbox.playing_select(shuffle(new_pop), int(preset_config['instr_count'][i]))
            play_fits = play_fits + [ind.fitness.values for ind in best_genes]
            best_genes = pd.DataFrame(best_genes, columns=gen_cols)

            # convert next play to phenotype and save as play.csv
            best_phenotypes = gen2phen(best_genes, phen_cols, i, preset_config, n_available_samples)
            next_play = pd.concat([next_play, best_phenotypes])

            # update the population ages
            age_table = pop_phenes.stack().isin(next_play.stack().values).unstack().all(axis=1)

            ages.iloc[:,i] += age_table  # increase age of present genes
            ages.iloc[:,i] *= age_table  # reset departed genes to 0
'''
