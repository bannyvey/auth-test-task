import asyncio
import logging
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker


from src.config.settings import get_settings
from src.Models.User import User
from src.security.jwt_service import JwtService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def seed_users():
    """Вставить тестовые данные: 30 пользователей, 4 админа"""
    
    settings = get_settings()
    db_url = settings.database.get_database
    
    engine = create_async_engine(db_url, echo=False)
    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    jwt_service = JwtService()
    
    try:
        async with async_session() as session:
            logger.info("Начинаю вставку тестовых данных...")
            
            # Админы
            admins = [
                {
                    "email": "admin1@example.com",
                    "first_name": "Admin",
                    "last_name": "One",
                    "role": "admin"
                },
                {
                    "email": "admin2@example.com",
                    "first_name": "Admin",
                    "last_name": "Two",
                    "role": "admin"
                },
                {
                    "email": "admin3@example.com",
                    "first_name": "Admin",
                    "last_name": "Three",
                    "role": "admin"
                },
                {
                    "email": "admin4@example.com",
                    "first_name": "Admin",
                    "last_name": "Four",
                    "role": "admin"
                },
            ]
            
            # Обычные пользователи
            users = [
                {
                    "email": f"user{i}@example.com",
                    "first_name": f"User",
                    "last_name": f"User{i}",
                    "role": "user"
                }
                for i in range(1, 27)  # 26 обычных пользователей
            ]
            
            all_users = admins + users
            
            for user_data in all_users:
                hash_password = await jwt_service.hash_password("password123")
                
                user = User(
                    email=user_data["email"],
                    first_name=user_data["first_name"],
                    last_name=user_data["last_name"],
                    hash_password=hash_password,
                    role=user_data["role"],
                    is_active=True
                )
                
                session.add(user)
                logger.info(f"Добавлен пользователь: {user_data['email']} ({user_data['role']})")
            
            await session.commit()
            logger.info(" Успешно вставлено 30 пользователей (4 админа + 26 обычных)")
            
    except Exception as e:
        logger.error(f"Ошибка при вставке данных: {e}")
    finally:
        await engine.dispose()


