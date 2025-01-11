# CryptoCurrencyPro
This is an iOS App.


DB Structure

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

# Relationships
# Define relationships explicitly in your ORM :
•	stocks → favorite_stocks (1-to-Many)
•	stocks → transactions (1-to-Many)
•	users → transactions and favorite_stocks (1-to-Many)
