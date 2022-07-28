# Crossroad2Effects

`Crossroad2Effects`, the functional successor to @jatinchowdhury 's [CrossroadsEffects](https://github.com/jatinchowdhury18/CrossroadsEffects), is a genetic algorithm infrastructure for filter exploration. Provided with dry and wet sound file, Crossroad2Effect determnines the filter that tampered the dry file and presents it as a [Faust](https://faust.grame.fr/) program. This allows users to have granular access to analog or VST filters through a programming interface. This project constructs its genetic algorithm search on top of [pedalboard](https://github.com/spotify/pedalboard), Spotify's new plugin API.

## Installation

This project requires installation of the [Faust](https://faust.grame.fr/) functional signal processing programming language - documentation on how to locally install it can be found on the [github](https://github.com/grame-cncm/faust) repository. Furthermore, ensure that you have [Python3](https://www.python.org/) locally installed - required packages can be installed by running
```
pip install -r requirements.txt
```
Naive use of `Crossroad2Effects` (i.e. without any further debug analysis) would not require installation of the `matplotlib` and `librosa` packages.

## Application

Running `Crossroad2Effects`'s filter search simply requires a python terminal prompt in the form
```
python main.py [-h] [--name NAME] [-d] dry wet
```
where `dry` is the dry `wav` file path and `wet` is the respective wet file path. Running `Crossroad2Effects` generates a `Faust` mono signal filter - an example can be found at `./examples/standard_application/ guitar_filt.dsp`.

The optional argument `--name` should be accompanied with a `Faust` filename `NAME`. Adding the debug flag `-d`  generates a series of supporting analysis files for further exploration of the filter function search space. `log.txt` is a generational trace which provides updates on the evolutionary population every 10 generations. `waveforms.png` compares the wave plot of the initial wet file and the dry file passed through the generated filter. `{NAME}-svg` generates an svg diagram of the filter for visual analysis. Examples of these debug files can be found in the `./examples/standard_application` directory.

## Interactive Granularity

mention constants in genAlgo and plugins in plgUtil