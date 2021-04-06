# standard library imports
import sys

sys.path.append("./src/api")

# third party imports
from flask import Flask


def create_app() -> Flask:
    """Create a app flask instance."""

    flask_app = Flask("omni_nlu_api")

    # local imports
    from nlp_models.models_settings.controller import models_settings_app
    from nlp_models.intents.controller import intents_app
    from nlp_models.entities.controller import entities_app
    from nlp_models.resources.train.controller import train_app
    from nlp_models.resources.classify.controller import classify_app

    flask_app.register_blueprint(models_settings_app)
    flask_app.register_blueprint(intents_app)
    flask_app.register_blueprint(entities_app)
    flask_app.register_blueprint(train_app)
    flask_app.register_blueprint(classify_app)

    return flask_app
