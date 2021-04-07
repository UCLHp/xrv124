# -*- coding: utf-8 -*-
"""
@author: Steven Court

Fixed user parameters for XRV-124 analysis
"""



# position of ball bearing in Logos coordinates
TARGET = [0,0,144.8]




# Gantry angles and energies of beams in full QA
# NOTE: these must be in the order of spot delivery
GANTRY = list( range(180,-151,-30) )
ENERGY = [245,240]+list( range(230,69,-10) )




# Threshold (%) for finding centre of BB shadow in entry-exit image
THRESHOLD = 50.0   
# Threshold (%) for finding centroid of spots
THRESH_CENTROID = 50.0

