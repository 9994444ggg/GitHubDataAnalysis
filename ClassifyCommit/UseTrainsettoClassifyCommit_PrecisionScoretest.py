# -*- coding: utf-8 -*-
"""
Created on Wed Jan  2 10:30:42 2019

@author: kmpoo

This code built on earlier code uses an existing trainset to classify commits (no randomization).
"""

import pandas as pd
import numpy as np
import ast
from time import time
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.utils import shuffle #To shuffle the dataframe
from sklearn.model_selection import train_test_split
from sklearn.neural_network import MLPClassifier
from sklearn.ensemble import RandomForestClassifier
from scipy.sparse import hstack
import matplotlib.pyplot as plt
from sklearn.model_selection import learning_curve
from sklearn.metrics import f1_score

TRAIN_CSV = r'C:/Users/pmedappa/Dropbox/HEC/Project 5 - Roles and Coordination/Data/ML/Commit Creativity - Train_Details_WithJava.xlsx'
#TRAIN_CSV = r'C:/Users/pmedappa/Dropbox/HEC/Project 5 - Roles and Coordination/Data/ML/Commit Creativity - Train3_Details.xlsx' # without java
TRAIN_SET = r'C:/Users/pmedappa/Dropbox\\Data\\092019 CommitInfo\Classifiers\Classifier 66 62\Trainset.xlsx'
TEST_SET = r'C:/Users/pmedappa/Dropbox\\Data\\092019 CommitInfo\Classifiers\Classifier 66 62\Testset.xlsx'
LABELFULL_CSV = r'C:/Users/pmedappa/Dropbox/HEC/Project 5 - Roles and Coordination/Data/ML/Trainout.csv'
TRAINSET_XL = r'C:/Users/pmedappa/Dropbox/HEC/Project 5 - Roles and Coordination/Data/ML/Trainset.xlsx'
TESTSET_XL = r'C:/Users/pmedappa/Dropbox/HEC/Project 5 - Roles and Coordination/Data/ML/Testset.xlsx'
COMMIT_XLSX =r"C:/Users/pmedappa/Dropbox/Data/092019 CommitInfo/RepoCommit6001_6570_1.xlsx"
COMMIT2_XLSX =r"C:/Users/pmedappa/Dropbox/Data/092019 CommitInfo/ClassifiedRepoCommit/ClassifiedRepoCommit6001_6570_1.xlsx"

"""
REPOCOMMIT_LIST =[
                   "C:/Data/092019 CommitInfo/RepoCommit1_287_1.xlsx",
                    "C:/Data/092019 CommitInfo/RepoCommit288_500_1.xlsx",
                    "C:/Data/092019 CommitInfo/RepoCommit501_1000_1.xlsx",
                    "C:/Data/092019 CommitInfo/RepoCommit1001_1500_1.xlsx",
                    "C:/Data/092019 CommitInfo/RepoCommit1501_2000_1.xlsx",
                    "C:/Data/092019 CommitInfo/RepoCommit2002_2500_1.xlsx",
                    "C:/Data/092019 CommitInfo/RepoCommit2501_3250_1.xlsx",
                    "C:/Data/092019 CommitInfo/RepoCommit3251_4000_1.xlsx",
                    "C:/Data/092019 CommitInfo/RepoCommit4001_5000_1.xlsx",
                    "C:/Data/092019 CommitInfo/RepoCommit5001_5202_1.xlsx",
                    "C:/Data/092019 CommitInfo/RepoCommit5203_6000_1.xlsx",
                    "C:/Data/092019 CommitInfo/RepoCommit6001_6570_1.xlsx"
                  ] """
