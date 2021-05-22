import numpy as np
from sklearn.preprocessing import OneHotEncoder
from sklearn.feature_extraction.text import TfidfVectorizer
import pickle
import json
import random
import os

local_path = os.path.dirname(os.path.abspath(__file__))

QUERY = {
    "tokenizer": "classic",
    "filter": [
        "lowercase",
        "asciifolding",
        {"type": "stop", "stopwords": "_portuguese_"},
        {"type": "stemmer", "language": "brazilian"},
    ],
    "text": "",
}


def clean_example(example, index, es):
    QUERY["text"] = example
    result = es.indices.analyze(index=index.index_name, body=QUERY)
    cleaned_example = " ".join([token["token"] for token in result["tokens"]])
    return cleaned_example


def get_sentece_features(sentence, index, es, tf_idf_corpus):
    new_sentence = clean_example(sentence, index, es)
    sentence_features = tf_idf_corpus.transform([new_sentence]).toarray()
    return sentence_features


def get_tfidf_corpus(workspace_id):
    file = local_path + "/resources/tf_idf_corpus_{workspace_id}.pickle".format(
        workspace_id=workspace_id
    )
    tf_idf_corpus = pickle.load(open(file, "rb"))
    return tf_idf_corpus


def get_intents_dictionary(workspace_id):
    file = local_path + "/resources/intents_dictionary-{workspace_id}.json".format(
        workspace_id=workspace_id
    )
    with open(file, "r") as f:
        intents_dictionary = json.load(f)
    return intents_dictionary


def intent_to_onehot(intents_names):
    data = np.asarray([[intent_name] for intent_name in intents_names])
    # define one hot encoding
    encoder = OneHotEncoder(sparse=False)
    # transform data
    intents_names_as_onehot = encoder.fit_transform(data)
    return intents_names_as_onehot


def tfidf_encoding(examples):
    # create the transform
    vectorizer = TfidfVectorizer()
    # tokenize and build vocab
    tf_idf_corpus = vectorizer.fit(examples)
    features = tf_idf_corpus.transform(examples)
    return tf_idf_corpus, features.toarray()


def save_resources(
    dic_onehot_intents,
    intent_dictionary,
    tf_idf_corpus,
    workspace_id,
    X_train,
    y_train,
    X_test,
    y_test,
):

    file = local_path + "/resources/dic_onehot_intents-{workspace_id}.npy".format(
        workspace_id=workspace_id
    )
    np.save(file, dic_onehot_intents)

    file = local_path + "/resources/intents_dictionary-{workspace_id}.json".format(
        workspace_id=workspace_id
    )
    with open(file, "w") as f:
        json.dump(intent_dictionary, f)
    f.close()

    #  save tf_idf_corpus instance
    file = local_path + "/resources/tf_idf_corpus_{workspace_id}.pickle".format(
        workspace_id=workspace_id
    )
    pickle.dump(tf_idf_corpus, open(file, "wb"))

    with open(
        local_path
        + "/resources/X_train_tfidf_{workspace_id}.npy".format(
            workspace_id=workspace_id
        ),
        "wb",
    ) as f:
        np.save(f, X_train)
        f.close()

    with open(
        local_path
        + "/resources/y_train_tfidf_{workspace_id}.npy".format(
            workspace_id=workspace_id
        ),
        "wb",
    ) as f:
        np.save(f, y_train)
        f.close()

    with open(
        local_path
        + "/resources/X_test_tfidf_{workspace_id}.npy".format(
            workspace_id=workspace_id
        ),
        "wb",
    ) as f:
        np.save(f, X_test)
        f.close()

    with open(
        local_path
        + "/resources/y_test_tfidf_{workspace_id}.npy".format(
            workspace_id=workspace_id
        ),
        "wb",
    ) as f:
        np.save(f, y_test)
        f.close()


def apply_pipe_tfidf_feature_encoding(train_examples, test_examples, index, es):
    # shuffle examples
    random.Random(42).shuffle(train_examples)
    random.Random(42).shuffle(test_examples)
    stard_idx_test = len(train_examples)
    # join all examples
    all_examples = list(map(lambda item: item[0], train_examples)) + list(
        map(lambda item: item[0], test_examples)
    )
    intents_name = list(map(lambda item: item[1], train_examples)) + list(
        map(lambda item: item[1], test_examples)
    )
    # clean examples (remove stop words, ponctuation and apply stemmer)
    cleaned_examples = []
    for example in all_examples:
        cleaned_example = clean_example(example, index, es)
        cleaned_examples.append(cleaned_example)

    # create onehot notation for all intents
    intents_name_set = set(intents_name)
    print(intents_name)
    intents_name_as_onehot = intent_to_onehot(intents_name_set)
    dic_onehot_intents = {
        intent: onehot
        for intent, onehot in zip(intents_name_set, intents_name_as_onehot)
    }
    intent_dictionary = {
        str(np.argmax(value)): key
        for key, value in zip(dic_onehot_intents.keys(), dic_onehot_intents.values())
    }

    # get tf-idf from all examples
    tf_idf_corpus, tf_idf = tfidf_encoding(examples=cleaned_examples)

    # split train and test
    X_train = np.stack(tf_idf[:stard_idx_test])
    y_train = np.stack(
        [dic_onehot_intents[intent] for intent in map(lambda x: x[1], train_examples)]
    )

    X_test = np.stack(tf_idf[stard_idx_test:])
    y_test = np.stack(
        [dic_onehot_intents[intent] for intent in map(lambda x: x[1], test_examples)]
    )

    # save resources
    save_resources(
        dic_onehot_intents=dic_onehot_intents,
        intent_dictionary=intent_dictionary,
        tf_idf_corpus=tf_idf_corpus,
        X_train=X_train,
        y_train=y_train,
        X_test=X_test,
        y_test=y_test,
        workspace_id=index.workspace_id,
    )
