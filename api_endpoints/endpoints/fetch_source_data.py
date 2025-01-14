import requests, json
import asyncio  # For periodic tasks
from fastapi import APIRouter, HTTPException, Depends, WebSocket
from sqlalchemy.orm import Session
from constants import constants
from utils.database import get_db
from utils.utils import get_current_time
from ..endpoint_utils.endpoint_utils import upsert_favourite_stock_in_db, remove_favourite_stock_from_db
from models.models import StockModel

{"id":"bitcoin","symbol":"btc","name":"Bitcoin","image":"https://coin-images.coingecko.com/coins/images/1/large/bitcoin.png?1696501400","current_price":"8371903","market_cap":"165790242423847","market_cap_rank":"1","high_24h":"8457221","low_24h":"7984591","price_change_24h":"328609","price_change_percentage_24h":"4"}
router = APIRouter()


# Global variables
API_SOURCE_DATA = []
FAVOURITE_STOCKS = []


# Function to fetch data during startup
async def fetch_source_data_from_api():
    """
    Fetch source data from the API and populate the global variable.
    This function is called once during application startup.
    """
    try:
        response = requests.get(constants.COINGECKO_API_URL, params=constants.URL_PARAMS)
        response.raise_for_status()  # Raise an HTTPError if the response status is 4xx/5xx
        response_data = response.json()
        
        # Populate the global variable
        API_SOURCE_DATA.extend(response_data)  # Use extend to add items directly
        
        print(">>> API_SOURCE_DATA populated - Length:", len(API_SOURCE_DATA))
    
    except requests.exceptions.RequestException as e:
        print(f"API request failed during startup: {str(e)}")
        raise HTTPException(status_code=502, detail=f"API request failed during startup: {str(e)}")

    except Exception as e:
        print(f"Unexpected error during startup: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Unexpected error during startup: {str(e)}")


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
        
        trending_data = API_SOURCE_DATA.copy()
        trending_data.sort(key=lambda stock : float(stock["price_change_percentage_24h"]), reverse=True)
        
        return trending_data[:10]
    
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


@router.post("/add-fav-stock")
def add_favourite_stocks(stock: StockModel, db: Session = Depends(get_db)):
    try:
        upsert_favourite_stock_in_db(stock_data=stock, db=db)
        return {"message": "Data inserted successfully", "data": stock}
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


# you can't directly call delete end point in browser, use curl
# ex:  curl -X DELETE "http://0.0.0.0:8500/api/remove-fav-stock?stock_id=bitcoin"
@router.delete("/remove-fav-stock") 
def remove_favourite_stocks(stock_id: str, db: Session = Depends(get_db)):
    try:
        remove_favourite_stock_from_db(stock_id=stock_id, db=db)
        return {"message": "Data removed successfully", "data": stock_id}
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

