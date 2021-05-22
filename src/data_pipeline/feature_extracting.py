from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import OneHotEncoder
import pandas as pd


def encode_features(df):
    x_transformer = TfidfVectorizer()
    y_transformer = OneHotEncoder(sparse=False)

    X = x_transformer.fit_transform(df.cleaned_examples)
    y = y_transformer.fit_transform(df.intents.to_numpy().reshape(-1, 1))
    df["intents_onehot"] = list(y)
    df1 = pd.DataFrame(X.toarray(), columns=x_transformer.get_feature_names())
    df2 = df.join(df1)
    return df2, x_transformer, y_transformer
