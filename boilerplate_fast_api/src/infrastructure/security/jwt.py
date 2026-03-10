import jwt
from datetime import datetime, timedelta
from src.settings import settings

# Estrutura na memória (lista negra)
TOKEN_BLACKLIST = set()

class JWTProvider:
    @staticmethod
    def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return encoded_jwt

    @staticmethod
    def decode_token(token: str) -> dict | None:
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            return payload
        except jwt.PyJWTError:
            return None

    @staticmethod
    def blacklist_token(token: str) -> None:
        TOKEN_BLACKLIST.add(token)

    @staticmethod
    def is_token_blacklisted(token: str) -> bool:
        return token in TOKEN_BLACKLIST

