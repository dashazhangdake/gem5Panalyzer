import numpy as np


class BinaryMethods:
    def __init__(self, in_number):
        self.number_in = in_number

    """
        An efficient? algorithm to calculate the number of set bits
        borrowed from:
        https://stackoverflow.com/questions/109023/how-to-count-the-number-of-set-bits-in-a-32-bit-integer#109025
    """
    def setbits_counter(self):  # Count the number of '1' s in the input number
        i = np.int64(self.number_in)
        i = i - ((i >> 1) & 0x55555555)
        i = (i & 0x33333333) + ((i >> 2) & 0x33333333)
        return (((i + (i >> 4) & 0xF0F0F0F) * 0x1010101) & 0xffffffff) >> 24

    '''
        Sometimes we need to find the location of MSB setbit, e.g. the CLZ instruction (counting leading zeros)
    '''
    # Find the index of the leading one in an integer
    def setbit_msb(self):
        return self.number_in.bit_length()

    # Find the index of the ending one in an integer
    def setbit_lsb(self):
        return self.number_in.bit_length()


if __name__ == "__main__":
    print(BinaryMethods(0xFFF).setbits_counter())
    print(BinaryMethods(8).setbit_msb())
