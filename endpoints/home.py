import schemas
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from database import get_db
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


@router.get("/get-items")
def get_items(db: Session = Depends(get_db)):
    sql_query = text("""
        SELECT * FROM items;
    """)
    result = db.execute(sql_query)
    db.commit() 
    result_dict = {}
    count = 1
    for i in result.fetchall():
        print(i)
        result_dict[count] = str(i)
        count += 1

    print(result_dict)
    return result_dict 

