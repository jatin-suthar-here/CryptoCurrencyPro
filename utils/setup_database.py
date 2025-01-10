from sqlalchemy import (create_engine, MetaData, Table, Column, Integer, String, 
    Numeric, Text, BigInteger, Float, text)
from constants import constants

"""
TO RUN THIS SCRIP INDIVIDUALLY : (cd root_dir) --> python3 -m utils.setup_database
"""


# Create the database engine
engine = create_engine(constants.EXTERNAL_DB_URL)

# Define metadata object for holding the schema
metadata = MetaData()


# TABLE 1
# stocks_table = Table(
#     "stocks",
#     metadata,
#     Column("id", Integer, primary_key=True, autoincrement=True),  # Primary key
#     Column("stocks_id", String(100), nullable=False, unique=True),  # Unique stock ID
#     Column("symbol", String(20), nullable=False),  # Stock symbol (e.g., BTC)
#     Column("name", String(100), nullable=False),  # Stock name (e.g., Bitcoin)
#     Column("image", String, nullable=False),  # URL for the image
#     Column("current_price", String(100), nullable=True),  # Current price of the stock
#     Column("market_cap", String(100), nullable=True),  # Market capitalization
#     Column("market_cap_rank", String(100), nullable=True),  # Market cap rank
#     Column("high_24h", String(100), nullable=True),  # Highest price in the last 24h
#     Column("low_24h", String(100), nullable=True),  # Lowest price in the last 24h
#     Column("price_change_24h", String(100), nullable=True),  # Absolute price change in the last 24h
#     Column("price_change_percentage_24h", String(100), nullable=True),  # Percentage price change in the last 24h
# )




# Function to create the table
def create_tables():
    try:
        metadata.create_all(engine)  # Create the table(s)
        print("Table 'stocks' created successfully.")
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










# if __name__ == "__main__":
#     create_tables()
#     reset_database()
