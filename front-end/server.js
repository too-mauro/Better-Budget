'use strict';
const express = require('express');
const app = express();
const bodyParser = require('body-parser');
const cookieParser = require('cookie-parser');
require('dotenv').config();
const axios = require('axios');
const fs = require('fs');
const jwt = require('jsonwebtoken');
const port = process.env.PORT || 3000;

// used for JSON refresh tokens, might want to use a database to store them
let refreshTokens = [];

// Initialize everything
app.use(express.json());
app.set('view engine', 'ejs');
app.use(express.static('public'));
app.use(bodyParser.urlencoded({ extended: false }));
app.use(cookieParser());

// Main page after authentication
app.get('/', (req, res) => {
	res.render("pages/index");
});

// attempt to register a user
app.post('/register', (req, res) => {

	axios.post("http://localhost/api/v1/authentication", {
	  operation: 'register',
	  username: req.body.username,
	  email: req.body.email,
	  pw: req.body.password,
	  ip: req.connection.remoteAddress
	})
	.then((apiData) => {
		console.log(apiData);
	  if (!apiData.data.result) {
	  	res.render('pages/auth', {message: "Couldn't register successfully. Please try again.", error: apiData.data.error});
	  }
	  else {
	  	res.render('pages/auth', {message: `${apiData.data.username} has been successfully registered.`, error: null});
	  }
	})
	.catch((error) => {
	  res.render('pages/auth', {message: "Something went wrong!", error: error});
	});
});

// Login page
app.get('/auth', (req, res) => {
	res.render('pages/auth', {message: "Please login with your credentials below.", error: null});
});

// attempt to log onto the system
app.post('/login', (req, res) => {

	axios.post("http://localhost/api/v1/authentication", {
	  operation: 'login',
	  username: req.body.username,
	  pw: req.body.password,
	  ip: req.connection.remoteAddress
	})
	.then((apiData) => {
	  if (!apiData.data.result) {
	  	res.render("pages/auth", {message: "Couldn't authenticate successfully. Please try again.", error: apiData.data.error});
	  }
	  else {
	  	const user = {name: req.body.username};
	  	const accessToken = generateAccessToken(user);
	  	const refreshToken = jwt.sign(user, process.env.REFRESH_TOKEN_SECRET);
	  	//refreshTokens = refreshTokens.push(refreshToken);
	  	return res.redirect(301, "./index");
	  }
	})
	.catch((error) => {
	  res.render('pages/auth', {message: "Something went wrong!", error: error});
	});
});

// used for regenerating auth tokens
app.post("/token", (req, res) => {
	const refreshToken = req.body.token;
	if (refreshToken == null) { return res.sendStatus(401); }
	if (!refreshTokens.includes(refreshToken)) { return res.sendStatus(403); }
	jwt.verify(refreshToken, process.env.REFRESH_TOKEN_SECRET, (err, user) => {
		if (err) { return res.sendStatus(403); }
		const accessToken = generateAccessToken({ name: user.name });
		res.json({ accessToken });
	});
});

// Alias for main page after authentication
app.get('/index', (req, res) => {
	res.render('pages/index');
});

// show budgets
app.get('/budgets', (req, res) => {
	axios.post("http://localhost/api/v1/system/viewUserBudgets", {
			"user_id" : 1,
		})
		.then((apiData) => {
			console.log(apiData.data.dataset);
		  if (apiData.data.dataset.length < 1) {
		  	res.render("pages/budgets", {message: "There are no budgets yet! Create one with the \"Create Budget\" button!", error: null});
		  }
		  else {
		  	let budgetList = "";
		  	for (let b = 0; b < apiData.data.dataset.length; b++) {
		  		budgetList += `Budget ID: ${apiData.data.dataset[b].budget_id}<br>`;
		  		budgetList += `Budget Month: ${apiData.data.dataset[b].budget_month}<br>`;
		  		budgetList += `Budget Year: ${apiData.data.dataset[b].budget_year}<br>`;
		  		budgetList += `Budget Month/Year: ${apiData.data.dataset[b].budget_month_year}<br>`;
		  		budgetList += `Budget Type: ${apiData.data.dataset[b].budget_type}<br>`;
		  		budgetList += `Budget's Expected Income: $${apiData.data.dataset[b].expected_income}<br><br>`;
		  	}

		  	res.render("pages/budgets", {message: budgetList, error: null});
		  }
		})
		.catch((error) => {
			res.render("pages/budgets", {message: "Something went wrong!", error: error});
		  	console.error(error);
	});
});

