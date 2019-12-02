import time
from presets import *

total_max = 6
max_bass = 1

def add_bass(section):
    section[0] += 1
    return section.copy()

def add_guitar(section):
    section[1] += 1
    return section.copy()

def add_hat(section):
    section[2] += 1
    return section.copy()

def add_kick(section):
    section[3] += 1
    return section.copy()

def add_perc(section):
    section[4] += 1
    return section.copy()

def add_snare(section):
    section[5] += 1
    return section.copy()

def add_synth(section):
    section[6] += 1
    return section.copy()



def remove_bass(section):
    if section[0] > 0:
        section[0] -= 1
    return section.copy()

def remove_guitar(section):
    if section[1] > 0:
        section[1] -= 1
    return section.copy()

def remove_hat(section):
    if section[2] > 0:
        section[2] -= 1
    return section.copy()

def remove_kick(section):
    if section[3] > 0:
        section[3] -= 1
    return section.copy()

def remove_perc(section):
    if section[4] > 0:
        section[4] -= 1
    return section.copy()

def remove_snare(section):
    if section[5] > 0:
        section[5] -= 1
    return section.copy()

def remove_synth(section):
    if section[6] > 0:
        section[6] -= 1
    return section.copy()


def create_structure():

    result = []
    section = [0, 0, 0, 0, 0, 0, 0]
    """
    result.append(add_guitar(section))
    result.append(add_bass(section))

    result.append(add_kick(section))
    result.append(add_snare(section))
    result.append(add_hat(section))
    result.append(add_perc(section))

    result.append(remove_kick(section))
    result.append(remove_snare(section))
    result.append(remove_bass(section))

    result.append(add_guitar(section))
    result.append(add_synth(section))

    result.append(remove_hat(section))
    result.append(remove_perc(section))
    result.append(remove_guitar(section))

    result.append(add_synth(section))
    result.append(remove_guitar(section))

    result.append(add_kick(section))
    result.append(add_snare(section))
    result.append(add_hat(section))
    result.append(remove_kick(section))
    result.append(remove_snare(section))

    """
    #result.append(add_kick(section))
    result.append(add_guitar(section))
    result.append(add_guitar(section))
    result.append(add_guitar(section))

    #result.append(add_perc(section))
    result.append(add_snare(section))
    result.append(add_kick(section))

    print(result)
    return result


def create_structure_from_seq(sequence=[[1], [2], [3, 5], [-1], [7], [-3, 4, 6], [-2], [-3, 1], [-4, -6]], last_section=[0, 0, 0, 0, 0, 0, 0]):

    result = []
    new_section = last_section.copy()

    for batch in sequence:
        for i in batch:
            if i == 1:
                new_section = add_bass(new_section)
            elif i == -1:
                new_section = remove_bass(new_section)
            elif i == 2:
                new_section = add_guitar(new_section)
            elif i == -2:
                new_section = remove_guitar(new_section)
            elif i == 3:
                new_section = add_hat(new_section)
            elif i == -3:
                new_section = remove_hat(new_section)
            elif i == 4:
                new_section = add_kick(new_section)
            elif i == -4:
                new_section = remove_kick(new_section)
            elif i == 5:
                new_section = add_perc(new_section)
            elif i == -5:
                new_section = remove_perc(new_section)
            elif i == 6:
                new_section = add_snare(new_section)
            elif i == -6:
                new_section = remove_snare(new_section)
            elif i == 7:
                new_section = add_synth(new_section)
            elif i == -7:
                new_section = add_synth(new_section)

        result.append(new_section.copy())

    print(result)
    return result


def create_sequence(last_section, seq_len=6):

    sequence = []

    for i in range(seq_len):
        if add_one:
            sequence.append([choose_addition()])
        elif add_two:
            sequence.append([choose_addition(), choose_addition()])
        elif remove_one:
            sequence.append([choose_removal()])
        elif remove_two:
            sequence.append([choose_removal(), choose_removal()])
        elif change_one:
            sequence.append([choose_addition(), choose_removal()])
        elif do_nothing:
            sequence.append([])


    return sequence


def choose_addition():

    included = [1, 0, 0, 1, 0, 1, 1]
    n = len(included)

    add_range = [x for i, x in enumerate(range(1, -n)) if included[i] > 0]

    add = random.choice(add_range)

    return add


def choose_removal():

    included = [1, 0, 0, 1, 0, 1, 1]
    n = len(included)

    remove_range = [x for i, x in enumerate(range(-1, -n, -1)) if included[i] > 0]

    rem = random.choice(remove_range)

    return rem


def main():

    preset_path = read_preset_path()
    preset_config = load_config(preset_path)

    structure = [preset_config['instr_count']]

    done = False
    while not done:

        # sequence = create_sequence(last_section=structure[-1], seq_len=5)
        # structure = create_structure_from_seq(sequence=sequence, last_section=structure[-1])
        # structure = create_structure_from_seq(last_section=structure[-1])
        # structure = [[1, 0, 0, 0, 0, 0, 0], [1, 1, 0, 0, 0, 0, 0], [1, 1, 1, 0, 0, 0, 0], [1, 1, 1, 1, 0, 0, 0]]
        # structure = create_structure()
        structure = [[1,0,0,0,0,0,0]]

        for section in structure:

            old_preset_path = str(preset_path)
            preset_path = read_preset_path()

            if old_preset_path == preset_path:

                preset_config = load_config(preset_path)

                preset_config['instr_count'] = section

                save_config(preset_path, preset_config)

                time.sleep(preset_config['refresh_rate'])

            else:
                structure = [preset_config['instr_count']]
                break


if __name__ == '__main__':
    main()

