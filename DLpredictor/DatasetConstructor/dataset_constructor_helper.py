import numpy as np
import math
import csv

"""
By default, the tick rate of gem5 is 1ps/tick. Default CPU frequency is set to 2GHz, then each cycle takes 500 ticks 
(0.5 ns)
"""


def find_nearest(array, value):
    idx = np.searchsorted(array, value, side="left")
    if idx > 0 and (idx == len(array) or math.fabs(value - array[idx - 1]) < math.fabs(value - array[idx])):
        return idx - 1
    else:
        return idx


def get_avf(avf_file, frequency=2):
    tickspercycle = 1 / frequency * 1000
    tick_list = []
    avf_list = []
    with open(avf_file, mode="r") as info_csv:
        info_reader = csv.reader(info_csv)
        for i, row in enumerate(info_reader):
            avf_list.append(row[1])  # Tick number list: an 1 x line_number np array
            tick_list.append((row[0]))
        avfs = np.array(avf_list, dtype=float)
        ticks = np.array(tick_list, dtype=float) // tickspercycle
        avf_array = np.vstack((ticks, avfs))
    return avf_array
