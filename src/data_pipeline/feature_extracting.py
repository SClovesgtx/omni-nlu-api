# standard library imports
from collections import namedtuple

Intent = namedtuple('Intent', 'intent_name examples_text')

# third party imports
import numpy as np
from sklearn.preprocessing import OneHotEncoder
from sklearn.feature_extraction.text import TfidfVectorizer

def intents_to_onehot(intents_name):
    array_intents_name = np.asarray([[intent_name] for intent_name in intents_name])
    encoder = OneHotEncoder(sparse=False)
    onehot_intents = encoder.fit_transform(array_intents_name) 
    map_onehot = {
        intent: onehot
        for intent, onehot in zip(intents_name, onehot_intents)
    }
    # use to identify the intent name 
    # in the prediction fase
    intent_dictionary = {
        str(np.argmax(value)): key
        for key, value in zip(map_onehot.keys(), map_onehot.values())
    }
    return map_onehot, intent_dictionary

def create_corpus(examples_text):
    vectorizer = TfidfVectorizer()
    corpus = vectorizer.fit(examples_text)
    return corpus

def encode_features(train, test, corpus, map_onehot):
    
    y_train = np.stack([map_onehot[example[0]] for example in train])
    X_train = corpus.transform([example[1] for example in train]).toarray()
    
    y_test = np.stack([map_onehot[example[0]] for example in test])
    X_test = corpus.transform([example[1] for example in test]).toarray()
    
    return X_train, y_train, X_test, y_test