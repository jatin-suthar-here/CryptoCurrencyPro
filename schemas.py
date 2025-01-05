from pydantic import BaseModel

# Schema for request body
class ItemCreate(BaseModel):
    name: str
    description: str
    price: float

# Schema for response
class ItemResponse(BaseModel):
    id: int
    name: str
    description: str
    price: float

    class Config:
        # Allow SQLAlchemy objects to be serialized
        orm_mode = True  
