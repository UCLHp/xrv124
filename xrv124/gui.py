# -*- coding: utf-8 -*-
"""
Created on Tue Oct 19 11:56:15 2021
@author: SCOURT01

GUI to select data directory, output destination and Gantry
"""

import PySimpleGUI as sg
import config


GANTRY_NAMES = config.GANTRY_NAMES



def gui():
    """GUI returns data location, gantry and save location as dict
    
    Keys for returned dict: datadir, gantry, outputdir
    """

    sg.theme('BlueMono')        
    layout = [
        [sg.Text('Choose data folder, gantry and save location', size=(45,2))],
        [sg.Text('Data folder', size=(10, 1)), sg.In(key="datadir"), sg.FolderBrowse()],
        [sg.Text('Gantry', size=(10, 1)), sg.Combo(GANTRY_NAMES, size=(20,4),key="gantry")],
        [sg.Text('Save location', size=(10, 1)), sg.In(key="outputdir"), sg.FolderBrowse()],
        [sg.Text('', size=(15, 1)) ],
        [sg.Text('',size=(20,1)),sg.Submit(), sg.Cancel()]
    ]
    window = sg.Window('XRV-124 Monthly QA Analysis', layout)
    event, values = window.read()
    window.close() 
    return values
        





if __name__=="__main__":
    vals = gui()
    print( vals["datadir"] )
    print( vals["gantry"] )
    print( vals["outputdir"] )
    #print( values )