from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    ContextTypes, ConversationHandler, filters
)

# Этапы разговора
CALORIE, TEST_QUESTION = range(2)

# Вопросы для теста
questions = [
    "Ты хочешь изменить питание?",
    "Готов ли ты соблюдать рекомендации ежедневно?",
    "Есть ли у тебя хронические заболевания?",
]

# Правильные ответы (для простоты 1 - Да, 2 - Нет)
# Допустим, для "подходит ли ведение" нужны ответы: Да, Да, Нет
correct_answers = [1, 1, 2]

# Для хранения ответов пользователя
user_answers = []

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(
        "Привет! Я бот-нутрициолог.\n"
        "Для расчета базовой нормы калорий введи свой пол в ответ (м/ж):"
    )
    return CALORIE

async def calorie_sex(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    sex = update.message.text.lower()
    if sex not in ['м', 'ж', 'm', 'f', 'male', 'female']:
        await update.message.reply_text("Пожалуйста, введи 'м' или 'ж'")
        return CALORIE
    context.user_data['sex'] = sex
    await update.message.reply_text("Теперь введи свой вес (кг):")
    return CALORIE + 1

async def calorie_weight(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    try:
        weight = float(update.message.text)
        context.user_data['weight'] = weight
    except ValueError:
        await update.message.reply_text("Пожалуйста, введи число для веса.")
        return CALORIE + 1
    await update.message.reply_text("Теперь введи свой рост (см):")
    return CALORIE + 2

async def calorie_height(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    try:
        height = float(update.message.text)
        context.user_data['height'] = height
    except ValueError:
        await update.message.reply_text("Пожалуйста, введи число для роста.")
        return CALORIE + 2
    await update.message.reply_text("Теперь введи свой возраст (лет):")
    return CALORIE + 3

async def calorie_age(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    try:
        age = int(update.message.text)
        context.user_data['age'] = age
    except ValueError:
        await update.message.reply_text("Пожалуйста, введи целое число для возраста.")
        return CALORIE + 3
    
    # Расчет базовой нормы калорий (формула Миффлина-Сан Жеора)
    sex = context.user_data['sex']
    weight = context.user_data['weight']
    height = context.user_data['height']
    age = context.user_data['age']

    if sex in ['м', 'm', 'male']:
        bmr = 10 * weight + 6.25 * height - 5 * age + 5
    else:
        bmr = 10 * weight + 6.25 * height - 5 * age - 161

    context.user_data['bmr'] = bmr

    await update.message.reply_text(f"Твоя базовая норма калорий: {bmr:.1f} ккал.\n"
                                    "Теперь пройдем короткий тест, чтобы понять, подходит ли тебе личное ведение нутрициолога.\n"
                                    f"{questions[0]}\n"
                                    "Ответь:\n1 - Да\n2 - Нет",
                                    reply_markup=ReplyKeyboardMarkup([['1', '2']], one_time_keyboard=True, resize_keyboard=True))
    context.user_data['test_q'] = 0
    context.user_data['user_answers'] = []
    return TEST_QUESTION

async def test_answer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    answer = update.message.text
    if answer not in ['1', '2']:
        await update.message.reply_text("Пожалуйста, ответь 1 или 2.")
        return TEST_QUESTION
    
    context.user_data['user_answers'].append(int(answer))
    q_index = context.user_data['test_q'] + 1

    if q_index >= len(questions):
        # Тест окончен, оцениваем результаты
        ua = context.user_data['user_answers']
        ca = correct_answers
        # Простая логика: подходит, если ответил правильно хотя бы на 2 вопроса
        score = sum([ua[i] == ca[i] for i in range(len(ca))])
        if score >= 2:
            await update.message.reply_text(
                "Поздравляю! Тебе подходит личное ведение.\n"
                "Напиши мне в Telegram: @alisa_son",
                reply_markup=ReplyKeyboardRemove()
            )
        else:
            await update.message.reply_text(
                "Похоже, личное ведение тебе пока не подходит. Но не расстраивайся!",
                reply_markup=ReplyKeyboardRemove()
            )
        return ConversationHandler.END
    else:
        context.user_data['test_q'] = q_index
        await update.message.reply_text(
            f"{questions[q_index]}\nОтветь:\n1 - Да\n2 - Нет",
            reply_markup=ReplyKeyboardMarkup([['1', '2']], one_time_keyboard=True, resize_keyboard=True)
        )
        return TEST_QUESTION

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(
        'Диалог отменен. Если захотите начать заново, введите /start.',
        reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END

def main():
    # Ваш токен сюда
    TOKEN = "5284761727:AAG5nQPZNpWLN4Gc3fCpYGtGBT83wYLNK0U"

    app = ApplicationBuilder().token(5284761727:AAG5nQPZNpWLN4Gc3fCpYGtGBT83wYLNK0U).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            CALORIE: [MessageHandler(filters.TEXT & ~filters.COMMAND, calorie_sex)],
            CALORIE + 1: [MessageHandler(filters.TEXT & ~filters.COMMAND, calorie_weight)],
            CALORIE + 2: [MessageHandler(filters.TEXT & ~filters.COMMAND, calorie_height)],
            CALORIE + 3: [MessageHandler(filters.TEXT & ~filters.COMMAND, calorie_age)],
            TEST_QUESTION: [MessageHandler(filters.Regex('^(1|2)$'), test_answer)]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    app.add_handler(conv_handler)

    print("Бот запущен...")
    app.run_polling()

if __name__ == '__main__':
    main()
