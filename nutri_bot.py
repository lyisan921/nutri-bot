from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from apscheduler.schedulers.background import BackgroundScheduler

# Твой токен
TOKEN = "5284761727:AAG5nQPZNpWLN4Gc3fCpYGtGBT83wYLNK0U"

# Пример простой команды
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Я — нутри-бот 🥦")

# Пример обработки сообщений
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    await update.message.reply_text(f"Ты написал: {text}")

# Если есть планировщик — он выглядит так:
def start_scheduler():
    scheduler = BackgroundScheduler()
    # scheduler.add_job(твоя_функция, 'interval', seconds=60) — пример
    scheduler.start()

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    # Команды
    app.add_handler(CommandHandler("start", start))

    # Обработка текстов
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Планировщик, если нужен
    start_scheduler()

    # Запуск бота
    app.run_polling()

if __name__ == "__main__":
    main()
