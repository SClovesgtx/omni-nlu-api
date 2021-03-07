from elasticsearch import Elasticsearch
from elasticsearch.exceptions import ConflictError
from flask import Response
from datetime import datetime
import os

ELASTICSEARCH_HOST = os.environ['ELASTICSEARCH_HOST']

# SETTING PARA BM25
SETTINGS = {
    "number_of_shards": 1,
    "index": {
      "similarity": {
        "default": {
          "type": "BM25",
          "b": 0.75,
          "k1": 1.2
        }
      }
    },
    "analysis": {
        "filter": {
          "pt_stop":{
                  "type": "stop",
                  "stopwords": "_portuguese_"
              },
          "my_pt_stemmer": {
            "type": "stemmer",
            "language": "portuguese_rslp"
          }
        },
      "analyzer": {
          "examples_intent_analyzer":{
                  "type":"custom",
                  "tokenizer":"standard",
                  "char_filter":  [ "html_strip" ],
                  "filter":[
                    "lowercase",
                    "asciifolding"
                  ]
              }
        }
      }
}

MAPPINGS_PROPERTIES =  {
    "properties": {
      "customer_id": {"type": "keyword"},
      "recipe": {"type": "object"},
      "intent": {"type": "keyword"},
          "examples": {
            "properties": {"text": {"type": "text", "analyzer": "examples_intent_analyzer"}}
          },
          "for_train": {
            "properties": {"text": {"type": "text", "analyzer": "examples_intent_analyzer"}}
          },
          "for_test": {
            "properties": {"text": {"type": "keyword"}}
          },
          "artificial_examples": {
            "properties": {"original": {"type": "keyword"},
                          "constructed": {"type": "keyword"}}
          },
      "description": {"type": "text"},
      "entity": {"type": "keyword"},
      "values": {
        "properties": {
          "type": {"type": "keyword"},
          "value": {"type": "keyword"},
          "patterns": {"type": "keyword"},
          "synonyms": {"type": "keyword"}
        }
      }
    }
}

DEFAULT_RECIPE = [
      {
        "model": "cnn",
        "settings": {
          "intermediate_layers": [
                {"activation":"relu"}
          ],
          "loss": "categorical_crossentropy",
          "epochs":100,
          "batch_size":100,
          "learning_rate":0.001
        }
      },
      {
        "model": "logit",
        "settings": {
          "C":5.0, 
          "fit_intercept":False,
          "random_state":1
        }
      },
      {
        "model": "svm",
        "settings": { 
            "degree":1, 
            "coef0":0.0, 
            "random_state":42
        }
      },
      {
        "model": "bm25",
        "settings": { 
            "b": 0.75,
            "k1": 1.2
        }
      }
]

def get_nlp_model(es, workspace_id):
    index = NLPmodelIndex(es=es, workspace_id=workspace_id)
    if not index.index_exist(es):
        return Response('Model %s do not exist!'%workspace_id,
                            status=404), False
    return index, True

def pipeline_to_update_index(es, index):
    index.update(es) # object fields update
    index.create_index(es)
    index.reindex(es) # criation of a new index with the new recipe
    index.delete_index(es, old_index_name=index.old_index_name)
    return index

def get_entities(es, index_name, value_type):
    synonyms_result = es.search(index=index_name, body = {
                                                          "query": {
                                                           "bool": {
                                                             "must": [
                                                               {"term": {"doc_type.keyword": "entity"}},
                                                               {"term": {"values.type": value_type}}
                                                             ]
                                                           }
                                                          }
                                                        })

    entities = [synonym["_source"] for synonym in synonyms_result["hits"]["hits"]]
    dic = dict()
    if value_type == "synonyms":
        for entity in entities:
            entity_name = entity["entity"] + ":"
            for value in entity["values"]:
                key = entity_name+value["value"]
                dic[key] = [value["value"]] + value[value_type]
    if value_type == "patterns":
        for entity in entities:
            entity_name = entity["entity"] + ":"
            for value in entity["values"]:
                key = entity_name+value["value"]
                dic[key] = value[value_type]

    return dic

def intent_exist(es, index, intent):
    res = es.search(index=index, body={
                                  "query": {
                                    "term": {
                                      "intent": intent
                                    }
                                  }
                                })
    if res["hits"]["hits"]:
        return 'Intent %s already exist!'%intent, 409
    return "Do not exist!", 200

