from pedalboard import Pedalboard, Plugin, Chain, Mix, Gain, Chorus, Reverb
import time as ti
import numpy as np
import random as rd
from plgUtil import *
from paramOptim import *

P_MUTATION = 0.4
P_MERGE = 0.4


def evolve(dry, wet, sr) :

    tol=1.0e-5

    N_pop = 20
    N_gens = 100
    N_survive = 16

    # initialize models
    models = [Pedalboard([Chain([newPlg(plg)])]) for plg in PLUGINS]
    
    # do I want this here?
    models = generation(models, N_pop, N_survive)

    gen_num = 0
    converge = False
    elapsed = ti.time()

    modf = open("models.txt", "w")


    while gen_num < N_gens :

        models = [mod for mod in models if mod != None]
        errors = [calc_error(mod(dry, sr), wet) for mod in models]
        aridxs = np.argsort(errors)[:N_pop]
        errors = [errors[i] for i in aridxs]
        models = [models[i] for i in aridxs]

        if errors[0] <= tol :
            converge = True
            break
            
        if N_pop < 72 :
            N_pop += 4

        if gen_num % 5 == 0 :
            modf.write(f"GEN {gen_num} MODELS: \n   {models}\n\n")

        models = generation(models, N_pop, N_survive)

        print(f"BEST MODEL THUS FAR ({gen_num})\n ERROR: {errors[0]}\n MODEL: {models[0]}")

        gen_num += 1

    
    # Can move this inside the loop to do itertively; better results higher time ceiling
    models[0] = optimize_board(models[0], dry, wet, sr)
    errors[0] = calc_error(models[0](dry, sr), wet)

    file = open("result.txt", "w")
    conv = "CONVERGED" if converge else "DID NOT CONVERGE"
    file.write(f"THE MODEL {conv}!")
    file.write(f"Model: {models[0]} \nError: {models[0]}\n Time: {ti.time() - elapsed}")
    file.close()

    return models[0]




def generation(models, N, N_survive):
    """ 
    create a generation of models from first two in existing list
    """
    while len(models) < N:

        for model in models :
            if model == None : models.remove(model)

        # NOTE: higher probability for closer averages. 
        parents = [newBoard(rd.choice(models[:N_survive])) for _ in range(2)]
        # print(f"PARENT IN MODEL: {parents[0] in models or parents[1] in models}")
        # print(f"MODELS (type={type(models)}): {models}\n")
        # print(f"    PARENTS: {parents}\n")
        # print(f"    CHILD (type={type(child(parents))}): {child(parents)}\n")
        models += [child(parents)]

        # check for duplicates
        for model in models[:-1]:
            if model == models[:-1] :
                # print('Duplicate detected! Mutating again...')
                models.pop()
                break

    return models


def child(parents) :
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

