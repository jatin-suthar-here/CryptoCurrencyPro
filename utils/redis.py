import subprocess, time, redis
from datetime import datetime, timezone


REDIS_HOST = "localhost"
REDIS_PORT = 6379
DB_FOR_JTI = 0
DB_FOR_USERS = 1

def start_redis():
    """ Start Redis server as a subprocess. """
    print("✅ Starting Redis Server...")
    redis_process = subprocess.Popen(["redis-server"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return redis_process

def stop_redis():
    try:
        print("🛑 Stopping Redis server...")
        subprocess.run(["pkill", "redis-server"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print("✅ Redis server stopped.")
    except Exception as e:
        print(f"Error stopping Redis: {e}")

def check_redis_connection():
    """ Check if Redis is running """
    r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=DB_FOR_JTI, decode_responses=True)
    for _ in range(5):
        try:
            r.ping()
            print("✅ Redis is running!")
            break
        except redis.ConnectionError:
            print("❌ Redis connection failed!")
            time.sleep(1)

def revoke_token(jti, exp_time):
    """ Store the revoked token's jti in Redis until it expires """
    r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=DB_FOR_JTI, decode_responses=True)
    exp_time = datetime.strptime(exp_time, "%Y-%m-%d %I:%M:%S %p").replace(tzinfo=timezone.utc)
    time_to_live = exp_time - datetime.now(timezone.utc)
    r.setex(jti, int(time_to_live.total_seconds()), "revoked") # Store data with expiration
    ## this jti will be available in the db till the token is not expired, 
    ## once the token is expired then the jti will also get expired.

def is_token_revoked(jti):
    """ Check if the token ID (jti) exists in the Redis blacklist. """
    r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=DB_FOR_JTI, decode_responses=True)
    return r.exists(jti)  # Returns True if token is blacklisted


def add_user_in_redis(user_id):
    r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=DB_FOR_USERS, decode_responses=True)
    r.set(user_id, "active")

def is_user_exists_in_redis(user_id):
    r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=DB_FOR_USERS, decode_responses=True)
    return r.exists(user_id)  # Returns True if token is blacklisted


