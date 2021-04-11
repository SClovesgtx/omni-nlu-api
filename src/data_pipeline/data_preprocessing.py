import random
from collections import namedtuple

Intent = namedtuple('Intent', 'intent_name examples_text')
Example = namedtuple('Example', 'intent_name example_text')

import pt_core_news_lg

nlp = pt_core_news_lg.load()
MIN_TOTAL_EXAMPLES = 8
MIN_EXAMPLES_FOR_TRAIN = 5
RANDOM_SEED = 42

# STOP_WORDS = read("data_pipe")

def keep_token(token):
    return token.is_alpha and not (token.is_space or token.is_punct)


def create_artificial_example(example):
    doc = nlp(example)
    return " ".join([token.lemma_ for token in doc if keep_token(token)]).lower()

def how_many_to_create(examples):
    """
    All possibilities:
    
    7 examples returns 1
    6 examples returns 2
    5 examples returns 3
    4 examples returns 4
    3 examples returns 3
    2 examples returns 2
    1 example  returns 1
    
    """
    quantity_of_examples = len(examples)
    quantity_to_complete = MIN_TOTAL_EXAMPLES - quantity_of_examples
    if quantity_to_complete >= MIN_EXAMPLES_FOR_TRAIN:
        return quantity_of_examples
    return quantity_to_complete

def fill_missing_examples(data, random_seed=RANDOM_SEED):
    """
    We expect at least 8 examples for each intent,
    5 to train and 3 to test the ML models.
    
    This function identify intents with less then 8 examples
    and fill it up with artificial examples created from the 
    exesting ones.
    
    Parameters
    ----------
    data: list of namedtuple representing Intents
    
    Returns
    -------
    list: list of namedtuple representing Intents
        
    Examples
    --------
    input = [
        Intent(
            intent_name='Inativar_Posição', 
            examples_text=['Como realizo a inativação de uma posição de minha estrutura?', 
                           'Como realizo a reativação de uma posição em minha estrutura?', 
                           'Em quanto tempo a inativação de uma posição é efetivada?', 
                           'Gostaria de fazer a inativação de uma posição, como faço?', 
                           'Realizei a inativação de uma posição e ela continua visível?']
            )
    ]

    output = [
        Intent(
            intent_name='Inativar_Posição', 
            examples_text=['Como realizo a inativação de uma posição de minha estrutura?', 
                           'Como realizo a reativação de uma posição em minha estrutura?', 
                           'Em quanto tempo a inativação de uma posição é efetivada?', 
                           'Gostaria de fazer a inativação de uma posição, como faço?', 
                           'Realizei a inativação de uma posição e ela continua visível?', 
                           'como realizar o inativação de umar posição de meu estruturar', 
                           'realizei o inativação de umar posição e ele continuar visível', 
                           'em quantum tempo o inativação de umar posição ser efetivada']
        )
    ]
    
    Raises
    ------
    
    Notes
    -----
    
    """
    random.seed(random_seed)
    new_data = []
    for intent in data:
        intent_name = intent[0]
        real_examples = intent[1]
        if len(real_examples) < MIN_TOTAL_EXAMPLES:
            qt = how_many_to_create(real_examples)
            sample = random.sample(real_examples, qt)
            artificial_examples = [create_artificial_example(example) for example in sample]
            intent_examples = real_examples + artificial_examples
            new_intent = Intent(intent_name, intent_examples)
            new_data.append(new_intent)
        else:
            new_data.append(intent)
    return new_data


def clean(text):
    text = text.lower()
    text = nlp(text)


def clean_examples(train, test):
    cleaned_examples = []
    for example in train + test:
        intent_name = example[0]
        example_text = example[1]
        cleaned_text = clean(example_text)
        cleaned_example = Example(intent_name, cleaned_text)
        cleaned_examples.append(cleaned_example)
    cleaned_train = clean_examples[:len(train)]
    cleaned_test = clean_examples[len(train):]
    return cleaned_train, cleaned_test
    
    