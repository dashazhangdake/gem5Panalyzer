import csv
import numpy as np
import re
import os
from pathlib import Path
'''
    Read the raw trace file line by line, then partitioning each line of executed instruction into:
    TICK | CPU_ID | PC(program counter)_STATUS | Instruction | DST1 | DST2 | OP1 | OP2 | ACCESS TYPE | DATA | R[i]
    Results will be written into a csv file, hopefully it can save memory
'''


def trace_to_csv(trace_file_name, trace_dir):
    # Initialize Path variables to store converted csv file
    base_dir = Path(__file__).resolve().parent
    csv_dir = base_dir.joinpath('csv_traces')
    trace_file_path = trace_dir / (trace_file_name + '.txt')
    csv_fname = csv_dir / (trace_file_name + ".csv")

    # Processing raw txt trace file
    with open(csv_fname, "w", newline="") as my_empty_csv:
        writer = csv.writer(my_empty_csv)
        '''
        #                            Columns of rearrange trace file are defined as: 
        #     ['Tick', 'CPU_ID', 'PC', 'INST', 'DST1', 'DST2', 'SRC1', 'SRC2', 'OFFSET', 'TYPE', 'DATA', #'ADDR'#]
        '''
        for i, line in enumerate(open(trace_file_path)):
            '''
                Ref: read specific lines but avoid reading the entire file, i.e, scripting in a line-by-line manner
                with open(trace_input_file) as fp:  # Print line38 to line33
                for i, line in enumerate(fp):
                    if 33 <= i <= 38:
                        print(line)
                    elif i > 55:
                        break
            '''
            split_line = line.strip().split(":")  # extract easy-to-get information
            current_tick = split_line[0]  # Tick
            current_cpu = split_line[1]  # CPU ID
            current_pc = split_line[2]  # PC VALUE
            current_inst = split_line[3].strip()  # INST TO BE SPLIT
            current_access_type = split_line[-2]  # Access type

            split_instruction = re.split("   ", current_inst.strip())
            operation = split_instruction[0]
            if len(split_instruction) > 1:
                current_operands = re.split(r',\s*(?![^[]*\])', split_instruction[1])  # Split by commas outside of "[]"
                '''
                    start from L = 2 
                '''
                if len(current_operands) == 2:
                    # Scenarios that imm values , i. e. Offset in L/R ops can be a concern when len(Op)=2
                    if "ldr" in operation:  # load Insts with only two operands
                        if "[" in current_operands[1]:  # ldr r3, [r3, #13]！
                            current_d1 = current_operands[0]
                            current_d2 = None
                            dst_address = re.split(" ", current_operands[1].strip("[]"))  # calculating address using reg
                            # value and offset
                            current_s1 = dst_address[0].strip("[]").strip(",")
                            current_s2 = None
                            current_offset = re.sub("[^\d\.]", "", dst_address[1])  # Offsets are formatted in decimal
                        elif "#" in current_operands[1]:  # ldr fp, #0
                            current_d1 = current_operands[0]
                            current_d2 = None
                            current_s1 = None
                            current_s2 = None
                            current_offset = current_operands[1].strip("#")
                    elif "str" in operation:  # store Insts with only two operands, both of ops are read
                        if "[" in current_operands[1]:  # str r3, [r3, #13]！
                            current_s1 = current_operands[0]
                            dst_address = re.split(" ", current_operands[1].strip("[]"))  # calculating address using reg
                            current_s2 = dst_address[0].strip("[]").strip(",")
                            current_d1 = None
                            current_d2 = None
                            current_offset = re.sub("[^\d\.]", "", dst_address[1])  # Offsets are formatted in decimal
                        elif "#" in current_operands[1]:  # ldr fp, #0
                            current_s1 = current_operands[0]
                            current_s2 = current_operands[1]
                            current_d1 = None
                            current_d2 = None
                            current_offset = current_operands[1].strip("#")
                    # Other than L/S ops, imm values are just "decimal values"
                    elif "mov" in operation or "mv" in operation:
                        current_d1 = current_operands[0]
                        current_d2 = None
                        current_s2 = None
                        if "#" in current_operands[1]:
                            current_s1 = current_operands[1].strip("#")
                        else:
                            current_s1 = current_operands[1]
                        current_offset = None
                    elif "cm" in operation or "tst" in operation:
                        current_d1 = None
                        current_d2 = None
                        current_s1 = current_operands[0]
                        if "#" in current_operands[1]:
                            current_s2 = current_operands[1].strip("#")
                        else:
                            current_s2 = current_operands[1]
                        current_offset = None
                    # Don't matter scenarios when len(ops) = 2
                    elif "pld" in operation:  # Pld always writes R34. PLD itself lookups in the cache, and start a
                        # refill if they missed. Pld retires immediately retires.
                        current_d1 = None
                        current_d2 = None
                        current_s1 = None
                        current_s2 = None
                        current_offset = None
                    else:
                        current_d1 = current_operands[0]
                        current_d2 = None
                        current_s1 = current_operands[1]
                        current_s2 = None
                        current_offset = None
                elif len(current_operands) == 3:
                    # Offset of L/R is associated with the source operands, address = source_op + offset
                    if "ldr" in operation:  # load Insts with three operands
                        dst_address = re.split(" ", current_operands[2].strip("[]"))
                        current_d1 = current_operands[0]
                        current_d2 = current_operands[1]
                        current_s1 = dst_address[0].strip("[]").strip(",")
                        current_s2 = None
                        current_offset = re.sub("[^\d\.]", "", dst_address[1])
                    elif "str" in operation:
                        dst_address = re.split(" ", current_operands[2].strip("[]"))
                        current_s1 = current_operands[0]
                        current_s2 = current_operands[1]
                        current_d1 = dst_address[0].strip("[]").strip(",")
                        current_d2 = None
                        current_offset = re.sub("[^\d\.]", "", dst_address[1])
                    elif 'add' in operation or 'sub' in operation or 'sb' in operation or 'mul' in operation \
                            or 'ml' in operation:
                        current_d1 = current_operands[0]
                        current_d2 = None
                        current_s1 = current_operands[1]
                        current_s2 = current_operands[2].strip("#")
                        current_offset = None
                    elif 'or' in operation or 'and' in operation or 'bic' in operation or 'tst' in operation:
                        current_d1 = current_operands[0]
                        current_d2 = None
                        current_s1 = current_operands[1]
                        current_s2 = current_operands[2].strip("#")
                        current_offset = None
                    elif 'mov' in operation:
                        current_d1 = current_operands[0]
                        current_s1 = current_operands[1]
                        current_s2 = current_operands[2].strip("#")
                        current_d2 = None
                        current_offset = None
                    else:  # Other cases, can be refurbished in the future
                        current_d1 = current_operands[0]
                        current_d2 = None
                        current_s1 = current_operands[1]
                        current_s2 = current_operands[2].strip("#")
                        current_offset = None
                elif len(current_operands) == 4:
                    if 'add' in operation or 'sub' in operation:
                        current_d1 = current_operands[0]
                        current_d2 = None
                        current_s1 = current_operands[1]
                        current_s2 = current_operands[2]
                        current_offset = current_operands[3]
                    else:
                        current_d1 = current_operands[0]
                        current_d2 = current_operands[1]
                        current_s1 = current_operands[2]
                        current_s2 = current_operands[3]
                        current_offset = None
            else:
                current_d1 = None
                current_d2 = None
                current_s1 = None
                current_s2 = None
                current_offset = None
                current_access_type = "operations without operands"
            if "b" == operation or 'bl' == operation:
                current_d1 = None
                current_d2 = None
                current_s1 = None
                current_s2 = None
                current_offset = None
            if "D=" in split_line[-1]:
                current_data_full = int(split_line[-1].split("=", 1)[1], 16)
                current_data = current_data_full & 0xFFFFFFFF  # Only keep lower 32bit of collected register data
            else:
                current_data = 0
            current_addr = None  # We don't consider address for now

            writer.writerow([current_tick, current_cpu, current_pc, operation, current_d1, current_d2,
                            current_s1, current_s2, current_offset, current_access_type, current_data])

    return i


if __name__ == "__main__":  # Test
    print(trace_to_csv("prime"))
