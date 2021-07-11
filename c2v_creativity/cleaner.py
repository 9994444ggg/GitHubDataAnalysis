#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Feb 19 11:48:26 2020

"""

import pandas as pd
import ast
import wrapper
import numpy as np
MAX_ROWS_PERWRITE = 10000

DF_REPO = pd.DataFrame()
DF_COUNT = 0

def getfcommitcode(i, commit):
    """
    input : commit row
    output : df with java code 
    Check if java files are modified in the commit and if yes, extarct the commit code form it. 
     return a dataframe with commit number, file name and code lines. Each row is a line of code.
    """
    df = pd.DataFrame()    
    #Need to check if it is java file
    try:
        for file, file_code in zip(ast.literal_eval(commit['OPEN_ISSUES']),ast.literal_eval(commit['LICENCE_NAME'])):
            if file.split('.')[-1].lower() == 'java':
    #                df_temp=pd.concat([df_temp, pd.Series(file_code.split('\n'))], axis=0, ignore_index=True)
                df_temp = pd.DataFrame()
                df_temp= df_temp.assign(code= pd.Series(file_code.split('\n')))
                df_temp= df_temp.assign(file= file)
                df_temp= df_temp.assign(commit= i)
                df=pd.concat([df, df_temp], axis=0, ignore_index=True,sort=False)    
    except: 
        print("Error parsing the commint info. Likely EOF encountered")        
    return df         
#Split code string into multiple rows of a dataframe
#df=pd.concat([pd.Series(row['SI'], row['LICENCE_NAME'].split('\\n'))              
#                for _, row in repo.iterrows()]).reset_index()


def preparedata(df):
    #Filter only added lines which start with '+'
    df1=df[df['code'].str.startswith('+')]
    df1['code']=df1['code'].str[1:] #Remove the '+' from the rows
#    df1['code'] = df1['code'].str.lower() # take lowercase of code
    
    #apply nuanced filter criteria
    ##remove 'import', '@', 'public', 'private'
    rem_brac=df1[~df1['code'].str.contains('import|@|public|private|package|protected|void|static')]
        
    # Bracket normalization
    rem_brac=rem_brac.reset_index()
    #iterate over each project
    df2 = pd.DataFrame( columns = df1.columns)
    remove_start = ['.',','] 
    for i_commit,rem_brac_cgp in rem_brac.groupby('commit'):
        file_no = 0
        for i_file,rem_brac_fgp in rem_brac_cgp.groupby('file'):

            o=0
            c=0
            os = 0 
            cs = 0
            comment_o = 0
            if_flag = 0
            file_no += 1
        #iterate over each line of code within filtered project
            for ind,row in rem_brac_fgp.iterrows():
                if len(row['code'].lstrip()) > 0:
                    if row['code'].lstrip()[0] in remove_start:
                        rem_brac_fgp.drop(ind,inplace=True)
#                        test_filename = 'input\\testran.txt'
#                        with open(test_filename , 'at', encoding="utf-8") as f:
#                            f.write(row['code'])
#                            f.write('\n')
                        continue
                    
                if '//' in row['code']: # Eliminate comments
                    row['code'] = row['code'].split('//')[0]
                if '/*' in row['code']:
                    comment_o = 1
                
                if 'else if' in row['code'] and comment_o == 0 :
                    pass
                elif 'if' in row['code'] and comment_o == 0:
                    if_flag = 1
                    
                if 'else' in row['code'] and comment_o == 0 :
                    if if_flag == 0 :
                        rem_brac_fgp.drop(ind,inplace=True)
                        continue
                    
                if '{' in row['code'] and comment_o == 0 :
                    o+=row['code'].count('{') #count the number of open brackects ??
                # small brackets 
                if '(' in row['code'] and comment_o == 0 :
                    os+= row['code'].count('(') #count the number of open brackects ??                    
                    
                if '}' in row['code'] and comment_o == 0 :
                    c+=row['code'].count('}')

                if ')' in row['code'] and comment_o == 0 :
                    cs+=row['code'].count(')') #count the number of open brackects ??                   

                if '*/' in row['code']:
                    comment_o = 0        
        
                if c > o:
                    rem_brac_fgp.drop(ind,inplace=True)
                    o=0
                    c=0  
                    if cs > os: # do not try and delete the same line twice
                        os=0
                        cs=0  
                        
                if cs > os: 
                    rem_brac_fgp.drop(ind,inplace=True)
                    os=0
                    cs=0   
                    
#            while os > cs: # add close bracket if applicable so that it balances with open brackets
##                print("***************more***************", o , " ", c)
#                row_value=pd.DataFrame({'index':[-1], 'commit':[i_commit],'file':[row['file']],'code':[')']})
##                rem_brac=pd.concat([rem_brac.loc[:ind],row_value,rem_brac.loc[ind+1:]]).reset_index(drop=True)
#                rem_brac_fgp=rem_brac_fgp.append(row_value).reset_index(drop=True)
#                cs+=1
                
            while o > c: # add close bracket if applicable so that it balances with open brackets
#                print("***************more***************", o , " ", c)
                row_value=pd.DataFrame({'index':[-1], 'commit':[i_commit],'file':[row['file']],'code':['}']})
#                rem_brac=pd.concat([rem_brac.loc[:ind],row_value,rem_brac.loc[ind+1:]]).reset_index(drop=True)
                rem_brac_fgp=rem_brac_fgp.append(row_value).reset_index(drop=True)
                c+=1


            # create function start
#            funct_def = "public class f"+str(i_commit)+str(file_no)+"{ " #using class packagind to avoid function defition parsing error 
            funct_def = "static int f"+str(i_commit)+str(file_no)+"(){ "
            func_start =pd.DataFrame({'commit':[i_commit],'file':row['file'],'code':[funct_def]})
            # close the function bracket
            row_value=pd.DataFrame({'index':[-1], 'commit':[i_commit],'file':[row['file']],'code':['}']})
            rem_brac_fgp=rem_brac_fgp.append(row_value).reset_index(drop=True)

            df2 = pd.concat([df2,func_start,rem_brac_fgp], axis=0, ignore_index=True,sort=False)
        # add '\n' for every code row of rem_brac so that looks similar to working text output
        #rem_brac['code']='\n' + rem_brac['code'].astype(str) 
    
    

    df2['code']='\n' + df2['code']        

    return df2

def getvectors(str_code, predictor):
    """
    run the wrapper to code2vec and retrun vectors
    """
#    output_filename = 'input\output.txt'
    try:
        str_code = str_code.encode('utf-8').decode('unicode_escape')
        vec = predictor.predict(str_code)
    except:
        vec = np.nan
#    with open(output_filename, 'at', encoding="utf-8") as f:
#        f.write(str_code)
#        f.write('\n')
    return vec

def appenddf(user_xl, row):
    """This code appends a row into the dataframe and returns the updated dataframe"""
    global DF_REPO 
    global DF_COUNT
    DF_REPO= DF_REPO.append(row, ignore_index = True)
    DF_COUNT = DF_COUNT + row.shape[0]
    if DF_COUNT >= MAX_ROWS_PERWRITE :
        df = pd.read_excel(user_xl,error_bad_lines=False,header= 0, index = False)
        df= df.append(DF_REPO, ignore_index = True)
        df.to_excel(user_xl, index = False) 
        DF_COUNT = 0
        DF_REPO = pd.DataFrame()
        
def main():
    global DF_REPO 
    global DF_COUNT
    pd.options.display.max_colwidth = 1000 #so that the long lines of code are displayed
    output_file = r'C:\Data\092019 CommitInfo\JavaSampling\Java_RepoCommit_Vec_1.xlsx'
    repo=pd.read_excel(r'C:\Data\092019 CommitInfo\JavaSampling\Java_RepoCommit_1.xlsx')#Read in the table
    predictor = wrapper.InteractivePredictorWrapper()

    df_out = pd.DataFrame()
    df_out.to_excel(output_file, index = False)
    for i,row in repo.iterrows(): 
        nrow = pd.DataFrame()
        write_row = pd.DataFrame()
        print(i)
        if pd.isna(row['PINDEX']):  # check if row is a repo or a commit          
            df = getfcommitcode(i,row)    
            if not df.empty: # if ast.literal_eval works on code, proceed        
                df2 = preparedata(df)
                if not df2.empty: # if there is code to find vectors proceed
#                    df2.to_excel('input\cleancode.xlsx')            
                    for j, cf_code in df2.groupby(['commit','file']):
                        
                        vec = getvectors(cf_code.code.to_string(index=False), predictor)

                        write_row = row[['PINDEX','REPO_ID','NAME','OWNER','OWNER_TYPE','SIZE','CREATE_DATE','PUSHED_DATE','MAIN_LANGUAGE','NO_LANGUAGES','SCRIPT_SIZE','STARS','SUBSCRIPTIONS']]
                        temp_ser = pd.Series([j, vec], index=['FILE_NO', 'VECTORS']) # if error in getting vectors it is np.nan
                        write_row = write_row.append(temp_ser)
                        nrow = nrow.append( write_row, ignore_index=True)                               
                else: 
                    write_row = row[['PINDEX','REPO_ID','NAME','OWNER','OWNER_TYPE','SIZE','CREATE_DATE','PUSHED_DATE','MAIN_LANGUAGE','NO_LANGUAGES','SCRIPT_SIZE','STARS','SUBSCRIPTIONS']]
                    temp_ser = pd.Series(["", ""], index=['FILE_NO', 'VECTORS'])
                    write_row = write_row.append(temp_ser)
                    nrow = nrow.append( write_row, ignore_index=True)                    
            else:
                write_row = row[['PINDEX','REPO_ID','NAME','OWNER','OWNER_TYPE','SIZE','CREATE_DATE','PUSHED_DATE','MAIN_LANGUAGE','NO_LANGUAGES','SCRIPT_SIZE','STARS','SUBSCRIPTIONS']]
                temp_ser = pd.Series(["", ""], index=['FILE_NO', 'VECTORS'])
                write_row = write_row.append(temp_ser)
                nrow = nrow.append( write_row, ignore_index=True)
        else:
            nrow = nrow.append(row, ignore_index=True)
#        df_out = pd.concat([df_out, nrow])
        appenddf(output_file, nrow)
    
    df = pd.read_excel(output_file,error_bad_lines=False,header= 0, index = False)
    df= df.append(DF_REPO, ignore_index = True)
    df.to_excel(output_file, index = False)


if __name__ == '__main__':
  main()