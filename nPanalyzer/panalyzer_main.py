# imported Python packages
# import matplotlib.pyplot as plt
import numpy as np
import time
import warnings
import argparse
import concurrent.futures
from pathlib import Path
import os

# Imported functions from utilities scripted by users
from Info2Csv import trace_to_csv
from utility.avf_calculator_packed import avf_calculator_packed
from utility.preprocessing import preprocessing


def main(trace_ut, debug=0):
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
    csv_dir = base_dir.joinpath('csv_traces')
    all_result_dir = base_dir.joinpath('avf_result')
    result_dir = all_result_dir.joinpath(trace_ut + '_results_directory')
    preprocessing(trace_ut, trace_dir)
    original_trace=trace_dir / (trace_ut + '.txt')
    os.remove(original_trace) # remove the original_trace
    trace_file_name = trace_ut + '_p'  # TUT(trace file which is preprocessed under test)
    print('Start panalyzing: ' + trace_file_name, ':')

    if debug == 0:
        total_number_of_line = trace_to_csv(trace_file_name, trace_dir)  # Convert raw file to csv & Record the length of
        print(total_number_of_line)
        # the input file
    else:
        total_number_of_line = 14000
    csv_file = csv_dir / (trace_file_name + '.csv')

    #  ---  TO DO IN THE FUTURE ---#
    log_file = result_dir/(trace_file_name + '_avf_log.csv')

    '''
            Analyzing stage, this stage consists of InfoExtraction and Analyzing
    '''
    num_reg = 16  # Number of the "general" use arch-registers, number of special purpose regs is 4 in ARMv7

    n_samples = 32	# Delcare the number of sampling points
    n_threads = 16  # Declare the number of threads
    number_of_window = n_samples
    
    start_line = 0
    analyzing_window_size = total_number_of_line // (number_of_window)  # Define start line, the size of analyzing window
    total_number_of_line_analyzed = analyzing_window_size * number_of_window
    
    thread_window = n_samples / n_threads

    print('%s %d %s %d %s %d' % ('threads: ', n_threads, ' ;window_size: ', analyzing_window_size,
                                 '; number_of_window: ', number_of_window))  # Analyzing threads/window
    # settings

    window_counter = 0
    thread_window_counter = 0
    end_line = thread_window * analyzing_window_size * n_threads
    print(start_line, end_line)
    ace_temp = []  # unsorted ACE results from multiprocessing unit, whose data structure is a list

    while start_line < end_line:
        print('analyzing line: ', start_line, 'to line: ', start_line + analyzing_window_size * n_threads)
        with concurrent.futures.ProcessPoolExecutor() as executor:
            results_this_thread = [executor.submit(avf_calculator_packed, csv_file,
                                                   start_line + i * analyzing_window_size, analyzing_window_size,
                                                   num_reg) for i in range(n_threads)]
            for f in concurrent.futures.as_completed(results_this_thread):
                if thread_window_counter < thread_window:
                    ace_temp.append(f.result())
                    window_counter += 1
        start_line = start_line + n_threads * analyzing_window_size
        thread_window_counter += 1

    ace_temp_np = np.array(ace_temp)     # Note at each analyzing window, Ace matrix's first row is Tick_list
    ace_matrix = ace_temp_np[ace_temp_np[:, -1].argsort()]  # Sort out-of-order ace array to and ascending order by tick
    ace_matrix[:, :-1] = np.cumsum(ace_matrix[:, :-1], axis=0)

    elapsed_time = time.perf_counter() - start_time  # Stop point of the timer

    os.makedirs(result_dir, exist_ok=True)
    avfres_path = result_dir/(trace_ut + 'avf.txt')
    with open(avfres_path, 'w') as f:
        print('Time has passed: ', elapsed_time, 'seconds', file=f)  # A timer counts elapsed time

        # # First Figure: pvf of r0~12
        # plt.figure(0)  # NOTE: Plot function disabled for systems without GUI
        total_ace_gpregs03 = np.zeros(window_counter)
        for i in range(0, 4):
            print('avf of REG', '[', i, ']:', ace_matrix[:, i] / ace_matrix[:, -1], file=f)
            total_ace_gpregs03 = total_ace_gpregs03 + ace_matrix[:, i]
        avf_list_03 = total_ace_gpregs03 / (ace_matrix[:, -1] * 4)

        total_ace_gpregs412 = np.zeros(window_counter)
        for i in range(4, 13):
            print('avf of REG', '[', i, ']:', ace_matrix[:, i] / ace_matrix[:, -1], file=f)
            total_ace_gpregs412 = total_ace_gpregs412 + ace_matrix[:, i]
        avf_list_412 = total_ace_gpregs412 / (ace_matrix[:, -1] * 9)
        # plt.plot(ace_matrix[:, -1], avf_list_03, label='Average PVF of reg[0~3]')
        # plt.plot(ace_matrix[:, -1], avf_list_412, label='Average PVF of reg[4 ~ 12]')
        # plt.title("Average PVFs of R[0:12]", fontsize=12, fontweight=0, color='orange')
        # plt.legend()
        # plt.xlabel("RuntimeTick")
        # plt.ylabel("PVF")

        # # Second Figure: pvf of r13 ~ r15
        # plt.figure(1)
        for i in range(13, num_reg):
            reg_name = ['sp', 'lr', 'pc']
            label_name = reg_name[i-13]
            print('avf of REG', '[', i, ']:', ace_matrix[:, i] / ace_matrix[:, -1], file=f)
        # plt.plot(ace_matrix[:, -1], np.divide(ace_matrix[:, i], ace_matrix[:, -1]), label=label_name)
        # plt.title("Average PVFs of sp; lr, pc")
        # plt.legend()
        # plt.xlabel("RuntimeTick")
        # plt.ylabel("PVF")

        print('average AVF of r[0:3] over time:', '\n', avf_list_03)
        print('average AVF of r[4:12] over time:', '\n', avf_list_412)

        total_ace_cycle = 0
        for i in range(0, num_reg):
            total_ace_cycle = ace_matrix[-1, i] + total_ace_cycle
        avf_overall = total_ace_cycle / (num_reg * ace_matrix[-1, -1])
        print('average AVF of Arch Regs at the end of analyzing window: ', avf_overall, file=f)
        # plt.show()

        '''
        Performance statistics: Memory consumption; Disabled when using ACCRE
        '''
        # pid = os.getpid()
        # py = psutil.Process(pid)
        # memoryUse = py.memory_info()[0] / 2. ** 30  # memory use in GB
        # print('memory use:', memoryUse, "GB")
        print('--------------CURRENT ANALYSIS DONE---------------------')


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument("-f", "--filename", required=True, help="name of raw input tracefile")
    args_traceut = vars(ap.parse_args())['filename']
    main(args_traceut, 0)
