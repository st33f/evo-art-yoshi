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


def create_new_structure(last_section, bar_length, max_instr_count):
    """Creates a new structure to be playing next"""

    melodic = [0, 1, 6]

    structure = []

    p = [0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2]

    for i in range(bar_length):
        if i == 0:
            new_section = list(np.zeros(7))
            for j in melodic:
                new_section[j] = 1
        else:
            new_section = []
            flip = np.random.binomial(1, p)
            for k, instrument in enumerate(last_section):
                if flip[k]:
                    if instrument == max_instr_count[k]:
                        if random.random() < 0.9:
                            instrument += 0
                        else:
                            instrument -= 1
                    elif instrument == 0:
                        instrument += 1
                    else:
                        instrument += np.random.randint(-1, 2)

                new_section.append(int(instrument))

        structure.append(new_section)

        last_section = new_section

    return structure


def auto_optimum(c, freq=0.1):
    """Lets the optimal order oscillate"""

    return np.sin(c * freq) * 4.5 + 7.5


def main():
    """If the autopilot is active, it creates new sequences and can schedule hyperparameters"""
    preset_path = read_preset_path()
    preset_config = load_config(preset_path)

    if preset_config["experiment_mode"].lower() == "y":
        use_schedule = True
    else:
        use_schedule = False

    structure = [preset_config["instr_count"]]

    c = 0
    done = False
    while not done:

        # sequence = create_sequence(last_section=structure[-1], seq_len=5)
        # structure = create_structure_from_seq(sequence=sequence, last_section=structure[-1])
        # structure = create_structure_from_seq(last_section=structure[-1])
        # structure = [[1, 0, 0, 0, 0, 0, 2], [1, 0, 0, 0, 1, 0, 2], [1, 1, 1, 1, 0, 1, 1], [0, 1, 0, 1, 1, 1, 2], [1, 1, 0, 1, 2, 0, 2], [1, 0, 1, 1, 2, 0, 3]]
        # structure = create_structure()
        #

        # structure = [[1,1,1,1,1,1,1]]

        for section in structure:

            c += 1

            old_preset_path = str(preset_path)
            preset_path = read_preset_path()

            if old_preset_path == preset_path:

                preset_config = load_config(preset_path)

                if not use_schedule:
                    preset_config["instr_count"] = section

                if preset_config["auto_opt"].lower() == "y":
                    preset_config["manual_optimum"] = [auto_optimum(c)]

                save_config(preset_path, preset_config)

                time.sleep(preset_config["gen_length"])

            else:
                preset_config = load_config(preset_path)

                structure = [preset_config["instr_count"]]
                break

        if preset_config["auto_seq"].lower() == "y":
            structure = create_new_structure(
                structure[-1],
                preset_config["bar_length"],
                preset_config["max_instr_count"],
            )


if __name__ == "__main__":
    main()
