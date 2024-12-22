import requests
from fastapi import APIRouter
from constants import constants

router = APIRouter()


# MODIFIED ->  https://api.coingecko.com/api/v3/coins/markets?vs_currency=Inr&order=market_cap_desc&per_page=250&page=1&price_change_percentage=24h


@router.get("/fetch_source_data")
def get_source_data():
    response = requests.get(constants.COINGECKO_API_URL, params=constants.URL_PARAMS)
    response_data = response.json()
    print(len(response_data))
    return response_data


