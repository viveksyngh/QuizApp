import redis
from settings import (REDIS_HOST_NAME, REDIS_PORT_NAME, DB_NAME)

r = redis.StrictRedis(host=REDIS_HOST_NAME, port=REDIS_PORT_NAME, db=DB_NAME)


def create_token(varname, value, time):
    """Create a redis token with expiry"""
    r.set(varname, value)
    r.expire(varname, time)


def refresh_token(varname):
    """Refresh a token to increasethe expiry time."""
    r.expire(varname, 900)


def get_token(varname):
    """Get token"""
    return r.get(varname)


def delete_token(varname):
    """Deletes a token in redis."""
    return r.delete(varname)
