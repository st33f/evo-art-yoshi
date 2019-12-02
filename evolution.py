"""
New version of evolution.py, which now evolves separate populations rather than one main.

Been thinking a bit about what selection etc actually means. In our implementation, there basically is no selection at
all, since we are using a generational model with a comma strategy. There is an equal number of offspring produced
to the amount of parents, which are all replaced (some offspring are left unmutated, but this is still technically
generational). Thus, no parent selection or survivor selection is enforced in the populations. Selection does come
into play for currently playing genes/phenes, but this is not technically evolutionary selection. The structure
could be changed to have survivor selection, for instance by producing a multitude of offspring and cutting a few
based on selection.

There's a bunch of redundancy in cloning offspring etc and the program works exactly the same without doing this (just
mutating the pop directly). I left it in because maybe in the future, it could be more interesting to generate more
offspring."""

from deap import base
from deap import creator
from deap import tools
from genetics import *
from presets import *
from fitness import *
import fitness as fit
import numpy as np
import pandas as pd
import time
import json
import glob as glob
from itertools import repeat


def initIndividual(icls, content):
    return icls(content)


def initPopulation(pcls, ind_init, filename):
    contents = []
    df = load_genepool(filename)
    for genome in df.values:
        contents.append(list(genome))
    return pcls(ind_init(c) for c in contents)


def shuffle(pop):
    """shuffles a population to prevent selWorst from prioritizing higher-up rows in a df"""
    return random.sample(pop, len(pop))


def evaluation(playing, age_col, population, optimum, toolbox, dist_weight=1.0, symm_weight=1.0, age_weight=0):

    # subset of cols to evaluate
    # calc distance based on subset
    # then score every individual in pop
    subset = ['order']

    opt = optimum.loc[:, subset].values
    pop = population.loc[:, subset].values

    fitnesses_dist = map(toolbox.evaluate_dist, pop, repeat(opt))
    fitnesses_symm = map(toolbox.evaluate_symm, pop, repeat(playing))
    fitnesses_age  = list(age_col.values) + [-5] * (len(pop) - len(age_col.values))

    fitnesses_dist = [i * dist_weight for i in fitnesses_dist]
    fitnesses_symm = [i * symm_weight for i in fitnesses_symm]
    fitnesses_age  = [i * age_weight  for i in fitnesses_age ]

    fits = [sum(x) for x in zip(fitnesses_dist, fitnesses_symm, fitnesses_age)]

    return fits


def initialize(preset_config):

    # DEAP stuff
    creator.create("FitnessMax", base.Fitness, weights=(1.00,))
    creator.create("Individual", list, fitness=creator.FitnessMax)

    toolbox = base.Toolbox()

    toolbox.register("individual", initIndividual, creator.Individual)
    toolbox.register("population", initPopulation, list, toolbox.individual)

    toolbox.register("evaluate_dist", distance)
    toolbox.register("evaluate_symm", symmetry)
    toolbox.register("mate", tools.cxTwoPoint)
    toolbox.register("mutate", tools.mutPolynomialBounded, eta=preset_config['mut_eta'], low=0., up=1., indpb=preset_config['mut_indpb'])
    # toolbox.register("mutate", tools.mutGaussian, mu=0.5, sigma=0.1, indpb=0.05)
    # toolbox.register("select", tools.selNSGA2)
    toolbox.register("parent_select", tools.selWorst)
    toolbox.register("survivor_select", tools.selWorst)
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
        else:
            new_pop.append(new_genes[k])
            k += 1

    return new_pop


def main():

    g = 0  # generation counter

    preset_path = read_preset_path()
    preset_config = load_config(preset_path)
    files = [file.replace('\\', '/') for file in glob.glob(preset_path + 'current/*.csv') if 'playing' not in file]

    ages = pd.DataFrame(np.zeros([preset_config['pop_size'], len(files)], dtype='int'),
                        columns=[name.split('/')[-1].split('.')[0] for name in files])

    test_df = pd.DataFrame()

    done = False
    while not done:

        g += 1

        preset_path = read_preset_path()
        preset_config = load_config(preset_path)
        playing_path = f'{preset_path}current/playing.csv'

        toolbox = initialize(preset_config)

        phen_cols = [x for x in load_genepool(playing_path).columns]
        gen_cols = [x for x in load_genepool(playing_path).columns if x not in ['nature', 'pitch']]

        # Initializing the populations
        pops = [toolbox.population(file) for file in files]

        mutpb = preset_config['mut_rate']

        next_play = pd.DataFrame(columns=phen_cols)

        print("-- Generation %i --" % g)

        # Optimum is the mean of the phenotype
        optimum = compute_optimum(load_genepool(playing_path), phen_cols)

        for i, pop in enumerate(pops):

            n = len(pop)
            # Select the next generation individuals
            offspring = toolbox.parent_select(shuffle(pop), 20)

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
            pop_fit = pd.DataFrame(new_pop, columns=gen_cols)
            pop_dict = pop_fit.to_dict(orient="records")

            pop_phenotypes = []

            for ind in pop_dict:
                pop_phenotypes.append(make_phenotype(ind, i, preset_config))

            pop_phenotypes_df = pd.DataFrame(pop_phenotypes, columns=phen_cols)

            fitnesses = evaluation(load_genepool(playing_path), ages.iloc[:,i],
                                   pop_phenotypes_df, optimum, toolbox)

            for j, ind in enumerate(new_pop):
                ind.fitness.values = (fitnesses[j],)
                print(ind.fitness.values)

            selected = toolbox.survivor_select(shuffle(new_pop), n)
            new_pop = insert(selected, pop)  # prevent population from being shuffled

            # save new populations to respective csv file
            pop_genes = pd.DataFrame(new_pop, columns=gen_cols)
            pop_phenes = gen2phen(pop_genes, phen_cols, i, preset_config)  # used for age calculation

            save_complete = False
            while not save_complete:
                try:
                    pop_genes.to_csv(files[i])
                    save_complete = True
                except:
                    print(f"saving {files[i]} failed.")

            # selection for next_play using NSGA2
            best_genes = toolbox.playing_select(shuffle(new_pop), int(preset_config['instr_count'][i]))
            best_genes = pd.DataFrame(best_genes, columns=gen_cols)

            # convert next play to phenotype and save as play.csv
            best_phenotypes = gen2phen(best_genes, phen_cols, i, preset_config)
            next_play = pd.concat([next_play, best_phenotypes])

            # update the population ages
            age_table = pop_phenes.stack().isin(next_play.stack().values).unstack().all(axis=1)

            ages.iloc[:,i] += age_table  # increase age of present genes
            ages.iloc[:,i] *= age_table  # reset departed genes to 0

            # print(fitnesses)
            print(ages)

        save_complete = False
        while not save_complete:
            try:
                next_play.to_csv(playing_path)
                save_complete = True
            except:
                print(f"saving {preset_path}current/playing.csv failed.")

        time.sleep(preset_config['gen_length'])



if __name__ == '__main__':
    main()
