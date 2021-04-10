


def get_data(workspace, es):
    query = {"size": 1000, "query": {"term": {"doc_type.keyword": "intent"}}}

    intents = es.search(index=workspace.index_name, body=query)
    intents = [result["_source"] for result in intents["hits"]["hits"]]
    
    return intents