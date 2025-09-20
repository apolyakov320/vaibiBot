import asyncpg
from typing import Optional

class Database:
    def __init__(self, pool: Optional[asyncpg.Pool] = None):
        self.pool = pool
    
    async def create_tables(self):
        """Создание таблиц (вызывается один раз при старте)"""
        async with self.pool.acquire() as conn:
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id BIGINT PRIMARY KEY,
                    username TEXT,
                    first_name TEXT NOT NULL,
                    registration_date TIMESTAMP DEFAULT NOW(),
                    last_activity TIMESTAMP DEFAULT NOW(),
                    subscription_end_date TIMESTAMP,
                    tariff_type TEXT DEFAULT 'free',
                    is_subscription_active BOOLEAN DEFAULT FALSE
                )
            ''')
    
    async def upsert_user(self, user_id: int, username: str, first_name: str) -> bool:
        """Добавление/обновление пользователя"""
        async with self.pool.acquire() as conn:
            await conn.execute('''
                INSERT INTO users (user_id, username, first_name)
                VALUES ($1, $2, $3)
                ON CONFLICT (user_id) DO UPDATE SET
                    username = EXCLUDED.username,
                    first_name = EXCLUDED.first_name,
                    last_activity = NOW()
            ''', user_id, username, first_name)
            return True
    
    async def get_user(self, user_id: int) -> Optional[dict]:
        """Получение данных пользователя"""
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                'SELECT * FROM users WHERE user_id = $1', 
                user_id
            )
            return dict(row) if row else None
    
    async def delete_user(self, user_id: int) -> bool:
        """Удаление пользователя"""
        async with self.pool.acquire() as conn:
            result = await conn.execute(
                'DELETE FROM users WHERE user_id = $1', 
                user_id
            )
            return "DELETE 1" in result
    
    async def activate_subscription(self, user_id: int, days: int, user_tariff: str='premium') -> bool:
        """Активация подписки на указанное кол-во дней""" 
        async with self.pool.acquire() as conn:
            await conn.execute('''
                               UPDATE users
                               SET subscription_end_date = NOW() + INTERVAL '1 day' * $1,
                                    tariff_type = $2,
                                    is_subscription_active = TRUE
                               WHERE user_id = $3
            ''', days, user_tariff, user_id)
            return True
        
    async def check_subscription(self, user_id: int) -> bool:
        """Проверяет активна ли подписка"""
        async with self.pool.acquire() as conn:
            result = await conn.fetchval('''
                SELECT is_subscription_active AND subscription_end_date > NOW()
                FROM users 
                WHERE user_id = $1
        ''', user_id)
        return bool(result)

    async def get_subscription_info(self, user_id: int) -> dict:
        """Возвращает информацию о подписке"""
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow('''
                SELECT subscription_end_date, tariff_type, is_subscription_active
                FROM users 
                WHERE user_id = $1
            ''', user_id)
            return dict(row) if row else None
    
    async def get_message_count_today(self, user_id: int) -> int:
        """Получает количество сообщений сегодня"""
        async with self.pool.acquire() as conn:
            count = await conn.fetchval('''
            SELECT COUNT(*) FROM messages 
            WHERE user_id = $1 AND DATE(created_at) = CURRENT_DATE
        ''', user_id)
        return count or 0