import spacy
import random
import math
import pt_core_news_lg

random.seed(42)

nlp = pt_core_news_lg.load()


def keep_token(token):
    return token.is_alpha and not (token.is_space or token.is_punct)


def create_new_sentence(sentence):
    doc = nlp(sentence)
    return " ".join([token.lemma_ for token in doc if keep_token(token)]).lower()


def complete_messing_examples(intent):
    quantity_of_examples = len(intent["examples"])
    messing_examples = quantity_of_examples - 8
    if messing_examples < 0 and messing_examples > -5:
        examples_ = random.sample(intent["examples"], abs(messing_examples))
        artificial_examples = [
            {
                "constructed": create_new_sentence(sentence["text"]),
                "original": sentence["text"],
            }
            for sentence in examples_
        ]
        intent["artificial_examples"] = artificial_examples
    elif messing_examples <= -5:
        examples_ = random.sample(intent["examples"], quantity_of_examples)
        artificial_examples = [
            {
                "constructed": create_new_sentence(sentence["text"]),
                "original": sentence["text"],
            }
            for sentence in examples_
        ]
        intent["artificial_examples"] = artificial_examples
    return intent


def update_doc(index, es, doc, _id):
    res = es.update(index=index.index_alias, id=_id, body={"doc": doc})
    return res


def update_intents_with_messing_examples(index, es):
    query = {"size": 1000, "query": {"term": {"doc_type.keyword": "intent"}}}
    intents = es.search(index=index.index_alias, body=query)
    intents = [result for result in intents["hits"]["hits"]]
    new_intents = []
    for intent in intents:
        if len(intent["_source"]["examples"]) < 8:
            new_intent = complete_messing_examples(intent["_source"])
            res = update_doc(index, es, new_intent, intent["_id"])
            print(res)


def train_test_split(index, es, percentage=0.3):
    query = {"size": 1000, "query": {"term": {"doc_type.keyword": "intent"}}}
    intents = es.search(index=index.index_alias, body=query)
    intents = [result for result in intents["hits"]["hits"]]
    for intent in intents:
        _id = intent["_id"]
        intent = intent["_source"]
        quantity_of_examples = len(intent["examples"])
        if quantity_of_examples >= 8:
            qt = math.ceil(quantity_of_examples * percentage)
            all_indices = set(range(0, quantity_of_examples))
            examples_indices_for_test = set(
                random.Random(42).sample(population=all_indices, k=qt)
            )
            examples_indices_for_train = all_indices - examples_indices_for_test
            intent["for_train"] = list(
                map(intent["examples"].__getitem__, examples_indices_for_train)
            )
            intent["for_test"] = list(
                map(intent["examples"].__getitem__, examples_indices_for_test)
            )

        elif quantity_of_examples >= 5 and quantity_of_examples < 8:
            qt = 3 - abs(8 - quantity_of_examples)
            all_indices = set(range(0, quantity_of_examples))
            examples_indices_for_test = set(
                random.Random(42).sample(population=all_indices, k=qt)
            )
            examples_indices_for_train = all_indices - examples_indices_for_test
            intent["for_train"] = list(
                map(intent["examples"].__getitem__, examples_indices_for_train)
            )
            intent["for_test"] = list(
                map(intent["examples"].__getitem__, examples_indices_for_test)
            ) + [
                {"text": item["constructed"]} for item in intent["artificial_examples"]
            ]
        elif quantity_of_examples < 5:
            intent["for_train"] = intent["examples"]
            intent["for_test"] = [
                {"text": item["constructed"]} for item in intent["artificial_examples"]
            ]
        res = update_doc(index, es, intent, _id)
        print(res)


def get_train_test(index, es):
    query = {"size": 1000, "query": {"term": {"doc_type.keyword": "intent"}}}

    intents = es.search(index=index.index_name, body=query)
    intents = [result["_source"] for result in intents["hits"]["hits"]]
    train_examples = []
    test_examples = []
    for intent in intents:
        intent_name = intent["intent"]
        try:
            train_examples += [
                (example["text"], intent_name) for example in intent["for_train"]
            ]
            test_examples += [
                (example["text"], intent_name) for example in intent["for_test"]
            ]
        except:
            print(intent)
            break
    return train_examples, test_examples
