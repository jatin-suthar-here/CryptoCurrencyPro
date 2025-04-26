from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from datetime import datetime, timedelta
from jose import JWTError, jwt

SECRET_KEY = "your_secret_key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 15
REFRESH_TOKEN_EXPIRE_DAYS = 7

app = FastAPI()
## The oauth2_scheme automatically looks for Authorization: Bearer <token> in the request header.
## The client should includes the token in the Authorization header.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

"""
RAW TOKEN DICT STRUCTURE:

{
    "iss": "jatin.suthar.com",  ## Verify Token Issuer (iss)
    'fullname',
    'username',
    'password',
    "exp": "expiry-datatime
}
"""


# Dummy database
fake_users_db = {"user1": {"password": "password123"}}
refresh_tokens = {}

# Generate JWT
def create_jwt(data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    to_encode["exp"] = datetime.utcnow() + expires_delta
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


# Login endpoint (returns access & refresh tokens)
@app.post("/login")
def login(username: str, password: str):
    if fake_users_db.get(username) and fake_users_db[username]["password"] == password:
        access_token = create_jwt({"sub": username}, timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
        refresh_token = create_jwt({"sub": username}, timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS))
        refresh_tokens[username] = refresh_token
        return {"access_token": access_token, "refresh_token": refresh_token}
    raise HTTPException(status_code=401, detail="Invalid credentials")

# Refresh token endpoint
@app.post("/refresh")
def refresh(refresh_token: str):
    try:
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload["sub"]
        if refresh_tokens.get(username) != refresh_token:
            raise HTTPException(status_code=401, detail="Invalid refresh token")
        new_access_token = create_jwt({"sub": username}, timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
        return {"access_token": new_access_token}
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")




## METHOD 1: -------------------------------------------------------
def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        exp = payload.get("exp")
        
        # Check if token is expired
        if exp and datetime.utcfromtimestamp(exp) < datetime.utcnow():
            raise HTTPException(status_code=401, detail="Token expired")

        return payload  # Return user data if valid
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    
@app.get("/protected")
def protected(token: str = Depends(oauth2_scheme)):
    try:
        ## verifying the token in every function on each API call.
        payload = verify_token(token)
        return {"message": "Access granted", "user": payload["sub"]}
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
## -----------------------------------------------------------------



## METHOD 2: -------------------------------------------------------
def verify_token(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if datetime.utcfromtimestamp(payload["exp"]) < datetime.utcnow():
            raise HTTPException(status_code=401, detail="Token expired")
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

@app.get("/protected")
def protected_route(payload: dict = Depends(verify_token)):
    return {"message": "Access granted", "user": payload["sub"]}
## -----------------------------------------------------------------

