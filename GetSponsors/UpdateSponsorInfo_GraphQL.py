# -*- coding: utf-8 -*-
"""
Created on Wed Sep 11 17:04:10 2019

@author: pmedappa
"""

import sys
if r"C:\Users\pmedappa\Dropbox\Code\CustomLib\PooLib" not in sys.path:
    sys.path.append(r'C:\Users\pmedappa\Dropbox\Code\CustomLib\PooLib')
    print(sys.path)
from poo_ghmodules import getGitHubapi
from poo_ghmodules import ghpaginate
from poo_ghmodules import ghparse_row
from poo_ghmodules import gettoken
import pandas as pd
import numpy as np
import requests

MAX_ROWS_PERWRITE = 10

DF_REPO = pd.DataFrame()
DF_COUNT = 0

LOG_CSV = r'C:\\Users\pmedappa\Dropbox\Course and Research Sharing\Research\Data\Sponsor\Rand\UserSpon_log.csv'


def appendrowindf(user_xl, row):
    """This code appends a row into the dataframe and returns the updated dataframe"""
    global DF_REPO 
    global DF_COUNT
    DF_REPO= DF_REPO.append(row, ignore_index = True, sort=False)
    DF_COUNT = DF_COUNT + 1
    if DF_COUNT >= MAX_ROWS_PERWRITE :
        df = pd.read_excel(user_xl,error_bad_lines=False,header= 0, index = False)
        df= df.append(DF_REPO, ignore_index = True, sort=False)
        df.to_excel(user_xl, index = False) 
        DF_COUNT = 0
        DF_REPO = pd.DataFrame()


def run_query(user_row,user_xl): 
    """ A simple function to use requests.post to make the API call. Note the json= section."""
    TOKEN = gettoken(r"C:\Users\pmedappa\Dropbox\Code\PW\GHtoken.txt")
    headers = {"Authorization": "Bearer "+ TOKEN } 

    query = """
        {
          rateLimit {
            cost
            remaining
            resetAt
          }
          user(login: \""""+str(user_row["login"])+"""\") {
            email
            location
            sponsorsListing {
              createdAt
              shortDescription
              name
              tiers(first: 100) {
                totalCount
                edges {
                  node {
                    name
                    description
                    monthlyPriceInDollars
                    updatedAt
                  }
                }
              }
            }
            sponsorshipsAsMaintainer(first: 100) {
              totalCount
              nodes {
                createdAt
                sponsor {
                  login
                }
              }
            }
          }
        }"""           
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
    
    temp_row = list()
    try:         
        sponsorl = req_json['data']['user']['sponsorsListing']            
        temp_row.append(sponsorl['tiers']['totalCount'])
        temp_row.append(sponsorl['tiers']['edges'])
    except: 
        temp_row.append("")
        temp_row.append("")
    
    try:
        sponsorasm = req_json['data']['user']['sponsorshipsAsMaintainer']
        temp_row.append(sponsorasm['totalCount'])
        temp_row.append(sponsorasm ['nodes'])
    except:
        temp_row.append("")
        temp_row.append("")
    user_row= user_row.append(pd.Series(temp_row), ignore_index = True)
    appendrowindf(user_xl, user_row)        

    return 0

      
    
def main():
    """Main function"""   
    global DF_REPO 
    global DF_COUNT
    r_user_xl = r'C:\\Users\pmedappa\Dropbox\Course and Research Sharing\Research\Data\Sponsor\CleanConsolidatedSponsors_SOMatch.xlsx'
    w_user_xl = r'C:\\Users\pmedappa\Dropbox\Course and Research Sharing\Research\Data\Sponsor\CleanConsolidatedSponsors_SOMatchOnly_test.xlsx'
    user_df = pd.read_excel(r_user_xl,error_bad_lines=False,header= 0, index = False)
    df_test = pd.DataFrame()
    df_test.to_excel(w_user_xl, index = False) 
    
    for i,row in user_df.iterrows():
        print(row['login'])
        run_query(row,w_user_xl)
    

    df = pd.read_excel(w_user_xl,error_bad_lines=False,header= 0, index = False)
    df= df.append(DF_REPO, ignore_index = True, sort=False)
    print(df.shape[0])
    df = df.drop(df.columns[0], 1)
    df.columns=["login", "name", "email", "company", "bio", "location",
                        "createdAt", "isHireable", "followers_totalCount", "following_totalCount","repositories_totalCount",
                        "sponsorsListing_createdAt","sponsorsListing_shortDescription","sponsorsListing_name",
                        "sponsorsListing_tiers_totalCount","sponsorsListing_tiers_edges","sponsorshipsAsMaintainer_totalCount",
                        "sponsorshipsAsMaintainer_nodes", "github username", "stack ID","stack url"
                        , "sponsorsListing_tiers_totalCount_0121","sponsorsListing_tiers_edges_0121","sponsorshipsAsMaintainer_totalCount_0121",
                        "sponsorshipsAsMaintainer_nodes_0121"]

    df.to_excel(w_user_xl, index = False) 
    DF_COUNT = 0
    DF_REPO = pd.DataFrame()

main()