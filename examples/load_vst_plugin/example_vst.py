
''' oc: https://github.com/spotify/pedalboard '''
from pedalboard import Pedalboard, Reverb, load_plugin
from pedalboard.io import AudioFile

# Load a VST3 or Audio Unit plugin from a known path on disk:
vst = load_plugin("./VSTs/RoughRider3.vst3")

print(vst.parameters.keys())
# dict_keys([
#   'sc_hpf_hz', 'input_lvl_db', 'sensitivity_db',
#   'ratio', 'attack_ms', 'release_ms', 'makeup_db',
#   'mix', 'output_lvl_db', 'sc_active',
#   'full_bandwidth', 'bypass', 'program',
# ])

# Set the "ratio" parameter to 15
vst.ratio = 15

# Use this VST to process some audio:
with AudioFile('some-file.wav', 'r') as f:
  audio = f.read(f.frames)
  samplerate = f.samplerate
effected = vst(audio, samplerate)

# ...or put this VST into a chain with other plugins:
board = Pedalboard([vst, Reverb()])
# ...and run that pedalboard with the same VST instance!
effected = board(audio, samplerate)