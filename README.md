# CryptoCurrencyPro
This is an iOS App.


# GET vs POST
Key Differences Between GET and POST:
	1.	GET:
		•	Sends parameters in the query string of the URL (e.g., /add-fav-stock?stock=...).
		•	Primarily used to retrieve data.
		•	Data is visible in the URL and limited in size.
		•	In your code, the stock parameter is being passed as a query parameter, which aligns with the GET method.
	2.	POST:
		•	Sends data in the body of the request.
		•	Primarily used to send or create data on the server.
		•	Does not pass data in the query string, but in the request body.




# APIS
1. User Management APIs
	•	User Registration - POST /api/v1/users/register
		Handles user sign-up with fields like email, password, and optional profile details.
	•	User Login - POST /api/v1/users/login
		Authenticates users and generates a session token or JWT.
	•	User Logout - POST /api/v1/users/logout
		Ends the user’s session and invalidates the token.
	•	Session Management
		•	GET /api/v1/users/session - Verifies the user’s session/token validity.
		•	POST /api/v1/users/refresh-token - Refreshes an expired or near-expired token.

2. Market Data APIs
	•	Fetch Cryptocurrency Data - GET /api/v1/market/prices
		Fetches real-time prices for all cryptocurrencies.
	•	Get Top Cryptocurrencies - GET /api/v1/market/top
		Returns the top cryptocurrencies by market cap, volume, or other metrics.
	•	Search Cryptocurrency by Symbol or Name - GET /api/v1/market/search
		Returns details of cryptocurrencies matching a query.

3. Portfolio Management APIs
	•	Get User Portfolio - GET /api/v1/portfolio
		Returns the user’s current holdings, total portfolio value, and performance metrics.
	•	Add Cryptocurrency to Portfolio - POST /api/v1/portfolio/add
		Adds a cryptocurrency holding to the user’s portfolio.
	•	Remove Cryptocurrency from Portfolio - POST /api/v1/portfolio/remove
		Removes a specific cryptocurrency from the portfolio.

4. Transaction APIs
	•	Buy Cryptocurrency - POST /api/v1/transactions/buy
		Processes a purchase of cryptocurrency.
	•	Sell Cryptocurrency - POST /api/v1/transactions/sell
		Processes the sale of cryptocurrency.
	•	Get Transaction History - GET /api/v1/transactions/history
		Returns a user’s full transaction history.

5. Watchlist/Favorites APIs
	•	Get Favorite Cryptocurrencies - GET /api/v1/watchlist
		Retrieves the user’s favorite cryptocurrencies.
	•	Add Cryptocurrency to Watchlist - POST /api/v1/watchlist/add
		Adds a cryptocurrency to the user’s watchlist.
	•	Remove Cryptocurrency from Watchlist - POST /api/v1/watchlist/remove
		Removes a cryptocurrency from the watchlist.

6. Credit Card APIs
	•	Link Credit Card - POST /api/v1/credit-cards/link
		Links a credit card to the user’s account.
	•	Get Linked Credit Cards - GET /api/v1/credit-cards
		Lists all linked credit cards.	
	•	Remove Linked Credit Card - POST /api/v1/credit-cards/remove
		Removes a linked credit card.

7. Notifications APIs
	•	Get Notifications - GET /api/v1/notifications
		Retrieves user notifications, such as price alerts or portfolio updates.
	•	Set Price Alert - POST /api/v1/notifications/price-alert
		Sets a price alert for a specific cryptocurrency.






# DB Structure
# Tables
stocks (Master table for stock data)
	•	id (Primary Key)
	•	symbol
	•	name
	•	image
	•	current_price
	•	market_cap
	•	market_cap_rank
	•	high_24h
	•	low_24h
	•	price_change_24h
	•	price_change_percentage_24h

favorite_stocks
	•	id (Primary Key)
	•	user_id (Foreign Key to users table for tracking which user marked the stock as favorite)
	•	stock_id (Foreign Key to stocks.id)

transactions (For both buy and sell operations)
	•	id (Primary Key)
	•	user_id (Foreign Key to users table)
	•	stock_id (Foreign Key to stocks.id)
	•	type (ENUM or VARCHAR for buy or sell)
	•	quantity
	•	price_at_transaction (Store the stock’s price at the time of the transaction)
	•	current_price (Optional: if you want to track the latest stock price for reporting purposes)
	•	status (ENUM for profit, loss, or neutral)
	•	timestamp (Transaction date and time)

users Table
	•	id (Primary Key)
	•	username (Unique username)
	•	email (Unique email)
	•	password_hash (Hashed password (e.g., bcrypt))
	•	is_active (Boolean (default TRUE))
	•	is_admin (Boolean (default FALSE))
	•	created_at (Account creation timestamp)
	•	refresh/access_token (Hashed refresh token)
	•	expires_at (Expiration timestamp)
	•	revoked (Boolean default FALSE)


# Relationships
# Define relationships explicitly in your ORM :
•	stocks → favorite_stocks (1-to-Many)
•	stocks → transactions (1-to-Many)
•	users → transactions and favorite_stocks (1-to-Many)
