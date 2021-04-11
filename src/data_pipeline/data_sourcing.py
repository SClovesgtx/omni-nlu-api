from collections import namedtuple

Intent = namedtuple('Intent', 'intent_name examples_text')


def get_data(workspace, es):
    """
    Get all the intents in the elasticsearch
    workspace's index.
    
    Parameters
    ----------
    workspace: the workspace object
    es: the elasticsearch conection instance
    
    Returns
    -------
    list: a list of namedtuple Intents
        
    Examples
    --------
    
    Raises
    ------
    
    Notes
    -----
    
    """
    query = {"size": 1000, "query": {"term": {"doc_type.keyword": "intent"}}}
    results = es.search(index=workspace.index_name, body=query)
    results = [result["_source"] for result in results["hits"]["hits"]]
    intents = []
    for item in results:
        intent_name = item["intent"]
        examples_text = [example["text"] for example in item["examples"]]
        intent = Intent(intent_name, examples_text)
        intents.append(intent)
    return intents