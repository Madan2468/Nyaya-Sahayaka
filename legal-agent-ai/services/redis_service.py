import os
import json
import redis
from typing import Optional, List, Dict, Any

class RedisService:
    def __init__(self, redis_url: Optional[str] = None):
        self.redis_url = redis_url or os.environ.get("REDIS_URL", "redis://localhost:6379/0")
        try:
            self.client = redis.Redis.from_url(self.redis_url, decode_responses=True)
            self.client.ping()
            self.is_connected = True
            print("[RedisService] Successfully connected to Redis.")
        except Exception as e:
            print(f"[RedisService] Warning: Redis not reachable ({e}). Operating in memory-fallback mode.")
            self.client = None
            self.is_connected = False
            self._local_cache = {}
            self._local_sessions = {}

    def get_cached_response(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Retrieves cached response for frequent queries."""
        if not self.is_connected or not self.client:
            return self._local_cache.get(cache_key)
        try:
            val = self.client.get(f"cache:{cache_key}")
            return json.loads(val) if val else None
        except Exception as e:
            print(f"[RedisService] Cache get error: {e}")
            return None

    def set_cached_response(self, cache_key: str, data: Dict[str, Any], ttl_seconds: int = 3600):
        """Caches query response with a TTL (default 1 hour)."""
        if not self.is_connected or not self.client:
            self._local_cache[cache_key] = data
            return
        try:
            self.client.setex(f"cache:{cache_key}", ttl_seconds, json.dumps(data))
        except Exception as e:
            print(f"[RedisService] Cache set error: {e}")

    def append_chat_message(self, chat_id: str, role: str, content: str, max_turns: int = 6):
        """
        Appends a message to the windowed chat context in Redis.
        Maintains a sliding window of the last `max_turns` messages.
        """
        msg = json.dumps({"role": role, "content": content})
        if not self.is_connected or not self.client:
            if chat_id not in self._local_sessions:
                self._local_sessions[chat_id] = []
            self._local_sessions[chat_id].append({"role": role, "content": content})
            if len(self._local_sessions[chat_id]) > max_turns:
                self._local_sessions[chat_id] = self._local_sessions[chat_id][-max_turns:]
            return

        key = f"session:{chat_id}:history"
        try:
            pipe = self.client.pipeline()
            pipe.rpush(key, msg)
            pipe.ltrim(key, -max_turns, -1) # Keep only the last `max_turns` items
            pipe.expire(key, 86400) # 24h expiration
            pipe.execute()
        except Exception as e:
            print(f"[RedisService] Error updating session memory: {e}")

    def get_chat_window(self, chat_id: str) -> List[Dict[str, str]]:
        """Retrieves the recent window of messages for the specified chat window."""
        if not self.is_connected or not self.client:
            return self._local_sessions.get(chat_id, [])

        key = f"session:{chat_id}:history"
        try:
            raw_items = self.client.lrange(key, 0, -1)
            return [json.loads(item) for item in raw_items]
        except Exception as e:
            print(f"[RedisService] Error fetching chat memory: {e}")
            return []

    def clear_chat_window(self, chat_id: str):
        """Clears memory for a specific chat window."""
        if not self.is_connected or not self.client:
            self._local_sessions.pop(chat_id, None)
            return
        try:
            self.client.delete(f"session:{chat_id}:history")
        except Exception as e:
            print(f"[RedisService] Error clearing chat session: {e}")
