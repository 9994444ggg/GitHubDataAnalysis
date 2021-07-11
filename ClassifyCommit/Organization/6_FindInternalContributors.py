# -*- coding: utf-8 -*-
"""
Created on Mon Mar  1 13:35:31 2021

@author: pmedappa

Find if contributors is internal or external . Ensure contributors are sorted in ascending ot their date to use rule 3.

rule 1: If org matches the org listed (Company, Orgnization affiliations)
rule 2: First day committers
rule 3: Org affiliation of committers identified from rulw 1 and 2

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
    if  pd.notnull(row['contributor_org_login']): # rule 1
        org.append(row['contributor_org_login'].lower())        
    if pd.notnull(row['contributor_company']):
        company = re.sub(r"[-()\"#/@;:<>{}`+=~|.!?, ]", "", row['contributor_company'])
        company = company.lower()
        org.append(company)
    if pd.notnull(row['contributor_organizations']):
        for o in ast.literal_eval(row['contributor_organizations']):
            o1 =  re.sub(r"[-()\"#/@;:<>{}`+=~|.!?, ]", "", o['login'])
            o1 = o1.lower()
            org.append(o1)    
    return org


def rules(row,w_user_xl,date,fc_date, o_name):
    """ rule 1: If org matches the org owner listed = 1 """
    """ rule 2: If org name matches any of the organizations found for the contributor"""
    """ rule 3: First day committers = 2"""
    """ rule 4: First committers matched by date = 3 """
    """ rule 5: Org affiliation linked to rule 1-3 = 4. Note: it is dependent on the listed order of committers """
    """ rule 6: org name is in the substring of any of the organization names """
    global ORG_NAME
    
    org_name = list()
    org_name = get_orgname(row)
    org_a = set(org_name)
    org_b = set(ORG_NAME)
    row['internal_contributor'] = 0
    if  pd.notnull(row['contributor_org_login']) : # rule 1
        row['internal_contributor'] = 1       
        # add company
    elif (o_name in org_name):
        row['internal_contributor'] = 1
    elif row['contributor_start_date'][:10] == date[:10]: #rule 2
        row['internal_contributor'] = 2 
    elif row['contributor_start_date'][:10] == fc_date[:10]:
        row['internal_contributor'] = 3 
        # adding first commiter date
    elif(org_a & org_b):
        row['internal_contributor'] = 4
    else:
        for o in org_name:
            if str(o_name) in str(o):
                row['internal_contributor'] = 5
        

    
    row['all_organizations'] = org_name
    if row['internal_contributor'] == 1 or row['internal_contributor'] == 2 or row['internal_contributor'] == 3 or row['internal_contributor'] == 5:
        for o in org_name:
            ORG_NAME.append(o)
        
    appendrowindf(w_user_xl, row)     

 

def main():
    """Main function"""   
    global DF_REPO 
    global DF_COUNT
    global ORG_NAME
    r_user_xl = r'C:\Users\pmedappa\Dropbox\Data\092019 CommitInfo\Organization_Specific\microsoft\Classified\int_org_col_classified_microsoft_commit_EMPTY.xlsx'
    w_user_xl = r'C:\Users\pmedappa\Dropbox\Data\092019 CommitInfo\Organization_Specific\microsoft\Classified\int2_org_col_classified_microsoft_commit_EMPTY.xlsx'
    user_df = pd.read_excel(r_user_xl,header= 0)
    df_test = pd.DataFrame()
    df_test.to_excel(w_user_xl, index = False) 

    first_c = 0
    for i,row in user_df.iterrows():        
        if  pd.notnull(row['repo_name']):
            print("Repo: ",row['repo_name']," Owner: ",row['org_login'])
            date = row['repo_createdAt']
            o_name= str(row['org_login'])
            ORG_NAME = list()
                
            appendrowindf(w_user_xl, row)    
            first_c = 1
        else:
            if first_c == 1:
                fc_date =  row['contributor_start_date'][:10]
                first_c = 0
            rules(row,w_user_xl,date,fc_date,o_name.lower())
            
    df = pd.read_excel(w_user_xl,header= 0)
    df= df.append(DF_REPO, ignore_index = True)
    df.to_excel(w_user_xl, index = False) 
    DF_COUNT = 0
    DF_REPO = pd.DataFrame()
  
main()