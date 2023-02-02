import redis
from configs import Config

redis_pool = redis.ConnectionPool(host=Config.REDIS_ARGS['host'], port=6379,
                                  password=Config.REDIS_ARGS['password'], max_connections=5, db=3)
