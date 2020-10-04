import re
line = 'system.cpu.memDep0.insertedStores                1247                       # Number of stores inserted to the mem dependence unit.'
temp = re.findall('\d*\.?\d+', line)
print(temp[1])