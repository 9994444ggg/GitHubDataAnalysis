# -*- coding: utf-8 -*-
"""
Created on Wed Nov 14 14:47:45 2018

@author: kmpoo

Find specific commits 
"""

import pandas as pd

import numpy as np
import ast


COMMIT_SAMPLE_Full = r'C:/Data/092019 CommitInfo/JavaSampling/Java_RepoCommit.xlsx'

COMMIT_VEC_1 = r'C:\Data\092019 CommitInfo\JavaSampling\Java_RepoCommit_Vec_1.xlsx'
COMMIT_VEC_2 = r'C:\Data\092019 CommitInfo\JavaSampling\Java_RepoCommit_Vec_2.xlsx'

COMMIT_VEC_text = r'C:\Data\092019 CommitInfo\JavaSampling\Java Commit Creativity - Full.xlsx'
COMMIT_XL = 'C:/Data/092019 CommitInfo/JavaSampling/LabelDatset_CodeVec.xlsx'
COMMIT_XL_TXT = 'C:/Data/092019 CommitInfo/JavaSampling/LabelDatset_Text.xlsx'
pd.options.display.max_rows = 10
pd.options.display.float_format = '{:.1f}'.format

#df_c1 = pd.read_excel(COMMIT_VEC_1,error_bad_lines=False,header = 0)
#print(df_c1.shape)
#df_c2 = pd.read_excel(COMMIT_VEC_2,error_bad_lines=False,header = 0)
#print(df_c2.shape)
#df_c1= df_c1.append(df_c2, ignore_index = True)
#print(df_c1.shape)
#commit_dataframe_com = pd.read_excel(COMMIT_SAMPLE_Full, sep=",",error_bad_lines=False,header = 0)
#print(commit_dataframe_com.shape)
#commit_dataframe_com = commit_dataframe_com.drop_duplicates()
#print(commit_dataframe_com.shape)
#commit_dataframe_com  = commit_dataframe_com.assign(SHA = commit_dataframe_com['Commit URL'].str.split('/').str[-1])
#
#final_df = df_c1.merge(commit_dataframe_com , left_on='REPO_ID', right_on='SHA',
#          how = 'inner', suffixes=('', '_right'))
#print(final_df.shape)
#
#final_df = final_df.dropna(subset = ['VECTORS'])
#final_df = final_df.dropna(subset = ['Novelty','Usefulness'])
#print(final_df.shape)
#final_df = final_df.rename({'REPO_ID.1': 'C_Author_Name', 'NAME': 'C_Author_Email', 'OWNER':'C_Author_Date', 'OWNER_TYPE': 'C_Commiter_Name', 'SIZE':'C_Commiter_Email', 'CREATE_DATE':'C_Commiter_Date', 
#                                  'PUSHED_DATE': 'C_Comments' ,'MAIN_LANGUAGE': 'C_Description','NO_LANGUAGES':	'C_Additions','SCRIPT_SIZE':'C_Deletions','STARS': 'C_nParents','SUBSCRIPTIONS':	'C_nFiles',
#                                  'OPEN_ISSUES':'C_Files','FORKS': 'C_FileModified'}, axis='columns')
#final_df = final_df.dropna(how='all', axis=1)
#final_df.to_excel(COMMIT_XL)


"""*************************  ********************** """
df_t1 = pd.read_excel(COMMIT_SAMPLE_Full,error_bad_lines=False,header = 0)
print(df_t1.shape)
commit_dataframe_com = pd.read_excel(COMMIT_VEC_text, sep=",",error_bad_lines=False,header = 0)
print(commit_dataframe_com.shape)
commit_dataframe_com = commit_dataframe_com.drop_duplicates()
print(commit_dataframe_com.shape)
commit_dataframe_com  = commit_dataframe_com.assign(SHA = commit_dataframe_com['Commit URL'].str.split('/').str[-1])
final_df = df_t1.merge(commit_dataframe_com , left_on='REPO_ID', right_on='SHA',
          how = 'inner', suffixes=('', '_right'))

print(final_df.shape)

final_df = final_df.dropna(subset = ['Novelty','Usefulness'])
print(final_df.shape)
final_df = final_df.rename({'REPO_ID.1': 'C_Author_Name', 'NAME': 'C_Author_Email', 'OWNER':'C_Author_Date', 'OWNER_TYPE': 'C_Commiter_Name', 'SIZE':'C_Commiter_Email', 'CREATE_DATE':'C_Commiter_Date', 
                                  'PUSHED_DATE': 'C_Comments' ,'MAIN_LANGUAGE': 'C_Description','NO_LANGUAGES':	'C_Additions','SCRIPT_SIZE':'C_Deletions','STARS': 'C_nParents','SUBSCRIPTIONS':	'C_nFiles',
                                  'OPEN_ISSUES':'C_Files','FORKS': 'C_FileModified'}, axis='columns')
final_df = final_df.dropna(how='all', axis=1)
final_df.to_excel(COMMIT_XL_TXT)

