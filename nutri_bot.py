from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
from apscheduler.schedulers.asyncio import AsyncIOScheduler

# Твой токен
TOKEN = "5284761727:AAG5nQPZNpWLN4Gc3fCpYGtGBT83wYLNK0U"

# Обработка команды /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Я нутри-бот 🥦")

# Обработка обычных сообщений
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"Ты написал: {update.message.text}")

# Планировщик
def start_scheduler():
    scheduler = AsyncIOScheduler()
    # scheduler.add_job(твоя_функция, 'interval', seconds=60)
    scheduler.start()

# Основной запуск
def main():
    application = Application.builder().token(TOKEN).build()

    # Хендлеры
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Планировщик
    start_scheduler()

    # Запуск
    application.run_polling()

if __name__ == "__main__":
    main()
