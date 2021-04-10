
def intents_with_few_data(data):
    """
    Identify intents with less then 8 examples.
    We expect at least 8 examples for each intent,
    5 to train and 3 to test the ML models.
    
    Parameters
    ----------
    data: list of namedtuple representing Intents
    
    Returns
    -------
    A list of indexes of the intents with less then 8 examples
        
    Examples
    --------
    
    Raises
    ------
    
    Notes
    -----
    
    """
    return [i for i, intent in enumerate(data) if len(intent[1]) < 8]