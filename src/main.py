from isort import file
from pedalboard import Pedalboard, Plugin, Chain, Mix
from pedalboard.io import AudioFile
import argparse
from plgUtil import *
from genAlgo import *
from faustGen import *

parser = argparse.ArgumentParser(description='CrossRoads2Effects: Your Filter Finder')

parser.add_argument('dry', type=str,
                    help='dry sound file directory path')
parser.add_argument('wet', type=str,
                    help='wet sound file directory path')
parser.add_argument('--name', type=str,
                help='An optional integer argument')
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

write_faust_file(board, error, name, time)