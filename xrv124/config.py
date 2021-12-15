# -*- coding: utf-8 -*-
"""
@author: Steven Court

Input and analysis options for XRV-124 analysis
"""


GANTRY_NAMES = ["Gantry 1","Gantry 2","Gantry 3","Gantry 4"]



# Gantry angles and energies of beams in QA
# NOTE: these must be in the order of spot delivery
op1 = "180,150,120,90,60,30,0,-30,-60,-90,-120,-150"
op2 = "165,135,105,75,45,15,-15,-45,-75,-105,-135,-165"
op3 = "180,90,0,-90"
GANTRY_ANGLE_OPTIONS = [op1,op2,op3]

ENERGIES = "245,240,230,220,210,200,190,180,170,160,150,140,130,120,110,100,90,80,70"



# Threshold (%) for finding centre of BB shadow in entry-exit image
THRESHOLD = 50.0   
# Threshold (%) for finding centroid of spots
THRESH_CENTROID = 50.0


# position of ball bearing in Logos coordinates
TARGET = [0,0,144.8]



# Database info
PATH_TO_DB = r""
SESSION_TABLE = "xrv124session"
RESULTS_TABLE = "xrv124results"