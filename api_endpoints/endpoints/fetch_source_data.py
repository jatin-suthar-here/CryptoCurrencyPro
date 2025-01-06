import requests
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from constants import constants
from utils.database import get_db
from ..endpoint_utils import endpoint_utils

router = APIRouter()


API_SOURCE_DATA = []
TRENDING_STOCKS = []


@router.get("/fetch-source-data")
def get_source_data(db: Session = Depends(get_db)):
    try:
        # Fetch source data from the external API
        response = requests.get(constants.COINGECKO_API_URL, params=constants.URL_PARAMS)
        response.raise_for_status()  # Raise an HTTPError if the response status is 4xx/5xx
        response_data = response.json()
        
        # Append the fetched data to the global variable
        API_SOURCE_DATA.append(response_data)
        print(">>> data length:", len(response_data))
        
        # Insert data into the database
        insert_result = endpoint_utils.insert_api_source_data_in_db(source_data=response_data, db=db)
        
        if insert_result["status"] == "failure":
            error_message = insert_result.get("error", "Unknown error occurred during insertion.")
            print(f"Insertion failed: {error_message}")
            raise HTTPException(status_code=500, detail=f"Insertion failed: {error_message}")
        
        return response_data
    
    except requests.exceptions.RequestException as e:
        # Handle any errors related to the API request
        print(f"API request failed: {str(e)}")
        raise HTTPException(status_code=502, detail=f"API request failed: {str(e)}")
    
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")



@router.get("/trending-stocks")
def get_tranding_stocks():
    tranding_data = API_SOURCE_DATA[0].copy()
    print(tranding_data)
    tranding_data.sort(key=lambda stock: float(stock["price_change_percentage_24h"]), reverse=True)
    return tranding_data[:10]




