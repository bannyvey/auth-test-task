from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Tuple
from jose import jwt
from jose.exceptions import JWTError, ExpiredSignatureError
import bcrypt

from src.config.settings import get_settings


class JwtService:
    def __init__(self):
        self.settings = get_settings()

    @staticmethod
    async def hash_password(password: str) -> str:
        """Хэширует пароль с использованием bcrypt."""
        password_bytes = password.encode('utf-8')
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password_bytes, salt).decode('utf-8')

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Проверяет соответствие пароля хэшу."""
        password_bytes = plain_password.encode('utf-8')
        hashed_bytes = hashed_password.encode('utf-8')
        return bcrypt.checkpw(password_bytes, hashed_bytes)

    @staticmethod
    def create_access_token(user_id: int) -> str:
        """Создаёт access token с коротким сроком жизни."""
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=get_settings().app.access_token_expire_minutes
        )
        payload = {
            "sub": str(user_id),
            "exp": expire,
            "type": "access"
        }
        return jwt.encode(
            payload,
            get_settings().app.jwt_secret_key.get_secret_value(),
            algorithm=get_settings().app.jwt_algorithm
        )

    @staticmethod
    def decode_token(token: str) -> Optional[Dict]:
        """Декодирует и валидирует токен. Возвращает None если токен невалидный."""
        try:
            payload = jwt.decode(
                token,
                get_settings().app.jwt_secret_key.get_secret_value(),
                algorithms=[get_settings().app.jwt_algorithm]
            )
            return payload
        except JWTError:
            return None

    def create_access_token_response(self, user_id: int) -> tuple[str, int]:
        """Возвращает токен и время жизни в секундах"""
        expire_minutes = get_settings().app.access_token_expire_minutes
        expire = datetime.now(timezone.utc) + timedelta(minutes=expire_minutes)
        payload = {
            "sub": str(user_id),
            "exp": expire,
            "type": "access"
        }
        token = jwt.encode(
            payload,
            get_settings().app.jwt_secret_key.get_secret_value(),
            algorithm=get_settings().app.jwt_algorithm
        )
        return token, int(expire_minutes * 60)

    def create_refresh_token(self, user_id: int) -> Tuple[str, int]:
        expire_days = get_settings().app.refresh_token_expire_days
        expire = datetime.now(timezone.utc) + timedelta(days=expire_days)
        payload = {
            "sub": str(user_id),
            "exp": expire,
            "type": "refresh"
        }
        token = jwt.encode(
            payload,
            get_settings().app.jwt_secret_key.get_secret_value(),
            algorithm=get_settings().app.jwt_algorithm
        )
        return token, int(expire_days * 86400)

    @staticmethod
    def hash_refresh_token(token: str) -> str:
        return bcrypt.hashpw(token.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    @staticmethod
    def verify_refresh_token(hashed: str, plain: str) -> bool:
        return bcrypt.checkpw(plain.encode('utf-8'), hashed.encode('utf-8'))
