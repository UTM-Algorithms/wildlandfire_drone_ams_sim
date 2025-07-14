# Graph Generator

Creates a 2D route network for testing Wildlandfire Airspace Management UTM concepts.

## Outline

A route for the sim consists of squence of in-air waypoints(x,y) and drone starts
at LRZ and ends at LRZ. Configurable to start/end at same/other LRZs. Incorportated
Geofencing in that LRZs are grouped by geofences (different subgraphs).

## How to use

1. One scenario,
- `main__path_generator.py` inputs from `\path_input\`
- `main__path_generator.py` outputs to `\path_output\`
- `\plots\main_plot__path_generator.py` used for visualization outputs to `\path_output\`

2. Multiple scenarios, TODO
- `multi__path_generator.sh`
