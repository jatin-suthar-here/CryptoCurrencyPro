from sqlalchemy.orm import Session
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from models.models import StockModel


# # main functions
# --------------------------------------------------------------------------
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
        sql_query = """ 
            SELECT 1 FROM favourite_stocks WHERE stock_id = :stock_id 
        """
        result = db.execute(text(sql_query), {"stock_id": stock_id})
        exists = result.fetchone() is not None
        print(">>> Data Checked successfully - (check_is_stock_favourite_from_db).")
        return exists
    except Exception as e:
        db.rollback()
        print(f"Unexpected error occurred - (check_is_stock_favourite_from_db) : {str(e)}")
        raise e
# --------------------------------------------------------------------------




# --------------------------------------------------------------------------
def upsert_buy_transaction_in_db(stock_data: dict, db: Session):
    try: 
        ## insert the BUY entry into transaction table       
        sql_query = """
            INSERT INTO transactions (stock_id, quantity, type, price_at_transaction, timestamp) 
            VALUES (:stock_id, :quantity, :type, :price_at_transaction, :timestamp)
        """
        db.execute(text(sql_query), stock_data)

        stock_data.pop("type")

        ## insert the entry into portfolio table, 
        ## if already present then it updates the quantity with sum of current + previous, and also updates the timestamp.
        sql_query = """
            INSERT INTO portfolio (stock_id, quantity, price_at_transaction, timestamp)
            VALUES (:stock_id, :quantity, :price_at_transaction, :timestamp)
            ON CONFLICT(stock_id)
            DO UPDATE SET 
                quantity = portfolio.quantity + EXCLUDED.quantity,
                timestamp = EXCLUDED.timestamp ;
        """
        db.execute(text(sql_query), stock_data)
        db.commit()
        print(">>> Data inserted successfully - (upsert_buy_transaction_in_db).")
    except Exception as e:
        db.rollback()
        print(f"Unexpected error occurred - (upsert_buy_transaction_in_db) : {str(e)}")
        raise e


def upsert_sell_transaction_in_db(stock_data: dict, db: Session):
    try: 
        ## insert the SELL entry into transaction table       
        sql_query = """
            INSERT INTO transactions (stock_id, quantity, type, price_at_transaction, timestamp) 
            VALUES (:stock_id, :quantity, :type, :price_at_transaction, :timestamp)
        """
        db.execute(text(sql_query), stock_data)

        stock_data.pop("type")
        stock_data.pop("price_at_transaction")

        ## Using TRANSACTION SQL query because
        ## in PostgreSQL, the UPDATE inside a CTE does not immediately make changes visible to the subsequent query in the same statement.
        ## NOTE: CTE (Common Table Expression) queries are slower than Transaction queries (in postgresql, etc)
        sql_query = """
            BEGIN;

            UPDATE portfolio 
            SET quantity = quantity - :quantity,
                timestamp = :timestamp
            WHERE stock_id = :stock_id;

            DELETE FROM portfolio 
            WHERE quantity <= 0;
        """
        db.execute(text(sql_query), stock_data)
        db.commit()
        print(">>> Data inserted successfully - (upsert_sell_transaction_in_db).")
    except Exception as e:
        db.rollback()
        print(f"Unexpected error occurred - (upsert_sell_transaction_in_db) : {str(e)}")
        raise e


def get_stock_quantity_available_for_sell_in_db(stock_id: str, db: Session):
    try: 
        sql_query = """
            SELECT quantity FROM portfolio WHERE stock_id = :stock_id ;
        """
        result = db.execute(text(sql_query), {"stock_id": stock_id})
        data = result.fetchone()
        print(">>> Data fetched successfully - (get_stock_quantity_available_for_sell_in_db).")
        return data[0]
    except Exception as e:
        db.rollback()
        print(f"Unexpected error occurred - (get_stock_quantity_available_for_sell_in_db) : {str(e)}")
        raise e

# --------------------------------------------------------------------------