def plot_learning_curve_std(estimator, X, y):
    """
    Generate a simple plot of the test and training learning curve.

    Parameters
    ----------
    estimator : object type that implements the "fit" and "predict" methods
        An object of that type which is cloned for each validation.

    title : string
        Title for the chart.

    X : array-like, shape (n_samples, n_features)
        Training vector, where n_samples is the number of samples and
        n_features is the number of features.

    y : array-like, shape (n_samples) or (n_samples, n_features), optional
        Target relative to X for classification or regression;
        None for unsupervised learning.

    ylim : tuple, shape (ymin, ymax), optional
        Defines minimum and maximum yvalues plotted.

    cv : int, cross-validation generator or an iterable, optional
        Determines the cross-validation splitting strategy.
        Possible inputs for cv are:
          - None, to use the default 3-fold cross-validation,
          - integer, to specify the number of folds.
          - :term:`CV splitter`,
          - An iterable yielding (train, test) splits as arrays of indices.

        For integer/None inputs, if ``y`` is binary or multiclass,
        :class:`StratifiedKFold` used. If the estimator is not a classifier
        or if ``y`` is neither binary nor multiclass, :class:`KFold` is used.

        Refer :ref:`User Guide <cross_validation>` for the various
        cross-validators that can be used here.

    n_jobs : int or None, optional (default=None)
        Number of jobs to run in parallel.
        ``None`` means 1 unless in a :obj:`joblib.parallel_backend` context.
        ``-1`` means using all processors. See :term:`Glossary <n_jobs>`
        for more details.

    train_sizes : array-like, shape (n_ticks,), dtype float or int
        Relative or absolute numbers of training examples that will be used to
        generate the learning curve. If the dtype is float, it is regarded as a
        fraction of the maximum size of the training set (that is determined
        by the selected validation method), i.e. it has to be within (0, 1].
        Otherwise it is interpreted as absolute sizes of the training sets.
        Note that for classification the number of samples usually have to
        be big enough to contain at least one sample from each class.
        (default: np.linspace(0.1, 1.0, 5))
        
        ref: https://chrisalbon.com/machine_learning/model_evaluation/plot_the_learning_curve/
    """
    train_sizes, train_scores, test_scores = learning_curve( RandomForestClassifier(), 
                                                            X, 
                                                            y,
                                                            # Number of folds in cross-validation
                                                            cv= 5,
                                                            # Evaluation metric
                                                            scoring='accuracy',
                                                            # Use all computer cores
                                                            n_jobs=1, 
                                                            # 50 different sizes of the training set
                                                            train_sizes=np.linspace(0.001, 1.0, 5))
    
    # Create means and standard deviations of training set scores
    train_mean = np.mean(train_scores, axis=1)
    
    # Create means and standard deviations of test set scores
    test_mean = np.mean(test_scores, axis=1)
    
    # Draw lines
    plt.plot(train_sizes, train_mean, '--', color="#111111",  label="Training score")
    plt.plot(train_sizes, test_mean, color="#111111", label="Cross-validation score")
        
    # Create plot
    plt.title("Learning Curve")
    plt.xlabel("Training Set Size"), plt.ylabel("Accuracy Score"), plt.legend(loc="best")
    plt.tight_layout()
    plt.show()
    

def getnoelements(x):
    """ Parse str represetation of python object into a list and return lenght"""
    no_parents = len(ast.literal_eval(x))
    return no_parents

def geticommit(x):
    text_file = ['txt','md','doc','docx','png','gif','jpg','avi','mpg','ppt','pptx']
    if pd.isna(x['PINDEX']) and pd.notna(x['OPEN_ISSUES']):
        try:
            # Check for EOL issues
            files = ast.literal_eval(x['OPEN_ISSUES'])
        except:
            return pd.Series([np.NaN,np.NaN,np.NaN,np.NaN,np.NaN,np.NaN], index=['Comments','Message','Added','Deleted','Parents','Files'])

        for i in files:
            l = i.split('.')
            if len(l) > 1:
                if l[1].lower() not in text_file:
                    return pd.Series([x['PUSHED_DATE'],x['MAIN_LANGUAGE'],x['NO_LANGUAGES'],x['SCRIPT_SIZE'],x['STARS'],x['SUBSCRIPTIONS']], index=['Comments','Message','Added','Deleted','Parents','Files'])

    return pd.Series([np.NaN,np.NaN,np.NaN,np.NaN,np.NaN,np.NaN], index=['Comments','Message','Added','Deleted','Parents','Files'])
    
def getVDF(TRAIN_CSV):
    """Get data from the training sample CSV and perform various cleaning and data preprocessing"""
    dataframe = pd.read_excel(TRAIN_CSV, sep=",",error_bad_lines=False,header= 0,  encoding = "Latin1")

    dataframe = dataframe.drop(axis=1,columns=['Commit URL', 'Sha','URL','Author Name','Author Email','Commit Date','Verification','Author Date'])
    # Shuffle the dataframe
    dataframe = shuffle(dataframe)
    # Encode type of commit
    dataframe = dataframe.assign(CommitType = lambda x: x['Type of Commit (Primary)'].str.split().str.get(0).str.strip(','))
    dataframe.CommitType = dataframe.CommitType.replace({'Feature': 1,
                                                                       'Bug/Issue': 2,
                                                                       'Documentation': 3,
                                                                       'Peer': 4,
                                                                       'Process': 5,
                                                                       'Testing': 6})
    dataframe = dataframe.drop(axis=1,columns=['Type of Commit (Primary)','Optional Type of Commit (Secondary)'])
    # Find number of parents
    dataframe['Parents'] = dataframe['Parents'].map(getnoelements)
    # Convert the number of lines of code into nChanges, nAdditions, nDeletions
    # Get total number of changes
    dataframe = dataframe.assign(nChanges = lambda x : x['Lines of Code Changed'].str.split(':').str.get(1).str.split(',').str.get(0) )
    # Get total number of additions
    dataframe = dataframe.assign(nAdditions = lambda x : x['Lines of Code Changed'].str.split(':').str.get(2).str.split(',').str.get(0) )
    # Get total number of deletions
    dataframe = dataframe.assign(nDeletions = lambda x : x['Lines of Code Changed'].str.split(':').str.get(3).str.split('}').str.get(0) )
    # Create three class labeld for novelty and usefulness
    conditions = [
        (dataframe['Novelty'] > 3),
        (dataframe['Novelty'] < 3),]
    choices = ['High', 'Low']
    dataframe['Novelty3'] = np.select(conditions, choices, default='Medium')
    
    conditions = [
        (dataframe['Usefulness'] > 3),
        (dataframe['Usefulness'] < 3),]
    choices = ['High', 'Low']
    dataframe['Usefulness3'] = np.select(conditions, choices, default='Medium')
    #Create count of words feature
    dataframe = dataframe.assign(nWords = lambda x : x['Description'].str.split().str.len() )
    dataframe_sd = dataframe.drop(dataframe[dataframe.CommitType.astype(int) == 3].index)

    return dataframe, dataframe_sd

