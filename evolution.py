"""
todo
- pd.concat all population dfs and give them a gen number
- pd.concat playing.csv

"""

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


def main():

    g = 0  # generation counter

    preset_path = read_preset_path()
    exp_path = create_exp_path()
    old_preset_path = preset_path
    n_available_samples = read_n_available_samples()
    preset_config = load_config(preset_path)

    # scramble all genes randomly
    fit.scramble_all(preset_path)

    files = [file.replace('\\', '/') for file in glob.glob(preset_path + 'current/*.csv') if 'playing' not in file]

    ages = pd.DataFrame(np.zeros([preset_config['pop_size'], len(preset_config["natures"])], dtype='int'),
                        columns=preset_config["natures"])

    done = False
    while not done:

        g += 1

        preset_path = read_preset_path()
        preset_config = load_config(preset_path)
        playing_path = f'{preset_path}current/playing.csv'
        if old_preset_path != preset_path:
            ages = pd.DataFrame(np.zeros([preset_config['pop_size'], len(files)], dtype='int'),
                                columns=preset_config["natures"])
        old_preset_path = preset_path

        toolbox = initialize(preset_config)

        phen_cols = [x for x in load_genepool(playing_path).columns]
        gen_cols = [x for x in load_genepool(playing_path).columns if x not in ['nature', 'pitch']]

        # Initializing the populations
        files = [file.replace('\\', '/') for file in glob.glob(preset_path + 'current/*.csv') if 'playing' not in file]

        pops = [toolbox.population(preset_path + f'current/{nature.lower()}.csv') for nature in preset_config["natures"]]
        #pops = [toolbox.population(file) for file in files]

        mutpb = preset_config['mut_rate']

        next_play = pd.DataFrame(columns=phen_cols)
        play_fits = []

        print("-- Generation %i --" % g)

        # Optimum
        optimum = compute_optimum(load_genepool(playing_path), phen_cols)
        gen_path = os.path.join(exp_path, "gen_{}".format(g))
        create_folder(gen_path)

        for i, pop in enumerate(pops):

            n = preset_config["pop_size"]
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
            pop_fit = pd.DataFrame(new_pop, columns=gen_cols)
            pop_dict = pop_fit.to_dict(orient="records")

            pop_phenotypes = []

            for ind in pop_dict:
                pop_phenotypes.append(make_phenotype(ind, i, preset_config, n_available_samples))

            pop_phenotypes_df = pd.DataFrame(pop_phenotypes, columns=phen_cols)

            fitnesses = evaluate(load_genepool(playing_path), ages.iloc[:,i],
                                           pop_phenotypes_df, optimum, toolbox,
                                           dist_weight=preset_config['dist_weight'], symm_weight=preset_config['symm_weight'],
                                           age_weight=preset_config['age_weight'], manual_optimum=preset_config['manual_optimum'])

            for j, ind in enumerate(new_pop):
                ind.fitness.values = (fitnesses[j],)

            new_pop = toolbox.survivor_select(shuffle(new_pop), n)  # implementation without AGE

            # just an ugly for loop that gets the job done
            surv_fits = []
            for ind in new_pop:
                surv_fits.append(ind.fitness.values)

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

        save_complete = False
        while not save_complete:
            try:
                next_play.to_csv(playing_path)
                save_data(next_play, play_fits, gen_path, playing_path)
                save_complete = True
            except:
                print(f"saving {preset_path}current/playing.csv failed.")

        time.sleep(preset_config['gen_length'])


if __name__ == '__main__':
    main()
