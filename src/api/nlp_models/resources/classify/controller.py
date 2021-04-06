# standard library imports
import sys
import re
from typing import Tuple, List, Dict

sys.path.append("./src/")

# third party imports
import numpy as np
from fuzzywuzzy import fuzz
from flask import Blueprint, request, Response

classify_app = Blueprint("classify_app", __name__)

# local imports
from models.models import load_models
from models.BM25.classifier import (
    find_intents_bm25,
    bm25_accuracy,
    bm25_result_to_vector,
)
from feature_encoding.tfidf.pipeline import (
    apply_pipe_tfidf_feature_encoding,
    get_tfidf_corpus,
    get_sentece_features,
    get_intents_dictionary,
)
from elasticsearch_db.elasticsearch import elastic_conection
from elasticsearch_db.elasticsearch import get_nlp_model

es = elastic_conection()

TOKENIZER_QUERY = {"analyzer": "standard", "text": ""}

# TYPING HINTS
PATTERNS = List[Tuple[str, List[str]]]
FOUND_ENTITIES = List[Dict[str, List[str]]]


def get_tokens(sentence, index_name):
    TOKENIZER_QUERY["text"] = sentence
    sentence_tokens = es.indices.analyze(index=index_name, body=TOKENIZER_QUERY)
    sentence_tokens = [item["token"] for item in sentence_tokens["tokens"]]
    return sentence_tokens


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


@classify_app.route("/nlp_models/resources/classify", methods=["POST"])
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
