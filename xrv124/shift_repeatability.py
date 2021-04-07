# -*- coding: utf-8 -*-
"""
Consistency in measured shifts. Point script to folder containing 
the results_shifts.txt output file from multiple data sets.
Folder could contain, for example, multiple irradiations without touching the
xrv124 (assess beam consistency) and with re-setting up (inter-user variation).
"""

from os import listdir
from os.path import join, isfile

import json
import matplotlib.pyplot as plt
import easygui



def choose_directory():
    """Choose directory containing acquisition files
    """
    msg = "Select data directory"
    title = "Select data directory"
    if easygui.ccbox(msg, title):
        pass
    else:
        exit(0)
    return easygui.diropenbox()



if __name__=="__main__":

    dirpath = choose_directory()
    allfiles = [join(dirpath,f) for f in listdir(dirpath) if isfile(join(dirpath, f))]
    
    xvals={}
    yvals={}
    tot={}
    for f in allfiles:
        xyshifts = json.loads(open(f).read())
        for k in xyshifts:
            x,y = xyshifts[k][0],xyshifts[k][1]
            
            if k in xvals:
                xvals[k].append(x)
                yvals[k].append(y)
                tot[k].append( (x**2+y**2)**0.5 )
            else:
                xvals[k] = [x]
                yvals[k] = [y]
                tot[k] = [(x**2+y**2)**0.5]
                
    xmaxdiffs=[]
    ymaxdiffs=[]
    totdiffs=[]
    for k in xvals:
        
#        if len(tot[k])>1:
#            totmax = max(tot[k]) - min(tot[k])
#            totdiffs.append(totmax)
#
#            tol=0.4
#            if totmax>=tol:
#                print("{}, >= {}mm".format(k,tol))
            
        if len(xvals[k])>1:
            xmax = max(xvals[k]) - min(xvals[k])
            xmaxdiffs.append(xmax)
            ymax = max(yvals[k]) - min(yvals[k])
            ymaxdiffs.append(ymax)
            
            tol=0.5
            if xmax>=tol or ymax>=tol:
                print("{}, >= {}mm".format(k,tol))
    
  
    plt.hist(xmaxdiffs,alpha=0.3,label="BEV-X",bins=[0,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9],align="left")
    plt.hist(ymaxdiffs,alpha=0.3,label="BEV-Y",bins=[0,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9],align="left")
    plt.legend()
    plt.xlabel("Max difference (mm)")
    plt.title("Max difference in spot position between irradiations")
    plt.show()
    
#    plt.figure()
#    plt.hist(totdiffs,alpha=0.3,label="Total shift",bins=[0,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.0],align="left")
#    plt.legend()
#    plt.xlabel("Max total difference (mm)")
#    plt.title("Max difference in spot position between irradiations")
#    plt.show()