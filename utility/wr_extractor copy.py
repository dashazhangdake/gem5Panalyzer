from utility.setbit_counter import BinaryMethods
import numpy as np


'''
    This script contains the following functions:
    1. Functionalized wr_extractor using in InfoExtractor and m_calculator basic blocks 
    2. Renaming/aliasing special purpose registers: fp(r11), sp(r13), lr(r14), pc(r15)
    3. m_calculator basic block: Binary calculations for the m of tens of typical logic operations. Note that operands 
    can be either "r#" or immediate values "#n". If src operand is r#: find the corresponding data stored in r(n) from 
    reg_val_table using index number. Otherwise(another operand is a decimal number), simply say val_src=src itself
'''


# Assign W/R status to W/R matrix
def wr_extractor(reg_id, dst1, dst2, src1, src2, op, data, val_prev):
    # InfoExtractor already assigned operands on the correct field based on the type of operation
    if (reg_id == src1) and 'str' in op:  # For read operation: D is the data stored in src1. However, we already
        # recorded D before store operation, it is unnecessary to assign D to reg_val
        r_entry = 1
    elif reg_id == src1 or reg_id == src2:
        r_entry = 1
    else:
        r_entry = 0

    if reg_id == dst1 or reg_id == dst2:  # If R[k] at line[i] is the dst operand: w=1 and reg_val=D
        w_entry = 1
        reg_val = data
    else:
        w_entry = 0  # Otherwise, w[k][i]=0, reg_val[k][i] = reg_val[k][i-1]
        reg_val = val_prev
    return w_entry, r_entry, reg_val


# # ------------------DISABLED BLOCK AS WE RENAMED SP REGISTERS IN PREPROCESSED MODULE--------------- ##
# def rename_spreg(reg_id, src1, src2, name, newname):
#     if reg_id == name:
#         reg_id = newname
#     else:
#         reg_id = reg_id
#     if src1 == name:
#         src1 = newname
#     else:
#         src1 = src1
#     if src2 == name:
#         src2 = newname
#     else:
#         src2 = src2
#     return reg_id, src1, src2


def m_calculator(line, current_op, reg_id, src1, src2, reg_val_table, reg_bw=32, num_reg=16):
    # # ------------------DISABLED BLOCK AS WE RENAMED SP REGISTERS IN PREPROCESSED MODULE--------------- ##
    # global current_val_src1, current_val_src2
    # reg_id = rename_spreg(reg_id, src1, src2, 'fp', 'r11')[0]
    # src1 = rename_spreg(reg_id, src1, src2, 'fp', 'r11')[1]
    # src2 = rename_spreg(reg_id, src1, src2, 'fp', 'r11')[2]
    # reg_id = rename_spreg(reg_id, src1, src2, 'sp', 'r13')[0]
    # src1 = rename_spreg(reg_id, src1, src2, 'sp', 'r13')[1]
    # src2 = rename_spreg(reg_id, src1, src2, 'sp', 'r13')[2]
    # reg_id = rename_spreg(reg_id, src1, src2, 'lr', 'r14')[0]
    # src1 = rename_spreg(reg_id, src1, src2, 'lr', 'r14')[1]
    # src2 = rename_spreg(reg_id, src1, src2, 'lr', 'r14')[2]
    # reg_id = rename_spreg(reg_id, src1, src2, 'pc', 'r15')[0]
    # src1 = rename_spreg(reg_id, src1, src2, 'pc', 'r15')[1]
    # src2 = rename_spreg(reg_id, src1, src2, 'pc', 'r15')[2]

    """
        AND m factor: m(op1/2): m = 1 - number_setbits(op2/1)/BW
        OR m factor: m(op1/2): m = number_setbits(op2/1)/BW
        ORN m factor: m(op1) = 1 - number_setbits(op2)/BW; m(op2) = number_setbits(op1)/BW
        CMP: the bits before MSB are "dominant":
    """
    # if 'r' in src1 and len(src1) <= 3:
    #     label_src1 = int(''.join(x for x in src1 if x.isdigit()))
    # else:
    #     label_src1 = None
    # val_src1 = reg_val_table[label_src1, line - 1] if type(src1) is str else src1
    # if 'r' in src2 and len(src2) <= 3:
    #     label_src2 = int(''.join(x for x in src2 if x.isdigit()))
    # else:
    #     label_src2 = None
    # val_src2 = reg_val_table[label_src2, line - 1] if type(src2) is str else src2
    r_list = ['r' + str(k) for k in range(num_reg)]
    if src1 in r_list:
        index_src1 = int(''.join(x for x in src1 if x.isdigit()))
        val_src1 = reg_val_table[index_src1, line - 1]
    elif type(src1) is int:
        val_src1 = src1
    else:
        val_src1 = 0xFFFF
    if src2 in r_list:
        index_src2 = int(''.join(x for x in src2 if x.isdigit()))
        val_src2 = reg_val_table[index_src2, line - 1]
    elif type(src2) is int:
        val_src2 = src2
    else:
        val_src2 = 0xFFFF

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
    src2_t = '100'
    reg_val_t = 111
    current_val_src2_t = reg_val_t if type(src2_t) is str else src2_t
    print(current_val_src2_t)
