import redis
from datetime import datetime, timezone

r = redis.Redis(host='localhost', port=6379, db=0)

def revoke_token(jti, exp_time):
    """ Store the revoked token's jti in Redis until it expires """
    time_to_live = exp_time - datetime.now(timezone.utc)
    r.setex(jti, int(time_to_live.total_seconds()), "revoked") # Store data with expiration
    ## this jti will be available in the db till the token is not expired, 
    ## once the token is expired then the jti will also get expired.

def is_token_revoked(jti):
    """ Check if the token ID (jti) exists in the Redis blacklist. """
    return r.exists(jti)  # Returns True if token is blacklisted


