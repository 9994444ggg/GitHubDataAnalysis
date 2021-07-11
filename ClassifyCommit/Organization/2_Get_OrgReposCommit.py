# -*- coding: utf-8 -*-
"""
Created on Fri Mar 12 15:49:27 2021

@author: pmedappa

The second code to get commit information for each repo collected
NOTE: master branch is called main branch for some repos
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

REPO_XL = r"C:\Users\pmedappa\Dropbox\Data\092019 CommitInfo\Organization_Specific\microsoft\microsoft_EMPTY_1.xlsx"
COMMIT_XL = r"C:\Users\pmedappa\Dropbox\Data\092019 CommitInfo\Organization_Specific\microsoft\microsoft_commit_EMPTY_1.xlsx"

MAX_ROWS_PERWRITE = 20000

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
        writer = pd.ExcelWriter(user_xl,options={'strings_to_urls': False})
        df.to_excel(writer , index = False) 
        writer.close()
        DF_COUNT = 0
        DF_REPO = pd.DataFrame()


def run_query(rname, rowner): 
    """ A simple function to use requests.post to make the API call. Note the json= section."""
    TOKEN = gettoken(r"C:\Users\pmedappa\Dropbox\Code\PW\GHtoken.txt")
    headers = {"Authorization": "Bearer "+ TOKEN } 
    query = """ 
query {
  repository(name:\""""+rname+"""\", owner:\""""+rowner+"""\") {
    ref(qualifiedName: "main") {
      target {
        ... on Commit {
          id
          history(first: 100) {
            totalCount
            pageInfo {
              hasNextPage
              startCursor
              endCursor
            }

          }
        }
      }
    }
  }
}"""    
    try:
        request = requests.post('https://api.github.com/graphql', json={'query':query}, headers=headers)
        req_json = request.json()
        endc = req_json['data']['repository']['ref']['target']['history']['pageInfo']['startCursor']
        print(req_json['data']['repository']['ref']['target']['history']['totalCount'])
        print(endc)
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
          repository(name:\""""+rname+"""\", owner:\""""+rowner+"""\") {
            ref(qualifiedName: "main") {
              target {
                ... on Commit {
                  id
                  history(first: 100, after:$cursor) {
                    totalCount
                    pageInfo {
                      hasNextPage
                      startCursor
                      endCursor
                    }
                    nodes {
                      id
                      oid
                      message
                      url
                      authoredByCommitter
                      authoredDate
                      committedDate
                      additions
                      deletions
                      parents(first:100){
                        totalCount
                        
                      }
                      comments(first :100){
                        totalCount
                      }
                      changedFiles
                      committer {
                        name
                        user {
                          login
                          email
                        }
                      }
                      author {
                        name
                        user {
                          login
                          email
                        }
                      }
                      authors(first: 100) {
                        totalCount
                        nodes {
                          user{
                            name
                            login
                            email
                          }
                        }
                      }
                    }
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
            commit_info = req_json['data']['repository']['ref']['target']['history']['nodes']

            print(req_json['data']['rateLimit']['remaining'])
            if int(req_json['data']['rateLimit']['remaining']) <100:
                print("sleeping ........")
                sleep(60)
        except:
            print("Error running graphql")
            end = True
            print(req_json)
            return 404
        
        if req_json['data']['repository']['ref']['target']['history']['pageInfo']['hasNextPage']:     
            endc = req_json['data']['repository']['ref']['target']['history']['pageInfo']['endCursor']
        else:
            end = True    
            
        for commit in commit_info:
            row = list()
            #Commit info    
            row.append(commit['id'])
            row.append(commit['oid'])
            
            # row.append(commit['url'])

            row.append(commit['authoredDate'])
            row.append(commit['author']['name']) 
            if commit['author']['user']:
                row.append(commit['author']['user']['login']) 
                row.append(commit['author']['user']['email']) 
            else:
                row.append("")
                row.append("")
                
            row.append(commit['committedDate'])
            row.append(commit['committer']['name']) 
            if commit['committer']['user']:
                row.append(commit['committer']['user']['login']) 
                row.append(commit['committer']['user']['email']) 
            else:
                row.append("")
                row.append("")
                
            row.append(commit['authors']['totalCount'])
            row.append(commit['authors']['nodes']) 
            
            row.append(commit['authoredByCommitter'])
            
            row.append(commit['additions'])            
            row.append(commit['deletions'])  
            row.append(commit['message'])            
            row.append(commit['changedFiles']) 
            row.append(commit['parents']['totalCount']) 
            
            s_row =  pd.Series(row, index =['commit_id', 'commit_oid',  'commit_authoredDate', 'commit_author_name',
                                               'commit_author_user_login','commit_author_user_email','commit_committedDate', 'commit_committer_name',
                                               'commit_committer_user_login','commit_committer_user_email','commit_authors_totalCount', 'commit_authors_nodes',
                                               'commit_authoredByCommitter','commit_additions','commit_deletions','commit_message','commit_changedFiles',
                                               'commit_parents_totalCount'])                         
            appendrowindf(COMMIT_XL, s_row, df_flag = 0)
    
    return 0

    


def main():
    """Main function"""   
    global DF_REPO 
    global DF_COUNT

    df_test = pd.DataFrame()
    df_test.to_excel(COMMIT_XL, index = False) 
    repo_df = pd.read_excel(REPO_XL,header= 0)

    
    for i,row in repo_df.iterrows():

        print("Repo ",row['repo_name'])
        appendrowindf(COMMIT_XL, row,df_flag = 0)        
        run_query(row['repo_name'],row['org_login'])

    
    
    df = pd.read_excel(COMMIT_XL,header= 0)
    df= df.append(DF_REPO, ignore_index = True)
    writer = pd.ExcelWriter(COMMIT_XL,options={'strings_to_urls': False})
    df.to_excel(writer, index = False) 
    writer.close()
    DF_COUNT = 0
    DF_REPO = pd.DataFrame()    
  
main()