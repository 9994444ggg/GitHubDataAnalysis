# -*- coding: utf-8 -*-
"""
Created on Fri Jan 31 15:11:32 2020

@author: pmedappa

Sort contributors in ascending order. This is needed to find organization affiliation in 6 
"""

import openpyxl
import pandas as pd
import numpy as np
import ast

COL_MC_XLSX = r"C:\Users\pmedappa\Dropbox\Data\092019 CommitInfo\Organization_Specific\microsoft\Classified\org_col_classified_microsoft_commit_EMPTY.xlsx"
NEW_XLSX = r"C:\Users\pmedappa\Dropbox\Data\092019 CommitInfo\Organization_Specific\microsoft\Classified\int_org_col_classified_microsoft_commit_EMPTY.xlsx"
DT_ERROR_LOG = r"C:\Users\pmedappa\Dropbox\Data\092019 CommitInfo\Organization_Specific\microsoft\Classified\DT_ERROR_LOG_UserInfo_Ext.xlsx"

MAX_ROWS_PERWRITE = 5000

DF_REPO = pd.DataFrame()
DF_COUNT = 0
ORG_NAME = list()

LOG_CSV = r'C:\Users\pmedappa\Dropbox\Data\092019 CommitInfo\Contributors_monthwise\UserSpon_log.csv'

def appendrowindf(user_xl, row, df_flag = 0):
    """This code appends a row into the dataframe and returns the updated dataframe"""
    global DF_REPO 
    global DF_COUNT
    
    
    # note there is an issue when shape is used for series and df. 
    if df_flag == 0:
        DF_REPO= DF_REPO.append(row, ignore_index = True)
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

def sortasc(df_repom, by):
    """ Find net colab """
    df_repom = df_repom.sort_values(by=by, ascending=True)
    df_repom['rank_yearmonth'] = df_repom['contributor_start_yearmonth'].rank(method='min')
        
    return df_repom    
    
    


def main():
    """Get data from the training sample CSV and perform various cleaning and data preprocessing"""
    global DF_REPO 
    global DF_COUNT
    pd.options.display.max_rows = 10
    pd.options.display.float_format = '{:.3f}'.format
    
    
    cont_df = pd.read_excel(COL_MC_XLSX ,header= 0)
    
    temp_df = pd.DataFrame()
    temp_df.to_excel(NEW_XLSX, index = False) 
    for i, row in cont_df.iterrows():
        if  pd.notnull(row[0]):
            print("Repo: ",row['repo_name'])
            if  len(temp_df) != 0:
                m_temp_df = sortasc(temp_df,'contributor_start_yearmonth' )
                # appendrowindf(NEW_XLSX, temp_df, df_flag = 1)
                appendrowindf(NEW_XLSX, m_temp_df, df_flag = 1)
            

            appendrowindf(NEW_XLSX, row, df_flag = 0)
            temp_df = pd.DataFrame()
        else:           
            temp_df = temp_df.append(row, ignore_index = True)
    
    if  len(temp_df) != 0:
        m_temp_df = sortasc(temp_df,'contributor_start_yearmonth' )
        appendrowindf(NEW_XLSX, m_temp_df, df_flag = 1)
    df = pd.read_excel(NEW_XLSX,header= 0)
    df= df.append(DF_REPO, ignore_index = True)
    df.to_excel(NEW_XLSX, index = False) 
    DF_COUNT = 0
    DF_REPO = pd.DataFrame()    


if __name__ == '__main__':
  main()
  