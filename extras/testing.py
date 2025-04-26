# @router.post("/refresh-token")
# def refresh_access_token(access_token: str, db: Session = Depends(get_db)):
#     """
#     CMD:  curl -X POST "http://0.0.0.0:8500/auth/refresh-token?access_token=your-token-string"
#     """
#     try:
#         payload = jwt.decode(token=access_token, key=constants.SECRET_KEY, algorithms=[constants.ALGORITHM])
#         user_id = payload["user_id"]
#         refresh_token = get_refresh_token_from_the_db(user_id=user_id, db=db)["refresh_token"]

#         refresh_token_payload = jwt.decode(token=refresh_token, key=constants.SECRET_KEY, algorithms=[constants.ALGORITHM])
#         expires_at = datetime.strptime(refresh_token_payload["expires_at"], "%Y-%m-%d %I:%M:%S %p").replace(tzinfo=timezone.utc)
#         if expires_at < datetime.now(timezone.utc):
#             raise HTTPException(status_code=401, detail="Refresh Token Expired.")
#             ## NOTE: Redirecting user to Login again...
        
#         user_data = {
#             "user_id": str(refresh_token_payload["user_id"]),  # Convert UUID to string
#             "fullname": refresh_token_payload["fullname"],
#             "email": refresh_token_payload["email"],
#             "password": refresh_token_payload["password"],
#             "iss": refresh_token_payload["iss"],
#             "jti": refresh_token_payload["jti"],  # Unique token ID for Token Blacklisting through Redis
#             "created_at": get_current_datetime(),
#             "expires_at": get_current_datetime(timedelta=constants.ACCESS_TOKEN_EXPIRE_MINUTES)
#         }
#         new_access_token = create_jwt_token(user_data=user_data)

#         return {
#             "access_token": new_access_token
#         }
    
#     except JWTError:
#         raise HTTPException(status_code=401, detail="Invalid token")
#     except Exception as e:
#         print("An error occurred [refresh_access_token]: ")
#         raise HTTPException(status_code=500, detail=f"Unexpected error in refresh_access_token: {str(e)}")


# @router.post("/login")
# def login_user(email: str, password: str, db: Session = Depends(get_db)):
#     """
#     CMD:  curl -X POST "http://0.0.0.0:8500/auth/login?email=jatin@apple.com&password=Hello" -L  
#     The -L flag ensures that curl follows the redirect and displays the response from the /signup endpoint.
#     """
#     try:
#         user_data = verify_user_exists_in_db(email=email, password=password, db=db)
#         if user_data:
#             user_data["iss"] = constants.TOKEN_ISS # Verify Token Issuer (iss)
#             user_data["created_at"] = get_current_datetime()

#             ## creating new access token
#             access_token_expiry = get_current_datetime(timedelta=constants.ACCESS_TOKEN_EXPIRE_MINUTES)
#             user_data["expires_at"] = access_token_expiry
#             new_access_token = create_jwt_token(user_data=user_data)

#             ## creating new refresh token
#             user_data["expires_at"] = get_current_datetime(timedelta=constants.REFRESH_TOKEN_EXPIRE_DAYS)
#             refresh_token = create_jwt_token(user_data=user_data)
            
#             refresh_token_dict = {
#                 "refresh_token": refresh_token,
#                 "user_id": user_data["user_id"],
#                 "created_at": user_data["created_at"],
#                 "expires_at": user_data["expires_at"]
#             }
#             upsert_refresh_token_in_db(data_dict=refresh_token_dict, db=db)

#             return {
#                 "access_token": new_access_token,
#                 "expires_at": access_token_expiry,
#                 "fullname": user_data["fullname"]
#             }
#         else:
#             return HTTPException(
#                 status_code=409,
#                 detail="User with this email does not exists. Please Signup."
#             )
#     except Exception as e:
#         print("An error occurred [login_user]: ")
#         raise HTTPException(status_code=500, detail=f"Unexpected error in login_user: {str(e)}")




