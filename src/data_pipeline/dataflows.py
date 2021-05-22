# standard library imports
import os

# setting working dir
os.chdir("../src")

# third party imports
from prefect import Flow, task, context

# local imports
from data_pipeline.data_sourcing import get_data
from data_pipeline.data_preprocessing import (
                                             fill_missing_examples, 
                                             clean_examples,
)
from data_pipeline.feature_engineering import (
                                               intents_to_onehot, 
                                               create_corpus, 
                                               encode_features,
)
from data_pipeline.data_splitting import data_splitting
from elasticsearch_db.elasticsearch import elastic_conection
from elasticsearch_db.elasticsearch import get_nlp_model

@task
def sourcing(workspace, es):

    return get_data(
                workspace=workspace, 
                es=es
            )

@task
def imputation(data):
    
    return fill_missing_examples(data)

@task
def cleansing(data):

    return clean_examples(data)



@task(nout=2)
def splitting(data):

    return data_splitting(data)

@task(nout=4)
def encoding(train, test):
    all_intents = set([example[0] for example in train])
    map_onehot, intent_dictionary = intents_to_onehot(
                                        intents_name=all_intents
                                    )
    all_examples = [example[0] for example in train] + \
                   [example[0] for example in test]
        
    corpus = create_corpus(examples_text=all_examples)
    
    X_train, y_train, X_test, y_test = encode_features(
                                            train=train, 
                                            test=test, 
                                            corpus=corpus, 
                                            map_onehot=map_onehot
                                    )
    return X_train, y_train, X_test, y_test


def train_data_flow(workspace, es):

    # Define prefect flow
    with Flow("train_dataflow") as flow:

        data = sourcing(workspace=workspace, es=es)
        data = imputation(data=data)
        data = cleansing(data=data)
        train, test = splitting(data=data)
        X_train, y_train, X_test, y_test = encoding(train=train, 
                                                    test=test)

    flow.run()
    flow.visualize(filename="src/data_pipeline/flow_diagrams/train_dataflow")