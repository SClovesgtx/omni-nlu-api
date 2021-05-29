import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn import svm


def train_logistic_regression(X, y, **hyper_parameters):
    model = LogisticRegression(**hyper_parameters)

    model.fit(X, y.intents)
    return model


def train_svm(X, y, **hyper_parameters):
    model = svm.SVC(**hyper_parameters)

    model.fit(X, y.intents)
    return model
