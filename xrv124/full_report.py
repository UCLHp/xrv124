import json

from reportlab.lib import colors
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, TableStyle, Table, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

import config

GANTRY = config.GANTRY
ENERGY = config.ENERGY



''' ## Temporary tolerances to be used

Action/Suspension limits:
Action limit: 		>1.0mm for at least 50% of energies for any given gantry angle;
			>1.5mm for at least 5 energies at any gantry angle;
			>2.0mm for any energy at any gantry angle.
Suspension limit:	>2.5mm for any energy at any gantry angle.
'''



# PyFPDF: https://www.blog.pythonlibrary.org/2018/06/05/creating-pdfs-with-pyfpdf-and-python/
# Interactive PDFs with ReportLab: https://www.blog.pythonlibrary.org/2018/05/29/creating-interactive-pdf-forms-in-reportlab-with-python/
# ReportLab user guide: https://www.reportlab.com/docs/reportlab-userguide.pdf



def get_total_displacement( shifts ):
    """Convert x,y shifts to total displacement"""
    displacements = {}
    for key in shifts:
        xy = shifts[key]
        total_shift = (xy[0]**2 + xy[1]**2)**0.5
        displacements[key] = total_shift

    return displacements




def get_table_data(displacements):
    """Method taking dicitonary of beam (GAxEy) and total displacement
    and formatting it for ReportLab PDF table"""
    
    data = []

    # Table header
    line_1 = ['Gantry', '50% energies < 1mm', 'Less than 5 energies > 1.5mm', 'No energy > 2mm']
    data.append(line_1)

    for ga in GANTRY:
        # Store beams that were out of certain tolerances
        gt_1 = []
        gt_1p5 = []
        gt_2 = []
        gt_2p5 = []

        ## Format of data lines (row tables) is [GA, tol 1 pass/fail, tol 2 tol 3]
        data_line = ["NONE_ERROR"]*4   
        data_line[0] = str(ga)

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
            print("WARNING: Suspension limit exceeded; beams {}\n".format( list(gt_2p5.keys()) ))
            #print(gt_2p5)
        if len(gt_2)>0:
            #print("WARNING: 2mm Action limit exceeded for GA={}\n".format(ga))
            #print( gt_2 + gt_2p5 )
            data_line[3] = "FAIL"
        else:
            data_line[3] = "pass"
        if len(gt_1p5)+len(gt_2) >= 5:
            #print("WARNING: 1.5mm Action Limit exceeded for GA={}\n".format(ga))
            #print( gt_1p5 + gt_2 + gt_2p5 )
            data_line[2] = "FAIL"
        else:
            data_line[2] = "pass"
        if len(gt_1)+len(gt_1p5)+len(gt_2) >= len(ENERGY)/2.0:
            #print("WARNING: 1.0mm Action Limit exceeded for GA={}\n".format(ga))
            #print( gt_1 + gt_1p5 + gt_2 + gt_2p5 )
            data_line[1]  = "FAIL"
        else:
            data_line[1] = "pass"
        
        data.append( data_line )

    return data




