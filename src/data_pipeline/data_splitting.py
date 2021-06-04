from sklearn.model_selection import train_test_split


def split(df):
    data = df[["cleaned_examples"]]
    target = df[["intents"]]
    X_train, X_test, y_train, y_test = train_test_split(
        data, target, stratify=target, test_size=0.2, random_state=42
    )
    return X_train, X_test, y_train, y_test
