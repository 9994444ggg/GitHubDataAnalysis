# -*- coding: utf-8 -*-
"""
Created on Wed Jan  2 10:30:42 2019

@author: kmpoo

This is the code that tries to build a clasifier model for creativity and uses it to label any commit.
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
from numpy import array
from numpy import float32
from sklearn.metrics import f1_score

TRAIN_XL = r'C:\Data\092019 CommitInfo\JavaSampling\ML\LabelDatset.xlsx'
TRAIN_XL_TEXT = r'C:\Data\092019 CommitInfo\JavaSampling\ML\LabelDatset_Text.xlsx'
LABELFULL_XL = r'C:\Data\092019 CommitInfo\JavaSampling\ML\PreProcessed.xlsx'
TRAINSET_XL = r'C:\Data\092019 CommitInfo\JavaSampling\ML\Trainset.xlsx'
TESTSET_XL = r'C:\Data\092019 CommitInfo\JavaSampling\ML\Testset.xlsx'
TEST = r'C:\Data\092019 CommitInfo\JavaSampling\ML\Test.xlsx'

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
    text_file = ['txt','md']
    if pd.isna(x['PINDEX']) and pd.notna(x['OPEN_ISSUES']):
        files = ast.literal_eval(x['OPEN_ISSUES'])
        for i in files:
            l = i.split('.')
            if len(l) > 1:
                if l[1].lower() not in text_file:
                    return pd.Series([x['PUSHED_DATE'],x['MAIN_LANGUAGE'],x['NO_LANGUAGES'],x['SCRIPT_SIZE'],x['STARS'],x['SUBSCRIPTIONS']], index=['Comments','Message','Added','Deleted','Parents','Files'])

    return pd.Series([np.NaN,np.NaN,np.NaN,np.NaN,np.NaN,np.NaN], index=['Comments','Message','Added','Deleted','Parents','Files'])
    
def getVDF(TRAIN_XL):
    """Get data from the training sample CSV and perform various cleaning and data preprocessing"""
    dataframe = pd.read_excel(TRAIN_XL, sep=",",error_bad_lines=False,header= 0,  encoding = "Latin1")

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
    
    # Convert the number of lines of code into nChanges, nAdditions, nDeletions

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
    dataframe = dataframe.assign(nWords = lambda x : x['C_Description'].str.split().str.len() )
#    dataframe_sd = dataframe.drop(dataframe[dataframe.CommitType.astype(int) == 3].index)

    return dataframe

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

def organizevectors(df):
    
    df['lVec'] = df['VECTORS'].apply(lambda x : dict(eval(x))).apply(pd.Series)
    df= pd.concat([df,(df['lVec'].apply(pd.Series))], axis = 1)
#    print (df)
    return df['lVec'].apply(pd.Series)
    
def main():
    pd.options.display.max_rows = 10
    pd.options.display.float_format = '{:.3f}'.format
    vector_dataframe = getVDF(TRAIN_XL)
    text_dataframe = getVDF(TRAIN_XL_TEXT)
#    vector_dataframe  = organizevectors(vector_dataframe)
    
   # Save the full labeled data sample post processing in CSV
#    vector_dataframe = vector_dataframe.drop_duplicates(subset = ['C_Description'])
    vector_dataframe.to_excel(LABELFULL_XL)

    #Split vector data frame into training and test samples
    df_train, df_test = train_test_split(vector_dataframe, test_size=0.2)
    t_df_train, t_df_test = train_test_split(text_dataframe , test_size=0.2)
    #Reset the indices for merging other features later on
    df_train=df_train.reset_index()
    df_test = df_test.reset_index()
    
    t_df_train=t_df_train.reset_index()
    t_df_test = t_df_test.reset_index()
    #Create new CSV represnting the training and testing samples
    df_train.to_excel(TRAINSET_XL)
    df_test.to_excel(TESTSET_XL)
    #Convert description text into a vetor of features. Train_x,test_x are in sparse matrix format
    v_train_x, v_test_x, v_word_vectorizer = vectordsc(vector_dataframe['C_Description'], df_train['C_Description'], df_test['C_Description'] )
    t_train_x, t_test_x, t_word_vectorizer = vectordsc(text_dataframe['C_Description'], t_df_train['C_Description'], t_df_test ['C_Description'] )


    acuracy = list()
    macc = list()
    macc_l = list()
#    df_classify = pd.DataFrame()
#    df_write = pd.read_excel(COMMIT_XLSX, sep=",",error_bad_lines=False,header=0,  encoding = "Latin1")
#    dataframe_classify = df_write.apply(geticommit, axis =1 )
#    dataframe_classify = dataframe_classify.assign(nWords = lambda x : x['Message'].str.split().str.len() )
#    word_features = word_vectorizer.transform(dataframe_classify['Message'].astype(str))

    for i in ["Novelty", "Usefulness"]:
        '''MLPClassifier'''
        print("************ TEXT ONLY *************")
        print("************ MLP Classifier *************")
        del acuracy[:] 
        del macc[:] 
        #Stage 1  
        print("*** MLP Classifier - One stage - "+i+"5 ***")
        print("*** TEXT ***")
        tp_train5,tp_test5, acc, classifier_mlp1s5 = MLPmodel(t_train_x, t_df_train[i], t_test_x, t_df_test[i])
        
        print("*** MLP Classifier - One stage - "+i+"3 ***")
        print("*** TEXT ***")
        tp_train3,tp_test3, acc, classifier_mlp1s3 = MLPmodel(t_train_x, t_df_train[i+'3'], t_test_x, t_df_test[i+'3'])
        

    for i in ["Novelty", "Usefulness"]:
        '''MLPClassifier'''
        print("************ CODE ONLY *************")
        print("************ MLP Classifier *************")
        #Stage 1  
        print("*** MLP Classifier - One stage - "+i+"5 ***")
        c_vec_train = organizevectors(df_train)
        c_vec_test = organizevectors(df_test)       
        print("*** CODE ***")
        vp_train5,vp_test5, acc, classifier_mlp1s5_vec = MLPmodel(c_vec_train, df_train[i], c_vec_test, df_test[i])
        grp_train = c_vec_train.groupby('SHA').mean()
        grp_train.to_excel(TEST)
        return
        """       
        print("*** MLP Classifier - Two stage - "+i+"5 ***")        #Stage 2
        print("*** TEXTPROB + CVEC ***")
        df_train_prob = pd.DataFrame(tp_train5, columns = ['p1','p2','p3','p4','p5'])
        train_x_s2 = pd.concat([df_train_prob,c_vec_train], axis=1)
        df_test_prob = pd.DataFrame(tp_test5, columns = ['p1','p2','p3','p4','p5'])
        test_x_s2 = pd.concat([df_test_prob,c_vec_test], axis=1)
        tvp_train_s2,tvp_test_s2, acc, classifier_mlp2s5 = MLPmodel(train_x_s2, df_train[i], test_x_s2, df_test[i], LCurve = False)
