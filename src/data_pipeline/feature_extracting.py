from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import OneHotEncoder
import pandas as pd


def tfidf_feature_ext(X_train):
    data_transformer = TfidfVectorizer()
    # y_transformer = OneHotEncoder(sparse=False)

    X = data_transformer.fit_transform(X_train.cleaned_examples)
    # y = y_transformer.fit_transform(df.intents.to_numpy().reshape(-1, 1))
    # df["intents_onehot"] = list(y)
    df = pd.DataFrame(X.toarray(), columns=data_transformer.get_feature_names())
    return df, data_transformer


def apply_transform(X_test, data_transformer):
    X = data_transformer.transform(X_test.cleaned_examples)
    df = pd.DataFrame(X.toarray(), columns=data_transformer.get_feature_names())
    return df
