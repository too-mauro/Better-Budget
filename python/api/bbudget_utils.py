import pyodbc
import json
import decimal

# ------------------------------------------------------------
# Better Budget Helper Methods.
# This is mostly to keep the api.py script relatively clean
#
# ------------------------------------------------------------

def createmssqlconnection():
    dbconn1 = pyodbc.connect(
        Trusted_Connection='No',
        Driver='{ODBC Driver 17 for SQL Server}',
        Server='localhost',
        Database='BETTER_BUDGET_DEV',
        UID='development',
        PWD='development')  # swap your credentials out here on a per-environment basis
    return dbconn1

def dec_serializer(o):
    if isinstance(o, decimal.Decimal):
        return float(o)

def logtodatabase(ipaddr, message, event_code):
    # dont forget to build log table in the database
    loggingscript = "INSERT INTO EVENT_LOGS (EVENT_TYPE, EVENT_TEXT, EVENT_DTTM, EVENT_IP_ADDR) " \
                    "VALUES ( ?, ?, GETDATE(), ?) ; "
    dbconn = createmssqlconnection()
    c = dbconn.cursor()
    try:
        c.execute(loggingscript, (event_code, message, ipaddr))
        c.commit()
        results = True
    except pyodbc.Error as e:
        dbconn.rollback()
        results = False
    dbconn.close()
    return results


def attemptRegister(username, passwd, email, ipaddr):
    insertscript = "INSERT INTO BBUDG_USERS (USER_NAME, USER_EMAIL, USER_HASHEDPASS, USER_REGISTERED_FROM_IP," \
                   "USER_REGISTERED_DTTM, USER_AUTH_TOKEN, USER_AUTH_TOKEN_EXP_DTTM, " \
                   "USER_DEACTIVATED_INDICATOR)VALUES ( ?, ?, ?, ?, GETDATE(), NEWID(), (getdate()+1), 'N' ) ; "
    check_username = "SELECT USER_KEY FROM BBUDG_USERS WHERE USER_NAME = ? ; "
    check_email = "SELECT USER_KEY FROM BBUDG_USERS WHERE USER_EMAIL = ? ;"
    get_token = "SELECT USER_AUTH_TOKEN FROM BBUDG_USERS WHERE USER_NAME = ? ;"
    conn = createmssqlconnection()
    c = conn.cursor()
    try:
        c.execute(check_username, (username,))
        if c.rowcount != 0:
            result = False
            message = "User already exists"
            token = None
            severity = "Error"
        else:
            c.execute(check_email, (email,))
            if c.rowcount != 0:
                result = False
                message = "Email address already taken"
                token = None
                severity = "Error"
            else:
                # ok if we made it this far we should be in the clear
                c.execute(insertscript, (username, email, passwd, ipaddr))
                c.commit()
                # need token
                c.execute(get_token, (username,))
                tmp = c.fetchone()
                token = tmp[0]
                message = None
                result = True
                severity = "Info"
    except pyodbc.Error as e:
        conn.rollback()
        result = False
        message = "Error connecting to the database. Error message from pyodbc: " + str(e)
        token = None
        severity = "Error"
    if severity == "Error":
        error_str = " ; An error was encountered: " + message
    else:
        error_str = ""
    logging_string = "Attempting to register new user: " + username + " ; Result is " \
                     + str(result) + error_str
    output_dict = {"operation": "register",
                   "username": username,
                   "result": result,
                   "error": message,
                   "token": token}
    logtodatabase(ipaddr, logging_string, severity)
    conn.close()
    return output_dict


