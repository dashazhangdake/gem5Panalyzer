import numpy as np
import csv
from itertools import islice
from Panalyzer.utils.wr_extractor import wr_extractor
from Panalyzer.TraceParser.logic_masking import *
from pathlib import Path
import pandas as pd
import time
from functools import partial

start_time = time.perf_counter()  # Time counter starts
chunksize = 1000
project_dir = Path(__file__).resolve().parent.parent
csv_dir = project_dir.joinpath('tempcsv')
fname = "fftbaseline.csv"

# Pandas method to read thru the csv
# chunk_counter = 0
# for chunk in pd.read_csv(csv_dir/fname, chunksize=chunksize):
#     print("current chunk: ", chunk_counter)
#     for index, row in chunk.iterrows():
#         pass
#     chunk_counter = chunk_counter + 1
#
elapsed_time_pandas = time.perf_counter() - start_time  # Stop point of the timer
fcsv = csv_dir/fname
# CSV method to go thru the csv file
# start = 0
# for i in range(0, 33000000, chunksize):
#     with open(fcsv, mode='r') as info_csv:
#         print("start from: ", start)
#         info_window = islice(info_csv, start, start + chunksize)
#         info_reader = csv.reader(info_window)
#         for idx, row in enumerate(info_reader):
#             pass
#     start = start + chunksize

elapsed_time_csv = time.perf_counter() - elapsed_time_pandas  # Stop point of the timer

# # CSV method but read the file for once
buffersize = 1000
with open(fcsv, mode='r') as info_csv:
    count = 0
    tick = []
    info_reader = csv.reader(info_csv)
    line = 0
    for idx, row in enumerate(info_reader):
        if idx % buffersize == 0:
            print(idx)
            count = 0
            tick = []
        else:
            count = count + 1
            tick.append(row[0])
        pass
        line = line + 1
    print(line)
elapsed_time_csv_once = time.perf_counter() - elapsed_time_csv  # Stop point of the timer

print('Read once pandas: Time has passed: ', elapsed_time_pandas, 'seconds')  # A timer counts elapsed time
print('Read many times csv: Time has passed: ', elapsed_time_csv, 'seconds')  # A timer counts elapsed time
print('Read once csv: Time has passed: ', elapsed_time_csv_once, 'seconds')  # A timer counts elapsed time
