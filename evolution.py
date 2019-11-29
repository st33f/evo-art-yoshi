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
offspring.

todo's
- could look a bit more at evolution strategy. Maybe adjust the parameters of .mutPolynomialBounded so a mutrate of
  1 guarantees mutation? This would be a bit more logical and enable more control.
- Update the evolution strategy to actually use survivor selection! The populations now are completely replaced by
  a similar amount of offspring. Over-producing offspring could generate more 'favourable' combinations prior to
  currently playing-selection.

- COULD experiment with 'demes', DEAP's preferred way of implementing multiple populations... but not required.
"""

from deap import base
from deap import creator
from deap import tools
from genetics import *
from presets import *
from fitness import *
import fitness as fit
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


def evaluation(population, optimum, toolbox):

    # subset of cols to evaluate
    # calc distance based on subset
    # then score every individual in pop
    subset = ['order']

    opt = [12] #optimum.loc[:,subset].values
    pop = population.loc[:,subset].values

    fitnesses = map(toolbox.evaluate, pop, repeat(opt))
    fits = list(fitnesses).copy()

    return fits


def initialize(preset_config):

    # DEAP stuff
    creator.create("FitnessMax", base.Fitness, weights=(1.00,))
    creator.create("Individual", list, fitness=creator.FitnessMax)

    toolbox = base.Toolbox()

    toolbox.register("individual", initIndividual, creator.Individual)
    toolbox.register("population", initPopulation, list, toolbox.individual)

    toolbox.register("evaluate", distance)
    toolbox.register("mate", tools.cxTwoPoint)
    toolbox.register("mutate", tools.mutPolynomialBounded, eta=preset_config['mut_eta'], low=0., up=1., indpb=preset_config['mut_indpb'])
    # toolbox.register("mutate", tools.mutGaussian, mu=0.5, sigma=0.1, indpb=0.05)
    # toolbox.register("select", tools.selNSGA2)
    toolbox.register("parent_select", tools.selWorst)
    toolbox.register("survivor_select", tools.selWorst)
    toolbox.register("playing_select", tools.selWorst)


    return toolbox

def main():

    g = 0  # generation counter

    done = False
    while not done:

        g += 1

        preset_path = read_preset_path()
        preset_config = load_config(preset_path)
        playing_path = preset_path + 'current/playing.csv'

        toolbox = initialize(preset_config)

        phen_cols = [x for x in load_genepool(playing_path).columns]
        gen_cols = [x for x in load_genepool(playing_path).columns if x not in ['nature', 'pitch']]

        # Initializing the populations
        files = [file.replace('\\', '/') for file in glob.glob(preset_path + 'current/*.csv') if 'playing' not in file]

        pops = [toolbox.population(file) for file in files]

        mutpb = preset_config['mut_rate']

        next_play = pd.DataFrame(columns=phen_cols)

        print("-- Generation %i --" % g)

        # if pop == ...: # using an if statement, different rules can be programmed for different instruments
        # Optimum is the mean of the phenotype
        optimum = compute_optimum(load_genepool(f'{preset_path}current/playing.csv'), phen_cols)

        for i, pop in enumerate(pops):

            n = len(pop)
            # Select the next generation individuals
            offspring = toolbox.parent_select(pop, 3)

            print(offspring)

            # Clone the selected individuals
            offspring = list(map(toolbox.clone, offspring))

            children = []
            for mutant in offspring:
                if random.random() < mutpb[i]:
                    toolbox.mutate(mutant)
                    #del mutant.fitness.values
                    children.append(mutant)

            print(pop)

            new_pop = pop + children

            # fitness assignment for each population // reworked
            pop_fit = pd.DataFrame(new_pop, columns=gen_cols)
            pop_dict = pop_fit.to_dict(orient="records")

            pop_phenotypes = []

            for ind in pop_dict:
                pop_phenotypes.append(make_phenotype(ind, i, preset_config))

            pop_phenotypes_df = pd.DataFrame(pop_phenotypes, columns=phen_cols)

            fitnesses = evaluation(pop_phenotypes_df, optimum, toolbox)

            print(fitnesses)

            print(new_pop)

            for j, ind in enumerate(new_pop):
                ind.fitness.values = (fitnesses[j],)

            #pop = [(ind, (fitnesses[j],)) for j, ind in enumerate(new_pop)]

            #print(pop)

            new_pop = toolbox.survivor_select(new_pop, n)

            # save new populations to respective csv file
            pop_genes = pd.DataFrame(new_pop, columns=gen_cols)

            save_complete = False
            while not save_complete:
                try:
                    pop_genes.to_csv(files[i])
                    save_complete = True
                except:
                    print(f"saving {files[i]} failed.")

            # selection for next_play using NSGA2
            best_genes = toolbox.playing_select(new_pop, int(preset_config['instr_count'][i]))
            best_genes = pd.DataFrame(best_genes, columns=gen_cols)
            print(best_genes)

            # convert next play to phenotype and save as play.csv
            best_phenotypes = gen2phen(best_genes, phen_cols, i, preset_config)
            next_play = pd.concat([next_play, best_phenotypes])

        # not the prettiest code but it works. Maps playing genes back to a pd.df of phenes
        save_complete = False
        while not save_complete:
            try:
                next_play.to_csv(f'{preset_path}current/playing.csv')
                save_complete = True
            except:
                print(f"saving {preset_path}current/playing.csv failed.")

        time.sleep(preset_config['gen_length'])


if __name__ == '__main__':
    main()
