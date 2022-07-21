/*** Error from Wet File: 0.000522 | Time to Generate: 93.75345 ***/
import("stdfaust.lib");

lpfc1ca0 = (fi).lowpass(1, 50.0);
lpf491b0 = (fi).lowpass(1, 50.0);
del3c000 = @(0.5);
rev846a0 = (re).mono_freeverb(0.988212, 1, 0.324687, 0.532281);
gainfed20 = +(0.999767);
hpfd1be0 = (fi).highpass(1, 50.0);

process = (lpfc1ca0) <: ((lpf491b0)), ((del3c000)) :> (rev846a0) : (gainfed20) : (hpfd1be0);