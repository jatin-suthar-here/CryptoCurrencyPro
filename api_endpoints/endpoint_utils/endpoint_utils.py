from sqlalchemy.orm import Session
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError


def test(db: Session):
    sql_query = text("""SELECT * FROM stocks WHERE stocks_id = 'bitcoin';""")
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
    
        