from aiogram import Router, F
from aiogram.types import Message, ContentType
from db_handler.database import Database
from services.hf_service import HuggingFaceService  # импорт класса
from decouple import config

# экземпляр сервиса ИИ
hf_service = HuggingFaceService(api_token=config("HF_API_TOKEN"))

ai_router = Router()

@ai_router.message(F.content_type !=ContentType.TEXT)
async def handle_non_text(message: Message):
    """Обрабатываем не текст"""
    await message.answer("😊 Извини, я пока умею работать только с текстовыми сообщениями!\n\n"
        "Напиши мне что-нибудь текстом — с радостью пообщаюсь! 💫")

@ai_router.message(F.text)
async def handle_ai_message(message: Message, db: Database):
    user_id = message.from_user.id
    
    # Проверяем зарегистрирован ли пользователь
    user_data = await db.get_user(user_id)
    if not user_data:
        await message.answer(
            "👋 Чтобы начать общение, сначала нужно зарегистрироваться!\n\n"
            "Нажми /start — и мы сможем познакомиться поближе 💫"
        )
        return
    
    message_count = await db.get_message_count_today(user_id)
    has_subscription = await db.check_subscription(user_id)
    
    if not has_subscription and message_count >= 10:
        await message.answer(f"⚠️ Лимит: {message_count}/10 сообщений. /subscribe")
        return
    
    await message.bot.send_chat_action(user_id, "typing")
    
    # Получаем историю ТОЛЬКО для подписчиков
    conversation_history = ""
    if has_subscription:
        conversation_history = await db.get_conversation_history(user_id)
    
    response = await hf_service.get_response(message.text, conversation_history)
    await message.answer(response)
    
    # Сохраняем в БД только для подписчиков
    if has_subscription:
        await db.add_message(user_id, 'user', message.text)
        await db.add_message(user_id, 'assistant', response)
    else:
        # Для неподписанных только увеличиваем счетчик (без сохранения истории)
        await db.add_message(user_id, 'user', 'free_message')
        await db.add_message(user_id, 'assistant', 'free_message')