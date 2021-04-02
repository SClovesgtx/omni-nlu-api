from elastic_db.elasticsearch import elastic_conection, NLPmodelIndex
from elastic_db.elasticsearch import get_nlp_model, pipeline_to_update_index
from elasticsearch.exceptions import NotFoundError
from flask import Flask, request, Response, jsonify
import numpy as np
from multiprocessing import Pool
from fuzzywuzzy import fuzz
import re
import traceback
import sys
import spacy
from spacy.matcher import PhraseMatcher
from spacy.tokens import Span
from utils.entities import SynonymMatcher, nlp, check_regex_pattern, entity_check
from utils.models import check_recipe
from utils.split_data import (
    update_intents_with_messing_examples,
    train_test_split,
    get_train_test,
)
from feature_encoding.tfidf.pipeline import (
    apply_pipe_tfidf_feature_encoding,
    get_tfidf_corpus,
    get_sentece_features,
    get_intents_dictionary,
)
from models.cnn.classifier import train_cnn_model
from models.multinomialLogit.classifier import train_logit_model
from models.polySVM.classifier import train_svm_model
from models.BM25.classifier import (
    find_intents_bm25,
    bm25_accuracy,
    bm25_result_to_vector,
)
from models.models import load_models
from typing import Tuple, List, Dict
import time
import os

local_path = os.path.dirname(os.path.abspath(__file__))

es = elastic_conection()
app = Flask(__name__)

# TYPING HINTS
PATTERNS = List[Tuple[str, List[str]]]
FOUND_ENTITIES = List[Dict[str, List[str]]]

##################################################
################### NLP Model ####################
##################################################


@app.route("/nlp_models", methods=["GET", "POST", "PUT", "DELETE"])
def nlp_models_crud():
    try:
        if request.method == "GET":
            workspace_id = request.args.get("workspace_id")
            index, exist = get_nlp_model(es, workspace_id=workspace_id)
            if not exist:
                return index
            doc = es.get(index=index.index_name, id=index.workspace_id)
            return doc

        elif request.method == "POST":
            workspace_id = request.args.get("workspace_id")
            nlp_model = request.get_json()
            if not nlp_model:
                return Response("Expect to recive the nlp_model object!", status=400)
            recipe = nlp_model.get("recipe")
            # Do tests after
            # if recipe:
            #     msg, status = check_recipe(recipe.get("model_kind"), recipe)
            #     if status != 200:
            #         return Response(msg, status=status)
            index = NLPmodelIndex(
                es=es,
                workspace_id=workspace_id,
                customer_id=nlp_model["customer_id"],
                recipe=recipe,
            )

            if index.index_exist(es):
                return Response("NLP Model already exist!", status=409)
            index.create_index(es)
            _, res = index.create_recipe(es)
            return res

        elif request.method == "PUT":
            workspace_id = request.args.get("workspace_id")
            nlp_model = request.get_json()
            if not nlp_model:
                return Response("Expect to recive the nlp_model object!", status=400)
            recipe = nlp_model.get("recipe")
            # if recipe:
            #     msg, status = check_recipe(recipe.get("model_kind"), recipe)
            #     if status != 200:
            #         return Response(msg, status=status)
            index, exist = get_nlp_model(es, workspace_id=workspace_id)
            if not exist:
                return index
            update_query = {"doc": nlp_model}
            res = es.update(
                index=index.index_name, id=index.workspace_id, body=update_query
            )
            index = pipeline_to_update_index(es, index)
            res["_index"] = index.index_name
            return res

        elif request.method == "DELETE":
            workspace_id = request.args.get("workspace_id")
            index, exist = get_nlp_model(es, workspace_id=workspace_id)
            if not exist:
                return index
            res = es.indices.delete(index=index.index_name)
            return res

    except:
        trace_back_error = "".join([str(item) for item in sys.exc_info()])
        print(sys.exc_info())
        return Response(
            '{"response":"%s"}' % trace_back_error,
            status=500,
            mimetype="application/json",
        )


##################################################
################### INTENT #######################
##################################################