// add budgets
app.post('/budgetadd', (req, res) => {

	axios.post("http://localhost/api/v1/system/setUpBudget", {
		"month" : parseInt(req.body.month),
		"year" : parseInt(req.body.year),
		"expected_income" : req.body.income,
		"type" : req.body.name,
		"user_id" : 1
	})
	.then((apiData) => {
	  if (!apiData.data.succeeded) {
	  	console.log(res.data.operation);
	  	es.render("pages/budgets", {message: apiData.data.operation, error: null});
	  }
	  else {
	  	console.log("Budget created successfully")
	  	res.render("pages/budgets", {message: `The budget ${req.body.name} has been successfully created.`, error: null});
	  }
	})
	.catch((error) => {
	  //console.error(error);
	  res.render("pages/budgets", {message: "Something went wrong!", error: error});
	});
});

// delete budgets
app.post('/budgetdel', (req, res) => {

	axios.post("http://localhost/api/v1/system/deleteBudget", {
		"operation" : 'delete',
		"budget_id": parseInt(req.body.budgetID)
	})
	.then((apiData) => {
	  if (!apiData.data.succeeded) {
	  	res.render("pages/budgets", {message: apiData.data.operation, error: null});
	  }
	  else {
	  	console.log("Budget deleted successfully")
	  	res.render("pages/budgets", {message: `Budget with ID ${req.body.budgetID} has been successfully deleted.`, error: null});
	  }
	})
	.catch((error) => {
	  console.error(error);
	  res.render("pages/budgets", {message: "Something went wrong!", error: error});
	  });
});

// show budget pools
app.get('/pools', (req, res) => {
	res.render("pages/pools", {message: `Create, update, or delete budget pools here.`, error: null});
});

app.post('/pooladd', (req, res) => {
	axios.post("http://localhost/api/v1/system/addBudgetPool", {
			"operation": "create",
			"budget_id": req.body.budgetID,
			"budget_pool_name": req.body.poolName,
			"amount_budgeted": req.body.budgetAmt,
			"pool_type": req.body.poolType,
			"user_id" : 1
		})
		.then((apiData) => {
		  if (!apiData.data.succeeded) {
		  	res.render("pages/pools", {message: `Budget pool ${req.body.poolName} could not be created.`, error: null});
		  }
		  else {
		  	res.render("pages/pools", {message: `Budget pool ${req.body.poolName} has been successfully created.`, error: null});
		  }
		})
		.catch((error) => {
			res.render("pages/pools", {message: "Something went wrong!", error: error});
		  	console.error(error);
	});
});

app.post('/poolupdate', (req, res) => {
	axios.post("http://localhost/api/v1/system/addBudgetPool", {
			"operation" : "update",
			"budget_pool_id" : req.body.poolID,
			"budget_id" : req.body.budgetID,
			"budget_pool_name" : req.body.poolName,
			"amount_budgeted" : req.body.budgetAmt,
			"amount_spent" : req.body.amtSpent,
			"pool_type" : req.body.poolType,
			"user_id" : 1
		})
		.then((apiData) => {
		  if (!apiData.data.succeeded) {
		  	res.render("pages/pools", {message: `Budget pool ${req.body.poolName} could not be updated.`, error: null});
		  }
		  else {
		  	res.render("pages/pools", {message: `Budget pool ${req.body.poolName} has been successfully updated.`, error: null});
		  }
		})
		.catch((error) => {
			res.render("pages/pools", {message: "Something went wrong!", error: error});
		  	console.error(error);
	});
});

