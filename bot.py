import logging
import json
import os
from flask import Flask, request, jsonify, send_from_directory
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
import threading
import time

# ========== НАСТРОЙКА ==========
TOKEN = "8928646520:AAEwt54ioC_bu2GdW2nBAWfYe-QT2F1XXko"
PORT = int(os.environ.get('PORT', 5000))

# ========== ЛОГИРОВАНИЕ ==========
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ========== СОЗДАЕМ БОТА ==========
bot = telebot.TeleBot(TOKEN)

# ========== FLASK ДЛЯ HTML ==========
app = Flask(__name__)

@app.route('/')
def index():
    """Отдает index.html"""
    return send_from_directory('.', 'index.html')

@app.route('/webhook', methods=['POST'])
def webhook():
    """Принимает данные от WebApp"""
    try:
        data = request.get_json()
        logger.info(f"Получены данные от WebApp: {data}")
        return jsonify({"status": "ok"}), 200
    except Exception as e:
        logger.error(f"Ошибка: {e}")
        return jsonify({"status": "error"}), 500

@app.route('/health')
def health():
    return "OK", 200

# ========== КОМАНДЫ БОТА ==========

@bot.message_handler(commands=['start'])
def start(message):
    """Команда /start"""
    host = os.environ.get('RENDER_EXTERNAL_HOSTNAME', 'localhost:5000')
    WEBAPP_URL = f"https://{host}"
    
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton(
        "📦 Открыть каталог",
        web_app=WebAppInfo(url=WEBAPP_URL)
    ))
    
    bot.send_message(
        message.chat.id,
        f"🤖 <b>Алгоритм.Дело</b> — разработка сайтов, ботов и игр.\n\n"
        f"👋 Привет, {message.from_user.first_name}!\n\n"
        f"Мы занимаемся разработкой Telegram-ботов, сайтов, интернет-магазинов, "
        f"игр на Unity и сложных систем с базами данных.\n\n"
        f"📦 <b>Воспользуйтесь мини-приложением</b>, чтобы выбрать услугу и оставить заявку.\n\n"
        f"Нажми на кнопку ниже 👇",
        reply_markup=keyboard,
        parse_mode="HTML"
    )

@bot.message_handler(commands=['help'])
def help_command(message):
    bot.send_message(
        message.chat.id,
        "📖 <b>Помощь</b>\n\n"
        "Напиши /start, чтобы открыть каталог услуг.\n"
        "Выбери услугу, заполни форму — и мы свяжемся с тобой!",
        parse_mode="HTML"
    )

@bot.message_handler(func=lambda message: True)
def echo(message):
    bot.send_message(
        message.chat.id,
        f"📨 Получено: {message.text}\n\n"
        "Напиши /start, чтобы открыть каталог услуг."
    )

# ========== ОБРАБОТЧИК ДАННЫХ ОТ WEBAPP (через Flask) ==========
@app.route('/webapp_data', methods=['POST'])
def webapp_data():
    """Обработка данных от WebApp (альтернативный способ)"""
    try:
        data = request.get_json()
        logger.info(f"Получены данные: {data}")
        
        # Отправляем админу в Telegram
        name = data.get('name', 'Не указано')
        phone = data.get('phone', 'Не указан')
        email = data.get('email', 'Не указана')
        service = data.get('service', 'Не указана')
        price = data.get('price', 'Не указана')
        
        admin_text = (
            f"📩 <b>НОВАЯ ЗАЯВКА!</b>\n\n"
            f"👤 <b>Имя:</b> {name}\n"
            f"📱 <b>Телефон:</b> {phone}\n"
            f"✉️ <b>Почта:</b> {email}\n"
            f"📦 <b>Услуга:</b> {service}\n"
            f"💰 <b>Цена:</b> {price}"
        )
        
        # Отправляем админу K3n871
        try:
            bot.send_message("@K3n871", admin_text, parse_mode="HTML")
        except Exception as e:
            logger.error(f"Не удалось отправить админу: {e}")
        
        return jsonify({"status": "ok"}), 200
    except Exception as e:
        logger.error(f"Ошибка: {e}")
        return jsonify({"status": "error"}), 500

# ========== ЗАПУСК БОТА В ПОТОКЕ ==========
def run_bot():
    """Запуск бота в отдельном потоке"""
    logger.info("🤖 Бот запущен!")
    bot.infinity_polling()

# ========== ЗАПУСК ==========
if __name__ == "__main__":
    bot_thread = threading.Thread(target=run_bot, daemon=True)
    bot_thread.start()
    logger.info(f"🚀 Сервер запущен на порту {PORT}")
    app.run(host='0.0.0.0', port=PORT)
