from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout
from tensorflow.keras.optimizers import Adam
import os

local_path = os.path.dirname(os.path.abspath(__file__))


def set_model(input_shape, number_of_intent_classes, settings):
    # Initializes a sequential model
    model = Sequential()

    # input
    model.add(
        Dense(
            units=input_shape[0],
            activation="relu",
            input_shape=input_shape,
            name="input_layer",
        )
    )

    # intermediate_layers
    if settings != None:
        layer_number = 1
        for layer_defination in settings["intermediate_layers"]:
            model.add(
                Dense(
                    units=layer_defination["number_of_neurons"]
                    if layer_defination.get("number_of_neurons", None) != None
                    else input_shape[0],
                    activation=layer_defination["activation"]
                    if layer_defination.get("activation", None) != None
                    else "relu",
                    name=f"intermediate_layer_{layer_number}",
                )
            )
            layer_number += 1
        learning_rate = (
            settings["learning_rate"]
            if settings.get("learning_rate", None) != None
            else 0.001
        )
        loss = (
            settings["loss"]
            if settings.get("loss", None) != None
            else "categorical_crossentropy"
        )
    else:
        model.add(Dense(units=input_shape[0], activation="relu", name="layer_2"))
        learning_rate = 0.001
        loss = "categorical_crossentropy"

    # Output
    model.add(
        Dense(units=number_of_intent_classes, activation="softmax", name="output_layer")
    )

    # Compile the model
    model.compile(
        optimizer=Adam(learning_rate=learning_rate),
        loss=loss,  # cosine_similarity, categorical_crossentropy, etc
        metrics=["accuracy"],
    )

    return model


def train_cnn_model(X_train, y_train, X_test, y_test, workspace_id, settings=None):
    input_shape = (X_train.shape[1],)
    number_of_intent_classes = y_train.shape[1]

    if settings != None:
        model = set_model(input_shape, number_of_intent_classes, settings)
        history = model.fit(
            X_train,
            y_train,
            epochs=settings["epochs"] if settings.get("epochs") else 100,
            verbose=False,
            batch_size=settings["batch_size"] if settings.get("batch_size") else 100,
            validation_data=(X_test, y_test),
        )
    else:
        model = set_model(input_shape, number_of_intent_classes, settings)
        history = model.fit(
            X_train,
            y_train,
            epochs=100,
            verbose=False,
            batch_size=100,
            validation_data=(X_test, y_test),
        )

    _, acc = model.evaluate(X_test, y_test)
    file = local_path + "/trained_models/cnn-{workspace_id}.h5".format(
        workspace_id=workspace_id
    )
    model.save(file)
    return acc
