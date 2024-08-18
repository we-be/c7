from dataclasses import dataclass, asdict, fields
from typing import Dict, Union
import json
import redis

@dataclass
class HTTPHeaders:
    accept: str
    accept_encoding: str
    accept_language: str
    cache_control: str
    connection: str
    cookie: str
    host: str
    referer: str
    sec_fetch_dest: str
    sec_fetch_mode: str
    sec_fetch_site: str
    sec_fetch_user: str
    upgrade_insecure_requests: str
    user_agent: str
    sec_ch_ua: str
    sec_ch_ua_mobile: str
    sec_ch_ua_platform: str

    def to_dict(self) -> Dict[str, str]:
        header_dict = asdict(self)
        return {k.replace('_', '-'): v for k, v in header_dict.items()}

    def to_requests_format(self) -> Dict[str, str]:
        return self.to_dict()

    def to_redis(self, redis_client: redis.Redis, key: str) -> None:
        """
        Write the headers to Redis.
        
        :param redis_client: An instance of redis.Redis
        :param key: The key under which to store the headers in Redis
        """
        redis_client.set(key, json.dumps(self.to_dict()))

    @classmethod
    def from_redis(cls, redis_client: redis.Redis, key: str) -> 'HTTPHeaders':
        """
        Read the headers from Redis and create an HTTPHeaders instance.
        
        :param redis_client: An instance of redis.Redis
        :param key: The key under which the headers are stored in Redis
        :return: An instance of HTTPHeaders
        """
        headers_json = redis_client.get(key)
        if headers_json is None:
            raise KeyError(f"No headers found in Redis with key: {key}")
        
        headers_dict = json.loads(headers_json)
        field_names = {f.name for f in fields(cls)}
        filtered_dict = {k.replace('-', '_'): v for k, v in headers_dict.items() if k.replace('-', '_') in field_names}
        return cls(**filtered_dict)


if __name__ == "__main__":
    import redis

    # Initialize Redis client
    redis_client = redis.Redis(host='localhost', port=6379, db=0)

    # Create headers dictionary
    headers = {'copy-headers': 'from your browser'}

    # Convert headers to JSON string
    headers_json = json.dumps(headers)

    # Set the headers in Redis
    redis_client.set('http_headers', headers_json)

    print("Headers have been set in Redis.")

    # To retrieve and verify:
    retrieved_headers = redis_client.get('http_headers')
    print(json.loads(retrieved_headers))