#        acuracy.append(["MLP Classifier - Two stage - "+i+"5", float(acc),classifier_mlp1s5, classifier_mlp2s5])
        
        df_train_prob_vec = pd.DataFrame(vp_train5, columns = ['cp1','cp2','cp3','cp4','cp5'])
        train_x_s2_cv = pd.concat([df_train_prob,df_train_prob_vec], axis=1)
        df_test_prob_vec = pd.DataFrame(vp_test5, columns = ['cp1','cp2','cp3','cp4','cp5'])
        test_x_s2_cv = pd.concat([df_test_prob,df_test_prob_vec], axis=1)
        print("*** TEXTPROB + CVECPROB ***")
        tvp2_train_s2,tvp2_test_s2, acc, classifier_mlp2s5 = MLPmodel(train_x_s2_cv, df_train[i], test_x_s2_cv, df_test[i], LCurve = False)
        
        """      
        print("*** MLP Classifier - One stage - "+i+"3 ***")
        print("*** CODE ***")
        tp2_train3,tp2_test3, acc, classifier_mlp1s5 = MLPmodel(c_vec_train,  df_train[i+'3'], c_vec_test, df_test[i+'3'])

        """        
#        acuracy.append(["MLP Classifier - One stage - "+i+"3", float(acc), classifier_mlp1s3])
        
        #Stage 2
        df_train_prob = pd.DataFrame(p_train3, columns = ['p1','p2','p3'])
        df_train_prob_vec = pd.DataFrame(p2_train3, columns = ['cp1','cp2','cp3'])
        train_x_s2 = pd.concat([df_train_prob,c_vec_train], axis=1)
        df_test_prob = pd.DataFrame(p_test3, columns = ['p1','p2','p3'])
        df_test_prob_vec = pd.DataFrame(p2_test3, columns = ['cp1','cp2','cp3'])
        test_x_s2 = pd.concat([df_test_prob,c_vec_test], axis=1)
        print("*** MLP Classifier - Two stage - "+i+"3 ***")
        print("*** TEXTPROB + CVEC ***")
        p3_train_s2,p3_test_s2, acc6, classifier_mlp2s3 = MLPmodel(train_x_s2, df_train[i+'3'], test_x_s2, df_test[i+'3'], LCurve = False)
#        acuracy.append(["MLP Classifier - Two stage - "+i+"3", float(acc),classifier_mlp1s3, classifier_mlp2s3])
        print("*** TEXTPROB + CVECPROB ***")
        train_x_s2_2 = pd.concat([df_train_prob,df_train_prob_vec ], axis=1)
        test_x_s2_2 = pd.concat([df_test_prob, df_test_prob_vec], axis=1)
        p3_train_s2,p3_test_s2, acc6, classifier_mlp2s3 = MLPmodel(train_x_s2_2, df_train[i+'3'], test_x_s2_2, df_test[i+'3'], LCurve = False)
 
        """

if __name__ == '__main__':
  main()
  