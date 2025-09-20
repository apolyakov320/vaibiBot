from aiogram import Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from db_handler.database import Database 


start_router = Router()


@start_router.message(CommandStart())
async def cmd_start(message: Message, db:Database):
    user = message.from_user

    # Сначала проверяем, существует ли пользователь
    existing_user = await db.get_user(user.id)
    
    # Добавляем пользователя в БД
    success = await db.upsert_user(
            user_id=user.id,
            username=user.username,
            first_name=user.first_name
        )
    
    has_sub = await db.check_subscription(user.id)

    if has_sub:
        await message.answer(
            f"💎 Привет, <b>{message.from_user.first_name}</b>!\n"
            "Рада снова тебя видеть! Чем займемся сегодня?"
        )
    else:
        await message.answer(
            f"👋 Привет, <b>{message.from_user.first_name}</b>!\n\n"
            "Теперь ты прошел регистрацию!\n"
            "Бесплатно ты можешь отправить 10 сообщений в день.\n"
            "Чтобы снять ограничения используй /subscribe"
        )
            

# политика конфиденциальности
@start_router.message(Command('privacy'))
async def cmd_privacy(message: Message):
    privacy_text = (
        "🔐 <b>Политика конфиденциальности</b>\n\n"
        "Ознакомиться с полной версией можно по ссылке:\n"
        "<a href='https://docs.google.com/document/d/10WCkCHAgtb96DQfdCzGjqJTdceB7s5-5A9MwuIsLQis/edit?usp=sharing'>Политика конфиденциальности</a>"
    )
    await message.answer(privacy_text, parse_mode='HTML')

# список всех команд
@start_router.message(Command('help'))
async def cmd_help(message: Message):
    await message.answer('<blockquote>👤/profile - Мой профиль\n'
                         '💎/subscribe - Приобрести подписку</blockquote>\n'
                         )
    
# связаться с разработчиком
@start_router.message(Command('contact'))
async def cmd_contact(message: Message):
    await message.answer('Нашли баг? Есть идеи? Пишите:\n\n'
                         '• <i>Создатель:</i> @deathiscure')
    
    
