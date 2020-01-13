'''
Setup different listeners for same instrument to ensure possibility for 2 notes at the same time
'''


from psonic import *
import glob as glob
import os
from presets import *

base_dir = os.getcwd() + '/'

# instruments
# get configs
preset_path = read_preset_path()
preset_config = load_config(preset_path)
# WE NEED TO MAKE THE FOLLOWING DYNAMIC
SYNTH = preset_config['synths']

BASS = [x for x in glob.glob('samples/BASS/*')]
GUITAR = [x for x in glob.glob('samples/GUITAR/*')]
HAT = [x for x in glob.glob('samples/HAT/*')]
KICK = [x for x in glob.glob('samples/KICK/*')]
PERC = [x for x in glob.glob('samples/PERC/*')]
SNARE = [x for x in glob.glob('samples/SNARE/*')]




def get_all_instruments():

    # get configs
    preset_path = read_preset_path()
    preset_config = load_config(preset_path)

    active_instruments = []

    active_natures = preset_config['natures']

    available_samples = read_available_samples()

    for k, v in available_samples.items():
        instr = k.split(os.sep)[-1]
        if instr in active_natures:
            active_instruments.append(v)

    if "SYNTH" in active_natures:
        active_instruments.append(preset_config['synths'])

    return active_instruments

def stop_all_listeners():
    # Stop running processes in Sonic Pi
    stop()




def get_sample_name(path):

    string = str(path)
    string = string.split('\\')[-1]
    elem = string.split('/')[-1]
    sample_name = elem.replace('.wav', '')

    return sample_name

def setup_synths(SYNTH):
    i = 0

    for synth in SYNTH:
        print("setting up listener for", synth)
        run(f"""in_thread do
      live_loop :{synth}_{i} do
      use_real_time
        n, c, a, r, p, m = sync "/osc/trigger/{synth}_{i}"
        with_fx :reverb, mix: m, room: 0.5, pre_amp: 0.1 do
          synth :{synth}, note: n, cutoff: c, attack: a, release: r, pan: p
        end
      end
    end""")
        i += 1


def setup_basses(BASS):
    for bass in BASS:
        sample_name = get_sample_name(bass)
        # print(sample_name)
        print('Setting up listener for: ', bass)
        run(f"""in_thread do
      live_loop :{sample_name} do
      use_real_time
        a, p = sync "/osc/trigger/{sample_name}"
        sample '{base_dir}{bass}', amp: a, pre_amp: 0.6, pitch: p
      end
    end""")


def setup_guitars(GUITAR):
    for guit in GUITAR:
        sample_name = get_sample_name(guit)
        # print('Setting up listener for: ', perc)
        # print(sample_name)
        run(f"""in_thread do
      live_loop :{sample_name} do
      use_real_time
        a, m, m_echo, p = sync "/osc/trigger/{sample_name}"
          with_fx :reverb, mix: m, pre_amp: 0.2, room: 0.4 do
            sample '{base_dir}{guit}', amp: a, pitch: p, pre_amp: 0.5
          end
      end
    end""")

def setup_hats(HAT):
    for hat in HAT:
        sample_name = get_sample_name(hat)
        print('Setting up listener for: ', hat)
        # print(sample_name)
        run(f"""in_thread do
      live_loop :{sample_name} do
      use_real_time
        a, m = sync "/osc/trigger/{sample_name}"
          with_fx :reverb, mix: m, pre_amp: 0.3, room: 0.2 do
            sample '{base_dir}{hat}', amp: a, pre_amp: 0.9
          end
      end
    end""")

def setup_kicks(KICK):
    for kick in KICK:
        sample = get_sample_name(kick)
        # print(sample)
        # print('Setting up listener for: ', sample)
        run(f"""in_thread do
            use_real_time
      live_loop :{sample} do
        a, p = sync "/osc/trigger/{sample}"
        sample '{base_dir}{kick}', amp: a, pre_amp: 0.7, pitch: p
      end
    end""")

