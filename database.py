import os
from constants import constants
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


# # Load environment variables
# load_dotenv()

# # Get the database URL
# DATABASE_URL = os.getenv("DATABASE_URL")


DATABASE_URL = constants.EXTERNAL_DB_URL
# "postgresql://user:password@localhost:5432/mydatabase"

# Create SQLAlchemy engine and session
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()