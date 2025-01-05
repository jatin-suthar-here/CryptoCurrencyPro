from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from utils.database import get_db
from typing import List, Annotated


def insert_api_source_data_in_db(name: str, db: Session = Depends(get_db)):
    sql_query = text("""
        INSERT INTO stocks (id, symbol, name, image, current_price, market_cap, market_cap_rank, high_24h, low_24h, price_change_24h, price_change_percentage_24h)
        VALUES (:name, :description, :price)
        RETURNING id, name, description, price
    """)
    result = db.execute(sql_query, {"name": name, "description": description, "price": price})
    db.commit() 
    created_item = result.fetchone() 
    
    # If no item was created, raise an exception
    if not created_item: raise HTTPException(status_code=400, detail="Item creation failed")
    
    sql_query = text("""
        SELECT * FROM items;
    """)
    result = db.execute(sql_query)
    db.commit() 
    result_dict = {}
    count = 1
    for i in result.fetchall():
        # print(i)
        result_dict[count] = str(i)
        count += 1

    # print(result_dict) 

    # Convert the result (tuple) to a dictionary for response validation
    return {
        "id": created_item[0],
        "name": created_item[1],
        "description": created_item[2],
        "price": created_item[3]
    }, result_dict