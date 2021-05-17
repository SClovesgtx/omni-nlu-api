from sklearn.model_selection import train_test_split


def split(df):
    data = df.iloc(1)[4:]
    target = df[["intents", "intents_onehot"]]
    X_train, X_test, y_train, y_test = train_test_split(
        data, target, stratify=target.intents, test_size=0.33, random_state=42
    )
    return X_train, X_test, y_train, y_test
