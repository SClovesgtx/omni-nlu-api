from joblib import load
from tensorflow.keras.models import load_model
import os

local_path = os.path.dirname(os.path.abspath(__file__))
# import pathlib
#
# local_path = pathlib.Path(__file__).parent.absolute()

# local_path = "/home/cloves/Desktop/omni_nlp_api/models"

def load_models(workspace_id):
    svm = load(local_path+'/polySVM/trained_models/svm-{workspace_id}.joblib'.format(workspace_id=workspace_id))
    logit = load(local_path+'/multinomialLogit/trained_models/logit-{workspace_id}.joblib'.format(workspace_id=workspace_id))
    cnn = load_model(local_path+'/cnn/trained_models/cnn-{workspace_id}.h5'.format(workspace_id=workspace_id))
    return svm, logit, cnn


# class NeuralNetWork:
#     file_path = local_path+'/cnn/trained_models/cnn-{workspace_id}.h5'.format(workspace_id=workspace_id)
#     def __init__(self, workspace_id, accuracy):
#         if os.path.exists(file_path):
#             self.model_exist = True
#             self.accuracy = accuracy
#             self.model = load_model(file_path)
#             self.model._make_predict_function()
#         else:
#             self.model_exist = False
#             return {"response": "Please, use the /train endpoint to train your model first."}
#
#     def predict(self, encoded_sentence):
#         return self.model.predict(encoded_sentence)
