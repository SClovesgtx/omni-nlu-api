# standard library imports
import time
import sys
import os

work_dir = os.getcwd()
sys.path.append("./src/")

# third party imports
import numpy as np
from flask import Blueprint, request, Response

train_app = Blueprint("train_app", __name__)

# local imports
from utils.split_data import (
    update_intents_with_messing_examples,
    train_test_split,
    get_train_test,
)
from feature_encoding.tfidf.pipeline import (
    apply_pipe_tfidf_feature_encoding,
)
from models.BM25.classifier import (
    bm25_accuracy,
)
from models.cnn.classifier import train_cnn_model
from models.multinomialLogit.classifier import train_logit_model
from models.polySVM.classifier import train_svm_model
from elasticsearch_db.elasticsearch import elastic_conection
from elasticsearch_db.elasticsearch import get_nlp_model

es = elastic_conection()


def read_recipe(index):
    cnn_settings = dict()
    logit_settings = dict()
    svm_settings = dict()
    for setting in index.recipe:
        if setting["model"] == "cnn":
            cnn_settings = setting["settings"]
        elif setting["model"] == "logit":
            logit_settings = setting["settings"]
        elif setting["model"] == "svm":
            svm_settings = setting["settings"]
    return cnn_settings, logit_settings, svm_settings


def read_td_idf_train_test_data(workspace_id):
    path = "./src/feature_encoding/tfidf/resources"
    with open(
        path + "/X_train_tfidf_{workspace_id}.npy".format(workspace_id=workspace_id),
        "rb",
    ) as f:
        X_train = np.load(f)

    with open(
        path + "/y_train_tfidf_{workspace_id}.npy".format(workspace_id=workspace_id),
        "rb",
    ) as f:
        y_train = np.load(f)

    with open(
        path + "/X_test_tfidf_{workspace_id}.npy".format(workspace_id=workspace_id),
        "rb",
    ) as f:
        X_test = np.load(f)

    with open(
        path + "/y_test_tfidf_{workspace_id}.npy".format(workspace_id=workspace_id),
        "rb",
    ) as f:
        y_test = np.load(f)

    return X_train, y_train, X_test, y_test


@train_app.route("/nlp_models/resources/train", methods=["POST"])
def train_nlp_models():
    if request.method == "POST":
        workspace_id = request.args.get("workspace_id")
        index, exist = get_nlp_model(es, workspace_id=workspace_id)
        if not exist:
            return index

        update_intents_with_messing_examples(index, es)
        time.sleep(15)
        train_test_split(index, es)
        time.sleep(30)
        train_examples, test_examples = get_train_test(index, es)
        apply_pipe_tfidf_feature_encoding(train_examples, test_examples, index, es)
        X_train, y_train, X_test, y_test = read_td_idf_train_test_data(
            index.workspace_id
        )
        bm25_acc = bm25_accuracy(test_examples, index, es)
        cnn_settings, logit_settings, svm_settings = read_recipe(index)
        cnn_accuracy = train_cnn_model(
            X_train=X_train,
            y_train=y_train,
            X_test=X_test,
            y_test=y_test,
            workspace_id=index.workspace_id,
            settings=cnn_settings,
        )
        logit_accuracy = train_logit_model(
            X_train=X_train,
            y_train=y_train,
            X_test=X_test,
            y_test=y_test,
            workspace_id=index.workspace_id,
            settings=logit_settings,
        )
        svm_accuracy = train_svm_model(
            X_train=X_train,
            y_train=y_train,
            X_test=X_test,
            y_test=y_test,
            workspace_id=index.workspace_id,
            settings=svm_settings,
        )
        # xgb_accuracy = train_xgboost_model(X_train, y_train, X_test, y_test, index.workspace_id)
        acc = {
            "bm25_accuracy": bm25_acc,
            "cnn_accuracy": cnn_accuracy,
            "logit_accuracy": logit_accuracy,
            # "xgb_accuracy": xgb_accuracy,
            "svm_accuracy": svm_accuracy,
        }
        es.update(
            index=index.index_name,
            id=index.workspace_id,
            body={"doc": {"accuracies": acc}},
        )
        return acc
