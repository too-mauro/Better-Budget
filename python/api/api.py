import json
import flask
from flask_api import FlaskAPI

app = FlaskAPI(__name__)


@app.route('/v0/test', methods=['GET'])
def resp():
    obj = {
        "operation": "testing",
        "result": True,
        "response": "It's alive?"
    }
    return obj


if __name__ == "__main__":
    app.run(debug=True)
