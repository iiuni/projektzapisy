import redis


def flush_by_pattern(redis_client: redis.Redis, key_pattern: str) -> None:
    for key in redis_client.scan_iter(key_pattern):
        redis_client.delete(key)
