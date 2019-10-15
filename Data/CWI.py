#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd


class Data:
    def __init__(self):
        pid = []
        word = []
        complexity = []
        gid = []
        self.dataset = pd.DataFrame(columns=['pid', 'word', 'complexity', 'gid'])
        df = pd.read_csv('RankedWordsFinal.csv')
        df.drop_duplicates(keep = 'first', subset=df.columns.difference(['complexity']),inplace = True)
        groups = pd.read_csv('Groups.csv')
        df['gid'] = ''
        for index, row in df.iterrows():
            if str(df.loc[index]['word']).find("_") != -1 or str(df.loc[index]['word']).find("-") != -1 or str(df.loc[index]['word']).strip().find(" ") != -1:
                print('INVALID: ', str(df.loc[index]['word']).replace("'",""))
                continue
            print('Appending: ', df.loc[index]['word'])
            word.append(str(df.loc[index]['word']).replace("'","").strip())
            pid.append(df.loc[index]['pid'])
            if df.loc[index]['complexity'] >= 3:
                complexity.append(1)
            else:
                complexity.append(0)
            g_index = groups.index[groups['pid'] == df.loc[index]['pid']].tolist()[0]
            gid.append(groups.loc[g_index]['gid'])

        self.dataset['pid'] = pid
        self.dataset['gid'] = gid
        self.dataset['word'] = word
        self.dataset['complexity'] = complexity



# In[2]:


import numpy as np

data_instance = Data()
#load the ranked dataset
dataset = data_instance.dataset
print(dataset)
print(len(dataset[dataset['complexity']==0]))
print(len(dataset[dataset['complexity']==1]))


# In[3]:


import csv
#TODO: remove akash's example

print(dataset.head())
#words = list(set(dataset['word'].tolist()))
#words = [word.replace("'","") for word in words]
#print(len(words))
#matrix = np.empty([100])
word_stats = dict()
rating = pd.DataFrame(columns=['gid', 'word', 'simple', 'complex'])
gid_list = list()
for index, row in dataset.iterrows():
    #if not rating[rating['gid'].str.contains(row['gid'])]:
        #rating[row['gid']] = dict()
        #fetch rows with the same gid
        if row['gid'] in gid_list:
            continue
        gid_list.append(row['gid'])
        print(gid_list)
        df_by_group = dataset[dataset['gid'] == row['gid']]
        #words = dict()
        for g_index, g_row in df_by_group.iterrows():
            rating_subset = rating[(rating['gid'] == row['gid']) & (rating['word'] == g_row['word'])]
            print(rating_subset)
            if g_row['complexity'] == 1:
                difficult = 1
                simple = 0
            else:
                difficult = 0
                simple = 1
            if len(rating_subset) == 0:
                rating = rating.append({'gid': row['gid'], 'word': g_row['word'], 'simple': simple, 'complex': difficult}, ignore_index=True)
            else:
                print('Index: ', rating_subset.index[0])
                rating.set_value(rating_subset.index[0], 'simple', int(rating.get_value(rating_subset.index[0], 'simple')) + simple)
                rating.set_value(rating_subset.index[0], 'complex', int(rating.get_value(rating_subset.index[0], 'complex')) + difficult)
                print(rating)
            if g_row['word'] not in word_stats:
                word_stats[g_row['word']] = 1
            else:
                word_stats[g_row['word']] = word_stats[g_row['word']] + 1
print(rating)
rating.to_csv('groupwise_data.csv')
open('wordstats.txt', 'w').write(str(word_stats))
print(word_stats)
#TODO:  create a matrix for calculating the coefficient for every group
#Calculate Fleiss' Kappa nad K's alpha


#array: number of raters who assigned word i to category j in each group of users(j=0 simple,1 complex


# In[ ]:
