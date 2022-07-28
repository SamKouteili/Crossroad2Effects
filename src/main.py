from pedalboard import Pedalboard, Plugin, Chain, Mix
from pedalboard.io import AudioFile
import subprocess
import argparse
import librosa
import matplotlib.pyplot as plt
from plgUtil import *
from genAlgo import *
from faustGen import *

parser = argparse.ArgumentParser(description='CrossRoads2Effects: Your Filter Finder')

parser.add_argument('dry', type=str,
                    help='dry sound file directory path')
parser.add_argument('wet', type=str,
                    help='wet sound file directory path')
parser.add_argument('--name', type=str,
                help='faust filter file name')
parser.add_argument("-d", "--debug", help="Debug Mode",
                action="store_true")
    
args = parser.parse_args()

__DEBUG__ = args.debug

with AudioFile(args.dry, 'r') as f:
    dry = f.read(f.frames)
    sr = f.samplerate
with AudioFile(args.wet, 'r') as f:
    wet = f.read(f.frames)

[board, error, time] = evolve(dry, wet, sr, __DEBUG__)

name = args.name if args.name != None else "filter.dsp"

subprocess.run("mkdir output")

write_faust_file(board, error, f"./output/{name}", time)

if __DEBUG__ :
        
    fig, ax = plt.subplots(1,2, figsize = (15,5), sharey = True)
    ax[0].set(title = f'Wet File Waveform')
    librosa.display.waveshow(wet, sr=sr, ax=ax[0], color="orange")
    ax[1].set(title = 'Generated Filter Waveform')
    librosa.display.waveshow(board(dry, sr), sr=sr, ax=ax[1])


    plt.savefig("./output/waveforms.png", facecolor='white')

    #FAUST2PNG!!! add to debug
