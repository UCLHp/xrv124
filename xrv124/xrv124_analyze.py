from os import listdir
from os.path import isfile, join, splitext
from math import sin, cos, radians
import numpy as np
import matplotlib.pyplot as plt
from skimage import data, util
from skimage.measure import label, regionprops, profile_line
import easygui
import json
# Robust alternative to curve_fit
from lmfit import Model
from lmfit import Parameters




# % threshold for finding centre of shadow in entry-exit image
THRESHOLD = 50.0   



def get_image_data(filename):
    """Return image dims and numpy array of spot image: [x,y,image]"""
    
    spotdata = open(filename).readlines()

    # Image pitch is in first line
    pitch = float( spotdata[0].split("Pitch:,")[1].split(",")[0].strip() )

    # 3rd line contains image dimension - ALWAYS??      ##TODO: CHECK CORRECT FOR NON-SQUARE IMAGES
    nrows = int( spotdata[2].split(",")[1].strip() )    # or is this x dim => no. columns?
    ncols = int( spotdata[2].split(",")[2].strip() )    # y dim => no. rows?
    
    spotimage = np.zeros( [nrows,ncols] )   ## format np([rows,cols])

    for row in range(3,nrows+3): ## IMAGE DATA STARTS ON ROW 3

        # https://scikit-image.org/docs/dev/user_guide/data_types.html
        # says NEVER USE astype() ON AN IMAGE
        #... but have I? Im just converting strings to floats here...
        spotimage[row-3] = np.array( spotdata[row].split(",") ).astype(float)

    return spotimage, pitch



def get_equivalent_diameter( entryspot ):
    """Return skimage.measure.regionprops() equivalent diameter
    """
    entry_max = entryspot.max()
    entry_thresh = entryspot>(entry_max*0.5) 
    # This works matches well the "diameter" in csv files

    # Use skimage to get region properties
    label_img = label(entry_thresh, connectivity=entry_thresh.ndim)
    props = regionprops(label_img)
    if len(props)!=1:
        print("ERROR: regionprops() did not return a single region")

    return props[0].equivalent_diameter