def vectordsc(corpus, train_text, test_text):
    """Convert the description text into ngram vector of features. Sparse matrix format"""
    word_vectorizer = TfidfVectorizer(
                                        sublinear_tf=True,
                                        strip_accents='unicode',
                                        analyzer='word',
                                        token_pattern=r'\w{1,}',
                                        stop_words='english',
                                        ngram_range=(1, 2),
                                        max_features=10000)

    word_vectorizer.fit(corpus)
    train_word_features = word_vectorizer.transform(train_text)
    test_word_features = word_vectorizer.transform(test_text)
    return train_word_features, test_word_features, word_vectorizer

def MLPmodel(train_x, train_y, test_x, test_y, LCurve = False):
    """MLP classifier model"""
    nn = MLPClassifier(
                        hidden_layer_sizes=(100),  activation='relu', solver='adam', alpha=0.001, batch_size='auto',
                        learning_rate='constant', learning_rate_init=0.001, power_t=0.5, max_iter=1000, shuffle=True,
                        random_state=None, tol=0.0001, verbose=False, warm_start=False, momentum=0.9, nesterovs_momentum=True,
                        early_stopping=False, validation_fraction=0.1, beta_1=0.9, beta_2=0.999, epsilon=1e-08)
    n = nn.fit(train_x, train_y)
    p_train = n.predict_proba(train_x)
    p_test = n.predict_proba(test_x)
    pred_test = n.predict(test_x)
    acc = n.score(test_x,test_y)
    print("accuracy is = ",  acc)
    print('f1 ', f1_score(test_y, pred_test, average='macro'))
    if LCurve: plot_learning_curve_std(nn, train_x, train_y)
    return p_train, p_test, acc, n

def RFCmodel(train_x, train_y, test_x, test_y, LCurve = False):
    """Random forest Classifier model"""
    rfc = RandomForestClassifier(n_estimators=10)
    r = rfc.fit(train_x, train_y)
    acc = r.score(test_x,test_y)
    print("accuracy of rfc is = ", acc)
    p_train = r.predict_proba(train_x)
    p_test = r.predict_proba(test_x)
    if LCurve: plot_learning_curve_std(rfc, train_x, train_y)
    return p_train, p_test, acc, r

def main():
    pd.options.display.max_rows = 10
    pd.options.display.float_format = '{:.3f}'.format
    vector_dataframe, vector_dataframe_sd = getVDF(TRAIN_CSV)
    # Save the full labeled data sample post processing in CSV
    # vector_dataframe.to_csv(LABELFULL_CSV)
    #Split vector data frame into training and test samples
    df_train, df_test = train_test_split(vector_dataframe, test_size=0.2)
#    df_train = pd.read_excel(TRAIN_SET, sep=",",error_bad_lines=False,header= 0) #Use pre trainset
#    df_test = pd.read_excel(TEST_SET, sep=",",error_bad_lines=False,header= 0)

    #Reset the indices for merging other features later on
    df_train=df_train.reset_index()
    df_test = df_test.reset_index()
    #Create new CSV represnting the training and testing samples
    df_train.to_excel(TRAINSET_XL)
    df_test.to_excel(TESTSET_XL)
    #Convert description text into a vetor of features. Train_x,test_x are in sparse matrix format
    train_x, test_x, word_vectorizer = vectordsc(vector_dataframe['Description'], df_train['Description'], df_test['Description'] )
    acuracy = list()
    macc = list()
    macc_l = list()
    df_classify = pd.DataFrame()
    df_write = pd.DataFrame()