def attemptLogin(username, passwd, ipaddr):
    verify_login_script = "SELECT USER_KEY, USER_HASHEDPASS FROM BBUDG_USERS WHERE USER_NAME = ? ;"
    update_token_script = "UPDATE BBUDG_USERS SET USER_AUTH_TOKEN = NEWID(), USER_AUTH_TOKEN_EXP_DTTM = GETDATE(" \
                          ")+1 WHERE USER_KEY = ? ; "
    get_token_script = "SELECT USER_AUTH_TOKEN FROM BBUDG_USERS WHERE USER_KEY = ? ;"
    conn = createmssqlconnection()
    c = conn.cursor()
    try:
        c.execute(verify_login_script, (username,))  # Check if the user already exists
        if c.rowcount == 0:
            message = "Username does not exist."
            result = False
            token = None
            severity = "Error"
        else:
            tmp = c.fetchone()
            userkey = tmp[0]
            userpass = tmp[1]
            verify_passwd = (userpass == passwd)  # check if the hashes match
            if not verify_passwd:
                message = "Password was not correct"
                result = False
                token = None
                severity = "Error"
            else:  # we good, refresh the token
                message = None
                c.execute(update_token_script, (userkey,))  # new login, update token
                c.commit()
                c.execute(get_token_script, (userkey,))
                tmp = c.fetchone()
                token = tmp[0]
                result = True
                severity = "Info"
    except pyodbc.Error as e:
        conn.rollback()
        result = False
        message = "Error connecting to the database. Error message from pyodbc: " + str(e)
        token = None
        severity = "Error"
    if severity == "Error":
        error_str = " ; An error was encountered: " + message
    else:
        error_str = ""
    logging_string = "Attempting login for user: " + username + " ; Result is " \
                     + str(result) + error_str
    logtodatabase(ipaddr, logging_string, severity)
    output_dict = {"operation": "login",
                   "username": username,
                   "result": result,
                   "error": message,
                   "token": token}
    conn.close()
    return output_dict


def getuseridfromtoken(uuid):
    getuserkey = "select USER_KEY from BBUDG_USERS where USER_AUTH_TOKEN = ? and USER_AUTH_TOKEN_EXP_DTTM >= GETDATE();"
    conn = createmssqlconnection()
    c = conn.cursor()
    try:
        c.execute(getuserkey, (str(uuid),))
        row = c.fetchone()
        if (not row) or (row is None):  # cursor rowcount doesnt work?
            message = "Login token not found. Please log in again"
            result = False
        else:
            message = None
            result = row[0]
    except pyodbc.Error as e:
        message = "There was a SQL error " + str(e)
        result = False

    output_dict = {"result": result,
                   "error": message}
    logging_string = "Checking uuid " + uuid + " for validity. Result is user_key=" + str(result)
    logtodatabase("localhost", logging_string, "Info")
    conn.close()
    return output_dict


def viewsyslogs():
    conn = createmssqlconnection()
    sql = "SELECT EVENT_KEY, EVENT_TYPE, EVENT_TEXT, EVENT_DTTM, EVENT_IP_ADDR FROM EVENT_LOGS ORDER BY 1;"
    c = conn.cursor()
    c.execute(sql)
    data = c.fetchall()
    events = []
    for line in data:
        event_line = {"event-key": line[0],
                      "event-type": line[1],
                      "event-text": line[2],
                      "event-dttm": line[3].isoformat(),
                      "event-ipaddr": line[4]}
        events.append(event_line)
    result = {
        "operation": "system event logs",
        "dataset": events}
    conn.close()
    return result

def getLineItems(budget_pool_id):
    conn = createmssqlconnection()
    sql = "SELECT USER_KEY, BUDGET_PL_ID, ITEM_NAME, AMOUNT_BUDGETED, AMOUNT_SPENT FROM BUDGET_POOL WHERE BUDGET_ID = ?" 
    c = conn.cursor()
    c.execute(sql, (int(budget_pool_id)))
    data = c.fetchall()
    line_items = []
    for row in data:
        line_item = {
            "user_key" : row[0],
            "budget_id" : row[1],
            "item_name" : row[2],
            "amount_budgeted" : dec_serializer(row[3]),
            "amount_spent" : dec_serializer(row[4])
        }
        line_items.append(line_item)
    result = {
        "operation" : "get line items",
        "dataset" : line_items
    }
    logging_string = "Getting line items for budget pool " + str(budget_pool_id) + "."
    logtodatabase("localhost", logging_string, "READ Operation")
    conn.close()
    return result

