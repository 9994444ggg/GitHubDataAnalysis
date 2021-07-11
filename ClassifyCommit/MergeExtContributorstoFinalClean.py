# -*- coding: utf-8 -*-
"""
Created on Mon Mar  8 09:59:48 2021

@author: pmedappa

Merge 28072020_FinalCleanData_Full_Clean2 with Final_COL_MC_RepoCommit_UserInfo_Ext
"""
import pandas as pd

LEFT_XLSX = r"C:\Users\pmedappa\Dropbox\Data\092019 CommitInfo\ClassifiedRepoCommit\UPnew28072020_FinalCleanData_Full.xlsx"
# LEFT_XLSX = r"C:\Users\pmedappa\Dropbox\Data\092019 CommitInfo\Contributors_monthwise\Final_COL_MC_RepoCommit_UserInfo_No2013_2.xlsx"

RIGHT_XLSX = r"C:\Users\pmedappa\Dropbox\Data\092019 CommitInfo\JavaSampling\Classified\new_Java_RepoCommit_Vec_class_full.xlsx"

MERGE_XLSX = r"C:\Users\pmedappa\Dropbox\Data\092019 CommitInfo\JavaSampling\Classified\merge_new_Java_RepoCommit_Vec_class.xlsx"


df_left = pd.read_excel(LEFT_XLSX ,header= 0)
df_right = pd.read_excel(RIGHT_XLSX ,header= 0)
df_left = df_left.rename(columns={0: 'REPO_ID'})
list_c = [i for i in range(0,384)]
df_right = df_right.rename(columns={'commit_month': 'month'})
df_right['REPO_ID'] = df_right['REPO_ID'].fillna(method='ffill')
df_temp = df_right[['REPO_ID','month','Novelty_tcmp1','Novelty_tcmp2','Novelty_tcmp3','Novelty_tcmp4','Novelty_tcmp5','Novelty_tcp1','Novelty_tcp2','Novelty_tcp3',
                     'Novelty_tcp4','Novelty_tcp5','Usefulness_tcmp1','Usefulness_tcmp2','Usefulness_tcmp3','Usefulness_tcmp4','Usefulness_tcmp5','Usefulness_tcp1',
                     'Usefulness_tcp2','Usefulness_tcp3','Usefulness_tcp4','Usefulness_tcp5','Novelty_tp1','Novelty_tp2','Novelty_tp3','Novelty_tp4','Novelty_tp5',
                     'Novelty_cp1','Novelty_cp2','Novelty_cp3','Novelty_cp4','Novelty_cp5']]



df_temp['Mean_Vec_Variance'] = df_right[list_c].mean(axis = 1)

df_right = pd.concat([df_temp  ,df_right[list_c]], axis=1)


print(df_left['REPO_ID'])
result = pd.merge(df_left, df_right,how="inner", on=["REPO_ID", "month"])
result.to_excel(MERGE_XLSX , index = False) 