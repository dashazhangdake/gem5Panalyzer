from pathlib import Path
import numpy as np
import argparse
import time
import os
from os import walk
import sys
import glob

from Panalyzer.parallel.parallel_analyzer import parallel_ace
from Panalyzer.preprocessing.txt2csv import txt2csv


# Multiprocessing module forced me to functionalize the top level code, users need to adjust configurations by modifying
# the function: panalyzertop
def panalyzertop(filename, mode='cumulative'):
    start_time = time.perf_counter()  # Time counter starts

    # Setup raw trace file Paths
    top_dir = Path(__file__).resolve().parent
    project_dir = Path(__file__).resolve().parent / 'Panalyzer'
    csv_dir = project_dir.joinpath('tempcsv')
    fin_csv = csv_dir / (filename + '.csv')

    # Setup AVF computation results Paths
    result_path = top_dir / "Panalyzer_results" / filename
    os.makedirs(result_path, exist_ok=True)
    lineoffset = []
    # check if we still get csv file in tempcsv directory
    if fin_csv.exists():
        print('csv file exists')
        # f_length = 10000000
        with open(result_path / (filename + '_log.txt'), 'r') as forigin:
            f_length = forigin.readline()
        flength = int(f_length)
    else:
        # Convert trace files from raw text to csv
        f_length, lineoffset = txt2csv(filename, trace_dir=top_dir / 'gem5traces' / 'exec_traces')
        flength = f_length  # By default, we are analyzing the entire trace file

    if mode == "cumulative":  # This Branch computes the cumulative A/PVFs through the program runtime
        # Cumulative Analyzer configurations
        reg_num = 16
        considered_reg_num = 15
        n_datapoint = 6000

        thread = 6
        startp = 0
        n_of_groups = 36

        ace_parallel = parallel_ace(fin_csv, reg_num, n_datapoint, flength).multiprocessing_ace(thread, startp,
                                                                                                n_of_groups, lineoffset)
    elif mode == "quanta":
        reg_num = 16
        considered_reg_num = 5

        thread = 6
        startp = 0
        n_of_groups = 2400
        n_datapoint = n_of_groups
        ace_parallel = parallel_ace(fin_csv, reg_num, n_datapoint, flength).multiprocessing_ace_q(thread, startp,
                                                                                                  n_of_groups,
                                                                                                  lineoffset)
    else:
        print("select a valid mode, terminate")
        sys.exit()

    actual_ace_size = np.shape(ace_parallel)
    elapsed_time = time.perf_counter() - start_time  # Stop point of the timer
    print('Time has passed: ', elapsed_time, 'seconds')  # A timer counts elapsed time

    # Redirect terminal logs to result dir
    with open(result_path / (filename + '_log.txt'), 'w') as f:
        print(f_length, file=f)  # Print Analyzing settings
        print('%s %d %s %d' % ('threads: ', thread, ' ;samples: ', n_datapoint), file=f)  # Print Analyzing settings
        print('Time has passed: ', elapsed_time, 'seconds', file=f)  # A timer counts elapsed time

    # Save averaged PVF to a csv file
    ace_matrix_all_regs = np.zeros([1, actual_ace_size[1]], dtype=np.float)
    ace_matrix_tick = ace_parallel[-1, :]
    for i in range(0, considered_reg_num):
        print('reg: ', i)
        ace_matrix_all_regs = ace_parallel[i, :] + ace_matrix_all_regs
    try:
        vf_all_regs = ace_matrix_all_regs / (considered_reg_num * ace_matrix_tick)
    except ZeroDivisionError:
        vf_all_regs = None

    vf_all_regs_with_timing = np.vstack((ace_matrix_tick, vf_all_regs))
    vf_all_regs_with_timing = np.transpose(vf_all_regs_with_timing)  # Transpose to two columns
    np.savetxt(result_path / (filename + "_pvf.csv"), vf_all_regs_with_timing, fmt='%10.5f', delimiter=",")

    # Cleanup after each vf analysis
    # os.remove(fin_csv)


if __name__ == '__main__':
    # via cmd prompt
    ap = argparse.ArgumentParser()
    ap.add_argument("-f", "--filename", required=True, help="name of raw input tracefile")
    ap.add_argument("-m", "--mode", required=True, help="analyzing mode")
    args_traceut = vars(ap.parse_args())['filename']
    args_mode = vars(ap.parse_args())['mode']
    panalyzertop(args_traceut, args_mode)

    # # run directly
    # top_dir1 = os.getcwd()  # use your path
    # tracepath = top_dir1 + '/gem5traces/exec_traces'
    # f = []
    # for (dirpath, dirnames, filenames) in walk(tracepath):
    #     f.extend(filenames)
    #     break
    # f = [fn.rstrip('.txt') for fn in f]
    # print(f)
    # # all_files = glob.glob(tracepath + "/*.txt")
    # # filenames = [fn.rstrip('.txt') for fn in all_files]
    # # print(filenames)
    #
    # for filename in f:
    #     panalyzertop(filename, 'cumulative')
