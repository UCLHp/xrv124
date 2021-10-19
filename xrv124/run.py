from os import listdir, mkdir
from os.path import isfile, splitext, join, getctime
import json
import csv
import datetime

#import easygui

import full_analyze as xan
import full_plot as xplot
import full_report as xreport
import partial_analyze
import config
import gui


#######################################
GANTRY_ANGLES = config.GANTRY_ANGLES
ENERGIES = config.ENERGIES

TARGET = config.TARGET

print("\n")
print("GANTRY_ANGLES={}".format(GANTRY_ANGLES))
print("ENERGIES={}".format(ENERGIES)) 
#######################################



def get_acquisition_date(file):
    """Return date of data acquisition from data file timestamp
    
    This only works on Windows OS
    """
    tt = getctime(file)
    date = datetime.datetime.fromtimestamp(tt).date()
    return str(date)


def get_filenames(directory):
    """Returns list of files in directory
    """
    onlyfiles = [f for f in listdir(directory) if isfile(join(directory, f))]
    return onlyfiles



def check_files(filenames):
    """Return true if all expected files present

    e.g. energies*GAs*3 files each (csv,txt,bmp)
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
    
    if( len(dignames)==len(GANTRY_ANGLES)*len(ENERGIES)*3 and 
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


def make_results_directory(basedir,attempted_name):
    """Make empty directory for results; return its name
    
    Try attempted_name; add integer if exists
    """
    result_dir = attempted_name
    try:
        mkdir( join(basedir,result_dir) )
    except Exception:  
        i=2
        looking=True
        while looking:
            try:
                nm=result_dir+"_"+str(i)
                mkdir( join(basedir,nm) )
                result_dir=nm
                looking=False
            except Exception:
                i+=1     
    return join(basedir,result_dir)           
                

def full_analysis(directory, beams, gantry_num, acq_date, outputdir):
    """Analsysis of full data set"""
     
    result_dir=outputdir
      
    print("Analyzing BEV spot shifts...")
    results_shifts = {}
    results_shifts = xan.analyse_shifts(directory, beams)
    ############## IMAGE TO BEV CONVERSION ########################
    # The analyse_shifts method works in image coordinate system.
    # IMG-Y = -BEV-Y hence if we want results in BEV coords:
    for key in results_shifts:
        results_shifts[key][1] *= -1
    ##############################################################
    print("Saving and printing shift results...")
    with open(join(result_dir,"results_shifts.txt"),"w") as json_file:
        json.dump(results_shifts, json_file)    
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


    """
    ## 3D SHIFTS VECTORS IN LOGOS COORDINATES - not using this
    print("Calculating 3D shifts (presence of ball bearing will reduce accuracy)...")
    results_3d_shifts = xan.shift_vector_logos_coords(directory, beams, GANTRY, ENERGY, TARGET)
    with open(join(result_dir,"results_3d_shifts.txt"),"w") as json_file:
        json.dump(results_3d_shifts, json_file)
    xplot.shifts_3d_histogram(results_3d_shifts, imgname=join(result_dir,"shifts_3d_histo.png"))  
    """
      
    results_spot_diameters = {}
    results_sigmas = {}
    print("Reading spot diameters...")
    results_spot_diameters = xan.read_spot_diameters(directory, beams)
    with open(join(result_dir,"results_spot_diameters.txt"),"w") as json_file:
        json.dump(results_spot_diameters, json_file)    
    ## Spot diameter plots
    xplot.plot_spot_diameters_by_gantry(results_spot_diameters, imgname=join(result_dir,"diameter_by_gantry.png"))
    xplot.plot_spot_diameters_by_energy(results_spot_diameters, imgname=join(result_dir,"diameter_by_energy.png"))        
        
    
    print("Analzying spot sigmas...")
    results_sigmas = xan.analyse_spot_profiles(directory, beams)
    with open(join(result_dir,"results_spot_sigmas.txt"),"w") as json_file:
        json.dump(results_sigmas, json_file)    
    ## Spot sigma (method can do either "image" or "spot" coordinate systems
    xplot.plot_spot_sigmas(results_sigmas, imgname=join(result_dir,"sigmas_xy.png"))        
        
    
    print("Reading arc and radial entry spot widths...")
    results_arc_radial = xan.read_arc_radial_widths(directory, beams)
    with open(join(result_dir,"results_arc_radial.txt"),"w") as json_file:
        json.dump(results_arc_radial, json_file)
    ## Arc and radial widths from entry spot
    xplot.plot_spot_sigmas(results_arc_radial, imgname=join(result_dir,"arc_radial.png"),
                               arc_radial=True)
    

    print("Generating summary PDF report...")
    xreport.summary_reportlab(results_shifts, acq_date, gantry_num,
                images=[join(result_dir,"shifts_by_gantry.png"),
                        join(result_dir,"shifts_by_energy.png"),
                        join(result_dir,"shifts_histo.png"),
                        join(result_dir,"shifts_polar.png")                         
                       ],
                output=join(result_dir,"Summary report.pdf")
                )


    print("Generating data for database...")
    # Store x and y shifts plus Logos-diameter for each spot
    db_results = join(result_dir,"db_results.csv")
    # need newline to avoid blank lines
    with open(db_results,'w', encoding='UTF8',newline='') as f:
        writer = csv.writer(f)
        header = ["Date","Gantry","GA","E","x-offset","y-offset","Diameter"]
        writer.writerow(header)
        for key in results_shifts:
            ga = key.split("GA")[1].split("E")[0]
            e = key.split("E")[1]
            xoff,yoff = results_shifts[key]
            diam = results_spot_diameters[key]
            
            data = [acq_date,gantry_num,ga,e,xoff,yoff,diam]
            writer.writerow(data)




def main():

    # User input
    gui_input = gui.gui()
    directory = gui_input["datadir"]
    gantry_name = gui_input["gantry"]
    outputdir = gui_input["outputdir"]
    
        
    filenames = get_filenames(directory)
    filesok = check_files(filenames)   
    acq_date = get_acquisition_date( join(directory,filenames[0]) )
    
    # New directory for results
    res_dir_name = gantry_name+" "+str(acq_date)
    result_dir = make_results_directory(outputdir,res_dir_name)
    print("Results will be printed to {}".format(result_dir))
    
    

    if filesok:
        print("Full data set found")
        beams = get_ordered_beams(filenames)
        full_analysis(directory, beams, gantry_name, acq_date, result_dir)
    else:
        msg = ("\nINCORRECT NUMBER OF FILES FOUND\n"
         "- Did you choose correct directory?\n"
         "- Are GANTRY and ENERGY correct in config.py?\n")
        print(msg)
        ask=True
        while ask:
            ans = input("Yes/No (Y/N): ")
            if ans.lower().strip([0])=="n":
                print("Exiting program")
                exit(0)
            elif ans.lower().strip()[0]=="y":
                partial_analyze.analysis()
                ask=False





if __name__=="__main__":
    main()



