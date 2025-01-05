import requests
from fastapi import APIRouter
from constants import constants

router = APIRouter()


API_SOURCE_DATA = []


@router.get("/fetch-source-data")
def get_source_data():
    global API_SOURCE_DATA
    response = requests.get(constants.COINGECKO_API_URL, params=constants.URL_PARAMS)
    response_data = response.json()
    API_SOURCE_DATA = len(response_data)
    print(len(response_data))
    return response_data


@router.get("/trending-stocks")
def get_tranding_stocks():
    return API_SOURCE_DATA




