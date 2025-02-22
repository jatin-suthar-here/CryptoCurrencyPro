from datetime import datetime, timedelta
from jose import JWTError, jwt
from fastapi import APIRouter, HTTPException, Depends, WebSocket
from fastapi.security import OAuth2PasswordBearer
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from utils.database import get_db
from utils.utils import get_current_datetime
from constants import constants
from ..endpoint_utils.endpoint_utils import (verify_user_exists_in_db, upsert_refresh_token_in_db)

router = APIRouter()


SECRET_KEY = "my-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = timedelta(minutes=24*60)
REFRESH_TOKEN_EXPIRE_DAYS = timedelta(days=7)

## The oauth2_scheme automatically looks for Authorization: Bearer <token> in the request header.
## The client should includes the token in the Authorization header.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")



def create_jwt_token(user_data: dict):
    """
    :param user_data (dict): user_id, fullname, email, password, iss, expires_at, created_at
    """
    to_encode = {
        "user_id": str(user_data["user_id"]),  # Convert UUID to string
        "fullname": user_data["fullname"],
        "email": user_data["email"],
        "password": user_data["password"],
        "iss": user_data["iss"],
        "expires_at": (user_data["expires_at"]),
        "created_at": (user_data["created_at"])
    }
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


@router.post("/login")
def login_user(email: str, password: str, db: Session = Depends(get_db)):
    """
    curl -X POST "http://0.0.0.0:8500/auth/login?email=jatin@apple.com&password=Hello" -L
    The -L flag ensures that curl follows the redirect and displays the response from the /signup endpoint.
    """
    user_data = verify_user_exists_in_db(email=email, password=password, db=db)
    if user_data:
        user_data["iss"] = constants.TOKEN_ISS # Verify Token Issuer (iss)
        user_data["created_at"] = get_current_datetime()

        ## creating new access token
        user_data["expires_at"] = get_current_datetime(timedelta=ACCESS_TOKEN_EXPIRE_MINUTES)
        new_access_token = create_jwt_token(user_data=user_data)

        ## creating new refresh token
        user_data["expires_at"] = get_current_datetime(timedelta=REFRESH_TOKEN_EXPIRE_DAYS)
        refresh_token = create_jwt_token(user_data=user_data)
        
        refresh_token_dict = {
            "refresh_token": refresh_token,
            "user_id": user_data["user_id"],
            "created_at": user_data["created_at"],
            "expires_at": user_data["expires_at"]
        }
        upsert_refresh_token_in_db(data_dict=refresh_token_dict, db=db)
        return {"access_token": new_access_token}
    else:
        return RedirectResponse(url=f"/auth/signup?email={email}&password={password}", status_code=301)


@router.post("/signup")
def signup_user(email: str, password: str, db: Session = Depends(get_db)):
    return f"Lets SignUp User [email={email}, password={password}]"



