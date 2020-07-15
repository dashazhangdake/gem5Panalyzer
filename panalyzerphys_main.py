# imported Python packages
import matplotlib.pyplot as plt
import numpy as np
import time
import warnings
import argparse
import concurrent.futures
from pathlib import Path
import os

# Imported functions from utilities scripted by users
from Info2Csv import trace_to_csv
from utility.avf_calculator_packed import avf_calculator_packed_lite
from utility.preprocessing import PreProcessing

"""
    The function to calculate AVF of PhysRegfile from Accessing/Setting information
"""


def Phy_AVF(trace_ut, num_reg):
    """
    Use Python argparser to support terminal cmds, ONLY ACTIVATE ARGUMENT PARSER STATEMENTS ON TERMINAL ONLY MACHINES
    Command : python3 analyzer.py --filename "$(basename "$file")" > "$(basename "$file")"_avf.txt
    """
    start_time = time.perf_counter()  # Counter starts

    '''
          Initialization Stage: Get the total line number and convert raw file to csv
    '''
    # Initialize Path variables
    base_dir = Path(__file__).resolve().parent
    trace_dir = base_dir.joinpath('../TraceDir')
    all_result_dir = base_dir.joinpath('avf_result')
    result_dir = all_result_dir.joinpath(trace_ut + '_results_directory')
    trace_file_name = trace_ut
    print('Start panalyzing: ' + trace_file_name, ':')

    trace_file = trace_dir / (trace_file_name + '.txt')

    total_number_of_line = 0
    for line in open(trace_file):
        total_number_of_line += 1
    # of the input file
    print(total_number_of_line)

    '''
            Analyzing stage, this stage consists of InfoExtraction and Analyzing
    '''
    n_samples = 96  # Delcare the number of sampling points
    n_threads = 8  # Declare the number of threads
    number_of_window = n_samples

    start_line = 0
    analyzing_window_size = total_number_of_line // number_of_window  # Define start line, the size of analyzing window
    total_number_of_line_analyzed = analyzing_window_size * number_of_window

    thread_window = n_samples / n_threads

    window_counter = 0
    thread_window_counter = 0
    end_line = thread_window * analyzing_window_size * n_threads
    print(start_line, end_line)
    ace_temp = []  # unsorted ACE results from multiprocessing unit, whose data structure is a list

    while start_line < end_line:
        print('analyzing line: ', start_line, 'to line: ', start_line + analyzing_window_size * n_threads)
        with concurrent.futures.ProcessPoolExecutor() as executor:
            results_this_thread = [executor.submit(avf_calculator_packed_lite, trace_file,
                                                   start_line + i * analyzing_window_size, analyzing_window_size,
                                                   num_reg) for i in range(n_threads)]
            for f in concurrent.futures.as_completed(results_this_thread):
                if thread_window_counter < thread_window:
                    ace_temp.append(f.result())
                    window_counter += 1
        start_line = start_line + n_threads * analyzing_window_size
        thread_window_counter += 1

    ace_temp_np = np.array(ace_temp)  # Note at each analyzing window, Ace matrix's first row is Tick_list
    ace_matrix = ace_temp_np[ace_temp_np[:, -1].argsort()]  # Sort out-of-order ace array to and ascending order by tick
    ace_matrix[:, :-1] = np.cumsum(ace_matrix[:, :-1], axis=0)

    elapsed_time = time.perf_counter() - start_time  # Stop point of the timer

    os.makedirs(result_dir, exist_ok=True)
    avfres_path = result_dir / (trace_ut + 'avf.txt')
    with open(avfres_path, 'w') as f:
        print('%s %d %s %d %s %d %s %d' % ('threads: ', n_threads, ' ;window_size: ', analyzing_window_size,
                                           '; number_of_window: ', number_of_window, 'analyzed_lines: ',
                                           total_number_of_line_analyzed))  # Print Analyzing settings
        print('Time has passed: ', elapsed_time, 'seconds')  # A timer counts elapsed time

        runtime_tick = ace_matrix[:, -1]
        total_ace_cycle = np.zeros(window_counter)
        for i in range(0, num_reg):
            total_ace_cycle = ace_matrix[:, i] + total_ace_cycle
        avf_overall = total_ace_cycle / (num_reg * ace_matrix[:, -1])
        avf_overall_array = np.vstack((runtime_tick, avf_overall))  # the first row is runtime tick; second row is avf
        avf_overall_array = np.transpose(avf_overall_array)
        print(avf_overall_array, file=f)   # Dump the average AVF of Arch Regs at the end of analyzing window to a txt
        print('--------------CURRENT ANALYSIS DONE---------------------')
        avfres_csv_path = result_dir / (trace_ut + 'avf.csv')
        np.savetxt(avfres_csv_path, avf_overall_array, delimiter=",")

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument("-f", "--filename", required=True, help="name of raw input tracefile")
    ap.add_argument("-n", "--numreg", type=int, help="number of int phyregs")
    args_traceut = vars(ap.parse_args())['filename']
    args_nreg = vars(ap.parse_args())['numreg']
    Phy_AVF(args_traceut, args_nreg)
