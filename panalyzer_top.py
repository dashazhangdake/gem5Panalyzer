from pathlib import Path
import numpy as np
import argparse
import time

from Panalyzer.parallel.parallel_analyzer import parallel_ace
from Panalyzer.preprocessing.txt2csv import txt2csv


def panalyzertop(filename):
    start_time = time.perf_counter()  # Counter starts

    reg_num = 16
    top_dir = Path(__file__).resolve().parent
    project_dir = Path(__file__).resolve().parent / 'Panalyzer'
    csv_dir = project_dir.joinpath('tempcsv')
    fin_csv = csv_dir/(filename + '.csv')

    f_length = txt2csv(filename, trace_dir=top_dir/'TraceExamples')

    n_datapoint = 1000
    flength = f_length
    thread = 8
    startp = 0
    n_of_groups = 8

    ace_test = parallel_ace(fin_csv, reg_num, n_datapoint, flength).multiprocessing_ace(thread, startp, n_of_groups)
    print(ace_test)
    print(np.shape(ace_test))
    elapsed_time = time.perf_counter() - start_time  # Stop point of the timer
    print('Time has passed: ', elapsed_time, 'seconds')  # A timer counts elapsed time


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument("-f", "--filename", required=True, help="name of raw input tracefile")
    args_traceut = vars(ap.parse_args())['filename']
    panalyzertop(args_traceut)
