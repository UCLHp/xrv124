import sys
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





# % threshold for finding centre of BB shadow in entry-exit image
THRESHOLD = 50.0   

# % threshold for finding centroid of spots
THRESH_CENTROID = 50.0




def progress_bar(value, endvalue, bar_length=50):
    """Displays percentage of beams processed"""

    percent = float(value) / endvalue
    arrow = '-' * int(round(percent * bar_length))
    spaces = ' ' * (bar_length - len(arrow))

    sys.stdout.write("\r[{0}] {1}%".format(arrow + spaces, int(round(percent * 100))))
    sys.stdout.flush()



def get_image_data(filename):
    """Return image numpy array of image plus pitch
    """
    
    spotdata = open(filename).readlines()

    # Image pitch (pixel width) is in first line
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



def get_centroid_of_largest_region( img, threshold, ga=None, en=None ):
    """Return centroid of spot based on threshold image

    Depending on choice of threshold there may be more than 1 region identified
    Method always chooses the largest based on diameter as this will be the main spot
    """
    # float images must be between -1 and 1
    norm_img = img / img.max() 

    # simple threshold of 50%.
    thresh = norm_img>(threshold/100.0)

    # Use skimage to get region properties
    label_img = label(thresh, connectivity=thresh.ndim)
    props = regionprops(label_img)
    # Our region of interest
    largest_region = None

    if len(props)==0:
        print("ERROR: regionprops() found no region!")
    else:
        if len(props)>1:
            print("Warning: regionprops() found multiple regions\
                      for GA={}, E={} at threshold={}. Choosing\
                         largest.".format(ga,en, threshold) )
        largest_diam = -999
        largest_index = -1        
        for i,p in enumerate(props):
            if p.equivalent_diameter>largest_diam:
                largest_diam = p.equivalent_diameter
                largest_index = i

        largest_region = props[largest_index]

    # Centroid of first labeled object
    # Centroid coordinate tuple is (row, col) - i.e. (y,x) so need to flip it
    # Rounded to nearest pixel 
    centroid = [ int(round(largest_region.centroid[1],0)), int(round(largest_region.centroid[0],0)) ] ## Now (x,y)
    # Leave coord as float 
    ##centroid = [ largest_region.centroid[1], largest_region.centroid[0] ] ## Now (x,y)

    return centroid




