import time
import multiprocessing
import sys


def run_geometry():
    import geometry
    geometry.main()


def run_autopilot():
    import autopilot
    autopilot.main()


def run_evolution():
    import evolution
    evolution.main()


def run_config():
    import config
    config.main()


if __name__ == '__main__':

    print("Welcome to the Evo Art geometric music project.")

    geo_thread = multiprocessing.Process(name='geo_thread', target=run_geometry)
    evo_thread = multiprocessing.Process(name='evo_thread', target=run_evolution)
    config_thread = multiprocessing.Process(name='config_thread', target=run_config)
    autopilot_thread = multiprocessing.Process(name='autopilot_thread', target=run_autopilot)

    #autopilot_thread.start()
    time.sleep(0.5)
    config_thread.start()
    time.sleep(2.5)
    geo_thread.start()
    time.sleep(4)
    evo_thread.start()


    while geo_thread.is_alive() and evo_thread.is_alive() and config_thread.is_alive():# and autopilot_thread.is_alive():
        time.sleep(1)

    geo_thread.terminate()
    evo_thread.terminate()
    config_thread.terminate()
    #autopilot_thread.terminate()


