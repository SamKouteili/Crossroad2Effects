from isort import code
from pedalboard import Pedalboard, Plugin, Chain, Mix, Gain, Delay, Limiter, Compressor, Reverb, HighpassFilter, LowpassFilter
from plgUtil import PLUGINS, get_plg_args, gen_plg_dict, strPlg, codePlg

def faust_str_block(plg : Plugin) -> str :
    """
    Generate a tuple consisting the plugin assignment and its name in the process
    """
    args = get_plg_args(plg)
    name, param = "?", "?"

    if isinstance(plg, Gain) :
        name = f'gain{codePlg(plg)}'
        param = f'+({args["gain_db"]})'
    elif isinstance(plg, Delay) :
        name = f'del{codePlg(plg)}'
        param = f'@({args["delay_seconds"]})'
    elif isinstance(plg, HighpassFilter) :
        name = f'hpf{codePlg(plg)}'
        param = f'(fi).highpass(1, {args["cutoff_frequency_hz"]})'
    elif isinstance(plg, LowpassFilter) :
        name = f'lpf{codePlg(plg)}'
        param = f'(fi).lowpass(1, {args["cutoff_frequency_hz"]})'
    elif isinstance(plg, Limiter) :
        name = f'lim{codePlg(plg)}'
        param = f'(co).limiter_lad_mono(0, {args["threshold_db"]}, 1, 0.3, {args["release_ms"]})'   
    elif isinstance(plg, Compressor) :
        name = f'comp{codePlg(plg)}'
        param = f'(co).compressor_mono({args["ratio"]}, {args["threshold_db"]}, 0.5, {args["release_ms"]})'
    elif isinstance(plg, Reverb) :
        name = f'rev{codePlg(plg)}'
        param = f'(re).mono_freeverb({args["width"]}, 1, {args["wet_level"]}, {args["room_size"]})'
    
    return [name, f'{name} = {param};\n']


def faustify(board : Pedalboard) -> str :
    """
    Generate a Faust process from a Pedalboard
    """
    if list(board) == [] :
        return ""
    
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
            o = " :> _"
        
        acc = acc[:-2] + o
    
    else :
        plg = faust_str_block(hd)[0]
        if tl != [] :
            o = " <: " if isinstance(tl[0], Mix) else " : "
            acc = plg + o
        else :
            acc = plg

    
    return acc + faustify(tl)


def faust_header(board : Pedalboard) -> str :
    """
    Generate faust header and variable assignments
    """
    if list(board) == [] : 
        return ""

    hd, *tl = board
    if isinstance(hd, Chain) or isinstance(hd, Mix) :
        app = faust_header(hd)
    else :
        app = faust_str_block(hd)[1]
    return app + faust_header(tl)


def write_faust_file(board : Pedalboard, name="filter.dsp") :
    w = f'import("stdfaust.lib");\n\n{faust_header(board)}\nprocess = {faustify(board)};'
    file = open(name, "w")
    file.write(w)
    file.close


            
        