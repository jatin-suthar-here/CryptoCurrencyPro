from sqlalchemy.orm import Session
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from models.models import StockModel


def test(db: Session):
    sql_query = text("""SELECT * FROM stocks;""")
    result = db.execute(sql_query)
    db.commit()
    
    # Fetch and print the inserted rows
    created_items = result.fetchall()
    return created_items


def insert_api_source_data_in_db(source_data: list, db: Session):
    try:        
        # Creating raw SQL query ...
        values = ", ".join(
            [
                f"('{d['id']}', '{d['symbol']}', '{d['name']}', '{d['image']}', '{d['current_price']}', "
                f"'{d['market_cap']}', '{d['market_cap_rank']}', '{d['high_24h']}', '{d['low_24h']}', "
                f"'{d['price_change_24h']}', '{d['price_change_percentage_24h']}')"
                for d in source_data
            ]
        )

        sql_query = f"""
        INSERT INTO stocks (stocks_id, symbol, name, image, current_price, market_cap, market_cap_rank,
            high_24h, low_24h, price_change_24h, price_change_percentage_24h) 
        VALUES {values};
        """
        
        db.execute(text(sql_query))
        db.commit()

        print(">>> Data inserted successfully.")
        return {"status": "success", "message": "Data inserted successfully."}

    except SQLAlchemyError as e:
        db.rollback()  # Rollback the transaction in case of an error
        print(f"Error occurred: {str(e)}")
        return {"status": "failure", "error": str(e)}

    except Exception as e:
        db.rollback()  # Handle any other unforeseen exceptions
        print(f"Unexpected error occurred: {str(e)}")
        return {"status": "failure", "error": str(e)}
    


# # main functions
def upsert_favourite_stock_in_db(stock_data: StockModel, db: Session):
    try:        
        sql_query = """
            INSERT INTO stocks (
                id, symbol, name, image, current_price, market_cap, market_cap_rank, 
                high_24h, low_24h, price_change_24h, price_change_percentage_24h, sparkline
            ) 
            VALUES (
                :id, :symbol, :name, :image, :current_price, :market_cap, :market_cap_rank, 
                :high_24h, :low_24h, :price_change_24h, :price_change_percentage_24h, :sparkline
            )
            ON CONFLICT (id) 
            DO UPDATE SET 
                symbol = EXCLUDED.symbol,
                name = EXCLUDED.name,
                image = EXCLUDED.image,
                current_price = EXCLUDED.current_price,
                market_cap = EXCLUDED.market_cap,
                market_cap_rank = EXCLUDED.market_cap_rank,
                high_24h = EXCLUDED.high_24h,
                low_24h = EXCLUDED.low_24h,
                price_change_24h = EXCLUDED.price_change_24h,
                price_change_percentage_24h = EXCLUDED.price_change_percentage_24h,
                sparkline = EXCLUDED.sparkline;
        """
        # Upsert into stocks
        db.execute(text(sql_query),
            {
                "id": stock_data.id,
                "symbol": stock_data.symbol,
                "name": stock_data.name,
                "image": stock_data.image,
                "current_price": stock_data.current_price,
                "market_cap": stock_data.market_cap,
                "market_cap_rank": stock_data.market_cap_rank,
                "high_24h": stock_data.high_24h,
                "low_24h": stock_data.low_24h,
                "price_change_24h": stock_data.price_change_24h,
                "price_change_percentage_24h": stock_data.price_change_percentage_24h,
                "sparkline": stock_data.sparkline
            })
        
        sql_query = """
            INSERT INTO favourite_stocks (stock_id) 
            VALUES (:stock_id)
            ON CONFLICT (stock_id) 
            DO NOTHING;
        """
        # Upsert into favourite_stocks
        db.execute(text(sql_query), {"stock_id": stock_data.id})
        
        db.commit()
        print(">>> Data inserted successfully - (upsert_favourite_stocks_in_db).")
    except Exception as e:
        db.rollback()
        print(f"Unexpected error occurred - (upsert_favourite_stocks_in_db) : {str(e)}")
        raise e
    

def remove_favourite_stock_from_db(stock_id: str, db: Session):
    try:        
        sql_query = """
            DELETE FROM favourite_stocks WHERE stock_id = :stock_id
        """
        # Remove stock from favourite_stocks
        db.execute(text(sql_query), {"stock_id": stock_id})

        sql_query = """
            DELETE FROM stocks WHERE id = :stock_id
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
            SELECT st.id, st.symbol, st.name, st.image, st.current_price, st.market_cap, st.market_cap_rank, 
                st.high_24h, st.low_24h, st.price_change_24h, st.price_change_percentage_24h, st.sparkline,
                fs.id AS fav_id
            FROM favourite_stocks fs
            LEFT JOIN stocks st
            ON fs.stock_id = st.id
            ORDER BY fs.id ; 
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

