from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, LabeledPrice, PreCheckoutQuery, SuccessfulPayment
from aiogram.filters import Command
from db_handler.database import Database
from datetime import datetime
from keyboards.inline_kb import subscription_kb
from decouple import config

subscription_router = Router()

# Красивые названия подписок
SUBSCRIPTION_NAMES = {
    "premium_1m": "💎 1 месяц",
    "premium_3m": "💎 3 месяца", 
    "premium_12m": "💎 12 месяцев",
    "free": "🆓 Бесплатная"
}

# Цены в копейках
SUBSCRIPTION_PRICES = {
    1: 29900,  # 299 руб
    3: 79900,   # 799 руб
    12: 199900  # 1999 руб
}

@subscription_router.message(Command('subscribe'))
async def cmd_subscribe(message: Message, db: Database):
    user_id = message.from_user.id

    # проверка подписки
    has_active_sub = await db.check_subscription(user_id)

    if has_active_sub:
        sub_info = await db.get_subscription_info(user_id)
        end_date = sub_info['subscription_end_date'].strftime('%d.%m.%Y')
        tariff_type = sub_info.get('tariff_type', 'free')
        pretty_name = SUBSCRIPTION_NAMES.get(tariff_type, tariff_type)
        
        await message.answer(
            f"🌟 У вас уже есть активная подписка!\n"
            f"Действует до: {end_date}\n"
            f"Тариф: {pretty_name}\n\n"
            f"Чтобы продлить - выберите вариант ниже:",
            reply_markup=subscription_kb()
        )
    else:
        await message.answer(
            "💎 Подписка открывает:\n\n"
            "• Безлимитное общение без ограничений\n"
            "• Приоритетную поддержку\n\n"
            "Выберите вариант подписки:",
            reply_markup=subscription_kb()
        )

@subscription_router.callback_query(F.data.startswith("pay_sub_"))
async def handle_subscription_payment(callback: CallbackQuery, bot: Bot, db: Database):
    """Обработчик выбора подписки - открывает окно оплаты"""
    try:
        months = int(callback.data.split("_")[2])
        user_id = callback.from_user.id
        price = SUBSCRIPTION_PRICES[months]
        
        # Проверяем регистрацию пользователя
        user_data = await db.get_user(user_id)
        if not user_data:
            await callback.answer(
                "❌ Сначала начните общение с ботом! Отправьте любое сообщение.",
                show_alert=True
            )
            return
        
        # Получаем provider_token из настроек
        provider_token = config('PROVIDER_TOKEN')
        if not provider_token or provider_token == 'YOUR_PROVIDER_TOKEN':
            await callback.answer(
                "❌ Платежная система временно недоступна",
                show_alert=True
            )
            return
        
        # Отправляем инвойс (окно оплаты)
        await bot.send_invoice(
            chat_id=user_id,
            title=f"💎 Премиум подписка на {months} месяц(ев)",
            description=(
                "Включает:\n"
                "• Безлимитное общение\n"
                "• Эксклюзивный контент\n"
                "• Приоритетную поддержку"
            ),
            payload=f"subscription_{months}_{user_id}",
            provider_token=provider_token,
            currency="RUB",
            prices=[LabeledPrice(label=f"Подписка {months} мес.", amount=price)],
            start_parameter=f"subscribe_{months}",
            need_email=True,
            need_phone_number=False,
            need_shipping_address=False,
            is_flexible=False
        )
        
        await callback.answer()
        
    except Exception as e:
        print(f"Ошибка создания инвойса: {e}")
        await callback.answer("❌ Ошибка создания платежа", show_alert=True)

