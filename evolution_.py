"""
todo
- use a pd dataframe to index and store populations.
- make sure indices are preserved during selection
- maintain a separate DF of fitnesses (and thus age as well) with the same MultiIndex
- passing to deap is done by passing df.values() and reindexing after selection/mutation (?)
	> is this possible?

- unique numbering for individuals could be implemented if needed.
- could try nsga2.
"""

from deap import base
from deap import creator
from deap import tools
from genetics import load_genepool, random_genome
from presets import *  #load_config
import fitness as fit
import numpy as np
import pandas as pd
import time
import glob as glob
import random
from itertools import repeat


def initIndividual(icls, content):
    return icls(content)


def initPopulation(pcls, ind_init, filename):
    contents = []
    df = load_genepool(filename)
    for genome in df.values:
        contents.append(list(genome))
    return pcls(ind_init(c) for c in contents)


def random_pops(natures, pop_size, gen_cols, only_ages=False, **kwargs):

    index = pd.MultiIndex.from_product([natures,
                                        range(pop_size)], names=['pop', 'ind'])

    pops = pd.DataFrame([random_genome() for _ in range(pop_size) for _ in natures],
                        index=index, columns=gen_cols)

    age = pd.DataFrame([0] * len(natures) * pop_size, index=index, columns=['age'])

    print(pops)

    return age if only_ages else index, pops, age


def shuffle(pop):
    """shuffles a population to prevent selWorst from prioritizing higher-up rows in a df"""
    return random.sample(pop, len(pop))


def evaluate(playing, age_col, population, optimum, toolbox, dist_weight=0.0,
             symm_weight=1.0, age_weight=0.0, manual_optimum=False):

    # subset of cols to evaluate
    # calc distance based on subset
    # then score every individual in pop
    subset = ['order']

    if not manual_optimum:
        opt = optimum.loc[:, subset].values
    else:
        opt = manual_optimum

    pop = population.loc[:, subset].values

    fitnesses_dist = list(map(toolbox.evaluate_dist, pop, repeat(opt)))
    fitnesses_symm = list(map(toolbox.evaluate_symm, pop, repeat(playing)))
    fitnesses_age  = list(age_col.values) + [0] * (len(pop) - len(age_col.values))

    fitnesses_dist_w = [i * dist_weight for i in fitnesses_dist]
    fitnesses_symm_w = [i * symm_weight for i in fitnesses_symm]
    fitnesses_age_w  = [i * age_weight  for i in fitnesses_age ]

    fits = [sum(x) for x in zip(fitnesses_dist_w, fitnesses_symm_w, fitnesses_age_w)]

    return fits


def create_toolbox(mut_eta, mut_indpb, **kwargs):

    creator.create("FitnessMax", base.Fitness, weights=(1.00,))
    creator.create("Individual", list, fitness=creator.FitnessMax)

    toolbox = base.Toolbox()

    toolbox.register("individual", initIndividual, creator.Individual)
    toolbox.register("population", initPopulation, list, toolbox.individual)

    toolbox.register("evaluate_dist", fit.distance)
    toolbox.register("evaluate_symm", fit.symmetry)
    toolbox.register("mate", tools.cxTwoPoint)
    toolbox.register("mutate", tools.mutPolynomialBounded, eta=mut_eta, low=0., up=1., indpb=mut_indpb)
    # toolbox.register("mutate", tools.mutGaussian, mu=0.5, sigma=0.1, indpb=0.05)
    # toolbox.register("select", tools.selNSGA2)

    toolbox.register("tournament_selection", tools.selTournament)
    toolbox.register("roulette_selection", tools.selRoulette)
    toolbox.register("parent_selection", tools.selRandom)
    toolbox.register("deterministic_selection", tools.selWorst)
    toolbox.register("playing_select", tools.selWorst)

    return toolbox


def insert(selected, population):
    """Returns the population in order, with any non-selected genes replaced with new ones"""

    new_pop = []
    k = 0
    new_genes = [new_gene for new_gene in selected if new_gene not in population]

    for gene in population:
        if gene in selected:
            new_pop.append(gene)
        elif gene not in selected:
            new_pop.append(new_genes[k])
            k += 1


    return new_pop


def create_exp_path():
    # print(glob.glob("experiments/*"))
    # print(glob.glob("experiments/*") is [])
    # # print(['experiments/'])
    # # print(glob.glob("experiments/*") is ['experiments/'])

    if not glob.glob("experiments/*"):
        exp_number = 0
    else:
        exp_number = max([int(f.split("\\")[-1].split("_")[-1]) for f in glob.glob("experiments/*")]) + 1

    root = "experiments"
    exp_path = os.path.join(root, "experiment_{}".format(exp_number)) + "\\"
    return exp_path