def setup_percs(PERC):

    for perc in PERC:
        sample_name = get_sample_name(perc)
        # print('Setting up listener for: ', perc)
        # print(sample_name)
        run(f"""in_thread do
      live_loop :{sample_name} do
      use_real_time
        a, m, m_echo, p = sync "/osc/trigger/{sample_name}"
        with_fx :echo, mix: m_echo, pre_mix: 0.3, phase: 1 do
          with_fx :reverb, mix: m, pre_amp: 0.3, room: 0.4 do
            sample '{base_dir}{perc}', amp: a, pitch: p, pre_amp: 1
          end
        end
      end
    end""")

def setup_snares(SNARE):
    for snare in SNARE:
        sample_name = get_sample_name(snare)
        print('Setting up listener for: ', snare)
        # print(sample_name)
        run(f"""in_thread do
      live_loop :{sample_name} do
      use_real_time
        a, m, m_echo, p = sync "/osc/trigger/{sample_name}"
        with_fx :echo, mix: m_echo, pre_mix: 0.2, phase: 1 do
          with_fx :reverb, mix: m, pre_amp: 0.3, room: 0.2 do
            sample '{base_dir}{snare}', amp: a, pitch: p, pre_amp: 0.5
          end
        end
      end
    end""")

def setup_listeners():
    i = 0
    # setting up metronome
    run("""use_debug false
    use_real_time""")

    for synth in SYNTH:
        # print("setting up listener for", synth)
        run(f"""in_thread do
  live_loop :{synth}_{i} do
  use_real_time
    n, c, a, r, p, m = sync "/osc/trigger/{synth}_{i}"
    with_fx :reverb, mix: m, room: 0.5, pre_amp: 0.1 do
      synth :{synth}, note: n, cutoff: c, attack: a, release: r, pan: p
    end
  end
end""")
        i += 1


    for bass in BASS:
        sample_name = get_sample_name(bass)
        # print(sample_name)
        # print('Setting up listener for: ', bass)
        run(f"""in_thread do
  live_loop :{sample_name} do
  use_real_time
    a, p = sync "/osc/trigger/{sample_name}"
    sample '{base_dir}{bass}', amp: a, pre_amp: 0.6, pitch: p
  end
end""")

    for guit in GUITAR:
        sample_name = get_sample_name(guit)
        # print('Setting up listener for: ', perc)
        # print(sample_name)
        run(f"""in_thread do
  live_loop :{sample_name} do
  use_real_time
    a, m, m_echo, p = sync "/osc/trigger/{sample_name}"
      with_fx :reverb, mix: m, pre_amp: 0.2, room: 0.4 do
        sample '{base_dir}{guit}', amp: a, pitch: p, pre_amp: 0.5
      end
  end
end""")

    for hat in HAT:
        sample_name = get_sample_name(hat)
        # print('Setting up listener for: ', perc)
        # print(sample_name)
        run(f"""in_thread do
  live_loop :{sample_name} do
  use_real_time
    a, m = sync "/osc/trigger/{sample_name}"
      with_fx :reverb, mix: m, pre_amp: 0.3, room: 0.2 do
        sample '{base_dir}{hat}', amp: a, pre_amp: 0.9
      end
  end
end""")

    for kick in KICK:
        sample = get_sample_name(kick)
        # print(sample)
        # print('Setting up listener for: ', sample)
        run(f"""in_thread do
        use_real_time
  live_loop :{sample} do
    a, p = sync "/osc/trigger/{sample}"
    sample '{base_dir}{kick}', amp: a, pre_amp: 0.7, pitch: p
  end
end""")

    for perc in PERC:
        sample_name = get_sample_name(perc)
        # print('Setting up listener for: ', perc)
        # print(sample_name)
        run(f"""in_thread do
  live_loop :{sample_name} do
  use_real_time
    a, m, m_echo, p = sync "/osc/trigger/{sample_name}"
    with_fx :echo, mix: m_echo, pre_mix: 0.3, phase: 1 do
      with_fx :reverb, mix: m, pre_amp: 0.3, room: 0.4 do
        sample '{base_dir}{perc}', amp: a, pitch: p, pre_amp: 1
      end
    end
  end
end""")

    for snare in SNARE:
        sample_name = get_sample_name(snare)
        # print('Setting up listener for: ', perc)
        # print(sample_name)
        run(f"""in_thread do
  live_loop :{sample_name} do
  use_real_time
    a, m, m_echo, p = sync "/osc/trigger/{sample_name}"
    with_fx :echo, mix: m_echo, pre_mix: 0.2, phase: 1 do
      with_fx :reverb, mix: m, pre_amp: 0.3, room: 0.2 do
        sample '{base_dir}{snare}', amp: a, pitch: p, pre_amp: 0.5
      end
    end
  end
end""")



