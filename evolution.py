from deap import base, creator, tools
from fitness import *
from vis import *
import numpy as np
import pandas as pd
import time
import glob
from itertools import repeat, compress

EXPERIMENT_PATH = "experiments"


def initIndividual(icls, content):
    """Creates an individual for a population"""
    return icls(content)


def initPopulation(pcls, ind_init, filename):
    """Creates a population of individuals"""
    contents = []
    df = load_genepool(filename)
    for genome in df.values:
        contents.append(list(genome))
    return pcls(ind_init(c) for c in contents)


def shuffle(pop):
    """Shuffles a population to prevent selWorst from prioritizing higher-up rows in a df"""
    return random.sample(pop, len(pop))


def evaluate(
    playing,
    age_col,
    population,
    optimum,
    toolbox,
    dist_weight=0.0,
    symm_weight=1.0,
    age_weight=0.0,
    manual_optimum=False,
):
    """Fitness evaluation function"""
    # subset of cols to evaluate
    # calc distance based on subset
    # then score every individual in pop
    subset = ["order"]

    if not manual_optimum:
        opt = optimum.loc[:, subset].values
    else:
        opt = manual_optimum

    pop = population.loc[:, subset].values

    fitnesses_dist = list(map(toolbox.evaluate_dist, pop, repeat(opt)))
    fitnesses_symm = list(map(toolbox.evaluate_symm, pop, repeat(playing)))
    age = np.array(list(age_col.values) + [0] * (len(pop) - len(age_col.values)))
    fitnesses_age = age2fit(age)
    fitnesses_dist_w = [i * dist_weight for i in fitnesses_dist]
    fitnesses_symm_w = [i * symm_weight for i in fitnesses_symm]
    fitnesses_age_w = [i * age_weight for i in fitnesses_age]

    fits_weighted = [
        sum(x) for x in zip(fitnesses_dist_w, fitnesses_symm_w, fitnesses_age_w)
    ]

    return fits_weighted, fitnesses_dist_w, fitnesses_symm_w, fitnesses_age_w, opt


def initialize(preset_config):
    """Initializes the population as well as selection and mutation mechanisms"""
    creator.create("FitnessMax", base.Fitness, weights=(1.00,))
    creator.create("Individual", list, fitness=creator.FitnessMax)

    toolbox = base.Toolbox()

    toolbox.register("individual", initIndividual, creator.Individual)
    toolbox.register("population", initPopulation, list, toolbox.individual)

    toolbox.register("evaluate_dist", distance)
    toolbox.register("evaluate_symm", symmetry)
    toolbox.register("mate", tools.cxTwoPoint)
    toolbox.register(
        "mutate",
        tools.mutPolynomialBounded,
        eta=preset_config["mut_eta"],
        low=0.0,
        up=1.0,
        indpb=preset_config["mut_indpb"],
    )
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


def scheduler(preset_config, c, step=30):
    """Scheduling function for manual hyperparameter settings"""

    number = int(time.time())
    init = {
        "pop_size": 10,
        "gen_length": 2.0,
        "bpm_base": 20,
        "bar_length": 8,
        "max_instr_count": [1, 1, 1, 1, 1, 1, 1],
        "instr_count": [1, 1, 1, 1, 1, 1, 1],
        "speed": 1.0,
        "mut_rate": [0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5],
        "mut_eta": 0.5,
        "mut_indpb": 0.5,
        "dist_weight": 0.0,
        "symm_weight": 0.0,
        "age_weight": 0.0,
        "manual_optimum": [],
        "auto_opt": "n",
        "auto_seq": "n",
        "experiment_mode": "y",
        "experiment_name": str(number),
        "step": step,
        "length": 8,
        "synths": [
            "mod_sine",
            "sine",
            "prophet",
            "pretty_bell",
            "blade",
            "dark_ambience",
            "growl",
            "hollow",
            "pluck",
            "subpulse",
        ],
        "natures": ["BASS", "GUITAR", "HAT", "KICK", "PERC", "SNARE", "SYNTH"],
    }

    init["plot_intervall"] = step * init["length"]

    for k, v in init.items():
        preset_config[k] = v

    if c > step:
        preset_config["symm_weight"] = 1.0

    if c > 2 * step:
        preset_config["age_weight"] = 1.0

    if c > 3 * step:
        preset_config["dist_weight"] = 1.0

    if c > 4 * step:
        preset_config["manual_optimum"] = [11]

    if c > 5 * step:
        preset_config["manual_optimum"] = [3]

    if c > 6 * step:
        preset_config["manual_optimum"] = [11]
        preset_config["mut_rate"] = [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0]

    if c > 7 * step:
        preset_config["manual_optimum"] = [3]

    save_config(preset_path, preset_config)

    return preset_config


