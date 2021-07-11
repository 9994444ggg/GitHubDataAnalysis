# -*- coding: utf-8 -*-
"""
Created on Sun Feb 16 00:07:14 2020

@author: pmedappa
"""


import pandas as pd

MC_XLSX = "C:/Users/pmedappa/Dropbox/Data/092019 CommitInfo/ClassifiedRepoCommit/28072020_MC_RepoCommit_Clean1.xlsx"
CLEAN_XLSX = "C:/Users/pmedappa/Dropbox/Data/092019 CommitInfo/ClassifiedRepoCommit/28072020_FinalCleanData_Full_Clean1.xlsx"

def main():
    pd.options.display.max_rows = 10
    pd.options.display.float_format = '{:.3f}'.format
    writer = pd.ExcelWriter(CLEAN_XLSX, engine='xlsxwriter',options={'strings_to_urls': False})

    df_mc = pd.read_excel(MC_XLSX, sep=",",error_bad_lines=False,header=0,  encoding = "Latin1")
    print(df_mc.shape[0])
    # remove headers that entered into the data
    df_mc = df_mc[df_mc['PINDEX'] != 'PINDEX']
    print(df_mc.shape[0])
    
#    df_mc = df_mc.drop(axis=1,columns=['PUSHED_0917', 'STARS_0917', 'SUBSCRIBERS_0917', 'FORKS_0917', 'SIZE_0917', 'LICENCE_0917', 'PUSHED_1017', 'STARS_1017', 'SUBSCRIBERS_1017', 'FORKS_1017', 
#                                       'SIZE_1017', 'LICENCE_1017', 'int_sup', 'int_sup_sq', 'month_jan_flag', 'month_feb_flag', 'month_mar_flag', 'month_apr_flag', 'month_may_flag', 'month_jun_flag',
#                                       'script_size_kb', 'script_size_mb', 'logsize_kb'])
    

    df_mc.iloc[:,:(df_mc.shape[1]-16)] = df_mc.iloc[:,:(df_mc.shape[1]-16)].fillna(method='ffill')
    #remove repo rows (non month rows)
    df_mc = df_mc.dropna(subset=['month'])
    #create new variables for duration for which collabs were contributing
    s_repo = df_mc['REPO_ID'].unique()
    new_repo =pd.DataFrame()
    
    for repo in s_repo:
        df_repom = df_mc[df_mc['REPO_ID'] == repo]
        df_repom = df_repom.assign(cs_colab = df_repom['start_colab'].cumsum())
        df_repom = df_repom.assign(net_colab = df_repom['cs_colab'] - df_repom['end_colab'].cumsum().shift(1).fillna(0))
        df_repom = df_repom.assign(cs_cont= df_repom['start_cont'].cumsum())
        df_repom = df_repom.assign(net_cont = df_repom['cs_cont'] - df_repom['end_cont'].cumsum().shift(1).fillna(0))        

        #create staggered novely, usefulness
        df_repom = df_repom.assign(m_novelty_diff = df_repom['m_novelty'].shift(-1) - df_repom['m_novelty'])
        df_repom = df_repom.assign(m_usefulness_diff =  df_repom['m_usefulness'].shift(-1) - df_repom['m_usefulness'])
        df_repom = df_repom.assign(m_noveltyp1_diff = df_repom['m_Noveltys2p1'].shift(-1) - df_repom['m_Noveltys2p1'])
        df_repom = df_repom.assign(m_noveltyp2_diff  =  df_repom['m_Noveltys2p2'].shift(-1) - df_repom['m_Noveltys2p2'])
        df_repom = df_repom.assign(m_noveltyp3_diff  =  df_repom['m_Noveltys2p2'].shift(-1) - df_repom['m_Noveltys2p2'])
        
        df_repom = df_repom.assign(m_usefulnessp1_diff = df_repom['m_Usefulnesss2p1'].shift(-1) - df_repom['m_Usefulnesss2p1'])
        df_repom = df_repom.assign(m_usefulnessp2_diff  =  df_repom['m_Usefulnesss2p2'].shift(-1) - df_repom['m_Usefulnesss2p2'])
        df_repom = df_repom.assign(m_usefulnessp3_diff  =  df_repom['m_Usefulnesss2p3'].shift(-1) - df_repom['m_Usefulnesss2p3'])
        
        df_repom = df_repom.dropna(subset=['m_novelty'])

       #create staggered novely, usefulness
        df_repom = df_repom.assign(m_novelty_ndiff = df_repom['m_novelty'].shift(-1) - df_repom['m_novelty'])
        df_repom = df_repom.assign(m_usefulness_ndiff =  df_repom['m_usefulness'].shift(-1) - df_repom['m_usefulness'])
        df_repom = df_repom.assign(m_noveltyp1_ndiff = df_repom['m_Noveltys2p1'].shift(-1) - df_repom['m_Noveltys2p1'])
        df_repom = df_repom.assign(m_noveltyp2_ndiff  =  df_repom['m_Noveltys2p2'].shift(-1) - df_repom['m_Noveltys2p2'])
        df_repom = df_repom.assign(m_noveltyp3_ndiff  =  df_repom['m_Noveltys2p2'].shift(-1) - df_repom['m_Noveltys2p2'])
        
        df_repom = df_repom.assign(m_usefulnessp1_ndiff = df_repom['m_Usefulnesss2p1'].shift(-1) - df_repom['m_Usefulnesss2p1'])
        df_repom = df_repom.assign(m_usefulnessp2_ndiff  =  df_repom['m_Usefulnesss2p2'].shift(-1) - df_repom['m_Usefulnesss2p2'])
        df_repom = df_repom.assign(m_usefulnessp3_ndiff  =  df_repom['m_Usefulnesss2p3'].shift(-1) - df_repom['m_Usefulnesss2p3'])
        
            
        new_repo = new_repo.append(df_repom, sort = False, ignore_index = True)
          
    print(df_mc.shape[1])
    new_repo.to_excel(writer, sheet_name='Sheet1', index=False)
    writer.close()
if __name__ == '__main__':
  main()
  