def play_sound(phenotype, available_samples):
    """Play the sounds in sonic pi"""
    if 'bass' in phenotype['nature'].lower():
        # print('Bass playing:  ', BASS[phenotype['instrument']])
        send_message(f"/trigger/{get_sample_name(BASS[phenotype['instrument']])}", phenotype['amp'], phenotype['pitch'])
    elif 'guitar' in phenotype['nature'].lower():
        send_message(f"/trigger/{get_sample_name(GUITAR[phenotype['instrument']])}", phenotype['amp'], phenotype['mix_reverb'],
                     phenotype['mix_echo'], phenotype['pitch'])
    elif 'hat' in phenotype['nature'].lower():
        send_message(f"/trigger/{get_sample_name(HAT[phenotype['instrument']])}", phenotype['amp'], phenotype['mix_reverb'])
    elif 'kick' in phenotype['nature'].lower():
        send_message(f"/trigger/{get_sample_name(KICK[phenotype['instrument']])}", phenotype['amp'], phenotype['pitch'])
    elif 'perc' in phenotype['nature'].lower():
        # print(PERC[phenotype['instrument']])
        send_message(f"/trigger/{get_sample_name(PERC[phenotype['instrument']])}", phenotype['amp'], phenotype['mix_reverb'],
                     phenotype['mix_echo'], phenotype['pitch'])
    elif 'snare' in phenotype['nature'].lower():
        # print(SNARE[phenotype['instrument']])
        send_message(f"/trigger/{get_sample_name(SNARE[phenotype['instrument']])}", phenotype['amp'], phenotype['mix_reverb'],
                     phenotype['mix_echo'], phenotype['pitch'])
    elif 'synth' in phenotype['nature'].lower():
        # print('Synth: ', synths[phenotype['instrument']])
        send_message(f"/trigger/{SYNTH[phenotype['instrument']]}_{phenotype['instrument']}", phenotype['note'], phenotype['cutoff'], phenotype['attack'],
                     phenotype['release'], phenotype['mix_reverb'])

    return


def reset_all_listeners():

    # stop active listeners
    #stop_all_listeners()

    # setting up metronome
    run("""use_debug false
    use_real_time""")

    # get current config
    preset_path = read_preset_path()
    preset_config = load_config(preset_path)

    # get available samples, active natures and synths
    active_synths = preset_config['synths']
    active_natures = preset_config['natures']
    all_instr = get_all_instruments()

    for nature in all_instr:
        if "BASS" in nature[0]:
            basses = [x for x in glob.glob(f"samples{os.sep}BASS{os.sep}*")]
            setup_basses(basses)
        elif "GUITAR" in nature[0]:
            guit = [x for x in glob.glob(f"samples{os.sep}GUITAR{os.sep}*")]
            setup_guitars(guit)
        elif "HAT" in nature[0]:
            hat = [x for x in glob.glob(f"samples{os.sep}HAT{os.sep}*")]
            setup_hats(hat)
        elif "KICK" in nature[0]:
            kick = [x for x in glob.glob(f"samples{os.sep}KICK{os.sep}*")]
            setup_kicks(kick)
        elif "PERC" in nature[0]:
            perc = [x for x in glob.glob(f"samples{os.sep}PERC{os.sep}*")]
            setup_percs(perc)
        elif "SNARE" in nature[0]:
            snare = [x for x in glob.glob(f"samples{os.sep}SNARE{os.sep}*")]
            setup_snares(snare)

    if "SYNTH" in active_natures:
        setup_synths(active_synths)


