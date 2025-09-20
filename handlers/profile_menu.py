from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from datetime import datetime
from db_handler.database import Database
from keyboards.inline_kb import profile_kb, delete_kb

profile_router = Router()


# мой профиль
@profile_router.message(Command('profile'))
async def cmd_profile(message: Message, db: Database):
    user_id = message.from_user.id
    user_data = await db.get_user(user_id)

    if not user_data:
        await message.answer("❌ Профиль не найден, пройдите регистрацию, нажав /start")
        return
    
    # форматируем данные
    username = f"@{user_data['username']}" if user_data['username'] else "Не указан"
    first_name = user_data['first_name'] or "Не указано"
    reg_date = user_data['registration_date'].strftime("%d.%m.%Y %H:%M")
    last_active = user_data['last_activity'].strftime("%d.%m.%Y %H:%M") if user_data['last_activity'] else "Не активен"

    # отправляем информацию о профиле
    profile_text = (
        f"👤 <b>Ваш профиль</b>\n\n"
        f"🆔 ID: <code>{user_data['user_id']}</code>\n"
        f"👁️ Username: {username}\n"
        f"📛 Имя: {first_name}\n"
        f"📅 Регистрация: {reg_date}\n"
        f"⏰ Последняя активность: {last_active}\n\n"
        f"<i>Обновлено: {datetime.now().strftime('%H:%M:%S')}</i>"
        )
    
    await message.answer(profile_text, reply_markup=profile_kb())  

    
# обновить данные     
@profile_router.callback_query(lambda c: c.data == "refresh_profile")
async def refresh_profile(callback, db: Database):
    user_id = callback.from_user.id
    user_data = await db.get_user(user_id)

    if not user_data:
        await callback.answer("❌ Профиль не найден, пройдите регистрацию, нажав /start")
        return
    
    # форматируем данные
    username = f"@{user_data['username']}" if user_data['username'] else "Не указан"
    first_name = user_data['first_name'] or "Не указано"
    reg_date = user_data['registration_date'].strftime("%d.%m.%Y %H:%M")
    last_active = user_data['last_activity'].strftime("%d.%m.%Y %H:%M") if user_data['last_activity'] else "Не активен"

    # отправляем информацию о профиле
    profile_text = (
        f"👤 <b>Ваш профиль</b>\n\n"
        f"🆔 ID: <code>{user_data['user_id']}</code>\n"
        f"👁️ Username: {username}\n"
        f"📛 Имя: {first_name}\n"
        f"📅 Регистрация: {reg_date}\n"
        f"⏰ Последняя активность: {last_active}\n\n"
        f"<i>Обновлено: {datetime.now().strftime('%H:%M:%S')}</i>"
        )
        
    await callback.message.edit_text(profile_text, reply_markup=profile_kb())
    await callback.answer("✅ Профиль обновлен")


# удалить профиль     
@profile_router.callback_query(lambda c: c.data == "delete_profile")
async def delete_profile(callback, db: Database):
    user_id = callback.from_user.id

    keyboard = delete_kb(user_id)
    
    await callback.message.edit_text(
        "⚠️ <b>Вы уверены, что хотите удалить профиль?</b>\n\n"
        "Это действие:\n"
        "• Удалит все ваши данные\n"
        "• Прекратит подписку\n"
        "• Будет необратимо\n\n"
        "<i>Подтвердите удаление:</i>",
        reply_markup=keyboard
        )


# подтверждение удаления
@profile_router.callback_query(lambda c: c.data.startswith('confirm_delete_'))
async def confirm_delete_handler(callback, db: Database):
    user_id = int(callback.data.split('_')[-1])

    if callback.from_user.id != user_id:
        await callback.answer("❌ Это не ваш аккаунт!")
        return
    
    success = await db.delete_user(user_id)
    
    if success:
        await callback.message.edit_text("✅ Профиль удален!")
    else:
        await callback.message.edit_text("❌ Профиль не найден")


# отмена удаления
@profile_router.callback_query(lambda c: c.data =='cancel_delete')
async def cancel_delete_handler(callback):
    await callback.message.edit_text(
         "✅ <b>Удаление отменено</b>\n\n"
        "Ваши данные в безопасности! 💖"
    )
    await callback.answer()