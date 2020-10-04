import numpy as np
import csv
from itertools import islice
from Panalyzer.utils.wr_extractor import wr_extractor
from Panalyzer.TraceParser.logic_masking import *
from pathlib import Path


class csv2np:
    def __init__(self, trace_csv, start_line, file_length, register_amount):
        self.trace_csv = trace_csv
        self.num_lines = file_length
        self.num_reg = register_amount
        self.start_point = start_line

    def tick_only(self):
        tick_info = {'tick': None, 'op': None}
        tick_list = np.zeros([self.num_lines], dtype=np.int64)
        op_list = []
        with open(self.trace_csv, mode='r') as info_csv:
            info_window = islice(info_csv, self.start_point, self.start_point + self.num_lines)
            info_reader = csv.reader(info_window)
            for i, row in enumerate(info_reader):
                tick_list[i] = row[0]  # Tick number list: an 1 x line_number np array
                op_list.append(row[3])
        tick_info['tick'] = tick_list
        tick_info['op'] = op_list
        return tick_info

    def arm32detailed(self, lineoffset):
        detailded_info = {'wr': None, 'regval': None, 'tick': None, 'masking': None, 'src1': None, 'src2': None,
                          'op': None}
        # Tick and opname
        tick_list = np.zeros([self.num_lines], dtype=np.int64)
        op_list = []
        src1_list = []
        src2_list = []
        # WR and reg value
        wr_list = np.full([self.num_reg, 2, self.num_lines], False, dtype=bool)
        reg_val_table = np.zeros([self.num_reg, self.num_lines], dtype=np.int64)
        with open(self.trace_csv, mode='r') as info_csv:
            # info_csv.seek(lineoffset[self.start_point])  # Try to use f.seek but failed
            info_window = islice(info_csv, self.start_point, self.start_point + self.num_lines)
            info_reader = csv.reader(info_window)
            for i, row in enumerate(info_reader):  # Tick[i], or ith row in file
                tick_list[i] = row[0]  # Tick number list: an 1 x line_number np array
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
                for k in range(self.num_reg):  # kth register
                    val_prev = reg_val_table[k, i - 1]
                    reg_name = 'r' + str(k)  # fp, lr, sp ,pc are renamed, simply
                    wr_list[k, 0, i] = \
                        wr_extractor(reg_name, op_dst1, op_dst2, op_src1, op_src2, op_id, data, val_prev)[0]
                    wr_list[k, 1, i] = \
                        wr_extractor(reg_name, op_dst1, op_dst2, op_src1, op_src2, op_id, data, val_prev)[1]
                    reg_val_table[k, i] = \
                        wr_extractor(reg_name, op_dst1, op_dst2, op_src1, op_src2, op_id, data, val_prev)[2]
            # if len(src1_list) <= 0:
            #     src1_list.append('dummy')
            # if len(src2_list) <= 0:
            #     src2_list.append('dummy')
            # if len(op_list) <= 0:
            #     op_list.append('dummy')

            m_table = arm32masking_calculator(self.num_lines, op_list, src1_list, src2_list, self.num_reg,
                                              reg_val_table).lmasking_calculator()
            detailded_info['wr'] = wr_list
            detailded_info['regval'] = reg_val_table
            detailded_info['tick'] = tick_list
            detailded_info['src1'] = src1_list
            detailded_info['src2'] = src2_list
            detailded_info['op'] = op_list
            detailded_info['masking'] = m_table

        return detailded_info


if __name__ == "__main__":
    project_dir = Path(__file__).resolve().parent.parent
    csv_dir = project_dir.joinpath('tempcsv')
    fname = "prime.csv"
    T = csv2np(csv_dir / fname, 0, 10, 16).arm32detailed()

    tickexample = T['tick']
    wrexample = T['wr']
    regvalexample = T['regval']
    masking_table = T['masking']
    op_list = T['op']

    # print('tick \n', tickexample, '\n wr: \n', wrexample, '\n regval:\n', regvalexample)
    print(op_list)
