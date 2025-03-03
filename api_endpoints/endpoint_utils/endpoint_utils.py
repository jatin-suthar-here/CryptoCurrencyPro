from sqlalchemy.orm import Session
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from models.models import StockModel



# --------------------------------------------------------------------------
def upsert_favourite_stock_in_db(stock_id: str, user_id: str, db: Session):
    try:        
        sql_query = """
            INSERT INTO favourite_stocks (stock_id, user_id) 
            VALUES (:stock_id, :user_id)
            ON CONFLICT (stock_id, user_id) 
            DO NOTHING;
        """
        # Prevents duplicates (user cannot favorite the same stock multiple times).
        # Does nothing if the user has already added this stock.

        # Upsert into favourite_stocks
        db.execute(text(sql_query), {"stock_id": stock_id, "user_id": user_id})
        db.commit()
        print(">>> upsert_favourite_stocks_in_db : success")
    except Exception as e:
        db.rollback()
        print(f"Unexpected error occurred - (upsert_favourite_stocks_in_db) : {str(e)}")
        raise e
    

def remove_favourite_stock_from_db(stock_id: str, user_id: str, db: Session):
    try:
        sql_query = """
            DELETE FROM favourite_stocks 
            WHERE stock_id = :stock_id AND user_id = :user_id
        """
        # Remove stock from favourite_stocks
        db.execute(text(sql_query), {"stock_id": stock_id, "user_id": user_id})
        db.commit()
        print(">>> remove_favourite_stock_from_db : success")
    except Exception as e:
        db.rollback()
        print(f"Unexpected error occurred - (remove_favourite_stock_from_db) : {str(e)}")
        raise e


def retrieve_favourite_stocks_from_db(user_id: str, db: Session):
    try:        
        sql_query = """
            SELECT id, stock_id
            FROM favourite_stocks
            WHERE user_id = :user_id
            ORDER BY id ; 
        """
        result = db.execute(text(sql_query), {"user_id": user_id})
        # Fetch all rows as dictionaries by extracting the data with column names as keys.
        data = [dict(row._mapping) for row in result.fetchall()]
        print(">>> retrieve_favourite_stocks_from_db : success")
        return data
    except Exception as e:
        db.rollback()
        print(f"Unexpected error occurred - (retrieve_favourite_stocks_from_db) : {str(e)}")
        raise e
    

def check_is_stock_favourite_from_db(stock_id: str, user_id: str, db: Session):
    try:        
        sql_query = """ 
            SELECT 1 FROM favourite_stocks WHERE stock_id = :stock_id AND user_id = :user_id
        """
        result = db.execute(text(sql_query), {"stock_id": stock_id, "user_id": user_id})
        exists = result.fetchone() is not None
        print(">>> check_is_stock_favourite_from_db : success")
        return exists
    except Exception as e:
        db.rollback()
        print(f"Unexpected error occurred - (check_is_stock_favourite_from_db) : {str(e)}")
        raise e
# --------------------------------------------------------------------------




# --------------------------------------------------------------------------
def upsert_buy_transaction_in_db(stock_data: dict, user_id: str, db: Session):
    try: 
        ## insert the BUY entry into transaction table       
        sql_query = """
            INSERT INTO transactions (user_id, stock_id, quantity, type, price_at_transaction, timestamp) 
            VALUES (:user_id, :stock_id, :quantity, :type, :price_at_transaction, :timestamp)
        """
        stock_data["user_id"] = user_id
        db.execute(text(sql_query), stock_data)

        stock_data.pop("type")

        ## insert the entry into portfolio table, 
        ## if already present then it updates the quantity with sum of current + previous, and also updates the timestamp.
        sql_query = """
            INSERT INTO portfolio (user_id, stock_id, quantity, price_at_transaction, timestamp)
            VALUES (:user_id, :stock_id, :quantity, :price_at_transaction, :timestamp)
            ON CONFLICT(stock_id, user_id)
            DO UPDATE SET 
                quantity = portfolio.quantity + EXCLUDED.quantity,
                timestamp = EXCLUDED.timestamp ;
        """
        db.execute(text(sql_query), stock_data)
        db.commit()
        print(">>> upsert_buy_transaction_in_db : success")
    except Exception as e:
        db.rollback()
        print(f"Unexpected error occurred - (upsert_buy_transaction_in_db) : {str(e)}")
        raise e


