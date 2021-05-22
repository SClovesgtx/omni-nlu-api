from sklearn.linear_model import LogisticRegression
from joblib import dump
import numpy as np
import os

local_path = os.path.dirname(os.path.abspath(__file__))


def train_LogisticRegression(**kwargs):
    grid = GridSearchCV(
            estimator=LogisticRegression(**kwargs),
            param_grid={'class_weight': [{0: 1, 1: v} for v in np.linspace(1, 20, 30)]},
            scoring={'precision': make_scorer(precision_score), 
                    'recall': make_scorer(recall_score),
                    'min_both': min_recall_precision
            },
            refit='min_both',
            return_train_score=True,
            cv=5,
            n_jobs=-1
    )
    grid.fit(X, y);
    else:
        model = LogisticRegression(multi_class="multinomial")
    return set_logit