def entity_exist(es, index, entity):
    res = es.search(index=index, body={
                                  "query": {
                                    "term": {
                                      "entity": entity
                                    }
                                  }
                                })
    if res["hits"]["hits"]:
        return 'Entity %s already exist!'%entity, 409
    return "Do not exist!", 200

def set_bm25_parameters(recipe):
    for model in recipe:
      if model["model"]=="bm25":
        SETTINGS["index"]["similarity"]["default"]["b"] = model["settings"]["b"]
        SETTINGS["index"]["similarity"]["default"]["k1"] = model["settings"]["k1"]


def elastic_conection():
    es = Elasticsearch([{'host':ELASTICSEARCH_HOST,'port':9200}])
    return es


def index_exist(es, index_name):
    "checks if index already exists"
    res = es.indices.exists(index=index_name)
    return res


class NLPmodelIndex:

    def __init__(self, es, workspace_id, customer_id=None, recipe=None):
        now = datetime.now()
        dt_string = now.strftime("%d%m%Y%H%M%S")
        self.index_alias = "nlp_model-{workspace_id}".format(workspace_id=workspace_id)
        if not index_exist(es, self.index_alias):
            self.index_name = "nlp_model-{workspace_id}-{dt_string}".format(workspace_id=workspace_id,
                                                                            dt_string=dt_string)
            self.old_index_name = None
            self.workspace_id = workspace_id
            if customer_id:
              self.customer_id = customer_id
            if recipe == None:
              recipe = DEFAULT_RECIPE
            set_bm25_parameters(recipe)
            self.recipe = recipe
            self.mapping = {"settings": SETTINGS,
                            "mappings": MAPPINGS_PROPERTIES}

        else:
            res = es.get(index=self.index_alias, id=workspace_id)
            self.index_name = res["_index"]
            self.workspace_id = res["_id"]
            self.customer_id = res["_source"]["customer_id"]
            self.recipe = res["_source"]["recipe"]
            set_bm25_parameters(self.recipe)
            self.mapping = {"settings": SETTINGS,
                            "mappings": MAPPINGS_PROPERTIES}
            self.synonyms_entities = get_entities(es, self.index_name, "synonyms")
            self.patterns_entities = get_entities(es, self.index_name, "patterns")


    def index_exist(self, es):
        "checks if index already exists"
        res = es.indices.exists(index=self.index_name)
        return res

    def create_recipe(self, es):
        "create the model recipe document"
        try:
            doc = {"workspace_id": self.workspace_id,
                   "customer_id": self.customer_id,
                   "recipe": self.recipe}
            res = es.create(index=self.index_name,
                      id=self.workspace_id,
                      body=doc)

            return False, res # false to indicate that recipe did not existed and now it was created
        except ConflictError:
            return True, "Recipe already exist!" # true to indicate that document already exist


    def create_index(self, es):
        "create a index"
        res = es.indices.create(index=self.index_name,  body=self.mapping)
        es.indices.put_alias(index=self.index_name, name=self.index_alias)
        return res

    def delete_index(self, es, old_index_name=None):
        "delete the index"
        if old_index_name:
            res = es.indices.delete(index=old_index_name)
            return res
        res = es.indices.delete(index=self.index_name)
        return res

    def add_intent(self, es, intent):
        intent["doc_type"] = "intent"
        msg, status = intent_exist(es, self.index_name, intent["intent"])
        if status != 200:
            return msg, status
        res = es.index(index=self.index_name, body=intent)
        return res, status

    def add_entity(self, es, entity):
        entity["doc_type"] = "entity"
        msg, status = entity_exist(es, self.index_name, entity["entity"])
        if status != 200:
            return msg, status
        res = es.index(index=self.index_name, body=entity)
        return res, status

    def update(self, es):
        now = datetime.now()
        dt_string = now.strftime("%d%m%Y%H%M%S")
        res = es.get(index=self.index_alias, id=self.workspace_id)
        self.old_index_name = self.index_name
        self.index_name = "nlp_model-{workspace_id}-{dt_string}".format(workspace_id=self.workspace_id,
                                                                        dt_string=dt_string)
        self.recipe = res["_source"]["recipe"]
        set_bm25_parameters(self.recipe)
        self.mapping = {"settings": SETTINGS,
                        "mappings": MAPPINGS_PROPERTIES}
        return self

    def reindex(self, es):
        res = es.reindex({
                "source": {"index": self.old_index_name},
                "dest": {"index": self.index_name}
                }, wait_for_completion=True, request_timeout=300)
        return res
