# -*- coding: utf-8 -*-
"""
Created on Fri Jan 31 15:11:32 2020

@author: pmedappa

Use graph ql and get user info for the contributors identified for a project
"""


import sys
if r"C:\Users\pmedappa\Dropbox\Code\CustomLib\PooLib" not in sys.path:
    sys.path.append(r'C:\Users\pmedappa\Dropbox\Code\CustomLib\PooLib')
    print(sys.path)
from poo_ghmodules import getGitHubapi
from poo_ghmodules import ghpaginate
from poo_ghmodules import ghparse_row
from poo_ghmodules import gettoken
from time import sleep

import math
import pandas as pd
import numpy as np
import requests

MAX_ROWS_PERWRITE = 5000

DF_REPO = pd.DataFrame()
DF_COUNT = 0

LOG_CSV = r'C:\Users\pmedappa\Dropbox\Data\092019 CommitInfo\Organization_Specific\microsoft\Classified\UserSpon_log.csv'

def appendrowindf(user_xl, row, df_flag = 0):
    """This code appends a row into the dataframe and returns the updated dataframe"""
    global DF_REPO 
    global DF_COUNT
        
    # note there is an issue when shape is used for series and df. 
    if df_flag == 0:
        DF_REPO= DF_REPO.append(pd.DataFrame(row).T, ignore_index = True)
        DF_COUNT = DF_COUNT + 1 # use row.shape[0] for dataframe
    else:
        # row = row.reset_index(drop=True)
        DF_REPO= DF_REPO.append(row, ignore_index = True)
        DF_COUNT = DF_COUNT + row.shape[0]
        
    if DF_COUNT >= MAX_ROWS_PERWRITE :
        df = pd.read_excel(user_xl,header= 0)
        df= df.append(DF_REPO, ignore_index = True)
        writer = pd.ExcelWriter(user_xl,options={'strings_to_urls': False})
        df.to_excel(writer , index = False) 
        writer.close()
        DF_COUNT = 0
        DF_REPO = pd.DataFrame()




        
def run_query2(row,user_xl,org_name): 
    """ A simple function to use requests.post to make the API call. Note the json= section."""
    TOKEN = gettoken(r"C:\Users\pmedappa\Dropbox\Code\PW\GHtoken.txt")
    headers = {"Authorization": "Bearer "+ TOKEN } 
    
    l_name = str(row['contributor_login'])
    temp_df = pd.DataFrame()


    query = """
             query { 
               rateLimit {
                cost
                remaining
                resetAt
              }

              user(login:\""""+l_name+"""\") { 
                login
                name
                bio
                location
                company
                email
                twitterUsername

                isHireable
                isSiteAdmin
                organization (login:\""""+org_name+"""\"){
                    name
                    login
                    location
                    twitterUsername
                    websiteUrl      
                }
                organizations(first :100) {
                  totalCount
                  nodes{
                    name
                    login
                    location
                    twitterUsername
                    websiteUrl
                  }
                }
              }
            }
            """
        
    body = {
            "query": query,
                }
    try:
        request = requests.post('https://api.github.com/graphql', json=body, headers=headers)
        req_json = request.json()

        print(req_json['data']['rateLimit']['remaining'])
        if int(req_json['data']['rateLimit']['remaining']) <100:
            print("sleeping ........")
            sleep(60)
        
    except:
        print("Error running graphql")
        return 404
    

    try:    
        user = req_json['data']['user']
        row['contributor_company'] = user['company']
        if user['organization']:
            row['contributor_org_name'] = user['organization']['name']
            row['contributor_org_login'] = user['organization']['login']
        if user['organizations']:
            row['contributor_organizations'] = user['organizations']['nodes']
        row['contributor_email'] = user['email']
        row['contributor_location'] = user['location']
        row['contributor_ishireable'] = user['isHireable']
    except:
        pass

    appendrowindf(user_xl, row)        

    return 0

      
    
def main():
    """Main function"""   
    global DF_REPO 
    global DF_COUNT
    r_user_xl = r'C:\Users\pmedappa\Dropbox\Data\092019 CommitInfo\Organization_Specific\microsoft\Classified\col_classified_microsoft_commit_6_2.xlsx'
    w_user_xl = r'C:\Users\pmedappa\Dropbox\Data\092019 CommitInfo\Organization_Specific\microsoft\Classified\org_col_classified_microsoft_commit_6_2.xlsx'
    user_df = pd.read_excel(r_user_xl,header= 0)
    df_test = pd.DataFrame()
    df_test.to_excel(w_user_xl, index = False) 
    
    for i,row in user_df.iterrows():
        if  pd.notnull(row['repo_name']):
            print("Repo ",row['repo_name'])
            org_name= str(row["org_login"])
            print(org_name)
            appendrowindf(w_user_xl, row)            
        else:
            run_query2(row,w_user_xl,org_name)
    
#
    df = pd.read_excel(w_user_xl,header= 0)
    df= df.append(DF_REPO, ignore_index = True)
    df.to_excel(w_user_xl, index = False) 
    DF_COUNT = 0
    DF_REPO = pd.DataFrame()
  
main()