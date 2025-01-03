from pedalboard import Pedalboard, Plugin, Chain, Mix, Delay, HighpassFilter, LowpassFilter
from Plugins import *

# List of plugin blocks considered by the genetic algorithm.
PLUGINS = BASE_PLUGINS + ADDITIONAL_PLUGINS

def isAdd(plg) :
    return list(plg.parameters.keys).count('add') == 1

def isMul(plg) :
    return list(plg.parameters.keys).count('mul') == 1


def get_plg_args(plg : Plugin) -> dict :
    """
    Retrieve argument dictionary of a Plugin
    """
    d = {}
    l = str(plg).split()[1:-2]
    for i in l :
        li = i.split("=")
        d[li[0]] = float(li[1])
    return d

def gen_plg_dict() :
    """
    Generates a string dictionary of all base plugins.
    """
    d = {}
    for plg in PLUGINS : 
        d[strPlg(plg)] = 0 
    return d

def newPlg(plg : Plugin) -> Plugin :
    """
    New instance of a Plugin (as Pedalboard objects are not pickleable)
    {Note: user defined plugins need to be instantiated here as well}
    """
    if isinstance(plg, Mix) :
        return Mix([newPlg(_plg) for _plg in list(plg)])
    elif isinstance(plg, Chain) :
        return Chain([newPlg(_plg) for _plg in list(plg)])
    elif isinstance(plg, Delay) :
        return Delay(mix=1)
    elif isinstance(plg, HighpassFilter) :
        return HighpassFilter()
    elif isinstance(plg, LowpassFilter) :
        return LowpassFilter()
    elif isAdd(plg) :
        return Add(plg.add)
    elif isMul(plg) :
        return Mul(plg.mul)

def strPlg(plg : Plugin) -> Plugin :
    """
    String instance of Plugins
    """
    if isinstance(plg, Delay) :
        return "Delay(mix=1)"
    elif isinstance(plg, HighpassFilter) :
        return "HighpassFilter()"
    elif isinstance(plg, LowpassFilter) :
        return "LowpassFilter()"
    elif isAdd(plg) :
        return f"Add({plg.add})"
    elif isMul(plg) :
        return f"Mul({plg.add})"
    
def codePlg(plg : Plugin) -> Plugin :
    """ Function that generates concise ID for each plugin """
    return str(plg)[len(str(plg))-6:-1]


def newBoard(board : Pedalboard) -> Pedalboard :
    """ New instance of a Pedalboard """
    return Pedalboard([newPlg(plg) for plg in list(board)])

def equal_boards(a : Pedalboard, b : Pedalboard) -> bool : 
    """
    Check if two boards contain the same plugins in the same order
    """
    if len(a) != len(b) :
        return False
    for i in range(len(a)) :
        if type(a[i]) != type(b[i]) : return False
    return True

def board_plg_num(board : Pedalboard) -> int :
    """
    Count the number of plugins in a board (excluding chain and mix)
    """
    if list(board) == [] :
        return 0

    hd, *tl = board
    ad = board_plg_num(hd) if isinstance(hd, Chain) or isinstance(hd, Mix) else 1
    return ad + board_plg_num(tl)


def addSeries(board1, board2) :
    """ Chain two boards in series """
    return Pedalboard(list(board1) + list(board2))

def addParallel(board1, board2) :
    """ Chain two boards in parallel """
    return Pedalboard([Mix([Chain(list(board1)), Chain(list(board2))])])
    

def simplify_chain(chain : Chain) :
    """
    Simplify plugin chain by combining effect instances
    """
    def rmv(board, elem, ctr) :
        board.remove(elem)
        ctr -= 1    

    ctr = 1
 
    while ctr < len(chain) :
        
        cur = chain[ctr-1]
        nxt = chain[ctr]

        if type(cur) == type(nxt) and not (isinstance(cur, Mix) or isinstance(cur, Chain)) :
            if isinstance(cur, Delay) :
                cur.delay_seconds += nxt.delay_seconds  
            if isinstance(cur, HighpassFilter) :
                cur.cutoff_frequency_hz = min(cur.cutoff_frequency_hz, nxt.cutoff_frequency_hz)
            if isinstance(cur, LowpassFilter) :
                cur.cutoff_frequency_hz = max(cur.cutoff_frequency_hz, nxt.cutoff_frequency_hz)
            if isAdd(cur) :
                cur.add += nxt.add
            if isMul(cur) :
                cur.mul *= nxt.mul
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
    def rmv(board, elem, ctr) :
        board.remove(elem)
        ctr -= 1
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
    
    return board
