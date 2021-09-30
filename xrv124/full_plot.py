import json
from math import radians

import matplotlib.pyplot as plt
from matplotlib import cm
import numpy as np
import easygui

import config


GANTRY = config.GANTRY
ENERGY = config.ENERGY


def select_file():
    msg = "File must contain a python dictionary object with:\n"
    msg+= "  KEYS:     in the form 'GA30E120' (gantry angle and energy)\n"
    msg+= "  VALUES:   as lists [xshift, yshift]"
    title = "SELECT FILE"
    if easygui.ccbox(msg, title):
        pass
    else:
        exit(0)
    return easygui.fileopenbox()


def trim_axs(axs, N):
    """
    Reduce *axs* to *N* Axes. All further Axes are removed from the figure.
    """
    axs = axs.flat
    for ax in axs[N:]:
        ax.remove()
    return axs[:N]



############### SHIFTS #################


def plot_shifts_by_gantry(results, imgname=None):
    """
    Plots showing shifts for each gantry angle
    """
    rows=4
    cols=4

    fig,axs = plt.subplots(rows,cols, figsize=(15,12), constrained_layout=True)
    axs = trim_axs(axs, len(GANTRY) )

    for ga,ax in zip(GANTRY,axs):

        colors = cm.rainbow(np.linspace(0, 1, len(ENERGY)))

        for en,c in zip(ENERGY,colors):    
            k="GA"+str(ga)+"E"+str(en)
            ax.scatter(results[k][0], results[k][1], color=c, label=str(en) )
            ax.plot( [-1.5,1.5], [0,0], linestyle=":", alpha=0.01 )
            ax.plot( [0,0], [-1.5,1.5], linestyle=":", alpha=0.01 )
        ax.set_xlim(-1.5,1.5)
        ax.set_ylim(-1.5,1.5)
        ax.set_title("GA = {}".format(str(ga)))

    handles, labels = plt.gca().get_legend_handles_labels()
    by_label = dict( zip(labels,handles) )
    fig.legend(by_label.values(), by_label.keys(), bbox_to_anchor=(0.62,0.22), ncol=3, title="Energy (MeV)" ) 
    fig.suptitle("BEV (x,y) shifts in mm", fontsize=16)
    plt.xlabel("x shift (mm)")
    plt.ylabel("y shift (mm)")
    if imgname is not None:
        fig.savefig(imgname, dpi=fig.dpi)
    else:
        plt.show()




def plot_shifts_by_energy(results, imgname=None):
    """
    Plots showing shifts for each energy
    """
    rows=4
    cols=5

    fig,axs = plt.subplots(rows,cols, figsize=(15,12), constrained_layout=True)
    axs = trim_axs(axs, len(ENERGY))

    for en,ax in zip(ENERGY,axs):

        colors = cm.rainbow(np.linspace(0, 1, len(GANTRY)))

        for ga,c in zip(GANTRY,colors):    
            k="GA"+str(ga)+"E"+str(en)
            ax.scatter(results[k][0], results[k][1], color=c, label=str(ga))
            ax.plot( [-1.5,1.5], [0,0], linestyle=":", alpha=0.01 )
            ax.plot( [0,0], [-1.5,1.5], linestyle=":", alpha=0.01 )
        ax.set_xlim(-1.5,1.5)
        ax.set_ylim(-1.5,1.5)
        ax.set_title("E = {} MeV".format(str(en)))
        
    handles, labels = plt.gca().get_legend_handles_labels()
    by_label = dict( zip(labels,handles) )
    fig.legend(by_label.values(), by_label.keys(), bbox_to_anchor=(0.97,0.23), ncol=2, title="GA (degrees)" )
    fig.suptitle("BEV (x,y) shifts in mm", fontsize=16)
    plt.xlabel("x shift (mm)")
    plt.ylabel("y shift (mm)")
    if imgname is not None:
        fig.savefig(imgname, dpi=fig.dpi)
    else:
        plt.show()