app.post('/pooldel', (req, res) => {
	axios.post("http://localhost/api/v1/system/deleteBudgetPool", {
			"operation" : "delete",
			"budget_pool_id" : req.body.poolID
		})
		.then((apiData) => {
		  if (!apiData.data.succeeded) {
		  	res.render("pages/pools", {message: `Budget pool with ID ${req.body.poolID} could not be deleted.`, error: null});
		  }
		  else {
		  	res.render("pages/pools", {message: `Budget pool with ID ${req.body.poolID} has been successfully deleted.`, error: null});
		  }
		})
		.catch((error) => {
			res.render("pages/pools", {message: "Something went wrong!", error: error});
		  	console.error(error);
	});
});

// show line items
app.get("/line", (req, res) => {
	res.render('pages/line', {message: "Please enter a budget ID to view its line items.", error: null});
});

app.post("/line", (req, res) => {
	axios.post("http://localhost/api/v1/system/viewLineItems" , {
		"budget_id": req.body.budgetID
	})
	.then((apiData) => {
		if (apiData.data.dataset.length < 1) {
			res.render('pages/line', {message: `There are no line items for the budget with an ID of ${req.body.budgetID}!`, error: null});
		}
		else {
			let litems = "";
			for (let i = 0; i < apiData.data.dataset.length; i++) {
				litems += `Budget ID: ${apiData.data.dataset[i].budget_id}<br>`;
				litem += `Item Name: ${apiData.data.dataset[i].item_name}<br>`;
				litem += `Amount Budgeted: $${apiData.data.dataset[i].amount_budgeted}<br>`;
				if (apiData.data.dataset[i].amount_spent == null) {
					litem += `Amount Spent: $0.00<br><br>`;
				}
				else {
					litem += `Amount Spent: $${apiData.data.dataset[i].amount_spent}<br><br>`;
				}
			}
			res.render('pages/line', {message: litems, error: null});
		}
	})
	.catch((error) => {
		res.render('pages/line', {message: "Something went wrong!", error: error});
	})
});

// Accounts page
app.get('/account', (req, res) => {
	axios.post("http://localhost/api/v1/system/viewAccountInfo", {
		"account_type": "",
		"user_id": 1
	})
	.then((apiData) => {
		if (apiData.data.dataset.length < 1) {
			res.render('pages/account', {message: `No accounts found! Create one using the "Create Account" button.`, error: null});
		}
		else {
			let accountInfo = "";
			for (let ac = 0; ac < apiData.data.dataset.length; ac++) {
				accountInfo += `Account Name: ${apiData.data.dataset[ac].account_name}<br>`;
				accountInfo += `Balance: $${apiData.data.dataset[ac].balance}<br>`;
				accountInfo += `Bank: ${apiData.data.dataset[ac].bank_name}<br>`;
				accountInfo += `Account Type: ${apiData.data.dataset[ac].type}<br><br>`;
			}
		res.render('pages/account', {message: accountInfo, error: null});
		}
	})
	.catch((error) => {
		res.render('pages/account', {message: "Something went wrong!", error: error});
	});
});

// add account
app.post('/accountadd', (req, res) => {
	axios.post("http://localhost/api/v1/system/addAccount", {
		"operation": "create",
		"user_key": 1,
		"account_name": req.body.account,
		"bank_name": req.body.bank,
		"account_type": req.body.type,
		"balance": req.body.balance
	})
	.then((apiData) => {
		if (!apiData.data.succeeded) {
			res.render('pages/account', {message: `Couldn't add account ${req.body.account}.`, error: null});
		}
		else {
			res.render('pages/account', {message: `The account ${req.body.account} has been created successfully.`, error: null});
		}
	})
	.catch((error) => {
		res.render('pages/account', {message: "Something went wrong!", error: error});
	});
});

