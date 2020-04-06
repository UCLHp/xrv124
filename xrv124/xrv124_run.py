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



# Christie data for testing is from 2020_0102_0001

# Define GAs and energies used (As at Christie)
GANTRY = list( range(180,-181,-30) )
ENERGY = [245,240]+list( range(230,69,-10) )

print("GANTRY run={}".format(GANTRY))
print("ENERGY run={}".format(ENERGY)) 





def choose_directory():
    """Choose directory containing acquisition files
    """
    msg = "Select data directory"
    title = "Select data directory"
    if easygui.ccbox(msg, title):
        pass
    else:
        sys.exit(0)
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
    results_spot_sizes = {}
    results_sigmas = {}
    ##equiv_diams = {}

    if filesok:
        beams = get_ordered_beams(filenames)
        print("Analyzing spot shifts...")
        results_shifts = xan.analyse_shifts(directory, beams, GANTRY, ENERGY)  ## FEED GANTRY AND ENERGY HERE
        print("Analyzing spot diameters...")
        results_spot_sizes = xan.analyse_spot_sizes(directory, beams, GANTRY, ENERGY)
        print("Analzying spot sigmas...")
        results_sigmas = xan.analyse_spot_profiles(directory, beams, GANTRY, ENERGY)
    else:
        #Need to decide how to deal with this
        print("Incorrect number of files found - did you choose correct directory?")
        exit(0)


    with open("results_shits.txt","w") as json_file:
        json.dump(results_shifts, json_file)
    with open("results_spot_sizes.txt","w") as json_file:
        json.dump(results_spot_sizes, json_file)
    with open("results_spot_sigmas.txt","w") as json_file:
        json.dump(results_sigmas, json_file)





if __name__=="__main__":
    main()



