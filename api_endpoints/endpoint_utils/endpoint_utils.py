from sqlalchemy.orm import Session
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from models.models import StockModel


# # main functions
def upsert_favourite_stock_in_db(stock_id: str, db: Session):
    try:        
        sql_query = """
            INSERT INTO favourite_stocks (stock_id) 
            VALUES (:stock_id)
            ON CONFLICT (stock_id) 
            DO NOTHING;
        """
        # Upsert into favourite_stocks
        db.execute(text(sql_query), {"stock_id": stock_id})
        db.commit()
        print(">>> Data inserted successfully - (upsert_favourite_stocks_in_db).")
    except Exception as e:
        db.rollback()
        print(f"Unexpected error occurred - (upsert_favourite_stocks_in_db) : {str(e)}")
        raise e
    

def remove_favourite_stock_from_db(stock_id: str, db: Session):
    try:
        sql_query = """
            DELETE FROM favourite_stocks 
            WHERE stock_id = :stock_id
        """
        # Remove stock from favourite_stocks
        db.execute(text(sql_query), {"stock_id": stock_id})
        db.commit()
        print(">>> Data removed successfully - (remove_favourite_stock_from_db).")
    except Exception as e:
        db.rollback()
        print(f"Unexpected error occurred - (remove_favourite_stock_from_db) : {str(e)}")
        raise e


def retrieve_favourite_stocks_from_db(db: Session):
    try:        
        sql_query = """
            SELECT id, stock_id
            FROM favourite_stocks
            ORDER BY id ; 
        """
        result = db.execute(text(sql_query))
        # Fetch all rows as dictionaries by extracting the data with column names as keys.
        data = [dict(row._mapping) for row in result.fetchall()]
        print(">>> Data retrieved successfully - (retrieve_favourite_stocks_from_db).")
        return data
    except Exception as e:
        db.rollback()
        print(f"Unexpected error occurred - (retrieve_favourite_stocks_from_db) : {str(e)}")
        raise e
    

def check_is_stock_favourite_from_db(stock_id: str, db: Session):
    try:        
        sql_query = """ SELECT 1 FROM favourite_stocks WHERE stock_id = :stock_id """
        result = db.execute(text(sql_query), {"stock_id": stock_id})
        exists = result.fetchone() is not None
        print(">>> Data Checked successfully - (check_is_stock_favourite_from_db).")
        return exists
    except Exception as e:
        db.rollback()
        print(f"Unexpected error occurred - (check_is_stock_favourite_from_db) : {str(e)}")
        raise e

