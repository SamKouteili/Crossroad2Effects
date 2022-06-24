import numpy as np
from pedalboard import Pedalboard, Chorus, Reverb, Mix, Chain, Gain, Plugin
from pedalboard.io import AudioFile
from scipy.optimize import minimize
from plgUtil import *

def get_param_error(argvals, argkeys, plg, board, input_buf, target_buf, samplerate) :
    """
    Retrieve error of Pedalboard module with certain parameters applied to a singular 
    plugin (plg) in the Pedalboard object (pb)
    
    """
    for i in range(len(argkeys)) : setattr(plg, argkeys[i], argvals[i])
    effected = board(input_buf, samplerate)
    
    return calc_error(effected, target_buf)

def optimize_plg_params(plg : Plugin, board : Pedalboard, input_buf, target_buf, samplerate, tol=1.0e-5) :
    """
    Optimize individual plugin parameters using scipy.optimize.minimize()
    """
    params = get_plg_args(plg)
    argkeys = list(params.keys())
    argvals = list(params.values())
    bounds = [(0, 1) if v <= 1 else (0, 2*v) for v in params.values()]

    if params == [] : return board

    result = minimize(get_param_error, argvals, \
                      args=(argkeys, plg, board, input_buf, target_buf, samplerate), tol=tol, \
                      bounds=bounds, options={'maxiter': 1000, 'eps': 1e-06, 'ftol': 1e-11, 'iprint': 1})
    
    for i in range(len(argkeys)) : setattr(plg, argkeys[i], result.x[i])
    
    return board