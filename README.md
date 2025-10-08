🌸 Vaibi - AI Girlfriend Chat Bot

Умный телеграм-бот с искусственным интеллектом, создающий комфортную атмосферу для общения. Бот имитирует общение с милой девушкой и предлагает премиум-функции через систему подписок.

✨ Возможности

- 💬 **Естественное общение** - AI-ассистент с характером милой девушки
- 💎 **Система подписок** - бесплатный лимит и премиум-доступ
- 💾 **История диалогов** - сохранение контекста для подписчиков
- 🔐 **Безопасность** - защита пользовательских данных
- 📊 **Аналитика** - отслеживание активности пользователей

🛠 Технологический стек

 Backend
- **Python 3.9+** - основной язык программирования
- **Aiogram 3.x** - асинхронный фреймворк для Telegram Bot API
- **PostgreSQL** - реляционная база данных
- **AsyncPG** - асинхронный драйвер для PostgreSQL
- **Hugging Face API** - AI-модели для генерации ответов

Вспомогательные библиотеки
- `python-decouple` - управление environment variables
- `aiohttp` - асинхронные HTTP-запросы
- `requests` - синхронные HTTP-запросы
- `yookassa` - система оплаты


📦 Установка и запуск

1. Клонирование репозитория
   
- `git clone https://github.com/your-username/vaibi-bot.git`
- `cd vaibi-bot`

2. Установка зависимостей

- `pip install -r requirements.txt`

3. Настройка окружения
   
Создайте файл `.env` в корневой директории:

`env`
- `BOT_TOKEN=`your_telegram_bot_token_here
- `PG_LINK=`postgresql://user:password@localhost:port/your_database
- `HF_API_TOKEN=`your_huggingface_api_token
- `PROVIDER_TOKEN=`your_telegram_payment_toke
- `YOOKASSA_SHOP_ID=`your_yookassa_shop_id
- `YOOKASSA_SECRET_KEY=`your_yookassa_secret_key

4. Настройка базы данных
   
- `createdb vaibi_db`

5. Запуск бота

- `python bot_run.py`

🏗 Структура проекта

vaibi-bot/

├── bot_run.py              # Точка входа

├── bot_base.py          # Базовая конфигурация

├── .env                 # Переменные окружения

├── requirements.txt     # Зависимости

├── db_handler/database.py       # Работа с БД

├── handlers/            # Хэндлеры бота

├── keyboards/inline_kb.py       # Клавиатуры

└── services/            # AI и YOOKASSA


⚙️ Конфигурация

  Настройка Telegram Bot
  
  Создайте бота через @BotFather
  
  Получите BOT_TOKEN
  
  Включите платежи через @BotFather
  
  Настройка AI API
  Получите токен на Hugging Face


🚀 Развертывание

  Локальный сервер
  
  - `python bot_run.py`

  Облачные платформы
  
  - `Railway, Heroku, Render для автоматического деплоя`

💳 Система подписок
  
  Бесплатный: 10 сообщений в день
  
  Премиум: безлимитное общение + история диалогов


👥 Контакты

  Разработчик: @deathiscure



