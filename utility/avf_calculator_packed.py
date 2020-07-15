from InfoExtractor import InfoExtractor
from InfoExtractor_lite import InfoExtractorLite
from AvfAnalyzer import AvfAnalyzer
from utility.masking_calculator import masking_calculator
from pathlib import Path
import os
import numpy as np


def avf_calculator_packed(csv_file_path, start, window_size, reg_count):
    ace_element = np.zeros(reg_count + 1, dtype=np.int64)
    all_info = InfoExtractor(csv_file_path, start, window_size, reg_count).get_wr_tick_list()
    t = all_info[2]
    h = all_info[0]
    rv = all_info[1]
    m = masking_calculator(csv_file_path, start, window_size, reg_count, rv)
    ace_element[-1] = t[-1]
    for i in range(reg_count):
        ace_local = (AvfAnalyzer(h[i, :, :], t, m[i, :]).ace_calculator_wr())[1, :]
        ace_element[i] = ace_local[-1]  # Only keep the final Ace tick number of each reg's each analyzing window
    return ace_element


def avf_calculator_packed_detail(csv_file_path, start, window_size, reg_count, sample_ratio=1):
    sample_number = int(sample_ratio * window_size)
    ace_local_matrix = np.zeros([reg_count + 1, sample_number], dtype=np.int64)
    all_info = InfoExtractor(csv_file_path, start, window_size, reg_count).get_wr_tick_list()
    t = all_info[2]
    h = all_info[0]
    rv = all_info[1]
    m = masking_calculator(csv_file_path, start, window_size, reg_count, rv)
    for i in range(reg_count):
        ace_local = (AvfAnalyzer(h[i, :, :], t, m[i, :]).ace_calculator_wr())[1, :]
        sample_idx = np.random.choice(window_size, sample_number)
        sampled_ace_local = ace_local[sample_idx]
        ace_local_matrix[i, :] = sampled_ace_local
        ace_local_matrix[i, -1] = ace_local[-1]
        ace_local_matrix[-1, :] = t[sample_idx]
        ace_local_matrix[-1, -1] = t[-1]
        ace_local_matrix = np.sort(ace_local_matrix, axis=1, kind='mergesort')
        # print('detail', ace_local_matrix)
    # print(ace_local_matrix, np.shape(ace_local_matrix))
    return ace_local_matrix


def avf_calculator_packed_lite(trace_file_path, start, window_size, reg_count):
    ace_element = np.zeros(reg_count + 1, dtype=np.int64)
    all_info = InfoExtractorLite(trace_file_path, start, window_size, reg_count).get_all_info()
    t = all_info[0]
    h = all_info[1]
    ace_element[-1] = t[-1]
    m = np.full([reg_count, window_size], 0, dtype=float)
    for i in range(reg_count):
        ace_local = (AvfAnalyzer(h[i, :, :], t, m[i, :]).ace_calculator_wr())[1, :]
        ace_element[i] = ace_local[-1]  # Only keep the final Ace tick number of each reg's each analyzing window
    return ace_element


def avf_calculator_packed_lite_hpi(trace_file_path, start, window_size, reg_count):
    ace_element = np.zeros(reg_count + 1, dtype=np.int64)
    all_info = InfoExtractorLite(trace_file_path, start, window_size, reg_count).get_all_info_hpi()
    t = all_info[0]
    h = all_info[1]
    ace_element[-1] = t[-1]
    m = np.full([reg_count, window_size], 0, dtype=float)
    for i in range(reg_count):
        ace_local = (AvfAnalyzer(h[i, :, :], t, m[i, :]).ace_calculator_wr())[1, :]
        ace_element[i] = ace_local[-1]  # Only keep the final Ace tick number of each reg's each analyzing window
    return ace_element


if __name__ == "__main__":
    # parent_folder = Path(Path(os.getcwd()).parent)
    # csv_folder = Path(str(parent_folder)+'/csv_traces')
    # ace_return = avf_calculator_packed(csv_folder/'prime.csv', 0, 1000, 12)
    # print(ace_return)

    base_dir = Path(__file__).resolve().parent.parent
    trace_dir = base_dir.joinpath('../TraceDir')
    ace_return = avf_calculator_packed_lite_hpi(trace_dir/'primehpi_phy.txt', 0, 10000, 0)
    print(ace_return)