@app.route("/nlp_models/intents", methods=["GET", "POST", "PUT", "DELETE"])
def intent_crud():
    try:
        if request.method == "POST":
            workspace_id = request.args.get("workspace_id")
            index, exist = get_nlp_model(es, workspace_id=workspace_id)
            if not exist:
                return index
            intent = request.get_json()
            if intent:
                res, status = index.add_intent(es, intent)
                if status != 200:
                    return Response(res, status=status)
                return res
            return Response("Expect to recive a intent object!", status=400)

        elif request.method == "GET":
            workspace_id = request.args.get("workspace_id")
            index, exist = get_nlp_model(es, workspace_id=workspace_id)
            if not exist:
                return index
            intent_id = request.args.get("intent_id")
            if intent_id:
                try:
                    res = es.get(index=index.index_name, id=intent_id)
                    return {"result": res}
                except NotFoundError:
                    return Response(
                        "Intent with id %s was not found!" % intent_id, status=404
                    )
            intent_name = request.args.get("intent_name")
            if intent_name:
                res = es.search(
                    index=index.index_name,
                    body={"query": {"term": {"intent": intent_name}}},
                )
                if res["hits"]["hits"]:
                    return res["hits"]["hits"][-1]
                else:
                    return Response(
                        "Intent with name %s was not found!" % intent_name, status=404
                    )
            return Response(
                "Expect to recive workspace_id and intent_name or intent_id!",
                status=400,
            )

        elif request.method == "PUT":
            workspace_id = request.args.get("workspace_id")
            index, exist = get_nlp_model(es, workspace_id=workspace_id)
            if not exist:
                return index
            intent = request.get_json()
            if not intent:
                return Response("Expect to recive a intent object!", status=400)
            update_query = {"doc": intent}
            intent_id = request.args.get("intent_id")
            if intent_id:
                try:
                    res = es.update(
                        index=index.index_name, id=intent_id, body=update_query
                    )
                    return res
                except NotFoundError:
                    return Response(
                        "Intent with id %s was not found!" % intent_id, status=404
                    )

            intent_name = request.args.get("intent_name")
            if intent_name:
                res = es.search(
                    index=index.index_name,
                    body={"query": {"term": {"intent": intent_name}}},
                )
                if res["hits"]["hits"]:
                    intent_id = res["hits"]["hits"][0]["_id"]
                    res = es.update(
                        index=index.index_name, id=intent_id, body=update_query
                    )
                    return res
                else:
                    return Response(
                        "Intent with name %s was not found!" % intent_name, status=404
                    )
            return Response(
                "Expect to recive workspace_id and intent_name or intent_id!",
                status=400,
            )

        elif request.method == "DELETE":
            workspace_id = request.args.get("workspace_id")
            index, exist = get_nlp_model(es, workspace_id=workspace_id)
            if not exist:
                return index
            intent_id = request.args.get("intent_id")
            if intent_id:
                try:
                    res = es.delete(index=index.index_name, id=intent_id)
                    return res
                except NotFoundError:
                    return Response(
                        "Intent with id %s was not found!" % intent_id, status=404
                    )
            intent_name = request.args.get("intent_name")
            if intent_name:
                res = es.search(
                    index=index.index_name,
                    body={"query": {"term": {"intent": intent_name}}},
                )
                if res["hits"]["hits"]:
                    intent_id = res["hits"]["hits"][0]["_id"]
                    res = es.delete(index=index.index_name, id=intent_id)
                    return res
                else:
                    return Response(
                        "Intent with name %s was not found!" % intent_name, status=404
                    )

            return Response(
                "Expect to recive workspace_id and intent_name or intent_id!",
                status=400,
            )

    except:
        trace_back_error = "".join([str(item) for item in sys.exc_info()])
        print(sys.exc_info())
        return Response(
            '{"response":"%s"}' % trace_back_error,
            status=500,
            mimetype="application/json",
        )


