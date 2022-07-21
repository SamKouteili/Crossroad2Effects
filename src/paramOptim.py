from pedalboard import Pedalboard, Plugin, Chain, Mix
import numpy as np
from scipy.signal import stft
from scipy.optimize import minimize
from plgUtil import get_plg_args

def calc_error(arr1 : np.ndarray, arr2 : np.ndarray, fs=2048) -> int:
    """
    oc: @jatinchowdhury18
    Calculate the error between two wav files, using a combination of 
    mean-squared error and spectrogram loss
    """
    mean_square_error = np.mean((arr1 - arr2)**2, axis=None) # get mse

    nseg = 2048 # hop size

    # sum to mono (maybe do stereo eventually...)
    des = (arr1[:,0] + arr1[:,1]) / 2
    out = (arr2[:,0] + arr2[:,1]) / 2

    # compute spectrogram error
    _, _, Z_des = stft(des, fs=fs, nperseg=nseg, nfft=nseg*2)
    _, _, Z_out = stft(out, fs=fs, nperseg=nseg, nfft=nseg*2)
    freq_err = np.mean(np.abs(Z_des - Z_out), axis=None)

    return mean_square_error + freq_err


def get_param_error(argvals, argkeys, plg, board, input_buf, target_buf, samplerate) :
    """
    Retrieve error of Pedalboard module with certain parameters applied to a 
    singular plugin (plg) in the Pedalboard object (pb)
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

# def get_bounds(argkeys, argvals) 

def optimize_board(board : Pedalboard, input_buf, target_buf, samplerate, tol=1.0e-5) :
    """
    Optimize the variables of all plugins in a Pedalboard
    """
    for plg in list(board) :
        if isinstance(plg, Mix) or isinstance(plg, Chain) :
            optimize_board(plg, input_buf, target_buf, samplerate)
        else :
            optimize_plg_params(plg, board, input_buf, target_buf, samplerate)
    return board

