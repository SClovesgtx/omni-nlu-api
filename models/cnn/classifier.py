from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout
from tensorflow.keras.optimizers import Adam
import os

local_path = os.path.dirname(os.path.abspath(__file__))

def set_model(input_shape, number_of_intent_classes):
    # Initializes a sequential model
    model = Sequential()

    # 1º layer
    model.add(Dense(input_shape[0], activation='relu', input_shape = input_shape,
                    name='input_layer'))

     # 2º layer
    model.add(Dense(input_shape[0], activation='relu', name='layer_2'))

    # Output layer
    model.add(Dense(number_of_intent_classes,
                    activation='softmax', name='output_layer'))

    # Compile the model
    model.compile(optimizer=Adam(learning_rate=0.001),
               loss='categorical_crossentropy',
               # loss="cosine_similarity",
               metrics=['accuracy'])

    return model

def train_cnn_model(X_train, y_train, X_test, y_test, workspace_id):
    input_shape = (X_train.shape[1],)
    number_of_intent_classes = y_train.shape[1]

    model = set_model(input_shape, number_of_intent_classes)
    history = model.fit(X_train, y_train,
                 epochs=100,
                 verbose=False,
                 batch_size=100,
                 validation_data=(X_test, y_test))

    _, acc = model.evaluate(X_test, y_test)
    file = local_path + "/trained_models/cnn-{workspace_id}.h5".format(workspace_id=workspace_id)
    model.save(file)
    return acc
