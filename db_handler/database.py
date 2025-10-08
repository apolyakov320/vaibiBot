import asyncpg
from typing import Optional, List
from datetime import datetime, timedelta

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
        #cоздание таблицы для сообщений
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS messages (
                    id SERIAL PRIMARY KEY,
                    user_id BIGINT NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
                    role TEXT NOT NULL CHECK (role IN ('user', 'assistant')),
                    message TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT NOW()
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
    
    async def activate_subscription(self, user_id: int, days: int, user_tariff: str = 'premium') -> bool:
        """Активация или продление подписки"""
        async with self.pool.acquire() as conn:
            try:
                # Получаем текущую дату окончания подписки
                current_end_date = await conn.fetchval(
                'SELECT subscription_end_date FROM users WHERE user_id = $1',
                user_id
            )
            
            # Если подписка уже есть и еще активна - продлеваем
                if current_end_date and current_end_date > datetime.now():
                    new_end_date = current_end_date + timedelta(days=days)
                else:
                    # Если подписки нет или истекла - начинаем с текущей даты
                    new_end_date = datetime.now() + timedelta(days=days)
            
                # ВСЕ операции в одной транзакции
                await conn.execute('''
                    UPDATE users
                    SET subscription_end_date = $1,
                        tariff_type = $2,
                        is_subscription_active = TRUE
                    WHERE user_id = $3
                ''', new_end_date, user_tariff, user_id)
                return True           
            except Exception as e:
                print(f"Ошибка активации подписки: {e}")
            return False

    async def get_subscription_info(self, user_id: int) -> dict:
        """Возвращает информацию о подписке"""
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow('''
                SELECT subscription_end_date, tariff_type, is_subscription_active
                FROM users 
                WHERE user_id = $1
            ''', user_id)
            return dict(row) if row else None
    
    async def check_subscription(self, user_id: int) -> bool:
        """Проверяет активна ли подписка"""
        async with self.pool.acquire() as conn:
            result = await conn.fetchval('''
                SELECT is_subscription_active AND subscription_end_date > NOW()
                FROM users 
                WHERE user_id = $1
            ''', user_id)
            return bool(result)
    
    async def get_message_count_today(self, user_id: int) -> int:
        """Получает количество сообщений сегодня"""
        async with self.pool.acquire() as conn:
            count = await conn.fetchval('''
            SELECT COUNT(*) FROM messages 
            WHERE user_id = $1 AND DATE(created_at) = CURRENT_DATE
        ''', user_id)
        return count or 0
    
    async def add_message(self, user_id: int, role: str, message: str) -> bool:
        """Добавление сообщения в историю"""
        async with self.pool.acquire() as conn:
            await conn.execute('''
                INSERT INTO messages (user_id, role, message) 
                VALUES ($1, $2, $3)
            ''', user_id, role, message)
        return True

    async def add_interaction(self, user_id: int, user_msg: str, bot_msg: str) -> bool:
        """Добавление пары сообщение-ответ"""
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                await self.add_message(user_id, 'user', user_msg)
                await self.add_message(user_id, 'assistant', bot_msg)
        return True

    async def get_conversation_history(self, user_id: int, limit: int = 6) -> str:
        """Получить историю диалога в текстовом формате"""
        async with self.pool.acquire() as conn:
            rows = await conn.fetch('''
                SELECT role, message 
                FROM messages 
                WHERE user_id = $1 
                ORDER BY created_at DESC 
                LIMIT $2
            ''', user_id, limit * 2)
        
        # Переворачиваем чтобы получить хронологический порядок
        rows.reverse()
        
        # Форматируем в текст
        lines = []
        for row in rows:
            prefix = "Ты" if row['role'] == 'user' else "Vaibi"
            lines.append(f"{prefix}: {row['message']}")
        
        return "\n".join(lines)

    async def clear_conversation_history(self, user_id: int) -> bool:
        """Очистить историю диалога пользователя"""
        async with self.pool.acquire() as conn:
            result = await conn.execute('''
                DELETE FROM messages WHERE user_id = $1
            ''', user_id)
            print(f"🗑️ Удалено сообщений для user_id {user_id}: {result}")
        return True