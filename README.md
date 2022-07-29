# Crossroad2Effects

[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/pedalboard)](https://pypi.org/project/pedalboard)
[![Supported Platforms](https://img.shields.io/badge/platforms-macOS%20%7C%20Windows%20%7C%20Linux-green)](https://pypi.org/project/pedalboard)

`Crossroad2Effects`, the functional successor to [@jatinchowdhury's](https://github.com/jatinchowdhury18) [CrossroadsEffects](https://github.com/jatinchowdhury18/CrossroadsEffects), is a genetic algorithm infrastructure for filter exploration. Provided with dry and wet sound file, Crossroad2Effect determnines the filter that tampered the dry file and presents it as a [Faust](https://faust.grame.fr/) program. This allows users to have granular access to analog or VST filters through a programming interface. This project constructs its genetic algorithm search on top of [pedalboard](https://github.com/spotify/pedalboard), Spotify's new plugin API.

## Installation

This project requires installation of the [Faust](https://faust.grame.fr/) functional signal processing programming language - documentation on how to locally install it can be found on the [github](https://github.com/grame-cncm/faust) repository. Furthermore, ensure that you have [Python3.9](https://www.python.org/) locally installed - required packages can be installed by running
```
pip install -r requirements.txt
```
Naive use of `Crossroad2Effects` (i.e. without any further debug analysis) would not require installation of the `matplotlib` and `librosa` packages.

## Application

Running `Crossroad2Effects`'s filter search simply requires a python terminal prompt in the form
```
python main.py [-h] [--name NAME] [-d] dry wet
```
where `dry` is the dry `wav` file path and `wet` is the respective wet file path. Running `Crossroad2Effects` generates a `Faust` mono signal filter - an example can be found at `./examples/standard_application/guitar_filt.dsp`.

The optional argument `--name` should be accompanied with a [Faust](https://faust.grame.fr/) filename `NAME`. Adding the debug flag `-d`  generates a series of supporting analysis files for further exploration of the filter function search space. `log.txt` is a generational trace which provides updates on the evolutionary population every 10 generations. `waveforms.png` compares the wave plot of the initial wet file and the dry file passed through the generated filter. `{NAME}-svg` generates an svg diagram of the filter for visual analysis. Examples of these debug files can be found in the `./examples/standard_application` directory.

Command line help/support can be generated with the `-h` flag, with instructions detailing how to format command line arguments interacting with Crossroad2Effects.

## Interactive Granularity

Fundementally, `Crossroad2Effects` attempts to present a genetic algorithm architecture for filter exploration. Indeed, users are provided with generic and simple access to algorithmic properties without having to alter the genetic evolution structure.

For example, within the `./src/genAlgo.py` file, users can find a series of constants.
```
RESET = 3 # Number of genetic resets
WEIGHTED = True # Choosing whether to weight surviving parents for reproduction probability
CALC_ERROR = False # Choosing method of testing equivalence between two models

TOL = 1.0e-5 # Convergence bound    

N_POP = 56 # Max population size
N_GEN = 4 # Number of generations
N_SURVIVE = 24 # Number of survivors after each generation

MAX_BOARD_SZ = 12 # Max generated board size

P_MUTATION = 0.4 # Probability of mutating a parent
P_MERGE = 0.5 # Probability of joining parents in full (as opposed to joining them in half)
```
We note that the definitions for the constants are relatively self evident - rather, this was introduced to invite users to tailor their search parameters. Depending on how the population is evolving, users can ammend constants to increase search time (with more generations), increase search diversity (with resets), or change the probabilities of mutation.

Furthermore, users are invited to look at `plugins.py`, which hosts the base plugin blocks  foundational to our generated filters.  If there is a specific block that, upon search analysis, seems to either be missing or detrimental, users can add/remove that plugin respectively. The idea is that with the debug analysis tools, users can iteratively improve their search space and hyperparameters to generate the most accurate filter possible.

## Contributions

With a library of plugins to chose from, users would be able to tailor each search to consider the components that they hear most clearly, while discarding plugins they are sure are not present. As such, an incredibly helpful contribution would be to add base plugin blocks to `plugins.py`. Given a [Faust](https://faust.grame.fr/) program, we can generate a VST plugin with the `faust2faustvst` command - documentation on usage can be found [here](https://faustdoc.grame.fr/manual/tools/). With a VST plugin, we can then load it as a `Pedalboard` plugin - the codebase below is taken from the pedalboard github [README](https://github.com/spotify/pedalboard/blob/master/README.md).
```python
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
```
Users are invited to add any additional plugins to the `./src/plugins.py` file. With this, you should also look at `./src/plgUtil.py` and update `newPlg` with the new plugin. Lastly consider changing `faust_str_block` from `./src/faustGen.py` to make the symbolic link back to the respective Faust object during translation. With these changes, the new plugin should seamlessly integrate within the evolutionary structure.
