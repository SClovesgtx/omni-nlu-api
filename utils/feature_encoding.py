from numpy import asarray
from sklearn.preprocessing import OneHotEncoder
from sklearn.feature_extraction.text import TfidfVectorizer

def intent_to_onehot(intents_names):
    data = asarray([ [intent_name]  for intent_name in intents_names])
    # define one hot encoding
    encoder = OneHotEncoder(sparse=False)
    # transform data
    intents_names_as_onehot = encoder.fit_transform(data)
    return intents_names_as_onehot


def encode_tfidf(all_examples):
    # create the transform
    vectorizer = TfidfVectorizer()
    # tokenize and build vocab
    vectorizer.fit(all_examples)
    return vectorizer
#     # summarize
#     print(vectorizer.vocabulary_)
#     print(vectorizer.idf_)
#     # encode document
#     vector = vectorizer.transform([text[0]])
#     # summarize encoded vector
#     print(vector.shape)
#     print(vector.toarray())
