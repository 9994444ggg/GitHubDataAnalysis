# -*- coding: utf-8 -*-
"""
Created on Wed Sep 11 17:04:10 2019

@author: pmedappa
"""
import csv
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

MAX_ROWS_PERWRITE = 100

DF_REPO = pd.DataFrame()
DF_COUNT = 0

LOG_CSV = r'C:\\Users\pmedappa\Dropbox\Course and Research Sharing\Research\MS Acquire Github\Data\Sponsor\Rand\UserSpon_log.csv'

def appendrowindf(user_xl, row):
    """This code appends a row into the dataframe and returns the updated dataframe"""
    global DF_REPO 
    global DF_COUNT
    DF_REPO= DF_REPO.append(row, ignore_index = True)
    DF_COUNT = DF_COUNT + row.shape[0]
    if DF_COUNT >= MAX_ROWS_PERWRITE :
        df = pd.read_excel(user_xl,error_bad_lines=False,header= 0, index = False)
        df= df.append(DF_REPO, ignore_index = True)
        df.to_excel(user_xl, index = False) 
        DF_COUNT = 0
        DF_REPO = pd.DataFrame()


def con_monthwise(df):
    """ MOnthwise consolidation of data"""
    df = df.assign( i_year =   pd.DatetimeIndex(pd.to_datetime(df['createdAt'], infer_datetime_format=True,errors='coerce')).year)
    df = df.assign( i_month =   pd.DatetimeIndex(pd.to_datetime(df['createdAt'], infer_datetime_format=True,errors='coerce')).month)
    df = df.assign( i_day =   pd.DatetimeIndex(pd.to_datetime(df['createdAt'], infer_datetime_format=True,errors='coerce')).day)
    
    df2 = df.groupby('i_month').agg(
                                {'i_day':['count']
                                 })
#    df2 = df.groupby('i_month')['i_day'].count()
#    
#    df2= pd.concat([df2,df.groupby('i_month')['i_day'].apply(list)], axis = 1)
    df2.columns = df2.columns.to_series()
    print(df2.columns)
    df2.columns = df2.columns.str.replace(',','a')
    print(df2.columns)
    return df2

def run_query(l_name,user_xl): 
    """ A simple function to use requests.post to make the API call. Note the json= section."""
    TOKEN = gettoken(r"C:\Users\pmedappa\Dropbox\Code\PW\GHtoken.txt")
    headers = {"Authorization": "Bearer "+ TOKEN } 
    
    query = """
{
  user(login: \""""+l_name+"""\") {
    issues(first: 1, filterBy: {since: "2019-01-01T00:00:00Z"}) {
      pageInfo {
        startCursor
        hasNextPage
      }
    }
  }
}

"""    
    try:
        request = requests.post('https://api.github.com/graphql', json={'query':query}, headers=headers)
        req_json = request.json()
        endc = req_json['data']['user']['issues']['pageInfo']['startCursor']
    except:
        print("Error getting starting cursor")
        print(req_json)
        return 404
    
    temp_df = pd.DataFrame()
    end = False
    while not end:
        query = """
                query($cursor:String! ) {
                  rateLimit {
                    cost
                    remaining
                    resetAt
                  }
                  user(login: \""""+l_name+"""\") {
                    email
                    location
                    issues(first: 100, filterBy: { since: "2019-01-01T00:00:00Z"}, after: $cursor) {
                      pageInfo {
                        endCursor
                        hasNextPage
                      }
                      totalCount
                      nodes {
                        id 
                        number
                        title
                        createdAt
                        closedAt
                        lastEditedAt
                        repository {
                          nameWithOwner
                          id
                          createdAt
                        }
                        labels(first: 100) {
                          totalCount
                          nodes {
                            name
                          }
                        }
                        comments(first: 100) {
                          totalCount
                        }
                        participants(first: 100) {
                          totalCount
                          nodes {
                            login
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
        try:
            request = requests.post('https://api.github.com/graphql', json=body, headers=headers)
            req_json = request.json()
            print(l_name," ",req_json['data']['user']['issues']['totalCount'] )
#            if  int(req_json['data']['search']['userCount']) > 1000:
#                # log if the total user count is greater than 1000
#                with open(LOG_CSV, 'at') as logobj:                    
#                    log = csv.writer(logobj)
#                    l_data = list()
#                    l_data.append("Search Results Exceeds 1000")
#                    l_data.append(loc)
#                    l_data.append(period)
#                    l_data.append(req_json['data']['search']['userCount'])
#                    log.writerow(l_data)
            print(req_json['data']['rateLimit']['remaining'])
            
        except:
            print("Error running graphql")
            end = True
            print(req_json)
            return 404
        
        if req_json['data']['user']['issues']['pageInfo']['hasNextPage']:     
            endc= req_json['data']['user']['issues']['pageInfo']['endCursor']
        else:
            end = True   
            
        issues = req_json['data']['user']['issues']

        for issue in issues['nodes']:
            issue_row = list()
            if(issue):

                issue_row = ghparse_row(issue,"id","number", "title", "createdAt", "closedAt", "repository*nameWithOwner", "repository*id",
                                       "repository*createdAt", "labels*totalCount", "labels*nodes", "comments*totalCount","participants*totalCount",
                                       "participants*nodes",prespace = 1)
                issue_row[0] = "issue"
                temp_df= temp_df.append(pd.Series( issue_row), ignore_index = True, sort=False)
            
    temp_df.columns = ["type","issue_id", "number", "title", "createdAt", "closedAt", "repo_nameWithOwner", "repo_id",
                       "repo_createdAt", "labels_totalCount", "labels_nodes", "comments_totalCount","participants_totalCount",
                        "participants_nodes"]        
#    mcon_df = con_monthwise(temp_df)
    appendrowindf(user_xl, temp_df)        
#    con_monthwise()
    return 0

      
    
def main():
    """Main function"""   
    global DF_REPO 
    global DF_COUNT
    r_user_xl = r'C:\Users\pmedappa\Dropbox\Course and Research Sharing\Research\Data\Sponsor\CleanConsolidatedSponsors_SOMatch_TEST.xlsx'
    w_user_xl = r'C:\Users\pmedappa\Dropbox\Course and Research Sharing\Research\Data\Sponsor\CleanConsolidatedSponsors_SOMatch_INFO3.xlsx'
    user_df = pd.read_excel(r_user_xl,error_bad_lines=False,header= 0, index = False)
    df_test = pd.DataFrame()
    df_test.to_excel(w_user_xl, index = False) 
    
    for i,row in user_df.iterrows():
        appendrowindf(w_user_xl, row)
        print(row['login'])
        run_query(row['login'],w_user_xl)
    

    df = pd.read_excel(w_user_xl,error_bad_lines=False,header= 0, index = False)
    df= df.append(DF_REPO, ignore_index = True)
    df.to_excel(w_user_xl, index = False) 
    DF_COUNT = 0
    DF_REPO = pd.DataFrame()
  
main()