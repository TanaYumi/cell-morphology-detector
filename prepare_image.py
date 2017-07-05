# -*- coding: utf-8 -*-
"""
Created on Fri Jan 27 11:14:15 2017

@author: tanakayumiko

wnd-charmを使用し、細胞の入っているウェルと入っていないウェルを見分ける分離器を作成する
そのためのデータを用意するモジュール

＊nd2ファイルをND2_Readerで読み込む
＊カウントファイルを読み込む

**************************************************************
for multipoint
＊nd2ファイルのピクセルデータを4分割(コの字)する
＊PILでimageオブジェクトを作成し、nd2ファイルの輝度データを貼り付ける

＊カウントファイルを参考に別々のフォルダにTIFFで保存する
  'others':stateが2
  'empty':Cellnumが0
  'single':Cellnumが1
  'multi':その他
**************************************************************
"""

from PIL import Image
from pims import ND2_Reader
#import nd2reader
import pandas as pd
import numpy as np

readfile = '/media/tanaka/Tanaka_rawdata/20161015-mNHdose/20161015_Quad2_mNH_IL2-33dose.nd2'
countfile = '/media/tanaka/Tanaka_rawdata/20161015-mNHdose/20161015_Quad2_mNH_IL2-33dose-count.csv'

nd2 = ND2_Reader(readfile)
nd2.iter_axes = 'm'
nd2.bundle_axes = ['t','y','x']
nd2.default_coords['c'] = 0

count = pd.read_csv(countfile, dtype = {'state':np.int32})
count_p = pd.pivot_table(count, index = ['time','XYID', 'ROIID'])

#%%
cls = ['empty', 'single', 'multi', 'others']
#以降 timeのfor loop(i)に収める
i = 0
#以降 multipoint(j)のfor loopに収める
for j in range(996):
    Cellnum = count_p.loc[i,j]['Cellnum'].values
    state = count_p.loc[i,j]['state'].values
    print 'm%d :well0: %d, well1: %d, well2: %d, well3: %d'%(j,Cellnum[0],Cellnum[1],Cellnum[2],Cellnum[3])
    savefile = '/home/tanaka/wndchrm/wndchrm-1.52.775/data/%s/image_%d_%d.tif'
    
    point = nd2[j][i]
    well = [
        point[:511,:512],
        point[:511:,512:],
        point[511:,512:],
        point[511:,:512],
    ]

    for k in range(4):
        image = Image.new('I', (512,511))
        image.putdata(well[k].reshape(1,512*511)[0])
        if state[k] == 2:
            image.save(savefile%(cls[3], j, k))
        elif Cellnum[k] == 0:
            image.save(savefile%(cls[0], j, k))
        elif Cellnum[k] == 1:
            image.save(savefile%(cls[1], j, k))
        else:
            image.save(savefile%(cls[2], j, k))

