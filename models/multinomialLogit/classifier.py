from sklearn.linear_model import LogisticRegression
from joblib import dump
import numpy as np
import os

local_path = os.path.dirname(os.path.abspath(__file__))

def train_logit_model(X_train, y_train, X_test, y_test, workspace_id, settings=None):
    y_train = np.array([np.argmax(onehot) for onehot in y_train.tolist()])
    y_test = np.array([np.argmax(onehot) for onehot in y_test.tolist()])
    # see https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.LogisticRegression.html
    if settings != None:
        model = LogisticRegression(
                        multi_class='multinomial',
                        **settings)
    else:
        model = LogisticRegression(multi_class='multinomial')
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    accuracy = np.sum(y_pred == y_test) / y_test.shape[0]
    dump(model, local_path+'/trained_models/logit-{workspace_id}.joblib'.format(workspace_id=workspace_id))
    return accuracy
