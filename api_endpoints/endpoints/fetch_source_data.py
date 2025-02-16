import requests, json
import aiofiles
import asyncio  # For periodic tasks
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, Depends, WebSocket
from sqlalchemy.orm import Session
from constants import constants
from utils.database import get_db
from utils.utils import get_current_time
from ..endpoint_utils.endpoint_utils import (upsert_favourite_stock_in_db, remove_favourite_stock_from_db,
    retrieve_favourite_stocks_from_db, check_is_stock_favourite_from_db, upsert_buy_transaction_in_db, 
    upsert_sell_transaction_in_db, get_stock_quantity_available_for_sell_in_db)
from models.models import StockModel, FavStockModel, TransactionType
from typing import Dict, List

router = APIRouter()


# Global variables
API_SOURCE_DATA: Dict[str, StockModel] = {} # Dictionary to store stock data with stock_id as key
USER_BALANCE = 7_50_750.45



# --------------------------------------------------------------------------
# Periodically fetch source data
async def periodic_fetch_data():
    """
    Periodically call `fetch_source_data_from_api` to update API_SOURCE_DATA.
    """
    while True:
        try:
            await fetch_source_data_from_api()  # Reuse the populate function
        except Exception as e:
            print(f"Error during periodic fetch: {str(e)}")

        # Wait for 15 minutes before the next fetch
        await asyncio.sleep(15 * 60)

# Function to fetch data during startup
async def fetch_source_data_from_api():
    """
    Fetch source data from the API and populate the global variable.
    This function is called once during application startup.
    """
    try:
        """ Fetching data from API """
        # response = requests.get(constants.COINGECKO_API_URL, params=constants.URL_PARAMS)
        # response.raise_for_status()  # Raise an HTTPError if the response status is 4xx/5xx
        # response_data = response.json()

        """ Fetching data from static json file present on local """
        # NOTE:  since this function is 'async' it will run in backgoround, but using normal open() method to read data from file will make this function work as 'sync' function (normal func) because file I/O is a blocking operation in Python.
        # So using 'aiofiles.open' will make file I/O a non-blocking operaion.
        async with aiofiles.open("api_data.json", "r") as file:
            content = await file.read()  # Read file asynchronously
            response_data = json.loads(content)  # Parse JSON
        
        for item in response_data:
            stock = StockModel(
                id=item["id"],
                symbol=item["symbol"],
                name=item["name"],
                image=item.get("image"),
                current_price=item.get("current_price"),
                market_cap=item.get("market_cap"),
                market_cap_rank=item.get("market_cap_rank"),
                high_24h=item.get("high_24h"),
                low_24h=item.get("low_24h"),
                price_change_24h=item.get("price_change_24h"),
                price_change_percentage_24h=item.get("price_change_percentage_24h"),
                sparkline=item["sparkline_in_7d"]["price"] if "sparkline_in_7d" in item else None
            )
            API_SOURCE_DATA[stock.id] = stock            

        print(">>> API_SOURCE_DATA populated - Length:", len(API_SOURCE_DATA))
    
    except requests.exceptions.RequestException as e:
        print(f"API request failed during startup: {str(e)}")
        raise HTTPException(status_code=502, detail=f"API request failed during startup: {str(e)}")

    except Exception as e:
        print(f"Unexpected error during startup: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Unexpected error during startup: {str(e)}")
# --------------------------------------------------------------------------




# --------------------------------------------------------------------------
@router.get("/fetch-source-data")
def get_source_data():
    """
    Endpoint to return already fetched source data.
    If the data has already been fetched during startup, it will return the cached data.
    """
    try:
        if not API_SOURCE_DATA:
            raise HTTPException(status_code=500, detail="Source data is not available.")

        return {
            "message": f"Successfully extracted data on {get_current_time()}", 
            "data": API_SOURCE_DATA
        }
    
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


@router.get("/trending-stocks")
def get_trending_stocks():
    """
    Endpoint to get the top 10 trending stocks.
    Depends on 'API_SOURCE_DATA' being populated.
    """
    try:
        if not API_SOURCE_DATA:
            raise HTTPException(status_code=500, detail="Source data is not available.")
        
        # Sorting the dictionary based on keys (stock_id)
        trending_data = dict(sorted(API_SOURCE_DATA.items()))

        return [i for i in trending_data.values()][:10]
    
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
# --------------------------------------------------------------------------




