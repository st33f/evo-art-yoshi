import random
import pandas as pd

DATA_PATH = 'data/'

'''
# instruments
synths = ['blade', 'mod_pulse', 'mod_sine', 'pretty_bell']
#synths = ['saw', 'sine', 'pluck']
high_percs = ['drum_cymbal_pedal', 'drum_cymbal_closed', 'drum_tom_hi_soft', 'perc_bell', 'ambi_choir', 'tabla_tun1', 'tabla_tun3', 'tabla_tas3']
low_percs = ['elec_soft_kick', 'tabla_ke2', 'drum_bass_soft', 'drum_tom_mid_soft', 'tabla_re']
#snares = ['tabla_na_s', 'elec_wood', 'drum_snare_soft']
snares = ['drum_snare_soft']
bass = ['bass_hard_c', 'bass_hit_c', 'bass_voxy_hit_c', 'mehackit_phone1']
vox = ['ambi_choir']

instruments = [synths, low_percs, snares, high_percs, synths, synths, high_percs, synths, bass, bass]
'''



def random_genome():
    """creates a pseudo-random genome"""

    genes = dict(rootnote=random.random(),
                 rootoctave=random.random(),
                 order=random.random(),
                 number=random.random(),
                 bpm=random.random(),
                 total_offset=random.random(),
                 initial_offset=random.random(),
                 red=random.random(), green=random.random(), blue=random.random(),
                 #nature=random.random(),
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
                 #pitch=random.random()
                 )

    return genes


