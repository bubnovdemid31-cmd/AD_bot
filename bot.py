import logging
import json
import os
from flask import Flask, request, jsonify, send_from_directory
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
import threading

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
    return send_from_directory('.', 'index.html')

@app.route('/webhook', methods=['POST'])
def webhook():
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
        "🚀 Открыть приложение",
        web_app=WebAppInfo(url=WEBAPP_URL)
    ))
    
    bot.send_message(
        message.chat.id,
        f"👋 Привет, {message.from_user.first_name}!\n\nНажми на кнопку:",
        reply_markup=keyboard
    )

@bot.message_handler(commands=['help'])
def help_command(message):
    bot.send_message(message.chat.id, "📖 /start - открыть приложение\n/help - помощь")

@bot.message_handler(func=lambda message: True)
def echo(message):
    bot.send_message(
        message.chat.id,
        f"📨 Получено: {message.text}\n\nНапиши /start"
    )

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
