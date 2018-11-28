# -*- coding: utf-8 -*-
"""
Created on Sun Nov  4 13:45:51 2018

@author: Adam Kehoe
"""

import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.feature_selection import RFE, SelectKBest, chi2
from sklearn.linear_model import LogisticRegression
import matplotlib.pyplot as plt
import math


performance_data = pd.read_csv("performance_data.csv")
weather_data = pd.read_csv("weather_data.csv")

# choosing which variables to analyze
df = performance_data[['YIELD','HYBRID_ID','ELEVATION','CLAY','SILT','SAND','AWC','PH','OM','CEC','KSAT']].copy()

features = ['CLAY', 'SILT', 'SAND', 'AWC', 'PH', 'OM', 'CEC', 'KSAT']

# create list of hybrid types
hybridlist = []

for i in range(len(df)-1):
    if df.HYBRID_ID[i] not in hybridlist:
        hybridlist.append(df.HYBRID_ID[i])

ends = np.zeros(len(hybridlist)+1)
  
j = 0

# since data is ordered by HYBRID_ID, "ends" helps determine which indices
# are associated with which Hybrids. From there, in essence, new dataframes can be created
# and analyzed for each hybrid. Done this way such that the whole dataset doesn't need to
# be constantly checked for HYBRID_ID matching as this is calculated before hand
for k in range(len(hybridlist)):
    while hybridlist[k] == df['HYBRID_ID'][j]:
        j +=1
        if j == len(df):
            break
    ends[k+1] = j
    
    
# feature selction with SelectKBest
X = df[features].values
X=X.astype('int')
Y = df['YIELD'].values
Y=Y.astype('int')
best = SelectKBest(chi2, k=3).fit_transform(X,Y)

# feature selection by recursive feature elimination
X = df[features].values
X=X.astype('int')
Y = df['YIELD'].values
Y=Y.astype('int')
model = LogisticRegression() 
rfe = RFE(model, 3)
fit = rfe.fit(X, Y)
print("Num Features: %d"% fit.n_features_)
print("Selected Features: %s"% fit.support_)
print("Feature Ranking: %s"% fit.ranking_)

# K means clustering
clmns = ['CLAY','SILT','SAND']
soildf = df[clmns].copy()
kmeans = KMeans(n_clusters=math.floor(math.sqrt(len(df)))).fit(soildf)
labels = kmeans.labels_
soildf['clusters'] = labels
clmns.extend(['clusters'])
print(soildf[clmns].groupby(['clusters']).mean())

for i in range(len(hybridlist)+1):
    currentdhybrid = df[ends[i]:ends[i+1]]

            
    
    
        
        

        
    
    