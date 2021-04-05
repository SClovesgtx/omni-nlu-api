# standard library imports
import sys

sys.path.append("./src/api")

# third party imports
from flask import Flask


def create_app() -> Flask:
    """Create a app flask instance."""

    flask_app = Flask("omni_nlu_api")

    # local imports
    from endpoints.models_settings.controller import models_settings_app
    from endpoints.intents.controller import intents_app
    from endpoints.entities.controller import entities_app
    from endpoints.train.controller import train_app
    from endpoints.classify.controller import classify_app

    flask_app.register_blueprint(models_settings_app)
    flask_app.register_blueprint(intents_app)
    flask_app.register_blueprint(entities_app)
    flask_app.register_blueprint(train_app)
    flask_app.register_blueprint(classify_app)

    return flask_app