def plot_xyshifts_vs_gantry(results, imgname=None):
    """
    Plots showing x,y shifts separately vs GA for each energy
    """
    rows=4
    cols=5

    fig,axs = plt.subplots(rows,cols, figsize=(15,12), constrained_layout=True)
    axs = trim_axs(axs, len(ENERGY))

    for en,ax in zip(ENERGY,axs):

        colors = cm.rainbow(np.linspace(0, 1, len(GANTRY)))
        xshifts=[]
        yshifts=[]

        for ga,c in zip(GANTRY,colors):    
            k="GA"+str(ga)+"E"+str(en)
            #ax.scatter(results[k][0]*PIXEL_SIZE, results[k][1]*PIXEL_SIZE, color=c, label=str(ga))
            xshifts.append( results[k][0] )
            yshifts.append( results[k][1] )
        ax.set_xlim(-181,181)
        ax.set_ylim(-2,2)
        #ax.set_xlabel("GA (degree)")
        #ax.set_ylabel("Shift (mm)")
        ax.plot( GANTRY, xshifts, label="x shifts" )
        ax.plot( GANTRY, yshifts, label="y shifts" )
        ax.set_title("E = {} MeV".format(str(en)))
        
    handles, labels = plt.gca().get_legend_handles_labels()
    by_label = dict( zip(labels,handles) )
    fig.legend(by_label.values(), by_label.keys(), bbox_to_anchor=(0.92,0.2), ncol=1, title="Image axis" )
    fig.suptitle("Shifts (mm) vs GA", fontsize=16)
    plt.xlabel("GA (degree)")
    plt.ylabel("Shift (mm)")
    if imgname is not None:
        fig.savefig(imgname, dpi=fig.dpi)
    else:
        plt.show()



def plot_xyshifts_vs_energy(results, imgname=None):
    """
    Plots showing x,y shifts separately vs GA for each energy
    """
    rows=4
    cols=4

    fig,axs = plt.subplots(rows,cols, figsize=(15,12), constrained_layout=True)
    axs = trim_axs(axs, len(GANTRY))

    for ga,ax in zip(GANTRY,axs):

        colors = cm.rainbow(np.linspace(0, 1, len(ENERGY)))
        xshifts=[]
        yshifts=[]

        for en,c in zip(ENERGY,colors):    
            k="GA"+str(ga)+"E"+str(en)
            #ax.scatter(results[k][0]*PIXEL_SIZE, results[k][1]*PIXEL_SIZE, color=c, label=str(ga))
            xshifts.append( results[k][0] )
            yshifts.append( results[k][1] )
        ax.set_xlim(60,260)
        ax.set_ylim(-2,2)
        #ax.set_xlabel("GA (degree)")
        #ax.set_ylabel("Shift (mm)")
        ax.plot( ENERGY, xshifts, label="x shifts" )
        ax.plot( ENERGY, yshifts, label="y shifts" )
        ax.set_title("GA = {}".format(str(ga)))
        
    handles, labels = plt.gca().get_legend_handles_labels()
    by_label = dict( zip(labels,handles) )
    fig.legend(by_label.values(), by_label.keys(), bbox_to_anchor=(0.5,0.18), ncol=1, title="Image axis" )
    fig.suptitle("Shifts (mm) vs energy", fontsize=16)
    plt.xlabel("Energy (MeV)")
    plt.ylabel("Shift (mm)")
    if imgname is not None:
        fig.savefig(imgname, dpi=fig.dpi)
    else:
        plt.show()


def shifts_histogram(shifts, imgname=None):
    """Histogram of shifts from all spots
    
    Input: dictionary {"GA180E150":[xshift,yshift],...}
    """
    #with open(shifts22, encoding='utf-8') as F:
    #    shifts = json.loads(F.read())
    # Absolute displacement
    displacements=[]
    for key in shifts:
        xy = shifts[key]
        total_shift = (xy[0]**2 + xy[1]**2)**0.5
        ##if total_shift>0.99:
        ##    print("2D {} = {}mm".format(key,total_shift))
        displacements.append(total_shift)
    
    bins = [0+i*0.1 for i in range(25)]
    fig=plt.figure()
    plt.hist(displacements, bins=bins, align="left")
    #plt.title("Absolute spot shifts (mm)")
    plt.ylabel("Frequency")
    plt.xlabel("Shift (mm)")
    if imgname is not None:
        fig.savefig(imgname, dpi=fig.dpi)
    else:
        plt.show()
   
    
