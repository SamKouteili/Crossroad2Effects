import time as ti
import numpy as np
import random as rd
from pedalboard import Pedalboard, Plugin, Chain, Mix, Gain, Chorus, Reverb
from plgUtil import *
from paramOptim import *

P_MUTATION = 0.6


def evolve(dry, wet, sr) :

    tol=1.0e-5

    N_pop = 12
    N_gens = 20
    N_survive = 10

    # models all held here
    models = [Pedalboard([])]

    # create initial population
    for plg in PLUGINS : 
        models += Pedalboard([copyPlg(plg)])

    models = generation(models, N_pop, N_survive)

    gen_num = 0
    converge = False
    elapsed = ti.time()


    while gen_num < N_gens :

        errors = [calc_error(model(dry, sr), wet) for model in models]
        aridxs = np.argsort(errors)[:N_pop]
        errors = [errors[i] for i in aridxs]
        models = [models[i] for i in aridxs]

        if errors[0] <= tol :
            converge = True
            break
            
        if N_pop < 48:
            N_pop += 4

        models = generation(models, N_pop, N_survive)
    
    conv = "converged" if converge else "did not converge"
    print(f"The model {conv}!")
    print(f"Best Model: {models[0]} \nError: {models[0]}")

    return models[0]




def generation(models, N, N_survive):
    """
    oc: @jatinchowdhury18    
    create a generation of models from first two in existing list
    """
    while len(models) < N:
        parent1 = rd.choice(models[:N_survive])
        parent2 = rd.choice(models[:N_survive])
        models += child(parent1, parent2)

        # check for duplicates
        for model in models[:-1]:
            if model == models[:-1] :
                # print('Duplicate detected! Mutating again...')
                models.pop()
                break

    return models


def child(parent1, parent2) :
    mutation = (rd.random() <= P_MUTATION)
    print(f"Parent1: {parent1}   ||  Parent2: {parent2}")
    parents = [parent1, parent2]
    rd.shuffle(parents)
    print(f"Parents: {parents}")
    if mutation : 
        print(f"Mutating!!")
        return mutate(parents[0])
    else : 
        print(f"Concatenating parents in srs/prl")
        return rd.choice([addSeries, addParallel])(parents[0], parents[1])


def mutate(board : Pedalboard) :
    """
    Add a plugin at a rd.random point in a Pedalboard
    """
    def chain_opt(elem) :
        return elem if isinstance(elem, Chain) else Chain([elem])

    # plugin in chain to mix
    def addAsMix(board, id, plg) :
        board[id] = Mix([chain_opt(board[id]), chain_opt(plg)])
    
    r_id = rd.randint(0, len(board)-1) if len(board) > 1 else 0
    curr = board[r_id]

    if isinstance(curr, Mix) : 
        mutate(rd.choice(curr))
    else : 
        r_plg = copyPlg(rd.choice(PLUGINS))
        rd.choice([Pedalboard.insert, addAsMix])(board, r_id, Chain([r_plg]))
        print(f"Board after mutation: \n{board}")
        return board


