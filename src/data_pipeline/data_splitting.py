import random
import math
from collections import namedtuple

Example = namedtuple('Example', 'intent_name example')
TEST_RATIO = 0.3
RANDOM_SEED = 42
MIN_TOTAL_EXAMPLES = 8
MIN_EXAMPLES_FOR_TRAIN = 5

def data_splitting(data, test_ratio=TEST_RATIO, random_seed=RANDOM_SEED):
    random.seed(random_seed)
    train = []; test = []
    for intent in data:
        intent_name = intent[0]
        intent_examples = intent[1]
        total_examples = len(intent_examples)
        indexes = set(range(0, total_examples))
        if total_examples >= MIN_TOTAL_EXAMPLES:
            k = math.ceil(total_examples * test_ratio)
        elif total_examples > MIN_EXAMPLES_FOR_TRAIN and total_examples <= MIN_TOTAL_EXAMPLES:
            k = 3 - (MIN_TOTAL_EXAMPLES - total_examples)
        else:
            k = 1
            
        test_indexes = set(
            random.sample(
                population=indexes, 
                k=k
            )
        )
        
        train_indexes = indexes - test_indexes
        
        train_examples = list(
            map(intent_examples.__getitem__, train_indexes)
        )
        
        test_examples = list(
            map(intent_examples.__getitem__, test_indexes)
        )
        
        train += [Example(intent_name, example) for example in train_examples]
        test += [Example(intent_name, example) for example in test_examples]
        
    return train, test