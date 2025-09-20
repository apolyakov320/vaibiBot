from aiogram import BaseMiddleware
from aiogram.types import Message

class SubscriptionMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):
        # Пропускаем команды связанные с подпиской
        if isinstance(event, Message) and event.text in ['/start', '/privacy', '/help', '/subscribe', '/profile', '/contact']:
            return await handler(event, data)
        
        # Проверяем подписку для остальных сообщений
        db = data.get('db')
        user_id = event.from_user.id
        
        if not await db.check_subscription(user_id):
            await event.answer(
                "⚠️ Для продолжения общения нужна подписка!\n\n"
                "Бесплатный лимит исчерпан.\n"
                "Используйте /subscribe чтобы получить доступ ко всем функциям 💖"
            )
            return
        
        return await handler(event, data)