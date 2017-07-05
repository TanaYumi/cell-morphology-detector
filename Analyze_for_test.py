# -*- coding: utf-8 -*-
"""
Created on Wed Dec 14 17:31:00 2016

@author: tanakayumiko
"""

import numpy as np
import pandas as pd
import os
import newFiles


def Analyze(scan, protein, nd2_file, Roi_Data_file, status_file, time_file, n):
    """
    pic = ND2_Reader(nd2_file + '%03d'%scan + '.nd2')#'/Volumes/tanaka/20160418_IL33andIL2/NDSequence%03d.nd2'%time)
    pic.iter_axes = 'm'
    pic.default_coords['c'] = protein

    newdata = []
    newtime = []
    for i in pic:
        roi_1 = np.mean(i[0:512,0:511])
        roi_2 = np.mean(i[0:512,512:1022])
        roi_3 = np.mean(i[513:2024,0:511])
        roi_4 = np.mean(i[513:2024,512:2022])
        
        df = roi_1,roi_2,roi_3,roi_4
        newdata.extend(df)
        newtime.append(i.metadata['t_ms'])
        """
    if not os.path.exists(Roi_Data_file):
        data, status, time = newFiles.newFiles(newdata, pic, Roi_Data_file, status_file, time_file, n)
    else:
        data = pd.read_csv(Roi_Data_file)
        data = data.iloc[:,:scan+2]
        #data['%d'%scan] = newdata
        #data.to_csv(Roi_Data_file, index = False) 
    
        time = pd.read_csv(time_file)
        #row, col = time.shape
        #time['%d'%scan] =  np.array(newtime) + max(time['%d'%(scan-1)])
        #time.to_csv(time_file, index = False)

    return data, time, #pic
    
"""
test = Analyze(1)
for i in range(2,6):
    test = pd.concat([test, Analyze(i)], axis = 1)
    """
