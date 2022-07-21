import("stdfaust.lib");

gainbb9a0 = +(1.0);
rev2e2d0 = (re).mono_freeverb(0.4724, 1, 1.0, 0.999996);
gainb7820 = +(1.0);
lima5950 = (co).limiter_lad_mono(0, 0.0, 1, 0.3, 100.0);
del1c930 = @(0.5);
hpff3940 = (fi).highpass(1, 50.0);

process = ((gainbb9a0)), ((rev2e2d0)) :> (gainb7820) <: ((lima5950)), ((del1c930)) :> (hpff3940);