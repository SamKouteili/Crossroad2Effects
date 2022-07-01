from pedalboard import Pedalboard, Plugin, Chain, Mix, Gain, Chorus, Reverb

def faust_str_block(plg : Plugin) -> str :
    if isinstance(plg, Gain) :
        return "GAIN"
    elif isinstance(plg, Reverb) :
        return "REVERB"
    elif isinstance(plg, Chorus) :
        return "CHORUS"

def faustify(board : Pedalboard) -> str :
        
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
            o = ":> _"
        
        acc = acc[:-2] + o
        
        print(f"ACC: {acc}, \n     ACC[-2]:{acc[-2:]}")
    
    # elif isinstance(hd, Chorus) or isinstance(hd, Reverb) :
    else :
        plg = faust_str_block(hd)
        if tl != [] :
            o = " <: " if isinstance(tl[0], Mix) else " : "
            acc = plg + o
        else :
            acc = plg
    
    return acc + faustify(tl)

def write_faust_file(board : Pedalboard, name="../filter.dsp") :
    
    file = open(name, "w")
    file.write('import("stdfaust.lib");\n\n')
    file.write(f'process = {faustify(board)};')
    file.close

    return


            
        