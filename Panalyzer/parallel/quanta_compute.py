"""
This function provides the indices of trace files to each multi-processing piece
Note n_threads must be dividable by n_quantas
For example, considering the scenario:
    10000 lines; 8 threads; analyzing starts from 0 and ends with 6000
    Require around 1000 samples out of 6000 in total
Slicing Steps:
    32 windows; 32 / 8 = 4 window groups
    size of each window = (start - end) // windows = 187
    sample_rate = (n_samples // windows) / size_window = 31 / 187

"""
import sys


def quanta_slice_compute(f_length, threads, n_quanta, n_sample=5):
    if threads > n_quanta:
        print("Number of threads should be smaller than the number of analyzing windows")
        sys.exit(0)
    length = f_length
    window_size = length // n_quanta
    n_bunch = n_quanta // threads
    sample_ratio = (n_sample / n_quanta) / window_size

    analyzed_length = n_bunch * threads * window_size

    sliced_window = {'window_size': window_size, 'n_groups': n_bunch,
                     'sample_ratio': sample_ratio, 'analyzing_length': analyzed_length}
    return sliced_window


if __name__ == "__main__":
    test_quanta = quanta_slice_compute(30000000, 6, 10000)
    print(test_quanta)
