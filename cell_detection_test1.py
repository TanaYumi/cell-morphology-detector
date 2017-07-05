# -*- coding: utf-8 -*-
"""
Created on Thu Jun 29 14:29:39 2017

@author: keisuke tsukada
"""
"""
nd2_celldetector
NIS-elements nd2 file converter
.nd2 file is converted to uint8 array for image processing on openCV

test1
canny>closing>areafilter>closing>plot
"""

import cv2, matplotlib
import numpy as np
import matplotlib.pyplot as plt
from nd2reader import ND2Reader
from scipy import ndimage
　
#readfile = "C:\WinPython-64bit-3.6.1.0Qt5\modules\Captured DIA_exome_3.nd2"
readfile = "D:\iPS\XY238.nd2"

IO = ND2Reader(readfile)   #image object
#temp = IO[0]   #temp unit64 2dim Frame 
temp = IO.get_frame_2D(0,451,0) #for multi-channel/time/XYposition
"""
get_frame_2D(c=0,t=0,z=0,x=0,y=0)
c:channel/t:time/z:XYposition/x,y:index designation(1dim extraction)
"""
pixel_x = len(temp)
pixel_y = len(temp[0])
temp_1dim = temp.reshape(-1,)  #for max, min, calculation
#mean = np.mean(temp_1dim)

"""
0-99% normalization 
"""
sortedarray = np.sort(temp_1dim)
length = len(sortedarray)
upper = int(round(length*0.99))
M = sortedarray[upper]
m = sortedarray[0]
"""
min-max normalization
"""
#M = temp_1dim.max()
#m = temp_1dim.min()

width = M-m     #for normalizetion into 0-255
temp_1dim = temp_1dim - m
norm = 255/width
temp_float_1dim = temp_1dim*norm
temp_uint8_1dim = temp_float_1dim.astype(np.uint8)
IO_uint8 = temp_uint8_1dim.reshape(pixel_x,pixel_y)
#plt.imshow(IO_uint8,"gray")

IO_gauss = cv2.GaussianBlur(IO_uint8, (9,9), 0)


ks1 = 10
#ks2 = 30
#kernel1 = np.ones((ks1,ks1),np.uint8) #rectangle kernel
#kernel1 = cv2.getStructuringElement(cv2.MORPH_CROSS,(ks1,ks1)) #cross kernel
kernel1 = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(ks1,ks1)) #ellipse kernel

#plt.imshow(IO_uint8,"gray")
#cv2.GaussianBlur(IO_uint8, (5, 5), 5) #noize elimination
#plt.imshow(IO_uint8,"gray")
#IO_canny = cv2.Canny(IO_uint8, 200, 10)
IO_canny = cv2.Canny(IO_gauss, 200, 10)

"""
#Canny(IO,first threshold,second threshold)
#first/second threshold corresponding to up/down differential width
"""
#plt.imshow(IO_canny,"gray")
IO_closing = cv2.morphologyEx(IO_canny, cv2.MORPH_CLOSE, kernel1) #filling holes
#plt.imshow(IO_closing,"gray")
label_im, nb_labels = ndimage.label(IO_closing) #objects labeling(1,2,3...)
areasizes = np.array(ndimage.sum(IO_closing,label_im,range(1,nb_labels + 1)))
##each area size/descending order. float64 does't need?
reject_small = areasizes >= 500000
reject_small = np.r_[np.array([False]),reject_small]
IO_sizefiltered = reject_small[label_im] #type bool
IO_sizefiltered = IO_sizefiltered.astype(np.uint8) #convert to uint8
IO_sizefiltered = IO_sizefiltered*255 #binary in uint8
plt.imshow(IO_sizefiltered,"gray")

#kernel2 = np.ones((ks2,ks2),np.uint8) #rectangle kernel
#kernel2 = cv2.getStructuringElement(cv2.MORPH_CROSS,(ks2,ks2)) #cross kernel
#kernel2 = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(ks2,ks2)) #ellipse kernel

IO_cluster = cv2.morphologyEx(IO_sizefiltered, cv2.MORPH_CLOSE, kernel2)
#plt.imshow(IO_cluster,"gray")





