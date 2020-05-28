import json
import matplotlib.pyplot as plt
from matplotlib import cm
import numpy as np
import easygui


from fpdf import FPDF  ## limited functionality

from reportlab.pdfgen import canvas

from reportlab.lib import colors
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, TableStyle, Table, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch


###############################################
GANTRY = list( range(180,-181,-30) )
ENERGY = [245,240]+list( range(230,69,-10) )
###############################################



''' ## Temporary tolerances to be used

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
            







def summary_fpdf( shifts ):
    """Print a pdf report of the beam shift results
    """

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=14)
    pdf.cell(200,10, txt="Logos XRV-124 QA results [date]", ln=1, align="C")
    pdf.ln(20)
    pdf.set_font("Arial", size=11)
    pdf.cell(0,10,txt="Testing the text position")

    pdf.add_page()
    pdf.set_font("Arial", size=11)
    pdf.image("shifts_by_gantry.png", x=15, w=170)
    pdf.ln(5)  # move 85 down

    pdf.output("test.pdf")







def summary_reportlab( shifts ):
    """Print a pdf report of the beam shift results
    """

    doc = SimpleDocTemplate("test-124.pdf",pagesize=letter,
                            rightMargin=72,leftMargin=72,
                            topMargin=72,bottomMargin=18)
    Story=[]

    styles=getSampleStyleSheet()
    styles.add(ParagraphStyle(name='Justify', alignment=TA_JUSTIFY))
      
    title = '<font size="16"> Logos XRV-124 monthly QA results </font>'
    ##ptext = "Logos XRV-124 monthly QA results"
    Story.append(Paragraph(title, styles["Justify"]))
    Story.append(Spacer(1, 50))



    ############# TABLE OF RESULTS

    data= [['Gantry', '50% energies < 1mm', 'Less than 5 energies > 1.5mm', 'No energy > 2mm'],
     ['-180', 'pass', 'pass', 'FAIL'],
     ['-150', 'pass', 'pass', 'pass'],
     ['-120', 'FAIL', 'pass', 'pass'],
     ['-90', 'pass', 'FAIL', 'pass']]


    fails = []
    for i,row in enumerate(data):
        for j,el in enumerate(row):
            if data[i][j]=="FAIL":
                ###print(j,i)
                fails.append( (j,i) ) 



    t=Table(data)
    #t.setStyle(TableStyle([('BACKGROUND',(1,1),(-2,-2),colors.green),
    t.setStyle(TableStyle([('BACKGROUND',(0,0),(0,len(data)),colors.lightblue),
     ###('TEXTCOLOR',(0,0),(1,-1),colors.red)]))
     ('BACKGROUND', (0,0),(len(data[0]),0),colors.lightblue)]))
    # Make fails red
    for coord in fails:
        t.setStyle(TableStyle([('BACKGROUND', coord, coord, colors.lightcoral)]))     

    Story.append(t)


    ############ IMAGES WE WANT TO INCLUDE

    Story.append(PageBreak())

    im = Image("shifts_by_gantry.png", 6*inch, 5*inch)
    Story.append(im)
    Story.append(Spacer(1, 12))



    Story.append(PageBreak())
    data= [['00', '01', '02', '03', '04'],
     ['10', '11', '12', '13', '14'],
     ['20', '21', '22', '23', '24'],
     ['30', '31', '32', '33', '34']]
    t=Table(data)
    t.setStyle(TableStyle([('BACKGROUND',(1,1),(-2,-2),colors.green),
     ('TEXTCOLOR',(0,0),(1,-1),colors.red)]))
    Story.append(t)

    doc.build(Story)



    #magName = "Pythonista"
    #issueNum = 12
    #subPrice = "99.00"
    #limitedDate = "03/05/2010"
    #freeGift = "tin foil hat"
    #formatted_time = time.ctime()
    #full_name = "Mike Driscoll"
    #address_parts = ["411 State St.", "Marshalltown, IA 50158"]

#    ptext = '<font size="12">We would like to welcome you to our subscriber base for %s Magazine! \
#            You will receive %s issues at the excellent introductory price of $%s. Please respond by\
#            %s to start receiving your subscription and get the following free gift: %s.</font>' % (magName, issueNum,  subPrice,   limitedDate,freeGift)

    #ptext = '<font size="12">Thank you very much and we look forward to serving you.</font>'
    #Story.append(Paragraph(ptext, styles["Justify"]))
    #Story.append(Spacer(1, 12))
    







if __name__=="__main__":

    shifts = {}
    #with open("results_2020_0102_0001.txt") as filein:
    with open("results_shifts.txt") as filein:
        shifts = json.load(filein)

    #print_pdf_summary(shifts)
    summary_reportlab(shifts)






        