def shifts_3d_histogram(shifts_3d, imgname=None):
    """Histogram of shifts in 3D Logos coords from all spots
    
    Input: dictionary {"GA180E150":[xshift,yshift,zshift],...}
    """
    #with open(shifts_3d22, encoding='utf-8') as F:
    #    shifts_3d = json.loads(F.read())
    ## Absolute displacement
    displacements=[]
    for key in shifts_3d:
        xyz = shifts_3d[key]
        total_shift = (xyz[0]**2 + xyz[1]**2 + xyz[2]**2)**0.5
        ##if total_shift>0.99:
        ##    print("3D {} = {}mm".format(key,total_shift))
        displacements.append(total_shift)
    
    bins = [0+i*0.1 for i in range(25)]
    fig=plt.figure()
    plt.hist(displacements, bins=bins, align="left")
    plt.title("Absolute shifts in 3D Logos coords (mm)")
    plt.ylabel("Frequency")
    plt.xlabel("Shift (mm)")
    if imgname is not None:
        fig.savefig(imgname, dpi=fig.dpi)
    else:
        plt.show()     
        
        
        
def shifts_polar(shifts, imgname=None):
    """Polar plot of shifts from all spots
    
    Input: dictionary {"GA180E150":[xshift,yshift],...}
    """
    #ENERGY = [245,240]+list( range(230,69,-10) )
    #with open(shifts22, encoding='utf-8') as F:
    #    shifts = json.loads(F.read())  
           
    # Absolute displacement
    displacements = {}
    for key in shifts:
        xy = shifts[key]
        total_shift = (xy[0]**2 + xy[1]**2)**0.5
        displacements[key] = total_shift
    
    colors = cm.rainbow(np.linspace(0, 1, len(ENERGY)))
    ga=[]
    en=[]
    d=[]
    cols=[]   
    for key in displacements:
        angle = int(key.split("GA")[1].split("E")[0])   
        ga.append( radians(angle) )
        energy = int(key.split("E")[1])
        en.append(energy)
        cols.append( colors[ENERGY.index(energy)] )        
        d.append(displacements[key])    

    fig, ax = plt.subplots(subplot_kw={'projection': 'polar'})   
    ax.set_rmax(2)
    ax.set_rticks([0.5, 1.0, 1.5, 2.0, 2.5])  # Radial ticks
    ax.set_rlabel_position(80)  # Move radial labels away from plotted line
    ax.grid(True)
    ax.set_theta_zero_location("N")
    ax.set_theta_direction(-1)  
    for angle,energy,dist,c in zip(ga,en,d,cols):
        ax.plot(angle,dist,color=c,marker='o',label=str(energy))
    plt.title("Absolute spot shifts (mm)\n")
    
    # Set legend with energy
    handles, labels = plt.gca().get_legend_handles_labels()
    by_label = dict( zip(labels,handles) )
    fig.legend(by_label.values(), by_label.keys(), bbox_to_anchor=(1.02,0.95),ncol=1, title="Energy (MeV)", frameon=False ) 
    #fig.legend(by_label.values(), by_label.keys(), bbox_to_anchor=(0.175,0.95),ncol=1, title="Energy (MeV)") 

    
    if imgname is not None:
        fig.savefig(imgname, dpi=fig.dpi) #, bbox_inches='tight'
    else:
        plt.show()




################ SPOT SIZES ######################

def plot_spot_diameters_by_gantry(results, imgname=None):
    """
    Plots showing spot size vs energy at each gantry angle
    """
    rows=4
    cols=4

    fig,axs = plt.subplots(rows,cols, figsize=(15,12), constrained_layout=True)
    axs = trim_axs(axs, len(GANTRY) )

    for ga,ax in zip(GANTRY,axs):

        colors = cm.rainbow(np.linspace(0, 1, len(ENERGY)))

        for en,c in zip(ENERGY,colors):    
            k="GA"+str(ga)+"E"+str(en)
            ax.scatter(en, results[k], color=c, label=str(en) )
        ax.set_ylim(4,15) # tune this to better see the oscilatory nature
        ax.set_title("GA = {}".format(str(ga)))

    handles, labels = plt.gca().get_legend_handles_labels()
    by_label = dict( zip(labels,handles) )
    fig.legend(by_label.values(), by_label.keys(), bbox_to_anchor=(0.62,0.22), ncol=3, title="Energy (MeV)" ) 
    fig.suptitle("Spot diameter (mm) vs energy", fontsize=16)
    plt.xlabel("Energy")
    plt.ylabel("Diameter (mm)")
    if imgname is not None:
        fig.savefig(imgname, dpi=fig.dpi)
    else:
        plt.show()


