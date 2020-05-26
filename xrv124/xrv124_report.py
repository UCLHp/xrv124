import json
import matplotlib.pyplot as plt
from matplotlib import cm
import numpy as np
import easygui

###############################################
GANTRY = list( range(180,-181,-30) )
ENERGY = [245,240]+list( range(230,69,-10) )
###############################################



'''# Temporary tolerances to be used

Action/Suspension limits:
Action limit: 		>1.0mm for at least 50% of energies for any given gantry angle;
			>1.5mm for at least 5 energies at any gantry angle;
			>2.0mm for any energy at any gantry angle.
Suspension limit:	>2.5mm for any energy at any gantry angle.
'''



# PyFPDF: https://www.blog.pythonlibrary.org/2018/06/05/creating-pdfs-with-pyfpdf-and-python/
# Interactive PDFs with ReportLab: https://www.blog.pythonlibrary.org/2018/05/29/creating-interactive-pdf-forms-in-reportlab-with-python/



def get_total_displacement( shifts ):
    """Convert x,y shifts to total displacement"""
    displacements = {}
    for key in shifts:
        xy = shifts[key]
        total_shift = (xy[0]**2 + xy[1]**2)**0.5
        displacements[key] = total_shift

    return displacements



def print_shift_summary( shifts ):
    """Print a report of the beam shift results with respect
    to the tolerances defined in XXX

    "shifts" input is a dictionary in form { "GA0E240":[xshift, yshift] }
    where x and y are in the image (hence BEV) coordinate system
    """

    displacements = get_total_displacement( shifts )

    for ga in GANTRY:

        # Store beams that were out of certain tolerances
        gt_1 = []
        gt_1p5 = []
        gt_2 = []
        gt_2p5 = []

        for en in ENERGY:
            k="GA"+str(ga)+"E"+str(en)

            if displacements[k] > 2.5:
                gt_2p5.append(k)
            elif displacements[k] > 2.0:
                gt_2.append(k)
            elif displacements[k] > 1.5:
                gt_1p5.append(k)
            elif displacements[k] > 1.0:
                gt_1.append(k)


        # Check tolerances per GA
        if len(gt_2p5)>0:
            print("WARNING: Suspension limit exceeded; beam {}\n".format(k))
            print(gt_2p5)
        if len(gt_2)>0:
            print("WARNING: 2mm Action limit exceeded for GA={}\n".format(ga))
            print( gt_2 + gt_2p5 )
        if len(gt_1p5)+len(gt_2) >= 5:
            print("WARNING: 1.5mm Action Limit exceeded for GA={}\n".format(ga))
            print( gt_1p5 + gt_2 + gt_2p5 )
        if len(gt_1)+len(gt_1p5)+len(gt_2) >= len(ENERGY)/2.0:
            print("WARNING: 1.0mm Action Limit exceeded for GA={}\n".format(ga))
            print( gt_1 + gt_1p5 + gt_2 + gt_2p5 )

        print( gt_1 )
            

        
