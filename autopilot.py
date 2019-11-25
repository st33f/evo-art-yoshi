import time
import pandas as pd
from presets import *
from genetics import *
import glob




bass_only = [1, 0, 0, 0]
synth_only = [0, 0, 0, 1]
high_only = [0, 1, 0, 0]

total_max = 6
max_bass = 1

def add_bass(section):
    section[0] += 1
    return section.copy()

def add_high_perc(section):
    section[1] += 1
    return section.copy()

def add_low_perc(section):
    section[2] += 1
    return section.copy()

def add_synth(section):
    section[3] += 1
    return section.copy()

def remove_bass(section):
    if section[0] > 0:
        section[0] -= 1
    return section.copy()

def remove_high_perc(section):
    if section[1] > 0:
        section[1] -= 1
    return section.copy()

def remove_low_perc(section):
    if section[2] > 0:
        section[2] -= 1
    return section.copy()

def remove_synth(section):
    if section[3] > 0:
        section[3] -= 1
    return section.copy()



def create_structure():

    result = []
    section = [0, 0, 0, 0]

    result.append(add_bass(section))
    result.append(add_synth(section))
    result.append(add_high_perc(section))
    result.append(add_low_perc(section))
    result.append(remove_bass(section))
    result.append(remove_low_perc(section))
    result.append(add_synth(section))
    result.append(add_bass(section))
    result.append(add_high_perc(section))

    print(result)
    return result




def main():

    #structure = [[1, 0, 0, 0], [1, 1, 0, 0], [1, 1, 1, 0], [1, 1, 1, 1]]
    #structure = [[0, 0, 0, 1], [0, 0, 0, 2], [0, 0, 0, 3], [0, 0, 0, 4]]
    #structure = [[0, 0, 0, 1], [0, 0, 0, 1], [0, 0, 0, 1], [0, 0, 0, 1]]
    structure = create_structure()
    done = False

    while not done:
        for i in range(len(structure)):

            cur_structure = structure[i]

            preset_path = read_preset_path()
            preset_config = load_config(preset_path)

            new_config = preset_config
            new_config['instr_count'] = cur_structure

            save_config(preset_path, new_config)

            time.sleep(new_config['refresh_rate'])


if __name__ == '__main__':
    main()

