'''
Setup different listeners for same instrument to ensure possibility for 2 notes at the same time
'''


from psonic import *
import glob as glob
import os

base_dir = os.getcwd() + '/'

# instruments
#synths = ['mod_beep', 'mod_pulse', 'mod_sine', 'growl']
#synths = ['hollow', 'dark_ambience', 'dull_bell', 'sine']
#synths = ['sine', 'sine', 'sine', 'sine']
#synths = ['piano', 'piano', 'piano', 'piano']
synths = ['pretty_bell', 'sine', 'fm', 'prophet']

BASS = [x for x in glob.glob('samples/BASS/*')]
GUITAR = [x for x in glob.glob('samples/GUITAR/*')]
HAT = [x for x in glob.glob('samples/HAT/*')]
KICK = [x for x in glob.glob('samples/KICK/*')]
PERC = [x for x in glob.glob('samples/PERC/*')]
SNARE = [x for x in glob.glob('samples/SNARE/*')]


#instruments = [synths, bass, low_percs, high_percs, synths, synths, high_percs, synths, bass, bass]


def get_sample_name(path):

    string = str(path)
    string = string.split('\\')[-1]
    elem = string.split('/')[-1]
    sample_name = elem.replace('.wav', '')

    return sample_name


def setup_listeners():
    i = 0
    # setting up metronome
    run("""use_debug false
    use_real_time""")

    for synth in synths:
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
    with_fx :echo, mix: m_echo, pre_mix: 0.2, phase: 1 do
      with_fx :reverb, mix: m, pre_amp: 0.3, room: 0.2 do
        sample '{base_dir}{guit}', amp: a, pitch: p, pre_amp: 0.5
      end
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



def play_sound(phenotype):
    """Play the sounds in sonic pi"""

    if 'bass' in phenotype['nature']:
        # print('Bass playing:  ', BASS[phenotype['instrument']])
        send_message(f"/trigger/{get_sample_name(BASS[phenotype['instrument']])}", phenotype['amp'], phenotype['pitch'])
    elif 'guitar' in phenotype['nature']:
        send_message(f"/trigger/{get_sample_name(GUITAR[phenotype['instrument']])}", phenotype['amp'], phenotype['mix_reverb'],
                     phenotype['mix_echo'], phenotype['pitch'])
    elif 'hat' in phenotype['nature']:
        send_message(f"/trigger/{get_sample_name(HAT[phenotype['instrument']])}", phenotype['amp'], phenotype['mix_reverb'])
    elif 'kick' in phenotype['nature']:
        send_message(f"/trigger/{get_sample_name(KICK[phenotype['instrument']])}", phenotype['amp'], phenotype['pitch'])
    elif 'perc' in phenotype['nature']:
        # print(PERC[phenotype['instrument']])
        send_message(f"/trigger/{get_sample_name(PERC[phenotype['instrument']])}", phenotype['amp'], phenotype['mix_reverb'],
                     phenotype['mix_echo'], phenotype['pitch'])
    elif 'snare' in phenotype['nature']:
        # print(SNARE[phenotype['instrument']])
        send_message(f"/trigger/{get_sample_name(SNARE[phenotype['instrument']])}", phenotype['amp'], phenotype['mix_reverb'],
                     phenotype['mix_echo'], phenotype['pitch'])
    elif 'synth' in phenotype['nature']:
        # print('Synth: ', synths[phenotype['instrument']])
        send_message(f"/trigger/{synths[phenotype['instrument']]}_{phenotype['instrument']}", phenotype['note'], phenotype['cutoff'], phenotype['attack'],
                     phenotype['release'], phenotype['mix_reverb'])

    return


def stop_all_listeners():
    # Stop running processes in Sonic Pi
    stop()


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