# -*- coding: utf-8 -*-
"""
Created on Fri Jan 31 15:11:32 2020

@author: pmedappa

New code to find the collaborators for each project and date of their first contribution.This code also groups collaborators
,contributors and contributions monthwise.
Using the merge events sheet C:/Users\pmedappa\Dropbox\HEC\Project 5 - Roles and Coordination\Data\MergeEvents 
"""

import openpyxl
import pandas as pd
import numpy as np
import ast

COL_MC_XLSX = r"C:\Users\pmedappa\Dropbox\Data\092019 CommitInfo\Contributors_monthwise\COL_MC_RepoCommit_UserInfo_Ext_No2013.xlsx"
NEW_XLSX = r"C:\Users\pmedappa\Dropbox\Data\092019 CommitInfo\Contributors_monthwise\Final_COL_MC_RepoCommit_UserInfo_No2013.xlsx"
DT_ERROR_LOG = r"C:\Users\pmedappa\Dropbox\Data\092019 CommitInfo\Contributors_monthwise\Contributors_monthwise/DT_ERROR_LOG_UserInfo_Ext.xlsx"

MAX_ROWS_PERWRITE = 2000

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


def monthwise(contri):
    #get month information for each commit
    # contri.columns = ['NAN', 'C_TYPE','C_NAME','CONTRIBUTIONS','PULLS','S_DATE','E_DATE'] #,'COMPANY','ORG_NAME','ORG_LOGIN','ORGANIZATIONS','EMAIL','LOCATION','ISHIREABLE','EXTERNAL','ALL_ORGS'

    contri= contri.assign( s_month =   pd.to_numeric(contri[5].str.split('-').str[1]))
    
    contri= contri.assign( e_month =   pd.to_numeric(contri[6].str.split('-').str[1]))

    contri['Collaborator']= contri[1].apply( lambda x: 1 if x == 'Collaborator' else 0)
    contri['Contributor']= contri[1].apply( lambda x: 1 if x == 'Contributor' else 0)
    contri['Internal_Acc']= contri[14].apply( lambda x: 1 if x > 0 and x < 4 else 0)
    contri['Internal_All']= contri[14].apply( lambda x: 1 if x > 0 else 0)

    contri['Internal_Acc_Colab']= contri.apply( lambda x: 1 if x[14] > 0 and x[14] < 4  and x[1] == 'Collaborator' else 0, axis = 1)
    contri['Internal_All_Colab']= contri.apply( lambda x: 1 if x[14] > 0 and  x[1] == 'Collaborator' else 0, axis = 1)
    contri['Internal_Acc_Cont']= contri.apply( lambda x: 1 if x[14] > 0 and x[14] < 4  and x[1] == 'Contributor' else 0, axis = 1)
    contri['Internal_All_Cont']= contri.apply( lambda x: 1 if x[14] > 0 and  x[1] == 'Contributor' else 0, axis = 1)

    
    df2 = pd.DataFrame({'month' : [1,2,3,4,5,6,7,8,9,10,11,12]})
    df2 = df2.set_index('month')
    df2 = pd.concat([df2,contri.groupby('s_month')['Collaborator'].sum().to_frame('start_colab')], axis=1)
    df2 = pd.concat([df2, contri.groupby('e_month')['Collaborator'].sum().to_frame('end_colab')], axis=1)
    df2 = pd.concat([df2,contri.groupby('s_month')['Contributor'].sum().to_frame('start_cont')], axis=1)
    df2 = pd.concat([df2, contri.groupby('e_month')['Contributor'].sum().to_frame('end_cont')], axis=1)
    
    df2 = pd.concat([df2,contri.groupby('s_month')['Internal_All'].sum().to_frame('start_int_all')], axis=1)
    df2 = pd.concat([df2, contri.groupby('e_month')['Internal_All'].sum().to_frame('end_int_all')], axis=1)    
    df2 = pd.concat([df2,contri.groupby('s_month')['Internal_Acc'].sum().to_frame('start_int_acc')], axis=1)
    df2 = pd.concat([df2, contri.groupby('e_month')['Internal_Acc'].sum().to_frame('end_int_acc')], axis=1)  

    df2 = pd.concat([df2,contri.groupby('s_month')['Internal_All_Colab'].sum().to_frame('start_int_all_colab')], axis=1)
    df2 = pd.concat([df2, contri.groupby('e_month')['Internal_All_Colab'].sum().to_frame('end_int_all_colab')], axis=1)        
    df2 = pd.concat([df2,contri.groupby('s_month')['Internal_All_Cont'].sum().to_frame('start_int_all_cont')], axis=1)
    df2 = pd.concat([df2, contri.groupby('e_month')['Internal_All_Cont'].sum().to_frame('end_int_all_cont')], axis=1)        

    df2 = pd.concat([df2,contri.groupby('s_month')['Internal_Acc_Colab'].sum().to_frame('start_int_acc_colab')], axis=1)
    df2 = pd.concat([df2, contri.groupby('e_month')['Internal_Acc_Colab'].sum().to_frame('end_int_acc_colab')], axis=1)        
    df2 = pd.concat([df2,contri.groupby('s_month')['Internal_Acc_Cont'].sum().to_frame('start_int_acc_cont')], axis=1)
    df2 = pd.concat([df2, contri.groupby('e_month')['Internal_Acc_Cont'].sum().to_frame('end_int_acc_cont')], axis=1) 

    df2 = df2.reset_index()
    df2.rename(columns={"index": "month"}, inplace = True)

    df2 = df2.fillna(0)


    return df2


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
        if  ~np.isnan(row[0]):
            print("Repo: ",row[0]," Owner: ",row[2]," Type: ",row[3])
            if  len(temp_df) != 0:
                m_temp_df= monthwise(temp_df)
                # appendrowindf(NEW_XLSX, temp_df, df_flag = 1)
                appendrowindf(NEW_XLSX, m_temp_df, df_flag = 1)
            

            appendrowindf(NEW_XLSX, row, df_flag = 0)
            temp_df = pd.DataFrame()
        else:           
            temp_df = temp_df.append(row, ignore_index = True)
    
    if  len(temp_df) != 0:
        m_temp_df= monthwise(temp_df)
        appendrowindf(NEW_XLSX, m_temp_df, df_flag = 1)
    df = pd.read_excel(NEW_XLSX,header= 0)
    df= df.append(DF_REPO, ignore_index = True)
    df.to_excel(NEW_XLSX, index = False) 
    DF_COUNT = 0
    DF_REPO = pd.DataFrame()    


if __name__ == '__main__':
  main()
  