def analyse_shifts(directory, beams, GANTRY, ENERGY):
    """Analyse spot shifts in x,y of IMAGE COORDINATES

    Q: define shift from centre of image or centre of spot???

    This means all beams were captured at all GAs and energies.
    FUNCTION WILL NOT WORK IS THERE IS MISSING DATA
    """
    results = {}

    cnt = -1

    spot_img_centre_shifts = []
    centre_shifts = []
    
    for ga in GANTRY:
        for en in ENERGY:
            cnt+=1
            
            progress_bar(cnt, len(beams) )

            # key for storing result
            k = "GA"+str(ga)+"E"+str(en)

            entry, pitch_en = get_image_data( join(directory,beams[cnt])+".csv" ) 
            exit, pitch_ex  = get_image_data( join(directory,beams[cnt])+".txt" )
    
            if pitch_en!=pitch_ex:
                print("WARNING: Pitch of entry and exit spots differs!!")
                #TODO: deal with unequal entry/exit spot sizes
            pitch = pitch_en

            ## np array [y][x]
            nrows = entry.shape[0]
            ncols = entry.shape[1]

            # subtract exit spot from entry spot for shadow
            sub = entry - exit

            # centroid of shadow
            shadowcentre = get_centroid_of_largest_region( sub, THRESHOLD, ga, en )

            ####### TODO, decide
            # Get centre of image coords
            imagecentre = [ ncols//2, nrows//2 ]  ## (x,y)
            # OR should this be centre of the exitspot?
            exitspotcentre = get_centroid_of_largest_region( exit, THRESH_CENTROID , ga, en )
            # Centre of entry? (To avoid issues with BB shadow)
            entryspotcentre = get_centroid_of_largest_region( entry, THRESH_CENTROID , ga, en )
            # Average both the exit and entry spot centres?
            avgcentre = [ 0.5*(exitspotcentre[0]+entryspotcentre[0]),
                          0.5*(exitspotcentre[1]+entryspotcentre[1])  ]


            #### experimenting #####
            ##print("####### {},{}".format(beams[cnt],k))
            ##print("Entry centre = {}, Exit Centre = {}".format(entryspotcentre, exitspotcentre)  )
            centre_diff = [ entryspotcentre[0]-exitspotcentre[0], entryspotcentre[1]-exitspotcentre[1]  ]
            ##print("   diff = {}".format(centre_diff) )
            centre_shifts.append(  (centre_diff[0]**2+centre_diff[1]**2)**0.5   )
      
            ##print("ExitSpotCentre = {}, ImageCentre = {}".format(exitspotcentre, imagecentre)  )
            spot_img_diff = [ exitspotcentre[0]-imagecentre[0], exitspotcentre[1]-imagecentre[1]  ]
            ##print("   diff = {}".format(spot_img_diff) )
            spot_img_centre_shifts.append(  (spot_img_diff[0]**2+spot_img_diff[1]**2)**0.5   )


            #####   TODO: DECIDE WHAT TO USE 
            # Benefit to image centre is it's not dependent on quality of spot image
            # Or if Logos gets this slightly misplaced then it's better to use spots, but best
            #     to use an avg of entry and exit in case BB shadow in exit spot affects centroid
            # Need to be sure regionprops works well
            ############################################################################
            # Shift reported as centrOfImage - centreOfBBShadow
            shift_pixels = np.array(imagecentre) - np.array(shadowcentre)
            #
            # Shift as centreOfExitSpot - centreOfBBShadow            
            ##shift_pixels = np.array(exitspotcentre) - np.array(shadowcentre)

            # I think we should use some info from the spots rather than just the image
            # coordinate centre. DECISION: avg entry and exit spot centres and use a 
            # threshold value (to determine centroid) of 50%
            ###shift_pixels = np.array(avgcentre) - np.array(shadowcentre)
            ########################################################################### 

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


    #print("Mean shift (mm) from centre of spot from centre of image = {}".format( pitch*sum(spot_img_centre_shifts)/len(spot_img_centre_shifts) ) )
    #print("Max shift = {}".format( max(spot_img_centre_shifts)*pitch ) )

    #print("Mean shift (mm) from centre of entry and exit spot = {}".format( pitch*sum(centre_shifts)/len(centre_shifts) ) )
    #print("Max shift = {}".format( max(centre_shifts)*pitch ) )
            
    # New line after porgress bar
    sys.stdout.write("\n")
    sys.stdout.flush()
            
    return results
        



def read_spot_diameters(directory, beams, GANTRY, ENERGY):
    """Retrieve entry spot "diameter" from csv file
    FUNCTION WILL NOT WORK IF THERE IS MISSING DATA
    """
    
    #TODO: Should I take the average of the entry and exit spot diameters?
    
    results = {}
    cnt = -1
    for ga in GANTRY:
        for en in ENERGY:
            cnt+=1
            
            progress_bar(cnt, len(beams) )
            
            # key for storing result
            k = "GA"+str(ga)+"E"+str(en)
            with open( join(directory,beams[cnt])+".csv" ) as f:
                #First line contains diameter
                line = f.readline()
                diameter = float( line.split("Diameter:,")[1].split(",")[0].strip() )
                results[k] = diameter

    # New line after porgress bar
    sys.stdout.write("\n")
    sys.stdout.flush()

    return results




def read_arc_radial_widths(directory, beams, GANTRY, ENERGY):
    """Retrieve entry spot "arc" (BEV-X) and "radial" (BEV-Y) widths 
    from entry spot csv file
    """
        
    results = {}
    cnt = -1
    for ga in GANTRY:
        for en in ENERGY:
            cnt+=1
            
            progress_bar(cnt, len(beams) )
            
            # key for storing result
            k = "GA"+str(ga)+"E"+str(en)
            with open( join(directory,beams[cnt])+".csv" ) as f:
                arc, radial = None, None
                for line in f.readlines():
                    if "Arc Style" in line:
                        arc = float( line.split("Entry (mm):,")[1].split(",")[0].strip() )
                    if "Radial Style" in line:
                        radial = float( line.split("Entry (mm):,")[1].split(",")[0].strip() )             

            results[k] = (arc,radial)

    # New line after porgress bar
    sys.stdout.write("\n")
    sys.stdout.flush()

    return results






def gaus(x,a,x0,sigma):
    """Gaussian function for fitting"""
    return a*np.exp(-(x-x0)**2/(2*sigma**2))




def sigma_from_gaussian_lmfit(profile, pitch):
    """Return sigma from Gaussian fit with lmfit"""

    # TODO: this needs to be robust; catch poor fits; choose better starting points

    profile_max = max(profile)
    xvals = np.array( range(len(profile))  ) * pitch     ##PITCH
    yvals = np.array(profile) / profile_max              ## NORM

    # Guess for starting values
    n = len(xvals)
    ##mean = sum(xvals*yvals) /n / profile_max
    mean_init = sum(yvals)/n
    sigma_init = sum(yvals*(xvals-mean_init)**2)/n * pitch

    #Make model
    model = Model( gaus )

    # Set initial guess
    params=Parameters()
    params.add("a", value=0.972)
    params.add("x0", value=mean_init)
    #params.add("sigma", value=sigma, min=0, max=50)
    params.add("sigma", value=sigma_init)

    fitresult = model.fit(yvals, params, x=xvals,method="powell")
    best_sigma = abs(fitresult.params["sigma"].value)

    # Try and catch obvious fitting erros with a second attempt: #TODO: DO PROPERLY WITH A GOODNESS OF FIT PARAM
    if( best_sigma<2.5 or best_sigma>8.0):
        #assume error and try different initial values
        print("  !! sig={}: trying second fit".format(best_sigma))
        mean2=mean_init*1.5
        sigma2=sigma_init * 5.1
        fitresult = model.fit(yvals, a=0.981, x0=mean2, sigma=sigma2, x=xvals, method="powell")
        best_sigma = abs(fitresult.params["sigma"].value)
        print("  !! sig={}: IN SECOND ATTEMPT".format(best_sigma))

    return best_sigma




def sigma_angled_profile(spot_img, img_angle, pitch):
    """Returns sigma of spot from a profile taken at img_angle
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
    
    profile = profile_line(spot_img, startpt, endpt)

    sigma = sigma_from_gaussian_lmfit(profile, pitch)
    return sigma




def analyse_spot_profiles(directory, beams, GANTRY, ENERGY):
    """Returns sigma of spot in x,y of SPOT COORDINATE system 
    (from a profile taken at specified angle in IMAGE coords)


    CHOICE of "spot" coords or "BEV" coords (to be commented out)
    """

    ## CAN I SIMPLY USE PITCH IF TAKING PROFILE AT AN ANGLE???????????

    results = {}
    cnt=-1
    for ga in GANTRY:
        for en in ENERGY:    
            cnt+=1
            
            progress_bar(cnt, len(beams) )

            k="GA"+str(ga)+"E"+str(en) 
            # Print which file corresponds to which beam
            #print("{},{}".format(beams[cnt],k))

            entry, pitch = get_image_data( join(directory,beams[cnt])+".csv" ) 

            ## Angle profile=0 at GA=0 SPOT and BEV and IMAGE axes all match
            ## hence implies x-profile in IMAGE COORDS but y profile in SPOT COORDS (AT GA=0)
            ##x_sigma = sigma_angled_profile( entry, -ga, pitch )
            ##y_sigma = sigma_angled_profile( entry, 90-ga,  pitch )

            ## USE THESE FOR FIXED IMAGE COORD PROFILES (BEV coords)
            x_sigma = sigma_angled_profile( entry, 0, pitch )
            y_sigma = sigma_angled_profile( entry, 90, pitch )
         

            if(x_sigma>8 or y_sigma>8):
                print("x_sigma={}, y_sigma={}".format(x_sigma, y_sigma) )
            elif(x_sigma<2 or y_sigma<2):
                print("x_sigma={}, y_sigma={}".format(x_sigma, y_sigma) )        

            results[k] = (x_sigma, y_sigma)
            
    # New line after porgress bar
    sys.stdout.write("\n")
    sys.stdout.flush()

    return results

