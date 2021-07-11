# -*- coding: utf-8 -*-
"""
Created on Fri Mar 12 15:49:27 2021

@author: pmedappa

Get organization specific repos and save in excel. 
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
from time import sleep

REPO_XL = r"C:\Users\pmedappa\Dropbox\Data\092019 CommitInfo\Organization_Specific\ibm.xlsx"

MAX_ROWS_PERWRITE = 100

DF_REPO = pd.DataFrame()
DF_COUNT = 0

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
        df.to_excel(user_xl, index = False) 
        DF_COUNT = 0
        DF_REPO = pd.DataFrame()


def run_query(org): 
    """ A simple function to use requests.post to make the API call. Note the json= section."""
    TOKEN = gettoken(r"C:\Users\pmedappa\Dropbox\Code\PW\GHtoken.txt")
    headers = {"Authorization": "Bearer "+ TOKEN } 
    query = """ 
query { 
  organization (login:\""""+org+"""\"){ 
    createdAt
    description
    email
    hasSponsorsListing
    isVerified
    location
    login
    name
    twitterUsername
    repositories(first : 1){
      totalCount
      pageInfo{
        startCursor
        hasNextPage
        endCursor
      }

    }
		twitterUsername
    updatedAt
    
    
  }
}"""    
    try:
        request = requests.post('https://api.github.com/graphql', json={'query':query}, headers=headers)
        req_json = request.json()
        org_info = req_json['data']['organization']
        endc = req_json['data']['organization']['repositories']['pageInfo']['startCursor']
    except:
        print("Error getting starting cursor")
        print(req_json)
        return 404
    
    end = False
    
# RUN QUERY USING START CURSOR
    while not end:
        query = """
        query($cursor:String!){
          rateLimit {
            cost
            remaining
            resetAt
          }
          organization(login:\""""+org+"""\") {
        
            repositories(first: 100, after:$cursor) {
              totalCount
              pageInfo {
                hasNextPage
                endCursor
              }
              nodes {
                id
                name
                createdAt
                pushedAt
                updatedAt
                description
                forkCount
                isFork
                isMirror
                isArchived
                isTemplate
                diskUsage
                stargazerCount
                issues(first :1){
                  totalCount
                }
                pullRequests(first: 1) {
                  totalCount
                }
                watchers(first: 1) {
                  totalCount
                }
                owner {
                  login
                }
                fundingLinks {
                  platform
                }
                
                languages(first: 100) {
                    totalCount
                    nodes {
                        name
                        }
                    }
                licenseInfo {
                    name
                    pseudoLicense
                    }
                
                
                labels(first: 100) {
                  totalCount
                  nodes {
                    name
                  }
                }
                releases(first: 100) {
                  totalCount
                  nodes {
                    author {
                      login
                    }
                    createdAt
                    description
                    isLatest
                    name
                    publishedAt
                    updatedAt
                  }
                }
              }
             }            
           }
         }

        """    
        variables = {
             "cursor" : endc
             }
        body = {
            "query": query,
            "variables": variables
            }
        print(variables)
    
        try:
            request = requests.post('https://api.github.com/graphql', json=body, headers=headers)
            req_json = request.json()
            repo_info = req_json['data']['organization']['repositories']['nodes']

            print(req_json['data']['rateLimit']['remaining'])
            if int(req_json['data']['rateLimit']['remaining']) <100:
                print("sleeping ........")
                sleep(60)
        except:
            print("Error running graphql")
            end = True
            print(req_json)
            return 404
        
        if req_json['data']['organization']['repositories']['pageInfo']['hasNextPage']:     
            endc = req_json['data']['organization']['repositories']['pageInfo']['endCursor']
        else:
            end = True     
        
        for repo in repo_info:
            row = list()
            #ORG info    
            row.append(org_info['createdAt'])
            row.append(org_info['description'])
            row.append(org_info['email'])
            row.append(org_info['isVerified'])
            row.append(org_info['location'])
            row.append(org_info['login'])
            row.append(org_info['name'])
            row.append(org_info['twitterUsername'])            
            
              
            # Repo info
            row.append(repo['id'])
            row.append(repo['name'])
            row.append(repo['createdAt'])
            row.append(repo['pushedAt'])
            row.append(repo['updatedAt'])
            row.append(repo['description'])
            row.append(repo['forkCount'])
            row.append(repo['isFork'])
            row.append(repo['isMirror'])
            row.append(repo['isArchived'])              
            row.append(repo['isTemplate'])
            row.append(repo['diskUsage'])
            row.append(repo['stargazerCount'])
            row.append(repo['issues']['totalCount'])
            row.append(repo['pullRequests']['totalCount'])
            row.append(repo['watchers']['totalCount'])
            row.append(repo['owner']['login'])
            if repo['fundingLinks']:
                row.append(repo['fundingLinks'])
            else:
                row.append("")
                
            row.append(repo['languages']['totalCount'])
            row.append(repo['languages']['nodes']) 
            
            if repo['licenseInfo']:
                row.append(repo['licenseInfo']['name'])
                row.append(repo['licenseInfo']['pseudoLicense']) 
            else:
                row.append("")
                row.append("")
                
            row.append(repo['labels']['nodes'])

            #Release info
            row.append(repo['releases']['totalCount'])
            row.append(repo['releases']['nodes']) 
            if repo['releases']['totalCount'] > 0 :
                row.append(repo['releases']['nodes'][0]['author'])
                row.append(repo['releases']['nodes'][0]['createdAt'])
                row.append(repo['releases']['nodes'][0]['publishedAt'])
                row.append(repo['releases']['nodes'][0]['updatedAt'])            
                row.append(repo['releases']['nodes'][0]['name'])                
                row.append(repo['releases']['nodes'][0]['isLatest'])
                row.append(repo['releases']['nodes'][0]['description'])
            else :
                row.append("")
                row.append("")
                row.append("")
                row.append("")            
                row.append("")                
                row.append("")
                row.append("")  
            appendrowindf(REPO_XL, row, df_flag = 0)
    
    return 0

    


def main():
    """Main function"""   
    global DF_REPO 
    global DF_COUNT

    df_test = pd.DataFrame()
    df_test.to_excel(REPO_XL, index = False) 
    
    run_query('ibm')
    

    df = pd.read_excel(REPO_XL,header= 0)
    if DF_COUNT > 0:
        df= df.append(DF_REPO, ignore_index = True)

    df.columns = ['org_createdAt','org_description','org_email','org_isVerified','org_location','org_login','org_name','org_twitterUsername',
                  'repo_id','repo_name','repo_createdAt','repo_pushedAt','repo_updatedAt','repo_description','repo_forkCount','repo_isFork','repo_isMirror',
                  'repo_isArchived','repo_isTemplate','repo_diskUsage','repo_stargazerCount','repo_issues_totalCount','repo_pullRequests_totalCount','repo_watchers_totalCount',
                  'repo_owner_login','repo_fundingLinks','repo_languages_totalCount','repo_languages_nodes','repo_licenseInfo_name',
                  'repo_licenseInfo_pseudoLicense', 'repo_labels_nodes','releases_totalCount','releases_nodes','releases_nodes_0_author',
                  'releases_nodes_0_createdAt','releases_nodes_0_publishedAt','releases_nodes_0_updatedAt','releases_nodes_0_name',
                  'releases_nodes_0_isLatest','releases_nodes_0_description'
                  ]

    df.to_excel(REPO_XL, index = False) 

main()