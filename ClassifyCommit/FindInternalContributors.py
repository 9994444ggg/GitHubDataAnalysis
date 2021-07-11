# -*- coding: utf-8 -*-
"""
Created on Mon Mar  1 13:35:31 2021

@author: pmedappa

Find if contributors is internal or external 

rule 1: If org matches the org listed
rule 2: First day committers
rule 3: Org affiliation of first day committers ??
rule 4: Sounds like
"""
import pandas as pd
import numpy as np
import json
import ast 
import re

MAX_ROWS_PERWRITE = 1000

DF_REPO = pd.DataFrame()
DF_COUNT = 0
ORG_NAME = list()

LOG_CSV = r'C:\Users\pmedappa\Dropbox\Data\092019 CommitInfo\Contributors_monthwise\UserSpon_log.csv'

def appendrowindf(user_xl, row):
    """This code appends a row into the dataframe and returns the updated dataframe"""
    global DF_REPO 
    global DF_COUNT
    DF_REPO= DF_REPO.append(row, ignore_index = True)
    # note there is an issue when shape is used for series and df. 
    DF_COUNT = DF_COUNT + 1 # use row.shape[0] for dataframe
    if DF_COUNT >= MAX_ROWS_PERWRITE :
        df = pd.read_excel(user_xl,header= 0)
        df= df.append(DF_REPO, ignore_index = True)
        df.to_excel(user_xl, index = False) 
        DF_COUNT = 0
        DF_REPO = pd.DataFrame()
    

def get_orgname(row):
    """Get the org name associated with an internal user """
    org = list()
    if  pd.notnull(row[9]): # rule 1
        org.append(row[9].lower())        
    if pd.notnull(row[7]):
        company = re.sub(r"[-()\"#/@;:<>{}`+=~|.!?, ]", "", row[7])
        company = company.lower()
        org.append(company)
    if pd.notnull(row[10]):
        for o in ast.literal_eval(row[10]):
            o1 =  re.sub(r"[-()\"#/@;:<>{}`+=~|.!?, ]", "", o['login'])
            o1 = o1.lower()
            org.append(o1)    
    return org


def rules(row,w_user_xl,date,fc_date, o_name):
    """ rule 1: If org matches the org owner listed = 1 """
    """ rule 2: First day committers = 2"""
    """ rule 3: First committers matched by date = 3 """
    """ rule 4: Org affiliation linked to rule 1-3 = 4. Note: it is dependent on the listed order of committers """
    global ORG_NAME
    org_name = list()
    org_name = get_orgname(row)
    if  pd.notnull(row[9]): # rule 1
        row[14] = 1       
        # add company
    elif row[5][:10] == date[:10]: #rule 2
        row[14] = 2 
    elif row[5][:10] == fc_date[:10]:
        row[14] = 3 
        # adding first commiter date 
    else:
        org_a = set(org_name)
        org_b = set(ORG_NAME)
        if o_name in org_name: #rule 1 check if any of the owner names matched the actual owner name    
            row[14] = 1
        elif (org_a & org_b): #rule 3.
            row[14] = 4
        else:
            row[14] = 0

    
    row[15] = org_name
    if row[14] == 1 or row[14] == 2 or row[14] == 3 :
        for o in org_name:
            ORG_NAME.append(o)
        
    appendrowindf(w_user_xl, row)     

 

def main():
    """Main function"""   
    global DF_REPO 
    global DF_COUNT
    global ORG_NAME
    r_user_xl = r'C:\Users\pmedappa\Dropbox\Data\092019 CommitInfo\Contributors_monthwise\COL_MC_RepoCommit_UserInfo.xlsx'
    w_user_xl = r'C:\Users\pmedappa\Dropbox\Data\092019 CommitInfo\Contributors_monthwise\COL_MC_RepoCommit_UserInfo_Ext.xlsx'
    user_df = pd.read_excel(r_user_xl,header= 0)
    df_test = pd.DataFrame()
    df_test.to_excel(w_user_xl, index = False) 
    u_flag = 0
    first_c = 0
    for i,row in user_df.iterrows():        
        if  ~np.isnan(row[0]):
            print("Repo: ",row[0]," Owner: ",row[2]," Type: ",row[3])
            date = row[5]
            o_name= str(row[2])
            ORG_NAME = list()
            if row[3] == "User":
                u_flag = 1
            else: 
                u_flag = 0                
                appendrowindf(w_user_xl, row)    
                first_c = 1
        else:
            if u_flag == 1:
                continue
            if first_c == 1:
                fc_date =  row[5][:10]
                first_c = 0
            rules(row,w_user_xl,date,fc_date,o_name.lower())
            
    df = pd.read_excel(w_user_xl,header= 0)
    df= df.append(DF_REPO, ignore_index = True)
    df.to_excel(w_user_xl, index = False) 
    DF_COUNT = 0
    DF_REPO = pd.DataFrame()
  
main()