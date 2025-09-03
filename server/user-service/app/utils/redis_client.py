import redis
from typing import Optional
from app.config import settings


class RedisClient:
    """Redis 클라이언트 싱글톤"""
    
    _instance = None
    _redis_pool = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(RedisClient, cls).__new__(cls)
            cls._redis_pool = redis.ConnectionPool.from_url(
                settings.redis_url,
                decode_responses=True
            )
        return cls._instance
    
    def get_client(self) -> redis.Redis:
        """Redis 클라이언트 반환"""
        return redis.Redis(connection_pool=self._redis_pool)
    
    async def set_token(self, user_id: str, token: str, expires_in: int = None) -> bool:
        """토큰을 Redis에 저장"""
        try:
            client = self.get_client()
            key = f"user_token:{user_id}"
            
            if expires_in:
                client.setex(key, expires_in, token)
            else:
                client.setex(key, settings.access_token_expire_minutes * 60, token)
            
            return True
        except Exception as e:
            print(f"Redis 토큰 저장 오류: {e}")
            return False
    
    async def get_token(self, user_id: str) -> Optional[str]:
        """Redis에서 토큰 조회"""
        try:
            client = self.get_client()
            key = f"user_token:{user_id}"
            return client.get(key)
        except Exception as e:
            print(f"Redis 토큰 조회 오류: {e}")
            return None
    
    async def delete_token(self, user_id: str) -> bool:
        """Redis에서 토큰 삭제 (로그아웃)"""
        try:
            client = self.get_client()
            key = f"user_token:{user_id}"
            client.delete(key)
            return True
        except Exception as e:
            print(f"Redis 토큰 삭제 오류: {e}")
            return False
    
    async def is_token_blacklisted(self, token: str) -> bool:
        """토큰이 블랙리스트에 있는지 확인"""
        try:
            client = self.get_client()
            key = f"blacklist_token:{token}"
            return client.exists(key) == 1
        except Exception as e:
            print(f"Redis 블랙리스트 확인 오류: {e}")
            return False
    
    async def blacklist_token(self, token: str, expires_in: int) -> bool:
        """토큰을 블랙리스트에 추가"""
        try:
            client = self.get_client()
            key = f"blacklist_token:{token}"
            client.setex(key, expires_in, "blacklisted")
            return True
        except Exception as e:
            print(f"Redis 블랙리스트 추가 오류: {e}")
            return False


# 전역 Redis 클라이언트 인스턴스
redis_client = RedisClient()

