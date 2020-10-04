import csv
import re
import os

'''
    This handy script finds all non-repetitive opcodes and write them to a csv_file 
    The extracted opcodes are primarily used in design the m_calculator
'''


def trace_to_csv(trace_file):
    # Initialize Path variables to store converted csv file
    current_path = os.getcwd()
    csv_fname = str(current_path) + '/..' + "/csv_traces/" + 'non_repetitive' + trace_file + ".csv"

    op_seen = []

    with open(csv_fname, "w", newline="") as my_empty_csv:  # Process raw trace file
        writer = csv.writer(my_empty_csv)
        for i, line in enumerate(open(trace_file)):
            split_line = line.strip().split(":")
            current_tick = split_line[0]
            current_inst = split_line[3].strip()  # INST TO BE SPLIT
            split_instruction = re.split("   ", current_inst.strip())
            if split_instruction[0] not in op_seen:
                writer.writerow([current_inst])
                op_seen.append(split_instruction[0])
            else:
                op_seen = op_seen


if __name__ == "__main__":  # Test
    print(trace_to_csv('susan_corner.txt'))
