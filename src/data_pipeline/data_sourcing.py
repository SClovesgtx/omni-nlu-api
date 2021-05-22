# standard library imports
import pandas as pd

# third party imports
# nothin yet

# local imports
# nothing yet


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
    list: a dataframe pandas with intens and examples

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
    data = []
    for item in results:
        if len(item["examples"]) >= 3:
            data += [(item["intent"], example["text"]) for example in item["examples"]]
    df = pd.DataFrame(data=data, columns=["intents", "examples"])
    return df
