from sklearn.feature_extraction.text import TfidfVectorizer
import pandas as pd


def encode_features(df):
    transformer = TfidfVectorizer()
    X = transformer.fit_transform(df["cleaned_examples"])
    df1 = pd.DataFrame(X.toarray(), columns=transformer.get_feature_names())
    df2 = df.join(df1)
    return df2, transformer
