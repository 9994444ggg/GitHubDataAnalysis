# -*- coding: utf-8 -*-
"""
Created on Fri Jan 31 15:11:32 2020

@author: pmedappa

USe graph ql and get user info 
"""


import sys
if r"C:\Users\pmedappa\Dropbox\Code\CustomLib\PooLib" not in sys.path:
    sys.path.append(r'C:\Users\pmedappa\Dropbox\Code\CustomLib\PooLib')
    print(sys.path)
from poo_ghmodules import getGitHubapi
from poo_ghmodules import ghpaginate
from poo_ghmodules import ghparse_row
from poo_ghmodules import gettoken

import math
import pandas as pd
import numpy as np
import requests

MAX_ROWS_PERWRITE = 500

DF_REPO = pd.DataFrame()
DF_COUNT = 0

LOG_CSV = r'C:\\Users\pmedappa\Dropbox\Course and Research Sharing\Research\MS Acquire Github\Data\Sponsor\Rand\UserSpon_log.csv'

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


def run_query1(row,user_xl,org_name): 
    """Get the organization details and structure ."""
    TOKEN = gettoken(r"C:\Users\pmedappa\Dropbox\Code\PW\GHtoken.txt")
    headers = {"Authorization": "Bearer "+ TOKEN } 
    query = """
             query { 
               rateLimit {
                cost
                remaining
                resetAt
              }
             organization(login: \""""+org_name+"""\") {
                name
                login
                location
                twitterUsername
                websiteUrl
                membersWithRole (first : 100 ){
                  totalCount
                  nodes {
                    login
                  }
                }
               pendingMembers(first: 100) {
                  totalCount
                  nodes {
                    login
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
        
    except:
        print("Error running graphql")
        print(req_json)
        return 404        
    try:    
        org = req_json['data']['organization']
        row = row.append(pd.Series(org['membersWithRole']['totalCount'], index = [105]))
        row = row.append(pd.Series(org['pendingMembers']['totalCount'], index= [106]))
        row = row.append(pd.Series(org['twitterUsername'], index= [107]))
    except:
        row = row.append(pd.Series("", index = [105]))
        row = row.append(pd.Series("", index= [106]))

    appendrowindf(user_xl, row)




        
def run_query2(row,user_xl,org_name): 
    """ A simple function to use requests.post to make the API call. Note the json= section."""
    TOKEN = gettoken(r"C:\Users\pmedappa\Dropbox\Code\PW\GHtoken.txt")
    headers = {"Authorization": "Bearer "+ TOKEN } 
    
    l_name = row[2]
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
        
    except:
        print("Error running graphql")
        return 404
    

    try:    
        user = req_json['data']['user']
        row[7] = user['company']
        if user['organization']:
            row[8] = user['organization']['name']
            row[9] = user['organization']['login']
        if user['organizations']:
            row[10] = user['organizations']['nodes']
        row[11] = user['email']
        row[12] = user['location']
        row[13] = user['isHireable']
    except:
        pass

    appendrowindf(user_xl, row)        

    return 0

      
    
def main():
    """Main function"""   
    global DF_REPO 
    global DF_COUNT
    r_user_xl = r'C:\Users\pmedappa\Dropbox\Data\092019 CommitInfo\Contributors_monthwise\COL_MC_RepoCommit_60000.xlsx'
    w_user_xl = r'C:\Users\pmedappa\Dropbox\Data\092019 CommitInfo\Contributors_monthwise\COL_MC_RepoCommit_UserInfo_60000.xlsx'
    user_df = pd.read_excel(r_user_xl,header= 0)
    df_test = pd.DataFrame()
    df_test.to_excel(w_user_xl, index = False) 
    
    for i,row in user_df.iterrows():
        if  ~np.isnan(row[0]):
            print("Repo ",row[0])
            org_name= str(row[2])
            run_query1(row,w_user_xl,org_name)
            
        else:
            pass
            print(row[2])
            run_query2(row,w_user_xl,org_name)
    
#
    df = pd.read_excel(w_user_xl,header= 0)
    df= df.append(DF_REPO, ignore_index = True)
    df.to_excel(w_user_xl, index = False) 
    DF_COUNT = 0
    DF_REPO = pd.DataFrame()
  
main()