# --------------------------------------------------------------------------
@router.get("/get-fav-stock") 
def get_favourite_stocks(db: Session = Depends(get_db)):
    try:
        favourite_stocks = retrieve_favourite_stocks_from_db(db=db)
        favourite_stocks_list = []
        # converting the each dict to StockModel format...
        if not API_SOURCE_DATA:
            raise HTTPException(status_code=500, detail="Source data is not available.")

        favourite_stocks_list.extend(
            FavStockModel(**API_SOURCE_DATA[item["stock_id"]].dict(), fav_id=int(item["id"])) for item in favourite_stocks
            # Converts all the API_SOURCE_DATA elements to dict + Add fav_id, and map all to FavStockModel.
        )
        return {
            "message": "Data fetched successfully.", 
            "data": favourite_stocks_list
        }
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


@router.post("/add-fav-stock")
def add_favourite_stocks(stock_id: str, db: Session = Depends(get_db)):
    """
    Ex:  curl -X POST "http://0.0.0.0:8500/api/add-fav-stock?stock_id=bitcoin"
    """
    try:
        upsert_favourite_stock_in_db(stock_id=stock_id, db=db)
        return {
            "message": "Data inserted successfully", 
            "data": stock_id
        }
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


@router.delete("/remove-fav-stock") 
def remove_favourite_stocks(stock_id: str, db: Session = Depends(get_db)):
    """
    Ex:  curl -X DELETE "http://0.0.0.0:8500/api/remove-fav-stock?stock_id=bitcoin"
    """
    try:
        remove_favourite_stock_from_db(stock_id=stock_id, db=db)
        return {
            "message": "Data removed successfully", 
            "data": stock_id
        }
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


@router.get("/check-fav-stock")
def check_is_stock_favourite(stock_id: str, db: Session = Depends(get_db)):
    data = check_is_stock_favourite_from_db(stock_id=stock_id, db=db)
    return {
        "message": "Data checked successfully", 
        "data": data
    }
# --------------------------------------------------------------------------




# --------------------------------------------------------------------------
@router.post("/buy-stock")
def buy_stocks(stock_id: str, quantity: int, current_price: str, db: Session = Depends(get_db)):
    """
    Ex:  curl -X POST "http://0.0.0.0:8500/api/buy-stock?stock_id=bitcoin&quantity=2&current_price=45000"
    """
    try:
        stock_data = {
            "stock_id": stock_id,
            "quantity": quantity,
            "type": TransactionType.BUY.value,
            "price_at_transaction": current_price,
            "timestamp": datetime.now(timezone.utc)
        }
        upsert_buy_transaction_in_db(stock_data=stock_data, db=db)
        return {
            "message": "Buy Transaction successfull", 
            "data": stock_data
        }
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


@router.post("/sell-stock")
def sell_stocks(stock_id: str, quantity: int, current_price: str, db: Session = Depends(get_db)):
    """
    Ex:  curl -X POST "http://0.0.0.0:8500/api/sell-stock?stock_id=bitcoin&quantity=2&current_price=45000"
    """
    try:
        stock_data = {
            "stock_id": stock_id,
            "quantity": quantity,
            "type": TransactionType.SELL.value,
            "price_at_transaction": current_price,
            "timestamp": datetime.now(timezone.utc)
        }
        upsert_sell_transaction_in_db(stock_data=stock_data, db=db)
        return {
            "message": "Sell Transaction successfull", 
            "data": stock_data
        }
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


@router.get("/get-stock-sell-qty")
def get_stock_quantity_available_for_sell(stock_id: str, db: Session = Depends(get_db)):
    """
    Ex:  curl -X GET "http://0.0.0.0:8500/api/get-stock-sell-qty?stock_id=bitcoin"
    """
    try:
        data = get_stock_quantity_available_for_sell_in_db(stock_id=stock_id, db=db)
        return {
            "message": "Sell Transaction successfull", 
            "data": data
        }
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
# --------------------------------------------------------------------------


@router.get("/get-balance")
def get_user_balance(): # db: Session = Depends(get_db)):
    """
    Ex:  curl -X GET "http://0.0.0.0:8500/api/get-balance"
    """
    try:
        data = USER_BALANCE
        return {
            "message": "Sell Transaction successfull", 
            "data": data
        }
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

