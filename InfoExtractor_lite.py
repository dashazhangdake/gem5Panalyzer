import numpy as np
from itertools import islice
from pathlib import Path


class InfoExtractorLite:
    def __init__(self, trace, start_line, file_length, register_amount):
        self.tracefile = trace
        self.num_lines = file_length
        self.num_reg = register_amount
        self.start_point = start_line

    def get_all_info(self):  # Outputs: Tick = get_tickop[0]; Op = get_tickop[1]
        tick_list = np.zeros([self.num_lines], dtype=np.int64)
        wr_list = np.full([self.num_reg, 2, self.num_lines], False, dtype=bool)
        with open(self.tracefile, mode='r') as info_file:
            info_window = islice(info_file, self.start_point, self.start_point + self.num_lines)
            for i, line in enumerate(info_window):
                split_line = line.strip().split(":")
                current_tick = split_line[0]
                current_access_type = split_line[3]
                tick_list[i] = current_tick
                for k in range(self.num_reg):
                    if "Setting int register " + str(k) in current_access_type:
                        wr_list[k, 0, i] = True
                    elif "Access to int register " + str(k) in current_access_type:
                        wr_list[k, 1, i] = True
                    else:
                        wr_list[k, 1, i] = False
                        wr_list[k, 1, i] = False
        return tick_list, wr_list

    def get_all_info_hpi(self):  # Outputs: Tick = get_tickop[0]; Op = get_tickop[1]
        tick_list = np.zeros([self.num_lines], dtype=np.int64)
        wr_list = np.full([self.num_reg, 2, self.num_lines], False, dtype=bool)
        with open(self.tracefile, mode='r') as info_file:
            info_window = islice(info_file, self.start_point, self.start_point + self.num_lines)
            for i, line in enumerate(info_window):
                split_line = line.strip().split(":")
                current_tick = split_line[0]
                current_access_type = split_line[-1]
                tick_list[i] = current_tick
                for k in range(self.num_reg):
                    if "Setting int reg " + str(k) in current_access_type:
                        wr_list[k, 0, i] = True
                    elif "Reading int reg " + str(k) in current_access_type:
                        wr_list[k, 1, i] = True
                    else:
                        wr_list[k, 1, i] = False
                        wr_list[k, 1, i] = False
        return tick_list, wr_list


if __name__ == "__main__":  # Test
    base_dir = Path(__file__).resolve().parent
    trace_dir = base_dir.joinpath('../TraceDir')
    T = InfoExtractorLite(trace_dir / 'primehpi_phy.txt', 20, 30, 56).get_all_info_hpi()[0]
    WR = InfoExtractorLite(trace_dir / 'primehpi_phy.txt', 0, 30, 56).get_all_info_hpi()[1][1, :, :]
    print(T)
    print(WR)
