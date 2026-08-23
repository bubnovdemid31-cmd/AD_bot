import logging
import json
import os
from flask import Flask, request, jsonify, send_from_directory
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo

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

# ========== FLASK ==========
app = Flask(__name__)

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/webapp_data', methods=['POST'])
def webapp_data():
    """Получает заявку и отправляет админу K3n871"""
    try:
        data = request.get_json()
        logger.info(f"Получена заявка: {data}")
        
        name = data.get('name', 'Не указано')
        username = data.get('username', 'без_username')
        service = data.get('service', 'Не указана')
        price = data.get('price', 'Не указана')
        
        # Формируем красивое сообщение для админа
        admin_text = (
            f"📩 <b>НОВАЯ ЗАЯВКА!</b>\n\n"
            f"👤 <b>Имя:</b> {name}\n"
            f"🆔 <b>Username:</b> @{username}\n"
            f"📦 <b>Услуга:</b> {service}\n"
            f"💰 <b>Цена:</b> {price}\n\n"
            f"🕐 {__import__('datetime').datetime.now().strftime('%d.%m.%Y %H:%M')}"
        )
        
        # Отправляем админу
        try:
            bot.send_message("@K3n871", admin_text, parse_mode="HTML")
            logger.info("✅ Заявка отправлена админу")
        except Exception as e:
            logger.error(f"Ошибка отправки админу: {e}")
        
        return jsonify({"status": "ok"}), 200
    except Exception as e:
        logger.error(f"Ошибка: {e}")
        return jsonify({"status": "error"}), 500

@app.route('/health')
def health():
    return "OK", 200

# ========== ЗАПУСК ==========
if __name__ == "__main__":
    logger.info(f"🚀 Сервер запущен на порту {PORT}")
    app.run(host='0.0.0.0', port=PORT)
