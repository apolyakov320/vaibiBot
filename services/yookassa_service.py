from yookassa import Configuration, Payment
from decouple import config

Configuration.account_id = config('YOOKASSA_SHOP_ID')
Configuration.secret_key = config('YOOKASSA_SECRET_KEY')

async def create_yookassa_payment(amount, description):
    payment = Payment.create({
        "amount": {
            "value": amount,
            "currency": "RUB"
        },
        "confirmation": {
            "type": "redirect",
            "return_url": "https://t.me/your_bot"
        },
        "capture": True,
        "description": description
    })
    return payment