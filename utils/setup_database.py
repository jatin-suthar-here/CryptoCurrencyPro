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

stocks_table = Table(
    "stocks",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),  # Primary key
    Column("stocks_id", String(100), nullable=False, unique=True),  # Unique stock ID
    Column("symbol", String(20), nullable=False),  # Stock symbol (e.g., BTC)
    Column("name", String(100), nullable=False),  # Stock name (e.g., Bitcoin)
    Column("image", String, nullable=False),  # URL for the image
    Column("current_price", BigInteger, nullable=True),  # Current price of the stock
    Column("market_cap", BigInteger, nullable=True),  # Market capitalization
    Column("market_cap_rank", Integer, nullable=True),  # Market cap rank
    Column("high_24h", BigInteger, nullable=True),  # Highest price in the last 24h
    Column("low_24h", BigInteger, nullable=True),  # Lowest price in the last 24h
    Column("price_change_24h", BigInteger, nullable=True),  # Absolute price change in the last 24h
    Column("price_change_percentage_24h", Float, nullable=True),  # Percentage price change in the last 24h
)

# Function to create the table
def create_tables():
    try:
        metadata.create_all(engine)  # Create the table(s)
        print("Table 'stocks' created successfully.")
    except Exception as e:
        print(f"An error occurred while creating the table: {e}")


def reset_database():
    print("resetting the database")




# if __name__ == "__main__":
#     # create_tables()
#     reset_database()
