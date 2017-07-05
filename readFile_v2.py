# -*- coding: utf-8 -*-
"""
Created on Sat Oct  1 14:26:52 2016

@author: tanakayumiko
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit


def readFile(Roi_Data_file, status_file, time_file, rawdata, rawtime):
    status = pd.read_csv(status_file)
    rawdata = pd.pivot_table(rawdata, index = ['Address', 'ROI'])
    names = []
    for i in range(1,len(rawdata.columns)+1):
        names.append('%d'%i)
    rawdata = rawdata.reindex(columns = names)
    rawdata = rawdata.sub(rawdata['1'], axis = 0)
    data = rawdata.copy()

    for i in range(1,len(data)/4):
        back = int(status[status['Address']==i][status['Status']==2].ROI.values)
        for j in range(1,5):
            data.ix[i,j] = rawdata.ix[i,j] - rawdata.ix[i,back]
            
    time = pd.pivot_table(rawtime, index = ['Address'])
    status = pd.pivot_table(status, index = ['Address', 'ROI'])

    return data, status, time
    

def sigmoid(x, a, b, c):
    y = b / (1. + np.exp( -a * (x - c)))
    return y
    
def fitting(scan, data, delta_t, cov):
    suggestion = []
    for i in range(1+data.shape[0]/4):
        for j in range(1,5):
            try:
                p, c = curve_fit(sigmoid, range(10), data.ix[i,j].values[scan-10:scan], maxfev=3000)
                c = np.diag(c)
                if c[1]+c[2]<2:
                    suggestion.append([i,j])
            except:
                pass
    return suggestion

def suggest(scan, data, timelag, difference, threthold):
    suggestion = []
    c = len(data.columns)
    if c-1 > timelag:
        diff = data['%d'%c]-data['%d'%(c-timelag)]

        for i in range(len(diff[diff>difference].index.labels[0])):
            suggestion.append([diff[diff>difference].index.labels[0][i]+1, \
            diff[diff>difference].index.labels[1][i]+1])
        for i in range(len(data[data['%d'%c]>threthold].index.labels[1])):
            suggestion.append([data[data['%d'%c]>threthold].index.labels[0][i]+1, \
            data[data['%d'%c]>threthold].index.labels[1][i]+1])
    return suggestion