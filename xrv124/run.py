from os import listdir, mkdir
from os.path import isfile, splitext, join
import easygui
import json

import full_analyze as xan
import full_plot as xplot
import full_report as xreport
import partial_analyze
import config


#######################################
GANTRY = config.GANTRY
ENERGY = config.ENERGY

print("\n")
print("GANTRY={}".format(GANTRY))
print("ENERGY={}".format(ENERGY)) 
#######################################



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
    #s="."
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



def full_analysis(directory, beams):
    """Analsysis of full data set"""
    
    # New directory for results
    result_dir = "full_results"
    try:
        mkdir(result_dir)
    except Exception:  
        i=2
        looking=True
        while looking:
            try:
                nm=result_dir+str(i)
                mkdir(nm)
                result_dir=nm
                looking=False
            except Exception:
                i+=1            
                   
    results_shifts = {}
    results_spot_diameters = {}
    results_sigmas = {}
    ##equiv_diams = {}
    print("Analyzing spot shifts...")
    results_shifts = xan.analyse_shifts(directory, beams, GANTRY, ENERGY)  ## FEED GANTRY AND ENERGY HERE
    print("Reading spot diameters...")
    results_spot_diameters = xan.read_spot_diameters(directory, beams, GANTRY, ENERGY)
    #exit()
    print("Analzying spot sigmas...")
    results_sigmas = xan.analyse_spot_profiles(directory, beams, GANTRY, ENERGY)
    print("Reading arc and radial entry spot widths...")
    results_arc_radial = xan.read_arc_radial_widths(directory, beams, GANTRY, ENERGY)
    
    
    ############## IMAGE TO BEV CONVERSION ########################
    # The analyse_shifts method works in image coordinate system.
    # IMG-Y = -BEV-Y hence if we want results in BEV coords:
    for key in results_shifts:
        results_shifts[key][1] *= -1
    ##############################################################
    
    # Save results
    with open(join(result_dir,"results_shifts.txt"),"w") as json_file:
        json.dump(results_shifts, json_file)
    with open(join(result_dir,"results_spot_diameters.txt"),"w") as json_file:
        json.dump(results_spot_diameters, json_file)
    with open(join(result_dir,"results_spot_sigmas.txt"),"w") as json_file:
        json.dump(results_sigmas, json_file)
    with open(join(result_dir,"results_arc_radial.txt"),"w") as json_file:
        json.dump(results_arc_radial, json_file)


    ######## Print result plots
    print("Printing results to {}...".format(result_dir))
  
    # 2D plot of shifts (x,y) grouped by GA
    xplot.plot_shifts_by_gantry(results_shifts, imgname=join(result_dir,"shifts_by_gantry.png"))
    # 2D plot of shifts (x,y) grouped by ENERGY
    xplot.plot_shifts_by_energy(results_shifts, imgname=join(result_dir,"shifts_by_energy.png"))
    # x & y shifts plotted separately vs GA (for each E)
    xplot.plot_xyshifts_vs_gantry(results_shifts, imgname=join(result_dir,"xy_shifts_vs_gantry.png"))
    # x & y shifts plotted separately vs E (for each GA)
    xplot.plot_xyshifts_vs_energy(results_shifts, imgname=join(result_dir,"xy_shifts_vs_energy.png"))
    # Histogram of shifts
    xplot.shifts_histogram(results_shifts, imgname=join(result_dir,"shifts_histo.png"))
    # Polar plot of shifts
    xplot.shifts_polar(results_shifts, imgname=join(result_dir,"shifts_polar.png"))

    ## Spot diameter plots
    xplot.plot_spot_diameters_by_gantry(results_spot_diameters, imgname=join(result_dir,"diameter_by_gantry.png"))
    xplot.plot_spot_diameters_by_energy(results_spot_diameters, imgname=join(result_dir,"diameter_by_energy.png"))
    
    ## Spot sigma (method can do either "image" or "spot" coordinate systems
    xplot.plot_spot_sigmas(results_sigmas, imgname=join(result_dir,"sigmas_xy.png"))
    
    ## Arc and radial widths from entry spot
    xplot.plot_spot_sigmas(results_arc_radial, imgname=join(result_dir,"arc_radial.png"),
                               arc_radial=True)
    
    ######## Print result summary PDF
    xreport.summary_reportlab(results_shifts, 
                images=[join(result_dir,"shifts_by_gantry.png"),
                        join(result_dir,"shifts_by_energy.png"),
                        join(result_dir,"shifts_histo.png"),
                        join(result_dir,"shifts_polar.png")                         
                       ],
                output=join(result_dir,"Summary report.pdf")
                )






def main():

    directory = choose_directory()
    filenames = get_filenames(directory)
    filesok = check_files(filenames)

    if filesok:
        print("Full data set found")
        beams = get_ordered_beams(filenames)
        full_analysis(directory, beams)
    else:
        msg = ("\nINCORRECT NUMBER OF FILES FOUND\n"
         "- Did you choose correct directory?\n"
         "- Are GANTRY and ENERGY correct in config.py?\n")
        print(msg)
        ask=True
        while ask:
            ans = input("Yes/No (Y/N): ")
            if ans.lower().strip()=="n":
                print("Exiting program")
                exit(0)
            elif ans.lower().strip()=="y":
                partial_analyze.analysis()
                ask=False





if __name__=="__main__":
    main()



