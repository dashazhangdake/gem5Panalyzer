from InfoExtractor import *
from AvfAnalyzer import AvfAnalyzer
from utility.masking_calculator import masking_calculator
from pathlib import Path
import os


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


if __name__ == "__main__":
    parent_folder = Path(Path(os.getcwd()).parent)
    csv_folder = Path(str(parent_folder)+'/csv_traces')
    ace_return = avf_calculator_packed(csv_folder/'prime.csv', 0, 1000, 12)
    print(ace_return)

