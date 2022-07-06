from pedalboard import Pedalboard, Plugin, Chain, Mix, Gain, Chorus, Reverb


PLUGINS = [Reverb(), Chorus(), Gain()]


def copyPlg(plg : Plugin ) -> Plugin :
    if isinstance(plg, Gain) :
        return Gain()
    elif isinstance(plg, Reverb) :
        return Reverb()
    elif isinstance(plg, Chorus) :
        return Chorus()

def get_plg_args(plg : Plugin) -> dict :
    d = {}
    l = str(plg).split()[1:-2]
    for i in l :
        li = i.split("=")
        d[li[0]] = float(li[1])
    return d

def addSeries(board1, board2) :
    return Pedalboard(list(board1) + list(board2))

def addParallel(board1, board2) :
    return Pedalboard([Mix([Chain(list(board1)), Chain(list(board2))])])

def rmv(board, elem, ctr) :
    board.remove(elem)
    ctr -= 1
    

def simplify_chain(chain : Chain) :
    """
    Simplify plugin chain by combining effect instances
    """
    ctr = 1
 
    while ctr < len(chain) :
        
        cur = chain[ctr-1]
        nxt = chain[ctr]

        if type(cur) == type(nxt) :
            
            if isinstance(cur, Gain) :
                cur.gain_db = cur.gain_db + nxt.gain_db
                rmv(chain, nxt, ctr)

            if isinstance(cur, Chorus) :
                if abs(cur.mix - nxt.mix) <= 0.005 :
                    cur.mix = cur.mix + nxt.mix
                    rmv(chain, nxt, ctr)
            
            if isinstance(cur, Reverb) :
                if abs(cur.wet_level - nxt.wet_level) <= 0.005 and \
                     abs(cur.width - nxt.width) <= 0.005 :
                    cur.wet_level = cur.wet_level + nxt.wet_level
                    rmv(chain, nxt, ctr)         
                
        ctr += 1

def flatten_chain(chain : Chain) -> list[Plugin] :
    """
    Flatten plugin chain by raising Chain constructors up
    """
    if list(chain) == [] : return []

    hd, *tl = chain
    app = flatten_chain(hd) if isinstance(hd, Chain) else [hd]
    return app + flatten_chain(tl)

def simplify_board(board : Pedalboard) :
    """
    Simplify Pedalboard by simplifying and concatenating chains
    """
    ctr = 1
 
    while ctr < len(board) :
    
        if isinstance(board[ctr-1], Chain) :

            board[ctr-1] = Chain(flatten_chain(board[ctr-1]))
            simplify_chain(board[ctr-1])

            if isinstance(board[ctr], Chain) :

                board[ctr] = Chain(flatten_chain(board[ctr]))
                simplify_chain(board[ctr])

                board[ctr-1] = Chain(list(board[ctr-1]) + list(board[ctr]))
                rmv(board, board[ctr], ctr)
            
            if len(board[ctr-1]) == 0 :
                rmv(board, board[ctr-1], ctr)
            elif len(board[ctr-1]) == 1 :
                if isinstance(board[ctr-1][0], Mix) :
                    board[ctr-1] = board[ctr-1][0]
                
        ctr += 1  
