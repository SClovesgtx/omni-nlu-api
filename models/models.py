from joblib import load
from tensorflow.keras.models import load_model
import os

local_path = os.path.dirname(os.path.abspath(__file__))


def load_models(workspace_id):
    svm = load(
        local_path
        + "/polySVM/trained_models/svm-{workspace_id}.joblib".format(
            workspace_id=workspace_id
        )
    )
    logit = load(
        local_path
        + "/multinomialLogit/trained_models/logit-{workspace_id}.joblib".format(
            workspace_id=workspace_id
        )
    )
    cnn = load_model(
        local_path
        + "/cnn/trained_models/cnn-{workspace_id}.h5".format(workspace_id=workspace_id)
    )
    return svm, logit, cnn