def getAccounts(account_type, user_key):
    conn = createmssqlconnection()
    c = conn.cursor()
    if(account_type == ""):
        sql = "SELECT ACCT_NAME, BALANCE, BANK_NAME, TYPE FROM ACCOUNTS WHERE USER_KEY = ?"
        c.execute(sql, (int(user_key)))
    else:
        sql = "SELECT ACCT_NAME, BALANCE, BANK_NAME, TYPE FROM ACCOUNTS WHERE USER_KEY = ? AND TYPE = ?"
        c.execute(sql, (int(user_key),str(account_type)))
    data = c.fetchall()
    accounts = []
    for row in data:
        account_data = {
            "account_name" : row[0],
            "balance" : dec_serializer(row[1]),
            "bank_name" : row[2],
            "type" : row[3]
            }
        accounts.append(account_data)
    print(accounts)
    if(account_type == ''):
        logging_string = "Getting account information for user " + str(user_key)+ "."
    else:
        logging_string = "Getting account information for user_key " + str(user_key) + ". Account Type: " + account_type

    result = {
        "operation" : "get account info",
        "dataset" : accounts
    }
    logtodatabase("localhost", logging_string, "READ Operation")
    conn.close()
    return result

def createBudget(month, year, expIncome, budType,user_key):
    conn = createmssqlconnection()
    c = conn.cursor()
    month_year = str(month) + '/' + str(year)
    sql = "INSERT INTO BUDGETS (USER_KEY, BUDGET_MONTH_NUM, BUDGET_YEAR_NUM, BUDGET_MONTH_YEAR, BUDGET_TYPE,EXPECTED_INCOME) VALUES (?,?,?,?,?,?)"
    try:
        c.execute(sql, (int(user_key), int(month), int(year), month_year, budType, expIncome))
        c.commit()
        print("affected rows = {}".format(c.rowcount))
        
        if c.rowcount > 0: 
            result = {
                "operation" : "Budget Successfully Created",
                "succeeded" : True
            }
        else:
            result = {
                "operation" : "Failed to Create Budget",
                "succeeded" : False
            }
    except:
        result = {
                "operation" : "Failed to Create Budget",
                "succeeded" : False
            }
    conn.close()
    return result

def deleteBudget(operation,budget_id):
    conn = createmssqlconnection()
    c = conn.cursor()

    if operation == "delete":
        sql = "DELETE FROM BUDGETS WHERE BUDGET_ID = ?"
        try:
            c.execute(sql, (int(budget_id)))
            c.commit()
            if(c.rowcount > 0):
                result = {
                    "operation" : "Attempting to delete budget",
                    "succeeded" : True
                 }
            else:
                result = {
                    "operation" : "Attempting to delete budget",
                    "succeeded" : False
                    }
                
        except:
            result = {
                    "operation" : "Attempting to delete budget",
                    "succeeded" : False
                    }
        conn.close()
        return result
            

