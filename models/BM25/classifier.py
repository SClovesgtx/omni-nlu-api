
def find_intents_bm25(index, sentence, es):
    query = {
        "query":{
           "more_like_this":{
              "fields":["examples.text"],
              "like":sentence,
              "min_term_freq":1,
              "max_query_terms":20
           }
        }
    }
    response = es.search(index=index.index_name, body = query)
    result = {"intents": []}
    for r in response["hits"]["hits"]:
        normalized_score = 1 - (1 / r["_score"]) if r["_score"] >= 1 else 0
        intent = {"intent": r["_source"]["intent"],
                  "confidence": normalized_score}
        result["intents"].append(intent)

    if not result["intents"]:
        result["intents"].append({"intent": "anything_else", "confidence": 0.1})

    return result

def bm25_accuracy(test_examples, index, es):
    right_answers = 0
    for test in test_examples:
        result = find_intents_bm25(index, test[0], es)
        if result["intents"][0]["intent"] == test[1]:
            right_answers += 1
    return right_answers/len(test_examples)
