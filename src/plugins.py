from pedalboard import Delay, HighpassFilter, LowpassFilter, load_plugin

######### ADDITIONAL PLUGINS HERE #####################################################################

 

 
#######################################################################################################

def Add(val) :
    plg = load_plugin("./plg/add/addx.vst3/")
    plg.add = val
    return plg

def Mul(val) :
    plg = load_plugin("./plg/mul/mulx.vst3/")
    plg.val = val
    return plg

BASE_PLUGINS = [Add(1), Add(-1), Mul(0.5), Mul(1.5), Delay(mix=1), HighpassFilter(), LowpassFilter()]

# Add plugins here
ADDITIONAL_PLUGINS = []