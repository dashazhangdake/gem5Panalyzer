import csv
import numpy as np
import re

import os
from os import listdir
from os.path import isfile, join
from pathlib import Path
import math

from DLpredictor.DatasetConstructor.dataset_constructor_helper import *


def stats2csv(filename, stats_dir, pvf_dir, dataset_dir, frequency=2):
    tickspercycle = 1 / frequency * 1000

    stats_file_name = filename + '_stats'
    avf_file_name = pvf_dir.joinpath(filename, filename + '_pvf.csv')

    avfarray = get_avf(avf_file_name)

    # Initialize Path variables to store converted csv file
    stats_file_path = stats_dir / (stats_file_name + '.txt')
    csv_fname = dataset_dir / (stats_file_name + ".csv")
    print(stats_file_path)
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
        branches = 0
        pvf = 0
        pvftemp = 0
        loadsdep = 0
        storesdep = 0
        writer.writerow(['IDX', 'IPC', 'CYCLE', 'INSTNUM', 'REGR', 'REGW', 'ROBR', 'ROBW', 'MEMR', 'MEMW',
                        'BRANCH', 'LOADDEP', 'STOREDEP', 'PVF'])
        for i, line in enumerate(open(stats_file_path)):
            temp = re.findall('\d*\.?\d+', line)
            if "---------- Begin Simulation Statistics ----------" in line:
                number_of_dump += 1
            if "final_tick" in line:
                # Configured fitting function with qsort results
                current_cycles = int(temp[0]) // tickspercycle
                idxavf_nearest = find_nearest(avfarray[0, :], current_cycles)
                pvf = avfarray[1, idxavf_nearest]
            # if pvftemp == pvf:
            #     continue
            # else:
            #     pvftemp = pvf
            if "Number of instructions committed" in line:
                committed_inst = int(temp[0])
            if "int_regfile_reads" in line:
                int_reg_reads = int(temp[0])
            if "int_regfile_writes" in line:
                int_reg_writes = int(temp[0])
            if "commit.op_class_0::MemRead" in line:
                mem_reads = int(temp[1])
            if "commit.op_class_0::MemWrite" in line:
                mem_writes = int(temp[1])
            if "commitSquashedInsts" in line:
                squashed_inst_commit = int(temp[0])
            if "rob_reads" in line:
                rob_reads = int(temp[0])
            if "rob_writes" in line:
                rob_writes = int(temp[0])
            if "CPI: Cycles Per Instruction" in line:
                cpi = float(temp[0])
            if "IPC: Instructions Per Cycle" in line:
                ipc = float(temp[0])
            if "Number of branches committed" in line:
                branches = float(temp[0])
            if "loads inserted to the mem dependence unit" in line:
                loadsdep = float(temp[1])
            if "stores inserted to the mem dependence unit" in line:
                storesdep = float(temp[1])
            # # if "final_tick" in line
            if "---------- End Simulation Statistics   ----------" in line:
                # writer.writerow([number_of_dump, ipc, current_cycles, committed_inst,
                #                  int_reg_reads, int_reg_writes,
                #                  rob_reads, rob_writes,
                #                  mem_reads, mem_writes,
                #                  branches, loadsdep, storesdep, pvf])
                writer.writerow([number_of_dump, ipc, current_cycles, committed_inst,
                                 int_reg_reads / current_cycles, int_reg_writes / current_cycles,
                                 rob_reads / current_cycles, rob_writes / current_cycles,
                                 mem_reads / current_cycles, mem_writes / current_cycles,
                                 branches / current_cycles, loadsdep/current_cycles, storesdep/current_cycles, pvf])
    return number_of_dump


if __name__ == "__main__":  # Test
    project_dir = Path(__file__).resolve().parent.parent.parent
    base_dir = Path(__file__).resolve().parent.parent
    # Stats and trace
    gem5traces_dir = project_dir.joinpath('gem5traces')
    gem5stats_dir = gem5traces_dir.joinpath('gem5stats')
    # PVF directory
    pvf_resdir = project_dir.joinpath('Panalyzer_results')
    # Output directory
    dataset_dirin = base_dir.joinpath('datasets')

    # Construct datasets
    # fname = ['aes_dbaseline', 'aes_ebaseline', 'basicmath']

    files = [f for f in listdir(gem5stats_dir) if isfile(join(gem5stats_dir, f))]
    filenames = [fn.rstrip('_stats.txt') for fn in files]
    # filenames = ['qsortbaseline']
    for fname in filenames:
        stats2csv(fname, gem5stats_dir, pvf_resdir, dataset_dirin)

    print(filenames)