def upsert_sell_transaction_in_db(stock_data: dict, user_id: str, db: Session):
    try: 
        ## insert the SELL entry into transaction table       
        sql_query = """
            INSERT INTO transactions (user_id, stock_id, quantity, type, price_at_transaction, timestamp) 
            VALUES (:user_id, :stock_id, :quantity, :type, :price_at_transaction, :timestamp)
        """
        stock_data["user_id"] = user_id
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
            WHERE stock_id = :stock_id AND user_id = :user_id;

            DELETE FROM portfolio 
            WHERE quantity <= 0 AND stock_id = :stock_id AND user_id = :user_id;
        """
        db.execute(text(sql_query), stock_data)
        db.commit()
        print(">>> upsert_sell_transaction_in_db : success")
    except Exception as e:
        db.rollback()
        print(f"Unexpected error occurred - (upsert_sell_transaction_in_db) : {str(e)}")
        raise e


def get_stock_quantity_available_for_sell_in_db(stock_id: str, user_id: str, db: Session):
    try: 
        sql_query = """
            SELECT quantity 
            FROM portfolio 
            WHERE stock_id = :stock_id AND user_id = :user_id;
        """
        result = db.execute(text(sql_query), {"stock_id": stock_id, "user_id": user_id})
        data = result.fetchone()
        print(">>> get_stock_quantity_available_for_sell_in_db : success")
        if data: return data[0]
        else: return 0
    except Exception as e:
        db.rollback()
        print(f"Unexpected error occurred - (get_stock_quantity_available_for_sell_in_db) : {str(e)}")
        raise e

# --------------------------------------------------------------------------




# AUTHENTICATION FUNCTIONS
# --------------------------------------------------------------------------
def verify_user_exists_in_db(email: str, password: str, db: Session):
    try:        
        sql_query = """
            SELECT * FROM users
            WHERE email = :email AND password = :password ;
        """
        result = db.execute(text(sql_query), {"email": email, "password": password})
        data = result.fetchone()
        if data: 
            return {
                "user_id": data[0], 
                "fullname": data[1],
                "email": data[2],
                "password": data[3],
            }
        else: return False
    except Exception as e:
        print(f"Unexpected error occurred - (verify_user_exists_in_db) : {str(e)}")
        raise e


def upsert_refresh_token_in_db(data_dict: dict, db: Session):
    try:        
        sql_query = """
            INSERT INTO auth_tokens (user_id, refresh_token, created_at, expires_at) 
            VALUES (:user_id, :refresh_token, :created_at, :expires_at)
            ON CONFLICT (user_id) 
            DO UPDATE SET 
                refresh_token = EXCLUDED.refresh_token,
                created_at = EXCLUDED.created_at,
                expires_at = EXCLUDED.expires_at ;
        """
        db.execute(text(sql_query), data_dict)
        db.commit()
        print(">>> upsert_refresh_token_in_db : success")
    except Exception as e:
        db.rollback()
        print(f"Unexpected error occurred - (upsert_refresh_token_in_db) : {str(e)}")
        raise e


def get_refresh_token_from_the_db(user_id: str, db: Session):
    try:        
        sql_query = """
            SELECT refresh_token
            FROM auth_tokens
            WHERE user_id = :user_id ;
        """
        result = db.execute(text(sql_query), {"user_id": user_id})
        data = result.fetchone()
        if data: 
            return {
                "refresh_token": data[0]
            }
        else: return False
    except Exception as e:
        print(f"Unexpected error occurred - (verify_user_exists_in_db) : {str(e)}")
        raise e


def insert_user_in_the_db(user_data: dict, db: Session) -> str:
    try:        
        sql_query = """
            INSERT INTO users (fullname, email, password) 
            VALUES (:fullname, :email, :password) 
            RETURNING user_id ;
        """
        result = db.execute(text(sql_query), user_data)
        user_id = result.fetchone()[0]  # Fetch the first row and get the first column
        db.commit()
        print(">>> insert_user_in_the_db : success")
        return user_id
    except Exception as e:
        db.rollback()
        print(f"Unexpected error occurred - (insert_user_in_the_db) : {str(e)}")
        raise e


def delete_user_from_the_db(user_id: str, db: Session):
    try:        
        sql_query = """
            DELETE FROM users 
            WHERE user_id = :user_id ;
        """
        db.execute(text(sql_query), {"user_id": user_id})
        db.commit()
        print(">>> delete_user_from_the_db : success")
        return user_id
    except Exception as e:
        db.rollback()
        print(f"Unexpected error occurred - (delete_user_from_the_db) : {str(e)}")
        raise e
# --------------------------------------------------------------------------