def createBudgetPool(operation, budget_id, budget_pool_name, amount_budgeted,pool_type,user_key, amount_spent=None, budget_pool_id=None):
    conn = createmssqlconnection()
    c = conn.cursor()
    if operation == "create":
        try:
            sql = "INSERT INTO BUDGET_POOL (USER_KEY, BUDGET_ID, ITEM_NAME, AMOUNT_BUDGETED) VALUES (?,?,?,?)"
            c.execute(sql, (int(user_key), int(budget_id), str(budget_pool_name), str(amount_budgeted)))
            c.commit()
            print("affected rows = {}".format(c.rowcount))
            
            if c.rowcount > 0: 
                result = {
                    "operation" : "Attempting to create budget pool",
                    "succeeded" : True
                }
            else:
                result = {
                    "operation" : "Attempting to create budget pool",
                    "succeeded" : False
                }
        except:
            result = {
                    "operation" : "Attempting to create budget pool",
                    "succeeded" : False
                }
        conn.close()
        return result
    else:
        sql = "UPDATE BUDGET_POOL SET ITEM_NAME= ?, AMOUNT_BUDGETED = ?, AMOUNT_SPENT = ?, TYPE = ? WHERE BUDGET_PL_ID = ?"
        try:
            c.execute(sql, (str(budget_pool_name), str(amount_budgeted), float(amount_spent), str(pool_type), int(budget_id)))
            c.commit()
            print("affected rows = {}".format(c.rowcount))
            
            if c.rowcount > 0: 
                result = {
                    "operation" : "Attempting to update budget pool",
                    "succeeded" : True
                }
            else:
                result = {
                    "operation" : "Attempting to update budget pool",
                    "succeeded" : False
                }
        except:
            result = {
                    "operation" : "Attempting to update budget pool",
                    "succeeded" : False
                }
        conn.close()
        return result

def deleteBudgetPool(operation, budget_pool_id):
    conn = createmssqlconnection()
    c = conn.cursor()

    if operation == "delete":
        
        try:
            sql = "DELETE FROM BUDGET_POOL WHERE BUDGET_PL_ID = ?"
            c.execute(sql, (int(budget_pool_id)))
            c.commit()
            print("HERE")
            if c.rowcount > 0:
                result = {
                    "operation" : "Deleted a row from budget pool",
                    "succeeded" : True
                }
            else:
                result = {
                    "operation" : "Failed to delete a row from budget pool",
                    "succeeded" : False
                }
        except:
                result = {
                    "operation" : "Failed to delete budget pool",
                    "succeeded" : False
                }
    conn.close()
    return result


def addAccount(operation, account_name, bank_name, account_type, user_key, balance, account_id=None):
    conn = createmssqlconnection()
    c = conn.cursor()

    if balance == None:
        balance = 0

    if operation == "create":
        sql = "INSERT INTO ACCOUNTS (USER_KEY, ACCT_NAME, BALANCE, BANK_NAME, TYPE) VALUES (?,?,?,?,?)"
        
        try:
            c.execute(sql, (int(user_key),str(account_name),float(balance), str(bank_name), str(account_type)))
            c.commit()
        except:
            result = {
                "operation":"Failed to create account",
                "succeeded": False
            }
            return result

        if c.rowcount > 0: 
            result = {
                "operation" : "Account created",
                "succeeded" : True
            }
        else:
             result = {
                "operation" : "Failed to create account",
                "succeeded" : False
            } 
    elif operation == "update":
        sql = "UPDATE ACCOUNTS SET ACCT_NAME = ?, BALANCE = ?, BANK_NAME = ?, TYPE = ? WHERE ACCOUNT_ID = ?"
        try:
            c.execute(sql, (account_name,balance, bank_name, account_type,account_id))
            c.commit()
        except:
            result = {
                "operation":"General failure",
                "succeeded": False
            }
            return result
        if c.rowcount > 0: 
            result = {
                "operation" : "Successfully updated account",
                "succeeded" : True
            }
        else:
             result = {
                "operation" : "Failed to update account",
                "succeeded" : False
            }   
    elif operation == "delete":
        sql = "DELETE FROM ACCOUNTS WHERE ACCOUNT_ID = ?"
        try:
            c.execute(sql, (account_id))
            c.commit()
            if c.rowcount > 0: 
                result = {
                    "operation" : "Successfully deleted account",
                    "succeeded" : True
                }
            else:
                result = {
                    "operation" : "Failed to delete account",
                    "succeeded" : False
            }   
        except:
            result = {
                "operation" : "Failed to delete an account",
                "succeeded" : False
            }
        
    else:
        result = {
            "operation" : "Attempting to " + operation + " an account",
            "succeeded" : False
        }
    conn.close()
    return result



