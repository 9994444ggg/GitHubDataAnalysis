# -*- coding: utf-8 -*-
"""
Created on Sat Mar 13 22:01:51 2021

@author: pmedappa

Updated code from 4. that includes total_month_contributions
"""


import sys
if r"C:\Users\pmedappa\Dropbox\Code\CustomLib\PooLib" not in sys.path:
    sys.path.append(r'C:\Users\pmedappa\Dropbox\Code\CustomLib\PooLib')
    print(sys.path)
from poo_ghmodules import getGitHubapi
from poo_ghmodules import ghpaginate
from poo_ghmodules import ghparse_row
from poo_ghmodules import gettoken
from sklearn.metrics.pairwise import cosine_similarity
import math
import pandas as pd
import numpy as np
from numpy import array
from numpy import float32
import requests


df_w_colab_xl = pd.DataFrame()
df_w_commit_xl = pd.DataFrame()
"""
MAX_ROWS_PERWRITE = 10000

GLOBAL_DF = dict()


def inintiateglobaldf(filenames):
    global GLOBAL_DF
    
    for f in filenames:
        GLOBAL_DF["DF_REPO_"+f] = pd.DataFrame()
        GLOBAL_DF["DF_COUNT_"+f] = 0
    

def appendrowindf(user_xl, row, df_flag = 0, filename ="" ):
    """"""This code appends a row into the dataframe and returns the updated dataframe""""""
    global GLOBAL_DF
    DF_REPO = GLOBAL_DF["DF_REPO_"+filename]
    DF_COUNT = GLOBAL_DF["DF_COUNT_"+filename]
        
    # note there is an issue when shape is used for series and df. 
    if df_flag == 0:
        DF_REPO= DF_REPO.append(pd.DataFrame(row).T, ignore_index = True)
        DF_COUNT = DF_COUNT + 1 # use row.shape[0] for dataframe
    else:

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

    GLOBAL_DF["DF_REPO_"+filename] = DF_REPO
    GLOBAL_DF["DF_COUNT_"+filename] = DF_COUNT       
    
"""
def monthwise(df_commit,w_commit_xl):
    #Aggregate over the entrie author month

    global df_w_commit_xl

    df2 = pd.DataFrame()
    df2 = df_commit.groupby('commit_month')['Novelty_tcp1','Novelty_tcp2','Novelty_tcp3','Novelty_tcp4','Novelty_tcp5',
                                            'Novelty_tcmp1','Novelty_tcmp2','Novelty_tcmp3','Novelty_tcmp4','Novelty_tcmp5',
                                            'Usefulness_tcp1','Usefulness_tcp2','Usefulness_tcp3','Usefulness_tcp4','Usefulness_tcp5',
                                            'Usefulness_tcmp1','Usefulness_tcmp2','Usefulness_tcmp3','Usefulness_tcmp4','Usefulness_tcmp5',
                                            'Novelty_tp1','Novelty_tp2','Novelty_tp3','Novelty_tp4','Novelty_tp5','Novelty_cp1','Novelty_cp2',
                                            'Novelty_cp3','Novelty_cp4','Novelty_cp5'].mean()
    
    df_commit['lVec'] = np.array(df_commit['VECTORS'].apply(lambda x : "" if x in ("",np.nan) else dict(eval(x))['f']))
    df_commit= pd.concat([df_commit,(df_commit['lVec'].apply(pd.Series))], axis = 1)
    list_c = [i for i in range(0,384)]

    temp = df_commit.groupby('commit_month')[list_c].var()
    df2 = pd.concat([df2, temp], axis=1)
    
    df2= df2.reset_index()

    df_w_commit_xl= df_w_commit_xl.append(df2, ignore_index = True)

    
    return df2

def parsedate(df_commit):
    """Split date into year month and day columns, aggregate month strating from 2008-01-01"""
    # Author date
    df_commit['commit_year'] = pd.to_numeric(df_commit['CREATE_DATE'].str.split('-').str[0])
    df_commit['commit_month'] = pd.to_numeric(df_commit['CREATE_DATE'].str.split('-').str[1])
    

    return df_commit
    


     
def main():
    
    global df_w_colab_xl
    global df_w_commit_xl

    r_commit_xl = r"C:\Users\pmedappa\Dropbox\Data\092019 CommitInfo\JavaSampling\Classified\Java_RepoCommit_Vec_class_4.xlsx"
    w_commit_xl = r"C:\Users\pmedappa\Dropbox\Data\092019 CommitInfo\JavaSampling\Classified\new_Java_RepoCommit_Vec_class_4.xlsx"

    
    commit_df = pd.read_excel(r_commit_xl,header= 0)
    df_commit = pd.DataFrame()
    df_commit.to_excel(w_commit_xl, index = False) 

    commit_df['REPO_ID.1'] = commit_df['REPO_ID.1'].fillna(method='ffill')
    for i,row in commit_df.iterrows():
        if  pd.notnull(row['LICENCE_NAME']):
            print("Repo ",row['REPO_ID'])
            
            if len(df_commit) > 0 :
                df_commit = parsedate(df_commit)
                
                monthwise(df_commit,w_commit_xl)


            df_commit = pd.DataFrame()

            df_w_commit_xl= df_w_commit_xl.append(row, ignore_index = True)

        else:
            df_commit = df_commit.append(row, ignore_index = True)
            
    if len(df_commit) > 0 :
        df_commit = parsedate(df_commit)

        monthwise(df_commit,w_commit_xl)



    

    df_w_commit_xl.to_excel(w_commit_xl , index = False) 
   


  
    
    
main()