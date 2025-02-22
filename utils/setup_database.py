import uuid
from sqlalchemy import (create_engine, MetaData, Table, Column, ForeignKey, Integer, String,
    DateTime, UniqueConstraint, ARRAY, Numeric, Text, BigInteger, Float, text)
from sqlalchemy.dialects.postgresql import ENUM, UUID
from constants import constants

"""
TO RUN THIS SCRIP INDIVIDUALLY : (cd root_dir) --> python3 -m utils.setup_database
"""


## -------------------------------------------------------------
# Create the database engine
engine = create_engine(constants.EXTERNAL_DB_URL)

# Define metadata object for holding the schema
metadata = MetaData()
## -------------------------------------------------------------




## -------------------------------------------------------------
transaction_enum = ENUM("BUY", "SELL", name="transactiontype", create_type=True, metadata=metadata)
transaction_enum.create(engine, checkfirst=True)  # Ensures it's created only if it doesn’t exist
"""
To Remove Enum (SQLAlchemy):
- transaction_enum.drop(engine, checkfirst=True) # to remove enum

To check enum present in the DB:
- SELECT * FROM pg_enum WHERE enumtypid = 'transactiontype'::regtype;

Raw SQL cmd to create enum:
- CREATE TYPE transactiontype AS ENUM ('BUY', 'SELL');
"""
## -------------------------------------------------------------




## -------------------------------------------------------------
# TABLE 1 
# USERS TABLE (Main Table)
users_table = Table(
    "users",
    metadata,
    ## user_id of uuid type will automatically generated on inserting data.
    Column("user_id", UUID(as_uuid=True), primary_key=True, server_default=text("uuid_generate_v4()"), nullable=False, unique=True),
    Column("fullname", String(100), nullable=False),  # Fullname
    Column("email", String(100), nullable=False, unique=True),  # Unique email
    Column("password", String(100), nullable=False),  # Hashed password
)

# TABLE 2
# AUTH TOKEN TABLE 
auth_token_table = Table(
    "auth_tokens",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True, nullable=False),  
    Column("user_id", UUID(as_uuid=True), ForeignKey("users.user_id"), nullable=False, unique=True),  # Ensure one token per user  
    Column("refresh_token", String(900), nullable=False, unique=True),  # Ensure token is unique  
    Column("created_at", DateTime, nullable=False, default=None),  
    Column("expires_at", DateTime, nullable=False, default=None)  
)

# TABLE 3
# USER WALLETS TABLE
user_wallets_table = Table(
    "user_wallets",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True, nullable=False),  
    Column("user_id", UUID(as_uuid=True), ForeignKey("users.user_id"), nullable=False, unique=True),  # One account per user
    Column("bank_name", String(100), nullable=False),  # Bank Name  
    Column("balance", Float, nullable=False, default=0.0),  # User balance  
    Column("credit_card_number", String(20), nullable=False, unique=True),  # Credit Card number  
    Column("expiry_date", String(7), nullable=True),  # Format: MM/YYYY
    Column("cvv", String(4), nullable=True), 
    Column("created_at", DateTime, nullable=False, default=None),
    Column("updated_at", DateTime, nullable=False, default=None)  
)

# TABLE 4
# FAVOURITE STOCKS TABLE (Child Table)
favourite_stocks_table = Table(
    "favourite_stocks",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True, nullable=False),  
    Column("user_id", UUID(as_uuid=True), ForeignKey("users.user_id"), nullable=False),  # Foregin Key to users
    Column("stock_id", String(100), nullable=False),  # Stock identifier

    # Ensure a user cannot favorite the same stock multiple times (user_id + stock_id - should be unique)
    UniqueConstraint("user_id", "stock_id", name="fav_table_uq_user_stock")
)

# TABLE 5
# TRANSACTION STOCKS TABLE (Child Table)
transaction_table = Table(
    "transactions",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True, nullable=False), 
    Column("user_id", UUID(as_uuid=True), ForeignKey("users.user_id"), nullable=False),  # Foregin Key to users
    Column("stock_id", String(100), nullable=False), # Removed unique=True - This means each stock can only have one transaction, which is incorrect because A single stock can have multiple transactions (buying, selling at different times).
    Column("quantity", Integer, nullable=True),
    Column("type", transaction_enum, nullable=False),  # Using Enum for buy/sell
    Column("price_at_transaction", String(100), nullable=True),
    Column("timestamp", DateTime, nullable=False, default=None) 
)

# TABLE 6
# PORTFOLIO STOCKS TABLE (Child Table)
portfolio_table = Table(
    "portfolio",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True, nullable=False), 
    Column("user_id", UUID(as_uuid=True), ForeignKey("users.user_id"), nullable=False),  # Foregin Key to users
    Column("stock_id", String(100), nullable=False, unique=True),
    Column("quantity", Integer, nullable=False),
    Column("price_at_transaction", String(100), nullable=True),
    Column("timestamp", DateTime, nullable=False, default=None),

    # Ensure a user cannot add the same stock multiple times (user_id + stock_id - should be unique)
    UniqueConstraint("user_id", "stock_id", name="portfolio_table_uq_user_stock")
)
## -------------------------------------------------------------




## -------------------------------------------------------------
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
## -------------------------------------------------------------



