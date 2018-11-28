# -*- coding: utf-8 -*-
"""
Created on Wed Nov 21 08:43:03 2018

@author: Adam Kehoe
"""
#6wkxWezoP3_qUvsA73q4

import quandl
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from math import *
from sklearn.metrics import mean_squared_error
from sklearn.preprocessing import MinMaxScaler
import tensorflow as tf
from keras.models import Sequential
from keras.layers import Dense
from keras.layers import LSTM


# Calculates expected value of an option given the current price,
# strike price, price of the option, and the days until expiration.
# Method is simple at the moment and involves calculating the historical "n"
# day percentage changes to form a probability distribution from which the 
# expected value of the option can be calculated.

def option_EV(current_price, strike_price, prem, n):

    quandl.ApiConfig.api_key = '6wkxWezoP3_qUvsA73q4'

    apple = quandl.get("WIKI/AAPL", api_key = '6wkxWezoP3_qUvsA73q4')
    aapl = pd.DataFrame(data=apple)
    dist = []
    
    for i in range(len(aapl)-n):
        dist.append((aapl['Close'][i+n] - aapl['Close'][i])/aapl['Close'][i])
        dist[i] =  round(dist[i],2)
    
    # having rounded to the nearest hundredths digit, can form a reasonable 
    # probability distribution from the number of counts of each percentage change occurence given a large enough
    # dataset.
    counts = {}
    probs = []
    for i in dist:
        counts[i] = counts.get(i, 0) + 1
    countslist = list(counts.keys())
    
    # calculate probabilities based on the number of counts of percentage changes
    for i, j in enumerate(counts):   
        probs.append(counts[j]/len(dist))
        
    # calculate percentage change to be in the money
    ITM = (strike_price - current_price)/(current_price)
    # calculate percentage change to break even
    BE = ITM + prem/(current_price)
    total_expected = 0
    for i, j in enumerate(counts):
        if countslist[i] >= ITM:
            total_expected += ((1+countslist[i])*(current_price)-strike_price - prem)*probs[i]
        if countslist[i] < ITM:
            total_expected -= prem*probs[i]
            
    return total_expected
    
        
# Histogram plot to view roughly normal distribution   
def histogram(dist):
    n, bins, patches = plt.hist(x=dist, bins='auto', color='#0504aa',
                                alpha=0.7, rwidth=0.85)
    plt.grid(axis='y', alpha=0.75)
    plt.xlabel('Value')
    plt.ylabel('Frequency')
    plt.title('Distribution')
    plt.text(23, 45, r'$\mu=15, b=3$')
    maxfreq = n.max()


# In progress: implementation of long short term memory network
def network(dist):
    train, test = dist[0:-1000], dist[-1000:]
    
    # frame a sequence as a supervised learning problem
    def timeseries_to_supervised(data, lag=1):
    	df = pd.DataFrame(data)
    	columns = [df.shift(i) for i in range(1, lag+1)]
    	columns.append(df)
    	df = pd.concat(columns, axis=1)
    	df.fillna(0, inplace=True)
    	return df
    
    # transform to supervised learning
    X = dist
    supervised = timeseries_to_supervised(X, 1)
    print(supervised.head())
    
    X = X.reshape(len(X), 1)
    scaler = MinMaxScaler(feature_range=(-1, 1))
    scaler = scaler.fit(X)
    scaled_X = scaler.transform(X)
    scaled_series = pd.Series(scaled_X[:, 0])
    inverted_X = scaler.inverse_transform(scaled_X)
    inverted_series = pd.Series(inverted_X[:, 0])
    
    X, y = train[:, 0:-1], train[:, -1]
    X = X.reshape(X.shape[0], 1, X.shape[1])
    layer = LSTM(neurons, batch_input_shape=(batch_size, X.shape[1], X.shape[2]), stateful=True)
    
    model = Sequential()
    model.add(LSTM(neurons, batch_input_shape=(batch_size, X.shape[1], X.shape[2]), stateful=True))
    model.add(Dense(1))
    model.compile(loss='mean_squared_error', optimizer='adam')
    
    
