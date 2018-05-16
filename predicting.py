import cPickle
import math
import pandas as pd
import time
from sklearn import preprocessing
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report
from sklearn.preprocessing import LabelEncoder

models = []
models.append("DecisionTreeClassifier")
models.append("RandomForestClassifier")
models.append("MLPClassifier")
models.append("LogisticRegression")
models.append("GaussianNB")
models.append("SVM")

for model in models:
    print "**************Running trained model %s***************"% model
    loc = "trained_model_%s.obj"%model
    print 'loading learned model...'
    f = file(loc,"rb") # Specify file location
    clf = cPickle.load(f)
    f.close()
    print 'loaded model..'

    test_data = pd.read_csv('test.csv', delimiter=',')

    # encoding user,page features to numeric values
    encoder = LabelEncoder()
    test_data['username'] = encoder.fit_transform(test_data['username'])
    test_data['pagetitle'] = encoder.fit_transform(test_data['pagetitle'])

    xt = test_data.as_matrix(columns=['username', 'revtime', 'pagetitle', 'ntus', 'fm', 'crmv', 'crmf' , 'crms', 'crm'])
    yt = test_data.as_matrix(columns=['vandal'])

    # scaling testing data
    scaler = preprocessing.MinMaxScaler(feature_range=(0,1)).fit(xt)
    xtt = scaler.transform(xt)

    # Predict on test data
    start = time.time()
    y_p = clf.predict(xtt)
    end = time.time()
    #print y_p
    print "Time to predict test data: ", math.ceil((end - start)/60), " minutes"

    # prediction metrics
    print 'Prediction accuracy : ', accuracy_score(yt, y_p)
    print "confusion matrix:"
    print(confusion_matrix(yt, y_p))
    print "classification report:"
    print(classification_report(yt, y_p))
    
