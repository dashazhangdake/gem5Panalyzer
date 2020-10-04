import pandas as pd
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
import glob
import os
import time

# TF packages
import tensorflow as tf
from tensorflow.keras.layers import Input, Dense, LSTM, Dropout, BatchNormalization
from tensorflow.keras.models import Model
# os.environ["CUDA_VISIBLE_DEVICES"] = "-1"  # GPU enable/disable

from tensorflow.keras.optimizers import Adam
from tensorflow.keras.losses import Huber

# My functions
from DLpredictor.PVFpredictor_helper import *


def buildModel(batchSize, featureNum, n_values):
    X_input = Input(shape=(batchSize, featureNum))
    X = BatchNormalization()(X_input)

    X = LSTM(units=8, return_sequences=True)(X)
    X = LSTM(units=1, return_sequences=True)(X)

    output = Dense(n_values, activation='relu')(X)

    model = Model(inputs=X_input, outputs=output)

    return model


def train_predictor(totallength):
    # datafile = dataname + '_stats.csv'
    # datadir = Path.cwd().joinpath('datasets', datafile)
    # data = pd.read_csv(datadir)
    data = load_data()

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

    batchSize = 200
    num_batches = features.shape[0] / batchSize

    num_train = int(num_batches * 0.7)
    num_test = int(num_batches * 0.2)
    num_val = int(num_batches * 7/257)

    X_train = features[0: batchSize * num_train]
    y_train = target[0: batchSize * num_train]

    X_test = features[batchSize * num_train: batchSize * num_train + batchSize * num_test]
    y_test = target[batchSize * num_train: batchSize * num_train + batchSize * num_test]

    X_val = features[-batchSize * num_val:]
    y_val = target[-batchSize * num_val:]

    X_train = np.array(np.split(X_train, batchSize, axis=0))
    y_train = np.array(np.split(y_train, batchSize, axis=0))

    X_test = np.array(np.split(X_test, batchSize, axis=0))
    y_test = np.array(np.split(y_test, batchSize, axis=0))

    X_val = np.array(np.split(X_val, batchSize, axis=0))
    Y_val = np.array(np.split(y_val, batchSize, axis=0))

    dlModel = buildModel(batchSize, features.shape[1], 1)
    dlModel.compile(optimizer=Adam(lr=1e-4), loss='mse')
    dlModel.save('./')

    hist = dlModel.fit(X_train, y_train, epochs=5000, validation_data=(X_test, y_test))

    plt.plot(hist.history['loss'], 'red', label='loss')
    plt.plot(hist.history['val_loss'], 'blue', label='val_loss')
    plt.show()

    y_predict = dlModel.predict(X_val)
    plt.plot(y_val.ravel()[-2200:], 'red')
    plt.plot(y_predict.ravel()[-2200:], 'green')
    plt.show()

    return dlModel


starttime = time.perf_counter()
pvf_predictor = train_predictor(102800)
endtime = time.perf_counter() - starttime
print('training time', endtime)
# valdf = load_data(0, 'susan_sbaseline')
#
# # instnum = np.array(data['INSTNUM'])[0: totallength].reshape(-1, 1)
# testpair = define_dpairs(valdf, 7000)
# # print(testpair)
#
# testx = testpair['features'][200 * 7000:]
# testy = testpair['target'][200 * 7000:]
# testx = np.array(np.split(testx, 200, axis=0))
# testy = np.array(np.split(testy, 200, axis=0))
#
# vf_predict = pvf_predictor.predict(testx)
# vf_actual = testpair[testy]
#
# plt.plot(vf_predict.ravel(), 'red')
# plt.plot(vf_actual.ravel(), 'green')
# plt.show()
