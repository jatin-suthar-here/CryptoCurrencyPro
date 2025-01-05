import requests
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from constants import constants
from utils.database import get_db
from ..endpoint_utils import endpoint_utils

router = APIRouter()


API_SOURCE_DATA = []


@router.get("/fetch-source-data")
def get_source_data(db: Session = Depends(get_db)):
    
    global API_SOURCE_DATA
    response = requests.get(constants.COINGECKO_API_URL, params=constants.URL_PARAMS)
    response_data = response.json()
    API_SOURCE_DATA = len(response_data)
    print(len(response_data))

    endpoint_utils.insert_api_source_data_in_db(source_data=response_data, db=db)
    return response_data



@router.get("/trending-stocks")
def get_tranding_stocks():
    return API_SOURCE_DATA




