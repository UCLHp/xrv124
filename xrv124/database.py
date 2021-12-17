# -*- coding: utf-8 -*-
"""
Created on Wed Dec 15 09:19:36 2021
@author: Steven Court

Interaction with QA database
"""

import pypyodbc
from pypyodbc import IntegrityError
import pandas as pd
import easygui as eg

import config

# NOTE: Cols with spaces or hyphens in name must be surrounded by square brackets

DB_PATH = config.PATH_TO_DB
SESSION_TABLE = config.SESSION_TABLE 
RESULTS_TABLE = config.RESULTS_TABLE
PASSWORD = config.PASSWORD



def write_session_data(conn,mach_name,adate,op1,op2,comment):
    """Write to session table; return True if successful"""
        
    cursor = conn.cursor()   
    sql = '''
            INSERT INTO "%s" (MachineName, ADate, [Operator 1], [Operator 2], Comments)
            VALUES (?, ?, ?, ?, ?)
          '''%(SESSION_TABLE)
    data = [mach_name,adate,op1,op2,comment] 
    
    try:
        cursor.execute(sql, data )
        conn.commit()
        return True
        
    except IntegrityError:
        eg.msgbox("Entry already exists, nothing writen to database","WARNING")
        print("Entry already exists, nothing writen to database")
        return False
        
    

def write_results_data(conn,df):
    """Write results to QA database"""    

    cursor = conn.cursor()   
    sql = '''
            INSERT INTO "%s" (ADate, MachineName, GA, Energy,\
            [x-offset], [y-offset], Diameter) 
            VALUES (?, ?, ?, ?, ?, ?, ?)  
            '''%(RESULTS_TABLE)

    for i,row in df.iterrows():
        data = [ row["ADate"], row["MachineName"], row["GA"], row["Energy"],
                 row["x-offset"], row["y-offset"], row["Diameter"] ]
        cursor.execute(sql, data)
        
    conn.commit()


 
def write_to_db(df,comment=""):
    
    conn=None  
    try:
        new_connection = 'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=%s;PWD=%s'%(DB_PATH,PASSWORD)    
        conn = pypyodbc.connect(new_connection)                 
    except:
        eg.msgbox("Could not connect to database; nothing written","WARNING")
        print("Could not connect to database; nothing written")
        
    
    if isinstance(conn,pypyodbc.Connection):
        session_written = write_session_data(conn,df["MachineName"][0],
                                df["ADate"][0], df["Operator 1"][0],
                                df["Operator 2"][0], comment )
        if session_written:
            write_results_data(conn,df)
        
 
    

def main():
    df = pd.read_csv(r"C:Desktop\db_results.csv")
    write_to_db(df)    
    
    
    
if __name__=="__main__":
    main()