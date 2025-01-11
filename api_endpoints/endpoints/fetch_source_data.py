import requests
import asyncio  # For periodic tasks
from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends, WebSocket
from sqlalchemy.orm import Session
from constants import constants
from utils.database import get_db
from ..endpoint_utils import endpoint_utils


router = APIRouter()


# Global variables
API_SOURCE_DATA = []
TRENDING_STOCKS = []


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
            "message": f"Successfully extracted data on {datetime.now()}", 
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








# @router.get("/fetch-source-data")
# def get_source_data(db: Session = Depends(get_db)):
#     # Fetch source data from the external API
#     response = requests.get(constants.COINGECKO_API_URL, params=constants.URL_PARAMS)
#     response.raise_for_status()  # Raise an HTTPError if the response status is 4xx/5xx
#     response_data = response.json()

#     # Insert data into the database
#     insert_result = endpoint_utils.insert_api_source_data_in_db(source_data=response_data, db=db)
    
#     if insert_result["status"] == "failure":
#         error_message = insert_result.get("error", "Unknown error occurred during insertion.")
#         print(f"Insertion failed: {error_message}")
#         raise HTTPException(status_code=500, detail=f"Insertion failed: {error_message}")
            
