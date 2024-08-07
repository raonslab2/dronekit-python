# -*- coding: utf-8 -*-
#!/usr/bin/env python3

import cv2
import numpy as np
import matplotlib.pylab as plt

imgs = []
imgs.append(cv2.imread('D://girPj//test1002//DJI_0001.JPG'))
imgs.append(cv2.imread('D://girPj//test1002//DJI_0002.JPG'))

hists = []

for img in imgs:
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    hist = cv2.calcHist([hsv], [0, 1], None, [180, 256], [0, 180, 0, 256])
    cv2.normalize(hist, hist, 0, 1, cv2.NORM_MINMAX) 
    hists.append(hist)

method = '원하는 비교 알고리즘'
query = hists[0]
ret = cv2.compareHist(query, hists[1], method)

if method == cv2.HISTCMP_INTERSECT:
    ret = ret/np.sum(query)   

if ret == 1:
    print('Same Image')
else:
    print('Different Image')