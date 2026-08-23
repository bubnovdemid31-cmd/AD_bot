import logging
import json
import os
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
import asyncio

# ========== ТОКЕН ==========
TOKEN = "8928646520:AAEwt54ioC_bu2GdW2nBAWfYe-QT2F1XXko"

# ========== URL ВАШЕГО WEBAPP ==========
# Это ссылка, где лежит index.html (на Render или GitHub Pages)
WEBAPP_URL = "https://ad-bot-xagu.onrender.com"  # ЗАМЕНИТЕ НА ВАШУ ССЫЛКУ!

# ========== ВАШ АККАУНТ В TELEGRAM ==========
ADMIN_USERNAME = "K3n871"  # Ваш юзернейм в Telegram (без @)

# ========== НАСТРОЙКА ЛОГИРОВАНИЯ ==========
logging.basicConfig(level=logging.INFO)

# ========== СОЗДАНИЕ БОТА ==========
bot = Bot(token=TOKEN)
dp = Dispatcher()


# ========== КОМАНДА /START ==========
@dp.message(Command("start"))
async def start(message: types.Message):
    """Приветственное сообщение + кнопка для открытия каталога"""
    user = message.from_user

    # Кнопка с WebApp (каталог)
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[[
            InlineKeyboardButton(
                text="📦 Открыть каталог",
                web_app=WebAppInfo(url=WEBAPP_URL)
            )
        ]]
    )

    await message.answer(
        f"🤖 <b>Алгоритм.Дело</b> — разработка сайтов, ботов и игр.\n\n"
        f"👋 Привет, {user.first_name}!\n\n"
        f"Мы занимаемся разработкой Telegram-ботов, сайтов, интернет-магазинов, "
        f"игр на Unity и сложных систем с базами данных.\n\n"
        f"📦 <b>Воспользуйтесь мини-приложением</b>, чтобы выбрать услугу и оставить заявку.\n\n"
        f"Нажми на кнопку ниже 👇",
        reply_markup=keyboard,
        parse_mode="HTML"
    )


# ========== КОМАНДА /HELP ==========
@dp.message(Command("help"))
async def help_command(message: types.Message):
    await message.answer(
        "📖 <b>Помощь</b>\n\n"
        "Напиши /start, чтобы открыть каталог услуг.\n"
        "Выбери услугу, заполни форму — и мы свяжемся с тобой!",
        parse_mode="HTML"
    )


# ========== ОБРАБОТЧИК ДАННЫХ ОТ WEBAPP ==========
@dp.message(F.web_app_data)
async def handle_webapp_data(message: types.Message):
    """Получает заявку из WebApp и отправляет админу"""
    try:
        data = json.loads(message.web_app_data.data)
        logging.info(f"Получены данные: {data}")

        # Данные из формы
        user_name = data.get('name', 'Не указано')
        user_phone = data.get('phone', 'Не указан')
        user_email = data.get('email', 'Не указана')
        service = data.get('service', 'Не указана')
        price = data.get('price', 'Не указана')

        # Формируем сообщение для админа
        admin_text = (
            f"📩 <b>НОВАЯ ЗАЯВКА!</b>\n\n"
            f"👤 <b>Имя:</b> {user_name}\n"
            f"📱 <b>Телефон:</b> {user_phone}\n"
            f"✉️ <b>Почта:</b> {user_email}\n"
            f"📦 <b>Услуга:</b> {service}\n"
            f"💰 <b>Цена:</b> {price}\n\n"
            f"🆔 <b>От пользователя:</b> @{message.from_user.username or 'без_username'}\n"
            f"🆔 <b>ID:</b> {message.from_user.id}"
        )

        # Отправляем админу
        try:
            await bot.send_message(
                chat_id=ADMIN_USERNAME,
                text=admin_text,
                parse_mode="HTML"
            )
        except Exception as e:
            logging.error(f"Не удалось отправить админу: {e}")
            # Если не получается по юзернейму, можно отправить по ID
            # await bot.send_message(chat_id=123456789, text=admin_text)

        # Отвечаем пользователю
        await message.answer(
            f"✅ <b>Заявка отправлена!</b>\n\n"
            f"Мы свяжемся с вами в ближайшее время.\n"
            f"📞 {user_phone}\n"
            f"📦 {service}",
            parse_mode="HTML"
        )

    except json.JSONDecodeError:
        await message.answer("❌ Ошибка: неверный формат данных.")
    except Exception as e:
        logging.error(f"Ошибка обработки WebApp: {e}")
        await message.answer(f"❌ Произошла ошибка. Попробуйте позже.")


# ========== ОТВЕТ НА ЛЮБЫЕ СООБЩЕНИЯ ==========
@dp.message()
async def echo(message: types.Message):
    """Отвечает на любые сообщения, если не команда"""
    await message.answer(
        f"📨 Получено: {message.text}\n\n"
        "Напиши /start, чтобы открыть каталог услуг."
    )


# ========== ЗАПУСК БОТА ==========
async def main():
    print("🚀 БОТ ЗАПУСКАЕТСЯ...")
    print(f"✅ Бот: @algoritmdelo_bot")
    print(f"✅ Админ: @{ADMIN_USERNAME}")
    print(f"✅ WebApp: {WEBAPP_URL}")
    print("✅ Напишите /start в Telegram")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