def analyse_shifts(directory, beams, GANTRY, ENERGY):
    """Analyse full acquisition data set

    This means all beams were captured at all GAs and energies.
    FUNCTION WILL NOT WORK IS THERE IS MISSING DATA
    """
    results = {}

    cnt = -1
    for ga in GANTRY:
        for en in ENERGY:
            cnt+=1

            # key for storing result
            k = "GA"+str(ga)+"E"+str(en)

            entry, pitch_en = get_image_data( join(directory,beams[cnt])+".csv" ) 
            exit, pitch_ex  = get_image_data( join(directory,beams[cnt])+".txt" )
    
            if pitch_en!=pitch_ex:
                print("WARNING: Pitch of entry and exit spots differs!!")
                #TODO: deal with unequal entry/exit spot sizes
            pitch = pitch_en

            nrows = entry.shape[0]
            ncols = entry.shape[1]

            '''plt.imshow( entry )
            plt.title( "Entry spot" )
            plt.show()
            plt.imshow( exit  )
            plt.title( "Exit spot" )
            plt.show()'''

            # subtract exit spot from entry spot
            sub = entry - exit
            # float images must be between -1 and 1
            sub = sub / sub.max() 
            ####################################
            ##sub = np.transpose(sub)
            #####################################
            # simple threshold of 50%. IS THIS APPROPRIATE? 80% BETTER?
            img = sub>(THRESHOLD/100.0)

            # Use skimage to get region properties
            label_img = label(img, connectivity=img.ndim)
            props = regionprops(label_img)
            if len(props)!=1:
                print("ERROR: regionprops() did not return a single region\
                            for GA={}, E={}".format(ga,en) )

            ## np array [y][x]
            imagecentre = [ ncols//2, nrows//2 ]  ## (x,y)
            # centroid of first labeled object
            # Centroid coordinate tuple is (row, col) - i.e. (y,x) so need to flip it
            shadowcentre = [ int(round(props[0].centroid[1],0)), int(round(props[0].centroid[0],0)) ] ## Now (x,y)
            
            # Shift reported as centrOfImage - centreOfBBShadow
            shift_pixels = np.array(imagecentre) - np.array(shadowcentre)
            # i.e. record shift  as tuple (x,y)
            # json does not allow numpy types; need lists and ints
            shift2 = list(shift_pixels)
            #shift3 = [ int(s) for s in shift2 ]        
            shift_mm = [ s*pitch for s in shift2 ]        
            
            # Store results in dictionary
            #results[k] = list(shift3) 
            results[k] = list(shift_mm) 
        
            '''# Plot centre of image and centroid of ball-bearing shadow
            #sub[imagecentre[1]][imagecentre[0]] = -0.99
            #sub[shadowcentre[0]][shadowcentre[1]] = -0.99
            #plt.imshow(sub, cmap=plt.cm.gray)
            #plt.title("Entry-exit spots.\nImage centre and ball-bearing shadow centre shown")
            #plt.show()'''

            
    return results
        



def analyse_spot_sizes(directory, beams, GANTRY, ENERGY):
    """Analyse FULL acquisition data set for entry spot "diameter" in csv file
    FUNCTION WILL NOT WORK IS THERE IS MISSING DATA
    """
    results = {}
    cnt = -1
    for ga in GANTRY:
        for en in ENERGY:
            cnt+=1
            # key for storing result
            k = "GA"+str(ga)+"E"+str(en)
            with open( join(directory,beams[cnt])+".csv" ) as f:
                #First line contains diameter
                line = f.readline()
                diameter = float( line.split("Diameter:,")[1].split(",")[0].strip() )
                results[k] = diameter

    return results







def gaus(x,a,x0,sigma):
    return a*np.exp(-(x-x0)**2/(2*sigma**2))



def sigma_angled_profile_lmfit(spot_img, img_angle, pitch):
    """Returns the sigma from a Gaussian fit along x and y axes
    in the SPOT COORDINATE system.

    DOES LMFIT DO A BETTER JOB AT FITTING?
    """

    nrows = spot_img.shape[0]
    ncols = spot_img.shape[1]    


    # DEFINE START AND END OF PROFILE THROUGH CENTRE
    r = min([nrows,ncols])//2 - 20

    strt_x = ncols//2 + r*cos(radians(img_angle))
    strt_y = nrows//2 - r*sin(radians(img_angle))
    end_x = ncols//2 - r*cos(radians(img_angle))
    end_y = nrows//2 + r*sin(radians(img_angle))

    # Must give start and destination points in (y,x) order
    startpt = (strt_y,strt_x)
    endpt   = (end_y,end_x)
    
    profile = profile_line( spot_img, startpt, endpt  )

    ## Sigma from Gaussian fit
    profile_max = max(profile)
    xvals = np.array( range(len(profile))  ) * pitch     ##PITCH
    yvals = np.array(profile) / profile_max       ## NORM

    # Guess for starting values
    n = len(xvals)
    ##mean = sum(xvals*yvals) /n / profile_max
    mean_init = sum(yvals)/n
    sigma_init = sum(yvals*(xvals-mean_init)**2)/n * pitch

    #Make model
    model = Model( gaus )

    ## If we want unrestricted parameters
    #params = model.make_params(R0=R0_init, sigma=sigma_init, epsilon=epsilon_init)
    # Or add lower bound of 0 to epsilon
    params=Parameters()
    params.add("a", value=0.972)
    params.add("x0", value=mean_init)
    #params.add("sigma", value=sigma, min=0, max=50)
    params.add("sigma", value=sigma_init)

    fitresult = model.fit(yvals, params, x=xvals,method="powell")
    best_sigma = abs(fitresult.params["sigma"].value)

    # Try and catch obvious fitting erros with a second attempt:
    if( best_sigma<2.5 or best_sigma>8.0):
        #assume error and try different initial values
        print("  !! sig={}: trying second fit".format(best_sigma))
        mean2=mean_init*1.5
        sigma2=sigma_init * 5.1
        fitresult = model.fit(yvals, a=0.981, x0=mean2, sigma=sigma2, x=xvals, method="powell")
        best_sigma = abs(fitresult.params["sigma"].value)
        print("  !! sig={}: IN SECOND ATTEMPT".format(best_sigma))

    ###########################################################
    return best_sigma




def analyse_spot_profiles(directory, beams, GANTRY, ENERGY):
    """
    Plots showing spot sizes at each gantry angle
    """

    PITCH = 0.1  
    ## CAN I SIMPLY USE PITCH LIKE THIS IF TAKING PROFILE AT AN ANGLE???????????

    results = {}
    cnt=-1
    for ga in GANTRY:
        for en in ENERGY:    
            cnt+=1

            k="GA"+str(ga)+"E"+str(en) 
            print("{},{}".format(beams[cnt],k))

            entry, pitch = get_image_data( join(directory,beams[cnt])+".csv" ) 

            # Angle profile = 0 at GA=0 SPOT and BEV and IMAGE axes all match
            # hence implies x-profile in IMAGE COORDS but y profile in SPOT COORDS (AT GA=0)
            x_sigma = sigma_angled_profile_lmfit( entry, -ga, pitch )
            y_sigma = sigma_angled_profile_lmfit( entry, 90-ga,  pitch )

            ## USE THESE FOR FIXED IMAGE COORD PROFILES
            #if coords.lower()=="image":
                #x_sigma = sigma_angled_profile_lmfit( entry, x, y, 0, pitch )
                #y_sigma = sigma_angled_profile_lmfit( entry, x, y, 90, pitch )
         
            if(x_sigma>8 or y_sigma>8):
                print("x_sigma={}, y_sigma={}".format(x_sigma, y_sigma) )
            elif(x_sigma<2 or y_sigma<2):
                print("x_sigma={}, y_sigma={}".format(x_sigma, y_sigma) )        

            results[k] = (x_sigma, y_sigma)


    #with open("results_sigmas_spotcoords.txt","w") as json_file:
    #    json.dump(results, json_file)
    return results


