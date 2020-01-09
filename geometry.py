import pygame
import math
from music import *
from genetics import *
from psonic import *
from presets import *
from autopilot import *

# Set the height and width of the screen
size = [1920, 1000]
CENTER = [size[0] / 2, size[1] / 2]
pos_line = [[CENTER[0], 0], CENTER]

# Set the scaling factor of the visualization between 0.1 and 0.5
#SCALING_FACTOR = 0.5 # can go

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

    print("Starting geometry main function.")
    time.sleep(1)
    clock = pygame.time.Clock()

    # retrieve config files
    preset_path = read_preset_path()
    #preset_config = load_config(preset_path)
    scaling_factor = read_scaling_factor()

    # set csv of currently playing instrument
    playing = preset_path + 'current/playing.csv'

    setup_listeners()

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
        '''
        print()
        print("i:", i)
        print("t_minus1", t_minus1)
        print("now     ", now)
        print("t0      ", t0)
        print("delta_t ", delta_t)
        #print(f"Delta T GEOMETRY{delta_t}")
        '''

        if i % (FPS/FPS) == 0:

            # make sure we have our config files
            preset_path = read_preset_path()
            preset_config = load_config(preset_path)
            scaling_factor = read_scaling_factor()

            # set csv of currently playing instrument
            playing = preset_path + 'current/playing.csv'

            try:
                df = load_genepool(playing)
            except:
                print('error loading genepool')
                pass
            phenotypes = df.to_dict(orient='records')

        i += 1

        for event in pygame.event.get():  # User did something
            if event.type == pygame.QUIT:  # If user clicked close
                done = True  # Flag that we are done so we exit this loop

        # All drawing code happens after the for loop and but
        # inside the main while done==False loop.
        # Clear the screen and set the screen background
        screen.fill(BLACK)
        pygame.draw.polygon(screen, WHITE, pos_line, 1)

        # This is where the magic happens
        for phenotype in phenotypes:
            #phenotype = make_phenotype(genes)
            new_sparks = make_polygon(phenotype, t0, delta_t, preset_config, scaling_factor)
            sparks = sparks + new_sparks

        if sparks != []:
            sparks = draw_sparks(screen, sparks)

        # This MUST happen after all the other drawing commands.
        pygame.display.flip()

    # Be IDLE friendly
    pygame.quit()

    # stop sonic pi listeners
    stop_all_listeners()
    print('Stopped program')

    return


def draw_sparks(screen, sparks):

    max_age = 20

    for spark in sparks:
        spark["age"] += 1
        age = spark["age"]
        alpha = int(255 * (1 - ((age-1) / max_age)))
        color = (max([0, spark["color"][0] - 5 * age]), max([0, spark["color"][1] - 5 * age]), max([0, spark["color"][2] - 5 * age]))
        m = [int(CENTER[0]), int(CENTER[1]) - int(spark["position"])]
        radius = 25 - int(age)
        pygame.draw.circle(screen, color, m, radius)
        if age > max_age:
            sparks.remove(spark)

    return sparks

def pol2cart(rho, phi):

    # get cartesian coordinates from polar

    x = CENTER[1] + rho * math.cos(math.radians(phi + 180))
    y = CENTER[0] - rho * math.sin(math.radians(phi + 180))

    return [y, x]


def rotatePoint(polarcorner, angle, CENTER=CENTER):

    # the name explains this pretty well i think

    newPolarcorner = [polarcorner[0], polarcorner[1] + angle]

    return newPolarcorner


def make_polygon(genes, t, delta_t, preset_config, scaling_factor):

    # Now this is where the magic happens...
    
    sparks = []

    for i in range(genes['number']):
        factor = round(1. / math.cos(math.radians(180./genes['order'])), 3)

        genes['note'] = genes['rootnote'] + 12 * ((genes['rootoctave'] - 1) + math.log2(factor) * i)  # + (factor*i))
        genes['radius'] = scaling_factor * 440 * 10 ** (math.log(2, 10) * (genes['note'] - 69) / 12)

        shape_base_note = genes['note'] if i == 0 else shape_base_note
        genes['pitch'] = ((genes['note'] - shape_base_note) / 24 * 12) * 2


        # get the rotation angles
        # prev_angle = round((t-delta_t) * (360. / genes['order']) * (genes['bpm'] / 60.), 3)
        # current_angle = round(preset_config['speed'] * t * (360. / genes['order']) * (genes['bpm'] / 60.), 3)
        prev_angle = round((t-delta_t) * 360. * (genes['bpm'] / 400.), 3)
        current_angle = round(preset_config['speed'] * t * 360. * (genes['bpm'] / 400.), 3)
        prev_angle += (genes['initial_offset'] * i + genes['total_offset']) * (360. / genes['order'])
        current_angle += (genes['initial_offset'] * i + genes['total_offset']) * (360. / genes['order'])

        pos = []
        for o in range(genes['order']):
            polarcorner = [genes['radius'], o*(360/genes['order'])]
            prev_polarcorner = rotatePoint(polarcorner, prev_angle, CENTER=CENTER)
            polarcorner = rotatePoint(polarcorner, current_angle, CENTER=CENTER)
            prev_polarcorner[1] = round(prev_polarcorner[1] % 360., 3)
            polarcorner[1] = round(polarcorner[1] % 360., 3)
            delta = abs(polarcorner[1] - prev_polarcorner[1])
            if delta > 180.:
                play_sound(genes)
                sparks.append({"position": genes['radius'],
                               "color": (genes['red'], genes['green'], genes['blue']),
                               "age": 0})
            corner = pol2cart(polarcorner[0], polarcorner[1])
            pos.append(corner)
        pygame.draw.polygon(screen, (genes['red'], genes['green'], genes['blue']), pos, LINEWIDTH)

    return sparks