from os.path import join
import numpy as np
#import matplotlib.pyplot as plt
#from skimage import data, util
#from skimage.measure import label, regionprops
from os import listdir
from os.path import isfile, join, splitext
import easygui
import json

import xrv124_analyze as xan
import xrv124_plot as xplot
import xrv124_report as xreport



# Christie data for testing is from 2020_0102_0001

# Define GAs and energies used (As at Christie)
GANTRY = list( range(180,-181,-30) )
ENERGY = [245,240]+list( range(230,69,-10) )

print("\n")
print("GANTRY={}".format(GANTRY))
print("ENERGY={}".format(ENERGY)) 






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



def get_filenames(directory):
    """Returns list of files in directory
    """
    onlyfiles = [f for f in listdir(directory) if isfile(join(directory, f))]
    return onlyfiles



def check_files(filenames):
    """Return true if all expected files present

    e.g. 19 energies, 13 GAs, 3 files each (csv,txt,bmp)
    """
    #Remove file extension
    s="."
    #names = [ s.join( n.split(".")[0:len(n.split("."))-1] ) for n in filenames]
    names = [ splitext(n)[0] for n in filenames]
    print("totalfiles={}".format(len(names)) )
    #Only take numeric names 
    dignames = [n for n in names if str.isdigit(n)]
    print("dignames={}".format(len(dignames)) )
    #Remove repeats
    uniqnames = list( set(dignames) )
    print("uniquenames={}".format(len(uniqnames)) )
    
    if( len(dignames)==len(GANTRY)*len(ENERGY)*3 and 
            len(uniqnames)==len(dignames)//3 ):
        return True
    else:
        return False 



def get_ordered_beams(filenames):
    """Return sorted, uniq file IDs for captured beams
    """
    num_names = [splitext(n)[0] for n in filenames if str.isdigit(splitext(n)[0]) ]
    uniq = list( set(num_names) )
    return sorted(uniq, key=lambda e: int(e))






def main():

    directory = choose_directory()
    filenames = get_filenames(directory)
    filesok = check_files(filenames)

    results_shifts = {}
    results_spot_diameters = {}
    results_sigmas = {}
    ##equiv_diams = {}

    if filesok:
        beams = get_ordered_beams(filenames)
        print("Analyzing spot shifts...")
        results_shifts = xan.analyse_shifts(directory, beams, GANTRY, ENERGY)  ## FEED GANTRY AND ENERGY HERE
        print("Reading spot diameters...")
        results_spot_diameters = xan.read_spot_diameters(directory, beams, GANTRY, ENERGY)
        print("Analzying spot sigmas...")
        results_sigmas = xan.analyse_spot_profiles(directory, beams, GANTRY, ENERGY)
        print("Reading arc and radial entry spot widths...")
        results_arc_radial = xan.read_arc_radial_widths(directory, beams, GANTRY, ENERGY)
    else:
        #Need to decide how to deal with this
        print("Incorrect number of files found - did you choose correct directory?")
        exit(0)



    ############## IMAGE TO BEV CONVERSION ###################
    # Analyse_shifts method works in image coordinate system
    # IMG-Y = -BEV-Y hence if we want results in BEV:
    for key in results_shifts:
        results_shifts[key][1] *= -1
    ##########################################################



    # Save results
    with open("results_shifts.txt","w") as json_file:
        json.dump(results_shifts, json_file)
    with open("results_spot_diameters.txt","w") as json_file:
        json.dump(results_spot_diameters, json_file)
    with open("results_spot_sigmas.txt","w") as json_file:
        json.dump(results_sigmas, json_file)
    with open("results_arc_radial.txt","w") as json_file:
        json.dump(results_arc_radial, json_file)




    ######## Print result plots
    print("Printing results...")

    
    # 2D plot of shifts (x,y) grouped by GA
    xplot.plot_shifts_by_gantry(results_shifts, imgname="shifts_by_gantry.png")
    # 2D plot of shifts (x,y) grouped by ENERGY
    xplot.plot_shifts_by_energy(results_shifts, imgname="shifts_by_energy.png")
    # x & y shifts plotted separately vs GA (for each E)
    xplot.plot_xyshifts_vs_gantry(results_shifts, imgname="xy_shifts_vs_gantry.png")
    # x & y shifts plotted separately vs E (for each GA)
    xplot.plot_xyshifts_vs_energy(results_shifts, imgname="xy_shifts_vs_energy.png")

    ## Spot diameter plots
    xplot.plot_spot_diameters_by_gantry(results_spot_diameters, imgname="diameter_by_gantry.png")
    xplot.plot_spot_diameters_by_energy(results_spot_diameters, imgname="diameter_by_energy.png")
    

    ## Spot sigma (method can do either "image" or "spot" coordinate systems
    xplot.plot_spot_sigmas(results_sigmas, imgname="sigmas_xy.png")
    
    ## Arc and radial widths from entry spot
    xplot.plot_spot_sigmas(results_arc_radial, imgname="arc_radial.png",
                               arc_radial=True)
    



    ######## Print result summary PDF
    xreport.summary_reportlab(results_shifts, 
                images=["shifts_by_gantry.png","shifts_by_energy.png"],
                output="Summary report.pdf"
                )







if __name__=="__main__":
    main()



