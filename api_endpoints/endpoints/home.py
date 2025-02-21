from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from utils.database import get_db, ENV
from typing import List, Annotated


router = APIRouter()

@router.get("/")
def home():
    return {"message": "This is the Home Page"}