def plot_spot_diameters_by_energy(results, imgname=None):
    """
    Plots showing spot diameters vs GA at each beam energy
    """
    rows=4
    cols=5

    fig,axs = plt.subplots(rows,cols, figsize=(15,12), constrained_layout=True)
    axs = trim_axs(axs, len(ENERGY) )

    for en,ax in zip(ENERGY,axs):

        colors = cm.rainbow(np.linspace(0, 1, len(GANTRY)))

        for ga,c in zip(GANTRY,colors):    
            k="GA"+str(ga)+"E"+str(en)
            ax.scatter(ga, results[k], color=c, label=str(ga) )
        ax.set_xlim(-200,200)
        ax.set_ylim(4,15) #use this to better see the oscilatory nature
        ax.set_title("E = {} MeV".format(str(en)))

    handles, labels = plt.gca().get_legend_handles_labels()
    by_label = dict( zip(labels,handles) )
    fig.legend(by_label.values(), by_label.keys(), bbox_to_anchor=(0.98,0.22), ncol=2, title="GA (degrees)" ) 
    fig.suptitle("Spot diameter (mm) vs GA", fontsize=16)
    plt.xlabel("Gantry angle)")
    plt.ylabel("Diameter (mm)")
    if imgname is not None:
        fig.savefig(imgname, dpi=fig.dpi)
    else:
        plt.show()




############### SPOT SIGMAS X,Y #####################

def plot_spot_sigmas(results, imgname=None, arc_radial=False):
    """Plot spot sigmas (x and y) for either SPOT or IMAGE xcoord systems
    """
    rows=4
    cols=5

    fig,axs = plt.subplots(rows,cols, figsize=(15,12), constrained_layout=True)
    axs = trim_axs(axs, len(ENERGY) )

    for en,ax in zip(ENERGY,axs):  
        for ga in GANTRY:    
            k="GA"+str(ga)+"E"+str(en)
            xlabel="x_sigma"
            ylabel="y_sigma"
            if arc_radial:
                xlabel="arc width"
                ylabel="radial width"
            ax.scatter(ga, results[k][0], color="red", label=xlabel, alpha=0.7 )
            ax.scatter(ga, results[k][1], color="blue", label=ylabel, alpha=0.7 )

        ax.set_xlim(-200,200)
        ax.set_ylim(2,8) #use this to better see the oscilatory nature
        if arc_radial:
            ax.set_ylim(4,15.8) ## diff lims if plotting arc & radial widths
        ax.set_title("E = {} MeV".format(str(en)))

    handles, labels = plt.gca().get_legend_handles_labels()
    by_label = dict( zip(labels,handles) )
    fig.legend(by_label.values(), by_label.keys(), bbox_to_anchor=(0.96,0.22), ncol=1, title="Axis" )
    if arc_radial:
        fig.suptitle("Spot arc/radial widths vs GA", fontsize=16)
    else:
        fig.suptitle("Spot sigmas (mm) vs GA", fontsize=16)
    plt.xlabel("Gantry angle)")
    plt.ylabel("Diameter (mm)")
    if imgname is not None:
        fig.savefig(imgname, dpi=fig.dpi)
    else:
        plt.show()








################ MAIN #################


def main():


    resultsfile = select_file()    

    results={}
    #with open("results_2020_0102_0001.txt") as filein:
    with open(resultsfile) as filein:
        results = json.load(filein)


    # Note that the different plots require different
    # formating of "results". Need to select correct file.

    # SHIFT PLOTS
    # 2D plot of shifts (x,y) grouped by GA
    plot_shifts_by_gantry(results, "test.png")
    '''# 2D plot of shifts (x,y) grouped by ENERGY
    plot_shifts_by_energy(results)
    # x & y shifts plotted separately vs GA (for each E)
    plot_xyshifts_vs_gantry(results)
    # x & y shifts plotted separately vs E (for each GA)
    plot_xyshifts_vs_energy(results)'''


    ##SPOT SIZE PLOTS
    #plot_spot_sizes_by_gantry(results)
    #plot_spot_sizes_by_energy(results)

    #plot_spot_sigmas(results)



if __name__=="__main__":
    main()

    
        