def make_phenotype(genes, nature, config_dict, n_available_samples):
    """
    Function that maps a genepool to a pool of phenotypes.
    Input: indexed pandas table of genes
    Output: indexed pandas table of phenes
    """

    natures = ['bass', 'guitar', 'hat', 'kick', 'perc', 'snare', 'synth']

    # mapping for BASSES
    if natures[nature] == "bass":

        phenotype = dict(nature=natures[nature],
                     rootnote=int(genes['rootnote'] * 12 + 24),
                     rootoctave=int(genes['rootoctave'] * 3 + 3),
                     order=int(genes['order'] * 10 + 3),
                     number=int(genes['number'] * 2 + 1),
                     bpm=int(config_dict['bpm_base']*2**int(genes['bpm']*3)),
                     total_offset=0,#(1/8)* int(genes['total_offset'] * 8) * 0.5**int(genes['bpm']*3),
                     initial_offset=0.5,
                     red=int(genes['red'] * 155 + 100),
                     green=255, #int(genes['green'] * 155 + 100),
                     blue=int(genes['blue'] * 155 + 100),
                     instrument=int(genes['instrument']*n_available_samples[0]),
                     # this is all relevant for a synth
                     amp=round(genes['amp'] * 0.5 + 0.5, 2),
                     cutoff=int(genes['cutoff'] * 10 + 90),
                     pan=0,#round(genes['pan'] - 0.5, 2),
                     attack=0, #round(genes['attack'] / 2, 2),
                     release=1,#round(genes['release'], 2),
                     mod_range=int(genes['mod_range'] * 10 + 2),
                     mod_phase=round(genes['mod_phase'] * .7 + .1, 2),
                     #effect stuff
                     mix_reverb=round(genes['mix_reverb'] * .7 + .3, 2),
                     mix_echo=0,#round(genes['mix_echo'] * .6, 2),
                     # Now the sample related stuff
                     pitch=0#int(genes['rootnote'] * 6 - 3)
                     )

    # mapping for GUITAR
    elif natures[nature] == "guitar":

        phenotype = dict(nature=natures[nature],
                         rootnote=int(genes['rootnote'] * 12 + 24),
                         rootoctave=int(genes['rootoctave'] * 3 + 3),
                         order=int(genes['order'] * 10 + 3),
                         #number=int(genes['number'] * 3 + 1),
                         number=int(genes['number'] * 4 + 1),
                         bpm=int(config_dict['bpm_base']*2**int(genes['bpm']*3)),
                         total_offset=(1/8)* int(genes['total_offset'] * 8) * 0.5**int(genes['bpm']*3),
                         initial_offset=0.5,#(1/8) * int(genes['initial_offset'] * 8) * 1**int(genes['bpm']*3),
                         red=int(genes['bpm'] * 155 + 100),# int(genes['red'] * 155 + 100),
                         green=int(genes['initial_offset'] * 155 + 100),#int(genes['green'] * 155 + 100),
                         blue=255,#int(genes['blue'] * 155 + 100),
                         instrument=int(genes['rootoctave']*n_available_samples[1]),
                         # this is all relevant for a synth
                         amp=round(genes['amp'] * 0.5 + 0.5, 2),
                         cutoff=int(genes['cutoff'] * 50 + 50),
                         pan=round(genes['pan'] - 0.5, 2),
                         attack=0, #round(genes['attack'] / 2, 2),
                         release=round(genes['release'], 2),
                         mod_range=int(genes['mod_range'] * 10 + 2),
                         mod_phase=round(genes['mod_phase'] * .7 + .1, 2),
                         #effect stuff
                         mix_reverb=round(genes['mix_reverb'] * .5 + .5, 2),
                         mix_echo=round(genes['mix_echo'] * .5, 2),
                         # Now the sample related stuff
                         pitch=int(genes['rootnote'] * 12 - 42)
                         )

    # mapping for HI-HATS
    elif natures[nature] == "hat":

        phenotype = dict(nature=natures[nature],
                         rootnote=int(genes['rootnote'] * 12 + 24),
                         rootoctave=int(genes['rootoctave'] * 3 + 3),
                         order=int(genes['order'] * 10 + 3),
                         #number=int(genes['number'] * 3 + 1),
                         number=int(genes['number'] * 2 + 2),
                         bpm=int(config_dict['bpm_base']*2**int(genes['bpm']*3)),
                         total_offset=(1/4)* int(genes['total_offset'] * 4) * 0.5**int(genes['bpm']*3),
                         initial_offset=(1/4) * int(genes['initial_offset'] * 4) * 1**int(genes['bpm']*3),
                         red=int(genes['red'] * 155 + 100),
                         green=int(genes['green'] * 155 + 100),
                         blue=255,#int(genes['blue'] * 155 + 100),
                         instrument=int(genes['instrument']*n_available_samples[2]),
                         # this is all relevant for a synth
                         amp=round(genes['amp'] * 0.5 + 0.5, 2),
                         cutoff=int(genes['cutoff'] * 30 + 70),
                         pan=round(genes['pan'] - 0.5, 2),
                         attack=0, #round(genes['attack'] / 2, 2),
                         release=round(genes['release'], 2),
                         mod_range=int(genes['mod_range'] * 10 + 2),
                         mod_phase=round(genes['mod_phase'] * .7 + .1, 2),
                         #effect stuff
                         mix_reverb=round(genes['mix_reverb'] * .5 + .5, 2),
                         mix_echo=round(genes['mix_echo'] * .5, 2),
                         # Now the sample related stuff
                         pitch=int(genes['rootnote'] * 12 - 6)
                         )

    # mapping for KICK
    elif natures[nature] == "kick":

        phenotype = dict(nature=natures[nature],
                         rootnote=int(genes['rootnote'] * 12 + 24),
                         rootoctave=int(genes['rootoctave'] * 3 + 3),
                         order=int(genes['order'] * 10 + 3),
                         number=int(genes['number'] * 2 + 1),
                         #number=1,
                         bpm=int(config_dict['bpm_base']*2**int(genes['bpm']*3)),
                         total_offset=0,#(1/4)* int(genes['total_offset'] * 4) * 0.5**int(genes['bpm']*3),
                         initial_offset=0.5,#(1/8) * int(genes['initial_offset'] * 8) * 1**int(genes['bpm']*3),
                         red=int(genes['red'] * 155 + 100),
                         green=int(genes['green'] * 155 + 100),
                         blue=int(genes['blue'] * 155 + 100),
                         instrument=int(genes['instrument']*n_available_samples[3]),
                         # this is all relevant for a synth
                         amp=round(genes['amp'] * 0.5 + 0.5, 2),
                         cutoff=100,#int(genes['cutoff'] * 30 + 70),
                         pan=0,#round(genes['pan'] - 0.5, 2),
                         attack=0, #round(genes['attack'] / 2, 2),
                         release=1,#round(genes['release'], 2),
                         mod_range=int(genes['mod_range'] * 10 + 2),
                         mod_phase=round(genes['mod_phase'] * .7 + .1, 2),
                         #effect stuff
                         mix_reverb=round(genes['mix_reverb'] * .3 + .1, 2),
                         mix_echo=round(genes['mix_echo'] * .6, 2),
                         # Now the sample related stuff
                         pitch=0#int(genes['rootnote'] * 6 - 3)
                         )

    # mapping for PERCS
    elif natures[nature] == "perc":

        phenotype = dict(nature=natures[nature],
                         rootnote=int(genes['rootnote'] * 12 + 24),
                         rootoctave=int(genes['rootoctave'] * 3 + 3),
                         order=int(genes['order'] * 10 + 3),
                         #number=int(genes['number'] * 3 + 1),
                         number=int(genes['number'] * 3 + 1),
                         bpm=int(config_dict['bpm_base']*2**int(genes['bpm']*3)),
                         total_offset=(1/4)* int(genes['total_offset'] * 4) * 0.5**int(genes['bpm']*3),
                         initial_offset=(1/4) * int(genes['initial_offset'] * 4) * 1**int(genes['bpm']*3),
                         red=int(genes['red'] * 155 + 100),
                         green=int(genes['green'] * 155 + 100),
                         blue=255,#int(genes['blue'] * 155 + 100),
                         instrument=int(genes['instrument'] * n_available_samples[4]),
                         # this is all relevant for a synth
                         amp=round(genes['amp'] * 0.2 + 0.8, 2),
                         cutoff=int(genes['cutoff'] * 10 + 90),
                         pan=round(genes['pan'] - 0.5, 2),
                         attack=0, #round(genes['attack'] / 2, 2),
                         release=round(genes['release'], 2),
                         mod_range=int(genes['mod_range'] * 10 + 2),
                         mod_phase=round(genes['mod_phase'] * .7 + .1, 2),
                         #effect stuff
                         mix_reverb=round(genes['mix_reverb'] * .5 + .5, 2),
                         mix_echo=round(genes['mix_echo'] * .5, 2),
                         # Now the sample related stuff
                         pitch=int(genes['rootnote'] * 6 - 3)
                         )

    # mapping for SNARE
    elif natures[nature] == "snare":

        phenotype = dict(nature=natures[nature],
                         rootnote=int(genes['rootnote'] * 12 + 24),
                         rootoctave=int(genes['rootoctave'] * 3 + 3),
                         order=int(genes['order'] * 10 + 3),
                         number=int(genes['number'] * 2 + 1),
                         bpm=int(config_dict['bpm_base']*2**int(genes['bpm']*3)),
                         total_offset=(1/4)* int(genes['total_offset'] * 4) * 0.5**int(genes['bpm']*3),
                         initial_offset=0.5,#(1/8) * int(genes['initial_offset'] * 8) * 1**int(genes['bpm']*3),
                         red=int(genes['red'] * 155 + 100), green=int(genes['green'] * 155 + 100),
                         blue=int(genes['blue'] * 155 + 100),
                         instrument=int(genes['instrument']*n_available_samples[5]),
                         # this is all relevant for a synth
                         amp=round(genes['amp'] * 0.5 + 0.5, 2),
                         cutoff=100,#int(genes['cutoff'] * 30 + 70),
                         pan=0,#round(genes['pan'] - 0.5, 2),
                         attack=0, #round(genes['attack'] / 2, 2),
                         release=1,#round(genes['release'], 2),
                         mod_range=int(genes['mod_range'] * 10 + 2),
                         mod_phase=round(genes['mod_phase'] * .7 + .1, 2),
                         #effect stuff
                         mix_reverb=round(genes['mix_reverb'] * .3 + .1, 2),
                         mix_echo=round(genes['mix_echo'] * .6, 2),
                         # Now the sample related stuff
                         pitch=int(genes['rootnote'] * 6 - 3)
                         )


    # mapping for SYNTH
    elif natures[nature] == "synth":

        phenotype = dict(nature=natures[nature],
                         rootnote=int(genes['rootnote'] * 12 + 24),
                         rootoctave=int(genes['rootoctave'] * 3 + 3),
                         order=int(genes['order'] * 10 + 3),
                         #number=int(genes['number'] * 3 + 1),
                         number=int(genes['number'] * 4 + 2),
                         bpm=int(config_dict['bpm_base']*2**int(genes['bpm']*3)),
                         total_offset=0,#(1/8)* int(genes['total_offset'] * 8) * 0.5**int(genes['bpm']*3),
                         initial_offset=0.33,#(1/4) * int(genes['initial_offset'] * 4) * 1**int(genes['bpm']*3),
                         red=255,#int(genes['red'] * 155 + 100),
                         green=int(genes['green'] * 155 + 100),
                         blue=int(genes['blue'] * 155 + 100),
                         instrument=int(genes['instrument']*4),
                         # this is all relevant for a synth
                         amp=round(genes['amp'] * 0.5 + 0.5, 2),
                         cutoff=int(genes['cutoff'] * 30 + 70),
                         pan=round(genes['pan'] - 0.5, 2),
                         attack=0, #round(genes['attack'] / 2, 2),
                         release=1,#round(genes['release'], 2),
                         mod_range=int(genes['mod_range'] * 10 + 2),
                         mod_phase=round(genes['mod_phase'] * .7 + .1, 2),
                         #effect stuff
                         mix_reverb=round(genes['mix_reverb'] * .4 + .6, 2),
                         mix_echo=round(genes['mix_echo'] * .6, 2),
                         # Now the sample related stuff
                         pitch=int(genes['rootnote'] * 12 - 6)
                         )

    return phenotype

def gen2phen(genotypes, phen_cols, i, config_dict, n_available_samples):

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

    return None


def save_genepool(df, filename='genepool.csv'):
    """save a genepool to a given csv file"""

    df.to_csv(filename)

    return