def summary_reportlab( shifts, images=None, output=None ):
    """Print a pdf report of the beam shift results

    'shifts' input is a dictionary in form { "GA0E240":[xshift, yshift] }
    where x and y are in the image (hence BEV) coordinate system
    """

    # Check if single image or list is provided
    images_to_plot = []
    if images is None:
        images_to_plot = []
    elif type(images) is list:
        images_to_plot = images
    elif type(images) is str:
        images_to_plot.append(images)
    else:
        print("Provide a link to image file or list of links for summary report")

    if output is None:
        output = "xrv124 summary.pdf"
    
        

    # Convert x,y shifts to total displacement
    displacements = get_total_displacement( shifts )

    # Data formatted for PDF table
    table_data = get_table_data(displacements)


    # Set up document
    doc = SimpleDocTemplate(output,pagesize=letter,
                            rightMargin=72,leftMargin=72,
                            topMargin=72,bottomMargin=18)

    # Story is a list of "Flowables" that will be converted into the PDF
    Story=[]

    # Make some paragraph styles we can call later
    styles=getSampleStyleSheet()
    styles.add(ParagraphStyle(name='Justify', alignment=TA_JUSTIFY))
    styles.add(ParagraphStyle(name='Indent', alignment=TA_JUSTIFY, leftIndent=20))
    styles.add(ParagraphStyle(name='Underline', alignment=TA_JUSTIFY, underlineWidth=1))
      
    title = '<font size="15"><u> Logos XRV-124 monthly QA results </u></font>'
    Story.append(Paragraph(title, styles["Justify"]))
    Story.append(Spacer(1, 50))


    ############# TABLE OF RESULTS
    Story.append(Paragraph("Summary of beam shift results:", styles["Underline"]))
    Story.append(Spacer(1, 20))

    #### Insert a FAIL manually
    ###table_data[5][2] = "FAIL"

    # Get table coordinates of FAIL cells
    fails = []
    for i,row in enumerate(table_data):
        for j,el in enumerate(row):
            if table_data[i][j]=="FAIL":
                ###print(j,i)
                fails.append( (j,i) ) 

    t=Table( table_data )
    t.setStyle(TableStyle([('BACKGROUND',(0,0),(0,len(table_data)),colors.lightblue),
     ('BACKGROUND', (0,0),(len(table_data[0]),0),colors.lightblue)]))
    # Make fails red
    for coord in fails:
        t.setStyle(TableStyle([('BACKGROUND', coord, coord, colors.lightcoral)]))     

    Story.append(t)


    ########## LIST all beams with displacements > 1, 1.5 and 2mm
    beams_gt_1mm = {}
    beams_gt_1pt5mm = {}
    beams_gt_2mm = {}

    for key in displacements:
        ga = str(key.split("GA")[1].split("E")[0])
        en = key.split("E")[1]+" MeV"
        if displacements[key] > 2.0:
            # Add new element of to existing list
            if ga in beams_gt_2mm:
                beams_gt_2mm[ga] = beams_gt_2mm[ga] + [en]
            else:
                beams_gt_2mm[ga] = [en]
        elif displacements[key] > 1.5:
            if ga in beams_gt_1pt5mm:
                beams_gt_1pt5mm[ga] = beams_gt_1pt5mm[ga] + [en]
            else:
                beams_gt_1pt5mm[ga] = [en]
        if displacements[key] > 1:
            if ga in beams_gt_1mm:
                beams_gt_1mm[ga] = beams_gt_1mm[ga] + [en]
            else:
                beams_gt_1mm[ga] = [en]


    if len(beams_gt_1mm)>0:
        Story.append(Spacer(1, 40))
        Story.append(Paragraph( "List of beams with displacements > 1 mm:", styles["Justify"]))             
        for ga in beams_gt_1mm:
            p = "GA {}: {}".format(ga, beams_gt_1mm[ga])
            Story.append(Paragraph( p, styles["Indent"]))             
    if len(beams_gt_1pt5mm)>0:
        Story.append(Spacer(1, 40))
        Story.append(Paragraph( "List of beams with displacements > 1.5 mm:", styles["Justify"]))             
        for ga in beams_gt_1pt5mm:
            p = "GA {}: {}".format(ga, beams_gt_1pt5mm[ga])
            Story.append(Paragraph( p, styles["Indent"]))        
    if len(beams_gt_2mm)>0:
        Story.append(Spacer(1, 40))
        Story.append(Paragraph( "List of beams with displacements > 2 mm:", styles["Justify"]))             
        for ga in beams_gt_2mm:
            p = "GA {}: {}".format(ga, beams_gt_2mm[ga])
            Story.append(Paragraph( p, styles["Indent"]))
    Story.append(Spacer(1, 20))



    ############ IMAGES we want to include
    for img in images_to_plot:
        Story.append(PageBreak())
        #Story.append(Paragraph( "Spot shifts grouped by gantry angle:", styles["Justify"]))
        Story.append(Spacer(1, 20))           
        im = Image(img, 7*inch, 5.5*inch)
        Story.append(im)



    ########## COMBINE ALL ELEMENTS OF Story into document
    doc.build(Story)








if __name__=="__main__":

    shifts = {}
    #with open("results_2020_0102_0001.txt") as filein:
    with open("results_shifts.txt") as filein:
        shifts = json.load(filein)

    #print_pdf_summary(shifts)
    ##summary_reportlab(shifts, output="output2.pdf")
    summary_reportlab(shifts, images=["shifts_by_gantry.png","shifts_by_energy.png"], output="output1.pdf")






        
