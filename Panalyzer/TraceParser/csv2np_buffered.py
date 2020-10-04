import csv
import numpy as np
import time

from pathlib import Path

from Panalyzer.utils.wr_extractor import wr_extractor
from Panalyzer.TraceParser.logic_masking import *


def arm32buffered_csv2np(fcsv, buffersize, num_reg):
    detailded_info = {'wr': None, 'regval': None, 'tick': None, 'masking': None, 'src1': None, 'src2': None,
                      'op': None}

    tick_list = np.zeros([buffersize], dtype=np.int64)
    wr_list = np.full([num_reg, 2, buffersize], False, dtype=bool)
    reg_val_table = np.zeros([num_reg, buffersize], dtype=np.int64)

    op_list = []
    src1_list = []
    src2_list = []

    with open(fcsv, mode='r') as infocsv:
        info_reader = csv.reader(infocsv)
        buffer_idx = 0
        chunk_counter = 0
        for idx, row in enumerate(info_reader):
            if idx % buffersize == 0:
                buffer_idx = 0
                chunk_counter = chunk_counter + 1
                print(chunk_counter)

                tick_list = np.zeros([buffersize], dtype=np.int64)
                wr_list = np.full([num_reg, 2, buffersize], False, dtype=bool)
                reg_val_table = np.zeros([num_reg, buffersize], dtype=np.int64)

                op_list = []
                src1_list = []
                src2_list = []
            else:
                buffer_idx = buffer_idx + 1
                tick_list[buffer_idx] = row[0]  # Tick number list: an 1 x line_number np array

                op_id = row[3]
                op_list.append(op_id)  # Opname is just a simple list of strings

                # Variables required for utility.wr_extractor, feed into the function, then abstract the required
                # data structure
                op_dst1 = row[4]
                op_dst2 = row[5]
                op_src1 = row[6]
                op_src2 = row[7]

                src1_list.append(op_src1)
                src2_list.append(op_src2)

                data = row[-1]
                for k in range(num_reg):  # kth register
                    val_prev = reg_val_table[k, buffer_idx - 1]
                    reg_name = 'r' + str(k)  # fp, lr, sp ,pc are renamed, simply
                    wr_list[k, 0, buffer_idx] = \
                        wr_extractor(reg_name, op_dst1, op_dst2, op_src1, op_src2, op_id, data, val_prev)[0]
                    wr_list[k, 1, buffer_idx] = \
                        wr_extractor(reg_name, op_dst1, op_dst2, op_src1, op_src2, op_id, data, val_prev)[1]
                    reg_val_table[k, buffer_idx] = \
                        wr_extractor(reg_name, op_dst1, op_dst2, op_src1, op_src2, op_id, data, val_prev)[2]
        return tick_list


if __name__ == "__main__":
    project_dir = Path(__file__).resolve().parent.parent
    csv_dir = project_dir.joinpath('tempcsv')
    fname = "fftbaseline.csv"

    start_time = time.perf_counter()  # Time counter starts
    T = arm32buffered_csv2np(csv_dir / fname, 10000, 16)
    elapsed_time_pandas = time.perf_counter() - start_time  # Stop point of the timer
    # tickexample = T['tick']
    # wrexample = T['wr']
    # regvalexample = T['regval']
    # masking_table = T['masking']
    # ops_list = T['op']
    #
    # # print('tick \n', tickexample, '\n wr: \n', wrexample, '\n regval:\n', regvalexample)
    # print(ops_list)