##################################################
################### ENTITY #######################
##################################################
@app.route("/nlp_models/entities", methods=["GET", "POST", "PUT", "DELETE"])
def entities_crud():
    try:
        if request.method == "POST":
            entity = request.get_json()
            if entity == None:
                return Response("Expect to recive a entity object!", status=400)
            workspace_id = request.args.get("workspace_id")
            index, exist = get_nlp_model(es, workspace_id=workspace_id)
            if not exist:
                return index
            if entity:
                res, status = entity_check(entity)
                if status != 200:
                    return Response(res, status=status)
                res, status = index.add_entity(es, entity)
                if status != 200:
                    return Response(res, status=status)
                return res
            return Response("Expect to recive a entity object!", status=400)
        if request.method == "GET":
            workspace_id = request.args.get("workspace_id")
            index, exist = get_nlp_model(es, workspace_id=workspace_id)
            if not exist:
                return index
            entity_id = request.args.get("entity_id")
            if entity_id:
                try:
                    res = es.get(index=index.index_name, id=entity_id)
                    return res
                except NotFoundError:
                    return Response(
                        "Entity with id %s was not found!" % entity_id, status=404
                    )
            entity_name = request.args.get("entity_name")
            if entity_name:
                res = es.search(
                    index=index.index_name,
                    body={"query": {"term": {"entity": entity_name}}},
                )
                if res["hits"]["hits"]:
                    return res["hits"]["hits"][-1]
                else:
                    return Response(
                        "Entity with name %s was not found!" % entity_name, status=404
                    )
            return Response(
                "Expect to recive workspace_id and entity_name or entity_id!",
                status=400,
            )

        elif request.method == "PUT":
            workspace_id = request.args.get("workspace_id")
            index, exist = get_nlp_model(es, workspace_id=workspace_id)
            if not exist:
                return index
            entity = request.get_json()
            if not entity:
                return Response("Expect to recive a intent object!", status=400)
            update_query = {"doc": entity}
            entity_id = request.args.get("entity_id")
            if entity_id:
                try:
                    res = es.update(
                        index=index.index_name, id=entity_id, body=update_query
                    )
                    return res
                except NotFoundError:
                    return Response(
                        "Entity with id %s was not found!" % entity_id, status=404
                    )

            entity_name = request.args.get("entity_name")
            if entity_name:
                res = es.search(
                    index=index.index_name,
                    body={"query": {"term": {"entity": entity_name}}},
                )
                if res["hits"]["hits"]:
                    entity_id = res["hits"]["hits"][0]["_id"]
                    res = es.update(
                        index=index.index_name, id=entity_id, body=update_query
                    )
                    return res
                else:
                    return Response(
                        "Entity_id with name %s was not found!" % entity_name,
                        status=404,
                    )
            return Response(
                "Expect to recive workspace_id and entity_name or entity_id!",
                status=400,
            )

        elif request.method == "DELETE":
            workspace_id = request.args.get("workspace_id")
            index, exist = get_nlp_model(es, workspace_id=workspace_id)
            if not exist:
                return index
            entity_id = request.args.get("entity_id")
            if entity_id:
                try:
                    res = es.delete(index=index.index_name, id=entity_id)
                    return res
                except NotFoundError:
                    return Response(
                        "Entity with id %s was not found!" % entity_id, status=404
                    )
            entity_name = request.args.get("entity_name")
            if entity_name:
                res = es.search(
                    index=index.index_name,
                    body={"query": {"term": {"entity": entity_name}}},
                )
                if res["hits"]["hits"]:
                    entity_id = res["hits"]["hits"][0]["_id"]
                    res = es.delete(index=index.index_name, id=entity_id)
                    return res
                else:
                    return Response(
                        "Entity with name %s was not found!" % entity_name, status=404
                    )

            return Response(
                "Expect to recive workspace_id and entity_name or entity_id!",
                status=400,
            )

    except:
        trace_back_error = "".join([str(item) for item in sys.exc_info()])
        print(sys.exc_info())
        return Response(
            '{"response":"%s"}' % trace_back_error,
            status=500,
            mimetype="application/json",
        )


##################################################
################### Resources ####################
##################################################
TOKENIZER_QUERY = {"analyzer": "standard", "text": ""}


def synonym_matcher(entities, sentence, sentence_tokens, fuzzy_match_threshold=90):
    found_entities = []
    for entity, values in entities:
        for value in values:
            words_of_entity = value.split(" ")
            if len(words_of_entity) > 1:
                score = fuzz.ratio(sentence.lower(), value.lower())
                if score >= fuzzy_match_threshold:
                    found_entities.append({entity: sentence})
                else:
                    pass
            else:
                for token in sentence_tokens:
                    score = fuzz.ratio(token.lower(), value.lower())
                    if score >= fuzzy_match_threshold:
                        found_entities.append({entity: token})
                    else:
                        continue
    return found_entities