def payLineItem(user_key, line_item_id, amount_paid, account_id):
    conn = createmssqlconnection()
    c = conn.cursor()
    error = False
    if amount_paid == None:
        amount_paid = 0
    account_sql = "UPDATE ACCOUNTS SET BALANCE = (ISNULL(BALANCE,0) - ?) WHERE ACCOUNT_ID = ? AND USER_KEY = ?"
    budget_pool_sql = "UPDATE BUDGET_POOL SET AMOUNT_SPENT = (ISNULL(AMOUNT_SPENT,0) + ?) WHERE BUDGET_PL_ID = ? AND USER_KEY = ?"

    try:
        c.execute(account_sql, (amount_paid, account_id, user_key))
        c.commit()
        if(c.rowcount == 0):
            error = True
        c.execute(budget_pool_sql, (amount_paid, line_item_id, user_key))
        c.commit()
        if(c.rowcount == 0):
            error = True
    except:
        result = {
                "operation":"Transaction failed",
                "succeeded": False
            }
        return result
    if(not error):
        result = {
            "operation" : "Transaction Successful",
            "succeeded" : True
        }
    else:
        result = {
            "operation" : "Transaction Failed",
            "succeeded" : False
        }
    return result


def logTransaction(user_key, amount_spent, account_used, date, vendor, location, item, budget_pool_id, budget_id):
    conn = createmssqlconnection()
    c = conn.cursor()

    if(amount_spent == None):
        amount_spent = 0.0
    
    transaction_insert_sql = "INSERT INTO BUDGET_TRANSACTION (USER_KEY, BUDGET_PL_ID, BUDGET_ID, AMOUNT_SPENT, ACCOUNT_ID, TRANSACTION_DATE, VENDOR_DESC, LOCATION_DESC, ITEM_DESC) VALUES (?,?,?,?,?,?,?,?,?)"

    update_bpool_sql = "UPDATE BUDGET_POOL SET AMOUNT_SPENT = (ISNULL(AMOUNT_SPENT,0) + ?) WHERE BUDGET_PL_ID = ? AND USER_KEY = ?"

    update_account_sql =  "UPDATE ACCOUNTS SET BALANCE = (ISNULL(BALANCE,0) - ?) WHERE ACCOUNT_ID = ? AND USER_KEY = ?"

    try:
        c.execute(transaction_insert_sql,(user_key, budget_pool_id,budget_id,amount_spent,account_used,date,vendor,location,item))
        c.execute(update_bpool_sql, (amount_spent, budget_pool_id,user_key))
        c.execute(update_account_sql,(amount_spent,account_used,user_key))
        c.commit()
        result = {
            "operation" : "Successfully Logged Transaction",
            "succeeded" : True
        }
    except pyodbc.Error as err:
        print(err)
        result = {
            "operation" : "Failed to Log Transaction",
            "succeeded" : False
        }
    return result

def viewUserBudgets(user_key):
    conn = createmssqlconnection()
    c = conn.cursor()

    sql = "SELECT BUDGET_ID,BUDGET_MONTH_NUM, BUDGET_YEAR_NUM,BUDGET_MONTH_YEAR,BUDGET_TYPE,EXPECTED_INCOME FROM BUDGETS WHERE USER_KEY = ?"
    c.execute(sql,(str(user_key)))
    data = c.fetchall()
    budgets = []
    for row in data:
        budget = {
            "budget_id" : row[0],
            "budget_month" : row[1],
            "budget_year" : row[2],
            "budget_month_year" : row[3],
            "budget_type" : row[4],
            "expected_income" : dec_serializer(row[5])
        }
        budgets.append(budget)
    result = {
        "operation" : "Get Budgets",
        "dataset" : budgets
    }
    return result