def main():
    """Runs the evolution on the populations with set parameters"""

    record = pd.DataFrame([])
    preset_path = read_preset_path()
    old_preset_path = preset_path
    n_available_samples = read_n_available_samples()
    preset_config = load_config(preset_path)

    print("Starting evolution")

    if preset_config["experiment_mode"].lower() == "y":
        print("Experiment mode on")
        use_schedule = True
    else:
        use_schedule = False

    # scramble all genes randomly
    scramble_all(preset_path)

    files = [
        file.replace("\\", "/")
        for file in glob.glob(preset_path + "current/*.csv")
        if "playing" not in file
    ]

    ages = pd.DataFrame(
        np.zeros(
            [preset_config["pop_size"], len(preset_config["natures"])], dtype="int"
        ),
        columns=preset_config["natures"],
    )

    g = 0  # generation counter

    done = False
    while not done:

        loop_t0 = time.time()

        g += 1

        preset_path = read_preset_path()
        preset_config = load_config(preset_path)
        if use_schedule:
            preset_config = scheduler(preset_config, g)

        playing_path = f"{preset_path}current/playing.csv"
        if old_preset_path != preset_path:
            ages = pd.DataFrame(
                np.zeros([preset_config["pop_size"], len(files)], dtype="int"),
                columns=preset_config["natures"],
            )
        old_preset_path = preset_path

        toolbox = initialize(preset_config)

        phen_cols = [x for x in load_genepool(playing_path).columns]
        gen_cols = [
            x
            for x in load_genepool(playing_path).columns
            if x not in ["nature", "pitch"]
        ]

        # Initializing the populations
        files = [
            file.replace("\\", "/")
            for file in glob.glob(preset_path + "current/*.csv")
            if "playing" not in file
        ]

        pops = [
            toolbox.population(preset_path + f"current/{nature.lower()}.csv")
            for nature in preset_config["natures"]
        ]
        # pops = [toolbox.population(file) for file in files]

        mutpb = preset_config["mut_rate"]

        next_play = pd.DataFrame(columns=phen_cols)
        play_fits = []
        print("\n--- Generation %i ---" % g)

        # Optimum
        optimum = compute_optimum(load_genepool(playing_path), phen_cols)

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
                    # del mutant.fitness.values
                    if mutant not in pop:
                        children.append(mutant)

            new_pop = pop + children

            # fitness assignment for each population // reworked
            pop_fit = pd.DataFrame(new_pop, columns=gen_cols)
            pop_dict = pop_fit.to_dict(orient="records")

            pop_phenotypes = []

            for ind in pop_dict:
                pop_phenotypes.append(
                    make_phenotype(ind, i, preset_config, n_available_samples)
                )

            pop_phenotypes_df = pd.DataFrame(pop_phenotypes, columns=phen_cols)
            (
                fitnesses,
                fitnesses_dist_w,
                fitnesses_symm_w,
                fitnesses_age_w,
                opt,
            ) = evaluate(
                load_genepool(playing_path),
                ages.iloc[:, i],
                pop_phenotypes_df,
                optimum,
                toolbox,
                dist_weight=preset_config["dist_weight"],
                symm_weight=preset_config["symm_weight"],
                age_weight=preset_config["age_weight"],
                manual_optimum=preset_config["manual_optimum"],
            )

            for j, ind in enumerate(new_pop):
                ind.fitness.values = (fitnesses[j],)

            new_pop_reduced = toolbox.survivor_select(shuffle(new_pop), n)
            survived = [True if i in new_pop_reduced else False for i in new_pop]
            mutated = [False if i in pop else True for i in new_pop_reduced]
            surv_fits = list(compress(fitnesses, survived))

            fitnesses_dist_w = list(compress(fitnesses_dist_w, survived))
            fitnesses_symm_w = list(compress(fitnesses_symm_w, survived))
            fitnesses_age_w = list(compress(fitnesses_age_w, survived))
            # save new populations to respective csv file
            pop_genes = pd.DataFrame(new_pop_reduced, columns=gen_cols)
            pop_phenes = gen2phen(
                pop_genes, phen_cols, i, preset_config, n_available_samples
            )

            save_complete = False
            while not save_complete:
                try:
                    pop_genes.to_csv(files[i])
                    save_complete = True
                except:
                    print(f"saving {files[i]} failed.")

            # selection for next_play
            best_genes = toolbox.playing_select(
                shuffle(new_pop_reduced), int(preset_config["instr_count"][i])
            )
            # best_genes = toolbox.playing_select(shuffle(new_pop_reduced), int(preset_config['instr_count'][i]))
            playing = [True if i in best_genes else False for i in new_pop_reduced]

            # play_fits = play_fits + [f for i, f in enumerate(surv_fits) if playing[i]]
            best_genes = pd.DataFrame(best_genes, columns=gen_cols)

            # convert next play to phenotype and save as play.csv
            best_phenotypes = gen2phen(
                best_genes, phen_cols, i, preset_config, n_available_samples
            )
            next_play = pd.concat([next_play, best_phenotypes])

            # update the population ages
            age_table = (
                pop_phenes.stack().isin(next_play.stack().values).unstack().all(axis=1)
            )

            ages.iloc[:, i] += age_table  # increase age of present genes
            ages.iloc[:, i] *= age_table  # reset departed genes to 0

            entry = pop_phenes[["order", "instrument", "rootnote"]].copy()
            pop_name = files[i].split("/")[-1].split(".")[0]
            entry["generation"] = g
            entry["population"] = pop_name
            entry["mutated"] = mutated
            entry["playing"] = playing
            entry["age"] = ages.iloc[:, i]
            entry["total fitness"] = surv_fits
            entry["f dist"] = fitnesses_dist_w
            entry["f symm"] = fitnesses_symm_w
            entry["f age"] = fitnesses_age_w
            # print("opt", float(opt[0]))
            entry["target order"] = float(opt[0])
            entry["w dist"] = preset_config["dist_weight"]
            entry["w symm"] = preset_config["symm_weight"]
            entry["w age"] = preset_config["age_weight"]
            entry["mut rate"] = preset_config["mut_rate"][i]

            record = record.append(entry, ignore_index=True)

        save_complete = False
        while not save_complete:
            try:
                next_play.to_csv(playing_path)
                save_complete = True
            except:
                print(f"saving {preset_path}current/playing.csv failed.")

        if use_schedule is True and g % preset_config["plot_intervall"] == 0:
            plot_path = preset_config["experiment_name"]
            result_path = os.path.join(EXPERIMENT_PATH, plot_path)
            record.to_csv(f"{result_path}_record.csv")
            if plot_path is not None:
                plot_record(
                    record,
                    title="Population average",
                    plot_name=f"{plot_path}_population",
                    playing_only=False,
                )
                plot_record(
                    record,
                    title="Playing only",
                    plot_name=f"{plot_path}_playing",
                    playing_only=True,
                )
                parameters = [
                    "w symm",
                    "w age",
                    "w dist",
                    "target order",
                    "mut rate",
                    "rootnote",
                ]
                plot_record(
                    record,
                    title="Parameters",
                    values=parameters,
                    plot_name=f"{plot_path}_parameters",
                    playing_only=False,
                    sharey=False,
                )

        delta_t = float(time.time() - loop_t0)
        print(f"--- generation loop runtime {delta_t:.2f} seconds ---")
        sleeptime = max([preset_config["gen_length"] - delta_t, 0])
        print(f"--- sleeping for {sleeptime} seconds ---")
        time.sleep(sleeptime)


if __name__ == "__main__":
    main()