// update account
app.post('/accountupdate', (req, res) => {
	axios.post("http://localhost/api/v1/system/addAccount", {
		"operation": "update",
		"user_key": 1,
		"account_name": req.body.account,
		"bank_name": req.body.bank,
		"account_type": req.body.type,
		"balance": req.body.balance,
		"account_key": 7
	})
	.then((apiData) => {
		if (!apiData.data.succeeded) {
			res.render('pages/account', {message: `Couldn't update account ${req.body.account}.`, error: null});
		}
		else {
			res.render('pages/account', {message: `The account ${req.body.account} has been updated successfully.`, error: null});
		}
	})
	.catch((error) => {
		res.render('pages/account', {message: "Something went wrong!", error: error});
	});
});

// delete account
app.post('/accountdel', (req, res) => {
	axios.post("http://localhost/api/v1/system/addAccount", {
		"operation": "delete",
		"user_key": 1,
		"account_name": req.body.account,
		"bank_name": req.body.bank,
		"account_type": req.body.type,
		"balance": req.body.balance,
		"account_key" : 7
	})
	.then((apiData) => {
		if (!apiData.data.succeeded) {
			res.render('pages/account', {message: `Couldn't delete account ${req.body.account}.`, error: null});
		}
		else {
			res.render('pages/account', {message: `The account ${req.body.account} has been deleted successfully.`, error: null});
		}
	})
	.catch((error) => {
		res.render('pages/account', {message: "Something went wrong!", error: error});
	});
});

// pay line item page
app.get("/pay", (req, res) => {
	res.render("pages/pay", {message: "Enter the requested information above, then click \"Submit\".", error: null});
});

app.post("/pay", (req, res) => {
	let date = new Date();
	axios.post("http://localhost/api/v1/system/logTransaction", {
		"user_key" : 1,
		"budget_pool_id" : req.body.poolID,
		"budget_id" : req.body.budgetID,
		"date" : `${date.getFullYear()}-${date.getMonth() + 1}-${date.getDate()}`,
		"vendor" : req.body.vendor,
		"location" : "?",
		"item" : req.body.item,
		"amount_spent" : req.body.amount,
		"account_id" : 1
	})
	.then((apiData) => {
		if (!apiData.data.succeeded) {
			res.render('pages/pay', {message: `Couldn't log the transaction.`, error: null});
		}
		else {
			res.render('pages/pay', {message: `The transaction has been logged successfully.`, error: null});
		}
	})
	.catch((error) => {
		res.render("pages/pay", {message: "Something went wrong!", error: error});
	})
});


// Log out (needs work)
app.get('/logout', (req, res) => {
	refreshTokens = refreshTokens.filter(token => token !== req.body.token);
	console.log(refreshTokens);
	return res.redirect(301, "./auth");
});

// View system logs
app.get("/logs", (req, res) => {
	axios.get("http://localhost/api/v1/system/viewlogs")
	.then((apiData) => {
		let fullDataset = "";
		for (let l = 0; l < apiData.data.dataset.length; l++) {
			fullDataset += `Event Key: ${apiData.data.dataset[l]["event-key"]}<br>`;
			fullDataset += `Event Type: ${apiData.data.dataset[l]["event-type"]}<br>`;
			fullDataset += `Event Text: ${apiData.data.dataset[l]["event-text"]}<br>`;
			fullDataset += `Event DateTime: ${apiData.data.dataset[l]["event-dttm"]}<br>`;
			fullDataset += `Event IP Address: ${apiData.data.dataset[l]["event-ipaddr"]}<br><br>`;
		}
		res.render('pages/logs', {message: fullDataset, error: null});
	}).catch((error) => {
		res.render('pages/logs', {message: "Couldn't get system logs.", error: error});
	})
});

function verifyToken(req, res, next) {
	const authHeader = req.headers['authorization'];
	const token = authHeader && authHeader.split(' ')[1];
	if (token == null) { return res.redirect(301, "./auth"); }

	jwt.verify(token, process.env.ACCESS_TOKEN_SECRET, (err, user) => {
		if (err) { return res.sendStatus(403); }
		req.user = user;
		next();
	});
}

function generateAccessToken(user) {
	return jwt.sign(user, process.env.ACCESS_TOKEN_SECRET, {expiresIn: '24h'});
}

// Let server listen on a port.
app.listen(port, () => {
	console.log(`BetterBudget front-end server now running on port ${port}!`);
});
