from pydantic import BaseModel
from typing import Optional

class StockModel(BaseModel):
    id: str
    symbol: str
    name: str
    image: Optional[str] = None
    current_price: float = None
    market_cap: Optional[float] = None
    market_cap_rank: Optional[int] = None
    high_24h: Optional[float] = None
    low_24h: Optional[float] = None
    price_change_24h: Optional[float] = None
    price_change_percentage_24h: Optional[float] = None
    sparkline: Optional[list] = None

class FavStockModel(BaseModel):
    id: str
    symbol: str
    name: str
    image: Optional[str] = None
    current_price: float = None
    market_cap: Optional[float] = None
    market_cap_rank: Optional[int] = None
    high_24h: Optional[float] = None
    low_24h: Optional[float] = None
    price_change_24h: Optional[float] = None
    price_change_percentage_24h: Optional[float] = None
    sparkline: Optional[list] = None
    fav_id: int


# class TransactionStockModel