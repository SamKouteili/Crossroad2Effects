from pedalboard import Pedalboard, Plugin, Chorus, Reverb, Mix, Chain

def faust_block(plg : Plugin) -> str :
    return "Node"

def faustify(board : Pedalboard) -> str :
        
    if board == [] :
        return ""
    
    (hd, *tl), acc = board, ""
            
    if isinstance(hd, Chain) :
        acc = '(' + faustify(hd) + ')'
        if tl != [] :
            o = "<: " if isinstance(tl[0], Mix) else ": "
            acc += + o
    
    elif isinstance(hd, Mix) :
        for fx in hd :
            inn = faustify([fx])
            if isinstance(fx, Mix) :
                inn = "_ <: " + inn
            acc += '(' + inn + '), '
        
        
        acc = acc[:-2] + " :> _"
    
    elif isinstance(hd, Chorus) or isinstance(hd, Reverb):
        plg = faust_block(hd)
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


            
        