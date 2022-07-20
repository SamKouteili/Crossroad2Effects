from ntpath import join
from pedalboard import Pedalboard, Plugin, Chain, Mix
import time as ti
import numpy as np
import random as rd
from plgUtil import *
from paramOptim import *
from faustGen import *

P_MUTATION = 0.4
P_MERGE = 0.5

MAX_BOARD_SZ = 16

N_POP = 12
N_GEN = 100
N_SURVIVE = 24

TOL = 1.0e-5

WEIGHTED = True # Choosing whether to weight surviving parents for reproduction probability
CALC_ERROR = False # Choosing method of testing equivalence between two models

def evolve(dry, wet, sr) :
    """
    Primary genetic algorithm
    """
    # initialize models
    models = [Pedalboard([Chain([newPlg(plg)])]) for plg in PLUGINS]
    
    N_pop = N_POP

    cur_gen = 0
    converged = False
    elapsed = ti.time()
    best = None
    
    # do I want this here?
    models = generation(models, wet, sr, N_pop)
    file = open("result.txt", "w")

    modf = open("models.txt", "w")


    while cur_gen < N_GEN :
        
        for mod in models :
            if mod == None :
                modf.write("\n\n****ANOTHER NONE****\n\n")

        models = [mod for mod in models if mod != None]
        # models = [simplify_board(mod) for mod in models]
        errors = [calc_error(mod(dry, sr), wet) for mod in models]
        aridxs = np.argsort(errors)[:N_SURVIVE]
        errors = [errors[i] for i in aridxs]
        models = [models[i] for i in aridxs]

        if errors[0] <= TOL :
            converged = True
            break
            
        if N_pop < 56 :
            N_pop += 4
        
        # reset search (second time weighted parent choice)
        # if cur_gen == N_GEN/2 :

        #     best = [models[0], errors[0]]

        #     N_pop = N_POP

        #     models = [Pedalboard([Chain([newPlg(plg)])]) for plg in PLUGINS]

        #     print(f"Resetting search with unweighted parent distributions...")
        #     print(f" Best Model: {best[0]}\n Error: {best[1]}")

        models = generation(models, wet, sr, N_pop)

        if cur_gen % 10 == 0 :
            fausted, n = [faustify(model) for model in models], '\n'
            modf.write(f"GEN {cur_gen} ERRORS:\n    {errors}\nMODELS:\n{n.join(fausted)}\n\n")

        cur_gen += 1

        print(f"BEST MODEL THUS FAR ({cur_gen})\n ERROR: {errors[0]}\n MODEL: {models[0]}")

    
    # # Can move this inside the loop to do itertively; better results higher time ceiling
    # simplify_board(models[0])
    # models[0] = optimize_board(models[0], dry, wet, sr)
    # errors[0] = calc_error(models[0](dry, sr), wet)

    # if errors[0] < best[1] :
    #     best[0] = optimize_board(models[0], dry, wet, sr)
    #     best[1] = errors[0]
    # else :
    #     best[0] = optimize_board(best[0], dry, wet, sr)
    # simplify_board(best[0])

    modf.close()
    conv = "CONVERGED" if converged else "DID NOT CONVERGE"
    file.write(f"THE MODEL {conv}!\n ")
    file.write(f"Model: {models[0]}\n Error: {errors[1]}\n Time: {ti.time() - elapsed}")
    file.close()

    return models




def generation(models, wet, sr, N_pop):
    """ 
    create a generation of models from first two in existing list
    """
    while len(models) < N_pop:

        for model in models :
            if model == None : 
                models.remove(model)
            elif board_plg_num(model) > MAX_BOARD_SZ :
                models.remove(model)

        while True :
            parents = choose_parents(models)
            child = offspring(parents)
            if child != None : break
        models.append(child)
        
        # print(f"PARENT IN MODEL: {parents[0] in models or parents[1] in models}")
        # print(f"MODELS (type={type(models)}): {models}\n")
        # print(f"    PARENTS: {parents}\n")
        # print(f"    CHILD (type={type(child(parents))}): {child(parents)}\n")


        # check for duplicates (more accurate to calc error, but creates large bottleneck)
        for model in models[:-1]:   
            same_model = calc_error(model(wet, sr), models[-1](wet, sr)) < TOL \
                 if CALC_ERROR else equal_boards(model, models[-1])
            if same_model :
                models.pop()
                break

    return models



def choose_parents(models) :
    """
    Choose two parents with a linear probability scale (i.e. there is a linearly
    higher probability to pick the parent with the best accuracy)
    """
    if WEIGHTED :
        parents = []
        for _ in range(2) :
            idLin = rd.triangular(0, N_SURVIVE, 0)
            # idUni = rd.randint(0, N_survive/4)
            id = min(len(models)-1, int(idLin))
            # print(f"PARENT ID: {id} ")
            parents.append(newBoard(models[id]))
        return parents
    else :
        return [newBoard(rd.choice(models[:N_SURVIVE])) for _ in range(2)]
    # idLin = [int(rd.triangular(0, N_survive/2, 0)) for _ in range(2)]
    # idUni = [rd.randint(0, N_survive/2) for _ in range(2)]
    # return [models[min(len(models)-1, idLin[i] + idUni[i])] for i in range(2)]
    # return [newBoard(models[min(len(models)-1, i)]) for i in idx]


def offspring(parents) :
    """
    Create a child from two parents by either concatenating them wholly, concatenating
    parts of each parent, or mutating one of the parents.
    """
    if rd.random() <= P_MUTATION : 
        return mutate(parents[0])
    else :
        plen = [len(parent) for parent in parents]
        phalf = [list(parents[i])[:int(plen[i]/2)] for i in range(2)]
        if plen[0] > 1 and plen[1] > 1 and rd.random() <= P_MERGE :
            return rd.choice([addSeries, addParallel])(phalf[0], phalf[1])
        else :
            return rd.choice([addSeries, addParallel])(parents[0], parents[1])



def mutate(board : Pedalboard) :
    """
    Add a plugin at a random point in a Pedalboard
    """
    def chain_opt(elem) :
        return elem if isinstance(elem, Chain) else Chain([elem])

    # plugin in chain to mix
    def addAsMix(board, id, plg) :
        board[id] = Mix([chain_opt(board[id]), chain_opt(plg)])

    if board == Pedalboard([]) :
        return Pedalboard([rd.choice(PLUGINS)])
    
    r_id = rd.randint(0, len(board)-1) if len(board) > 1 else 0
    # print(f"Mutation: r_id={r_id}\n     Board = {board}")
    curr = board[r_id]

    if isinstance(curr, Mix) : 
        mutate(rd.choice(curr))
    else : 
        r_plg = newPlg(rd.choice(PLUGINS))
        rd.choice([Pedalboard.insert, addAsMix])(board, r_id, Chain([r_plg]))
        # print(f"Board after mutation: \n{board}")
        return newBoard(board)

