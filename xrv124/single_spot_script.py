from os.path import isfile, join, splitext
import numpy as np
from skimage.measure import label, regionprops, profile_line
import matplotlib.pyplot as plt
import easygui

################################################################
#
# Script for analysing shifts of a single spot for use during 
# engineer work / acceptance.
# Also prints spot sizes as determined by Logos software
#
################################################################


# Threshold (%) for finding centre of shadow in entry-exit image
THRESHOLD = 50.0   
###########################



def get_image_data(filename):
    """Return image numpy array of image plus pitch (pixel size)
    """
    
    spotdata = open(filename).readlines()

    # Image pitch (pixel width) is in first line
    pitch = float( spotdata[0].split("Pitch:,")[1].split(",")[0].strip() )

    # 3rd line contains image dimension - ALWAYS??      ##TODO: CHECK CORRECT FOR NON-SQUARE IMAGES
    nrows = int( spotdata[2].split(",")[1].strip() )    # or is this x dim => no. columns?
    ncols = int( spotdata[2].split(",")[2].strip() )    # y dim => no. rows?
    
    spotimage = np.zeros( [nrows,ncols] )   ## format np([rows,cols])

    for row in range(3,nrows+3): # Image data starts on fourth row
        spotimage[row-3] = np.array( spotdata[row].split(",") ).astype(float)

    return spotimage, pitch




def print_spot_diameter(spotfile, spot="Entry"):
    """Retrieve entry spot "diameter" from csv file
    """  
    filetype=""  
    if spot=="Entry":
        filetype=".csv"
    elif spot=="Exit":
        filetype=".txt"

    #TODO: Should I take the average of the entry and exit spot diameters?
    with open( spotfile+filetype ) as f:
        #First line contains diameter
        line = f.readline()
        diameter = float( line.split("Diameter:,")[1].split(",")[0].strip() )
    #return diameter
    print("    Effective diameter = {}mm".format(diameter))




def print_arc_radial_widths(spotfile, spot="Entry"):
    """Retrieve entry spot "arc" (BEV-X) and "radial" (BEV-Y) widths 
    from entry spot csv file
    """
    filetype=""
    if spot=="Entry":
        filetype=".csv"
    elif spot=="Exit":
        filetype=".txt"

    arc, radial = None, None
    with open( spotfile+filetype ) as f:
        for line in f.readlines():
            if "Arc Style" in line:
                arc = float( line.split(spot+" (mm):,")[1].split(",")[0].strip() )
            if "Radial Style" in line:
                radial = float( line.split(spot+" (mm):,")[1].split(",")[0].strip() )             
    #return (arc,radial)
    print("    Arc width (BEV-X) = {}mm".format(arc) )
    print("    Radial width (BEV-Y) = {}mm".format(radial) )




def print_shifts(beamname):
    """Print x,y shifts in BEV coords of exit spot from BB shadown
    """

    entry, pitch_en = get_image_data( join(beamname+".csv" ) )
    exit, pitch_ex  = get_image_data( join(beamname+".txt" ) )

    if pitch_en!=pitch_ex:
        print("WARNING: Pitch of entry and exit spots differs!!")
        #TODO: deal with unequal entry/exit spot sizes
    pitch = pitch_en

    nrows = entry.shape[0]
    ncols = entry.shape[1]

    plt.imshow( entry )
    plt.title( "Entry spot" )
    plt.show()

    # subtract exit spot from entry spot
    sub = entry - exit
    # float images must be between -1 and 1
    sub = sub / sub.max() 

    # simple threshold - 50% most appropriate?
    img = sub>(THRESHOLD/100.0)

    # Use skimage to get region properties
    label_img = label(img, connectivity=img.ndim)
    props = regionprops(label_img)
    if len(props)!=1:
        print("ERROR: regionprops() did not return a single region")

    ## np array [y][x]
    imagecentre = [ ncols//2, nrows//2 ]  ## (x,y)
    # centroid of first labeled object
    # Centroid coordinate tuple is (row, col) - i.e. (y,x) so need to flip it
    shadowcentre = [ int(round(props[0].centroid[1],0)), int(round(props[0].centroid[0],0)) ] ## Now (x,y)

    # Shift reported as centreOfImage(Spot) - centreOfBBShadow
    shift_pixels = np.array(imagecentre) - np.array(shadowcentre)
    shift2 = list(shift_pixels)
    shift_mm = [ s*pitch for s in shift2 ]        

    print( f"    x={shift_mm[0]}, y={-shift_mm[1]}" )

    #Plot centre of image and centroid of ball-bearing shadow
    exit[imagecentre[1]][imagecentre[0]] = -0.99
    exit[shadowcentre[1]][shadowcentre[0]] = -0.99
    plt.ylabel("BEV  Y  --->", fontsize=16)
    plt.xlabel("BEV  X  --->", fontsize=16)
    plt.tick_params(
    axis='both',       # changes apply to the x-axis
    which='both',      # both major and minor ticks are affected
    bottom=False,      # ticks along the bottom edge are off
    top=False,
    left=False,
    labelleft=False,        
    labelbottom=False) # labels along the bottom edge are off
    plt.imshow(exit)
    plt.title("Entry-exit spots.\nImage and BB centres shown", fontsize=18)
    plt.show()



def rm_ext(filepath):
    """Rm file extension"""
    x = filepath.split(".")
    x.pop()
    no_ext = ""
    for s in x:
        no_ext=no_ext+s
    return no_ext 




if __name__=="__main__":
    
    #myfile = easygui.fileopenbox(msg="Choose a beamfile", default=r"C:\pathtofiles")
    beamfile = str(easygui.fileopenbox(msg="Choose a beamfile"))
    beampath = rm_ext(beamfile)

    print("Entry spot:")
    print_arc_radial_widths( beampath, spot="Entry" )
    print_spot_diameter( beampath, spot="Entry" )
    print("Exit spot:")
    print_arc_radial_widths( beampath, spot="Exit" )
    print_spot_diameter( beampath, spot="Exit" )


    print( "Shifts in BEV coordinates: ")
    print_shifts(beampath)














