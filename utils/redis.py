import redis
from datetime import datetime, timezone
from constants import constants


r = redis.Redis(
    host=constants.REDIS_UPSTASH_HOST,
    port=constants.REDIS_PORT,
    password=constants.REDIS_UPSTASH_PASSWORD,
    ssl=True
)


## REDIS FUNCTIONS FOR JTI TOKEN DB
## -------------------------------------------------------------------------------
def revoke_token(jti, exp_time):
    """ Store the revoked token's jti in Redis until it expires """
    exp_time = datetime.strptime(exp_time, "%Y-%m-%d %I:%M:%S %p").replace(tzinfo=timezone.utc)
    time_to_live = exp_time - datetime.now(timezone.utc)
    jti_str = constants.REDIS_JTI_DB+jti
    r.setex(jti_str, int(time_to_live.total_seconds()), "revoked") # Store data with expiration
    ## this jti will be available in the db till the token is not expired, 
    ## once the token is expired then the jti will also get expired.

def is_token_revoked(jti):
    """ Check if the token ID (jti) exists in the Redis blacklist. """
    jti_str = constants.REDIS_USERS_SESSION_DB+jti
    return r.exists(jti_str)  # Returns True if token is blacklisted
## -------------------------------------------------------------------------------



## REDIS FUNCTIONS FOR USER SESSION DB
## -------------------------------------------------------------------------------
def add_user_session_in_redis(email: str, status: str):
    """ :param status (str): active | inactive | deleted """
    user_str = constants.REDIS_USERS_SESSION_DB + email
    r.set(user_str, status)

def get_user_session_from_redis(email: str):
    user_str = constants.REDIS_USERS_SESSION_DB + email
    return r.get(user_str)  # Returns the value of the key

def delete_user_session_from_redis(email: str):
    user_str = constants.REDIS_USERS_SESSION_DB + email
    return r.delete(user_str)  # Deletes the matching values from the Redis DB
## -------------------------------------------------------------------------------

