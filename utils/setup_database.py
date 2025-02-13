from datetime import datetime, timezone
from sqlalchemy import (create_engine, MetaData, Table, Column, ForeignKey, Integer, String,
    DateTime, ARRAY, Enum, Numeric, Text, BigInteger, Float, text)
from enum import Enum as PyEnum
from constants import constants

"""
TO RUN THIS SCRIP INDIVIDUALLY : (cd root_dir) --> python3 -m utils.setup_database
"""


# Create the database engine
engine = create_engine(constants.EXTERNAL_DB_URL)

# Define metadata object for holding the schema
metadata = MetaData()


# Define Enums
class TransactionType(PyEnum):
    BUY = "buy"
    SELL = "sell"

class TransactionStatus(PyEnum):
    PROFIT = "profit"
    LOSS = "loss"
    NEUTRAL = "neutral"


# TODO: Will Create Later
# # TABLE 1
# users_table = Table(
#     "users",
#     metadata,
#     # Unique user ID
#     # ALTERNATE OPTION : # Column("user_id", String(36), primary_key=True, default=lambda: str(uuid.uuid4()), nullable=False),
#     Column("id", String(100), primary_key=True, nullable=False, unique=True),  
#     Column("username", String(50), nullable=False, unique=True),  # Username
#     Column("email", String(100), nullable=False, unique=True),  # Email
#     Column("password", String(100), nullable=False),  # Hashed password
# )

# TABLE 2
stocks_table = Table(
    "stocks",
    metadata,
    Column("id", String(100), primary_key=True, nullable=False, unique=True),  # Unique ID
    Column("symbol", String(20), nullable=False),  # Stock symbol (e.g., BTC)
    Column("name", String(100), nullable=False),  # Stock name (e.g., Bitcoin)
    Column("image", String, nullable=False),  # URL for the image
    Column("current_price", String(100), nullable=True),  # Current price of the stock
    Column("market_cap", String(100), nullable=True),  # Market capitalization
    Column("market_cap_rank", String(100), nullable=True),  # Market cap rank
    Column("high_24h", String(100), nullable=True),  # Highest price in the last 24h
    Column("low_24h", String(100), nullable=True),  # Lowest price in the last 24h
    Column("price_change_24h", String(100), nullable=True),  # Absolute price change in the last 24h
    Column("price_change_percentage_24h", String(100), nullable=True),  # Percentage price change in the last 24h
    Column("sparkline", ARRAY(Float), nullable=True),  # Percentage price change in the last 24h
)

# TABLE 3
favourite_stocks_table = Table(
    "favourite_stocks",
    metadata,
    # Unique ID for the favorite entry
    Column("id", Integer, primary_key=True, autoincrement=True, nullable=False), 
    # Foreign key to stocks
    Column("stock_id", String(100), ForeignKey("stocks.id"), nullable=False, unique=True)

    # TODO: # Foreign key to users
    # Column("user_id", String(100), ForeignKey("users.id"), nullable=False),  
)

# TABLE 4
transaction_table = Table(
    "transactions",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True, nullable=False), 
    Column("stock_id", String(100), ForeignKey("stocks.id"), nullable=False), 
        # Removed unique=True - This means each stock can only have one transaction, which is incorrect 
        # because A single stock can have multiple transactions (buying, selling at different times).
    Column("quantity", Integer, nullable=True),
    Column("price_at_transaction", String(100), nullable=True),
    Column("timestamp", DateTime, nullable=False, default=lambda: datetime.now(timezone.utc)),  # Use DateTime
    Column("type", Enum(TransactionType), nullable=False),  # Using Enum for buy/sell
    Column("status", Enum(TransactionStatus), nullable=False)  # Using Enum for profit/loss/neutral
)



# Function to create the table
def create_tables():
    try:
        metadata.create_all(engine)  # Create the table(s)
        print("Tables created successfully.")
    except Exception as e:
        print(f"An error occurred while creating the table: {e}")


# Function to reset the database (drop and recreate tables)
def reset_database():
    try:
        metadata.drop_all(engine)  # Drop all tables
        print("All tables dropped successfully.")
        metadata.create_all(engine)  # Recreate tables
        print("All tables recreated successfully.")
    except Exception as e:
        print(f"An error occurred while resetting the database: {e}")


# Function to drop all tables without recreating them
def drop_database():
    try:
        metadata.drop_all(engine)  # Drop all tables defined in metadata
        print("All tables dropped successfully. Database is now empty.")
    except Exception as e:
        print(f"An error occurred while dropping the database: {e}")