def save_data(pop_phenes, pop_fits, gen_path, filename):

    pop_fits = [round(i,2) for (i,) in pop_fits]

    pop_phenes['fitness'] = pop_fits

    name = filename.split('/')[-1]
    pop_phenes.to_csv(os.path.join(gen_path, name))


def future_ui_features(preset_path, params):
    # todo: Load these from somewhere else. Add button functionality.
    # once this is done this function can be removed and toolbox can be moved out of the loop.
    params['gen_cols'] = pd.read_csv(f'{preset_path}\\current\\bass.csv',
                                     header=0, nrows=1).columns.tolist()[1:]
    params['phen_cols'] = pd.read_csv(f'{preset_path}\\current\\playing.csv',
                                      header=0, nrows=1).columns.tolist()[1:]
    params['scramble'] = False
    params['parent_selection'] = random.choice(['roulette', 'tournament', 'random'])
    params['survivor_selection'] = 'deterministic'

    return params


def evolve(pops, toolbox, pop_size, natures, parent_selection, survivor_selection, **kwargs):
    # offspring = toolbox.parent_select([pops[nature].sample(frac=1), pop_size
    #                                   for nature in natures])

    genes = [pops.loc[pop].sample(frac=1).values.tolist()
             for pop in pops.index.levels[0]]

    parents = select_parents(genes, parent_selection)

    offspring = list(map(toolbox.clone, offspring))

    # todo: [LEFT OFF] implement the evolution procedure.

    # todo: implement crossover as an optional feature?

    return pops

#
# def select_parents(genes, parent_selection):
#     if parent_selection == random:
#

def random_playing_selection(pops, instr_count):
    playing = pd.concat([pops.xs(pop, drop_level=False).sample(count)
                            for pop, count in zip(pops.index.levels[0],instr_count)])
    print(playing)
    return playing


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

def main():

    g = 0  # generation counter

    exp_path = create_exp_path()
    preset_path = read_preset_path()
    # old_preset_path = preset_path
    # n_available_samples = read_n_available_samples()
    # preset_config = load_config(preset_path)
    # files = [file.replace('\\', '/') for file in glob.glob(preset_path + 'current/*.csv') if 'playing' not in file]

    print('Evolution module loaded.')
    # time.sleep(6) # give the user some time to configure the params (such as recovery).
                   # todo: Could be replaced with a prompt for the user to set params.

    preset_path = read_preset_path()
    old_preset_path = preset_path
    n_available_samples = read_n_available_samples()
    params = load_config(preset_path)

    # if preset_config['recovery']: # todo
    #     # index, pops, fits = load_pops(**preset_config)
    #     raise NotImplementedError()

    done = False
    while not done:
        start_time = time.time()

        g += 1

        preset_path = read_preset_path()
        params = load_config(preset_path)
        playing_path = f'{preset_path}current/playing.csv'

        params = future_ui_features(preset_path, params) # todo: implement UI buttons
        toolbox = create_toolbox(**params)

        if (g == 1 or params['scramble']) and not params['recovery']: # May need to always do this if changing preset.
            index, pops, fits = random_pops(**params)
            playing = random_playing_selection(pops, params['instr_count'])

        elif old_preset_path != preset_path:
            fits = random_pops(**params, only_ages=True)

        old_preset_path = preset_path

        # next_play = pd.DataFrame(columns=params['phen_cols']) # todo: may not need

        print("-- Generation %i --" % g)

        # optimum = fit.compute_optimum(load_genepool(playing_path), params['phen_cols'])
        # todo: update with autopilot call
        optimum = params['manual_optimum']

        gen_path = os.path.join(exp_path, "gen_{}".format(g))
        create_folder(gen_path)

        index, pops, fits = evolve(pops, playing, toolbox, **params)

        next_play = playing_selection(pops, fits)

        save_complete = False
        while not save_complete:
            try:
                next_play.to_csv(playing_path)
                if collect_data: save_data(next_play, play_fits, gen_path, playing_path) # todo: function needs a rewrite
                save_complete = True
            except:
                print(f"saving {preset_path}current/playing.csv failed.")

        if params['debug_mode']: print('Cycle time: ', time.time() - start_time)

        time.sleep(preset_config['gen_length'])


if __name__ == '__main__':
    main()
