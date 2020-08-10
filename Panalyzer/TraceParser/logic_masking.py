import numpy as np
import re
from Panalyzer.utils.BinaryMethods import BinaryMethods


class arm32masking_calculator:
    def __init__(self, length, ops, src1, src2, reg_num, reg_val_table):
        self.lnum = length
        self.op = ops
        self.num_reg = reg_num
        self.src1_list = src1
        self.src2_list = src2
        self.reg_val_matrix = reg_val_table

    def lmasking_calculator(self):
        masking_table = np.full([self.num_reg, self.lnum], 0, dtype=float)
        for i in range(self.lnum):
            regvals_i = regval_fetcher(i, self.src1_list, self.src2_list, self.reg_val_matrix)
            src1_i = regvals_i['src1']
            src2_i = regvals_i['src2']
            src1_val_i = regvals_i['val1']
            src2_val_i = regvals_i['val2']
            op_i = self.op[i]
            for j in range(self.num_reg):
                regid = 'r' + str(j)
                m_ij = arm32logic_masking(op_i, regid, src1_i, src2_i, src1_val_i, src2_val_i)
                masking_table[j, i] = m_ij
        return masking_table


def regval_fetcher(index, src1_list, src2_list, reg_val_table, num_reg=16):
    src1 = src1_list[index]
    src2 = src2_list[index]
    reg_values = {'src1': None, 'val1': None, 'src2': None, 'val2': None}

    #  # Retrive source operands and operands vals
    reg_list = ['r' + str(k) for k in range(num_reg)]
    if src1 in reg_list:
        regid = int(src1.replace('r', ''))
        reg_values['val1'] = reg_val_table[regid, index]
    elif src1.isdigit():  # When src1 is imm val, val1 = src1
        src1 = int(src1)
        reg_values['val1'] = src1
    else:  # when src[i] is none, assume half of the word are set bits
        reg_values['val1'] = 0xFFFF

    #  # Repeat what we did to src1
    if src2 in reg_list:
        regid = int(src2.replace('r', ''))
        reg_values['val2'] = reg_val_table[regid, index]
    elif src2.isdigit():  # When src1 is imm val, val1 = src1
        src2 = int(src2)
        reg_values['val2'] = src2
    else:  # when src[i] is none, assume half of the word are set bits
        reg_values['val2'] = 0xFFFF

    reg_values['src1'] = src1
    reg_values['src2'] = src2

    return reg_values


def arm32logic_masking(current_op, reg_id, src1, src2, val_src1, val_src2, reg_bw=32):
    if 'and' in current_op and reg_id == src1:  # AND OP
        m = 1 - BinaryMethods(val_src2).setbits_counter() / reg_bw
    elif 'and' in current_op and reg_id == src2:
        m = 1 - BinaryMethods(val_src1).setbits_counter() / reg_bw

    elif 'bic' in current_op and reg_id == src1:
        m = BinaryMethods(val_src2).setbits_counter() / reg_bw
    elif 'bic' in current_op and reg_id == src2:
        m = 1 - BinaryMethods(val_src1).setbits_counter() / reg_bw

    elif 'clz' in current_op and reg_id == src1:
        m = 1 - BinaryMethods(val_src2).setbits_counter() / reg_bw

    elif 'cmp' in current_op and reg_id == src1 and src2 == 0:
        m = 1 - 1 / reg_bw

    elif 'movt' in current_op and reg_id == src1:
        m = 1 / 2

    elif 'orr' in current_op and reg_id == src1:  # OR OP
        m = BinaryMethods(val_src2).setbits_counter() / reg_bw
    elif 'orr' in current_op and reg_id == src2:
        m = BinaryMethods(val_src1).setbits_counter() / reg_bw

    elif 'orn' in current_op and reg_id == src1:  # OR OP
        m = 1 - BinaryMethods(val_src2).setbits_counter() / reg_bw
    elif 'orn' in current_op and reg_id == src2:
        m = BinaryMethods(val_src1).setbits_counter() / reg_bw

    elif 'cmp' in current_op and reg_id == src1 and src2 == 0:
        if val_src1 == 0:
            m = 0
        else:
            m = 1 - 1 / reg_bw

    elif 'sel' in current_op and reg_id == src1:
        m = 1 / 2
    elif 'sel' in current_op and reg_id == src2:
        m = 1 / 2

    elif 'strb' in current_op and reg_id == src1:
        m = 1 / 2

    elif 'sxth' in current_op and reg_id == src1:
        m = 1 / 4
    elif 'sxth' in current_op and reg_id == src2:
        m = 1 / 4

    elif 'bfx' in current_op and reg_id == src1:
        m = 1 / 4
    elif 'bfx' in current_op and reg_id == src2:
        m = 1 / 4  # Actually, m = width / bw

    elif 'stx' in current_op and reg_id == src1:
        m = 1 / 2
    elif 'stx' in current_op and reg_id == src2:
        m = 1 / 2

    elif 'teq' in current_op and reg_id == src1:
        if val_src1 != val_src2:
            m = 1
        else:
            m = 0
    elif 'teq' in current_op and reg_id == src2:
        if val_src1 != val_src2:
            m = 1
        else:
            m = 0

    elif 'tst' in current_op and reg_id == src1:
        m = 1 - BinaryMethods(val_src2).setbits_counter() / reg_bw
    elif 'tst' in current_op and reg_id == src2:
        m = 1 - BinaryMethods(val_src1).setbits_counter() / reg_bw

    elif 'uadd8' in current_op and reg_id == src1:
        m = 1 / 4
    elif 'uadd8' in current_op and reg_id == src2:
        m = 1 / 4

    elif 'add8' in current_op and reg_id == src1:
        m = 1 / 4
    elif 'sub8' in current_op and reg_id == src2:
        m = 1 / 4

    else:
        m = 0
    return m


if __name__ == "__main__":
    ops = ['mov.w', 'mov.w', 'mov', 'ldr.w', 'ldr', 'ldr', 'bl.w', 'mov.w', 'and', 'movt.w']
    src1h = ['0', '0', 'r1', 'r1', 'r1', 'r1', '', '0', 'r1', 'r0']
    src2h = ['', '', '', '', '', '', '', '', 'r0', '0']
    regtable = np.array([[0, 0, 0, 0, 66437, 66437, 66437, 66437, 66437, 66437],
                         [0, 0, 0, 0, 15, 6637, 37, 66, 664, 7]])
    res = regval_fetcher(8, src1h, src2h, regtable)
    m_table = arm32masking_calculator(10, ops, src1h, src2h, 2,
                                      regtable).lmasking_calculator()
    print(m_table)
    print(res['val1'], res['val2'])