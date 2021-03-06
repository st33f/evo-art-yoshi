import random
import pandas as pd
import time

DATA_PATH = "data/"


def random_genome():
    """creates a pseudo-random genome"""

    genes = dict(
        rootnote=random.random(),
        rootoctave=random.random(),
        order=random.random(),
        number=random.random(),
        bpm=random.random(),
        total_offset=random.random(),
        initial_offset=random.random(),
        red=random.random(),
        green=random.random(),
        blue=random.random(),
        # nature=random.random(),
        instrument=random.random(),
        amp=random.random(),
        cutoff=random.random(),
        pan=random.random(),
        attack=random.random(),
        release=random.random(),
        mod_range=random.random(),
        mod_phase=random.random(),
        mix_reverb=random.random(),
        mix_echo=random.random()
        # pitch=random.random()
    )

    return genes


def make_phenotype(genes, nature, config_dict, n_available_samples):
    """
    Function that maps a genepool to a pool of phenotypes.
    Input: indexed pandas table of genes
    Output: indexed pandas table of phenes
    """

    # natures = ['bass', 'guitar', 'hat', 'kick', 'perc', 'snare', 'synth']

    natures = config_dict["natures"]
    synths = config_dict["synths"]

    # mapping for BASSES

    if natures[nature].lower() == "bass":

        phenotype = dict(
            nature=natures[nature],
            rootnote=int(genes["rootnote"] * 12 + 24),
            rootoctave=3,  # int(genes['rootoctave'] * 3 + 3),
            order=int(genes["order"] * 10 + 3),
            number=int(genes["number"] * 2 + 1),
            bpm=int(config_dict["bpm_base"] * 2 ** int(genes["bpm"] * 3)),
            total_offset=0,  # (1/8)* int(genes['total_offset'] * 8) * 0.5**int(genes['bpm']*3),
            initial_offset=0.5,
            red=int(genes["red"] * 155 + 100),
            green=255,  # int(genes['green'] * 155 + 100),
            blue=int(genes["blue"] * 155 + 100),
            instrument=int(genes["instrument"] * n_available_samples[0]),
            # this is all relevant for a synth
            amp=round(genes["amp"] * 0.5 + 0.5, 2),
            cutoff=int(genes["cutoff"] * 10 + 90),
            pan=0,  # round(genes['pan'] - 0.5, 2),
            attack=0,  # round(genes['attack'] / 2, 2),
            release=1,  # round(genes['release'], 2),
            mod_range=int(genes["mod_range"] * 10 + 2),
            mod_phase=round(genes["mod_phase"] * 0.7 + 0.1, 2),
            # effect stuff
            mix_reverb=round(genes["mix_reverb"] * 0.7 + 0.3, 2),
            mix_echo=0,  # round(genes['mix_echo'] * .6, 2),
            # Now the sample related stuff
            pitch=0,  # int(genes['rootnote'] * 6 - 3)
        )

    # mapping for GUITAR
    elif natures[nature].lower() == "guitar":

        phenotype = dict(
            nature=natures[nature],
            rootnote=int(genes["rootnote"] * 12 + 24),
            rootoctave=int(genes["rootoctave"] * 3 + 3),
            order=int(genes["order"] * 10 + 3),
            # number=int(genes['number'] * 3 + 1),
            number=int(genes["number"] * 4 + 1),
            bpm=int(config_dict["bpm_base"] * 2 ** int(genes["bpm"] * 3)),
            total_offset=(1 / 8)
            * int(genes["total_offset"] * 8)
            * 0.5 ** int(genes["bpm"] * 3),
            initial_offset=0.5,  # (1/8) * int(genes['initial_offset'] * 8) * 1**int(genes['bpm']*3),
            red=int(genes["bpm"] * 155 + 100),  # int(genes['red'] * 155 + 100),
            green=int(
                genes["initial_offset"] * 155 + 100
            ),  # int(genes['green'] * 155 + 100),
            blue=255,  # int(genes['blue'] * 155 + 100),
            instrument=int(genes["rootoctave"] * n_available_samples[1]),
            # this is all relevant for a synth
            amp=round(genes["amp"] * 0.5 + 0.5, 2),
            cutoff=int(genes["cutoff"] * 50 + 50),
            pan=round(genes["pan"] - 0.5, 2),
            attack=0,  # round(genes['attack'] / 2, 2),
            release=round(genes["release"], 2),
            mod_range=int(genes["mod_range"] * 10 + 2),
            mod_phase=round(genes["mod_phase"] * 0.7 + 0.1, 2),
            # effect stuff
            mix_reverb=round(genes["mix_reverb"] * 0.5 + 0.5, 2),
            mix_echo=round(genes["mix_echo"] * 0.5, 2),
            # Now the sample related stuff
            pitch=int(genes["rootnote"] * 12 - 42),
        )

    # mapping for HI-HATS
    elif natures[nature].lower() == "hat":

        phenotype = dict(
            nature=natures[nature],
            rootnote=int(genes["rootnote"] * 12 + 24),
            rootoctave=int(genes["rootoctave"] * 3 + 3),
            order=int(genes["order"] * 10 + 3),
            # number=int(genes['number'] * 3 + 1),
            number=int(genes["number"] * 2 + 2),
            bpm=int(config_dict["bpm_base"] * 2 ** int(genes["bpm"] * 3)),
            total_offset=(1 / 4)
            * int(genes["total_offset"] * 4)
            * 0.5 ** int(genes["bpm"] * 3),
            initial_offset=(1 / 4)
            * int(genes["initial_offset"] * 4)
            * 1 ** int(genes["bpm"] * 3),
            red=int(genes["red"] * 155 + 100),
            green=int(genes["green"] * 155 + 100),
            blue=255,  # int(genes['blue'] * 155 + 100),
            instrument=int(genes["instrument"] * n_available_samples[2]),
            # this is all relevant for a synth
            amp=round(genes["amp"] * 0.5 + 0.5, 2),
            cutoff=int(genes["cutoff"] * 30 + 70),
            pan=round(genes["pan"] - 0.5, 2),
            attack=0,  # round(genes['attack'] / 2, 2),
            release=round(genes["release"], 2),
            mod_range=int(genes["mod_range"] * 10 + 2),
            mod_phase=round(genes["mod_phase"] * 0.7 + 0.1, 2),
            # effect stuff
            mix_reverb=round(genes["mix_reverb"] * 0.5 + 0.5, 2),
            mix_echo=round(genes["mix_echo"] * 0.5, 2),
            # Now the sample related stuff
            pitch=int(genes["rootnote"] * 12 - 6),
        )

    # mapping for KICK
    elif natures[nature].lower() == "kick":

        phenotype = dict(
            nature=natures[nature],
            rootnote=int(genes["rootnote"] * 12 + 24),
            rootoctave=int(genes["rootoctave"] * 3 + 3),
            order=int(genes["order"] * 10 + 3),
            number=int(genes["number"] * 2 + 1),
            # number=1,
            bpm=int(config_dict["bpm_base"] * 2 ** int(genes["bpm"] * 3)),
            total_offset=0,  # (1/4)* int(genes['total_offset'] * 4) * 0.5**int(genes['bpm']*3),
            initial_offset=0.5,  # (1/8) * int(genes['initial_offset'] * 8) * 1**int(genes['bpm']*3),
            red=int(genes["red"] * 155 + 100),
            green=int(genes["green"] * 155 + 100),
            blue=int(genes["blue"] * 155 + 100),
            instrument=int(genes["instrument"] * n_available_samples[3]),
            # this is all relevant for a synth
            amp=round(genes["amp"] * 0.5 + 0.5, 2),
            cutoff=100,  # int(genes['cutoff'] * 30 + 70),
            pan=0,  # round(genes['pan'] - 0.5, 2),
            attack=0,  # round(genes['attack'] / 2, 2),
            release=1,  # round(genes['release'], 2),
            mod_range=int(genes["mod_range"] * 10 + 2),
            mod_phase=round(genes["mod_phase"] * 0.7 + 0.1, 2),
            # effect stuff
            mix_reverb=round(genes["mix_reverb"] * 0.3 + 0.1, 2),
            mix_echo=round(genes["mix_echo"] * 0.6, 2),
            # Now the sample related stuff
            pitch=0,  # int(genes['rootnote'] * 6 - 3)
        )

    # mapping for PERCS
    elif natures[nature].lower() == "perc":

        phenotype = dict(
            nature=natures[nature],
            rootnote=int(genes["rootnote"] * 12 + 24),
            rootoctave=int(genes["rootoctave"] * 3 + 3),
            order=int(genes["order"] * 10 + 3),
            # number=int(genes['number'] * 3 + 1),
            number=int(genes["number"] * 3 + 1),
            bpm=int(config_dict["bpm_base"] * 2 ** int(genes["bpm"] * 3)),
            total_offset=(1 / 4)
            * int(genes["total_offset"] * 4)
            * 0.5 ** int(genes["bpm"] * 3),
            initial_offset=(1 / 4)
            * int(genes["initial_offset"] * 4)
            * 1 ** int(genes["bpm"] * 3),
            red=int(genes["red"] * 155 + 100),
            green=int(genes["green"] * 155 + 100),
            blue=255,  # int(genes['blue'] * 155 + 100),
            instrument=int(genes["instrument"] * n_available_samples[4]),
            # this is all relevant for a synth
            amp=round(genes["amp"] * 0.2 + 0.8, 2),
            cutoff=int(genes["cutoff"] * 10 + 90),
            pan=round(genes["pan"] - 0.5, 2),
            attack=0,  # round(genes['attack'] / 2, 2),
            release=round(genes["release"], 2),
            mod_range=int(genes["mod_range"] * 10 + 2),
            mod_phase=round(genes["mod_phase"] * 0.7 + 0.1, 2),
            # effect stuff
            mix_reverb=round(genes["mix_reverb"] * 0.5 + 0.5, 2),
            mix_echo=round(genes["mix_echo"] * 0.5, 2),
            # Now the sample related stuff
            pitch=int(genes["rootnote"] * 6 - 3),
        )

    # mapping for SNARE
    elif natures[nature].lower() == "snare":

        phenotype = dict(
            nature=natures[nature],
            rootnote=int(genes["rootnote"] * 12 + 24),
            rootoctave=int(genes["rootoctave"] * 3 + 3),
            order=int(genes["order"] * 10 + 3),
            number=int(genes["number"] * 2 + 1),
            bpm=int(config_dict["bpm_base"] * 2 ** int(genes["bpm"] * 3)),
            total_offset=(1 / 4)
            * int(genes["total_offset"] * 4)
            * 0.5 ** int(genes["bpm"] * 3),
            initial_offset=0.5,  # (1/8) * int(genes['initial_offset'] * 8) * 1**int(genes['bpm']*3),
            red=int(genes["red"] * 155 + 100),
            green=int(genes["green"] * 155 + 100),
            blue=int(genes["blue"] * 155 + 100),
            instrument=int(genes["instrument"] * n_available_samples[5]),
            # this is all relevant for a synth
            amp=round(genes["amp"] * 0.5 + 0.5, 2),
            cutoff=100,  # int(genes['cutoff'] * 30 + 70),
            pan=0,  # round(genes['pan'] - 0.5, 2),
            attack=0,  # round(genes['attack'] / 2, 2),
            release=1,  # round(genes['release'], 2),
            mod_range=int(genes["mod_range"] * 10 + 2),
            mod_phase=round(genes["mod_phase"] * 0.7 + 0.1, 2),
            # effect stuff
            mix_reverb=round(genes["mix_reverb"] * 0.3 + 0.1, 2),
            mix_echo=round(genes["mix_echo"] * 0.6, 2),
            # Now the sample related stuff
            pitch=int(genes["rootnote"] * 6 - 3),
        )

    # mapping for SYNTH
    elif natures[nature].lower() == "synth":

        phenotype = dict(
            nature=natures[nature],
            rootnote=int(genes["rootnote"] * 12 + 24),
            rootoctave=int(genes["rootoctave"] * 3 + 3),
            order=int(genes["order"] * 10 + 3),
            # number=int(genes['number'] * 3 + 1),
            number=int(genes["number"] * 4 + 2),
            bpm=int(config_dict["bpm_base"] * 2 ** int(genes["bpm"] * 3)),
            total_offset=0,  # (1/4) * int(genes['total_offset'] * 4) * 0.5**int(genes['bpm']*3),
            initial_offset=random.choice(
                [1.25, 1.333, 1.5]
            ),  # random.choice([0.125, 0.25, 0.33, 0.5, 0.66, 0.75]),#(1/24) * int(genes['initial_offset'] * 24) * 1**int(genes['bpm']*3),
            red=255,  # int(genes['red'] * 155 + 100),
            green=int(genes["green"] * 155 + 100),
            blue=int(genes["blue"] * 155 + 100),
            instrument=int(genes["instrument"] * len(synths)),
            # this is all relevant for a synth
            amp=round(genes["amp"] * 0.5 + 0.5, 2),
            cutoff=int(genes["cutoff"] * 30 + 70),
            pan=round(genes["pan"] - 0.5, 2),
            attack=0,  # round(genes['attack'] / 2, 2),
            release=1,  # round(genes['release'], 2),
            mod_range=int(genes["mod_range"] * 10 + 2),
            mod_phase=round(genes["mod_phase"] * 0.7 + 0.1, 2),
            # effect stuff
            mix_reverb=round(genes["mix_reverb"] * 0.4 + 0.6, 2),
            mix_echo=round(genes["mix_echo"] * 0.6, 2),
            # Now the sample related stuff
            pitch=int(genes["rootnote"] * 12 - 6),
        )

    return phenotype


def gen2phen(genotypes, phen_cols, i, config_dict, n_available_samples):
    """Convert genotypes to phenotypes for playing and evaluation"""

    geno_dict = genotypes.to_dict(orient="records")

    phenotypes = []

    for child in geno_dict:
        phenotypes.append(make_phenotype(child, i, config_dict, n_available_samples))

    phenotypes_df = pd.DataFrame(phenotypes, columns=phen_cols)
    return phenotypes_df


def add_genes(df, genes):
    """add genes to genome"""

    df.append(genes, ignore_index=True)

    return df


def make_genepool(size=3, crispr=[dict()]):
    """Create a pool of random genomes"""

    genepool = []

    for i in range(size):
        gen = random_genome()
        genepool.append(gen)

    df = pd.DataFrame(genepool)

    return df


def load_genepool(filename):
    """Load a genepool from a given file"""
    done = False
    while not done:
        try:
            df = pd.read_csv(filename, index_col=0)
            return df
        except:
            print("error loeading genepool")
            time.sleep(0.01)

    return None


def save_genepool(df, filename="genepool.csv"):
    """save a genepool to a given csv file"""

    df.to_csv(filename)

    return
