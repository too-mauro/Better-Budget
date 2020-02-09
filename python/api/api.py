import json
# import flask
import pyodbc
from flask_api import FlaskAPI

app = FlaskAPI(__name__)


@app.route('/v0/test', methods=['GET'])
def testresp():
    obj = {
        "operation": "testing",
        "result": True,
        "response": "It's alive?"
    }
    return obj


@app.route('/v0/test2', methods=['GET'])
def testresp2():
    dbconn1 = pyodbc.connect(
        "DRIVER={ODBC Driver 17 for SQL Server};SERVER=127.0.0.1;DATABASE=BETTER_BUDGET_DEV;UID=development;PWD=development")
    c = dbconn1.cursor()
    c.execute("select IDENTITY_KEY, TEXTFIELD, INSERT_DTTM FROM PYODBC_TEST;")
    dataset = c.fetchall()
    result_json = []
    for item in dataset:
        tmp = {"identity-key": item[0],
               "text-field": item[1],
               "insert-dttm": item[2].isoformat()}
        result_json.append(tmp)
    return result_json


if __name__ == "__main__":
    app.run(debug=True)