# The first function of this project using typing hint, 2021-03-20
def patterns_matcher(patterns: PATTERNS, sentence: str) -> FOUND_ENTITIES:
    found_entities = []
    for entity, values in patterns:
        for value in values:
            results = re.findall(value, sentence)
            if results:
                found_entities.append({entity: results})
            else:
                pass
    return found_entities


def get_tokens(sentence, index_name):
    TOKENIZER_QUERY["text"] = sentence
    sentence_tokens = es.indices.analyze(index=index_name, body=TOKENIZER_QUERY)
    sentence_tokens = [item["token"] for item in sentence_tokens["tokens"]]
    return sentence_tokens


def read_td_idf_train_test_data(workspace_id):
    path = local_path + "/feature_encoding/tfidf/resources"
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


@app.route("/nlp_models/resources/train", methods=["POST"])
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


@app.route("/nlp_models/resources/classify", methods=["POST"])
def nlp_model_classify():
    if request.method == "POST":
        sentence = request.args.get("sentence")
        if not sentence:
            return Response(
                "Expect to recive a sentence for classification", status=400
            )
        workspace_id = request.args.get("workspace_id")
        index, exist = get_nlp_model(es, workspace_id=workspace_id)
        if not exist:
            return index
        fuzzy_match_threshold = request.args.get("fuzzy_match_threshold")
        if fuzzy_match_threshold:
            try:
                fuzzy_match_threshold = float(fuzzy_match_threshold)
                if fuzzy_match_threshold < 0 or fuzzy_match_threshold > 100:
                    return Response(
                        "The fuzzy_match_threshold must be between 0 and 100.",
                        status=400,
                    )
            except:
                return Response(
                    "The fuzzy_match_threshold must be a float.", status=400
                )
        else:
            fuzzy_match_threshold = 90
        entities = [
            (k, v)
            for k, v in zip(
                index.synonyms_entities.keys(), index.synonyms_entities.values()
            )
        ]
        patterns = [
            (k, v)
            for k, v in zip(
                index.patterns_entities.keys(), index.patterns_entities.values()
            )
        ]
        nlp_model_doc = es.get(index=index.index_alias, id=index.workspace_id)
        accuracies = nlp_model_doc["_source"]["accuracies"]
        sentence_tokens = get_tokens(sentence=sentence, index_name=index.index_name)
        svm, logit, cnn = load_models(index.workspace_id)
        tf_idf_corpus = get_tfidf_corpus(index.workspace_id)
        intents_dictionary = get_intents_dictionary(index.workspace_id)
        sentence_features = get_sentece_features(sentence, index, es, tf_idf_corpus)
        logit_result = (
            logit.predict_proba(sentence_features) * accuracies["logit_accuracy"]
        )
        svm_result = svm.predict_proba(sentence_features) * accuracies["svm_accuracy"]
        cnn_result = cnn.predict(sentence_features) * accuracies["cnn_accuracy"]
        bm25_result = find_intents_bm25(index, sentence, es)
        if bm25_result != False:
            array_result_bm25 = (
                bm25_result_to_vector(
                    result=bm25_result, intents_dictionary=intents_dictionary
                )
                * accuracies["bm25_accuracy"]
            )

            ensemble_result = (
                logit_result + cnn_result + svm_result + array_result_bm25
            ) / (
                accuracies["logit_accuracy"]
                + accuracies["svm_accuracy"]
                + accuracies["cnn_accuracy"]
                + accuracies["bm25_accuracy"]
            )
        else:
            ensemble_result = (logit_result + cnn_result + svm_result) / (
                accuracies["logit_accuracy"]
                + accuracies["svm_accuracy"]
                + accuracies["cnn_accuracy"]
            )

        intents_index = np.argsort(ensemble_result)  # np.argmax(ensemble_result)
        found_synonyms = synonym_matcher(
            entities, sentence, sentence_tokens, fuzzy_match_threshold
        )
        found_patterns = patterns_matcher(patterns, sentence)
        result = dict()
        result["intents"] = [
            {"intent": intents_dictionary[str(i)], "confidence": ensemble_result[0][i]}
            for i in intents_index[0][::-1]
        ]
        result["entities"] = found_synonyms + found_patterns
        return result


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
