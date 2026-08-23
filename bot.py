import logging
import json
import os
from flask import Flask, request, jsonify, send_from_directory
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import Application, CommandHandler, ContextTypes
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
        return jsonify({"status": "ok", "message": "Данные получены"}), 200
    except Exception as e:
        logger.error(f"Ошибка: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

# ========== TELEGRAM БОТ ==========
def run_bot():
    """Запуск бота в отдельном потоке"""
    
    # Создаем приложение
    application = Application.builder().token(TOKEN).build()
    
    # URL для WebApp (автоматически подставится)
    WEBAPP_URL = f"https://{os.environ.get('RENDER_EXTERNAL_HOSTNAME', 'localhost:5000')}"
    
    # ===== КОМАНДЫ =====
    async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /start"""
        user = update.effective_user
        
        # Кнопка с WebApp
        keyboard = InlineKeyboardMarkup([[
            InlineKeyboardButton(
                "🚀 Открыть приложение",
                web_app=WebAppInfo(url=WEBAPP_URL)
            )
        ]])
        
        await update.message.reply_text(
            f"👋 Привет, {user.first_name}!\n\n"
            "Нажми на кнопку, чтобы открыть мини-приложение:",
            reply_markup=keyboard
        )
    
    async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /help"""
        await update.message.reply_text(
            "📖 Доступные команды:\n"
            "/start - открыть приложение\n"
            "/help - помощь\n\n"
            "Просто нажми кнопку 'Открыть приложение'!"
        )
    
    # Регистрируем команды
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    
    # Запускаем бота
    logger.info("🤖 Бот запущен!")
    application.run_polling()

# ========== ЗАПУСК ==========
if __name__ == "__main__":
    # Запускаем бота в отдельном потоке
    bot_thread = threading.Thread(target=run_bot)
    bot_thread.start()
    
    # Запускаем Flask сервер для HTML
    logger.info(f"🚀 Сервер запущен на порту {PORT}")
    app.run(host='0.0.0.0', port=PORT)