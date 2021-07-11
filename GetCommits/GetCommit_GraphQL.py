# -*- coding: utf-8 -*-
"""
Created on Wed Sep 11 17:04:10 2019

@author: pmedappa
"""
import csv
import sys
if "C:\\Users\\pmedappa\\\Dropbox\\HEC\\Python\\CustomLib\\PooLIB" not in sys.path:
    sys.path.append('C:\\Users\\pmedappa\\\Dropbox\\HEC\\Python\\CustomLib\\PooLIB')
    print(sys.path)
from poo_ghmodules import getGitHubapi
from poo_ghmodules import ghpaginate
from poo_ghmodules import ghparse_row

import pandas as pd
import numpy as np
import requests

LOG_CSV = 'C:\\Data\\092019 CommitInfo\\RepoCommit_log.csv'

def run_query(name, owner, NEWREPO_xl): 
    """ A simple function to use requests.post to make the API call. Note the json= section."""
    headers = {"Authorization": "Bearer "+"dfb9844388015057b2bb8331c562068b04d9807f"}  
    endc = ""
    commit_row = list() 
    while True:
        query = """
                    query{
                      rateLimit {
                        cost
                        remaining
                        resetAt
                      }
                      repository(name: """+name+""", owner: """+owner+""") {
                        ref(qualifiedName: "master") {
                          target {
                            ... on Commit {
                              history(first:100 until: "2016-01-01T00:00:00Z" """+endc+"""){
                                totalCount
                                pageInfo {
                                  endCursor
                                  hasNextPage
                                }
                                    edges {
                                      node {
                                        comments{
                                          totalCount
                                        }
                                        parents{
                                          totalCount
                                        }
                                        changedFiles
                                        additions
                                        deletions
                                        messageHeadline
                                        oid
                                        message
                                        author {
                                          name
                                          email
                                          date                        
                                          }
                                        committer {
                                          name
                                          email
                                          date                        
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
        try:
            request = requests.post('https://api.github.com/graphql', json={'query': query}, headers=headers)
            req_json = request.json()
        except:
            print("Error runnig graphql")
            break
        
        endcursor = req_json['data']['repository']['ref']['target']['history']['pageInfo']['endCursor']            
        commits = req_json['data']['repository']['ref']['target']['history']['edges']
        del commit_row[:]
        for commit in commits:
            print(commit['node']['oid'])
            commit_row.append("")
            commit_row.append(commit['node']['oid'])
            commit_row.append(commit['node']['author']['name']) 
            commit_row.append(commit['node']['author']['email']) 
            commit_row.append(commit['node']['author']['date']) 
            commit_row.append(commit['node']['committer']['name']) 
            commit_row.append(commit['node']['committer']['email']) 
            commit_row.append(commit['node']['committer']['date']) 
            commit_row.append(commit['node']['comments']['totalCount'])
            commit_row.append(commit['node']['additions'])
            commit_row.append(commit['node']['deletions'])
            commit_row.append(commit['node']['changedFiles'])
            commit_row.append(commit['node']['parents']['totalCount']) 
            commit_row.append(commit['node']['message'])
            
            appendrowindf(NEWREPO_xl, commit_row)
        return req_json

    return "404"
       


def get_name(repo_id):
    repo_url = "https://api.github.com/repositories/"+str(repo_id)
    repo_req = getGitHubapi(repo_url,PW_CSV,LOG_CSV)
    if repo_req:
        repo_json = repo_req.json()
        return repo_json['name'], repo_json['owner']['login']
    else:
        return None, None

def appendrowindf(NEWREPO_xl, row):
    """This code appends a row into the dataframe and returns the updated dataframe"""
    df = pd.read_excel(NEWREPO_xl,error_bad_lines=False,header= 0, index = False)
    df= df.append(pd.Series(row), ignore_index = True)
    df.to_excel(NEWREPO_xl, index = False) 
    
def main():
    """Main function"""   
    repo_csv = "C:\\Users\pmedappa\Dropbox\HEC\\2014GithubRepoData_Latest\FullData_20190604IVT_COLAB_Test5.csv"
    NEWREPO_xl = 'C:\\Data\\092019 CommitInfo\\RepoCommit_Test.xlsx'
    df_full = pd.DataFrame()
    df_full.to_excel(NEWREPO_xl, index = False) 
    with open(repo_csv, 'rt', encoding = 'utf-8') as repolist:
        repo_handle = csv.reader(repolist)
        rcount = 1
        for repo_row in repo_handle:
            appendrowindf(NEWREPO_xl, repo_row)
            repo_id = repo_row[1]            
            name, owner = get_name(repo_id)  
            result = "0"
            if name:  
                result = run_query(name, owner, NEWREPO_xl )            
#                print(result)
                if result == '404':
                    print("Error runnig graphql")
            
main()