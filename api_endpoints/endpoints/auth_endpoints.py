import uuid
from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from fastapi import APIRouter, HTTPException, Depends, WebSocket
from fastapi.security import OAuth2PasswordBearer
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

## local file imports
from constants import constants
from ..endpoint_utils.endpoint_utils import (verify_user_exists_in_db, upsert_refresh_token_in_db, get_refresh_token_from_the_db)
from utils.database import get_db
from utils.utils import get_current_datetime
from utils.redis import is_token_revoked, revoke_token


router = APIRouter()


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
        "jti": str(uuid.uuid4()),  # Unique token ID for Token Blacklisting through Redis
        "created_at": (user_data["created_at"]),
        "expires_at": (user_data["expires_at"])
    }
    return jwt.encode(to_encode, constants.SECRET_KEY, algorithm=constants.ALGORITHM)


def verify_token(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, constants.SECRET_KEY, algorithms=[constants.ALGORITHM])

        # Parse the expires_at string into a datetime object
        expires_at = datetime.strptime(payload["expires_at"], "%Y-%m-%d %I:%M:%S %p").replace(tzinfo=timezone.utc)
        if expires_at < datetime.now(timezone.utc):
            raise HTTPException(status_code=401, detail="Token expired")
        
        # Check if token is blacklisted
        if is_token_revoked(payload["jti"]):
            return HTTPException(status_code=401, detail="Invalid - Token is Blacklisted")

        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


# Refresh token endpoint
@router.post("/refresh-token")
def refresh(access_token: str):
    try:
        payload = jwt.decode(token=access_token, key=constants.SECRET_KEY, algorithms=[constants.ALGORITHM])
        user_id = payload["user_id"]
        data = get_refresh_token_from_the_db(user_id=user_id)
        refresh_token = data["refresh_token"]

        refresh_token_payload = jwt.decode(refresh_token, constants.SECRET_KEY, algorithms=[constants.ALGORITHM])
        expires_at = datetime.strptime(refresh_token_payload["expires_at"], "%Y-%m-%d %I:%M:%S %p").replace(tzinfo=timezone.utc)
        if expires_at < datetime.now(timezone.utc):
            raise HTTPException(status_code=401, detail="Refresh Token Expired.")
        
        user_data = {
            "user_id": str(refresh_token_payload["user_id"]),  # Convert UUID to string
            "fullname": refresh_token_payload["fullname"],
            "email": refresh_token_payload["email"],
            "password": refresh_token_payload["password"],
            "iss": refresh_token_payload["iss"],
            "jti": refresh_token_payload["jti"],  # Unique token ID for Token Blacklisting through Redis
            "created_at": get_current_datetime(),
            "expires_at": constants.ACCESS_TOKEN_EXPIRE_MINUTES
        }
        new_access_token = create_jwt_token(user_data=user_data)
        return {"access_token": new_access_token}
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    

@router.get("/test")
def protected_route(payload: dict = Depends(verify_token)):
    """
    curl -X GET "http://localhost:8000/test" -H "Authorization: Bearer your_jwt_token_here"
    curl -X GET "http://0.0.0.0:8500/auth/test" -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiZWIwMTA0MTItYmE5OC00ZDU5LWJhZjYtMjZkYzUzYWU1OTYwIiwiZnVsbG5hbWUiOiJKYXRpbiBTdXRoYXIiLCJlbWFpbCI6ImphdGluQGFwcGxlLmNvbSIsInBhc3N3b3JkIjoiSGVsbG9KIiwiaXNzIjoiamF0aW4tc3V0aGFyLmNvbSIsImV4cGlyZXNfYXQiOiIyMDI1LTAyLTIzIDExOjQzOjI3IFBNIiwiY3JlYXRlZF9hdCI6IjIwMjUtMDItMjIgMTE6NDM6MjcgUE0ifQ.3LHo4TsET1qks7LugDMqOqLzUrLMbqs0qy-jI1TD1-Q"
    """
    return {"message": "Access granted", "user": payload}


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
        user_data["expires_at"] = get_current_datetime(timedelta=constants.ACCESS_TOKEN_EXPIRE_MINUTES)
        new_access_token = create_jwt_token(user_data=user_data)

        ## creating new refresh token
        user_data["expires_at"] = get_current_datetime(timedelta=constants.REFRESH_TOKEN_EXPIRE_DAYS)
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



