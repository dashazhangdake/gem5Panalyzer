import numpy as np
import csv
from itertools import islice
from utility.wr_extractor import *
'''
    This is just the top level of masking factor calculator module, the detailed codes define how to calculate masking 
    factor is in wr_extractor.m_calculator.
    m_calculator includes all considered cases of logic masking  
'''


def masking_calculator(trace_csv, start_line, file_length, reg_amount, reg_val_table):
    m_table = np.full([reg_amount, file_length], 0, dtype=float)
    with open(trace_csv, mode='r') as info_csv:
        info_window = islice(info_csv, start_line, start_line + file_length)
        info_reader = csv.reader(info_window)
        for i, row in enumerate(info_reader):  # Tick[i], or ith row in current window (start + i)
            op_src1 = row[6]
            op_src2 = row[7]
            op_id = row[3]
            #  # Test whether the current operand is a number or string, then convert type
            if (op_src1 is not None) and type(op_src1) is str and op_src1.isdigit():
                # If is a number, return int(str)
                op_src1 = int(op_src1)
            else:
                op_src1 = op_src1

            if (op_src2 is not None) and type(op_src2) is str and op_src2.isdigit():
                op_src2 = int(op_src2)
            else:
                op_src2 = op_src2

            for k in range(reg_amount):
                reg_name = 'r' + str(k)
                m_current = m_calculator(i, op_id, reg_name, op_src1, op_src2, reg_val_table)
                m_table[k, i] = m_current
    return m_table

