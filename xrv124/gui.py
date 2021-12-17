# -*- coding: utf-8 -*-
"""
Created on Tue Oct 19 11:56:15 2021
@author: SCOURT01

GUI to select data directory, output destination and Gantry
"""

import PySimpleGUI as sg
import config


GANTRY_NAMES = config.GANTRY_NAMES
GANTRY_ANGLE_OPTIONS = config.GANTRY_ANGLE_OPTIONS
ENERGIES = config.ENERGIES


def gui():
    """GUI returns data location, gantry and save location as dict
    
    Keys for returned dict: datadir, gantry, operator 1, operator 2, outputdir
    as well as optional gantry angle and energy lists from second tab
    """
    
    off = 14

    sg.theme('BlueMono')        
    tab1_layout = [
        [sg.Text('Choose data folder, gantry and save location', size=(45,2))],
        [sg.Text('Data folder', size=(off, 1)), sg.In(key="datadir"), sg.FolderBrowse()],
        [sg.Text('Gantry', size=(off, 1)), sg.Combo(GANTRY_NAMES, size=(14,4),key="gantry")],
        [sg.Text('Operator 1', size=(off, 1)), sg.In(key="op1", size=(5,1)) , sg.Text('      Operator 2', size=(12, 1)), sg.In(key="op2",size=(5,1))],
        [sg.Text('Save location', size=(off, 1)), sg.In(key="outputdir"), sg.FolderBrowse()],
        [sg.Text('', size=(off, 1)) ],
        [sg.Text('',size=(25,1)),sg.Submit(), sg.Cancel()],
        [sg.Text('Optional comment', size=(off, 1)), sg.In(key="comment")],
        [sg.Text('', size=(off, 1)) ]
    ]
    
    
    tab2_layout = [
        [sg.Text('', size=(65,1))],
        [sg.Text('Define order of gantry angles and energies acquired', size=(50,1))],      
        [sg.Text('Separate entries with a comma; integers only', size=(50,2))],
        [sg.Text('Gantry angles', size=(12, 1)), 
           sg.Combo(GANTRY_ANGLE_OPTIONS, key="angles", default_value=GANTRY_ANGLE_OPTIONS[0], size=(50,1)) ],
        [sg.Text('Energies (MeV)', size=(12, 1)), sg.In(ENERGIES, key="energies", size=(50,1)) ],
        [sg.Text('', size=(15, 2)) ],
        [sg.Text('',size=(20,1)),sg.Submit(), sg.Cancel()]           
    ]

    
    layout = [[sg.TabGroup( [
                 [sg.Tab(' Data ', tab1_layout), 
                  sg.Tab('GAs and energies', tab2_layout, tooltip='Beam data') ]  ])
             ]]
   

    window = sg.Window('XRV-124 Monthly QA Analysis', layout)
    event, values = window.read()
    window.close() 
    return values
        



if __name__=="__main__":
    vals = gui()
    print( vals["datadir"] )
    print( vals["gantry"] )
    print( vals["outputdir"] )
    print( vals["op1"])
    print( vals["op2"])
    print( vals["energies"] )
    print( vals["angles"] )
    print( vals["comment"] )
    #print( vals["op2"]=="" )
    #print( values )