reset_all_listeners()

'''
    run("""use_debug false
    use_real_time
live_loop :metronome do
  cue :tick
  sleep 0.0625
end""")

def setup_listeners():
    i = 0
    # setting up metronome
    run("""use_debug false
    use_real_time
live_loop :metronome do
  cue :tick
end""")

    for synth in synths:
        # print("setting up listener for", synth)
        run(f"""in_thread do
  live_loop :{synth}_{i}, sync: :tick do
    n, c, a, r, p, m = sync "/osc/trigger/{synth}_{i}"
    with_fx :reverb, mix: m, room: 0.5, pre_amp: 0.1 do
    with_fx :distortion do
      synth :{synth}, note: n, cutoff: c, attack: a, release: r, pan: p
    end
    end
  end
end""")
        i += 1


    for bass in BASS:
        sample_name = get_sample_name(bass)
        # print(sample_name)
        # print('Setting up listener for: ', bass)
        run(f"""in_thread do
  live_loop :{sample_name}, sync: :tick do
    a, p = sync "/osc/trigger/{sample_name}"
    sample '{base_dir}{bass}', amp: a, pre_amp: 0.6, pitch: p
  end
end""")

    for guit in GUITAR:
        sample_name = get_sample_name(guit)
        # print('Setting up listener for: ', perc)
        # print(sample_name)
        run(f"""in_thread do
  live_loop :{sample_name}, sync: :tick do
    a, m, m_echo, p = sync "/osc/trigger/{sample_name}"
    with_fx :echo, mix: m_echo, pre_mix: 0.2, phase: 1 do
      with_fx :reverb, mix: m, pre_amp: 0.3, room: 0.2 do
        sample '{base_dir}{guit}', amp: a, pitch: p, pre_amp: 0.7
      end
    end
  end
end""")

    for hat in HAT:
        sample_name = get_sample_name(hat)
        # print('Setting up listener for: ', perc)
        # print(sample_name)
        run(f"""in_thread do
  live_loop :{sample_name}, sync: :tick do
    a, m = sync "/osc/trigger/{sample_name}"
      with_fx :reverb, mix: m, pre_amp: 0.3, room: 0.2 do
        sample '{base_dir}{hat}', amp: a, pre_amp: 0.9
      end
  end
end""")

    for kick in KICK:
        sample = get_sample_name(kick)
        # print(sample)
        # print('Setting up listener for: ', sample)
        run(f"""in_thread do
  live_loop :{sample}, sync: :tick do
    a, p = sync "/osc/trigger/{sample}"
    sample '{base_dir}{kick}', amp: a, pre_amp: 0.7, pitch: p
  end
end""")

    for perc in PERC:
        sample_name = get_sample_name(perc)
        # print('Setting up listener for: ', perc)
        # print(sample_name)
        run(f"""in_thread do
  live_loop :{sample_name}, sync: :tick do
    a, m, m_echo, p = sync "/osc/trigger/{sample_name}"
    with_fx :echo, mix: m_echo, pre_mix: 0.2, phase: 1 do
      with_fx :reverb, mix: m, pre_amp: 0.3, room: 0.2 do
        sample '{base_dir}{perc}', amp: a, pitch: p, pre_amp: 1
      end
    end
  end
end""")

    for snare in SNARE:
        sample_name = get_sample_name(snare)
        # print('Setting up listener for: ', perc)
        # print(sample_name)
        run(f"""in_thread do
  live_loop :{sample_name}, sync: :tick do
    a, m, m_echo, p = sync "/osc/trigger/{sample_name}"
    with_fx :echo, mix: m_echo, pre_mix: 0.2, phase: 1 do
      with_fx :reverb, mix: m, pre_amp: 0.3, room: 0.2 do
        sample '{base_dir}{snare}', amp: a, pitch: p, pre_amp: 0.5
      end
    end
  end
end""")
'''