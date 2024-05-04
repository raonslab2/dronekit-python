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
 
query = hists[0]

 
methods = ['CORREL', 'CHISQR', 'INTERSECT', 'BHATTACHARYYA', 'EMD']

 
for index, name in enumerate(methods): 
    print('%-10s' % name, end = '\t')  
     
    for i, histogram in enumerate(hists):
        ret = cv2.compareHist(query, histogram, index) 
        
        if index == cv2.HISTCMP_INTERSECT:                
            ret = ret/np.sum(query)                          
        print(str(i+1)+' ==> '+str(ret))   
        #print("img%d :%7.2f"% (i+1 , ret), end='\t').      

    print()   