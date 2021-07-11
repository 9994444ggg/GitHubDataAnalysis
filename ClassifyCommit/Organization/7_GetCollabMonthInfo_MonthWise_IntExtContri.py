# -*- coding: utf-8 -*-
"""
Created on Fri Jan 31 15:11:32 2020

@author: pmedappa

Get month info of the collaborators and external contributors. Find the net contributors for each month.
"""

import openpyxl
import pandas as pd
import numpy as np
import ast

COL_MC_XLSX = r"C:\Users\pmedappa\Dropbox\Data\092019 CommitInfo\Organization_Specific\microsoft\Classified\int2_org_col_classified_microsoft_commit_EMPTY.xlsx"
NEW_XLSX = r"C:\Users\pmedappa\Dropbox\Data\092019 CommitInfo\Organization_Specific\microsoft\Classified\month_int2_org_col_classified_microsoft_commit_EMPTY.xlsx"
DT_ERROR_LOG = r"C:\Users\pmedappa\Dropbox\Data\092019 CommitInfo\Organization_Specific\ibm\Classified\DT_ERROR_LOG_UserInfo_Ext.xlsx"

MAX_ROWS_PERWRITE = 20000

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

def getcolab(df_repom):
    """ Find net colab """
    df_repom = df_repom.sort_values(by='contributor_start_yearmonth', ascending=True)    
    #get colab and contributors
    df_repom['Collaborator']= df_repom['contributor_type'].apply( lambda x: 1 if x == 'Collaborator' else 0)
    df_repom['Contributor']= df_repom['contributor_type'].apply( lambda x: 1 if x == 'Contributor' else 0)
    
    #get internal colab and contributors
    df_repom['Internal_Acc']= df_repom['internal_contributor'].apply( lambda x: 1 if x > 0 and x < 4 else 0)
    df_repom['Internal_All']= df_repom['internal_contributor'].apply( lambda x: 1 if x > 0 else 0)
    df_repom['Internal_Acc_Colab']= df_repom.apply( lambda x: 1 if x['internal_contributor'] > 0 and x['internal_contributor'] < 4  and x['contributor_type'] == 'Collaborator' else 0, axis = 1)
    df_repom['Internal_All_Colab']= df_repom.apply( lambda x: 1 if x['internal_contributor'] > 0 and  x['contributor_type'] == 'Collaborator' else 0, axis = 1)
    df_repom['Internal_Acc_Cont']= df_repom.apply( lambda x: 1 if x['internal_contributor'] > 0 and x['internal_contributor'] < 4  and x['contributor_type'] == 'Contributor' else 0, axis = 1)
    df_repom['Internal_All_Cont']= df_repom.apply( lambda x: 1 if x['internal_contributor'] > 0 and  x['contributor_type'] == 'Contributor' else 0, axis = 1)
    
     
    return df_repom    
    
    
