#!/usr/bin/python

import sys
import pickle
import pandas as pd
sys.path.append("../tools/")

from feature_format import featureFormat, targetFeatureSplit
from tester import dump_classifier_and_data
from helper_functions import *
import matplotlib.pyplot
from sklearn.feature_selection import SelectKBest
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from numpy import mean
from sklearn import cross_validation
from sklearn.metrics import accuracy_score, precision_score, recall_score
from sklearn.cluster import KMeans
from sklearn.pipeline import Pipeline
from sklearn.decomposition import PCA
from sklearn.svm import SVC
from sklearn import tree
from sklearn.grid_search import GridSearchCV
from sklearn.preprocessing import MinMaxScaler
from sklearn.feature_selection import f_classif
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from tester import test_classifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.cross_validation import StratifiedShuffleSplit
from sklearn.naive_bayes import GaussianNB
from sklearn.neighbors import KNeighborsClassifier
from sklearn.ensemble import AdaBoostClassifier

### Task 1: Select what features you'll use.
### features_list is a list of strings, each of which is a feature name.
### The first feature must be "poi".
#features_list = ['poi','salary'] # You will need to use more features ###We will come back to this later
target_label = 'poi'
email_features_list = [
    'from_messages',
    'from_poi_to_this_person',
    'from_this_person_to_poi',
    'shared_receipt_with_poi',
    'to_messages',
    ]
financial_features_list = [
    'bonus',
    'deferral_payments',
    'deferred_income',
    'director_fees',
    'exercised_stock_options',
    'expenses',
    'loan_advances',
    'long_term_incentive',
    'other',
    'restricted_stock',
    'restricted_stock_deferred',
    'salary',
    'total_payments',
    'total_stock_value',]

features_list = [target_label] + financial_features_list + email_features_list

### Load the dictionary containing the dataset
with open("final_project_dataset.pkl", "r") as data_file:
    data_dict = pickle.load(data_file)
## 1.1 Data exploration
print "--------Data Exporation-----------------\n"
## Check the first 5 entries in the data-dict to get a feel of the structure
first_5_items = take(5, data_dict.iteritems())
print "First 5 items in our data dictionary: \n", first_5_items, "\n"

## 1.2 Basic statistics of the data structure
print "------------Data Structure-------------------\n"
## Total number of data points
print "Number of total records in the dataset:", len(data_dict.keys()), "\n"
##allocation across classes (POI/non-POI)
count_poi = 0
for person in data_dict.iterkeys():
    if data_dict[person]["poi"] == 1:
        count_poi += 1

print "The number of poi in the dataset are: ", count_poi, "\n"
print "The number of non-poi in the dataset are:", (len(data_dict.keys()) - count_poi), "\n"

##number of features
print "Number of total features per record are: ", len(data_dict['METTS MARK'].values()), "\n"

##Features with many missing values
all_features = data_dict['METTS MARK'].keys()
#print all_features

#Create a dictionary to list the count of missing data for each feature
missing_feature_list = {}

for feature in all_features:
    missing_feature_list[feature] = 0

for k in data_dict.iterkeys():
    for feature in all_features:
        if data_dict[k][feature] == "NaN":
            missing_feature_list[feature] += 1

### Print results
print "Record of missing values in each feature:", "\n"
print pd.DataFrame(missing_feature_list.items(), columns=['Feature', "Missing Values"]).sort_values(by=["Missing Values"],
                                                                                           ascending=False)

### Task 2: Remove outliers
features = ["salary", "bonus"]
data = featureFormat(data_dict, features)

# Visualize outlier
for point in data:
    salary = point[0]
    bonus = point[1]
    matplotlib.pyplot.scatter( salary, bonus )

matplotlib.pyplot.xlabel("salary")
matplotlib.pyplot.ylabel("bonus")
matplotlib.pyplot.show()

# From the plot we see that the TOTAL column is an outlier
#Remove unexpected names(outliers) from our data
data_dict.pop("TOTAL", 0)
data_dict.pop("THE TRAVEL AGENCY IN THE PARK", 0)
data = featureFormat(data_dict, features)

for point in data:
    salary = point[0]
    bonus = point[1]
    matplotlib.pyplot.scatter( salary, bonus )

matplotlib.pyplot.xlabel("salary")
matplotlib.pyplot.ylabel("bonus")
matplotlib.pyplot.show()

### Task 3: Create new feature(s)
## Store to my_dataset for easy export below.
my_dataset = data_dict

## Create new feature for exploration
def computeFraction(poi_messages, all_messages):
    """ given a number messages to/from POI (numerator)
        and number of all messages to/from a person (denominator),
        return the fraction of messages to/from that person
        that are from/to a POI
   """
    fraction = 0.
    if poi_messages != "NaN" or all_messages != "NaN":
        fraction = float(poi_messages) / float(all_messages)

    return fraction

