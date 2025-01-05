import os
from dotenv import load_dotenv
from constants import constants
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker



# Load environment variables from .env file
load_dotenv()

ENV = os.getenv("ENV", "development")  # Defaults to 'development'
if ENV == "production":  DATABASE_URL = os.getenv("INTERNAL_DB_URL")  # Internal URL from Render's environment variables
else: DATABASE_URL = os.getenv("EXTERNAL_DB_URL")  # External URL from local .env

print(">>> ENV :", ENV)
print(">>> DATABASE_URL :", DATABASE_URL)

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
