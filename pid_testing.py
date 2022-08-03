#!/usr/bin/python3

from djitellopy import Tello
from light_tracking_pid import track_light

px_movements = []

for m in len(px_movements):
    track_light(px_movements[m])