import csv
import numpy as np

# Recursive Feature Elimination
from sklearn import datasets
from sklearn.feature_selection import RFE
from sklearn.linear_model import LogisticRegression
# load the iris datasets
#dataset = datasets.load_iris()
dataset = {}
file = open('pilotdataset.csv', 'r')
reader = csv.reader(file)
data_col = []
target_col = []
feature_names = []
index = 0
for csv_row in reader:
	if index == 0:
		for value in csv_row:
			feature_names.append(value)
		index += 1
		continue
	data_col.append(csv_row[0:len(csv_row)-1]) # store the attribute values
	target_col.append(csv_row[len(csv_row)-1]) # store the label
dataset['data'] = np.array(data_col)
dataset['target'] = np.array(target_col)
dataset['target_names'] = ['Complex', 'Simple']
dataset['feature_names'] = feature_names
dataset['DESCR'] = 'Data obtained from the pilot study'



# create a base classifier used to evaluate a subset of attributes
model = LogisticRegression()
# create the RFE model and select 3 attributes
rfe = RFE(model, 3)
print(dataset['data'])
#print(dataset.feature_names)
#print(type(dataset))
rfe = rfe.fit(dataset['data'], dataset['target'])
# summarize the selection of the attributes
print(rfe.support_)
print(rfe.ranking_)