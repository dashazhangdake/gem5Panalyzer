"""
    This script contains the following functions:
    1. Functionalized wr_extractor using in InfoExtractor and m_calculator basic blocks 
    2. Renaming/aliasing special purpose registers: fp(r11), sp(r13), lr(r14), pc(r15)
    3. m_calculator basic block: Binary calculations for the m of tens of typical logic operations. Note that operands 
    can be either "r#" or immediate values "#n". If src operand is r#: find the corresponding data stored in r(n) from 
    reg_val_table using index number. Otherwise(another operand is a decimal number), simply say val_src=src itself
"""


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


if __name__ == "__main__":
    src2_t = '100'
    reg_val_t = 111
    current_val_src2_t = reg_val_t if type(src2_t) is str else src2_t
    print(current_val_src2_t)
