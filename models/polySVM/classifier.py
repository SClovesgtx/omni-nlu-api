from sklearn import svm
import numpy as np
from sklearn.metrics import accuracy_score
from joblib import dump
import os

local_path = os.path.dirname(os.path.abspath(__file__))

def train_svm_model(X_train, y_train, X_test, y_test, workspace_id, settings=None):
    y_train = np.array([np.argmax(onehot) for onehot in y_train.tolist()])
    y_test = np.array([np.argmax(onehot) for onehot in y_test.tolist()])
    if settings != None:
        model = svm.SVC(    
                    kernel='poly', 
                    probability=True,
                    **settings) 
    else:
        model = svm.SVC(    
                    kernel='poly', 
                    probability=True,
                    degree=1, 
                    coef0=0.0, 
                    random_state=42) 
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    dump(model, local_path+'/trained_models/svm-{workspace_id}.joblib'.format(workspace_id=workspace_id))
    return accuracy
