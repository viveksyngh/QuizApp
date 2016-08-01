import redis
from settings import (REDIS_HOST_NAME, REDIS_PORT_NAME, DB_NAME)

r = redis.StrictRedis(host=REDIS_HOST_NAME, port=REDIS_PORT_NAME, db=DB_NAME)


def setex(varname, value, time):
    r.set(varname, value)
    r.expire(varname, time)


def create_token(varname, value, time):
    r.set(varname, value)
    r.expire(varname, time)


def refresh_token(varname):
    r.expire(varname, 900)


def get_token(varname):
    return r.get(varname)


def delete_token(varname):
    return r.delete(varname)
