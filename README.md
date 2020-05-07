# Better Budget
Better Budget is a capstone project built on a Node.js/HTML front-end, a Microsoft SQL Server back-end, and a Python API which takes and returns JSON data. This is a single-server system that can login/register users, create/delete budgets, add/remove/update budget pools and accounts, and pay line items.

## Setting Up the Back-End
Please refer to [this guide](https://docs.microsoft.com/en-us/sql/linux/sql-server-linux-setup?view=sql-server-ver15) for installing Microsoft SQL Server on Linux. Once installed, open an application that can view SQL Server databases (DBeaver Community Edition works well) and create a new database. Either use the system administrator account or create a new one with system administrator privileges, then run the `createDBWithIdentities.sql` file in the repository from within the application. This will create the necessary tables for the API to function properly.

## Setting Up the Front-End
The front-end is mostly plug-and-play. Install Node.js v12 or later (see [the Node.js website](https://nodejs.org/en/) for installation), then go to the directory where this project was cloned. Open a terminal from that directory and type `npm install`, which will install everything necessary for the server to run.

Within the directory, create a new file and name it `.env`. Open it and enter the following data:
```
PORT=(custom port number here, or remove the whole line to use the default port: 3000)
ACCESS_TOKEN_SECRET='(access token hash string here)'
REFRESH_TOKEN_SECRET='(refresh token hash string here)'
```
(For the latter two, the values can be anything you'd like. However, it's recommended to use a random 64-character hash string for security. In a terminal, enter `node` in the window. Then, enter the following command: `require("crypto").createHash('sha256').digest('hex').toString()`, which will generate a 64-character hashed string. Run it once for each token secret you'd like to use, and copy-paste the different strings into each of the fields in the '.env' file. Exit the Node command line with '.exit', then save and close the '.env' file.)

Finally, type `node server.js` in the terminal, which will start listening for the front-end server on either the designated port from the '.env' file or on port 3000.
