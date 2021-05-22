from sklearn import svm
import numpy as np
from sklearn.metrics import accuracy_score
from joblib import dump
import os

local_path = os.path.dirname(os.path.abspath(__file__))


def set_svm(settings=None):
    if settings != None:
        model = svm.SVC(kernel="poly", probability=True, **settings)
    else:
        model = svm.SVC(
            kernel="poly", probability=True, degree=1, coef0=0.0, random_state=42
        )
    return model
