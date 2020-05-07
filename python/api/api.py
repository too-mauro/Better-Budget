import json
import pyodbc
from flask_api import FlaskAPI
from flask import request
import bbudget_utils

app = FlaskAPI(__name__)


#
#  v0, does not do anything meaningful, only useful to see that the services are alive
#
@app.route('/v0/test', methods=['GET'])
def testresp():
    obj = {
        "operation": "testing",
        "result": True,
        "response": "It's alive?"
    }
    return obj


@app.route('/v0/echo', methods=['POST'])
def testecho():
    # should echo back whatever json string you pass it in a post body
    return request.json


@app.route('/v0/test2', methods=['GET'])
def testresp2():
    dbconn1 = bbudget_utils.createmssqlconnection()
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


@app.route('/v0/authtest', methods=['GET'])
def authtest():
    uuid = request.headers.get('Authorization')
    # in /etc/apache2/sites-available/000-default.conf, make sure WSGIPassAuthorization is defined as On
    # otherwise the Authorization header will come out null
    return bbudget_utils.getuseridfromtoken(uuid)


#
#  v1 methods for the application itself
#
@app.route('/v1/authentication', methods=['POST'])
def authenticate():
    print(request.json)
    authinput = request.json
    if not authinput["operation"]:
        # operation is required, need to know what action to take
        result = False
        message = "json key operation is missing from your request"
    elif authinput["operation"] == "register":
        # register new account here
        out_reg = bbudget_utils.attemptRegister(authinput["username"], authinput["pw"], authinput["email"],
                                                authinput["ip"])
        return out_reg
    elif authinput["operation"] == "login":
        # attempt login here
        out_login = bbudget_utils.attemptLogin(authinput["username"], authinput["pw"], authinput["ip"])
        return out_login
    else:
        # you fucked up
        result = False
        message = "Bad operation. I don't know what " + authinput["operation"] + " means."
    return {"result": result,
            "message": message}


@app.route('/v1/system/viewlogs', methods=['GET'])
def getsyslogs():
    return bbudget_utils.viewsyslogs()

@app.route('/v1/system/viewLineItems', methods=['POST'])
def getLineItems():
    user_input = request.json
    budget_id = user_input["budget_id"]
    return bbudget_utils.getLineItems(budget_id)

@app.route('/v1/system/viewAccountInfo', methods=['POST'])
def getAccountInfo():
    authinput = request.json
    user_key = authinput["user_id"]
    if authinput["account_type"] == "":
        return bbudget_utils.getAccounts("",user_key)
    else:
        return bbudget_utils.getAccounts(str(authinput["account_type"]),user_key)

@app.route('/v1/system/setUpBudget', methods=['POST'])
def createBudget():
    userInput = request.json
    month = userInput["month"]
    year = userInput["year"]
    expIncome = userInput["expected_income"]
    budType = userInput["type"]
    user_key = userInput["user_id"]
    return bbudget_utils.createBudget(month,year,expIncome,budType,user_key)

@app.route('/v1/system/deleteBudget', methods=["POST"])
def deleteBudget():
    user_input = request.json
    operation = user_input["operation"]
    budget_id = user_input["budget_id"]
    return bbudget_utils.deleteBudget(operation,budget_id)

@app.route('/v1/system/addBudgetPool', methods=["POST"])
def createBudgetPool():
    user_input = request.json

    operation = user_input["operation"]
    if operation == "create":
        budget_id = user_input["budget_id"]
        budget_pool_name = user_input["budget_pool_name"]
        amount_budgeted = user_input["amount_budgeted"]
        pool_type = user_input["pool_type"]
        user_id = user_input["user_id"]
        return bbudget_utils.createBudgetPool(operation, budget_id,budget_pool_name,amount_budgeted,pool_type,user_id)
    elif operation == "update":
        budget_pl_id = user_input["budget_pool_id"]
        budget_id = user_input["budget_id"]
        budget_pool_name = user_input["budget_pool_name"]
        amount_budgeted = user_input["amount_budgeted"]
        amount_spent = user_input["amount_spent"]
        pool_type = user_input["pool_type"]
        user_id = user_input["user_id"]
        return bbudget_utils.createBudgetPool(operation, budget_id,budget_pool_name,amount_budgeted, pool_type,user_id,amount_spent,budget_pl_id)
    else:
        return {
            "operation" : "Invalid Operation",
            "result" : "false"
        }

@app.route('/v1/system/deleteBudgetPool', methods=["POST"])
def deleteBudgetPool():
    user_input = request.json
    operation = user_input["operation"]
    budget_pool_id = user_input["budget_pool_id"]
    return bbudget_utils.deleteBudgetPool(operation, budget_pool_id)



@app.route('/v1/system/addAccount', methods=["POST"])
def addAccount():
    user_input = request.json

    operation = user_input["operation"]
    user_key = user_input["user_key"]
    account_name = user_input["account_name"]
    bank_name = user_input["bank_name"]
    account_type = user_input["account_type"]
    balance = user_input["balance"]
    if operation == "create":
        return bbudget_utils.addAccount(operation, account_name,bank_name,account_type, user_key, balance, None)
    else:
        account_id = user_input["account_key"]
        return bbudget_utils.addAccount(operation, account_name,bank_name,account_type, user_key, balance, account_id)


@app.route('/v1/system/payLineItem', methods=["POST"])
def payLineItem():
    user_input = request.json

    line_item_id = user_input["line_item_id"]
    amount_paid = user_input["amount_paid"]
    account_id = user_input["account_id"]
    user_key = user_input["user_key"]
    return bbudget_utils.payLineItem(user_key,line_item_id,amount_paid,account_id)


@app.route('/v1/system/logTransaction', methods=["POST"])
def logTransaction():
    user_input = request.json

    user_key = user_input["user_key"]
    amount_spent = user_input["amount_spent"]
    account_used = user_input["account_id"]
    date = user_input["date"]
    vendor = user_input["vendor"]
    location = user_input["location"]
    item = user_input["item"]
    budget_pool_id = user_input["budget_pool_id"]
    budget_id = user_input["budget_id"]

    return bbudget_utils.logTransaction(user_key,amount_spent,account_used,date,vendor,location,item,budget_pool_id,budget_id)

@app.route('/v1/system/viewUserBudgets', methods=["POST"])
def viewUserBudgets():
    user_input = request.json
    user_key = user_input["user_id"]

    return bbudget_utils.viewUserBudgets(user_key)

if __name__ == "__main__":
    app.run(debug=True)
