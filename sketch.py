line = "204909: system.cpu: 0x107c2    :   sub   sp, lr, #296       : IntAlu :  D=0x00000000befffd88"

h = line.replace('fp', 'r11').replace('sp', 'r13').replace('lr', 'r14').replace('pc', 'r15')  # Rename registers
print(h)