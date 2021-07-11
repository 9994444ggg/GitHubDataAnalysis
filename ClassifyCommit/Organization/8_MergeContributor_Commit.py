# -*- coding: utf-8 -*-
"""
Created on Thu Mar 18 09:11:11 2021

@author: pmedappa

Drop columns
Merge
combine files
drop repeated repos
Create metrics
. Find release date

"""
import pandas as pd
import numpy as np

def mergefiles():
    """ Combine commits and contributions for all the files """
    # commit_files = [r'C:\Users\pmedappa\Dropbox\Data\092019 CommitInfo\Organization_Specific\microsoft\Classified\new2_classified_ibm_commit_1.xlsx',
    #                 r'C:\Users\pmedappa\Dropbox\Data\092019 CommitInfo\Organization_Specific\microsoft\Classified\new2_classified_ibm_commit_2.xlsx',
    #                 r'C:\Users\pmedappa\Dropbox\Data\092019 CommitInfo\Organization_Specific\microsoft\Classified\new2_classified_ibm_commit_3.xlsx',
    #                 r'C:\Users\pmedappa\Dropbox\Data\092019 CommitInfo\Organization_Specific\microsoft\Classified\new2_classified_ibm_commit_4.xlsx',
    #                 r'C:\Users\pmedappa\Dropbox\Data\092019 CommitInfo\Organization_Specific\microsoft\Classified\new2_classified_ibm_commit_EMPTY.xlsx']
    
    # contri_files = [r'C:\Users\pmedappa\Dropbox\Data\092019 CommitInfo\Organization_Specific\ibm\Classified\month_int2_org_col_classified_ibm_commit_1.xlsx',
    #           r'C:\Users\pmedappa\Dropbox\Data\092019 CommitInfo\Organization_Specific\ibm\Classified\month_int2_org_col_classified_ibm_commit_2.xlsx',
    #           r'C:\Users\pmedappa\Dropbox\Data\092019 CommitInfo\Organization_Specific\ibm\Classified\month_int2_org_col_classified_ibm_commit_3.xlsx',
    #           r'C:\Users\pmedappa\Dropbox\Data\092019 CommitInfo\Organization_Specific\ibm\Classified\month_int2_org_col_classified_ibm_commit_4.xlsx',
    #           r'C:\Users\pmedappa\Dropbox\Data\092019 CommitInfo\Organization_Specific\ibm\Classified\month_int2_org_col_classified_ibm_commit_EMPTY.xlsx']    
    
    # commit_files = [r'C:\Users\pmedappa\Dropbox\Data\092019 CommitInfo\Organization_Specific\ibm\Classified\new2_classified_ibm_commit_EMPTY.xlsx']
    
    # contri_files = [r'C:\Users\pmedappa\Dropbox\Data\092019 CommitInfo\Organization_Specific\ibm\Classified\month_int2_org_col_classified_ibm_commit_EMPTY.xlsx']  
    write_df = pd.DataFrame()
    # combi = zip(commit_files, contri_files)
    # write_df = pd.DataFrame()
    combi = [1,'1_2',2,3,4,5,'6_2',7,8,'EMPTY']
    # combi = ['test']
    for i in combi:
        commit = r'C:\Users\pmedappa\Dropbox\Data\092019 CommitInfo\Organization_Specific\microsoft\Classified\new2_classified_microsoft_commit_'+str(i)+'.xlsx'
        contri = r'C:\Users\pmedappa\Dropbox\Data\092019 CommitInfo\Organization_Specific\microsoft\Classified\month_int2_org_col_classified_microsoft_commit_'+str(i)+'.xlsx'
        print(commit,"  ", contri)

        commit_df = pd.read_excel(commit ,header= 0)
        contri_df = pd.read_excel(contri ,header= 0)
        
        contri_df ['repo_name'] = contri_df['repo_name'].fillna(method='ffill')
        contri_df = contri_df[['repo_name','month','contributor_start_2008yearmonth','contributor_ishireable','contributor_start_date',
                               'total_author_contributions','total_committing_contributions','total_organizations',
                               'start_colab_count','cs_colab','start_cont_count','cs_cont','end_colab_count','end_cont_count','net_colab_count',
                               'net_cont_count','start_intall_count','cs_intall','start_intacc_count','cs_intacc','end_intall_count','end_intacc_count',
                               'net_intall_count','net_intacc_count','start_intall_colab_count','cs_intall_colab','end_intall_colab_count',
                               'net_intall_colab_count','start_intacc_colab_count','cs_intacc_colab','end_intacc_colab_count','net_intacc_colab_count',
                               'start_intall_cont_count','cs_intall_cont','end_intall_cont_count','net_intall_cont_count','start_intacc_cont_count',
                               'cs_intacc_cont','end_intacc_cont_count','net_intacc_cont_count']]
        
        commit_df = commit_df.drop(columns = ['Unnamed: 0','commit_author_name','commit_author_user_email','commit_author_user_login',
                               'commit_authoredDate','commit_authors_nodes','commit_committedDate','commit_committer_name',
                               'commit_committer_user_email','commit_committer_user_login','commit_id','commit_message','commit_oid',
                               'org_description','org_email','org_isVerified','org_location'
                               ])

        
        
        #merge dataframes
        commit_df.rename(columns={"commit_authoredDate_yearmonth": "month"}, inplace = True)
         
        
        commit_df ['repo_name'] = commit_df['repo_name'].fillna(method='ffill')
        commit_df ['repo_id'] = commit_df['repo_id'].fillna(method='ffill')
        result = commit_df.merge(contri_df,how="left", on=['repo_name', "month"])
        write_df = write_df.append(result, ignore_index = True)
        
    return write_df    

