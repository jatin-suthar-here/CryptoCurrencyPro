from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from utils.database import get_db, ENV
from typing import List, Annotated


router = APIRouter()

@router.get("/")
def home():
    return {"message": "This is the Home Page"}


@router.get("/items/") #, response_model=schemas.ItemResponse)
def create_item(name: str,
    description: str,
    price: float,
    db: Session = Depends(get_db)):
    sql_query = text("""
        INSERT INTO items (name, description, price)
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

    # Convert the result (tuple) to a dictionary for response validation
    return {
        "id": created_item[0],
        "name": created_item[1],
        "description": created_item[2],
        "price": created_item[3],
        "ENV": ENV
    }


@router.get("/get-items")
def get_items(db: Session = Depends(get_db)):
    sql_query = text(""" SELECT * FROM stocks; """)
    result = db.execute(sql_query)

    # # Fetch column names from the result
    column_names = result.keys()
    print(column_names)

    # Convert result rows into a list of dictionaries
    result_list = [
        {column: value for column, value in zip(column_names, row)} 
        for row in result.fetchall()
    ]
    return result_list