@subscription_router.pre_checkout_query()
async def process_pre_checkout(pre_checkout_query: PreCheckoutQuery, db: Database):
    """Проверка перед оплатой"""
    try:
        payload = pre_checkout_query.invoice_payload
        
        if not payload.startswith("subscription_"):
            await pre_checkout_query.answer(
                ok=False, 
                error_message="Неверный товар"
            )
            return
            
        # Проверяем существование пользователя
        user_id = pre_checkout_query.from_user.id
        user_data = await db.get_user(user_id)
        
        if not user_data:
            await pre_checkout_query.answer(
                ok=False,
                error_message="Пользователь не найден"
            )
            return
            
        await pre_checkout_query.answer(ok=True)
        
    except Exception as e:
        print(f"Ошибка pre_checkout: {e}")
        await pre_checkout_query.answer(
            ok=False,
            error_message="Внутренняя ошибка"
        )

@subscription_router.message(F.successful_payment)
async def process_successful_payment(message: Message, db: Database):
    """Обработка успешной оплаты - активируем подписку"""
    try:
        payment = message.successful_payment
        payload = payment.invoice_payload
        user_id = message.from_user.id
        
        # Извлекаем данные из payload
        parts = payload.split('_')
        months = int(parts[1])
        days = months * 30
        
        # Получаем информацию о текущей подписке
        sub_info = await db.get_subscription_info(user_id)
        has_active_sub = sub_info and sub_info['is_subscription_active'] and sub_info['subscription_end_date'] > datetime.now()
        
        # Активируем подписку (автоматически продлевает если уже есть)
        success = await db.activate_subscription(user_id, days, f"premium_{months}m")
        
        if success:
            # Получаем обновленную информацию
            new_sub_info = await db.get_subscription_info(user_id)
            end_date = new_sub_info['subscription_end_date'].strftime('%d.%m.%Y')
            
            if has_active_sub:
                message_text = (
                    f"🎉 <b>Оплата прошла успешно!</b>\n\n"
                    f"<b>Подписка продлена на {months} месяцев</b>\n"
                    f"Новая дата окончания: <b>{end_date}</b>\n"
                    f"Сумма: <b>{payment.total_amount / 100} ₽</b>\n\n"
                    f"<i>Подписка автоматически продлена!</i>"
                )
            else:
                message_text = (
                    f"🎉 <b>Оплата прошла успешно!</b>\n\n"
                    f"<b>Подписка активирована на {months} месяцев</b>\n"
                    f"Действует до: <b>{end_date}</b>\n"
                    f"Сумма: <b>{payment.total_amount / 100} ₽</b>\n\n"
                    f"<i>Теперь вам доступны все премиум-функции!</i>"
                )
            
            await message.answer(message_text, parse_mode='HTML')
        else:
            await message.answer(
                "✅ <b>Оплата прошла успешно, но возникла ошибка активации</b>\n\n"
                "Пожалуйста, обратитесь в поддержку: @vaibi_support",
                parse_mode='HTML'
            )
            
    except Exception as e:
        print(f"Ошибка обработки платежа: {e}")
        await message.answer(
            "✅ <b>Оплата прошла успешно, но возникла техническая ошибка</b>\n\n"
            "Пожалуйста, обратитесь в поддержку: @vaibi_support",
            parse_mode='HTML'
        )

@subscription_router.callback_query(F.data == "my_subscription")
async def handle_my_subscription(callback: CallbackQuery, db: Database):
    user_id = callback.from_user.id
    sub_info = await db.get_subscription_info(user_id)
    
    if sub_info and sub_info['is_subscription_active']:
        end_date = sub_info['subscription_end_date'].strftime("%d.%m.%Y %H:%M")
        status = "✅ Активна" if sub_info['subscription_end_date'] > datetime.now() else "❌ Истекла"
        tariff_type = sub_info.get('tariff_type', 'free')
        pretty_name = SUBSCRIPTION_NAMES.get(tariff_type, tariff_type)
        
        await callback.message.edit_text(
            f"📊 Ваша подписка:\n\n"
            f"Статус: {status}\n"
            f"Тариф: {pretty_name}\n"
            f"Действует до: {end_date}\n\n"
            f"Чтобы продлить - /subscribe"
        )
    else:
        await callback.message.edit_text(
            "❌ У вас нет активной подписки\n\n"
            "Используйте /subscribe чтобы получить доступ ко всем функциям!"
        )