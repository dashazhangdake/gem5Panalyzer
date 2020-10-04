import csv
import numpy as np
import multiprocessing as mp
import time

from pathlib import Path

from Panalyzer.utils.wr_extractor import wr_extractor
from Panalyzer.TraceParser.logic_masking import *


def arm32buffered_read_once(fcsv, buffersize, threads, num_reg):
    chunksize = threads * buffersize
    detailded_info = {'wr': None, 'regval': None, 'tick': None, 'masking': None, 'src1': None, 'src2': None,
                      'op': None}
    # Initialize buffered tick/wr/reg_val
    tick_list = np.zeros([chunksize], dtype=np.int64)
    wr_list = np.full([num_reg, 2, chunksize], False, dtype=bool)
    reg_val_table = np.zeros([num_reg, chunksize], dtype=np.int64)

    # Initialize internal variables for buffered info
    op_list = []
    src1_list = []
    src2_list = []

    with open(fcsv, mode='r') as infocsv:
        info_reader = csv.reader(infocsv)
        chunk_idx = 0
        chunk_counter = 0
        for line_number, row in enumerate(info_reader):
            if line_number % chunksize == 0:  # If reached the end of chunk
                if chunk_counter > 0:
                    masking_table = arm32masking_calculator(chunksize, op_list, src1_list, src2_list, num_reg,
                                                            reg_val_table).lmasking_calculator()
                    detailded_info['wr'] = wr_list
                    detailded_info['regval'] = reg_val_table
                    detailded_info['tick'] = tick_list
                    detailded_info['src1'] = src1_list
                    detailded_info['src2'] = src2_list
                    detailded_info['op'] = op_list
                    detailded_info['masking'] = masking_table

                chunk_idx = 0  # reset chunk idx and add 1 to chunk counter
                chunk_counter += 1

                # rest internal states
                tick_list = np.zeros([chunksize], dtype=np.int64)
                wr_list = np.full([num_reg, 2, chunksize], False, dtype=bool)
                reg_val_table = np.zeros([num_reg, chunksize], dtype=np.int64)
                op_list = []
                src1_list = []
                src2_list = []
                chunk_idx = chunk_idx + 1
                tick_list[chunk_idx] = row[0]
                op_id = row[3]
                op_list.append(op_id)  # Opname is just a simple list of strings

                # internal_variables
                op_dst1 = row[4]
                op_dst2 = row[5]
                op_src1 = row[6]
                op_src2 = row[7]
                src1_list.append(op_src1)
                src2_list.append(op_src2)
                data = row[-1]

                for k in range(num_reg):  # iterate thru arch registers
                    val_prev = reg_val_table[k, chunk_idx - 1]
                    reg_name = 'r' + str(k)  # fp, lr, sp ,pc are renamed, simply
                    wr_list[k, 0, chunk_idx] = \
                        wr_extractor(reg_name, op_dst1, op_dst2, op_src1, op_src2, op_id, data, val_prev)[0]
                    wr_list[k, 1, chunk_idx] = \
                        wr_extractor(reg_name, op_dst1, op_dst2, op_src1, op_src2, op_id, data, val_prev)[1]
                    reg_val_table[k, chunk_idx] = \
                        wr_extractor(reg_name, op_dst1, op_dst2, op_src1, op_src2, op_id, data, val_prev)[2]
            else:
                tick_list[chunk_idx] = row[0]
                op_id = row[3]
                op_list.append(op_id)  # Opname is just a simple list of strings

                # internal_variables
                op_dst1 = row[4]
                op_dst2 = row[5]
                op_src1 = row[6]
                op_src2 = row[7]
                src1_list.append(op_src1)
                src2_list.append(op_src2)
                data = row[-1]

                for k in range(num_reg):  # iterate thru arch registers
                    val_prev = reg_val_table[k, chunk_idx - 1]
                    reg_name = 'r' + str(k)  # fp, lr, sp ,pc are renamed, simply
                    wr_list[k, 0, chunk_idx] = \
                        wr_extractor(reg_name, op_dst1, op_dst2, op_src1, op_src2, op_id, data, val_prev)[0]
                    wr_list[k, 1, chunk_idx] = \
                        wr_extractor(reg_name, op_dst1, op_dst2, op_src1, op_src2, op_id, data, val_prev)[1]
                    reg_val_table[k, chunk_idx] = \
                        wr_extractor(reg_name, op_dst1, op_dst2, op_src1, op_src2, op_id, data, val_prev)[2]

                chunk_idx = chunk_idx + 1

        return tick_list


if __name__ == "__main__":
    project_dir = Path(__file__).resolve().parent
    csv_dir = project_dir.joinpath('Panalyzer', 'tempcsv')
    fname = "fftbaseline.csv"

    start_time = time.perf_counter()  # Time counter starts
    T = arm32buffered_read_once(csv_dir / fname, 10000, 6, 16)
    elapsed_time_pandas = time.perf_counter() - start_time  # Stop point of the timer