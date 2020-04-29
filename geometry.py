import pygame
import math
from music import *
from autopilot import *

# Set the height and width of the screen
size = [1920, 1080]
CENTER = [size[0] / 2, size[1] / 2]
pos_line = [[CENTER[0], 0], CENTER]

# How thick are the lines on the screen
LINEWIDTH = 2

# Set the maximum iterations per second
FPS = 60

# Define some colors for the screen
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

# Initialize the game engine
pygame.init()
pygame.display.set_caption("Evo Art")
screen = pygame.display.set_mode(size)


def main():
    """Geometric visualization and sound trigger calculation"""

    print("Starting geometry main function.")
    time.sleep(1)
    clock = pygame.time.Clock()

    # retrieve config files
    preset_path = read_preset_path()
    preset_config = load_config(preset_path)
    scaling_factor = read_scaling_factor()

    # set csv of currently playing instrument
    playing = preset_path + "current/playing.csv"

    # setup_listeners()
    reset_all_listeners()

    # get some time info
    start = time.time()
    now = time.time()

    # for the visuals
    sparks = []

    # Loop until the user clicks the close button.
    done = False
    i = 0
    while not done:

        # This limits the while loop to a max of 10 times per second.
        # Leave this out and we will use all CPU we can.
        clock.tick(FPS)

        # Time each iteration to know how far to move the geometry
        t_minus1 = now - start
        now = time.time()
        t0 = now - start
        delta_t = t0 - t_minus1

        if i % (FPS / FPS) == 0:

            # make sure we have our config files
            preset_path = read_preset_path()
            preset_config = load_config(preset_path)
            scaling_factor = read_scaling_factor()
            available_samples = read_available_samples()

            # set csv of currently playing instrument
            playing = preset_path + "current/playing.csv"

            try:
                df = load_genepool(playing)
            except:
                print("error loading genepool")
                pass
            phenotypes = df.to_dict(orient="records")

        i += 1

        for event in pygame.event.get():  # User did something
            if event.type == pygame.QUIT:  # If user clicked close
                done = True  # Flag that we are done so we exit this loop

        # All drawing code happens after the for loop and but
        # inside the main while done==False loop.
        # Clear the screen and set the screen background
        screen.fill(BLACK)
        pygame.draw.polygon(screen, WHITE, pos_line, 1)

        if preset_config["experiment_mode"]:
            show_parameters()

        # This is where the magic happens
        for phenotype in phenotypes:
            new_sparks = make_polygon(
                phenotype, t0, delta_t, preset_config, scaling_factor, available_samples
            )
            sparks = sparks + new_sparks

        if sparks != []:
            sparks = draw_sparks(screen, sparks, scaling_factor)

        # This MUST happen after all the other drawing commands.
        pygame.display.flip()

    # Be IDLE friendly
    pygame.quit()

    # stop sonic pi listeners
    stop_all_listeners()
    print("Stopped program")

    return


def show_parameters():
    """Shows the current parameter settings on the screen"""

    text_X = 20
    text_Y = 20
    font = pygame.font.Font(None, 28)
    text = font.render("Current Parameter Values", True, WHITE)
    textRect = text.get_rect()
    textRect.topleft = (text_X, text_Y)
    screen.blit(text, textRect)
    parameters = [
        "pop_size",
        "gen_length",
        "bpm_base",
        "instr_count",
        "mut_rate",
        "mut_eta",
        "mut_indpb",
        "symm_weight",
        "age_weight",
        "dist_weight",
        "auto_opt",
        "manual_optimum",
    ]
    names = [
        "Population size",
        "Generation length",
        "Base rotation speed",
        "Instrument count",
        "Mutation rate",
        "Parent similarity",
        "Gene mutation prob",
        "Symmetry weight",
        "Age weight",
        "Distance weight",
        "Auto optimum",
        "Manual optimum order",
    ]
    text_Y += 13
    for i, p in enumerate(parameters):
        text_Y += 36
        text = font.render(names[i], True, WHITE)
        textRect = text.get_rect()
        textRect.topleft = (text_X, text_Y)
        screen.blit(text, textRect)

        value = preset_config[p]
        text = font.render(f"{value}", True, WHITE)
        textRect = text.get_rect()
        textRect.topleft = (text_X + 300, text_Y)
        screen.blit(text, textRect)


def draw_sparks(screen, sparks, scaling_factor):
    """Draws a sparking animation when a tone is played"""

    max_age = 20

    for spark in sparks:
        spark["age"] += 1
        age = spark["age"]
        alpha = int(255 * (1 - ((age - 1) / max_age)))
        color = (
            max([0, spark["color"][0] - 5 * age]),
            max([0, spark["color"][1] - 5 * age]),
            max([0, spark["color"][2] - 5 * age]),
        )
        m = [int(CENTER[0]), int(CENTER[1]) - int(spark["position"])]
        radius = int((25 - int(age)) * scaling_factor)
        pygame.draw.circle(screen, color, m, radius)
        if age > max_age:
            sparks.remove(spark)

    return sparks


def pol2cart(rho, phi):
    """Converts polar coordinates to cartesian """

    x = CENTER[1] + rho * math.cos(math.radians(phi + 180))
    y = CENTER[0] - rho * math.sin(math.radians(phi + 180))

    return [y, x]


def rotatePoint(polarcorner, angle):
    """Rotates a point around the center of the screen"""

    newPolarcorner = [polarcorner[0], polarcorner[1] + angle]

    return newPolarcorner


def make_polygon(genes, t, delta_t, preset_config, scaling_factor, available_samples):
    """Creates the rotating geometric visualization"""

    sparks = []

    for i in range(genes["number"]):
        factor = round(1.0 / math.cos(math.radians(180.0 / genes["order"])), 3)

        genes["note"] = genes["rootnote"] + 12 * (
            (genes["rootoctave"] - 1) + math.log2(factor) * i
        )
        genes["radius"] = (
            scaling_factor * 440 * 10 ** (math.log(2, 10) * (genes["note"] - 69) / 12)
        )

        shape_base_note = genes["note"] if i == 0 else shape_base_note
        genes["pitch"] = ((genes["note"] - shape_base_note) / 24 * 12) * 2

        # get the rotation angles
        prev_angle = round((t - delta_t) * 360.0 * (genes["bpm"] / 400.0), 3)
        current_angle = round(
            preset_config["speed"] * t * 360.0 * (genes["bpm"] / 400.0), 3
        )
        prev_angle += (genes["initial_offset"] * i + genes["total_offset"]) * (
            360.0 / genes["order"]
        )
        current_angle += (genes["initial_offset"] * i + genes["total_offset"]) * (
            360.0 / genes["order"]
        )

        pos = []
        for o in range(genes["order"]):
            polarcorner = [genes["radius"], o * (360 / genes["order"])]
            prev_polarcorner = rotatePoint(polarcorner, prev_angle)
            polarcorner = rotatePoint(polarcorner, current_angle)
            prev_polarcorner[1] = round(prev_polarcorner[1] % 360.0, 3)
            polarcorner[1] = round(polarcorner[1] % 360.0, 3)
            delta = abs(polarcorner[1] - prev_polarcorner[1])
            if delta > 180.0:
                play_sound(genes, available_samples)
                sparks.append(
                    {
                        "position": genes["radius"],
                        "color": (genes["red"], genes["green"], genes["blue"]),
                        "age": 0,
                    }
                )
            corner = pol2cart(polarcorner[0], polarcorner[1])
            pos.append(corner)
        pygame.draw.polygon(
            screen, (genes["red"], genes["green"], genes["blue"]), pos, LINEWIDTH
        )

    return sparks
