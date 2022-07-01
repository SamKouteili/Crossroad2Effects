import numpy as np
import scipy.signal as signal
# import matplotlib.pyplot as plt
from pedalboard import Pedalboard, Chorus, Reverb, Mix, Chain, Gain, Plugin
from pedalboard.io import AudioFile


PLUGINS = [Reverb(), Chorus(), Gain()]

# as cannot deepcopy
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


def simplify_chain(chn : Chain) -> Chain :
    
    ctr = 1

    def rmv(nxt, ctr) :
        chn.remove(nxt)
        ctr -= 1
    
    def sim(a, b) :
        return abs(a, b) <= 0.02
 
    while ctr < len(chn) :

        cur, nxt = chn[ctr-1], chn[ctr]

        # if isinstance(cur, Mix) :
            # mixes = [m for m in cur if isinstance(m, Mix)]

        if type(cur) == type(nxt) :

            if isinstance(cur, Gain) :
                cur.gain_db = cur.gain_db + nxt.gain_db
                rmv(nxt, ctr)

            if isinstance(cur, Chorus) :
                if sim(cur.mix, nxt.mix) :
                    cur.mix = cur.mix + nxt.mix
                    rmv(nxt, ctr)
            
            if isinstance(cur, Reverb) :
                if sim(cur.mix, nxt.mix) and sim(cur.width, nxt.width) :
                    cur.wet_level = cur.wet_level + nxt.wet_level
                    rmv(nxt, ctr)         
                
        ctr += 1
    
    return chn


def calc_error(des_wav : np.ndarray, out_wav : np.ndarray, fs=2048) -> int:
    """
    oc: @jatinchowdhury18
    Calculate the error between two wav files,
    using a combination  of mean-squared error
    and spectrogram loss
    """
    mean_square_error = np.mean((des_wav - out_wav)**2, axis=None) # get mse

    nseg = 2048 # hop size

    # sum to mono (maybe do stereo eventually...)
    des = (des_wav[:,0] + des_wav[:,1]) / 2
    out = (out_wav[:,0] + out_wav[:,1]) / 2

    # compute spectrogram error
    _, _, Z_des = signal.stft(des, fs=fs, nperseg=nseg, nfft=nseg*2)
    _, _, Z_out = signal.stft(out, fs=fs, nperseg=nseg, nfft=nseg*2)
    freq_err = np.mean(np.abs(Z_des - Z_out), axis=None)

    return mean_square_error + freq_err



