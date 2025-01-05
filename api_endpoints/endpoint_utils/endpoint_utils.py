from sqlalchemy.orm import Session
from sqlalchemy import text


def test(db: Session):
    sql_query = text("""SELECT * FROM stocks WHERE stocks_id = 'bitcoin';""")
    result = db.execute(sql_query)
    db.commit()
    
    # Fetch and print the inserted rows
    created_items = result.fetchall()
    return created_items






def insert_api_source_data_in_db(source_data: list, db: Session):
    print("Reached here ...")
    
    # Prepare the SQL query template
    sql_query = """
        INSERT INTO stocks (
            stocks_id, symbol, name, image, current_price, market_cap, market_cap_rank,
            high_24h, low_24h, price_change_24h, price_change_percentage_24h
        )
        VALUES
        {}
        RETURNING id, stocks_id, symbol, name, image, current_price, market_cap, market_cap_rank,
            high_24h, low_24h, price_change_24h, price_change_percentage_24h;
    """
    
    # Prepare the values list for all rows
    for row in source_data:
        values = []
        # for row in source_data:
        values.append(
            "(:stocks_id, :symbol, :name, :image, :current_price, :market_cap, :market_cap_rank, :high_24h, :low_24h, :price_change_24h, :price_change_percentage_24h)"
        )
        
        # Join all value placeholders into a single string
        values_str = ", ".join(values)
        
        # Format the query with the values placeholders
        final_query = sql_query.format(values_str)
        
        # Flatten all source data into a single list of dictionaries for execution
        params = [
            {
                "stocks_id": row["id"],
                "symbol": row["symbol"],
                "name": row["name"],
                "image": row["image"],
                "current_price": row["current_price"],
                "market_cap": row["market_cap"],
                "market_cap_rank": row["market_cap_rank"],
                "high_24h": row["high_24h"],
                "low_24h": row["low_24h"],
                "price_change_24h": row["price_change_24h"],
                "price_change_percentage_24h": row["price_change_percentage_24h"],
            }
            # for row in source_data
        ]
        
        # Execute the final query with parameters for all rows
        result = db.execute(text(final_query), params)
        db.commit()
        
        # Fetch and print the inserted rows
        created_items = result.fetchall()
        print("Inserted rows:", created_items)
        
    # # If no item was created, raise an exception
    # if not created_item: raise HTTPException(status_code=400, detail="Item creation failed")
    
 

    # # Convert the result (tuple) to a dictionary for response validation
    # return {
    #     "id": created_item[0],
    #     "name": created_item[1],
    #     "description": created_item[2],
    #     "price": created_item[3]
    # }