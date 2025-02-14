from datetime import datetime
from pydantic import BaseModel
from enum import Enum as PyEnum
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



class TransactionType(PyEnum):
    BUY = "buy"
    SELL = "sell"

class TransactionStatus(PyEnum):
    PROFIT = "profit"
    LOSS = "loss"
    NEUTRAL = "neutral"

class TransactionStockModel(BaseModel):
    id: int
    stock_id: str
    quantity: int
    type: TransactionType
    status: TransactionStatus
    price_at_transaction: float
    timestamp: datetime