for name in my_dataset:
    data_point = my_dataset[name]
    from_poi_to_this_person = data_point["from_poi_to_this_person"]
    to_messages = data_point["to_messages"]
    fraction_from_poi = computeFraction( from_poi_to_this_person, to_messages )
    my_dataset[name]["fraction_from_poi"] = fraction_from_poi

    from_this_person_to_poi = data_point["from_this_person_to_poi"]
    from_messages = data_point["from_messages"]
    fraction_to_poi = computeFraction( from_this_person_to_poi, from_messages )
    my_dataset[name]["fraction_to_poi"] = fraction_to_poi

## Update the feature list
my_feature_list = features_list + ["fraction_from_poi"] + ["fraction_to_poi"]

print my_feature_list

### Extract features and labels from dataset for local testing
data = featureFormat(my_dataset, my_feature_list, sort_keys = True)
labels, features = targetFeatureSplit(data)

from sklearn.cross_validation import train_test_split
features_train, features_test, labels_train, labels_test = \
    train_test_split(features, labels, test_size=0.3, random_state=42)

### Task 4: Try a varity of classifiers
### Please name your classifier clf for easy export below.
### Note that if you want to do PCA or other multi-stage operations,
### you'll need to use Pipelines. For more info:
### http://scikit-learn.org/stable/modules/pipeline.html
from sklearn import preprocessing
'''
scaler = preprocessing.MinMaxScaler()
skb = SelectKBest(k = 5)
clf = Pipeline(steps=[('scaling',scaler),("SKB", skb), ("NaiveBayes", GaussianNB())])
clf.fit(features_train, labels_train)
'''
cv_strata = StratifiedShuffleSplit(labels,100, test_size=0.3, random_state=24)

# build a pipeline for find the Kbest feature
fs_pipe = Pipeline(steps=[('min_max_scaler', MinMaxScaler()),
                        ('select_KBest', SelectKBest()),
                        #('pca', PCA()),
                       ('gaussian_nb', GaussianNB()),
                        #('kmeans', KMeans()),
                        #('svc', SVC()),
                        #('tree', DecisionTreeClassifier()),
                        #('random_forest', RandomForestClassifier())
                        # ('knc', KNeighborsClassifier()),
                        #('ada', AdaBoostClassifier()),
                        #('logistic_regression', LogisticRegression())
                      ])
parameters = dict(select_KBest__k = [4,5,6],
                  #pca__n_components= [5],
                  #pca__whiten = [False],
                  #kmeans__n_clusters = [3,4],
                  #kmeans__n_init = [2,5,8],
                  # svc__gamma = [0.01, 0.1, 1, 10.0, 50.0, 100.0],
                  # svc__C = [0.1, 1, 2, 4, 6, 8, 10],
                  # svc__kernel = ['rbf','poly','sigmoid'],
                  # tree__max_features = [1],
                  # tree__min_samples_split = [10],
                  # tree__criterion = ['gini'],
                  #random_forest__n_estimators = [5,10],
                  #random_forest__max_features = [1],
                  #random_forest__criterion = ['gini']
                  # knc__n_neighbors = [2,3,5],
                  # knc__algorithm = ['auto'],
                  # knc__leaf_size = [1,2,3]
                  #ada__n_estimators = [30,40,90],
                  #ada__learning_rate = [5],
                  #ada__algorithm = ['SAMME.R']
                  #logistic_regression__C=[0.5,1,2,3,4,5],
                  #logistic_regression__class_weight=[{True: 2, False: 1}],
                  #logistic_regression__fit_intercept=[False],
                  #logistic_regression__dual = [True],
                  #logistic_regression__penalty = ['l2']
                  )

grid = GridSearchCV(fs_pipe, parameters, cv=cv_strata ,scoring="f1")
grid.fit(features, labels)
print "Best estimator parameters: \n", grid.best_estimator_

print 'Best parameters set:'
best_parameters = grid.best_estimator_.get_params()
for param_name in sorted(parameters.keys()):
       print '\t%s: %r' % (param_name, best_parameters[param_name])


#print the best features and their scores.
k_best_features= grid.best_params_['select_KBest__k']
kb_clf=SelectKBest(f_classif, k=k_best_features)
kb_clf.fit_transform(features, labels)
feature_scores = kb_clf.scores_
features_selected=[my_feature_list[i+1]for i in kb_clf.get_support(indices=True)]
features_scores_selected=[feature_scores[i]for i in kb_clf.get_support(indices=True)]
print ' '
print 'Selected Features using K-Best', features_selected
print 'Feature Scores', features_scores_selected

# Select the final classifier
clf = grid.best_estimator_

# Evaluation of the model
print ' '
print "Testing Report:\n"
test_classifier(clf, my_dataset, my_feature_list)

### Task 6: Dump your classifier, dataset, and features_list so anyone can
### check your results. You do not need to change anything below, but make sure
### that the version of poi_id.py that you submit can be run on its own and
### generates the necessary .pkl files for validating your results.

dump_classifier_and_data(clf, my_dataset, my_feature_list)