def getnetcolab(contri):
    """Aggregate contributor information monthwise"""
    # convert float yearmonth to int
    contri['contributor_start_yearmonth'] = contri['contributor_start_yearmonth'].astype(int)
    contri['contributor_end_yearmonth'] = contri['contributor_end_yearmonth'].astype(int)
    
    # Set index as all month from 0 till the end of last contributor
    df2 = pd.DataFrame({'month' : [i for i in range(contri['contributor_end_yearmonth'].astype(int).max()+1)]})
    df2 = df2.set_index('month')
    
    # get various variables
    df2 = pd.concat([df2,contri.groupby('contributor_start_yearmonth')['contributor_start_2008yearmonth'].min()], axis=1)
    df2 = pd.concat([df2,contri.groupby('contributor_start_yearmonth')['contributor_start_date'].min()], axis=1)
    df2 = pd.concat([df2,contri.groupby('contributor_start_yearmonth')['total_author_contributions'].mean()], axis=1)
    df2 = pd.concat([df2,contri.groupby('contributor_start_yearmonth')['total_committing_contributions'].mean()], axis=1)
    df2 = pd.concat([df2,contri.groupby('contributor_start_yearmonth')['contributor_ishireable'].sum()], axis=1)
    contri['total_organizations'] = contri['all_organizations'].str.len()
    df2 = pd.concat([df2,contri.groupby('contributor_start_yearmonth')['total_organizations'].sum()], axis=1)

    

    # Aggregate contributors monthwise and find cummulative collab and contributors    
    df2 = pd.concat([df2,contri.groupby('contributor_start_yearmonth')['Collaborator'].sum().to_frame('start_colab_count')], axis=1)
    df2['start_colab_count'] = df2['start_colab_count'].fillna(0)
    df2 = df2.assign(cs_colab= df2['start_colab_count'].cumsum())

    df2 = pd.concat([df2,contri.groupby('contributor_start_yearmonth')['Contributor'].sum().to_frame('start_cont_count')], axis=1)
    df2['start_cont_count'] = df2['start_cont_count'].fillna(0)
    df2 = df2.assign(cs_cont= df2['start_cont_count'].cumsum())
    
    # Find end count for collabs and contributors    
    df2 = pd.concat([df2,contri.groupby('contributor_end_yearmonth')['Collaborator'].sum().to_frame('end_colab_count')], axis=1)
    df2['end_colab_count'] = df2['end_colab_count'].fillna(0)

    df2 = pd.concat([df2,contri.groupby('contributor_end_yearmonth')['Contributor'].sum().to_frame('end_cont_count')], axis=1)
    df2['end_cont_count'] = df2['end_cont_count'].fillna(0)


    # Calculate net contributors  
    df2 = df2.assign(net_colab_count = df2['cs_colab'] - df2['end_colab_count'].cumsum().shift(1).fillna(0))
    df2 = df2.assign(net_cont_count = df2['cs_cont'] - df2['end_cont_count'].cumsum().shift(1).fillna(0))
    
    
    # repeat for all internal contributors
    df2 = pd.concat([df2,contri.groupby('contributor_start_yearmonth')['Internal_All'].sum().to_frame('start_intall_count')], axis=1)
    df2['start_intall_count'] = df2['start_intall_count'].fillna(0)
    df2 = df2.assign(cs_intall= df2['start_intall_count'].cumsum())
    
    df2 = pd.concat([df2,contri.groupby('contributor_start_yearmonth')['Internal_Acc'].sum().to_frame('start_intacc_count')], axis=1)
    df2['start_intacc_count'] = df2['start_intacc_count'].fillna(0)
    df2 = df2.assign(cs_intacc= df2['start_intacc_count'].cumsum())  
    
    df2 = pd.concat([df2,contri.groupby('contributor_end_yearmonth')['Internal_All'].sum().to_frame('end_intall_count')], axis=1)
    df2['end_intall_count'] = df2['end_intall_count'].fillna(0)    

    df2 = pd.concat([df2,contri.groupby('contributor_end_yearmonth')['Internal_Acc'].sum().to_frame('end_intacc_count')], axis=1)
    df2['end_intacc_count'] = df2['end_intacc_count'].fillna(0)   
    
    df2 = df2.assign(net_intall_count = df2['cs_intall'] - df2['end_intall_count'].cumsum().shift(1).fillna(0))
    df2 = df2.assign(net_intacc_count = df2['cs_intacc'] - df2['end_intacc_count'].cumsum().shift(1).fillna(0))    

    # repeat for internal collaborators
    df2 = pd.concat([df2,contri.groupby('contributor_start_yearmonth')['Internal_All_Colab'].sum().to_frame('start_intall_colab_count')], axis=1)
    df2['start_intall_colab_count'] = df2['start_intall_colab_count'].fillna(0)
    df2 = df2.assign(cs_intall_colab= df2['start_intall_colab_count'].cumsum())
    
    df2 = pd.concat([df2,contri.groupby('contributor_end_yearmonth')['Internal_All_Colab'].sum().to_frame('end_intall_colab_count')], axis=1)
    df2['end_intall_colab_count'] = df2['end_intall_colab_count'].fillna(0)       
    
    df2 = df2.assign(net_intall_colab_count = df2['cs_intall_colab'] - df2['end_intall_colab_count'].cumsum().shift(1).fillna(0))
    
    df2 = pd.concat([df2,contri.groupby('contributor_start_yearmonth')['Internal_Acc_Colab'].sum().to_frame('start_intacc_colab_count')], axis=1)
    df2['start_intacc_colab_count'] = df2['start_intacc_colab_count'].fillna(0)
    df2 = df2.assign(cs_intacc_colab= df2['start_intacc_colab_count'].cumsum())
    
    df2 = pd.concat([df2,contri.groupby('contributor_end_yearmonth')['Internal_Acc_Colab'].sum().to_frame('end_intacc_colab_count')], axis=1)
    df2['end_intacc_colab_count'] = df2['end_intacc_colab_count'].fillna(0)       
    
    df2 = df2.assign(net_intacc_colab_count = df2['cs_intacc_colab'] - df2['end_intacc_colab_count'].cumsum().shift(1).fillna(0))    
    
    # repeat for internal contributors
    df2 = pd.concat([df2,contri.groupby('contributor_start_yearmonth')['Internal_All_Cont'].sum().to_frame('start_intall_cont_count')], axis=1)
    df2['start_intall_cont_count'] = df2['start_intall_cont_count'].fillna(0)
    df2 = df2.assign(cs_intall_cont= df2['start_intall_cont_count'].cumsum())
    
    df2 = pd.concat([df2,contri.groupby('contributor_end_yearmonth')['Internal_All_Cont'].sum().to_frame('end_intall_cont_count')], axis=1)
    df2['end_intall_cont_count'] = df2['end_intall_cont_count'].fillna(0)       
    
    df2 = df2.assign(net_intall_cont_count = df2['cs_intall_cont'] - df2['end_intall_cont_count'].cumsum().shift(1).fillna(0))    

    df2 = pd.concat([df2,contri.groupby('contributor_start_yearmonth')['Internal_Acc_Cont'].sum().to_frame('start_intacc_cont_count')], axis=1)
    df2['start_intacc_cont_count'] = df2['start_intacc_cont_count'].fillna(0)
    df2 = df2.assign(cs_intacc_cont= df2['start_intacc_cont_count'].cumsum())
    
    df2 = pd.concat([df2,contri.groupby('contributor_end_yearmonth')['Internal_Acc_Cont'].sum().to_frame('end_intacc_cont_count')], axis=1)
    df2['end_intacc_cont_count'] = df2['end_intacc_cont_count'].fillna(0)       
    
    df2 = df2.assign(net_intacc_cont_count = df2['cs_intacc_cont'] - df2['end_intacc_cont_count'].cumsum().shift(1).fillna(0)) 
    
    df2 = df2.reset_index()
    df2.rename(columns={"index": "month"}, inplace = True)
    
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
        if  pd.notnull(row[0]):
            print("Repo: ",row['repo_name'])
            if  len(temp_df) != 0:
                m_temp_df = getcolab(temp_df)
                m_temp_df= getnetcolab(m_temp_df)
                appendrowindf(NEW_XLSX, m_temp_df, df_flag = 1)
            

            appendrowindf(NEW_XLSX, row, df_flag = 0)
            temp_df = pd.DataFrame()
        else:           
            temp_df = temp_df.append(row, ignore_index = True)
    
    if  len(temp_df) != 0:
        m_temp_df = getcolab(temp_df)
        m_temp_df= getnetcolab(m_temp_df)
        appendrowindf(NEW_XLSX, m_temp_df, df_flag = 1)
    df = pd.read_excel(NEW_XLSX,header= 0)
    df= df.append(DF_REPO, ignore_index = True)
    df.to_excel(NEW_XLSX, index = False) 
    DF_COUNT = 0
    DF_REPO = pd.DataFrame()    


if __name__ == '__main__':
  main()
  