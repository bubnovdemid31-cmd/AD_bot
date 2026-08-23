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

# ========== FLASK ДЛЯ HTML И ВЕБХУКА ==========
app = Flask(__name__)

@app.route('/')
def index():
    """Отдает index.html"""
    return send_from_directory('.', 'index.html')

@app.route('/webhook', methods=['POST'])
def webhook():
    """Принимает вебхук от Telegram"""
    try:
        data = request.get_json()
        logger.info(f"Получен вебхук: {data}")
        
        # Обрабатываем входящее обновление
        if 'message' in data:
            message = data['message']
            chat_id = message['chat']['id']
            text = message.get('text', '')
            
            # Обрабатываем команды
            if text == '/start':
                host = os.environ.get('RENDER_EXTERNAL_HOSTNAME', 'localhost:5000')
                WEBAPP_URL = f"https://{host}"
                
                keyboard = InlineKeyboardMarkup()
                keyboard.add(InlineKeyboardButton(
                    "📦 Открыть каталог",
                    web_app=WebAppInfo(url=WEBAPP_URL)
                ))
                
                bot.send_message(
                    chat_id,
                    f"🤖 <b>Алгоритм.Дело</b> — разработка сайтов, ботов и игр.\n\n"
                    f"👋 Привет! Нажми на кнопку ниже 👇",
                    reply_markup=keyboard,
                    parse_mode="HTML"
                )
            else:
                bot.send_message(
                    chat_id,
                    f"📨 Получено: {text}\n\nНапиши /start"
                )
        
        return jsonify({"status": "ok"}), 200
    except Exception as e:
        logger.error(f"Ошибка вебхука: {e}")
        return jsonify({"status": "error"}), 500

@app.route('/webapp_data', methods=['POST'])
def webapp_data():
    """Обработка данных от WebApp"""
    try:
        data = request.get_json()
        logger.info(f"Получены данные от WebApp: {data}")
        
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
        
        try:
            bot.send_message("@K3n871", admin_text, parse_mode="HTML")
        except Exception as e:
            logger.error(f"Не удалось отправить админу: {e}")
        
        return jsonify({"status": "ok"}), 200
    except Exception as e:
        logger.error(f"Ошибка: {e}")
        return jsonify({"status": "error"}), 500

@app.route('/health')
def health():
    return "OK", 200

@app.route('/set_webhook')
def set_webhook():
    """Устанавливает вебхук"""
    host = os.environ.get('RENDER_EXTERNAL_HOSTNAME', 'localhost:5000')
    webhook_url = f"https://{host}/webhook"
    
    import requests
    url = f"https://api.telegram.org/bot{TOKEN}/setWebhook?url={webhook_url}"
    response = requests.get(url)
    return jsonify(response.json())

# ========== ЗАПУСК ==========
if __name__ == "__main__":
    # Устанавливаем вебхук
    import requests
    host = os.environ.get('RENDER_EXTERNAL_HOSTNAME', 'localhost:5000')
    webhook_url = f"https://{host}/webhook"
    
    try:
        response = requests.get(f"https://api.telegram.org/bot{TOKEN}/setWebhook?url={webhook_url}")
        logger.info(f"Вебхук установлен: {response.json()}")
    except Exception as e:
        logger.error(f"Ошибка установки вебхука: {e}")
    
    logger.info(f"🚀 Сервер запущен на порту {PORT}")
    app.run(host='0.0.0.0', port=PORT)
