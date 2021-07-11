# -*- coding: utf-8 -*-
"""
Created on Mon Feb 10 18:53:53 2020

@author: pmedappa
"""

import csv
import pandas as pd
import sys
if "C:\\Users\\pmedappa\\\Dropbox\\HEC\\Python\\CustomLib\\PooLIB" not in sys.path:
    sys.path.append('C:\\Users\\pmedappa\\\Dropbox\\HEC\\Python\\CustomLib\\PooLIB')
    print(sys.path)
from poo_ghmodules import getGitHubapi

from poo_ghmodules import ghparse_row


TRAIN_CSV = r'C:/Users/pmedappa/Dropbox/HEC/Project 5 - Roles and Coordination/Data/ML/Java Commit Creativity - Full.csv'
PW_CSV = r'C:\\Users\pmedappa\Dropbox\HEC\Python\PW\PW_GitHub.csv'
LOG_CSV = r'C:/Users/pmedappa/Dropbox/HEC/Project 5 - Roles and Coordination/Data/ML\RepoCommit_log.csv'
NEWREPO_xl = r'C:/Users/pmedappa/Dropbox/HEC/Project 5 - Roles and Coordination/Data/ML/Java Commit Labels.xlsx'


with open(TRAIN_CSV, 'rt', encoding = 'latin-1') as rdobj:
    rd_repo = csv.reader(rdobj)
    df = pd.DataFrame()
    for row in rd_repo:
        sp_url = row[0].split('/')
        if len(sp_url) > 5:
            commit_url = 'https://api.github.com/repos/'+sp_url[3]+'/'+sp_url[4]+'/commits/'+sp_url[6]
                       
            commit_req = getGitHubapi(commit_url,PW_CSV,LOG_CSV)
            if commit_req:
                commit = commit_req.json()

                commit_row = ghparse_row(commit,"sha","commit*author*date", "commit*message","commit*comment_count","commit*author*name","commit*author*email","commit*committer*date","commit*url","parents","commit*verification","stats","files", prespace = 0)
                commit_row[-1] = len(commit_row[-1])
                df = df.append(pd.Series(commit_row),sort = False, ignore_index = True)

            else:
                print("Error getting commit info ",commit_url)
                commit_row.append('')
                commit_row.append('')
                commit_row.append('')
                commit_row[-1] = len(commit_row[-1])
                df = df.append(pd.Series(commit_row),sort = False, ignore_index = True)

                with open(LOG_CSV, 'at', encoding = 'utf-8', newline ="") as loglist:
                    log_handle = csv.writer(loglist)
                    log_handle.writerow(["Error getting commit",commit_url,"UNKNOWN"])
                continue
df.to_excel(NEWREPO_xl)