#    df_write = pd.read_excel(COMMIT_XLSX,error_bad_lines=False,header=0)
#    print(COMMIT_XLSX," rows ",df_write.shape[0])

#    dataframe_classify = df_write.apply(geticommit, axis =1 )
#
#    dataframe_classify = dataframe_classify.assign(nWords = lambda x : x['Message'].str.split().str.len() )
#    word_features = word_vectorizer.transform(dataframe_classify['Message'].astype(str))
    
    for i in ["Novelty", "Usefulness"]:
        '''MLPClassifier'''
        print("************ MLP Classifier *************")
        del acuracy[:] 
        del macc[:] 
        #Stage 1  
        print("*** MLP Classifier - One stage - "+i+"5 ***")
        p_train5,p_test5, acc, classifier_mlp1s5 = MLPmodel(train_x, df_train[i], test_x, df_test[i])
        #Stage 2
        df_train_prob = pd.DataFrame(p_train5, columns = ['p1','p2','p3','p4','p5'])
        train_x_s2 = pd.concat([df_train_prob,df_train['Files Changed'],df_train['nAdditions'],df_train['nDeletions'],df_train['Parents'],df_train['nWords']], axis=1)
        df_test_prob = pd.DataFrame(p_test5, columns = ['p1','p2','p3','p4','p5'])
        test_x_s2 = pd.concat([df_test_prob,df_test['Files Changed'],df_test['nAdditions'],df_test['nDeletions'],df_test['Parents'],df_test['nWords']], axis=1)
        print("*** MLP Classifier - Two stage - "+i+"5 ***")
        p_train_s2,p_test_s2, acc, classifier_mlp2s5 = MLPmodel(train_x_s2, df_train[i+'3'], test_x_s2, df_test[i+'3'], LCurve = False)
        acuracy.append(["MLP Classifier - Two stage - "+i+"5", float(acc),classifier_mlp1s5, classifier_mlp2s5])
        print("MLP Classifier - Two stage - "+i+"5 ", acc)


        print("*** MLP Classifier - One stage - "+i+"3 ***")
        p_train3,p_test3, acc, classifier_mlp1s3 = MLPmodel(train_x, df_train[i+'3'], test_x, df_test[i+'3'])
        acuracy.append(["MLP Classifier - One stage - "+i+"3", float(acc), classifier_mlp1s3])
        
        #Stage 2
        df_train_prob = pd.DataFrame(p_train3, columns = ['p1','p2','p3'])
        train_x_s2 = pd.concat([df_train_prob,df_train['Files Changed'],df_train['nAdditions'],df_train['nDeletions'],df_train['Parents'],df_train['nWords']], axis=1)
        df_test_prob = pd.DataFrame(p_test3, columns = ['p1','p2','p3'])
        test_x_s2 = pd.concat([df_test_prob,df_test['Files Changed'],df_test['nAdditions'],df_test['nDeletions'],df_test['Parents'],df_test['nWords']], axis=1)
        print("*** MLP Classifier - Two stage - "+i+"3 ***")
        p_train_s2,p_test_s2, acc, classifier_mlp2s3 = MLPmodel(train_x_s2, df_train[i+'3'], test_x_s2, df_test[i+'3'], LCurve = False)
        acuracy.append(["MLP Classifier - Two stage - "+i+"3", float(acc),classifier_mlp1s3, classifier_mlp2s3])
        print("MLP Classifier - Two stage - "+i+"3 ", acc)
    
        # USE 1S-5p, 2S - 3p MLP classifier for classifying the commits
#        p_classify5 = classifier_mlp1s5.predict_proba(word_features)
#        df_classify_prob = pd.DataFrame(p_classify5, columns = [i+'p1',i+'p2',i+'p3',i+'p4',i+'p5'])
#        classify_x_s1 = pd.DataFrame(pd.concat([df_classify_prob,dataframe_classify['Files'],dataframe_classify['Added'],dataframe_classify['Deleted'],dataframe_classify['Parents'],dataframe_classify['nWords']], axis=1) ).fillna(0)
#        p_classify_s2  = classifier_mlp2s5.predict_proba(classify_x_s1)
#        classify_x_s2  = pd.DataFrame(p_classify_s2, columns = [i+'s2p1',i+'s2p2',i+'s2p3'])
        
#        df_classify = pd.concat([df_classify, classify_x_s2], axis=1)
        
        macc = max(acuracy, key=lambda x: x[1])
#        print("MAX ACCURACY - = ",macc)
        macc_l.append([macc[0],macc[1],macc[2]]) 
    
#    print(df_write.shape[0],df_classify.shape[0])
#    df_write = pd.concat([df_write,df_classify], axis=1)
#    print(df_write.shape[0])
#    df_write.to_excel(COMMIT2_XLSX)   
#    print(macc_l)

if __name__ == '__main__':
  main()
  