import asyncio
import asyncpg
from bot_base import bot, dp
from decouple import config
from db_handler.database import Database
from middlewares.subscription import SubscriptionMiddleware
from handlers.start_menu import start_router
from handlers.profile_menu import profile_router
from handlers.subscription import subscription_router


async def main():
    # Инициализируем пул подключений к БД
    pool = await asyncpg.create_pool(
        config('PG_LINK')
    )
    
    # Создаем экземпляр Database с пулом
    db = Database(pool)
    await db.create_tables()  # Создаем таблицы при старте
    
    # Сохраняем db в диспетчер для dependency injection
    dp["db"] = db

    # Добавляем middleware
    dp.message.middleware(SubscriptionMiddleware())
    
    # роутеры
    dp.include_router(start_router) 
    dp.include_router(profile_router)
    dp.include_router(subscription_router)
  
    
    try:
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        await bot.session.close()

if __name__=='__main__':
    asyncio.run(main())