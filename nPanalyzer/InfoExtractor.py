import numpy as np
import csv
from itertools import islice
from utility.wr_extractor import wr_extractor


class InfoExtractor:
    def __init__(self, trace_csv, start_line, file_length, register_amount):
        self.trace_csv = trace_csv
        self.num_lines = file_length
        self.num_reg = register_amount
        self.start_point = start_line

    def get_tickop_list(self):  # Outputs: Tick = get_tickop[0]; Op = get_tickop[1]
        tick_list = np.zeros([self.num_lines], dtype=np.int64)
        op_list = []
        with open(self.trace_csv, mode='r') as info_csv:
            info_window = islice(info_csv, self.start_point, self.start_point + self.num_lines)
            info_reader = csv.reader(info_window)
            for i, row in enumerate(info_reader):
                tick_list[i] = row[0]  # Tick number list: an 1 x line_number np array
                op_list.append(row[3])
        return tick_list, op_list

    """
    W/R List is a num_reg x 2 x len(file) np array
        TICK INDEX : 1, 2, 3, 4, 5 ......
    W = WR[reg(k), 0, line_number]               [F T F T F]
    R = WR[reg(k), 1, line_number]               [F F F F T]
    
    Reg_val_table is a num_reg x len(file) np array storing Reg[k] value at each tick, 
    which will be referenced when calculating M
    """

    def get_wr_tick_list(self):
        # Tick and opname
        tick_list = np.zeros([self.num_lines], dtype=np.int64)
        op_list = []
        # WR and reg value
        wr_list = np.full([self.num_reg, 2, self.num_lines], False, dtype=bool)
        reg_val_table = np.zeros([self.num_reg, self.num_lines], dtype=np.int64)
        with open(self.trace_csv, mode='r') as info_csv:
            info_window = islice(info_csv, self.start_point, self.start_point + self.num_lines)
            info_reader = csv.reader(info_window)
            for i, row in enumerate(info_reader):  # Tick[i], or ith row in file
                tick_list[i] = row[0]  # Tick number list: an 1 x line_number np array
                op_list.append(row[3])  # Opname is just a simple list of strings

                # Variables required for utility.wr_extractor, feed into the function, then abstract the required
                # data structure
                op_dst1 = row[4]
                op_dst2 = row[5]
                op_src1 = row[6]
                op_src2 = row[7]
                op_id = row[3]
                data = row[-1]
                for k in range(self.num_reg):  # kth register
                    val_prev = reg_val_table[k, i - 1]
                    reg_name = 'r' + str(k)  # fp, lr, sp ,pc are "special registers", these registers
                    # will be handled later
                    wr_list[k, 0, i] = \
                        wr_extractor(reg_name, op_dst1, op_dst2, op_src1, op_src2, op_id, data, val_prev)[0]
                    wr_list[k, 1, i] = \
                        wr_extractor(reg_name, op_dst1, op_dst2, op_src1, op_src2, op_id, data, val_prev)[1]
                    reg_val_table[k, i] = \
                        wr_extractor(reg_name, op_dst1, op_dst2, op_src1, op_src2, op_id, data, val_prev)[2]

                # # ------------------DISABLED BLOCK AS WE RENAMED SP REGISTERS IN PREPROCESSED MODULE--------------- ##
                # # Frame pointer, i.e, fp(r11), we place w/r/reg_val to wr_list[11, :, :]
                # wr_list[11, 0, i] = wr_extractor('fp', op_dst1, op_dst2, op_src1, op_src2, op_id, data, val_prev)[0]
                # wr_list[11, 1, i] = wr_extractor('fp', op_dst1, op_dst2, op_src1, op_src2, op_id, data, val_prev)[1]
                # reg_val_table[11, i] = \
                #     wr_extractor('fp', op_dst1, op_dst2, op_src1, op_src2, op_id, data, reg_val_table[11, i - 1])[2]
                #
                # # Stack pointer, i.e, sp(r13), we place w/r/reg_val to wr_list[13, :, :]
                # wr_list[-3, 0, i] = wr_extractor('sp', op_dst1, op_dst2, op_src1, op_src2, op_id, data, val_prev)[0]
                # wr_list[-3, 1, i] = wr_extractor('sp', op_dst1, op_dst2, op_src1, op_src2, op_id, data, val_prev)[1]
                # reg_val_table[-3, i] = \
                #     wr_extractor('sp', op_dst1, op_dst2, op_src1, op_src2, op_id, data, reg_val_table[-3, i - 1])[2]
                #
                # # Link Register, i.e, lr(r14), we place w/r/reg_val to wr_list[14, :, :]
                # wr_list[-2, 0, i] = wr_extractor('lr', op_dst1, op_dst2, op_src1, op_src2, op_id, data, val_prev)[0]
                # wr_list[-2, 1, i] = wr_extractor('lr', op_dst1, op_dst2, op_src1, op_src2, op_id, data, val_prev)[1]
                # reg_val_table[-2, i] = \
                #     wr_extractor('lr', op_dst1, op_dst2, op_src1, op_src2, op_id, data, reg_val_table[-2, i - 1])[2]
                #
                # # Program Counter, i.e, pc(r15), we place w/r/reg_val to wr_list[15, :, :]
                # wr_list[-1, 0, i] = wr_extractor('pc', op_dst1, op_dst2, op_src1, op_src2, op_id, data, val_prev)[0]
                # wr_list[-1, 1, i] = wr_extractor('pc', op_dst1, op_dst2, op_src1, op_src2, op_id, data, val_prev)[1]
                # reg_val_table[-1, i] = \
                #     wr_extractor('pc', op_dst1, op_dst2, op_src1, op_src2, op_id, data, reg_val_table[-1, i - 1])[2]

        return wr_list, reg_val_table, tick_list, op_list

#
# if __name__ == "__main__":
#     T = InfoExtractor('csv_traces/prime.txt.csv', 0, 10, 12).get_tickop_list()[0]
#     H = InfoExtractor('csv_traces/prime.txt.csv', 0, 10, 12).get_wr_tick_list()[0][0, :, :]
#     V = InfoExtractor('csv_traces/prime.txt.csv', 0, 10, 12).get_wr_tick_list()[1][15]
#     print(H, '\n', np.vectorize(hex)(V))
