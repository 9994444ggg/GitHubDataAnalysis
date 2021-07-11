# -*- coding: utf-8 -*-
"""
Created on Tue Mar 16 11:08:45 2021

@author: pmedappa

Find empty repos to try with 'main' instead of 'master' branch
"""
import pandas as pd


COMMIT_EMPTY = r"C:\Users\pmedappa\Dropbox\Data\092019 CommitInfo\Organization_Specific\microsoft\microsoft_EMPTY.xlsx"
pd.options.display.max_rows = 10
pd.options.display.float_format = '{:.3f}'.format
    

file_i = [1,'1_2',2,3,4,5,6,7,8]
temp_df = pd.DataFrame()
temp_df.to_excel(COMMIT_EMPTY , index = False) 

for index in file_i:
    COMMIT_XL = r"C:\Users\pmedappa\Dropbox\Data\092019 CommitInfo\Organization_Specific\microsoft\microsoft_commit_"+str(index)+".xlsx"
    print(COMMIT_XL)    
    commit_df = pd.read_excel(COMMIT_XL ,header= 0)

    empty = 1
    p_row = pd.Series()
    for i, row in commit_df.iterrows():
        if pd.notnull(row["repo_name"]):
            if empty == 1 and i > 0:
                temp_df = temp_df.append(p_row, ignore_index = True)
                print("Empty Repo: ",p_row["repo_name"])
 
            p_row = row
            empty = 1
        else:           
            empty = 0
temp_df.to_excel(COMMIT_EMPTY , index = False) 