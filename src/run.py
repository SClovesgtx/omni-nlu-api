# standard library imports
import sys

sys.path.append("./src/")

# local imports
from api.app import create_app

application = create_app()

if __name__ == "__main__":
    application.run(debug=False, host="0.0.0.0")
