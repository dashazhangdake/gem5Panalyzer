import re


'''
    Instruction Parser takes the instruction string in "split_line" as the input
    Next, this module will specify the Source/Destination Operands, RegValues, Offsets, etc
'''


class InstructionParser:
    def __init__(self, instruction):
        self.inst = re.split("   ", instruction.strip())
        self.op = self.inst[0]
        self.len_inst = len(self.inst)

    def arm32parser(self):
        res = {'d1': None, 'd2': None, 's1': None, 's2': None, 'offset': None, 'op': self.op}
        if self.len_inst > 1:
            current_operands = re.split(r',\s*(?![^[]*\])', self.inst[1])  # Split by commas outside of "[]"
            '''
                start from L = 2 
            '''
            if len(current_operands) == 2:
                # Scenarios that imm values , i. e. Offset in L/R ops can be a concern when len(Op)=2
                if "ldr" in self.op:  # load Insts with only two operands
                    if "[" in current_operands[1]:  # ldr r3, [r3, #13]！
                        res['d1'] = current_operands[0]
                        dst_address = re.split(" ", current_operands[1].strip("[]"))  # calculating address using reg
                        # value and offset
                        res['s1'] = dst_address[0].strip("[]").strip(",")
                        res['offset'] = re.sub("[^\d\.]", "", dst_address[1])  # Offsets are formatted in decimal
                    elif "#" in current_operands[1]:  # ldr fp, #0
                        res['d1'] = current_operands[0]
                        res['offset'] = current_operands[1].strip("#")
                elif "str" in self.op:  # store Insts with only two operands, both of ops are read
                    if "[" in current_operands[1]:  # str r3, [r3, #13]！
                        res['s1'] = current_operands[0]
                        dst_address = re.split(" ", current_operands[1].strip("[]"))  # calculating address using reg
                        res['s2'] = dst_address[0].strip("[]").strip(",")
                        res['offset'] = re.sub("[^\d\.]", "", dst_address[1])  # Offsets are formatted in decimal
                    elif "#" in current_operands[1]:  # ldr fp, #0
                        res['s1'] = current_operands[0]
                        res['s2'] = current_operands[1]
                        res['offset'] = current_operands[1].strip("#")
                # Other than L/S ops, imm values are just "decimal values"
                elif "mov" in self.op or "mv" in self.op:
                    res['d1'] = current_operands[0]
                    if "#" in current_operands[1]:
                        res['s1'] = current_operands[1].strip("#")
                    else:
                        res['s1'] = current_operands[1]
                elif "cm" in self.op or "tst" in self.op:
                    res['s1'] = current_operands[0]
                    if "#" in current_operands[1]:
                        res['s2'] = current_operands[1].strip("#")
                    else:
                        res['s2'] = current_operands[1]
                else:
                    res['d1'] = current_operands[0]
                    res['s1'] = current_operands[1]
            elif len(current_operands) == 3:
                # Offset of L/R is associated with the source operands, address = source_op + offset
                if "ldr" in self.op:  # load Insts with three operands
                    dst_address = re.split(" ", current_operands[2].strip("[]"))
                    res['d1'] = current_operands[0]
                    res['d2'] = current_operands[1]
                    res['s1'] = dst_address[0].strip("[]").strip(",")
                    res['offset'] = re.sub("[^\d\.]", "", dst_address[1])
                elif "str" in self.op:
                    dst_address = re.split(" ", current_operands[2].strip("[]"))
                    res['s1'] = current_operands[0]
                    res['s2'] = current_operands[1]
                    res['d1'] = dst_address[0].strip("[]").strip(",")
                    res['offset'] = re.sub("[^\d\.]", "", dst_address[1])
                elif 'add' in self.op or 'sub' in self.op or 'sb' in self.op or 'mul' in self.op \
                        or 'ml' in self.op:
                    res['d1'] = current_operands[0]
                    res['s1'] = current_operands[1]
                    res['s2'] = current_operands[2].strip("#")
                elif 'or' in self.op or 'and' in self.op or 'bic' in self.op or 'tst' in self.op:
                    res['d1'] = current_operands[0]
                    res['s1'] = current_operands[1]
                    res['s2'] = current_operands[2].strip("#")
                elif 'mov' in self.op:
                    res['d1'] = current_operands[0]
                    res['s1'] = current_operands[1]
                    res['s2'] = current_operands[2].strip("#")
                else:  # Other cases, can be refurbished in the future
                    res['d1'] = current_operands[0]
                    res['s1'] = current_operands[1]
                    res['s2'] = current_operands[2].strip("#")
            elif len(current_operands) == 4:
                if 'add' in self.op or 'sub' in self.op:
                    res['d1'] = current_operands[0]
                    res['s1'] = current_operands[1]
                    res['s2'] = current_operands[2]
                    res['offset'] = current_operands[3]
                else:
                    res['d1'] = current_operands[0]
                    res['d2'] = current_operands[1]
                    res['s1'] = current_operands[2]
                    res['s2'] = current_operands[3]
        return res

