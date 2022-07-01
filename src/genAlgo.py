import numpy as np
from pedalboard import Pedalboard, Chorus, Reverb, Mix, Chain, Gain, Plugin
from pedalboard.io import AudioFile
from plgUtil import *
from paramOptim import optimize_plg_params
from faustify import faustify
import typing
from random import choice, randint


def mutate(board : Pedalboard) :

    def chain_opt(elem) :
        return elem if isinstance(elem, Chain) else Chain([elem])

    # plugin in chain to mix
    def addAsMix(board, id, plg) :
        board[id] = Mix([chain_opt(board[id]), chain_opt(plg)])
    
    r_id = randint(0, len(board)-1)
    curr = board[r_id]

    if isinstance(curr, Mix) : 
        mutate(choice(curr))
    else : 
        r_plg = copyPlg(choice(PLUGINS))
        choice([Pedalboard.insert, addAsMix])(board, r_id, Chain([r_plg])) 

def rmv(board, elem, ctr) :
    board.remove(elem)
    ctr -= 1
    
def sim(a, b) :
    return abs(a - b) <= 0.02

def simplify_chain(chain : Chain) :
    
    ctr = 1
 
    while ctr < len(chain) :

        if type(chain[ctr-1]) == type(chain[ctr]) :

            if isinstance(chain[ctr-1], Gain) :
                chain[ctr-1].gain_db = chain[ctr-1].gain_db + chain[ctr].gain_db
                rmv(chain, chain[ctr], ctr)

            if isinstance(chain[ctr-1], Chorus) :
                if sim(chain[ctr-1].mix, chain[ctr].mix) :
                    chain[ctr-1].mix = chain[ctr-1].mix + chain[ctr].mix
                    rmv(chain, chain[ctr], ctr)
            
            if isinstance(chain[ctr-1], Reverb) :
                if sim(chain[ctr-1].wet_level, chain[ctr].wet_level) and \
                     sim(chain[ctr-1].width, chain[ctr].width) :
                    chain[ctr-1].wet_level = chain[ctr-1].wet_level + chain[ctr].wet_level
                    rmv(chain, chain[ctr], ctr)         
                
        ctr += 1


def flatten_chain(chain : Chain) -> list :

    if list(chain) == [] : return []

    hd, *tl = chain
    app = flatten_chain(hd) if isinstance(hd, Chain) else [hd]
    return app + flatten_chain(tl)

def simplify_board(board : Pedalboard) :
   
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
