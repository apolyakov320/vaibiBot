from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

def profile_kb():
    inline_kb_list = [
            [InlineKeyboardButton(text="🔄 Обновить", callback_data="refresh_profile")],
            [InlineKeyboardButton(text="🗑️ Удалить профиль", callback_data="delete_profile")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=inline_kb_list)

def delete_kb(user_id: int):
    inline_kb_list = [
        [InlineKeyboardButton(text="✅ Да, удалить навсегда", callback_data=f"confirm_delete_{user_id}")],
        [InlineKeyboardButton(text="❌ Нет, отменить", callback_data="cancel_delete")]
    ]  
    return InlineKeyboardMarkup(inline_keyboard=inline_kb_list)

def subscription_kb():
    inline_kb_list = [
        [InlineKeyboardButton(text='💎 1 месяц - 299₽', callback_data='pay_sub_1')],
        [InlineKeyboardButton(text='💎 3 месяца - 799₽', callback_data='pay_sub_3')],
        [InlineKeyboardButton(text='💎 12 месяцев - 1999₽', callback_data='pay_sub_12')],
        [InlineKeyboardButton(text='📊 Моя подписка', callback_data='my_subscription')]
    ]
    return InlineKeyboardMarkup(inline_keyboard=inline_kb_list)