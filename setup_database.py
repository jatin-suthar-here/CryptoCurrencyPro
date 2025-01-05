from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Numeric, Text
from constants import constants


DATABASE_URL = constants.EXTERNAL_DB_URL
# "postgresql://user:password@localhost:5432/mydatabase"

# Create the database engine
engine = create_engine(DATABASE_URL)

# Define metadata object for holding the schema
metadata = MetaData()

# Define the "items" table
items_table = Table(
    "items",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("name", String(100), nullable=False),
    Column("description", Text, nullable=False),
    Column("price", Numeric(10, 2), nullable=False),
)

# Function to create the table
def create_tables():
    try:
        metadata.create_all(engine)  # Create the table(s)
        print("Table 'items' created successfully.")
    except Exception as e:
        print(f"An error occurred while creating the table: {e}")

# Entry point
if __name__ == "__main__":
    create_tables()