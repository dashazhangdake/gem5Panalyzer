import os
import pandas as pd
import glob
import random
import numpy as np


def shuffle_list(some_list):
    randomized_list = some_list[:]
    while True:
        random.shuffle(randomized_list)
        for a, b in zip(some_list, randomized_list):
            if a == b:
                break
        else:
            return randomized_list


def load_data(mode=1, file=''):  # by default, load all files in the dataset
    path = os.getcwd()  # use your path
    if mode == 1:
        all_files = glob.glob(path + "/datasets/*.csv")
        shuffle_num = 1
        li = []
        for i in range(shuffle_num):
            all_files_shuffled = shuffle_list(all_files)
            for filename in all_files_shuffled:
                df = pd.read_csv(filename, index_col=None, header=0)
                df.drop_duplicates(subset=['PVF'], keep='last', inplace=True)
                li.append(df)
        # val_file = path + '/validation_datasets/shabaseline_stats.csv'
        # val_df = pd.read_csv(val_file, index_col=None, header=0)
        # val_df.drop_duplicates(subset=['PVF'], keep='last', inplace=True)
        # li.append(val_df)
    else:
        all_files = [path + '/validation_datasets/' + file + '_stats.csv']
        li = []
        for filename in all_files:
            df = pd.read_csv(filename, index_col=None, header=0)
            # df.drop_duplicates(subset=['PVF'], keep='last', inplace=True)
            li.append(df)

    frame = pd.concat(li, axis=0, ignore_index=True)
    frame.to_csv('PVF.csv')
    print(frame.shape)
    return frame


def define_dpairs(data, totallength):
    dpair = {'features': None, 'target': None}
    # instnum = np.array(data['INSTNUM'])[0: totallength].reshape(-1, 1)
    ipc = np.array(data['IPC'])[0: totallength].reshape(-1, 1)
    cycle = np.array(data['CYCLE'])[0: totallength].reshape(-1, 1)
    regr = np.array(data['REGR'])[0: totallength].reshape(-1, 1)
    regw = np.array(data['REGW'])[0: totallength].reshape(-1, 1)
    robr = np.array(data['ROBR'])[0: totallength].reshape(-1, 1)
    robw = np.array(data['ROBW'])[0: totallength].reshape(-1, 1)
    memr = np.array(data['MEMR'])[0: totallength].reshape(-1, 1)
    memw = np.array(data['MEMW'])[0: totallength].reshape(-1, 1)
    loaddep = np.array(data['LOADDEP'])[0: totallength].reshape(-1, 1)
    storedep = np.array(data['STOREDEP'])[0: totallength].reshape(-1, 1)
    branches = np.array(data['BRANCH'])[0: totallength].reshape(-1, 1)

    pvf = np.array(data['PVF'])[0: totallength].reshape(-1, 1)

    features = np.concatenate((ipc, cycle, regr, regw, robr, robw, memr, memw, loaddep, storedep, branches), axis=1)
    target = pvf
    dpair['features'] = features
    dpair['target'] = target

    return dpair


print(load_data(0, 'gsmbaseline'))

