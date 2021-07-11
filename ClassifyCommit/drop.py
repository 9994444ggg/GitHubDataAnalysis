# -*- coding: utf-8 -*-
"""
Created on Tue Jul 28 16:31:04 2020

@author: pmedappa
"""


import pandas as pd

MC_XLSX = "C:/Users/pmedappa/Dropbox/Data/092019 CommitInfo/ClassifiedRepoCommit/28072020_FinalCleanData_Full_Clean1.xlsx"
CLEAN_XLSX = "C:/Users/pmedappa/Dropbox/Data/092019 CommitInfo/ClassifiedRepoCommit/28072020_FinalCleanData_Full_Clean2.xlsx"

def main():
    pd.options.display.max_rows = 10
    pd.options.display.float_format = '{:.3f}'.format
    writer = pd.ExcelWriter(CLEAN_XLSX, engine='xlsxwriter',options={'strings_to_urls': False})

    df_mc = pd.read_excel(MC_XLSX, sep=",",error_bad_lines=False,header=0,  encoding = "Latin1")
    print(df_mc.shape[0])
    df_mc = df_mc.dropna(subset=['c_count'])
    print(df_mc.shape[0])
    df_mc.to_excel(writer, sheet_name='Sheet1', index=False)
    writer.close()
    
main()