import uuid
from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from fastapi import APIRouter, HTTPException, Depends, WebSocket
from fastapi.security import OAuth2PasswordBearer
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

## local file imports
from constants import constants
from ..endpoint_utils.endpoint_utils import (verify_user_exists_in_db, upsert_refresh_token_in_db,
    get_refresh_token_from_the_db, insert_user_in_the_db, delete_user_from_the_db)
from utils.database import get_db
from utils.utils import get_current_datetime
from utils.redis import (is_token_revoked, revoke_token, add_user_session_in_redis, get_user_session_from_redis)


router = APIRouter()
# http://0.0.0.0:8500/auth/login


## The oauth2_scheme automatically looks for Authorization: Bearer <token> in the request header.
## The client should includes the token in the Authorization header.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def create_jwt_token(user_data: dict):
    """
    :param user_data (dict): user_id, fullname, email, password, iss, expires_at, created_at
    NOTE: JTI will be created in this function.
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
    token = jwt.encode(to_encode, constants.SECRET_KEY, algorithm=constants.ALGORITHM)
    return token


def verify_token(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, constants.SECRET_KEY, algorithms=[constants.ALGORITHM])
        print("payload : ", payload)
        # Parse the expires_at string into a datetime object
        expires_at = datetime.strptime(payload["expires_at"], "%Y-%m-%d %I:%M:%S %p").replace(tzinfo=timezone.utc)
        if expires_at < datetime.now(timezone.utc):
            raise HTTPException(status_code=401, detail="Token expired")
        
        # Check if token is blacklisted
        if is_token_revoked(payload["jti"]):
            raise HTTPException(status_code=401, detail="Invalid - Token is Blacklisted")

        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


@router.post("/refresh-token")
def refresh_access_token(access_token: str, db: Session = Depends(get_db)):
    """
    curl -X POST "http://0.0.0.0:8500/auth/refresh-token?access_token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiZDI4ZmU2MjUtNmI1Ny00MGI5LTg1ZmUtYjExYzQ5ZWRkMzA5IiwiZnVsbG5hbWUiOiJKYXRpbiBTdXRoYXIiLCJlbWFpbCI6ImphdGluQGFwcGxlLmNvbSIsInBhc3N3b3JkIjoiSjExIiwiaXNzIjoiamF0aW4tc3V0aGFyLmNvbSIsImp0aSI6ImQyZGM5M2Y5LWExZGUtNGI1MC05YTNmLTNmOWEzMDdkZGYxMSIsImNyZWF0ZWRfYXQiOiIyMDI1LTAyLTI4IDEwOjI3OjI2IFBNIiwiZXhwaXJlc19hdCI6IjIwMjUtMDMtMDEgMTA6Mjc6MjYgUE0ifQ.AGOB8qVF9wl475Nlt6smVbYSokWmSZlv33zGRb5ykWg"
    """
    try:
        payload = jwt.decode(token=access_token, key=constants.SECRET_KEY, algorithms=[constants.ALGORITHM])
        user_id = payload["user_id"]
        refresh_token = get_refresh_token_from_the_db(user_id=user_id, db=db)["refresh_token"]

        refresh_token_payload = jwt.decode(token=refresh_token, key=constants.SECRET_KEY, algorithms=[constants.ALGORITHM])
        expires_at = datetime.strptime(refresh_token_payload["expires_at"], "%Y-%m-%d %I:%M:%S %p").replace(tzinfo=timezone.utc)
        if expires_at < datetime.now(timezone.utc):
            raise HTTPException(status_code=401, detail="Refresh Token Expired.")
            ## NOTE: Redirecting user to Login again...
        
        user_data = {
            "user_id": str(refresh_token_payload["user_id"]),  # Convert UUID to string
            "fullname": refresh_token_payload["fullname"],
            "email": refresh_token_payload["email"],
            "password": refresh_token_payload["password"],
            "iss": refresh_token_payload["iss"],
            "jti": refresh_token_payload["jti"],  # Unique token ID for Token Blacklisting through Redis
            "created_at": get_current_datetime(),
            "expires_at": get_current_datetime(timedelta=constants.ACCESS_TOKEN_EXPIRE_MINUTES)
        }
        new_access_token = create_jwt_token(user_data=user_data)
        return {"access_token": new_access_token}
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error in refresh_access_token: {str(e)}")
    

@router.get("/test")
def protected_route(payload: dict = Depends(verify_token)):
    """
    curl -X GET "http://0.0.0.0:8500/auth/test" -H "Authorization: Bearer your_jwt_token_here"
    curl -X GET "http://0.0.0.0:8500/auth/test" -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoieydmdWxsbmFtZSc6ICdKYXRpbiBTdXRoYXInLCAnZW1haWwnOiAnanRuQGFwcGxlLmNvbScsICdwYXNzd29yZCc6ICdKMTEnLCAndXNlcl9pZCc6IHsuLi59LCAnaXNzJzogJ2phdGluLXN1dGhhci5jb20nLCAnY3JlYXRlZF9hdCc6ICcyMDI1LTAzLTAzIDA5OjExOjA0IFBNJywgJ2V4cGlyZXNfYXQnOiAnMjAyNS0wMy0wNCAwOToxMTowNCBQTSd9IiwiZnVsbG5hbWUiOiJKYXRpbiBTdXRoYXIiLCJlbWFpbCI6Imp0bkBhcHBsZS5jb20iLCJwYXNzd29yZCI6IkoxMSIsImlzcyI6ImphdGluLXN1dGhhci5jb20iLCJqdGkiOiI1MDkyOWMwOS04NjcwLTRkNmEtYWYwZi02MWJkNzE2NjA5NmMiLCJjcmVhdGVkX2F0IjoiMjAyNS0wMy0wMyAwOToxMTowNCBQTSIsImV4cGlyZXNfYXQiOiIyMDI1LTAzLTA0IDA5OjExOjA0IFBNIn0.9tcHxTEsPxLNnf96za4CF6KAmGpMihRxvqXVTgiYjx"
    
    """
    return {"message": "Access granted", "user": payload}


@router.post("/login")
def login_user(email: str, password: str, db: Session = Depends(get_db)):
    """
    curl -X POST "http://0.0.0.0:8500/auth/login?email=jatin@apple.com&password=Hello" -L
    The -L flag ensures that curl follows the redirect and displays the response from the /signup endpoint.
    """
    try:
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
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error in login_user: {str(e)}")


@router.post("/signup")
def signup_user(email: str, password: str, fullname: str, db: Session = Depends(get_db)):
    try:
        user_session = get_user_session_from_redis(email=email)
        if user_session:
            return {"User Already Exists."}
        else:
            user_data = {
                "fullname": fullname,
                "email": email,
                "password": password
            }
            user_id = insert_user_in_the_db(user_data=user_data, db=db)

            user_data["user_id"] = user_id
            user_data["iss"] = constants.TOKEN_ISS
            user_data["created_at"] = get_current_datetime()

            ## creating new access token
            user_data["expires_at"] = get_current_datetime(timedelta=constants.ACCESS_TOKEN_EXPIRE_MINUTES)
            new_access_token = create_jwt_token(user_data=user_data)

            ## creating new refresh token
            user_data["expires_at"] = get_current_datetime(timedelta=constants.REFRESH_TOKEN_EXPIRE_DAYS)
            refresh_token = create_jwt_token(user_data=user_data)
            
            refresh_token_dict = {
                "refresh_token": refresh_token,
                "user_id": user_id,
                "created_at": user_data["created_at"],
                "expires_at": user_data["expires_at"]
            }
            upsert_refresh_token_in_db(data_dict=refresh_token_dict, db=db)
            add_user_session_in_redis(email=email, status="active")
            return {"access_token": new_access_token}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error in signup_user: {str(e)}")


@router.post("/logout")
def logout_user(payload: dict = Depends(verify_token)):
    """
    curl -X POST "http://0.0.0.0:8500/auth/logout" -H "Authorization: Bearer ....."
    """
    try:
        print("logout Payload: ", payload)
        revoke_token(jti=payload["jti"], exp_time=payload["expires_at"])
        return {"User logged out successfully."}
    except Exception as e:
        raise e


@router.post("/delete-user")
def delete_user(payload: dict = Depends(verify_token), db: Session = Depends(get_db)):
    """
    NOTE: all the table contains ForeignKey("users.user_id", ondelete="CASCADE"), 
    this will automatically delete all the associated data of the user on deletion of user.

    curl -X POST "http://0.0.0.0:8500/auth/delete-user" -H "Authorization: Bearer ....."
    """
    try:
        user_id = payload["user_id"]
        delete_user_from_the_db(user_id=user_id, db=db)
        revoke_token(jti=payload["jti"], exp_time=payload["expires_at"])
        return {"User Deleted Successfully."}
    except Exception as e:
        raise e
    
    