def dataprep(write_df):
    """ Find the various metrics and clean data """   
    
    #iterate through the file
    write_df['first_release'] = write_df.apply(lambda x :"2050-01-01T00:00:00Z" if pd.isna(x['releases_nodes_0_publishedAt']) and pd.notna(x['org_login']) else x['releases_nodes_0_publishedAt'],axis = 1)
    write_df['first_release'] = (pd.to_numeric(write_df['first_release'].str.split('-').str[0]) - 2008) * 12 + pd.to_numeric(write_df['first_release'].str.split('-').str[1])
    
    write_df[['org_createdAt','org_login','org_name','org_twitterUsername','releases_nodes','releases_nodes_0_author','releases_nodes_0_createdAt',
     'releases_nodes_0_description','releases_nodes_0_isLatest',
     'releases_nodes_0_name','releases_nodes_0_publishedAt','releases_nodes_0_updatedAt','releases_totalCount','repo_createdAt',
     'repo_description','repo_diskUsage','repo_forkCount','repo_fundingLinks','repo_id','repo_isArchived','repo_isFork','repo_isMirror',
     'repo_isTemplate','repo_issues_totalCount','repo_labels_nodes','repo_languages_nodes','repo_languages_totalCount','repo_licenseInfo_name',
     'repo_licenseInfo_pseudoLicense','repo_owner_login','repo_pullRequests_totalCount','repo_pushedAt','repo_stargazerCount','repo_updatedAt',
     'repo_watchers_totalCount','first_release']]  =  write_df[['org_createdAt','org_login','org_name','org_twitterUsername','releases_nodes','releases_nodes_0_author','releases_nodes_0_createdAt',
     'releases_nodes_0_description','releases_nodes_0_isLatest',
     'releases_nodes_0_name','releases_nodes_0_publishedAt','releases_nodes_0_updatedAt','releases_totalCount','repo_createdAt',
     'repo_description','repo_diskUsage','repo_forkCount','repo_fundingLinks','repo_id','repo_isArchived','repo_isFork','repo_isMirror',
     'repo_isTemplate','repo_issues_totalCount','repo_labels_nodes','repo_languages_nodes','repo_languages_totalCount','repo_licenseInfo_name',
     'repo_licenseInfo_pseudoLicense','repo_owner_login','repo_pullRequests_totalCount','repo_pushedAt','repo_stargazerCount','repo_updatedAt',
     'repo_watchers_totalCount','first_release']].fillna(method='ffill')
    
   
    write_df = write_df.dropna(subset=['month'])  

    #loop to incrementally fill up missing values with calculated previous value
    while(write_df['contributor_start_2008yearmonth'].isnull().values.any()):
        write_df['p_2008ymon'] = write_df['contributor_start_2008yearmonth'].shift(1) + (write_df['month'] - write_df['month'].shift(1))
        write_df['contributor_start_2008yearmonth'] =  write_df.apply( lambda x: x['p_2008ymon'] if pd.isnull(x['contributor_start_2008yearmonth'] ) else x['contributor_start_2008yearmonth'] , axis = 1)
                                    
    
    write_df['post_release'] = write_df.apply( lambda x : 1 if x['first_release'] < x['contributor_start_2008yearmonth'] else 0 , axis = 1)
    write_df = write_df.drop(columns = ['p_2008ymon'])
    write_df.rename(columns={"contributor_start_2008yearmonth": "2008yearmonth"}, inplace = True)
    
    write_df[['contributor_ishireable','total_author_contributions','total_committing_contributions','total_organizations']] = write_df[['contributor_ishireable','total_author_contributions','total_committing_contributions','total_organizations']].fillna(0) 

    unique_repos = write_df['repo_name'].unique() 
    new_write_df = pd.DataFrame()
    for r in unique_repos:    
        repo_df =  write_df[write_df['repo_name'] == r]
        repo_df['continuos_yearmonth'] = repo_df['month'].rank()
        new_write_df = new_write_df.append(repo_df, ignore_index = True)

    return new_write_df
    

def main():
    """main function"""
    
    merged_file = r'C:\Users\pmedappa\Dropbox\Data\092019 CommitInfo\Organization_Specific\microsoft\Merged\merge_month_int2_org_col_classified_microsoft_commit_full_clean.xlsx'
    pd.options.display.max_rows = 10
    pd.options.display.float_format = '{:.3f}'.format
    
    write_df = mergefiles()
    write_df = write_df.drop_duplicates(subset = ['repo_id', 'month'])
    print(write_df.shape)

    write_df = dataprep(write_df)

    write_df.to_excel( merged_file , index = False)
        

main()



