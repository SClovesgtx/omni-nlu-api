from sklearn.linear_model import LogisticRegression
from joblib import dump
import numpy as np
import os

local_path = os.path.dirname(os.path.abspath(__file__))


def set_logit(settings=None):
    # see https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.LogisticRegression.html
    if settings != None:
        model = LogisticRegression(multi_class="multinomial", **settings)
    else:
        model = LogisticRegression(multi_class="multinomial")
    return set_logit
