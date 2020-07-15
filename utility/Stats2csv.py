import csv
import numpy as np
import re
import os
from pathlib import Path
import math
"""
By default, the tick rate of gem5 is 1ps/tick. Default CPU frequency is set to 2GHz, then each cycle takes 500 ticks 
(0.5 ns)
"""


def find_nearest(array, value):
    idx = np.searchsorted(array, value, side="left")
    if idx > 0 and (idx == len(array) or math.fabs(value - array[idx-1]) < math.fabs(value - array[idx])):
        return idx-1
    else:
        return idx


def get_avf(avf_file_name, frequency=2):
    tickspercycle = 1 / frequency * 1000
    # Initialize Path variables to store converted csv file
    base_dir = Path(__file__).resolve().parent.parent
    csv_dir = base_dir.joinpath('csv_traces')
    csv_fname = csv_dir / (avf_file_name + ".csv")
    tick_list = []
    avf_list = []
    with open(csv_fname, mode="r") as info_csv:
        info_reader = csv.reader(info_csv)
        for i, row in enumerate(info_reader):
            avf_list.append(row[1])  # Tick number list: an 1 x line_number np array
            tick_list.append((row[0]))
        avfs = np.array(avf_list, dtype=float)
        ticks = np.array(tick_list, dtype=float)//tickspercycle
        avf_array = np.vstack((ticks, avfs))
    return avf_array


def stats2csv(stats_file_name, avf_file_name, trace_dir, frequency=2):
    tickspercycle = 1 / frequency * 1000
    avfarray = get_avf(avf_file_name)
    # Initialize Path variables to store converted csv file
    base_dir = Path(__file__).resolve().parent.parent
    csv_dir = base_dir.joinpath('csv_traces')
    trace_file_path = trace_dir / (stats_file_name + '.txt')
    csv_fname = csv_dir / (stats_file_name + ".csv")
    print(trace_file_path)
    # Processing raw txt trace file
    with open(csv_fname, "w", newline="") as my_empty_csv:
        writer = csv.writer(my_empty_csv)
        number_of_dump = 0
        current_cycles = 0
        committed_inst = 0
        int_reg_reads = 0
        int_reg_writes = 0
        mem_reads = 0
        mem_writes = 0
        rob_reads = 0
        rob_writes = 0
        squashed_inst_commit = 0
        cpi_sum = 0
        ipc_sum = 0
        branches = 0
        pvf = 0
        for i, line in enumerate(open(trace_file_path)):
            temp = re.findall('\d*\.?\d+', line)
            if "---------- Begin Simulation Statistics ----------" in line:
                number_of_dump += 1
            if "final_tick" in line:
                # Configured fitting function with qsort results
                current_cycles = int(temp[0]) // tickspercycle
                idxavf_nearest = find_nearest(avfarray[0, :], current_cycles)
                print(idxavf_nearest)
                pvf = avfarray[1, idxavf_nearest]
            if "Number of instructions committed" in line:
                committed_inst += int(temp[0])
            if "int_regfile_reads" in line:
                int_reg_reads += int(temp[0])
            if "int_regfile_writes" in line:
                int_reg_writes += int(temp[0])
            if "commit.op_class_0::MemRead" in line:
                mem_reads += int(temp[1])
            if "commit.op_class_0::MemWrite" in line:
                mem_writes += int(temp[1])
            if "commitSquashedInsts" in line:
                squashed_inst_commit += int(temp[0])
            if "rob_reads" in line:
                rob_reads += int(temp[0])
            if "rob_writes" in line:
                rob_writes += int(temp[0])
            if "CPI: Cycles Per Instruction" in line:
                cpi_sum += float(temp[0])
                cpi = cpi_sum/number_of_dump
            if "IPC: Instructions Per Cycle" in line:
                ipc_sum += float(temp[0])
                ipc = ipc_sum / number_of_dump
            if "Number of branches committed" in line:
                branches += float(temp[0])
            # # if "final_tick" in line

            if "---------- End Simulation Statistics   ----------" in line:
                writer.writerow([number_of_dump, ipc, current_cycles, committed_inst,
                                 int_reg_reads / current_cycles, int_reg_writes / current_cycles,
                                 rob_reads / current_cycles, rob_writes / current_cycles,
                                 mem_reads / committed_inst, mem_writes / committed_inst,
                                 branches / committed_inst, pvf])
    return number_of_dump


if __name__ == "__main__":  # Test
    base_dir1 = Path(__file__).resolve().parent.parent
    trace_dir1 = base_dir1.joinpath('../TraceDir')
    print(stats2csv("stats", "qsortbaselineavf", trace_dir1))
    # out_array = get_avf("qsortbaselineavf")
    # print(out_array[0, 3])