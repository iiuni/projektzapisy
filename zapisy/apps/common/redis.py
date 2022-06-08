import redis


def flush_with_prefix(redis_client: redis.Redis, key_pattern: str) -> None:
    for key in redis_client.scan_iter(key_pattern):
        redis_client.delete(key)
