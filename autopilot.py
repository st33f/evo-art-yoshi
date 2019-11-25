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


def main():

    structure = [[1, 0, 0, 0], [1, 1, 0, 0], [1, 1, 1, 0], [1, 1, 1, 1]]

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

