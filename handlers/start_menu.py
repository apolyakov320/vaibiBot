import random
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
    
    # Добавляем/обновляем пользователя в БД
    await db.upsert_user(
        user_id=user.id,
        username=user.username,
        first_name=user.first_name
    )
    
    # Проверяем подписку ПОСЛЕ добавления пользователя
    has_sub = await db.check_subscription(user.id)

    if has_sub:
        welcome_messages = [
            f"💎 Привет, <b>{message.from_user.first_name}</b>! Рада снова тебя видеть! Чем займемся сегодня?",
            f"✨ <b>{message.from_user.first_name}</b>, как здорово, что ты снова здесь! О чем поговорим?",
            f"🌸 <b>{message.from_user.first_name}</b>, привет! Готова к новым интересным беседам!",
            f"💫 С возвращением, <b>{message.from_user.first_name}</b>! Соскучилась по нашим разговорам!"
        ]
        await message.answer(random.choice(welcome_messages))
    else:
    # Если пользователь уже существовал - показываем предложение о подписке
        if existing_user:
                welcome_back_messages = [
                    f"👋 С возвращением, <b>{message.from_user.first_name}</b>!\n\n"
                    "💎 <b>Хочешь больше возможностей?</b>\n"
                    "• ♾️ Общайся без ограничений\n" 
                    "• 💾 Сохраняй все наши диалоги\n"
                    "• 🧠 Получай ответы с памятью о прошлых беседах\n\n"
                    "Не начинай с чистого листа — оформи подписку!\n"
                    "/subscribe - продолжить диалог 💫",
                    
                    f"✨ Рада тебя видеть, <b>{message.from_user.first_name}</b>!\n\n"
                    "💎 <b>Давай сделаем наше общение еще лучше:</b>\n"
                    "• Безлимитные сообщения\n"
                    "• Полная история переписки\n"
                    "• Персонализированные ответы\n\n"
                    "Я запомню все наши разговоры 💾\n"
                    "/subscribe - улучшить общение 🌸",
                    
                    f"🌸 Привет, <b>{message.from_user.first_name}</b>! Скучала по нашим беседам!\n\n"
                    "💎 <b>С подпиской я смогу:</b>\n"
                    "• Помнить все твои предпочтения\n"
                    "• Не прерывать диалог лимитами\n"
                    "• Стать настоящим другом-собеседником\n\n"
                    "Давай не будем терять ни слова?\n"
                    "/subscribe - сохранить наши истории 💫"
                ]
                await message.answer(random.choice(welcome_back_messages))
        else:
            # Если пользователь новый
            new_user_messages = [
                f"👋 Привет, <b>{message.from_user.first_name}</b>! Рада знакомству!\n\n"
                "🎁 <b>Для начала дарим 10 бесплатных сообщений</b>\n"
                "А с подпиской откроются все возможности:\n\n"
                "💎 <b>Премиум-общение:</b>\n"
                "• Безлимитное количество сообщений\n"
                "• Сохранение истории диалогов\n"
                "• Ответы с учетом прошлых бесед\n"
                "• Персональный подход\n\n"
                "Не ограничивай наши разговоры — \n"
                "/subscribe - открыть все функции 🌟",
                
                f"✨ Добро пожаловать, <b>{message.from_user.first_name}</b>!\n\n"
                "🚀 <b>Начнем наше путешествие в общении!</b>\n"
                "Бесплатно: 10 сообщений в день\n\n"
                "💎 <b>С подпиской ты получишь:</b>\n"
                "• Неограниченное общение\n"
                "• Память всех наших диалогов\n" 
                "• Понимание твоих интересов\n"
                "• По-настоящему личные ответы\n\n"
                "Давай создадим историю вместе?\n"
                "/subscribe - начать осознанный диалог 💫",
                
                f"🌸 Приветствую, <b>{message.from_user.first_name}</b>! Готова к нашим первым беседам!\n\n"
                "📝 <b>Бесплатно можно отправить 10 сообщений</b>\n\n"
                "💎 <b>Но есть кое-что особенное:</b>\n"
                "• Бесконечные разговоры без лимитов\n"
                "• Я запомню все, что ты расскажешь\n"
                "• Наши диалоги будут становиться глубже\n"
                "• Ты получишь настоящего собеседника\n\n"
                "Готов к полноценному общению?\n"
                "/subscribe - раскрыть весь потенциал 🚀"
            ]
            await message.answer(random.choice(new_user_messages))

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