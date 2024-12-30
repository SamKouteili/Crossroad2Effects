import("stdfaust.lib");
addv = hslider("add", 0, -1.0, 1.0, 0.01);
process = _ + addv;