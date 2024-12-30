import("stdfaust.lib");
mulv = hslider("mul", 1, 0.0, 2.0, 0.01);
process = _ * mulv;