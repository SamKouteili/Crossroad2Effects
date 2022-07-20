from pedalboard import Pedalboard, Plugin, Chain, Mix, Gain, Delay, Limiter, Compressor, Reverb, HighpassFilter, LowpassFilter
from plgUtil import PLUGINS, get_plg_args

def faust_str_block(plg : Plugin, ctr : int) -> str :
    """
    Generate a tuple consisting the plugin assignment and its name in the process
    """
    args = get_plg_args(plg)
    name, param = "?", "?"

    if isinstance(plg, Gain) :
        name = f'gain{ctr}'
        param = f'+({args["gain_db"]})'
    elif isinstance(plg, Delay) :
        name = f'del{ctr}'
        param = f'@({args["delay_seconds"]})'
    elif isinstance(plg, HighpassFilter) :
        name = f'hpf{ctr}'
        param = f'(fi).highpass(1, {args["cutoff_frequency_hz"]})'
    elif isinstance(plg, LowpassFilter) :
        name = f'lpf{ctr}'
        param = f'(fi).lowpass(1, {args["cutoff_frequency_hz"]})'
    elif isinstance(plg, Limiter) :
        name = f'lim{ctr}'
        param = f'(co).limiter_lad_mono(0, {args["threshold_db"]}, 1, 0.3, {args["release_ms"]})'   
    elif isinstance(plg, Compressor) :
        name = f'comp{ctr}'
        param = f'(co).compressor_mono({args["ratio"]}, {args["threshold_db"]}, 0.5, {args["release_ms"]})'
    elif isinstance(plg, Reverb) :
        name = f'rev{ctr}'
        param = f'(re).mono_freeverb({args["width"]}, 1, {args["wet_level"]}, {args["room_size"]})'
    
    return [name, f'{name} = {param}\n;']


def faustify(board : Pedalboard, d={}, pre="", acc="") -> str :
    """
    Generate a Faust process from a Pedalboard
    """
    if list(board) == [] :
        return f'import("stdfaust.lib");\n\n{pre}\nprocess = {acc};'
    
    (hd, *tl), acc = board, ""
            
    if isinstance(hd, Chain) :
        acc = '(' + faustify(hd) + ')'
        if tl != [] :
            o = " <: " if isinstance(tl[0], Mix) else " : "
            acc += o
    
    elif isinstance(hd, Mix) :
        for fx in hd :
            inn = faustify([fx])
            if isinstance(fx, Mix) :
                inn = "_ <: " + inn
            acc += '(' + inn + '), '
        
        if tl != [] :
            o = " :> " if not isinstance(tl[0], Mix) else \
             (" <: " if len(hd) < len(tl[0]) else " :> " )
        else :
            o = ":> _"
        
        acc = acc[:-2] + o
    
    else :
        plg = faust_str_block(hd, d[hd])
        pre += plg[1]
        if tl != [] :
            o = " <: " if isinstance(tl[0], Mix) else " : "
            acc = plg[0] + o
        else :
            acc = plg[0]
        
        acc[hd] += 1

    
    return acc + faustify(tl)

def gen_plg_dict() :
    d = {}
    for plg in PLUGINS : 
        d[plg] = 0 
    return d

def write_faust_file(board : Pedalboard, name="filter.dsp") :
    file = open(name, "w")
    file.write(faustify(board))
    file.close


            
        