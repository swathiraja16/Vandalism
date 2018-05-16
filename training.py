import cPickle
from collections import defaultdict
import math
import time
from sklearn import svm, preprocessing
import matplotlib.pyplot as plt
from sklearn.metrics import roc_curve
from sklearn.metrics import roc_auc_score
import pandas as pd
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import GaussianNB
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import LabelEncoder


training_data = pd.read_csv('processed_data.csv', delimiter=',')
#print " dataset size: ", training_data.shape

# encoding user,page features to numeric values
encoder = LabelEncoder()
training_data['username'] = encoder.fit_transform(training_data['username'])
training_data['pagetitle'] = encoder.fit_transform(training_data['pagetitle'])

# storing data in numpy array
xt = training_data.as_matrix(columns=['username', 'revtime', 'pagetitle', 'ntus', 'fm', 'crmv', 'crmf' , 'crms', 'crm'])
yt = training_data.as_matrix(columns=['vandal'])
# cross validation
x_train, x_test, y_train, y_test = train_test_split(xt, yt)

#scaling datasets
scaler = preprocessing.MinMaxScaler(feature_range=(0,1)).fit(x_train)
xt_train = scaler.transform(x_train)
xt_test = scaler.transform(x_test)

classifiers = []
classifiers.append(("DecisionTreeClassifier", DecisionTreeClassifier()))
classifiers.append(("RandomForestClassifier", RandomForestClassifier()))
classifiers.append(("MLPClassifier", MLPClassifier(hidden_layer_sizes=(8,8,8))))
classifiers.append(("LogisticRegression", LogisticRegression()))
classifiers.append(("GaussianNB", GaussianNB()))
#svm is running only with a smaller dataset so trained with a smaller data and stored
#classifiers.append(("SVM", svm.SVC()))
for cls in classifiers:
    print "****************Running classifier : %s****************************" % cls[0]
    start = time.time()
    classifier = cls[1].fit(xt_train, y_train.ravel())      
    end = time.time()
    print "Time for training: ", math.ceil((end - start)/60), " min"
    start = time.time()
    y_p = classifier.predict(xt_test)
    end = time.time()
    print "Time for predicting:", math.ceil((end - start)/60), " min"

    # prediction metrics
    print 'Prediction Accuracy :', accuracy_score(y_test, y_p)
    print "confusion matrix:"
    print(confusion_matrix(y_test, y_p))
    print "classification report:"
    print(classification_report(y_test, y_p))
    
#    #roc_curve
#    print ('ROC',roc_auc_score(y_test,y_p))
#    fpr, tpr, thresholds = roc_curve(y_test,y_p)    
#    print "fpr", fpr
#    print "tpr", tpr
#    plt.title('Receiver Operating Characteristic')
#    plt.plot(fpr,tpr)
#    plt.show() 
    
    # storing the model for future predictions
    loc = "trained_model_%s.obj"%cls[0]
    f = file(loc,"wb") 
    cPickle.dump(classifier, f, protocol=cPickle.HIGHEST_PROTOCOL)
    f.close()


